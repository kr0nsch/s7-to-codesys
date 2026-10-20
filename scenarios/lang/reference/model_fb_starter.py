"""Эталонная модель и сценарии FB_Starter — пускателя на четырёх языках (LAD, FBD, STL, SCL).

Источник логики — описание в комментарии блоков samples/lang/FB_Starter*.xml (тот же текст —
samples/lang/README.md и STARTER_DESCRIPTION в samples/lang/blocks.py), пункты 1–4. Один CSV —
scenarios/lang/FB_Starter.csv — проверяет все четыре перевода (алиасы — scenarios/lang/aliases.json).
"""

from __future__ import annotations

from collections.abc import Mapping

from scenario_lib import BlockScenarios, Clock, Port, Row, Scenario, Ton, Value

INT_MIN, INT_SPAN = -32768, 65536


class StarterModel:
    def __init__(self) -> None:
        self.run_mem = False
        self.edge_mem = False
        self.fault = False
        self.starts = 0
        self.ton = Ton()

    def step(self, clock: Clock, i: Mapping[str, Value]) -> dict[str, Value]:
        start, stop, interlock = bool(i["xStart"]), bool(i["xStop"]), bool(i["xInterlock"])
        # 1. SR S7 с битом xRunMem: сначала S, затем R1 — сброс главнее; xFault — прошлого вызова
        if start and interlock:
            self.run_mem = True
        if stop or not interlock or self.fault:
            self.run_mem = False
        run = self.run_mem
        # 2. контроль обратной связи
        self.ton(clock, run and not bool(i["xFeedback"]), int(i["tFeedbackTime"]))
        # 3. авария с самоподхватом
        self.fault = (self.ton.q or self.fault) and not bool(i["xReset"])
        # 4. счётчик пусков по фронту xRun (Int с переносом)
        if run and not self.edge_mem:
            self.starts = (self.starts + 1 - INT_MIN) % INT_SPAN + INT_MIN
        self.edge_mem = run
        return {"xRun": run, "xFault": self.fault, "iStarts": self.starts}


INPUTS = (
    Port("xStart", "BOOL"),
    Port("xStop", "BOOL"),
    Port("xInterlock", "BOOL"),
    Port("xFeedback", "BOOL"),
    Port("tFeedbackTime", "TIME"),
    Port("xReset", "BOOL"),
)
OUTPUTS = (Port("xRun", "BOOL"), Port("xFault", "BOOL"), Port("iStarts", "INT"))
DEFAULTS: dict[str, Value] = {
    "xStart": False,
    "xStop": False,
    "xInterlock": True,
    "xFeedback": False,
    "tFeedbackTime": 2000,
    "xReset": False,
}

