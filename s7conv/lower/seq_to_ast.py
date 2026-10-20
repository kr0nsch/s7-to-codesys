"""S7-GRAPH (SeqIR) → ST-двойник: последовательность как флаги шагов в синтезированном SCL.

ST-двойник строится всегда: на нём работают интерпретатор ST, RuSTy, iec_checker и сценарии со временем;
вариант SFC (PLCopen XML, s7conv/plcopen/sfc.py) строится из того же SeqIR. Модель цикла одного вызова
(docs/ASSUMPTIONS.md, записи L18–L22; эталон — s7conv/semantics/graph_seq.py):

1. INIT_SQ (и первый вызов) — активны начальные шаги, ошибки сброшены; OFF_SQ — все шаги выключены; в этом
   вызове переходы не срабатывают, события S1/S0 считаются и от INIT_SQ/OFF_SQ;
2. ACK_EF — квитирование: защёлки ошибок контроля сброшены (в цикле квитирования переход возможен);
3. время активных шагов `<Шаг>_T` — от момента активации по F_S7Now();
4. условия переходов — по состоянию шагов прошлого вызова; переход срабатывает, если активны все
   шаги-предшественники, условие истинно и у них нет ошибки контроля; у альтернатив — первый слева;
5. переключение: предшественники выключаются, преемники включаются; события S1 (активирован) и S0
   (выключен) — по сравнению с прошлым вызовом;
6. контроль (`Supervision`) активных шагов защёлкивает ошибку (ERR_FLT), блокировка (`Interlock`) — условие C;
7. действия шагов по порядку: N (пока активен, при выключении — 0), S/R (каждый цикл активности),
   D/L (по времени шага), инструкции SCL; с событием S1/S0 — один раз;
8. постоперации.

Ссылки на шаг в условиях и инструкциях (`#Шаг.X`, `#Шаг.T`) — статические `#Шаг_X`, `#Шаг_T`.
"""

from __future__ import annotations

import re
from collections.abc import Callable

from s7conv.frontends.simaticml import XUnit
from s7conv.ir.net import build_network
from s7conv.ir.seq import SeqStep, parse_graph, topology
from s7conv.lower.common import AUTO, CHECK, TODO, BlockLower, LLine, worst
from s7conv.lower.net_to_ast import PARTS, NetLowerer
from s7conv.nodes import LowerNote

_STATIC_STEP_FIELDS = ("X", "T")
_SUPPORTED_EVENTS = ("", "S1", "S0")
_SYSTEM_INPUTS = {"INIT_SQ", "OFF_SQ", "ACK_EF"}
_SYSTEM_OUTPUTS = {"ERR_FLT"}
_UNSUPPORTED_SYSTEM = {
    "SW_AUTO",
    "SW_TAP",
    "SW_TOP",
    "SW_MAN",
    "S_SEL",
    "S_ON",
    "S_OFF",
    "S_PREV",
    "S_NEXT",
    "T_PUSH",
    "S_NO",
    "S_MORE",
    "S_ACTIVE",
    "AUTO_ON",
    "TAP_ON",
    "TOP_ON",
    "MAN_ON",
    "EN_ACKREQ",
    "REG_EF",
    "REG_S",
    "HALT_SQ",
    "HALT_TM",
    "ZERO_OP",
    "EN_IL",
    "EN_SV",
}


# Чистые элементы условия (входят в выражение катушки); остальные элементы сети выводятся операторами
_PURE = ("Contact", "Not", "O", "A", "X", "Eq", "Ne", "Gt", "Ge", "Lt", "Le")


def _ident(step: SeqStep) -> str:
    return step.name if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", step.name) else f"S{step.number}"


def _static_ref(name: str) -> Callable[[re.Match[str]], str]:
    """Замена `#Шаг.X` / `#Шаг.T` статической переменной двойника `#Шаг_X` / `#Шаг_T`."""

    def repl(m: re.Match[str]) -> str:
        return f"#{name}_{m.group(1).upper()}"

    return repl


