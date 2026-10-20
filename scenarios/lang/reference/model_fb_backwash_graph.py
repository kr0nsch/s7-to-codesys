"""Эталонная модель и сценарии FB_BackwashGraph — промывки фильтра на S7-GRAPH.

Источник логики — описание в комментарии блока samples/lang/FB_BackwashGraph.xml (BACKWASH_DESCRIPTION
в samples/lang/blocks.py) и модель цикла GRAPH из docs/ASSUMPTIONS.md (записи L18–L22): переходы — по
состоянию после INIT_SQ/OFF_SQ, затем действия активных шагов в том же вызове; N — пока шаг активен, при
выключении — 0; S/R — каждый цикл активности; D — по времени шага; событие S1 — один раз; ошибка контроля
держит шаг до ACK_EF. Модель не использует s7conv: третья запись той же семантики после ST-двойника и
эталона s7conv/semantics/graph_seq.py.
"""

from __future__ import annotations

from collections.abc import Mapping

from scenario_lib import BlockScenarios, Clock, Port, Row, Scenario, Value

STEPS = ("Idle", "Drain", "Air", "Rinse", "QuickRinse", "Refill")
AIR_DONE_MS = 10_000  # T4 AirDone: Air.T >= 10 с
AIR_VALVE_DELAY_MS = 2_000  # D xAirValve, T#2S


class BackwashModel:
    def __init__(self) -> None:
        self.active = dict.fromkeys(STEPS, False)
        self.since = dict.fromkeys(STEPS, 0)
        self.time = dict.fromkeys(STEPS, 0)
        self.started = False
        self.fault = False  # защёлка ошибки контроля шага Drain
        self.out: dict[str, Value] = {
            "xReady": False,
            "xDrainValve": False,
            "xBlower": False,
            "xAirValve": False,
            "xWashPump": False,
            "xInletValve": False,
            "xWashActive": False,
            "iWashCount": 0,
        }

    def step(self, clock: Clock, i: Mapping[str, Value]) -> dict[str, Value]:
        now = clock.now_ms
        act = self.active
        before = dict(act)
        init = not self.started or bool(i["INIT_SQ"])
        hold = init or bool(i["OFF_SQ"])
        if init:  # начальное состояние: только Idle, ошибок нет
            self.started = True
            for s in STEPS:
                act[s] = s == "Idle"
            self.fault = False
        if i["OFF_SQ"]:
            for s in STEPS:
                act[s] = False
        if i["ACK_EF"]:
            self.fault = False
        for s in STEPS:
            if act[s]:
                self.time[s] = now - self.since[s]
        if not hold:
            low, high, short = bool(i["xLevelLow"]), bool(i["xLevelHigh"]), bool(i["xShortWash"])
            air_done = clock.compare(self.time["Air"], AIR_DONE_MS) if act["Air"] and act["Rinse"] else False
            fire = {
                "Start": act["Idle"] and bool(i["xStart"]),
                "LongWash": act["Drain"] and low and not short and not self.fault,
            }
            fire["ShortWash"] = act["Drain"] and low and short and not self.fault and not fire["LongWash"]
            fire["AirDone"] = act["Air"] and act["Rinse"] and air_done
            fire["QuickDone"] = act["QuickRinse"] and high
            fire["Full"] = act["Refill"] and high
            off = {
                "Start": ("Idle",),
                "LongWash": ("Drain",),
                "ShortWash": ("Drain",),
                "AirDone": ("Air", "Rinse"),
                "QuickDone": ("QuickRinse",),
                "Full": ("Refill",),
            }
            on = {
                "Start": ("Drain",),
                "LongWash": ("Air", "Rinse"),
                "ShortWash": ("QuickRinse",),
                "AirDone": ("Refill",),
                "QuickDone": ("Refill",),
                "Full": ("Idle",),
            }
            for t, did in fire.items():
                if did:
                    for s in off[t]:
                        act[s] = False
            for t, did in fire.items():
                if did:
                    for s in on[t]:
                        act[s] = True
        rose = {s for s in STEPS if act[s] and not before[s]}
        fell = {s for s in STEPS if before[s] and not act[s]}
        for s in rose:
            self.since[s], self.time[s] = now, 0
        if act["Drain"] and i["xValveFault"]:  # контроль S2: защёлка до квитирования
            self.fault = True
        o = self.out
        # действия по порядку шагов: N — пока активен, при выключении 0; S/R — каждый цикл; D — по времени
        if act["Idle"] or "Idle" in fell:
            o["xReady"] = act["Idle"]
        if act["Drain"] or "Drain" in fell:
            o["xDrainValve"] = act["Drain"]
        if act["Drain"]:
            o["xWashActive"] = True
        if "Drain" in rose:
            o["iWashCount"] = int(o["iWashCount"]) + 1
        if act["Air"] or "Air" in fell:
            o["xBlower"] = act["Air"]
            delay = clock.compare(self.time["Air"], AIR_VALVE_DELAY_MS) if act["Air"] else False
            o["xAirValve"] = act["Air"] and delay
        if act["Rinse"] or "Rinse" in fell:
            o["xWashPump"] = act["Rinse"] and bool(i["xPumpOk"])
        if act["QuickRinse"] or "QuickRinse" in fell:
            o["xWashPump"] = act["QuickRinse"]
        if act["Refill"] or "Refill" in fell:
            o["xInletValve"] = act["Refill"]
        if act["Refill"]:
            o["xWashActive"] = False
        busy = bool(o["xDrainValve"]) or bool(o["xInletValve"])  # постоперация
        return {"ERR_FLT": self.fault, **o, "xValvesBusy": busy}


