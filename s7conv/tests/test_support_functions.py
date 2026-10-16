"""Объекты поддержки S7Compat: раскладка, интерфейс, согласованность тестов CfUnit с формулой Siemens.

Ожидаемые значения наборов FB_F_NormX_Test и FB_F_ScaleX_Test пересчитываются здесь по формулам
из документации S7 (docs/MAPPING.md, «NORM_X и SCALE_X»), независимо от кода ST:
NORM_X: OUT = (VALUE - MIN) / (MAX - MIN); SCALE_X: OUT = VALUE * (MAX - MIN) + MIN; без ограничения
диапазоном. Вырожденный диапазон NORM_X (MIN = MAX) — решение s7conv: 0.0.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from s7conv import mapping as M
from s7conv.layout import SUPPORT_FOLDER, L
from s7conv.pipeline import support_objects
from s7conv.tests.conftest import REPO_ROOT

CALL_RE = re.compile(
    r"rResult := (F_NormX|F_ScaleX)\(rMin := (?P<min>[-\d.]+), rValue := (?P<value>[-\d.]+), rMax := (?P<max>[-\d.]+)\);"
)
EXPECTED_RE = re.compile(r"AssertEquals_REAL\(Expected := (?P<expected>[-\d.]+),")


def norm_x(lo: float, value: float, hi: float) -> float:
    return 0.0 if hi == lo else (value - lo) / (hi - lo)


def scale_x(lo: float, value: float, hi: float) -> float:
    return value * (hi - lo) + lo


SCALING = ["F_NormX", "F_ScaleX"]


def test_every_support_object_is_hand_written_in_s7compat() -> None:
    """Все объекты mapping.SUPPORT_DEPENDENCIES есть в src/*/S7Compat; зависимости тоже из этого списка."""
    objects = support_objects(sorted(M.SUPPORT_DEPENDENCIES))
    assert sorted(o.name for o in objects) == sorted(M.SUPPORT_DEPENDENCIES)
    for obj in objects:
        assert obj.folder == [SUPPORT_FOLDER], obj.name
        assert set(M.SUPPORT_DEPENDENCIES[obj.name]) <= set(M.SUPPORT_DEPENDENCIES)


def test_support_closure_adds_dependencies() -> None:
    assert M.support_closure(["FB_S7Ton"]) == ["FB_S7Ton", "F_S7Now", "GVL_S7Clock"]
    assert M.support_closure(["F_NormX"]) == ["F_NormX"]


def test_compat_timers_keep_iec_interface() -> None:
    """FB_S7Ton/Tof/Tp — с интерфейсом IN, PT / Q, ET (замена TON/TOF/TP без правок вызовов)."""
    timers = [o for o in support_objects(sorted(M.COMPAT_TIMERS.values())) if o.name in M.COMPAT_TIMERS.values()]
    assert len(timers) == len(M.COMPAT_TIMERS)
    for obj in timers:
        blocks = {b.keyword: [n for d in b.decls for n in d.name_list] for b in L.parse_var_blocks(obj.decl)}
        assert blocks["VAR_INPUT"] == ["IN", "PT"] and blocks["VAR_OUTPUT"] == ["Q", "ET"], obj.name
    (ftrig,) = support_objects([M.COMPAT_F_TRIG])
    blocks = {b.keyword: [n for d in b.decls for n in d.name_list] for b in L.parse_var_blocks(ftrig.decl)}
    assert blocks["VAR_INPUT"] == ["CLK"] and blocks["VAR_OUTPUT"] == ["Q"]


def test_support_pous_are_valid_layout_objects() -> None:
    objects = support_objects(SCALING)
    assert [o.name for o in objects] == SCALING
    for obj in objects:
        assert obj.pou_kind == L.POU_FUNCTION
        assert obj.header is not None and obj.header.return_type == "REAL"
        blocks = L.parse_var_blocks(obj.decl)
        inputs = [name for b in blocks if b.keyword == "VAR_INPUT" for d in b.decls for name in d.name_list]
        assert inputs == ["rMin", "rValue", "rMax"]


@pytest.mark.parametrize(("suite", "func"), [("FB_F_NormX_Test", norm_x), ("FB_F_ScaleX_Test", scale_x)])
def test_cfunit_expectations_match_siemens_formula(suite: str, func: object) -> None:
    folder = REPO_ROOT / "tests" / "POUs" / SUPPORT_FOLDER / suite
    methods = sorted(folder.glob("*.method.impl.st"))
    assert len(methods) >= 6
    for path in methods:
        text = Path(path).read_text(encoding="utf-8")
        call = CALL_RE.search(text)
        expected = EXPECTED_RE.search(text)
        assert call and expected, path.name
        assert callable(func)
        value = func(float(call["min"]), float(call["value"]), float(call["max"]))
        assert value == pytest.approx(float(expected["expected"]), abs=1e-4), path.name
