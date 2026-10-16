#!/usr/bin/env python3
"""Матрица покрытия корпуса SCL: какие конструкции есть в каких файлах samples/scl/*.scl.

    python samples/coverage_matrix.py           # напечатать таблицу Markdown
    python samples/coverage_matrix.py --write   # обновить таблицу в samples/scl/README.md
    python samples/coverage_matrix.py --check   # код 1, если таблица в README устарела

Поиск — регулярными выражениями по тексту файла (для большинства строк — по коду без
комментариев и строковых литералов). Это грубый, но воспроизводимый способ: матрица
описывает корпус, а не результат разбора конвертером.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections.abc import Callable, Sequence

HERE = os.path.dirname(os.path.abspath(__file__))
SCL_DIR = os.path.join(HERE, "scl")
README = os.path.join(SCL_DIR, "README.md")
BEGIN_MARK = "<!-- coverage:begin -->"
END_MARK = "<!-- coverage:end -->"

FILES: tuple[tuple[str, str], ...] = (
    ("UDT", "UDT_PlantTypes.scl"),
    ("DB", "DB_Plant.scl"),
    ("AI", "FB_AnalogIn.scl"),
    ("MOT", "FB_Motor.scl"),
    ("ALM", "FB_AlarmDelay.scl"),
    ("TOT", "FB_Totalizer.scl"),
    ("ALT", "FB_PumpAlternation.scl"),
    ("SEQ", "FB_Sequencer.scl"),
    ("DEB", "FB_Debounce.scl"),
    ("VLV", "FB_Valve.scl"),
    ("PI", "FB_PIController.scl"),
    ("RMP", "FB_Ramp.scl"),
    ("CNT", "FB_BatchCounter.scl"),
    ("MOD", "FB_ModeSelect.scl"),
    ("STA", "FC_Statistics.scl"),
    ("LOG", "FB_EventLogger.scl"),
    ("LEG", "FB_LegacyTelegram.scl"),
    ("OB1", "OB_Main.scl"),
    ("OB30", "OB_Cyclic.scl"),
    ("OB100", "OB_Startup.scl"),
)

Matcher = str | Callable[[str], bool]
BLOCK_KW = r"^(FUNCTION_BLOCK|FUNCTION|DATA_BLOCK|TYPE|ORGANIZATION_BLOCK)\b"


def _code_only(text: str) -> str:
    """Текст без комментариев // и без содержимого строк '...'."""
    lines = []
    for line in text.split("\n"):
        line = re.sub(r"'[^']*'", "''", line)
        pos = line.find("//")
        lines.append(line if pos < 0 else line[:pos])
    return "\n".join(lines)


def _has_tag(text: str) -> bool:
    return re.search(r'"(?!DB_|FB_|FC_|UDT_)[A-Za-z]\w*"(?!\s*[:(])', _code_only(text)) is not None


