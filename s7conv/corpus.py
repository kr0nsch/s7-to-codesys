"""Сборка корпусов samples/scl/ и samples/lang/ в раскладку репозитория — команда `s7conv build-corpus`.

Один источник всего, что в репозитории получено из корпусов и сценариев:

- `src/{DUTs,GVLs,POUs}/Converted/` — результат конвертера с настройками CORPUS_OPTIONS (папка проекта
  CODESYS `Converted`; таймеры S7Compat с подменяемым временем; периоды и номера OB — `ob_config.json`
  корпуса). Рукописные объекты поддержки (`src/*/S7Compat`: F_NormX, F_ScaleX, таймеры) не
  генерируются — сборка только проверяет, что нужные на месте;
- `docs/CONVERSION_REPORT.md` — отчёт конвертации (и `build/report.html` при записи);
- `tools/codesys/config.json` — задачи из OB (`modes.normal.tasks`); остальной текст файла не меняется;
- `tests/POUs/Scenarios/` и `tests/POUs/PRG_Tests/` — тесты сценариев и программа запуска (testgen);
- корпус всех языков (SimaticML LAD/FBD/STL/SCL, samples/lang): `src/{DUTs,GVLs,POUs}/Lang/Converted/` с
  суффиксом `_Lang` у генерируемых GVL (один проект CODESYS с корпусом SCL, плоское пространство имён),
  `docs/CONVERSION_REPORT_LANG.md` и тесты сценариев `scenarios/lang/` в тех же `tests/POUs/Scenarios`.
  Корпус SCL 1.0.0 собирается так же, как раньше: его файлы не меняются.

`--check` ничего не пишет и возвращает код 1, если файлы репозитория отличаются от результата:
так CI и pytest проверяют, что закоммиченный результат воспроизводится из корпуса.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from s7conv import mapping as M
from s7conv import pipeline as P
from s7conv import report as R
from s7conv import testgen as TG
from s7conv.emitter import ConversionResult, Options
from s7conv.layout import REPO_ROOT, SUPPORT_FOLDER, L

CORPUS_REL = "samples/scl"
SCENARIOS_REL = "scenarios"
FOLDER = "Converted"
REPORT_REL = "docs/CONVERSION_REPORT.md"
REPORT_HTML_REL = "build/report.html"
CONFIG_REL = "tools/codesys/config.json"
COMMAND = "s7conv build-corpus"
# Корпус всех языков S7 (SimaticML)
LANG_CORPUS_REL = "samples/lang"
LANG_SCENARIOS_REL = "scenarios/lang"
# Папка проекта CODESYS Lang/Converted: шаблоны src/*/Converted/* настроек статанализа (tools/check) и правила
# для сгенерированного кода действуют на оба корпуса; src/<вид>/Converted/ корпуса SCL 1.0.0 не меняется
LANG_FOLDER = "Lang/Converted"
LANG_FOLDERS = ("Lang", "Converted")
LANG_SUFFIX = "_Lang"
LANG_REPORT_REL = "docs/CONVERSION_REPORT_LANG.md"
LANG_REPORT_HTML_REL = "build/report-lang.html"
# Вариант SFC блоков S7-GRAPH (PLCopen XML для импорта в CODESYS: tools_project/cds_plcopen.py)
LANG_PLCOPEN_REL = "plcopen/Lang/Converted"

# Каталоги, которыми сборка владеет целиком: лишние файлы в них удаляются (--check сообщает о них)
MANAGED_DIRS = (
    *(f"src/{cat}/{FOLDER}" for cat in L.CATEGORIES),
    f"tests/POUs/{TG.SCENARIO_FOLDER}",
    f"tests/POUs/{TG.PRG_TESTS}",
)
# Каталоги корпуса всех языков — управляемые, только если корпус samples/lang есть в корне
LANG_MANAGED_DIRS = (
    *(f"src/{cat}/{LANG_FOLDER}" for cat in L.CATEGORIES),
    f"tests/POUs/{TG.LANG_SCENARIO_FOLDER}",
    LANG_PLCOPEN_REL,
)


class CorpusError(Exception):
    """Сборку корпуса нельзя выполнить: нет поддержки, конфликт имён, неверный config.json (код 2)."""


def corpus_options(corpus: Path = REPO_ROOT / CORPUS_REL) -> Options:
    """Настройки конвертера для корпуса: одни и те же для src/, отчёта и тестов сценариев."""
    ob_path = corpus / P.OB_CONFIG_NAME
    return Options(
        folder=(FOLDER,),
        timers=M.S7COMPAT,
        f_trig=M.STANDARD,
        ob_config=P.load_ob_config(str(ob_path)) if ob_path.is_file() else {},
    )


def lang_options() -> Options:
    """Настройки корпуса всех языков: папка Lang/Converted, суффикс GVL, таймеры S7Compat, профиль по XML."""
    return Options(
        folder=LANG_FOLDERS,
        timers=M.S7COMPAT,
        f_trig=M.STANDARD,
        global_suffix=LANG_SUFFIX,
    )


@dataclass
class CorpusBuild:
    files: dict[str, str]  # путь от корня -> текст
    result: ConversionResult
    tests: TG.TestsBuild
    html: str
    warnings: list[str] = field(default_factory=list)
    lang_result: ConversionResult | None = None
    lang_html: str = ""
    lang_files: dict[str, str] = field(default_factory=dict)  # корпус всех языков: путь -> текст
    lang_tests: TG.TestsBuild | None = None
    lang_dirs_managed: bool = False  # каталог samples/lang есть: Lang/Converted и ScenariosLang — под сборкой

    @property
    def all_files(self) -> dict[str, str]:
        return {**self.files, **self.lang_files}

    @property
    def managed(self) -> tuple[str, ...]:
        lang = self.lang_result is not None or self.lang_dirs_managed
        return MANAGED_DIRS + (LANG_MANAGED_DIRS if lang else ())


def _object_files(objects: list[L.StObject], subdir: str) -> dict[str, str]:
    files: dict[str, str] = {}
    for obj in objects:
        for rel, text in L.object_files(obj, subdir):
            files[rel] = L.normalize_text(text)
    return files


def _managed(rel: str) -> bool:
    return any(rel == d or rel.startswith(d + "/") for d in (*MANAGED_DIRS, *LANG_MANAGED_DIRS))


def _hand_written(root: Path) -> list[L.StObject]:
    """Объекты src/, которые сборка не генерирует (рукописные)."""
    if not (root / "src").is_dir():
        return []
    scan = L.scan(str(root), "src")
    return [o for o in scan.objects if not _managed(o.rel_dir("src"))]


def _check_hand_written(root: Path, result: ConversionResult) -> None:
    hand = _hand_written(root)
    names = {o.name.lower(): o for o in hand}
    missing = [n for n in sorted(result.support) if n.lower() not in names]
    if missing:
        raise CorpusError(
            f"нет рукописных объектов поддержки {', '.join(missing)} (ожидаются в src/*/{SUPPORT_FOLDER})"
        )
    clash = sorted(o.name for o in result.objects if o.name.lower() in names)
    if clash:
        raise CorpusError(f"имена сгенерированных объектов совпадают с рукописными в src/: {', '.join(clash)}")


def config_tasks(result: ConversionResult) -> list[dict[str, Any]]:
    """Задачи для tools/codesys/config.json (формат modes.<режим>.tasks: name, interval_ms, priority, pous)."""
    tasks: list[dict[str, Any]] = []
    for task in result.tasks:
        if task.type != "cyclic" or task.interval_ms is None:
            raise CorpusError(f"задача {task.name}: tools/codesys создаёт только циклические задачи с периодом")
        tasks.append({"name": task.name, "interval_ms": task.interval_ms, "priority": task.priority, "pous": task.pous})
    return tasks


def _skip_string(text: str, i: int) -> int:
    """Индекс после строки JSON, начинающейся с кавычки в позиции i."""
    i += 1
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == '"':
            return i + 1
        i += 1
    raise CorpusError("config.json: незакрытая строка")


def _find_key(text: str, start: int, end: int, key: str) -> int:
    """Позиция значения ключа key на верхнем уровне объекта text[start:end] (start — после '{')."""
    depth = 0
    i = start
    while i < end:
        c = text[i]
        if c == '"':
            j = _skip_string(text, i)
            if depth == 0 and text[i + 1 : j - 1] == key:
                k = j
                while text[k] in " \t\r\n":
                    k += 1
                if text[k] == ":":
                    k += 1
                    while text[k] in " \t\r\n":
                        k += 1
                    return k
            i = j
            continue
        if c in "{[":
            depth += 1
        elif c in "}]":
            depth -= 1
        i += 1
    raise CorpusError(f"config.json: нет ключа {key!r}")


def _value_end(text: str, i: int) -> int:
    """Индекс после значения JSON (объект или массив), начинающегося в позиции i."""
    depth = 0
    while i < len(text):
        c = text[i]
        if c == '"':
            i = _skip_string(text, i)
            continue
        if c in "{[":
            depth += 1
        elif c in "}]":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise CorpusError("config.json: незакрытый объект или массив")


def update_config_tasks(text: str, tasks: list[dict[str, Any]]) -> str:
    """Заменить modes.normal.tasks в тексте config.json, не трогая остальной текст и форматирование."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CorpusError(f"config.json: неверный JSON ({exc})") from exc
    if not isinstance(data.get("modes"), dict) or not isinstance(data["modes"].get("normal"), dict):
        raise CorpusError("config.json: нет раздела modes.normal")
    root_start = text.index("{") + 1
    modes = _find_key(text, root_start, len(text), "modes")
    normal = _find_key(text, modes + 1, _value_end(text, modes), "normal")
    tasks_at = _find_key(text, normal + 1, _value_end(text, normal), "tasks")
    tasks_end = _value_end(text, tasks_at)
    line_start = text.rfind("\n", 0, tasks_at) + 1
    indent = len(text[line_start:tasks_at]) - len(text[line_start:tasks_at].lstrip())
    items = [json.dumps(t, ensure_ascii=False) for t in tasks]
    pad = " " * (indent + 2)
    rendered = "[\n" + ",\n".join(pad + item for item in items) + "\n" + " " * indent + "]" if items else "[]"
    new_text = text[:tasks_at] + rendered + text[tasks_end:]
    expected = json.loads(text)
    expected["modes"]["normal"]["tasks"] = tasks
    if json.loads(new_text) != expected:  # pragma: no cover - защита от ошибки замены
        raise CorpusError("config.json: замена modes.normal.tasks изменила другие значения")
    return new_text


