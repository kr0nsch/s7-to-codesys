"""Интерпретатор stsim: старая точка импорта и модели стандартных ФБ."""

from __future__ import annotations

import s7conv.sim.stsim as new
import s7conv.tests.stsim as old


def test_old_import_path_reexports_simulator() -> None:
    """Соседние проекты импортируют s7conv.tests.stsim (выпуск 1.0.0): имена те же объекты."""
    for name in new.__all__:
        assert getattr(old, name) is getattr(new, name)
    assert old.__all__ == new.__all__
