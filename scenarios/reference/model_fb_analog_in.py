"""Эталонная модель и сценарии FB_AnalogIn.

Источник логики — нормативное описание в заголовке samples/scl/FB_AnalogIn.scl
(пункты 1–4). Значения raw подобраны так, что value точно представимо в REAL:
при шкале 0...16 value = raw / 1728, raw кратно 27 (см. scenarios/README.md).
"""

from __future__ import annotations

from collections.abc import Mapping

from scenario_lib import BlockScenarios, Clock, Port, Scenario, Value, limit, norm_x, scale_x, untimed_rows

RAW_NOMINAL_LOW = 0
RAW_NOMINAL_HIGH = 27648
RAW_OVERSHOOT_MAX = 32511
RAW_UNDERSHOOT_MIN = -4864


def _high(flag: bool, value: float, setpoint: float, hyst: float) -> bool:
    if value >= setpoint:
        return True
    if value < setpoint - hyst:
        return False
    return flag


def _low(flag: bool, value: float, setpoint: float, hyst: float) -> bool:
    if value <= setpoint:
        return True
    if value > setpoint + hyst:
        return False
    return flag


class AnalogInModel:
    def __init__(self) -> None:
        self.alarm_hh = False
        self.warn_h = False
        self.warn_l = False
        self.alarm_ll = False

    def step(self, clock: Clock, i: Mapping[str, Value]) -> dict[str, Value]:
        raw = int(i["raw"])
        fault = raw > RAW_OVERSHOOT_MAX or raw < RAW_UNDERSHOOT_MIN
        over = not fault and raw > RAW_NOMINAL_HIGH
        under = not fault and raw < RAW_NOMINAL_LOW
        sim = bool(i["simulation"])
        if sim:
            value, valid = float(i["simValue"]), True
        elif fault:
            value, valid = float(i["substitute"]), False
        else:
            clamped = limit(RAW_NOMINAL_LOW, raw, RAW_NOMINAL_HIGH)
            normalized = norm_x(RAW_NOMINAL_LOW, clamped, RAW_NOMINAL_HIGH)
            value, valid = scale_x(float(i["rangeLow"]), normalized, float(i["rangeHigh"])), True
        hyst = float(i["hysteresis"])
        if valid:
            self.alarm_hh = _high(self.alarm_hh, value, float(i["limitHH"]), hyst)
            self.warn_h = _high(self.warn_h, value, float(i["limitH"]), hyst)
            self.warn_l = _low(self.warn_l, value, float(i["limitL"]), hyst)
            self.alarm_ll = _low(self.alarm_ll, value, float(i["limitLL"]), hyst)
        else:
            self.alarm_hh = self.warn_h = self.warn_l = self.alarm_ll = False
        bits = (valid, fault, over, under, self.alarm_hh, self.warn_h, self.warn_l, self.alarm_ll, sim)
        status = sum(1 << n for n, bit in enumerate(bits) if bit)
        return {
            "value": value,
            "valid": valid,
            "channelFault": fault,
            "overrange": over,
            "underrange": under,
            "alarmHH": self.alarm_hh,
            "warnH": self.warn_h,
            "warnL": self.warn_l,
            "alarmLL": self.alarm_ll,
            "statusWord": status,
        }


INPUTS = (
    Port("raw", "INT"),
    Port("rangeLow", "REAL"),
    Port("rangeHigh", "REAL"),
    Port("limitHH", "REAL"),
    Port("limitH", "REAL"),
    Port("limitL", "REAL"),
    Port("limitLL", "REAL"),
    Port("hysteresis", "REAL"),
    Port("substitute", "REAL"),
    Port("simulation", "BOOL"),
    Port("simValue", "REAL"),
)
OUTPUTS = (
    Port("value", "REAL", 0.001),
    Port("valid", "BOOL"),
    Port("channelFault", "BOOL"),
    Port("overrange", "BOOL"),
    Port("underrange", "BOOL"),
    Port("alarmHH", "BOOL"),
    Port("warnH", "BOOL"),
    Port("warnL", "BOOL"),
    Port("alarmLL", "BOOL"),
    Port("statusWord", "WORD"),
)
DEFAULTS: dict[str, Value] = {
    "raw": 0,
    "rangeLow": 0.0,
    "rangeHigh": 16.0,
    "limitHH": 14.0,
    "limitH": 12.0,
    "limitL": 2.0,
    "limitLL": 1.0,
    "hysteresis": 0.5,
    "substitute": 0.0,
    "simulation": False,
    "simValue": 0.0,
}

