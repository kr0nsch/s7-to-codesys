"""Генерация ST CODESYS из AST SCL в раскладке шаблона (объекты stlayout.StObject).

Соответствия — docs/MAPPING.md. Каждая «конструкция» (блок, объявление, оператор) получает статус:
auto — переведена автоматически; check — переведена, но нужна проверка (в коде
`// MIGRATION-CHECK: причина`); todo — не переведена (в коде `// MIGRATION-TODO: причина` и
закомментированный исходный текст). Статусы и пометки собирает отчёт (report.py).
"""

from __future__ import annotations

import re
import textwrap
from collections import Counter
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field

from s7conv import __version__
from s7conv import mapping as M
from s7conv import symbols as S
from s7conv import tasks as T
from s7conv.layout import L
from s7conv.nodes import (
    BLOCK_DB,
    BLOCK_FB,
    BLOCK_FC,
    BLOCK_OB,
    BLOCK_UDT,
    AddressRef,
    Arg,
    ArrayInit,
    ArrayType,
    Assign,
    Binary,
    Block,
    Call,
    CallStmt,
    Case,
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
    Lowering,
    LowerNote,
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
from s7conv.parser import ParseError, Parser, parse_expression

AUTO = "auto"
CHECK = M.CHECK
TODO = M.TODO
IND = "    "
MAX_COMMENT = 116
STARTUP_FLAG = "xS7convStartupDone"
FIRST_CYCLE_FLAG = "xS7convFirstCycleDone"

# Приоритеты операций ST (те же, что в SCL; ** печатается как EXPT(...))
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
}
UNARY_PREC = 8
PRIMARY = 10
COMPARISONS = frozenset({"=", "<>", "<", ">", "<=", ">="})
LOGICAL = frozenset({"AND", "&", "OR", "XOR"})
INTEGER_TYPES = frozenset({"SINT", "USINT", "INT", "UINT", "DINT", "UDINT", "LINT", "ULINT"})
BIT_TYPES = frozenset({"BYTE", "WORD", "DWORD", "LWORD"})
# Типы, вычитание которых в S7 может дать отрицательный TIME, а в CODESYS (без знака) переполняется
TIME_LIKE = frozenset({"TIME", "LTIME", "TOD", "DT", "DATE"})
# Деление этих типов — целочисленное: делитель 0 в CODESYS вызывает исключение
INTEGER_LIKE = INTEGER_TYPES | BIT_TYPES | {"TIME", "LTIME"}

# Типы входов/выходов функциональных блоков инструкций (для вывода типов)
INSTRUCTION_MEMBERS: dict[str, dict[str, str]] = {
    "TON": {"IN": "BOOL", "PT": "TIME", "Q": "BOOL", "ET": "TIME"},
    "TOF": {"IN": "BOOL", "PT": "TIME", "Q": "BOOL", "ET": "TIME"},
    "TP": {"IN": "BOOL", "PT": "TIME", "Q": "BOOL", "ET": "TIME"},
    "LTON": {"IN": "BOOL", "PT": "LTIME", "Q": "BOOL", "ET": "LTIME"},
    "LTOF": {"IN": "BOOL", "PT": "LTIME", "Q": "BOOL", "ET": "LTIME"},
    "LTP": {"IN": "BOOL", "PT": "LTIME", "Q": "BOOL", "ET": "LTIME"},
    "R_TRIG": {"CLK": "BOOL", "Q": "BOOL"},
    "F_TRIG": {"CLK": "BOOL", "Q": "BOOL"},
    "CTU": {"CU": "BOOL", "RESET": "BOOL", "PV": "WORD", "Q": "BOOL", "CV": "WORD"},
    "CTD": {"CD": "BOOL", "LOAD": "BOOL", "PV": "WORD", "Q": "BOOL", "CV": "WORD"},
    "CTUD": {
        "CU": "BOOL",
        "CD": "BOOL",
        "RESET": "BOOL",
        "LOAD": "BOOL",
        "PV": "WORD",
        "QU": "BOOL",
        "QD": "BOOL",
        "CV": "WORD",
    },
    "SR": {"SET1": "BOOL", "RESET": "BOOL", "Q1": "BOOL"},
    "RS": {"SET": "BOOL", "RESET1": "BOOL", "Q1": "BOOL"},
}
# ФБ слоя совместимости S7Compat — с интерфейсом заменяемых ФБ Standard
INSTRUCTION_MEMBERS.update({compat: INSTRUCTION_MEMBERS[std] for std, compat in M.COMPAT_TIMERS.items()})
INSTRUCTION_MEMBERS[M.COMPAT_F_TRIG] = INSTRUCTION_MEMBERS["F_TRIG"]


# ---------------------------------------------------------------------------
# Результаты
# ---------------------------------------------------------------------------


@dataclass
class Options:
    retain_mode: str = "retain"  # retain | persistent
    folder: tuple[str, ...] = ()
    main_task: str = "cyclic"  # cyclic | freewheeling
    main_interval_ms: int = 10
    ob_config: dict[str, object] = field(default_factory=dict)
    # TON/TOF/TP: "standard" — CODESYS Standard; "s7compat" — FB_S7Ton/FB_S7Tof/FB_S7Tp (S7Compat)
    # с подменяемым источником времени для детерминированных тестов сценариев
    timers: str = M.STANDARD
    # F_TRIG: "standard" — CODESYS Standard; "s7compat" — FB_S7FTrig (семантика S7 на первом вызове)
    f_trig: str = M.STANDARD
    # суффикс генерируемых глобальных объектов (GVL_IO, GVL_InstanceDBs ...): второй корпус в том же
    # проекте CODESYS не сталкивается с первым по именам (корпус всех языков — "_Lang")
    global_suffix: str = ""
    # профиль CPU для STL: s7-300 | s7-1500 | None — по MemoryLayout блока SimaticML
    cpu: str | None = None
    # переходы STL: structured — IF/WHILE/CASE; pc — автомат WHILE/CASE для всего блока
    stl_jumps: str = "structured"


@dataclass(frozen=True)
class Note:
    severity: str  # check | todo
    rule: str
    message: str
    line: int
    block: str = ""


@dataclass(frozen=True)
class Item:
    category: str  # block | decl | stmt
    status: str  # auto | check | todo
    line: int
    label: str
    block: str = ""


@dataclass
class FileResult:
    path: str
    blocks: list[tuple[str, str, str]] = field(default_factory=list)  # (вид S7, имя S7, объект ST)
    items: list[Item] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)
    rules: Counter[str] = field(default_factory=Counter)
    parse_issues: list[ParseIssue] = field(default_factory=list)
    # SimaticML/AWL: происхождение строк синтезированного SCL, языки блоков, единицы учёта языков
    lowering: Lowering | None = None

    def where(self, line: int) -> str:
        """Место пометки: номер строки SCL или трасса понижения («сеть 3, UId 27»)."""
        if self.lowering is not None and line in self.lowering.trace:
            return self.lowering.trace[line]
        return str(line) if line else "—"

    def count(self, status: str, category: str | None = None) -> int:
        return sum(1 for i in self.items if i.status == status and (category is None or i.category == category))


@dataclass
class ConversionResult:
    files: list[FileResult]
    objects: list[L.StObject]
    obs: list[T.ObInfo]
    tasks: list[T.TaskInfo]
    support: set[str]
    errors: list[str]
    options: Options
    # таблицы имён конвертера: генератор тестов сценариев (testgen) переводит пути SCL в имена ST так же,
    # как эмиттер (переименования, поля структур, типы после конвертации)
    project: S.Project | None = None
    scopes: dict[str, dict[str, LocalVar]] = field(default_factory=dict)  # блок S7 (lower) -> область
    type_scopes: dict[str, dict[str, LocalVar]] = field(default_factory=dict)  # тип ST (lower) -> поля

    def tasks_json(self) -> dict[str, object]:
        return T.tasks_json(self.obs, self.tasks, f"s7conv {__version__}")


class Unsupported(Exception):
    def __init__(self, reason: str, rule: str = "unsupported") -> None:
        super().__init__(reason)
        self.reason = reason
        self.rule = rule


# ---------------------------------------------------------------------------
# Типы для вывода
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Ty:
    name: str  # INT, REAL, STRING, ARRAY, TON, FB_Motor, UDT_X ...
    elem: Ty | None = None


@dataclass
class LocalVar:
    name: str
    st_name: str
    section: str
    decl: VarDecl
    ty: Ty | None = None
    fb_rule: M.FbRule | None = None
    dropped: str | None = None  # объявление не переносится (MIGRATION-TODO): причина
    constant: bool = False  # VAR CONSTANT / CONST: значение известно при компиляции


Scope = dict[str, LocalVar]


@dataclass
class Frame:
    """Кадр конструкции: свои пометки (notes), пометки вложенных (child_notes), вложенные конструкции."""

    notes: list[Note] = field(default_factory=list)
    items: list[Item] = field(default_factory=list)
    child_notes: list[Note] = field(default_factory=list)


@dataclass
class BlockCtx:
    sym: S.BlockSym
    scope: Scope
    file: SourceFile
    display: str
    fc_name: str = ""


def _ty_name(ty: Ty | None) -> str | None:
    return ty.name if ty is not None else None


def walk_expr(e: Expr) -> Iterator[Expr]:
    yield e
    if isinstance(e, Member | Slice):
        yield from walk_expr(e.base)
    elif isinstance(e, Index):
        yield from walk_expr(e.base)
        for i in e.indices:
            yield from walk_expr(i)
    elif isinstance(e, Call):
        yield from walk_expr(e.callee)
        for a in e.args:
            yield from walk_expr(a.value)
    elif isinstance(e, Unary):
        yield from walk_expr(e.operand)
    elif isinstance(e, Binary):
        yield from walk_expr(e.left)
        yield from walk_expr(e.right)


def stmt_exprs(stmts: Sequence[Stmt]) -> Iterator[Expr]:
    """Все выражения операторов (рекурсивно по телам)."""
    for s in stmts:
        if isinstance(s, Assign):
            yield from walk_expr(s.target)
            yield from walk_expr(s.value)
        elif isinstance(s, CallStmt):
            yield from walk_expr(s.call)
        elif isinstance(s, If):
            for cond, body in s.branches:
                yield from walk_expr(cond)
                yield from stmt_exprs(body)
            if s.else_body:
                yield from stmt_exprs(s.else_body)
        elif isinstance(s, Case):
            yield from walk_expr(s.selector)
            for clause in s.clauses:
                yield from stmt_exprs(clause.body)
            if s.else_body:
                yield from stmt_exprs(s.else_body)
        elif isinstance(s, For):
            for e in (s.var, s.start, s.end) + ((s.step,) if s.step is not None else ()):
                yield from walk_expr(e)
            yield from stmt_exprs(s.body)
        elif isinstance(s, While | Repeat):
            yield from walk_expr(s.cond)
            yield from stmt_exprs(s.body)
        elif isinstance(s, Region):
            yield from stmt_exprs(s.body)


def _wrap_comment(prefix: str, message: str, ind: str) -> list[str]:
    width = max(40, MAX_COMMENT - len(ind) - len(prefix))
    parts = textwrap.wrap(message, width=width, break_long_words=False, break_on_hyphens=False) or [""]
    lines = [f"{ind}{prefix}{parts[0]}".rstrip()]
    pad = "//" + " " * (len(prefix) - 2)
    lines.extend(f"{ind}{pad}{p}" for p in parts[1:])
    return lines


def comment_text(c: Comment) -> list[str]:
    """Текст комментария для ST: табы → пробелы, вложенные '(*' обезврежены."""
    text = c.text.replace("\t", "    ")
    if c.style == "(*":
        inner = text[2:-2] if text.endswith("*)") else text[2:] + " "
        text = "(*" + inner.replace("(*", "( *") + "*)"
    return [line.rstrip() for line in text.split("\n")]


def strip_comment_marks(c: Comment) -> str:
    text = c.text
    if c.style == "//":
        return text[2:].strip()
    inner = text[2:-2] if text.endswith("*)") else text[2:]
    return " ".join(line.strip(" *") for line in inner.splitlines()).strip()


@dataclass
class InitNode:
    """Дерево начальных значений из секции BEGIN блока данных: a.b[2] := v."""

    value: Expr | None = None
    line: int = 0
    fields: dict[str, tuple[str, InitNode]] = field(default_factory=dict)  # имя (lower) -> (имя, узел)
    items: dict[int, InitNode] = field(default_factory=dict)


def init_path(e: Expr) -> list[str | int] | None:
    """Путь цели присваивания BEGIN: Ident/LocalRef, .поле, [целый литерал]; иначе None."""
    if isinstance(e, Ident | LocalRef):
        return [e.name]
    if isinstance(e, Member):
        base = init_path(e.base)
        return None if base is None else [*base, e.name]
    if isinstance(e, Index) and len(e.indices) == 1:
        idx = e.indices[0]
        number: int | None = None
        if isinstance(idx, Literal) and idx.kind == "int":
            number = int(idx.text.replace("_", ""))
        elif (
            isinstance(idx, Unary) and idx.op == "-" and isinstance(idx.operand, Literal) and idx.operand.kind == "int"
        ):
            number = -int(idx.operand.text.replace("_", ""))
        base = init_path(e.base)
        return None if base is None or number is None else [*base, number]
    return None


def _array_low(t: TypeRef | None) -> int | None:
    """Нижняя граница одномерного массива с целыми границами."""
    if not isinstance(t, ArrayType) or len(t.ranges) != 1 or t.ranges[0] is None:
        return None
    lo = t.ranges[0][0]
    if isinstance(lo, Literal) and lo.kind == "int":
        return int(lo.text.replace("_", ""))
    if isinstance(lo, Unary) and lo.op == "-" and isinstance(lo.operand, Literal) and lo.operand.kind == "int":
        return -int(lo.operand.text.replace("_", ""))
    return None


def _array_size(t: ArrayType) -> int | None:
    """Число элементов одномерного массива с целыми границами."""
    low = _array_low(t)
    rng = t.ranges[0] if len(t.ranges) == 1 else None
    if low is None or rng is None:
        return None
    hi = rng[1]
    if isinstance(hi, Literal) and hi.kind == "int":
        return int(hi.text.replace("_", "")) - low + 1
    return None


def _expand_array_init(init: ArrayInit) -> list[Expr | ArrayInit] | None:
    """[1.0, 3(0.0)] -> [1.0, 0.0, 0.0, 0.0]; None, если число повторов не целый литерал."""
    out: list[Expr | ArrayInit] = []
    for count, value in init.items:
        if count is None:
            out.append(value)
            continue
        if not (isinstance(count, Literal) and count.kind == "int"):
            return None
        out.extend([value] * int(count.text.replace("_", "")))
    return out


def _compress_runs(parts: list[str]) -> list[str]:
    """Подряд идущие одинаковые элементы — в форму повтора ST: ['0.0', '0.0'] -> ['2(0.0)']."""
    out: list[str] = []
    i = 0
    while i < len(parts):
        j = i
        while j + 1 < len(parts) and parts[j + 1] == parts[i]:
            j += 1
        run = j - i + 1
        out.append(parts[i] if run == 1 else f"{run}({parts[i]})")
        i = j + 1
    return out


