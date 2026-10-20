"""Общее для понижения LAD/FBD/STL: строки синтезированного SCL с трассой, выражения, временные переменные.

Понижение пишет текст SCL (тот же диалект, что внешние источники TIA): потом его разбирает parser.py 1.0.0,
и эмиттер, отчёт и генератор тестов работают с ним как с обычным SCL. У каждой строки есть трасса
(«сеть 3, UId 27»), у оператора — пометки понижения (правило и причина), которые эмиттер ставит в код
как MIGRATION-CHECK/MIGRATION-TODO.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from s7conv.frontends.simaticml import XBlock
from s7conv.nodes import LangUnit, LowerNote

AUTO = "auto"
CHECK = "check"
TODO = "todo"
IMPOSSIBLE = "impossible"
_SEVERITY = {AUTO: 0, CHECK: 1, TODO: 2, IMPOSSIBLE: 3}
IND = "   "


def worst(*statuses: str) -> str:
    """Тяжелейший статус: impossible > todo > check > auto."""
    return max(statuses, key=lambda s: _SEVERITY.get(s, 0)) if statuses else AUTO


# ---------------------------------------------------------------------------
# Выражения: (текст, приоритет)
# ---------------------------------------------------------------------------

Ex = tuple[str, int]
P_OR, P_XOR, P_AND, P_CMP, P_ADD, P_MUL, P_NOT, P_ATOM = 1, 2, 3, 4, 5, 6, 7, 9
TRUE: Ex = ("TRUE", P_ATOM)
FALSE: Ex = ("FALSE", P_ATOM)


def atom(text: str) -> Ex:
    return (text, P_ATOM)


def _wrap(e: Ex, keep: tuple[int, ...]) -> str:
    return e[0] if e[1] in keep else f"({e[0]})"


def and_(*items: Ex | None) -> Ex:
    xs = [x for x in items if x is not None and x != TRUE]
    if any(x == FALSE for x in xs):
        return FALSE
    if not xs:
        return TRUE
    if len(xs) == 1:
        return xs[0]
    return (" AND ".join(_wrap(x, (P_ATOM, P_NOT, P_AND)) for x in xs), P_AND)


def or_(*items: Ex | None) -> Ex:
    xs = [x for x in items if x is not None and x != FALSE]
    if any(x == TRUE for x in xs):
        return TRUE
    if not xs:
        return FALSE
    if len(xs) == 1:
        return xs[0]
    return (" OR ".join(_wrap(x, (P_ATOM, P_NOT, P_AND, P_OR)) for x in xs), P_OR)


def xor_(*items: Ex) -> Ex:
    xs = list(items)
    if len(xs) == 1:
        return xs[0]
    return (" XOR ".join(_wrap(x, (P_ATOM, P_NOT, P_AND, P_XOR)) for x in xs), P_XOR)


def not_(e: Ex) -> Ex:
    if e == TRUE:
        return FALSE
    if e == FALSE:
        return TRUE
    if e[1] == P_NOT and e[0].startswith("NOT "):
        inner = e[0][4:]
        return (inner[1:-1], P_OR) if inner.startswith("(") and inner.endswith(")") else (inner, P_ATOM)
    return (f"NOT {_wrap(e, (P_ATOM,))}", P_NOT)


def cmp_(op: str, a: Ex, b: Ex) -> Ex:
    keep = (P_ATOM, P_NOT, P_ADD, P_MUL)
    return (f"{_wrap(a, keep)} {op} {_wrap(b, keep)}", P_CMP)


def arith(op: str, *items: Ex) -> Ex:
    prec = P_ADD if op in ("+", "-") else P_MUL
    keep = (P_ATOM, P_MUL) if prec == P_ADD else (P_ATOM,)
    parts = [_wrap(items[0], keep), *[_wrap(x, (P_ATOM,) if op in ("-", "/", "MOD") else keep) for x in items[1:]]]
    return (f" {op} ".join(parts), prec)


def is_simple(e: Ex) -> bool:
    """Операнд без вычислений: переменная, литерал, элемент — вычислять повторно безопасно."""
    return e[1] == P_ATOM and "(" not in e[0]


# ---------------------------------------------------------------------------
# Строки синтезированного SCL
# ---------------------------------------------------------------------------


@dataclass
class LLine:
    """Строка тела SCL: текст, трасса до исходника, пометки оператора, начинающегося в строке."""

    text: str
    trace: str
    notes: list[LowerNote] = field(default_factory=list)


@dataclass
class Temp:
    name: str
    type: str
    comment: str


@dataclass
class BlockLower:
    """Состояние понижения одного блока: строки тела, временные, единицы учёта, пометки блока."""

    block: XBlock
    lang: str
    registry: dict[str, XBlock] = field(default_factory=dict)  # все блоки входа (имя в нижнем регистре)
    profile: str = "s7-300"
    stl_jumps: str = "structured"
    lines: list[LLine] = field(default_factory=list)
    temps: list[Temp] = field(default_factory=list)
    statics: list[Temp] = field(default_factory=list)  # GRAPH: состояние шагов (VAR синтезированного ФБ)
    units: list[LangUnit] = field(default_factory=list)
    block_notes: list[LowerNote] = field(default_factory=list)
    support: set[str] = field(default_factory=set)
    _taken: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        self._taken = {m.name.lower() for s in self.block.sections for m in s.members}

    def temp(self, name: str, type_name: str, comment: str) -> str:
        """Временная переменная с уникальным именем (VAR_TEMP синтезированного блока)."""
        base, n = name, 2
        while name.lower() in self._taken:
            name = f"{base}_{n}"
            n += 1
        self._taken.add(name.lower())
        self.temps.append(Temp(name, type_name, comment))
        return f"#{name}"

    def static(self, name: str, type_name: str, comment: str) -> str:
        """Статическая переменная с уникальным именем (VAR синтезированного ФБ): сохраняется между вызовами."""
        base, n = name, 2
        while name.lower() in self._taken:
            name = f"{base}_{n}"
            n += 1
        self._taken.add(name.lower())
        self.statics.append(Temp(name, type_name, comment))
        return f"#{name}"

    def emit(self, text: str, trace: str, notes: list[LowerNote] | tuple[LowerNote, ...] = ()) -> None:
        self.lines.append(LLine(text, trace, list(notes)))

    def unit(self, kind: str, status: str, rule: str, trace: str) -> None:
        self.units.append(LangUnit(self.block.name, self.lang, kind, status, rule, trace))

    def member_type(self, text: str) -> str | None:
        """Тип локального операнда `#name` по интерфейсу блока (без индексов и элементов)."""
        if not text.startswith("#"):
            return None
        name = text[1:].split(".", 1)[0].split("[", 1)[0].strip('"')
        found = self.block.member_type(name)
        if found is None:
            for t in [*self.temps, *self.statics]:
                if t.name.lower() == name.lower():
                    return t.type
        return found

    def member_section(self, text: str) -> str | None:
        if not text.startswith("#"):
            return None
        name = text[1:].split(".", 1)[0].split("[", 1)[0].strip('"')
        return self.block.member_section(name)


def indent(lines: list[LLine], levels: int = 1) -> list[LLine]:
    return [LLine(IND * levels + ln.text if ln.text else ln.text, ln.trace, ln.notes) for ln in lines]


__all__ = [
    "AUTO",
    "CHECK",
    "FALSE",
    "IMPOSSIBLE",
    "IND",
    "TODO",
    "TRUE",
    "BlockLower",
    "Ex",
    "LLine",
    "Temp",
    "and_",
    "arith",
    "atom",
    "cmp_",
    "indent",
    "is_simple",
    "not_",
    "or_",
    "worst",
    "xor_",
]
