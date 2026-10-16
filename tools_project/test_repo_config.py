"""Проверки настроек репозитория s7-to-codesys: проект отличается от шаблона ровно так, как задумано.

Тесты шаблона проверяют у файлов проекта только разбор и схему (test_repository_toml_is_valid,
test_cds_config.py); здесь — что отличия именно те, что описаны в docs/STATIC_ANALYSIS.md:

- st_lint.toml = умолчания st_lint.py плюс исключения src/*/Converted/* для правил оформления;
- tools/codesys/config.json: как у шаблона, кроме задач режима normal (они из OB корпуса) и ссылки на
  библиотеку Standard (плейсхолдер в library.libraries — сконвертированный код использует TON, R_TRIG, CTU).
"""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any

import st_lint

REPO_ROOT = Path(__file__).resolve().parents[1]
CONVERTED = "src/*/Converted/*"
# Правила оформления, снятые с кода, который генерирует s7conv (обоснование — шапка st_lint.toml)
EXEMPT_RULES = ("STL004", "STL006", "STL007", "STL008", "STL011")


def test_st_lint_config_differs_from_template_only_by_converted_exemptions() -> None:
    expected = copy.deepcopy(st_lint.DEFAULT_CONFIG)
    for rule in EXEMPT_RULES:
        cfg = expected["rules"].setdefault(rule, {})
        cfg["exclude"] = [*cfg.get("exclude", []), CONVERTED]
    assert st_lint.load_config(st_lint.DEFAULT_CONFIG_PATH) == expected


def test_st_lint_still_checks_format_rules_in_converted() -> None:
    config = st_lint.load_config(st_lint.DEFAULT_CONFIG_PATH)
    assert config["lint"]["exclude"] == []
    for rule in ("STL001", "STL002", "STL003", "STL005", "STL009", "STL010", "STL012"):
        assert CONVERTED not in config["rules"].get(rule, {}).get("exclude", []), rule
        assert config["severity"][rule] == "error"


CONFIG = REPO_ROOT / "tools" / "codesys" / "config.json"


def test_codesys_config_is_template_config_with_corpus_tasks() -> None:
    from s7conv import corpus as C

    text = CONFIG.read_text(encoding="utf-8")
    data: dict[str, Any] = json.loads(text)
    user = os.environ.get("USERNAME") or os.environ.get("USER")
    assert not user or f"/{user.lower()}/" not in text.lower().replace("\\\\", "/")
    assert "C:\\\\Users" not in text and "C:/Users" not in text
    assert data["device"]["type"]["default"] == 4096
    assert data["device"]["id"]["default"] == "0000 0001"
    assert data["modes"]["test"]["tasks"] == [{"name": "TestTask", "interval_ms": 10, "pous": ["PRG_Tests"]}]
    assert data["modes"]["test"]["libraries"] == ["counit"]
    built = C.build(REPO_ROOT)
    assert data["modes"]["normal"]["tasks"] == C.config_tasks(built.result)
    main = data["modes"]["normal"]["tasks"][0]
    assert main["name"] == "MainTask" and main["pous"][-1] == "PRG_Main"
    # единственное отличие ссылок на библиотеки от шаблона — Standard через плейсхолдер профиля
    assert data["libraries"]["standard"] == {
        "label": "Standard (плейсхолдер, разрешает профиль CODESYS)",
        "title": "Standard",
        "company": "System",
        "version": "*",
        "placeholder": "Standard",
        "namespace": "Standard",
        "qualified_only": False,
    }
    assert data["library"]["libraries"] == ["standard"]
    assert data["modes"]["normal"]["libraries"] == []


def test_codesys_projects_reference_standard_and_counit(tmp_path: Path) -> None:
    """Замена test_cds.py::test_mode_config_resolves_libraries: Standard нужен проекту приложения, тестам и
    проверке всего пула объектов (cds.py library), coUnit — только тестовому проекту."""
    from cdshost import cli

    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    environ = {"USERPROFILE": str(tmp_path), "HOME": str(tmp_path), "LOCALAPPDATA": str(tmp_path)}
    s = cli.Settings(data, tmp_path, cli.make_getenv(environ, registry=False))
    assert [x["key"] for x in s.mode_config("normal")["libraries"]] == ["standard"]
    assert [x["key"] for x in s.mode_config("test")["libraries"]] == ["counit", "standard"]
    assert [x["key"] for x in s.other_libraries("normal")] == ["counit"]
    assert s.other_libraries("test") == []
    assert s.referenced_library_keys() == ["counit", "standard"]
    assert [x["key"] for x in s.library_config()["libraries"]] == ["standard"]
    standard = s.library_spec("standard")
    assert standard["placeholder"] == "Standard" and standard["install_from"] is None
