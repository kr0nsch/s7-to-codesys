"""Эталон таймеров и счётчиков S5 S7-300/400 — по справочникам STL (AWL_e.pdf, гл. 4 и 12) и LAD (s7kop__b.pdf,
гл. 13), независимо от слоя S7Compat (src/POUs/S7Compat/F_S5*) и понижения.

Таймер — слово CPU: шкала, остаток, состояние Q и память фронта пуска (её сбрасывает FR). Остаток
считается от момента пуска по часам эталона (мс) на момент чтения: в S7 его уменьшает часовой процесс CPU
асинхронно циклу. Фаза часового процесса не моделируется (остаток в единицах шкалы — округление вверх,
истечение — ровно через значение × шкала); сброс R — по уровню RLO. Спорные места — docs/ASSUMPTIONS.md,
записи L13–L16; независимая сверка — awlsim (s7conv/tests/test_s5_awlsim.py, если awlsim установлен).
"""

from __future__ import annotations

from dataclasses import dataclass

BASE_MS = (10, 100, 1000, 10000)  # код шкалы (биты 12–13) → мс
_DURATION = {"D": 86_400_000, "H": 3_600_000, "M": 60_000, "S": 1000, "MS": 1}


def bcd_value(word: int) -> int:
    """Три младшие тетрады BCD → 0…999 (нецифровые тетрады — как есть)."""
    return (word & 0xF) + 10 * ((word >> 4) & 0xF) + 100 * ((word >> 8) & 0xF)


def to_bcd(value: int) -> int:
    return (value % 10) | ((value // 10) % 10) << 4 | ((value // 100) % 10) << 8


def s5time_word(ms: int) -> int:
    """S5T# → слово ACCU1-L: наименьшая шкала, в которую помещается время; значение — вниз до шкалы (§12.2)."""
    for code, base in enumerate(BASE_MS):
        if ms <= 999 * base or code == 3:
            return code << 12 | to_bcd(min(ms // base, 999))
    raise AssertionError("недостижимо")


def parse_s5time(text: str) -> int | None:
    """S5T#2S, S5TIME#1M30S → мс; не литерал S5TIME — None."""
    up = text.strip().upper()
    if not up.startswith(("S5T#", "S5TIME#")):
        return None
    body = up.split("#", 1)[1].replace("_", "")
    total, number = 0, ""
    i = 0
    while i < len(body):
        ch = body[i]
        if ch.isdigit():
            number += ch
            i += 1
            continue
        unit = "MS" if body.startswith("MS", i) else ch
        total += int(number or 0) * _DURATION[unit]
        number = ""
        i += len(unit)
    return total


@dataclass
class S5Timer:
    running: bool = False
    q: bool = False
    rlo_start: bool = False  # память фронта пуска
    rlo_free: bool = False  # память фронта FR
    set_at_end: bool = False  # Q по истечении: SD, SS — 1; SP, SE, SF — 0
    start_ms: int = 0
    preset_ms: int = 0
    rest_ms: int = 0
    base: int = 0

    def _update(self, now: int) -> None:
        if not self.running:
            return
        elapsed = (now - self.start_ms) & 0xFFFFFFFF
        if elapsed >= self.preset_ms:
            self.running, self.q, self.rest_ms = False, self.set_at_end, 0
        else:
            self.rest_ms = self.preset_ms - elapsed

    def _start(self, word: int, now: int) -> None:
        self.base = (word >> 12) & 0x3
        self.preset_ms = bcd_value(word) * BASE_MS[self.base]
        self.start_ms, self.rest_ms, self.running = now, self.preset_ms, True

    def start(self, kind: str, rlo: bool, word: int, now: int) -> None:
        """Пуск: kind — SP, SE, SD, SS, SF (мнемоники EN)."""
        rising, falling = rlo and not self.rlo_start, (not rlo) and self.rlo_start
        if kind == "SP":  # импульс: идёт, пока RLO = 1
            self.set_at_end = False
            if rising:
                self._start(word, now)
                self.q = True
            elif not rlo:
                self._update(now)
                self.running, self.q = False, False
        elif kind == "SE":  # продлённый импульс: RLO = 0 не останавливает, фронт перезапускает
            self.set_at_end = False
            if rising:
                self._start(word, now)
                self.q = True
        elif kind == "SD":  # задержка включения: Q по истечении при RLO = 1
            self.set_at_end = True
            if rising:
                self._start(word, now)
            elif not rlo:
                self._update(now)
                self.running, self.q = False, False
        elif kind == "SS":  # с памятью: Q до сброса
            self.set_at_end = True
            if rising:
                self._start(word, now)
        elif kind == "SF":  # задержка выключения: пуск по спаду, фронт останавливает
            self.set_at_end = False
            if rising:
                self._update(now)
                self.running, self.q = False, True
            if falling:
                self._start(word, now)
                self.q = True
        else:
            raise ValueError(kind)
        self.rlo_start = rlo

    def enable(self, rlo: bool) -> None:
        """FR: фронт RLO сбрасывает память фронта пуска."""
        if rlo and not self.rlo_free:
            self.rlo_start = False
        self.rlo_free = rlo

    def reset(self, rlo: bool) -> None:
        if rlo:
            self.running, self.q, self.rest_ms = False, False, 0

    def read_q(self, now: int) -> bool:
        self._update(now)
        return self.q

    def read_bin(self, now: int) -> int:
        self._update(now)
        base = BASE_MS[self.base]
        return -(-self.rest_ms // base)

    def read_bcd(self, now: int) -> int:
        return self.base << 12 | to_bcd(self.read_bin(now))


@dataclass
class S5Counter:
    value: int = 0
    rlo_up: bool = False
    rlo_down: bool = False
    rlo_set: bool = False
    rlo_free: bool = False

    def up(self, rlo: bool) -> None:
        if rlo and not self.rlo_up and self.value < 999:
            self.value += 1
        self.rlo_up = rlo

    def down(self, rlo: bool) -> None:
        if rlo and not self.rlo_down and self.value > 0:
            self.value -= 1
        self.rlo_down = rlo

    def set(self, rlo: bool, word: int) -> None:
        if rlo and not self.rlo_set:
            self.value = bcd_value(word)
        self.rlo_set = rlo

    def reset(self, rlo: bool) -> None:
        if rlo:
            self.value = 0

    def enable(self, rlo: bool) -> None:
        if rlo and not self.rlo_free:
            self.rlo_up = self.rlo_down = self.rlo_set = False
        self.rlo_free = rlo


__all__ = ["BASE_MS", "S5Counter", "S5Timer", "bcd_value", "parse_s5time", "s5time_word", "to_bcd"]
