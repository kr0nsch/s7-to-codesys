"""Сценарии корпуса всех языков: актуальность CSV, формат, алиасы, ручные контрольные точки.

Контрольные точки посчитаны вручную по описаниям логики блоков (samples/lang/README.md), не моделью
и не конвертером, — вторая, независимая от модели проверка ожидаемых значений.
"""

from __future__ import annotations

import json
import os

import pytest

import generate_lang_csv
from scenario_lib import BlockScenarios, ParsedRow, Value, read_csv, to_csv


def _load(block: str) -> list[ParsedRow]:
    with open(os.path.join(generate_lang_csv.SCENARIOS_DIR, block + ".csv"), encoding="utf-8", newline="") as fh:
        _, rows = read_csv(fh.read())
    return rows


def _row(block: str, scenario: str, cycle: int) -> ParsedRow:
    found = [r for r in _load(block) if r.scenario == scenario and r.cycle == cycle]
    assert found, f"нет строки {block}.{scenario}#{cycle}"
    return found[0]


@pytest.mark.parametrize("block", generate_lang_csv.BLOCKS, ids=lambda b: b.block)
def test_csv_files_are_up_to_date(block: BlockScenarios) -> None:
    with open(generate_lang_csv.csv_path(block), encoding="utf-8", newline="") as fh:
        assert fh.read() == to_csv(block), "устарел: python scenarios/lang/reference/generate_lang_csv.py"


def test_scenario_minimums_of_release_1_1() -> None:
    """ТЗ: FB_Starter ≥ 8 сценариев на все четыре языка, FB_PumpInterlockLad ≥ 4, всего ≥ 12."""
    counts = {b.block: len(b.scenarios) for b in generate_lang_csv.BLOCKS}
    assert counts["FB_Starter"] >= 8
    assert counts["FB_PumpInterlockLad"] >= 4
    assert sum(counts.values()) >= 12


def test_aliases_cover_four_languages() -> None:
    with open(os.path.join(generate_lang_csv.SCENARIOS_DIR, "aliases.json"), encoding="utf-8") as fh:
        aliases = json.load(fh)
    assert aliases == {"FB_Starter": ["FB_StarterLad", "FB_StarterFbd", "FB_StarterStl", "FB_StarterScl"]}


def test_generate_check_mode_passes() -> None:
    assert generate_lang_csv.main(["--check"]) == 0


