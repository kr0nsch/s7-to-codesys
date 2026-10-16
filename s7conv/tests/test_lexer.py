"""Лексер SCL: токены TIA Portal, литералы с префиксом, адреса, комментарии, зона заголовка блока."""

from __future__ import annotations

import pytest

from s7conv import lexer as lx
from s7conv.lexer import tokenize


def kinds(text: str) -> list[tuple[str, str]]:
    return [(t.kind, t.text) for t in tokenize(text) if t.kind != lx.EOF]


def test_locals_globals_and_identifiers() -> None:
    toks = tokenize('#start "DB_Plant".level #"my var" plain')
    assert [(t.kind, t.value) for t in toks[:3]] == [
        (lx.LOCAL, "start"),
        (lx.QIDENT, "DB_Plant"),
        (lx.OP, None),
    ]
    assert toks[3].kind == lx.IDENT and toks[3].text == "level"
    assert (toks[4].kind, toks[4].value) == (lx.LOCAL, "my var")
    assert toks[5].kind == lx.IDENT


@pytest.mark.parametrize(
    "text",
    [
        "T#5s",
        "t#1h30m",
        "T#-5s",
        "TIME#2m",
        "LT#5s",
        "S5T#2s",
        "S5TIME#200ms",
        "DT#2024-01-31-12:30:00",
        "DATE_AND_TIME#2024-01-31-12:30:00.5",
        "TOD#08:30:00",
        "TIME_OF_DAY#08:30",
        "D#2024-01-31",
        "DATE#2024-01-31",
        "16#FF",
        "2#1010_1010",
        "8#17",
        "B#16#0F",
        "W#16#FFFF",
        "DW#16#0000_FFFF",
        "L#100",
        "INT#5",
        "INT#-5",
        "DINT#16#FF",
        "REAL#1.5",
        "LREAL#1.5e3",
        "BOOL#TRUE",
        "WSTRING#'abc'",
        "CHAR#'A'",
        "P#M100.0 BYTE 16",
        "P#DB30.DBX4.0 BYTE 16",
    ],
)
def test_typed_literals_are_single_tokens(text: str) -> None:
    toks = kinds(text)
    assert toks == [(lx.TYPED, text)]


@pytest.mark.parametrize(
    ("text", "kind"),
    [("0", lx.INT), ("1_000", lx.INT), ("1.5", lx.REAL), ("1.5e-3", lx.REAL), ("2E5", lx.REAL)],
)
def test_numbers(text: str, kind: str) -> None:
    assert kinds(text) == [(kind, text)]


def test_range_is_not_a_real() -> None:
    assert kinds("0..9") == [(lx.INT, "0"), (lx.OP, ".."), (lx.INT, "9")]


@pytest.mark.parametrize(
    "text", ["%I0.0", "%IW64", "%QW80", "%MD20", "%M12.1", "%IW272:P", "%DB30.DBW0", "%DB1.DBX0.0"]
)
def test_addresses(text: str) -> None:
    assert kinds(text) == [(lx.ADDRESS, text)]


def test_slice_after_dot() -> None:
    assert kinds("#w.%X3") == [(lx.LOCAL, "#w"), (lx.OP, "."), (lx.ADDRESS, "%X3")]


def test_strings_with_dollar_escapes() -> None:
    assert kinds("'it$'s $N'") == [(lx.STRING, "'it$'s $N'")]


def test_unclosed_string_is_error_token() -> None:
    toks = tokenize("'abc\nx")
    assert toks[0].kind == lx.ERROR
    assert toks[1].kind == lx.IDENT


def test_operators_longest_match() -> None:
    ops = [t.text for t in tokenize(":= => <= >= <> ** .. += -= *= /= ?= & ^") if t.kind == lx.OP]
    assert ops == [":=", "=>", "<=", ">=", "<>", "**", "..", "+=", "-=", "*=", "/=", "?=", "&", "^"]


def test_comments_are_attached_to_next_token() -> None:
    toks = tokenize("a := 1; // trailing\n(* block\ncomment *)\nb := 2;")
    b = next(t for t in toks if t.text == "b")
    assert [c.style for c in b.comments] == ["//", "(*"]
    assert not b.comments[0].own_line  # в строке есть код
    assert b.comments[1].own_line


def test_comment_markers_inside_strings_are_text() -> None:
    assert kinds("'a//b (* c *)'") == [(lx.STRING, "'a//b (* c *)'")]


def test_pragma_token_keeps_content() -> None:
    toks = tokenize("{ S7_Optimized_Access := 'TRUE' }")
    assert toks[0].kind == lx.PRAGMA and toks[0].value == "S7_Optimized_Access := 'TRUE'"


def test_header_properties_only_in_header_zone() -> None:
    text = (
        'FUNCTION_BLOCK "FB_X"\nTITLE = Motor (fast)\nAUTHOR : J. Doe\nVERSION : 0.1\n'
        "VAR\n   name : String;\n   version : Int;\nEND_VAR\nEND_FUNCTION_BLOCK\n"
    )
    toks = tokenize(text)
    props = [t.value for t in toks if t.kind == lx.HEADER_PROP]
    assert props == [("TITLE", "Motor (fast)"), ("AUTHOR", "J. Doe"), ("VERSION", "0.1")]
    names = [t.text for t in toks if t.kind == lx.IDENT]
    assert "name" in names and "version" in names  # объявления в VAR — обычные токены


def test_type_variable_does_not_open_header_zone() -> None:
    toks = tokenize("VAR\n   type : Int;\n   name : Int;\nEND_VAR\n")
    assert not [t for t in toks if t.kind == lx.HEADER_PROP]


def test_region_name_is_rest_of_line() -> None:
    toks = tokenize("REGION Pump group (P101...P103) // comment\nEND_REGION")
    region = [t for t in toks if t.kind == lx.REGION_NAME]
    assert [t.value for t in region] == ["Pump group (P101...P103)"]
    end = next(t for t in toks if t.text == "END_REGION")
    assert end.comments and end.comments[0].text == "// comment"


def test_variable_named_region_is_not_a_region() -> None:
    toks = tokenize("region : Int;")
    assert not [t for t in toks if t.kind == lx.REGION_NAME]


def test_bom_and_unknown_character() -> None:
    toks = tokenize("﻿a ` b")
    assert [t.kind for t in toks] == [lx.IDENT, lx.ERROR, lx.IDENT, lx.EOF]


def test_line_and_column() -> None:
    toks = tokenize("a :=\n  #b;")
    b = next(t for t in toks if t.kind == lx.LOCAL)
    assert (b.line, b.col) == (2, 3)


def test_eof_keeps_trailing_comments() -> None:
    toks = tokenize("a; // last")
    assert toks[-1].kind == lx.EOF and toks[-1].comments[0].text == "// last"
