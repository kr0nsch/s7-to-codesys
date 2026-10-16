"""Лексер SCL в формате внешнего источника TIA Portal (*.scl).

Особенности, ради которых лексер написан вручную (а не правилами lark):
- `#name` и `#"имя с пробелом"` — локальные переменные; `"DB"` — глобальный символ, а не строка;
- литералы с префиксом: T#5s, S5T#2s, DT#2024-01-01-12:00:00, TOD#08:30:00, D#2024-01-01,
  16#FF, B#16#FF, L#5, INT#-5, REAL#1.5, WSTRING#'...'; тело литерала зависит от префикса
  (в DT# есть '-' и ':');
- прямые адреса %I0.0, %IW64, %MD10, %Q4.1:P, %DB1.DBX0.0 и срезы .%X3;
- строки свойств заголовка блока (TITLE = ..., AUTHOR : ..., VERSION : ...) — до конца строки,
  но только в «зоне заголовка» (до первой секции VAR/BEGIN/STRUCT): `name : String;` в секции
  VAR — обычное объявление;
- имя REGION — остаток строки;
- комментарии // и (* *) не теряются: каждый токен хранит комментарии перед ним.

Неизвестный символ даёт токен ERROR (разбор оператора с ним завершится восстановлением).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from s7conv.nodes import Comment

# Виды токенов
IDENT = "IDENT"  # имя или ключевое слово (сравнение без учёта регистра — через .upper)
QIDENT = "QIDENT"  # "символ"
LOCAL = "LOCAL"  # #имя
INT = "INT"
REAL = "REAL"
STRING = "STRING"  # 'строка'
TYPED = "TYPED"  # префикс#значение
ADDRESS = "ADDRESS"  # %...
OP = "OP"
PRAGMA = "PRAGMA"  # { ... }
HEADER_PROP = "HEADER_PROP"  # TITLE/AUTHOR/FAMILY/NAME/VERSION (value = (ключ, значение))
REGION_NAME = "REGION_NAME"  # остаток строки после REGION
ERROR = "ERROR"
EOF = "EOF"

BLOCK_KEYWORDS = frozenset({"FUNCTION_BLOCK", "FUNCTION", "ORGANIZATION_BLOCK", "DATA_BLOCK", "TYPE"})
_HEADER_END = frozenset(
    {
        "VAR",
        "VAR_INPUT",
        "VAR_OUTPUT",
        "VAR_IN_OUT",
        "VAR_TEMP",
        "VAR_STAT",
        "CONST",
        "LABEL",
        "BEGIN",
        "STRUCT",
    }
)

TIME_PREFIXES = frozenset({"T", "TIME", "LT", "LTIME", "S5T", "S5TIME"})
DATE_PREFIXES = frozenset({"D", "DATE"})
TOD_PREFIXES = frozenset({"TOD", "TIME_OF_DAY", "LTOD", "LTIME_OF_DAY"})
DT_PREFIXES = frozenset({"DT", "DATE_AND_TIME", "LDT"})
STRING_PREFIXES = frozenset({"CHAR", "WCHAR", "STRING", "WSTRING"})

_OPERATORS = (
    ":=",
    "=>",
    "<=",
    ">=",
    "<>",
    "**",
    "..",
    "+=",
    "-=",
    "*=",
    "/=",
    "?=",
    "+",
    "-",
    "*",
    "/",
    "=",
    "<",
    ">",
    "(",
    ")",
    "[",
    "]",
    ",",
    ";",
    ":",
    ".",
    "&",
    "^",
)

_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_NUMBER_RE = re.compile(
    r"(?P<based>\d+#[0-9A-Fa-f_]+)"
    r"|(?P<real>\d[\d_]*\.\d[\d_]*(?:[eE][+-]?\d+)?|\d[\d_]*[eE][+-]?\d+)"
    r"|(?P<int>\d[\d_]*)"
)
_TYPED_VALUE_RE = re.compile(
    r"[+-]?(?:\d+#[0-9A-Fa-f_]+|\d[\d_]*\.\d[\d_]*(?:[eE][+-]?\d+)?|\d[\d_]*(?:[eE][+-]?\d+)?)"
    r"|TRUE\b|FALSE\b",
    re.IGNORECASE,
)
_TIME_BODY_RE = re.compile(r"[+-]?[0-9A-Za-z_.]+")
_DATE_BODY_RE = re.compile(r"\d+-\d+-\d+")
_TOD_BODY_RE = re.compile(r"\d+:\d+(?::\d+(?:\.\d+)?)?")
_DT_BODY_RE = re.compile(r"\d+-\d+-\d+-\d+:\d+(?::\d+(?:\.\d+)?)?")
_RAW_BODY_RE = re.compile(r"[^\s;,()\[\]]*")
# P#M100.0 BYTE 16, P#DB30.DBX4.0 BYTE 16 — указатель ANY S7 (поддерживается только разбор)
_POINTER_BODY_RE = re.compile(r"[A-Za-z0-9_.]+(?:[ \t]+[A-Za-z_][A-Za-z0-9_]*[ \t]+\d+)?")
_ADDRESS_RE = re.compile(r"%[A-Za-z]+\d*(?:\.[A-Za-z]*\d+)*(?::P\b)?")
_BLOCK_NAME_RE = re.compile(r"[ \t]+(?:\"|[A-Za-z_])")
_HEADER_PROP_RE = re.compile(
    r"(TITLE)[ \t]*=[ \t]*(.*)|(AUTHOR|FAMILY|NAME|VERSION)[ \t]*:(?!=)[ \t]*(.*)", re.IGNORECASE
)


@dataclass
class Token:
    kind: str
    text: str
    line: int
    col: int
    pos: int
    end: int
    value: object = None
    comments: list[Comment] = field(default_factory=list)

    @property
    def upper(self) -> str:
        return self.text.upper() if self.kind == IDENT else ""

    def is_kw(self, *words: str) -> bool:
        return self.kind == IDENT and self.text.upper() in words

    def is_op(self, *ops: str) -> bool:
        return self.kind == OP and self.text in ops

    def __repr__(self) -> str:
        return f"Token({self.kind}, {self.text!r}, {self.line}:{self.col})"


class Lexer:
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.line = 1
        self.line_start = 0
        self.tokens: list[Token] = []
        self.pending: list[Comment] = []
        self.header_zone = False
        self.last_code_line = 0  # строка последнего токена (для own_line комментариев)

    # -- служебное ---------------------------------------------------------
    def _advance_to(self, new_pos: int) -> None:
        chunk = self.text[self.pos : new_pos]
        newlines = chunk.count("\n")
        if newlines:
            self.line += newlines
            self.line_start = self.pos + chunk.rfind("\n") + 1
        self.pos = new_pos

    def _col(self, pos: int) -> int:
        return pos - self.line_start + 1

    def _at_line_start(self, pos: int) -> bool:
        return self.text[self.line_start : pos].strip() == ""

    def _add(self, kind: str, start: int, end: int, value: object = None) -> Token:
        tok = Token(kind, self.text[start:end], self.line, self._col(start), start, end, value, self.pending)
        self.pending = []
        self.tokens.append(tok)
        self._advance_to(end)
        self.last_code_line = self.line
        return tok

    def _comment(self, start: int, end: int, style: str) -> None:
        own = self.last_code_line != self.line
        self.pending.append(Comment(self.text[start:end], self.line, style, own))
        self._advance_to(end)

    # -- основной цикл -------------------------------------------------------
    def run(self) -> list[Token]:
        text = self.text
        n = len(text)
        while self.pos < n:
            ch = text[self.pos]
            if ch in " \t\r\n\f\v﻿":
                self._advance_to(self.pos + 1)
                continue
            if text.startswith("//", self.pos):
                end = text.find("\n", self.pos)
                end = n if end < 0 else end
                self._comment(self.pos, end, "//")
                continue
            if text.startswith("(*", self.pos):
                end = text.find("*)", self.pos + 2)
                end = n if end < 0 else end + 2
                self._comment(self.pos, end, "(*")
                continue
            if self.header_zone and self._at_line_start(self.pos):
                match = _HEADER_PROP_RE.match(text, self.pos)
                if match:
                    eol = text.find("\n", self.pos)
                    eol = n if eol < 0 else eol
                    key = (match.group(1) or match.group(3)).upper()
                    raw = (match.group(2) if match.group(1) else match.group(4)) or ""
                    value = raw.split("\n", 1)[0].strip()
                    self._add(HEADER_PROP, self.pos, eol, (key, value))
                    continue
            if ch == "{":
                self._pragma()
                continue
            if ch == "'":
                self._string()
                continue
            if ch == '"':
                end = text.find('"', self.pos + 1)
                eol = text.find("\n", self.pos + 1)
                if end < 0 or (0 <= eol < end):
                    self._add(ERROR, self.pos, n if eol < 0 else eol, "незакрытый символ в кавычках")
                else:
                    self._add(QIDENT, self.pos, end + 1, text[self.pos + 1 : end])
                continue
            if ch == "#":
                self._local()
                continue
            if ch == "%":
                match = _ADDRESS_RE.match(text, self.pos)
                if match:
                    self._add(ADDRESS, self.pos, match.end(), match.group(0))
                else:
                    self._add(ERROR, self.pos, self.pos + 1, "неизвестный адрес")
                continue
            if "0" <= ch <= "9":
                self._number()
                continue
            if (ch.isascii() and ch.isalpha()) or ch == "_":
                self._ident()
                continue
            if not ch.isascii():
                # не-ASCII вне комментариев и строк (кириллица в коде): одна ошибка на слово
                end = self.pos + 1
                while end < n and not text[end].isascii() and not text[end].isspace():
                    end += 1
                self._add(ERROR, self.pos, end, f"символы вне ASCII {text[self.pos : end]!r}")
                continue
            for op in _OPERATORS:
                if text.startswith(op, self.pos):
                    self._add(OP, self.pos, self.pos + len(op))
                    break
            else:
                self._add(ERROR, self.pos, self.pos + 1, f"неизвестный символ {ch!r}")
        eof = Token(EOF, "", self.line, self._col(self.pos), n, n, None, self.pending)
        self.pending = []
        self.tokens.append(eof)
        return self.tokens

    def _pragma(self) -> None:
        text = self.text
        i = self.pos + 1
        quote = ""
        while i < len(text):
            c = text[i]
            if quote:
                if c == quote:
                    quote = ""
            elif c in "'\"":
                quote = c
            elif c == "}":
                break
            i += 1
        if i >= len(text):
            self._add(ERROR, self.pos, len(text), "незакрытая прагма {")
            return
        self._add(PRAGMA, self.pos, i + 1, text[self.pos + 1 : i].strip())

    def _scan_string(self, start: int) -> int:
        """Конец строки '...' (позиция после закрывающей кавычки) или -1."""
        text = self.text
        i = start + 1
        while i < len(text):
            c = text[i]
            if c == "$":
                i += 2
                continue
            if c == "'":
                return i + 1
            if c == "\n":
                return -1
            i += 1
        return -1

    def _string(self) -> None:
        end = self._scan_string(self.pos)
        if end < 0:
            eol = self.text.find("\n", self.pos)
            self._add(ERROR, self.pos, len(self.text) if eol < 0 else eol, "незакрытая строка")
        else:
            self._add(STRING, self.pos, end)

    def _local(self) -> None:
        text = self.text
        nxt = self.pos + 1
        if nxt < len(text) and text[nxt] == '"':
            end = text.find('"', nxt + 1)
            if end < 0:
                self._add(ERROR, self.pos, len(text), 'незакрытое имя #"..."')
            else:
                self._add(LOCAL, self.pos, end + 1, text[nxt + 1 : end])
            return
        match = _IDENT_RE.match(text, nxt)
        if match:
            self._add(LOCAL, self.pos, match.end(), match.group(0))
        else:
            self._add(ERROR, self.pos, self.pos + 1, "одиночный '#'")

    def _number(self) -> None:
        match = _NUMBER_RE.match(self.text, self.pos)
        assert match is not None  # начинается с цифры
        if match.group("based"):
            self._add(TYPED, self.pos, match.end(), ("", match.group(0)))
        elif match.group("real"):
            self._add(REAL, self.pos, match.end())
        else:
            self._add(INT, self.pos, match.end())

    def _ident(self) -> None:
        text = self.text
        match = _IDENT_RE.match(text, self.pos)
        assert match is not None
        word = match.group(0)
        end = match.end()
        if end < len(text) and text[end] == "#":
            self._typed(word, end + 1)
            return
        upper = word.upper()
        tok = self._add(IDENT, self.pos, end)
        if upper in BLOCK_KEYWORDS and self._starts_block(tok):
            self.header_zone = True
        elif upper in _HEADER_END or upper.startswith("END_"):
            self.header_zone = False
        if upper == "REGION":
            self._region_name(tok)

    def _starts_block(self, tok: Token) -> bool:
        """Ключевое слово блока в начале строки, за ним имя: `TYPE "UDT"`, но не `type : Int;`."""
        if not self._at_line_start(tok.pos):
            return False
        return _BLOCK_NAME_RE.match(self.text, tok.end) is not None

    def _region_name(self, tok: Token) -> None:
        text = self.text
        eol = text.find("\n", self.pos)
        eol = len(text) if eol < 0 else eol
        raw = text[self.pos : eol]
        for marker in ("//", "(*"):
            cut = raw.find(marker)
            if cut >= 0:
                raw = raw[:cut]
        name = raw.strip()
        if name.startswith(":"):
            return  # переменная с именем region (классический SCL), не оператор REGION
        start = self.pos + (len(raw) - len(raw.lstrip()))
        if name:
            self._add(REGION_NAME, start, start + len(name), name)

    def _typed(self, prefix: str, body_start: int) -> None:
        text = self.text
        upper = prefix.upper()
        if upper in TIME_PREFIXES:
            regex = _TIME_BODY_RE
        elif upper in DT_PREFIXES:
            regex = _DT_BODY_RE
        elif upper in TOD_PREFIXES:
            regex = _TOD_BODY_RE
        elif upper in DATE_PREFIXES:
            regex = _DATE_BODY_RE
        elif upper in STRING_PREFIXES:
            end = self._scan_string(body_start) if body_start < len(text) and text[body_start] == "'" else -1
            if end < 0:
                self._add(ERROR, self.pos, body_start, f"нет строки после {prefix}#")
            else:
                self._add(TYPED, self.pos, end, (prefix, text[body_start:end]))
            return
        elif upper in ("B", "W", "DW", "LW", "L", "C") or _is_type_prefix(upper):
            regex = _TYPED_VALUE_RE
        elif upper == "P":
            regex = _POINTER_BODY_RE
        else:
            regex = _RAW_BODY_RE
        match = regex.match(text, body_start)
        if not match or match.end() == body_start:
            self._add(ERROR, self.pos, body_start, f"нет значения после {prefix}#")
            return
        self._add(TYPED, self.pos, match.end(), (prefix, match.group(0)))


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


def _is_type_prefix(upper: str) -> bool:
    return upper in _TYPE_PREFIXES


def tokenize(text: str) -> list[Token]:
    """Токены текста SCL; последний — EOF (с комментариями в конце файла)."""
    return Lexer(text).run()
