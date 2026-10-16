"""Таблицы соответствий: литералы, преобразования типов, имена, адреса, таблица тегов, OB → задачи."""

from __future__ import annotations

import pytest

from s7conv import mapping as M
from s7conv import symbols as S
from s7conv import tasks as T

# ---------------------------------------------------------------------------
# Литералы
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("kind", "text", "expected", "severity"),
    [
        ("int", "1_000", "1_000", None),
        ("real", "1.5e-3", "1.5e-3", None),
        ("bool", "true", "TRUE", None),
        ("string", "'a$'b'", "'a$'b'", None),
        ("typed", "T#5s", "T#5s", None),
        ("typed", "TIME#1h2m", "T#1h2m", None),
        ("typed", "T#-5s", "T#-5s", M.CHECK),
        ("typed", "LT#5s", "LTIME#5s", None),
        ("typed", "S5T#2s", "T#2s", M.CHECK),
        ("typed", "S5TIME#100ms", "T#100ms", M.CHECK),
        ("typed", "D#2024-01-31", "D#2024-01-31", None),
        ("typed", "DATE#2024-01-31", "D#2024-01-31", None),
        ("typed", "TOD#08:30:00", "TOD#08:30:00", None),
        ("typed", "TIME_OF_DAY#08:30:00", "TOD#08:30:00", None),
        ("typed", "DT#2024-01-31-12:00:00", "DT#2024-01-31-12:00:00", None),
        ("typed", "DATE_AND_TIME#2024-01-31-12:00:00", "DT#2024-01-31-12:00:00", None),
        ("typed", "LDT#2024-01-31-12:00:00", "LDT#2024-01-31-12:00:00", M.CHECK),
        ("typed", "16#FF", "16#FF", None),
        ("typed", "B#16#0F", "BYTE#16#0F", None),
        ("typed", "W#16#FFFF", "WORD#16#FFFF", None),
        ("typed", "DW#16#0001", "DWORD#16#0001", None),
        ("typed", "LW#16#1", "LWORD#16#1", None),
        ("typed", "L#100", "DINT#100", None),
        ("typed", "int#-5", "INT#-5", None),
        ("typed", "REAL#1.5", "REAL#1.5", None),
        ("typed", "STRING#'abc'", "'abc'", None),
        ("typed", "WSTRING#'it$'s \"q\"'", '"it\'s $"q$""', None),
        ("typed", "CHAR#'A'", "'A'", M.CHECK),
        ("typed", "C#5", "C#5", M.TODO),
        ("typed", "P#M100.0 BYTE 16", "P#M100.0 BYTE 16", M.TODO),
        ("typed", "XYZ#1", "XYZ#1", M.TODO),
    ],
)
def test_literal_mapping(kind: str, text: str, expected: str, severity: str | None) -> None:
    mapped = M.map_literal(kind, text)
    assert (mapped.text, mapped.severity) == (expected, severity)


def test_split_typed() -> None:
    assert M.split_typed("T#5s") == ("T", "5s")
    assert M.split_typed("16#FF") == ("", "16#FF")
    assert M.split_typed("B#16#FF") == ("B", "16#FF")


@pytest.mark.parametrize(
    ("kind", "text", "expected"),
    [
        ("bool", "TRUE", "BOOL"),
        ("real", "1.0", "REAL"),
        ("int", "5", None),
        ("typed", "T#5s", "TIME"),
        ("typed", "S5T#5s", "TIME"),
        ("typed", "W#16#1", "WORD"),
        ("typed", "INT#3", "INT"),
        ("typed", "L#3", "DINT"),
        ("string", "'x'", "STRING"),
    ],
)
def test_literal_types(kind: str, text: str, expected: str | None) -> None:
    assert M.literal_type(kind, text) == expected


# ---------------------------------------------------------------------------
# Преобразования и функции
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "target", "severity"),
    [
        ("INT_TO_REAL", "INT_TO_REAL", None),
        ("WORD_TO_INT", "WORD_TO_INT", None),
        ("REAL_TO_INT", "REAL_TO_INT", M.CHECK),
        ("DWORD_TO_REAL", "DWORD_TO_REAL", M.CHECK),
        ("REAL_TO_DWORD", "REAL_TO_DWORD", M.CHECK),
        ("S5TIME_TO_TIME", "", M.CHECK),
        ("S5TIME_TO_DINT", "", M.TODO),
        ("CHAR_TO_INT", "", M.TODO),
        ("WORD_TO_BLOCK_DB", "", M.TODO),
    ],
)
def test_conversion_rules(name: str, target: str, severity: str | None) -> None:
    rule = M.conversion_rule(name)
    assert rule is not None
    assert (rule.target, rule.severity) == (target, severity)


