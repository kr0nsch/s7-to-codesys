"""Таблицы соответствий S7/SCL → ST CODESYS V3.5 (описаны в docs/MAPPING.md).

Здесь только данные и чистые функции без состояния: типы, функциональные блоки инструкций,
встроенные функции, литералы, имена. Решения, которые зависят от контекста (тип цели
присваивания, таблица символов), принимает emitter.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Пометки
# ---------------------------------------------------------------------------

CHECK = "check"
TODO = "todo"


@dataclass(frozen=True)
class Mapped:
    """Результат сопоставления: текст ST и пометка (severity, правило, сообщение) или None."""

    text: str
    severity: str | None = None
    rule: str = ""
    message: str = ""


# ---------------------------------------------------------------------------
# Элементарные типы
# ---------------------------------------------------------------------------

# Тип SCL (верхний регистр) -> тип CODESYS. Сопоставление 1:1, без пометок.
ELEMENTARY: dict[str, str] = {
    "BOOL": "BOOL",
    "BYTE": "BYTE",
    "WORD": "WORD",
    "DWORD": "DWORD",
    "LWORD": "LWORD",
    "SINT": "SINT",
    "USINT": "USINT",
    "INT": "INT",
    "UINT": "UINT",
    "DINT": "DINT",
    "UDINT": "UDINT",
    "LINT": "LINT",
    "ULINT": "ULINT",
    "REAL": "REAL",
    "LREAL": "LREAL",
    "TIME": "TIME",
    "LTIME": "LTIME",
    "DATE": "DATE",
    "TIME_OF_DAY": "TOD",
    "TOD": "TOD",
    "DATE_AND_TIME": "DT",
    "DT": "DT",
}

# Типы с пометкой «проверить»
CHECKED_TYPES: dict[str, tuple[str, str, str]] = {
    "S5TIME": ("TIME", "type.s5time", "S5Time → TIME: в S7 S5TIME — BCD с шагом 10 мс…10 с, диапазон до 2h46m30s"),
    "CHAR": ("STRING(1)", "type.char", "Char → STRING(1): в CODESYS нет типа CHAR, сравнения и CHAR_TO_* проверить"),
    "WCHAR": ("WSTRING(1)", "type.wchar", "WChar → WSTRING(1): в CODESYS нет типа WCHAR"),
    "LDT": ("LDT", "type.ldt", "LDT: поддержка в CODESYS 3.5.17 — сверить с источником"),
    "LTOD": ("LTOD", "type.ltod", "LTOD: поддержка в CODESYS 3.5.17 — сверить с источником"),
    "LTIME_OF_DAY": ("LTOD", "type.ltod", "LTOD: поддержка в CODESYS 3.5.17 — сверить с источником"),
}

# Типы без аналога: объявление становится MIGRATION-TODO
UNSUPPORTED_TYPES: dict[str, str] = {
    "DTL": "DTL — структура S7 (YEAR, MONTH, ...), в CODESYS нет; заменить на DT или свою структуру",
    "VARIANT": "Variant — нет аналога в CODESYS; переписать (ANY, POINTER или перегрузка)",
    "ANY": "Any (указатель S7) — нет аналога",
    "POINTER": "Pointer (S7, 6 байт) — нет аналога, переписать через POINTER TO",
    "BLOCK_FB": "Block_FB — нет аналога",
    "BLOCK_FC": "Block_FC — нет аналога",
    "BLOCK_DB": "Block_DB — нет аналога",
    "BLOCK_SDB": "Block_SDB — нет аналога",
    "DB_ANY": "DB_ANY — номер DB, в CODESYS нет; переписать через POINTER/REFERENCE",
    "DB_DYN": "DB_DYN — нет аналога",
    "DB_WWW": "DB_WWW — нет аналога",
    "TIMER": "Timer (S5) — нет аналога, заменить на TON/TOF/TP",
    "COUNTER": "Counter (S5) — нет аналога, заменить на CTU/CTD/CTUD",
    "TONR_TIME": "TONR (таймер с накоплением) — в CODESYS Standard нет",
    "TONR_LTIME": "TONR (таймер с накоплением) — в CODESYS Standard нет",
    "IEC_TIMER": "IEC_TIMER без вызова .TON/.TOF/.TP — тип таймера не определить",
    "IEC_LTIMER": "IEC_LTIMER без вызова — тип таймера не определить",
    "ERROR_STRUCT": "ErrorStruct (GET_ERROR) — нет аналога",
}

UNSUPPORTED_TYPE_PREFIXES = ("HW_", "OB_", "EVENT_", "CONN_", "AOM_", "PORT", "RTM", "PIP", "DB_")

# Функциональные блоки инструкций: тип S7 -> (тип CODESYS, пометка или None, переименование входов/выходов)


@dataclass(frozen=True)
class FbRule:
    target: str
    rule: str
    message: str = ""  # пустое — без пометки
    params: dict[str, str] = field(default_factory=dict)  # входы/выходы S7 -> CODESYS
    members: dict[str, str] = field(default_factory=dict)  # доступ inst.X -> inst.Y


_COUNTER_MSG = "счётчик S7 → {t} (CODESYS Standard): PV и CV — WORD (0…65535), в S7 — тип счётчика; проверить диапазон"


def _counter_rules() -> dict[str, FbRule]:
    rules: dict[str, FbRule] = {}
    suffixes = ("", "_SINT", "_INT", "_DINT", "_LINT", "_USINT", "_UINT", "_UDINT", "_ULINT")
    for base, params in (
        ("CTU", {"R": "RESET"}),
        ("CTD", {"LD": "LOAD"}),
        ("CTUD", {"R": "RESET", "LD": "LOAD"}),
    ):
        for suffix in suffixes:
            rules[base + suffix] = FbRule(base, "fb.counter", _COUNTER_MSG.format(t=base), params)
    return rules


FB_TYPES: dict[str, FbRule] = {
    "TON_TIME": FbRule("TON", "fb.timer"),
    "TOF_TIME": FbRule("TOF", "fb.timer"),
    "TP_TIME": FbRule("TP", "fb.timer"),
    "TON": FbRule("TON", "fb.timer"),
    "TOF": FbRule("TOF", "fb.timer"),
    "TP": FbRule("TP", "fb.timer"),
    "TON_LTIME": FbRule(
        "LTON", "fb.ltimer", "TON_LTIME → LTON: наличие LTON в CODESYS Standard — сверить с источником"
    ),
    "TOF_LTIME": FbRule(
        "LTOF", "fb.ltimer", "TOF_LTIME → LTOF: наличие LTOF в CODESYS Standard — сверить с источником"
    ),
    "TP_LTIME": FbRule("LTP", "fb.ltimer", "TP_LTIME → LTP: наличие LTP в CODESYS Standard — сверить с источником"),
    "R_TRIG": FbRule("R_TRIG", "fb.trig"),
    "F_TRIG": FbRule(
        "F_TRIG",
        "fb.f_trig",
        "F_TRIG: в S7 на первом вызове с CLK = FALSE спада нет; даёт ли F_TRIG CODESYS Standard ложный спад "
        "на первом вызове (начальное значение памяти) — сверить с источником или тестом",
    ),
    "SR": FbRule(
        "SR",
        "fb.flipflop",
        "SR: входы S/R1 → SET1/RESET, выход Q → Q1 (CODESYS Standard)",
        {"S": "SET1", "R1": "RESET", "Q": "Q1"},
        {"Q": "Q1"},
    ),
    "RS": FbRule(
        "RS",
        "fb.flipflop",
        "RS: входы R/S1 → RESET1/SET, выход Q → Q1 (CODESYS Standard)",
        {"R": "RESET1", "S1": "SET", "Q": "Q1"},
        {"Q": "Q1"},
    ),
    **_counter_rules(),
}

# ---------------------------------------------------------------------------
# Режимы таймеров и F_TRIG: CODESYS Standard или рукописный слой совместимости S7Compat
# ---------------------------------------------------------------------------

STANDARD = "standard"
S7COMPAT = "s7compat"
SEMANTICS_MODES = (STANDARD, S7COMPAT)

# TON/TOF/TP CODESYS Standard -> ФБ S7Compat с тем же интерфейсом (IN, PT, Q, ET) и подменяемым
# источником времени F_S7Now (детерминированные тесты сценариев — docs/methodology.md)
COMPAT_TIMERS: dict[str, str] = {"TON": "FB_S7Ton", "TOF": "FB_S7Tof", "TP": "FB_S7Tp"}
# F_TRIG -> ФБ S7Compat с семантикой S7: на первом вызове с CLK = FALSE спада нет
COMPAT_F_TRIG = "FB_S7FTrig"

# Рукописные объекты поддержки (src/*/S7Compat): имя -> объекты, без которых оно не компилируется
SUPPORT_DEPENDENCIES: dict[str, tuple[str, ...]] = {
    "F_NormX": (),
    "F_ScaleX": (),
    "FB_S7Ton": ("F_S7Now",),
    "FB_S7Tof": ("F_S7Now",),
    "FB_S7Tp": ("F_S7Now",),
    "F_S7Now": ("GVL_S7Clock",),
    "GVL_S7Clock": (),
    "FB_S7FTrig": (),
}


def support_closure(names: set[str] | list[str] | tuple[str, ...]) -> list[str]:
    """Объекты поддержки вместе с зависимостями (по имени, отсортировано)."""
    result: set[str] = set()
    stack = list(names)
    while stack:
        name = stack.pop()
        if name in result:
            continue
        result.add(name)
        stack.extend(SUPPORT_DEPENDENCIES.get(name, ()))
    return sorted(result)


def fb_types(timers: str = STANDARD, f_trig: str = STANDARD) -> dict[str, FbRule]:
    """Таблица ФБ инструкций для режимов таймеров и F_TRIG (Options.timers, Options.f_trig)."""
    for mode in (timers, f_trig):
        if mode not in SEMANTICS_MODES:
            raise ValueError(f"режим {mode!r}: ожидалось {' или '.join(SEMANTICS_MODES)}")
    if timers == STANDARD and f_trig == STANDARD:
        return FB_TYPES
    table: dict[str, FbRule] = {}
    for key, rule in FB_TYPES.items():
        if timers == S7COMPAT and rule.rule == "fb.timer" and rule.target in COMPAT_TIMERS:
            table[key] = FbRule(COMPAT_TIMERS[rule.target], "fb.timer_s7compat", "", rule.params, rule.members)
        elif f_trig == S7COMPAT and rule.target == "F_TRIG":
            table[key] = FbRule(COMPAT_F_TRIG, "fb.f_trig_s7compat")
        else:
            table[key] = rule
    return table


# IEC_TIMER / IEC_COUNTER: тип определяется по вызову "DB".TON(...) или #t.TON(...)
GENERIC_INSTANCE_TYPES = frozenset(
    {
        "IEC_TIMER",
        "IEC_LTIMER",
        "IEC_COUNTER",
        "IEC_SCOUNTER",
        "IEC_DCOUNTER",
        "IEC_LCOUNTER",
        "IEC_USCOUNTER",
        "IEC_UCOUNTER",
        "IEC_UDCOUNTER",
        "IEC_ULCOUNTER",
    }
)
GENERIC_METHODS = frozenset({"TON", "TOF", "TP", "TONR", "CTU", "CTD", "CTUD"})


def generic_method_type(generic: str, method: str) -> str:
    """Тип экземпляра по вызову метода экземпляра IEC_TIMER/IEC_COUNTER: TON, TON_LTIME, CTU_INT ..."""
    method = method.upper()
    generic = generic.upper()
    if generic == "IEC_LTIMER" and method in ("TON", "TOF", "TP", "TONR"):
        return method + "_LTIME"
    if method in ("TON", "TOF", "TP"):
        return method
    if method == "TONR":
        return "TONR_TIME"
    suffix = {
        "IEC_SCOUNTER": "_SINT",
        "IEC_COUNTER": "_INT",
        "IEC_DCOUNTER": "_DINT",
        "IEC_LCOUNTER": "_LINT",
        "IEC_USCOUNTER": "_USINT",
        "IEC_UCOUNTER": "_UINT",
        "IEC_UDCOUNTER": "_UDINT",
        "IEC_ULCOUNTER": "_ULINT",
    }.get(generic, "")
    return method + suffix


# ---------------------------------------------------------------------------
# Встроенные функции
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FuncRule:
    """Функция S7 -> CODESYS.

    params — имена параметров S7 в позиционном порядке CODESYS (именованный вызов S7 переводится
    в позиционный, операторы CODESYS именованных параметров не принимают); None — аргументы как есть.
    variadic — префикс параметров переменного числа (IN1, IN2, ... для MIN/MAX).
    named — имена параметров CODESYS для именованного вызова (F_NormX, F_ScaleX).
    """

    target: str
    rule: str
    params: tuple[str, ...] | None = None
    severity: str | None = None
    message: str = ""
    variadic: str = ""
    named: tuple[str, ...] = ()


def _same(name: str, params: tuple[str, ...], rule: str = "func.std") -> FuncRule:
    return FuncRule(name, rule, params)


FUNCTIONS: dict[str, FuncRule] = {
    **{n: _same(n, ("IN",)) for n in ("ABS", "SQRT", "LN", "LOG", "EXP", "SIN", "COS", "TAN", "ASIN", "ACOS", "ATAN")},
    "TRUNC": _same("TRUNC", ("IN",)),
    "EXPT": _same("EXPT", ("IN1", "IN2")),
    "LIMIT": _same("LIMIT", ("MN", "IN", "MX")),
    "SEL": _same("SEL", ("G", "IN0", "IN1")),
    "MIN": FuncRule("MIN", "func.std", (), variadic="IN"),
    "MAX": FuncRule("MAX", "func.std", (), variadic="IN"),
    "MUX": FuncRule(
        "MUX", "func.std", ("K",), variadic="IN", severity=CHECK, message="MUX: вход ELSE S7 не переносится"
    ),
    **{n: _same(n, ("IN", "N")) for n in ("SHL", "SHR", "ROL", "ROR")},
    "CONCAT": _same("CONCAT", ("IN1", "IN2"), "func.string"),
    "LEN": _same("LEN", ("IN",), "func.string"),
    "LEFT": _same("LEFT", ("IN", "L"), "func.string"),
    "RIGHT": _same("RIGHT", ("IN", "L"), "func.string"),
    "MID": _same("MID", ("IN", "L", "P"), "func.string"),
    "FIND": _same("FIND", ("IN1", "IN2"), "func.string"),
    "DELETE": _same("DELETE", ("IN", "L", "P"), "func.string"),
    "INSERT": _same("INSERT", ("IN1", "IN2", "P"), "func.string"),
    "REPLACE": _same("REPLACE", ("IN1", "IN2", "L", "P"), "func.string"),
    "SQR": FuncRule("EXPT", "func.sqr", ("IN",)),  # особый случай: EXPT(x, 2)
    "ROUND": FuncRule(
        "REAL_TO_DINT",
        "func.round",
        ("IN",),
        CHECK,
        "ROUND → REAL_TO_DINT: правило округления половины (x.5) сверить с источником",
    ),
    "NORM_X": FuncRule("F_NormX", "func.norm_x", ("MIN", "VALUE", "MAX"), named=("rMin", "rValue", "rMax")),
    "SCALE_X": FuncRule("F_ScaleX", "func.scale_x", ("MIN", "VALUE", "MAX"), named=("rMin", "rValue", "rMax")),
    "S5TI_TIM": FuncRule(
        "", "conv.s5time", ("IN",), CHECK, "S5TI_TIM: S5Time уже сопоставлен с TIME — преобразование убрано"
    ),
    "TIM_S5TI": FuncRule(
        "", "conv.s5time", ("IN",), CHECK, "TIM_S5TI: S5Time уже сопоставлен с TIME — преобразование убрано"
    ),
    "TIME_TCK": FuncRule(
        "TIME", "func.time_tck", (), CHECK, "TIME_TCK → TIME(): системное время в мс, переполнение UDINT/DINT сверить"
    ),
    "UPPER_BOUND": FuncRule(
        "UPPER_BOUND", "func.bound", ("ARR", "DIM"), CHECK, "UPPER_BOUND: в CODESYS — для ARRAY[*], сверить"
    ),
    "LOWER_BOUND": FuncRule(
        "LOWER_BOUND", "func.bound", ("ARR", "DIM"), CHECK, "LOWER_BOUND: в CODESYS — для ARRAY[*], сверить"
    ),
}

UNSUPPORTED_FUNCTIONS: dict[str, str] = dict.fromkeys(
    (
        "CEIL",
        "FLOOR",
        "FRAC",
        "MOVE_BLK",
        "UMOVE_BLK",
        "MOVE_BLK_VARIANT",
        "FILL_BLK",
        "UFILL_BLK",
        "SWAP",
        "PEEK",
        "PEEK_BOOL",
        "POKE",
        "POKE_BOOL",
        "POKE_BLK",
        "READ_BIG",
        "WRITE_BIG",
        "READ_LITTLE",
        "WRITE_LITTLE",
        "RD_SYS_T",
        "WR_SYS_T",
        "RD_LOC_T",
        "WR_LOC_T",
        "T_ADD",
        "T_SUB",
        "T_DIFF",
        "T_COMBINE",
        "T_CONV",
        "STRG_VAL",
        "VAL_STRG",
        "S_CONV",
        "STRG_TO_CHARS",
        "CHARS_TO_STRG",
        "ATH",
        "HTA",
        "MAX_LEN",
        "GET_ERROR",
        "GET_ERR_ID",
        "GEN_DIAG",
        "GET_DIAG",
        "RUNTIME",
        "DECO",
        "ENCO",
        "SCATTER",
        "SCATTER_BLK",
        "GATHER",
        "GATHER_BLK",
        "TYPEOF",
        "TYPEOFELEMENTS",
        "TYPEOFDB",
        "IS_ARRAY",
        "COUNTOFELEMENTS",
        "VARIANTGET",
        "VARIANTPUT",
        "SERIALIZE",
        "DESERIALIZE",
        "RE_TRIGR",
        "STP",
        "GETSYMBOLNAME",
        "GETSYMBOLPATH",
        "GETINSTANCENAME",
        "GETINSTANCEPATH",
        "GETBLOCKNAME",
        "CREATE_DB",
        "DELETE_DB",
        "READ_DBL",
        "WRIT_DBL",
        "ATTR_DB",
        "DPRD_DAT",
        "DPWR_DAT",
        "RDREC",
        "WRREC",
        "RALRM",
        "LOG2GEO",
        "GEO2LOG",
        "DEVICESTATES",
        "MODULESTATES",
        "IS_NULL",
        "NOT_NULL",
        "REF",
        "S_ODT",
        "S_ODTS",
        "S_OFFDT",
        "S_PULSE",
        "S_PEXT",
        "S_CU",
        "S_CD",
        "S_CUD",
        "BLKMOV",
        "UBLKMOV",
        "FILL",
    ),
    "нет прямого аналога в CODESYS Standard",
)
UNSUPPORTED_FUNCTIONS.update(
    {
        "BCD16_TO_INT": "BCD: в CODESYS — BCD_TO_INT из библиотеки Util; подключить и проверить",
        "INT_TO_BCD16": "BCD: в CODESYS — INT_TO_BCD из библиотеки Util; подключить и проверить",
        "BCD32_TO_DINT": "BCD: в CODESYS — Util; проверить",
        "DINT_TO_BCD32": "BCD: в CODESYS — Util; проверить",
    }
)

_UNSUPPORTED_PREFIXES = ("PEEK", "POKE", "MOVE_BLK", "FILL_BLK", "SCATTER", "GATHER", "T_", "TYPEOF", "VARIANT")


def unsupported_function(upper: str) -> str | None:
    """Причина, по которой функция S7 не переносится, или None."""
    if upper in UNSUPPORTED_FUNCTIONS:
        return UNSUPPORTED_FUNCTIONS[upper]
    if upper.startswith(_UNSUPPORTED_PREFIXES) and upper not in FUNCTIONS:
        return "нет прямого аналога в CODESYS Standard"
    return None


CODESYS_ELEMENTARY = frozenset(
    {
        "BOOL",
        "BYTE",
        "WORD",
        "DWORD",
        "LWORD",
        "SINT",
        "USINT",
        "INT",
        "UINT",
        "DINT",
        "UDINT",
        "LINT",
        "ULINT",
        "REAL",
        "LREAL",
        "TIME",
        "LTIME",
        "DATE",
        "TOD",
        "TIME_OF_DAY",
        "DT",
        "DATE_AND_TIME",
        "STRING",
        "WSTRING",
    }
)
_CONVERSION_RE = re.compile(r"([A-Z0-9_]+?)_TO_([A-Z0-9_]+)$")
# Преобразования, которые в S7-1200/1500 переносят битовый образ, а в CODESYS — числовое значение
_BITCAST = {
    ("DWORD", "REAL"),
    ("REAL", "DWORD"),
    ("LWORD", "LREAL"),
    ("LREAL", "LWORD"),
}
_INTEGER_TYPES = frozenset({"SINT", "USINT", "INT", "UINT", "DINT", "UDINT", "LINT", "ULINT"})


def conversion_rule(name: str) -> FuncRule | None:
    """Функции преобразования X_TO_Y: None — не преобразование."""
    match = _CONVERSION_RE.match(name.upper())
    if not match:
        return None
    src, dst = match.group(1), match.group(2)
    if src in ("S5TIME",) or dst in ("S5TIME",):
        other = dst if src == "S5TIME" else src
        if other == "TIME":
            return FuncRule("", "conv.s5time", ("IN",), CHECK, f"{name}: S5TIME уже сопоставлен с TIME — вызов убран")
        return FuncRule(
            "", "conv.unsupported", None, "todo", f"{name}: преобразование S5TIME↔{other} не поддерживается"
        )
    if src in ("CHAR", "WCHAR") or dst in ("CHAR", "WCHAR"):
        return FuncRule("", "conv.unsupported", None, "todo", f"{name}: в CODESYS нет типа CHAR/WCHAR")
    if src not in CODESYS_ELEMENTARY or dst not in CODESYS_ELEMENTARY:
        return FuncRule("", "conv.unsupported", None, "todo", f"{name}: преобразование без аналога в CODESYS")
    target = f"{src}_TO_{dst}"
    if (src, dst) in _BITCAST:
        return FuncRule(
            target,
            "conv.bitcast",
            ("IN",),
            CHECK,
            f"{name}: в S7-1200/1500 переносится битовый образ, в CODESYS — числовое значение",
        )
    if src in ("REAL", "LREAL") and dst in _INTEGER_TYPES:
        return FuncRule(target, "conv.round", ("IN",), CHECK, f"{name}: округление при x.5 в S7 и CODESYS сверить")
    return FuncRule(target, "conv.std", ("IN",))


# ---------------------------------------------------------------------------
# Литералы
# ---------------------------------------------------------------------------

_TYPE_PREFIXES = frozenset(
    {
        "BOOL",
        "BYTE",
        "WORD",
        "DWORD",
        "LWORD",
        "SINT",
        "USINT",
        "INT",
        "UINT",
        "DINT",
        "UDINT",
        "LINT",
        "ULINT",
        "REAL",
        "LREAL",
    }
)


def split_typed(text: str) -> tuple[str, str]:
    """'T#5s' -> ('T', '5s'); '16#FF' -> ('', '16#FF'); 'B#16#FF' -> ('B', '16#FF')."""
    head, sep, tail = text.partition("#")
    if not sep:
        return "", text
    if head.isdigit():
        return "", text
    return head, tail


def map_literal(kind: str, text: str) -> Mapped:
    """Литерал SCL -> литерал CODESYS."""
    if kind in ("int", "real"):
        return Mapped(text)
    if kind == "bool":
        return Mapped(text.upper())
    if kind == "string":
        return Mapped(text)
    prefix, body = split_typed(text)
    upper = prefix.upper()
    if upper == "":
        return Mapped(text)
    if upper in ("T", "TIME"):
        if body.startswith("-"):
            return Mapped(
                "T#" + body, CHECK, "lit.time_negative", "отрицательный TIME: в CODESYS TIME беззнаковый (UDINT мс)"
            )
        return Mapped("T#" + body)
    if upper in ("LT", "LTIME"):
        return Mapped("LTIME#" + body)
    if upper in ("S5T", "S5TIME"):
        rule, message = CHECKED_TYPES["S5TIME"][1:]
        return Mapped("T#" + body, CHECK, rule, message)
    if upper in ("D", "DATE"):
        return Mapped("D#" + body)
    if upper in ("TOD", "TIME_OF_DAY"):
        return Mapped("TOD#" + body)
    if upper in ("DT", "DATE_AND_TIME"):
        return Mapped("DT#" + body)
    if upper in ("LTOD", "LTIME_OF_DAY", "LDT"):
        return Mapped(f"{upper}#{body}", CHECK, "lit.long_date", f"{upper}#: поддержка в CODESYS 3.5.17 сверить")
    if upper in ("B", "W", "DW", "LW"):
        full = {"B": "BYTE", "W": "WORD", "DW": "DWORD", "LW": "LWORD"}[upper]
        return Mapped(f"{full}#{body}")
    if upper == "L":
        return Mapped("DINT#" + body)
    if upper in _TYPE_PREFIXES:
        return Mapped(f"{upper}#{body}")
    if upper == "STRING":
        return Mapped(body)
    if upper == "WSTRING":
        return Mapped(to_wstring_literal(body))
    if upper == "CHAR":
        return Mapped(body, CHECK, "lit.char", "CHAR# → строка из одного символа (STRING(1))")
    if upper == "WCHAR":
        return Mapped(to_wstring_literal(body), CHECK, "lit.char", "WCHAR# → WSTRING(1)")
    if upper == "C":
        return Mapped(text, TODO, "lit.counter", "C# — константа счётчика S5, нет аналога")
    if upper == "P":
        return Mapped(text, TODO, "lit.pointer", "P# — указатель S7, нет аналога")
    return Mapped(text, TODO, "lit.unknown", f"литерал {prefix}# не поддерживается")


def to_wstring_literal(body: str) -> str:
    """'abc$'x' (SCL) -> "abc'x" (WSTRING CODESYS)."""
    inner = body[1:-1] if len(body) >= 2 else body
    out: list[str] = []
    i = 0
    while i < len(inner):
        c = inner[i]
        if c == "$" and i + 1 < len(inner):
            nxt = inner[i + 1]
            out.append("'" if nxt == "'" else c + nxt)
            i += 2
            continue
        out.append('$"' if c == '"' else c)
        i += 1
    return '"' + "".join(out) + '"'


