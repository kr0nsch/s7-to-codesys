"""Общая часть эталонных моделей сценариев поведения (scenarios/reference/).

Модели ``model_*.py`` написаны по нормативному описанию логики в заголовках
``samples/scl/<Блок>.scl`` — не по тексту SCL и не по результату конвертера.
Здесь: моделируемые часы, таймеры IEC (TON, TOF), детекторы фронтов (R_TRIG,
F_TRIG), NORM_X/SCALE_X, описание сценариев и запись CSV в формате
``scenarios/README.md``.

Время моделируется: перед вызовом блока для строки сценария часы ставятся на
``t_ms`` строки; между строками блок не вызывается. Таймеры и сравнения времени
записывают запас до порога (``Clock.deltas``) — по нему проверяется, что строки
без пометки ``boundary`` отстоят от любого порога не меньше чем на
``REALTIME_MARGIN_MS`` (тогда сценарий проходит и в реальном времени).
"""

from __future__ import annotations

import csv
import io
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Protocol

Value = bool | int | float | str

# Типы ячеек CSV (типы CODESYS после конвертации; см. scenarios/README.md)
INT_TYPES = ("SINT", "INT", "DINT", "LINT", "USINT", "UINT", "UDINT", "ULINT")
BIT_TYPES = {"BYTE": 2, "WORD": 4, "DWORD": 8, "LWORD": 16}
REAL_TYPES = ("REAL", "LREAL")
ALL_TYPES = ("BOOL", *INT_TYPES, *BIT_TYPES, *REAL_TYPES, "TIME", "STRING")

# Запас до порога времени для строк без пометки boundary, мс
REALTIME_MARGIN_MS = 200

# Шаг t_ms для блоков, которые от времени не зависят, мс
UNTIMED_STEP_MS = 100

IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PATH_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*|\[-?[0-9]+\])*$")


class ScenarioError(Exception):
    """Ошибка в описании сценария (не в модели блока)."""


class Clock:
    """Моделируемые часы сценария, мс от начала сценария."""

    def __init__(self) -> None:
        self.now_ms = 0
        self.deltas: list[int] = []

    def compare(self, elapsed_ms: int, limit_ms: int) -> bool:
        """Сравнение ``elapsed >= limit`` с записью запаса до порога."""
        self.deltas.append(elapsed_ms - limit_ms)
        return elapsed_ms >= limit_ms


class Ton:
    """TON (задержка включения): Q = IN и прошло не меньше PT с вызова, где IN стал TRUE."""

    def __init__(self) -> None:
        self.q = False
        self.et = 0
        self._prev_in = False
        self._start_ms = 0

    def __call__(self, clock: Clock, in_: bool, pt_ms: int) -> None:
        if in_:
            if not self._prev_in:
                self._start_ms = clock.now_ms
            elapsed = clock.now_ms - self._start_ms
            self.q = clock.compare(elapsed, pt_ms)
            self.et = min(elapsed, pt_ms)
        else:
            self.q = False
            self.et = 0
        self._prev_in = in_


class Tof:
    """TOF (задержка выключения): Q = TRUE при IN; после спада IN — ещё PT, затем FALSE."""

    def __init__(self) -> None:
        self.q = False
        self.et = 0
        self._prev_in = False
        self._running = False
        self._start_ms = 0

    def __call__(self, clock: Clock, in_: bool, pt_ms: int) -> None:
        if in_:
            self.q = True
            self.et = 0
            self._running = False
        else:
            if self._prev_in:
                self._start_ms = clock.now_ms
                self._running = True
            if self._running:
                elapsed = clock.now_ms - self._start_ms
                if clock.compare(elapsed, pt_ms):
                    self.q = False
                    self.et = pt_ms
                    self._running = False
                else:
                    self.et = elapsed
        self._prev_in = in_


class RTrig:
    """R_TRIG: Q = CLK AND NOT M; M := CLK; M в начале FALSE."""

    def __init__(self) -> None:
        self.q = False
        self._m = False

    def __call__(self, clk: bool) -> None:
        self.q = clk and not self._m
        self._m = clk


class FTrig:
    """F_TRIG по семантике S7: Q = NOT CLK AND M; M := CLK; M в начале FALSE.

    На первом вызове экземпляра спада нет, даже если CLK = FALSE.
    """

    def __init__(self) -> None:
        self.q = False
        self._m = False

    def __call__(self, clk: bool) -> None:
        self.q = (not clk) and self._m
        self._m = clk


def norm_x(mn: float, value: float, mx: float) -> float:
    """NORM_X: (VALUE - MIN) / (MAX - MIN), без ограничения."""
    return (value - mn) / (mx - mn)


