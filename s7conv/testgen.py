"""Генератор наборов тестов coUnit (CfUnit) из сценариев поведения scenarios/*.csv.

Сценарий — входы блока по вызовам и ожидаемые выходы (формат — scenarios/README.md). Генератор строит
для **сконвертированного** блока набор `FB_<Блок>_ScenarioTest` (папка тестов `Scenarios`): один
метод-тест на сценарий, в методе — строки сценария по порядку. Ожидаемые значения берутся только из
CSV (их считают эталонные модели по описанию логики блоков), а не из результата конвертации.

Время. Таймеры сконвертированного кода (`--timers s7compat`) читают источник времени `F_S7Now()`:
тест включает `GVL_S7Clock.xSimulation` и перед каждым вызовом ставит часы `GVL_S7Clock.tSimNow` на
`t_ms` строки. Сценарий выполняется целиком в одном цикле ПЛК, проверяются все строки, в том числе
строки ровно на пороге таймера (`boundary = TRUE`). Обоснование выбора — docs/methodology.md.

Имена. Пути столбцов (`out.status.faultCode`) — имена интерфейса SCL; генератор переводит их в имена
ST по таблицам самого конвертера (ConversionResult.scopes/type_scopes): переименования (ключевые слова,
повторы) и поля структур — те же, что в сконвертированном коде. Направление (вход — VAR_INPUT, выход —
VAR_OUTPUT) и тип столбца сверяются с объявлением после конвертации: расхождение — ошибка генерации.

Выполнение. coUnit вызывает методы-тесты каждый цикл, пока набор не завершён. Экземпляры блоков — в
переменных набора (у ФБ с VAR RETAIN экземпляр не может быть временным), поэтому сценарий выполняется
один раз, по флагу `x<Сценарий>Done`; в следующих циклах метод только подтверждает TEST_FINISHED().

PRG_Tests (тоже генерируется) объявляет экземпляры всех наборов из tests/: сгенерированных и
рукописных (функциональные блоки `EXTENDS coUnit.FB_TestSuite`), и каждый цикл вызывает coUnit.RUN().
"""

from __future__ import annotations

import csv
import io
import re
import textwrap
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from s7conv import __version__
from s7conv import mapping as M
from s7conv.emitter import ConversionResult, LocalVar, wrap_line
from s7conv.layout import L
from s7conv.nodes import BLOCK_FB

AUTO_GENERATED = "AUTO-GENERATED — не редактировать"
SUITE_SUFFIX = "_ScenarioTest"
SCENARIO_FOLDER = "Scenarios"
PRG_TESTS = "PRG_Tests"
CLOCK = "GVL_S7Clock"
IND = "    "

_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
# Имя сценария становится именем метода набора: не ключевое слово ST и не метод базового coUnit.FB_TestSuite
# (имена методов — по описаниям библиотеки coUnit 1.2.0.0; плюс всё, что начинается с Assert)
_RESERVED_METHOD_NAMES = M.RESERVED_ST | {
    n.upper()
    for n in (
        "AddTest",
        "AddTestNameToInstancePath",
        "AreAllTestsFinished",
        "CalculateAndSetNumberOfAssertsForTest",
        "FindTestSuiteInstancePath",
        "GetAreTestResultsAvailable",
        "GetHasStartedRunning",
        "GetNumberOfFailedTests",
        "GetNumberOfSkippedTests",
        "GetNumberOfSuccessfulTests",
        "GetNumberOfTests",
        "GetTestByPosition",
        "GetTestOrder",
        "GetTestOrderNumber",
        "IsTestFinished",
        "SetHasStartedRunning",
        "SetTestFailed",
        "SetTestFinished",
        "SetTestOrder",
        "FB_init",
        "FB_exit",
        "FB_reinit",
    )
}
_PATH_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*|\[[0-9]+\])*\Z")
_SEGMENT_RE = re.compile(r"\.?([A-Za-z_][A-Za-z0-9_]*)|\[([0-9]+)\]")
_INT_TYPES = ("SINT", "INT", "DINT", "LINT", "USINT", "UINT", "UDINT", "ULINT")
_BIT_DIGITS = {"BYTE": 2, "WORD": 4, "DWORD": 8, "LWORD": 16}
TYPES = frozenset({"BOOL", *_INT_TYPES, *_BIT_DIGITS, "REAL", "LREAL", "TIME", "STRING"})
_INT_RE = re.compile(r"-?[0-9]+\Z")
_REAL_RE = re.compile(r"-?[0-9]+\.[0-9]{1,9}\Z")
_TIME_RE = re.compile(r"T#[0-9]+MS\Z")
_STRING_RE = re.compile(r"[\x20-\x7e]*\Z")


