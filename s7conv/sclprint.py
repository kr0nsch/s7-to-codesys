"""Печать выражений AST обратно в SCL с минимальными скобками.

Свойство (проверяется hypothesis в tests/test_roundtrip.py): parse_expression(expr_to_scl(e)) == e для
любого выражения e, которое может вернуть разборщик. Скобки ставятся по приоритетам SCL:
левый операнд — если его приоритет ниже, правый — если ниже или равен (левая ассоциативность);
унарный операнд и операнды '**' в скобках, если это унарная операция.
"""

from __future__ import annotations

import re

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

PREC = {
    "OR": 1,
    "XOR": 2,
    "AND": 3,
    "&": 3,
    "=": 4,
    "<>": 4,
    "<": 5,
    ">": 5,
    "<=": 5,
    ">=": 5,
    "+": 6,
    "-": 6,
    "*": 7,
    "/": 7,
    "MOD": 7,
    "**": 9,
}
UNARY_PREC = 8
PRIMARY = 10
_PLAIN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")


def precedence(e: Expr) -> int:
    if isinstance(e, Binary):
        return PREC[e.op]
    if isinstance(e, Unary):
        return UNARY_PREC
    return PRIMARY


def _name(name: str) -> str:
    return name if _PLAIN.match(name) else f'"{name}"'


def _postfix_base(e: Expr) -> str:
    text = expr_to_scl(e)
    return text if precedence(e) >= PRIMARY else f"({text})"


def _arg(a: Arg) -> str:
    value = expr_to_scl(a.value)
    if a.name is None:
        return value
    return f"{a.name} {'=>' if a.output else ':='} {value}"


def expr_to_scl(e: Expr) -> str:
    if isinstance(e, Literal):
        return e.text
    if isinstance(e, LocalRef):
        return "#" + _name(e.name)
    if isinstance(e, GlobalRef):
        return f'"{e.name}"'
    if isinstance(e, Ident):
        return e.name
    if isinstance(e, AddressRef):
        return e.text
    if isinstance(e, Member):
        member = f'"{e.name}"' if e.quoted else e.name
        return f"{_postfix_base(e.base)}.{member}"
    if isinstance(e, Index):
        return f"{_postfix_base(e.base)}[{', '.join(expr_to_scl(i) for i in e.indices)}]"
    if isinstance(e, Slice):
        suffix = f"%{e.size}{e.number}" if e.size else str(e.number)
        return f"{_postfix_base(e.base)}.{suffix}"
    if isinstance(e, Call):
        return f"{_postfix_base(e.callee)}({', '.join(_arg(a) for a in e.args)})"
    if isinstance(e, Unary):
        operand = expr_to_scl(e.operand)
        if precedence(e.operand) < UNARY_PREC or isinstance(e.operand, Unary):
            operand = f"({operand})"
        return f"NOT {operand}" if e.op == "NOT" else f"{e.op}{operand}"
    prec = PREC[e.op]
    left = expr_to_scl(e.left)
    right = expr_to_scl(e.right)
    if precedence(e.left) < prec or (e.op == "**" and isinstance(e.left, Unary)):
        left = f"({left})"
    if precedence(e.right) <= prec or (e.op == "**" and isinstance(e.right, Unary)):
        right = f"({right})"
    return f"{left} {e.op} {right}"