_DEFAULTS = {
    **dict.fromkeys(("SINT", "USINT", "INT", "UINT", "DINT", "UDINT", "LINT", "ULINT"), "0"),
    **dict.fromkeys(("BYTE", "WORD", "DWORD", "LWORD"), "0"),
    "REAL": "0.0",
    "LREAL": "0.0",
    "BOOL": "FALSE",
    "TIME": "T#0s",
    "STRING": "''",
    "WSTRING": '""',
}

_WRAP_LIMIT = 120
_BLANK_LINE_RE = re.compile(r"\n[ \t]*\n")


def _scan_top_level(text: str) -> list[tuple[int, str]]:
    """Позиции символов текста ST вне строк и вложенных скобок: [(индекс, символ)] и глубина через '(' ')'."""
    result: list[tuple[int, str]] = []
    i = 0
    quote = ""
    while i < len(text):
        c = text[i]
        if quote:
            if c == "$":
                i += 2
                continue
            if c == quote:
                quote = ""
            i += 1
            continue
        if c in "'\"":
            quote = c
        elif text.startswith("//", i) or text.startswith("(*", i):
            break
        result.append((i, c))
        i += 1
    return result


def wrap_line(line: str) -> list[str]:
    """Перенос длинной строки ST: аргументы вызова — по одному в строке, иначе — перед AND/OR."""
    if len(line) <= _WRAP_LIMIT or line.lstrip().startswith("//"):
        return [line]
    chars = _scan_top_level(line)
    depth = 0
    open_at = -1
    close_at = -1
    commas: list[int] = []
    for i, c in chars:
        if c in "([":
            call_like = i > 0 and (line[i - 1].isalnum() or line[i - 1] == "_" or line[max(0, i - 3) : i] == ":= ")
            if depth == 0 and c == "(" and open_at < 0 and call_like:
                open_at = i
            depth += 1
        elif c in ")]":
            depth -= 1
            if depth == 0 and i > open_at >= 0 and close_at < 0:
                close_at = i
        elif c == "," and depth == 1 and open_at >= 0 and close_at < 0:
            commas.append(i)
    if open_at >= 0 and close_at > 0 and commas:
        pad = " " * (open_at + 1)
        parts = []
        start = open_at + 1
        for comma in commas:
            parts.append(line[start : comma + 1].strip())
            start = comma + 1
        last = line[start:close_at].strip()
        out = [line[: open_at + 1] + parts[0]]
        out.extend(pad + p for p in parts[1:])
        out.append(pad + last + line[close_at:])
        return out
    # логические операции верхнего уровня
    indent = len(line) - len(line.lstrip())
    breaks: list[int] = []
    depth = 0
    for i, c in chars:
        if c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        elif depth == 0 and c == " " and (line.startswith(" OR ", i) or line.startswith(" AND ", i)):
            breaks.append(i)
    if not breaks:
        return [line]
    out = []
    current_start = 0
    pad = " " * (indent + 8)
    last_break = 0
    for b in breaks:
        if b - current_start > _WRAP_LIMIT - len(pad) - 8 and last_break > current_start:
            out.append(line[current_start:last_break].rstrip())
            current_start = last_break + 1
        last_break = b
    if len(line) - current_start > _WRAP_LIMIT - len(pad) and last_break > current_start:
        out.append(line[current_start:last_break].rstrip())
        current_start = last_break + 1
    out.append(line[current_start:])
    return [out[0]] + [pad + piece.strip() for piece in out[1:]]


# ---------------------------------------------------------------------------
# Эмиттер
# ---------------------------------------------------------------------------