def build(root: Path = REPO_ROOT) -> CorpusBuild:
    """Всё, что получается из корпуса и сценариев: {путь: текст} без записи на диск."""
    corpus = root / CORPUS_REL
    if not corpus.is_dir():
        raise CorpusError(f"нет корпуса {corpus}")
    inputs = P.collect_inputs([str(corpus)])
    result, _files = P.run(inputs, corpus_options(corpus), base=root)
    _check_hand_written(root, result)
    files = _object_files(result.objects, "src")
    files[REPORT_REL] = R.render_markdown(
        result,
        [CORPUS_REL],
        command=COMMAND,
        tasks_target=f"`{CONFIG_REL}` (режим normal, `modes.normal.tasks`)",
    )
    config_path = root / CONFIG_REL
    warnings = list(result.errors)
    if config_path.is_file():
        files[CONFIG_REL] = update_config_tasks(config_path.read_text(encoding="utf-8"), config_tasks(result))
    else:
        warnings.append(f"{CONFIG_REL} нет — задачи только в отчёте ({REPORT_REL})")
    html = R.render_html(result, [CORPUS_REL])
    built = CorpusBuild(files=files, result=result, tests=TG.TestsBuild([], [], []), html=html, warnings=warnings)
    # samples/lang без *.xml (демокорпус убран, своих блоков нет): старый результат Lang/Converted удаляется
    built.lang_dirs_managed = (root / LANG_CORPUS_REL).is_dir()
    if any((root / LANG_CORPUS_REL).rglob("*.xml")):
        _build_lang(root, built)
    lang_suites = [s.obj.name for s in built.lang_tests.suites] if built.lang_tests is not None else []
    built.tests = TG.generate(root / SCENARIOS_REL, result, root, "tests", root, lang_suites)
    files.update(_object_files(built.tests.objects, "tests"))
    check_names_unique(root, built)
    return built


