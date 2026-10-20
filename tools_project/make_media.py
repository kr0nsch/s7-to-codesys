"""Медиа README из общего медиа-кита портфолио: баннер, снимки, график покрытия, GIF терминала.

Кит лежит вне репозитория (каталог `_scripts/media` портфолио); путь к нему — переменная окружения
`MEDIA_KIT` или ключ `--kit`. Снимки строятся из файлов репозитория и прогонов, поэтому перед `shots`
нужны `python -m s7conv build-corpus` (отчёты `build/report.html`, `build/report-lang.html`),
`python tools/codesys/cds.py test` (`build/test-results.json`) и `python tools_project/cds_plcopen.py test`
(`build/codesys/plcopen/test-results.json` — для снимка варианта SFC).

    set MEDIA_KIT=C:\\path\\to\\_scripts\\media
    python tools_project/make_media.py banner          # docs/media/banner-*.svg|png, social-preview.png
    python tools_project/make_media.py shots           # shot-*.png (и shot-graph-sfc) и chart-lang-coverage-*.png
    python tools_project/make_media.py gif             # demo-all-languages.gif из снятой сессии
    python tools_project/make_media.py gif --capture   # снять сессию заново (нужен CODESYS)

Сессия терминала хранится в `tools_project/media/demo-all-languages.json`: вывод снят командой
`term2gif.py capture` (домашний каталог заменён на `~`), при отрисовке длинные паузы сокращаются.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MEDIA = REPO / "docs" / "media"
SESSION = REPO / "tools_project" / "media" / "demo-all-languages.json"
DEMO_COMMANDS = (
    "python -m s7conv check samples/lang",
    "python -m s7conv convert samples/lang --out build/lang --timers s7compat --emit-support --plcopen build/plc",
    "python -m s7conv equiv samples/lang --scenarios scenarios/lang --random 500",
    "python tools/codesys/cds.py test --clean",
    "python tools_project/cds_plcopen.py test",
)
PROMPT = "\x1b[90mPS \x1b[94ms7-to-codesys\x1b[0m> "


def run(kit: Path, *args: str) -> None:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    print("[media]", " ".join(args))
    subprocess.run([sys.executable, *args], cwd=kit, env=env, check=True)


def banner(kit: Path) -> None:
    run(kit, "banner.py", "render", "--repo", "s7-to-codesys", "--repo-layout", "--out", str(MEDIA))


def shots(kit: Path) -> None:
    run(kit, str(Path("repo_media") / "s7_to_codesys.py"), "--repo", str(REPO))


def gif(kit: Path, capture: bool) -> None:
    if capture:
        opts = ["-o", str(SESSION), "--shell", "powershell", "--cwd", str(REPO), "--title", "Windows PowerShell"]
        opts += ["--prompt", PROMPT, "--cols", "100", "--pause", "1.2", "--"]
        run(kit, "term2gif.py", "capture", *opts, *DEMO_COMMANDS)
    run(kit, "term2gif.py", "render", str(SESSION), str(MEDIA / "demo-all-languages.gif"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="медиа README из медиа-кита портфолио")
    ap.add_argument("what", choices=["banner", "shots", "gif", "all"])
    ap.add_argument("--kit", default=os.environ.get("MEDIA_KIT"), help="каталог медиа-кита (MEDIA_KIT)")
    ap.add_argument("--capture", action="store_true", help="для gif: снять сессию заново")
    a = ap.parse_args(argv)
    if not a.kit or not (Path(a.kit) / "banner.py").is_file():
        print("make_media: укажите каталог медиа-кита: MEDIA_KIT или --kit", file=sys.stderr)
        return 2
    kit = Path(a.kit).resolve()
    if a.what in ("banner", "all"):
        banner(kit)
    if a.what in ("shots", "all"):
        shots(kit)
    if a.what in ("gif", "all"):
        gif(kit, a.capture)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