class ScenarioError(Exception):
    """Ошибка формата CSV или несоответствие столбца сконвертированному блоку (код выхода 2)."""


# ---------------------------------------------------------------------------
# Чтение CSV (правила scenarios/README.md)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Column:
    kind: str  # in | out | tol
    path: str  # путь SCL: status.faultCode, samples[3]
    type: str  # тип CODESYS из заголовка (для tol — тип выхода, к которому он относится)


@dataclass
class Row:
    scenario: str
    cycle: int
    t_ms: int
    inputs: dict[str, str] = field(default_factory=dict)  # путь -> текст ячейки
    outputs: dict[str, str] = field(default_factory=dict)
    tolerances: dict[str, str] = field(default_factory=dict)
    boundary: bool = False
    comment: str = ""


@dataclass
class ScenarioFile:
    path: str  # путь для сообщений и шапок (от корня репозитория)
    block: str  # имя блока SCL = имя файла
    columns: list[Column]
    rows: list[Row]

    def scenarios(self) -> list[tuple[str, list[Row]]]:
        """Сценарии в порядке файла: [(имя, строки)]."""
        out: list[tuple[str, list[Row]]] = []
        for row in self.rows:
            if not out or out[-1][0] != row.scenario:
                out.append((row.scenario, []))
            out[-1][1].append(row)
        return out

    def column(self, kind: str, path: str) -> Column:
        return next(c for c in self.columns if c.kind == kind and c.path == path)


def _parse_header(cells: list[str], where: str) -> list[Column]:
    if cells[:3] != ["scenario", "cycle", "t_ms"] or cells[-2:] != ["boundary", "comment"]:
        raise ScenarioError(f"{where}: заголовок должен начинаться с scenario,cycle,t_ms и кончаться boundary,comment")
    columns: list[Column] = []
    seen: set[tuple[str, str]] = set()
    for cell in cells[3:-2]:
        kind, _, rest = cell.partition(".")
        if kind == "tol":
            path, type_name = rest, ""
            prev = columns[-1] if columns else None
            if prev is None or prev.kind != "out" or prev.path != path or prev.type not in ("REAL", "LREAL"):
                raise ScenarioError(f"{where}: {cell} — допуск идёт сразу после out.{path}:REAL/LREAL")
            type_name = prev.type
        elif kind in ("in", "out"):
            path, _, type_name = rest.partition(":")
            if type_name not in TYPES:
                raise ScenarioError(f"{where}: {cell} — неизвестный тип {type_name!r}")
        else:
            raise ScenarioError(f"{where}: столбец {cell!r} — ожидалось in.*, out.* или tol.*")
        if not _PATH_RE.match(path):
            raise ScenarioError(f"{where}: {cell} — неверный путь {path!r}")
        if (kind, path) in seen:
            raise ScenarioError(f"{where}: {cell} — путь повторяется")
        seen.add((kind, path))
        columns.append(Column(kind, path, type_name))
    for i, col in enumerate(columns):
        if col.kind == "out" and col.type in ("REAL", "LREAL"):
            nxt = columns[i + 1] if i + 1 < len(columns) else None
            if nxt is None or nxt.kind != "tol" or nxt.path != col.path:
                raise ScenarioError(f"{where}: у out.{col.path}:{col.type} нет столбца tol.{col.path} сразу после")
    return columns


def check_value(cell: str, type_name: str) -> None:
    """Проверка записи значения по таблице «Значения» scenarios/README.md."""
    ok: bool
    if type_name == "BOOL":
        ok = cell in ("TRUE", "FALSE")
    elif type_name in _INT_TYPES:
        ok = bool(_INT_RE.match(cell)) and not (type_name.startswith("U") and cell.startswith("-"))
    elif type_name in _BIT_DIGITS:
        digits = _BIT_DIGITS[type_name]
        ok = re.fullmatch(f"16#[0-9A-F]{{{digits}}}", cell) is not None
    elif type_name in ("REAL", "LREAL"):
        ok = bool(_REAL_RE.match(cell))
    elif type_name == "TIME":
        ok = bool(_TIME_RE.match(cell))
    else:  # STRING
        ok = bool(_STRING_RE.match(cell)) and "'" not in cell and "$" not in cell
    if not ok:
        raise ScenarioError(f"значение {cell!r} не соответствует типу {type_name}")


