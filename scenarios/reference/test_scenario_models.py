"""Проверки сценариев поведения: формат CSV, актуальность файлов, ручные контрольные точки.

Контрольные точки ниже посчитаны вручную по описаниям логики в samples/scl/*.scl
(не моделью и не конвертером) — это вторая, независимая от модели проверка
ожидаемых значений.
"""

from __future__ import annotations

import os
from collections.abc import Mapping

import pytest

import generate_csv
from scenario_lib import (
    REALTIME_MARGIN_MS,
    BlockScenarios,
    Clock,
    FTrig,
    ParsedRow,
    Port,
    Row,
    RTrig,
    Scenario,
    ScenarioError,
    Tof,
    Ton,
    Value,
    format_real,
    read_csv,
    run_block,
    to_csv,
)


def _load(block: str) -> list[ParsedRow]:
    path = os.path.join(generate_csv.SCENARIOS_DIR, block + ".csv")
    with open(path, encoding="utf-8", newline="") as fh:
        _, rows = read_csv(fh.read())
    return rows


def _row(block: str, scenario: str, cycle: int) -> ParsedRow:
    for row in _load(block):
        if row.scenario == scenario and row.cycle == cycle:
            return row
    raise AssertionError(f"нет строки {block}.{scenario}#{cycle}")


@pytest.mark.parametrize("block", generate_csv.BLOCKS, ids=lambda b: b.block)
def test_csv_files_are_up_to_date(block: BlockScenarios) -> None:
    path = generate_csv.csv_path(block)
    with open(path, encoding="utf-8", newline="") as fh:
        assert fh.read() == to_csv(block), f"{path} устарел: python scenarios/reference/generate_csv.py"


@pytest.mark.parametrize("block", generate_csv.BLOCKS, ids=lambda b: b.block)
def test_csv_files_follow_format(block: BlockScenarios) -> None:
    path = generate_csv.csv_path(block)
    with open(path, encoding="utf-8", newline="") as fh:
        raw = fh.read()
    assert "\r" not in raw and not raw.startswith("﻿")
    columns, rows = read_csv(raw)
    assert [c.path for c in columns if c.kind == "in"] == [p.path for p in block.inputs]
    assert [c.path for c in columns if c.kind == "out"] == [p.path for p in block.outputs]
    assert len({r.scenario for r in rows}) >= 4
    # во всех строках этих файлов заданы все входы и все выходы
    assert all(len(r.inputs) == len(block.inputs) and len(r.outputs) == len(block.outputs) for r in rows)


def test_six_blocks_covered() -> None:
    names = {b.block for b in generate_csv.BLOCKS}
    assert names == {
        "FB_AnalogIn",
        "FB_Motor",
        "FB_AlarmDelay",
        "FB_Totalizer",
        "FB_PumpAlternation",
        "FB_Sequencer",
    }
    timed = {b.block for b in generate_csv.BLOCKS if b.timed}
    assert timed == {"FB_Motor", "FB_AlarmDelay", "FB_Sequencer"}


def test_generate_check_mode_passes() -> None:
    assert generate_csv.main(["--check"]) == 0


# --- Ручные контрольные точки -------------------------------------------------------------

