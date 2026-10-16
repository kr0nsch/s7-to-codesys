"""Эталонная модель и сценарии FB_Motor.

Источник логики — нормативное описание в заголовке samples/scl/FB_Motor.scl
(пункты 1–8, правило «первая авария»).
"""

from __future__ import annotations

from collections.abc import Mapping

from scenario_lib import BlockScenarios, Clock, Port, Row, RTrig, Scenario, Ton, Value

FAULT_NONE = 0
FAULT_NO_FEEDBACK = 1
FAULT_FEEDBACK_LOST = 2
FAULT_THERMAL = 3
FAULT_UNEXPECTED_FEEDBACK = 4


class MotorModel:
    def __init__(self) -> None:
        self.fault = False
        self.fault_code = FAULT_NONE
        self.man_run = False
        self.feedback_seen = False
        self.start_count = 0
        self.ton_feedback = Ton()
        self.edge_reset = RTrig()
        self.edge_run = RTrig()

    def step(self, clock: Clock, i: Mapping[str, Value]) -> dict[str, Value]:
        auto = bool(i["autoMode"])
        auto_start = bool(i["autoStart"])
        feedback = bool(i["feedback"])
        thermal_ok = bool(i["thermalOk"])
        # 1. Сброс по фронту
        self.edge_reset(bool(i["reset"]))
        if self.edge_reset.q and thermal_ok:
            self.fault = False
            self.fault_code = FAULT_NONE
        # 2. Тепловая защита
        if not thermal_ok and not self.fault:
            self.fault = True
            self.fault_code = FAULT_THERMAL
        # 3. Ручная защёлка
        if auto:
            self.man_run = auto_start
        elif bool(i["manStop"]) or self.fault:
            self.man_run = False
        elif bool(i["manStart"]):
            self.man_run = True
        # 4. Запрос и команда
        demand = auto_start if auto else self.man_run
        run_cmd = demand and not self.fault
        # 5. Обратная связь была
        if not run_cmd:
            self.feedback_seen = False
        elif feedback:
            self.feedback_seen = True
        # 6. Рассогласование
        self.ton_feedback(clock, run_cmd != feedback, int(i["feedbackTime"]))
        if self.ton_feedback.q and not self.fault:
            self.fault = True
            if not run_cmd:
                self.fault_code = FAULT_UNEXPECTED_FEEDBACK
            elif self.feedback_seen:
                self.fault_code = FAULT_FEEDBACK_LOST
            else:
                self.fault_code = FAULT_NO_FEEDBACK
            run_cmd = False
        # 7. Счётчик пусков
        self.edge_run(run_cmd)
        if self.edge_run.q:
            self.start_count += 1
        # 8. Выходы
        return {
            "runCmd": run_cmd,
            "fault": self.fault,
            "status.running": run_cmd and feedback,
            "status.fault": self.fault,
            "status.autoMode": auto,
            "status.faultCode": self.fault_code,
            "status.startCount": self.start_count,
        }


INPUTS = (
    Port("autoMode", "BOOL"),
    Port("autoStart", "BOOL"),
    Port("manStart", "BOOL"),
    Port("manStop", "BOOL"),
    Port("feedback", "BOOL"),
    Port("thermalOk", "BOOL"),
    Port("reset", "BOOL"),
    Port("feedbackTime", "TIME"),
)
OUTPUTS = (
    Port("runCmd", "BOOL"),
    Port("fault", "BOOL"),
    Port("status.running", "BOOL"),
    Port("status.fault", "BOOL"),
    Port("status.autoMode", "BOOL"),
    Port("status.faultCode", "INT"),
    Port("status.startCount", "DINT"),
)
DEFAULTS: dict[str, Value] = {
    "autoMode": False,
    "autoStart": False,
    "manStart": False,
    "manStop": False,
    "feedback": False,
    "thermalOk": True,
    "reset": False,
    "feedbackTime": 3000,
}