def read_scenarios(text: str, path: str) -> ScenarioFile:
    """Разобрать и проверить файл сценариев; path — для сообщений, имя файла — имя блока."""
    block = Path(path).stem
    if not _IDENT_RE.match(block):
        raise ScenarioError(f"{path}: имя файла {block!r} — не имя блока")
    table = list(csv.reader(io.StringIO(text)))
    if not table:
        raise ScenarioError(f"{path}: пустой файл")
    columns = _parse_header(table[0], f"{path}:1")
    width = len(table[0])
    rows: list[Row] = []
    seen: set[str] = set()
    for n, cells in enumerate(table[1:], start=2):
        where = f"{path}:{n}"
        if len(cells) != width:
            raise ScenarioError(f"{where}: {len(cells)} ячеек вместо {width}")
        name = cells[0]
        if not _IDENT_RE.match(name):
            raise ScenarioError(f"{where}: имя сценария {name!r} — не идентификатор ST")
        if name.upper() in _RESERVED_METHOD_NAMES or name.upper().startswith("ASSERT"):
            raise ScenarioError(f"{where}: имя сценария {name!r} занято (ключевое слово ST или метод coUnit)")
        try:
            cycle, t_ms = int(cells[1]), int(cells[2])
        except ValueError as exc:
            raise ScenarioError(f"{where}: cycle и t_ms — целые") from exc
        prev = rows[-1] if rows else None
        if prev is None or prev.scenario != name:
            if name in seen:
                raise ScenarioError(f"{where}: строки сценария {name} идут не подряд")
            seen.add(name)
            if cycle != 1 or t_ms != 0:
                raise ScenarioError(f"{where}: сценарий начинается с cycle = 1 и t_ms = 0")
        elif cycle != prev.cycle + 1 or t_ms < prev.t_ms:
            raise ScenarioError(f"{where}: cycle растёт на 1 без пропусков, t_ms не убывает")
        boundary = cells[-2]
        if boundary not in ("TRUE", "FALSE"):
            raise ScenarioError(f"{where}: boundary — TRUE или FALSE")
        row = Row(name, cycle, t_ms, boundary=boundary == "TRUE", comment=cells[-1])
        for col, cell in zip(columns, cells[3:-2], strict=True):
            if cell == "":
                continue
            try:
                check_value(cell, "REAL" if col.kind == "tol" else col.type)
            except ScenarioError as exc:
                raise ScenarioError(f"{where}: {col.kind}.{col.path}: {exc}") from exc
            if col.kind == "in":
                row.inputs[col.path] = cell
            elif col.kind == "out":
                row.outputs[col.path] = cell
            else:
                if cell.startswith("-"):
                    raise ScenarioError(f"{where}: tol.{col.path} — допуск не меньше 0")
                row.tolerances[col.path] = cell
        for out_path in row.outputs:
            if row_type(columns, out_path) in ("REAL", "LREAL") and out_path not in row.tolerances:
                raise ScenarioError(f"{where}: задан out.{out_path}, но пуст tol.{out_path}")
        if cycle == 1:
            missing = [c.path for c in columns if c.kind == "in" and c.path not in row.inputs]
            if missing:
                raise ScenarioError(f"{where}: в первой строке сценария заданы не все входы: {missing}")
        rows.append(row)
    if not rows:
        raise ScenarioError(f"{path}: нет строк данных")
    return ScenarioFile(path=path, block=block, columns=columns, rows=rows)


def row_type(columns: Sequence[Column], out_path: str) -> str:
    return next(c.type for c in columns if c.kind == "out" and c.path == out_path)


# ---------------------------------------------------------------------------
# Имена ST по таблицам конвертера
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Target:
    st_path: str  # status.faultCode в именах ST
    st_type: str  # тип после конвертации: INT, STRING, ...


