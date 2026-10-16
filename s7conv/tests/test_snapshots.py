"""Снапшоты сгенерированного ST по собственным фикстурам (настройки конвертера по умолчанию).

Снапшот — весь результат `s7conv convert` (раскладка src/, tasks.json) и отчёт Markdown. Снапшот корпуса
samples/scl/ — закоммиченный результат `s7conv build-corpus` в src/*/Converted/ (test_corpus_build.py).
Обновление после осознанного изменения эмиттера или корпуса:

    UPDATE_SNAPSHOTS=1 python -m pytest s7conv/tests/test_snapshots.py

и просмотр диффа в git.
"""

from __future__ import annotations

import difflib
import json
import os
import shutil
from pathlib import Path

import pytest

from s7conv import pipeline as P
from s7conv import report as R
from s7conv.emitter import Options
from s7conv.tests.conftest import CORPUS, FIXTURES, REPO_ROOT, SNAPSHOTS

UPDATE = os.environ.get("UPDATE_SNAPSHOTS") == "1"


def render_tree(inputs_dir: Path, out: Path) -> dict[str, str]:
    """Сконвертировать каталог и вернуть {путь: текст} результата и отчёта."""
    inputs = P.collect_inputs([str(inputs_dir)])
    ob_config = P.load_ob_config(str(inputs.ob_config)) if inputs.ob_config else {}
    result, _files = P.run(inputs, Options(ob_config=ob_config))
    P.write_layout(result, out)
    label = inputs_dir.relative_to(REPO_ROOT).as_posix()
    files = {
        p.relative_to(out).as_posix(): p.read_text(encoding="utf-8") for p in sorted(out.rglob("*")) if p.is_file()
    }
    files["CONVERSION_REPORT.md"] = R.render_markdown(result, [label])
    return files


def compare(actual: dict[str, str], snapshot_dir: Path) -> None:
    if UPDATE:
        if snapshot_dir.exists():
            shutil.rmtree(snapshot_dir)
        for rel, text in actual.items():
            target = snapshot_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(text.encode("utf-8"))
        return
    assert snapshot_dir.is_dir(), f"нет снапшота {snapshot_dir}: запустите с UPDATE_SNAPSHOTS=1"
    expected = {
        p.relative_to(snapshot_dir).as_posix(): p.read_bytes().decode("utf-8")
        for p in sorted(snapshot_dir.rglob("*"))
        if p.is_file()
    }
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    changed = sorted(k for k in set(expected) & set(actual) if expected[k] != actual[k])
    if missing or extra or changed:
        diffs: list[str] = []
        for rel in changed[:3]:
            diffs.extend(
                difflib.unified_diff(
                    expected[rel].splitlines(),
                    actual[rel].splitlines(),
                    f"snapshot/{rel}",
                    f"actual/{rel}",
                    lineterm="",
                )
            )
        pytest.fail(
            "снапшот не совпал (UPDATE_SNAPSHOTS=1 — обновить):\n"
            f"нет в результате: {missing}\nлишние: {extra}\nизменены: {changed}\n" + "\n".join(diffs[:200])
        )


@pytest.fixture
def in_repo_root(monkeypatch: pytest.MonkeyPatch) -> None:
    """Пути в шапках и отчёте — от корня репозитория, как при запуске из него."""
    monkeypatch.chdir(REPO_ROOT)


@pytest.mark.usefixtures("in_repo_root")
def test_fixture_snapshots(tmp_path: Path) -> None:
    compare(render_tree(FIXTURES, tmp_path / "out"), SNAPSHOTS / "fixtures")


@pytest.mark.usefixtures("in_repo_root")
@pytest.mark.skipif(not CORPUS.is_dir(), reason="корпус samples/scl/ отсутствует")
def test_corpus_converts_without_crash_and_parses(tmp_path: Path) -> None:
    """Весь корпус проходит конвертер; результат — корректная раскладка; разбор без «потерянных» блоков."""
    from s7conv.layout import L

    inputs = P.collect_inputs([str(CORPUS)])
    files = P.parse_inputs(inputs)
    assert len(files) == len(inputs.scl) >= 15
    raw_blocks = [b for sf in files for b in sf.blocks if getattr(b, "reason", None)]
    assert not raw_blocks, raw_blocks
    result, _ = P.run(inputs, Options(ob_config=P.load_ob_config(str(inputs.ob_config)) if inputs.ob_config else {}))
    out = tmp_path / "out"
    P.write_layout(result, out, support=True)
    scan = L.scan(str(out), "src")
    assert scan.ok, [i.format() for i in scan.issues]
    tot = R.totals(R.all_items(result))
    assert tot.total > 500 and tot.auto / tot.total > 0.8
    tasks = json.loads((out / "tasks.json").read_text(encoding="utf-8"))
    assert tasks["tasks"][0]["name"] == "MainTask"