# (блок, сценарий, cycle, выход, значение) — по описанию логики, вручную
HAND_CHECKS: list[tuple[str, str, int, str, Value]] = [
    # SR S7 с операндом: S = R1 = 1 — сброс главнее (одноимённый SR CODESYS дал бы TRUE)
    ("FB_Starter", "StartAndStopTogether", 2, "xRun", False),
    ("FB_Starter", "StartAndStopTogether", 3, "xRun", True),
    ("FB_Starter", "StartAndStopTogether", 5, "xRun", False),
    ("FB_Starter", "InterlockBlocksStart", 4, "xRun", False),  # пуск при блокировке не запоминается
    # tFeedbackTime 2 с от 0.1 с: 1.9 с — 1.8 с прошло; 2.1 с — ровно 2.0 с
    ("FB_Starter", "FeedbackTimeout", 3, "xFault", False),
    ("FB_Starter", "FeedbackTimeout", 4, "xFault", True),
    ("FB_Starter", "FeedbackTimeout", 4, "xRun", True),  # сеть 1 раньше сети 3
    ("FB_Starter", "FeedbackTimeout", 5, "xRun", False),
    ("FB_Starter", "FaultResetAndBlock", 4, "xRun", False),  # R1 = xFault главнее Пуска
    ("FB_Starter", "FaultResetAndBlock", 6, "iStarts", 2),
    ("FB_Starter", "StartCounter", 6, "iStarts", 2),
    ("FB_Starter", "ResetWhileRunning", 3, "iStarts", 1),
    # FB_PumpInterlockLad
    ("FB_PumpInterlockLad", "AutoRunAndCount", 2, "iSetpoint_pct", 80),  # 120 → 100 → 90 → 80
    ("FB_PumpInterlockLad", "AutoRunAndCount", 2, "xCountOk", True),
    ("FB_PumpInterlockLad", "AutoRunAndCount", 3, "xCountOk", False),  # EN = 0 → ENO = 0
    ("FB_PumpInterlockLad", "LowLevelTripAndAck", 4, "xAlarm", True),  # квитирование при низком уровне
    ("FB_PumpInterlockLad", "LowLevelTripAndAck", 5, "iRunCount", 2),
    ("FB_PumpInterlockLad", "HighPressure", 3, "xHighPress", False),  # 600 не больше 600
    ("FB_PumpInterlockLad", "MaintenanceJump", 2, "xCountOk", True),  # сеть 7 пропущена: значение прежнее
    ("FB_PumpInterlockLad", "MaintenanceJump", 2, "xPumpOn", False),
    ("FB_PumpInterlockLad", "MaintenanceJump", 4, "iRunCount", 1),  # бит памяти фронта остался 1
    ("FB_PumpInterlockLad", "MaintenanceJump", 6, "iRunCount", 2),
    ("FB_PumpInterlockLad", "SetpointClamp", 3, "iSetpoint_pct", 20),  # 15 → 15 → 15 → 20
    ("FB_PumpInterlockLad", "SetpointClamp", 4, "iSetpoint_pct", 20),  # 5 → 5 → 10 → 20
    # FB_ConveyorStl: шкала S5T#2S — 10 мс, остаток L T — в единицах шкалы
    ("FB_ConveyorStl", "StartSequence", 1, "iDelayLeft", 200),  # 2 с / 10 мс
    ("FB_ConveyorStl", "StartSequence", 2, "iDelayLeft", 170),  # прошло 0,3 с
    ("FB_ConveyorStl", "StartSequence", 3, "xHorn", False),  # SP 1 с истёк ровно в 1 с
    ("FB_ConveyorStl", "StartSequence", 5, "xMotor", True),  # SD 2 с истёк, SF T3 = 1 сразу
    ("FB_ConveyorStl", "HornCutShort", 3, "iDelayLeft", 170),  # RLO SD = 0: остаток замер
    ("FB_ConveyorStl", "CountResetIsLevel", 6, "iCount", 0),  # R по уровню после CU того же вызова
    # FB_BackwashGraph: активация Air в t = 1000 мс; квитирование — до переходов того же вызова
    ("FB_BackwashGraph", "LongWash", 2, "iWashCount", 1),  # событие S1 при активации Drain
    ("FB_BackwashGraph", "LongWash", 3, "iWashCount", 1),  # шаг активен, события нет
    ("FB_BackwashGraph", "LongWash", 5, "xAirValve", False),  # D 2 с: прошло 0,1 с
    ("FB_BackwashGraph", "LongWash", 6, "xAirValve", True),  # ровно 2 с
    ("FB_BackwashGraph", "LongWash", 7, "xBlower", True),  # Air.T = 9,7 с < 10 с
    ("FB_BackwashGraph", "LongWash", 8, "xInletValve", True),  # Air.T = 10 с: T4 — Refill
    ("FB_BackwashGraph", "LongWash", 8, "xWashActive", False),  # R xWashActive в Refill
    ("FB_BackwashGraph", "Supervision", 5, "xDrainValve", True),  # переход держит ошибка контроля
    ("FB_BackwashGraph", "Supervision", 6, "ERR_FLT", True),  # квитирование при неисправности — снова
    ("FB_BackwashGraph", "AckSwitches", 5, "xWashPump", True),  # квитирование и T3 в одном вызове
    ("FB_BackwashGraph", "AckSwitches", 5, "ERR_FLT", False),  # Drain выключен — контроль не действует
]


@pytest.mark.parametrize(("block", "scenario", "cycle", "output", "expected"), HAND_CHECKS)
def test_hand_checked_values(block: str, scenario: str, cycle: int, output: str, expected: Value) -> None:
    assert _row(block, scenario, cycle).outputs[output] == expected