SCENARIOS = (
    Scenario(
        "ScalingPoints",
        "Опорные точки шкалы 0...16 бар",
        untimed_rows(
            [
                ({"raw": 0}, "0 -> 0.0 бар; ниже L и LL"),
                ({"raw": 13824}, "середина шкалы -> 8.0; L и LL сброшены (8.0 > 2.5 и > 1.5)"),
                ({"raw": 27648}, "номинальный максимум -> 16.0; HH и H"),
                ({"raw": 6912}, "четверть -> 4.0; HH и H сброшены"),
                ({"raw": 20736}, "-> 12.0 = limitH: H включается (>=)"),
                ({"raw": 1728}, "-> 1.0 = limitLL: L и LL включаются (<=), H сброшен"),
            ]
        ),
    ),
    Scenario(
        "HighLimitsHysteresis",
        "Уставки H и HH с гистерезисом 0.5",
        untimed_rows(
            [
                ({"raw": 19008}, "11.0 — ниже всех верхних уставок"),
                ({"raw": 20736}, "12.0 = limitH: H включается"),
                ({"raw": 20304}, "11.75 — в зоне гистерезиса, H держится"),
                ({"raw": 19872}, "11.5 = limitH - hysteresis: не меньше порога, H держится"),
                ({"raw": 19440}, "11.25 < 11.5: H сбрасывается"),
                ({"raw": 24192}, "14.0 = limitHH: HH и H"),
                ({"raw": 23328}, "13.5 = limitHH - hysteresis: HH держится"),
                ({"raw": 22896}, "13.25 < 13.5: HH сброшен, H держится"),
                ({"raw": 23760}, "13.75 < 14.0: HH снова не включается"),
                ({"raw": 19008}, "11.0: H сброшен"),
            ]
        ),
    ),
    Scenario(
        "LowLimitsHysteresis",
        "Уставки L и LL с гистерезисом 0.5",
        untimed_rows(
            [
                ({"raw": 5184}, "3.0 — выше нижних уставок"),
                ({"raw": 3456}, "2.0 = limitL: L включается"),
                ({"raw": 3888}, "2.25 — в зоне гистерезиса, L держится"),
                ({"raw": 4320}, "2.5 = limitL + hysteresis: не больше порога, L держится"),
                ({"raw": 4752}, "2.75 > 2.5: L сбрасывается"),
                ({"raw": 1728}, "1.0 = limitLL: L и LL"),
                ({"raw": 2592}, "1.5 = limitLL + hysteresis: LL держится"),
                ({"raw": 3024}, "1.75 > 1.5: LL сброшен; 1.75 <= 2.0 — L"),
                ({"raw": 2160}, "1.25 > limitLL: LL не включается"),
            ]
        ),
    ),
    Scenario(
        "ChannelDiagnostics",
        "Зоны перегрузки, неисправность канала, замещающее значение",
        untimed_rows(
            [
                ({"raw": 13824, "substitute": 5.0}, "норма 8.0; замещающее значение 5.0"),
                ({"raw": 27649}, "выше номинала: overrange, value ограничено 16.0, HH и H"),
                ({"raw": 32511}, "верхняя граница зоны перегрузки — ещё не неисправность"),
                ({"raw": 32512}, "за зоной перегрузки: channelFault, value := substitute, уставки сброшены"),
                ({"raw": 32767}, "переполнение/обрыв (7FFF)"),
                ({"raw": 13824}, "канал восстановлен: 8.0, уставки снова считаются (HH не держится)"),
                ({"raw": -1}, "ниже номинала: underrange, value ограничено 0.0, L и LL"),
                ({"raw": -4864}, "нижняя граница зоны перегрузки — ещё не неисправность"),
                ({"raw": -4865}, "за зоной: channelFault"),
                ({"raw": -32768}, "антипереполнение (8000)"),
                ({"raw": 3456}, "канал восстановлен: 2.0 — только L"),
            ]
        ),
    ),
    Scenario(
        "Simulation",
        "Имитация перекрывает неисправный канал",
        untimed_rows(
            [
                ({"raw": 32767}, "неисправность, value = substitute 0.0"),
                ({"simulation": True, "simValue": 15.0}, "имитация 15.0: valid, HH и H; channelFault по raw остаётся"),
                ({"simValue": 13.0}, "13.0 < 13.5: HH сброшен, H держится"),
                ({"raw": 13824}, "канал исправен, имитация продолжается: value 13.0"),
                ({"simulation": False}, "имитация снята: value по raw 8.0, H сброшен"),
            ]
        ),
    ),
    Scenario(
        "CustomRanges",
        "Шкала -50...150 и обратная шкала 16...0",
        untimed_rows(
            [
                (
                    {
                        "raw": 6912,
                        "rangeLow": -50.0,
                        "rangeHigh": 150.0,
                        "limitHH": 120.0,
                        "limitH": 100.0,
                        "limitL": 0.0,
                        "limitLL": -20.0,
                        "hysteresis": 2.0,
                    },
                    "шкала -50...150: четверть -> 0.0 = limitL",
                ),
                ({"raw": 20736}, "три четверти -> 100.0 = limitH; L сброшен"),
                ({"raw": 27648}, "максимум -> 150.0: HH и H"),
                ({"raw": 0}, "минимум -> -50.0: L и LL"),
                (
                    {
                        "raw": 6912,
                        "rangeLow": 16.0,
                        "rangeHigh": 0.0,
                        "limitHH": 14.0,
                        "limitH": 12.0,
                        "limitL": 2.0,
                        "limitLL": 1.0,
                        "hysteresis": 0.5,
                    },
                    "обратная шкала 16...0: четверть -> 12.0 = limitH",
                ),
                ({"raw": 27648}, "обратная шкала: максимум raw -> 0.0, L и LL"),
            ]
        ),
    ),
)

BLOCK = BlockScenarios(
    block="FB_AnalogIn",
    source="samples/scl/FB_AnalogIn.scl",
    description="Масштабирование 0...27648, диагностика канала, уставки с гистерезисом",
    inputs=INPUTS,
    outputs=OUTPUTS,
    defaults=DEFAULTS,
    factory=AnalogInModel,
    scenarios=SCENARIOS,
    timed=False,
)