def segments(path: str) -> list[str | int]:
    return [m.group(1) if m.group(1) is not None else int(m.group(2)) for m in _SEGMENT_RE.finditer(path)]


def _base_type(name: str) -> str:
    return name.split("(")[0].upper()


def resolve(result: ConversionResult, block: str, col: Column) -> Target:
    """Путь столбца в именах ST сконвертированного блока; проверка направления и типа."""
    scope = result.scopes.get(block.lower())
    sym = result.project.block(block) if result.project is not None else None
    if scope is None or sym is None or sym.kind != BLOCK_FB:
        raise ScenarioError(f"блок {block} не найден среди функциональных блоков корпуса")
    parts: list[str] = []
    var: LocalVar | None = None
    ty_name: str | None = None
    elem_of: str | None = None
    current: dict[str, LocalVar] | None = scope
    for n, seg in enumerate(segments(col.path)):
        if isinstance(seg, int):
            if ty_name != "ARRAY":
                raise ScenarioError(f"{col.kind}.{col.path}: индекс у не-массива")
            parts[-1] += f"[{seg}]"
            ty_name, elem_of = elem_of, None
            current = result.type_scopes.get(ty_name.lower()) if ty_name else None
            continue
        if current is None or seg.lower() not in current:
            raise ScenarioError(f"{col.kind}.{col.path}: «{seg}» нет в интерфейсе {block} после конвертации")
        var = current[seg.lower()]
        if var.dropped:
            raise ScenarioError(f"{col.kind}.{col.path}: «{seg}» не перенесена конвертером ({var.dropped})")
        if n == 0:
            want = "VAR_INPUT" if col.kind == "in" else "VAR_OUTPUT"
            if var.section != want:
                raise ScenarioError(f"{col.kind}.{col.path}: «{seg}» объявлена в {var.section}, ожидалась {want}")
        parts.append(var.st_name)
        ty_name = var.ty.name if var.ty is not None else None
        elem_of = var.ty.elem.name if var.ty is not None and var.ty.elem is not None else None
        current = result.type_scopes.get(ty_name.lower()) if ty_name else None
    if ty_name is None:
        raise ScenarioError(f"{col.kind}.{col.path}: тип после конвертации не определён")
    if _base_type(ty_name) != col.type:
        raise ScenarioError(f"{col.kind}.{col.path}: в CSV тип {col.type}, после конвертации — {ty_name}")
    return Target(".".join(parts), _base_type(ty_name))


# ---------------------------------------------------------------------------
# Текст ST
# ---------------------------------------------------------------------------


def st_literal(cell: str, type_name: str) -> str:
    """Литерал ST для значения ячейки (таблица «Значения» scenarios/README.md)."""
    if type_name == "STRING":
        return f"'{cell}'"
    return cell


def assert_call(type_name: str, expected: str, actual: str, message: str, delta: str | None) -> str:
    args = [f"Expected := {expected}", f"Actual := {actual}"]
    if delta is not None:
        args.append(f"Delta := {delta}")
    args.append(f"Message := '{message}'")
    return f"AssertEquals_{type_name}({', '.join(args)});"


def _wrapped(ind: str, text: str) -> list[str]:
    return wrap_line(ind + text)


def suite_name(block_st: str) -> str:
    return f"{block_st}{SUITE_SUFFIX}"


def _short(name: str) -> str:
    return name[3:] if name.upper().startswith("FB_") else name


@dataclass
class SuiteBuild:
    obj: L.StObject
    asserts: int
    rows: int
    tests: int


