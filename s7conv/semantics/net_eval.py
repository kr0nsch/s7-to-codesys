"""Эталон LAD/FBD S7: поток питания по сетям (справочник LAD S7-300/400, s7kop__b.pdf).

Правила (независимо от lower/net_to_ast.py):
- контакт пропускает питание, если операнд = 1 (размыкающий — = 0); ветви объединяет элемент O, FBD — A/O/X;
- катушка = RLO; S/R — только при RLO = 1; SR — «сначала S, затем R» (§1.10), RS — «сначала R, затем S» (§1.11),
  состояние хранит бит-операнд;
- P/N: фронт по сравнению с битом памяти, бит памяти := текущее значение (§1.17–1.20);
- блоки с EN/ENO: при EN = 0 блок не выполняется, ENO = 0; ENO арифметики = EN AND NOT переполнение
  (прил. C.1), результат пишется с переносом;
- прыжок JMP/JMPN к метке впереди: сети до метки не выполняются; RET — конец блока;
- порядок: сети по порядку, внутри сети — элементы с действием в порядке XML, входы вычисляются по
  требованию (сверху вниз, слева направо).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from s7conv.frontends.simaticml import XBlock
from s7conv.ir.net import IDENT, PIN, RAIL, Network, build_network
from s7conv.semantics.values import UNDEF, Counter, Memory, Timer, Value, type_key, wrap

_INT_LIMITS = {"INT": (-32768, 32767), "DINT": (-(2**31), 2**31 - 1), "SINT": (-128, 127)}
_PURE = {"Contact", "Not", "O", "A", "X", "Eq", "Ne", "Gt", "Ge", "Lt", "Le", "InRange", "OutRange"}


class EvalError(Exception):
    """Конструкция вне эталона (неизвестный элемент) — блок не сравнивается."""


@dataclass
class Trace:
    """Кто последним писал переменную: «сеть 3, UId 27» — для первого расхождения equiv."""

    writes: dict[str, str] = field(default_factory=dict)


class NetEvaluator:
    """Экземпляр блока LAD/FBD: память и вызов `call(inputs, now_ms)`."""

    def __init__(self, block: XBlock, registry: dict[str, XBlock] | None = None) -> None:
        self.block = block
        self.registry = registry or {}
        self.mem = Memory()
        for sec in block.sections:
            if sec.name in ("Return",):
                continue
            for m in sec.members:
                self.mem.declare(m.name, m.datatype, m.start_value)
        ret = block.section("Return")
        self.ret_type = ret.members[0].datatype if ret and ret.members else ""
        if self.ret_type and self.ret_type.lower() != "void":
            self.mem.declare("Ret_Val", self.ret_type)
        self.networks = [
            build_network(u.body, u.number, u.lang, u.title, u.comment)
            for u in block.units
            if u.body is not None and u.body_kind == "FlgNet"
        ]
        if len(self.networks) != len([u for u in block.units if u.body is not None]):
            raise EvalError(f"{block.name}: в блоке есть сети не LAD/FBD")
        self.trace = Trace()
        self.now = 0
        self.temps = [m.name.lower() for s in block.sections if s.name == "Temp" for m in s.members]

    # -- вызов блока ------------------------------------------------------------------
    def call(self, inputs: dict[str, Value], now: int) -> None:
        self.now = now
        for name in self.temps:
            self.mem.declare(name, self.mem.types[name])
        for name, value in inputs.items():
            self.mem.write(f"#{name}", value)
        skip_to: str | None = None
        for net in self.networks:
            if skip_to is not None:
                if skip_to not in net.labels:
                    continue
                skip_to = None
            run = _NetRun(self, net)
            result = run.execute()
            if result == "RET":
                return
            if result is not None:
                skip_to = result

    def read(self, name: str) -> Value:
        return self.mem.read(f"#{name}")

    def outputs(self) -> dict[str, Value]:
        """Выходы и статика (без временных) — что сравнивает equiv."""
        out: dict[str, Value] = {}
        for sec in self.block.sections:
            if sec.name in ("Output", "InOut", "Static"):
                for m in sec.members:
                    key = m.name.lower()
                    if key in self.mem.values:
                        out[m.name] = self.mem.values[key]
                    elif key in self.mem.instances:
                        inst = self.mem.instances[key]
                        out[f"{m.name}.Q"] = inst.member("Q")
        return out


class _NetRun:
    def __init__(self, ev: NetEvaluator, net: Network) -> None:
        self.ev = ev
        self.net = net
        self.done: set[int] = set()
        self.outs: dict[tuple[int, str], Value] = {}
        self.jump: str | None = None
        self.ret = False

    def where(self, uid: int) -> str:
        return f"сеть {self.net.number}, UId {uid}"

    def write(self, operand: str, value: Value, uid: int) -> None:
        self.ev.mem.write(operand, value)
        self.ev.trace.writes[operand.lstrip("#").lower()] = self.where(uid)

    def operand(self, uid: int, pin: str = "operand") -> str:
        acc = self.net.operand(uid, pin)
        if acc is None:
            raise EvalError(f"{self.where(uid)}: нет операнда {pin}")
        return acc.text

    def signal(self, uid: int, pin: str, default: Value = None) -> Value:
        """Значение на входе pin элемента uid (с отрицанием Negated)."""
        src = self.net.driver(uid, pin)
        if src is None:
            if default is None:
                raise EvalError(f"{self.where(uid)}: вход {pin} не подключён")
            return default
        if src.kind == RAIL:
            value: Value = True
        elif src.kind == IDENT:
            value = self.ev.mem.read(self.net.accesses[src.uid].text)
        elif src.kind == PIN:
            value = self.output(src.uid, src.pin)
        else:
            raise EvalError(f"{self.where(uid)}: вход {pin} — свободный конец")
        if pin.lower() in self.net.parts[uid].negated:
            value = not value
        return value

    def output(self, uid: int, pin: str) -> Value:
        part = self.net.parts[uid]
        key = (uid, pin.lower())
        if part.name in _PURE:
            if key not in self.outs:
                value = self.pure(uid)
                if pin.lower() in part.negated:
                    value = not value
                self.outs[key] = value
            return self.outs[key]
        self.run_part(uid)
        if key not in self.outs:
            raise EvalError(f"{self.where(uid)}: у {part.name} нет выхода {pin}")
        return self.outs[key]

    def pure(self, uid: int) -> Value:
        p = self.net.parts[uid]
        if p.name == "Contact":
            op = bool(self.ev.mem.read(self.operand(uid)))
            if "operand" in p.negated:
                op = not op
            return bool(self.signal(uid, "in", True)) and op
        if p.name == "Not":
            return not self.signal(uid, "in", True)
        if p.name in ("O", "A", "X"):
            vals = [bool(self.signal(uid, f"in{i}")) for i in range(1, p.card + 1) if self.net.driver(uid, f"in{i}")]
            if p.name == "O":
                return any(vals)
            if p.name == "A":
                return all(vals)
            result = False
            for v in vals:
                result = result != v
            return result
        pre = bool(self.signal(uid, "pre", True))
        if p.name in ("InRange", "OutRange"):
            lo, val, hi = self.signal(uid, "min"), self.signal(uid, "val"), self.signal(uid, "max")
            inside = lo <= val <= hi
            return pre and (inside if p.name == "InRange" else not inside)
        a, b = self.signal(uid, "in1"), self.signal(uid, "in2")
        cmp = {"Eq": a == b, "Ne": a != b, "Gt": a > b, "Ge": a >= b, "Lt": a < b, "Le": a <= b}[p.name]
        return pre and cmp

    # -- элементы с действием -------------------------------------------------------
    def run_part(self, uid: int) -> None:
        if uid in self.done:
            return
        self.done.add(uid)
        p = self.net.parts[uid]
        name = p.name
        if name in ("Coil", "SCoil", "RCoil"):
            rlo = bool(self.signal(uid, "in", True))
            op = self.operand(uid)
            if name == "Coil":
                self.write(op, (not rlo) if "operand" in p.negated else rlo, uid)
            elif rlo:
                self.write(op, name == "SCoil", uid)
            self.outs[(uid, "out")] = rlo
        elif name in ("SR", "RS"):
            op = self.operand(uid)
            if name == "SR":
                if self.signal(uid, "s", False):
                    self.write(op, True, uid)
                if self.signal(uid, "r1", False):
                    self.write(op, False, uid)
            else:
                if self.signal(uid, "r", False):
                    self.write(op, False, uid)
                if self.signal(uid, "s1", False):
                    self.write(op, True, uid)
            self.outs[(uid, "q")] = self.ev.mem.read(op)
            for s in self.net.sinks_of(uid, "q"):
                if s.kind == IDENT:
                    self.write(self.net.accesses[s.uid].text, self.outs[(uid, "q")], uid)
        elif name in ("PBox", "NBox"):
            clk = bool(self.signal(uid, "in", True))
            bit = self.operand(uid, "bit")
            m = bool(self.ev.mem.read(bit))
            self.outs[(uid, "out")] = (clk and not m) if name == "PBox" else (not clk and m)
            self.write(bit, clk, uid)
        elif name in ("PContact", "NContact"):
            rlo = bool(self.signal(uid, "in", True))
            sig = bool(self.ev.mem.read(self.operand(uid)))
            bit = self.operand(uid, "bit")
            m = bool(self.ev.mem.read(bit))
            edge = (sig and not m) if name == "PContact" else (not sig and m)
            self.write(bit, sig, uid)
            self.outs[(uid, "out")] = rlo and edge
        elif name in ("PCoil", "NCoil"):
            rlo = bool(self.signal(uid, "in", True))
            bit = self.operand(uid, "bit")
            m = bool(self.ev.mem.read(bit))
            self.write(self.operand(uid), (rlo and not m) if name == "PCoil" else (not rlo and m), uid)
            self.write(bit, rlo, uid)
            self.outs[(uid, "out")] = rlo
        elif name == "Move":
            en = bool(self.signal(uid, "en", True))
            if en:
                value = self.signal(uid, "in")
                for i in range(1, p.card + 1):
                    self.set_out(uid, f"out{i}", value)
            self.outs[(uid, "eno")] = en
        elif name in ("Add", "Sub", "Mul", "Div", "Mod"):
            self.math(uid)
        elif name == "Convert":
            en = bool(self.signal(uid, "en", True))
            if en:
                self.set_out(uid, "out", self.signal(uid, "in"))
            self.outs[(uid, "eno")] = en
        elif name in ("TON", "TOF", "TP", "CTU", "CTD", "CTUD"):
            self.instance(uid)
        elif name == "Call":
            self.call(uid)
        elif name in ("Jump", "JumpNot"):
            rlo = bool(self.signal(uid, "in", True))
            if rlo == (name == "Jump"):
                self.jump = self.operand(uid)
        elif name == "Return":
            if self.signal(uid, "in", True):
                self.ret = True
        else:
            raise EvalError(f"{self.where(uid)}: элемент «{name}» эталоном не моделируется")

    def set_out(self, uid: int, pin: str, value: Value) -> None:
        """Выход блока: в операнды-приёмники (с разрядностью их типа) и для элементов дальше по сети."""
        targets = [s for s in self.net.sinks_of(uid, pin) if s.kind == IDENT]
        for s in targets:
            self.write(self.net.accesses[s.uid].text, value, uid)
        if targets:
            value = self.ev.mem.read(self.net.accesses[targets[0].uid].text)
        self.outs[(uid, pin.lower())] = value

    def math(self, uid: int) -> None:
        p = self.net.parts[uid]
        en = bool(self.signal(uid, "en", True))
        eno = en
        if en:
            count = p.card if p.name in ("Add", "Mul") else 2
            vals = [self.signal(uid, f"in{i}") for i in range(1, count + 1)]
            typ = (p.templates.get("SrcType") or "").upper()
            if not typ:
                acc = self.net.operand(uid, "out")
                typ = type_key(self.ev.mem.type_of(acc.text)) if acc is not None else "INT"
            if p.name in ("Div", "Mod") and vals[1] == 0:
                eno = False
            else:
                exact = vals[0]
                for v in vals[1:]:
                    if p.name == "Add":
                        exact += v
                    elif p.name == "Sub":
                        exact -= v
                    elif p.name == "Mul":
                        exact *= v
                    elif p.name == "Div":
                        exact = int(exact / v) if isinstance(exact, int) else exact / v
                    else:
                        exact = exact - int(exact / v) * v
                lo, hi = _INT_LIMITS.get(typ, (None, None))
                if lo is not None and not lo <= exact <= hi:
                    eno = False
                self.set_out(uid, "out", wrap(exact, typ) if lo is not None else exact)
        self.outs[(uid, "eno")] = eno

    def instance(self, uid: int) -> None:
        p = self.net.parts[uid]
        key = p.instance.lstrip("#").strip('"').lower()
        inst = self.ev.mem.instances.get(key)
        if inst is None:
            raise EvalError(f"{self.where(uid)}: экземпляр {p.instance} не найден")
        pins: tuple[str, ...]
        if isinstance(inst, Timer):
            inst.call(self.ev.now, bool(self.signal(uid, "IN", False)), int(self.signal(uid, "PT", 0)))
            pins = ("Q", "ET")
        else:
            args = {pin: self.signal(uid, pin, False) for pin in ("CU", "CD", "R", "LD") if self.net.driver(uid, pin)}
            if self.net.driver(uid, "PV"):
                args["PV"] = self.signal(uid, "PV")
            inst.call(args)
            pins = ("QU", "QD", "CV") if p.name == "CTUD" else ("Q", "CV")
        for pin in pins:
            self.set_out(uid, pin, inst.member(pin))

    def call(self, uid: int) -> None:
        p = self.net.parts[uid]
        info = p.call
        assert info is not None
        en = bool(self.signal(uid, "en", True))
        self.outs[(uid, "eno")] = en
        if not en:
            return
        callee = self.ev.registry.get(info.name.lower())
        if callee is None or callee.kind != "FC":
            raise EvalError(f"{self.where(uid)}: вызов {info.name} эталоном не моделируется (нужен FC LAD во входе)")
        sub = NetEvaluator(callee, self.ev.registry)
        args = {n: self.signal(uid, n) for n, section, _t in info.params if section in ("Input", "InOut")}
        sub.call(args, self.ev.now)
        for name, section, _t in info.params:
            if section == "Return":
                self.set_out(uid, name, sub.read("Ret_Val"))
            elif section in ("Output", "InOut"):
                self.set_out(uid, name, sub.read(name))

    def execute(self) -> str | None:
        """Сеть целиком; результат — метка прыжка, "RET" или None."""
        for uid, part in self.net.parts.items():
            if part.name not in _PURE:
                self.run_part(uid)
            if self.ret:
                return "RET"
        return self.jump


__all__ = ["UNDEF", "Counter", "EvalError", "NetEvaluator", "Trace"]