# (блок, сценарий, cycle, выход, ожидаемое значение) — посчитано по описанию логики вручную
HAND_CHECKS: list[tuple[str, str, int, str, Value]] = [
    # FB_AnalogIn: value = 0 + 16 * raw / 27648
    ("FB_AnalogIn", "ScalingPoints", 2, "value", 8.0),
    ("FB_AnalogIn", "ScalingPoints", 3, "statusWord", 0x0031),  # valid + HH + H
    ("FB_AnalogIn", "ScalingPoints", 6, "statusWord", 0x00C1),  # valid + L + LL
    ("FB_AnalogIn", "HighLimitsHysteresis", 4, "warnH", True),  # 11.5 не меньше 12 - 0.5
    ("FB_AnalogIn", "HighLimitsHysteresis", 5, "warnH", False),  # 11.25 < 11.5
    ("FB_AnalogIn", "ChannelDiagnostics", 2, "value", 16.0),  # 27649 ограничено 27648
    ("FB_AnalogIn", "ChannelDiagnostics", 4, "value", 5.0),  # замещающее значение
    ("FB_AnalogIn", "ChannelDiagnostics", 4, "valid", False),
    ("FB_AnalogIn", "ChannelDiagnostics", 7, "statusWord", 0x00C9),  # valid + under + L + LL
    ("FB_AnalogIn", "Simulation", 2, "statusWord", 0x0133),  # valid fault HH H sim
    ("FB_AnalogIn", "CustomRanges", 2, "value", 100.0),  # -50 + 200 * 0.75
    ("FB_AnalogIn", "CustomRanges", 5, "value", 12.0),  # 16 + (0 - 16) * 0.25
    # FB_Motor: feedbackTime 3 с
    ("FB_Motor", "NoFeedbackTimeout", 2, "fault", False),  # 2.8 с
    ("FB_Motor", "NoFeedbackTimeout", 3, "status.faultCode", 1),  # 3.0 с
    ("FB_Motor", "NoFeedbackTimeout", 3, "runCmd", False),
    ("FB_Motor", "NoFeedbackTimeout", 5, "status.startCount", 2),  # повторный пуск после сброса
    ("FB_Motor", "FeedbackLost", 5, "status.faultCode", 2),
    ("FB_Motor", "UnexpectedFeedback", 3, "fault", True),  # сброс не снимает аварию 4
    ("FB_Motor", "UnexpectedFeedback", 5, "fault", False),
    ("FB_Motor", "ThermalTripManual", 6, "fault", True),  # сброс при сработавшем реле
    ("FB_Motor", "ThermalTripManual", 8, "runCmd", False),  # после сброса сам не стартует
    ("FB_Motor", "ThermalTripManual", 10, "runCmd", False),  # стоп приоритетнее пуска
    ("FB_Motor", "BumplessAutoToManual", 3, "runCmd", True),
    ("FB_Motor", "BumplessAutoToManual", 3, "status.autoMode", False),
    # FB_AlarmDelay: onDelay 5 с, offDelay 2 с
    ("FB_AlarmDelay", "ActivateAckClear", 3, "active", False),  # 4.8 с
    ("FB_AlarmDelay", "ActivateAckClear", 4, "state", 1),  # 5.0 с
    ("FB_AlarmDelay", "ActivateAckClear", 6, "state", 2),
    ("FB_AlarmDelay", "AckHeldDuringActivation", 3, "state", 1),  # ack держится, фронта нет: не квитирован
    ("FB_AlarmDelay", "AckHeldDuringActivation", 5, "state", 2),  # новый фронт ack
    ("FB_AlarmDelay", "ActivateAckClear", 9, "active", True),  # 1.8 с после снятия условия
    ("FB_AlarmDelay", "ActivateAckClear", 10, "state", 0),  # 2.0 с
    ("FB_AlarmDelay", "ClearedBeforeAck", 4, "state", 3),
    ("FB_AlarmDelay", "ChatterSuppressed", 6, "count", 0),
    ("FB_AlarmDelay", "ReturnDuringOffDelay", 7, "count", 1),
    ("FB_AlarmDelay", "NewActivationAfterOffDelay", 6, "count", 2),
    ("FB_AlarmDelay", "Disabled", 3, "alarm", False),
    ("FB_AlarmDelay", "AckSameCallAsActivation", 2, "unacked", True),
    # FB_Totalizer: dV = flow * dt / 3600
    ("FB_Totalizer", "IntegrationAndPulses", 8, "total", 1.0),  # 8 * 450 * 1 / 3600
    ("FB_Totalizer", "IntegrationAndPulses", 8, "pulseCount", 2),  # 1.0 / 0.5
    ("FB_Totalizer", "IntegrationAndPulses", 10, "total", 1.5),  # + 2 * 900 / 3600
    ("FB_Totalizer", "CutoffAndEnable", 5, "total", 0.125 + 0.5 / 3600),
    ("FB_Totalizer", "ResetLevel", 4, "total", 0.0),
    ("FB_Totalizer", "ResetLevel", 4, "lifetimeTotal", 1.0),  # 4 * 900 / 3600
    ("FB_Totalizer", "VariableCycleTime", 5, "total", 0.4),  # 450 * (0.5 + 0.5 + 2 + 0.1 + 0.1) / 3600
    ("FB_Totalizer", "LargeStepPulsesCatchUp", 4, "pulseCount", 4),
    ("FB_Totalizer", "LargeStepPulsesCatchUp", 5, "pulse", False),
    # FB_PumpAlternation
    ("FB_PumpAlternation", "RotateOnStop", 1, "leadPump", 1),  # первый вызов: спада нет
    ("FB_PumpAlternation", "RotateOnStop", 6, "runningCount", 3),
    ("FB_PumpAlternation", "StandbyTakesOver", 2, "run2", True),
    ("FB_PumpAlternation", "StandbyTakesOver", 4, "shortage", True),
    ("FB_PumpAlternation", "StandbyTakesOver", 5, "leadPump", 3),
    ("FB_PumpAlternation", "ForcedAlternate", 3, "leadPump", 2),
    ("FB_PumpAlternation", "DemandClamped", 2, "leadPump", 2),
    # FB_Sequencer
    ("FB_Sequencer", "FullCycle", 5, "stepNo", 20),  # 29.8 с продувки
    ("FB_Sequencer", "FullCycle", 6, "stepNo", 30),  # 30.2 с
    ("FB_Sequencer", "FullCycle", 8, "stepText", "REFILL"),
    ("FB_Sequencer", "FullCycle", 10, "cycleCount", 1),
    ("FB_Sequencer", "DrainTimeout", 4, "faultStep", 10),
    ("FB_Sequencer", "DrainTimeout", 5, "stepNo", 90),
    ("FB_Sequencer", "AbortByStop", 5, "stepNo", 0),
    ("FB_Sequencer", "PermissiveMissing", 3, "stepNo", 0),
    ("FB_Sequencer", "RefillTimeoutBoundary", 6, "faultStep", 40),
]