class Emitter:
    def __init__(self, project: S.Project, options: Options | None = None) -> None:
        self.p = project
        self.o = options or Options()
        self.fb_types = M.fb_types(self.o.timers, self.o.f_trig)
        self.frames: list[Frame] = []
        self.objects: list[L.StObject] = []
        self.support: set[str] = set()
        self.scopes: dict[str, Scope] = {}  # ключ блока (lower) -> область
        self.type_scopes: dict[str, Scope] = {}  # имя типа ST (lower) -> поля/интерфейс
        self.generic_local: dict[str, str] = {}  # "блок.переменная" -> TON/CTU_INT ...
        self.dut_names: set[str] = set()
        # (st_name, тип, источник, пометки, реманентный)
        self.instances: list[tuple[str, str, str, list[Note], bool]] = []
        self.implicit: dict[str, tuple[str, str]] = {}  # имя DB (lower) -> (st_name, тип ST)
        self.obs: list[T.ObInfo] = []
        self.s5_used: dict[str, set[int]] = {"T": set(), "C": set()}  # номера таймеров и счётчиков S5
        self.cur: BlockCtx | None = None
        self.result: FileResult | None = None
        self._line_hint = 0

    def g(self, name: str) -> str:
        """Имя генерируемого глобального объекта с суффиксом --global-suffix."""
        return f"{name}{self.o.global_suffix}" if name in S.GENERATED_GVLS else name

    # -- пометки и кадры ------------------------------------------------------------
    def push(self) -> None:
        self.frames.append(Frame())

    def pop(self) -> Frame:
        return self.frames.pop()

    def note(self, severity: str, rule: str, message: str, line: int | None = None) -> None:
        block = self.cur.sym.name if self.cur else ""
        note = Note(severity, rule, message, line if line is not None else self._line_hint, block)
        if self.frames:
            if note not in self.frames[-1].notes:
                self.frames[-1].notes.append(note)
        elif self.result is not None:
            self.result.notes.append(note)

    def check(self, rule: str, message: str) -> None:
        self.note(CHECK, rule, message)

    def hit(self, rule: str) -> None:
        if self.result is not None:
            self.result.rules[rule] += 1

    def commit(self, frame: Frame, item: Item) -> None:
        """Пометки и конструкции кадра — в родительский кадр или в результат файла."""
        if self.frames:
            parent = self.frames[-1]
            parent.items.extend(frame.items)
            parent.items.append(item)
            parent.child_notes.extend(frame.notes)
            parent.child_notes.extend(frame.child_notes)
            return
        assert self.result is not None
        self.result.items.extend(frame.items)
        self.result.items.append(item)
        self.result.notes.extend(frame.notes)
        self.result.notes.extend(frame.child_notes)

    @staticmethod
    def status_of(notes: Sequence[Note]) -> str:
        if any(n.severity == TODO for n in notes):
            return TODO
        if notes:
            return CHECK
        return AUTO

    def note_lines(self, notes: Sequence[Note], ind: str) -> list[str]:
        out: list[str] = []
        lowering = self.cur.file.lowering if self.cur is not None else None
        for n in notes:
            tag = "MIGRATION-TODO" if n.severity == TODO else "MIGRATION-CHECK"
            where = f" (стр. {n.line})" if n.line else ""
            if lowering is not None and self.cur is not None and n.line in lowering.trace:
                where = f" ({self.cur.display.rsplit('/', 1)[-1]}, {lowering.trace[n.line]})"
            out.extend(_wrap_comment(f"// {tag}: ", f"{n.message}{where}", ind))
        return out

    def comment_lines(self, comments: Sequence[Comment], ind: str) -> list[str]:
        out: list[str] = []
        for c in comments:
            lines = comment_text(c)
            out.append(ind + lines[0])
            out.extend(ind + line.strip() for line in lines[1:])
        return out

    @staticmethod
    def trailing(lines: list[str], comments: Sequence[Comment]) -> None:
        if comments and lines:
            lines[-1] += "  " + " ".join(comment_text(c)[0] for c in comments)

    def original_lines(self, text: str, start: int, ind: str) -> list[str]:
        src = self.cur.file.text if self.cur else ""
        col = start - (src.rfind("\n", 0, start) + 1) if src else 0
        block = (" " * col + text).replace("\t", "    ")
        lines = textwrap.dedent(block).splitlines()
        return [f"{ind}// {line}".rstrip() for line in lines]

    # -- запуск --------------------------------------------------------------------------
    def run(self, files: list[SourceFile], display: dict[str, str] | None = None) -> ConversionResult:
        display = display or {}
        S.collect_blocks(self.p, files)
        self.prepass(files)
        results: list[FileResult] = []
        for sf in files:
            self.result = FileResult(
                path=display.get(sf.path, sf.path), parse_issues=list(sf.issues), lowering=sf.lowering
            )
            for blk in sf.blocks:
                if isinstance(blk, RawBlock):
                    self.raw_block(blk, sf)
                    continue
                sym = self.p.block(blk.name)
                if sym is None or sym.block is not blk:
                    self.result.items.append(Item("block", TODO, blk.span.line, f"{blk.kind} {blk.name}", blk.name))
                    self.result.notes.append(
                        Note(TODO, "block.duplicate", f"блок {blk.name} объявлен повторно — пропущен", blk.span.line)
                    )
                    continue
                self.cur = BlockCtx(sym=sym, scope=self.scopes[blk.name.lower()], file=sf, display=self.result.path)
                self.block(sym)
                self.cur = None
            results.append(self.result)
        self.result = FileResult(path="(проект: слой ввода-вывода, теги, экземпляры DB)")
        self.project_objects()
        if self.result.items or self.result.notes:
            results.append(self.result)
        self.result = None
        tasks = T.build_tasks(self.obs, self.o.main_task, self.o.main_interval_ms)
        return ConversionResult(
            files=results,
            objects=self.objects,
            obs=self.obs,
            tasks=tasks,
            support=set(M.support_closure(self.support)),
            errors=list(self.p.errors),
            options=self.o,
            project=self.p,
            scopes=self.scopes,
            type_scopes=self.type_scopes,
        )

    # -- предварительный проход: области видимости и типы IEC_TIMER -----------------------
    def prepass(self, files: list[SourceFile]) -> None:
        for sym in self.p.blocks.values():
            body = sym.block.body
            for e in stmt_exprs(body):
                if not (isinstance(e, Call) and isinstance(e.callee, Member)):
                    continue
                method = e.callee.name.upper()
                if method not in M.GENERIC_METHODS:
                    continue
                base = e.callee.base
                if isinstance(base, GlobalRef):
                    db = self.p.block(base.name)
                    generic = db.db_type_name.upper() if db is not None and db.db_type_name else "IEC_TIMER"
                    self.p.generic_types.setdefault(base.name.lower(), M.generic_method_type(generic, method))
                elif isinstance(base, LocalRef | Ident):
                    var = self._find_decl(sym.block, base.name)
                    generic = var.type.name.upper() if var and isinstance(var.type, NamedType) else "IEC_TIMER"
                    key = f"{sym.name.lower()}.{base.name.lower()}"
                    self.generic_local.setdefault(key, M.generic_method_type(generic, method))
        for sym in self.p.blocks.values():
            self.scopes[sym.name.lower()] = self.build_scope(sym)
        for sym in self.p.blocks.values():
            if sym.kind in (BLOCK_FB, BLOCK_UDT) or (sym.kind == BLOCK_DB and sym.db_role == S.DB_GLOBAL):
                self.type_scopes[sym.st_name.lower()] = self.scopes[sym.name.lower()]

    @staticmethod
    def _find_decl(blk: Block, name: str) -> VarDecl | None:
        for sec in blk.sections:
            for d in sec.items:
                if isinstance(d, VarDecl) and any(n.lower() == name.lower() for n in d.names):
                    return d
        return None

    def build_scope(self, sym: S.BlockSym) -> Scope:
        scope: Scope = {}
        used: set[str] = set()
        blk = sym.block
        sections: list[tuple[str, list[VarDecl | RawDecl], bool]] = [
            (s.kind, s.items, s.kind == "CONST" or "CONSTANT" in s.modifiers) for s in blk.sections
        ]
        if blk.struct is not None:
            sections.append(("STRUCT", blk.struct.decls, False))
        for kind, items, constant in sections:
            for d in items:
                if not isinstance(d, VarDecl):
                    continue
                for name in d.names:
                    st = M.sanitize(name)
                    base, n = st, 2
                    while st.lower() in used:
                        st = f"{base}_{n}"
                        n += 1
                    used.add(st.lower())
                    var = LocalVar(name=name, st_name=st, section=kind, decl=d, constant=constant)
                    var.ty, var.fb_rule = self.peek_type(d.type, sym, name)
                    var.dropped = self.decl_drop_reason(d, sym, name)
                    scope[name.lower()] = var
        return scope

    def peek_type(self, t: TypeRef, owner: S.BlockSym, field_name: str) -> tuple[Ty | None, M.FbRule | None]:
        """Тип для вывода (без пометок и побочных эффектов)."""
        if isinstance(t, StringType):
            return Ty("WSTRING" if t.wide else "STRING"), None
        if isinstance(t, ArrayType):
            elem, _ = self.peek_type(t.element, owner, field_name)
            return Ty("ARRAY", elem), None
        if isinstance(t, StructType):
            name = self.struct_name(owner, field_name)
            # поля анонимной структуры — для вывода типов доступа a.b
            sub: Scope = {}
            for d in t.decls:
                if isinstance(d, VarDecl):
                    for n in d.names:
                        lv = LocalVar(n, M.sanitize(n), "STRUCT", d)
                        lv.ty, lv.fb_rule = self.peek_type(d.type, owner, f"{field_name}_{n}")
                        lv.dropped = self.decl_drop_reason(d, owner, f"{field_name}_{n}")
                        sub[n.lower()] = lv
            self.type_scopes[name.lower()] = sub
            return Ty(name), None
        if isinstance(t, RefType):
            return None, None
        upper = t.name.upper()
        if not t.quoted:
            if upper in M.ELEMENTARY:
                return Ty(M.ELEMENTARY[upper]), None
            if upper in M.CHECKED_TYPES:
                text = M.CHECKED_TYPES[upper][0]
                return Ty(text.split("(")[0]), None
            if upper in M.GENERIC_INSTANCE_TYPES:
                inferred = self.generic_local.get(f"{owner.name.lower()}.{field_name.lower()}")
                rule = self.fb_types.get(inferred or "")
                return (Ty(rule.target), rule) if rule else (None, None)
            if upper in self.fb_types:
                rule = self.fb_types[upper]
                return Ty(rule.target), rule
        sym = self.p.block(t.name)
        if sym is not None:
            return Ty(sym.st_name), None
        return Ty(M.sanitize(t.name)), None

    def decl_drop_reason(self, d: VarDecl, owner: S.BlockSym, field_name: str) -> str | None:
        if d.at is not None:
            return "AT (наложение переменных S7)"
        found = self.unsupported_type(d.type, owner, field_name)
        return found[0] if found else None

    def unsupported_type(self, t: TypeRef, owner: S.BlockSym, field_name: str) -> tuple[str, str] | None:
        """(причина, правило), если тип не переносится; иначе None. Без побочных эффектов."""
        if isinstance(t, ArrayType):
            return self.unsupported_type(t.element, owner, field_name)
        if isinstance(t, RefType):
            return "REF_TO — ссылки S7 не поддерживаются (POINTER TO / REFERENCE TO вручную)", "type.ref"
        if not isinstance(t, NamedType):
            return None
        upper = t.name.upper()
        if not t.quoted:
            if upper in M.ELEMENTARY or upper in M.CHECKED_TYPES or upper in self.fb_types:
                return None
            if upper in M.GENERIC_INSTANCE_TYPES:
                inferred = self.generic_local.get(f"{owner.name.lower()}.{field_name.lower()}")
                if inferred and self.fb_types.get(inferred):
                    return None
                if inferred:
                    return f"{t.name}.{inferred}: нет аналога в CODESYS Standard", "fb.unsupported"
                return M.UNSUPPORTED_TYPES.get(upper, f"{t.name}: тип не определён"), "type.generic"
            if upper in M.UNSUPPORTED_TYPES:
                return M.UNSUPPORTED_TYPES[upper], "type.unsupported"
            if upper.startswith(M.UNSUPPORTED_TYPE_PREFIXES) and self.p.block(t.name) is None:
                return f"системный тип S7 {t.name} не поддерживается", "type.unsupported"
            if upper == "VOID":
                return "Void как тип переменной", "type.unsupported"
        sym = self.p.block(t.name)
        if sym is not None and sym.kind not in (BLOCK_UDT, BLOCK_FB):
            return f"«{t.name}» ({sym.kind}) не может быть типом", "type.unsupported"
        return None

    def use_var(self, var: LocalVar) -> None:
        """Обращение к переменной, объявление которой не перенесено, — оператор тоже не переносится."""
        if var.dropped:
            raise Unsupported(
                f"использует «{var.name}», объявление которой не перенесено ({var.dropped})", "decl.dropped_use"
            )

    def struct_name(self, owner: S.BlockSym, field_name: str) -> str:
        return "ST_" + M.sanitize(f"{owner.st_name}_{field_name}").strip("_")

    # -- блоки ----------------------------------------------------------------------------
    def raw_block(self, blk: RawBlock, sf: SourceFile) -> None:
        assert self.result is not None
        label = f"{blk.kind} {blk.name}".strip() or "текст вне блоков"
        self.result.items.append(Item("block", TODO, blk.span.line, label, blk.name))
        self.result.notes.append(Note(TODO, "parse.block", f"{label}: не разобран — {blk.reason}", blk.span.line))

    def block(self, sym: S.BlockSym) -> None:
        assert self.result is not None and self.cur is not None
        blk = sym.block
        self._line_hint = blk.span.line
        self.push()
        if blk.attributes.get("S7_Optimized_Access", "").upper() == "FALSE":
            self.check(
                "block.non_optimized",
                "стандартный (неоптимизированный) доступ S7: абсолютная адресация и порядок байтов не переносятся",
            )
        if "KNOW_HOW_PROTECT" in blk.flags:
            self.check("block.know_how", "блок был защищён KNOW_HOW_PROTECT")
        if blk.kind == BLOCK_UDT:
            self.udt(sym)
        elif blk.kind == BLOCK_DB:
            self.data_block(sym)
        else:
            self.pou(sym)
        frame = self.pop()
        status = self.status_of(frame.notes)
        self.commit(frame, Item("block", status, blk.span.line, f"{blk.kind} {blk.name}", blk.name))

    def header(self, sym: S.BlockSym, what: str, extra_notes: Sequence[Note] = ()) -> list[str]:
        assert self.cur is not None
        blk = sym.block
        desc = [strip_comment_marks(c) for c in blk.comments if strip_comment_marks(c)]
        lowering = self.cur.file.lowering
        lang = lowering.langs.get(blk.name.lower(), "SCL") if lowering is not None else "SCL"
        if blk.title:
            purpose = blk.title
        elif desc:
            purpose = desc.pop(0)
        else:
            purpose = f"{what} «{blk.name}», сконвертирован из {lang}"
        lines = _wrap_comment("// Назначение: ", purpose, "")
        for d in desc[:8]:
            lines.extend(_wrap_comment("//             ", d, ""))
        author = blk.props.get("AUTHOR") or "не указан"
        version = blk.props.get("VERSION") or "не указана"
        family = blk.props.get("FAMILY")
        lines.append(f"// Автор:      {author} (исходный блок S7); перевод в ST — s7conv {__version__}")
        lines.append(f"// Версия:     {version} (исходный блок S7)")
        lines.append("// Документ:   docs/CONVERSION_REPORT.md, docs/MAPPING.md")
        source = f'{self.cur.display}, строки {blk.span.line}–{blk.span.end_line}, {blk.kind} "{blk.name}"'
        if lowering is not None:
            source = f"{self.cur.display}, {lowering.origin.get(blk.name.lower(), lang)}"
        lines.extend(_wrap_comment("// Источник:   ", source + (f", FAMILY {family}" if family else ""), ""))
        lines.append("// Сгенерировано s7conv: пометки MIGRATION-CHECK и MIGRATION-TODO требуют ручного разбора.")
        lines.extend(self.note_lines(extra_notes, ""))
        if blk.preamble:
            lines.append("// ---- комментарий в начале исходного файла SCL ----")
            lines.extend(self.comment_lines(blk.preamble, ""))
        return lines

    def obj(self, kind: str, name: str, decl: str, impl: str | None = None, pou_kind: str | None = None) -> None:
        obj = L.StObject(kind, name, decl, folder=list(self.o.folder), impl=impl, pou_kind=pou_kind)
        self.objects.append(obj)
        if self.result is not None and self.cur is not None:
            self.result.blocks.append((self.cur.sym.block.kind, self.cur.sym.name, name))

    # UDT -> DUT
    def udt(self, sym: S.BlockSym) -> None:
        blk = sym.block
        self.hit("udt.dut")
        if blk.struct is None:
            raise_note = f"TYPE без STRUCT ({type(blk.db_type).__name__}) не поддерживается"
            self.note(TODO, "udt.alias", raise_note)
            return
        body = self.decl_lines(blk.struct.decls, IND, sym)
        head = self.header(sym, "Тип (UDT)", self.frames[-1].notes)
        decl = "\n".join([*head, f"TYPE {sym.st_name} :", "STRUCT", *body, "END_STRUCT", "END_TYPE"])
        self.obj(L.KIND_DUT, sym.st_name, decl)

    def struct_dut(self, name: str, owner: S.BlockSym, field_name: str, st: StructType) -> None:
        if name.lower() in self.dut_names:
            return
        self.dut_names.add(name.lower())
        body = self.decl_lines(st.decls, IND, owner, struct_prefix=field_name)
        assert self.cur is not None
        header = [
            f"// Назначение: структура поля «{field_name}» блока «{owner.name}» (анонимный Struct в SCL)",
            f"// Автор:      s7conv {__version__} (сгенерировано)",
            "// Версия:     не указана",
            "// Документ:   docs/MAPPING.md, раздел «Типы»",
            f'// Источник:   {self.cur.display}, {owner.block.kind} "{owner.name}"',
        ]
        decl = "\n".join([*header, f"TYPE {name} :", "STRUCT", *body, "END_STRUCT", "END_TYPE"])
        self.objects.append(L.StObject(L.KIND_DUT, name, decl, folder=list(self.o.folder)))
        self.hit("type.struct_dut")

    # DB -> GVL или экземпляр
    def data_block(self, sym: S.BlockSym) -> None:
        assert self.cur is not None and self.result is not None
        blk = sym.block
        if "READ_ONLY" in blk.flags:
            self.check("db.read_only", "DB только для чтения (READ_ONLY): в CODESYS запись не запрещена")
        if sym.db_role == S.DB_GLOBAL:
            self.global_db(sym)
            return
        # экземплярный или типизированный DB -> переменная в GVL_InstanceDBs
        type_text = self.instance_type(sym)
        init = self.instance_init(sym)
        retain = self.instance_retain(sym)
        notes = list(self.frames[-1].notes)
        decl_type = type_text + (f" := {init}" if init else "")
        self.instances.append((sym.st_name, decl_type, f"{self.cur.display}:{blk.span.line}", notes, retain))
        self.result.blocks.append((blk.kind, sym.name, f"{self.g(S.GVL_INSTANCES)}.{sym.st_name}"))
        self.hit("db.instance" if sym.db_role == S.DB_INSTANCE else "db.typed")

    def instance_retain(self, sym: S.BlockSym) -> bool:
        """Реманентность экземплярного или типизированного DB целиком.

        Оптимизированный экземплярный DB реманентен по переменным ФБ (`VAR RETAIN` остаётся в ФБ). Стандартный
        (неоптимизированный) DB без NON_RETAIN в S7 реманентен целиком — то же правило, что у глобального DB
        (`db.retain_standard`). Доступ экземплярного DB без своего атрибута — как у его ФБ.
        """
        blk = sym.block
        if "NON_RETAIN" in blk.flags:
            return False
        optimized = blk.attributes.get("S7_Optimized_Access")
        if optimized is None and sym.db_role == S.DB_INSTANCE:
            fb = self.p.block(sym.db_type_name)
            if fb is not None:
                optimized = fb.block.attributes.get("S7_Optimized_Access")
        if "RETAIN" not in blk.flags and (optimized or "").upper() != "FALSE":
            return False
        if "RETAIN" not in blk.flags:
            self.check(
                "db.retain_standard",
                "стандартный (неоптимизированный) экземплярный или типизированный DB без NON_RETAIN: в S7 он "
                f"реманентный целиком — объявлен в VAR_GLOBAL RETAIN {self.g(S.GVL_INSTANCES)}",
            )
        if self.o.retain_mode == "persistent":
            self.check(
                "db.persistent",
                "PERSISTENT в обычном GVL: CODESYS 3.5.17 предупреждает C0244 (в приложении нет списка "
                "VAR_PERSISTENT) — создать объект Persistent Variables и внести в него пути переменных",
            )
        return True

    def instance_type(self, sym: S.BlockSym) -> str:
        blk = sym.block
        assert blk.db_type is not None
        if isinstance(blk.db_type, NamedType):
            upper = blk.db_type.name.upper()
            if not blk.db_type.quoted and upper in M.GENERIC_INSTANCE_TYPES:
                inferred = self.p.generic_types.get(sym.name.lower())
                if inferred is None:
                    self.note(TODO, "db.generic", f"{blk.db_type.name}: тип таймера/счётчика не определён (нет вызова)")
                    return "BOOL"
                rule = self.fb_types.get(inferred)
                if rule is None:
                    self.note(TODO, "fb.unsupported", f"{inferred}: нет аналога в CODESYS Standard")
                    return "BOOL"
                self.fb_rule_note(rule)
                return rule.target
        try:
            return self.map_type(blk.db_type, sym, sym.name)
        except Unsupported as u:
            self.note(TODO, u.rule, u.reason)
            return "BOOL"

    def begin_tree(self, sym: S.BlockSym) -> InitNode:
        """Дерево начальных значений BEGIN; неподдерживаемые присваивания — пометка TODO."""
        root = InitNode()
        for s in sym.block.body:
            if isinstance(s, Empty | CommentStmt):
                continue
            self._line_hint = s.span.line
            path = init_path(s.target) if isinstance(s, Assign) and s.op == ":=" else None
            if not isinstance(s, Assign) or path is None:
                self.note(TODO, "db.begin", "оператор в BEGIN блока данных (не начальное значение) не переносится")
                continue
            node = root
            for seg in path:
                if isinstance(seg, int):
                    node = node.items.setdefault(seg, InitNode())
                else:
                    node = node.fields.setdefault(seg.lower(), (seg, InitNode()))[1]
            node.value = s.value
            node.line = s.span.line
            self.hit("db.begin_init")
        return root

    def render_init(
        self,
        node: InitNode,
        ty: Ty | None,
        tref: TypeRef | None,
        scope: Scope | None = None,
        default: Expr | ArrayInit | None = None,
    ) -> str:
        """Начальное значение ST: выражение, (поле := ...) или [элементы] по дереву BEGIN.

        default — начальное значение из объявления (переменной DB, поля UDT, входа ФБ): элементы
        массива, которых нет в BEGIN, сохраняют его, как в S7 (BEGIN меняет только перечисленные).
        """
        if node.line:
            self._line_hint = node.line
        if node.value is not None:
            return self.ex(node.value, _ty_name(ty))
        if node.fields:
            if scope is None and ty is not None:
                scope = self.type_scopes.get(ty.name.lower())
            parts: list[str] = []
            for key, (orig, child) in node.fields.items():
                var = scope.get(key) if scope is not None else None
                if var is None:
                    self.check(
                        "db.begin_member", f"начальное значение «{orig}»: элемент не найден — перенесён по имени"
                    )
                    parts.append(f"{M.sanitize(orig)} := {self.render_init(child, None, None)}")
                else:
                    text = self.render_init(child, var.ty, var.decl.type, default=var.decl.init)
                    parts.append(f"{var.st_name} := {text}")
            return "(" + ", ".join(parts) + ")"
        return self.render_array_init(node, ty, tref, default)

    def render_array_init(
        self, node: InitNode, ty: Ty | None, tref: TypeRef | None, default: Expr | ArrayInit | None
    ) -> str:
        """[элементы] одномерного массива: BEGIN поверх начального значения объявления или типа."""
        low = _array_low(tref)
        size = _array_size(tref) if isinstance(tref, ArrayType) else None
        keys = sorted(node.items)
        elem_ty = ty.elem if ty is not None else None
        type_default = _DEFAULTS.get(elem_ty.name if elem_ty else "", "")
        declared = _expand_array_init(default) if isinstance(default, ArrayInit) else None
        if low is None or any(k < low or (size is not None and k >= low + size) for k in keys):
            raise Unsupported(
                "начальные значения элементов массива в BEGIN: нижняя граница массива не литерал или индекс "
                "вне границ — перенести вручную",
                "db.begin_array",
            )
        assert isinstance(tref, ArrayType)
        if size is None:
            # верхняя граница — не литерал: только элементы подряд от нижней границы, остальные — по умолчанию
            if declared is not None or keys != list(range(low, low + len(keys))):
                raise Unsupported(
                    "начальные значения элементов массива в BEGIN: верхняя граница не литерал, а элементы не "
                    "подряд от нижней границы или у массива есть начальное значение — перенести вручную",
                    "db.begin_array",
                )
            return "[" + ", ".join(self.render_init(node.items[k], elem_ty, tref.element) for k in keys) + "]"
        # с начальным значением в объявлении — все элементы (неперечисленные в BEGIN сохраняют его),
        # без него — до последнего перечисленного, остальные — значение по умолчанию типа
        end = size if declared is not None else keys[-1] - low + 1
        parts: list[str] = []
        for pos in range(end):
            from_decl = declared[pos] if declared is not None and pos < len(declared) else None
            if low + pos in node.items:
                parts.append(self.render_init(node.items[low + pos], elem_ty, tref.element, default=from_decl))
            elif from_decl is not None:
                parts.append(self.init_text(from_decl, _ty_name(elem_ty)))
            elif type_default:
                parts.append(type_default)
            else:
                raise Unsupported(
                    "начальные значения элементов массива структур в BEGIN не подряд от нижней границы — "
                    "перенести вручную",
                    "db.begin_array",
                )
        rest = size - len(parts)
        if rest > 0 and type_default and declared is None:
            parts.extend([type_default] * rest)
        return "[" + ", ".join(_compress_runs(parts)) + "]"

    def instance_init(self, sym: S.BlockSym) -> str:
        """Начальные значения экземплярного/типизированного DB: DB_P101 : FB_Motor := (feedbackTime := T#5S)."""
        root = self.begin_tree(sym)
        if not root.fields and not root.items:
            return ""
        blk = sym.block
        scope: Scope | None = None
        ty: Ty | None = None
        if sym.db_role == S.DB_INSTANCE:
            fb = self.p.block(sym.db_type_name)
            if fb is not None and fb.kind == BLOCK_FB:
                scope = self.scopes[fb.name.lower()]
                inner = [
                    orig
                    for key, (orig, _n) in root.fields.items()
                    if key in scope and scope[key].section not in ("VAR_INPUT", "VAR_OUTPUT")
                ]
                if inner:
                    self.check(
                        "db.begin_static",
                        "начальные значения внутренних переменных экземпляра ФБ ("
                        + ", ".join(inner)
                        + ") — инициализацию экземпляра проверить компилятором CODESYS",
                    )
        elif blk.db_type is not None:
            ty = self.peek_type(blk.db_type, sym, sym.name)[0]
        try:
            return self.render_init(root, ty, blk.db_type, scope)
        except Unsupported as u:
            self.note(TODO, u.rule, u.reason)
            return ""

    def retain_of(self, sym: S.BlockSym, sec: VarSection) -> bool:
        if "RETAIN" in sec.modifiers:
            return True
        if "NON_RETAIN" in sec.modifiers:
            return False
        blk = sym.block
        if "NON_RETAIN" in blk.flags:
            return False
        if "RETAIN" in blk.flags:
            return True
        if blk.attributes.get("S7_Optimized_Access", "").upper() == "FALSE":
            self.check("db.retain_standard", "стандартный DB без NON_RETAIN: в S7 он реманентный — объявлен RETAIN")
            return True
        return False

    def global_db(self, sym: S.BlockSym) -> None:
        assert self.cur is not None
        blk = sym.block
        self.hit("db.global")
        inits = {key: node for key, (_orig, node) in self.begin_tree(sym).fields.items()}
        normal: list[str] = []
        retained: list[str] = []
        sections: list[tuple[VarSection | None, list[VarDecl | RawDecl]]] = [(s, s.items) for s in blk.sections]
        if blk.struct is not None:
            sections.append((None, blk.struct.decls))
        for sec, items in sections:
            retain = self.retain_of(sym, sec) if sec is not None else False
            if sec is not None:
                (retained if retain else normal).extend(self.comment_lines(sec.comments, IND))
            lines = self.decl_lines(items, IND, sym, inits=inits)
            (retained if retain else normal).extend(lines)
        for name in sorted(set(inits) - {v.name.lower() for v in self.scopes[blk.name.lower()].values()}):
            self.note(TODO, "db.begin", f"начальное значение для {name} в BEGIN: переменная не найдена")
        if retained and self.o.retain_mode == "persistent":
            self.check(
                "db.persistent",
                "PERSISTENT в обычном GVL: CODESYS 3.5.17 предупреждает C0244 (в приложении нет списка "
                "VAR_PERSISTENT) — создать объект Persistent Variables и внести в него пути переменных",
            )
        head = self.header(sym, "Глобальный DB", self.frames[-1].notes)
        out = [*head, "{attribute 'qualified_only'}", "VAR_GLOBAL", *normal, "END_VAR"]
        if retained:
            if self.o.retain_mode == "persistent":
                out += ["VAR_GLOBAL PERSISTENT RETAIN", *retained, "END_VAR"]
            else:
                out += ["VAR_GLOBAL RETAIN", *retained, "END_VAR"]
            self.hit("db.retain")
        self.obj(L.KIND_GVL, sym.st_name, "\n".join(out))

    # FB/FC/OB -> POU
    def pou(self, sym: S.BlockSym) -> None:
        assert self.cur is not None
        blk = sym.block
        startup = False
        event_ob = False
        if blk.kind == BLOCK_FB:
            keyword, pou_kind, what = f"FUNCTION_BLOCK {sym.st_name}", L.POU_FUNCTION_BLOCK, "Функциональный блок"
            self.hit("pou.fb")
        elif blk.kind == BLOCK_FC:
            self.cur.fc_name = blk.name
            ret = ""
            if blk.return_type is not None and not (
                isinstance(blk.return_type, NamedType) and blk.return_type.name.upper() == "VOID"
            ):
                try:
                    ret = " : " + self.map_type(blk.return_type, sym, blk.name)
                except Unsupported as u:
                    self.note(TODO, u.rule, f"тип результата: {u.reason}")
                    ret = " : BOOL"
            keyword, pou_kind, what = f"FUNCTION {sym.st_name}{ret}", L.POU_FUNCTION, "Функция (FC)"
            self.hit("pou.fc")
        else:
            keyword, pou_kind, what = f"PROGRAM {sym.st_name}", L.POU_PROGRAM, "Программа (OB)"
            ob_kind = self.register_ob(sym)
            startup = ob_kind == T.STARTUP
            event_ob = ob_kind == T.EVENT
            self.hit("pou.ob")
        decl_lines: list[str] = []
        for sec in blk.sections:
            decl_lines.extend(self.section(sym, sec, event_ob=event_ob))
        initial_call = None
        if blk.kind == BLOCK_OB:
            var = self.cur.scope.get("initial_call")
            if var is not None and var.section == "VAR_INPUT":
                initial_call = var.st_name
        if startup:
            decl_lines += ["VAR", f"    {STARTUP_FLAG} : BOOL; // флаг первого цикла (замена OB100)", "END_VAR"]
        if initial_call:
            decl_lines += ["VAR", f"    {FIRST_CYCLE_FLAG} : BOOL; // для эмуляции Initial_Call", "END_VAR"]
            self.check(
                "ob.initial_call",
                "вход OB Initial_Call эмулируется флагом первого цикла: флаг (не RETAIN) сбрасывается загрузкой, "
                "Reset warm/cold и перезапуском ПЛК, но не командой Stop → Start CODESYS (в S7 Initial_Call = TRUE "
                "после каждого STOP → RUN)",
            )
        body = self.body(blk.body, IND if startup else "")
        if initial_call:
            body = [
                "// Initial_Call (вход OB S7): TRUE только в первом цикле после запуска — эмуляция s7conv",
                f"{initial_call} := NOT {FIRST_CYCLE_FLAG};",
                f"{FIRST_CYCLE_FLAG} := TRUE;",
                *body,
            ]
        if startup:
            self._line_hint = blk.span.line
            body = [
                f"IF NOT {STARTUP_FLAG} THEN",
                f"    {STARTUP_FLAG} := TRUE;",
                *body,
                "END_IF",
            ]
        if not [line for line in body if line.strip()]:
            body = ["// тело пустое: в исходном блоке нет операторов"]
        decl = "\n".join([*self.header(sym, what, self.frames[-1].notes), keyword, *decl_lines])
        self.obj(L.KIND_POU, sym.st_name, decl, "\n".join(body), pou_kind)

    def register_ob(self, sym: S.BlockSym) -> str:
        """Классифицирует OB (задача, номер, период) и возвращает его вид: tasks.MAIN, CYCLIC, STARTUP или EVENT."""
        assert self.cur is not None
        blk = sym.block
        info = T.ObInfo(name=blk.name, program=sym.st_name, file=self.cur.display, line=blk.span.line)
        comments = " ".join(strip_comment_marks(c) for c in blk.comments)
        T.classify(info, blk.title or "", comments, self.o.ob_config)
        self.obs.append(info)
        number = f"OB{info.number}" if info.number is not None else "номер OB не определён"
        if info.kind == T.EVENT:
            self.note(
                TODO,
                "ob.event",
                f"{number}: событийный OB — задача по событию не создаётся, настроить вручную",
            )
        elif info.kind == T.STARTUP:
            self.check(
                "ob.startup",
                f"{number} (Startup) → однократное выполнение по флагу первого цикла в MainTask: флаг (не RETAIN) "
                "сбрасывается загрузкой, Reset warm/cold и перезапуском ПЛК, но не командой Stop → Start CODESYS "
                "(в S7 OB100 выполняется при каждом STOP → RUN); задачи с более высоким приоритетом могут "
                "выполниться раньше",
            )
        elif info.kind == T.CYCLIC:
            msg = f"{number} → циклическая задача {info.interval_ms} мс ({info.interval_origin})"
            if info.notes:
                self.check("ob.cyclic", msg + "; " + "; ".join(info.notes))
            else:
                self.hit("ob.cyclic")
        else:
            if info.number is None:
                self.check("ob.main", "номер OB не указан — принят OB1 по имени блока")
            self.hit("ob.main")
        return info.kind

    def section(self, sym: S.BlockSym, sec: VarSection, event_ob: bool = False) -> list[str]:
        blk = sym.block
        kind = sec.kind
        mods = list(sec.modifiers)
        self._line_hint = sec.span.line
        if kind == "CONST":
            kind, mods = "VAR", ["CONSTANT"]
        if kind == "VAR_STAT":
            kind = "VAR"
        if blk.kind == BLOCK_FC and kind == "VAR_TEMP":
            kind = "VAR"
            self.hit("section.fc_temp")
        if blk.kind == BLOCK_OB and kind == "VAR_INPUT":
            if event_ob:
                # Событийный OB вызывает рукописный обработчик события: стартовую информацию он передаёт
                # параметрами вызова. В VAR программы извне записать нельзя (CODESYS 3.5.17: ошибка C0037).
                self.check(
                    "ob.start_info",
                    "входы событийного OB (стартовая информация S7) оставлены VAR_INPUT: CODESYS их не заполняет — "
                    "их передаёт вызов из обработчика события",
                )
            else:
                self.check(
                    "ob.start_info", "входы OB (стартовая информация S7) объявлены как VAR — CODESYS их не заполняет"
                )
                kind = "VAR"
        if blk.kind == BLOCK_FC and kind == "VAR" and "CONSTANT" not in mods:
            self.hit("section.fc_var")
        out_mods: list[str] = []
        for m in mods:
            if m == "CONSTANT":
                out_mods.append("CONSTANT")
            elif m == "RETAIN":
                out_mods.append("RETAIN")
                if blk.kind == BLOCK_FB:
                    self.check(
                        "section.fb_retain",
                        "VAR RETAIN в ФБ: в CODESYS при RETAIN-переменной в retain-памяти хранится весь экземпляр "
                        "ФБ, в S7 — только эти переменные (сверить с источником)",
                    )
                else:
                    self.hit("section.retain")
            elif m == "NON_RETAIN":
                self.hit("section.non_retain")
            elif m == "DB_SPECIFIC":
                self.check(
                    "section.db_specific", "реманентность задаётся в экземпляре DB (DB_SPECIFIC) — объявлено VAR"
                )
            elif m == "PERSISTENT":
                out_mods.append("PERSISTENT")
        head = " ".join([kind, *out_mods])
        lines = [*self.comment_lines(sec.comments, ""), head]
        lines.extend(self.decl_lines(sec.items, IND, sym))
        lines.extend(self.comment_lines(sec.end_comments, IND))
        lines.append("END_VAR")
        return lines

    # -- объявления --------------------------------------------------------------------
    def decl_lines(
        self,
        items: Sequence[VarDecl | RawDecl],
        ind: str,
        owner: S.BlockSym,
        inits: dict[str, InitNode] | None = None,
        struct_prefix: str = "",
    ) -> list[str]:
        out: list[str] = []
        for d in items:
            self._line_hint = d.span.line
            pre = self.comment_lines(d.comments, ind)
            self.push()
            if isinstance(d, RawDecl):
                self.pop()
                note = Note(TODO, "parse.decl", f"объявление не разобрано: {d.reason}", d.span.line, owner.name)
                out += pre + self.note_lines([note], ind) + self.original_lines(d.text, d.span.start, ind)
                self.commit(Frame(notes=[note]), Item("decl", TODO, d.span.line, "объявление", owner.name))
                continue
            label = "переменная " + ", ".join(d.names)
            try:
                code = self.decl_line(d, ind, owner, inits, struct_prefix)
            except Unsupported as u:
                self.pop()
                note = Note(TODO, u.rule, u.reason, d.span.line, owner.name)
                out += pre + self.note_lines([note], ind) + self.original_lines(self.src(d.span), d.span.start, ind)
                self.commit(Frame(notes=[note]), Item("decl", TODO, d.span.line, label, owner.name))
                continue
            frame = self.pop()
            self.trailing(code, d.trailing)
            code = [w for line in code for w in wrap_line(line)]
            out += pre + self.note_lines(frame.notes, ind) + code
            self.commit(frame, Item("decl", self.status_of(frame.notes), d.span.line, label, owner.name))
        return out

    def src(self, span: Span) -> str:
        """Исходный текст фрагмента файла текущего блока."""
        assert self.cur is not None
        return self.cur.file.text[span.start : span.end]

    def decl_line(
        self,
        d: VarDecl,
        ind: str,
        owner: S.BlockSym,
        inits: dict[str, InitNode] | None,
        struct_prefix: str,
    ) -> list[str]:
        if d.at is not None:
            raise Unsupported("AT (наложение переменных S7) — переписать через UNION или битовый доступ", "decl.at")
        self.attributes(d.attributes)
        scope = self.scopes.get(owner.name.lower(), {})
        if struct_prefix:
            names = [M.sanitize(n) for n in d.names]
        else:
            names = [scope[n.lower()].st_name if n.lower() in scope else M.sanitize(n) for n in d.names]
        for orig, new in zip(d.names, names, strict=True):
            if new != orig and M.is_plain_ident(orig):
                self.check("name.renamed", f"имя «{orig}» переименовано в «{new}» (ключевое слово CODESYS или повтор)")
            elif new != orig:
                self.hit("name.sanitized")
        field_name = f"{struct_prefix}_{d.names[0]}" if struct_prefix else d.names[0]
        type_text = self.map_type(d.type, owner, field_name)
        default = ""
        if d.init is not None:
            var0 = scope.get(d.names[0].lower()) if not struct_prefix else None
            default = " := " + self.init_text(d.init, _ty_name(var0.ty) if var0 else None)
        texts: list[str] = []
        for n in d.names:
            node = inits.get(n.lower()) if inits is not None else None
            if node is None:
                texts.append(default)
                continue
            var = scope.get(n.lower())
            try:
                texts.append(" := " + self.render_init(node, var.ty if var else None, d.type, default=d.init))
            except Unsupported as u:
                self.note(TODO, u.rule, u.reason)
                texts.append(default)
        if len(set(texts)) == 1:
            return [f"{ind}{', '.join(names)} : {type_text}{texts[0]};"]
        return [f"{ind}{name} : {type_text}{text};" for name, text in zip(names, texts, strict=True)]

    def init_text(self, init: Expr | ArrayInit, expect: str | None) -> str:
        if isinstance(init, ArrayInit):
            parts: list[str] = []
            for count, value in init.items:
                text = self.init_text(value, None)
                parts.append(f"{self.ex(count)}({text})" if count is not None else text)
            return "[" + ", ".join(parts) + "]"
        return self.ex(init, expect)

    def attributes(self, attrs: dict[str, str]) -> None:
        hidden = [
            k
            for k in ("ExternalAccessible", "ExternalVisible", "ExternalWritable")
            if attrs.get(k, "").lower() == "false"
        ]
        if hidden:
            self.check(
                "decl.hmi_access",
                "S7: " + ", ".join(hidden) + " = False — в CODESYS видимость для HMI/OPC UA задаётся символьной "
                "конфигурацией",
            )
        for key in attrs:
            if key in ("InstructionName", "LibVersion", "S7_SetPoint") or key in hidden:
                self.hit("decl.attr_dropped")
            elif key not in ("ExternalAccessible", "ExternalVisible", "ExternalWritable"):
                self.check("decl.attr", f"атрибут S7 {key} не переносится")

    def fb_rule_note(self, rule: M.FbRule) -> None:
        if rule.message:
            self.check(rule.rule, rule.message)
        else:
            self.hit(rule.rule)
        if rule.target in M.SUPPORT_DEPENDENCIES:
            self.support.add(rule.target)

    def map_type(self, t: TypeRef, owner: S.BlockSym, field_name: str) -> str:
        if isinstance(t, StringType):
            base = "WSTRING" if t.wide else "STRING"
            if t.length is None:
                self.hit("type.string_default")
                return f"{base}(254)"
            self.hit("type.string")
            return f"{base}({self.ex(t.length)})"
        if isinstance(t, ArrayType):
            ranges: list[str] = []
            for r in t.ranges:
                if r is None:
                    self.check("type.array_star", "Array[*]: в CODESYS — только для VAR_IN_OUT, сверить")
                    ranges.append("*")
                else:
                    ranges.append(f"{self.ex(r[0])}..{self.ex(r[1])}")
            self.hit("type.array")
            return f"ARRAY[{', '.join(ranges)}] OF {self.map_type(t.element, owner, field_name)}"
        if isinstance(t, StructType):
            name = self.struct_name(owner, field_name)
            self.struct_dut(name, owner, field_name, t)
            return name
        unsupported = self.unsupported_type(t, owner, field_name)
        if unsupported is not None:
            raise Unsupported(*unsupported)
        assert isinstance(t, NamedType)
        upper = t.name.upper()
        if not t.quoted:
            if upper in M.ELEMENTARY:
                self.hit("type.elementary")
                return M.ELEMENTARY[upper]
            if upper in M.CHECKED_TYPES:
                text, rule_id, message = M.CHECKED_TYPES[upper]
                self.check(rule_id, message)
                return text
            if upper in M.GENERIC_INSTANCE_TYPES:
                inferred = self.generic_local.get(f"{owner.name.lower()}.{field_name.lower()}", "")
                rule = self.fb_types[inferred]
                self.check("fb.generic", f"{t.name} → {rule.target} (по вызову .{inferred.split('_')[0]})")
                if rule.target in M.SUPPORT_DEPENDENCIES:
                    self.support.add(rule.target)
                return rule.target
            if upper in self.fb_types:
                rule = self.fb_types[upper]
                self.fb_rule_note(rule)
                return rule.target
        sym = self.p.block(t.name)
        if sym is not None:
            self.hit("type.user")
            return sym.st_name
        self.check("type.unknown", f"тип «{t.name}» не найден в корпусе — перенесён по имени")
        return M.sanitize(t.name)

    # -- операторы ---------------------------------------------------------------------
    def body(self, stmts: Sequence[Stmt], ind: str) -> list[str]:
        """Операторы подряд; пустая строка между группами операторов исходника сохраняется."""
        out: list[str] = []
        text = self.cur.file.text if self.cur else ""
        prev_end = -1
        for s in stmts:
            lines = self.stmt(s, ind)
            if lines and out and prev_end >= 0 and _BLANK_LINE_RE.search(text, prev_end, max(prev_end, s.span.start)):
                out.append("")
            out.extend(lines)
            if not isinstance(s, CommentStmt):
                prev_end = s.span.end
        return out

    def stmt(self, s: Stmt, ind: str) -> list[str]:
        self._line_hint = s.span.line
        pre = self.comment_lines(s.comments, ind)
        if isinstance(s, CommentStmt):
            return pre
        if isinstance(s, Empty):
            # явный пустой оператор SCL ';' переносится как есть, вместе с комментарием в строке
            empty = [*pre, f"{ind};"]
            self.trailing(empty, s.trailing)
            self.hit("stmt.empty")
            return empty
        label = _stmt_label(s)
        self.push()
        lowered = self.lowered_notes(s.span.line)
        todo = [n for n in lowered if n.severity == TODO]
        if todo and not isinstance(s, RawStmt):
            self.pop()
            note = Note(TODO, todo[0].rule, todo[0].message, s.span.line, self._block_name())
            lines = pre + self.note_lines([note], ind) + self.original_lines(self.src(s.span), s.span.start, ind)
            self.trailing(lines, s.trailing)
            self.commit(Frame(notes=[note]), Item("stmt", TODO, s.span.line, label, self._block_name()))
            return lines
        for n in lowered:
            self.note(n.severity, n.rule, n.message, s.span.line)
        if isinstance(s, RawStmt):
            self.pop()
            note = Note(TODO, "parse.stmt", f"оператор не разобран: {s.reason}", s.span.line, self._block_name())
            lines = pre + self.note_lines([note], ind) + self.original_lines(s.text, s.span.start, ind)
            self.trailing(lines, s.trailing)
            self.commit(Frame(notes=[note]), Item("stmt", TODO, s.span.line, label, self._block_name()))
            return lines
        try:
            code = self._stmt(s, ind)
        except Unsupported as u:
            self.pop()
            note = Note(TODO, u.rule, u.reason, s.span.line, self._block_name())
            lines = pre + self.note_lines([note], ind) + self.original_lines(self.src(s.span), s.span.start, ind)
            self.trailing(lines, s.trailing)
            self.commit(Frame(notes=[note]), Item("stmt", TODO, s.span.line, label, self._block_name()))
            return lines
        frame = self.pop()
        self.trailing(code, s.trailing)
        code = [w for line in code for w in wrap_line(line)]
        lines = pre + self.note_lines(frame.notes, ind) + code
        status = self.status_of(frame.notes)
        self.commit(frame, Item("stmt", status, s.span.line, label, self._block_name()))
        return lines

    def _block_name(self) -> str:
        return self.cur.sym.name if self.cur else ""

    def lowered_notes(self, line: int) -> list[LowerNote]:
        """Пометки понижения LAD/FBD/STL для оператора строки line синтезированного SCL."""
        lowering = self.cur.file.lowering if self.cur is not None else None
        if lowering is None:
            return []
        return list(lowering.notes.get(line, ()))

    def _stmt(self, s: Stmt, ind: str) -> list[str]:
        if isinstance(s, Assign):
            return [ind + self.assign(s)]
        if isinstance(s, CallStmt):
            return [f"{ind}{self.call(s.call, None)};"]
        if isinstance(s, If):
            lines: list[str] = []
            for n, (cond, body) in enumerate(s.branches):
                kw = "IF" if n == 0 else "ELSIF"
                lines.append(f"{ind}{kw} {self.ex(cond, 'BOOL')} THEN")
                lines.extend(self.block_body(body, ind + IND))
            if s.else_body is not None:
                lines.append(f"{ind}ELSE")
                lines.extend(self.block_body(s.else_body, ind + IND))
            lines.append(f"{ind}END_IF")
            return lines
        if isinstance(s, Case):
            sel_t = _ty_name(self.infer(s.selector))
            lines = [f"{ind}CASE {self.ex(s.selector, sel_t)} OF"]
            for clause in s.clauses:
                labels = ", ".join(
                    f"{self.ex(lb.lo)}..{self.ex(lb.hi)}" if isinstance(lb, CaseRange) else self.ex(lb)
                    for lb in clause.labels
                )
                lines.extend(self.comment_lines(clause.comments, ind + IND))
                lines.append(f"{ind}{IND}{labels}:")
                lines.extend(self.block_body(clause.body, ind + IND * 2))
            if s.else_body is not None:
                lines.append(f"{ind}ELSE")
                lines.extend(self.block_body(s.else_body, ind + IND))
            lines.append(f"{ind}END_CASE")
            return lines
        if isinstance(s, For):
            step = f" BY {self.ex(s.step)}" if s.step is not None else ""
            head = f"{ind}FOR {self.ex(s.var)} := {self.ex(s.start)} TO {self.ex(s.end)}{step} DO"
            return [head, *self.block_body(s.body, ind + IND), f"{ind}END_FOR"]
        if isinstance(s, While):
            head = f"{ind}WHILE {self.ex(s.cond, 'BOOL')} DO"
            return [head, *self.block_body(s.body, ind + IND), f"{ind}END_WHILE"]
        if isinstance(s, Repeat):
            rbody = self.block_body(s.body, ind + IND)
            self._line_hint = s.span.line
            return [f"{ind}REPEAT", *rbody, f"{ind}UNTIL {self.ex(s.cond, 'BOOL')}", f"{ind}END_REPEAT"]
        if isinstance(s, Exit):
            return [f"{ind}EXIT;"]
        if isinstance(s, Continue):
            return [f"{ind}CONTINUE;"]
        if isinstance(s, Return):
            return [f"{ind}RETURN;"]
        if isinstance(s, Region):
            self.hit("stmt.region")
            name = f" {s.name}" if s.name else ""
            return [f"{ind}// REGION{name}", *self.body(s.body, ind), f"{ind}// END_REGION{name}"]
        if isinstance(s, Goto):
            raise Unsupported("GOTO — переходы не переносятся (переписать структурно)", "stmt.goto")
        if isinstance(s, Label):
            raise Unsupported("метка перехода — переходы не переносятся", "stmt.label")
        if isinstance(s, Pragma):
            self.check("stmt.pragma", f"прагма S7 {s.text} опущена")
            return []
        raise Unsupported(f"оператор {type(s).__name__} не поддерживается", "stmt.unknown")

    def block_body(self, body: Sequence[Stmt], ind: str) -> list[str]:
        lines = self.body(body, ind)
        if not any(line.strip() and not line.strip().startswith("//") for line in lines):
            lines.append(f"{ind}; // нет операторов")
        return lines

    def assign(self, s: Assign) -> str:
        if s.op == "?=":
            raise Unsupported("?= (присваивание с проверкой типа) не поддерживается", "stmt.try_assign")
        if isinstance(s.target, Call | Literal | Binary | Unary):
            raise Unsupported("слева от := не переменная", "stmt.lvalue")
        if isinstance(s.target, Slice) and s.target.size in ("B", "W", "D"):
            raise Unsupported(
                f"запись в срез .%{s.target.size}{s.target.number} — в CODESYS только битовый доступ; "
                "переписать маской и сдвигом",
                "expr.slice_write",
            )
        target_ty = self.infer(s.target)
        value_ty = self.infer(s.value)
        target = self.ex(s.target, _ty_name(value_ty))
        value, prec = self.expr(s.value, _ty_name(target_ty))
        if isinstance(s.value, Member) and s.op == ":=":
            base_ty = self.infer(s.value.base)
            if base_ty is not None and self.fb_rule_for(base_ty.name) is not None:
                converted = self.instruction_conversion(value, value_ty, _ty_name(target_ty))
                if converted != value:
                    value, prec = converted, PRIMARY
        value = self.scale_x_int(s.value, value, _ty_name(target_ty))
        if s.op in ("+=", "-=", "*=", "/="):
            op = s.op[0]
            self.hit("stmt.compound_assign")
            self.arith_checks(op, s.target, s.value)
            if prec <= PREC[op]:
                value = f"({value})"
            return f"{target} := {target} {op} {value};"
        return f"{target} := {value};"

    def scale_x_int(self, e: Expr, text: str, target: str | None) -> str:
        """SCALE_X (и SCALE_X_<тип>) с целым или битовым OUT: F_ScaleX возвращает REAL — явное REAL_TO_<тип>.

        В S7 тип OUT SCALE_X задаёт цель (переменная или параметр), в CODESYS F_ScaleX всегда REAL.
        """
        if not (
            isinstance(e, Call)
            and isinstance(e.callee, Ident)
            and (e.callee.name.upper() == "SCALE_X" or e.callee.name.upper().startswith("SCALE_X_"))
            and target is not None
            and (target in INTEGER_TYPES or target in BIT_TYPES)
        ):
            return text
        self.check("func.scale_x_int", f"SCALE_X с целым OUT: REAL_TO_{target} округляет — сверить с S7")
        return f"REAL_TO_{target}({text})"

    # -- выражения ---------------------------------------------------------------------
    def ex(self, e: Expr, expect: str | None = None) -> str:
        return self.expr(e, expect)[0]

    def expr(self, e: Expr, expect: str | None = None) -> tuple[str, int]:
        if isinstance(e, Literal):
            mapped = M.map_literal(e.kind, e.text)
            if mapped.severity == TODO:
                raise Unsupported(mapped.message, mapped.rule)
            if mapped.severity == CHECK:
                self.check(mapped.rule, mapped.message)
            return mapped.text, PRIMARY
        if isinstance(e, LocalRef):
            return self.local_text(e.name), PRIMARY
        if isinstance(e, Ident):
            return self.ident_text(e.name, expect), PRIMARY
        if isinstance(e, GlobalRef):
            return self.global_text(e.name, expect, member=False), PRIMARY
        if isinstance(e, AddressRef):
            return self.address_text(e.text, expect), PRIMARY
        if isinstance(e, Member):
            return self.member_text(e, expect), PRIMARY
        if isinstance(e, Index):
            base_ty = self.infer(e.base)
            if base_ty is not None and base_ty.name in ("STRING", "WSTRING"):
                raise Unsupported(
                    "символ строки по индексу: в S7 — CHAR (WCHAR), нумерация с 1; в CODESYS индекс строки даёт "
                    "BYTE (WORD) — код символа, нумерацию сверить с источником; переписать через MID/REPLACE",
                    "expr.string_index",
                )
            if isinstance(e.base, GlobalRef):
                base = self.global_text(e.base.name, None, member=True)
            else:
                base = self.postfix_text(e.base, None)
            return f"{base}[{', '.join(self.ex(i) for i in e.indices)}]", PRIMARY
        if isinstance(e, Slice):
            if e.size not in ("X", ""):
                return self.slice_read(e), PRIMARY
            self.hit("expr.slice_bit")
            return f"{self.postfix_text(e.base, 'WORD')}.{e.number}", PRIMARY
        if isinstance(e, Call):
            return self.call(e, expect), PRIMARY
        if isinstance(e, Unary):
            operand, oprec = self.expr(e.operand, expect)
            if oprec < UNARY_PREC or isinstance(e.operand, Unary):
                operand = f"({operand})"
            if e.op == "NOT":
                return f"NOT {operand}", UNARY_PREC
            if e.op == "+":
                return operand, UNARY_PREC
            operand_ty = _ty_name(self.infer(e.operand))
            if operand_ty in TIME_LIKE:
                self.check(
                    "expr.time_sub",
                    f"унарный минус {operand_ty}: в S7 TIME со знаком, в CODESYS без знака — отрицательное значение "
                    "переполняется",
                )
            return f"-{operand}", UNARY_PREC
        if isinstance(e, Binary):
            return self.binary(e, expect)
        raise Unsupported(f"выражение {type(e).__name__} не поддерживается", "expr.unknown")

    def binary(self, e: Binary, expect: str | None) -> tuple[str, int]:
        if e.op == "**":
            types = {_ty_name(self.infer(e.left)), _ty_name(self.infer(e.right))}
            if types - {"REAL", "LREAL"}:
                self.check("expr.power", "** → EXPT: тип результата для целых операндов сверить (в S7 — REAL/LREAL)")
            else:
                self.hit("expr.power")
            left = self.ex(e.left, "ANY_NUM")
            right = self.ex(e.right, "ANY_NUM")
            return f"EXPT({left}, {right})", PRIMARY
        op = e.op
        if op == "&":
            op = "AND"
            self.hit("expr.ampersand")
        prec = PREC[e.op]
        if e.op in COMPARISONS:
            lt = _ty_name(self.infer(e.right)) or "ANY_NUM"
            rt = _ty_name(self.infer(e.left)) or "ANY_NUM"
            left, lp = self.expr(e.left, lt)
            right, rp = self.expr(e.right, rt)
        elif e.op in LOGICAL:
            sub = expect if expect in BIT_TYPES or expect == "BOOL" else None
            left, lp = self.expr(e.left, sub or _ty_name(self.infer(e.right)) or "BOOL")
            right, rp = self.expr(e.right, sub or _ty_name(self.infer(e.left)) or "BOOL")
        else:
            sub = expect if expect not in (None, "BOOL") else None
            left, lp = self.expr(e.left, sub or _ty_name(self.infer(e.right)) or "ANY_NUM")
            right, rp = self.expr(e.right, sub or _ty_name(self.infer(e.left)) or "ANY_NUM")
        if lp < prec:
            left = f"({left})"
        if rp <= prec or (isinstance(e.right, Unary) and e.right.op in ("-", "+") and op in ("+", "-")):
            right = f"({right})"
        self.arith_checks(e.op, e.left, e.right)
        return f"{left} {op} {right}", prec

    def arith_checks(self, op: str, left: Expr, right: Expr) -> None:
        """Пометки для арифметики, смысл которой в S7 и CODESYS расходится (вычитание TIME, деление целых)."""
        if op == "-":
            lt = _ty_name(self.infer(left))
            if lt in TIME_LIKE:
                self.check(
                    "expr.time_sub",
                    f"вычитание {lt}: в S7 TIME со знаком (разность может быть отрицательной), в CODESYS TIME, "
                    "LTIME, TOD, DT без знака — отрицательная разность переполняется; проверить порядок операндов "
                    "и сравнения с T#0s",
                )
        elif op in ("/", "MOD"):
            types = {_ty_name(self.infer(left)), _ty_name(self.infer(right))} - {None}
            if types & INTEGER_LIKE and not types & {"REAL", "LREAL"} and not self.is_constant(right):
                what = "деление" if op == "/" else "MOD"
                self.check(
                    "expr.div_int",
                    f"целочисленное {what} на переменную: делитель 0 в CODESYS — исключение и останов задачи, "
                    "если в проекте нет функций неявной проверки CheckDivDInt/CheckDivLInt; в S7 CPU продолжает "
                    "работу (результат и ENO — сверить с источником); проверить делитель",
                )

    def is_constant(self, e: Expr) -> bool:
        """Значение известно при компиляции: литерал, VAR CONSTANT, константа пользователя, выражение из них."""
        if isinstance(e, Literal):
            return True
        if isinstance(e, LocalRef | Ident):
            var = self.lookup(e.name)
            if var is not None:
                return var.constant
            tag = self.p.tag(e.name) if isinstance(e, Ident) else None
            return tag is not None and tag.gvl == S.GVL_USER_CONST
        if isinstance(e, GlobalRef):
            tag = self.p.tag(e.name)
            return tag is not None and tag.gvl == S.GVL_USER_CONST
        if isinstance(e, Unary):
            return self.is_constant(e.operand)
        if isinstance(e, Binary):
            return self.is_constant(e.left) and self.is_constant(e.right)
        return False

    def slice_read(self, e: Slice) -> str:
        """Чтение среза .%Bn/.%Wn/.%Dn: <тип>_TO_<часть>(SHR(x, k)); нумерация S7 — от младшей части."""
        widths = {"B": 8, "W": 16, "D": 32}
        part = {"B": "BYTE", "W": "WORD", "D": "DWORD"}[e.size]
        base_ty = self.infer(e.base)
        base_bits = {"WORD": 16, "DWORD": 32, "LWORD": 64}.get(base_ty.name if base_ty else "", 0)
        shift = widths[e.size] * e.number
        if not base_bits or shift + widths[e.size] > base_bits:
            raise Unsupported(
                f"срез .%{e.size}{e.number}: тип переменной не WORD/DWORD/LWORD или срез вне её — перенести вручную",
                "expr.slice",
            )
        assert base_ty is not None
        base = self.postfix_text(e.base, None)
        inner = f"SHR({base}, {shift})" if shift else base
        self.check(
            "expr.slice_read",
            f"срез .%{e.size}{e.number} → {base_ty.name}_TO_{part}(SHR(...)): нумерация срезов S7 от младшей "
            "части — сверить с источником",
        )
        return f"{base_ty.name}_TO_{part}({inner})"

    def postfix_text(self, e: Expr, expect: str | None) -> str:
        text, prec = self.expr(e, expect)
        return text if prec >= PRIMARY else f"({text})"

    def lookup(self, name: str) -> LocalVar | None:
        if self.cur is None:
            return None
        return self.cur.scope.get(name.lower())

    def local_text(self, name: str) -> str:
        var = self.lookup(name)
        if var is not None:
            self.use_var(var)
            return var.st_name
        assert self.cur is not None
        if self.cur.fc_name and name.lower() == self.cur.fc_name.lower():
            self.hit("fc.return")
            return self.cur.sym.st_name
        if name.upper() in ("RET_VAL",) and self.cur.fc_name:
            self.hit("fc.return")
            return self.cur.sym.st_name
        self.check("name.undeclared", f"#{name} не объявлена в блоке")
        return M.sanitize(name)

    def ident_text(self, name: str, expect: str | None) -> str:
        upper = name.upper()
        if upper in ("ENO", "EN", "OK"):
            raise Unsupported(f"{name}: флаги EN/ENO/OK S7 не поддерживаются", "expr.eno")
        if self.lookup(name) is not None or (self.cur and self.cur.fc_name.lower() == name.lower()):
            return self.local_text(name)
        if self.p.block(name) is not None or self.p.tag(name) is not None:
            return self.global_text(name, expect, member=False)
        self.check("name.plain", f"имя «{name}» без # и кавычек не найдено — перенесено как есть")
        return M.sanitize(name)

    def global_text(self, name: str, expect: str | None, member: bool) -> str:
        assert self.cur is not None
        where = f"{self.cur.display}:{self._line_hint}"
        sym = self.p.block(name)
        if sym is not None:
            if sym.kind == BLOCK_DB:
                if sym.db_role == S.DB_GLOBAL:
                    if not member:
                        raise Unsupported(f'обращение к DB "{name}" целиком (без элемента)', "expr.db_whole")
                    self.hit("access.db_global")
                    return sym.st_name
                self.hit("access.db_instance")
                return f"{self.g(S.GVL_INSTANCES)}.{sym.st_name}"
            if sym.kind == BLOCK_FC and self.cur.fc_name.lower() == name.lower():
                self.hit("fc.return")
                return sym.st_name
            raise Unsupported(f"«{name}» ({sym.kind}) использован как значение", "expr.block_value")
        tag = self.p.tag(name)
        if tag is not None:
            tag.used = True
            if tag.gvl == S.TAG_S5:
                raise Unsupported(f'тег "{name}" ({tag.raw_address}) — таймер/счётчик S5, в CODESYS нет', "tag.s5")
            if tag.address is not None:
                var = self.p.io_var(tag.address, where)
                self.hit("access.io_tag")
                return f"{self.g(var.gvl)}.{var.st_name}"
            self.hit("access.tag")
            return f"{self.g(tag.gvl)}.{tag.st_name}"
        implicit = self.implicit.get(name.lower())
        if implicit is not None:
            return f"{self.g(S.GVL_INSTANCES)}.{implicit[0]}"
        if member:
            raise Unsupported(f'DB "{name}" не найден в корпусе — добавьте его исходник', "sym.unknown_db")
        unknown = self.p.unknown.get(name.lower())
        if unknown is None:
            taken = {u.st_name.lower() for u in self.p.unknown.values()}
            taken |= {t.st_name.lower() for t in self.p.tags.values() if t.gvl == S.GVL_TAGS}
            st_name = base = M.sanitize(name)
            n = 2
            while st_name.lower() in taken:
                st_name = f"{base}_{n}"
                n += 1
            unknown = S.UnknownSym(name=name, st_name=st_name)
            self.p.unknown[name.lower()] = unknown
        if expect:
            unknown.types.append(expect)
        unknown.lines.append(where)
        tags_gvl = self.g(S.GVL_TAGS)
        self.check("sym.unknown", f'символ "{name}" не найден в корпусе и таблице тегов — объявлен в {tags_gvl}')
        return f"{tags_gvl}.{unknown.st_name}"

    def address_text(self, text: str, expect: str | None) -> str:
        assert self.cur is not None
        addr = S.parse_address(text)
        if addr is None:
            raise Unsupported(f"адрес {text} не поддерживается (только %I, %Q, %M)", "addr.unsupported")
        if addr.peripheral:
            raise Unsupported(f"{text}: прямой доступ к периферии (:P) не поддерживается", "addr.peripheral")
        var = self.p.io_var(addr, f"{self.cur.display}:{self._line_hint}")
        if expect and var.type_name:
            if addr.size == "W" and expect in ("INT", "ANY_NUM", "UINT"):
                var.type_name = "INT" if expect == "ANY_NUM" else expect
            elif addr.size == "D" and expect in ("DINT", "REAL", "UDINT", "ANY_NUM"):
                var.type_name = "DINT" if expect == "ANY_NUM" else expect
            elif addr.size == "B" and expect in ("SINT", "USINT"):
                var.type_name = expect
        self.hit("access.address")
        return f"{self.g(var.gvl)}.{var.st_name}"

    def member_text(self, e: Member, expect: str | None) -> str:
        base = e.base
        if isinstance(base, GlobalRef):
            sym = self.p.block(base.name)
            if sym is not None and sym.kind == BLOCK_DB and sym.db_role == S.DB_GLOBAL:
                scope = self.scopes[sym.name.lower()]
                var = scope.get(e.name.lower())
                if var is None:
                    self.check("access.db_member", f'элемент «{e.name}» не найден в DB "{base.name}"')
                    return f"{sym.st_name}.{M.sanitize(e.name)}"
                self.use_var(var)
                self.hit("access.db_global")
                return f"{sym.st_name}.{var.st_name}"
            base_text = self.global_text(base.name, None, member=True)
        else:
            base_text = self.postfix_text(base, None)
        base_ty = self.infer(base)
        name = M.sanitize(e.name)
        if base_ty is not None:
            rule = self.fb_rule_for(base_ty.name)
            if rule is not None and e.name.upper() in rule.members:
                name = rule.members[e.name.upper()]
                self.hit("access.member_renamed")
            tscope = self.type_scopes.get(base_ty.name.lower())
            if tscope is not None and e.name.lower() in tscope:
                var = tscope[e.name.lower()]
                self.use_var(var)
                name = var.st_name
                fb = self.p.block(base_ty.name) or self._block_by_st(base_ty.name)
                if fb is not None and fb.kind == BLOCK_FB and var.section in ("VAR", "VAR_TEMP", "VAR_STAT"):
                    self.check(
                        "access.fb_static",
                        f"доступ к внутренней переменной «{e.name}» экземпляра ФБ: в CODESYS снаружи "
                        "доступны входы и выходы — сверить",
                    )
        return f"{base_text}.{name}"

    def _block_by_st(self, st_name: str) -> S.BlockSym | None:
        for sym in self.p.blocks.values():
            if sym.st_name.lower() == st_name.lower():
                return sym
        return None

    def fb_rule_for(self, type_name: str) -> M.FbRule | None:
        for rule in self.fb_types.values():
            if rule.target == type_name:
                return rule
        return None

    # -- вызовы ------------------------------------------------------------------------
    def call(self, c: Call, expect: str | None) -> str:
        callee = c.callee
        if isinstance(callee, Ident):
            name = callee.name
            upper = name.upper()
            var = self.lookup(name)
            if var is not None:
                return self.instance_call(var.st_name, var, c.args)
            if upper in M.S5_TIMER_CALLS or upper in M.S5_COUNTER_CALLS:
                return self.s5_call(c, upper)
            if upper == "S7_TIMEDIFF" and len(c.args) == 2:
                # время активности шага ST-двойника GRAPH: разность моментов F_S7Now по модулю 2^32
                self.support.add("F_S7TimeDiff")
                self.hit("graph.time")
                now, start = (self.ex(a.value, "TIME") for a in c.args)
                return f"F_S7TimeDiff({now}, {start})"
            if upper == "S7_NOW" and not c.args:
                # время ST-двойника GRAPH (lower/seq_to_ast.py): F_S7Now — TIME(), в тестах — часы GVL_S7Clock
                self.support.add("F_S7Now")
                self.hit("graph.time")
                return "F_S7Now()"
            rule = M.FUNCTIONS.get(upper)
            if rule is None and (upper.startswith("NORM_X_") or upper.startswith("SCALE_X_")):
                rule = M.FUNCTIONS[upper[: upper.index("_X_") + 2]]
                self.check("func.typed_variant", f"{name}: типизированный вариант сведён к REAL")
            if rule is not None:
                return self.builtin(rule, c, upper)
            reason = M.unsupported_function(upper)
            if reason is not None:
                raise Unsupported(f"{name}: {reason}", "func.unsupported")
            conv = M.conversion_rule(upper)
            if conv is not None:
                return self.builtin(conv, c, upper)
            sym = self.p.block(name)
            if sym is not None:
                return self.block_call(sym, c)
            self.check("call.unknown", f"функция {name} не найдена в корпусе — вызов перенесён как есть")
            return f"{M.sanitize(name)}({self.plain_args(c.args)})"
        if isinstance(callee, GlobalRef):
            sym = self.p.block(callee.name)
            if sym is not None:
                return self.block_call(sym, c)
            fb = self.guess_instance_fb(callee.name)
            if fb is not None:
                st = self.implicit_instance(callee.name, fb.st_name)
                scope = self.scopes[fb.name.lower()]
                return f"{self.g(S.GVL_INSTANCES)}.{st}({self.map_args(c.args, scope, None)})"
            self.check("call.unknown", f'блок "{callee.name}" не найден в корпусе — вызов перенесён как функция')
            return f"{M.sanitize(callee.name)}({self.plain_args(c.args)})"
        if isinstance(callee, LocalRef):
            var = self.lookup(callee.name)
            if var is None:
                self.check("name.undeclared", f"экземпляр #{callee.name} не объявлен в блоке")
                return f"{M.sanitize(callee.name)}({self.plain_args(c.args)})"
            return self.instance_call(var.st_name, var, c.args)
        if isinstance(callee, Member) and callee.name.upper() in M.GENERIC_METHODS:
            return self.generic_call(callee, c.args)
        if isinstance(callee, Member | Index):
            text = self.postfix_text(callee, None)
            self.check("call.member", "вызов экземпляра через элемент структуры/массива — проверить тип и параметры")
            return f"{text}({self.plain_args(c.args)})"
        raise Unsupported("вызов этого вида не поддерживается", "call.unsupported")

    def guess_instance_fb(self, name: str) -> S.BlockSym | None:
        lowered = name.lower()
        for suffix in ("_db", "_idb", "_instance", "db"):
            if lowered.endswith(suffix):
                fb = self.p.block(name[: -len(suffix)])
                if fb is not None and fb.kind == BLOCK_FB:
                    return fb
        return None

    def implicit_instance(self, name: str, type_st: str) -> str:
        key = name.lower()
        if key not in self.implicit:
            self.implicit[key] = (M.sanitize(name), type_st)
        self.check(
            "db.implicit_instance",
            f'экземплярный DB "{name}" не найден в корпусе — создан в {self.g(S.GVL_INSTANCES)} с типом {type_st}',
        )
        return self.implicit[key][0]

    def generic_call(self, callee: Member, args: tuple[Arg, ...]) -> str:
        assert self.cur is not None
        method = callee.name.upper()
        base = callee.base
        if isinstance(base, GlobalRef):
            inferred = self.p.generic_types.get(base.name.lower(), method)
            rule = self.fb_types.get(inferred)
            if rule is None:
                raise Unsupported(f"{inferred}: нет аналога в CODESYS Standard", "fb.unsupported")
            if self.p.block(base.name) is None:
                self.implicit_instance(base.name, rule.target)
            base_text = self.global_text(base.name, None, member=False)
        else:
            if isinstance(base, LocalRef | Ident):
                key = f"{self.cur.sym.name.lower()}.{base.name.lower()}"
                inferred = self.generic_local.get(key, method)
            else:
                inferred = method
            rule = self.fb_types.get(inferred)
            if rule is None:
                raise Unsupported(f"{inferred}: нет аналога в CODESYS Standard", "fb.unsupported")
            base_text = self.postfix_text(base, None)
        self.hit("fb.generic_call")
        return f"{base_text}({self.map_args(args, None, rule)})"

    def instance_call(self, text: str, var: LocalVar, args: tuple[Arg, ...]) -> str:
        self.use_var(var)
        if var.fb_rule is not None:
            self.hit("call.instruction")
            return f"{text}({self.map_args(args, None, var.fb_rule)})"
        ty = var.ty
        scope = self.type_scopes.get(ty.name.lower()) if ty is not None else None
        if scope is None:
            self.check("call.instance_unknown", f"тип экземпляра {text} не найден в корпусе — параметры как есть")
        self.hit("call.multi_instance")
        return f"{text}({self.map_args(args, scope, None)})"

    def block_call(self, sym: S.BlockSym, c: Call) -> str:
        if sym.kind == BLOCK_FC:
            self.hit("call.fc")
            return f"{sym.st_name}({self.map_args(c.args, self.scopes[sym.name.lower()], None)})"
        if sym.kind == BLOCK_DB and sym.db_role == S.DB_INSTANCE:
            self.hit("call.instance_db")
            fb = self.p.block(sym.db_type_name)
            scope = self.scopes[fb.name.lower()] if fb is not None and fb.kind == BLOCK_FB else None
            rule = None
            if scope is None:
                inferred = self.p.generic_types.get(sym.name.lower(), sym.db_type_name.upper())
                rule = self.fb_types.get(inferred)
            return f"{self.g(S.GVL_INSTANCES)}.{sym.st_name}({self.map_args(c.args, scope, rule)})"
        raise Unsupported(f"вызов «{sym.name}» ({sym.kind}) не поддерживается", "call.unsupported")

    def plain_args(self, args: Sequence[Arg]) -> str:
        return self.map_args(args, None, None)

    def map_args(self, args: Sequence[Arg], scope: Scope | None, rule: M.FbRule | None) -> str:
        parts: list[str] = []
        types = INSTRUCTION_MEMBERS.get(rule.target, {}) if rule is not None else {}
        for a in args:
            if a.name is None:
                parts.append(self.ex(a.value))
                continue
            upper = a.name.upper()
            if upper in ("EN", "ENO"):
                raise Unsupported(f"параметр {a.name} (EN/ENO) не поддерживается", "call.eno")
            pname = a.name
            expect: str | None = None
            if rule is not None:
                if upper in rule.params:
                    pname = rule.params[upper]
                    self.hit("call.param_renamed")
                else:
                    pname = upper
                expect = types.get(pname.upper())
            elif scope is not None:
                var = scope.get(a.name.lower())
                if var is None:
                    self.check("call.param_unknown", f"параметр {a.name} не найден в интерфейсе вызываемого блока")
                    pname = M.sanitize(a.name)
                elif var.dropped:
                    self.note(
                        TODO,
                        "call.param_dropped",
                        f"параметр {a.name} не перенесён ({var.dropped}) — аргумент опущен",
                    )
                    continue
                else:
                    pname = var.st_name
                    expect = _ty_name(var.ty)
            op = " => " if a.output else " := "
            value = self.ex(a.value, expect)
            if not a.output:
                value = self.scale_x_int(a.value, value, expect)
            if rule is not None and not a.output:
                value = self.instruction_conversion(value, self.infer(a.value), expect)
            parts.append(f"{pname}{op}{value}")
        return ", ".join(parts)

    def instruction_conversion(self, text: str, source: Ty | None, target: str | None) -> str:
        """Явное преобразование там, где тип сменило сопоставление ФБ инструкции (CTU_INT.PV/CV: INT → WORD).

        В S7 вход PV и выход CV счётчика CTU_INT — INT, в CODESYS Standard — WORD: без явного
        преобразования CODESYS выдаёт предупреждение о неявном преобразовании со сменой знака.
        """
        numeric = INTEGER_TYPES | BIT_TYPES
        if source is None or target is None or source.name not in numeric or target not in numeric:
            return text
        if source.name == target:
            return text
        self.hit("conv.instruction_type")
        return f"{source.name}_TO_{target}({text})"

    def s5_call(self, c: Call, name: str) -> str:
        """Псевдовызов S5 из понижения STL → функция S7Compat с элементом GVL_S5Timers/GVL_S5Counters.

        S5_SD(T_NO := 3, RLO := x, TV := T#2S) → F_S5OnDelay(stTimer := GVL_S5Timers.aTimer[3], xRlo := x,
        wS5Time := F_S5TimeWord(T#2S)); значение S5TIME из слова (L MW10) передаётся как есть.
        """
        timer = name in M.S5_TIMER_CALLS
        target, _ret = (M.S5_TIMER_CALLS if timer else M.S5_COUNTER_CALLS)[name]
        args = {a.name.upper(): a.value for a in c.args if a.name}
        number = args.get("T_NO" if timer else "C_NO")
        if not isinstance(number, Literal) or number.kind != "int":
            raise Unsupported(f"{name}: номер таймера/счётчика не константа", "s5.address")
        n = int(number.text)
        self.s5_used["T" if timer else "C"].add(n)
        gvl = self.g(S.GVL_S5TIMERS if timer else S.GVL_S5COUNTERS)
        parts = [f"{'stTimer' if timer else 'stCounter'} := {gvl}.{'aTimer' if timer else 'aCounter'}[{n}]"]
        if "RLO" in args:
            parts.append(f"xRlo := {self.ex(args['RLO'], 'BOOL')}")
        for key, param in (("TV", "wS5Time"), ("PV", "wBcd")):
            if key not in args:
                continue
            value = args[key]
            kind = _ty_name(self.infer(value))
            text = self.ex(value, kind or None)
            if kind in ("TIME", "S5TIME"):
                self.support.add("F_S5TimeWord")
                text = f"F_S5TimeWord({text})"
            elif kind and kind != "WORD":
                text = f"{kind}_TO_WORD({text})"
            parts.append(f"{param} := {text}")
        self.support.add(target)
        self.support.add("ST_S5Timer" if timer else "ST_S5Counter")
        self.hit("s5.timer" if timer else "s5.counter")
        return f"{target}({', '.join(parts)})"

    def builtin(self, rule: M.FuncRule, c: Call, name: str) -> str:
        if rule.severity == TODO:
            raise Unsupported(rule.message, rule.rule)
        if rule.severity == CHECK:
            self.check(rule.rule, rule.message)
        else:
            self.hit(rule.rule)
        args = list(c.args)
        for a in args:
            if a.name and a.name.upper() in ("EN", "ENO"):
                raise Unsupported(f"{name}: параметр {a.name} (EN/ENO) не поддерживается", "call.eno")
        named = [a for a in args if a.name]
        ordered: list[Arg]
        if rule.params is None or not named:
            ordered = args
        elif len(named) != len(args):
            raise Unsupported(f"{name}: смешаны позиционные и именованные аргументы", "call.mixed_args")
        elif rule.variadic:
            fixed: dict[str, Arg | None] = dict.fromkeys(rule.params)
            var: dict[int, Arg] = {}
            for a in args:
                assert a.name is not None
                up = a.name.upper()
                if up in fixed:
                    fixed[up] = a
                elif up.startswith(rule.variadic) and up[len(rule.variadic) :].isdigit():
                    var[int(up[len(rule.variadic) :])] = a
                else:
                    raise Unsupported(f"{name}: параметр {a.name} не поддерживается", "call.param")
            missing = [k for k, v in fixed.items() if v is None]
            if missing:
                raise Unsupported(f"{name}: не задан параметр {missing[0]}", "call.param")
            ordered = [v for v in fixed.values() if v is not None] + [var[k] for k in sorted(var)]
        else:
            lookup = {a.name.upper(): a for a in args if a.name}
            extra = sorted(set(lookup) - set(rule.params))
            if extra:
                raise Unsupported(f"{name}: параметр {extra[0]} не поддерживается", "call.param")
            missing = [p for p in rule.params if p not in lookup]
            if missing:
                raise Unsupported(f"{name}: не задан параметр {missing[0]}", "call.param")
            ordered = [lookup[p] for p in rule.params]
        if any(a.output for a in ordered):
            raise Unsupported(f"{name}: выходные параметры (=>) встроенной функции не поддерживаются", "call.param")
        numeric = rule.named or name in ("ABS", "SQR", "SQRT", "LIMIT", "MIN", "MAX")
        rendered = [self.expr(a.value, "ANY_NUM" if numeric else None) for a in ordered]
        values = [text for text, _prec in rendered]
        if name == "SQR":
            if len(values) != 1:
                raise Unsupported("SQR: нужен один аргумент", "call.param")
            if not any(isinstance(sub, Call) for sub in walk_expr(ordered[0].value)):
                # без вызовов операнд можно вычислить дважды: SQR(x) = x * x точно, без EXPT
                text, prec = rendered[0]
                operand = text if prec > PREC["*"] else f"({text})"
                return f"{operand} * {operand}"
            self.check(
                "func.sqr",
                "SQR(выражение с вызовом) → EXPT(x, 2.0): результат EXPT CODESYS при отрицательном основании сверить "
                "с источником (в S7 SQR(-3.0) = 9.0); при сомнении — промежуточная переменная и x * x",
            )
            return f"EXPT({values[0]}, 2.0)"
        if rule.target == "":
            if len(values) != 1:
                raise Unsupported(f"{name}: нужен один аргумент", "call.param")
            text, prec = rendered[0]
            return text if prec >= PRIMARY else f"({text})"
        if rule.named:
            if len(values) != len(rule.named):
                raise Unsupported(f"{name}: нужно {len(rule.named)} аргумента", "call.param")
            self.support.add(rule.target)
            return f"{rule.target}({', '.join(f'{n} := {v}' for n, v in zip(rule.named, values, strict=True))})"
        if name == "ROUND" and len(ordered) == 1 and _ty_name(self.infer(ordered[0].value)) == "LREAL":
            # REAL_TO_DINT сузил бы LREAL до REAL (24 бита мантиссы) до округления
            return f"LREAL_TO_DINT({values[0]})"
        return f"{rule.target}({', '.join(values)})"

    # -- вывод типов -------------------------------------------------------------------
    def infer(self, e: Expr) -> Ty | None:
        if isinstance(e, Literal):
            name = M.literal_type(e.kind, e.text)
            return Ty(name) if name else None
        if isinstance(e, LocalRef | Ident):
            var = self.lookup(e.name)
            if var is not None:
                return var.ty
            if self.cur and self.cur.fc_name.lower() == e.name.lower():
                return self._fc_return_ty(self.cur.sym)
            if isinstance(e, Ident):
                tag = self.p.tag(e.name)
                if tag is not None:
                    return self._tag_ty(tag)
            return None
        if isinstance(e, GlobalRef):
            tag = self.p.tag(e.name)
            if tag is not None:
                return self._tag_ty(tag)
            sym = self.p.block(e.name)
            if sym is not None and sym.kind == BLOCK_DB and sym.db_role != S.DB_GLOBAL:
                if sym.db_role == S.DB_INSTANCE:
                    inferred = self.p.generic_types.get(sym.name.lower(), sym.db_type_name.upper())
                    rule = self.fb_types.get(inferred)
                    if rule is not None:
                        return Ty(rule.target)
                fb = self.p.block(sym.db_type_name)
                return Ty(fb.st_name) if fb else None
            if sym is not None and sym.kind == BLOCK_FC and self.cur and self.cur.fc_name.lower() == e.name.lower():
                return self._fc_return_ty(sym)
            return None
        if isinstance(e, AddressRef):
            addr = S.parse_address(e.text)
            if addr is None:
                return None
            for tag in self.p.tags.values():
                if tag.address is not None and tag.address.s7_text == addr.s7_text:
                    return self._tag_ty(tag) or Ty(addr.default_type)
            iov = self.p.io_vars.get(addr.s7_text)
            if iov is not None and iov.type_name:
                return Ty(iov.type_name)
            return Ty(addr.default_type)
        if isinstance(e, Member):
            if isinstance(e.base, GlobalRef):
                sym = self.p.block(e.base.name)
                if sym is not None and sym.kind == BLOCK_DB and sym.db_role == S.DB_GLOBAL:
                    var = self.scopes[sym.name.lower()].get(e.name.lower())
                    return var.ty if var else None
            base = self.infer(e.base)
            if base is None:
                return None
            rule = self.fb_rule_for(base.name)
            if rule is not None:
                member = rule.members.get(e.name.upper(), e.name.upper())
                found = INSTRUCTION_MEMBERS.get(rule.target, {}).get(member)
                return Ty(found) if found else None
            scope = self.type_scopes.get(base.name.lower())
            if scope is not None and e.name.lower() in scope:
                return scope[e.name.lower()].ty
            return None
        if isinstance(e, Index):
            base = self.infer(e.base)
            return base.elem if base is not None and base.name == "ARRAY" else None
        if isinstance(e, Slice):
            return Ty("BOOL")
        if isinstance(e, Call):
            return self._infer_call(e)
        if isinstance(e, Unary):
            if e.op == "NOT":
                return self.infer(e.operand) or Ty("BOOL")
            return self.infer(e.operand)
        if isinstance(e, Binary):
            if e.op in COMPARISONS:
                return Ty("BOOL")
            if e.op == "**":
                return Ty("REAL")
            return self.infer(e.left) or self.infer(e.right)

    def _tag_ty(self, tag: S.TagSym) -> Ty | None:
        try:
            parsed = Parser(tag.type_name).type_ref()
        except ParseError:
            return None
        upper = parsed.name.upper() if isinstance(parsed, NamedType) else ""
        if upper in M.ELEMENTARY:
            return Ty(M.ELEMENTARY[upper])
        if isinstance(parsed, StringType):
            return Ty("WSTRING" if parsed.wide else "STRING")
        return None

    def _fc_return_ty(self, sym: S.BlockSym) -> Ty | None:
        rt = sym.block.return_type
        if rt is None:
            return None
        return self.peek_type(rt, sym, sym.name)[0]

    def _infer_call(self, e: Call) -> Ty | None:
        callee = e.callee
        if isinstance(callee, Ident | GlobalRef):
            upper = callee.name.upper()
            s5 = M.S5_TIMER_CALLS.get(upper) or M.S5_COUNTER_CALLS.get(upper)
            if s5 is not None:
                return Ty(s5[1])
            if upper in ("S7_NOW", "S7_TIMEDIFF"):
                return Ty("TIME")
            if upper in ("NORM_X", "SCALE_X") or upper.startswith(("NORM_X_", "SCALE_X_")):
                return Ty("REAL")
            if upper in ("ABS", "LIMIT", "MIN", "MAX", "SEL", "MUX", "SQR", "SQRT", "EXPT"):
                values = [a.value for a in e.args if not (a.name and a.name.upper() in ("G", "K"))]
                for v in values:
                    t = self.infer(v)
                    if t is not None:
                        return t
                return None
            if upper in ("LEN", "FIND"):
                return Ty("INT")
            if upper in ("TRUNC", "ROUND"):
                return Ty("DINT")
            conv = M.conversion_rule(upper)
            if conv is not None and conv.target:
                return Ty(conv.target.split("_TO_")[1])
            sym = self.p.block(callee.name)
            if sym is not None and sym.kind == BLOCK_FC:
                return self._fc_return_ty(sym)
        return None

    # -- объекты проекта: экземпляры, ввод-вывод, теги ----------------------------------
    def project_objects(self) -> None:
        assert self.result is not None
        self.instances_gvl()
        self.io_gvls()
        self.tags_gvl()
        self.const_gvl()
        self.s5_gvls()

    def _project_header(self, purpose: str, doc: str) -> list[str]:
        return [
            *(_wrap_comment("// Назначение: ", purpose, "")),
            f"// Автор:      s7conv {__version__} (сгенерировано)",
            "// Версия:     не указана",
            f"// Документ:   {doc}",
        ]

    def _project_item(self, line_label: str, notes: list[Note]) -> None:
        assert self.result is not None
        self.result.items.append(Item("decl", self.status_of(notes), 0, line_label, ""))
        self.result.notes.extend(notes)

    def instances_gvl(self) -> None:
        if not self.instances and not self.implicit:
            return
        lines = [
            *self._project_header(
                "экземпляры функциональных блоков и типизированные DB S7 (экземплярные DB → переменные GVL)",
                "docs/MAPPING.md, раздел «DB»",
            ),
            "{attribute 'qualified_only'}",
            "VAR_GLOBAL",
        ]
        ordered = sorted(self.instances, key=lambda x: x[0].lower())
        retained: list[str] = []
        for st_name, type_text, source, notes, retain in ordered:
            target = retained if retain else lines
            target.extend(self.note_lines(notes, IND))
            target.extend(wrap_line(f"{IND}{st_name} : {type_text}; // {source}"))
        for key in sorted(self.implicit):
            st_name, type_st = self.implicit[key]
            note = Note(
                CHECK,
                "db.implicit_instance",
                f"экземплярный DB {st_name} выведен по вызову (исходника DB в корпусе нет)",
                0,
                st_name,
            )
            lines.extend(self.note_lines([note], IND))
            lines.append(f"{IND}{st_name} : {type_st};")
            self._project_item(f"экземпляр {st_name}", [note])
        lines.append("END_VAR")
        if retained:
            section = "VAR_GLOBAL PERSISTENT RETAIN" if self.o.retain_mode == "persistent" else "VAR_GLOBAL RETAIN"
            lines += [section, *retained, "END_VAR"]
        self.objects.append(
            L.StObject(L.KIND_GVL, self.g(S.GVL_INSTANCES), "\n".join(lines), folder=list(self.o.folder))
        )
        self.hit("gvl.instances")

    def s5_gvls(self) -> None:
        """GVL_S5Timers / GVL_S5Counters: слова таймеров и счётчиков S5 (в S7 — глобальные объекты CPU)."""
        for kind, gvl, member, type_name, what in (
            ("T", S.GVL_S5TIMERS, "aTimer", "ST_S5Timer", "таймеров"),
            ("C", S.GVL_S5COUNTERS, "aCounter", "ST_S5Counter", "счётчиков"),
        ):
            used = sorted(self.s5_used[kind])
            if not used:
                continue
            listed = ", ".join(f"{kind}{n}" for n in used)
            lines = [
                *self._project_header(
                    f"слова {what} S5 из STL (в S7 — глобальные объекты CPU, индекс — номер): {listed}",
                    "docs/MAPPING_STL.md, правила s5.timebase, s5.timer, s5.counter",
                ),
                "{attribute 'qualified_only'}",
                "VAR_GLOBAL",
                f"{IND}{member} : ARRAY[0..{used[-1]}] OF {type_name};  // используются: {listed}",
                "END_VAR",
            ]
            self.objects.append(L.StObject(L.KIND_GVL, self.g(gvl), "\n".join(lines), folder=list(self.o.folder)))
            self.hit(f"gvl.s5_{'timers' if kind == 'T' else 'counters'}")

    def io_gvls(self) -> None:
        groups: dict[str, list[S.IoVar]] = {S.GVL_IO: [], S.GVL_MARKERS: []}
        for var in self.p.io_vars.values():
            groups.setdefault(var.gvl, []).append(var)
        for gvl, items in groups.items():
            if not items:
                continue
            items.sort(key=lambda v: (v.address.area, v.address.byte, v.address.bit or 0, v.address.size))
            area = "входов/выходов" if gvl == S.GVL_IO else "меркеров (%M)"
            lines = [
                *self._project_header(
                    f"символьный слой {area} S7: прямые адреса и теги с адресом → переменные с AT",
                    "docs/MAPPING.md, раздел «Адреса»",
                ),
                "// Адресная модель: S7 нумерует байты (%IW64 — байты 64–65, big-endian), CODESYS — слова",
                "// (%IW32 — байты 64–65, little-endian). Адреса ниже — заготовка: на ПЛК210 каналы модулей",
                "// привязываются в дереве устройств (I/O mapping) — сверить с конфигурацией.",
                "{attribute 'qualified_only'}",
                "VAR_GLOBAL",
            ]
            for var in items:
                notes: list[Note] = []
                tag = self._tag_for_address(var)
                type_text = var.type_name or var.address.default_type
                if tag is not None:
                    try:
                        type_text = self._map_tag_type(tag)
                    except Unsupported as u:
                        notes.append(Note(TODO, u.rule, f"тег {tag.name}: {u.reason}", 0, var.st_name))
                at = var.address.codesys_at()
                overlaps = [
                    o.address.s7_text for o in items if o is not var and _byte_order_overlap(o.address, var.address)
                ]
                if at is None:
                    notes.append(
                        Note(
                            CHECK,
                            "addr.unaligned",
                            f"S7 {var.address.s7_text}: адрес не выражается в CODESYS (не выровнен) — "
                            "переменная без AT",
                            0,
                            var.st_name,
                        )
                    )
                if overlaps:
                    notes.append(
                        Note(
                            CHECK,
                            "addr.overlap",
                            f"S7 {var.address.s7_text} перекрывается с {', '.join(sorted(overlaps))}: порядок байтов "
                            "S7 (big-endian) и CODESYS (little-endian) различается",
                            0,
                            var.st_name,
                        )
                    )
                comment = f"S7 {var.address.s7_text}" + (f"; {tag.comment}" if tag is not None and tag.comment else "")
                lines.extend(self.note_lines(notes, IND))
                at_text = f" AT {at}" if at else ""
                lines.append(f"{IND}{var.st_name}{at_text} : {type_text}; // {comment}")
                self._project_item(f"{self.g(gvl)}.{var.st_name}", notes)
                self.hit("addr.io_var")
            lines.append("END_VAR")
            self.objects.append(L.StObject(L.KIND_GVL, self.g(gvl), "\n".join(lines), folder=list(self.o.folder)))

    def _tag_for_address(self, var: S.IoVar) -> S.TagSym | None:
        for tag in self.p.tags.values():
            if tag.address is not None and tag.address.s7_text == var.address.s7_text:
                return tag
        return None

    def _map_tag_type(self, tag: S.TagSym) -> str:
        try:
            parsed = Parser(tag.type_name).type_ref()
        except ParseError as exc:
            raise Unsupported(f"тип «{tag.type_name}» не разобран", "tag.type") from exc
        if isinstance(parsed, StringType):
            base = "WSTRING" if parsed.wide else "STRING"
            if isinstance(parsed.length, Literal):
                return f"{base}({parsed.length.text})"
            return f"{base}(254)"
        if isinstance(parsed, NamedType):
            upper = parsed.name.upper()
            if upper in M.ELEMENTARY:
                return M.ELEMENTARY[upper]
            if upper in M.CHECKED_TYPES:
                return M.CHECKED_TYPES[upper][0]
            sym = self.p.block(parsed.name)
            if sym is not None and sym.kind == BLOCK_UDT:
                return sym.st_name
        raise Unsupported(f"тип тега «{tag.type_name}» не поддерживается", "tag.type")

    def tags_gvl(self) -> None:
        entries: list[str] = []
        for tag in sorted(self.p.tags.values(), key=lambda t: t.st_name.lower()):
            if tag.address is not None or tag.gvl != S.GVL_TAGS or not tag.used:
                continue
            notes: list[Note] = []
            try:
                type_text = self._map_tag_type(tag)
            except Unsupported as u:
                notes.append(Note(TODO, u.rule, u.reason, 0, tag.name))
                type_text = "BOOL"
            entries.extend(self.note_lines(notes, IND))
            comment = f" // {tag.comment}" if tag.comment else ""
            entries.append(f"{IND}{tag.st_name} : {type_text};{comment}")
            self._project_item(f"{self.g(S.GVL_TAGS)}.{tag.st_name}", notes)
        for key in sorted(self.p.unknown):
            unk = self.p.unknown[key]
            concrete = [t for t in unk.types if t not in ("ANY_NUM",) and not t.startswith("ARRAY")]
            if concrete:
                type_text = Counter(concrete).most_common(1)[0][0]
                note = Note(
                    CHECK,
                    "sym.unknown_decl",
                    f'символ "{unk.name}" не найден — тип {type_text} выведен по использованию ({unk.lines[0]})',
                    0,
                    unk.name,
                )
            elif unk.types:
                type_text = "INT"
                note = Note(
                    CHECK,
                    "sym.unknown_decl",
                    f'символ "{unk.name}" не найден — принят INT (числовой контекст)',
                    0,
                    unk.name,
                )
            else:
                type_text = "BOOL"
                note = Note(
                    TODO,
                    "sym.unknown_decl",
                    f'символ "{unk.name}" не найден и тип не выведен — принят BOOL ({unk.lines[0]})',
                    0,
                    unk.name,
                )
            entries.extend(self.note_lines([note], IND))
            entries.append(f"{IND}{unk.st_name} : {type_text};")
            self._project_item(f"{self.g(S.GVL_TAGS)}.{unk.st_name}", [note])
        if not entries:
            return
        lines = [
            *self._project_header(
                "глобальные теги S7 без адреса и символы, не найденные в корпусе", "docs/MAPPING.md, раздел «Теги»"
            ),
            "{attribute 'qualified_only'}",
            "VAR_GLOBAL",
            *entries,
            "END_VAR",
        ]
        self.objects.append(L.StObject(L.KIND_GVL, self.g(S.GVL_TAGS), "\n".join(lines), folder=list(self.o.folder)))

    def const_gvl(self) -> None:
        consts = [t for t in self.p.tags.values() if t.gvl == S.GVL_USER_CONST]
        if not consts:
            return
        entries: list[str] = []
        for tag in sorted(consts, key=lambda t: t.st_name.lower()):
            notes: list[Note] = []
            try:
                type_text = self._map_tag_type(tag)
                value = tag.value
                lit = parse_expression(value)
                if isinstance(lit, Literal):
                    value = M.map_literal(lit.kind, lit.text).text
            except (Unsupported, ParseError) as exc:
                notes.append(Note(TODO, "tag.const", f"константа {tag.name}: {exc}", 0, tag.name))
                type_text, value = "INT", "0"
            comment = f" // {tag.comment}" if tag.comment else ""
            entries.extend(self.note_lines(notes, IND))
            entries.append(f"{IND}{tag.st_name} : {type_text} := {value};{comment}")
            self._project_item(f"{self.g(S.GVL_USER_CONST)}.{tag.st_name}", notes)
        lines = [
            *self._project_header("константы пользователя S7 (User constants)", "docs/MAPPING.md, раздел «Теги»"),
            "{attribute 'qualified_only'}",
            "VAR_GLOBAL CONSTANT",
            *entries,
            "END_VAR",
        ]
        self.objects.append(
            L.StObject(L.KIND_GVL, self.g(S.GVL_USER_CONST), "\n".join(lines), folder=list(self.o.folder))
        )


