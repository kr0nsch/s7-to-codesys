#!/usr/bin/env python3
"""Пересчёт ожидаемых значений сценариев: scenarios/<Блок>.csv из эталонных моделей.

    python scenarios/reference/generate_csv.py          # записать CSV
    python scenarios/reference/generate_csv.py --check  # только сравнить с файлами (для CI)

Модели (model_*.py) написаны по описанию логики в заголовках samples/scl/*.scl,
а не по результату конвертера. Коды выхода: 0 — успех / файлы актуальны,
1 — файлы устарели или ошибка в описании сценария.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import model_fb_alarm_delay  # noqa: E402
import model_fb_analog_in  # noqa: E402
import model_fb_motor  # noqa: E402
import model_fb_pump_alternation  # noqa: E402
import model_fb_sequencer  # noqa: E402
import model_fb_totalizer  # noqa: E402
from scenario_lib import BlockScenarios, ScenarioError, to_csv  # noqa: E402

SCENARIOS_DIR = os.path.dirname(HERE)

BLOCKS: tuple[BlockScenarios, ...] = (
    model_fb_analog_in.BLOCK,
    model_fb_motor.BLOCK,
    model_fb_alarm_delay.BLOCK,
    model_fb_totalizer.BLOCK,
    model_fb_pump_alternation.BLOCK,
    model_fb_sequencer.BLOCK,
)


def csv_path(block: BlockScenarios, out_dir: str = SCENARIOS_DIR) -> str:
    return os.path.join(out_dir, block.block + ".csv")


def render_all() -> dict[str, str]:
    """Имя блока -> текст CSV."""
    return {block.block: to_csv(block) for block in BLOCKS}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--check", action="store_true", help="только проверить, что CSV актуальны")
    parser.add_argument("--out", default=SCENARIOS_DIR, help="каталог CSV (по умолчанию scenarios/)")
    args = parser.parse_args(argv)
    try:
        rendered = render_all()
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
    if stale:
        for path in stale:
            print(f"устарел: {os.path.relpath(path)} (запустите generate_csv.py)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
