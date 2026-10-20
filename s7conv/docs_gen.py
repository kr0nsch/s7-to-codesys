"""Справочники соответствий языков S7, генерируемые из таблиц конвертера (build-corpus, --check).

docs/MAPPING_LADFBD.md — словарь элементов LAD/FBD (PARTS, lower/net_to_ast.py) с происхождением каждой
строки; docs/MAPPING_STL.md — все 172 токена StlToken XSD V21 (TOKENS, lower/stl_tokens.py) с классом,
правилом и тестами. Тесты строк — из samples/rules_matrix.py. Руками эти файлы не правятся.
"""

from __future__ import annotations

import importlib.util
from collections import Counter
from pathlib import Path

from s7conv import __version__
from s7conv.layout import REPO_ROOT
from s7conv.lower.net_to_ast import PARTS
from s7conv.lower.stl_tokens import TOKENS

GEN = "Сгенерирован `s7conv {v}` из таблиц конвертера — не редактировать, пересоздаётся `s7conv build-corpus`."

# Что получается в ST из правила (для таблицы LAD/FBD)
LAD_ST = {
    "contact": "булево выражение: последовательно — AND, ветви (O) — OR, Negated — NOT",
    "coil": "`op := rlo;` (Negated operand — `op := NOT rlo;`)",
    "set_reset": "`IF rlo THEN op := TRUE/FALSE; END_IF`",
    "edge": "явный бит памяти: `q := clk AND NOT m; m := clk;`",
    "sr_operand": "два IF в порядке S7 (SR: сначала S, затем R1; RS: сначала R, затем S1), `q := op`",
    "compare": "`pre AND (a op b)`",
    "move": "`IF en THEN out := in; END_IF`, ENO = EN",
    "math": "`IF en THEN out := a op b; END_IF`; подключённый ENO — `F_S7Eno<Оп><Тип>` до записи",
    "convert": "`SRC_TO_DST(in)` по SrcType/DestType",
    "calculate": "выражение Equation с подстановкой IN1…INn",
    "instruction": "функция SCL (LIMIT, SEL, NORM_X → F_NormX, SCALE_X → F_ScaleX, SHL/SHR, MIN/MAX)",
    "timer": "вызов экземпляра `inst(IN := …, PT := …)`, выходы `inst.Q/ET`; TON_TIME → TON или FB_S7Ton",
    "counter": "вызов экземпляра `inst(CU := …, R := …, PV := …)`",
    "call": "вызов FB/FC под `IF en`; вызываемый на LAD/FBD без ENO/BR — ENO = EN",
    "jump": "прыжок вперёд через сети → `IF NOT rlo THEN … END_IF`",
    "return": "`IF rlo THEN RETURN; END_IF`",
}


def _rule_tests() -> dict[str, tuple[str, ...]]:
    path = REPO_ROOT / "samples" / "rules_matrix.py"
    spec = importlib.util.spec_from_file_location("s7conv_rules_matrix", path)
    if spec is None or spec.loader is None:  # pragma: no cover - файл в репозитории
        return {}
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    tests: dict[str, tuple[str, ...]] = module.RULE_TESTS
    return tests


def _tests_cell(tests: tuple[str, ...]) -> str:
    return "<br>".join(f"`{t}`" for t in tests) if tests else "— (P1)"