def _byte_order_overlap(a: S.S7Address, b: S.S7Address) -> bool:
    """Перекрытие адресов, при котором важен порядок байтов: хотя бы один — слово или двойное слово."""
    if a.area != b.area or (a.size in ("X", "B") and b.size in ("X", "B")):
        return False
    a_lo, a_hi = a.byte_range()
    b_lo, b_hi = b.byte_range()
    return not (a_hi < b_lo or b_hi < a_lo)


def _stmt_label(s: Stmt) -> str:
    if isinstance(s, Assign):
        return "присваивание"
    if isinstance(s, CallStmt):
        callee = s.call.callee
        name = getattr(callee, "name", "")
        return f"вызов {name}".strip()
    if isinstance(s, RawStmt):
        return "не разобрано"
    return {
        If: "IF",
        Case: "CASE",
        For: "FOR",
        While: "WHILE",
        Repeat: "REPEAT",
        Exit: "EXIT",
        Continue: "CONTINUE",
        Return: "RETURN",
        Region: "REGION",
        Goto: "GOTO",
        Label: "метка",
        Pragma: "прагма",
    }.get(type(s), type(s).__name__)


def convert(
    files: list[SourceFile],
    project: S.Project | None = None,
    options: Options | None = None,
    display: dict[str, str] | None = None,
) -> ConversionResult:
    """Сконвертировать разобранные файлы (общая таблица символов — по всем файлам)."""
    return Emitter(project or S.Project(), options).run(files, display)
