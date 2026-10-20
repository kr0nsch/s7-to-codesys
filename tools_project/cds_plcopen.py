"""Вариант SFC блоков S7-GRAPH в CODESYS: импорт PLCopen XML скриптом, сборка и наборы coUnit.

    python tools_project/cds_plcopen.py check    # импорт PLCopen XML и сборка на устройстве (без coUnit)
    python tools_project/cds_plcopen.py test     # импорт, сборка и наборы coUnit в CODESYS Control Win
    python tools_project/cds_plcopen.py test --export build/codesys/plcopen/export.xml   # и обратный экспорт

Вход — файлы `plcopen/Lang/Converted/<Блок>.xml` (их пишет `python -m s7conv build-corpus`) или пути в
аргументах `--xml`. Устройство, CODESYS и профиль — те же настройки и переменные окружения, что у `cds.py`
(`CODESYS_EXE`, `CODESYS_PROFILE`, `CDS_DEVICE_*`): `check` собирает вариант SFC и для REGUL R500 в Astra.IDE, и для
ОВЕН ПЛК210 — программа `PRG_SfcCheck` в задаче `MainTask` вызывает каждый блок, coUnit не нужен.
`test` для каждого блока берёт рукописный многоцикловый набор `tests/POUs/Graph/<Блок>_SeqTest` — тот же, что
`cds.py test` прогоняет на ST-двойнике `src/POUs/Lang/Converted/<Блок>`: оба варианта проходят одни проверки.
Проект — `build/codesys/<имя>-plcopen.project` (отдельный от проектов `cds.py`), раскладка для импорта (наборы
и программа запуска `PRG_Tests` или программа `PRG_SfcCheck`) — во временном каталоге, после прогона удаляется.

Шаги выполняются в одном процессе CODESYS (`tools_project/codesys/cds_plcopen_entry.py`): import (модуль
шаблона `tools/codesys/import_sources.py`, раскладка ST), plcopen (`app.import_xml`, PLCopen XML — после ST),
build, test (`tools/codesys/run_tests.py`). Блокировки и рантайм — общие с `cds.py` (один рантайм на машину).
Итоги — `build/codesys/plcopen/test-results.json`, журналы — `build/codesys/plcopen/*.log`.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
TOOLS_CODESYS = REPO / "tools" / "codesys"
ENTRY = REPO / "tools_project" / "codesys" / "cds_plcopen_entry.py"
PLCOPEN_DIR = REPO / "plcopen" / "Lang" / "Converted"
SUITES_DIR = REPO / "tests" / "POUs" / "Graph"
SUITE_SUFFIX = "_SeqTest"
if str(TOOLS_CODESYS) not in sys.path:
    sys.path.insert(0, str(TOOLS_CODESYS))

from cdshost import cli  # noqa: E402

PRG_DECL = """// Программа запуска наборов варианта SFC (сгенерировано tools_project/cds_plcopen.py, не хранится в git).
PROGRAM PRG_Tests
VAR
{instances}
    xAllFinished : BOOL;  // все наборы завершены
