"""Снапшот корпуса на уровне коммита: `s7conv build-corpus` воспроизводит закоммиченные файлы побайтно.

Закоммиченный результат — src/{DUTs,GVLs,POUs}/Converted/, docs/CONVERSION_REPORT.md, задачи в
tools/codesys/config.json, тесты сценариев tests/POUs/Scenarios/ и tests/POUs/PRG_Tests/. После
осознанного изменения конвертера, корпуса или сценариев: `python -m s7conv build-corpus` и просмотр
диффа в git.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from s7conv import corpus as C
from s7conv import mapping as M
from s7conv.cli import main
from s7conv.layout import L
from s7conv.tests.conftest import REPO_ROOT


@pytest.fixture(scope="module")
def built() -> C.CorpusBuild:
    return C.build(REPO_ROOT)


def test_build_corpus_reproduces_repository(built: C.CorpusBuild) -> None:
    diff = C.compare(built, REPO_ROOT)
    assert diff.clean, (
        "результат build-corpus отличается от репозитория — python -m s7conv build-corpus:\n"
        f"изменены: {diff.changed}\nнет в репозитории: {diff.missing}\nлишние: {diff.stale}"
    )


def test_build_corpus_check_cli(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["build-corpus", "--check"]) == 0
    assert "совпадает" in capsys.readouterr().out


def test_converted_objects_are_in_converted_folder(built: C.CorpusBuild) -> None:
    for obj in built.result.objects:
        assert obj.folder == [C.FOLDER], obj.name
    src_files = [rel for rel in built.files if rel.startswith("src/")]
    assert src_files and all(f"/{C.FOLDER}/" in rel for rel in src_files)


def test_corpus_uses_s7compat_timers_and_support_is_hand_written(built: C.CorpusBuild) -> None:
    assert built.result.options.timers == M.S7COMPAT
    assert {"FB_S7Ton", "FB_S7Tof", "FB_S7Tp", "F_S7Now", "GVL_S7Clock", "F_NormX", "F_ScaleX"} <= built.result.support
    text = "\n".join(t for rel, t in built.files.items() if rel.startswith("src/"))
    assert ": TON;" not in text and ": TOF;" not in text and ": TP;" not in text
    assert ": FB_S7Ton;" in text
    # объекты поддержки не генерируются
    assert not any("/S7Compat/" in rel for rel in built.files)


def test_whole_layout_is_valid(built: C.CorpusBuild) -> None:
    for subdir in ("src", "tests"):
        scan = L.scan(str(REPO_ROOT), subdir)
        assert scan.ok, [i.format() for i in scan.issues]


def test_config_tasks_come_from_obs(built: C.CorpusBuild) -> None:
    tasks = C.config_tasks(built.result)
    assert tasks[0] == {"name": "MainTask", "interval_ms": 10, "priority": 15, "pous": ["PRG_Startup", "PRG_Main"]}
    assert {"name": "Task_OB30", "interval_ms": 100, "priority": 1, "pous": ["PRG_Cyclic_interrupt"]} in tasks
    data = json.loads(built.files[C.CONFIG_REL])
    assert data["modes"]["normal"]["tasks"] == tasks
    assert data["modes"]["test"]["tasks"][0]["pous"] == ["PRG_Tests"]


CONFIG_SAMPLE = """{
  "_doc": ["x"],
  "modes": {
    "normal": {
      "tasks": [{"name": "MainTask", "interval_ms": 20, "pous": ["PRG_Main"]}],
      "libraries": []
    },
    "test": {
      "tasks": [{"name": "TestTask", "interval_ms": 10, "pous": ["PRG_Tests"]}],
      "libraries": ["counit"]
    }
  },
  "tasks": "не трогать: ключ верхнего уровня с тем же именем"
}
"""


def test_update_config_tasks_replaces_only_normal_tasks() -> None:
    tasks = [{"name": "MainTask", "interval_ms": 10, "priority": 15, "pous": ["PRG_Startup", "PRG_Main"]}]
    text = C.update_config_tasks(CONFIG_SAMPLE, tasks)
    data = json.loads(text)
    assert data["modes"]["normal"]["tasks"] == tasks
    assert data["modes"]["test"]["tasks"][0]["name"] == "TestTask"
    assert data["tasks"].startswith("не трогать")
    before, after = CONFIG_SAMPLE.splitlines(), text.splitlines()
    assert before[:4] == after[:4] and before[-8:] == after[-8:]
    assert C.update_config_tasks(text, tasks) == text  # идемпотентно


def test_update_config_tasks_errors() -> None:
    with pytest.raises(C.CorpusError):
        C.update_config_tasks("{", [])
    with pytest.raises(C.CorpusError):
        C.update_config_tasks('{"modes": {}}', [])


def _mini_repo(tmp: Path) -> Path:
    """Копия того, что нужно сборке: корпус, сценарии, рукописные src/ и tests/, config.json."""
    root = tmp / "repo"
    for rel in ("samples/scl", "samples/lang", "scenarios"):
        shutil.copytree(REPO_ROOT / rel, root / rel, ignore=shutil.ignore_patterns("__pycache__", "reference"))
    shutil.copytree(REPO_ROOT / "src", root / "src", ignore=shutil.ignore_patterns(C.FOLDER))
    for suites in ("S7Compat", "Graph"):  # рукописные наборы (PRG_Tests объявляет и их)
        shutil.copytree(REPO_ROOT / "tests" / "POUs" / suites, root / "tests" / "POUs" / suites)
    (root / "tools" / "codesys").mkdir(parents=True)
    shutil.copy(REPO_ROOT / C.CONFIG_REL, root / C.CONFIG_REL)
    (root / "docs").mkdir()
    return root


def test_write_into_fresh_copy_then_check_is_clean(tmp_path: Path) -> None:
    root = _mini_repo(tmp_path)
    stale = root / "src" / "POUs" / C.FOLDER / "FB_Old" / "FB_Old.decl.st"
    stale.parent.mkdir(parents=True)
    stale.write_text("FUNCTION_BLOCK FB_Old\n", encoding="utf-8")
    first = C.build(root)
    diff = C.write(first, root, html=False)
    assert diff.stale == ["src/POUs/Converted/FB_Old/FB_Old.decl.st"]
    assert not stale.parent.exists()
    assert C.compare(C.build(root), root).clean
    # результат копии совпадает с репозиторием (сборка не зависит от расположения корня)
    for rel, text in first.files.items():
        if rel != C.CONFIG_REL:
            assert (REPO_ROOT / rel).read_bytes() == text.encode("utf-8"), rel


def test_missing_support_object_is_an_error(tmp_path: Path) -> None:
    root = _mini_repo(tmp_path)
    shutil.rmtree(root / "src" / "POUs" / "S7Compat" / "FB_S7Ton")
    with pytest.raises(C.CorpusError, match="FB_S7Ton"):
        C.build(root)
    assert main(["build-corpus", "--root", str(root), "--check"]) == 2


def test_name_clash_with_hand_written_object_is_an_error(tmp_path: Path) -> None:
    root = _mini_repo(tmp_path)
    clash = root / "src" / "POUs" / "PRG_Main"
    clash.mkdir(parents=True)
    (clash / "PRG_Main.decl.st").write_text("PROGRAM PRG_Main\n", encoding="utf-8")
    (clash / "PRG_Main.impl.st").write_text(";\n", encoding="utf-8")
    with pytest.raises(C.CorpusError, match="PRG_Main"):
        C.build(root)