def test_not_a_conversion() -> None:
    assert M.conversion_rule("NORM_X") is None


@pytest.mark.parametrize("name", ["PEEK", "PEEK_WORD", "POKE_BLK", "RD_SYS_T", "S_ODT", "BLKMOV", "TypeOf".upper()])
def test_unsupported_functions(name: str) -> None:
    assert M.unsupported_function(name) is not None


def test_supported_functions_are_not_unsupported() -> None:
    for name in M.FUNCTIONS:
        assert M.unsupported_function(name) is None, name


def test_generic_method_types() -> None:
    assert M.generic_method_type("IEC_TIMER", "TON") == "TON"
    assert M.generic_method_type("IEC_LTIMER", "TOF") == "TOF_LTIME"
    assert M.generic_method_type("IEC_COUNTER", "CTU") == "CTU_INT"
    assert M.generic_method_type("IEC_TIMER", "TONR") == "TONR_TIME"


def test_counter_rules_rename_inputs() -> None:
    assert M.FB_TYPES["CTU_INT"].target == "CTU" and M.FB_TYPES["CTU_INT"].params == {"R": "RESET"}
    assert M.FB_TYPES["CTD_DINT"].params == {"LD": "LOAD"}
    assert M.FB_TYPES["CTUD"].params == {"R": "RESET", "LD": "LOAD"}
    assert M.FB_TYPES["TON_TIME"].target == "TON" and not M.FB_TYPES["TON_TIME"].message


# ---------------------------------------------------------------------------
# Имена
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("start", "start"),
        ("Motor 1", "Motor_1"),
        ("Cyclic interrupt", "Cyclic_interrupt"),
        ("1st", "_1st"),
        ("a--b", "a_b"),
        ("time", "time_"),
        ("MAX", "MAX_"),
        ("R", "R_"),
        ("Насос", "Nasos"),
        ("уровень бака", "uroven_baka"),
        ("", "x_"),
    ],
)
def test_sanitize(name: str, expected: str) -> None:
    assert M.sanitize(name) == expected


def test_pou_prefix() -> None:
    assert M.pou_prefixed("Main", "PRG_") == "PRG_Main"
    assert M.pou_prefixed("PRG_Main", "PRG_") == "PRG_Main"


# ---------------------------------------------------------------------------
# Адреса и теги
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "at", "name", "type_name"),
    [
        ("%I0.0", "%IX0.0", "I0_0", "BOOL"),
        ("%Q4.7", "%QX4.7", "Q4_7", "BOOL"),
        ("%M12.1", "%MX12.1", "M12_1", "BOOL"),
        ("%IB3", "%IB3", "IB3", "BYTE"),
        ("%IW64", "%IW32", "IW64", "WORD"),
        ("%QW80", "%QW40", "QW80", "WORD"),
        ("%MW11", None, "MW11", "WORD"),
        ("%MD20", "%MD5", "MD20", "DWORD"),
        ("%MD10", None, "MD10", "DWORD"),
        ("%E1.2", "%IX1.2", "I1_2", "BOOL"),
    ],
)
def test_address_model(text: str, at: str | None, name: str, type_name: str) -> None:
    addr = S.parse_address(text)
    assert addr is not None
    assert (addr.codesys_at(), addr.generated_name(), addr.default_type) == (at, name, type_name)


@pytest.mark.parametrize("text", ["%I0.8", "%IW1.2", "%I3", "%DB1.DBX0.0", "%T5", "%L0.0"])
def test_invalid_addresses(text: str) -> None:
    assert S.parse_address(text) is None


def test_peripheral_flag() -> None:
    addr = S.parse_address("%IW272:P")
    assert addr is not None and addr.peripheral


