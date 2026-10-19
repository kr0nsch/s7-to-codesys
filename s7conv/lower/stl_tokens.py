"""Матрица токенов STL: все 172 значения `StlToken` XSD V21 → класс перевода, правило, мнемоники EN/DE.

Источник перечня — `SW.PlcBlocks.STL_v5.xsd` (dotnetprojects/DotNetSiemensPLCToolBoxLibrary @ bbe5bec,
SHA-256 в samples/lang/EXTERNAL.json); немецкие мнемоники — аннотации XSD и справочник STL S7-300/400
(AWL_e.pdf). Класс:

- auto — переводится без пометки (lower/stl_lift.py);
- check — переводится с пометкой MIGRATION-CHECK (правило в rule);
- todo — не переводится в этом выпуске: MIGRATION-TODO и исходная инструкция в комментарии;
- impossible — аналога в CODESYS нет.

docs/MAPPING_STL.md генерируется из этой таблицы (python -m s7conv build-corpus); тест
s7conv/tests/test_stl_tokens.py сверяет таблицу с XSD и требует теста на каждую строку класса auto/check.
"""

from __future__ import annotations

from dataclasses import dataclass

AUTO, CHECK, TODO, IMPOSSIBLE = "auto", "check", "todo", "impossible"


@dataclass(frozen=True)
class TokenRule:
    cls: str
    rule: str
    title: str
    en: str  # мнемоника EN (STEP 7 / TIA)
    de: str  # мнемоника DE


def _t(cls: str, rule: str, title: str, en: str, de: str | None = None) -> TokenRule:
    return TokenRule(cls, rule, title, en, de if de is not None else en)


_LOGIC = "stl.logic"
_ACCU = "stl.accu"
_MATH = "stl.math"
_CMP = "stl.compare"
_JUMP = "stl.jump_structured"
_CONV = "stl.convert"
_WORD = "stl.word_logic"
_SHIFT = "stl.shift"
_MODE_B = "stl.mode_b"
_ADDR = "stl.addr_register"
_DB = "stl.db_register"
_S5 = "s5.timer"
_S5C = "s5.counter"
_MCR = "stl.mcr"

