"""Командная строка: convert, report, check, коды выхода, --help, ошибки входа."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from s7conv import __version__
from s7conv.cli import EXIT_OK, EXIT_THRESHOLD, EXIT_USAGE, main
from s7conv.layout import L
from s7conv.tests.conftest import FIXTURES, REPO_ROOT

GOOD = ["motor.scl", "analog.scl", "main.scl", "tags.csv"]


@pytest.fixture
def good_dir(tmp_path: Path) -> Path:
    """Каталог с исходниками без неподдерживаемых конструкций."""
    target = tmp_path / "scl"
    target.mkdir()
    for name in GOOD:
        shutil.copy(FIXTURES / name, target / name)
    return target


def test_convert_writes_layout_tasks_and_reports(
    good_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "out"
    md = tmp_path / "rep.md"
    html = tmp_path / "rep.html"
    code = main(
        [
            "convert",
            str(good_dir),
            "--out",
            str(out),
            "--emit-support",
            "--report-md",
            str(md),
            "--report-html",
            str(html),
        ]
    )
    assert code == EXIT_OK
    assert "конструкций" in capsys.readouterr().out
    scan = L.scan(str(out), "src")
    assert scan.ok, [i.format() for i in scan.issues]
    names = {o.name for o in scan.objects}
    assert {"FB_Motor", "FC_ScaleAnalog", "PRG_Main", "GVL_IO", "GVL_InstanceDBs", "F_NormX", "F_ScaleX"} <= names
    tasks = json.loads((out / "tasks.json").read_text(encoding="utf-8"))
    assert tasks["generator"] == f"s7conv {__version__}"
    assert [t["name"] for t in tasks["tasks"]] == ["MainTask", "Task_100ms"]
    assert md.read_text(encoding="utf-8").startswith("# Отчёт конвертации")
    assert html.read_text(encoding="utf-8").startswith("<!doctype html>")


def test_convert_clean_removes_stale_files(good_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    stale = out / "src" / "POUs" / "FB_Old" / "FB_Old.decl.st"
    stale.parent.mkdir(parents=True)
    stale.write_text("FUNCTION_BLOCK FB_Old\n", encoding="utf-8")
    assert main(["convert", str(good_dir), "--out", str(out), "--clean", "-q"]) == EXIT_OK
    assert not stale.exists()


def test_convert_folder_option(good_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    assert main(["convert", str(good_dir), "--out", str(out), "--folder", "Migrated", "-q"]) == EXIT_OK
    assert (out / "src" / "POUs" / "Migrated" / "FB_Motor" / "FB_Motor.decl.st").is_file()


def test_fail_on_thresholds(tmp_path: Path) -> None:
    out = tmp_path / "out"
    src = str(FIXTURES / "unsupported.scl")
    assert main(["convert", src, "--out", str(out), "-q"]) == EXIT_OK
    assert main(["convert", src, "--out", str(out), "-q", "--fail-on", "todo"]) == EXIT_THRESHOLD
    motor = str(FIXTURES / "motor.scl")  # без TODO, но с пометками проверки (VAR RETAIN в ФБ)
    assert main(["convert", motor, "--out", str(out), "-q", "--fail-on", "todo"]) == EXIT_OK
    assert main(["convert", motor, "--out", str(out), "-q", "--fail-on", "check"]) == EXIT_THRESHOLD
    clean = tmp_path / "clean.scl"
    clean.write_text(
        'FUNCTION "F_Add" : Int\n VAR_INPUT\n  a : Int;\n END_VAR\nBEGIN\n #F_Add := #a + 1;\nEND_FUNCTION\n', "utf-8"
    )
    assert main(["convert", str(clean), "--out", str(out), "-q", "--fail-on", "check"]) == EXIT_OK


def test_report_command_defaults(good_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert main(["report", str(good_dir), "-q"]) == EXIT_OK
    assert (tmp_path / "docs" / "CONVERSION_REPORT.md").is_file()
    assert (tmp_path / "build" / "report.html").is_file()


def test_report_only_html(good_dir: Path, tmp_path: Path) -> None:
    html = tmp_path / "only.html"
    assert main(["report", str(good_dir), "--html", str(html), "-q"]) == EXIT_OK
    assert html.is_file() and not (tmp_path / "docs").exists()


def test_check_command(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["check", str(FIXTURES / "motor.scl")]) == EXIT_OK
    assert "без ошибок" in capsys.readouterr().out
    assert main(["check", str(FIXTURES / "unsupported.scl")]) == EXIT_THRESHOLD
    out = capsys.readouterr().out
    assert "unsupported.scl:30:" in out and "ошибок разбора 3" in out


def test_input_errors(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["convert", str(tmp_path / "missing"), "--out", str(tmp_path)]) == EXIT_USAGE
    assert "не найден" in capsys.readouterr().err
    empty = tmp_path / "empty"
    empty.mkdir()
    assert main(["check", str(empty)]) == EXIT_USAGE
    bad = tmp_path / "bad.json"
    bad.write_text("[1, 2", encoding="utf-8")
    code = main(["convert", str(FIXTURES / "motor.scl"), "--out", str(tmp_path / "o"), "--ob-config", str(bad)])
    assert code == EXIT_USAGE


def test_usage_errors_and_help(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == EXIT_USAGE
    assert main(["convert", "x.scl"]) == EXIT_USAGE  # нет --out
    assert main(["--help"]) == EXIT_OK
    out = capsys.readouterr().out
    assert "примеры:" in out and "s7conv convert samples/scl --out build/converted" in out
    assert main(["--version"]) == EXIT_OK


def test_ob_config_is_found_in_input_directory(good_dir: Path, tmp_path: Path) -> None:
    (good_dir / "ob_config.json").write_text(
        json.dumps({"Cyclic interrupt 100ms": {"number": 35, "kind": "cyclic", "interval_ms": 50}}), encoding="utf-8"
    )
    out = tmp_path / "out"
    assert main(["convert", str(good_dir), "--out", str(out), "-q"]) == EXIT_OK
    tasks = json.loads((out / "tasks.json").read_text(encoding="utf-8"))
    assert [(t["name"], t["interval_ms"]) for t in tasks["tasks"]] == [("MainTask", 10), ("Task_OB35", 50)]


def test_cp1251_and_crlf_input(tmp_path: Path) -> None:
    src = tmp_path / "win.scl"
    text = 'FUNCTION_BLOCK "FB_W"\r\n// комментарий\r\nVAR\r\n   a : Bool;\r\nEND_VAR\r\nBEGIN\r\n#a := TRUE;\r\nEND_FUNCTION_BLOCK\r\n'
    src.write_bytes(text.encode("cp1251"))
    out = tmp_path / "out"
    assert main(["convert", str(src), "--out", str(out), "-q"]) == EXIT_OK
    impl = (out / "src" / "POUs" / "FB_W" / "FB_W.impl.st").read_bytes()
    assert impl == b"a := TRUE;\n"


def test_module_entry_point() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "s7conv", "--version"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert proc.returncode == 0 and __version__ in proc.stdout
