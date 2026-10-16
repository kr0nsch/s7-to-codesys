"""Эталонная модель и сценарии FB_Sequencer.

Источник логики — нормативное описание в заголовке samples/scl/FB_Sequencer.scl
(пункты 1–3). stepTime — время с вызова, на котором шаг стал текущим; переходы
по времени сравнивают stepTime с параметром (>=) в момент вызова.
"""

from __future__ import annotations

from collections.abc import Mapping

from scenario_lib import BlockScenarios, Clock, Port, Row, RTrig, Scenario, Value

STEP_IDLE = 0
STEP_DRAIN = 10
STEP_AIR_SCOUR = 20
STEP_BACKWASH = 30
STEP_REFILL = 40
STEP_FAULT = 90
RUNNING_STEPS = (STEP_DRAIN, STEP_AIR_SCOUR, STEP_BACKWASH, STEP_REFILL)
STEP_TEXT = {
    STEP_IDLE: "IDLE",
    STEP_DRAIN: "DRAIN",
    STEP_AIR_SCOUR: "AIR SCOUR",
    STEP_BACKWASH: "BACKWASH",
    STEP_REFILL: "REFILL",
    STEP_FAULT: "FAULT",
}


class SequencerModel:
    def __init__(self) -> None:
        self.step_no = STEP_IDLE
        self.step_start_ms = 0
        self.fault_step = 0
        self.cycle_count = 0
        self.edge_start = RTrig()
        self.edge_reset = RTrig()

    def step(self, clock: Clock, i: Mapping[str, Value]) -> dict[str, Value]:
        self.edge_start(bool(i["start"]))
        self.edge_reset(bool(i["reset"]))
        stop = bool(i["stop"])
        entry = self.step_no
        step_time = clock.now_ms - self.step_start_ms

        def elapsed(limit_name: str) -> bool:
            return clock.compare(step_time, int(i[limit_name]))

        new = entry
        if stop and entry in RUNNING_STEPS:
            new = STEP_IDLE
        elif entry == STEP_IDLE:
            if self.edge_start.q and bool(i["permissive"]) and not stop:
                new = STEP_DRAIN
        elif entry == STEP_DRAIN:
            if bool(i["levelLow"]):
                new = STEP_AIR_SCOUR
            elif elapsed("drainTimeout"):
                self.fault_step = STEP_DRAIN
                new = STEP_FAULT
        elif entry == STEP_AIR_SCOUR:
            if elapsed("airTime"):
                new = STEP_BACKWASH
        elif entry == STEP_BACKWASH:
            if elapsed("washTime"):
                new = STEP_REFILL
        elif entry == STEP_REFILL:
            if bool(i["levelHigh"]):
                self.cycle_count += 1
                new = STEP_IDLE
            elif elapsed("refillTimeout"):
                self.fault_step = STEP_REFILL
                new = STEP_FAULT
        elif entry == STEP_FAULT:
            if self.edge_reset.q:
                self.fault_step = 0
                new = STEP_IDLE
        else:
            new = STEP_IDLE
        if new != entry:
            self.step_start_ms = clock.now_ms
        self.step_no = new
        return {
            "stepNo": new,
            "drainValve": new in (STEP_DRAIN, STEP_BACKWASH),
            "airBlower": new == STEP_AIR_SCOUR,
            "washPump": new == STEP_BACKWASH,
            "inletValve": new == STEP_REFILL,
            "busy": new in RUNNING_STEPS,
            "fault": new == STEP_FAULT,
            "faultStep": self.fault_step,
            "cycleCount": self.cycle_count,
            "stepText": STEP_TEXT[new],
        }


INPUTS = (
    Port("start", "BOOL"),
    Port("stop", "BOOL"),
    Port("permissive", "BOOL"),
    Port("levelLow", "BOOL"),
    Port("levelHigh", "BOOL"),
    Port("reset", "BOOL"),
    Port("drainTimeout", "TIME"),
    Port("airTime", "TIME"),
    Port("washTime", "TIME"),
    Port("refillTimeout", "TIME"),
)
OUTPUTS = (
    Port("stepNo", "INT"),
    Port("drainValve", "BOOL"),
    Port("airBlower", "BOOL"),
    Port("washPump", "BOOL"),
    Port("inletValve", "BOOL"),
    Port("busy", "BOOL"),
    Port("fault", "BOOL"),
    Port("faultStep", "INT"),
    Port("cycleCount", "DINT"),
    Port("stepText", "STRING"),
)
DEFAULTS: dict[str, Value] = {
    "start": False,
    "stop": False,
    "permissive": False,
    "levelLow": False,
    "levelHigh": False,
    "reset": False,
    "drainTimeout": 60000,
    "airTime": 30000,
    "washTime": 40000,
    "refillTimeout": 90000,
}