INPUTS = (
    Port("OFF_SQ", "BOOL"),
    Port("INIT_SQ", "BOOL"),
    Port("ACK_EF", "BOOL"),
    Port("xStart", "BOOL"),
    Port("xLevelLow", "BOOL"),
    Port("xLevelHigh", "BOOL"),
    Port("xShortWash", "BOOL"),
    Port("xPumpOk", "BOOL"),
    Port("xValveFault", "BOOL"),
)
OUTPUTS = (
    Port("ERR_FLT", "BOOL"),
    Port("xReady", "BOOL"),
    Port("xDrainValve", "BOOL"),
    Port("xBlower", "BOOL"),
    Port("xAirValve", "BOOL"),
    Port("xWashPump", "BOOL"),
    Port("xInletValve", "BOOL"),
    Port("xWashActive", "BOOL"),
    Port("xValvesBusy", "BOOL"),
    Port("iWashCount", "INT"),
)
DEFAULTS: dict[str, Value] = {
    "OFF_SQ": False,
    "INIT_SQ": False,
    "ACK_EF": False,
    "xStart": False,
    "xLevelLow": False,
    "xLevelHigh": False,
    "xShortWash": False,
    "xPumpOk": True,
    "xValveFault": False,
}


def _to_drain() -> list[Row]:
    return [
        Row(0, {}, "первый вызов: начальный шаг Idle"),
        Row(100, {"xStart": True}, "T1 Start: Drain, промывка №1, слив открыт"),
        Row(200, {"xStart": False}, "слив"),
    ]


