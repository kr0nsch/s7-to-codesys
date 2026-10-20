"""Корпус всех языков в репозитории: Lang/Converted, суффикс GVL, уникальность имён, отчёт по языкам, наборы."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from s7conv import corpus as C
from s7conv import testgen as TG
from s7conv.layout import L
from s7conv.tests.conftest import REPO_ROOT


@pytest.fixture(scope="module")
def built() -> C.CorpusBuild:
    return C.build(REPO_ROOT)


def test_language_corpus_goes_to_converted_lang(built: C.CorpusBuild) -> None:
    assert built.lang_result is not None
    for obj in built.lang_result.objects:
        assert obj.folder == list(C.LANG_FOLDERS), obj.name
    src = [rel for rel in built.lang_files if rel.startswith("src/")]
    assert src and all(f"/{C.LANG_FOLDER}/" in rel for rel in src)
    names = {o.name for o in built.lang_result.objects}
    assert {"FB_StarterLad", "FB_StarterFbd", "FB_StarterStl", "FB_StarterScl", "FB_PumpInterlockLad"} <= names
    assert {"FC_ClampPctLad", "DB_Process", "UDT_Valve"} <= names


def test_generated_globals_get_lang_suffix() -> None:
    """--global-suffix: экземплярные DB и теги второго корпуса не сталкиваются с GVL корпуса SCL."""
    from s7conv.emitter import Options
    from s7conv.tests.conftest import convert_texts

    src = 'DATA_BLOCK "IDB_T" "FB_T"\nBEGIN\nEND_DATA_BLOCK\nFUNCTION_BLOCK "FB_T"\nVERSION : 0.1\nBEGIN\nEND_FUNCTION_BLOCK\n'
    r = convert_texts({"t.scl": src}, options=Options(global_suffix="_Lang"))
    assert "GVL_InstanceDBs_Lang" in r.objects
    assert "GVL_InstanceDBs" not in r.objects


def test_names_unique_across_corpora(built: C.CorpusBuild) -> None:
    C.check_names_unique(REPO_ROOT, built)  # не бросает


def test_names_clash_is_reported(tmp_path: Path, built: C.CorpusBuild) -> None:
    """Член GVL нового корпуса с именем члена GVL корпуса SCL — ошибка сборки (RuSTy E004)."""
    assert built.lang_result is not None
    gvl = next(o for o in built.lang_result.objects if o.name == "DB_Process")
    clash = L.StObject(L.KIND_GVL, "DB_Process", gvl.decl.replace("xPumpRun", "estopOk"), folder=list(C.LANG_FOLDERS))
    objects = [clash if o is gvl else o for o in built.lang_result.objects]
    broken = C.CorpusBuild(files={}, result=built.result, tests=built.tests, html="")
    broken.lang_result = type(built.lang_result)(**{**built.lang_result.__dict__, "objects": objects})
    with pytest.raises(C.CorpusError, match="estopOk"):
        C.check_names_unique(REPO_ROOT, broken)


def test_language_report_has_languages_section(built: C.CorpusBuild) -> None:
    text = built.lang_files[C.LANG_REPORT_REL]
    assert text.startswith("# Отчёт конвертации S7 (LAD, FBD, STL, SCL) → ST CODESYS")
    assert "## По языкам" in text
    for lang in ("| LAD | элемент", "| LAD | сеть", "| FBD | элемент", "| STL | инструкция"):
        assert lang in text
    assert "(FB_PumpInterlockLad.xml, сеть" in "".join(built.lang_files.values()) or "сеть" in text
    # отчёт корпуса SCL 1.0.0 — без раздела по языкам
    assert "## По языкам" not in built.files[C.REPORT_REL]


def test_language_scenario_suites_are_in_own_folder_and_prg_tests(built: C.CorpusBuild) -> None:
    """Наборы корпуса всех языков — в ScenariosLang; PRG_Tests объявляет их (иначе coUnit их не выполнит:
    экземпляры в GVL, на которую не ссылается задача, в сборку CODESYS не попадают — проверено в Control Win)."""
    assert built.lang_tests is not None
    suites = sorted(s.obj.name for s in built.lang_tests.suites)
    assert suites == sorted(
        f"{b}{TG.SUITE_SUFFIX}"
        for b in ("FB_StarterLad", "FB_StarterFbd", "FB_StarterStl", "FB_StarterScl", "FB_PumpInterlockLad")
    )
    assert all(s.obj.folder == [TG.LANG_SCENARIO_FOLDER] for s in built.lang_tests.suites)
    prg = built.files["tests/POUs/PRG_Tests/PRG_Tests.decl.st"]
    for name in suites:
        assert f": {name};  // сценарии CSV всех языков (сгенерировано)" in prg
    assert built.tests.hand_written and not set(suites) & set(built.tests.hand_written)


def test_corpus_without_language_samples_ignores_lang_dirs(tmp_path: Path) -> None:
    """Копия с одним корпусом SCL (как сборка своего проекта): каталоги Lang/Converted не управляются."""
    root = tmp_path / "repo"
    for rel in ("samples/scl", "scenarios"):
        shutil.copytree(REPO_ROOT / rel, root / rel, ignore=shutil.ignore_patterns("__pycache__", "reference", "lang"))
    shutil.copytree(REPO_ROOT / "src", root / "src", ignore=shutil.ignore_patterns(C.FOLDER))
    shutil.copytree(REPO_ROOT / "tests" / "POUs" / "S7Compat", root / "tests" / "POUs" / "S7Compat")
    (root / "tools" / "codesys").mkdir(parents=True)
    shutil.copy(REPO_ROOT / C.CONFIG_REL, root / C.CONFIG_REL)
    first = C.build(root)
    assert first.lang_result is None and not first.lang_files
    C.write(first, root, html=False)
    assert C.compare(C.build(root), root).clean


def test_own_xml_without_scenarios_builds_code_and_report(tmp_path: Path) -> None:
    """Копия со своим блоком SimaticML и без сценариев CSV: код и отчёт есть, наборов ScenariosLang нет."""
    from s7conv.tests.test_corpus_build import _mini_repo

    root = _mini_repo(tmp_path)
    for path in (root / "samples" / "lang").glob("*.xml"):
        if path.name != "FB_StarterStl.xml":
            path.unlink()
    shutil.rmtree(root / "scenarios" / "lang")
    first = C.build(root)
    assert first.lang_result is not None
    assert {o.name for o in first.lang_result.objects} == {"FB_StarterStl"}
    assert C.LANG_REPORT_REL in first.lang_files
    assert not any(f"/{TG.LANG_SCENARIO_FOLDER}/" in rel for rel in first.all_files)
    C.write(first, root, html=False)
    assert C.compare(C.build(root), root).clean


def test_removed_language_corpus_cleans_generated_lang_dirs(tmp_path: Path) -> None:
    """samples/lang без *.xml (демокорпус убран): сгенерированные Lang/Converted и ScenariosLang удаляются."""
    from s7conv.tests.test_corpus_build import _mini_repo

    root = _mini_repo(tmp_path)
    C.write(C.build(root), root, html=False)
    assert (root / "src" / "POUs" / "Lang" / "Converted" / "FB_StarterStl").is_dir()
    for path in (root / "samples" / "lang").glob("*.xml"):
        path.unlink()
    shutil.rmtree(root / "scenarios" / "lang")
    second = C.build(root)
    assert second.lang_result is None
    diff = C.write(second, root, html=False)
    assert any(rel.startswith("src/POUs/Lang/Converted/") for rel in diff.stale)
    assert any(rel.startswith(f"tests/POUs/{TG.LANG_SCENARIO_FOLDER}/") for rel in diff.stale)
    assert not any((root / "src").rglob("Lang/Converted/**/*.st"))
    assert C.compare(C.build(root), root).clean
