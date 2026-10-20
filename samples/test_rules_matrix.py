"""Матрица «правило перевода LAD/FBD/STL → тест»: у каждого правила выпуска есть существующий тест."""

from __future__ import annotations

import re
from pathlib import Path

import rules_matrix

ROOT = Path(__file__).resolve().parents[1]


def _test_names() -> set[str]:
    names: set[str] = set()
    for path in [*ROOT.glob("s7conv/tests/test_*.py"), *ROOT.glob("samples/**/test_*.py")]:
        names |= set(re.findall(r"^def (test_\w+)", path.read_text(encoding="utf-8"), re.MULTILINE))
    return names


def test_every_rule_has_a_test() -> None:
    missing = [
        r
        for r in [*rules_matrix.lad_rules(), *rules_matrix.stl_rules()]
        if r not in rules_matrix.RULE_TESTS and r not in rules_matrix.P1_RULES
    ]
    assert not missing, f"правила без теста: {missing}"


def test_matrix_points_to_existing_tests() -> None:
    names = _test_names()
    unknown = sorted({t for tests in rules_matrix.RULE_TESTS.values() for t in tests} - names)
    assert not unknown, f"в матрице несуществующие тесты: {unknown}"


def test_matrix_renders() -> None:
    text = rules_matrix.render()
    assert "| `stl.logic` |" in text and "| `sr_operand` |" in text
