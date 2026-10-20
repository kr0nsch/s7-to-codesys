"""Отчёт конвертации: Markdown (docs/CONVERSION_REPORT.md) и автономный HTML (build/report.html).

«Конструкция» — единица учёта: блок S7, объявление переменной или оператор (вложенные операторы
считаются отдельно). Статус конструкции: auto — переведена автоматически; check — переведена,
нужна проверка (MIGRATION-CHECK); todo — не переведена (MIGRATION-TODO). Отчёт детерминирован:
без даты и абсолютных путей, чтобы его можно было хранить в git и сравнивать.
"""

from __future__ import annotations

import html
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from s7conv import __version__
from s7conv.emitter import AUTO, CHECK, TODO, ConversionResult, FileResult, Item, Note
from s7conv.nodes import LangUnit

STATUS_LABEL = {AUTO: "автоматически", CHECK: "требует проверки", TODO: "не поддерживается"}
STATUS_ICON = {AUTO: "✓", CHECK: "!", TODO: "✕"}
CATEGORY_LABEL = {"block": "Блоки", "decl": "Объявления", "stmt": "Операторы"}

# Короткие названия правил для сводки (полное описание — docs/MAPPING.md)
RULE_TITLES = {
    "parse.stmt": "оператор не разобран",
    "parse.decl": "объявление не разобрано",
    "parse.block": "блок не разобран",
    "type.s5time": "S5Time → TIME",
    "type.char": "Char → STRING(1)",
    "type.wchar": "WChar → WSTRING(1)",
    "type.unsupported": "тип S7 без аналога",
    "type.unknown": "тип не найден в корпусе",
    "type.ref": "REF_TO",
    "type.generic": "IEC_TIMER/IEC_COUNTER без вызова",
    "type.array_star": "Array[*]",
    "fb.counter": "счётчики CTU/CTD/CTUD (WORD)",
    "fb.ltimer": "таймеры LTIME",
    "fb.f_trig": "F_TRIG: начальное состояние памяти",
    "fb.flipflop": "SR/RS: имена входов",
    "fb.generic": "IEC_TIMER → тип по вызову",
    "fb.unsupported": "ФБ инструкции без аналога",
    "func.unsupported": "функция S7 без аналога",
    "func.round": "ROUND → REAL_TO_DINT",
    "func.scale_x_int": "SCALE_X с целым результатом",
    "func.typed_variant": "NORM_X/SCALE_X с типом",
    "func.bound": "UPPER_BOUND/LOWER_BOUND",
    "func.time_tck": "TIME_TCK → TIME()",
    "conv.bitcast": "DWORD↔REAL: битовый образ",
    "conv.round": "REAL → целое: округление",
    "conv.s5time": "S5TIME_TO_TIME",
    "conv.unsupported": "преобразование без аналога",
    "lit.time_negative": "отрицательный TIME",
    "lit.char": "литерал CHAR#",
    "lit.counter": "литерал C#",
    "lit.pointer": "указатель P#",
    "lit.long_date": "LDT#/LTOD#",
    "lit.unknown": "неизвестный литерал",
    "stmt.goto": "GOTO",
    "stmt.label": "метка перехода",
    "stmt.pragma": "прагма в коде",
    "stmt.try_assign": "присваивание ?=",
    "stmt.lvalue": "неверная левая часть :=",
    "expr.slice": "срез .%B/.%W/.%D",
    "expr.eno": "EN/ENO/OK",
    "expr.power": "** → EXPT для целых",
    "expr.time_sub": "вычитание TIME: знак",
    "expr.div_int": "целое деление на переменную",
    "expr.string_index": "символ строки по индексу",
    "func.sqr": "SQR(вызов) → EXPT",
    "expr.db_whole": "DB целиком",
    "expr.block_value": "блок как значение",
    "call.eno": "параметр EN/ENO",
    "call.unknown": "вызов неизвестного блока",
    "call.param": "параметры встроенной функции",
    "call.param_unknown": "параметр не найден",
    "call.mixed_args": "смешанные аргументы",
    "call.member": "вызов через элемент",
    "call.instance_unknown": "тип экземпляра не найден",
    "call.unsupported": "вызов не поддерживается",
    "decl.at": "AT (наложение)",
    "decl.dropped_use": "использует неперенесённое объявление",
    "call.param_dropped": "аргумент неперенесённого параметра",
    "call.param_renamed": "параметр ФБ инструкции переименован",
    "decl.hmi_access": "атрибуты доступа HMI/OPC UA",
    "decl.attr": "атрибут S7",
    "name.renamed": "переименование (ключевое слово)",
    "name.undeclared": "необъявленная переменная",
    "name.plain": "имя без # и кавычек",
    "sym.unknown": "символ не найден → GVL_Tags",
    "sym.unknown_db": "DB не найден в корпусе",
    "sym.unknown_decl": "тип символа выведен",
    "addr.unsupported": "адрес не I/Q/M",
    "addr.peripheral": "доступ к периферии :P",
    "addr.unaligned": "адрес не выровнен",
    "addr.overlap": "перекрытие адресов (порядок байтов)",
    "access.fb_static": "доступ к статике экземпляра",
    "access.db_member": "элемент DB не найден",
    "db.begin": "BEGIN DB: оператор не начальное значение",
    "db.begin_array": "BEGIN DB: элементы массива не подряд",
    "db.begin_static": "BEGIN DB: внутренние переменные экземпляра",
    "db.begin_member": "BEGIN DB: элемент не найден",
    "expr.slice_read": "чтение среза .%B/.%W/.%D",
    "expr.slice_write": "запись в срез .%B/.%W/.%D",
    "ob.initial_call": "Initial_Call: эмуляция",
    "tag.s5": "тег таймера/счётчика S5",
    "db.retain_standard": "стандартный DB: retain",
    "db.persistent": "PERSISTENT в GVL",
    "db.read_only": "DB READ_ONLY",
    "db.generic": "DB IEC_TIMER без вызова",
    "db.implicit_instance": "экземплярный DB выведен по вызову",
    "block.non_optimized": "неоптимизированный доступ",
    "block.know_how": "KNOW_HOW_PROTECT",
    "block.duplicate": "повтор блока",
    "section.db_specific": "реманентность DB_SPECIFIC",
    "section.fb_retain": "VAR RETAIN в ФБ: весь экземпляр",
    "ob.start_info": "стартовая информация OB",
    "ob.startup": "OB100 → флаг первого цикла",
    "ob.cyclic": "период циклического OB",
    "ob.main": "номер OB не указан",
    "ob.event": "событийный OB",
    "udt.alias": "TYPE без STRUCT",
    "tag.type": "тип тега",
    "tag.const": "константа пользователя",
}