def test_tag_table_loading_and_groups() -> None:
    text = (
        "Name;Path;Data Type;Logical Address;Comment\n"
        "Start;T;Bool;%I0.0;Пуск\n"
        "Level;T;Int;%IW64;\n"
        "Flag;T;Bool;%M1.0;\n"
        "T_Retry;T;Timer;%T5;\n"
        "Bad;T;Bool;%X9;\n"
        "Free;T;Real;;\n"
    )
    tags, errors = S.load_tag_table(text, "tags.csv")
    by_name = {t.name: t for t in tags}
    assert by_name["Start"].gvl == S.GVL_IO and by_name["Start"].comment == "Пуск"
    assert by_name["Flag"].gvl == S.GVL_MARKERS
    assert by_name["T_Retry"].gvl == S.TAG_S5
    assert by_name["Free"].gvl == S.GVL_TAGS
    assert errors == ["tags.csv:6: адрес '%X9' тега 'Bad' не распознан"]


def test_tag_table_constants_and_comma_delimiter() -> None:
    tags, errors = S.load_tag_table("Name,Data Type,Value\nMAX_N,Int,10\n", "c.csv")
    assert not errors and tags[0].gvl == S.GVL_USER_CONST and tags[0].value == "10"


def test_tag_table_requires_columns() -> None:
    _tags, errors = S.load_tag_table("Foo;Bar\n1;2\n", "x.csv")
    assert errors


def test_duplicate_tag_names_are_reported() -> None:
    project = S.Project()
    tags, _ = S.load_tag_table("Name;Data Type;Logical Address\nA;Bool;%I0.0\na;Bool;%I0.1\n", "t.csv")
    project.add_tags(tags)
    assert len(project.tags) == 1 and project.errors


def test_looks_like_tag_table() -> None:
    assert S.looks_like_tag_table("Name,Path,Data Type,Logical Address\n")
    assert not S.looks_like_tag_table("Block,Kind,Number\n")


# ---------------------------------------------------------------------------
# OB → задачи
# ---------------------------------------------------------------------------


def classify(name: str, title: str = "", comments: str = "", config: dict[str, object] | None = None) -> T.ObInfo:
    info = T.ObInfo(name=name, program="PRG_" + name.replace(" ", "_"), file="f.scl", line=1)
    T.classify(info, title, comments, config or {})
    return info


def test_classify_standard_names() -> None:
    assert (classify("Main").number, classify("Main").kind) == (1, T.MAIN)
    assert classify("Startup").kind == T.STARTUP
    cyc = classify("Cyclic interrupt")
    assert (cyc.number, cyc.kind, cyc.interval_ms) == (30, T.CYCLIC, 5000)
    assert cyc.notes  # период по умолчанию требует проверки


def test_classify_hints_and_config() -> None:
    info = classify("Fast", title="OB35 control loop 50 ms")
    assert (info.number, info.kind, info.interval_ms) == (35, T.CYCLIC, 50)
    info = classify("X", config={"X": {"number": 33, "kind": "cyclic", "interval_ms": 250, "priority": 3}})
    assert (info.number, info.interval_ms, info.priority, info.number_origin) == (33, 250, 3, "ob-config")
    info = classify(
        "Diagnostic error interrupt", config={"Diagnostic error interrupt": {"number": 82, "kind": "event"}}
    )
    assert info.kind == T.EVENT


def test_period_hint_seconds() -> None:
    assert classify("Cyclic 0,5 s").interval_ms == 500


def test_build_tasks_orders_startup_first_and_rate_monotonic() -> None:
    obs = [
        classify("Main"),
        classify("Startup"),
        classify("Slow", config={"Slow": {"number": 31, "kind": "cyclic", "interval_ms": 1000}}),
        classify("Fast", config={"Fast": {"number": 38, "kind": "cyclic", "interval_ms": 10}}),
        classify("HW", config={"HW": {"number": 40, "kind": "event"}}),
    ]
    tasks = T.build_tasks(obs, "freewheeling", 10)
    assert [(t.name, t.type, t.interval_ms, t.priority) for t in tasks] == [
        ("MainTask", "freewheeling", 10, T.MAIN_PRIORITY),
        ("Task_OB38", "cyclic", 10, 1),
        ("Task_OB31", "cyclic", 1000, 2),
    ]
    assert tasks[0].pous == ["PRG_Startup", "PRG_Main"]
    data = T.tasks_json(obs, tasks, "s7conv test")
    assert data["manual"] == ["PRG_HW: HW (OB40) — задача по событию не создаётся автоматически, настроить вручную"]