SCENARIOS = (
    Scenario(
        "FullCycle",
        "Полный цикл промывки; переходы по времени — в первой строке после порога",
        [
            Row(0, {"permissive": True}, "ожидание"),
            Row(1000, {"start": True}, "пуск: опорожнение, шаг 10 с 1.0 с"),
            Row(1500, {"start": False}, "опорожнение"),
            Row(21000, {"levelLow": True}, "фильтр опорожнён: продувка, шаг 20 с 21.0 с"),
            Row(50800, {}, "продувка 29.8 с < 30 с"),
            Row(51200, {}, "30.2 с: промывка, шаг 30 с 51.2 с"),
            Row(91000, {"levelLow": False}, "промывка 39.8 с < 40 с"),
            Row(91400, {}, "40.2 с: заполнение, шаг 40 с 91.4 с"),
            Row(150000, {}, "заполнение 58.6 с, уровня нет"),
            Row(160000, {"levelHigh": True}, "фильтр заполнен: цикл №1 завершён"),
            Row(161000, {}, "ожидание, повторного пуска без фронта start нет"),
        ],
    ),
    Scenario(
        "DrainTimeout",
        "Нет опорожнения за drainTimeout: авария, сброс",
        [
            Row(0, {"permissive": True}, "ожидание"),
            Row(1000, {"start": True}, "пуск: опорожнение с 1.0 с"),
            Row(60800, {"start": False}, "59.8 с < 60 с: опорожнение"),
            Row(61200, {}, "60.2 с: авария на шаге 10, всё закрыто"),
            Row(65000, {"start": True}, "пуск во время аварии не действует"),
            Row(70000, {"start": False, "reset": True}, "сброс: ожидание, faultStep 0"),
            Row(71000, {"reset": False}, "ожидание"),
        ],
    ),
    Scenario(
        "AbortByStop",
        "Прерывание stop из рабочего шага; пуск при stop запрещён",
        [
            Row(0, {"permissive": True}, "ожидание"),
            Row(1000, {"start": True}, "пуск: опорожнение"),
            Row(5000, {"start": False, "levelLow": True}, "продувка с 5.0 с"),
            Row(10000, {"stop": True}, "прерывание: ожидание, без аварии и без счёта"),
            Row(11000, {"start": True}, "фронт start при stop: не запускается"),
            Row(12000, {"start": False, "stop": False}, "stop снят"),
            Row(13000, {"start": True}, "новый фронт start: опорожнение"),
        ],
    ),
    Scenario(
        "PermissiveMissing",
        "Без разрешения пуск не проходит; нужен новый фронт start",
        [
            Row(0, {}, "разрешения нет"),
            Row(1000, {"start": True}, "фронт start без разрешения: ожидание"),
            Row(2000, {"permissive": True}, "разрешение есть, start держится — фронта нет"),
            Row(3000, {"start": False}, "start отпущен"),
            Row(4000, {"start": True}, "новый фронт: опорожнение"),
        ],
    ),
    Scenario(
        "DrainTimeoutBoundary",
        "Авария ровно при stepTime = drainTimeout (>=)",
        [
            Row(0, {"permissive": True, "start": True}, "пуск в первом вызове: опорожнение с 0 с"),
            Row(59800, {"start": False}, "59.8 с: опорожнение"),
            Row(60000, {}, "60.0 с = drainTimeout: авария", boundary=True),
            Row(60200, {}, "авария"),
        ],
    ),
    Scenario(
        "RefillTimeoutBoundary",
        "Заполнение не завершилось за refillTimeout; укороченные времена шагов",
        [
            Row(
                0,
                {"permissive": True, "start": True, "airTime": 5000, "washTime": 5000, "refillTimeout": 10000},
                "пуск: опорожнение; продувка и промывка по 5 с, заполнение до 10 с",
            ),
            Row(1000, {"start": False, "levelLow": True}, "продувка с 1.0 с"),
            Row(6400, {"levelLow": False}, "5.4 с: промывка с 6.4 с"),
            Row(11800, {}, "5.4 с: заполнение с 11.8 с"),
            Row(21600, {}, "9.8 с < 10 с: заполнение"),
            Row(21800, {}, "10.0 с = refillTimeout: авария на шаге 40", boundary=True),
            Row(22000, {}, "авария"),
            Row(23000, {"reset": True}, "сброс"),
        ],
    ),
)

BLOCK = BlockScenarios(
    block="FB_Sequencer",
    source="samples/scl/FB_Sequencer.scl",
    description="Шаговая программа промывки фильтра: CASE, время шага, аварии по времени",
    inputs=INPUTS,
    outputs=OUTPUTS,
    defaults=DEFAULTS,
    factory=SequencerModel,
    scenarios=SCENARIOS,
)