@dataclass(frozen=True)
class Totals:
    auto: int
    check: int
    todo: int

    @property
    def total(self) -> int:
        return self.auto + self.check + self.todo

    def pct(self, value: int) -> float:
        return 100.0 * value / self.total if self.total else 0.0

    def of(self, status: str) -> int:
        return {AUTO: self.auto, CHECK: self.check, TODO: self.todo}[status]


def totals(items: Iterable[Item]) -> Totals:
    counter = Counter(i.status for i in items)
    return Totals(counter[AUTO], counter[CHECK], counter[TODO])


def all_items(result: ConversionResult) -> list[Item]:
    return [i for f in result.files for i in f.items]


def all_notes(result: ConversionResult) -> list[tuple[FileResult, Note]]:
    return [(f, n) for f in result.files for n in f.notes]


def rule_title(note: Note) -> str:
    return RULE_TITLES.get(note.rule, note.rule)


def rule_summary(result: ConversionResult, severity: str) -> list[tuple[str, str, int]]:
    """(правило, название, число пометок) по убыванию числа."""
    counter: Counter[str] = Counter()
    titles: dict[str, str] = {}
    for _f, n in all_notes(result):
        if n.severity == severity:
            counter[n.rule] += 1
            titles.setdefault(n.rule, rule_title(n))
    return [(rule, titles[rule], count) for rule, count in sorted(counter.items(), key=lambda x: (-x[1], x[0]))]


def _pct(value: float) -> str:
    return f"{value:.0f} %"


def _sorted_notes(notes: Sequence[Note]) -> list[Note]:
    order = {TODO: 0, CHECK: 1}
    return sorted(notes, key=lambda n: (n.line == 0, n.line, order.get(n.severity, 2), n.rule, n.message))


# ---------------------------------------------------------------------------
# Языки S7 (LAD, FBD, STL, GRAPH): раздел появляется, только если во входе есть SimaticML
# ---------------------------------------------------------------------------

LANG_ORDER = ("LAD", "FBD", "STL", "SCL", "GRAPH", "DB", "UDT")
UNIT_KINDS = {"element": "элемент", "network": "сеть", "instruction": "инструкция", "step": "шаг"}
UNIT_STATUSES = (AUTO, CHECK, TODO, "impossible")
UNIT_STATUS_LABEL = {AUTO: "авто", CHECK: "проверка", TODO: "нет", "impossible": "невозможно"}
LANG_RULE_TITLES = {
    "lad.contact": "LAD: контакты, ветви, NOT",
    "lad.coil": "LAD: катушка",
    "lad.set_reset": "LAD: катушки S/R",
    "lad.sr_operand": "LAD: SR/RS с битом-операндом",
    "lad.edge": "LAD: фронт с явным битом памяти",
    "lad.edge_memory": "LAD: бит памяти фронта во временной области",
    "lad.compare": "LAD: сравнение",
    "lad.move": "LAD: MOVE",
    "lad.math": "LAD: арифметика",
    "lad.eno_error": "LAD: ENO = EN AND NOT ошибка",
    "lad.div_zero": "LAD: деление на 0",
    "lad.convert": "LAD: преобразование",
    "lad.instruction": "LAD: инструкция-блок",
    "lad.calculate": "LAD: CALCULATE",
    "lad.timer": "LAD: таймер с экземпляром",
    "lad.counter": "LAD: счётчик с экземпляром",
    "lad.call": "LAD: вызов FB/FC",
    "lad.call_eno": "LAD: ENO вызова",
    "lad.jump": "LAD: прыжок вперёд → IF",
    "lad.jump_irreducible": "LAD: несводимый прыжок",
    "lad.return": "LAD: RET",
    "lad.wire": "LAD: висячий провод или операнд",
    "lad.instance": "LAD: блок без экземпляра",
    "lad.unknown_part": "LAD: неизвестный элемент",
    "lad.vocab_unverified": "LAD: форма XML элемента не подтверждена экспортом",
    "scl.network": "сеть SCL",
    "stl.logic": "STL: логика битов",
    "stl.edge": "STL: FP/FN с явным битом памяти",
    "stl.edge_memory": "STL: бит памяти фронта во временной области",
    "stl.accu": "STL: L/T",
    "stl.math": "STL: арифметика",
    "stl.compare": "STL: сравнение",
    "stl.call": "STL: CALL/UC/CC",
    "stl.call_registers_1500": "STL S7-1500: состояние после CALL",
    "stl.block_end": "STL: BE/BEU/BEC",
    "stl.nop": "STL: NOP, комментарии",
    "stl.jump_structured": "STL: переход → IF/ELSE",
    "stl.jump_pc": "STL: автомат переходов CASE",
    "stl.jump_dead": "STL: недостижимый участок после JU",
    "stl.zero_extend": "STL: L WORD/INT в DINT — дополнение нулями",
    "stl.accu_high": "STL: старшая часть ACCU1",
    "stl.bitcopy": "STL: копия битов через ACCU",
    "stl.type": "STL: тип ACCU1 и операнда",
    "stl.mode_b": "STL: слово состояния, TAK/PUSH/POP (режим B)",
    "stl.addr_register": "STL: адресные регистры",
    "stl.db_register": "STL: регистры DB",
    "stl.db_offset": "STL: доступ к DB по смещению",
    "stl.mcr": "STL: MCR",
    "stl.loop": "STL: LOOP",
    "stl.jump_list": "STL: JL",
    "stl.round": "STL: RND",
    "stl.convert": "STL: преобразования",
    "stl.word_logic": "STL: логика слов",
    "stl.shift": "STL: сдвиги",
    "stl.rlo_unknown": "STL: RLO не определён",
    "stl.accu_unknown": "STL: ACCU не определён",
    "stl.operand": "STL: инструкция без операнда",
    "stl.bracket": "STL: скобки",
    "stl.bracket_depth": "STL: глубина скобок",
    "stl.unknown": "STL: неизвестный токен",
    "s5.timer": "S5: таймер",
    "s5.counter": "S5: счётчик",
    "xml.profile_mismatch": "XML: профиль CPU не совпадает с MemoryLayout",
    "xml.unit_unsupported": "XML: сеть на неподдерживаемом языке",
    "func.s7compat_eno": "ENO арифметики S7 (S7Compat)",
}
RULE_TITLES.update(LANG_RULE_TITLES)
RULE_TITLES.update({k.replace("lad.", "fbd.", 1): v.replace("LAD:", "FBD:", 1) for k, v in LANG_RULE_TITLES.items()})


