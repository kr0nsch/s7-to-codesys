"""Внешняя сверка корпуса всех языков: XSD SimaticML своей версии и приёмка на открытых экспортах TIA.

Файлы — по samples/lang/EXTERNAL.json: скачиваются в .cache/lang/ с проверкой SHA-256 (XSD © Siemens и
чужие экспорты в git не кладутся). Без сети или без lxml — skip с сообщением. XSD проверяет пространства
имён и структуру фрагментов (Sections, FlgNet, StatementList, StructuredText), но не словарь элементов
Part — его держат образцы и docs/MAPPING_LADFBD.md.
"""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from s7conv import pipeline as P
from s7conv.tests.conftest import REPO_ROOT

LANG = REPO_ROOT / "samples" / "lang"
CACHE = REPO_ROOT / ".cache" / "lang"
EXTERNAL: dict[str, Any] = json.loads((LANG / "EXTERNAL.json").read_text(encoding="utf-8"))
RAW = "https://raw.githubusercontent.com"


def fetch(repo: str, commit: str, path: str, sha256: str, dest: Path) -> Path:
    """Файл из репозитория GitHub по коммиту в кэш; SHA-256 обязателен. Без сети — skip."""
    if dest.is_file() and hashlib.sha256(dest.read_bytes()).hexdigest() == sha256:
        return dest
    url = f"{RAW}/{repo}/{commit}/{path}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = resp.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        pytest.skip(f"нет сети для {url}: {exc}")
    digest = hashlib.sha256(data).hexdigest()
    assert digest == sha256, f"{url}: SHA-256 {digest}, ожидался {sha256}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return dest


def xsd_dir(version: str) -> Path:
    spec = EXTERNAL["xsd"]
    info = spec["versions"][version]
    target = CACHE / "xsd" / version
    for name, sha in info["files"].items():
        fetch(spec["repo"], spec["commit"], f"{info['path']}/{name}", sha, target / name)
    return target


def _strip(el: Any) -> Any:
    """Копия элемента без пространств имён: XSD Siemens объявлены без targetNamespace."""
    from lxml import etree

    for node in el.iter():
        if isinstance(node.tag, str) and node.tag.startswith("{"):
            node.tag = node.tag.split("}", 1)[1]
    etree.cleanup_namespaces(el)
    return el


FRAGMENTS = ("Sections", "FlgNet", "StatementList", "StructuredText", "Graph")


def test_corpus_validates_against_v21_xsd() -> None:
    etree = pytest.importorskip("lxml.etree", reason="lxml нет — проверка XSD пропущена")
    version = "V21"
    info = EXTERNAL["xsd"]["versions"][version]
    folder = xsd_dir(version)
    schemas = {frag: etree.XMLSchema(etree.parse(str(folder / info["schemas"][frag]))) for frag in FRAGMENTS}
    namespaces = {
        frag: f"http://www.siemens.com/automation/Openness/SW/{ns}" for frag, ns in info["namespaces"].items()
    }
    namespaces["Sections"] = namespaces["Interface"]
    checked = dict.fromkeys(FRAGMENTS, 0)
    for path in sorted(LANG.glob("*.xml")):
        doc = etree.parse(str(path))
        for frag in FRAGMENTS:
            for el in doc.iter(f"{{{namespaces[frag]}}}{frag}"):
                copy = _strip(etree.fromstring(etree.tostring(el)))
                assert schemas[frag].validate(copy), f"{path.name}: {frag}: {schemas[frag].error_log.last_error}"
                checked[frag] += 1
    assert all(checked.values()), checked


def test_external_lad_sample_validates_against_its_xsd() -> None:
    """Открытый экспорт V21 проходит ту же проверку XSD — значит, проверка не подогнана под корпус."""
    etree = pytest.importorskip("lxml.etree", reason="lxml нет — проверка XSD пропущена")
    info = EXTERNAL["xsd"]["versions"]["V21"]
    folder = xsd_dir("V21")
    schema = etree.XMLSchema(etree.parse(str(folder / info["schemas"]["FlgNet"])))
    sample = next(s for s in EXTERNAL["samples"] if s["id"] == "lad-cookbook")
    paths = _sample_files(sample)
    ns = "{http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v5}FlgNet"
    count = 0
    for path in paths:
        for el in etree.parse(str(path)).iter(ns):
            assert schema.validate(_strip(etree.fromstring(etree.tostring(el)))), path.name
            count += 1
    assert count >= 10


def _sample_files(sample: dict[str, Any]) -> list[Path]:
    target = CACHE / "samples" / sample["id"]
    return [
        fetch(sample["repo"], sample["commit"], f"{sample['path']}/{rel}", sha, target / rel)
        for rel, sha in sample["files"].items()
    ]


@pytest.mark.parametrize("sample", EXTERNAL["samples"], ids=lambda s: s["id"])
def test_external_samples_convert_with_expected_outcome(sample: dict[str, Any]) -> None:
    paths = _sample_files(sample)
    inputs = P.Inputs(xml=sorted(paths))
    result, files = P.run(inputs)
    raw = sum(1 for sf in files for b in sf.blocks if getattr(b, "reason", None))
    assert raw == sample["expect"]["raw_blocks"]
    notes = [n for f in result.files for n in f.notes]
    todo = sorted({n.rule for n in notes if n.severity == "todo"})
    check = sorted({n.rule for n in notes if n.severity == "check"})
    assert todo == sorted(sample["expect"]["todo"]), todo
    assert set(check) <= set(sample["expect"]["check"]), check
    units = [u for f in result.files if f.lowering for u in f.lowering.units]
    assert units and not [u for u in units if u.status == "todo"]


# ---------------------------------------------------------------------------
# Порча XML: разбор не падает, причина — в пометке
# ---------------------------------------------------------------------------

CORRUPTIONS = ("drop_wire", "dup_uid", "unknown_part", "drop_operand", "truncate")


@settings(max_examples=40, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(st.sampled_from(sorted(LANG.glob("FB_*.xml"))), st.sampled_from(CORRUPTIONS), st.integers(0, 50))
def test_corrupted_xml_never_crashes(tmp_path_factory: pytest.TempPathFactory, path: Path, how: str, k: int) -> None:
    import re

    text = path.read_text(encoding="utf-8")
    if how == "drop_wire":
        wires = list(re.finditer(r"<Wire UId=\"\d+\">.*?</Wire>", text))
        if wires:
            w = wires[k % len(wires)]
            text = text[: w.start()] + text[w.end() :]
    elif how == "dup_uid":
        uids = re.findall(r'UId="(\d+)"', text)
        if len(uids) > 1:
            text = text.replace(f'UId="{uids[(k + 1) % len(uids)]}"', f'UId="{uids[k % len(uids)]}"', 1)
    elif how == "unknown_part":
        text = re.sub(r'<Part Name="(Contact|Coil|SR|PBox|Add|A|O)"', '<Part Name="FancyUnknownBox"', text, count=1)
    elif how == "drop_operand":
        accs = list(re.finditer(r"<Access Scope=\"LocalVariable\"[^>]*>.*?</Access>", text))
        if accs:
            a = accs[k % len(accs)]
            text = text[: a.start()] + text[a.end() :]
    else:
        text = text[: max(1, len(text) * (k + 1) // 60)]
    target = tmp_path_factory.mktemp("bad") / path.name
    target.write_text(text, encoding="utf-8")
    result, files = P.run(P.Inputs(xml=[target]))
    if how != "truncate" and "<Document" in text and text.rstrip().endswith("</Document>"):
        assert (files and files[0].lowering is not None) or files[0].issues
    assert result is not None