SCENARIOS = (
    Scenario(
        "AutoStartOk",
        "Пуск и останов в авто, обратная связь в пределах feedbackTime",
        [
            Row(0, {"autoMode": True}, "авто, команды нет"),
            Row(100, {"autoStart": True}, "пуск: runCmd, пуск №1; таймер рассогласования запущен"),
            Row(1100, {"feedback": True}, "обратная связь через 1 с: работает"),
            Row(5000, {}, "работает, аварии нет"),
            Row(5100, {"autoStart": False}, "стоп: runCmd снят, контактор ещё держит — рассогласование"),
            Row(6000, {"feedback": False}, "обратная связь пропала через 0.9 с — нормальный останов"),
            Row(9500, {}, "покой"),
        ],
    ),
    Scenario(
        "NoFeedbackTimeout",
        "Нет обратной связи после пуска: авария 1 ровно через feedbackTime",
        [
            Row(0, {"autoMode": True, "autoStart": True}, "пуск, обратной связи нет"),
            Row(2800, {}, "2.8 с < 3 с: аварии нет"),
            Row(3000, {}, "3.0 с = feedbackTime: авария 1, runCmd снят в этом же вызове", boundary=True),
            Row(3200, {}, "авария держится, код 1"),
            Row(4000, {"reset": True}, "сброс по фронту: авто-запрос ещё есть — повторный пуск №2"),
            Row(4500, {"reset": False, "feedback": True}, "обратная связь пришла: работает"),
            Row(8000, {}, "работает"),
            Row(8100, {"autoStart": False}, "стоп"),
            Row(8300, {"feedback": False}, "контактор отпал"),
        ],
    ),
    Scenario(
        "FeedbackLost",
        "Обратная связь пропала в работе: авария 2",
        [
            Row(0, {"autoMode": True, "autoStart": True}, "пуск"),
            Row(500, {"feedback": True}, "обратная связь есть"),
            Row(10000, {"feedback": False}, "обратная связь пропала; отсчёт с 10.0 с"),
            Row(12800, {}, "2.8 с без обратной связи: аварии нет"),
            Row(13200, {}, "3.2 с: авария 2 (обратная связь уже была), runCmd снят"),
            Row(14000, {"autoStart": False, "reset": True}, "сброс, запроса нет — стоит без аварии"),
            Row(14500, {"reset": False}, "покой"),
        ],
    ),
    Scenario(
        "UnexpectedFeedback",
        "Обратная связь без команды (залип контактор): авария 4 и повторная постановка при сбросе",
        [
            Row(0, {"autoMode": True, "feedback": True}, "команды нет, обратная связь есть"),
            Row(3200, {}, "3.2 с: авария 4"),
            Row(4000, {"reset": True}, "сброс: таймер всё ещё в Q — авария 4 снова в том же вызове"),
            Row(4500, {"reset": False, "feedback": False}, "контактор отпал, авария держится"),
            Row(5000, {"reset": True}, "сброс: авария снята"),
            Row(5500, {"reset": False, "autoStart": True}, "пуск №1"),
            Row(6000, {"feedback": True}, "работает"),
        ],
    ),
    Scenario(
        "ThermalTripManual",
        "Ручной режим, тепловая защита, приоритет стопа",
        [
            Row(0, {}, "ручной режим, покой"),
            Row(100, {"manStart": True}, "пуск оператором: пуск №1"),
            Row(200, {"manStart": False, "feedback": True}, "работает"),
            Row(1000, {"thermalOk": False}, "тепловая защита: авария 3, ручная защёлка сброшена"),
            Row(1500, {"feedback": False}, "контактор отпал"),
            Row(2000, {"reset": True}, "сброс при сработавшем реле не действует"),
            Row(2500, {"reset": False, "thermalOk": True}, "реле вернулось, авария держится до сброса"),
            Row(3000, {"reset": True}, "сброс: авария снята, насос не стартует сам"),
            Row(3500, {"reset": False, "manStart": True}, "новый пуск оператором: пуск №2"),
            Row(3600, {"manStop": True}, "стоп и пуск одновременно: стоп приоритетнее"),
            Row(3700, {"manStop": False, "manStart": False}, "покой"),
        ],
    ),
    Scenario(
        "BumplessAutoToManual",
        "Переход авто -> ручной без останова, ручной -> авто по команде авто",
        [
            Row(0, {"autoMode": True, "autoStart": True}, "авто, пуск №1"),
            Row(500, {"feedback": True}, "работает"),
            Row(1000, {"autoMode": False}, "в ручной: защёлка следила за авто — продолжает работать"),
            Row(2000, {"manStop": True}, "стоп оператором"),
            Row(2500, {"manStop": False, "feedback": False}, "остановлен"),
            Row(3000, {"autoMode": True, "autoStart": False}, "в авто без запроса"),
            Row(3500, {"autoStart": True}, "запрос авто: пуск №2"),
            Row(4000, {"feedback": True}, "работает"),
        ],
    ),
    Scenario(
        "CustomFeedbackTime",
        "feedbackTime = 5 с из экземплярного DB: обратная связь через 4.5 с допустима",
        [
            Row(0, {"autoMode": True, "autoStart": True, "feedbackTime": 5000}, "пуск, feedbackTime 5 с"),
            Row(4500, {"feedback": True}, "обратная связь через 4.5 с — аварии нет"),
            Row(6000, {}, "работает"),
        ],
    ),
)

BLOCK = BlockScenarios(
    block="FB_Motor",
    source="samples/scl/FB_Motor.scl",
    description="Насос: авто/ручной, контроль обратной связи, тепловая защита, счётчик пусков",
    inputs=INPUTS,
    outputs=OUTPUTS,
    defaults=DEFAULTS,
    factory=MotorModel,
    scenarios=SCENARIOS,
)