def scale_x(mn: float, value: float, mx: float) -> float:
    """SCALE_X: VALUE * (MAX - MIN) + MIN, без ограничения."""
    return value * (mx - mn) + mn


def limit(mn: int, value: int, mx: int) -> int:
    return max(mn, min(value, mx))


class Model(Protocol):
    """Модель экземпляра ФБ: один вызов ``step`` — один вызов блока."""

    def step(self, clock: Clock, inputs: Mapping[str, Value]) -> Mapping[str, Value]: ...


@dataclass(frozen=True)
class Port:
    """Вход или выход блока: путь от экземпляра, тип ячейки, допуск (для REAL/LREAL выходов)."""

    path: str
    type: str
    tol: float | None = None


@dataclass(frozen=True)
class Row:
    """Строка сценария: момент вызова, изменённые входы (остальные — как в прошлой строке)."""

    t_ms: int
    changes: Mapping[str, Value]
    comment: str
    boundary: bool = False


@dataclass(frozen=True)
class Scenario:
    name: str
    title: str
    rows: Sequence[Row]


@dataclass(frozen=True)
class BlockScenarios:
    """Сценарии одного блока корпуса."""

    block: str
    source: str
    description: str
    inputs: Sequence[Port]
    outputs: Sequence[Port]
    defaults: Mapping[str, Value]
    factory: Callable[[], Model]
    scenarios: Sequence[Scenario]
    period_input: str | None = None  # вход TIME, равный разнице t_ms соседних строк
    timed: bool = True  # блок зависит от времени (таймеры)
    notes: Sequence[str] = field(default_factory=tuple)


def untimed_rows(items: Sequence[tuple[Mapping[str, Value], str]]) -> list[Row]:
    """Строки для блока без таймеров: t_ms = 0, 100, 200, ..."""
    return [Row(UNTIMED_STEP_MS * k, changes, comment) for k, (changes, comment) in enumerate(items)]


def format_cell(value: Value, type_name: str) -> str:
    """Значение -> текст ячейки CSV (scenarios/README.md, раздел «Значения»)."""
    if type_name == "BOOL":
        if not isinstance(value, bool):
            raise ScenarioError(f"BOOL ожидает bool, получено {value!r}")
        return "TRUE" if value else "FALSE"
    if type_name in INT_TYPES:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ScenarioError(f"{type_name} ожидает int, получено {value!r}")
        return str(value)
    if type_name in BIT_TYPES:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ScenarioError(f"{type_name} ожидает int >= 0, получено {value!r}")
        return "16#" + format(value, f"0{BIT_TYPES[type_name]}X")
    if type_name in REAL_TYPES:
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise ScenarioError(f"{type_name} ожидает число, получено {value!r}")
        return format_real(float(value))
    if type_name == "TIME":
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ScenarioError(f"TIME ожидает целое число мс >= 0, получено {value!r}")
        return f"T#{value}MS"
    if type_name == "STRING":
        if not isinstance(value, str) or not value.isascii() or "'" in value or "$" in value:
            raise ScenarioError(f"STRING ожидает ASCII без ' и $, получено {value!r}")
        return value
    raise ScenarioError(f"неизвестный тип {type_name}")


def format_real(value: float) -> str:
    """Десятичная запись без экспоненты, не больше 9 знаков после точки, минимум один."""
    text = f"{value:.9f}".rstrip("0")
    if text.endswith("."):
        text += "0"
    if text == "-0.0":
        text = "0.0"
    return text


def header(block: BlockScenarios) -> list[str]:
    cols = ["scenario", "cycle", "t_ms"]
    cols += [f"in.{p.path}:{p.type}" for p in block.inputs]
    for p in block.outputs:
        cols.append(f"out.{p.path}:{p.type}")
        if p.type in REAL_TYPES:
            cols.append(f"tol.{p.path}")
    cols += ["boundary", "comment"]
    return cols


def _check_block(block: BlockScenarios) -> None:
    names = [p.path for p in (*block.inputs, *block.outputs)]
    if len({n.lower() for n in names}) != len(names):
        raise ScenarioError(f"{block.block}: имена входов и выходов повторяются")
    for p in (*block.inputs, *block.outputs):
        if not PATH_RE.match(p.path) or p.type not in ALL_TYPES:
            raise ScenarioError(f"{block.block}: неверный порт {p}")
    for p in block.outputs:
        if (p.type in REAL_TYPES) != (p.tol is not None):
            raise ScenarioError(f"{block.block}: допуск нужен ровно у REAL/LREAL выходов ({p.path})")
    missing = [p.path for p in block.inputs if p.path not in block.defaults]
    if missing:
        raise ScenarioError(f"{block.block}: нет значений по умолчанию для {missing}")
    seen: set[str] = set()
    for sc in block.scenarios:
        if not IDENT_RE.match(sc.name) or sc.name.lower() in seen:
            raise ScenarioError(f"{block.block}: имя сценария {sc.name!r} не идентификатор или повторяется")
        seen.add(sc.name.lower())
        if not sc.rows or sc.rows[0].t_ms != 0:
            raise ScenarioError(f"{block.block}.{sc.name}: первая строка должна иметь t_ms = 0")


