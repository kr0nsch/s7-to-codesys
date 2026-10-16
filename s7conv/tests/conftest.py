"""Общие помощники тестов s7conv: конвертация текста SCL в памяти, доступ к объектам результата."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from s7conv import symbols as S
from s7conv.emitter import ConversionResult, Note, Options, convert
from s7conv.layout import L
from s7conv.parser import parse_source

TESTS_DIR = Path(__file__).resolve().parent
FIXTURES = TESTS_DIR / "fixtures"
SNAPSHOTS = TESTS_DIR / "snapshots"
REPO_ROOT = TESTS_DIR.parent.parent
CORPUS = REPO_ROOT / "samples" / "scl"


class Converted:
    """Результат конвертации набора исходников с удобным доступом к объектам и пометкам."""

    def __init__(self, result: ConversionResult) -> None:
        self.result = result
        self.objects = {o.name: o for o in result.objects}

    def obj(self, name: str) -> L.StObject:
        assert name in self.objects, f"нет объекта {name}; есть: {sorted(self.objects)}"
        return self.objects[name]

    def decl(self, name: str) -> str:
        return self.obj(name).decl

    def impl(self, name: str) -> str:
        impl = self.obj(name).impl
        assert impl is not None
        return impl

    def code(self, name: str) -> list[str]:
        """Строки тела без комментариев и пустых строк (для точных сравнений)."""
        return [
            line.strip() for line in self.impl(name).splitlines() if line.strip() and not line.strip().startswith("//")
        ]

    @property
    def notes(self) -> list[Note]:
        return [n for f in self.result.files for n in f.notes]

    def rules(self, severity: str | None = None) -> set[str]:
        return {n.rule for n in self.notes if severity is None or n.severity == severity}

    def statuses(self) -> dict[str, int]:
        counts = {"auto": 0, "check": 0, "todo": 0}
        for f in self.result.files:
            for item in f.items:
                counts[item.status] += 1
        return counts


ConvertFn = Callable[..., Converted]


def convert_texts(
    sources: dict[str, str],
    tags: str | None = None,
    options: Options | None = None,
) -> Converted:
    files = [parse_source(text, name) for name, text in sources.items()]
    project = S.Project()
    if tags is not None:
        loaded, errors = S.load_tag_table(tags, "tags.csv")
        assert not errors, errors
        project.add_tags(loaded)
    return Converted(convert(files, project, options))


@pytest.fixture
def conv() -> ConvertFn:
    """conv(text, *more_texts, tags=None, options=None) — конвертировать один или несколько текстов SCL."""

    def run(*texts: str, tags: str | None = None, options: Options | None = None) -> Converted:
        return convert_texts({f"t{i}.scl": t for i, t in enumerate(texts)}, tags, options)

    return run


def fb(body: str, decls: str = "", name: str = "FB_T") -> str:
    """Минимальный FUNCTION_BLOCK TIA с объявлениями и телом."""
    return f'FUNCTION_BLOCK "{name}"\nVERSION : 0.1\n{decls}\nBEGIN\n{body}\nEND_FUNCTION_BLOCK\n'