def _build_lang(root: Path, built: CorpusBuild) -> None:
    """Корпус всех языков: Lang/Converted, отчёт CONVERSION_REPORT_LANG.md, наборы ScenariosLang."""
    lang_inputs = P.collect_inputs([str(root / LANG_CORPUS_REL)])
    lang_result, _lang_files = P.run(lang_inputs, lang_options(), base=root)
    _check_hand_written(root, lang_result)
    clash = {o.name.lower() for o in built.result.objects} & {o.name.lower() for o in lang_result.objects}
    if clash:
        raise CorpusError(f"имена объектов корпусов SCL и всех языков совпадают: {', '.join(sorted(clash))}")
    lang_files = _object_files(lang_result.objects, "src")
    lang_files[LANG_REPORT_REL] = R.render_markdown(
        lang_result,
        [LANG_CORPUS_REL],
        command=COMMAND,
        tasks_target="— (OB в корпусе всех языков нет)",
        title="Отчёт конвертации S7 (LAD, FBD, STL, SCL) → ST CODESYS",
    )
    built.warnings.extend(lang_result.errors)
    from s7conv.plcopen import graph_sfc

    sfc = graph_sfc(list(lang_inputs.xml), base=root)
    for name, xml in sfc.files.items():
        lang_files[f"{LANG_PLCOPEN_REL}/{name}.xml"] = xml
    built.warnings.extend(f"{name}: вариант SFC не построен — {why}" for name, why in sfc.skipped.items())
    lang_scenarios = root / LANG_SCENARIOS_REL
    if any(lang_scenarios.glob("*.csv")):  # свои блоки XML без сценариев: код и отчёт без наборов
        source = TG.ScenarioSource(lang_scenarios, lang_result, TG.load_aliases(lang_scenarios))
        built.lang_tests = TG.generate_lang(source, "tests", root)
        lang_files.update(_object_files(built.lang_tests.objects, "tests"))
    from s7conv import docs_gen

    lang_files.update(docs_gen.write_all(root))
    built.lang_result = lang_result
    built.lang_html = R.render_html(lang_result, [LANG_CORPUS_REL])
    built.lang_files = lang_files