# (группа, конструкция, образец, искать по полному тексту)
CONSTRUCTS: tuple[tuple[str, str, Matcher, bool], ...] = (
    ("Блоки", "FUNCTION_BLOCK", r'^FUNCTION_BLOCK "', False),
    ("Блоки", "FUNCTION с типом результата, `#Имя := ...`", r'^FUNCTION "[^"]+"\s*:', False),
    ("Блоки", "ORGANIZATION_BLOCK", r"^ORGANIZATION_BLOCK", False),
    ("Блоки", "TYPE (UDT) / STRUCT ... END_STRUCT;", r'^TYPE "', False),
    ("Блоки", "DATA_BLOCK глобальный (VAR внутри)", r'^DATA_BLOCK "[^"]+"\s*\n(?:(?!BEGIN).*\n)*?\s*VAR\s', True),
    (
        "Блоки",
        "DATA_BLOCK экземплярный, раскладка TIA (тип отдельной строкой)",
        r'^(NON_RETAIN|VERSION : [0-9.]+)\s*\n"FB_',
        True,
    ),
    ("Блоки", 'DATA_BLOCK "DB" "FB" (компактная форма)', r'^DATA_BLOCK "[^"]+" "', True),
    ("Блоки", "DATA_BLOCK по типу UDT", r'^NON_RETAIN\s*\n"UDT_', True),
    ("Блоки", "Несколько блоков в одном файле", lambda t: len(re.findall(BLOCK_KW, t, re.M)) > 1, False),
    ("Шапка и атрибуты", "TITLE / AUTHOR / FAMILY / VERSION", r"^(TITLE =|AUTHOR :|FAMILY :|VERSION :)", False),
    ("Шапка и атрибуты", "NAME", r"^NAME :", False),
    ("Шапка и атрибуты", "{ S7_Optimized_Access := 'TRUE' }", r"S7_Optimized_Access := 'TRUE'", True),
    ("Шапка и атрибуты", "{ S7_Optimized_Access := 'FALSE' }", r"S7_Optimized_Access := 'FALSE'", True),
    (
        "Шапка и атрибуты",
        "Атрибуты переменных {InstructionName ...}, {ExternalAccessible ...}",
        r"\{\s*(InstructionName|ExternalAccessible)",
        False,
    ),
    ("Секции", "VAR_INPUT", r"^\s*VAR_INPUT\b", False),
    ("Секции", "VAR_OUTPUT", r"^\s*VAR_OUTPUT\b", False),
    ("Секции", "VAR_IN_OUT", r"^\s*VAR_IN_OUT\b", False),
    ("Секции", "VAR (статические / переменные DB)", r"^\s*VAR\s*$", False),
    ("Секции", "VAR_TEMP", r"^\s*VAR_TEMP\b", False),
    ("Секции", "VAR CONSTANT", r"^\s*VAR CONSTANT\b", False),
    ("Секции", "VAR RETAIN", r"^\s*VAR RETAIN\b", False),
    ("Секции", "NON_RETAIN", r"^NON_RETAIN\b", False),
    ("Секции", "Начальные значения в BEGIN блока данных", r"^BEGIN\s*\n\s+\w[\w\[\].]*\s*:=", True),
    ("Типы", "Bool, Int, DInt, Real", r":\s*(Bool|Int|DInt|Real)\b", False),
    ("Типы", "LReal", r":\s*LReal\b", False),
    ("Типы", "Byte / Word / DWord", r":\s*(Byte|Word|DWord)\b", False),
    ("Типы", "UInt / UDInt", r":\s*(UInt|UDInt)\b", False),
    ("Типы", "Time", r":\s*Time\b", False),
    ("Типы", "S5Time", r":\s*S5Time\b", False),
    ("Типы", "String[n]", r":\s*String\[\d+\]", False),
    ("Типы", "Date_And_Time", r":\s*Date_And_Time\b", False),
    ("Типы", "DTL", r":\s*DTL\b", False),
    ("Типы", "Array[a..b] of ...", r"Array\[-?\d+\.\.\d+\] of", False),
    ("Типы", "Struct (анонимная)", r":\s*Struct\b|of Struct\b", False),
    ("Типы", 'Тип UDT "UDT_..." в объявлении', r':\s*(Array\[[^\]]+\] of )?"UDT_', False),
    ("Типы", "Any", r":\s*Any\b", False),
    ("Типы", "Variant", r":\s*Variant\b", False),
    ("Типы", "HW_ANY", r":\s*HW_ANY\b", False),
    ("Литералы", "T#...", r"\bT#", False),
    ("Литералы", "S5T#...", r"\bS5T#", False),
    ("Литералы", "DT#...", r"\bDT#", False),
    ("Литералы", "16#... (Byte/Word)", r"\b16#[0-9A-F]+", False),
    ("Литералы", "P#... (указатель ANY)", r"\bP#", False),
    ("Литералы", "Инициализатор массива [..], повторение n(..)", r":= \[", False),
    ("Обращения", "#локальная, #ЛОКАЛЬНАЯ_КОНСТАНТА", r"#[A-Za-z_]", False),
    ("Обращения", '"DB".переменная', r'"DB_\w+"\.\w', False),
    ("Обращения", '"Тег" из таблицы тегов', _has_tag, False),
    ("Обращения", "%I / %Q (бит)", r"%[IQ]\d+\.\d", False),
    ("Обращения", "%IW / %QW", r"%[IQ]W\d+", False),
    ("Обращения", "%M / %MW / %MD", r"%M[WD]?\d+", False),
    ("Обращения", "Доступ к периферии :P", r"%IW\d+:P", False),
    ("Обращения", "Абсолютный %DB30.DBW0", r"%DB\d+\.DB", False),
    ("Обращения", "Срезы .%Xn / .%Bn / .%Wn", r"\.%[XBW]\d", False),
    ("Обращения", "AT-наложение", r"\bAT\b", False),
    ("Операторы", "REGION / END_REGION", r"^\s*REGION\b", False),
    ("Операторы", "IF ... THEN ... ELSE", r"\bIF\b", False),
    ("Операторы", "ELSIF", r"\bELSIF\b", False),
    ("Операторы", "CASE с метками-литералами и ELSE", r"\bCASE\b", False),
    ("Операторы", "CASE: список меток (1, 2:) и диапазон (3..99:)", r"^\s*\d+\s*,\s*\d+:|^\s*\d+\.\.\d+:", False),
    ("Операторы", "FOR ... TO ... DO", r"\bFOR\b", False),
    ("Операторы", "FOR ... BY", r"\bFOR\b.*\bBY\b", False),
    ("Операторы", "WHILE", r"\bWHILE\b", False),
    ("Операторы", "REPEAT ... UNTIL", r"\bREPEAT\b", False),
    ("Операторы", "EXIT / CONTINUE / RETURN", r"\b(EXIT|CONTINUE|RETURN)\s*;", False),
    ("Операторы", "GOTO и метки", r"\bGOTO\b", False),
    ("Операторы", "ENO := FALSE", r"\bENO\s*:=", False),
    ("Операторы", "XOR / MOD / SHL", r"\b(XOR|MOD|SHL)\b", False),
    ("Вызовы", "TON_TIME", r"TON_TIME", False),
    ("Вызовы", "TOF_TIME", r"TOF_TIME", False),
    ("Вызовы", "TP_TIME", r"TP_TIME", False),
    ("Вызовы", "CTU_INT", r"CTU_INT", False),
    ("Вызовы", "R_TRIG", r": R_TRIG", False),
    ("Вызовы", "F_TRIG", r": F_TRIG", False),
    ("Вызовы", "Повторный вызов таймера в одном цикле", lambda t: len(re.findall(r"#tonStep\(", t)) > 1, False),
    ("Вызовы", "Мультиэкземпляр пользовательского ФБ", r':\s*"FB_\w+";', False),
    ("Вызовы", 'Вызов экземплярного DB "DB_X"(...)', r'^\s*"DB_\w+"\(', False),
    ("Вызовы", "Присваивание выхода => в вызове", r"=>", False),
    ("Вызовы", "Вызов FC с результатом", r':= "FC_\w+"\(', False),
    ("Вызовы", "NORM_X / SCALE_X", r"\b(NORM_X|SCALE_X)\(", False),
    ("Вызовы", "LIMIT / MIN / MAX / ABS (именованные MN/IN/MX, IN1/IN2)", r"\b(LIMIT|MIN|MAX|ABS)\(", False),
    ("Вызовы", "Преобразования *_TO_*", r"\b[A-Z]+_TO_[A-Z]+\(", False),
    ("Вызовы", "S5TI_TIM", r"S5TI_TIM\(", False),
    ("Вызовы", "CONCAT / LEFT", r"\b(CONCAT|LEFT)\(", False),
    ("Вызовы", "BLKMOV", r"\bBLKMOV\(", False),
    ("Вызовы", "WORD_TO_BLOCK_DB(...).DW[...]", r"WORD_TO_BLOCK_DB\(", False),
    ("Вызовы", "S_ODT (таймер S5 с номером)", r"\bS_ODT\(", False),
    ("Вызовы", "PEEK / POKE", r"\b(PEEK|POKE)\(", False),
    ("Вызовы", "RD_SYS_T / WR_SYS_T / RUNTIME", r"\b(RD_SYS_T|WR_SYS_T|RUNTIME)\(", False),
    ("Вызовы", "TypeOf / VariantGet", r"\b(TypeOf|VariantGet)\(", False),
    (
        "OB",
        "Входы стартовой информации OB (Initial_Call, LostRetentive, ...)",
        r"(Initial_Call|LostRetentive|IO_State)\s*:",
        False,
    ),
)