def literal_type(kind: str, text: str) -> str | None:
    """Тип CODESYS литерала, если однозначен (для вывода типа тегов)."""
    if kind == "bool":
        return "BOOL"
    if kind == "real":
        return "REAL"
    if kind == "int":
        return None
    if kind == "string":
        return "STRING"
    prefix, _ = split_typed(text)
    upper = prefix.upper()
    if upper in ("T", "TIME", "S5T", "S5TIME"):
        return "TIME"
    if upper in ("D", "DATE"):
        return "DATE"
    if upper in ("TOD", "TIME_OF_DAY"):
        return "TOD"
    if upper in ("DT", "DATE_AND_TIME"):
        return "DT"
    if upper in ("B",):
        return "BYTE"
    if upper == "W":
        return "WORD"
    if upper == "DW":
        return "DWORD"
    if upper == "L":
        return "DINT"
    if upper in _TYPE_PREFIXES:
        return upper
    return None


# ---------------------------------------------------------------------------
# Имена
# ---------------------------------------------------------------------------

_TRANSLIT = dict(
    zip(
        "абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
        [
            "a",
            "b",
            "v",
            "g",
            "d",
            "e",
            "e",
            "zh",
            "z",
            "i",
            "y",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "r",
            "s",
            "t",
            "u",
            "f",
            "kh",
            "ts",
            "ch",
            "sh",
            "shch",
            "",
            "y",
            "",
            "e",
            "yu",
            "ya",
        ],
        strict=True,
    )
)

