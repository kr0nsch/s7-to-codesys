"""Доступ к tools/codesys/stlayout.py — единственной реализации раскладки шаблона.

stlayout написан на общем подмножестве Python 2.7/3 и лежит вне пакета; s7conv используется из
репозитория (pip install -e . или python -m s7conv), поэтому путь вычисляется от корня репозитория.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LAYOUT_DIR = REPO_ROOT / "tools" / "codesys"
if str(LAYOUT_DIR) not in sys.path:
    sys.path.insert(0, str(LAYOUT_DIR))

import stlayout as L  # noqa: E402

# Рукописные объекты поддержки (F_NormX, F_ScaleX, таймеры S7Compat, ...) лежат в src/ репозитория,
# в папке проекта S7Compat; список имён и зависимостей — mapping.SUPPORT_DEPENDENCIES
SUPPORT_SRC = REPO_ROOT / "src"
SUPPORT_FOLDER = "S7Compat"

__all__ = ["LAYOUT_DIR", "REPO_ROOT", "SUPPORT_FOLDER", "SUPPORT_SRC", "L"]
