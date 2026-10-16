"""Эталонная модель и сценарии FB_PumpAlternation.

Источник логики — нормативное описание в заголовке samples/scl/FB_PumpAlternation.scl
(пункты 1–5). F_TRIG — по семантике S7: на первом вызове спада нет.
"""

from __future__ import annotations

from collections.abc import Mapping

from scenario_lib import BlockScenarios, Clock, FTrig, Port, RTrig, Scenario, Value, limit, untimed_rows

PUMP_COUNT = 3


class PumpAlternationModel:
    def __init__(self) -> None:
        self.lead = 1
        self.edge_alternate = RTrig()
        self.edge_stop = FTrig()

    def step(self, clock: Clock, i: Mapping[str, Value]) -> dict[str, Value]:
        avail = {n: bool(i[f"available{n}"]) for n in range(1, PUMP_COUNT + 1)}
        required = limit(0, int(i["demand"]), PUMP_COUNT)
        self.edge_alternate(bool(i["alternate"]))
        self.edge_stop(required > 0)
        rotate = self.edge_alternate.q or (self.edge_stop.q and bool(i["rotateOnStop"]))
        if not 1 <= self.lead <= PUMP_COUNT:
            self.lead = 1
        if rotate:
            # следующий доступный после lead по кругу: lead+1, lead+2, lead
            for k in range(1, PUMP_COUNT + 1):
                candidate = (self.lead - 1 + k) % PUMP_COUNT + 1
                if avail[candidate]:
                    self.lead = candidate
                    break
        run = dict.fromkeys(avail, False)
        assigned = 0
        for k in range(PUMP_COUNT):
            idx = (self.lead - 1 + k) % PUMP_COUNT + 1
            if avail[idx] and assigned < required:
                run[idx] = True
                assigned += 1
        return {
            "run1": run[1],
            "run2": run[2],
            "run3": run[3],
            "leadPump": self.lead,
            "runningCount": assigned,
            "shortage": assigned < required,
        }


INPUTS = (
    Port("demand", "INT"),
    Port("available1", "BOOL"),
    Port("available2", "BOOL"),
    Port("available3", "BOOL"),
    Port("alternate", "BOOL"),
    Port("rotateOnStop", "BOOL"),
)
OUTPUTS = (
    Port("run1", "BOOL"),
    Port("run2", "BOOL"),
    Port("run3", "BOOL"),
    Port("leadPump", "INT"),
    Port("runningCount", "INT"),
    Port("shortage", "BOOL"),
)
DEFAULTS: dict[str, Value] = {
    "demand": 0,
    "available1": False,
    "available2": False,
    "available3": False,
    "alternate": False,
    "rotateOnStop": True,
}
ALL_AVAILABLE: dict[str, Value] = {"available1": True, "available2": True, "available3": True}

SCENARIOS = (
    Scenario(
        "RotateOnStop",
        "Смена ведущего при каждом останове группы: 1 -> 2 -> 3 -> 1",
        untimed_rows(
            [
                ({**ALL_AVAILABLE}, "первый вызов при demand = 0: спада нет, ведущий 1"),
                ({"demand": 1}, "один насос: ведущий 1"),
                ({"demand": 2}, "два насоса: 1 и 2"),
                ({"demand": 0}, "останов группы: ведущий -> 2"),
                ({"demand": 1}, "один насос: 2"),
                ({"demand": 3}, "три насоса: 2, 3, 1"),
                ({"demand": 0}, "останов: ведущий -> 3"),
                ({"demand": 1}, "один насос: 3"),
                ({"demand": 0}, "останов: ведущий -> 1 (по кругу)"),
                ({}, "demand остаётся 0: спада нет, ведущий 1"),
            ]
        ),
    ),
    Scenario(
        "StandbyTakesOver",
        "Недоступный насос подхватывает следующий по кругу; нехватка насосов",
        untimed_rows(
            [
                ({**ALL_AVAILABLE, "demand": 1}, "один насос: 1"),
                ({"available1": False}, "насос 1 недоступен: работает 2, ведущий остаётся 1"),
                ({"available1": True}, "насос 1 вернулся: снова 1"),
                ({"demand": 3, "available2": False}, "нужно 3, доступно 2: 1 и 3, нехватка"),
                ({"demand": 0}, "останов: после 1 недоступен 2 — ведущий 3"),
                ({"demand": 1}, "один насос: 3"),
            ]
        ),
    ),
    Scenario(
        "ForcedAlternate",
        "Принудительная смена ведущего по фронту alternate, в том числе в работе",
        untimed_rows(
            [
                ({**ALL_AVAILABLE, "demand": 1}, "один насос: 1"),
                ({"alternate": True}, "фронт alternate: ведущий 2, переключение в работе"),
                ({}, "alternate держится: фронта нет"),
                ({"alternate": False}, "отпущен"),
                ({"alternate": True}, "фронт: ведущий 3"),
            ]
        ),
    ),
    Scenario(
        "RotateOnStopDisabled",
        "rotateOnStop = FALSE: при останове ведущий не меняется",
        untimed_rows(
            [
                ({**ALL_AVAILABLE, "rotateOnStop": False, "demand": 1}, "один насос: 1"),
                ({"demand": 0}, "останов: ведущий остаётся 1"),
                ({"demand": 1}, "снова 1"),
            ]
        ),
    ),
    Scenario(
        "NoPumpsAvailable",
        "Доступных нет: ничего не работает, ведущий не меняется",
        untimed_rows(
            [
                ({"demand": 2}, "нужно 2, доступных нет: нехватка"),
                ({"demand": 0}, "останов: искать некого, ведущий 1"),
                ({"alternate": True}, "фронт alternate: искать некого, ведущий 1"),
                ({"available3": True, "alternate": False, "demand": 1}, "доступен только 3: работает 3, ведущий 1"),
            ]
        ),
    ),
    Scenario(
        "DemandClamped",
        "demand вне 0...3 ограничивается",
        untimed_rows(
            [
                ({**ALL_AVAILABLE, "demand": 5}, "demand 5 -> 3: все три"),
                ({"demand": -1}, "demand -1 -> 0: останов, ведущий -> 2"),
                ({"demand": 4}, "demand 4 -> 3: 2, 3, 1"),
            ]
        ),
    ),
)

BLOCK = BlockScenarios(
    block="FB_PumpAlternation",
    source="samples/scl/FB_PumpAlternation.scl",
    description="Чередование трёх насосов: смена ведущего, подхват резервным, нехватка",
    inputs=INPUTS,
    outputs=OUTPUTS,
    defaults=DEFAULTS,
    factory=PumpAlternationModel,
    scenarios=SCENARIOS,
    timed=False,
)