TOKENS: dict[str, TokenRule] = {
    # логика битов
    "A": _t(AUTO, _LOGIC, "AND с операндом", "A", "U"),
    "AN": _t(AUTO, _LOGIC, "AND NOT", "AN", "UN"),
    "O": _t(AUTO, _LOGIC, "OR с операндом; без операнда — AND перед OR", "O"),
    "ON": _t(AUTO, _LOGIC, "OR NOT", "ON"),
    "X": _t(AUTO, _LOGIC, "XOR", "X"),
    "XN": _t(AUTO, _LOGIC, "XOR NOT", "XN"),
    "S": _t(AUTO, _LOGIC, "установить бит (с таймером/счётчиком — S5)", "S"),
    "R": _t(AUTO, _LOGIC, "сбросить бит (с таймером/счётчиком — S5)", "R"),
    "Assign": _t(AUTO, _LOGIC, "присвоить RLO", "=", "="),
    "Rise": _t(AUTO, "stl.edge", "FP: фронт RLO, явный бит памяти", "FP"),
    "Fall": _t(AUTO, "stl.edge", "FN: спад RLO, явный бит памяти", "FN"),
    "A_BRACK": _t(AUTO, _LOGIC, "A( — скобка", "A(", "U("),
    "AN_BRACK": _t(AUTO, _LOGIC, "AN( — скобка", "AN(", "UN("),
    "O_BRACK": _t(AUTO, _LOGIC, "O( — скобка", "O("),
    "ON_BRACK": _t(AUTO, _LOGIC, "ON( — скобка", "ON("),
    "X_BRACK": _t(AUTO, _LOGIC, "X( — скобка", "X("),
    "XN_BRACK": _t(AUTO, _LOGIC, "XN( — скобка", "XN("),
    "BRACKET": _t(AUTO, _LOGIC, ") — закрыть скобку", ")"),
    "NEG": _t(AUTO, _LOGIC, "NOT — инверсия RLO", "NOT"),
    "SET": _t(AUTO, _LOGIC, "RLO := 1", "SET"),
    "CLR": _t(AUTO, _LOGIC, "RLO := 0", "CLR"),
    "SAVE": _t(TODO, _MODE_B, "BR := RLO (ENO через BR) — режим B", "SAVE"),
    # загрузка и запись
    "L": _t(AUTO, _ACCU, "загрузить в ACCU1 (L WORD/INT в DINT — с обнулением, stl.zero_extend)", "L"),
    "T": _t(AUTO, _ACCU, "записать ACCU1 (разные типы — stl.bitcopy)", "T"),
    "LAR1": _t(TODO, _ADDR, "загрузить AR1", "LAR1"),
    "LAR2": _t(TODO, _ADDR, "загрузить AR2", "LAR2"),
    "TAR1": _t(TODO, _ADDR, "записать AR1", "TAR1"),
    "TAR2": _t(TODO, _ADDR, "записать AR2", "TAR2"),
    "LAR1_ACCU1": _t(TODO, _ADDR, "LAR1 из ACCU1", "LAR1"),
    "LAR1_AR2": _t(TODO, _ADDR, "LAR1 AR2", "LAR1 AR2"),
    "LAR2_ACCU1": _t(TODO, _ADDR, "LAR2 из ACCU1", "LAR2"),
    "TAR1_ACCU1": _t(TODO, _ADDR, "TAR1 в ACCU1", "TAR1"),
    "TAR2_ACCU1": _t(TODO, _ADDR, "TAR2 в ACCU1", "TAR2"),
    "TAR1_AR2": _t(TODO, _ADDR, "TAR1 AR2", "TAR1 AR2"),
    "CAR": _t(TODO, _ADDR, "обмен AR1 и AR2", "CAR", "TAR"),
    "ADDAR1": _t(TODO, _ADDR, "+AR1", "+AR1"),
    "ADDAR2": _t(TODO, _ADDR, "+AR2", "+AR2"),
    "CDB": _t(TODO, _DB, "обмен регистров DB и DI", "CDB", "TDB"),
    "L_DBLG": _t(TODO, _DB, "длина открытого DB", "L DBLG"),
    "L_DILG": _t(TODO, _DB, "длина открытого DI", "L DILG"),
    "L_DBNO": _t(TODO, _DB, "номер открытого DB", "L DBNO"),
    "L_DINO": _t(TODO, _DB, "номер открытого DI", "L DINO"),
    "OPEN_DB": _t(TODO, "stl.db_offset", "OPN DB — открыть DB (адресация по смещению)", "OPN", "AUF"),
    "OPEN_DI": _t(TODO, "stl.db_offset", "OPN DI", "OPN DI", "AUF DI"),
    # таймеры и счётчики S5
    "Pulse": _t(TODO, _S5, "SP — импульс", "SP", "SI"),
    "Extend": _t(TODO, _S5, "SE — продлённый импульс", "SE", "SV"),
    "OnDelay": _t(TODO, _S5, "SD — задержка включения", "SD", "SE"),
    "Retentive": _t(TODO, _S5, "SS — задержка включения с памятью", "SS"),
    "OffDelay": _t(TODO, _S5, "SF — задержка выключения", "SF", "SA"),
    "Free": _t(TODO, _S5, "FR — разрешение таймера/счётчика", "FR"),
    "LC": _t(TODO, _S5, "LC — загрузить таймер/счётчик в BCD", "LC"),
    "CU": _t(TODO, _S5C, "CU — счёт вверх", "CU", "ZV"),
    "CD": _t(TODO, _S5C, "CD — счёт вниз", "CD", "ZR"),
    # вызовы
    "CALL": _t(AUTO, "stl.call", "CALL блока или инструкции (TON/TOF/TP ...)", "CALL"),
    "CC": _t(AUTO, "stl.call", "CC — условный вызов FC без параметров", "CC"),
    "UC": _t(AUTO, "stl.call", "UC — безусловный вызов FC без параметров", "UC"),
    # сравнения
    **{
        f"{op}_{ty}": _t(AUTO, _CMP, f"сравнение {sym}{ty}", f"{sym}{ty}")
        for op, sym in (("EQ", "=="), ("NE", "<>"), ("GT", ">"), ("GE", ">="), ("LT", "<"), ("LE", "<="))
        for ty in ("I", "D", "R")
    },
    # переходы
    "JU": _t(AUTO, _JUMP, "безусловный переход", "JU", "SPA"),
    "JC": _t(AUTO, _JUMP, "переход при RLO = 1", "JC", "SPB"),
    "JCN": _t(AUTO, _JUMP, "переход при RLO = 0", "JCN", "SPBN"),
    "JCB": _t(TODO, _MODE_B, "переход при RLO = 1 с сохранением в BR", "JCB", "SPBB"),
    "JNB": _t(TODO, _MODE_B, "переход при RLO = 0 с сохранением в BR", "JNB", "SPBNB"),
    "JBI": _t(TODO, _MODE_B, "переход при BR = 1", "JBI", "SPBI"),
    "JNBI": _t(TODO, _MODE_B, "переход при BR = 0", "JNBI", "SPBIN"),
    "JO": _t(TODO, _MODE_B, "переход при OV = 1", "JO", "SPO"),
    "JOS": _t(TODO, _MODE_B, "переход при OS = 1", "JOS", "SPS"),
    "JZ": _t(TODO, _MODE_B, "переход при результате = 0", "JZ", "SPZ"),
    "JN": _t(TODO, _MODE_B, "переход при результате <> 0", "JN", "SPN"),
    "JP": _t(TODO, _MODE_B, "переход при результате > 0", "JP", "SPP"),
    "JM": _t(TODO, _MODE_B, "переход при результате < 0", "JM", "SPM"),
    "JMZ": _t(TODO, _MODE_B, "переход при результате <= 0", "JMZ", "SPMZ"),
    "JPZ": _t(TODO, _MODE_B, "переход при результате >= 0", "JPZ", "SPPZ"),
    "JUN": _t(TODO, _MODE_B, "переход при неупорядоченном результате (REAL)", "JUN", "SPU"),
    "LOOP": _t(TODO, "stl.loop", "LOOP — цикл по ACCU1-L", "LOOP"),
    "JL": _t(TODO, "stl.jump_list", "JL — список переходов", "JL", "SPL"),
    # арифметика
    "ADD": _t(AUTO, _MATH, "+ константа к ACCU1", "+"),
    **{
        f"{op}_{ty}": _t(AUTO, _MATH, f"{sym}{ty}", f"{sym}{ty}")
        for op, sym in (("ADD", "+"), ("SUB", "-"), ("MUL", "*"), ("DIV", "/"))
        for ty in ("I", "D", "R")
    },
    "MOD_D": _t(AUTO, _MATH, "остаток DINT", "MOD"),
    "INC": _t(TODO, _MATH, "INC — ACCU1-L-L + n", "INC"),
    "DEC": _t(TODO, _MATH, "DEC — ACCU1-L-L - n", "DEC"),
    "INV_I": _t(TODO, _CONV, "INVI — дополнение до единицы INT", "INVI", "KEW"),
    "INV_D": _t(TODO, _CONV, "INVD — дополнение до единицы DINT", "INVD", "KED"),
    "NEG_I": _t(TODO, _CONV, "NEGI — смена знака INT", "NEGI", "KZW"),
    "NEG_D": _t(TODO, _CONV, "NEGD — смена знака DINT", "NEGD", "KZD"),
    "NEG_R": _t(TODO, _CONV, "NEGR — смена знака REAL", "NEGR"),
    "ABS_R": _t(TODO, _MATH, "ABS REAL", "ABS"),
    **{
        f: _t(TODO, _MATH, f"{f} REAL", f)
        for f in ("SQRT", "SQR", "LN", "EXP", "SIN", "ASIN", "COS", "ACOS", "TAN", "ATAN")
    },
    # преобразования
    "BTI": _t(TODO, _CONV, "BCD → INT", "BTI"),
    "ITB": _t(TODO, _CONV, "INT → BCD", "ITB"),
    "BTD": _t(TODO, _CONV, "BCD → DINT", "BTD"),
    "DTB": _t(TODO, _CONV, "DINT → BCD", "DTB"),
    "ITD": _t(TODO, _CONV, "INT → DINT", "ITD"),
    "DTR": _t(TODO, _CONV, "DINT → REAL", "DTR"),
    "RND": _t(TODO, "stl.round", "округление к ближайшему (половина к чётному)", "RND"),
    "RND_M": _t(TODO, "stl.round", "округление вниз", "RND-"),
    "RND_P": _t(TODO, "stl.round", "округление вверх", "RND+"),
    "TRUNC": _t(TODO, _CONV, "отбрасывание дробной части", "TRUNC"),
    "CAW": _t(TODO, _CONV, "обмен байтов ACCU1-L", "CAW", "TAW"),
    "CAD": _t(TODO, _CONV, "обмен байтов ACCU1", "CAD", "TAD"),
    # логика слов и сдвиги
    **{t: _t(TODO, _WORD, f"{t} — логика слов", t, d) for t, d in (("AW", "UW"), ("OW", "OW"), ("XW", "XOW"))},
    **{t: _t(TODO, _WORD, f"{t} — логика двойных слов", t, d) for t, d in (("AD", "UD"), ("OD", "OD"), ("XD", "XOD"))},
    "SLW": _t(TODO, _SHIFT, "сдвиг слова влево", "SLW"),
    "SRW": _t(TODO, _SHIFT, "сдвиг слова вправо", "SRW"),
    "SLD": _t(TODO, _SHIFT, "сдвиг двойного слова влево", "SLD"),
    "SRD": _t(TODO, _SHIFT, "сдвиг двойного слова вправо", "SRD"),
    "SRSW": _t(TODO, _SHIFT, "сдвиг INT со знаком", "SSI", "SSI"),
    "SRSD": _t(TODO, _SHIFT, "сдвиг DINT со знаком", "SSD", "SSD"),
    "RLD": _t(TODO, _SHIFT, "циклический сдвиг влево", "RLD"),
    "RRD": _t(TODO, _SHIFT, "циклический сдвиг вправо", "RRD"),
    "RLDA": _t(TODO, _MODE_B, "сдвиг через CC1 влево", "RLDA"),
    "RRDA": _t(TODO, _MODE_B, "сдвиг через CC1 вправо", "RRDA"),
    # аккумуляторы
    "CAC": _t(TODO, _MODE_B, "TAK — обмен ACCU1 и ACCU2", "TAK"),
    "PUSH": _t(TODO, _MODE_B, "PUSH", "PUSH"),
    "POP": _t(TODO, _MODE_B, "POP", "POP"),
    "ENT": _t(TODO, _MODE_B, "ENT (только 4 ACCU, S7-400)", "ENT"),
    "LEAVE": _t(TODO, _MODE_B, "LEAVE (только 4 ACCU, S7-400)", "LEAVE"),
    # конец блока, MCR, служебное
    "BE": _t(AUTO, "stl.block_end", "конец блока", "BE"),
    "BEU": _t(AUTO, "stl.block_end", "безусловный конец блока", "BEU", "BEA"),
    "BEC": _t(AUTO, "stl.block_end", "условный конец блока", "BEC", "BEB"),
    "MCR_BRACK": _t(TODO, _MCR, "MCR( — открыть зону MCR", "MCR(", "MCR("),
    "BRACK_MCR": _t(TODO, _MCR, ")MCR — закрыть зону MCR", ")MCR", ")MCR"),
    "MCRA": _t(TODO, _MCR, "включить MCR", "MCRA"),
    "MCRD": _t(TODO, _MCR, "выключить MCR", "MCRD"),
    "NOP_0": _t(AUTO, "stl.nop", "NOP 0", "NOP 0"),
    "NOP_1": _t(AUTO, "stl.nop", "NOP 1", "NOP 1"),
    "BLD": _t(AUTO, "stl.nop", "BLD — команда отображения, без действия", "BLD"),
    "COMMENT": _t(AUTO, "stl.nop", "строка-комментарий", "//"),
    "EMPTY_LINE": _t(AUTO, "stl.nop", "пустая строка", ""),
    "PSEUDO": _t(TODO, "stl.unknown", "псевдоинструкция TIA (смысл не документирован)", "PSEUDO"),
    "MOVE": _t(TODO, "stl.unknown", "MOVE в сети STL TIA (не документирован в справочнике STL)", "MOVE"),
    "MOVE_BLOCK": _t(TODO, "stl.unknown", "MOVE_BLOCK в сети STL TIA", "MOVE_BLOCK"),
}


def rule_of(token: str) -> TokenRule:
    return TOKENS.get(token) or TokenRule(TODO, "stl.unknown", f"токен {token} не из XSD V21", token, token)


__all__ = ["AUTO", "CHECK", "IMPOSSIBLE", "TODO", "TOKENS", "TokenRule", "rule_of"]
