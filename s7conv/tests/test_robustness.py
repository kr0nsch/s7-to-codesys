"""Устойчивость: разбор и конвертация не падают ни на каком входе (ошибки → RawStmt/RawDecl/RawBlock).

Генерируются произвольный текст (в том числе не-ASCII) и «поломанные» исходники: из фикстур и
корпуса вырезаются и вставляются куски, ключевые слова, скобки и кавычки.
"""

from __future__ import annotations

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from s7conv import symbols as S
from s7conv.emitter import convert
from s7conv.parser import parse_source
from s7conv.tests.conftest import CORPUS, FIXTURES

SOURCES = [p.read_text(encoding="utf-8") for p in sorted(FIXTURES.glob("*.scl"))]
SOURCES += [p.read_text(encoding="utf-8") for p in sorted(CORPUS.glob("*.scl"))[:6]] if CORPUS.is_dir() else []
JUNK = ["(", ")", "'", '"', "#", "%", "{", "}", "END_IF;", ":=", "(*", "*)", "BEGIN", "END_VAR", "REGION x", "Привет"]


def run(text: str) -> None:
    sf = parse_source(text, "fuzz.scl")
    result = convert([sf], S.Project())
    for obj in result.objects:
        assert obj.name and obj.decl is not None


@settings(max_examples=300, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(st.text(max_size=400))
def test_arbitrary_text_never_crashes(text: str) -> None:
    run(text)


@settings(max_examples=150, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(
    st.sampled_from(SOURCES),
    st.integers(min_value=0, max_value=10_000),
    st.integers(min_value=0, max_value=60),
    st.sampled_from(["", *JUNK]),
)
def test_damaged_sources_never_crash(source: str, at: int, cut: int, insert: str) -> None:
    pos = at % (len(source) + 1)
    run(source[:pos] + insert + source[pos + cut :])
