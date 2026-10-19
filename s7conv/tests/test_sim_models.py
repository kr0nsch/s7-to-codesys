"""Интерпретатор stsim: старая точка импорта и модели стандартных ФБ."""

from __future__ import annotations

import s7conv.sim.stsim as new
import s7conv.tests.stsim as old


def test_old_import_path_reexports_simulator() -> None:
    """Соседние проекты импортируют s7conv.tests.stsim (выпуск 1.0.0): имена те же объекты."""
    for name in new.__all__:
        assert getattr(old, name) is getattr(new, name)
    assert old.__all__ == new.__all__


def _fb(sim: new.Sim, type_name: str) -> new.Obj:
    return sim.new_object(type_name)


def _call(sim: new.Sim, inst: new.Obj, **inputs: object) -> new.Obj:
    for key, value in inputs.items():
        inst.vars[key.lower()] = value
    sim.builtin_fb(inst)
    return inst


def test_sr_is_set_dominant_and_rs_is_reset_dominant() -> None:
    sim = new.Sim([])
    sr = _call(sim, _fb(sim, "SR"), SET1=True, RESET=True)
    assert sr.vars["q1"] is True
    rs = _call(sim, _fb(sim, "RS"), SET=True, RESET1=True)
    assert rs.vars["q1"] is False


def test_rs_follows_set_level_after_reset_pulse() -> None:
    sim = new.Sim([])
    rs = _fb(sim, "RS")
    assert _call(sim, rs, SET=True, RESET1=False).vars["q1"] is True
    assert _call(sim, rs, SET=True, RESET1=True).vars["q1"] is False
    assert _call(sim, rs, SET=True, RESET1=False).vars["q1"] is True


def test_ctu_counts_rising_edges_and_saturates_at_word_max() -> None:
    sim = new.Sim([])
    ctu = _fb(sim, "CTU")
    for cu in (True, True, False, True):
        _call(sim, ctu, CU=cu, RESET=False, PV=2)
    assert ctu.vars["cv"] == 2
    assert ctu.vars["q"] is True
    ctu.vars["cv"] = 0xFFFF
    _call(sim, ctu, CU=False)
    _call(sim, ctu, CU=True)
    assert ctu.vars["cv"] == 0xFFFF


def test_ctd_does_not_go_below_zero() -> None:
    sim = new.Sim([])
    ctd = _call(sim, _fb(sim, "CTD"), CD=False, LOAD=True, PV=1)
    _call(sim, ctd, CD=True, LOAD=False)
    _call(sim, ctd, CD=False)
    _call(sim, ctd, CD=True)
    assert ctd.vars["cv"] == 0
    assert ctd.vars["q"] is True


def test_ctud_reset_beats_load_and_simultaneous_edges_cancel() -> None:
    sim = new.Sim([])
    ctud = _call(sim, _fb(sim, "CTUD"), RESET=True, LOAD=True, PV=3)
    assert ctud.vars["cv"] == 0
    assert ctud.vars["qd"] is True
    _call(sim, ctud, RESET=False, LOAD=True, PV=5)
    _call(sim, ctud, LOAD=False)
    _call(sim, ctud, CU=True, CD=True)
    assert ctud.vars["cv"] == 5