# Ключевые слова и операторы CODESYS/МЭК, которые нельзя использовать как имена
RESERVED_ST = frozenset(
    {
        "ABS",
        "ABSTRACT",
        "ACOS",
        "ACTION",
        "ADD",
        "ADR",
        "AND",
        "AND_THEN",
        "ANY",
        "ARRAY",
        "ASIN",
        "AT",
        "ATAN",
        "BITADR",
        "BIT",
        "BOOL",
        "BY",
        "BYTE",
        "CAL",
        "CALC",
        "CALCN",
        "CASE",
        "CONFIGURATION",
        "CONSTANT",
        "CONTINUE",
        "COS",
        "DATE",
        "DATE_AND_TIME",
        "DINT",
        "DIV",
        "DO",
        "DT",
        "DWORD",
        "ELSE",
        "ELSIF",
        "EN",
        "ENO",
        "EQ",
        "EXIT",
        "EXP",
        "EXPT",
        "EXTENDS",
        "FALSE",
        "FINAL",
        "FOR",
        "FUNCTION",
        "FUNCTION_BLOCK",
        "GE",
        "GT",
        "IF",
        "IMPLEMENTS",
        "INDEXOF",
        "INT",
        "INTERFACE",
        "INTERNAL",
        "JMP",
        "JMPC",
        "JMPCN",
        "LD",
        "LDN",
        "LE",
        "LIMIT",
        "LINT",
        "LN",
        "LOG",
        "LREAL",
        "LT",
        "LTIME",
        "LWORD",
        "MAX",
        "METHOD",
        "MIN",
        "MOD",
        "MOVE",
        "MUL",
        "MUX",
        "NE",
        "NOT",
        "OF",
        "OR",
        "OR_ELSE",
        "ORN",
        "PERSISTENT",
        "POINTER",
        "PRIVATE",
        "PROGRAM",
        "PROPERTY",
        "PROTECTED",
        "PUBLIC",
        "R",
        "REAL",
        "REF",
        "REFERENCE",
        "REPEAT",
        "RET",
        "RETAIN",
        "RETURN",
        "ROL",
        "ROR",
        "S",
        "SEL",
        "SHL",
        "SHR",
        "SIN",
        "SINT",
        "SIZEOF",
        "SQRT",
        "ST",
        "STN",
        "STRING",
        "STRUCT",
        "SUB",
        "SUPER",
        "TAN",
        "THEN",
        "THIS",
        "TIME",
        "TIME_OF_DAY",
        "TO",
        "TOD",
        "TRUE",
        "TRUNC",
        "TYPE",
        "UDINT",
        "UINT",
        "ULINT",
        "UNION",
        "UNTIL",
        "USINT",
        "VAR",
        "VAR_CONFIG",
        "VAR_EXTERNAL",
        "VAR_GLOBAL",
        "VAR_INPUT",
        "VAR_IN_OUT",
        "VAR_INST",
        "VAR_OUTPUT",
        "VAR_STAT",
        "VAR_TEMP",
        "WHILE",
        "WORD",
        "WSTRING",
        "XOR",
        "XORN",
    }
)

_IDENT_OK = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")


def sanitize(name: str) -> str:
    """Имя S7 -> допустимый идентификатор ST (ASCII): транслитерация, '_' вместо прочего, без ключевых слов."""
    out: list[str] = []
    for ch in name:
        low = ch.lower()
        if ch.isascii() and (ch.isalnum() or ch == "_"):
            out.append(ch)
        elif low in _TRANSLIT:
            rep = _TRANSLIT[low]
            out.append(rep.capitalize() if ch.isupper() and rep else rep)
        else:
            out.append("_")
    result = re.sub(r"_{2,}", "_", "".join(out))
    if not result or result == "_":
        result = "x_"
    if result[0].isdigit():
        result = "_" + result
    if result.upper() in RESERVED_ST:
        result += "_"
    return result


def is_plain_ident(name: str) -> bool:
    return bool(_IDENT_OK.match(name))


def pou_prefixed(name: str, prefix: str) -> str:
    """Имя с префиксом CONTRIBUTING.md (PRG_ для OB), если его ещё нет."""
    return name if name.upper().startswith(prefix.upper()) else prefix + name
