"""Эталонная модель и сценарии FB_AlarmDelay.

Источник логики — нормативное описание в заголовке samples/scl/FB_AlarmDelay.scl
(пункты 1–8: квитирование раньше фронта появления).
"""

from __future__ import annotations

from collections.abc import Mapping

from scenario_lib import BlockScenarios, Clock, Port, Row, RTrig, Scenario, Tof, Ton, Value


class AlarmDelayModel:
    def __init__(self) -> None:
        self.ton_on = Ton()
        self.tof_off = Tof()
        self.edge_ack = RTrig()
        self.edge_active = RTrig()
        self.unacked = False
        self.count = 0

    def step(self, clock: Clock, i: Mapping[str, Value]) -> dict[str, Value]:
        enable = bool(i["enable"])
        self.edge_ack(bool(i["ack"]))
        self.ton_on(clock, bool(i["condition"]) and enable, int(i["onDelay"]))
        self.tof_off(clock, self.ton_on.q, int(i["offDelay"]))
        active = self.tof_off.q and enable
        if self.edge_ack.q:
            self.unacked = False
        self.edge_active(active)
        if self.edge_active.q:
            self.unacked = True
            self.count += 1
        if not enable:
            self.unacked = False
        if active and self.unacked:
            state = 1
        elif active:
            state = 2
        elif self.unacked:
            state = 3
        else:
            state = 0
        return {
            "active": active,
            "unacked": self.unacked,
            "alarm": active or self.unacked,
            "state": state,
            "count": self.count,
        }


INPUTS = (
    Port("condition", "BOOL"),
    Port("enable", "BOOL"),
    Port("ack", "BOOL"),
    Port("onDelay", "TIME"),
    Port("offDelay", "TIME"),
)
OUTPUTS = (
    Port("active", "BOOL"),
    Port("unacked", "BOOL"),
    Port("alarm", "BOOL"),
    Port("state", "INT"),
    Port("count", "DINT"),
)
DEFAULTS: dict[str, Value] = {
    "condition": False,
    "enable": True,
    "ack": False,
    "onDelay": 5000,
    "offDelay": 2000,
}

