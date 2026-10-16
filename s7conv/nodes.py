"""Модель AST подмножества SCL (TIA Portal external source).

Выражения — неизменяемые dataclass без позиций: равенство структурное, это нужно тесту
«разбор ∘ печать» (hypothesis). Позиции и комментарии хранятся у операторов, объявлений и
блоков; у операторов они не участвуют в сравнении (compare=False).

Грамматика подмножества — docs/GRAMMAR.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeAlias

# ---------------------------------------------------------------------------
# Позиции и комментарии
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Span:
    """Фрагмент исходника: строки (с 1) и смещения [start, end) в тексте файла."""

    line: int
    end_line: int
    start: int
    end: int


@dataclass(frozen=True)
class Comment:
    """Комментарий исходника. style: '//' или '(*'. own_line — в строке нет кода перед ним."""

    text: str
    line: int
    style: str
    own_line: bool


# ---------------------------------------------------------------------------
# Выражения
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Literal:
    """Литерал. kind: int, real, bool, string, typed (T#5s, INT#3, 16#FF, B#16#FF ...)."""

    kind: str
    text: str


@dataclass(frozen=True)
class LocalRef:
    """Локальная переменная блока: #name (или #"name")."""

    name: str


@dataclass(frozen=True)
class GlobalRef:
    """Глобальный символ в кавычках: "DB", "Tag", "FC_Name"."""

    name: str


@dataclass(frozen=True)
class Ident:
    """Имя без префикса: функция (ABS, NORM_X), ENO, переменная классического SCL."""

    name: str


@dataclass(frozen=True)
class AddressRef:
    """Прямой адрес: %I0.0, %IW64, %MD10, %Q4.1, %DB1.DBX0.0 (текст как в исходнике)."""

    text: str


@dataclass(frozen=True)
class Member:
    """Доступ к элементу: base.name (quoted — имя было в кавычках)."""

    base: Expr
    name: str
    quoted: bool = False


@dataclass(frozen=True)
class Index:
    """Индекс массива: base[i] или base[i, j]."""

    base: Expr
    indices: tuple[Expr, ...]


@dataclass(frozen=True)
class Slice:
    """Срез S7: base.%X3 (size 'X'), .%B1, .%W0, .%D0; size '' — форма base.3."""

    base: Expr
    size: str
    number: int


@dataclass(frozen=True)
class Arg:
    """Аргумент вызова: позиционный (name None), name := value или name => value (output)."""

    name: str | None
    value: Expr
    output: bool = False


@dataclass(frozen=True)
class Call:
    """Вызов: функции, FC, экземпляра ФБ (#inst(...), "IDB"(...)) или "DB".TON(...)."""

    callee: Expr
    args: tuple[Arg, ...]


@dataclass(frozen=True)
class Unary:
    """Унарная операция: '-', '+', 'NOT'."""

    op: str
    operand: Expr


@dataclass(frozen=True)
class Binary:
    """Бинарная операция. op — как в исходнике в верхнем регистре: '+', 'AND', '&', '**', 'MOD' ..."""

    op: str
    left: Expr
    right: Expr


Expr: TypeAlias = Literal | LocalRef | GlobalRef | Ident | AddressRef | Member | Index | Slice | Call | Unary | Binary


@dataclass(frozen=True)
class ArrayInit:
    """Начальное значение массива: [1, 2, 3(0)] — элементы (повтор или None, значение)."""

    items: tuple[tuple[Expr | None, Expr | ArrayInit], ...]


# ---------------------------------------------------------------------------
# Типы
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NamedType:
    """Тип по имени: Int, Bool, TON_TIME, IEC_TIMER, "UDT_Motor" (quoted), "FB_Valve"."""

    name: str
    quoted: bool = False


@dataclass(frozen=True)
class StringType:
    """String / String[n] / WString[n]; length None — длина по умолчанию (254)."""

    wide: bool
    length: Expr | None


@dataclass(frozen=True)
class ArrayType:
    """Array[lo..hi, ...] of element; диапазон None — Array[*]."""

    ranges: tuple[tuple[Expr, Expr] | None, ...]
    element: TypeRef


@dataclass(frozen=True)
class RefType:
    """REF_TO <тип> (не поддерживается эмиттером)."""

    target: TypeRef


@dataclass(eq=True)
class StructType:
    """Анонимная структура: Struct ... END_STRUCT."""

    decls: list[VarDecl | RawDecl]


TypeRef: TypeAlias = NamedType | StringType | ArrayType | RefType | StructType


# ---------------------------------------------------------------------------
# Объявления
# ---------------------------------------------------------------------------


@dataclass(kw_only=True)
class VarDecl:
    """Объявление: a, b {attrs} : type := init; // комментарий."""

    names: list[str]
    type: TypeRef
    init: Expr | ArrayInit | None = None
    attributes: dict[str, str] = field(default_factory=dict)
    at: Expr | None = None
    span: Span = field(compare=False)
    comments: list[Comment] = field(default_factory=list, compare=False)
    trailing: list[Comment] = field(default_factory=list, compare=False)


@dataclass(kw_only=True)
class RawDecl:
    """Объявление, которое не удалось разобрать (исходный текст и причина)."""

    text: str
    reason: str
    span: Span = field(compare=False)
    comments: list[Comment] = field(default_factory=list, compare=False)


@dataclass(kw_only=True)
class VarSection:
    """Секция переменных: kind VAR_INPUT/VAR_OUTPUT/VAR_IN_OUT/VAR/VAR_TEMP/CONST; modifiers RETAIN, ..."""

    kind: str
    modifiers: list[str] = field(default_factory=list)
    items: list[VarDecl | RawDecl] = field(default_factory=list)
    span: Span = field(compare=False)
    comments: list[Comment] = field(default_factory=list, compare=False)
    end_comments: list[Comment] = field(default_factory=list, compare=False)


# ---------------------------------------------------------------------------
# Операторы
# ---------------------------------------------------------------------------


@dataclass(kw_only=True)
class Stmt:
    """Базовый класс оператора: позиция и комментарии не участвуют в сравнении."""

    span: Span = field(compare=False)
    comments: list[Comment] = field(default_factory=list, compare=False)
    trailing: list[Comment] = field(default_factory=list, compare=False)


@dataclass(kw_only=True)
class Assign(Stmt):
    target: Expr
    value: Expr
    op: str = ":="


@dataclass(kw_only=True)
class CallStmt(Stmt):
    call: Call


@dataclass(kw_only=True)
class If(Stmt):
    branches: list[tuple[Expr, list[Stmt]]]
    else_body: list[Stmt] | None = None


@dataclass(frozen=True)
class CaseRange:
    lo: Expr
    hi: Expr


CaseLabel: TypeAlias = Expr | CaseRange


@dataclass(kw_only=True)
class CaseClause:
    labels: list[CaseLabel]
    body: list[Stmt]
    span: Span = field(compare=False)
    comments: list[Comment] = field(default_factory=list, compare=False)


@dataclass(kw_only=True)
class Case(Stmt):
    selector: Expr
    clauses: list[CaseClause]
    else_body: list[Stmt] | None = None


@dataclass(kw_only=True)
class For(Stmt):
    var: Expr
    start: Expr
    end: Expr
    step: Expr | None
    body: list[Stmt]


@dataclass(kw_only=True)
class While(Stmt):
    cond: Expr
    body: list[Stmt]


@dataclass(kw_only=True)
class Repeat(Stmt):
    body: list[Stmt]
    cond: Expr


@dataclass(kw_only=True)
class Exit(Stmt):
    pass


@dataclass(kw_only=True)
class Continue(Stmt):
    pass


@dataclass(kw_only=True)
class Return(Stmt):
    pass


@dataclass(kw_only=True)
class Goto(Stmt):
    label: str


@dataclass(kw_only=True)
class Label(Stmt):
    name: str


@dataclass(kw_only=True)
class Region(Stmt):
    name: str
    body: list[Stmt]


@dataclass(kw_only=True)
class Empty(Stmt):
    """Пустой оператор ';'."""


@dataclass(kw_only=True)
class CommentStmt(Stmt):
    """Только комментарии (перед END_IF, в конце тела и т. п.)."""


@dataclass(kw_only=True)
class Pragma(Stmt):
    text: str


@dataclass(kw_only=True)
class RawStmt(Stmt):
    """Оператор, который не удалось разобрать: исходный текст и причина."""

    text: str
    reason: str


# ---------------------------------------------------------------------------
# Блоки и файл
# ---------------------------------------------------------------------------

BLOCK_FB = "FUNCTION_BLOCK"
BLOCK_FC = "FUNCTION"
BLOCK_OB = "ORGANIZATION_BLOCK"
BLOCK_DB = "DATA_BLOCK"
BLOCK_UDT = "TYPE"
BLOCK_KINDS = (BLOCK_FB, BLOCK_FC, BLOCK_OB, BLOCK_DB, BLOCK_UDT)


@dataclass(kw_only=True)
class Block:
    """Блок S7: FUNCTION_BLOCK, FUNCTION, ORGANIZATION_BLOCK, DATA_BLOCK, TYPE."""

    kind: str
    name: str
    quoted: bool = False
    return_type: TypeRef | None = None
    title: str | None = None
    props: dict[str, str] = field(default_factory=dict)
    flags: list[str] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)
    sections: list[VarSection] = field(default_factory=list)
    body: list[Stmt] = field(default_factory=list)
    db_type: TypeRef | None = None
    struct: StructType | None = None
    span: Span = field(compare=False)
    comments: list[Comment] = field(default_factory=list, compare=False)
    preamble: list[Comment] = field(default_factory=list, compare=False)


@dataclass(kw_only=True)
class RawBlock:
    """Блок (или текст вне блоков), который не удалось разобрать."""

    kind: str
    name: str
    text: str
    reason: str
    span: Span = field(compare=False)


@dataclass(frozen=True)
class ParseIssue:
    """Замечание разбора: severity error (конструкция не разобрана) или warning."""

    line: int
    col: int
    message: str
    severity: str = "error"


@dataclass(kw_only=True)
class SourceFile:
    path: str
    text: str
    blocks: list[Block | RawBlock] = field(default_factory=list)
    issues: list[ParseIssue] = field(default_factory=list)
