"""tools_project/cds_plcopen.py без CODESYS: входы, раскладка для импорта, задание из шагов шаблона."""

from __future__ import annotations

from pathlib import Path

import pytest

import cds_plcopen as CP  # tools_project/cds_plcopen.py (каталог теста pytest добавляет в sys.path)
from cdshost import cli


def test_default_inputs_have_shared_suites() -> None:
    files = CP.find_inputs([])
    assert [f.name for f in files] == ["FB_BackwashGraph.xml"]
    assert [d.name for d in CP.suite_dirs(files)] == ["FB_BackwashGraph_SeqTest"]


def test_missing_input_or_suite_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(CP.PlcopenError, match="нет файлов"):
        CP.find_inputs([str(tmp_path / "FB_None.xml")])
    lonely = tmp_path / "FB_Lonely.xml"
    lonely.write_text("<project />", encoding="utf-8")
    with pytest.raises(CP.PlcopenError, match="нет набора tests/POUs/Graph/FB_Lonely_SeqTest"):
        CP.suite_dirs([lonely])


def test_layout_has_suites_and_own_prg_tests_only(tmp_path: Path) -> None:
    layout = tmp_path / "layout"
    suites = CP.suite_dirs(CP.find_inputs([]))
    CP.make_layout(layout, suites)
    assert (layout / "src").is_dir() and not any((layout / "src").iterdir())
    suite = layout / "tests" / "POUs" / "Graph" / "FB_BackwashGraph_SeqTest"
    assert (suite / "FB_BackwashGraph_SeqTest.decl.st").is_file()
    decl = (layout / "tests" / "POUs" / "PRG_Tests" / "PRG_Tests.decl.st").read_text(encoding="utf-8")
    impl = (layout / "tests" / "POUs" / "PRG_Tests" / "PRG_Tests.impl.st").read_text(encoding="utf-8")
    assert "fbFB_BackwashGraph_SeqTest : FB_BackwashGraph_SeqTest;" in decl
    assert impl == "coUnit.RUN();\nxAllFinished := fbFB_BackwashGraph_SeqTest.AreAllTestsFinished();\n"


def test_job_imports_layout_then_plcopen_then_builds_and_tests(tmp_path: Path) -> None:
    settings = cli.make_settings(CP.REPO)
    files = CP.find_inputs([])
    steps = CP.steps_for(settings, "test", tmp_path / "layout", tmp_path, files, None)
    assert [s["action"] for s in steps] == ["import", "plcopen", "build", "test"]
    imp, plc, build, test = steps
    assert imp["repo_root"] == str(tmp_path / "layout") and imp["clean"] is True and imp["with_tests"] is True
    assert plc["files"] == [str(f) for f in files] and plc["project"] == imp["project"] == build["project"]
    assert imp["project"].endswith("-plcopen.project")
    assert test["results"] == str(tmp_path / "test-results.json")
    assert [s["action"] for s in CP.steps_for(settings, "check", tmp_path, tmp_path, files, None)] == [
        "import",
        "plcopen",
        "build",
    ]


def test_check_layout_calls_every_block_without_counit(tmp_path: Path) -> None:
    """check собирает вариант SFC на любом устройстве (R500, ПЛК210): PRG_SfcCheck в MainTask, без coUnit."""
    layout = tmp_path / "layout"
    CP.make_check_layout(layout, ["FB_BackwashGraph"])
    prg = layout / "src" / "POUs" / "PRG_SfcCheck"
    assert "fbFB_BackwashGraph : FB_BackwashGraph;" in (prg / "PRG_SfcCheck.decl.st").read_text(encoding="utf-8")
    assert (prg / "PRG_SfcCheck.impl.st").read_text(encoding="utf-8") == "fbFB_BackwashGraph();\n"
    assert not (layout / "tests").exists()
    settings = cli.make_settings(CP.REPO)
    imp = CP.steps_for(settings, "check", layout, tmp_path, CP.find_inputs([]), None)[0]
    assert imp["with_tests"] is False
    (task,) = imp["mode_config"]["tasks"]
    assert (task["name"], task["pous"]) == ("MainTask", ["PRG_SfcCheck"])
    assert all(lib["key"] != "counit" for lib in imp["mode_config"]["libraries"])
