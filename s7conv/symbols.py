"""Таблица символов проекта: блоки корпуса, DB, теги (таблица тегов CSV), прямые адреса.

Адресная модель (docs/MAPPING.md, раздел «Адреса»):
- S7 адресует память байтами: %MW10 — слово из байтов 10 и 11, %MD10 — байты 10…13;
  порядок байтов — big-endian (старший байт по младшему адресу).
- CODESYS адресует словами и двойными словами по их номеру: %MW5 — байты 10 и 11, %MD2 — байты 8…11;
  на x86/ARM порядок байтов little-endian.
- Поэтому S7 %IW64 → CODESYS %IW32, S7 %MD12 → %MD3; адрес слова с нечётным байтом (%MW11) или
  двойного слова не кратный 4 в CODESYS не выражается — переменная создаётся без AT.
- Биты совпадают: S7 %I0.0 → %IX0.0, %M10.1 → %MX10.1; байты: %IB3 → %IB3.
"""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass, field

from s7conv import mapping as M
from s7conv.nodes import BLOCK_DB, BLOCK_FB, BLOCK_FC, BLOCK_OB, BLOCK_UDT, Block, NamedType, SourceFile

GVL_IO = "GVL_IO"
GVL_MARKERS = "GVL_Markers"
GVL_TAGS = "GVL_Tags"
GVL_USER_CONST = "GVL_UserConstants"
GVL_INSTANCES = "GVL_InstanceDBs"
# Глобальные объекты, которые генерирует конвертер (к ним применяется Options.global_suffix)
GVL_S5TIMERS = "GVL_S5Timers"  # таймеры S5 из STL: массив aTimer[0..n] OF ST_S5Timer
GVL_S5COUNTERS = "GVL_S5Counters"  # счётчики S5 из STL: массив aCounter[0..n] OF ST_S5Counter
GENERATED_GVLS = frozenset({GVL_IO, GVL_MARKERS, GVL_TAGS, GVL_USER_CONST, GVL_INSTANCES, GVL_S5TIMERS, GVL_S5COUNTERS})
TAG_S5 = "S5"  # тег таймера/счётчика S5 (%T5, %C3): не переносится

_S5_ADDR_RE = re.compile(r"%?[TCZ]\d+\Z", re.I)

_ADDR_RE = re.compile(r"%(?P<area>[IQMEA])(?P<size>[XBWD]?)(?P<byte>\d+)(?:\.(?P<bit>\d+))?(?P<per>:P)?\Z", re.I)
_SIZE_TYPE = {"X": "BOOL", "B": "BYTE", "W": "WORD", "D": "DWORD"}
_SIZE_BYTES = {"X": 1, "B": 1, "W": 2, "D": 4}


@dataclass(frozen=True)
class S7Address:
    area: str  # I, Q, M
    size: str  # X, B, W, D
    byte: int
    bit: int | None
    peripheral: bool = False

    @property
    def s7_text(self) -> str:
        if self.size == "X":
            return f"%{self.area}{self.byte}.{self.bit}"
        return f"%{self.area}{self.size}{self.byte}"

    @property
    def default_type(self) -> str:
        return _SIZE_TYPE[self.size]

    def codesys_at(self) -> str | None:
        """Адрес CODESYS для AT или None, если адрес не выровнен (см. модуль)."""
        if self.size == "X":
            return f"%{self.area}X{self.byte}.{self.bit}"
        if self.size == "B":
            return f"%{self.area}B{self.byte}"
        width = _SIZE_BYTES[self.size]
        if self.byte % width:
            return None
        return f"%{self.area}{self.size}{self.byte // width}"

    def generated_name(self) -> str:
        if self.size == "X":
            return f"{self.area}{self.byte}_{self.bit}"
        return f"{self.area}{self.size}{self.byte}"

    def byte_range(self) -> tuple[int, int]:
        return self.byte, self.byte + _SIZE_BYTES[self.size] - 1


def parse_address(text: str) -> S7Address | None:
    """%I0.0, %IW64, %MD10, %Q4.1, %I0.0:P; немецкая мнемоника E/A → I/Q. None — не адрес I/Q/M."""
    match = _ADDR_RE.match(text.strip())
    if not match:
        return None
    area = match.group("area").upper()
    area = {"E": "I", "A": "Q"}.get(area, area)
    size = match.group("size").upper()
    bit = match.group("bit")
    if size in ("", "X"):
        if bit is None:
            return None
        size = "X"
        if int(bit) > 7:
            return None
    elif bit is not None:
        return None
    return S7Address(
        area, size, int(match.group("byte")), int(bit) if bit is not None else None, bool(match.group("per"))
    )


