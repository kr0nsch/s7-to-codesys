"""Разбор SCL (TIA Portal external source) в AST — рекурсивный спуск.

Почему не lark (обоснование — docs/GRAMMAR.md, раздел «Выбор подхода»):
- восстановление после ошибок на уровне оператора и объявления: неразобранный оператор
  становится RawStmt (исходный текст + причина), разбор продолжается со следующего;
- комментарии привязываются к операторам и объявлениям (переносятся в ST);
- контекстные части лексики (строки заголовка блока, имя REGION, литералы DT#...) проще
  разобрать вручную, чем описать грамматикой без конфликтов.

Приоритеты операций SCL (от сильного к слабому): ( ), вызов и доступ (. [ ] ( )), **, унарные
- + NOT, * / MOD, + -, < > <= >=, = <>, AND &, XOR, OR. Бинарные операции левоассоциативны.
"""

from __future__ import annotations

import re

from s7conv import lexer as lx
from s7conv.lexer import Token, tokenize
from s7conv.nodes import (
    BLOCK_DB,
    BLOCK_FC,
    BLOCK_KINDS,
    BLOCK_UDT,
    Arg,
    ArrayInit,
    ArrayType,
    Assign,
    Binary,
    Block,
    Call,
    CallStmt,
    Case,
    CaseClause,
    CaseLabel,
    CaseRange,
    Comment,
    CommentStmt,
    Continue,
    Empty,
    Exit,
    Expr,
    For,
    GlobalRef,
    Goto,
    Ident,
    If,
    Index,
    Label,
    Literal,
    LocalRef,
    Member,
    NamedType,
    ParseIssue,
    Pragma,
    RawBlock,
    RawDecl,
    RawStmt,
    RefType,
    Region,
    Repeat,
    Return,
    Slice,
    SourceFile,
    Span,
    Stmt,
    StringType,
    StructType,
    TypeRef,
    Unary,
    VarDecl,
    VarSection,
    While,
)
from s7conv.nodes import AddressRef as AddrRef

SECTION_KEYWORDS = frozenset({"VAR_INPUT", "VAR_OUTPUT", "VAR_IN_OUT", "VAR", "VAR_TEMP", "VAR_STAT", "CONST", "LABEL"})
SECTION_MODIFIERS = frozenset({"CONSTANT", "RETAIN", "NON_RETAIN", "DB_SPECIFIC", "PERSISTENT"})
BLOCK_FLAGS = frozenset(
    {"NON_RETAIN", "RETAIN", "KNOW_HOW_PROTECT", "READ_ONLY", "UNLINKED", "CODE_VERSION1", "NON_OPTIMIZED"}
)
BLOCK_ENDS = {kind: "END_" + kind for kind in BLOCK_KINDS}
BLOCK_END_WORDS = frozenset(BLOCK_ENDS.values())
COMPOUND_ENDS = {
    "IF": "END_IF",
    "CASE": "END_CASE",
    "FOR": "END_FOR",
    "WHILE": "END_WHILE",
    "REPEAT": "END_REPEAT",
    "REGION": "END_REGION",
}
# Слова, которые не могут быть именем в выражении
RESERVED = frozenset(
    {
        "IF",
        "THEN",
        "ELSIF",
        "ELSE",
        "END_IF",
        "CASE",
        "OF",
        "END_CASE",
        "FOR",
        "TO",
        "BY",
        "DO",
        "END_FOR",
        "WHILE",
        "END_WHILE",
        "REPEAT",
        "UNTIL",
        "END_REPEAT",
        "EXIT",
        "CONTINUE",
        "RETURN",
        "GOTO",
        "REGION",
        "END_REGION",
        "AND",
        "OR",
        "XOR",
        "NOT",
        "MOD",
        "BEGIN",
        "VAR",
        "VAR_INPUT",
        "VAR_OUTPUT",
        "VAR_IN_OUT",
        "VAR_TEMP",
        "END_VAR",
        "END_STRUCT",
    }
    | BLOCK_END_WORDS
    | frozenset(BLOCK_KINDS)
)
_ATTR_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*:=\s*'([^']*)'")


class ParseError(Exception):
    def __init__(self, message: str, token: Token) -> None:
        super().__init__(message)
        self.message = message
        self.token = token