def run_block(block: BlockScenarios) -> list[list[str]]:
    """Прогон модели по всем сценариям блока; строки CSV без заголовка."""
    _check_block(block)
    in_names = {p.path for p in block.inputs}
    table: list[list[str]] = []
    for sc in block.scenarios:
        model = block.factory()
        clock = Clock()
        state: dict[str, Value] = dict(block.defaults)
        prev_t = 0
        for cycle, row in enumerate(sc.rows, start=1):
            where = f"{block.block}.{sc.name}, строка {cycle}"
            unknown = set(row.changes) - in_names
            if unknown:
                raise ScenarioError(f"{where}: неизвестные входы {sorted(unknown)}")
            if row.t_ms < prev_t:
                raise ScenarioError(f"{where}: t_ms убывает")
            state.update(row.changes)
            if block.period_input is not None and cycle > 1:
                period = state[block.period_input]
                if row.t_ms - prev_t != period:
                    raise ScenarioError(f"{where}: t_ms должен расти на {block.period_input} = {period!r}")
            prev_t = row.t_ms
            clock.now_ms = row.t_ms
            clock.deltas = []
            outputs = model.step(clock, state)
            _check_margins(where, row, clock.deltas)
            cells = [sc.name, str(cycle), str(row.t_ms)]
            cells += [format_cell(state[p.path], p.type) for p in block.inputs]
            for p in block.outputs:
                cells.append(format_cell(outputs[p.path], p.type))
                if p.tol is not None:
                    cells.append(format_real(p.tol))
            cells += ["TRUE" if row.boundary else "FALSE", row.comment]
            table.append(cells)
    return table


def _check_margins(where: str, row: Row, deltas: Sequence[int]) -> None:
    close = [d for d in deltas if abs(d) < REALTIME_MARGIN_MS]
    if row.boundary:
        if 0 not in deltas:
            raise ScenarioError(f"{where}: boundary = TRUE, но ни одно время не равно порогу")
    elif close:
        raise ScenarioError(
            f"{where}: до порога времени меньше {REALTIME_MARGIN_MS} мс ({close}); "
            "сдвиньте строку или пометьте boundary"
        )


def to_csv(block: BlockScenarios) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(header(block))
    writer.writerows(run_block(block))
    return buf.getvalue()


# --- Чтение CSV: исполняемая версия формата из scenarios/README.md ---------------------------

COLUMN_RE = re.compile(r"^(?P<kind>in|out)\.(?P<path>[^:]+):(?P<type>[A-Z]+)$")
TOL_RE = re.compile(r"^tol\.(?P<path>.+)$")
INT_CELL_RE = re.compile(r"^-?[0-9]+$")
HEX_CELL_RE = re.compile(r"^16#[0-9A-F]+$")
REAL_CELL_RE = re.compile(r"^-?[0-9]+\.[0-9]+$")
TIME_CELL_RE = re.compile(r"^T#([0-9]+)MS$")
META_HEAD = ("scenario", "cycle", "t_ms")
META_TAIL = ("boundary", "comment")


@dataclass(frozen=True)
class Column:
    """Столбец данных: kind — in, out или tol; type — тип ячейки (у tol — REAL допуска)."""

    kind: str
    path: str
    type: str


@dataclass(frozen=True)
class ParsedRow:
    scenario: str
    cycle: int
    t_ms: int
    inputs: Mapping[str, Value]  # пустая ячейка входа — ключа нет (вход не присваивается)
    outputs: Mapping[str, Value]  # пустая ячейка выхода — ключа нет (не проверяется)
    tolerances: Mapping[str, float]
    boundary: bool
    comment: str