SCENARIOS = (
    Scenario(
        "ActivateAckClear",
        "Появление через onDelay, квитирование, снятие через offDelay",
        [
            Row(0, {}, "норма"),
            Row(1000, {"condition": True}, "условие появилось; отсчёт onDelay с 1.0 с"),
            Row(5800, {}, "4.8 с < 5 с: ещё не активен"),
            Row(6000, {}, "5.0 с = onDelay: активен, не квитирован, появление №1", boundary=True),
            Row(6200, {}, "активен, не квитирован"),
            Row(7000, {"ack": True}, "квитирование: активен, квитирован"),
            Row(7500, {"ack": False}, "кнопка отпущена"),
            Row(9000, {"condition": False}, "условие пропало; отсчёт offDelay с 9.0 с, сигнал держится"),
            Row(10800, {}, "1.8 с < 2 с: ещё активен"),
            Row(11000, {}, "2.0 с = offDelay: снят, квитирован — норма", boundary=True),
            Row(11200, {}, "норма"),
        ],
    ),
    Scenario(
        "ClearedBeforeAck",
        "Сигнал снялся без квитирования: состояние 3 до квитирования",
        [
            Row(0, {"condition": True}, "условие"),
            Row(5200, {}, "активен, появление №1"),
            Row(6000, {"condition": False}, "условие пропало"),
            Row(8200, {}, "через 2.2 с снят, но не квитирован: состояние 3, индикация есть"),
            Row(9000, {"ack": True}, "квитирование: норма"),
            Row(9500, {"ack": False}, "норма"),
        ],
    ),
    Scenario(
        "ChatterSuppressed",
        "Короткие появления условия (меньше onDelay) не дают сигнала",
        [
            Row(0, {"condition": True}, "условие"),
            Row(3000, {"condition": False}, "пропало через 3 с"),
            Row(3500, {"condition": True}, "снова; отсчёт заново с 3.5 с"),
            Row(8000, {}, "4.5 с < 5 с: не активен"),
            Row(8300, {"condition": False}, "пропало"),
            Row(9000, {}, "появлений нет"),
        ],
    ),
    Scenario(
        "ReturnDuringOffDelay",
        "Условие вернулось во время offDelay: сигнал не снимается, нового появления нет",
        [
            Row(0, {"condition": True, "offDelay": 6000}, "условие, offDelay 6 с"),
            Row(5200, {}, "активен, появление №1"),
            Row(5500, {"ack": True}, "квитирован"),
            Row(6000, {"ack": False, "condition": False}, "условие пропало; offDelay с 6.0 с"),
            Row(7000, {"condition": True}, "условие вернулось; onDelay заново с 7.0 с"),
            Row(11800, {}, "onDelay 4.8 с, offDelay 5.8 с: ещё активен по задержке снятия"),
            Row(12200, {}, "onDelay истёк раньше offDelay: активен без перерыва, счёт не растёт"),
            Row(13000, {"condition": False}, "условие пропало; offDelay с 13.0 с"),
            Row(19200, {}, "6.2 с: снят — норма"),
        ],
    ),
    Scenario(
        "NewActivationAfterOffDelay",
        "Сигнал снялся и появился снова: появление №2, снова не квитирован",
        [
            Row(0, {"condition": True}, "условие"),
            Row(5200, {}, "активен, появление №1"),
            Row(6000, {"condition": False}, "условие пропало"),
            Row(7000, {"condition": True}, "вернулось; onDelay с 7.0 с, offDelay ещё идёт"),
            Row(8200, {}, "offDelay 2.2 с истёк: снят, не квитирован — состояние 3"),
            Row(12200, {}, "onDelay 5.2 с: активен снова, появление №2"),
            Row(13000, {"ack": True}, "квитирование"),
        ],
    ),
    Scenario(
        "Disabled",
        "Вывод сигнала из работы снимает его сразу; после ввода — отсчёт заново",
        [
            Row(0, {"condition": True}, "условие"),
            Row(5200, {}, "активен, появление №1"),
            Row(6000, {"enable": False}, "выведен из работы: active и unacked сброшены сразу"),
            Row(7000, {}, "выведен"),
            Row(8500, {}, "выведен (задержка снятия внутри уже истекла)"),
            Row(9000, {"enable": True}, "введён: условие есть, onDelay с 9.0 с"),
            Row(14200, {}, "5.2 с: активен, появление №2"),
        ],
    ),
    Scenario(
        "AckSameCallAsActivation",
        "Фронт квитирования в вызове появления не квитирует новый сигнал",
        [
            Row(0, {"condition": True}, "условие"),
            Row(5200, {"ack": True}, "появление и фронт ack в одном вызове: не квитирован"),
            Row(5400, {"ack": False}, "не квитирован"),
            Row(5600, {"ack": True}, "квитирован"),
        ],
    ),
    Scenario(
        "AckHeldDuringActivation",
        "Квитирование — по фронту: кнопка, нажатая до появления и удерживаемая, новый сигнал не квитирует",
        [
            Row(0, {"condition": True, "ack": True}, "условие; кнопка нажата заранее — фронт ack до появления"),
            Row(5200, {}, "появление №1 при удерживаемой кнопке: не квитирован"),
            Row(5400, {}, "кнопка всё ещё нажата, фронта нет: не квитирован"),
            Row(5600, {"ack": False}, "кнопка отпущена"),
            Row(5800, {"ack": True}, "новый фронт: квитирован"),
        ],
    ),
)

BLOCK = BlockScenarios(
    block="FB_AlarmDelay",
    source="samples/scl/FB_AlarmDelay.scl",
    description="Сигнализация: задержки появления и снятия, квитирование, состояния ISA-18.2",
    inputs=INPUTS,
    outputs=OUTPUTS,
    defaults=DEFAULTS,
    factory=AlarmDelayModel,
    scenarios=SCENARIOS,
)