def generate_suite(sf: ScenarioFile, result: ConversionResult) -> SuiteBuild:
    """Набор тестов coUnit для одного файла сценариев."""
    sym = result.project.block(sf.block) if result.project is not None else None
    if sym is None:
        raise ScenarioError(f"{sf.path}: блок {sf.block} не найден в корпусе")
    targets: dict[tuple[str, str], Target] = {}
    for col in sf.columns:
        if col.kind == "tol":
            continue
        try:
            targets[(col.kind, col.path)] = resolve(result, sf.block, col)
        except ScenarioError as exc:
            raise ScenarioError(f"{sf.path}: {exc}") from exc
    name = suite_name(sym.st_name)
    scenarios = sf.scenarios()
    source = f"сценарии {sf.path}"
    decl = [
        f"// {AUTO_GENERATED}: s7conv gen-tests, {source}",
        "// Правка — в CSV (scenarios/README.md), затем python -m s7conv build-corpus.",
        f"// Назначение: тесты поведения сконвертированного {sym.st_name} по сценариям CSV (сценариев: "
        f"{len(scenarios)}, строк: {len(sf.rows)}):",
        "//             один метод-тест на сценарий, строки — по порядку с моделируемым временем GVL_S7Clock.",
        "//             Ожидаемые значения — из CSV (эталонные модели по описанию логики блока), не из",
        "//             результата конвертации.",
        f"// Автор:      s7conv {__version__} (сгенерировано)",
        "// Версия:     не указана",
        "// Документ:   scenarios/README.md, docs/methodology.md, раздел «Проверка поведения»",
        f"FUNCTION_BLOCK {name} EXTENDS coUnit.FB_TestSuite",
        "VAR",
    ]
    for scenario, _rows in scenarios:
        decl.append(f"{IND}fb{scenario} : {sym.st_name};  // свой экземпляр на сценарий")
        decl.append(f"{IND}x{scenario}Done : BOOL;  // сценарий выполнен (выполняется один раз)")
    decl.append("END_VAR")
    impl = [
        f"// {AUTO_GENERATED}: s7conv gen-tests, {source}",
        "// coUnit вызывает тесты каждый цикл; каждый сценарий выполняется в первом цикле целиком.",
        *[f"{scenario}();" for scenario, _rows in scenarios],
    ]
    obj = L.StObject(
        L.KIND_POU,
        name,
        "\n".join(decl) + "\n",
        folder=[SCENARIO_FOLDER],
        impl="\n".join(impl) + "\n",
        pou_kind=L.POU_FUNCTION_BLOCK,
        subdir="tests",
    )
    asserts = 0
    for scenario, rows in scenarios:
        mdecl = [
            f"// {AUTO_GENERATED}: {sf.path}, сценарий {scenario} (строк: {len(rows)})",
            f"METHOD PRIVATE {scenario}",
        ]
        inst = f"fb{scenario}"
        body = [
            f"// {AUTO_GENERATED}: {sf.path}, сценарий {scenario}",
            f"coUnit.TEST('{scenario}');",
            f"IF NOT x{scenario}Done THEN",
            f"{IND}x{scenario}Done := TRUE;",
            f"{IND}{CLOCK}.xSimulation := TRUE;",
        ]
        last: dict[str, str] = {}
        for row in rows:
            mark = ", на пороге таймера" if row.boundary else ""
            comment = f" — {row.comment}" if row.comment else ""
            body += ["", *wrap_comment(f"#{row.cycle}, t = {row.t_ms} мс{mark}{comment}", IND)]
            body.append(f"{IND}{CLOCK}.tSimNow := T#{row.t_ms}MS;")
            for path, cell in row.inputs.items():
                if last.get(path) == cell:
                    continue  # значение не изменилось: экземпляр хранит его с прошлой строки
                last[path] = cell
                target = targets[("in", path)]
                body.append(f"{IND}{inst}.{target.st_path} := {st_literal(cell, target.st_type)};")
            body.append(f"{IND}{inst}();")
            for path, cell in row.outputs.items():
                target = targets[("out", path)]
                delta = row.tolerances.get(path) if target.st_type in ("REAL", "LREAL") else None
                message = f"{scenario}#{row.cycle} {path}"
                text = assert_call(
                    target.st_type, st_literal(cell, target.st_type), f"{inst}.{target.st_path}", message, delta
                )
                body.extend(_wrapped(IND, text))
                asserts += 1
        body += ["", f"{IND}{CLOCK}.xSimulation := FALSE;", "END_IF", "coUnit.TEST_FINISHED();"]
        obj.methods.append(L.StMethod(scenario, "\n".join(mdecl) + "\n", "\n".join(body) + "\n"))
    _check_widths(obj)
    _check_counit_limits(sf.path, obj.name, asserts, len(scenarios))
    return SuiteBuild(obj, asserts, len(sf.rows), len(scenarios))


MAX_LINE = 120  # tools/check/st_lint.toml, max_line_length

