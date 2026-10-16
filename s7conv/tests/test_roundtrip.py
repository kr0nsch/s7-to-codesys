"""Свойство «разбор ∘ печать»: parse_expression(expr_to_scl(e)) == e (hypothesis).

Генератор строит произвольные деревья выражений из всех форм, которые возвращает разборщик:
литералы всех видов, #локальные, "глобальные", имена, адреса, доступ к элементу, индекс, срез,
вызовы с позиционными, именованными и выходными аргументами, унарные и все бинарные операции.
Печать ставит минимум скобок, поэтому свойство проверяет и приоритеты, и ассоциативность.
"""

from __future__ import annotations

import re

from hypothesis import given, settings
from hypothesis import strategies as st

from s7conv.nodes import (
    AddressRef,
    Arg,
    Binary,
    Call,
    Expr,
    GlobalRef,
    Ident,
    Index,
    Literal,
    LocalRef,
    Member,
    Slice,
    Unary,
)
from s7conv.parser import RESERVED, parse_expression
from s7conv.sclprint import expr_to_scl

_EXCLUDED = {w.upper() for w in RESERVED} | {"TRUE", "FALSE"}

idents = st.from_regex(r"[A-Za-z][A-Za-z0-9_]{0,6}", fullmatch=True).filter(
    lambda s: s.upper() not in _EXCLUDED and not re.search(r"__", s)
)
spaced_names = st.from_regex(r"[A-Za-z][A-Za-z0-9 _.]{0,8}[A-Za-z0-9]", fullmatch=True)

int_lits = st.integers(min_value=0, max_value=10**6).map(lambda n: Literal("int", str(n)))
real_lits = st.sampled_from(["0.5", "1.0", "3.14", "1.5e-3", "2.0E5", "100.25"]).map(lambda t: Literal("real", t))
bool_lits = st.sampled_from(["TRUE", "FALSE", "true"]).map(lambda t: Literal("bool", t))
str_lits = st.sampled_from(["''", "'abc'", "'it$'s'", "'$N$L'", "'a // b'", "'(* x *)'"]).map(
    lambda t: Literal("string", t)
)
typed_lits = st.sampled_from(
    [
        "T#5s",
        "T#1h30m",
        "T#-250ms",
        "S5T#2s",
        "LT#10s",
        "DT#2024-01-31-12:30:00",
        "TOD#08:30:00",
        "D#2024-01-31",
        "16#FF",
        "2#1010_1010",
        "B#16#0F",
        "W#16#FFFF",
        "DW#16#0000_00FF",
        "L#100",
        "INT#5",
        "INT#-5",
        "REAL#1.5",
        "WSTRING#'abc'",
    ]
).map(lambda t: Literal("typed", t))
addresses = st.sampled_from(["%I0.0", "%IW64", "%QW80", "%MD20", "%M12.1", "%Q4.7"]).map(AddressRef)

names: st.SearchStrategy[Expr] = st.one_of(
    idents.map(LocalRef),
    spaced_names.map(LocalRef),
    idents.map(GlobalRef),
    spaced_names.map(GlobalRef),
    idents.map(Ident),
)
literals: st.SearchStrategy[Expr] = st.one_of(int_lits, real_lits, bool_lits, str_lits, typed_lits)

UNARY = ["-", "+", "NOT"]
BINARY = ["+", "-", "*", "/", "MOD", "**", "=", "<>", "<", ">", "<=", ">=", "AND", "&", "OR", "XOR"]


def postfix_of(base: st.SearchStrategy[Expr], inner: st.SearchStrategy[Expr]) -> st.SearchStrategy[Expr]:
    """Доступ к элементу, индекс, срез и вызов поверх имени (не поверх литерала: '5.3' — это REAL)."""
    args = st.one_of(
        inner.map(lambda v: Arg(None, v)),
        st.tuples(idents, inner).map(lambda t: Arg(t[0], t[1])),
        st.tuples(idents, inner).map(lambda t: Arg(t[0], t[1], True)),
    )
    return st.one_of(
        st.tuples(base, idents).map(lambda t: Member(t[0], t[1])),
        st.tuples(base, spaced_names).map(lambda t: Member(t[0], t[1], quoted=True)),
        st.tuples(base, st.lists(inner, min_size=1, max_size=2)).map(lambda t: Index(t[0], tuple(t[1]))),
        st.tuples(base, st.sampled_from(["X", "B", "W", "D", ""]), st.integers(0, 31)).map(
            lambda t: Slice(t[0], t[1], t[2])
        ),
        st.tuples(base, st.lists(args, max_size=3)).map(lambda t: Call(t[0], tuple(t[1]))),
    )


def extend(inner: st.SearchStrategy[Expr]) -> st.SearchStrategy[Expr]:
    return st.one_of(
        st.tuples(st.sampled_from(UNARY), inner).map(lambda t: Unary(t[0], t[1])),
        st.tuples(st.sampled_from(BINARY), inner, inner).map(lambda t: Binary(t[0], t[1], t[2])),
        postfix_of(names, inner),
        # срез .%Xn поверх адреса: '%MW10.%X3' лексер разбирает однозначно
        st.tuples(addresses, st.integers(0, 15)).map(lambda t: Slice(t[0], "X", t[1])),
    )


expressions: st.SearchStrategy[Expr] = st.recursive(st.one_of(literals, names, addresses), extend, max_leaves=24)


@settings(max_examples=600, deadline=None)
@given(expressions)
def test_parse_print_roundtrip(expr: Expr) -> None:
    text = expr_to_scl(expr)
    assert parse_expression(text) == expr, text


@settings(max_examples=200, deadline=None)
@given(expressions)
def test_print_is_stable(expr: Expr) -> None:
    once = expr_to_scl(expr)
    assert expr_to_scl(parse_expression(once)) == once


def test_minimal_parentheses_examples() -> None:
    cases = {
        "#a + #b * #c": "#a + #b * #c",
        "(#a + #b) * #c": "(#a + #b) * #c",
        "#a - (#b - #c)": "#a - (#b - #c)",
        "NOT (#a AND #b)": "NOT (#a AND #b)",
        "-#a ** 2": "-#a ** 2",
        "(-#a) ** 2": "(-#a) ** 2",
        "2 ** (-1)": "2 ** (-1)",
        "#a * -#b": "#a * -#b",
        "-(-#a)": "-(-#a)",
    }
    for source, printed in cases.items():
        assert expr_to_scl(parse_expression(source)) == printed