END_VAR
"""
PRG_IMPL = """coUnit.RUN();
xAllFinished := {finished};
"""
CHECK_PRG = "PRG_SfcCheck"
CHECK_DECL = """// Проверка сборки вариантов SFC (сгенерировано tools_project/cds_plcopen.py, не хранится в git).
PROGRAM PRG_SfcCheck
VAR
{instances}
END_VAR
"""


class PlcopenError(Exception):
    """Нет входных файлов или набора для блока."""


def find_inputs(paths: list[str]) -> list[Path]:
    files = [Path(p).resolve() for p in paths] if paths else sorted(PLCOPEN_DIR.glob("*.xml"))
    if not files:
        raise PlcopenError(f"нет файлов PLCopen XML в {PLCOPEN_DIR} (python -m s7conv build-corpus)")
    missing = [str(f) for f in files if not f.is_file()]
    if missing:
        raise PlcopenError(f"нет файлов: {', '.join(missing)}")
    return files


def suite_dirs(xml_files: list[Path]) -> list[Path]:
    """Набор `<Блок>_SeqTest` для каждого файла `<Блок>.xml`."""
    found: list[Path] = []
    for xml in xml_files:
        suite = SUITES_DIR / f"{xml.stem}{SUITE_SUFFIX}"
        if not suite.is_dir():
            raise PlcopenError(f"нет набора {suite.relative_to(REPO).as_posix()} для {xml.name}")
        found.append(suite)
    return found


def prg_tests(suites: list[str]) -> tuple[str, str]:
    instances = "\n".join(f"    fb{name} : {name};  // рукописный набор" for name in suites)
    finished = "\n        AND ".join(f"fb{name}.AreAllTestsFinished()" for name in suites)
    return PRG_DECL.format(instances=instances), PRG_IMPL.format(finished=finished)


def make_check_layout(layout: Path, blocks: list[str]) -> None:
    """Раскладка проверки сборки: в src/ только PRG_SfcCheck с вызовом каждого блока (блоки — из PLCopen XML)."""
    if layout.exists():
        shutil.rmtree(layout)
    prg = layout / "src" / "POUs" / CHECK_PRG
    prg.mkdir(parents=True)
    instances = "\n".join(f"    fb{name} : {name};" for name in blocks)
    calls = "".join(f"fb{name}();\n" for name in blocks)
    (prg / f"{CHECK_PRG}.decl.st").write_text(CHECK_DECL.format(instances=instances), encoding="utf-8", newline="\n")
    (prg / f"{CHECK_PRG}.impl.st").write_text(calls, encoding="utf-8", newline="\n")


def make_layout(layout: Path, suites: list[Path]) -> None:
    """Раскладка тестов: пустой src/ (блоки — из PLCopen XML), наборы и PRG_Tests в tests/."""
    if layout.exists():
        shutil.rmtree(layout)
    (layout / "src").mkdir(parents=True)
    pous = layout / "tests" / "POUs"
    for suite in suites:
        shutil.copytree(suite, pous / "Graph" / suite.name)
    decl, impl = prg_tests([s.name for s in suites])
    prg = pous / "PRG_Tests"
    prg.mkdir(parents=True)
    (prg / "PRG_Tests.decl.st").write_text(decl, encoding="utf-8", newline="\n")
    (prg / "PRG_Tests.impl.st").write_text(impl, encoding="utf-8", newline="\n")


def run_entry(settings: cli.Settings, work: Path, job: dict[str, Any], timeout_s: float) -> dict[str, Any]:
    """Запуск CODESYS --noUI со скриптом cds_plcopen_entry.py (как cdshost.cli.run_codesys)."""
    job_path = work / "job.json"
    result_path = work / "result.json"
    stdout_path = work / "codesys.stdout.log"
    with contextlib.suppress(FileNotFoundError):
        result_path.unlink()
    cli.write_job(job_path, {**job, "result": str(result_path)})
    cmdline = cli.build_cmdline(settings.codesys_exe, settings.profile, ENTRY)
    env = {**os.environ, cli.JOB_ENV: str(job_path), "S7_TOOLS_CODESYS": str(TOOLS_CODESYS)}
    print(f"[plcopen] CODESYS {settings.profile}: {ENTRY.name} ...", flush=True)
    started = time.time()
    proc = subprocess.Popen(
        cmdline,
        cwd=str(REPO),
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        out, _ = proc.communicate(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        cli._kill_tree(proc.pid)
        out, _ = proc.communicate()
        stdout_path.write_text(out.decode(cli._oem_encoding(), "replace"), encoding="utf-8")
        raise cli.CdsError(
            f"CODESYS не завершился за {timeout_s:.0f} с; вывод: {stdout_path}", cli.EXIT_TIMEOUT
        ) from None
    stdout_path.write_text(out.decode(cli._oem_encoding(), "replace"), encoding="utf-8", newline="\n")
    if not result_path.exists():
        raise cli.CdsError(
            f"CODESYS завершился с кодом {proc.returncode}, но не записал результат; вывод: {stdout_path}",
            cli.EXIT_ENV,
        )
    result: dict[str, Any] = json.loads(result_path.read_text(encoding="utf-8"))
    result["elapsed_s"] = round(time.time() - started, 1)
    return result


def steps_for(
    settings: cli.Settings, command: str, layout: Path, work: Path, xml_files: list[Path], export: str | None
) -> list[dict[str, Any]]:
    project = REPO / cli.WORK_DIR / f"{settings.value('project.name')}-plcopen.project"
    tests = command == "test"
    imp = cli.import_step(settings, tests, project, clean=True, log_dir=work, name="import")
    imp["repo_root"] = str(layout)
    if not tests:  # одна задача с PRG_SfcCheck вместо задач режима normal (их программ в раскладке нет)
        task = {"name": "MainTask", "interval_ms": 10, "priority": 15, "pous": [CHECK_PRG]}
        imp["mode_config"] = {**imp["mode_config"], "tasks": [task]}
    plcopen = {
        "action": "plcopen",
        "project": str(project),
        "files": [str(f) for f in xml_files],
        "log": str(work / "plcopen.log"),
        "report": str(work / "plcopen.json"),
    }
    if export:
        plcopen["export"] = str(Path(export).resolve())
    build = {**cli.build_step(settings, project), "log": str(work / "build.log"), "report": str(work / "build.json")}
    steps = [imp, plcopen, build]
    if tests:
        test = cli.test_step(settings, project)
        test["log"] = str(work / "test.log")
        test["results"] = str(work / "test-results.json")
        test["meta"] = {**test["meta"], "repo": f"{REPO.name} (вариант SFC)"}
        steps.append(test)
    return steps


def print_plcopen(result: dict[str, Any]) -> None:
    for step in result.get("steps", []):
        if step.get("action") == "plcopen":
            print(f"[plcopen] импортировано из PLCopen XML: {', '.join(step.get('added') or []) or '—'}")
            for warn in step.get("warnings") or []:
                print(f"[plcopen]   предупреждение импорта: {warn}")


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            with contextlib.suppress(Exception):
                reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("check", "test"), help="check — импорт и сборка; test — и coUnit")
    parser.add_argument("--xml", action="append", default=[], metavar="ФАЙЛ", help="файл PLCopen XML (повторять)")
    parser.add_argument("--export", metavar="ФАЙЛ", help="после импорта выгрузить приложение в PLCopen XML")
    parser.add_argument("--restart-runtime", action="store_true", help="перезапустить рантайм перед тестами")
    args = parser.parse_args(argv)
    try:
        settings = cli.make_settings(REPO)
        xml_files = find_inputs(args.xml)
        work = REPO / cli.WORK_DIR / "plcopen"
        work.mkdir(parents=True, exist_ok=True)
        # раскладка — во временном каталоге с коротким путём: пути методов наборов в глубоком build/ клона
        # упираются в предел 260 символов Windows (shutil.copytree: WinError 3)
        with tempfile.TemporaryDirectory(prefix="s7plc-") as tmp:
            layout = Path(tmp) / "layout"
            if args.command == "test":
                make_layout(layout, suite_dirs(xml_files))
            else:
                make_check_layout(layout, [f.stem for f in xml_files])
            steps = steps_for(settings, args.command, layout, work, xml_files, args.export)
            timeout = settings.number("codesys.timeout_s")
            with cli.repo_lock(settings, f"plcopen {args.command}"):
                if args.command == "test":
                    timeout += settings.number("tests.timeout_s")
                    with cli.runtime_lock(settings, f"plcopen test {REPO.name}"):
                        cli.ensure_runtime(settings, restart=args.restart_runtime)
                        result = run_entry(settings, work, {"steps": steps}, timeout)
                else:
                    result = run_entry(settings, work, {"steps": steps}, timeout)
    except PlcopenError as exc:
        print(f"[plcopen] {exc}", file=sys.stderr)
        return cli.EXIT_USAGE
    except cli.CdsError as exc:
        print(f"[plcopen] {exc}", file=sys.stderr)
        return exc.code
    print_plcopen(result)
    code = cli._finish(result)
    results = work / "test-results.json"
    if args.command == "test" and results.exists():
        print(f"[plcopen] результаты: {results}")
    return code


if __name__ == "__main__":
    sys.exit(main())
