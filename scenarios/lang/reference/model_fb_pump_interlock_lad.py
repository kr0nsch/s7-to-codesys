"""Эталонная модель и сценарии FB_PumpInterlockLad.

Источник логики — описание в комментарии блока samples/lang/FB_PumpInterlockLad.xml (PUMP_DESCRIPTION
в samples/lang/blocks.py), пункты 1–12, и описание FC_ClampPctLad.
"""

from __future__ import annotations

from collections.abc import Mapping

from scenario_lib import BlockScenarios, Clock, Port, Scenario, Value, untimed_rows

INT_MIN, INT_MAX, INT_SPAN = -32768, 32767, 65536


def clamp(value: int, lo: int, hi: int) -> int:
    """FC_ClampPctLad: сначала верхний предел, затем нижний (оба сравнения — с исходным значением)."""
    result = value
    if value > hi:
        result = hi
    if value < lo:
        result = lo
    return result


class PumpInterlockModel:
    def __init__(self) -> None:
        self.pump_on = False
        self.alarm_latch = False
        self.run_edge = False
        self.run_count = 0
        self.count_ok = False
        self.stage1 = 0
        self.stage2 = 0
        self.setpoint = 0

    def step(self, clock: Clock, i: Mapping[str, Value]) -> dict[str, Value]:
        del clock
        level, press = int(i["iLevel_cm"]), int(i["iPressure_kPa"])
        low = level < int(i["iLevelMin_cm"])
        high = press > int(i["iPressureMax_kPa"])
        if low or high:
            self.alarm_latch = True
        if bool(i["xAck"]) and not low and not high:
            self.alarm_latch = False
        maint = bool(i["xMaint"])
        if not maint:  # 5. прыжок к NoAuto при обслуживании: сети 6–7 не выполняются
            self.pump_on = bool(i["xAutoReq"]) and not self.alarm_latch
            edge = self.pump_on and not self.run_edge
            self.run_edge = self.pump_on
            # 7. ADD с ENO: ENO = EN AND NOT переполнение; при EN = FALSE ENO = FALSE
            total = self.run_count + 1
            self.count_ok = edge and INT_MIN <= total <= INT_MAX
            if edge:
                self.run_count = (total - INT_MIN) % INT_SPAN + INT_MIN
        if maint:  # 8. метка NoAuto: обслуживание выключает насос
            self.pump_on = False
        if self.pump_on:  # 9. три вызова через EN/ENO; у FC_ClampPctLad ENO = EN
            self.stage1 = clamp(level, 0, 100)
            self.stage2 = clamp(self.stage1, 10, 90)
            self.setpoint = clamp(self.stage2, 20, 80)
        chain_ok = self.pump_on
        if not self.pump_on:  # 10. MOVE 0
            self.setpoint = 0
        return {
            "xPumpOn": self.pump_on,
            "xLowLevel": low,
            "xHighPress": high,
            "xAlarm": self.alarm_latch,
            "iRunCount": self.run_count,
            "xCountOk": self.count_ok,
            "iSetpoint_pct": self.setpoint,
            "xChainOk": chain_ok,
            "xRunMem": self.run_edge,
        }


INPUTS = (
    Port("xAutoReq", "BOOL"),
    Port("iLevel_cm", "INT"),
    Port("iLevelMin_cm", "INT"),
    Port("iPressure_kPa", "INT"),
    Port("iPressureMax_kPa", "INT"),
    Port("xAck", "BOOL"),
    Port("xMaint", "BOOL"),
)
OUTPUTS = (
    Port("xPumpOn", "BOOL"),
    Port("xLowLevel", "BOOL"),
    Port("xHighPress", "BOOL"),
    Port("xAlarm", "BOOL"),
    Port("iRunCount", "INT"),
    Port("xCountOk", "BOOL"),
    Port("iSetpoint_pct", "INT"),
    Port("xChainOk", "BOOL"),
    Port("xRunMem", "BOOL"),
)
DEFAULTS: dict[str, Value] = {
    "xAutoReq": False,
    "iLevel_cm": 120,
    "iLevelMin_cm": 50,
    "iPressure_kPa": 400,
    "iPressureMax_kPa": 600,
    "xAck": False,
    "xMaint": False,
}

SCENARIOS = (
    Scenario(
        "AutoRunAndCount",
        "Запрос автоматики: насос включается, включение №1, ENO сложения — в одном вызове",
        untimed_rows(
            [
                ({}, "покой: уставка 0"),
                ({"xAutoReq": True}, "включение №1: ENO = 1, уставка 120 → 100 → 90 → 80"),
                ({}, "работает: фронта нет, ENO = 0"),
                ({"xAutoReq": False}, "запрос снят: насос выключен, уставка 0 (MOVE)"),
                ({"xAutoReq": True}, "включение №2"),
            ]
        ),
    ),
    Scenario(
        "LowLevelTripAndAck",
        "Низкий уровень: защёлка аварии, квитирование только при норме",
        untimed_rows(
            [
                ({"xAutoReq": True}, "включение №1"),
                ({"iLevel_cm": 40}, "уровень 40 < 50: авария, насос выключен"),
                ({"iLevel_cm": 60}, "уровень в норме: авария держится"),
                ({"xAck": True, "iLevel_cm": 45}, "квитирование при низком уровне: не снимается"),
                ({"iLevel_cm": 70}, "уровень в норме при нажатом квитировании: снята, включение №2"),
                ({"xAck": False}, "работает"),
            ]
        ),
    ),
    Scenario(
        "HighPressure",
        "Высокое давление: авария по второму условию",
        untimed_rows(
            [
                ({"xAutoReq": True}, "включение №1"),
                ({"iPressure_kPa": 650}, "650 > 600: авария, насос выключен"),
                ({"iPressure_kPa": 600, "xAck": True}, "600 не больше 600: квитирование снимает, включение №2"),
                ({"xAck": False}, "работает"),
            ]
        ),
    ),
    Scenario(
        "MaintenanceJump",
        "Обслуживание: прыжок мимо сетей 6–7 — насос выключен, бит фронта и ENO не обновляются",
        untimed_rows(
            [
                ({"xAutoReq": True}, "включение №1, xCountOk = 1"),
                ({"xMaint": True}, "обслуживание: насос выключен; xCountOk и xRunMem сохраняют значения"),
                ({}, "обслуживание держится"),
                ({"xMaint": False}, "выход из обслуживания: насос включён, фронта нет — бит памяти остался 1"),
                ({"xAutoReq": False}, "запрос снят"),
                ({"xAutoReq": True}, "включение №2"),
            ]
        ),
    ),
    Scenario(
        "SetpointClamp",
        "Уставка: три ограничения подряд через EN/ENO",
        untimed_rows(
            [
                ({"xAutoReq": True, "iLevel_cm": 55}, "55 → 55 → 55 → 55"),
                ({"iLevel_cm": 95}, "95 → 95 → 90 → 80"),
                ({"iLevel_cm": 15, "iLevelMin_cm": 10}, "15 → 15 → 15 → 20"),
                ({"iLevel_cm": 5, "iLevelMin_cm": 0}, "5 → 5 → 10 → 20"),
            ]
        ),
    ),
)

BLOCK = BlockScenarios(
    block="FB_PumpInterlockLad",
    source="samples/lang/FB_PumpInterlockLad.xml",
    description="блокировки насоса: S/R, сравнения, прыжок, PBox, ADD с ENO, цепочка EN/ENO",
    inputs=INPUTS,
    outputs=OUTPUTS,
    defaults=DEFAULTS,
    factory=PumpInterlockModel,
    scenarios=SCENARIOS,
    timed=False,
)