def _hit(matcher: Matcher, text: str, raw: bool) -> bool:
    if callable(matcher):
        return matcher(text)
    return re.search(matcher, text if raw else _code_only(text), re.M) is not None


def render(texts: dict[str, str]) -> str:
    codes = [code for code, _ in FILES]
    lines = [
        "| Конструкция | " + " | ".join(codes) + " |",
        "|---|" + "|".join(":-:" for _ in codes) + "|",
    ]
    group = None
    for grp, name, matcher, raw in CONSTRUCTS:
        if grp != group:
            lines.append(f"| **{grp}** |" + "|" * len(codes))
            group = grp
        cells = ["x" if _hit(matcher, texts[code], raw) else "" for code in codes]
        if not any(cells):
            raise SystemExit(f"конструкция не найдена ни в одном файле: {name}")
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def load() -> dict[str, str]:
    texts = {}
    for code, name in FILES:
        with open(os.path.join(SCL_DIR, name), encoding="utf-8") as fh:
            texts[code] = fh.read()
    return texts


def splice(readme: str, table: str) -> str:
    head, sep, rest = readme.partition(BEGIN_MARK)
    _, sep2, tail = rest.partition(END_MARK)
    if not sep or not sep2:
        raise SystemExit(f"в {README} нет меток {BEGIN_MARK} / {END_MARK}")
    return head + BEGIN_MARK + "\n" + table + END_MARK + tail


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Матрица покрытия корпуса SCL")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="обновить таблицу в samples/scl/README.md")
    mode.add_argument("--check", action="store_true", help="проверить, что таблица в README актуальна")
    args = parser.parse_args(argv)
    table = render(load())
    if not (args.write or args.check):
        sys.stdout.buffer.write(table.encode("utf-8"))
        return 0
    with open(README, encoding="utf-8", newline="") as fh:
        current = fh.read()
    updated = splice(current, table)
    if args.check:
        if updated != current:
            print(
                "матрица покрытия в samples/scl/README.md устарела: python samples/coverage_matrix.py --write",
                file=sys.stderr,
            )
            return 1
        return 0
    if updated != current:
        with open(README, "w", encoding="utf-8", newline="") as fh:
            fh.write(updated)
    return 0


if __name__ == "__main__":
    sys.exit(main())