def _net_status(lowerer: NetLowerer, default_rule: str) -> tuple[str, str]:
    """Тяжелейший статус элементов сети условия или пред-/постоперации и его правило; элемент уровня L
    (форма XML не подтверждена экспортом) — не выше check, как в сетях LAD/FBD."""
    result = (AUTO, default_rule)
    for uid, part in lowerer.net.parts.items():
        entry = PARTS.get(part.name)
        status, rule = lowerer.status.get(uid, (AUTO, lowerer.rule(entry.rule) if entry else default_rule))
        if entry is not None and entry.level == "L" and status == AUTO:
            status, rule = CHECK, lowerer.rule("vocab_unverified")
        if worst(result[0], status) != result[0]:
            result = (status, rule)
    return result


class GraphLowerer:
    def __init__(self, bl: BlockLower, unit: XUnit) -> None:
        self.bl = bl
        self.unit = unit
        self.trace0 = f"сеть {unit.number} (GRAPH)"
        self.names: dict[int, str] = {}
        self.step_status: dict[int, tuple[str, str]] = {}
        self.trans_status: dict[int, tuple[str, str]] = {}

    # -- служебное -------------------------------------------------------------------
    def emit(self, text: str, trace: str | None = None, notes: list[LowerNote] | None = None) -> None:
        self.bl.lines.append(LLine(text, trace or self.trace0, notes or []))

    def mark(self, step: int, status: str, rule: str) -> None:
        old = self.step_status.get(step)
        if old is None or worst(old[0], status) != old[0]:
            self.step_status[step] = (status, rule)

    def rewrite(self, text: str) -> str:
        """`#Шаг.X` / `#Шаг.T` → `#Шаг_X` / `#Шаг_T` (состояние шага в статических переменных)."""
        for name in self.names.values():
            text = re.sub(rf'#"?{re.escape(name)}"?\.(X|T)\b', _static_ref(name), text)
        return text

    def lower_condition(self, flgnet: object, target: str, trace: str, lang: str = "LAD") -> tuple[str, str]:
        """Сеть условия → `target := выражение;`; возвращает тяжелейший статус элементов сети и его правило
        (элемент уровня L — катушки TrCoil/SvCoil/IlCoil — не выше check, как в сетях LAD/FBD)."""
        net = build_network(flgnet, 0, lang)  # type: ignore[arg-type]
        for acc in net.accesses.values():
            acc.text = self.rewrite(acc.text)
        lowerer = NetLowerer(self.bl, net)
        lowerer.cond_target = target
        for uid, part in net.parts.items():
            if part.name not in _PURE:
                lowerer.emit_part(uid)
        for line in lowerer.lines:
            self.bl.lines.append(LLine(line.text, f"{trace}, {line.trace.split(', ', 1)[-1]}", line.notes))
        if not any(p.name in ("TrCoil", "SvCoil", "IlCoil") for p in net.parts.values()):
            note = LowerNote(TODO, "graph.condition_missing", f"{trace}: в сети нет катушки условия")
            self.emit(f"{target} := FALSE;", trace, [note])
            return TODO, "graph.condition_missing"
        return _net_status(lowerer, "graph.transition")

    # -- блок ------------------------------------------------------------------------
    def run(self) -> None:
        assert self.unit.body is not None
        graph = parse_graph(self.unit.body)
        blk = self.bl.block
        members = {m.name.upper() for s in blk.sections for m in s.members}
        if len(graph.sequences) != 1:
            note = LowerNote(TODO, "graph.sequences", f"последовательностей {len(graph.sequences)}: переводится одна")
            self.emit("// GRAPH: последовательностей больше одной", None, [note])
        if not graph.sequences:
            return
        seq = graph.sequences[0]
        topo = topology(seq)
        self.names = {s.number: _ident(s) for s in seq.steps}
        block_notes = [
            LowerNote(
                CHECK,
                "graph.cycle_order",
                "GRAPH → ST-двойник: переходы — по состоянию прошлого вызова, затем действия активных шагов в том "
                "же вызове; порядок цикла GRAPH S7-1500 сверить (docs/ASSUMPTIONS.md, запись L18)",
            )
        ]
        unsupported = sorted(members & _UNSUPPORTED_SYSTEM)
        if unsupported:
            block_notes.append(
                LowerNote(
                    TODO,
                    "graph.mode_unsupported",
                    f"параметры GRAPH {', '.join(unsupported)} (режимы, ручной выбор шагов) не переводятся",
                )
            )
        for issue in topo.issues:
            block_notes.append(LowerNote(TODO, "graph.topology", issue))
        bl = self.bl
        now = bl.temp("tGraphNow", "Time", "GRAPH: время вызова (F_S7Now)")
        init_done = bl.static("GraphInitDone", "Bool", "GRAPH: начальное состояние установлено")
        x: dict[int, str] = {}
        t: dict[int, str] = {}
        start: dict[int, str] = {}
        prev: dict[int, str] = {}
        s1: dict[int, str] = {}
        s0: dict[int, str] = {}
        sv_err: dict[int, str] = {}
        il: dict[int, str] = {}
        for st in seq.steps:
            name = self.names[st.number]
            x[st.number] = bl.static(f"{name}_X", "Bool", f"шаг S{st.number} {st.name} активен")
            t[st.number] = bl.static(f"{name}_T", "Time", f"шаг S{st.number}: время активности (последней)")
            start[st.number] = bl.static(f"{name}_Start", "Time", f"шаг S{st.number}: момент активации")
            if st.supervision is not None:
                sv_err[st.number] = bl.static(f"{name}_SvErr", "Bool", f"шаг S{st.number}: ошибка контроля")
        for st in seq.steps:
            name = self.names[st.number]
            prev[st.number] = bl.temp(f"x{name}_Prev", "Bool", f"шаг S{st.number}: активен в прошлом вызове")
            s1[st.number] = bl.temp(f"x{name}_S1", "Bool", f"шаг S{st.number}: событие S1 (активирован)")
            s0[st.number] = bl.temp(f"x{name}_S0", "Bool", f"шаг S{st.number}: событие S0 (выключен)")
            if st.interlock is not None:
                il[st.number] = bl.temp(f"x{name}_Il", "Bool", f"шаг S{st.number}: блокировка выполнена")
        trace = self.trace0
        self.emit(f"// Сеть {self.unit.number} (GRAPH): {self.unit.title or 'последовательность'}", trace, block_notes)
        self.emit(f"{now} := S7_NOW();", trace)
        for k, (net, lang) in enumerate(graph.pre, start=1):
            self.emit(f"// Предоперация {k}", f"{trace}, предоперация {k}")
            self.lower_plain(net, lang, f"{trace}, предоперация {k}")
        # 1. состояние прошлого вызова (для событий S1/S0), начальное состояние и выключение
        self.emit("// Состояние шагов прошлого вызова: события S1/S0 — и от INIT_SQ, OFF_SQ", trace)
        for st in seq.steps:
            self.emit(f"{prev[st.number]} := {x[st.number]};", f"{trace}, шаг S{st.number}")
        init_cond = f"#INIT_SQ OR NOT {init_done}" if "INIT_SQ" in members else f"NOT {init_done}"
        hold = bl.temp("xGraphHold", "Bool", "GRAPH: INIT_SQ, OFF_SQ или первый вызов — переходы не срабатывают")
        hold_cond = f"{init_cond} OR #OFF_SQ" if "OFF_SQ" in members else init_cond
        self.emit(f"{hold} := {hold_cond};", trace)
        self.emit("// Начальное состояние (INIT_SQ, первый вызов) и выключение (OFF_SQ)", trace)
        self.emit(f"IF {init_cond} THEN", trace)
        self.emit(f"   {init_done} := TRUE;", trace)
        for st in seq.steps:
            self.emit(f"   {x[st.number]} := {'TRUE' if st.init else 'FALSE'};", f"{trace}, шаг S{st.number}")
            if st.init:
                self.emit(f"   {start[st.number]} := {now};", f"{trace}, шаг S{st.number}")
                self.emit(f"   {t[st.number]} := T#0MS;", f"{trace}, шаг S{st.number}")
        for n, var in sv_err.items():
            self.emit(f"   {var} := FALSE;", f"{trace}, шаг S{n}")
        self.emit("END_IF;", trace)
        if "OFF_SQ" in members:
            self.emit("IF #OFF_SQ THEN", trace)
            for st in seq.steps:
                self.emit(f"   {x[st.number]} := FALSE;", f"{trace}, шаг S{st.number}")
            self.emit("END_IF;", trace)
        # 2. квитирование
        if sv_err and "ACK_EF" in members:
            self.emit("// Квитирование ошибок контроля (ACK_EF): в этом вызове переход возможен", trace)
            self.emit("IF #ACK_EF THEN", trace)
            for n, var in sv_err.items():
                self.emit(f"   {var} := FALSE;", f"{trace}, шаг S{n}")
            self.emit("END_IF;", trace)
        elif sv_err:
            note = LowerNote(CHECK, "graph.supervision", "контроль без входа ACK_EF: ошибка не квитируется")
            self.emit("// контроль шагов без квитирования", trace, [note])
        # 3. время шагов
        self.emit("// Время активных шагов", trace)
        for st in seq.steps:
            n = st.number
            self.emit(f"IF {x[n]} THEN", f"{trace}, шаг S{n}")
            self.emit(f"   {t[n]} := S7_TIMEDIFF({now}, {start[n]});", f"{trace}, шаг S{n}")
            self.emit("END_IF;", f"{trace}, шаг S{n}")
        # 4. переходы
        cond: dict[int, str] = {}
        fire: dict[int, str] = {}
        for link in topo.links:
            tr = seq.transition(link.number)
            cond[link.number] = bl.temp(f"xT{link.number}_Cond", "Bool", f"переход T{link.number} {tr.name}: условие")
            fire[link.number] = bl.temp(f"xT{link.number}_Fire", "Bool", f"переход T{link.number}: срабатывает")
        self.emit("// Условия переходов (сети LAD/FBD)", trace)
        for link in topo.links:
            tr = seq.transition(link.number)
            where = f"{trace}, переход T{link.number}"
            if tr.net is None:
                note = LowerNote(TODO, "graph.condition_missing", f"T{link.number} {tr.name}: нет сети условия")
                self.emit(f"{cond[link.number]} := FALSE;", where, [note])
                continue
            self.trans_status[link.number] = self.lower_condition(tr.net, cond[link.number], where, tr.lang)
        self.emit(
            "// Срабатывание: предшественники активны, условие, нет ошибки контроля; альтернативы — слева направо",
            trace,
        )
        alt_notes: list[LowerNote] = []
        taken: dict[int, list[str]] = {}
        for link in topo.links:
            n = link.number
            parts = [x[p] for p in link.preds] + [cond[n], f"NOT {hold}"]
            parts += [f"NOT {sv_err[p]}" for p in link.preds if p in sv_err]
            earlier = [f for p in link.preds for f in taken.get(p, [])]
            parts += [f"NOT {f}" for f in earlier]
            if earlier and not alt_notes:
                alt_notes.append(
                    LowerNote(
                        CHECK,
                        "graph.alt_priority",
                        "альтернативная ветвь: из одновременно истинных переходов срабатывает левый (первый); "
                        "настройку блока S7-1500 сверить",
                    )
                )
            self.emit(f"{fire[n]} := {' AND '.join(parts)};", f"{trace}, переход T{n}", alt_notes if earlier else [])
            for p in link.preds:
                taken.setdefault(p, []).append(fire[n])
        # 5. переключение и события
        self.emit("// Переключение: сначала выключение предшественников, затем включение преемников", trace)
        for link in topo.links:
            if link.preds:
                self.emit(f"IF {fire[link.number]} THEN", f"{trace}, переход T{link.number}")
                for p in link.preds:
                    self.emit(f"   {x[p]} := FALSE;", f"{trace}, переход T{link.number}")
                self.emit("END_IF;", f"{trace}, переход T{link.number}")
        for link in topo.links:
            if link.succs:
                self.emit(f"IF {fire[link.number]} THEN", f"{trace}, переход T{link.number}")
                for sc in link.succs:
                    self.emit(f"   {x[sc]} := TRUE;", f"{trace}, переход T{link.number}")
                self.emit("END_IF;", f"{trace}, переход T{link.number}")
        self.emit("// События шагов S1/S0; активация — новый отсчёт времени", trace)
        for st in seq.steps:
            n = st.number
            self.emit(f"{s1[n]} := {x[n]} AND NOT {prev[n]};", f"{trace}, шаг S{n}")
            self.emit(f"{s0[n]} := {prev[n]} AND NOT {x[n]};", f"{trace}, шаг S{n}")
            self.emit(f"IF {s1[n]} THEN", f"{trace}, шаг S{n}")
            self.emit(f"   {start[n]} := {now};", f"{trace}, шаг S{n}")
            self.emit(f"   {t[n]} := T#0MS;", f"{trace}, шаг S{n}")
            self.emit("END_IF;", f"{trace}, шаг S{n}")
        # 6. контроль и блокировка
        for st in seq.steps:
            n = st.number
            if st.max_time or st.warn_time:
                limits = ", ".join(
                    f"{k} {v}" for k, v in (("MaximumStepTime", st.max_time), ("WarningTime", st.warn_time)) if v
                )
                note = LowerNote(TODO, "graph.step_time_limits", f"S{n}: {limits} — предел времени шага не переводится")
                self.emit(f"// S{n} {st.name}: {limits} не переведено", f"{trace}, шаг S{n}", [note])
                self.mark(n, TODO, "graph.step_time_limits")
            if st.supervision is not None:
                sv = bl.temp(f"x{self.names[n]}_Sv", "Bool", f"шаг S{n}: условие контроля")
                where = f"{trace}, шаг S{n}, контроль"
                self.emit(f"// Контроль шага S{n} {st.name}", where)
                sv_status = self.lower_condition(st.supervision, sv, where)
                note = LowerNote(
                    CHECK,
                    "graph.supervision",
                    f"контроль S{n}: ошибка защёлкивается и держит шаг до ACK_EF; Si.U и сообщения ProDiag не "
                    "переносятся",
                )
                self.emit(f"IF {x[n]} AND {sv} THEN", where, [note])
                self.emit(f"   {sv_err[n]} := TRUE;", where)
                self.emit("END_IF;", where)
                self.mark(n, CHECK, "graph.supervision")
                self.mark(n, *sv_status)
            if st.interlock is not None:
                where = f"{trace}, шаг S{n}, блокировка"
                self.emit(f"// Блокировка шага S{n} {st.name}", where)
                self.mark(n, *self.lower_condition(st.interlock, il[n], where))
        # 7. действия
        for st in seq.steps:
            self.lower_actions(st, x[st.number], t[st.number], s1[st.number], s0[st.number], il.get(st.number))
        if sv_err and "ERR_FLT" in members:
            self.emit(f"#ERR_FLT := {' OR '.join(sv_err.values())};", f"{trace}, ERR_FLT")
        for k, (net, lang) in enumerate(graph.post, start=1):
            self.emit(f"// Постоперация {k}", f"{trace}, постоперация {k}")
            self.lower_plain(net, lang, f"{trace}, постоперация {k}")
        # единицы учёта: шаг — тяжелейшее из правил его действий, контроля и блокировки
        for st in seq.steps:
            status, rule = self.step_status.get(st.number, (AUTO, "graph.step"))
            self.bl.unit("step", status, rule, f"{trace}, шаг S{st.number}")
        for link in topo.links:
            status, rule = self.trans_status.get(link.number, (TODO, "graph.condition_missing"))
            self.bl.unit("transition", status, rule, f"{trace}, переход T{link.number}")

    def lower_plain(self, flgnet: object, lang: str, trace: str) -> None:
        net = build_network(flgnet, 0, lang)  # type: ignore[arg-type]
        for acc in net.accesses.values():
            acc.text = self.rewrite(acc.text)
        lowerer = NetLowerer(self.bl, net)
        for uid, part in net.parts.items():
            if part.name not in _PURE:
                lowerer.emit_part(uid)
        for line in lowerer.lines:
            self.bl.lines.append(LLine(line.text, f"{trace}, {line.trace.split(', ', 1)[-1]}", line.notes))
        self.bl.unit("network", *_net_status(lowerer, lowerer.rule("network")), trace)

    def lower_actions(self, st: SeqStep, x: str, t: str, s1: str, s0: str, il: str | None) -> None:
        n = st.number
        if not st.actions:
            return
        self.emit(f"// Действия шага S{n} {st.name}", f"{self.trace0}, шаг S{n}")
        for a in st.actions:
            where = f"{self.trace0}, шаг S{n}, действие {a.index}"
            q = a.qualifier.upper()
            ilk = f" AND {il}" if a.interlock and il is not None else ""
            notes: list[LowerNote] = []
            if a.interlock and il is None:
                notes.append(LowerNote(CHECK, "graph.interlock", f"S{n}: действие с C, а условия блокировки нет"))
            if a.event not in _SUPPORTED_EVENTS:
                note = LowerNote(TODO, "graph.event_unsupported", f"S{n}: событие {a.event} не переводится")
                self.emit(f'"GRAPH_ACTION"(); // {a.event} {q} {a.text}', where, [note])
                self.mark(n, TODO, "graph.event_unsupported")
                continue
            text = self.rewrite(a.text)
            operand = self.rewrite(a.operand) if a.operand else ""
            if a.event:
                event = s1 if a.event == "S1" else s0
                ilk_event = ilk if a.event == "S1" else ""
                body = self._event_body(q, operand, text)
                if body is None:
                    note = LowerNote(TODO, "graph.action_unsupported", f"S{n}: {a.event} {q} {a.text} не переводится")
                    self.emit(f'"GRAPH_ACTION"(); // {a.event} {q} {a.text}', where, [note])
                    self.mark(n, TODO, "graph.action_unsupported")
                    continue
                self.emit(f"IF {event}{ilk_event} THEN", where, notes)
                self.emit(f"   {body}", where)
                self.emit("END_IF;", where)
                self.mark(n, AUTO, "graph.event")
                continue
            if q == "N" and operand:
                self.emit(f"IF {x} OR {s0} THEN", where, notes)
                self.emit(f"   {operand} := {x}{ilk};", where)
                self.emit("END_IF;", where)
                self.mark(n, AUTO, "graph.action_n")
            elif q == "N":
                self.emit(f"IF {x}{ilk} THEN", where, notes)
                self.emit(f"   {text if text.rstrip().endswith(';') else text + ';'}", where)
                self.emit("END_IF;", where)
                self.mark(n, AUTO, "graph.action_n")
            elif q in ("S", "R") and operand:
                self.emit(f"IF {x}{ilk} THEN", where, notes)
                self.emit(f"   {operand} := {'TRUE' if q == 'S' else 'FALSE'};", where)
                self.emit("END_IF;", where)
                self.mark(n, AUTO, "graph.action_sr")
            elif q in ("D", "L") and operand and a.time:
                op = ">=" if q == "D" else "<"
                note = LowerNote(
                    CHECK,
                    "graph.timer_clock",
                    f"S{n}: {q} {operand}, {a.time} — по времени шага {t} (F_S7Now); в SFC — IEC {q} по своему таймеру",
                )
                self.emit(f"IF {x} OR {s0} THEN", where, [*notes, note])
                self.emit(f"   {operand} := {x} AND ({t} {op} {a.time}){ilk};", where)
                self.emit("END_IF;", where)
                self.mark(n, CHECK, "graph.timer_clock")
            else:
                note = LowerNote(TODO, "graph.action_unsupported", f"S{n}: действие {q} {a.text} не переводится")
                self.emit(f'"GRAPH_ACTION"(); // {q} {a.text}', where, [note])
                self.mark(n, TODO, "graph.action_unsupported")

    @staticmethod
    def _event_body(q: str, operand: str, text: str) -> str | None:
        """Действие по событию S1/S0 — один раз в цикле события."""
        if q == "N" and operand:
            return None  # «один раз 1» на операнде — импульс на цикл: не переводится (graph.action_unsupported)
        if q == "N":
            return text if text.rstrip().endswith(";") else text + ";"
        if q in ("S", "R") and operand:
            return f"{operand} := {'TRUE' if q == 'S' else 'FALSE'};"
        return None


def lower_graph(bl: BlockLower, unit: XUnit) -> None:
    GraphLowerer(bl, unit).run()


__all__ = ["GraphLowerer", "lower_graph"]
