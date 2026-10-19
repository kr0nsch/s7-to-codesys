"""Старая точка импорта интерпретатора ST: код переехал в s7conv/sim/stsim.py.

Соседние проекты миграции импортируют `s7conv.tests.stsim` (закреплено на выпуске 1.0.0) — модуль
остаётся и только реэкспортирует s7conv.sim.stsim.
"""

from s7conv.sim.stsim import *  # noqa: F403
from s7conv.sim.stsim import __all__ as __all__