# ---------------------------------------------------------------------------
# Таблица тегов
# ---------------------------------------------------------------------------


@dataclass
class TagSym:
    """Тег S7 из таблицы тегов: "Start_PB" с адресом %I0.0 или константа пользователя."""

    name: str
    st_name: str
    type_name: str  # тип SCL (Bool, Int, ...)
    address: S7Address | None = None
    raw_address: str = ""
    comment: str = ""
    value: str = ""  # для констант
    gvl: str = GVL_TAGS
    source: str = ""  # откуда (файл:строка)
    used: bool = False


_NAME_COLS = ("name", "имя")
_TYPE_COLS = ("data type", "datatype", "type", "тип данных", "тип")
_ADDR_COLS = ("logical address", "address", "адрес", "логический адрес")
_COMMENT_COLS = ("comment", "комментарий")
_VALUE_COLS = ("value", "значение")


def _col(header: list[str], names: tuple[str, ...]) -> int | None:
    lowered = [h.strip().lower() for h in header]
    for name in names:
        if name in lowered:
            return lowered.index(name)
    return None


def load_tag_table(text: str, source: str = "") -> tuple[list[TagSym], list[str]]:
    """CSV с заголовком (Name; Data Type; Logical Address; Comment; [Value]) — разделитель ',', ';' или TAB.

    Формат повторяет столбцы экспорта таблицы тегов TIA Portal (PLC tags). Возвращает теги и ошибки.
    """
    errors: list[str] = []
    sample = text[:2048]
    try:
        dialect: type[csv.Dialect] | csv.Dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    rows = list(csv.reader(io.StringIO(text), dialect))
    if not rows:
        return [], [f"{source}: пустая таблица тегов"]
    header = rows[0]
    i_name = _col(header, _NAME_COLS)
    i_type = _col(header, _TYPE_COLS)
    i_addr = _col(header, _ADDR_COLS)
    i_comment = _col(header, _COMMENT_COLS)
    i_value = _col(header, _VALUE_COLS)
    if i_name is None or i_type is None:
        return [], [f"{source}: нет столбцов Name и Data Type"]
    tags: list[TagSym] = []
    for number, row in enumerate(rows[1:], 2):
        if not row or not any(cell.strip() for cell in row):
            continue

        def cell(index: int | None, row: list[str] = row) -> str:
            return row[index].strip() if index is not None and index < len(row) else ""

        name = cell(i_name).strip('"')
        type_name = cell(i_type).strip('"')
        raw = cell(i_addr)
        value = cell(i_value)
        if not name:
            continue
        address = None
        s5 = bool(raw) and _S5_ADDR_RE.match(raw) is not None
        if raw and not s5:
            address = parse_address(raw if raw.startswith("%") else "%" + raw)
            if address is None:
                errors.append(f"{source}:{number}: адрес {raw!r} тега {name!r} не распознан")
        tag = TagSym(
            name=name,
            st_name=M.sanitize(name),
            type_name=type_name,
            address=address,
            raw_address=raw,
            comment=cell(i_comment),
            value=value,
            source=f"{source}:{number}",
        )
        if s5:
            tag.gvl = TAG_S5
        elif address is not None:
            tag.gvl = GVL_MARKERS if address.area == "M" else GVL_IO
        elif value:
            tag.gvl = GVL_USER_CONST
        tags.append(tag)
    return tags, errors


def looks_like_tag_table(text: str) -> bool:
    first = text.lstrip("﻿").split("\n", 1)[0].lower()
    return any(n in first for n in _NAME_COLS) and any(t in first for t in _TYPE_COLS)


# ---------------------------------------------------------------------------
# Блоки
# ---------------------------------------------------------------------------

DB_GLOBAL = "global"
DB_INSTANCE = "instance"  # экземпляр ФБ корпуса или инструкции (TON_TIME, IEC_TIMER)
DB_TYPED = "typed"  # DB с типом UDT или массив


@dataclass
class BlockSym:
    kind: str
    name: str
    st_name: str
    block: Block
    file: str
    db_role: str = ""
    db_type_name: str = ""  # исходное имя типа экземплярного/типизированного DB


@dataclass
class IoVar:
    """Переменная слоя ввода-вывода для прямого адреса или тега с адресом."""

    st_name: str
    gvl: str
    type_name: str  # тип CODESYS
    address: S7Address
    comment: str = ""
    lines: list[str] = field(default_factory=list)  # где использован (файл:строка)


@dataclass
class UnknownSym:
    """Глобальный символ без объявления в корпусе и таблице тегов."""

    name: str
    st_name: str
    types: list[str] = field(default_factory=list)  # выведенные типы CODESYS
    lines: list[str] = field(default_factory=list)