def parse_attributes(text: str) -> dict[str, str]:
    """Атрибуты S7 из прагмы: `S7_Optimized_Access := 'TRUE'; ExternalVisible := 'False'`."""
    return {m.group(1): m.group(2) for m in _ATTR_RE.finditer(text)}


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def _describe(tok: Token) -> str:
    if tok.kind == lx.EOF:
        return "конец файла"
    if tok.kind == lx.ERROR:
        return f"ошибка лексики ({tok.value}): {tok.text!r}"
    return repr(tok.text)


class Parser:
    def __init__(self, text: str, path: str = "") -> None:
        self.text = text
        self.path = path
        self.toks = tokenize(text)
        self.i = 0
        self.issues: list[ParseIssue] = []

    # -- навигация -------------------------------------------------------------
    def peek(self, k: int = 0) -> Token:
        j = min(self.i + k, len(self.toks) - 1)
        return self.toks[j]

    def next(self) -> Token:
        tok = self.toks[self.i]
        if tok.kind != lx.EOF:
            self.i += 1
        return tok

    def at_kw(self, *words: str) -> bool:
        return self.peek().is_kw(*words)

    def at_op(self, *ops: str) -> bool:
        return self.peek().is_op(*ops)

    def expect_kw(self, word: str) -> Token:
        tok = self.peek()
        if not tok.is_kw(word):
            raise ParseError(f"ожидалось {word}, найдено {_describe(tok)}", tok)
        return self.next()

    def expect_op(self, op: str) -> Token:
        tok = self.peek()
        if not tok.is_op(op):
            raise ParseError(f"ожидалось '{op}', найдено {_describe(tok)}", tok)
        return self.next()

    def span(self, start: int, stop: int) -> Span:
        """Позиция токенов [start, stop)."""
        first = self.toks[start]
        last = self.toks[max(start, stop - 1)]
        return Span(first.line, last.line, first.pos, last.end)

    @staticmethod
    def take(tok: Token) -> list[Comment]:
        comments = tok.comments
        tok.comments = []
        return comments

    def take_trailing(self) -> list[Comment]:
        """Комментарии в той же строке, что и предыдущий токен (после ';')."""
        tok = self.peek()
        prev_line = self.toks[self.i - 1].line if self.i > 0 else -1
        same = [c for c in tok.comments if not c.own_line and c.line == prev_line]
        if same:
            tok.comments = [c for c in tok.comments if c not in same]
        return same

    def take_inner(self, start: int, stop: int) -> list[Comment]:
        result: list[Comment] = []
        for j in range(start + 1, stop):
            if self.toks[j].comments:
                result.extend(self.take(self.toks[j]))
        return result

    def issue(self, tok: Token, message: str, severity: str = "error") -> None:
        self.issues.append(ParseIssue(tok.line, tok.col, message, severity))

    # -- файл ----------------------------------------------------------------------
    def parse_file(self) -> SourceFile:
        result = SourceFile(path=self.path, text=self.text)
        while self.peek().kind != lx.EOF:
            tok = self.peek()
            if tok.kind == lx.IDENT and tok.upper in BLOCK_KINDS:
                result.blocks.append(self.block())
            else:
                start = self.i
                while self.peek().kind != lx.EOF and not (
                    self.peek().kind == lx.IDENT and self.peek().upper in BLOCK_KINDS
                ):
                    self.next()
                span = self.span(start, self.i)
                text = self.text[span.start : span.end]
                self.issue(tok, "текст вне блока пропущен")
                result.blocks.append(RawBlock(kind="", name="", text=text, reason="текст вне блока", span=span))
        result.issues = self.issues
        return result

    # -- блоки -----------------------------------------------------------------------
    def block(self) -> Block | RawBlock:
        start = self.i
        kw_tok = self.peek()
        kind = kw_tok.upper
        preamble = self.take(kw_tok)
        try:
            blk = self._block(kind)
            blk.preamble = preamble
            blk.span = self.span(start, self.i)
            return blk
        except ParseError as exc:
            self.i = start
            end_word = BLOCK_ENDS[kind]
            self.next()
            while self.peek().kind != lx.EOF and not self.at_kw(end_word):
                if self.peek().kind == lx.IDENT and self.peek().upper in BLOCK_KINDS and self._line_start(self.peek()):
                    break
                self.next()
            if self.at_kw(end_word):
                self.next()
            span = self.span(start, self.i)
            name_tok = self.toks[start + 1] if start + 1 < len(self.toks) else kw_tok
            name = str(name_tok.value) if name_tok.kind == lx.QIDENT else name_tok.text
            self.issue(exc.token, f"блок {kind} {name}: {exc.message}")
            return RawBlock(kind=kind, name=name, text=self.text[span.start : span.end], reason=exc.message, span=span)

    def _line_start(self, tok: Token) -> bool:
        line_begin = self.text.rfind("\n", 0, tok.pos) + 1
        return self.text[line_begin : tok.pos].strip() == ""

    def _block(self, kind: str) -> Block:
        self.next()
        name_tok = self.next()
        if name_tok.kind == lx.QIDENT:
            name, quoted = str(name_tok.value), True
        elif name_tok.kind == lx.IDENT:
            name, quoted = name_tok.text, False
        else:
            raise ParseError(f"ожидалось имя блока, найдено {_describe(name_tok)}", name_tok)
        blk = Block(kind=kind, name=name, quoted=quoted, span=Span(name_tok.line, name_tok.line, 0, 0))
        if kind == BLOCK_FC:
            if self.at_op(":"):
                self.next()
                blk.return_type = self.type_ref()
            else:
                blk.return_type = NamedType("Void")
        if kind == BLOCK_UDT and self.at_op(":"):
            self.next()
        self.block_header(blk)
        blk.comments.extend(self.take(self.peek()))
        end_word = BLOCK_ENDS[kind]
        if kind == BLOCK_UDT:
            if self.at_kw("STRUCT"):
                self.next()
                blk.struct = self.struct_body()
                if self.at_op(";"):
                    self.next()
            else:
                blk.db_type = self.type_ref()
                if self.at_op(";"):
                    self.next()
        elif kind == BLOCK_DB:
            if self.at_section():
                self.sections(blk)
            elif self.at_kw("STRUCT"):
                self.next()
                blk.struct = self.struct_body()
                if self.at_op(";"):
                    self.next()
            elif not self.at_kw("BEGIN", end_word):
                blk.db_type = self.type_ref()
                # компактная форма DATA_BLOCK "DB" "FB": атрибуты и VERSION идут после типа
                self.block_header(blk)
                blk.comments.extend(self.take(self.peek()))
            if self.at_kw("BEGIN"):
                self.next()
            blk.body = self.body({end_word})
        else:
            self.sections(blk)
            if self.at_kw("BEGIN"):
                self.next()
            blk.body = self.body({end_word})
        self.expect_kw(end_word)
        if self.at_op(";"):
            self.next()
        return blk

    def block_header(self, blk: Block) -> None:
        while True:
            tok = self.peek()
            if tok.kind == lx.HEADER_PROP:
                self.next()
                blk.comments.extend(self.take(tok))
                assert isinstance(tok.value, tuple)
                key, value = tok.value
                value = _strip_quotes(str(value).strip())
                if key == "TITLE":
                    blk.title = value
                else:
                    blk.props[str(key)] = value
            elif tok.kind == lx.PRAGMA:
                self.next()
                blk.comments.extend(self.take(tok))
                blk.attributes.update(parse_attributes(str(tok.value)))
            elif tok.kind == lx.IDENT and tok.upper in BLOCK_FLAGS:
                self.next()
                blk.comments.extend(self.take(tok))
                blk.flags.append(tok.upper)
            else:
                return

    # -- секции переменных -----------------------------------------------------------
    def at_section(self) -> bool:
        """Ключевое слово секции, а не объявление переменной с таким именем (`label : String;`)."""
        tok = self.peek()
        return tok.kind == lx.IDENT and tok.upper in SECTION_KEYWORDS and not self.peek(1).is_op(":", ",", ":=")

    def sections(self, blk: Block) -> None:
        while self.at_section():
            blk.sections.append(self.section())

    def section(self) -> VarSection:
        start = self.i
        kw_tok = self.next()
        sec = VarSection(kind=kw_tok.upper, span=Span(kw_tok.line, kw_tok.line, kw_tok.pos, kw_tok.end))
        sec.comments = self.take(kw_tok)
        while self.peek().kind == lx.IDENT and self.peek().upper in SECTION_MODIFIERS:
            sec.modifiers.append(self.next().upper)
        if sec.kind == "CONST":
            end_word = "END_CONST"
        elif sec.kind == "LABEL":
            end_word = "END_LABEL"
        else:
            end_word = "END_VAR"
        while not self.at_kw(end_word):
            tok = self.peek()
            if tok.kind == lx.EOF or (tok.kind == lx.IDENT and (tok.upper in BLOCK_END_WORDS or tok.upper == "BEGIN")):
                raise ParseError(f"нет {end_word}", tok)
            if self.at_section():
                raise ParseError(f"нет {end_word} перед {tok.text}", tok)
            if sec.kind == "LABEL":
                sec.items.append(self.raw_decl("метки GOTO (LABEL) не поддерживаются"))
            elif sec.kind == "CONST":
                sec.items.append(self.decl(const=True))
            else:
                sec.items.append(self.decl())
        sec.end_comments = self.take(self.peek())
        self.next()
        if self.at_op(";"):
            self.next()
        sec.span = self.span(start, self.i)
        return sec

    def raw_decl(self, reason: str) -> RawDecl:
        start = self.i
        comments = self.take(self.peek())
        self.skip_simple()
        span = self.span(start, self.i)
        return RawDecl(text=self.text[span.start : span.end], reason=reason, span=span, comments=comments)

    def decl(self, const: bool = False) -> VarDecl | RawDecl:
        start = self.i
        leading = self.take(self.peek())
        try:
            item = self._decl(const)
        except ParseError as exc:
            self.i = start
            self.skip_simple()
            span = self.span(start, self.i)
            self.issue(exc.token, f"объявление не разобрано: {exc.message}")
            raw = RawDecl(text=self.text[span.start : span.end], reason=exc.message, span=span, comments=leading)
            raw.comments.extend(self.take_trailing())
            return raw
        item.comments = leading + self.take_inner(start, self.i)
        item.trailing = self.take_trailing()
        item.span = self.span(start, self.i)
        return item

    def _decl_name(self) -> str:
        tok = self.next()
        if tok.kind == lx.QIDENT:
            return str(tok.value)
        if tok.kind == lx.IDENT and tok.upper not in RESERVED:
            return tok.text
        raise ParseError(f"ожидалось имя переменной, найдено {_describe(tok)}", tok)

    def _decl(self, const: bool) -> VarDecl:
        names = [self._decl_name()]
        attributes: dict[str, str] = {}
        while True:
            if self.peek().kind == lx.PRAGMA:
                attributes.update(parse_attributes(str(self.next().value)))
                continue
            if self.at_op(","):
                self.next()
                names.append(self._decl_name())
                continue
            break
        if const:
            # классический SCL: CONST имя := значение; END_CONST
            self.expect_op(":=")
            value = self.expression()
            self.expect_op(";")
            return VarDecl(names=names, type=NamedType(""), init=value, span=Span(0, 0, 0, 0))
        at: Expr | None = None
        if self.at_kw("AT"):
            self.next()
            at = self.postfix()
        self.expect_op(":")
        typ = self.type_ref()
        while self.peek().kind == lx.PRAGMA:
            attributes.update(parse_attributes(str(self.next().value)))
        init: Expr | ArrayInit | None = None
        if self.at_op(":="):
            self.next()
            init = self.initializer()
        self.expect_op(";")
        return VarDecl(names=names, type=typ, init=init, attributes=attributes, at=at, span=Span(0, 0, 0, 0))

    def initializer(self) -> Expr | ArrayInit:
        if not self.at_op("["):
            return self.expression()
        self.next()
        items: list[tuple[Expr | None, Expr | ArrayInit]] = []
        while True:
            count: Expr | None = None
            if self.peek().kind == lx.INT and self.peek(1).is_op("("):
                count = Literal("int", self.next().text)
                self.next()
                value = self.initializer()
                self.expect_op(")")
            else:
                value = self.initializer()
            items.append((count, value))
            if self.at_op(","):
                self.next()
                continue
            break
        self.expect_op("]")
        return ArrayInit(tuple(items))

    # -- типы --------------------------------------------------------------------------
    def type_ref(self) -> TypeRef:
        tok = self.next()
        if tok.kind == lx.QIDENT:
            return NamedType(str(tok.value), quoted=True)
        if tok.kind != lx.IDENT:
            raise ParseError(f"ожидался тип, найдено {_describe(tok)}", tok)
        upper = tok.upper
        if upper in ("STRING", "WSTRING"):
            length: Expr | None = None
            if self.at_op("["):
                self.next()
                length = self.expression()
                self.expect_op("]")
            return StringType(wide=upper == "WSTRING", length=length)
        if upper == "ARRAY":
            self.expect_op("[")
            ranges: list[tuple[Expr, Expr] | None] = []
            while True:
                if self.at_op("*"):
                    self.next()
                    ranges.append(None)
                else:
                    lo = self.expression()
                    self.expect_op("..")
                    hi = self.expression()
                    ranges.append((lo, hi))
                if self.at_op(","):
                    self.next()
                    continue
                break
            self.expect_op("]")
            self.expect_kw("OF")
            return ArrayType(tuple(ranges), self.type_ref())
        if upper == "STRUCT":
            return self.struct_body()
        if upper == "REF_TO":
            return RefType(self.type_ref())
        if upper in RESERVED:
            raise ParseError(f"ожидался тип, найдено {_describe(tok)}", tok)
        return NamedType(tok.text)

    def struct_body(self) -> StructType:
        """Поля после STRUCT до END_STRUCT (END_STRUCT съедается, ';' — нет)."""
        decls: list[VarDecl | RawDecl] = []
        while not self.at_kw("END_STRUCT"):
            tok = self.peek()
            if tok.kind == lx.EOF or (tok.kind == lx.IDENT and tok.upper in BLOCK_END_WORDS):
                raise ParseError("нет END_STRUCT", tok)
            decls.append(self.decl())
        st = StructType(decls)
        end = self.next()
        if end.comments and decls:
            # комментарии перед END_STRUCT — к последнему полю
            decls[-1].comments.extend(self.take(end))
        return st

    # -- операторы -------------------------------------------------------------------
    def at_body_end(self, terminators: set[str]) -> bool:
        tok = self.peek()
        if tok.kind == lx.EOF:
            return True
        return tok.kind == lx.IDENT and (tok.upper in terminators or tok.upper in BLOCK_END_WORDS)

    def body(self, terminators: set[str]) -> list[Stmt]:
        out: list[Stmt] = []
        while not self.at_body_end(terminators):
            out.append(self.statement())
        self._closing_comments(out)
        return out

    def _closing_comments(self, out: list[Stmt]) -> None:
        tok = self.peek()
        if tok.comments:
            comments = self.take(tok)
            out.append(CommentStmt(span=Span(comments[0].line, comments[-1].line, tok.pos, tok.pos), comments=comments))

    def statement(self) -> Stmt:
        start = self.i
        leading = self.take(self.peek())
        try:
            stmt = self._statement()
        except ParseError as exc:
            self.i = start
            self.skip_statement()
            if self.i == start:
                self.next()
            span = self.span(start, self.i)
            self.issue(exc.token, f"оператор не разобран: {exc.message}")
            stmt = RawStmt(text=self.text[span.start : span.end], reason=exc.message, span=span)
            stmt.comments = leading
            stmt.trailing = self.take_trailing()
            return stmt
        stmt.span = self.span(start, self.i)
        stmt.comments = leading + self.take_inner(start, self.i) + stmt.comments
        stmt.trailing = self.take_trailing()
        return stmt

    def _end_compound(self, word: str) -> None:
        self.expect_kw(word)
        if self.at_op(";"):
            self.next()

    def _semicolon(self) -> None:
        if self.at_op(";"):
            self.next()
            return
        tok = self.peek()
        # TIA всегда ставит ';'; без него допускаем только перед концом списка операторов
        if tok.kind == lx.EOF or (
            tok.kind == lx.IDENT and (tok.upper.startswith("END_") or tok.upper in ("ELSE", "ELSIF", "UNTIL"))
        ):
            return
        raise ParseError(f"ожидалось ';', найдено {_describe(tok)}", tok)

    def _statement(self) -> Stmt:
        tok = self.peek()
        dummy = Span(tok.line, tok.line, tok.pos, tok.end)
        if tok.kind == lx.OP and tok.text == ";":
            self.next()
            return Empty(span=dummy)
        if tok.kind == lx.PRAGMA:
            self.next()
            return Pragma(text=tok.text, span=dummy)
        if tok.kind == lx.IDENT:
            upper = tok.upper
            if upper == "IF":
                return self.if_stmt()
            if upper == "CASE":
                return self.case_stmt()
            if upper == "FOR":
                return self.for_stmt()
            if upper == "WHILE":
                self.next()
                cond = self.expression()
                self.expect_kw("DO")
                body = self.body({"END_WHILE"})
                self._end_compound("END_WHILE")
                return While(cond=cond, body=body, span=dummy)
            if upper == "REPEAT":
                self.next()
                body = self.body({"UNTIL"})
                self.expect_kw("UNTIL")
                cond = self.expression()
                if self.at_op(";"):
                    self.next()
                self._end_compound("END_REPEAT")
                return Repeat(body=body, cond=cond, span=dummy)
            if upper == "REGION":
                self.next()
                name = ""
                if self.peek().kind == lx.REGION_NAME:
                    name = str(self.next().value)
                body = self.body({"END_REGION"})
                self._end_compound("END_REGION")
                return Region(name=name, body=body, span=dummy)
            if upper in ("EXIT", "CONTINUE", "RETURN"):
                self.next()
                self._semicolon()
                cls = {"EXIT": Exit, "CONTINUE": Continue, "RETURN": Return}[upper]
                return cls(span=dummy)
            if upper == "GOTO":
                self.next()
                label = self.next()
                if label.kind != lx.IDENT:
                    raise ParseError(f"ожидалась метка после GOTO, найдено {_describe(label)}", label)
                self._semicolon()
                return Goto(label=label.text, span=dummy)
            if upper in RESERVED:
                raise ParseError(f"неожиданное {tok.text}", tok)
            if self.peek(1).is_op(":"):
                self.next()
                self.next()
                return Label(name=tok.text, span=dummy)
        target = self.postfix()
        if self.at_op(":=", "+=", "-=", "*=", "/=", "?="):
            op = self.next().text
            value = self.expression()
            if self.at_op(":="):
                raise ParseError("множественное присваивание a := b := c не поддерживается", self.peek())
            self._semicolon()
            return Assign(target=target, value=value, op=op, span=dummy)
        if isinstance(target, Call):
            self._semicolon()
            return CallStmt(call=target, span=dummy)
        raise ParseError(f"ожидалось присваивание или вызов, найдено {_describe(self.peek())}", self.peek())

    def if_stmt(self) -> If:
        tok = self.next()
        branches: list[tuple[Expr, list[Stmt]]] = []
        cond = self.expression()
        self.expect_kw("THEN")
        branches.append((cond, self.body({"ELSIF", "ELSE", "END_IF"})))
        else_body: list[Stmt] | None = None
        while True:
            if self.at_kw("ELSIF"):
                self.next()
                cond = self.expression()
                self.expect_kw("THEN")
                branches.append((cond, self.body({"ELSIF", "ELSE", "END_IF"})))
                continue
            if self.at_kw("ELSE"):
                self.next()
                else_body = self.body({"END_IF"})
            break
        self._end_compound("END_IF")
        return If(branches=branches, else_body=else_body, span=Span(tok.line, tok.line, tok.pos, tok.end))

    def case_stmt(self) -> Case:
        tok = self.next()
        selector = self.expression()
        self.expect_kw("OF")
        clauses: list[CaseClause] = []
        else_body: list[Stmt] | None = None
        current: CaseClause | None = None
        while True:
            if self.at_kw("END_CASE") or self.peek().kind == lx.EOF or self.at_body_end(set()):
                if current is not None:
                    self._closing_comments(current.body)
                break
            if self.at_kw("ELSE"):
                if current is not None:
                    self._closing_comments(current.body)
                self.next()
                if self.at_op(":"):
                    self.next()
                else_body = self.body({"END_CASE"})
                break
            label_start = self.i
            labels = self.try_case_labels()
            if labels is not None:
                current = CaseClause(labels=labels, body=[], span=self.span(label_start, self.i))
                current.comments = self.take(self.toks[label_start])
                clauses.append(current)
                continue
            if current is None:
                raise ParseError(f"ожидалась метка CASE, найдено {_describe(self.peek())}", self.peek())
            current.body.append(self.statement())
        self._end_compound("END_CASE")
        return Case(selector=selector, clauses=clauses, else_body=else_body, span=Span(tok.line, tok.line, 0, 0))

    def try_case_labels(self) -> list[CaseLabel] | None:
        save = self.i
        try:
            labels: list[CaseLabel] = []
            while True:
                lo = self.additive()
                if self.at_op(".."):
                    self.next()
                    labels.append(CaseRange(lo, self.additive()))
                else:
                    labels.append(lo)
                if self.at_op(","):
                    self.next()
                    continue
                break
            self.expect_op(":")
            return labels
        except ParseError:
            self.i = save
            return None

    def for_stmt(self) -> For:
        tok = self.next()
        var = self.postfix()
        self.expect_op(":=")
        start = self.expression()
        self.expect_kw("TO")
        end = self.expression()
        step: Expr | None = None
        if self.at_kw("BY"):
            self.next()
            step = self.expression()
        self.expect_kw("DO")
        body = self.body({"END_FOR"})
        self._end_compound("END_FOR")
        return For(var=var, start=start, end=end, step=step, body=body, span=Span(tok.line, tok.line, 0, 0))

    # -- восстановление -----------------------------------------------------------------
    def skip_statement(self) -> None:
        tok = self.peek()
        if tok.kind == lx.IDENT and tok.upper in COMPOUND_ENDS:
            opener = tok.upper
            closer = COMPOUND_ENDS[opener]
            depth = 0
            while self.peek().kind != lx.EOF:
                cur = self.peek()
                if cur.kind == lx.IDENT and cur.upper in BLOCK_END_WORDS:
                    return
                self.next()
                if cur.is_kw(opener):
                    depth += 1
                elif cur.is_kw(closer):
                    depth -= 1
                    if depth == 0:
                        if self.at_op(";"):
                            self.next()
                        return
            return
        self.skip_simple()

    def skip_simple(self) -> None:
        """До ';' (включительно) на нулевой глубине скобок или до ключевого слова конца."""
        depth = 0
        first = True
        while self.peek().kind != lx.EOF:
            tok = self.peek()
            if not first and depth == 0 and tok.kind == lx.IDENT:
                if tok.upper.startswith("END_") or tok.upper in ("ELSE", "ELSIF", "UNTIL", "BEGIN"):
                    return
                if tok.upper in BLOCK_KINDS and self._line_start(tok):
                    return
            first = False
            self.next()
            if tok.is_op("(", "["):
                depth += 1
            elif tok.is_op(")", "]"):
                depth = max(0, depth - 1)
            elif tok.is_op(";") and depth == 0:
                return

    # -- выражения ----------------------------------------------------------------------
    def expression(self) -> Expr:
        return self.or_expr()

    def or_expr(self) -> Expr:
        left = self.xor_expr()
        while self.at_kw("OR"):
            self.next()
            left = Binary("OR", left, self.xor_expr())
        return left

    def xor_expr(self) -> Expr:
        left = self.and_expr()
        while self.at_kw("XOR"):
            self.next()
            left = Binary("XOR", left, self.and_expr())
        return left

    def and_expr(self) -> Expr:
        left = self.eq_expr()
        while self.at_kw("AND") or self.at_op("&"):
            op = "AND" if self.next().kind == lx.IDENT else "&"
            left = Binary(op, left, self.eq_expr())
        return left

    def eq_expr(self) -> Expr:
        left = self.rel_expr()
        while self.at_op("=", "<>"):
            op = self.next().text
            left = Binary(op, left, self.rel_expr())
        return left

    def rel_expr(self) -> Expr:
        left = self.additive()
        while self.at_op("<", ">", "<=", ">="):
            op = self.next().text
            left = Binary(op, left, self.additive())
        return left

    def additive(self) -> Expr:
        left = self.multiplicative()
        while self.at_op("+", "-"):
            op = self.next().text
            left = Binary(op, left, self.multiplicative())
        return left

    def multiplicative(self) -> Expr:
        left = self.unary()
        while self.at_op("*", "/") or self.at_kw("MOD"):
            tok = self.next()
            op = "MOD" if tok.kind == lx.IDENT else tok.text
            left = Binary(op, left, self.unary())
        return left

    def unary(self) -> Expr:
        if self.at_op("-", "+"):
            op = self.next().text
            return Unary(op, self.unary())
        if self.at_kw("NOT"):
            self.next()
            return Unary("NOT", self.unary())
        return self.power()

    def power(self) -> Expr:
        left = self.postfix()
        while self.at_op("**"):
            self.next()
            left = Binary("**", left, self.power_operand())
        return left

    def power_operand(self) -> Expr:
        if self.at_op("-", "+"):
            op = self.next().text
            return Unary(op, self.power_operand())
        if self.at_kw("NOT"):
            self.next()
            return Unary("NOT", self.power_operand())
        return self.postfix()

    def postfix(self) -> Expr:
        expr = self.primary()
        while True:
            if self.at_op("."):
                dot = self.next()
                tok = self.next()
                if tok.kind == lx.IDENT:
                    expr = Member(expr, tok.text)
                elif tok.kind == lx.QIDENT:
                    expr = Member(expr, str(tok.value), quoted=True)
                elif tok.kind == lx.ADDRESS and re.fullmatch(r"%[XBWDxbwd]\d+", tok.text):
                    expr = Slice(expr, tok.text[1].upper(), int(tok.text[2:]))
                elif tok.kind == lx.INT and tok.text.isdigit():
                    expr = Slice(expr, "", int(tok.text))
                else:
                    raise ParseError(f"ожидалось имя после '.', найдено {_describe(tok)}", dot)
            elif self.at_op("["):
                self.next()
                indices = [self.expression()]
                while self.at_op(","):
                    self.next()
                    indices.append(self.expression())
                self.expect_op("]")
                expr = Index(expr, tuple(indices))
            elif self.at_op("("):
                self.next()
                expr = Call(expr, tuple(self.arguments()))
            else:
                return expr

    def arguments(self) -> list[Arg]:
        args: list[Arg] = []
        if self.at_op(")"):
            self.next()
            return args
        while True:
            tok = self.peek()
            if tok.kind == lx.IDENT and self.peek(1).is_op(":=", "=>"):
                self.next()
                output = self.next().text == "=>"
                args.append(Arg(tok.text, self.expression(), output))
            else:
                args.append(Arg(None, self.expression()))
            if self.at_op(","):
                self.next()
                continue
            break
        self.expect_op(")")
        return args

    def primary(self) -> Expr:
        tok = self.peek()
        kind = tok.kind
        if kind == lx.INT:
            self.next()
            return Literal("int", tok.text)
        if kind == lx.REAL:
            self.next()
            return Literal("real", tok.text)
        if kind == lx.STRING:
            self.next()
            return Literal("string", tok.text)
        if kind == lx.TYPED:
            self.next()
            return Literal("typed", tok.text)
        if kind == lx.LOCAL:
            self.next()
            return LocalRef(str(tok.value))
        if kind == lx.QIDENT:
            self.next()
            return GlobalRef(str(tok.value))
        if kind == lx.ADDRESS:
            self.next()
            return AddrRef(tok.text)
        if kind == lx.IDENT:
            upper = tok.upper
            if upper in ("TRUE", "FALSE"):
                self.next()
                return Literal("bool", tok.text)
            if upper in RESERVED:
                raise ParseError(f"неожиданное {tok.text} в выражении", tok)
            self.next()
            return Ident(tok.text)
        if tok.is_op("("):
            self.next()
            inner = self.expression()
            self.expect_op(")")
            return inner
        raise ParseError(f"ожидалось выражение, найдено {_describe(tok)}", tok)


def parse_source(text: str, path: str = "") -> SourceFile:
    """Разбор файла SCL: блоки, замечания разбора (issues)."""
    return Parser(text, path).parse_file()


def parse_expression(text: str) -> Expr:
    """Разбор одного выражения (для тестов); остаток текста — ошибка."""
    parser = Parser(text)
    expr = parser.expression()
    if parser.peek().kind != lx.EOF:
        raise ParseError(f"лишний текст после выражения: {_describe(parser.peek())}", parser.peek())
    return expr


def parse_statements(text: str) -> tuple[list[Stmt], list[ParseIssue]]:
    """Разбор списка операторов (для тестов)."""
    parser = Parser(text)
    body = parser.body(set())
    return body, parser.issues