def parse_header(cols: Sequence[str]) -> list[Column]:
    """Проверка заголовка; столбцы данных между t_ms и boundary."""
    if tuple(cols[:3]) != META_HEAD or tuple(cols[-2:]) != META_TAIL:
        raise ScenarioError("заголовок: первые столбцы scenario,cycle,t_ms, последние boundary,comment")
    result: list[Column] = []
    for name in cols[3:-2]:
        m = COLUMN_RE.match(name)
        if m:
            path, type_name = m.group("path"), m.group("type")
            if not PATH_RE.match(path) or type_name not in ALL_TYPES:
                raise ScenarioError(f"заголовок: неверный столбец {name!r}")
            result.append(Column(m.group("kind"), path, type_name))
            continue
        t = TOL_RE.match(name)
        if not t:
            raise ScenarioError(f"заголовок: неизвестный столбец {name!r}")
        prev = result[-1] if result else None
        if prev is None or prev.kind != "out" or prev.path != t.group("path") or prev.type not in REAL_TYPES:
            raise ScenarioError(f"заголовок: {name!r} должен идти сразу за out.{t.group('path')}:REAL|LREAL")
        result.append(Column("tol", t.group("path"), "REAL"))
    paths = [(c.kind, c.path.lower()) for c in result if c.kind != "tol"]
    if len(set(paths)) != len(paths):
        raise ScenarioError("заголовок: столбцы повторяются")
    for i, c in enumerate(result):
        if c.kind == "out" and c.type in REAL_TYPES:
            nxt = result[i + 1] if i + 1 < len(result) else None
            if nxt is None or nxt.kind != "tol" or nxt.path != c.path:
                raise ScenarioError(f"заголовок: нет tol.{c.path} для out.{c.path}:{c.type}")
    return result


def parse_value(text: str, type_name: str) -> Value:
    """Текст ячейки -> значение Python (bool, int, float, str); TIME — int мс."""
    if type_name == "BOOL":
        if text not in ("TRUE", "FALSE"):
            raise ScenarioError(f"BOOL: {text!r}")
        return text == "TRUE"
    if type_name in INT_TYPES:
        if not INT_CELL_RE.match(text):
            raise ScenarioError(f"{type_name}: {text!r}")
        return int(text)
    if type_name in BIT_TYPES:
        if not HEX_CELL_RE.match(text) or len(text) - 3 != BIT_TYPES[type_name]:
            raise ScenarioError(f"{type_name}: {text!r}")
        return int(text[3:], 16)
    if type_name in REAL_TYPES:
        if not REAL_CELL_RE.match(text):
            raise ScenarioError(f"{type_name}: {text!r}")
        return float(text)
    if type_name == "TIME":
        m = TIME_CELL_RE.match(text)
        if not m:
            raise ScenarioError(f"TIME: {text!r}")
        return int(m.group(1))
    if type_name == "STRING":
        if not text.isascii() or "'" in text or "$" in text:
            raise ScenarioError(f"STRING: {text!r}")
        return text
    raise ScenarioError(f"неизвестный тип {type_name}")


def read_csv(text: str) -> tuple[list[Column], list[ParsedRow]]:
    """Разбор и проверка файла сценариев (правила scenarios/README.md)."""
    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        raise ScenarioError("пустой файл")
    columns = parse_header(rows[0])
    width = len(rows[0])
    parsed: list[ParsedRow] = []
    seen: set[str] = set()
    for n, cells in enumerate(rows[1:], start=2):
        where = f"строка файла {n}"
        if len(cells) != width:
            raise ScenarioError(f"{where}: {len(cells)} ячеек вместо {width}")
        name = cells[0]
        if not IDENT_RE.match(name):
            raise ScenarioError(f"{where}: имя сценария {name!r}")
        cycle, t_ms = int(cells[1]), int(cells[2])
        prev = parsed[-1] if parsed else None
        if prev is None or prev.scenario != name:
            if name in seen:
                raise ScenarioError(f"{where}: строки сценария {name} не подряд")
            seen.add(name)
            if cycle != 1 or t_ms != 0:
                raise ScenarioError(f"{where}: сценарий начинается с cycle = 1, t_ms = 0")
        elif cycle != prev.cycle + 1 or t_ms < prev.t_ms:
            raise ScenarioError(f"{where}: cycle должен расти на 1, t_ms — не убывать")
        inputs: dict[str, Value] = {}
        outputs: dict[str, Value] = {}
        tolerances: dict[str, float] = {}
        for col, cell in zip(columns, cells[3:-2], strict=True):
            if cell == "":
                if col.kind == "tol" and col.path in outputs:
                    raise ScenarioError(f"{where}: пустой tol.{col.path} при заданном выходе")
                continue
            value = parse_value(cell, col.type)
            if col.kind == "in":
                inputs[col.path] = value
            elif col.kind == "out":
                outputs[col.path] = value
            else:
                if not isinstance(value, float) or value < 0.0:
                    raise ScenarioError(f"{where}: допуск {cell!r}")
                tolerances[col.path] = value
        if cycle == 1:
            missing = [c.path for c in columns if c.kind == "in" and c.path not in inputs]
            if missing:
                raise ScenarioError(f"{where}: в первой строке сценария заданы не все входы: {missing}")
        boundary = parse_value(cells[-2], "BOOL") is True
        parsed.append(ParsedRow(name, cycle, t_ms, inputs, outputs, tolerances, boundary, cells[-1]))
    return columns, parsed