def check_names_unique(root: Path, built: CorpusBuild) -> None:
    """Объекты уникальны по всему src/ (CODESYS — плоское пространство имён); члены GVL корпуса всех языков
    не совпадают с членами остальных GVL (RuSTy снимает имена GVL — E004). Повторы внутри корпуса SCL 1.0.0
    (heartbeat в DB_Plant и DB_Telegram) уже были и проверяются RuSTy с исключениями (tools/check)."""
    lang = list(built.lang_result.objects) if built.lang_result else []
    generated = list(built.result.objects) + lang
    names = {x.name.lower() for x in generated}
    hand = [o for o in _hand_written(root) if o.name.lower() not in names]
    seen: set[str] = set()
    errors: list[str] = []
    for obj in [*generated, *hand]:
        if obj.name.lower() in seen:
            errors.append(f"объект {obj.name}")
        seen.add(obj.name.lower())

    def members(objs: list[L.StObject]) -> dict[str, tuple[str, str]]:
        found: dict[str, tuple[str, str]] = {}  # имя (lower) -> (GVL, имя как в объявлении)
        for obj in objs:
            if obj.kind != L.KIND_GVL:
                continue
            for block in L.parse_var_blocks(obj.decl):
                for d in block.decls:
                    for name in d.name_list:
                        prev = found.get(name.lower())
                        if prev is not None and prev[0] != obj.name and obj in lang:
                            errors.append(f"член GVL {name} ({prev[0]} и {obj.name})")
                        found.setdefault(name.lower(), (obj.name, name))
        return found

    lang_members = members(lang)
    other_members = members([o for o in [*built.result.objects, *hand] if o not in lang])
    for key, (gvl, name) in lang_members.items():
        if key in other_members:
            errors.append(f"член GVL {name} ({gvl} и {other_members[key][0]})")
    if errors:
        raise CorpusError("имена в src/ повторяются: " + "; ".join(sorted(set(errors))))