@dataclass
class Project:
    blocks: dict[str, BlockSym] = field(default_factory=dict)
    tags: dict[str, TagSym] = field(default_factory=dict)
    io_vars: dict[str, IoVar] = field(default_factory=dict)  # ключ — S7Address.s7_text
    unknown: dict[str, UnknownSym] = field(default_factory=dict)
    generic_types: dict[str, str] = field(default_factory=dict)  # DB/переменная IEC_TIMER -> TON ...
    errors: list[str] = field(default_factory=list)

    def block(self, name: str) -> BlockSym | None:
        return self.blocks.get(name.lower())

    def tag(self, name: str) -> TagSym | None:
        return self.tags.get(name.lower())

    def add_tags(self, tags: list[TagSym]) -> None:
        used: set[str] = {t.st_name.lower() for t in self.tags.values()}
        for tag in tags:
            key = tag.name.lower()
            if key in self.tags:
                self.errors.append(f"{tag.source}: тег {tag.name!r} объявлен повторно")
                continue
            base = tag.st_name
            n = 2
            while tag.st_name.lower() in used:
                tag.st_name = f"{base}_{n}"
                n += 1
            used.add(tag.st_name.lower())
            self.tags[key] = tag
            if tag.address is not None:
                self.io_vars[tag.address.s7_text] = IoVar(
                    st_name=tag.st_name,
                    gvl=tag.gvl,
                    type_name="",
                    address=tag.address,
                    comment=tag.comment,
                )

    def io_var(self, address: S7Address, where: str) -> IoVar:
        """Переменная для адреса: из таблицы тегов или сгенерированная (I0_0, IW64, MD20)."""
        key = address.s7_text
        var = self.io_vars.get(key)
        if var is None:
            var = IoVar(
                st_name=address.generated_name(),
                gvl=GVL_MARKERS if address.area == "M" else GVL_IO,
                type_name=address.default_type,
                address=address,
            )
            self.io_vars[key] = var
        var.lines.append(where)
        return var


def collect_blocks(project: Project, files: list[SourceFile]) -> None:
    """Блоки всех файлов: имена ST, роль DB (глобальный, экземплярный, типизированный)."""
    used: set[str] = set()
    for sf in files:
        for blk in sf.blocks:
            if not isinstance(blk, Block):
                continue
            key = blk.name.lower()
            if key in project.blocks:
                project.errors.append(f"{sf.path}:{blk.span.line}: блок {blk.name!r} объявлен повторно — пропущен")
                continue
            st_name = M.sanitize(blk.name)
            if blk.kind == BLOCK_OB:
                st_name = M.pou_prefixed(st_name, "PRG_")
            base = st_name
            n = 2
            while st_name.lower() in used:
                st_name = f"{base}_{n}"
                n += 1
            used.add(st_name.lower())
            sym = BlockSym(kind=blk.kind, name=blk.name, st_name=st_name, block=blk, file=sf.path)
            project.blocks[key] = sym
    for sym in project.blocks.values():
        blk = sym.block
        if blk.kind != BLOCK_DB:
            continue
        if blk.db_type is None:
            sym.db_role = DB_GLOBAL
            continue
        if isinstance(blk.db_type, NamedType):
            sym.db_type_name = blk.db_type.name
            target = project.block(blk.db_type.name)
            if target is not None and target.kind == BLOCK_FB:
                sym.db_role = DB_INSTANCE
            elif target is not None and target.kind == BLOCK_UDT:
                sym.db_role = DB_TYPED
            elif blk.db_type.name.upper() in M.FB_TYPES or blk.db_type.name.upper() in M.GENERIC_INSTANCE_TYPES:
                sym.db_role = DB_INSTANCE
            else:
                sym.db_role = DB_TYPED
        else:
            sym.db_role = DB_TYPED


KINDS_WITH_CODE = (BLOCK_FB, BLOCK_FC, BLOCK_OB)
__all__ = [
    "BLOCK_DB",
    "BLOCK_FB",
    "BLOCK_FC",
    "BLOCK_OB",
    "BLOCK_UDT",
    "DB_GLOBAL",
    "DB_INSTANCE",
    "DB_TYPED",
    "GENERATED_GVLS",
    "GVL_INSTANCES",
    "GVL_IO",
    "GVL_MARKERS",
    "GVL_S5COUNTERS",
    "GVL_S5TIMERS",
    "GVL_TAGS",
    "GVL_USER_CONST",
    "TAG_S5",
    "BlockSym",
    "IoVar",
    "Project",
    "S7Address",
    "TagSym",
    "UnknownSym",
    "collect_blocks",
    "load_tag_table",
    "looks_like_tag_table",
    "parse_address",
]
