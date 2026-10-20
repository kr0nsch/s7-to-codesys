"""LAD/FBD (NetIR) → SCL: поток питания по правилам S7, ветви — OR, последовательно — AND.

Алгоритм (docs/ARCHITECTURE.md, «Все языки»): элементы с действием (катушки, блоки, вызовы, фронты)
выводятся операторами в порядке XML с подтягиванием зависимостей — так сохраняется порядок S7 «сверху
вниз, слева направо»; логика контактов встраивается в выражение оператора-приёмника, общий участок
(выход с несколькими приёмниками) вычисляется один раз во временную `xNet<N>_<k>`.

Ловушки S7 (R§5.2) переводятся явно: SR/RS с битом-операндом — двумя IF в порядке S7 (SR — сброс
последним), фронты — явным битом памяти (`q := clk AND NOT m; m := clk;`), ENO арифметики — функцией
S7Compat `F_S7Eno<Оп><Тип>`, вычисленной до записи результата.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from s7conv.ir.net import IDENT, PIN, RAIL, End, Network, NPart
from s7conv.lower.common import (
    AUTO,
    CHECK,
    FALSE,
    TODO,
    TRUE,
    BlockLower,
    Ex,
    LLine,
    and_,
    arith,
    atom,
    cmp_,
    indent,
    is_simple,
    not_,
    or_,
    worst,
    xor_,
)
from s7conv.nodes import LowerNote


@dataclass(frozen=True)
class PartRule:
    """Строка словаря Part: правило, что это, уровень подтверждения формы XML и откуда она взята."""

    rule: str
    title: str
    level: str  # H — имя и пины есть в открытом экспорте; L — по руководству, экспорта нет
    source: str


_COOKBOOK = "lad-cookbook @ e131b25"
# Словарь элементов: имя Part → правило (docs/MAPPING_LADFBD.md). Правило уровня L — не выше check.
PARTS: dict[str, PartRule] = {
    "Contact": PartRule("contact", "контакт (Negated — размыкающий)", "H", f"{_COOKBOOK}: MCPVerify_FB_LAD_v3.xml"),
    "Coil": PartRule("coil", "катушка (Negated operand — отрицающая)", "H", f"{_COOKBOOK}: MCPVerify_FB_LAD_v3.xml"),
    "SCoil": PartRule("set_reset", "катушка S", "H", f"{_COOKBOOK}: MCPVerify_FC_LAD.xml"),
    "RCoil": PartRule("set_reset", "катушка R", "H", f"{_COOKBOOK}: MCPVerify_FC_LAD.xml"),
    "Not": PartRule("contact", "NOT (инверсия RLO)", "H", f"{_COOKBOOK}: MCPVerify_FB_LAD_v3.xml"),
    "O": PartRule("contact", "слияние ветвей / OR", "H", f"{_COOKBOOK}: MCPVerify_FC_LAD.xml"),
    "A": PartRule("contact", "AND (FBD)", "L", "s7kop/FBD: блок AND; имя Part «A» — по аналогии с «O»"),
    "X": PartRule("contact", "XOR (FBD)", "L", "блок XOR; имя Part «X» — по аналогии с «O»"),
    "PBox": PartRule("edge", "P_TRIG: фронт RLO, бит памяти bit", "H", f"{_COOKBOOK}: MCPVerify_FB_LAD_v3.xml"),
    "NBox": PartRule("edge", "N_TRIG: спад RLO, бит памяти bit", "L", "по аналогии с PBox"),
    "PContact": PartRule("edge", "контакт P: фронт операнда, бит памяти bit", "L", "s7kop__b.pdf, §1.17"),
    "NContact": PartRule("edge", "контакт N: спад операнда, бит памяти bit", "L", "s7kop__b.pdf, §1.18"),
    "PCoil": PartRule("edge", "катушка P: импульс по фронту RLO", "L", "справка TIA, «-(P)-»"),
    "NCoil": PartRule("edge", "катушка N: импульс по спаду RLO", "L", "справка TIA, «-(N)-»"),
    "SR": PartRule("sr_operand", "SR с битом-операндом: сброс главнее", "L", "s7kop__b.pdf, §1.10"),
    "RS": PartRule("sr_operand", "RS с битом-операндом: установка главнее", "L", "s7kop__b.pdf, §1.11"),
    "Eq": PartRule("compare", "сравнение ==", "H", f"{_COOKBOOK}: MCPVerify_FC_LAD_v2.xml"),
    "Ne": PartRule("compare", "сравнение <>", "H", f"{_COOKBOOK}: MCPVerify_FC_LAD_v2.xml"),
    "Gt": PartRule("compare", "сравнение >", "H", f"{_COOKBOOK}: MCPVerify_FC_LAD.xml"),
    "Ge": PartRule("compare", "сравнение >=", "H", f"{_COOKBOOK}: MCPVerify_FC_LAD_v2.xml"),
    "Lt": PartRule("compare", "сравнение <", "H", f"{_COOKBOOK}: MCPVerify_FB_LAD_v3.xml"),
    "Le": PartRule("compare", "сравнение <=", "H", f"{_COOKBOOK}: MCPVerify_FC_LAD_v2.xml"),
    "InRange": PartRule("compare", "IN_RANGE", "L", "справка TIA, IN_RANGE"),
    "OutRange": PartRule("compare", "OUT_RANGE", "L", "справка TIA, OUT_RANGE"),
    "Move": PartRule("move", "MOVE (en, in, out1…outN)", "H", f"{_COOKBOOK}: MCPVerify_FC_LAD.xml"),
    "Add": PartRule("math", "ADD", "H", f"{_COOKBOOK}: MCPVerify_FC_LAD.xml"),
    "Sub": PartRule("math", "SUB", "H", f"{_COOKBOOK}: MCPVerify_FC_LAD_v2.xml"),
    "Mul": PartRule("math", "MUL", "H", f"{_COOKBOOK}: MCPVerify_FC_LAD_v2.xml"),
    "Div": PartRule("math", "DIV", "H", f"{_COOKBOOK}: MCPVerify_FC_LAD_v2.xml"),
    "Mod": PartRule("math", "MOD", "H", f"{_COOKBOOK}: MCPVerify_FC_LAD_v2.xml"),
    "Neg": PartRule("math", "NEG", "L", "справка TIA, NEG"),
    "Abs": PartRule("math", "ABS", "L", "справка TIA, ABS"),
    "Convert": PartRule("convert", "CONVERT (SrcType → DestType)", "H", f"{_COOKBOOK}: MCPVerify_FC_LAD_v2.xml"),
    "Round": PartRule("convert", "ROUND", "L", "справка TIA, ROUND"),
    "Trunc": PartRule("convert", "TRUNC", "L", "справка TIA, TRUNC"),
    "Calculate": PartRule("calculate", "CALCULATE (Equation)", "L", "XSD LADFBD_v5: Equation — только для Calculate"),
    "Limit": PartRule("instruction", "LIMIT", "L", "справка TIA, LIMIT"),
    "Min": PartRule("instruction", "MIN", "L", "справка TIA, MIN"),
    "Max": PartRule("instruction", "MAX", "L", "справка TIA, MAX"),
    "Sel": PartRule("instruction", "SEL", "L", "справка TIA, SEL"),
    "NormX": PartRule("instruction", "NORM_X", "L", "справка TIA, NORM_X"),
    "ScaleX": PartRule("instruction", "SCALE_X", "L", "справка TIA, SCALE_X"),
    "Shl": PartRule("instruction", "SHL", "L", "справка TIA, SHL"),
    "Shr": PartRule("instruction", "SHR", "L", "справка TIA, SHR"),
    "And": PartRule("instruction", "AND слов", "L", "справка TIA, AND"),
    "Or": PartRule("instruction", "OR слов", "L", "справка TIA, OR"),
    "Xor": PartRule("instruction", "XOR слов", "L", "справка TIA, XOR"),
    "TON": PartRule("timer", "TON (экземпляр)", "H", f"{_COOKBOOK}: MCPVerify_FB_LAD_v3.xml"),
    "TOF": PartRule("timer", "TOF (экземпляр)", "L", "по аналогии с TON"),
    "TP": PartRule("timer", "TP (экземпляр)", "L", "по аналогии с TON"),
    "CTU": PartRule("counter", "CTU (экземпляр)", "L", "справка TIA, CTU"),
    "CTD": PartRule("counter", "CTD (экземпляр)", "L", "справка TIA, CTD"),
    "CTUD": PartRule("counter", "CTUD (экземпляр)", "L", "справка TIA, CTUD"),
    "Call": PartRule("call", "вызов FB/FC (EN/ENO)", "L", "XSD LADFBD_v5: Call/CallInfo; экспорта нет"),
    "Jump": PartRule("jump", "прыжок JMP к метке", "L", "XSD LADFBD_v5: Labels; экспорта нет"),
    "JumpNot": PartRule("jump", "прыжок JMPN к метке", "L", "XSD LADFBD_v5: Labels; экспорта нет"),
    "Return": PartRule("return", "RET", "L", "справка TIA, RET"),
    # GRAPH: катушки условий (переход, контроль, блокировка). Имена — по описанию формата GRAPH в открытых
    # образцах без лицензии (не используются): уровень L, docs/ASSUMPTIONS.md, запись L17
    "TrCoil": PartRule("graph_condition", "катушка условия перехода GRAPH", "L", "образцы GRAPH без лицензии"),
    "SvCoil": PartRule("graph_condition", "катушка контроля шага GRAPH", "L", "образцы GRAPH без лицензии"),
    "IlCoil": PartRule("graph_condition", "катушка блокировки шага GRAPH", "L", "образцы GRAPH без лицензии"),
}
COMBINATIONAL = frozenset({"Contact", "Not", "O", "A", "X", "Eq", "Ne", "Gt", "Ge", "Lt", "Le", "InRange", "OutRange"})
_COMPARE = {"Eq": "=", "Ne": "<>", "Gt": ">", "Ge": ">=", "Lt": "<", "Le": "<="}
_MATH = {"Add": "+", "Sub": "-", "Mul": "*", "Div": "/", "Mod": "MOD"}
_ENO_FUNCS = {("Add", "INT"), ("Sub", "INT"), ("Mul", "INT"), ("Add", "DINT"), ("Sub", "DINT"), ("Mul", "DINT")}
# Инструкция-блок → (функция SCL, [(пин, параметр)], выход)
_INSTR: dict[str, tuple[str, tuple[tuple[str, str], ...]]] = {
    "Limit": ("LIMIT", (("mn", "MN"), ("in", "IN"), ("mx", "MX"))),
    "Sel": ("SEL", (("g", "G"), ("in0", "IN0"), ("in1", "IN1"))),
    "NormX": ("NORM_X", (("min", "MIN"), ("value", "VALUE"), ("max", "MAX"))),
    "ScaleX": ("SCALE_X", (("min", "MIN"), ("value", "VALUE"), ("max", "MAX"))),
    "Shl": ("SHL", (("in", "IN"), ("n", "N"))),
    "Shr": ("SHR", (("in", "IN"), ("n", "N"))),
}
_TIMER_PINS = ("IN", "PT")
_COUNTER_PINS = {"CTU": ("CU", "R", "PV"), "CTD": ("CD", "LD", "PV"), "CTUD": ("CU", "CD", "R", "LD", "PV")}
_INT_TYPES = {"INT", "DINT", "SINT", "USINT", "UINT", "UDINT", "LINT", "ULINT"}


class NetLowerer:
    """Одна сеть LAD/FBD → строки SCL; выход прыжка — (метка, временная RLO, прыжок при FALSE)."""

    def __init__(self, bl: BlockLower, net: Network) -> None:
        self.bl = bl
        self.net = net
        self.prefix = "fbd" if net.lang.upper().startswith("FBD") else "lad"
        self.memo: dict[tuple[int, str], Ex] = {}
        self.emitted: set[int] = set()
        self.active: set[int] = set()
        self.k = 0
        self.status: dict[int, tuple[str, str]] = {}
        self.jump: tuple[str, str, bool] | None = None
        self.lines: list[LLine] = []
        self.cond_target: str | None = None  # GRAPH: куда записать условие катушки TrCoil/SvCoil/IlCoil

    # -- служебное -------------------------------------------------------------------
    def trace(self, uid: int | None = None) -> str:
        where = f"сеть {self.net.number}"
        return f"{where}, UId {uid}" if uid is not None else where

    def rule(self, name: str) -> str:
        return f"{self.prefix}.{name}"

    def line(self, text: str, uid: int | None, notes: list[LowerNote] | None = None) -> None:
        self.lines.append(LLine(text, self.trace(uid), notes or []))

    def mark(self, uid: int, status: str, rule: str) -> None:
        old = self.status.get(uid)
        if old is None or worst(old[0], status) != old[0]:
            self.status[uid] = (status, rule)

    def temp(self, type_name: str = "Bool", comment: str = "") -> str:
        self.k += 1
        return self.bl.temp(f"xNet{self.net.number}_{self.k}", type_name, comment or f"сеть {self.net.number}")

    def note(self, uid: int, severity: str, rule: str, message: str) -> LowerNote:
        self.mark(uid, severity, rule)
        return LowerNote(severity, rule, message)

    def vocab_notes(self, uid: int, part: NPart) -> list[LowerNote]:
        """Элемент, форма XML которого не подтверждена открытым экспортом: не выше check."""
        entry = PARTS.get(part.name)
        if entry is not None and entry.level == "L":
            return [
                self.note(
                    uid,
                    CHECK,
                    self.rule("vocab_unverified"),
                    f"элемент «{part.name}»: имя и пины в SimaticML не подтверждены открытым экспортом "
                    "(docs/MAPPING_LADFBD.md, уровень L)",
                )
            ]
        return []

    # -- значения ----------------------------------------------------------------------
    def source_value(self, src: End) -> Ex | None:
        if src.kind == RAIL:
            return TRUE
        if src.kind == IDENT:
            acc = self.net.accesses.get(src.uid)
            return atom(acc.text) if acc is not None else None
        if src.kind == PIN:
            return self.output(src.uid, src.pin)
        return None

    def value(self, uid: int, pin: str, default: Ex | None = None) -> Ex | None:
        src = self.net.driver(uid, pin)
        part = self.net.parts[uid]
        if src is None:
            return default
        ex = self.source_value(src)
        if ex is None:
            return default
        if pin.lower() in part.negated:
            ex = not_(ex)
        return ex

    def operand_text(self, uid: int, pin: str = "operand") -> str | None:
        acc = self.net.operand(uid, pin)
        return acc.text if acc is not None else None

    def fanout(self, uid: int, pin: str) -> int:
        return len(self.net.sinks_of(uid, pin))

    def output(self, uid: int, pin: str) -> Ex:
        key = (uid, pin.lower())
        if key in self.memo:
            return self.memo[key]
        part = self.net.parts.get(uid)
        if part is None:
            return FALSE
        if part.name not in COMBINATIONAL:
            self.emit_part(uid)
            return self.memo.get(key, FALSE)
        ex = self.combinational(uid, part)
        if pin.lower() in part.negated:
            ex = not_(ex)
        if self.fanout(uid, pin) > 1 and not is_simple(ex):
            tmp = self.temp(comment=f"сеть {self.net.number}: общий участок (UId {uid})")
            self.line(f"{tmp} := {ex[0]};", uid)
            ex = atom(tmp)
        self.memo[key] = ex
        return ex

    def combinational(self, uid: int, part: NPart) -> Ex:
        notes = self.vocab_notes(uid, part)
        del notes  # пометка уровня L ставится на оператор-приёмник через mark(); здесь — только учёт
        name = part.name
        self.mark(uid, AUTO, self.rule(PARTS[name].rule))
        if name == "Contact":
            opnd = self.operand_text(uid)
            if opnd is None:
                self.mark(uid, TODO, self.rule("wire"))
                return FALSE
            op_ex = atom(opnd)
            if "operand" in part.negated:
                op_ex = not_(op_ex)
            return and_(self.value(uid, "in", TRUE), op_ex)
        if name == "Not":
            return not_(self.value(uid, "in", TRUE) or TRUE)
        if name in ("O", "A", "X"):
            ins = [self.value(uid, f"in{i}") for i in range(1, part.card + 1)]
            present = [x for x in ins if x is not None]
            if name == "O":
                return or_(*present)
            if name == "A":
                return and_(*present)
            return xor_(*present) if present else FALSE
        if name in _COMPARE:
            a = self.value(uid, "in1", FALSE) or FALSE
            b = self.value(uid, "in2", FALSE) or FALSE
            return and_(self.value(uid, "pre", TRUE), cmp_(_COMPARE[name], a, b))
        if name in ("InRange", "OutRange"):
            lo = self.value(uid, "min", FALSE) or FALSE
            val = self.value(uid, "val", FALSE) or FALSE
            hi = self.value(uid, "max", FALSE) or FALSE
            if name == "InRange":
                inner = and_(cmp_("<=", lo, val), cmp_("<=", val, hi))
            else:
                inner = or_(cmp_("<", val, lo), cmp_(">", val, hi))
            return and_(self.value(uid, "pre", TRUE), inner)
        return FALSE

    # -- элементы с действием ----------------------------------------------------------
    def emit_part(self, uid: int) -> None:
        if uid in self.emitted or uid in self.active:
            return
        self.active.add(uid)
        part = self.net.parts[uid]
        handler = getattr(self, f"do_{part.name.lower()}", None)
        if part.name in ("Coil", "SCoil", "RCoil"):
            self.do_coil(uid, part)
        elif part.name in ("TrCoil", "SvCoil", "IlCoil"):
            self.do_cond_coil(uid, part)
        elif part.name in ("PBox", "NBox"):
            self.do_edge_box(uid, part)
        elif part.name in ("PContact", "NContact"):
            self.do_edge_contact(uid, part)
        elif part.name in ("PCoil", "NCoil"):
            self.do_edge_coil(uid, part)
        elif part.name in ("SR", "RS"):
            self.do_flipflop(uid, part)
        elif part.name in ("Move",):
            self.do_move(uid, part)
        elif part.name in _MATH or part.name in ("Neg", "Abs"):
            self.do_math(uid, part)
        elif part.name in ("Convert", "Round", "Trunc"):
            self.do_convert(uid, part)
        elif part.name in _INSTR or part.name in ("Min", "Max", "And", "Or", "Xor"):
            self.do_instruction(uid, part)
        elif part.name == "Calculate":
            self.do_calculate(uid, part)
        elif part.name in ("TON", "TOF", "TP"):
            self.do_instance(uid, part, _TIMER_PINS, ("Q", "ET"), "timer")
        elif part.name in _COUNTER_PINS:
            outs = ("QU", "QD", "CV") if part.name == "CTUD" else ("Q", "CV")
            self.do_instance(uid, part, _COUNTER_PINS[part.name], outs, "counter")
        elif part.name == "Call" and part.call is not None:
            self.do_call(uid, part)
        elif part.name in ("Jump", "JumpNot"):
            self.do_jump(uid, part)
        elif part.name == "Return":
            self.do_return(uid, part)
        elif handler is None:
            self.do_unknown(uid, part)
        self.active.discard(uid)
        self.emitted.add(uid)

    def en_value(self, uid: int) -> Ex:
        """Вход EN блока: не подключён — TRUE (блок без EN в FBD)."""
        return self.value(uid, "en", TRUE) or TRUE

    def guarded(self, uid: int, en: Ex, body: list[str], notes: list[LowerNote]) -> None:
        """Операторы блока под IF en (без IF, если EN = TRUE)."""
        if not body:
            return
        if en == TRUE:
            for n, text in enumerate(body):
                self.line(text, uid, notes if n == 0 else None)
            return
        self.line(f"IF {en[0]} THEN", uid, notes)
        for text in body:
            self.line(f"   {text}", uid)
        self.line("END_IF;", uid)

    def materialize(self, uid: int, ex: Ex, comment: str) -> Ex:
        if is_simple(ex):
            return ex
        tmp = self.temp(comment=comment)
        self.line(f"{tmp} := {ex[0]};", uid)
        return atom(tmp)

    def assign_outputs(self, uid: int, pin: str, value: str) -> list[str]:
        """Присваивания выхода pin операндам-приёмникам (FBD: выход блока прямо в переменную)."""
        return [f"{self.net.accesses[s.uid].text} := {value};" for s in self.net.sinks_of(uid, pin) if s.kind == IDENT]

    def do_coil(self, uid: int, part: NPart) -> None:
        en = self.value(uid, "in", TRUE) or TRUE
        notes = self.vocab_notes(uid, part)
        self.mark(uid, AUTO, self.rule(PARTS[part.name].rule))
        opnd = self.operand_text(uid)
        if opnd is None:
            notes.append(self.note(uid, TODO, self.rule("wire"), f"катушка {part.name} без операнда"))
            self.line(f'"{part.name}"(in := {en[0]});', uid, notes)
            return
        if part.name == "Coil":
            value = not_(en) if "operand" in part.negated else en
            self.line(f"{opnd} := {value[0]};", uid, notes)
        else:
            const = "TRUE" if part.name == "SCoil" else "FALSE"
            if en == TRUE:
                self.line(f"{opnd} := {const};", uid, notes)
            else:
                self.line(f"IF {en[0]} THEN", uid, notes)
                self.line(f"   {opnd} := {const};", uid)
                self.line("END_IF;", uid)
        self.memo[(uid, "out")] = en

    def do_cond_coil(self, uid: int, part: NPart) -> None:
        """Катушка условия GRAPH: значение входа — условие перехода, контроля или блокировки шага."""
        value = self.value(uid, "in", FALSE) or FALSE
        target = self.cond_target or "#xGraphCondition"
        self.mark(uid, AUTO, self.rule("graph_condition"))
        self.line(f"{target} := {value[0]};", uid, self.vocab_notes(uid, part))

    def edge_memory_notes(self, uid: int, bit: str | None) -> list[LowerNote]:
        if bit is not None and self.bl.member_section(bit) == "Temp":
            return [
                self.note(
                    uid,
                    CHECK,
                    self.rule("edge_memory"),
                    f"бит памяти фронта {bit} во временной области: между вызовами значение не сохраняется "
                    "(ошибка исходной программы S7)",
                )
            ]
        return []

    def do_edge_box(self, uid: int, part: NPart) -> None:
        notes = self.vocab_notes(uid, part)
        self.mark(uid, AUTO, self.rule("edge"))
        bit = self.operand_text(uid, "bit")
        clk = self.value(uid, "in", TRUE) or TRUE
        if bit is None:
            notes.append(self.note(uid, TODO, self.rule("wire"), f"{part.name} без бита памяти"))
            self.line(f'"{part.name}"(in := {clk[0]});', uid, notes)
            self.memo[(uid, "out")] = FALSE
            return
        notes += self.edge_memory_notes(uid, bit)
        clk = self.materialize(uid, clk, f"сеть {self.net.number}: вход фронта (UId {uid})")
        out = self.temp(comment=f"сеть {self.net.number}: {part.name} (UId {uid})")
        edge = and_(clk, not_(atom(bit))) if part.name == "PBox" else and_(not_(clk), atom(bit))
        self.line(f"{out} := {edge[0]};", uid, notes)
        self.line(f"{bit} := {clk[0]};", uid)
        self.memo[(uid, "out")] = atom(out)

    def do_edge_contact(self, uid: int, part: NPart) -> None:
        notes = self.vocab_notes(uid, part)
        self.mark(uid, AUTO, self.rule("edge"))
        opnd = self.operand_text(uid)
        bit = self.operand_text(uid, "bit")
        rlo = self.value(uid, "in", TRUE) or TRUE
        if opnd is None or bit is None:
            notes.append(self.note(uid, TODO, self.rule("wire"), f"{part.name} без операнда или бита памяти"))
            self.line(f'"{part.name}"(in := {rlo[0]});', uid, notes)
            self.memo[(uid, "out")] = FALSE
            return
        notes += self.edge_memory_notes(uid, bit)
        out = self.temp(comment=f"сеть {self.net.number}: {part.name} (UId {uid})")
        sig = atom(opnd)
        edge = and_(sig, not_(atom(bit))) if part.name == "PContact" else and_(not_(sig), atom(bit))
        self.line(f"{out} := {edge[0]};", uid, notes)
        self.line(f"{bit} := {opnd};", uid)
        self.memo[(uid, "out")] = and_(rlo, atom(out))

    def do_edge_coil(self, uid: int, part: NPart) -> None:
        notes = self.vocab_notes(uid, part)
        self.mark(uid, AUTO, self.rule("edge"))
        opnd = self.operand_text(uid)
        bit = self.operand_text(uid, "bit")
        rlo = self.value(uid, "in", TRUE) or TRUE
        if opnd is None or bit is None:
            notes.append(self.note(uid, TODO, self.rule("wire"), f"{part.name} без операнда или бита памяти"))
            self.line(f'"{part.name}"(in := {rlo[0]});', uid, notes)
            return
        notes += self.edge_memory_notes(uid, bit)
        rlo = self.materialize(uid, rlo, f"сеть {self.net.number}: вход катушки фронта (UId {uid})")
        edge = and_(rlo, not_(atom(bit))) if part.name == "PCoil" else and_(not_(rlo), atom(bit))
        self.line(f"{opnd} := {edge[0]};", uid, notes)
        self.line(f"{bit} := {rlo[0]};", uid)
        self.memo[(uid, "out")] = rlo

    def do_flipflop(self, uid: int, part: NPart) -> None:
        """SR: сначала S, потом R1 (сброс главнее); RS: сначала R, потом S1 (установка главнее)."""
        notes = self.vocab_notes(uid, part)
        self.mark(uid, AUTO, self.rule("sr_operand"))
        opnd = self.operand_text(uid)
        if opnd is None:
            notes.append(self.note(uid, TODO, self.rule("wire"), f"{part.name} без бита-операнда"))
            self.line(f'"{part.name}"();', uid, notes)
            self.memo[(uid, "q")] = FALSE
            return
        if part.name == "SR":
            first, first_val, second, second_val = (
                self.value(uid, "s", FALSE),
                "TRUE",
                self.value(uid, "r1", FALSE),
                "FALSE",
            )
        else:
            first, first_val, second, second_val = (
                self.value(uid, "r", FALSE),
                "FALSE",
                self.value(uid, "s1", FALSE),
                "TRUE",
            )
        first = first or FALSE
        second = second or FALSE
        order = "сброс главнее" if part.name == "SR" else "установка главнее"
        self.line(f"// {part.name} с битом {opnd}: порядок S7 — {order}", uid)
        self.line(f"IF {first[0]} THEN", uid, notes)
        self.line(f"   {opnd} := {first_val};", uid)
        self.line("END_IF;", uid)
        self.line(f"IF {second[0]} THEN", uid)
        self.line(f"   {opnd} := {second_val};", uid)
        self.line("END_IF;", uid)
        self.memo[(uid, "q")] = atom(opnd)
        for text in self.assign_outputs(uid, "q", opnd):
            self.line(text, uid)

    def out_target(self, uid: int, pin: str, type_name: str) -> str:
        """Куда пишет выход блока: первый операнд-приёмник или временная переменная."""
        for s in self.net.sinks_of(uid, pin):
            if s.kind == IDENT:
                return self.net.accesses[s.uid].text
        return self.temp(type_name, f"сеть {self.net.number}: выход {pin} (UId {uid})")

    def src_type(self, uid: int, part: NPart, *pins: str) -> str:
        for key in ("SrcType", "DestType"):
            if part.templates.get(key):
                return part.templates[key].upper()
        for pin in pins:
            acc = self.net.operand(uid, pin)
            if acc is not None:
                found = self.bl.member_type(acc.text)
                if found:
                    return found.upper()
        return ""

    def finish_box(self, uid: int, part: NPart, en: Ex, body: list[str], notes: list[LowerNote], eno: Ex) -> None:
        self.guarded(uid, en, body, notes)
        self.memo[(uid, "eno")] = eno
        for text in self.assign_outputs(uid, "eno", eno[0]):
            self.line(text, uid)

    def do_move(self, uid: int, part: NPart) -> None:
        notes = self.vocab_notes(uid, part)
        self.mark(uid, AUTO, self.rule("move"))
        en = self.en_value(uid)
        if self.net.connected(uid, "eno"):
            en = self.materialize(uid, en, f"сеть {self.net.number}: EN (UId {uid})")
        src = self.value(uid, "in", FALSE) or FALSE
        body = []
        for i in range(1, part.card + 1):
            pin = f"out{i}"
            for s in self.net.sinks_of(uid, pin):
                if s.kind == IDENT:
                    body.append(f"{self.net.accesses[s.uid].text} := {src[0]};")
            if self.net.connected(uid, pin):
                self.memo[(uid, pin)] = src
        self.finish_box(uid, part, en, body, notes, en)

    def do_math(self, uid: int, part: NPart) -> None:
        notes = self.vocab_notes(uid, part)
        self.mark(uid, AUTO, self.rule("math"))
        en = self.en_value(uid)
        eno_used = self.net.connected(uid, "eno")
        if eno_used:
            en = self.materialize(uid, en, f"сеть {self.net.number}: EN (UId {uid})")
        typ = self.src_type(uid, part, "in1", "in", "out")
        if part.name in ("Neg", "Abs"):
            a = self.value(uid, "in", FALSE) or FALSE
            expr: Ex = (f"-{a[0]}", 7) if part.name == "Neg" and is_simple(a) else atom(f"ABS({a[0]})")
            if part.name == "Neg" and not is_simple(a):
                expr = atom(f"-({a[0]})")
            ins = [a]
        else:
            count = part.card if part.name in ("Add", "Mul") else 2
            ins = [self.value(uid, f"in{i}", FALSE) or FALSE for i in range(1, count + 1)]
            expr = arith(_MATH[part.name], *ins)
        eno = en
        if eno_used:
            if (part.name, typ) in _ENO_FUNCS and len(ins) == 2:
                func = f"F_S7Eno{part.name}{typ.capitalize()}"
                self.bl.support.add(func)
                ok = atom(f"{func}({ins[0][0]}, {ins[1][0]})")
                eno_tmp = self.temp(comment=f"сеть {self.net.number}: ENO {part.name} (UId {uid})")
                eno_note = self.note(
                    uid,
                    CHECK,
                    self.rule("eno_error"),
                    f"ENO {part.name} S7 = EN AND NOT переполнение: {func} из S7Compat (в CODESYS ENO = EN); "
                    "результат при переполнении записывается с переносом, как у S7-300 [M]",
                )
                self.line(f"{eno_tmp} := {and_(en, ok)[0]};", uid, [eno_note])
                eno = atom(eno_tmp)
            else:
                notes.append(
                    self.note(
                        uid,
                        CHECK,
                        self.rule("eno_error"),
                        f"ENO {part.name} ({typ or 'тип не определён'}): ошибка блока не моделируется, ENO = EN",
                    )
                )
        out_type = typ or "Int"
        target = self.out_target(uid, "out", out_type.capitalize())
        body = [f"{target} := {expr[0]};"]
        if part.name in ("Div", "Mod"):
            divisor = ins[1]
            notes.append(
                self.note(
                    uid,
                    CHECK,
                    self.rule("div_zero"),
                    f"{part.name.upper()} на 0: S7 даёт ENO = 0, CODESYS — исключение; "
                    "деление под условием делитель <> 0",
                )
            )
            body = [f"IF {cmp_('<>', divisor, atom('0'))[0]} THEN", f"   {target} := {expr[0]};", "END_IF;"]
        self.memo[(uid, "out")] = atom(target)
        extra = [t for t in self.assign_outputs(uid, "out", target) if not t.startswith(f"{target} :=")]
        self.finish_box(uid, part, en, body + extra, notes, eno)

    def do_convert(self, uid: int, part: NPart) -> None:
        notes = self.vocab_notes(uid, part)
        self.mark(uid, AUTO, self.rule("convert"))
        en = self.en_value(uid)
        if self.net.connected(uid, "eno"):
            en = self.materialize(uid, en, f"сеть {self.net.number}: EN (UId {uid})")
            notes.append(
                self.note(uid, CHECK, self.rule("eno_error"), f"ENO {part.name}: ошибка диапазона не моделируется")
            )
        src = self.value(uid, "in", FALSE) or FALSE
        if part.name == "Convert":
            s_type = part.templates.get("SrcType", "") or self.src_type(uid, part, "in")
            d_type = part.templates.get("DestType", "")
            if not d_type:
                acc = self.net.operand(uid, "out")
                d_type = (self.bl.member_type(acc.text) or "") if acc is not None else ""
            func = f"{s_type.upper()}_TO_{d_type.upper()}" if s_type and d_type else "CONVERT"
            out_type = d_type or "Int"
        else:
            func = part.name.upper()
            out_type = part.templates.get("DestType", "DInt")
        target = self.out_target(uid, "out", out_type)
        self.memo[(uid, "out")] = atom(target)
        self.finish_box(uid, part, en, [f"{target} := {func}({src[0]});"], notes, en)

    def do_instruction(self, uid: int, part: NPart) -> None:
        notes = self.vocab_notes(uid, part)
        self.mark(uid, AUTO, self.rule("instruction"))
        en = self.en_value(uid)
        if self.net.connected(uid, "eno"):
            en = self.materialize(uid, en, f"сеть {self.net.number}: EN (UId {uid})")
        if part.name in _INSTR:
            func, params = _INSTR[part.name]
            args = ", ".join(f"{param} := {(self.value(uid, pin, FALSE) or FALSE)[0]}" for pin, param in params)
            expr = f"{func}({args})"
        elif part.name in ("Min", "Max"):
            args = ", ".join(
                f"IN{i} := {(self.value(uid, f'in{i}', FALSE) or FALSE)[0]}" for i in range(1, part.card + 1)
            )
            expr = f"{part.name.upper()}({args})"
        else:
            ins = [self.value(uid, f"in{i}", FALSE) or FALSE for i in range(1, part.card + 1)]
            expr = {"And": and_, "Or": or_, "Xor": xor_}[part.name](*ins)[0]
        typ = self.src_type(uid, part, "out", "in", "in1", "value")
        target = self.out_target(uid, "out", (typ or "Int").capitalize())
        self.memo[(uid, "out")] = atom(target)
        self.finish_box(uid, part, en, [f"{target} := {expr};"], notes, en)

    def do_calculate(self, uid: int, part: NPart) -> None:
        notes = self.vocab_notes(uid, part)
        self.mark(uid, AUTO, self.rule("calculate"))
        en = self.en_value(uid)
        equation = part.equation or "IN1"

        def repl(m: re.Match[str]) -> str:
            val = self.value(uid, m.group(0).lower(), FALSE) or FALSE
            return val[0] if is_simple(val) else f"({val[0]})"

        expr = re.sub(r"\bIN\d+\b", repl, equation, flags=re.IGNORECASE)
        typ = self.src_type(uid, part, "out")
        target = self.out_target(uid, "out", (typ or "Real").capitalize())
        self.memo[(uid, "out")] = atom(target)
        self.finish_box(uid, part, en, [f"{target} := {expr};"], notes, en)

    def do_instance(self, uid: int, part: NPart, inputs: tuple[str, ...], outputs: tuple[str, ...], kind: str) -> None:
        notes = self.vocab_notes(uid, part)
        self.mark(uid, AUTO, self.rule(kind))
        if not part.instance:
            notes.append(self.note(uid, TODO, self.rule("instance"), f"{part.name} без экземпляра (Instance)"))
            self.line(f'"{part.name}"();', uid, notes)
            for pin in outputs:
                self.memo[(uid, pin.lower())] = FALSE
            return
        args = []
        for pin in inputs:
            val = self.value(uid, pin)
            if val is not None:
                args.append(f"{pin} := {val[0]}")
        inst = part.instance
        call = f"{inst}({', '.join(args)});"
        if part.instance_scope == "GlobalVariable":
            call = f"{inst}.{part.name}({', '.join(args)});"
        self.line(call, uid, notes)
        for pin in outputs:
            self.memo[(uid, pin.lower())] = atom(f"{inst}.{pin}")
            for text in self.assign_outputs(uid, pin, f"{inst}.{pin}"):
                self.line(text, uid)

    def callee_eno_plain(self, part: NPart) -> bool:
        """Вызываемый блок есть во входе, написан на LAD/FBD/STL и не пишет ENO/BR → ENO = EN."""
        assert part.call is not None
        callee = self.bl.registry.get(part.call.name.lower())
        if callee is None or callee.set_eno:
            return False
        if callee.lang.upper() not in ("LAD", "FBD", "LAD_IEC", "FBD_IEC"):
            return False
        for unit in callee.units:
            if unit.body is None:
                continue
            for el in unit.body.iter():
                if el.get("Name", "").upper() == "ENO" or el.get("Combination") == "BR":
                    return False
        return True

    def do_call(self, uid: int, part: NPart) -> None:
        notes = self.vocab_notes(uid, part)
        self.mark(uid, AUTO, self.rule("call"))
        info = part.call
        assert info is not None
        en = self.en_value(uid)
        eno_used = self.net.connected(uid, "eno")
        if eno_used:
            en = self.materialize(uid, en, f"сеть {self.net.number}: EN вызова (UId {uid})")
        args: list[str] = []
        after: list[str] = []
        ret_target = ""
        for name, section, typ in info.params:
            if section in ("Input", "InOut"):
                val = self.value(uid, name)
                if val is not None:
                    args.append(f"{name} := {val[0]}")
                elif section == "InOut":
                    acc = self.net.operand(uid, name)
                    if acc is not None:
                        args.append(f"{name} := {acc.text}")
            elif section == "Output":
                idents = [s for s in self.net.sinks_of(uid, name) if s.kind == IDENT]
                others = [s for s in self.net.sinks_of(uid, name) if s.kind != IDENT]
                if info.block_type == "FB" and info.instance:
                    for s in idents:
                        after.append(f"{self.net.accesses[s.uid].text} := {info.instance}.{name};")
                    self.memo[(uid, name.lower())] = atom(f"{info.instance}.{name}")
                elif idents or others:
                    target = (
                        self.net.accesses[idents[0].uid].text
                        if idents
                        else self.temp(typ or "Bool", f"сеть {self.net.number}: выход {name} вызова (UId {uid})")
                    )
                    args.append(f"{name} => {target}")
                    for s in idents[1:]:
                        after.append(f"{self.net.accesses[s.uid].text} := {target};")
                    self.memo[(uid, name.lower())] = atom(target)
            elif section == "Return" and typ.lower() != "void":
                idents = [s for s in self.net.sinks_of(uid, name) if s.kind == IDENT]
                ret_target = (
                    self.net.accesses[idents[0].uid].text
                    if idents
                    else self.temp(typ or "Int", f"сеть {self.net.number}: результат вызова (UId {uid})")
                )
                self.memo[(uid, name.lower())] = atom(ret_target)
        callee = f'"{info.name}"'
        if info.block_type == "FB":
            if not info.instance:
                notes.append(self.note(uid, TODO, self.rule("instance"), f"вызов FB {info.name} без экземпляра"))
            callee = info.instance or callee
        text = f"{callee}({', '.join(args)});"
        if ret_target:
            text = f"{ret_target} := {callee}({', '.join(args)});"
        eno = en
        if eno_used and not self.callee_eno_plain(part):
            notes.append(
                self.note(
                    uid,
                    CHECK,
                    self.rule("call_eno"),
                    f"ENO вызова {info.name}: вызываемый блок может писать ENO/BR — перевод ставит ENO = EN",
                )
            )
        self.guarded(uid, en, [text, *after], notes)
        self.memo[(uid, "eno")] = eno
        for t in self.assign_outputs(uid, "eno", eno[0]):
            self.line(t, uid)

    def do_jump(self, uid: int, part: NPart) -> None:
        notes = self.vocab_notes(uid, part)
        self.mark(uid, AUTO, self.rule("jump"))
        label = self.operand_text(uid) or ""
        rlo = self.value(uid, "in", TRUE) or TRUE
        tmp = self.temp(comment=f"сеть {self.net.number}: условие прыжка к {label} (UId {uid})")
        self.line(f"{tmp} := {rlo[0]};", uid, notes)
        # Jump: прыжок при RLO = TRUE → следующие сети выполняются при NOT tmp; JumpNot — наоборот
        self.jump = (label, tmp, part.name == "Jump")

    def do_return(self, uid: int, part: NPart) -> None:
        notes = self.vocab_notes(uid, part)
        self.mark(uid, AUTO, self.rule("return"))
        rlo = self.value(uid, "in", TRUE) or TRUE
        if rlo == TRUE:
            self.line("RETURN;", uid, notes)
        else:
            self.line(f"IF {rlo[0]} THEN", uid, notes)
            self.line("   RETURN;", uid)
            self.line("END_IF;", uid)

    def do_unknown(self, uid: int, part: NPart) -> None:
        ins = []
        for pin in sorted(self.net.pins(uid)):
            src = self.net.driver(uid, pin)
            if src is not None:
                val = self.source_value(src)
                if val is not None:
                    ins.append(f"{pin} := {val[0]}")
        note = self.note(uid, TODO, self.rule("unknown_part"), f"элемент «{part.name}» не поддерживается")
        self.line(f'"{part.name}"({", ".join(ins)});', uid, [note])
        for pin in self.net.pins(uid):
            self.memo.setdefault((uid, pin), FALSE)

    # -- сеть целиком -----------------------------------------------------------------
    def run(self) -> list[LLine]:
        if self.net.title:
            self.line(f"// Сеть {self.net.number}: {self.net.title}", None)
        else:
            self.line(f"// Сеть {self.net.number}", None)
        for issue in self.net.issues:
            m = re.search(r"UId (\d+)", issue)
            uid = int(m.group(1)) if m else 0
            note = self.note(uid, TODO, self.rule("wire"), f"сеть {self.net.number}: {issue}")
            self.line(f'"FlgNet"(); // {issue}', uid if m else None, [note])
        for uid, part in self.net.parts.items():
            if part.name not in COMBINATIONAL:
                self.emit_part(uid)
        for uid, part in self.net.parts.items():
            if uid not in self.status:
                known = PARTS.get(part.name)
                self.mark(uid, AUTO, self.rule(known.rule) if known else self.rule("unknown_part"))
            entry = PARTS.get(part.name)
            if entry is not None and entry.level == "L" and self.status[uid][0] == AUTO:
                self.status[uid] = (CHECK, self.rule("vocab_unverified"))
        for uid, (status, rule) in self.status.items():
            if uid in self.net.parts:
                self.bl.unit("element", status, rule, self.trace(uid))
        statuses = [s for s, _r in self.status.values()] or [AUTO]
        net_status = worst(*statuses)
        net_rule = next((r for s, r in self.status.values() if s == net_status), self.rule("network"))
        self.bl.unit("network", net_status, net_rule, self.trace())
        return self.lines


def structure_jumps(
    networks: list[tuple[list[LLine], tuple[str, str, bool] | None, list[str]]], trace: str
) -> tuple[list[LLine], list[LowerNote]]:
    """Прыжки вперёд через сети → IF; метка — в начале сети-цели. Несводимое — пометка todo.

    networks: (строки сети, прыжок (метка, временная, прыжок при TRUE), метки сети).
    """
    out: list[LLine] = []
    notes: list[LowerNote] = []
    i = 0
    while i < len(networks):
        lines, jump, _labels = networks[i]
        out.extend(lines)
        if jump is None:
            i += 1
            continue
        label, tmp, when_true = jump
        target = next((j for j in range(i + 1, len(networks)) if label in networks[j][2]), None)
        if target is None:
            notes.append(
                LowerNote(
                    TODO, "lad.jump_irreducible", f"прыжок к {label}: метка не найдена впереди (назад — не переносится)"
                )
            )
            i += 1
            continue
        inner_nets = networks[i + 1 : target]
        if any(
            n[1] is not None and next((j for j, m in enumerate(networks) if n[1][0] in m[2]), 0) > target
            for n in inner_nets
        ):
            notes.append(LowerNote(TODO, "lad.jump_irreducible", f"прыжок к {label} пересекается с другим прыжком"))
            i += 1
            continue
        inner, inner_notes = structure_jumps(inner_nets, trace)
        notes.extend(inner_notes)
        cond = f"NOT {tmp}" if when_true else tmp
        out.append(LLine(f"IF {cond} THEN // прыжок к {label}: сети {i + 2}–{target} выполняются без прыжка", trace))
        out.extend(indent(inner) if inner else [LLine("   ;", trace)])
        out.append(LLine("END_IF;", trace))
        i = target
    return out, notes


def lower_networks(bl: BlockLower, networks: list[Network]) -> None:
    """Сети блока LAD/FBD → строки bl.lines (с прыжками вперёд через сети)."""
    parts: list[tuple[list[LLine], tuple[str, str, bool] | None, list[str]]] = []
    for net in networks:
        lowerer = NetLowerer(bl, net)
        lines = lowerer.run()
        parts.append((lines, lowerer.jump, net.labels))
    body, notes = structure_jumps(parts, "сети блока")
    if notes:
        bl.block_notes.extend(notes)
    bl.lines.extend(body)


__all__ = ["COMBINATIONAL", "PARTS", "NetLowerer", "PartRule", "lower_networks", "structure_jumps"]
