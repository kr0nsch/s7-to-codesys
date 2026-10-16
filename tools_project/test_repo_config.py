"""Проверки настроек репозитория s7-to-codesys вместо трёх тестов шаблона (pyproject.toml, addopts).

Тесты шаблона сравнивают настройки с настройками самого шаблона; здесь проверяется, что проект
отличается от шаблона ровно так, как задумано и описано в docs/STATIC_ANALYSIS.md:

- st_lint.toml = умолчания st_lint.py плюс исключения src/*/Converted/* для правил оформления;
- tools/codesys/config.json: как у шаблона, кроме задач режима normal (они из OB корпуса) и ссылки на
  библиотеку Standard (плейсхолдер в library.libraries — сконвертированный код использует TON, R_TRIG, CTU);
- тесты шаблона, которые берут config.json репозитория за основу фикстур и рассчитаны на пустой
  library.libraries, выполняются против config.json без ссылки на Standard (template_shaped_config);
- статанализ iec_checker проходит через обёртку tools_project/iec_checker_gate.py.
"""

from __future__ import annotations

import copy
import importlib
import inspect
import json
import os
import re
import sys
from pathlib import Path
from types import ModuleType
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
    # единственное отличие ссылок на библиотеки от шаблона — Standard через плейсхолдер профиля
    assert data["libraries"]["standard"] == {
        "label": "Standard (плейсхолдер, разрешает профиль CODESYS)",
        "title": "Standard",
        "company": "System",
        "version": "*",
        "placeholder": "Standard",
    }
    assert data["library"]["libraries"] == ["standard"]
    assert data["modes"]["normal"]["libraries"] == []


def test_codesys_projects_reference_standard_and_counit(tmp_path: Path) -> None:
    """Замена test_cds.py::test_mode_config_resolves_libraries: Standard нужен проекту приложения, тестам и
    проверке всего пула объектов (cds.py library), coUnit — только тестовому проекту."""
    from cdshost import cli

    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    environ = {"USERPROFILE": str(tmp_path), "HOME": str(tmp_path), "LOCALAPPDATA": str(tmp_path)}
    s = cli.Settings(data, tmp_path, cli.make_getenv(environ, registry=False))
    assert [x["key"] for x in s.mode_config("normal")["libraries"]] == ["standard"]
    assert [x["key"] for x in s.mode_config("test")["libraries"]] == ["counit", "standard"]
    assert [x["key"] for x in s.other_libraries("normal")] == ["counit"]
    assert s.other_libraries("test") == []
    assert s.referenced_library_keys() == ["counit", "standard"]
    assert [x["key"] for x in s.library_config()["libraries"]] == ["standard"]
    standard = s.library_spec("standard")
    assert standard["placeholder"] == "Standard" and standard["install_from"] is None


# --- тесты шаблона, рассчитанные на config.json шаблона ------------------------------------------------

TEMPLATE_TESTS_DIR = REPO_ROOT / "tools" / "tests"
# Тесты шаблона берут config.json репозитория за основу фикстур и рассчитаны на пустой library.libraries:
# сравнивают описания библиотек со списком ключей, ждут ровно одну ссылку (coUnit), а поддельный
# репозиторий библиотек в тестах deps не знает Standard. Здесь они выполняются против config.json без
# ссылки на Standard; в pyproject.toml они исключены (--deselect), обоснование — docs/STATIC_ANALYSIS.md.
TEMPLATE_SHAPED_TESTS = [
    ("test_cds", "test_mode_config_resolves_libraries"),
    ("test_cds_library", "test_repo_library_config"),
    ("test_cds_library", "test_doc_keys_are_not_libraries"),
    ("test_cds_library", "test_import_step_carries_repository"),
    ("test_cds_library", "test_cmd_deps_builds_missing"),
    ("test_cds_library", "test_cmd_deps_rebuild_present"),
    ("test_cds_library", "test_cmd_deps_library_without_its_dependencies"),
]


def _template_test_module(name: str) -> ModuleType:
    if str(TEMPLATE_TESTS_DIR) not in sys.path:
        sys.path.insert(0, str(TEMPLATE_TESTS_DIR))
    return importlib.import_module(name)


def template_shaped_config() -> dict[str, Any]:
    """config.json репозитория без ссылки на Standard — в том виде, на который рассчитаны тесты шаблона."""
    data: dict[str, Any] = json.loads(CONFIG.read_text(encoding="utf-8"))
    del data["libraries"]["standard"]
    data["library"]["libraries"] = []
    return data


@pytest.mark.parametrize(("module_name", "test_name"), TEMPLATE_SHAPED_TESTS)
def test_template_tests_pass_with_template_shaped_config(
    module_name: str,
    test_name: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = _template_test_module(module_name)
    config = tmp_path / "template-config.json"
    config.write_text(json.dumps(template_shaped_config(), ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(module, "CONFIG", config)
    if hasattr(module, "repo_library_raw"):  # test_cds_library читает раздел library с диска сам
        monkeypatch.setattr(module, "repo_library_raw", lambda: template_shaped_config()["library"])
    func = getattr(module, test_name)
    work = tmp_path / "t"
    work.mkdir()
    fixtures: dict[str, Any] = {"tmp_path": work, "monkeypatch": monkeypatch, "capsys": capsys}
    params = inspect.signature(func).parameters
    assert set(params) <= set(fixtures), f"{test_name}: неизвестные фикстуры {set(params) - set(fixtures)}"
    func(**{name: fixtures[name] for name in params})


def test_template_shaped_tests_are_deselected_in_pyproject() -> None:
    text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    for module_name, test_name in TEMPLATE_SHAPED_TESTS:
        assert f"--deselect=tools/tests/{module_name}.py::{test_name}" in text, test_name


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
