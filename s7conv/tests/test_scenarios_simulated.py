"""Тесты coUnit, исполненные интерпретатором ST (s7conv/tests/stsim.py) без CODESYS.

Исполняются закоммиченные файлы: сгенерированные наборы tests/POUs/Scenarios против сконвертированного
кода src/*/Converted и слоя S7Compat, рукописные наборы tests/POUs/S7Compat. Это предварительная
проверка: интерпретатор — модель CODESYS (разрядность целых, float32 для REAL, семантика стандартных ФБ
задана явно), а окончательный результат — прогон в CODESYS Control Win (docs/TEST_REPORT.md).

Что показывает: (1) сгенерированные тесты и сконвертированный код согласованы со сценариями при
семантике F_TRIG S7; (2) если F_TRIG CODESYS Standard даёт ложный спад на первом вызове, упадёт ровно
один тест — RotateOnStop; (3) тесты не пустые: искажённое ожидание или искажённая логика блока ловятся.
"""

from __future__ import annotations

import copy

import pytest

from s7conv.layout import L
from s7conv.tests.conftest import REPO_ROOT
from s7conv.tests.stsim import F_TRIG_IEC_M_FALSE, F_TRIG_S7, Sim, SuiteOutcome

SCENARIO_SUITES = [
    "FB_AlarmDelay_ScenarioTest",
    "FB_AnalogIn_ScenarioTest",
    "FB_Motor_ScenarioTest",
    "FB_PumpAlternation_ScenarioTest",
    "FB_Sequencer_ScenarioTest",
    "FB_Totalizer_ScenarioTest",
]
COMPAT_SUITES = [
    "FB_S7Ton_Test",
    "FB_S7Tof_Test",
    "FB_S7Tp_Test",
    "FB_S7FTrig_Test",
    "FB_F_S7Now_Test",
    "FB_F_NormX_Test",
    "FB_F_ScaleX_Test",
]


@pytest.fixture(scope="module")
def objects() -> list[L.StObject]:
    return list(L.scan(str(REPO_ROOT), "src").objects) + list(L.scan(str(REPO_ROOT), "tests").objects)


def _methods(objs: list[L.StObject], suite: str) -> list[str]:
    return [m.name for o in objs if o.name == suite for m in o.methods]


@pytest.mark.parametrize("suite", SCENARIO_SUITES)
def test_scenario_suite_passes_in_simulation(objects: list[L.StObject], suite: str) -> None:
    out = Sim(objects, f_trig=F_TRIG_S7).run_suite(suite, cycles=3)
    assert out.failures == {}, out.failures
    assert sorted(out.registered) == sorted(_methods(objects, suite))
    assert out.finished == set(out.registered)
    expected_asserts = sum((m.impl or "").count("AssertEquals_") for o in objects if o.name == suite for m in o.methods)
    # каждая проверка выполнена ровно один раз за три цикла: сценарий не повторяется (флаг xDone)
    assert out.asserts == expected_asserts


def test_f_trig_with_false_edge_on_first_call_breaks_only_rotate_on_stop(objects: list[L.StObject]) -> None:
    """Гипотеза «F_TRIG Standard: Q := NOT CLK AND NOT M, M = FALSE» — что именно упадёт в CODESYS."""
    sim = Sim(objects, f_trig=F_TRIG_IEC_M_FALSE)
    results: dict[str, SuiteOutcome] = {suite: sim.run_suite(suite) for suite in SCENARIO_SUITES}
    failed = {suite: sorted(out.failures) for suite, out in results.items() if out.failures}
    assert failed == {"FB_PumpAlternation_ScenarioTest": ["RotateOnStop"]}
    first = results["FB_PumpAlternation_ScenarioTest"].failures["RotateOnStop"][0]
    assert first.startswith("RotateOnStop#1 leadPump: Expected 1, Actual 2")


@pytest.mark.parametrize("suite", COMPAT_SUITES)
def test_s7compat_suite_passes_in_simulation(objects: list[L.StObject], suite: str) -> None:
    """Рукописные тесты S7Compat; тесты в реальном времени — с моделью таймеров Standard по МЭК."""
    out = Sim(objects).run_suite(suite, cycles=100, cycle_ms=10)
    assert out.failures == {}, out.failures
    assert out.finished == set(out.registered) == set(_methods(objects, suite))


def _replace(objs: list[L.StObject], name: str, method: str | None, old: str, new: str) -> list[L.StObject]:
    result = copy.deepcopy(objs)
    for obj in result:
        if obj.name != name:
            continue
        if method is None:
            assert obj.impl is not None and old in obj.impl
            obj.impl = obj.impl.replace(old, new, 1)
        else:
            m = next(m for m in obj.methods if m.name == method)
            assert m.impl is not None and old in m.impl
            m.impl = m.impl.replace(old, new, 1)
    return result


def test_wrong_expectation_is_reported(objects: list[L.StObject]) -> None:
    broken = _replace(
        objects,
        "FB_Motor_ScenarioTest",
        "NoFeedbackTimeout",
        "AssertEquals_INT(Expected := 1,",
        "AssertEquals_INT(Expected := 7,",
    )
    out = Sim(broken).run_suite("FB_Motor_ScenarioTest")
    assert list(out.failures) == ["NoFeedbackTimeout"]


@pytest.mark.parametrize(
    ("block", "old", "new", "suite"),
    [
        ("FB_Motor", "runCmd := demand AND NOT fault;", "runCmd := demand;", "FB_Motor_ScenarioTest"),
        ("FB_AlarmDelay", "count := count + 1;", "count := count + 2;", "FB_AlarmDelay_ScenarioTest"),
        # квитирование уровнем вместо фронта: ловит только сценарий AckHeldDuringActivation, добавленный после
        # того, как эта мутация прошла незамеченной
        ("FB_AlarmDelay", "IF edgeAck.Q THEN", "IF ack THEN", "FB_AlarmDelay_ScenarioTest"),
        (
            "FB_AnalogIn",
            "ELSIF value < limitHH - hysteresis THEN",
            "ELSIF value < limitHH THEN",
            "FB_AnalogIn_ScenarioTest",
        ),
        ("FB_S7Ton", "Q := IN AND tElapsed >= PT;", "Q := IN AND tElapsed > PT;", "FB_Motor_ScenarioTest"),
    ],
)
def test_mutated_logic_is_caught(objects: list[L.StObject], block: str, old: str, new: str, suite: str) -> None:
    """Мутация логики (в том числе порога таймера: >= → >) роняет тесты сценариев."""
    out = Sim(_replace(objects, block, None, old, new)).run_suite(suite)
    assert out.failures
