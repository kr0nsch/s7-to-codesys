#!/usr/bin/env python3
"""Пересчёт ожидаемых значений сценариев корпуса всех языков: scenarios/lang/<Блок>.csv из эталонных моделей.

    python scenarios/lang/reference/generate_lang_csv.py          # записать CSV
    python scenarios/lang/reference/generate_lang_csv.py --check  # только сравнить с файлами (для CI)

Модели (model_*.py) написаны по описанию логики в комментариях блоков samples/lang/*.xml, а не по
результату конвертера. Общая часть (часы, таймеры, формат CSV) — scenarios/reference/scenario_lib.py.
Коды выхода: 0 — успех / файлы актуальны, 1 — файлы устарели или ошибка в описании сценария.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence

HERE = os.path.dirname(os.path.abspath(__file__))
SCENARIOS_DIR = os.path.dirname(HERE)
LIB_DIR = os.path.join(os.path.dirname(SCENARIOS_DIR), "reference")
for path in (HERE, LIB_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

import model_fb_backwash_graph  # noqa: E402
import model_fb_conveyor_stl  # noqa: E402
import model_fb_pump_interlock_lad  # noqa: E402
import model_fb_starter  # noqa: E402
from scenario_lib import BlockScenarios, ScenarioError, to_csv  # noqa: E402

BLOCKS: tuple[BlockScenarios, ...] = (
    model_fb_starter.BLOCK,
    model_fb_pump_interlock_lad.BLOCK,
    model_fb_conveyor_stl.BLOCK,
    model_fb_backwash_graph.BLOCK,
)


def csv_path(block: BlockScenarios, out_dir: str = SCENARIOS_DIR) -> str:
    return os.path.join(out_dir, block.block + ".csv")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--check", action="store_true", help="только проверить, что CSV актуальны")
    parser.add_argument("--out", default=SCENARIOS_DIR, help="каталог CSV (по умолчанию scenarios/lang/)")
    args = parser.parse_args(argv)
    try:
        rendered = {block.block: to_csv(block) for block in BLOCKS}
    except ScenarioError as exc:
        print(f"ошибка сценария: {exc}", file=sys.stderr)
        return 1
    stale: list[str] = []
    for block in BLOCKS:
        path = csv_path(block, args.out)
        text = rendered[block.block]
        current = None
        if os.path.exists(path):
            with open(path, encoding="utf-8", newline="") as fh:
                current = fh.read()
        if current == text:
            continue
        if args.check:
            stale.append(path)
        else:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(text)
            print(f"записан {os.path.relpath(path)}")
    for path in stale:
        print(f"устарел: {os.path.relpath(path)} (запустите generate_lang_csv.py)", file=sys.stderr)
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