# Лимиты coUnit 1.2.0.0 (GVL_Param_coUnit, значения по умолчанию): библиотека их не проверяет — лишние проверки
# и тесты пишутся за границы массивов набора. Генератор держит запас: набор с проверками больше бюджета или
# с тестами больше лимита не выпускается — CSV нужно разделить (один набор на файл CSV).
COUNIT_MAX_ASSERTS_PER_SUITE = 1000  # MaxNumberOfAssertsForEachTestSuite
COUNIT_ASSERTS_BUDGET = 900  # запас под проверки, которые добавит ручная правка набора
COUNIT_MAX_TESTS_PER_SUITE = 100  # MaxNumberOfTestsForEachTestSuite


def _check_counit_limits(path: str, suite: str, asserts: int, tests: int) -> None:
    if asserts > COUNIT_ASSERTS_BUDGET:
        raise ScenarioError(
            f"{path}: в наборе {suite} проверок {asserts} — больше {COUNIT_ASSERTS_BUDGET} (лимит coUnit 1.2.0.0 "
            f"{COUNIT_MAX_ASSERTS_PER_SUITE} на набор не проверяется библиотекой); разделите сценарии на несколько CSV"
        )
    if tests > COUNIT_MAX_TESTS_PER_SUITE:
        raise ScenarioError(
            f"{path}: в наборе {suite} сценариев {tests} — больше лимита coUnit {COUNIT_MAX_TESTS_PER_SUITE} тестов "
            "на набор; разделите сценарии на несколько CSV"
        )


def _check_widths(obj: L.StObject) -> None:
    """Сгенерированные строки не длиннее MAX_LINE (иначе st_lint STL003): длинные имена — ошибка генерации."""
    texts = [obj.decl, obj.impl or ""] + [m.decl for m in obj.methods] + [m.impl or "" for m in obj.methods]
    for text in texts:
        for line in text.splitlines():
            if len(line) > MAX_LINE:
                raise ScenarioError(f"{obj.name}: строка длиннее {MAX_LINE} символов — укоротите имена: {line[:60]}...")


def wrap_comment(text: str, ind: str, width: int = 116) -> list[str]:
    """Комментарий // с переносом по словам."""
    parts = textwrap.wrap(text, width=width - len(ind) - 3, break_long_words=False) or [""]
    return [f"{ind}// {p}" for p in parts]


def instance_name(suite: str) -> str:
    """Имя экземпляра набора в PRG_Tests.

    FB_F_NormX_Test -> fbF_NormXTest, FB_Motor_ScenarioTest -> fbMotor_ScenarioTest.
    """
    short = _short(suite)
    if short.endswith("_Test"):
        short = short[: -len("_Test")] + "Test"
    return "fb" + short


def is_test_suite(obj: L.StObject) -> bool:
    if obj.kind != L.KIND_POU or obj.pou_kind != L.POU_FUNCTION_BLOCK:
        return False
    header = obj.header or L.parse_header(obj.decl)
    return header is not None and any(
        e.lower() in ("counit.fb_testsuite", "cfunit.fb_testsuite") for e in header.extends
    )


def hand_written_suites(
    root: Path, subdir: str = "tests", exclude_folder: str = SCENARIO_FOLDER
) -> list[tuple[list[str], str]]:
    """Рукописные наборы тестов в root/subdir (кроме папки сгенерированных): [(папки, имя)]."""
    if not (root / subdir).is_dir():
        return []
    scan = L.scan(str(root), subdir)
    found = [
        (list(o.folder), o.name)
        for o in scan.objects
        if is_test_suite(o) and (not o.folder or o.folder[0] != exclude_folder)
    ]
    return sorted(found, key=lambda x: ([f.lower() for f in x[0]], x[1].lower()))