def render_mapping_ladfbd() -> str:
    tests = _rule_tests()
    out = [
        "# Соответствие LAD/FBD → ST: словарь элементов",
        "",
        GEN.format(v=__version__),
        "",
        "XSD SimaticML не ограничивает имена элементов `Part` и их пинов (`SimaticName`, `PinName_TE` —",
        "`xs:string`), поэтому перевод держится на словаре: строка — имя Part, правило, что получается в ST и",
        "откуда известны имя и пины. Уровень **H** — имя и пины есть в открытом экспорте TIA Portal",
        "(`samples/lang/EXTERNAL.json`), **L** — по руководству Siemens, экспорта нет; элемент уровня L",
        "переводится, но получает пометку `vocab_unverified` (не выше «требует проверки»). Префикс правила в",
        "отчёте — `lad.` для LAD и `fbd.` для FBD. Неизвестный элемент — `unknown_part` (MIGRATION-TODO с UId),",
        "висячий провод или потерянный операнд — `wire`.",
        "",
        "| Part | Правило | Что | Уровень | Откуда имя и пины | ST | Тесты |",
        "|---|---|---|---|---|---|---|",
    ]
    for name, rule in sorted(PARTS.items(), key=lambda kv: (kv[1].rule, kv[0])):
        out.append(
            f"| `{name}` | `{rule.rule}` | {rule.title} | {rule.level} | {rule.source} | "
            f"{LAD_ST.get(rule.rule, '—')} | {_tests_cell(tests.get(rule.rule, ()))} |"
        )
    counts = Counter(p.level for p in PARTS.values())
    out += [
        "",
        f"Элементов в словаре: {len(PARTS)}; подтверждены открытым экспортом (H): {counts['H']}, по руководству",
        f"(L): {counts['L']}.",
        "",
        "## Ловушки, которые перевод учитывает явно",
        "",
        "| Ловушка | Как переводится | Правило |",
        "|---|---|---|",
        "| SR/RS у S7 и CODESYS называются одинаково, приоритет противоположный; в LAD/FBD состояние хранит "
        "бит-операнд | два IF на бит-операнд в порядке S7; экземпляр SR/RS CODESYS не используется (бит пишут "
        "другие сети и HMI) | `sr_operand` |",
        "| ENO = EN AND NOT ошибка блока (LAD S7-300/400, прил. C.1); в CODESYS ENO = EN | ENO арифметики INT/DINT "
        "— `F_S7Eno<Оп><Тип>` до записи результата; прочее — ENO = EN с пометкой | `eno_error` |",
        "| бит памяти P/N может читать другая сеть | явная переменная-бит, а не скрытая память R_TRIG | `edge` |",
        "| бит памяти фронта во временной области (ошибка исходной программы) | перевод как есть, пометка | "
        "`edge_memory` |",
        "| деление на 0: S7 — ENO = 0, CODESYS — исключение | деление под условием делитель <> 0 | `div_zero` |",
        "| вызов блока, который пишет ENO/BR | ENO = EN с пометкой | `call_eno` |",
        "",
        "Сети SCL внутри блока LAD/FBD переводятся как SCL (правило `scl.network`); сети STL — по",
        "[MAPPING_STL.md](MAPPING_STL.md).",
    ]
    return "\n".join(out) + "\n"


def render_mapping_stl() -> str:
    tests = _rule_tests()
    counts = Counter(t.cls for t in TOKENS.values())
    out = [
        "# Соответствие STL → ST: все токены XSD V21",
        "",
        GEN.format(v=__version__),
        "",
        "Перечень — 172 значения `StlToken` из `SW.PlcBlocks.STL_v5.xsd` (TIA Portal V21; SHA-256 файла — в",
        "`samples/lang/EXTERNAL.json`). Имя токена не зависит от мнемоники: XML даёт его напрямую, разборщик",
        "AWL переводит мнемонику EN/DE в те же имена. Класс: **auto** — переводится без пометки; **check** —",
        "с пометкой `MIGRATION-CHECK`; **todo** — в этом выпуске не переводится (`MIGRATION-TODO`, исходная",
        "инструкция в комментарии); **impossible** — аналога в CODESYS нет.",
        "",
        "Перевод — символьный подъём (режим A): RLO — выражение, /FC, OR-группы и скобки — состояние",
        "транслятора, ACCU — типизированные выражения; переходы восстанавливаются в IF/ELSE (`structured`) или",
        "автомат CASE (`pc`), `JMP` в ST не попадает. Правила с пометкой, которые возникают не из токена, а из",
        "типов: `stl.zero_extend` (`L` WORD/INT → DINT дополняется нулями), `stl.accu_high` (старшая часть",
        "ACCU1), `stl.bitcopy` (копия битов между INT/DINT и REAL), `stl.jump_pc` (автомат переходов).",
        "",
        f"Итог классификации: {len(TOKENS)} из {len(TOKENS)} токенов; auto — {counts['auto']}, check — "
        f"{counts['check']}, todo — {counts['todo']}, impossible — {counts['impossible']}.",
        "",
        "| Токен XSD | EN | DE | Класс | Правило | Что | Тесты |",
        "|---|---|---|---|---|---|---|",
    ]
    for token, rule in sorted(TOKENS.items(), key=lambda kv: kv[0].lower()):
        cell = _tests_cell(tests.get(rule.rule, ())) if rule.cls in ("auto", "check") else "—"
        en = f"`{rule.en}`" if rule.en else "—"
        de = f"`{rule.de}`" if rule.de else "—"
        out.append(f"| `{token}` | {en} | {de} | {rule.cls} | `{rule.rule}` | {rule.title} | {cell} |")
    return "\n".join(out) + "\n"


def write_all(root: Path = REPO_ROOT) -> dict[str, str]:
    return {"docs/MAPPING_LADFBD.md": render_mapping_ladfbd(), "docs/MAPPING_STL.md": render_mapping_stl()}


__all__ = ["render_mapping_ladfbd", "render_mapping_stl", "write_all"]