def has_languages(result: ConversionResult) -> bool:
    """Во входе есть SimaticML/AWL (понижённые языки S7)."""
    return any(f.lowering is not None for f in result.files)


def _lang_units(result: ConversionResult) -> list[LangUnit]:
    return [u for f in result.files if f.lowering is not None for u in f.lowering.units]


def _block_langs(result: ConversionResult) -> dict[str, str]:
    langs: dict[str, str] = {}
    for f in result.files:
        if f.lowering is None:
            for _kind, name, _st in f.blocks:
                langs.setdefault(name.lower(), "SCL")
            continue
        langs.update(f.lowering.langs)
    return langs


def language_rows(result: ConversionResult) -> list[tuple[str, str, int, dict[str, int]]]:
    """(язык, вид единицы, блоков, {статус: число}) — единица учёта по M8: элемент и сеть, инструкция, шаг."""
    units = _lang_units(result)
    blocks: dict[str, set[str]] = {}
    for u in units:
        blocks.setdefault(u.lang, set()).add(u.block)
    rows: list[tuple[str, str, int, dict[str, int]]] = []
    for lang in sorted({u.lang for u in units}, key=lambda x: (LANG_ORDER.index(x) if x in LANG_ORDER else 99, x)):
        for kind in UNIT_KINDS:
            subset = [u for u in units if u.lang == lang and u.kind == kind]
            if subset:
                counts = {s: sum(1 for u in subset if u.status == s) for s in UNIT_STATUSES}
                rows.append((lang, kind, len(blocks[lang]), counts))
    return rows


