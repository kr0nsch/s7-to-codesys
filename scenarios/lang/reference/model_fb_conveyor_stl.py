"""Эталонная модель и сценарии FB_ConveyorStl — конвейера на STL S7-300 с таймерами и счётчиком S5.

Источник логики — описание в комментарии блока samples/lang/FB_ConveyorStl.xml (CONVEYOR_DESCRIPTION в
samples/lang/blocks.py), пункты 1–7. Таймеры S5 — по справочникам STL и LAD S7-300/400 (AWL_e.pdf гл. 12,
s7kop__b.pdf гл. 13): виды SP, SE, SD, SS, SF, разрешение FR, сброс R по уровню, остаток в единицах шкалы
(округление вверх, шкала 10 мс для времени до 9,99 с). Модель не использует s7conv: третья независимая
запись той же семантики после S7Compat и эталона s7conv/semantics/s5.py.

Остатки iDelayLeft и wRunOutBcd зависят от момента вызова, а не только от порогов: они точны в тестах с
моделируемыми часами (GVL_S7Clock), в реальном времени — нет.
"""

from __future__ import annotations

from collections.abc import Mapping

from scenario_lib import BlockScenarios, Clock, Port, Row, Scenario, Value

BASE_10MS = 10  # шкала таймеров блока: все времена до 9,99 с — 10 мс, код шкалы 0


class S5Timer:
    """Таймер S5 одного вида; memory — RLO прошлой инструкции пуска (память фронта, её сбрасывает FR)."""

    def __init__(self, kind: str, preset_ms: int) -> None:
        self.kind = kind
        self.preset_ms = preset_ms
        self.running = False
        self.q = False
        self.memory = False
        self.free = False
        self.start_ms = 0
        self.rest_ms = 0

    def update(self, clock: Clock) -> None:
        if not self.running:
            return
        elapsed = clock.now_ms - self.start_ms
        if clock.compare(elapsed, self.preset_ms):
            self.running = False
            self.q = self.kind in ("SD", "SS")  # задержки включения: Q по истечении; импульсы и SF — 0
            self.rest_ms = 0
        else:
            self.rest_ms = self.preset_ms - elapsed

    def _go(self, clock: Clock) -> None:
        self.running, self.start_ms, self.rest_ms = True, clock.now_ms, self.preset_ms

    def run(self, clock: Clock, rlo: bool) -> None:
        rising, falling = rlo and not self.memory, self.memory and not rlo
        if self.kind == "SP":
            if rising:
                self._go(clock)
                self.q = True
            elif not rlo:
                self.update(clock)
                self.running, self.q = False, False
        elif self.kind == "SE":
            if rising:
                self._go(clock)
                self.q = True
        elif self.kind == "SD":
            if rising:
                self._go(clock)
            elif not rlo:
                self.update(clock)
                self.running, self.q = False, False
        elif self.kind == "SS":
            if rising:
                self._go(clock)
        elif self.kind == "SF":
            if rising:
                self.update(clock)
                self.running, self.q = False, True
            if falling:
                self._go(clock)
                self.q = True
        self.memory = rlo

    def enable(self, rlo: bool) -> None:
        if rlo and not self.free:
            self.memory = False
        self.free = rlo

    def reset(self, rlo: bool) -> None:
        if rlo:
            self.running, self.q, self.rest_ms = False, False, 0

    def read(self, clock: Clock) -> bool:
        self.update(clock)
        return self.q

    def units(self, clock: Clock) -> int:
        self.update(clock)
        return (self.rest_ms + BASE_10MS - 1) // BASE_10MS