SCENARIOS = (
    Scenario(
        "StartStop",
        "Пуск кнопкой, работа с обратной связью, стоп",
        [
            Row(0, {}, "покой"),
            Row(100, {"xStart": True}, "Пуск: SR установлен, пуск №1"),
            Row(200, {"xStart": False, "xFeedback": True}, "кнопка отпущена, обратная связь: работает"),
            Row(1000, {"xStop": True}, "Стоп: SR сброшен"),
            Row(1100, {"xStop": False, "xFeedback": False}, "стоп отпущен: остаётся выключенным"),
        ],
    ),
    Scenario(
        "StartAndStopTogether",
        "Пуск и Стоп одновременно: SR S7 — сброс главнее (S = R1 = 1)",
        [
            Row(0, {}, "покой"),
            Row(100, {"xStart": True, "xStop": True}, "S = R1 = 1: не включается"),
            Row(200, {"xStop": False}, "Стоп отпущен, Пуск держится: включается, пуск №1"),
            Row(300, {"xStart": False, "xFeedback": True}, "работает"),
            Row(400, {"xStart": True, "xStop": True}, "в работе снова S = R1 = 1: выключается"),
            Row(500, {"xStart": False, "xStop": False, "xFeedback": False}, "выключен"),
        ],
    ),
    Scenario(
        "InterlockBlocksStart",
        "Блокировка не в норме: пуск не проходит и не запоминается",
        [
            Row(0, {"xInterlock": False}, "блокировка"),
            Row(100, {"xStart": True}, "Пуск при блокировке: не включается"),
            Row(200, {"xStart": False}, "кнопка отпущена"),
            Row(300, {"xInterlock": True}, "блокировка снята: пуск не запомнен"),
            Row(400, {"xStart": True}, "новый Пуск: включается, пуск №1"),
        ],
    ),
    Scenario(
        "InterlockDropStops",
        "Потеря блокировки в работе выключает насос",
        [
            Row(0, {"xStart": True}, "Пуск, пуск №1"),
            Row(100, {"xStart": False, "xFeedback": True}, "работает"),
            Row(500, {"xInterlock": False}, "блокировка пропала: выключается"),
            Row(600, {"xInterlock": True, "xFeedback": False}, "блокировка вернулась: остаётся выключенным"),
        ],
    ),
    Scenario(
        "FeedbackOk",
        "Обратная связь пришла раньше tFeedbackTime: аварии нет",
        [
            Row(0, {}, "покой"),
            Row(100, {"xStart": True}, "Пуск, таймер обратной связи с 0.1 с"),
            Row(1000, {"xStart": False, "xFeedback": True}, "обратная связь через 0.9 с"),
            Row(5000, {}, "работает, аварии нет"),
        ],
    ),
    Scenario(
        "FeedbackTimeout",
        "Нет обратной связи tFeedbackTime: авария, насос выключается следующим вызовом",
        [
            Row(0, {}, "покой"),
            Row(100, {"xStart": True}, "Пуск без обратной связи, таймер с 0.1 с"),
            Row(1900, {"xStart": False}, "1.8 с < 2 с: аварии нет"),
            Row(2100, {}, "2.0 с = tFeedbackTime: авария; xRun ещё TRUE (сеть 1 раньше сети 3)", boundary=True),
            Row(2300, {}, "R1 = xFault: насос выключен, авария держится"),
            Row(3000, {}, "авария держится (самоподхват)"),
        ],
    ),
    Scenario(
        "FaultResetAndBlock",
        "Авария блокирует пуск до сброса; после сброса пуск снова проходит",
        [
            Row(0, {"xStart": True}, "Пуск без обратной связи, пуск №1"),
            Row(100, {"xStart": False}, "ждём"),
            Row(2400, {}, "2.4 с: авария"),
            Row(2600, {"xStart": True}, "Пуск при аварии: R1 = 1 главнее — не включается"),
            Row(2700, {"xStart": False, "xReset": True}, "сброс: авария снята"),
            Row(2800, {"xReset": False, "xStart": True}, "Пуск: включается, пуск №2"),
            Row(2900, {"xStart": False, "xFeedback": True}, "обратная связь: работает без аварии"),
        ],
    ),
    Scenario(
        "StartCounter",
        "Счётчик пусков считает только фронты xRun",
        [
            Row(0, {"xStart": True, "xFeedback": True}, "пуск №1"),
            Row(100, {}, "Пуск держится: без нового счёта"),
            Row(200, {"xStart": False, "xStop": True}, "стоп"),
            Row(300, {"xStop": False, "xStart": True}, "пуск №2"),
            Row(400, {"xStart": False, "xStop": True}, "стоп"),
            Row(500, {"xStop": False}, "покой: 2 пуска"),
        ],
    ),
    Scenario(
        "ResetWhileRunning",
        "Сброс без аварии ничего не меняет; повторный Пуск в работе не считается",
        [
            Row(0, {"xStart": True, "xFeedback": True}, "пуск №1"),
            Row(100, {"xStart": False, "xReset": True}, "сброс в работе: без изменений"),
            Row(200, {"xReset": False, "xStart": True}, "Пуск в работе: SR уже установлен, счёта нет"),
            Row(300, {"xStart": False}, "работает"),
        ],
    ),
)

BLOCK = BlockScenarios(
    block="FB_Starter",
    source="samples/lang/FB_Starter*.xml",
    description="пускатель насоса: SR с операндом, TON обратной связи, авария с самоподхватом, P-фронт счётчика",
    inputs=INPUTS,
    outputs=OUTPUTS,
    defaults=DEFAULTS,
    factory=StarterModel,
    scenarios=SCENARIOS,
)