def language_section(result: ConversionResult) -> list[str]:
    if not has_languages(result):
        return []
    out = [
        "",
        "## По языкам",
        "",
        "Единица учёта языка: LAD/FBD — элемент и сеть, STL — инструкция, GRAPH — шаг (ниже — независимо от",
        "конструкций ST выше). Статус единицы — тяжелейший из её правил: **авто**, **проверка**",
        "(`MIGRATION-CHECK`), **нет** (`MIGRATION-TODO`), **невозможно** (аналога в CODESYS нет).",
        "",
        "| Язык | Единица | Блоков | Всего | Авто | Проверка | Нет | Невозможно |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for lang, kind, nblocks, counts in language_rows(result):
        total = sum(counts.values())
        out.append(
            f"| {lang} | {UNIT_KINDS[kind]} | {nblocks} | {total} | {counts[AUTO]} | {counts[CHECK]} | "
            f"{counts[TODO]} | {counts['impossible']} |"
        )
    out += ["", "### Блоки: язык, стратегия, переходы STL", ""]
    out += ["| Блок | Язык | Стратегия | Профиль и переходы STL | Источник |", "|---|---|---|---|---|"]
    opts = result.options
    for f in result.files:
        if f.lowering is None:
            continue
        for _kind, name, _st in f.blocks:
            key = name.lower()
            lang = f.lowering.langs.get(key, "SCL")
            strategy = f.lowering.strategies.get(key, "st")
            stl = "—"
            if lang == "STL":
                pc = any(u.rule == "stl.jump_pc" for u in f.lowering.units if u.block.lower() == key)
                cpu = opts.cpu or "по MemoryLayout"
                stl = f"{cpu}; переходы: {'pc' if pc or opts.stl_jumps == 'pc' else 'structured'}"
            out.append(f"| `{_md(name)}` | {lang} | `{strategy}` | {stl} | `{_md(f.path)}` |")
    counter: Counter[str] = Counter()
    statuses: dict[str, str] = {}
    for u in _lang_units(result):
        if u.status != AUTO:
            counter[u.rule] += 1
            statuses[u.rule] = u.status
    out += ["", "### Правила языков: проверка и ручная работа", ""]
    if not counter:
        out += ["Нет: все единицы переведены автоматически.", ""]
        return out
    out += ["| Правило | Что | Статус | Единиц |", "|---|---|---|---:|"]
    for rule, count in sorted(counter.items(), key=lambda x: (-x[1], x[0])):
        title = RULE_TITLES.get(rule, rule)
        out.append(f"| `{rule}` | {_md(title)} | {UNIT_STATUS_LABEL.get(statuses[rule], statuses[rule])} | {count} |")
    out.append("")
    return out


def language_html(result: ConversionResult) -> str:
    """Карточка «По языкам» для HTML-отчёта."""
    if not has_languages(result):
        return ""
    parts = ['<section class="card">', "<h2>По языкам S7</h2>"]
    parts.append(
        '<p class="hint">Единица учёта: LAD/FBD — элемент и сеть, STL — инструкция. Статус — тяжелейший из '
        "правил единицы.</p>"
    )
    parts.append('<div class="scroll"><table><thead><tr><th>Язык</th><th>Единица</th><th class="num">Блоков</th>')
    parts.append('<th class="num">Всего</th><th class="barcell">Статус</th>')
    parts.append(
        f'<th class="num">{STATUS_ICON[AUTO]}</th><th class="num">{STATUS_ICON[CHECK]}</th>'
        f'<th class="num">{STATUS_ICON[TODO]}</th></tr></thead><tbody>'
    )
    for lang, kind, nblocks, counts in language_rows(result):
        t = Totals(counts[AUTO], counts[CHECK], counts[TODO] + counts["impossible"])
        parts.append(
            f"<tr><td><strong>{_e(lang)}</strong></td><td>{_e(UNIT_KINDS[kind])}</td>"
            f'<td class="num">{nblocks}</td><td class="num">{t.total}</td>'
            f'<td class="barcell">{_bar(t, f"{lang} {kind}")}</td><td class="num">{t.auto}</td>'
            f'<td class="num">{t.check}</td><td class="num">{t.todo}</td></tr>'
        )
    parts.append("</tbody></table></div>")
    parts.append(_legend())
    parts.append("</section>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------------


def _md(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _support_section(result: ConversionResult) -> list[str]:
    """Режимы семантики и рукописные объекты S7Compat, от которых зависит «автоматический» перевод."""
    opts = result.options
    out = [
        "## Слой совместимости S7Compat",
        "",
        f"Режимы: таймеры TON/TOF/TP — `{opts.timers}`, F_TRIG — `{opts.f_trig}` (`standard` — библиотека",
        "Standard CODESYS, `s7compat` — рукописные ФБ с семантикой S7; [MAPPING.md](MAPPING.md),",
        "«Слой совместимости S7Compat»).",
        "",
    ]
    if not result.support:
        out += ["Для этого кода объекты S7Compat не нужны.", ""]
        return out
    out += [
        "Сконвертированный код вызывает рукописные объекты (не генерируются, лежат в `src/*/S7Compat`): "
        + ", ".join(f"`{name}`" for name in sorted(result.support))
        + ". Конструкции, переведённые через них, считаются «автоматически»: их поведение задают описания в",
        "объявлениях этих объектов и тесты `tests/POUs/S7Compat`, результат прогона в CODESYS —",
        "[TEST_REPORT.md](TEST_REPORT.md).",
        "",
    ]
    return out


def render_markdown(
    result: ConversionResult,
    inputs: Sequence[str],
    command: str = "s7conv report",
    tasks_target: str = "`tasks.json` рядом с раскладкой",
    title: str = "Отчёт конвертации SCL → ST CODESYS",
) -> str:
    """Отчёт Markdown; command — команда пересоздания, tasks_target — куда записаны задачи."""
    items = all_items(result)
    tot = totals(items)
    files = [f for f in result.files if f.items]
    blocks = sum(1 for i in items if i.category == "block")
    out: list[str] = [
        f"# {title}",
        "",
        f"Сгенерирован `s7conv {__version__}` — не редактировать вручную, пересоздаётся командой",
        f"`{command}` (см. README). Вход: " + ", ".join(f"`{_md(p)}`" for p in inputs) + ".",
        "",
        "Единица учёта — **конструкция**: блок S7, объявление переменной или оператор (вложенные",
        "операторы считаются отдельно). Статусы: **автоматически** — переведено без замечаний;",
        "**требует проверки** — переведено, в коде пометка `// MIGRATION-CHECK: причина`;",
        "**не поддерживается** — не переведено, в коде `// MIGRATION-TODO: причина` и закомментированный",
        "исходный текст. Правила соответствия — [MAPPING.md](MAPPING.md), подмножество SCL —",
        "[GRAMMAR.md](GRAMMAR.md).",
        "",
        "## Итог",
        "",
        "| Показатель | Значение |",
        "|---|---:|",
        f"| {'Файлов' if has_languages(result) else 'Файлов SCL'} | "
        f"{sum(1 for f in result.files if not f.path.startswith('('))} |",
        f"| Блоков S7 | {blocks} |",
        f"| Конструкций | {tot.total} |",
        f"| Автоматически | {tot.auto} ({_pct(tot.pct(tot.auto))}) |",
        f"| Требуют проверки | {tot.check} ({_pct(tot.pct(tot.check))}) |",
        f"| Не поддерживаются | {tot.todo} ({_pct(tot.pct(tot.todo))}) |",
        "",
        "### По видам конструкций",
        "",
        "| Вид | Всего | Автоматически | Требуют проверки | Не поддерживаются |",
        "|---|---:|---:|---:|---:|",
    ]
    for cat, label in CATEGORY_LABEL.items():
        t = totals(i for i in items if i.category == cat)
        out.append(f"| {label} | {t.total} | {t.auto} | {t.check} | {t.todo} |")
    out += [
        "",
        "## По файлам",
        "",
        "| Файл | Блоков | Конструкций | Автоматически | Требуют проверки | Не поддерживаются | Авто, % |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for f in files:
        t = totals(f.items)
        nblocks = sum(1 for i in f.items if i.category == "block")
        out.append(
            f"| `{_md(f.path)}` | {nblocks} | {t.total} | {t.auto} | {t.check} | {t.todo} | {_pct(t.pct(t.auto))} |"
        )
    out.append(
        f"| **Итого** | {blocks} | {tot.total} | {tot.auto} | {tot.check} | {tot.todo} | {_pct(tot.pct(tot.auto))} |"
    )
    out += language_section(result)
    out += ["", "## Задачи CODESYS (из OB)", ""]
    if result.tasks:
        out += [
            "| Задача | Тип | Период, мс | Приоритет | POU (порядок вызова) | OB S7 |",
            "|---|---|---:|---:|---|---|",
        ]
        for task in result.tasks:
            interval = str(task.interval_ms) if task.interval_ms is not None else "—"
            sources = _md("; ".join(task.sources))
            out.append(
                f"| {task.name} | {task.type} | {interval} | {task.priority} | {', '.join(task.pous)} | {sources} |"
            )
        out.append("")
    else:
        out += ["OB в исходниках нет.", ""]
    manual = [o for o in result.obs if o.kind == "event"]
    if manual:
        out.append("OB без задачи (настроить вручную): " + ", ".join(f"`{o.program}`" for o in manual) + ".")
        out.append("")
    out.append(f"Задачи записываются в {tasks_target} (формат — MAPPING.md, «OB и задачи»).")
    out.append("")
    out += _support_section(result)
    for severity, title in ((TODO, "Не поддерживается — причины"), (CHECK, "Требует проверки — причины")):
        rows = rule_summary(result, severity)
        out += [f"## {title}", ""]
        if not rows:
            out += ["Нет.", ""]
            continue
        out += ["| Правило | Что | Пометок |", "|---|---|---:|"]
        out += [f"| `{rule}` | {_md(name)} | {count} |" for rule, name, count in rows]
        out.append("")
    if result.errors:
        out += ["## Ошибки входных данных", ""]
        out += [f"- {_md(e)}" for e in result.errors]
        out.append("")
    out += ["## Подробно по файлам", ""]
    for f in files:
        t = totals(f.items)
        out += [f"### `{_md(f.path)}`", ""]
        out.append(
            f"Конструкций {t.total}: автоматически {t.auto}, требуют проверки {t.check}, не поддерживаются {t.todo}."
        )
        out.append("")
        if f.blocks:
            out.append("Блоки: " + "; ".join(f"{kind} «{name}» → `{st}`" for kind, name, st in f.blocks) + ".")
            out.append("")
        notes = _sorted_notes(f.notes)
        if not notes:
            out += ["Пометок нет.", ""]
            continue
        where = "Место" if f.lowering is not None else "Строка"
        out += [f"| {where} | Статус | Блок | Правило | Причина |", "|---:|---|---|---|---|"]
        for n in notes:
            line = f.where(n.line)
            out.append(
                f"| {line} | {STATUS_ICON[n.severity]} {STATUS_LABEL[n.severity]} | {_md(n.block) or '—'} | "
                f"`{n.rule}` | {_md(n.message)} |"
            )
        out.append("")
    return "\n".join(out).rstrip() + "\n"


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------

_CSS = """
:root {
  color-scheme: light;
  --page: #f9f9f7;
  --surface: #fcfcfb;
  --surface-2: #f3f2ee;
  --ink: #0b0b0b;
  --ink-2: #52514e;
  --muted: #898781;
  --grid: #e1e0d9;
  --axis: #c3c2b7;
  --border: rgba(11, 11, 11, 0.10);
  --good: #0ca30c;
  --warning: #fab219;
  --critical: #d03b3b;
  --good-ink: #006300;
  --accent: #2a78d6;
  --shadow: 0 1px 2px rgba(11, 11, 11, 0.04), 0 4px 16px rgba(11, 11, 11, 0.04);
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --page: #0d0d0d;
    --surface: #1a1a19;
    --surface-2: #222220;
    --ink: #ffffff;
    --ink-2: #c3c2b7;
    --muted: #898781;
    --grid: #2c2c2a;
    --axis: #383835;
    --border: rgba(255, 255, 255, 0.10);
    --good-ink: #0ca30c;
    --accent: #3987e5;
    --shadow: none;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --page: #0d0d0d;
  --surface: #1a1a19;
  --surface-2: #222220;
  --ink: #ffffff;
  --ink-2: #c3c2b7;
  --muted: #898781;
  --grid: #2c2c2a;
  --axis: #383835;
  --border: rgba(255, 255, 255, 0.10);
  --good-ink: #0ca30c;
  --accent: #3987e5;
  --shadow: none;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0;
  background: var(--page);
  color: var(--ink);
  font: 14px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}
.wrap { max-width: 1120px; margin: 0 auto; padding: 32px 16px 48px; }
header.top { display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between; gap: 12px 24px;
  margin-bottom: 24px; }
.eyebrow { font-size: 12px; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin: 0 0 6px; }
h1 { font-size: 26px; line-height: 1.2; margin: 0; font-weight: 650; letter-spacing: -0.01em; }
h2 { font-size: 17px; margin: 0 0 4px; font-weight: 600; }
.sub { color: var(--ink-2); margin: 6px 0 0; }
.meta { color: var(--muted); font-size: 12px; text-align: right; }
.meta code { color: var(--ink-2); }
code { font-family: ui-monospace, "Cascadia Mono", Consolas, monospace; font-size: 12.5px; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; box-shadow: var(--shadow);
  padding: 20px; margin-bottom: 16px; }
.card .hint { color: var(--muted); font-size: 12.5px; margin: 0 0 16px; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 16px; }
.tile { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; box-shadow: var(--shadow);
  padding: 14px 16px; display: flex; flex-direction: column; }
.tile .label { color: var(--ink-2); font-size: 12.5px; display: flex; align-items: flex-start; gap: 6px; }
.tile .label .dot { margin-top: 4px; }
/* значение и подпись прижаты к низу плитки: в ряду они на одной линии, даже если подпись плитки в две строки */
.tile .value { font-size: 28px; font-weight: 600; line-height: 1.15; margin-top: auto; padding-top: 4px; }
.tile .note { color: var(--muted); font-size: 12px; }
.tile.hero .value { font-size: 40px; }
.dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; flex: none; }
.s-auto { background: var(--good); }
.s-check { background: var(--warning); }
.s-todo { background: var(--critical); }
.badge { display: inline-flex; align-items: center; gap: 6px; white-space: nowrap; font-size: 12.5px;
  color: var(--ink-2); }
.badge .ico { width: 18px; height: 18px; border-radius: 50%; display: inline-grid; place-items: center;
  font-size: 11px; font-weight: 700; color: #fff; }
.badge.check .ico { color: #0b0b0b; }
.legend { display: flex; flex-wrap: wrap; gap: 8px 20px; margin: 12px 0 0; padding: 0; list-style: none;
  color: var(--ink-2); font-size: 12.5px; }
.legend li { display: inline-flex; align-items: center; gap: 6px; }
.bar { display: flex; gap: 2px; height: 14px; width: 100%; }
.bar.big { height: 22px; }
.seg { height: 100%; min-width: 2px; cursor: default; outline: none; }
.seg:first-child { border-radius: 4px 0 0 4px; }
.seg:last-child { border-radius: 0 4px 4px 0; }
.seg:only-child { border-radius: 4px; }
.seg:hover, .seg:focus-visible { filter: brightness(1.08);
  box-shadow: 0 0 0 2px var(--surface), 0 0 0 3px var(--ink-2); }
.scale { display: flex; justify-content: space-between; color: var(--muted); font-size: 11px; margin-top: 6px;
  font-variant-numeric: tabular-nums; }
table { border-collapse: collapse; width: 100%; }
th, td { padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--grid); vertical-align: top; }
th { color: var(--muted); font-weight: 500; font-size: 12px; white-space: nowrap; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
tr:last-child td { border-bottom: 0; }
tfoot td { font-weight: 600; border-top: 1px solid var(--axis); }
td.barcell { width: 32%; min-width: 140px; }
.file { font-family: ui-monospace, "Cascadia Mono", Consolas, monospace; font-size: 12.5px; word-break: break-all; }
.scroll { overflow-x: auto; }
.grid2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; }
.reasons { list-style: none; margin: 0; padding: 0; }
.reasons li { display: grid; grid-template-columns: minmax(0, 1fr) 40px; gap: 4px 12px; align-items: center;
  padding: 6px 0; border-bottom: 1px solid var(--grid); }
.reasons li:last-child { border-bottom: 0; }
.reasons .name { font-size: 13px; overflow-wrap: anywhere; }
.reasons .name code { color: var(--muted); font-size: 11.5px; margin-left: 6px; }
.reasons .count { text-align: right; font-variant-numeric: tabular-nums; color: var(--ink-2); }
.reasons .track { grid-column: 1 / -1; height: 6px; }
.reasons .fill { height: 100%; border-radius: 0 4px 4px 0; min-width: 3px; }
details { border-top: 1px solid var(--grid); }
details:first-of-type { border-top: 0; }
summary { cursor: pointer; padding: 12px 0; display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 12px;
  align-items: center; list-style: none; }
summary::-webkit-details-marker { display: none; }
summary .chev { color: var(--muted); transition: transform .15s; display: inline-block; margin-right: 6px; }
details[open] summary .chev { transform: rotate(90deg); }
summary .counts { display: flex; gap: 14px; color: var(--ink-2); font-size: 12.5px;
  font-variant-numeric: tabular-nums; }
summary .counts > span { display: inline-flex; align-items: center; gap: 5px; min-width: 3.4em; }
.blocks { color: var(--ink-2); font-size: 12.5px; margin: 0 0 10px; }
.blocks code { background: var(--surface-2); padding: 1px 5px; border-radius: 4px; }
.msg { overflow-wrap: anywhere; }
.empty { color: var(--muted); font-style: italic; }
footer { color: var(--muted); font-size: 12px; margin-top: 24px; text-align: center; }
#tip { position: fixed; pointer-events: none; z-index: 10; background: var(--surface); color: var(--ink);
  border: 1px solid var(--border); border-radius: 8px; box-shadow: 0 6px 24px rgba(0,0,0,.12); padding: 8px 10px;
  font-size: 12.5px; display: none; max-width: 280px; }
#tip strong { font-variant-numeric: tabular-nums; }
@media (max-width: 640px) {
  .meta { text-align: left; }
  td.barcell { min-width: 100px; }
  .tile.hero .value { font-size: 32px; }
  table.notes th:nth-child(3), table.notes td:nth-child(3) { display: none; }
  table.notes .badge { white-space: normal; }
}
@media print { .card, .tile { box-shadow: none; } details { break-inside: avoid; } }
"""

_JS = """
(function () {
  var tip = document.getElementById('tip');
  function show(el, x, y) {
    tip.textContent = '';
    var strong = document.createElement('strong');
    strong.textContent = el.getAttribute('data-value');
    tip.appendChild(strong);
    tip.appendChild(document.createTextNode(' ' + el.getAttribute('data-label')));
    tip.style.display = 'block';
    var w = tip.offsetWidth, h = tip.offsetHeight;
    var left = Math.min(window.innerWidth - w - 8, Math.max(8, x + 12));
    var top = y - h - 12 < 8 ? y + 16 : y - h - 12;
    tip.style.left = left + 'px';
    tip.style.top = top + 'px';
  }
  document.querySelectorAll('.seg').forEach(function (el) {
    el.addEventListener('pointermove', function (e) { show(el, e.clientX, e.clientY); });
    el.addEventListener('pointerleave', function () { tip.style.display = 'none'; });
    el.addEventListener('focus', function () {
      var r = el.getBoundingClientRect();
      show(el, r.left + r.width / 2, r.top);
    });
    el.addEventListener('blur', function () { tip.style.display = 'none'; });
  });
})();
"""


def _e(text: object) -> str:
    return html.escape(str(text), quote=True)


def _bar(t: Totals, context: str, big: bool = False) -> str:
    segs: list[str] = []
    for status in (AUTO, CHECK, TODO):
        value = t.of(status)
        if value == 0:
            continue
        pct = t.pct(value)
        label = f"{STATUS_LABEL[status]} — {pct:.0f} % ({context})"
        segs.append(
            f'<span class="seg s-{status}" style="flex: {value} 1 0" tabindex="0" role="img" '
            f'aria-label="{_e(STATUS_LABEL[status])}: {value}" data-value="{value}" data-label="{_e(label)}"></span>'
        )
    cls = "bar big" if big else "bar"
    return f'<div class="{cls}">{"".join(segs)}</div>'


def _badge(status: str) -> str:
    return (
        f'<span class="badge {status}"><span class="ico s-{status}" aria-hidden="true">{STATUS_ICON[status]}</span>'
        f"{_e(STATUS_LABEL[status])}</span>"
    )


def _legend() -> str:
    return (
        '<ul class="legend">'
        + "".join(
            f'<li><span class="dot s-{s}" aria-hidden="true"></span>{STATUS_ICON[s]} {_e(STATUS_LABEL[s])}</li>'
            for s in (AUTO, CHECK, TODO)
        )
        + "</ul>"
    )


def _common_dir(paths: Sequence[str]) -> str:
    """Общий каталог путей файлов ('samples/scl/') — его не повторяем в каждой строке HTML."""
    dirs = [p.rsplit("/", 1)[0] + "/" for p in paths if "/" in p and not p.startswith("(")]
    if not dirs or len(dirs) != len([p for p in paths if not p.startswith("(")]):
        return ""
    prefix = dirs[0]
    return prefix if all(d == prefix for d in dirs) else ""


def render_html(result: ConversionResult, inputs: Sequence[str]) -> str:
    items = all_items(result)
    tot = totals(items)
    files = [f for f in result.files if f.items]
    n_files = sum(1 for f in result.files if not f.path.startswith("("))
    n_blocks = sum(1 for i in items if i.category == "block")
    common = _common_dir([f.path for f in files])

    def short(path: str) -> str:
        return path[len(common) :] if common and path.startswith(common) else path

    parts: list[str] = []
    a = parts.append
    a("<!doctype html>")
    a('<html lang="ru">')
    a("<head>")
    a('<meta charset="utf-8">')
    a('<meta name="viewport" content="width=device-width, initial-scale=1">')
    lang_title = "S7" if has_languages(result) else "SCL"
    a(f"<title>Отчёт конвертации {lang_title}</title>")
    a(f"<style>{_CSS}</style>")
    a("</head>")
    a("<body>")
    a('<div class="wrap">')
    a('<header class="top"><div>')
    a('<p class="eyebrow">Миграция Siemens S7 → CODESYS V3.5</p>')
    a(f"<h1>Отчёт конвертации {lang_title} → ST</h1>")
    a(
        '<p class="sub">Сколько конструкций переведено автоматически, сколько требует проверки '
        "и что не поддерживается — по каждому файлу.</p>"
    )
    a("</div>")
    a(
        f'<div class="meta">s7conv {_e(__version__)}<br>вход: '
        + ", ".join(f"<code>{_e(p)}</code>" for p in inputs)
        + "</div>"
    )
    a("</header>")

    # плитки
    a('<section class="tiles" aria-label="Итог">')
    a(
        '<div class="tile hero"><div class="label"><span class="dot s-auto" aria-hidden="true"></span>'
        f'{STATUS_ICON[AUTO]} Переведено автоматически</div><div class="value">{tot.pct(tot.auto):.0f}&nbsp;%</div>'
        f'<div class="note">{tot.auto} из {tot.total} конструкций</div></div>'
    )
    a(
        '<div class="tile"><div class="label"><span class="dot s-check" aria-hidden="true"></span>'
        f'{STATUS_ICON[CHECK]} Требуют проверки</div><div class="value">{tot.check}</div>'
        f'<div class="note">{tot.pct(tot.check):.0f} % конструкций</div></div>'
    )
    a(
        '<div class="tile"><div class="label"><span class="dot s-todo" aria-hidden="true"></span>'
        f'{STATUS_ICON[TODO]} Не поддерживаются</div><div class="value">{tot.todo}</div>'
        f'<div class="note">{tot.pct(tot.todo):.0f} % конструкций</div></div>'
    )
    a(
        f'<div class="tile"><div class="label">Файлы и блоки S7</div><div class="value">{n_files}'
        f' / {n_blocks}</div><div class="note">файлов SCL / блоков</div></div>'
    )
    a(
        f'<div class="tile"><div class="label">Задачи CODESYS</div><div class="value">{len(result.tasks)}</div>'
        f'<div class="note">из {len(result.obs)} OB</div></div>'
    )
    a("</section>")

    a(language_html(result))
    # общая полоса и разрез по видам
    a('<section class="card">')
    a("<h2>Все конструкции</h2>")
    a(
        '<p class="hint">Конструкция — блок S7, объявление переменной или оператор. '
        "Наведите на сегмент, чтобы увидеть число.</p>"
    )
    a(_bar(tot, "все конструкции", big=True))
    a('<div class="scale"><span>0 %</span><span>50 %</span><span>100 %</span></div>')
    a(_legend())
    a('<div class="scroll" style="margin-top:16px"><table>')
    a(
        '<thead><tr><th>Вид</th><th class="num">Всего</th><th class="barcell">Доля</th>'
        f'<th class="num">{STATUS_ICON[AUTO]} авто</th><th class="num">{STATUS_ICON[CHECK]} проверка</th>'
        f'<th class="num">{STATUS_ICON[TODO]} нет</th></tr></thead><tbody>'
    )
    for cat, label in CATEGORY_LABEL.items():
        t = totals(i for i in items if i.category == cat)
        a(
            f'<tr><td>{_e(label)}</td><td class="num">{t.total}</td><td class="barcell">{_bar(t, label.lower())}</td>'
            f'<td class="num">{t.auto}</td><td class="num">{t.check}</td><td class="num">{t.todo}</td></tr>'
        )
    a("</tbody></table></div>")
    a("</section>")

    # по файлам
    a('<section class="card">')
    a("<h2>По файлам</h2>")
    where = f" Каталог: <code>{_e(common)}</code>." if common else ""
    a(f'<p class="hint">Доля конструкций каждого файла по статусу; строки — в порядке входа.{where}</p>')
    a('<div class="scroll"><table>')
    a(
        '<thead><tr><th>Файл</th><th class="num">Блоков</th><th class="num">Конструкций</th>'
        '<th class="barcell">Статус</th>'
        f'<th class="num">{STATUS_ICON[AUTO]}</th><th class="num">{STATUS_ICON[CHECK]}</th>'
        f'<th class="num">{STATUS_ICON[TODO]}</th><th class="num">Авто</th></tr></thead><tbody>'
    )
    for f in files:
        t = totals(f.items)
        nb = sum(1 for i in f.items if i.category == "block")
        a(
            f'<tr><td class="file" title="{_e(f.path)}">{_e(short(f.path))}</td><td class="num">{nb}</td>'
            f'<td class="num">{t.total}</td>'
            f'<td class="barcell">{_bar(t, f.path)}</td><td class="num">{t.auto}</td><td class="num">{t.check}</td>'
            f'<td class="num">{t.todo}</td><td class="num">{t.pct(t.auto):.0f} %</td></tr>'
        )
    a(
        f'</tbody><tfoot><tr><td>Итого</td><td class="num">{n_blocks}</td><td class="num">{tot.total}</td>'
        f'<td class="barcell">{_bar(tot, "итого")}</td><td class="num">{tot.auto}</td>'
        f'<td class="num">{tot.check}</td><td class="num">{tot.todo}</td>'
        f'<td class="num">{tot.pct(tot.auto):.0f} %</td></tr></tfoot>'
    )
    a("</table></div>")
    a(_legend())
    a("</section>")

    # причины
    a('<section class="grid2">')
    for severity, title, hint in (
        (TODO, "Не поддерживается: причины", "Что придётся переписать вручную (пометки MIGRATION-TODO)."),
        (CHECK, "Требует проверки: причины", "Что переведено, но требует инженерного решения (MIGRATION-CHECK)."),
    ):
        rows = rule_summary(result, severity)
        a('<div class="card">')
        a(f"<h2>{_e(title)}</h2>")
        a(f'<p class="hint">{_e(hint)}</p>')
        if not rows:
            a('<p class="empty">Нет пометок.</p>')
        else:
            top = rows[0][2]
            a('<ul class="reasons">')
            for rule, name, count in rows[:12]:
                width = 100.0 * count / top if top else 0
                a(
                    f'<li><span class="name">{_e(name)}<code>{_e(rule)}</code></span>'
                    f'<span class="count">{count}</span>'
                    f'<span class="track"><span class="fill s-{severity}" style="display:block;width:{width:.1f}%">'
                    "</span></span></li>"
                )
            a("</ul>")
            if len(rows) > 12:
                rest = sum(c for _r, _n, c in rows[12:])
                a(f'<p class="hint" style="margin:10px 0 0">и ещё {len(rows) - 12} правил ({rest} пометок)</p>')
        a("</div>")
    a("</section>")

    # задачи
    a('<section class="card">')
    a("<h2>Задачи CODESYS из организационных блоков</h2>")
    a(
        '<p class="hint">OB1 → MainTask, циклические OB → циклические задачи, OB100 → флаг первого цикла '
        "в MainTask; записываются в <code>tasks.json</code>.</p>"
    )
    if result.tasks:
        a('<div class="scroll"><table><thead><tr><th>Задача</th><th>Тип</th><th class="num">Период, мс</th>')
        a('<th class="num">Приоритет</th><th>POU (порядок вызова)</th><th>OB S7</th></tr></thead><tbody>')
        for task in result.tasks:
            interval = str(task.interval_ms) if task.interval_ms is not None else "—"
            a(
                f"<tr><td><strong>{_e(task.name)}</strong></td><td>{_e(task.type)}</td>"
                f"<td class='num'>{interval}</td><td class='num'>{task.priority}</td>"
                f"<td><code>{_e(', '.join(task.pous))}</code></td><td>{_e('; '.join(task.sources))}</td></tr>"
            )
        a("</tbody></table></div>")
    else:
        a('<p class="empty">OB в исходниках нет.</p>')
    manual = [o for o in result.obs if o.kind == "event"]
    if manual:
        a(
            '<p class="hint" style="margin:12px 0 0">Без задачи (событийные OB, настроить вручную): '
            + ", ".join(f"<code>{_e(o.program)}</code>" for o in manual)
            + "</p>"
        )
    a("</section>")

    # слой совместимости S7Compat: режимы и рукописные объекты, от которых зависит «автоматический» перевод
    a('<section class="card">')
    a("<h2>Слой совместимости S7Compat</h2>")
    a(
        f'<p class="hint">Таймеры TON/TOF/TP — <code>{_e(result.options.timers)}</code>, F_TRIG — '
        f"<code>{_e(result.options.f_trig)}</code> (<code>standard</code> — библиотека Standard CODESYS, "
        "<code>s7compat</code> — рукописные ФБ с семантикой S7).</p>"
    )
    if result.support:
        a(
            "<p>Рукописные объекты <code>src/*/S7Compat</code> (не генерируются): "
            + ", ".join(f"<code>{_e(name)}</code>" for name in sorted(result.support))
            + ". Переведённое через них считается «автоматически»; поведение задают их описания и тесты "
            "<code>tests/POUs/S7Compat</code>.</p>"
        )
    else:
        a('<p class="empty">Объекты S7Compat не нужны.</p>')
    a("</section>")

    # подробности
    a('<section class="card">')
    a("<h2>Подробно по файлам</h2>")
    a('<p class="hint">Пометки с номерами строк исходного файла SCL.</p>')
    for f in files:
        t = totals(f.items)
        notes = _sorted_notes(f.notes)
        a("<details>")
        a(
            f'<summary><span class="file" title="{_e(f.path)}"><span class="chev" aria-hidden="true">›</span>'
            f"{_e(short(f.path))}</span>"
            f'<span class="counts"><span><span class="dot s-auto" aria-hidden="true"></span>{t.auto}</span>'
            f'<span><span class="dot s-check" aria-hidden="true"></span>{t.check}</span>'
            f'<span><span class="dot s-todo" aria-hidden="true"></span>{t.todo}</span></span></summary>'
        )
        if f.blocks:
            a(
                '<p class="blocks">'
                + "; ".join(f"{_e(kind)} «{_e(name)}» → <code>{_e(st)}</code>" for kind, name, st in f.blocks)
                + "</p>"
            )
        if notes:
            a('<div class="scroll"><table class="notes"><thead><tr><th class="num">Строка</th><th>Статус</th>')
            a("<th>Блок</th><th>Причина</th></tr></thead><tbody>")
            for n in notes:
                line = str(n.line) if n.line else "—"
                a(
                    f'<tr><td class="num">{line}</td><td>{_badge(n.severity)}</td><td>{_e(n.block or "—")}</td>'
                    f'<td class="msg">{_e(n.message)} <code style="color:var(--muted)">{_e(n.rule)}</code></td></tr>'
                )
            a("</tbody></table></div>")
        else:
            a('<p class="empty">Пометок нет — всё переведено автоматически.</p>')
        a("</details>")
    a("</section>")
    a(
        f"<footer>s7conv {_e(__version__)} · правила соответствия — docs/MAPPING.md · "
        "подмножество SCL — docs/GRAMMAR.md</footer>"
    )
    a("</div>")
    a('<div id="tip" role="tooltip"></div>')
    a(f"<script>{_JS}</script>")
    a("</body>")
    a("</html>")
    return "\n".join(parts) + "\n"