def bcd(value: int) -> int:
    return (value % 10) | ((value // 10) % 10) << 4 | ((value // 100) % 10) << 8


class ConveyorModel:
    def __init__(self) -> None:
        self.req = False
        self.jam = False
        self.t1 = S5Timer("SP", 1000)
        self.t2 = S5Timer("SD", 2000)
        self.t3 = S5Timer("SF", 3000)
        self.t4 = S5Timer("SE", 4000)
        self.t5 = S5Timer("SS", 5000)
        self.count = 0
        self.count_memory = False

    def step(self, clock: Clock, i: Mapping[str, Value]) -> dict[str, Value]:
        sensor, ack = bool(i["xSensor"]), bool(i["xAck"])
        # 1. запрос работы: S, затем R (сброс главнее); xJam — прошлого вызова
        if bool(i["xStart"]):
            self.req = True
        if bool(i["xStop"]) or self.jam:
            self.req = False
        # 2. сирена — импульс T1 по запросу
        self.t1.run(clock, self.req)
        horn = self.t1.read(clock)
        # 3. задержка пуска T2
        self.t2.run(clock, self.req)
        # 4. выбег T3 по T2: двигатель
        self.t3.run(clock, self.t2.read(clock))
        motor = self.t3.read(clock)
        # 5. контроль потока T4, взвод T5, затор, квитирование
        self.t4.run(clock, sensor)
        flow_ok = self.t4.read(clock)
        self.t5.run(clock, motor)
        self.t5.reset(not motor)
        if self.t5.read(clock) and not self.t4.read(clock):
            self.jam = True
        self.t4.enable(ack)
        if ack:
            self.jam = False
        # 6. диагностика: остаток T2 в единицах, T3 — BCD со шкалой (код 0 — 10 мс)
        delay_left = self.t2.units(clock)
        run_out = bcd(self.t3.units(clock))
        # 7. счётчик изделий C1: CU по фронту, R по уровню
        if sensor and not self.count_memory and self.count < 999:
            self.count += 1
        self.count_memory = sensor
        if bool(i["xCountReset"]):
            self.count = 0
        return {
            "xHorn": horn,
            "xMotor": motor,
            "xFlowOk": flow_ok,
            "xJam": self.jam,
            "iDelayLeft": delay_left,
            "wRunOutBcd": run_out,
            "iCount": self.count,
            "wCountBcd": bcd(self.count),
        }


INPUTS = (
    Port("xStart", "BOOL"),
    Port("xStop", "BOOL"),
    Port("xSensor", "BOOL"),
    Port("xAck", "BOOL"),
    Port("xCountReset", "BOOL"),
)
OUTPUTS = (
    Port("xHorn", "BOOL"),
    Port("xMotor", "BOOL"),
    Port("xFlowOk", "BOOL"),
    Port("xJam", "BOOL"),
    Port("iDelayLeft", "INT"),
    Port("wRunOutBcd", "WORD"),
    Port("iCount", "INT"),
    Port("wCountBcd", "WORD"),
)
DEFAULTS: dict[str, Value] = {
    "xStart": False,
    "xStop": False,
    "xSensor": False,
    "xAck": False,
    "xCountReset": False,
}


def _start_rows() -> list[Row]:
    return [
        Row(0, {"xStart": True}, "пуск: запрос, сирена T1 и задержка T2 пошли"),
        Row(100, {"xStart": False}, "кнопка отпущена"),
        Row(2000, {}, "2 с: задержка T2 истекла — двигатель (T3 = 1)", boundary=True),
    ]


SCENARIOS = (
    Scenario(
        "StartSequence",
        "Пуск: сирена 1 с (SP), задержка 2 с (SD), остаток задержки L T2",
        [
            Row(0, {"xStart": True}, "пуск: сирена и задержка, остаток 200 единиц"),
            Row(300, {"xStart": False}, "кнопка отпущена: сирена звучит, остаток 170"),
            Row(1000, {}, "1 с: сирена выключилась (T1 истёк), остаток 100", boundary=True),
            Row(1500, {}, "остаток 50"),
            Row(2000, {}, "2 с: задержка истекла — двигатель", boundary=True),
            Row(2500, {}, "работает"),
        ],
    ),
    Scenario(
        "StopRunOut",
        "Стоп: выбег 3 с (SF), остаток выбега LC T3 в BCD",
        [
            *_start_rows(),
            Row(3000, {"xStop": True}, "стоп: запрос снят, выбег T3 пошёл, 16#0300"),
            Row(3100, {"xStop": False}, "выбег: остаток 290 единиц"),
            Row(4500, {}, "выбег: остаток 150 единиц"),
            Row(6000, {}, "3 с выбега: двигатель остановлен", boundary=True),
        ],
    ),
    Scenario(
        "JamWithoutProducts",
        "Нет изделий: через 5 с работы (SS) — затор, выбег, квитирование",
        [
            *_start_rows(),
            Row(6700, {}, "4,7 с работы: контроль ещё не взведён"),
            Row(7000, {}, "5 с работы: T5 взвёл контроль, T4 не идёт — затор", boundary=True),
            Row(7100, {}, "затор сбросил запрос: выбег 3 с"),
            Row(10100, {}, "выбег закончен: двигатель остановлен, T5 сброшен", boundary=True),
            Row(10500, {"xAck": True}, "квитирование: затор снят"),
            Row(10600, {"xAck": False}, "покой"),
        ],
    ),
    Scenario(
        "ProductsKeepFlow",
        "Изделия каждые 2 с перезапускают T4 (SE): затора нет; 4 с без изделий — затор",
        [
            *_start_rows(),
            Row(2500, {"xSensor": True}, "изделие №1: T4 пошёл"),
            Row(2600, {"xSensor": False}, "датчик свободен"),
            Row(4500, {"xSensor": True}, "изделие №2: T4 перезапущен"),
            Row(4600, {"xSensor": False}, "датчик свободен"),
            Row(6500, {"xSensor": True}, "изделие №3"),
            Row(6600, {"xSensor": False}, "датчик свободен"),
            Row(7000, {}, "5 с работы: контроль взведён, T4 идёт — затора нет", boundary=True),
            Row(8500, {"xSensor": True}, "изделие №4"),
            Row(8600, {"xSensor": False}, "датчик свободен"),
            Row(10600, {}, "2,1 с без изделий"),
            Row(12500, {}, "4 с без изделий: T4 истёк — затор", boundary=True),
        ],
    ),
    Scenario(
        "CountResetIsLevel",
        "Счётчик изделий C1: CU по фронту, R по уровню",
        [
            Row(0, {"xSensor": True}, "изделие №1"),
            Row(100, {"xSensor": False}, "датчик свободен"),
            Row(200, {"xSensor": True}, "изделие №2"),
            Row(300, {"xSensor": False}, "датчик свободен"),
            Row(400, {"xCountReset": True}, "сброс счётчика"),
            Row(500, {"xSensor": True}, "изделие при нажатом сбросе: CU считает, R тут же обнуляет"),
            Row(600, {"xSensor": False, "xCountReset": False}, "сброс отпущен"),
            Row(700, {"xSensor": True}, "изделие №1 после сброса"),
        ],
    ),
    Scenario(
        "HornCutShort",
        "Стоп через 0,3 с: сирена оборвана (SP), задержка остановлена — остаток сохраняется",
        [
            Row(0, {"xStart": True}, "пуск: сирена, остаток 200"),
            Row(300, {"xStart": False, "xStop": True}, "стоп: сирена оборвана, T2 остановлен с остатком 170"),
            Row(400, {"xStop": False}, "остаток 170 сохраняется"),
            Row(5000, {}, "остаток 170 сохраняется"),
        ],
    ),
    Scenario(
        "AckRestartsFlowWatch",
        "Датчик залип в 1: T4 истёк, затор; квитирование FR T4 перезапускает контроль потока",
        [
            *_start_rows(),
            Row(2500, {"xSensor": True}, "датчик залип в 1: T4 пошёл один раз, изделие №1"),
            Row(6500, {}, "4 с: T4 истёк, фронтов нет", boundary=True),
            Row(7000, {}, "контроль взведён: затор", boundary=True),
            Row(7100, {}, "запрос снят: выбег"),
            Row(10100, {}, "выбег закончен", boundary=True),
            Row(10500, {"xAck": True}, "квитирование: затор снят, FR T4 (SE в этом вызове уже прошёл)"),
            Row(10600, {"xAck": False}, "следующий вызов: SE видит фронт — T4 перезапущен"),
        ],
    ),
)

BLOCK = BlockScenarios(
    block="FB_ConveyorStl",
    source="samples/lang/FB_ConveyorStl.xml",
    description="конвейер на STL: таймеры S5 SP, SE, SD, SS, SF, FR, R, L/LC T и счётчик CU, R, L/LC C",
    inputs=INPUTS,
    outputs=OUTPUTS,
    defaults=DEFAULTS,
    factory=ConveyorModel,
    scenarios=SCENARIOS,
)