@pytest.mark.parametrize(("block", "scenario", "cycle", "output", "expected"), HAND_CHECKS)
def test_hand_checked_values(block: str, scenario: str, cycle: int, output: str, expected: Value) -> None:
    row = _row(block, scenario, cycle)
    actual = row.outputs[output]
    if isinstance(expected, float):
        assert isinstance(actual, float)
        assert abs(actual - expected) <= row.tolerances[output]
    else:
        assert actual == expected


def test_pump_lead_sequence_by_hand() -> None:
    leads = [r.outputs["leadPump"] for r in _load("FB_PumpAlternation") if r.scenario == "RotateOnStop"]
    assert leads == [1, 1, 1, 2, 2, 2, 3, 3, 1, 1]


def test_boundary_rows_are_marked() -> None:
    marked = {
        (r.scenario, r.cycle)
        for block in ("FB_Motor", "FB_AlarmDelay", "FB_Sequencer")
        for r in _load(block)
        if r.boundary
    }
    assert marked == {
        ("NoFeedbackTimeout", 3),
        ("ActivateAckClear", 4),
        ("ActivateAckClear", 10),
        ("DrainTimeoutBoundary", 3),
        ("RefillTimeoutBoundary", 6),
    }


# --- Примитивы модели ---------------------------------------------------------------------


def test_ton_fires_at_pt_and_resets() -> None:
    clock, ton = Clock(), Ton()
    for t, in_, q in [(0, True, False), (2999, True, False), (3000, True, True), (3500, False, False)]:
        clock.now_ms = t
        ton(clock, in_, 3000)
        assert ton.q is q, t
    clock.now_ms = 4000
    ton(clock, True, 3000)
    assert not ton.q and ton.et == 0


def test_tof_holds_for_pt_after_fall() -> None:
    clock, tof = Clock(), Tof()
    steps = [(0, False, False), (100, True, True), (200, False, True), (2199, False, True), (2200, False, False)]
    for t, in_, q in steps:
        clock.now_ms = t
        tof(clock, in_, 2000)
        assert tof.q is q, t


def test_edges_first_call() -> None:
    r, f = RTrig(), FTrig()
    r(True)
    f(False)
    assert r.q and not f.q  # R_TRIG срабатывает на первом вызове с TRUE, F_TRIG с FALSE — нет
    f(True)
    f(False)
    assert f.q


def test_format_real() -> None:
    assert format_real(8.0) == "8.0"
    assert format_real(-0.0) == "0.0"
    assert format_real(0.125) == "0.125"
    assert format_real(1.0 / 3.0) == "0.333333333"


class _ConstTon:
    """Модель с одним TON 1000 мс для проверки контроля запаса времени."""

    def __init__(self) -> None:
        self.ton = Ton()

    def step(self, clock: Clock, inputs: Mapping[str, Value]) -> dict[str, Value]:
        self.ton(clock, bool(inputs["x"]), 1000)
        return {"q": self.ton.q}


def _probe(rows: list[Row]) -> BlockScenarios:
    return BlockScenarios(
        block="FB_Probe",
        source="-",
        description="-",
        inputs=(Port("x", "BOOL"),),
        outputs=(Port("q", "BOOL"),),
        defaults={"x": False},
        factory=_ConstTon,
        scenarios=(Scenario("Probe", "-", rows),),
    )


def test_margin_violation_is_rejected() -> None:
    close = REALTIME_MARGIN_MS // 2
    with pytest.raises(ScenarioError):
        run_block(_probe([Row(0, {"x": True}, "-"), Row(1000 - close, {}, "-")]))
    with pytest.raises(ScenarioError):
        run_block(_probe([Row(0, {"x": True}, "-"), Row(1500, {}, "-", boundary=True)]))
    table = run_block(_probe([Row(0, {"x": True}, "-"), Row(1000, {}, "-", boundary=True)]))
    assert table[-1][4] == "TRUE"
