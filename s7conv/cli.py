"""Командная строка s7conv: convert, report, check, build-corpus, gen-tests.

Коды выхода: 0 — успех; 1 — порог --fail-on превышен (convert, report), есть ошибки разбора
(check) или результат в репозитории устарел (build-corpus --check, gen-tests --check); 2 — неверные
аргументы, входные файлы или сценарии; 3 — внутренняя ошибка конвертера.
"""

from __future__ import annotations

import argparse
import sys
import traceback
from collections.abc import Sequence
from pathlib import Path

from s7conv import __version__
from s7conv import corpus as C
from s7conv import mapping as M
from s7conv import pipeline as P
from s7conv import report as R
from s7conv import testgen as TG
from s7conv.emitter import ConversionResult, Options
from s7conv.layout import REPO_ROOT, L

EXIT_OK = 0
EXIT_THRESHOLD = 1
EXIT_USAGE = 2
EXIT_INTERNAL = 3

EPILOG = """\
примеры:
  s7conv convert samples/scl --out build/converted
      разобрать все *.scl каталога (и таблицы тегов *.csv), записать раскладку
      build/converted/src/{DUTs,GVLs,POUs}/... и build/converted/tasks.json
  s7conv convert samples/scl --out build/converted --tags tags.csv --emit-support --clean
      то же с явной таблицей тегов, объектами поддержки S7Compat в раскладке и удалением старых файлов
  s7conv report samples/scl --md docs/CONVERSION_REPORT.md --html build/report.html
      только отчёт: что переведено автоматически, что требует проверки, что не поддерживается
  s7conv check samples/scl
      только разбор: синтаксические ошибки с номерами строк, код 1 при ошибках
  s7conv build-corpus [--check]
      корпус samples/scl → src/*/Converted, docs/CONVERSION_REPORT.md, задачи в
      tools/codesys/config.json, тесты сценариев tests/POUs/Scenarios и PRG_Tests;
      --check — только сравнить с репозиторием (код 1, если устарело)
  s7conv gen-tests scenarios --out tests [--check]
      только тесты coUnit по сценариям CSV для сконвертированного корпуса

коды выхода: 0 — успех, 1 — превышен порог --fail-on / ошибки разбора (check) / результат
в репозитории устарел (--check), 2 — неверные аргументы, входные файлы или сценарии,
3 — внутренняя ошибка конвертера
"""