def generate_prg_tests(generated: Sequence[str], hand_written: Sequence[str]) -> L.StObject:
    """PRG_Tests: экземпляры всех наборов (объявление регистрирует набор в coUnit) и coUnit.RUN()."""
    suites = [*hand_written, *generated]
    decl = [
        f"// {AUTO_GENERATED}: s7conv gen-tests — список наборов собирается из tests/ (рукописные наборы",
        "//             EXTENDS coUnit.FB_TestSuite) и сценариев scenarios/*.csv; новый набор — пересоздать.",
        "// Назначение: программа запуска юнит-тестов CfUnit (coUnit 1.2.0.0). Объявляет экземпляры наборов",
        "//             тестов (объявление регистрирует набор в coUnit) и каждый цикл вызывает coUnit.RUN().",
        "//             Назначается задаче только тестового приложения (CODESYS Control Win), не рабочего ПЛК.",
        f"// Автор:      s7conv {__version__} (сгенерировано)",
        "// Версия:     не указана",
        "// Документ:   docs/TEST_REPORT.md, docs/methodology.md",
        f"PROGRAM {PRG_TESTS}",
        "VAR",
    ]
    kinds = dict.fromkeys(hand_written, "рукописный набор")
    kinds.update(dict.fromkeys(generated, "сценарии CSV (сгенерировано)"))
    for suite in suites:
        decl.append(f"{IND}{instance_name(suite)} : {suite};  // {kinds[suite]}")
    decl += [
        f"{IND}// все наборы завершены — флаг для скрипта запуска тестов (read_value)",
        f"{IND}xAllFinished : BOOL;",
        "END_VAR",
    ]
    impl = [
        f"// {AUTO_GENERATED}: s7conv gen-tests",
        "// Все зарегистрированные наборы выполняются параллельно; итоги — в журнал устройства (логгер",
        "// coUnit) и в XML-файл xUnit.",
        "coUnit.RUN();",
        "",
        "// AreAllTestsFinished() вызывается после RUN(): у метода есть побочный эффект на первом цикле.",
        "// Наборы объединяются через AND (не AND_THEN): метод вызывается у каждого набора в каждом цикле.",
    ]
    if suites:
        calls = [f"{instance_name(s)}.AreAllTestsFinished()" for s in suites]
        impl.append(f"xAllFinished := {calls[0]}")
        impl.extend(f"{IND}{IND}AND {c}" for c in calls[1:])
        impl[-1] += ";"
    else:
        impl.append("xAllFinished := TRUE;")
    prg = L.StObject(
        L.KIND_POU,
        PRG_TESTS,
        "\n".join(decl) + "\n",
        impl="\n".join(impl) + "\n",
        pou_kind=L.POU_PROGRAM,
        subdir="tests",
    )
    _check_widths(prg)
    return prg


@dataclass
class TestsBuild:
    objects: list[L.StObject]
    suites: list[SuiteBuild]
    hand_written: list[str]


def scenario_files(scenario_dir: Path, base: Path) -> list[ScenarioFile]:
    files: list[ScenarioFile] = []
    for path in sorted(scenario_dir.glob("*.csv"), key=lambda p: p.name.lower()):
        try:
            label = path.resolve().relative_to(base.resolve()).as_posix()
        except ValueError:
            label = path.as_posix()
        text = path.read_bytes().decode("utf-8")
        files.append(read_scenarios(text, label))
    if not files:
        raise ScenarioError(f"{scenario_dir}: нет файлов *.csv")
    return files


def generate(scenario_dir: Path, result: ConversionResult, tests_root: Path, subdir: str, base: Path) -> TestsBuild:
    """Наборы по всем CSV каталога и PRG_Tests (рукописные наборы — из tests_root/subdir).

    base — корень для путей CSV в шапках; объекты получают subdir (раскладка tests_root/subdir).
    """
    suites = [generate_suite(sf, result) for sf in scenario_files(scenario_dir, base)]
    for s in suites:
        s.obj.subdir = subdir
    hand = [name for _folders, name in hand_written_suites(tests_root, subdir)]
    generated = [s.obj.name for s in suites]
    clash = sorted(set(hand) & set(generated))
    if clash:
        raise ScenarioError(f"рукописный набор с именем сгенерированного: {', '.join(clash)}")
    prg = generate_prg_tests(generated, hand)
    prg.subdir = subdir
    return TestsBuild([*(s.obj for s in suites), prg], suites, hand)


__all__ = [
    "AUTO_GENERATED",
    "PRG_TESTS",
    "SCENARIO_FOLDER",
    "Column",
    "Row",
    "ScenarioError",
    "ScenarioFile",
    "Target",
    "TestsBuild",
    "check_value",
    "generate",
    "generate_prg_tests",
    "generate_suite",
    "hand_written_suites",
    "instance_name",
    "read_scenarios",
    "resolve",
    "scenario_files",
    "suite_name",
]
