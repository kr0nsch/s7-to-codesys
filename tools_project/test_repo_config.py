"""Проверки настроек репозитория s7-to-codesys вместо трёх тестов шаблона (pyproject.toml, addopts).

Тесты шаблона сравнивают настройки с настройками самого шаблона; здесь проверяется, что проект
отличается от шаблона ровно так, как задумано и описано в docs/STATIC_ANALYSIS.md:

- st_lint.toml = умолчания st_lint.py плюс исключения src/*/Converted/* для правил оформления;
- tools/codesys/config.json: как у шаблона, кроме задач режима normal — они из OB корпуса;
- статанализ iec_checker проходит через обёртку tools_project/iec_checker_gate.py.
"""

from __future__ import annotations

import copy
import json
import os
import re
from pathlib import Path
from typing import Any

import pytest

import iec_checker_gate as G
import run_iec_checker
import st_lint

REPO_ROOT = Path(__file__).resolve().parents[1]
CONVERTED = "src/*/Converted/*"
# Правила оформления, снятые с кода, который генерирует s7conv (обоснование — шапка st_lint.toml)
EXEMPT_RULES = ("STL004", "STL006", "STL007", "STL008", "STL011")


def test_st_lint_config_differs_from_template_only_by_converted_exemptions() -> None:
    expected = copy.deepcopy(st_lint.DEFAULT_CONFIG)
    for rule in EXEMPT_RULES:
        cfg = expected["rules"].setdefault(rule, {})
        cfg["exclude"] = [*cfg.get("exclude", []), CONVERTED]
    assert st_lint.load_config(st_lint.DEFAULT_CONFIG_PATH) == expected


def test_st_lint_still_checks_format_rules_in_converted() -> None:
    config = st_lint.load_config(st_lint.DEFAULT_CONFIG_PATH)
    assert config["lint"]["exclude"] == []
    for rule in ("STL001", "STL002", "STL003", "STL005", "STL009", "STL010", "STL012"):
        assert CONVERTED not in config["rules"].get(rule, {}).get("exclude", []), rule
        assert config["severity"][rule] == "error"


CONFIG = REPO_ROOT / "tools" / "codesys" / "config.json"


def test_codesys_config_is_template_config_with_corpus_tasks() -> None:
    from s7conv import corpus as C

    text = CONFIG.read_text(encoding="utf-8")
    data: dict[str, Any] = json.loads(text)
    user = os.environ.get("USERNAME") or os.environ.get("USER")
    assert not user or f"/{user.lower()}/" not in text.lower().replace("\\\\", "/")
    assert "C:\\\\Users" not in text and "C:/Users" not in text
    assert data["device"]["type"]["default"] == 4096
    assert data["device"]["id"]["default"] == "0000 0001"
    assert data["modes"]["test"]["tasks"] == [{"name": "TestTask", "interval_ms": 10, "pous": ["PRG_Tests"]}]
    assert data["modes"]["test"]["libraries"] == ["counit"]
    built = C.build(REPO_ROOT)
    assert data["modes"]["normal"]["tasks"] == C.config_tasks(built.result)
    main = data["modes"]["normal"]["tasks"][0]
    assert main["name"] == "MainTask" and main["pous"][-1] == "PRG_Main"


# --- обёртка iec_checker ------------------------------------------------------------------------------


def _report(*findings: dict[str, Any], unused: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {"findings": list(findings), "unused_allow": unused or [], "summary": {}}


def _gap(file: str, match: str) -> G.Gap:
    return G.Gap(file, re.compile(match), "причина")


def test_gate_accepts_only_listed_parser_gaps(tmp_path: Path) -> None:
    src = tmp_path / "src" / "POUs" / "FB_A"
    src.mkdir(parents=True)
    (src / "FB_A.impl.st").write_text("x := 1;\nbuf[i].code := 0;\n", encoding="utf-8")
    known = {"id": "ParserError", "status": "error", "source": "src/POUs/FB_A/FB_A.impl.st", "source_line": 2}
    other = {"id": "ParserError", "status": "error", "source": "src/POUs/FB_A/FB_A.impl.st", "source_line": 1}
    allowed = {"id": "PLCOPEN-CP3", "status": "allowed", "source": "src/POUs/FB_A/FB_A.decl.st"}
    result = G.evaluate(_report(known, allowed), [_gap("src/POUs/FB_A/FB_A.impl.st", r"\]\.\w")], tmp_path, True)
    assert result.ok and len(result.known) == 1 and result.known[0]["line_text"] == "buf[i].code := 0;"
    result = G.evaluate(_report(other), [_gap("src/POUs/FB_A/FB_A.impl.st", r"\]\.\w")], tmp_path, True)
    assert not result.ok and result.errors == [other] and len(result.stale_gaps) == 1


def test_gate_fails_on_unjustified_finding_and_unused_allow(tmp_path: Path) -> None:
    finding = {"id": "PLCOPEN-L17", "status": "error", "source": "src/POUs/FB_A/FB_A.impl.st", "source_line": 3}
    assert G.evaluate(_report(finding), [], tmp_path, True).errors == [finding]
    unused = [{"id": "X", "file": "src/*"}]
    assert not G.evaluate(_report(unused=unused), [], tmp_path, True).ok
    assert G.evaluate(_report(unused=unused), [], tmp_path, False).ok


def test_gate_gap_file_is_valid_and_points_to_existing_files() -> None:
    gaps = G.load_gaps(G.DEFAULT_GAPS)
    assert gaps
    for gap in gaps:
        assert (REPO_ROOT / gap.file).is_file(), gap.file
        text = (REPO_ROOT / gap.file).read_text(encoding="utf-8")
        assert any(gap.match.search(line) for line in text.splitlines()), gap.file


def test_gate_rejects_bad_gap_file(tmp_path: Path) -> None:
    bad = tmp_path / "gaps.toml"
    bad.write_text('[[gap]]\nfile = "a"\nmatch = "("\nreason = "r"\n', encoding="utf-8")
    with pytest.raises(G.GapError):
        G.load_gaps(bad)
    bad.write_text('[[gap]]\nfile = "a"\nmatch = "x"\n', encoding="utf-8")
    with pytest.raises(G.GapError):
        G.load_gaps(bad)
    assert G.main(["--gaps", str(bad)]) == G.EXIT_CONFIG


def _iec_checker_available() -> bool:
    try:
        run_iec_checker.find_binary()
    except run_iec_checker.ToolMissing:
        return False
    return True


@pytest.mark.integration
@pytest.mark.skipif(not _iec_checker_available(), reason="iec_checker не найден")
def test_repository_sources_pass_iec_checker_gate(tmp_path: Path) -> None:
    """Замена test_integration_repository_sources шаблона: src/ и tests/ через обёртку, каждое обоснование
    и каждая запись о пробеле разборщика используются."""
    out = tmp_path / "gate.json"
    assert G.main(["--root", str(REPO_ROOT), "--json", str(out)]) == G.EXIT_OK
    summary = json.loads(out.read_text(encoding="utf-8"))
    assert summary["ok"] and summary["errors"] == 0 and summary["unused_allow"] == []
    assert {g["source"] for g in summary["known_parser_gaps"]} == {g.file for g in G.load_gaps(G.DEFAULT_GAPS)}
