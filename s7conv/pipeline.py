"""Конвейер: входные файлы → разбор → таблица символов → эмиттер → раскладка, tasks.json, отчёт.

Входы: исходники SCL (*.scl и выгрузка TIA Portal *.db, *.udt — тот же синтаксис), таблицы тегов *.csv
(экспорт TIA Portal) и каталоги (рекурсивно; таблицы тегов распознаются по заголовку, ob_config.json в
каталоге — конфигурация OB). Кодировка входа — UTF-8
(с BOM или без) или cp1251, переводы строк любые.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from s7conv import mapping as M
from s7conv import symbols as S
from s7conv.emitter import ConversionResult, Options, convert
from s7conv.layout import SUPPORT_SRC, L
from s7conv.nodes import SourceFile
from s7conv.parser import parse_source

# «Generate source from blocks» TIA Portal: блоки — .scl, блоки данных — .db, типы данных PLC — .udt
SCL_SUFFIXES = (".scl", ".db", ".udt")
TAG_SUFFIXES = (".csv",)


class InputError(Exception):
    """Ошибка входных данных (нет файла, не читается) — код выхода 2."""


OB_CONFIG_NAME = "ob_config.json"


@dataclass
class Inputs:
    scl: list[Path] = field(default_factory=list)
    tags: list[Path] = field(default_factory=list)
    ob_config: Path | None = None  # ob_config.json, найденный во входном каталоге


def display_path(path: Path, base: Path | None = None) -> str:
    base = base or Path.cwd()
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def read_source(path: Path) -> str:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise InputError(f"{path}: не читается ({exc.strerror})") from exc
    for encoding in ("utf-8-sig", "cp1251"):
        try:
            text = data.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:  # pragma: no cover - cp1251 декодирует любые байты
        raise InputError(f"{path}: кодировка не распознана")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def collect_inputs(paths: list[str], tag_files: list[str] | None = None) -> Inputs:
    """Исходники SCL (*.scl, *.db, *.udt) и таблицы тегов *.csv из путей (каталоги — рекурсивно, по имени)."""
    inputs = Inputs()
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            if inputs.ob_config is None and (path / OB_CONFIG_NAME).is_file():
                inputs.ob_config = path / OB_CONFIG_NAME
            for found in sorted(path.rglob("*"), key=lambda p: p.as_posix().lower()):
                if not found.is_file():
                    continue
                suffix = found.suffix.lower()
                if suffix in SCL_SUFFIXES:
                    inputs.scl.append(found)
                elif suffix in TAG_SUFFIXES and S.looks_like_tag_table(read_source(found)):
                    inputs.tags.append(found)
        elif path.is_file():
            if path.suffix.lower() in TAG_SUFFIXES:
                inputs.tags.append(path)
            else:
                inputs.scl.append(path)
        else:
            raise InputError(f"{raw}: файл или каталог не найден")
    for raw in tag_files or []:
        path = Path(raw)
        if not path.is_file():
            raise InputError(f"{raw}: таблица тегов не найдена")
        inputs.tags.append(path)
    if not inputs.scl:
        raise InputError("нет входных файлов *.scl, *.db, *.udt")
    return inputs


def parse_inputs(inputs: Inputs) -> list[SourceFile]:
    return [parse_source(read_source(p), str(p)) for p in inputs.scl]


def load_project(inputs: Inputs, base: Path | None = None) -> S.Project:
    project = S.Project()
    for path in inputs.tags:
        tags, errors = S.load_tag_table(read_source(path), display_path(path, base))
        project.errors.extend(errors)
        project.add_tags(tags)
    return project


def load_ob_config(path: str | None) -> dict[str, object]:
    if not path:
        return {}
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InputError(f"{path}: конфигурация OB не читается ({exc})") from exc
    if not isinstance(data, dict):
        raise InputError(f'{path}: ожидался объект JSON {{"<имя OB>": {{...}}}}')
    return data


def run(
    inputs: Inputs, options: Options | None = None, base: Path | None = None
) -> tuple[ConversionResult, list[SourceFile]]:
    """Разбор и конвертация; пути в шапках и отчёте — от base (по умолчанию — от текущего каталога)."""
    files = parse_inputs(inputs)
    project = load_project(inputs, base)
    display = {sf.path: display_path(Path(sf.path), base) for sf in files}
    result = convert(files, project, options, display)
    return result, files


def write_layout(result: ConversionResult, out_dir: Path, clean: bool = False, support: bool = False) -> list[str]:
    """Объекты → <out>/src/... (stlayout.write_objects), tasks.json; support — скопировать объекты поддержки."""
    out_dir.mkdir(parents=True, exist_ok=True)
    objects = list(result.objects)
    if support:
        objects.extend(support_objects(sorted(result.support)))
    written = L.write_objects(objects, str(out_dir), "src", clean=clean)
    tasks_path = out_dir / "tasks.json"
    with open(tasks_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(result.tasks_json(), fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    written.append("tasks.json")
    return written


def support_objects(names: list[str]) -> list[L.StObject]:
    """Объекты поддержки (F_NormX, F_ScaleX, таймеры S7Compat и их зависимости) из src/ репозитория.

    Их исходники пишутся вручную (src/*/S7Compat), не генерируются; папка проекта сохраняется.
    """
    wanted = [n for n in M.support_closure(names) if n in M.SUPPORT_DEPENDENCIES]
    if not wanted:
        return []
    scan = L.scan(str(SUPPORT_SRC.parent), "src")
    found = {o.name: o for o in scan.objects}
    result: list[L.StObject] = []
    for name in wanted:
        obj = found.get(name)
        if obj is None:
            raise InputError(f"объект поддержки {name} не найден в {SUPPORT_SRC}")
        result.append(obj)
    return result


__all__ = [
    "InputError",
    "Inputs",
    "collect_inputs",
    "display_path",
    "load_ob_config",
    "load_project",
    "parse_inputs",
    "read_source",
    "run",
    "support_objects",
    "write_layout",
]
