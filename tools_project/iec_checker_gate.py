#!/usr/bin/env python3
"""Статанализ iec_checker для s7-to-codesys: обёртка над tools/check/run_iec_checker.py (шаблон).

Зачем обёртка. run_iec_checker.py не позволяет обосновать ParserError, а iec_checker 0.4 не разбирает
несколько конструкций, допустимых в CODESYS и нужных проекту: оператор TIME(), поле элемента массива
`a[i].b`, пустой оператор `;`, начальное значение массива в поле структуры (последнее — ошибка понижения
iec-checker в шаблоне). Править шаблон (tools/check, tools/st_flavors.py) в проекте нельзя, поэтому:

1. запускается run_iec_checker.py — тот же вариант сборки iec-checker и тот же файл обоснований
   tools/check/iec_checker_allow.toml (по умолчанию с tests/);
2. ParserError принимается только там, где он описан в tools_project/iec_checker_parser_gaps.toml
   (файл и регулярное выражение по тексту строки); любая другая необоснованная находка — ошибка;
3. запись о пробеле, которой больше не соответствует ни одна находка, — ошибка (список актуален);
4. обоснование из iec_checker_allow.toml, которое ни разу не использовано, — ошибка (с --tests).

Коды выхода: 0 — все находки обоснованы; 1 — нет (или устаревшие записи); 2 — неверные настройки;
3 — нет iec_checker (с --optional — предупреждение и 0).
Отчёты — как у run_iec_checker.py: build/iec_checker.json и build/iec_checker.md, плюс итог обёртки
build/iec_checker_gate.json.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tomllib
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_DIR.parent
CHECK_DIR = REPO_ROOT / "tools" / "check"
for extra in (CHECK_DIR, REPO_ROOT / "tools", REPO_ROOT / "tools" / "codesys"):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

import run_iec_checker as R  # noqa: E402

DEFAULT_GAPS = PROJECT_DIR / "iec_checker_parser_gaps.toml"
EXIT_OK, EXIT_FAIL, EXIT_CONFIG, EXIT_TOOL = 0, 1, 2, 3


class GapError(Exception):
    """Неверный файл пробелов разборщика."""


@dataclass
class Gap:
    file: str
    match: re.Pattern[str]
    reason: str
    used: int = 0


@dataclass
class GateResult:
    errors: list[dict[str, Any]] = field(default_factory=list)  # необоснованные находки
    known: list[dict[str, Any]] = field(default_factory=list)  # ParserError из списка пробелов
    stale_gaps: list[Gap] = field(default_factory=list)
    unused_allow: list[dict[str, Any]] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not (self.errors or self.stale_gaps or self.unused_allow)


def load_gaps(path: Path) -> list[Gap]:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise GapError(f"{path}: {exc}") from exc
    gaps: list[Gap] = []
    for n, item in enumerate(data.get("gap", []), 1):
        file, match, reason = item.get("file"), item.get("match"), item.get("reason")
        if not (isinstance(file, str) and isinstance(match, str) and isinstance(reason, str) and reason.strip()):
            raise GapError(f"{path}: запись {n}: нужны file, match и непустой reason")
        try:
            pattern = re.compile(match)
        except re.error as exc:
            raise GapError(f"{path}: запись {n}: match: {exc}") from exc
        gaps.append(Gap(file, pattern, reason))
    return gaps


def source_line(root: Path, source: str | None, line: int | None) -> str:
    if not source or not line:
        return ""
    try:
        lines = (root / source).read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    return lines[line - 1] if 0 < line <= len(lines) else ""


def evaluate(report: dict[str, Any], gaps: list[Gap], root: Path, require_all_allow: bool) -> GateResult:
    """Разбор отчёта run_iec_checker.py: ParserError из списка пробелов — допустим, прочие ошибки — нет."""
    result = GateResult()
    for finding in report.get("findings", []):
        if finding.get("status") != "error":
            continue
        if finding.get("id") in R.PARSER_IDS:
            text = source_line(root, finding.get("source"), finding.get("source_line"))
            gap = next((g for g in gaps if g.file == finding.get("source") and g.match.search(text)), None)
            if gap is not None:
                gap.used += 1
                result.known.append({**finding, "reason": gap.reason, "line_text": text.strip()})
                continue
        result.errors.append(finding)
    result.stale_gaps = [g for g in gaps if not g.used]
    if require_all_allow:
        result.unused_allow = list(report.get("unused_allow", []))
    return result


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="iec_checker_gate.py", description="iec_checker для s7-to-codesys (обёртка).")
    p.add_argument("--root", default=str(REPO_ROOT), help="корень репозитория")
    p.add_argument("--no-tests", action="store_true", help="только src/ (без проверки неиспользованных обоснований)")
    p.add_argument("--gaps", default=str(DEFAULT_GAPS), help="файл пробелов разборщика (TOML)")
    p.add_argument("--allow", default=None, help="файл обоснований (по умолчанию tools/check/iec_checker_allow.toml)")
    p.add_argument("--binary", default=None, help="путь к iec_checker")
    p.add_argument("--docker", default=None, metavar="IMAGE", help="Docker-образ iec_checker")
    p.add_argument(
        "--json", dest="json_out", default=None, help="итог обёртки (по умолчанию build/iec_checker_gate.json)"
    )
    p.add_argument("--optional", action="store_true", help="нет инструмента — предупреждение и код 0")
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root).resolve()
    try:
        gaps = load_gaps(Path(args.gaps))
    except GapError as exc:
        print(f"iec_checker_gate: {exc}", file=sys.stderr)
        return EXIT_CONFIG
    build = root / "build"
    report_path = build / "iec_checker.json"
    run_args = ["--root", str(root), "--json", str(report_path), "--md", str(build / "iec_checker.md")]
    if not args.no_tests:
        run_args.append("--tests")
    if args.allow:
        run_args += ["--allow", args.allow]
    if args.binary:
        run_args += ["--binary", args.binary]
    if args.docker:
        run_args += ["--docker", args.docker]
    if report_path.exists():
        report_path.unlink()
    code = R.main(run_args)
    if not report_path.is_file():
        # нет отчёта: нет инструмента, ошибка настроек или раскладки — код run_iec_checker.py как есть
        if code == 1 and args.optional:
            print("iec_checker_gate: ПРЕДУПРЕЖДЕНИЕ: отчёт не создан; статанализ пропущен (--optional)")
            return EXIT_OK
        return code if code in (EXIT_CONFIG,) else EXIT_TOOL
    report = json.loads(report_path.read_text(encoding="utf-8"))
    result = evaluate(report, gaps, root, require_all_allow=not args.no_tests)
    for finding in result.known:
        print(
            f"iec_checker_gate: известный пробел разборщика: {finding.get('source')}:{finding.get('source_line')}: "
            f"{finding.get('line_text')}"
        )
    for finding in result.errors:
        where = f"{finding.get('source') or finding.get('file')}:{finding.get('source_line') or finding.get('line')}"
        print(f"iec_checker_gate: НЕОБОСНОВАННО: {where}: {finding.get('id')}: {finding.get('msg')}", file=sys.stderr)
    for gap in result.stale_gaps:
        print(f"iec_checker_gate: устаревшая запись о пробеле: {gap.file} ({gap.match.pattern})", file=sys.stderr)
    for rule in result.unused_allow:
        print(f"iec_checker_gate: неиспользованное обоснование: {rule.get('id')} / {rule.get('file')}", file=sys.stderr)
    summary = {
        "version": 1,
        "ok": result.ok,
        "errors": len(result.errors),
        "known_parser_gaps": [
            {"source": f.get("source"), "line": f.get("source_line"), "text": f.get("line_text"), "reason": f["reason"]}
            for f in result.known
        ],
        "stale_gaps": [g.file for g in result.stale_gaps],
        "unused_allow": result.unused_allow,
        "run_iec_checker": report.get("summary", {}),
    }
    out = Path(args.json_out) if args.json_out else build / "iec_checker_gate.json"
    os.makedirs(out.parent, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = report.get("summary", {})
    print(
        f"iec_checker_gate: {'пройдено' if result.ok else 'НЕ пройдено'}; необоснованных {len(result.errors)}, "
        f"известных пробелов разборщика {len(result.known)}, обоснованных {counts.get('allowed', 0)}, "
        f"артефактов сборки {counts.get('artifact', 0)}"
    )
    return EXIT_OK if result.ok else EXIT_FAIL


if __name__ == "__main__":
    sys.exit(main())
