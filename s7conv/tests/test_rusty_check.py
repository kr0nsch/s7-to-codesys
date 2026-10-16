"""Проверка сгенерированного ST компилятором RuSTy (plc --check) — ранний поиск синтаксических ошибок.

Фикстуры без намеренно неподдерживаемых конструкций конвертируются вместе с F_NormX/F_ScaleX, затем
tools/check/run_rusty.py проверяет результат. Пропускается, если RuSTy не установлен.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import pytest

from s7conv import pipeline as P
from s7conv.emitter import Options
from s7conv.tests.conftest import CORPUS, FIXTURES

run_rusty = pytest.importorskip("run_rusty")

GOOD = ["motor.scl", "analog.scl", "main.scl", "tags.csv"]


def _tool_available() -> bool:
    try:
        plc = run_rusty.find_compiler()
        run_rusty.find_stdlib(plc)
    except run_rusty.ToolMissing:
        return False
    return True


@pytest.mark.integration
@pytest.mark.skipif(not _tool_available(), reason="RuSTy (plc) не установлен")
def test_generated_st_passes_rusty_check(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    scl = tmp_path / "scl"
    scl.mkdir()
    for name in GOOD:
        shutil.copy(FIXTURES / name, scl / name)
    root = tmp_path / "out"
    result, _ = P.run(P.collect_inputs([str(scl)]))
    P.write_layout(result, root, support=True)
    build = tmp_path / "build"
    no_exclude = tmp_path / "no_exclude.txt"  # исключения репозитория (rusty_exclude.txt) к фикстурам не относятся
    no_exclude.write_text("", encoding="utf-8")
    code = run_rusty.main(
        [
            "--root",
            str(root),
            "--no-tests",
            "--exclude-file",
            str(no_exclude),
            "--out",
            str(build / "assembled"),
            "--log",
            str(build / "rusty.log"),
            "--json",
            str(build / "rusty.json"),
        ]
    )
    output = capsys.readouterr().out
    assert code == 0, output
    assert "error[" not in output


# Объявления, которых нет в stdlib RuSTy (в RuSTy TIME 64-битный), но которые есть в CODESYS
EXTRA_SHIM = """FUNCTION TIME_TO_DINT : DINT
VAR_INPUT
    IN : TIME;
END_VAR
END_FUNCTION
"""
# RuSTy убирает префикс GVL (замена R3): одинаковые имена в разных GVL для него — дубль.
# DB_Telegram (heartbeat — как и в DB_Plant) из кода не используется символьно (только %DB30/PEEK — TODO).
EXCLUDE = "DB_Telegram.st  # имя heartbeat есть и в DB_Plant: в CODESYS GVL с qualified_only, в RuSTy — дубль\n"


@pytest.mark.integration
@pytest.mark.skipif(not _tool_available(), reason="RuSTy (plc) не установлен")
@pytest.mark.skipif(not CORPUS.is_dir(), reason="корпус samples/scl/ отсутствует")
def test_converted_corpus_passes_rusty_check(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Весь сконвертированный корпус проходит plc --check: операторы с неперенесённым — закомментированы."""
    inputs = P.collect_inputs([str(CORPUS)])
    result, _ = P.run(inputs, Options(ob_config=P.load_ob_config(str(inputs.ob_config)) if inputs.ob_config else {}))
    root = tmp_path / "out"
    P.write_layout(result, root, support=True)
    # Ограничение RuSTy 1.0.6: адреса с одинаковым номером разного размера (%MW5 и %MD5 — в CODESYS это
    # байты 10–11 и 20–23) он считает одной «аппаратной» переменной (E037). Для проверки RuSTy AT убирается.
    markers = root / "src" / "GVLs" / "GVL_Markers.gvl.st"
    if markers.is_file():
        markers.write_text(re.sub(r" AT %M[XBWD][\d.]+", "", markers.read_text(encoding="utf-8")), encoding="utf-8")
    shims = tmp_path / "shims"
    shutil.copytree(run_rusty.DEFAULT_SHIMS, shims)
    (shims / "s7conv_extra.st").write_text(EXTRA_SHIM, encoding="utf-8")
    exclude = tmp_path / "exclude.txt"
    exclude.write_text(EXCLUDE, encoding="utf-8")
    build = tmp_path / "build"
    code = run_rusty.main(
        [
            "--root",
            str(root),
            "--no-tests",
            "--shims",
            str(shims),
            "--exclude-file",
            str(exclude),
            "--out",
            str(build / "assembled"),
            "--log",
            str(build / "rusty.log"),
            "--json",
            str(build / "rusty.json"),
        ]
    )
    output = capsys.readouterr().out
    assert code == 0, output


@pytest.mark.integration
@pytest.mark.skipif(not _tool_available(), reason="RuSTy (plc) не установлен")
def test_repository_sources_pass_rusty_with_shims(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Весь src/ и tests/ репозитория (сгенерированный, рукописный код и тесты) проходит plc --check.

    tools/check/rusty_exclude.txt исключает из run_rusty.py файлы с расхождениями диалектов и зависящие от них;
    здесь те же расхождения сняты иначе — объявлением TIME_TO_DINT и снятием AT у GVL_Markers, — и компилятор
    видит все файлы, кроме DB_Telegram (неоднозначное имя без квалификатора GVL).
    """
    from s7conv.layout import REPO_ROOT

    root = tmp_path / "repo"
    shutil.copytree(REPO_ROOT / "src", root / "src")
    shutil.copytree(REPO_ROOT / "tests", root / "tests")
    markers = root / "src" / "GVLs" / "Converted" / "GVL_Markers.gvl.st"
    markers.write_text(re.sub(r" AT %M[XBWD][\d.]+", "", markers.read_text(encoding="utf-8")), encoding="utf-8")
    shims = tmp_path / "shims"
    shutil.copytree(run_rusty.DEFAULT_SHIMS, shims)
    (shims / "s7conv_extra.st").write_text(EXTRA_SHIM, encoding="utf-8")
    exclude = tmp_path / "exclude.txt"
    exclude.write_text(EXCLUDE, encoding="utf-8")
    build = tmp_path / "build"
    code = run_rusty.main(
        [
            "--root",
            str(root),
            "--shims",
            str(shims),
            "--exclude-file",
            str(exclude),
            "--out",
            str(build / "assembled"),
            "--log",
            str(build / "rusty.log"),
            "--json",
            str(build / "rusty.json"),
        ]
    )
    output = capsys.readouterr().out
    assert code == 0, output
    summary = json.loads((build / "rusty.json").read_text(encoding="utf-8"))
    assert len(summary["files"]) >= 50 and "PRG_Main.st" in summary["files"] and "PRG_Tests.st" in summary["files"]
