"""Эталон таймеров и счётчиков S5 (s7conv/semantics/s5.py) против awlsim — независимой реализации STL S7-300.

awlsim (GPL-2.0+, PyPI 0.77.1) — внешнее средство: в репозиторий не входит и не импортируется кодом
конвертера; без него тесты пропускаются (python -m pip install awlsim==0.77.1 в отдельное окружение).
Сравниваются Q после каждой инструкции и остаток L T там, где округление не влияет (у awlsim — до
ближайшего, у эталона — вверх, docs/ASSUMPTIONS.md, запись L13). Время — кратно 125 мс, чтобы сумма
секунд awlsim (float) была точной и порог истечения совпадал до миллисекунды.
"""

from __future__ import annotations

import random

import pytest

from s7conv.semantics.s5 import S5Counter, S5Timer, s5time_word

awlsim_timers = pytest.importorskip("awlsim.core.timers", reason="awlsim не установлен — сверка S5 пропущена")
awlsim_counters = pytest.importorskip("awlsim.core.counters")

# мнемоника EN -> метод awlsim (немецкие мнемоники: SI = SP, SV = SE, SE = SD, SS = SS, SA = SF)
AWLSIM_START = {"SP": "run_SI", "SE": "run_SV", "SD": "run_SE", "SS": "run_SS", "SF": "run_SA"}


class _StatusWord:
    def __init__(self) -> None:
        self.VKE = 0
        self.OR = 0
        self.NER = 0


class _Cpu:
    def __init__(self) -> None:
        self.now = 0.0
        self.statusWord = _StatusWord()
        self.accu1 = self

    def get(self) -> int:  # Counter.set читает ACCU1 через cpu.accu1.get()
        return self.word

    word = 0


@pytest.mark.parametrize("seed", range(40))
def test_reference_s5_timer_matches_awlsim(seed: int) -> None:
    rng = random.Random(seed)
    cpu = _Cpu()
    theirs = awlsim_timers.Timer(cpu, 1)
    ours = S5Timer()
    now = 0
    for step in range(120):
        now += rng.choice((0, 125, 250, 500, 1000, 2000))
        cpu.now = now / 1000.0
        rlo = rng.random() < 0.5
        cpu.statusWord.VKE = int(rlo)
        op = rng.choice(("start", "start", "start", "FR", "R", "read"))
        where = f"seed {seed}, шаг {step}, t = {now} мс, {op}, RLO = {int(rlo)}"
        if op == "start":
            kind = rng.choice(tuple(AWLSIM_START))
            word = s5time_word(rng.choice((250, 500, 1000, 2500, 4000)))
            getattr(theirs, AWLSIM_START[kind])(word)
            ours.start(kind, rlo, word, now)
            where += f", {kind}"
        elif op == "FR":
            theirs.run_FR()
            ours.enable(rlo)
        elif op == "R":
            if rlo:
                theirs.reset()
            ours.reset(rlo)
        assert ours.read_q(now) == bool(theirs.get()), where
        if ours.rest_ms % 10 == 0:
            assert ours.read_bin(now) == theirs.getTimevalBin(), where


@pytest.mark.parametrize("seed", range(20))
def test_reference_s5_counter_matches_awlsim(seed: int) -> None:
    rng = random.Random(seed)
    cpu = _Cpu()
    theirs = awlsim_counters.Counter(cpu, 1)
    ours = S5Counter()
    for step in range(200):
        rlo = rng.random() < 0.5
        op = rng.choice(("CU", "CU", "CD", "S", "R", "FR"))
        where = f"seed {seed}, шаг {step}, {op}, RLO = {int(rlo)}"
        if op == "CU":
            theirs.run_ZV(int(rlo))
            ours.up(rlo)
        elif op == "CD":
            theirs.run_ZR(int(rlo))
            ours.down(rlo)
        elif op == "S":
            value = rng.choice((0, 5, 998, 999, 123))
            cpu.word = int(str(value), 16)
            theirs.set(int(rlo))
            ours.set(rlo, cpu.word)
        elif op == "R":
            if rlo:
                theirs.reset()
            ours.reset(rlo)
        else:
            theirs.run_FR(int(rlo))
            ours.enable(rlo)
        assert ours.value == theirs.getValueBin(), where
