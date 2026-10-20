"""Эталон S7-GRAPH: последовательность одного FB по руководству S7-GRAPH (Graph7_e.pdf, гл. 6–7), независимо
от lower/seq_to_ast.py.

Состояние: множество активных шагов, время активации каждого шага, защёлки ошибок контроля. Один вызов:
- INIT_SQ (и первый вызов) — активны начальные шаги, ошибки сброшены; OFF_SQ — активных шагов нет; в этом
  вызове переходы не срабатывают, события S1/S0 — по сравнению с началом вызова (до INIT_SQ/OFF_SQ);
- ACK_EF — ошибки контроля квитированы (в цикле квитирования переход возможен, Graph7_e.pdf §7.11);
- переход допустим, если активны все его шаги-предшественники (§6.x: синхронизация параллельной ветви),
  условие истинно и у предшественников нет ошибки контроля; в альтернативной ветви — первый слева (§6.7);
- переключение по состоянию начала вызова; новые шаги активны в этом же вызове;
- контроль активного шага защёлкивает ошибку, блокировка — условие C (§7.2);
- действия: N — операнд = 1, пока шаг активен (C — и блокировка выполнена), при выключении — 0; S/R —
  каждый цикл активности; D — через время после активации, пока шаг активен; L — первые n мс; инструкции
  SCL — пока шаг активен; с событием S1/S0 — один раз (§7.3);
- постоперации LAD/FBD.
Спорное (порядок цикла S7-1500, одновременное включение и выключение шага) — docs/ASSUMPTIONS.md, L18–L22.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from s7conv.frontends.simaticml import XBlock
from s7conv.ir.net import RAIL, Network, build_network
from s7conv.ir.seq import parse_graph, topology
from s7conv.nodes import Assign, Binary, Ident, Literal, LocalRef, Member, Unary
from s7conv.parser import parse_statements
from s7conv.semantics.net_eval import EvalError, _NetRun
from s7conv.semantics.values import Memory, Value


@dataclass
class _StepState:
    active: bool = False
    since: int = 0  # момент активации, мс
    last: int = 0  # время активности (последней), мс


def _binary(op: str, a: Any, b: Any) -> Value | None:
    """Двухместная операция инструкции SCL; None — операция эталоном не моделируется."""
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "AND":
        return bool(a) and bool(b)
    if op == "OR":
        return bool(a) or bool(b)
    if op == "XOR":
        return bool(a) != bool(b)
    compare = {"=": a == b, "<>": a != b}
    if op in compare:
        return bool(compare[op])
    if op in ("<", ">", "<=", ">="):
        return bool({"<": a < b, ">": a > b, "<=": a <= b, ">=": a >= b}[op])
    return None


class _StepView:
    """`#Шаг.X`, `#Шаг.T` для чтения из сетей условий (Memory.read ищет экземпляр по имени)."""

    def __init__(self, state: _StepState) -> None:
        self.state = state

    def member(self, name: str) -> Value:
        key = name.upper()
        if key == "X":
            return self.state.active
        if key == "T":
            return self.state.last
        raise EvalError(f"элемент шага {name} эталоном не моделируется")


@dataclass
class _Holder:
    """Минимум, который нужен _NetRun: память, часы, журнал записей."""

    mem: Memory
    now: int = 0
    trace: Any = None
    registry: dict[str, XBlock] = field(default_factory=dict)


class _Writes:
    def __init__(self) -> None:
        self.writes: dict[str, str] = {}


class GraphEvaluator:
    """Экземпляр FB GRAPH: память интерфейса и состояние последовательности."""

    def __init__(self, block: XBlock) -> None:
        self.block = block
        self.mem = Memory()
        for sec in block.sections:
            for m in sec.members:
                self.mem.declare(m.name, m.datatype, m.start_value)
        units = [u for u in block.units if u.body is not None]
        if len(units) != 1 or units[0].body_kind != "Graph":
            raise EvalError(f"{block.name}: ожидается одна сеть GRAPH")
        graph = parse_graph(units[0].body)  # type: ignore[arg-type]
        if len(graph.sequences) != 1:
            raise EvalError(f"{block.name}: последовательностей {len(graph.sequences)}")
        self.seq = graph.sequences[0]
        self.topo = topology(self.seq)
        if self.topo.issues:
            raise EvalError("; ".join(self.topo.issues))
        self.post = [build_network(net, 0, lang) for net, lang in graph.post]
        self.pre = [build_network(net, 0, lang) for net, lang in graph.pre]
        self.steps = {s.number: _StepState() for s in self.seq.steps}
        for st in self.seq.steps:
            self.mem.instances[st.name.lower()] = _StepView(self.steps[st.number])  # type: ignore[assignment]
        self.errors: dict[int, bool] = {s.number: False for s in self.seq.steps if s.supervision is not None}
        self.started = False
        self.holder = _Holder(self.mem, trace=_Writes())
        self.writes = self.holder.trace.writes
        self.trans_nets = {t.number: build_network(t.net, 0, t.lang) for t in self.seq.transitions if t.net is not None}
        self.sv_nets = {
            s.number: build_network(s.supervision, 0, "LAD") for s in self.seq.steps if s.supervision is not None
        }
        self.il_nets = {
            s.number: build_network(s.interlock, 0, "LAD") for s in self.seq.steps if s.interlock is not None
        }
        names = {m.name.upper() for s in block.sections for m in s.members}
        self.has = {n: n in names for n in ("INIT_SQ", "OFF_SQ", "ACK_EF", "ERR_FLT")}

    # -- условия ------------------------------------------------------------------------
    def condition(self, net: Network) -> bool:
        run = _NetRun(self.holder, net)  # type: ignore[arg-type]
        coils = [uid for uid, p in net.parts.items() if p.name in ("TrCoil", "SvCoil", "IlCoil")]
        if len(coils) != 1:
            raise EvalError("в сети условия нет одной катушки условия")
        src = net.driver(coils[0], "in")
        if src is None:
            return False
        if src.kind == RAIL:
            return True
        return bool(run.signal(coils[0], "in", False))

    def run_plain(self, net: Network) -> None:
        run = _NetRun(self.holder, net)  # type: ignore[arg-type]
        run.execute()

    # -- инструкции SCL в действиях ---------------------------------------------------------
    def expr(self, e: Any) -> Value:
        if isinstance(e, Literal):
            if e.kind == "bool":
                return e.text.upper() == "TRUE"
            if e.kind == "int":
                return int(e.text)
            raise EvalError(f"литерал {e.text} эталоном не моделируется")
        if isinstance(e, LocalRef | Ident):
            return self.mem.read(f"#{e.name}")
        if isinstance(e, Member):
            base = e.base
            if isinstance(base, LocalRef | Ident):
                return self.mem.read(f"#{base.name}.{e.name}")
        if isinstance(e, Unary) and e.op == "NOT":
            return not self.expr(e.operand)
        if isinstance(e, Unary) and e.op == "-":
            return -self.expr(e.operand)
        if isinstance(e, Binary):
            a, b = self.expr(e.left), self.expr(e.right)
            op = "AND" if e.op == "&" else e.op
            result = _binary(op, a, b)
            if result is not None:
                return result
        raise EvalError(f"выражение {type(e).__name__} эталоном не моделируется")

    def instruction(self, text: str) -> None:
        body, issues = parse_statements(text if text.rstrip().endswith(";") else text + ";")
        if issues:
            raise EvalError(f"инструкция {text!r} не разобрана")
        for st in body:
            if not isinstance(st, Assign) or not isinstance(st.target, LocalRef | Ident):
                raise EvalError(f"инструкция {text!r} эталоном не моделируется")
            self.mem.write(f"#{st.target.name}", self.expr(st.value))
            self.writes[st.target.name.lower()] = f"действие: {text}"

    def write(self, operand: str, value: Value, where: str) -> None:
        self.mem.write(operand, value)
        self.writes[operand.lstrip("#").lower()] = where

    # -- вызов ----------------------------------------------------------------------------
    def call(self, inputs: dict[str, Value], now: int) -> None:
        self.holder.now = now
        for name, value in inputs.items():
            self.mem.write(f"#{name}", value)
        for net in self.pre:
            self.run_plain(net)
        steps = self.steps
        before = {n: s.active for n, s in steps.items()}
        hold = not self.started or bool(self.has["INIT_SQ"] and self.mem.read("#INIT_SQ"))
        hold = hold or bool(self.has["OFF_SQ"] and self.mem.read("#OFF_SQ"))
        if not self.started or (self.has["INIT_SQ"] and self.mem.read("#INIT_SQ")):
            self.started = True
            for st in self.seq.steps:
                state = steps[st.number]
                state.active = st.init
                if st.init:
                    state.since, state.last = now, 0
            for n in self.errors:
                self.errors[n] = False
        if self.has["OFF_SQ"] and self.mem.read("#OFF_SQ"):
            for state in steps.values():
                state.active = False
        if self.has["ACK_EF"] and self.mem.read("#ACK_EF"):
            for n in self.errors:
                self.errors[n] = False
        for state in steps.values():
            if state.active:
                state.last = (now - state.since) & 0xFFFFFFFF
        current = {n: s.active for n, s in steps.items()}
        # переходы по состоянию после INIT/OFF; альтернативы одного шага — по приоритету
        fired: list[int] = []
        used: set[int] = set()
        for link in self.topo.links:
            if hold:
                break
            if not link.preds or not all(current[p] for p in link.preds):
                continue
            if any(self.errors.get(p, False) for p in link.preds):
                continue
            if any(p in used for p in link.preds):
                continue
            tnet = self.trans_nets.get(link.number)
            if tnet is not None and self.condition(tnet):
                fired.append(link.number)
                used.update(link.preds)
        for number in fired:
            for p in self.topo.link(number).preds:
                steps[p].active = False
        for number in fired:
            for sc in self.topo.link(number).succs:
                steps[sc].active = True
        rose = {n for n, s in steps.items() if s.active and not before[n]}
        fell = {n for n, s in steps.items() if before[n] and not s.active}
        for n in rose:
            steps[n].since, steps[n].last = now, 0
        # контроль и блокировка
        for n, net in self.sv_nets.items():
            if steps[n].active and self.condition(net):
                self.errors[n] = True
        interlock = {n: self.condition(net) for n, net in self.il_nets.items()}
        # действия
        for st in self.seq.steps:
            n = st.number
            active = steps[n].active
            for a in st.actions:
                where = f"шаг S{n}, действие {a.index}"
                ok = interlock.get(n, True) if a.interlock else True
                q = a.qualifier.upper()
                if a.event:
                    happened = n in rose if a.event == "S1" else n in fell if a.event == "S0" else None
                    if happened is None:
                        raise EvalError(f"{where}: событие {a.event} эталоном не моделируется")
                    if happened and (ok or a.event != "S1"):
                        if q == "N" and not a.operand:
                            self.instruction(a.text)
                        elif q in ("S", "R") and a.operand:
                            self.write(a.operand, q == "S", where)
                        else:
                            raise EvalError(f"{where}: {a.event} {q} эталоном не моделируется")
                    continue
                if q == "N" and a.operand:
                    if active or n in fell:
                        self.write(a.operand, active and ok, where)
                elif q == "N":
                    if active and ok:
                        self.instruction(a.text)
                elif q in ("S", "R") and a.operand:
                    if active and ok:
                        self.write(a.operand, q == "S", where)
                elif q in ("D", "L") and a.operand and a.time:
                    limit = int(self.mem.read(a.time))
                    elapsed = steps[n].last
                    value = elapsed >= limit if q == "D" else elapsed < limit
                    if active or n in fell:
                        self.write(a.operand, active and value and ok, where)
                else:
                    raise EvalError(f"{where}: действие {q} эталоном не моделируется")
        if self.has["ERR_FLT"] and self.errors:
            self.write("#ERR_FLT", any(self.errors.values()), "ERR_FLT")
        for net in self.post:
            self.run_plain(net)

    def read(self, name: str) -> Value:
        return self.mem.read(f"#{name}")

    def outputs(self) -> dict[str, Value]:
        out: dict[str, Value] = {}
        for sec in self.block.sections:
            if sec.name in ("Output", "InOut"):
                for m in sec.members:
                    out[m.name] = self.mem.values[m.name.lower()]
        return out


__all__ = ["GraphEvaluator"]