SCENARIOS = (
    Scenario(
        "LongWash",
        "Длинная промывка: слив, параллельно продувка (D задвижки воздуха 2 с) и отмывка, 10 с, заполнение",
        [
            *_to_drain(),
            Row(1000, {"xLevelLow": True}, "T2 LongWash: параллельно Air и Rinse"),
            Row(1100, {"xLevelLow": False}, "воздуходувка и насос; задвижка воздуха ещё закрыта"),
            Row(3000, {}, "2 с продувки: задвижка воздуха открыта (D)", boundary=True),
            Row(10_700, {}, "9,7 с: синхронизация ещё не прошла"),
            Row(11_000, {}, "10 с: T4 AirDone — Refill, подача открыта", boundary=True),
            Row(11_500, {"xLevelHigh": True}, "T6 Full: прыжок к Idle"),
            Row(11_600, {"xLevelHigh": False}, "готов к новой промывке"),
        ],
    ),
    Scenario(
        "ShortWash",
        "Короткая промывка: альтернативная ветвь без продувки",
        [
            *_to_drain(),
            Row(1000, {"xLevelLow": True, "xShortWash": True}, "T3 ShortWash: QuickRinse"),
            Row(1100, {"xLevelLow": False}, "быстрая отмывка"),
            Row(2000, {"xLevelHigh": True}, "T5 QuickDone: Refill"),
            Row(2100, {}, "T6 Full: прыжок к Idle"),
            Row(2200, {"xLevelHigh": False, "xShortWash": False}, "готов"),
        ],
    ),
    Scenario(
        "Supervision",
        "Ошибка контроля в Drain держит шаг до квитирования; квитирование при ошибке — снова ошибка",
        [
            *_to_drain(),
            Row(500, {"xValveFault": True}, "неисправность задвижки: ERR_FLT"),
            Row(600, {"xLevelLow": True}, "уровень низкий, но переход заблокирован ошибкой"),
            Row(700, {"xLevelLow": False, "ACK_EF": True}, "квитирование при неисправности: ошибка сразу снова"),
            Row(800, {"ACK_EF": False, "xValveFault": False}, "неисправность ушла, ошибка держится"),
            Row(900, {"ACK_EF": True}, "квитирование: ошибка снята"),
            Row(1000, {"ACK_EF": False, "xLevelLow": True}, "T2 LongWash: Air и Rinse"),
        ],
    ),
    Scenario(
        "AckSwitches",
        "В цикле квитирования переход срабатывает, даже если условие контроля ещё истинно",
        [
            *_to_drain(),
            Row(500, {"xValveFault": True, "xShortWash": True}, "ошибка контроля"),
            Row(600, {"xLevelLow": True, "ACK_EF": True}, "квитирование и уровень: T3 ShortWash в том же вызове"),
            Row(700, {"ACK_EF": False, "xLevelLow": False}, "QuickRinse: контроль Drain больше не действует"),
        ],
    ),
    Scenario(
        "InterlockPump",
        "Блокировка шага Rinse (NC): насос промывки только при исправном насосе",
        [
            *_to_drain(),
            Row(1000, {"xLevelLow": True}, "Air и Rinse: насос промывки включён"),
            Row(1100, {"xLevelLow": False, "xPumpOk": False}, "насос неисправен: блокировка не выполнена"),
            Row(1200, {"xPumpOk": True}, "насос исправен: снова включён"),
        ],
    ),
    Scenario(
        "OffAndInit",
        "OFF_SQ выключает все шаги (N-выходы — 0), INIT_SQ возвращает начальный шаг",
        [
            *_to_drain(),
            Row(300, {"OFF_SQ": True}, "OFF_SQ: шаг Drain выключен, слив закрыт; промывка идёт (S держится)"),
            Row(400, {"OFF_SQ": False, "xStart": True}, "пуск без активных шагов: ничего"),
            Row(500, {"xStart": False, "INIT_SQ": True}, "INIT_SQ: Idle"),
            Row(600, {"INIT_SQ": False, "xStart": True}, "пуск: Drain, промывка №2"),
        ],
    ),
)

BLOCK = BlockScenarios(
    block="FB_BackwashGraph",
    source="samples/lang/FB_BackwashGraph.xml",
    description="промывка фильтра на GRAPH: ветви, D, NC с блокировкой, контроль с ACK_EF, INIT_SQ/OFF_SQ",
    inputs=INPUTS,
    outputs=OUTPUTS,
    defaults=DEFAULTS,
    factory=BackwashModel,
    scenarios=SCENARIOS,
)