def _common(p: argparse.ArgumentParser) -> None:
    p.add_argument("inputs", nargs="+", metavar="ВХОД", help="файлы *.scl, таблицы тегов *.csv или каталоги")
    p.add_argument("--tags", action="append", default=[], metavar="CSV", help="таблица тегов (можно повторять)")
    p.add_argument(
        "--ob-config",
        metavar="JSON",
        help='номера и периоды OB: {"Имя OB": {"number": 35, ...}}; по умолчанию ob_config.json из входного каталога',
    )
    p.add_argument(
        "--retain",
        choices=("retain", "persistent"),
        default="retain",
        help="реманентные переменные DB → VAR_GLOBAL RETAIN (по умолчанию) или PERSISTENT RETAIN",
    )
    p.add_argument(
        "--main-task", choices=("cyclic", "freewheeling"), default="cyclic", help="тип задачи для OB1 (MainTask)"
    )
    p.add_argument("--main-interval", type=int, default=10, metavar="МС", help="период MainTask, мс (cyclic)")
    p.add_argument("--folder", metavar="ИМЯ", help="папка проекта CODESYS для сгенерированных объектов")
    p.add_argument(
        "--timers",
        choices=M.SEMANTICS_MODES,
        default=M.STANDARD,
        help="TON/TOF/TP: standard — CODESYS Standard (по умолчанию); s7compat — FB_S7Ton/FB_S7Tof/FB_S7Tp "
        "с подменяемым источником времени (детерминированные тесты сценариев)",
    )
    p.add_argument(
        "--f-trig",
        choices=M.SEMANTICS_MODES,
        default=M.STANDARD,
        help="F_TRIG: standard — CODESYS Standard (по умолчанию); s7compat — FB_S7FTrig (семантика S7 "
        "на первом вызове)",
    )
    p.add_argument(
        "--fail-on",
        choices=("never", "todo", "check"),
        default="never",
        help="код 1, если есть неподдерживаемые (todo) или требующие проверки (check) конструкции",
    )
    p.add_argument("-q", "--quiet", action="store_true", help="без итоговой сводки")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="s7conv",
        description="Частичная автоматическая конвертация Siemens SCL (TIA Portal) в ST CODESYS V3.5 "
        "с отчётом о ручной работе.",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"s7conv {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="КОМАНДА")
    sub.required = True

    conv = sub.add_parser(
        "convert",
        help="сконвертировать и записать раскладку src/ и tasks.json",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _common(conv)
    conv.add_argument("--out", required=True, metavar="КАТАЛОГ", help="каталог результата (в нём src/ и tasks.json)")
    conv.add_argument("--clean", action="store_true", help="удалить из <out>/src файлы *.st, которых нет в результате")
    conv.add_argument(
        "--emit-support",
        action="store_true",
        help="добавить нужные объекты поддержки S7Compat (F_NormX, таймеры ...) из src/ репозитория",
    )
    conv.add_argument("--report-md", metavar="ФАЙЛ", help="записать отчёт Markdown")
    conv.add_argument("--report-html", metavar="ФАЙЛ", help="записать отчёт HTML")

    rep = sub.add_parser(
        "report",
        help="только отчёт конвертации (Markdown и/или HTML)",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _common(rep)
    rep.add_argument("--md", metavar="ФАЙЛ", help="отчёт Markdown (по умолчанию docs/CONVERSION_REPORT.md)")
    rep.add_argument("--html", metavar="ФАЙЛ", help="отчёт HTML (по умолчанию build/report.html)")

    chk = sub.add_parser(
        "check",
        help="только разбор SCL: синтаксические ошибки с номерами строк",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    chk.add_argument("inputs", nargs="+", metavar="ВХОД", help="файлы *.scl или каталоги")
    chk.add_argument("-q", "--quiet", action="store_true", help="только ошибки")

    bld = sub.add_parser(
        "build-corpus",
        help="корпус samples/scl → src/*/Converted, отчёт, задачи, тесты сценариев (--check — сверка)",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    bld.add_argument("--root", default=str(REPO_ROOT), metavar="КАТАЛОГ", help="корень репозитория")
    bld.add_argument("--check", action="store_true", help="ничего не писать: код 1, если файлы устарели")
    bld.add_argument("-q", "--quiet", action="store_true", help="без итоговой сводки")

    gen = sub.add_parser(
        "gen-tests",
        help="тесты coUnit по сценариям CSV для сконвертированного корпуса",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    gen.add_argument("scenarios", metavar="СЦЕНАРИИ", help="каталог с *.csv (формат — scenarios/README.md)")
    gen.add_argument("--out", required=True, metavar="КАТАЛОГ", help="каталог раскладки тестов (tests)")
    gen.add_argument(
        "--corpus",
        default=str(REPO_ROOT / C.CORPUS_REL),
        metavar="КАТАЛОГ",
        help="корпус SCL, по которому сопоставляются имена (по умолчанию samples/scl)",
    )
    gen.add_argument("--check", action="store_true", help="ничего не писать: код 1, если файлы устарели")
    gen.add_argument("-q", "--quiet", action="store_true", help="без итоговой сводки")
    return parser


def _options(args: argparse.Namespace, inputs: P.Inputs) -> Options:
    """Параметры эмиттера; --ob-config, иначе ob_config.json из входного каталога."""
    ob_config = args.ob_config or (str(inputs.ob_config) if inputs.ob_config else None)
    return Options(
        retain_mode=args.retain,
        folder=(args.folder,) if args.folder else (),
        main_task=args.main_task,
        main_interval_ms=args.main_interval,
        ob_config=P.load_ob_config(ob_config),
        timers=args.timers,
        f_trig=args.f_trig,
    )


def _write(path: str, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def _summary(result: ConversionResult) -> str:
    tot = R.totals(R.all_items(result))
    return (
        f"конструкций {tot.total}: автоматически {tot.auto} ({tot.pct(tot.auto):.0f} %), "
        f"требуют проверки {tot.check}, не поддерживаются {tot.todo}"
    )


def _threshold(result: ConversionResult, fail_on: str) -> bool:
    tot = R.totals(R.all_items(result))
    if fail_on == "todo":
        return tot.todo > 0
    if fail_on == "check":
        return tot.todo > 0 or tot.check > 0
    return False


def _input_labels(inputs: Sequence[str]) -> list[str]:
    return [P.display_path(Path(p)) for p in inputs]


def cmd_convert(args: argparse.Namespace) -> int:
    inputs = P.collect_inputs(args.inputs, args.tags)
    result, _files = P.run(inputs, _options(args, inputs))
    written = P.write_layout(result, Path(args.out), clean=args.clean, support=args.emit_support)
    labels = _input_labels(args.inputs)
    if args.report_md:
        _write(args.report_md, R.render_markdown(result, labels))
    if args.report_html:
        _write(args.report_html, R.render_html(result, labels))
    for error in result.errors:
        print(f"s7conv: предупреждение: {error}", file=sys.stderr)
    if not args.quiet:
        print(f"s7conv: файлов SCL {len(inputs.scl)}, записано {len(written)} файлов в {args.out}")
        print(f"s7conv: {_summary(result)}")
        if result.support and not args.emit_support:
            names = ", ".join(sorted(result.support))
            print(f"s7conv: нужны объекты поддержки {names} (src/*/S7Compat репозитория или --emit-support)")
    return EXIT_THRESHOLD if _threshold(result, args.fail_on) else EXIT_OK


def cmd_report(args: argparse.Namespace) -> int:
    inputs = P.collect_inputs(args.inputs, args.tags)
    result, _files = P.run(inputs, _options(args, inputs))
    labels = _input_labels(args.inputs)
    md = args.md or ("docs/CONVERSION_REPORT.md" if not args.html else None)
    html_path = args.html or ("build/report.html" if not args.md else None)
    if md:
        _write(md, R.render_markdown(result, labels))
    if html_path:
        _write(html_path, R.render_html(result, labels))
    if not args.quiet:
        targets = ", ".join(p for p in (md, html_path) if p)
        print(f"s7conv: отчёт записан: {targets}")
        print(f"s7conv: {_summary(result)}")
    return EXIT_THRESHOLD if _threshold(result, args.fail_on) else EXIT_OK


def cmd_check(args: argparse.Namespace) -> int:
    inputs = P.collect_inputs(args.inputs)
    files = P.parse_inputs(inputs)
    errors = 0
    blocks = 0
    for sf in files:
        name = P.display_path(Path(sf.path))
        blocks += sum(1 for b in sf.blocks if not getattr(b, "reason", None))
        for issue in sf.issues:
            print(f"{name}:{issue.line}:{issue.col}: {issue.severity}: {issue.message}")
            if issue.severity == "error":
                errors += 1
    if not args.quiet:
        status = "без ошибок" if not errors else f"ошибок разбора {errors}"
        print(f"s7conv check: файлов {len(files)}, блоков {blocks}, {status}")
    return EXIT_THRESHOLD if errors else EXIT_OK


def _print_diff(diff: C.Diff, what: str) -> None:
    for title, items in (("изменён", diff.changed), ("отсутствует", diff.missing), ("лишний", diff.stale)):
        for rel in items:
            print(f"s7conv: {what}: {title}: {rel}")


def cmd_build_corpus(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    try:
        built = C.build(root)
    except (C.CorpusError, TG.ScenarioError) as exc:
        print(f"s7conv build-corpus: ошибка: {exc}", file=sys.stderr)
        return EXIT_USAGE
    for warning in built.warnings:
        print(f"s7conv build-corpus: предупреждение: {warning}", file=sys.stderr)
    if args.check:
        diff = C.compare(built, root)
        if not diff.clean:
            _print_diff(diff, "build-corpus --check")
            print("s7conv build-corpus: результат в репозитории устарел — запустите python -m s7conv build-corpus")
            return EXIT_THRESHOLD
    else:
        diff = C.write(built, root)
    if not args.quiet:
        asserts = sum(s.asserts for s in built.tests.suites)
        tests = sum(s.tests for s in built.tests.suites)
        if args.check:
            state = "репозиторий совпадает с результатом"
        else:
            state = f"записано файлов {len(diff.changed) + len(diff.missing)}, удалено {len(diff.stale)}"
        print(f"s7conv build-corpus: {state}; файлов результата {len(built.files)}")
        print(f"s7conv build-corpus: {_summary(built.result)}")
        print(
            f"s7conv build-corpus: тесты сценариев — наборов {len(built.tests.suites)}, тестов {tests}, "
            f"проверок {asserts}; рукописных наборов в PRG_Tests {len(built.tests.hand_written)}"
        )
    return EXIT_OK


def cmd_gen_tests(args: argparse.Namespace) -> int:
    out = Path(args.out).resolve()
    corpus = Path(args.corpus)
    try:
        inputs = P.collect_inputs([str(corpus)])
        result, _ = P.run(inputs, C.corpus_options(corpus), base=Path.cwd())
        built = TG.generate(Path(args.scenarios), result, out.parent, out.name, Path.cwd())
    except TG.ScenarioError as exc:
        print(f"s7conv gen-tests: ошибка: {exc}", file=sys.stderr)
        return EXIT_USAGE
    root = out.parent
    files: dict[str, str] = {}
    for obj in built.objects:
        for rel, text in L.object_files(obj, out.name):
            files[rel] = L.normalize_text(text)
    managed = (f"{out.name}/POUs/{TG.SCENARIO_FOLDER}", f"{out.name}/POUs/{TG.PRG_TESTS}")
    diff = C.diff_files(files, root, managed)
    if args.check:
        if not diff.clean:
            _print_diff(diff, "gen-tests --check")
            return EXIT_THRESHOLD
    else:
        C.apply_diff(diff, files, root, managed)
    if not args.quiet:
        asserts = sum(s.asserts for s in built.suites)
        tests = sum(s.tests for s in built.suites)
        print(
            f"s7conv gen-tests: наборов {len(built.suites)}, тестов {tests}, проверок {asserts}; "
            f"рукописных наборов в PRG_Tests {len(built.hand_written)}"
        )
    return EXIT_OK


def configure_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def main(argv: Sequence[str] | None = None) -> int:
    configure_output()
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else EXIT_USAGE
        return EXIT_OK if code == 0 else EXIT_USAGE
    handlers = {
        "convert": cmd_convert,
        "report": cmd_report,
        "check": cmd_check,
        "build-corpus": cmd_build_corpus,
        "gen-tests": cmd_gen_tests,
    }
    try:
        return handlers[args.command](args)
    except (P.InputError, C.CorpusError, TG.ScenarioError) as exc:
        print(f"s7conv: ошибка: {exc}", file=sys.stderr)
        return EXIT_USAGE
    except Exception:  # pragma: no cover - защитная ветка: сбой конвертера не должен быть немым
        print("s7conv: внутренняя ошибка конвертера (сообщите с этим выводом):", file=sys.stderr)
        traceback.print_exc()
        return EXIT_INTERNAL


__all__ = ["EXIT_INTERNAL", "EXIT_OK", "EXIT_THRESHOLD", "EXIT_USAGE", "build_parser", "main"]
