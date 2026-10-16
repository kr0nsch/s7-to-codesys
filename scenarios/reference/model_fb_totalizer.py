"""Эталонная модель и сценарии FB_Totalizer.

Источник логики — нормативное описание в заголовке samples/scl/FB_Totalizer.scl
(пункты 1–4). Время блоку передаётся входом cycleTime; t_ms в CSV растёт на
cycleTime строки (проверяет scenario_lib). Расходы и периоды подобраны так, что
приращения точно представимы в двоичном виде (450 м3/ч за 1 с = 0.125 м3).
"""

from __future__ import annotations

from collections.abc import Mapping

from scenario_lib import BlockScenarios, Clock, Port, Row, Scenario, Value

SECONDS_PER_HOUR = 3600.0
MS_PER_SECOND = 1000.0


class TotalizerModel:
    def __init__(self) -> None:
        self.total = 0.0
        self.pulse_count = 0
        self.pulse_acc = 0.0
        self.lifetime_acc = 0.0

    def step(self, clock: Clock, i: Mapping[str, Value]) -> dict[str, Value]:
        flow = float(i["flow"])
        cutoff = flow < float(i["lowFlowCutoff"])
        dt = int(i["cycleTime"]) / MS_PER_SECOND
        delta = flow * dt / SECONDS_PER_HOUR if bool(i["enable"]) and not cutoff else 0.0
        self.lifetime_acc += delta
        pulse = False
        pulse_volume = float(i["pulseVolume"])
        if bool(i["reset"]):
            self.total = 0.0
            self.pulse_count = 0
            self.pulse_acc = 0.0
        else:
            self.total += delta
            self.pulse_acc += delta
            if pulse_volume > 0.0 and self.pulse_acc >= pulse_volume:
                pulse = True
                self.pulse_count += 1
                self.pulse_acc -= pulse_volume
        return {
            "total": self.total,
            "lifetimeTotal": self.lifetime_acc,
            "pulseCount": self.pulse_count,
            "pulse": pulse,
            "cutoffActive": cutoff,
        }


INPUTS = (
    Port("flow", "REAL"),
    Port("cycleTime", "TIME"),
    Port("lowFlowCutoff", "REAL"),
    Port("enable", "BOOL"),
    Port("reset", "BOOL"),
    Port("pulseVolume", "REAL"),
)
OUTPUTS = (
    Port("total", "LREAL", 1e-6),
    Port("lifetimeTotal", "LREAL", 1e-6),
    Port("pulseCount", "DINT"),
    Port("pulse", "BOOL"),
    Port("cutoffActive", "BOOL"),
)
DEFAULTS: dict[str, Value] = {
    "flow": 0.0,
    "cycleTime": 100,
    "lowFlowCutoff": 0.5,
    "enable": True,
    "reset": False,
    "pulseVolume": 1.0,
}

SCENARIOS = (
    Scenario(
        "IntegrationAndPulses",
        "450 м3/ч за 1 с = 0.125 м3; импульс на каждые 0.5 м3",
        [
            Row(0, {"flow": 450.0, "cycleTime": 1000, "pulseVolume": 0.5}, "0.125 м3"),
            Row(1000, {}, "0.25 м3"),
            Row(2000, {}, "0.375 м3"),
            Row(3000, {}, "0.5 м3: импульс №1"),
            Row(4000, {}, "0.625 м3, импульса нет"),
            Row(5000, {}, "0.75 м3"),
            Row(6000, {}, "0.875 м3"),
            Row(7000, {}, "1.0 м3: импульс №2"),
            Row(8000, {"flow": 900.0}, "900 м3/ч: +0.25 м3 = 1.25"),
            Row(9000, {}, "1.5 м3: импульс №3"),
        ],
    ),
    Scenario(
        "CutoffAndEnable",
        "Отсечка малых и обратных расходов, запрет интегрирования",
        [
            Row(0, {"flow": 0.25, "cycleTime": 1000}, "0.25 < отсечки 0.5: не считается"),
            Row(1000, {"flow": -10.0}, "обратный расход ниже отсечки: не считается"),
            Row(2000, {"flow": 450.0, "enable": False}, "интегрирование запрещено (отсечка не активна)"),
            Row(3000, {"enable": True}, "разрешено: 0.125 м3"),
            Row(4000, {"flow": 0.5}, "0.5 = отсечке — считается: +0.5/3600 м3"),
            Row(5000, {"flow": 0.49}, "0.49 < 0.5: не считается"),
        ],
    ),
    Scenario(
        "ResetLevel",
        "Сброс уровнем: сменный счётчик держится в нуле, общий объём считает дальше",
        [
            Row(0, {"flow": 900.0, "cycleTime": 1000}, "0.25 м3"),
            Row(1000, {}, "0.5 м3"),
            Row(2000, {"reset": True}, "сброс: total 0, общий 0.75"),
            Row(3000, {}, "сброс держится: total 0, общий 1.0"),
            Row(4000, {"reset": False}, "сброс снят: total 0.25, общий 1.25"),
            Row(5000, {}, "0.5"),
            Row(6000, {}, "0.75"),
            Row(7000, {}, "1.0 м3 после сброса: импульс №1"),
        ],
    ),
    Scenario(
        "VariableCycleTime",
        "Приращение пропорционально cycleTime каждого вызова",
        [
            Row(0, {"flow": 450.0, "cycleTime": 500, "pulseVolume": 0.5}, "0.5 с: 0.0625 м3"),
            Row(500, {}, "0.125 м3"),
            Row(2500, {"cycleTime": 2000}, "2 с: +0.25 = 0.375 м3"),
            Row(2600, {"cycleTime": 100}, "0.1 с: +0.0125 = 0.3875 м3"),
            Row(2700, {}, "0.4 м3, до импульса 0.1 м3"),
        ],
    ),
    Scenario(
        "LargeStepPulsesCatchUp",
        "Приращение больше pulseVolume: не больше одного импульса за вызов",
        [
            Row(
                0,
                {"flow": 3600.0, "cycleTime": 1000, "pulseVolume": 0.5},
                "+1.0 м3 за вызов: импульс №1, остаток 0.5",
            ),
            Row(1000, {}, "2.0 м3: импульс №2, остаток 1.0"),
            Row(2000, {"flow": 0.0}, "расход 0: импульс №3 из остатка, остаток 0.5"),
            Row(3000, {}, "импульс №4, остаток 0"),
            Row(4000, {}, "импульсов нет: 4 x 0.5 = 2.0 м3"),
        ],
    ),
    Scenario(
        "PulseVolumeZero",
        "pulseVolume = 0: импульсы выключены",
        [
            Row(0, {"flow": 3600.0, "cycleTime": 1000, "pulseVolume": 0.0}, "1.0 м3, импульсов нет"),
            Row(1000, {}, "2.0 м3, импульсов нет"),
        ],
    ),
)

BLOCK = BlockScenarios(
    block="FB_Totalizer",
    source="samples/scl/FB_Totalizer.scl",
    description="Счётчик объёма: интегрирование расхода с периодом cycleTime, отсечка, импульсы",
    inputs=INPUTS,
    outputs=OUTPUTS,
    defaults=DEFAULTS,
    factory=TotalizerModel,
    scenarios=SCENARIOS,
    period_input="cycleTime",
    timed=False,
)