def _existing(root: Path, managed: Sequence[str]) -> set[str]:
    found: set[str] = set()
    for rel_dir in managed:
        base = root / rel_dir
        if base.is_dir():
            found.update(p.relative_to(root).as_posix() for p in base.rglob("*") if p.is_file())
    return found


@dataclass
class Diff:
    changed: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)  # есть в результате, нет в репозитории
    stale: list[str] = field(default_factory=list)  # есть в управляемых каталогах, нет в результате

    @property
    def clean(self) -> bool:
        return not (self.changed or self.missing or self.stale)


def diff_files(files: dict[str, str], root: Path, managed: Sequence[str]) -> Diff:
    """Сравнение {путь: текст} с диском; лишние — файлы управляемых каталогов, которых нет в files."""
    diff = Diff()
    for rel, text in sorted(files.items()):
        path = root / rel
        if not path.is_file():
            diff.missing.append(rel)
        elif path.read_bytes() != text.encode("utf-8"):
            diff.changed.append(rel)
    diff.stale = sorted(_existing(root, managed) - set(files))
    return diff


def apply_diff(diff: Diff, files: dict[str, str], root: Path, managed: Sequence[str]) -> None:
    """Записать изменённые и новые файлы, удалить лишние и опустевшие каталоги управляемых каталогов."""
    for rel in diff.stale:
        (root / rel).unlink()
    for rel_dir in managed:
        base = root / rel_dir
        if base.is_dir():
            for d in sorted((p for p in base.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
                if not any(d.iterdir()):
                    d.rmdir()
            if not any(base.iterdir()):
                base.rmdir()
    for rel in [*diff.missing, *diff.changed]:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(files[rel].encode("utf-8"))


def compare(build_result: CorpusBuild, root: Path = REPO_ROOT) -> Diff:
    return diff_files(build_result.all_files, root, build_result.managed)


def write(build_result: CorpusBuild, root: Path = REPO_ROOT, html: bool = True) -> Diff:
    """Записать результат; удалить лишние файлы управляемых каталогов. Возвращает, что изменилось."""
    diff = compare(build_result, root)
    apply_diff(diff, build_result.all_files, root, build_result.managed)
    if html:
        target = root / REPORT_HTML_REL
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(build_result.html.encode("utf-8"))
        if build_result.lang_html:
            (root / LANG_REPORT_HTML_REL).write_bytes(build_result.lang_html.encode("utf-8"))
    return diff


__all__ = [
    "COMMAND",
    "CONFIG_REL",
    "CORPUS_REL",
    "FOLDER",
    "LANG_CORPUS_REL",
    "LANG_FOLDER",
    "LANG_FOLDERS",
    "LANG_PLCOPEN_REL",
    "LANG_REPORT_REL",
    "LANG_SCENARIOS_REL",
    "LANG_SUFFIX",
    "MANAGED_DIRS",
    "REPORT_REL",
    "CorpusBuild",
    "CorpusError",
    "Diff",
    "apply_diff",
    "build",
    "check_names_unique",
    "compare",
    "config_tasks",
    "corpus_options",
    "diff_files",
    "lang_options",
    "update_config_tasks",
    "write",
]
