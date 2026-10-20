"""STL (StlIR) → SCL: символьный подъём (режим A) и структурные переходы.

Режим A (по умолчанию, как STL-фронтенд CBMC): /FC, OR-группы и стек скобок — значения времени трансляции,
RLO — выражение, ACCU1/ACCU2 — типизированные выражения. Цепочка до `=`/`S`/`R` становится одним
присваиванием; переменная, которую цепочка читает, перед записью в неё «замораживается» во временную.

Переходы (`--stl-jumps`):
- structured — прямой JC/JCN через участок → IF (JCN … JU … метка → IF/ELSE), обратный JC/JCN → REPEAT;
- pc — автомат `WHILE xStlRun DO CASE iStlPc OF … END_CASE END_WHILE` по базовым блокам; включается и
  сам, если поток несводим (правило stl.jump_pc).

Профиль S7-300 (2 ACCU): арифметика пишет ACCU1, ACCU2 не меняется (AWL_e.pdf, §7.3); `L` обнуляет ACCU1
перед загрузкой (§9.2) — `L` INT/WORD с записью в DINT/DWORD дополняется нулями (stl.zero_extend).
Слово состояния (OV, BR, CC), TAK/PUSH/POP, адресные регистры, S5-таймеры и MCR — режим B, P1: пока todo.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from s7conv.frontends.simaticml import XUnit
from s7conv.ir.stl import StlBlock, StlInstr, add_statement_list
from s7conv.lower.common import (
    AUTO,
    CHECK,
    FALSE,
    TODO,
    TRUE,
    BlockLower,
    Ex,
    LLine,
    and_,
    arith,
    atom,
    cmp_,
    indent,
    is_simple,
    not_,
    or_,
    worst,
    xor_,
)
from s7conv.lower.stl_tokens import rule_of
from s7conv.nodes import LowerNote

UNKNOWN: Ex = ("<RLO не определён>", 0)
_LOGIC_OPS = {"A": "A", "AN": "AN", "O": "O", "ON": "ON", "X": "X", "XN": "XN"}
_BRACKETS = {"A_BRACK": "A", "AN_BRACK": "AN", "O_BRACK": "O", "ON_BRACK": "ON", "X_BRACK": "X", "XN_BRACK": "XN"}
_CMP = {"EQ": "=", "NE": "<>", "GT": ">", "GE": ">=", "LT": "<", "LE": "<="}
_MATH_OPS = {"ADD": "+", "SUB": "-", "MUL": "*", "DIV": "/"}
_MATH_TYPES = {"I": "INT", "D": "DINT", "R": "REAL"}
_JUMPS = {"JU", "JC", "JCN"}
_RLO_READERS = {"Assign", "S", "R", "NEG", "Rise", "Fall", "SAVE", "JC", "JCN", "JCB", "JNB", "CC", "BEC", "MCR_BRACK"}
_NEUTRAL = {"COMMENT", "EMPTY_LINE", "NOP_0", "NOP_1", "BLD", "L", "T"}
_WIDTH = {"BYTE": 8, "SINT": 8, "USINT": 8, "CHAR": 8, "INT": 16, "WORD": 16, "UINT": 16, "DATE": 16, "S5TIME": 16}
_WIDTH.update({"DINT": 32, "DWORD": 32, "UDINT": 32, "REAL": 32, "TIME": 32, "TIME_OF_DAY": 32})
_PREFIX = {"INT": "i", "DINT": "di", "REAL": "r", "WORD": "w", "DWORD": "dw", "BYTE": "b", "TIME": "t", "BOOL": "x"}
_SIGNED_INT = {"INT", "DINT", "SINT"}


@dataclass
class Val:
    """Значение аккумулятора: выражение SCL и тип S7 (ANY — целый литерал без типа)."""

    ex: Ex
    type: str


@dataclass
class Frame:
    op: str
    terms: list[Ex]
    cur: Ex | None
    fc: bool


@dataclass
class State:
    fc: bool = False
    terms: list[Ex] = field(default_factory=list)
    cur: Ex | None = None
    rlo_after: Ex | None = UNKNOWN
    stack: list[Frame] = field(default_factory=list)
    accu1: Val | None = None
    accu2: Val | None = None


class StlLifter:
    def __init__(self, bl: BlockLower, block: StlBlock, mode: str = "structured") -> None:
        self.bl = bl
        self.blk = block
        self.instrs = block.instrs
        self.mode = mode
        self.s = State()
        self.out: list[LLine] = []
        self.k: dict[int, int] = {}
        self.status: dict[int, tuple[str, str]] = {}
        self.labels = block.labels()
        self.net_titles = {n.start: n for n in block.networks}
        self.pending: list[LowerNote] = []  # пометки для следующего оператора (например, +I с DINT)

    # -- служебное -------------------------------------------------------------------
    def mark(self, ins: StlInstr, status: str, rule: str) -> None:
        old = self.status.get(ins.index)
        if old is None or worst(old[0], status) != old[0]:
            self.status[ins.index] = (status, rule)

    def note(self, ins: StlInstr, severity: str, rule: str, message: str) -> LowerNote:
        self.mark(ins, severity, rule)
        return LowerNote(severity, rule, message)

    def emit(self, text: str, ins: StlInstr | None, notes: list[LowerNote] | None = None) -> None:
        trace = ins.trace if ins is not None else "сети STL"
        attached = list(notes or [])
        if self.pending and not text.lstrip().startswith("//") and text.strip() not in ("ELSE", "END_IF;"):
            attached = self.pending + attached
            self.pending = []
        self.out.append(LLine(text, trace, attached))

    def temp(self, ins: StlInstr, kind: str, type_name: str = "Bool", comment: str = "") -> str:
        n = ins.network
        self.k[n] = self.k.get(n, 0) + 1
        prefix = _PREFIX.get(type_name.upper(), "x")
        name = f"{prefix}{kind}{n}_{self.k[n]}"
        return self.bl.temp(name, _scl_type(type_name), comment or f"сеть {n}, строка {ins.line}")

    @staticmethod
    def source_text(ins: StlInstr) -> str:
        mnemonic = rule_of(ins.token).en
        operand = f" {ins.operand}" if ins.operand else ""
        return f"{mnemonic}{operand}".strip()

    def todo(self, ins: StlInstr, rule: str, message: str) -> None:
        """Инструкция без перевода: заглушка-оператор с MIGRATION-TODO, состояние машины — неизвестно."""
        note = self.note(ins, TODO, rule, f"{self.source_text(ins)}: {message}")
        self.emit(f'"STL_{ins.token}"(); // {self.source_text(ins)}', ins, [note])
        self.s.rlo_after = UNKNOWN
        self.s.fc = False
        self.s.accu1 = None
        self.s.accu2 = None

    # -- RLO -------------------------------------------------------------------------
    def value(self) -> Ex:
        s = self.s
        if not s.fc:
            return s.rlo_after if s.rlo_after is not None else UNKNOWN
        parts = [*s.terms, *([s.cur] if s.cur is not None else [])]
        return or_(*parts) if parts else TRUE

    def logic(self, op: str, x: Ex) -> None:
        s = self.s
        if op.endswith("N"):
            x = not_(x)
            op = op[:-1]
        if not s.fc:
            s.terms, s.cur, s.fc = [], x, True
            return
        if op == "A":
            s.cur = and_(s.cur, x) if s.cur is not None else x
        elif op == "O":
            if s.cur is not None:
                s.terms.append(s.cur)
            s.cur = x
        else:
            full = self.value()
            s.terms, s.cur = [], xor_(full, x)

    def rlo_read_next(self, i: int) -> bool:
        """Читает ли код после инструкции i значение RLO до начала новой цепочки."""
        for ins in self.instrs[i + 1 :]:
            if ins.label:
                return True
            if ins.token in _RLO_READERS:
                return True
            if ins.token in _NEUTRAL:
                continue
            return False
        return False

    def freeze(self, ins: StlInstr, ex: Ex, kind: str = "Rlo") -> Ex:
        if is_simple(ex):
            return ex
        tmp = self.temp(ins, kind, "Bool", f"сеть {ins.network}, строка {ins.line}: RLO")
        self.emit(f"{tmp} := {ex[0]};", ins)
        return atom(tmp)

    def need_rlo(self, ins: StlInstr) -> Ex | None:
        v = self.value()
        if v == UNKNOWN:
            self.todo(ins, "stl.rlo_unknown", "RLO в этом месте не определён символьно (после вызова или прыжка)")
            return None
        return v

    # -- запись: «заморозка» выражений, читающих записываемую переменную ------------------
    def invalidate(self, ins: StlInstr, var: str) -> None:
        pattern = re.compile(re.escape(var) + r"(?![\w])")
        s = self.s

        def fix(ex: Ex | None, kind: str = "Rlo") -> Ex | None:
            if ex is None or ex == UNKNOWN or not pattern.search(ex[0]) or ex[0] == var:
                return ex
            return self.freeze(ins, ex, kind) if not is_simple(ex) else ex

        s.cur = fix(s.cur)
        s.terms = [t for t in (fix(x) for x in s.terms) if t is not None]
        s.rlo_after = fix(s.rlo_after)
        for fr in s.stack:
            fr.cur = fix(fr.cur)
            fr.terms = [t for t in (fix(x) for x in fr.terms) if t is not None]
        live1, live2 = self.accu_live(ins.index)
        for name, live in (("accu1", live1), ("accu2", live2)):
            val: Val | None = getattr(s, name)
            if val is not None and not live:
                continue
            if val is not None and pattern.search(val.ex[0]):
                tmp = self.temp(
                    ins, "Accu", val.type if val.type != "ANY" else "INT", f"{name.upper()} до записи {var}"
                )
                self.emit(f"{tmp} := {val.ex[0]};", ins)
                setattr(s, name, Val(atom(tmp), val.type))

    def accu_live(self, i: int) -> tuple[bool, bool]:
        """Читается ли после инструкции i текущее значение ACCU1 / ACCU2 (до перезаписи).

        Метка — граница: состояние ACCU через неё не переносится (join, базовые блоки pc), значит
        значение там уже мертво. Неизвестная инструкция — осторожно «живо».
        """
        where = {"a1": "accu1", "a2": "accu2"}  # где сейчас исходные значения
        live = {"accu1": False, "accu2": False}
        for ins in self.instrs[i + 1 :]:
            if ins.label or ins.token in _JUMPS or ins.token in ("CALL", "UC", "CC", "BE", "BEU", "BEC"):
                break
            tok = ins.token
            if tok in ("COMMENT", "EMPTY_LINE", "NOP_0", "NOP_1", "BLD") or tok in _LOGIC_OPS or tok in _BRACKETS:
                continue
            if tok in ("BRACKET", "NEG", "SET", "CLR", "Rise", "Fall", "Assign", "S", "R", "SAVE"):
                continue
            if tok == "L":
                src2 = next((k for k, v in where.items() if v == "accu1"), None)
                for k in list(where):
                    if where[k] == "accu2":
                        del where[k]
                if src2 is not None:
                    where[src2] = "accu2"
                continue
            if tok == "T":
                for k, v in where.items():
                    if v == "accu1":
                        live["accu1" if k == "a1" else "accu2"] = True
                continue
            if re.fullmatch(r"(EQ|NE|GT|GE|LT|LE)_(I|D|R)", tok):
                for k in where:
                    live["accu1" if k == "a1" else "accu2"] = True
                continue
            if re.fullmatch(r"(ADD|SUB|MUL|DIV)_(I|D|R)|MOD_D", tok):
                for k in where:
                    live["accu1" if k == "a1" else "accu2"] = True
                where = {k: v for k, v in where.items() if v != "accu1"}
                continue
            return True, True
        return live["accu1"], live["accu2"]

    # -- типы ------------------------------------------------------------------------
    def type_of(self, operand: str) -> str:
        if operand.startswith("#"):
            found = self.bl.member_type(operand)
            if found and "." in operand:
                found = None
            return found.upper().split("[")[0] if found else ""
        up = operand.upper()
        if re.fullmatch(r"-?\d+", operand):
            return "ANY"
        if re.fullmatch(r"-?\d+\.\d*(E[-+]?\d+)?", up):
            return "REAL"
        if up.startswith(("L#", "DINT#")):
            return "DINT"
        if up.startswith(("T#", "TIME#")):
            return "TIME"
        if up.startswith("S5T#"):
            return "S5TIME"
        if up.startswith(("DW#", "DWORD#")):
            return "DWORD"
        if up.startswith(("W#", "WORD#", "16#", "2#", "8#")):
            return "WORD"
        if up.startswith(("B#", "BYTE#")):
            return "BYTE"
        if up.startswith("INT#"):
            return "INT"
        if up.startswith("REAL#"):
            return "REAL"
        return ""

    def convert(self, ins: StlInstr, val: Val, target: str) -> tuple[str, list[LowerNote]]:
        """Значение ACCU1 при записи T в переменную типа target (правила AWL_e.pdf §9.2)."""
        src = val.type
        text = val.ex[0]
        if not target or src in ("", target, "ANY"):
            return text, []
        sw, tw = _WIDTH.get(src), _WIDTH.get(target)
        if sw is None or tw is None:
            return text, [self.note(ins, CHECK, "stl.type", f"T {ins.operand}: тип ACCU1 {src}, тип операнда {target}")]
        if "REAL" in (src, target) and src != target:
            note = self.note(
                ins,
                TODO,
                "stl.bitcopy",
                f"T {ins.operand}: копия битов {src} → {target} через ACCU (U_S7Bits32 — P1)",
            )
            return text, [note]
        if sw == tw:
            return f"{src}_TO_{target}({text})", []
        if sw < tw:
            unsigned = {8: "BYTE", 16: "WORD"}[sw]
            inner = text if src == unsigned else f"{src}_TO_{unsigned}({text})"
            note = self.note(
                ins,
                CHECK,
                "stl.zero_extend",
                f"L {src} → T {target}: ACCU1 обнуляется перед загрузкой (AWL_e.pdf §9.2), значение "
                "дополняется нулями, знак не расширяется; для S7-1500 — сверить",
            )
            return f"{unsigned}_TO_{target}({inner})", [note]
        note = self.note(
            ins,
            CHECK,
            "stl.accu_high",
            f"T {ins.operand}: записывается младшая часть ACCU1 ({target}), старшие биты {src} отбрасываются",
        )
        return f"{src}_TO_{target}({text})", [note]

    # -- инструкции --------------------------------------------------------------------
    def lift(self, ins: StlInstr) -> None:
        token = ins.token
        rule = rule_of(token)
        self.mark(ins, rule.cls if rule.cls in (AUTO, CHECK) else TODO, rule.rule)
        s = self.s
        if token in ("COMMENT",):
            if ins.comment:
                self.emit(f"// {ins.comment}", ins)
            return
        if token in ("EMPTY_LINE", "NOP_0", "NOP_1", "BLD"):
            return
        if token in _LOGIC_OPS:
            if ins.operand is None:
                if token == "O":
                    if s.fc and s.cur is not None:
                        s.terms.append(s.cur)
                        s.cur = None
                    return
                self.todo(ins, "stl.operand", "логическая инструкция без операнда")
                return
            if ins.operand_scope == "Statusword" or ins.operand.upper() in ("OV", "OS", "BR", "UO", "==0", "<>0"):
                self.todo(ins, "stl.mode_b", "проверка слова состояния — режим B (P1)")
                return
            if ins.operand.upper().startswith(("%T", "%C")):
                self.todo(ins, "s5.timer", "опрос таймера/счётчика S5 — P1")
                return
            self.logic(token, atom(ins.operand))
            return
        if token in _BRACKETS:
            if len(s.stack) >= 7:
                self.todo(ins, "stl.bracket_depth", "глубина скобок больше 7 — ошибка программы S7")
                return
            s.stack.append(Frame(_BRACKETS[token], list(s.terms), s.cur, s.fc))
            s.fc, s.terms, s.cur = False, [], None
            return
        if token == "BRACKET":
            if not s.stack:
                self.todo(ins, "stl.bracket", "закрывающая скобка без открывающей")
                return
            inner = self.value()
            fr = s.stack.pop()
            s.terms, s.cur, s.fc = fr.terms, fr.cur, fr.fc
            self.logic(fr.op, inner)
            return
        if token == "NEG":
            v = self.value()
            if s.fc:
                s.terms, s.cur = [], not_(v)
            else:
                s.rlo_after = not_(v) if v != UNKNOWN else UNKNOWN
            return
        if token in ("SET", "CLR"):
            s.fc, s.terms, s.cur = False, [], None
            s.rlo_after = TRUE if token == "SET" else FALSE
            return
        if token in ("Rise", "Fall"):
            self.edge(ins)
            return
        if token == "Assign":
            self.assign(ins)
            return
        if token in ("S", "R"):
            self.set_reset(ins)
            return
        if token == "L":
            self.load(ins)
            return
        if token == "T":
            self.transfer(ins)
            return
        m = re.fullmatch(r"(EQ|NE|GT|GE|LT|LE)_(I|D|R)", token)
        if m:
            self.compare(ins, _CMP[m.group(1)], _MATH_TYPES[m.group(2)])
            return
        m = re.fullmatch(r"(ADD|SUB|MUL|DIV)_(I|D|R)", token)
        if m:
            self.math(ins, _MATH_OPS[m.group(1)], _MATH_TYPES[m.group(2)])
            return
        if token == "MOD_D":
            self.math(ins, "MOD", "DINT")
            return
        if token == "ADD" and ins.operand is not None:
            if s.accu1 is None:
                self.todo(ins, "stl.accu_unknown", "ACCU1 не определён")
                return
            s.accu1 = Val(arith("+", s.accu1.ex, atom(ins.operand)), s.accu1.type)
            return
        if token == "CALL" and ins.call is not None:
            self.call(ins)
            return
        if token in ("UC", "CC") and ins.operand:
            name = ins.operand if ins.operand.startswith('"') else f'"{ins.operand}"'
            if token == "UC":
                self.emit(f"{name}();", ins)
            else:
                rv = self.need_rlo(ins)
                if rv is None:
                    return
                self.emit(f"IF {rv[0]} THEN", ins)
                self.emit(f"   {name}();", ins)
                self.emit("END_IF;", ins)
            s.fc, s.rlo_after, s.accu1, s.accu2 = False, UNKNOWN, None, None
            return
        if token in ("BE", "BEU"):
            if token == "BE" and ins.index == len(self.instrs) - 1:
                return
            self.emit("RETURN;", ins)
            return
        if token == "BEC":
            bv = self.need_rlo(ins)
            if bv is None:
                return
            self.emit(f"IF {bv[0]} THEN", ins)
            self.emit("   RETURN;", ins)
            self.emit("END_IF;", ins)
            s.fc, s.rlo_after = False, TRUE
            return
        if token in _JUMPS:
            self.todo(ins, "stl.jump_pc", "переход вне структурного участка")
            return
        cls_rule = rule_of(token)
        self.todo(ins, cls_rule.rule, f"{cls_rule.title} — не переводится в этом выпуске")

    def edge(self, ins: StlInstr) -> None:
        if ins.operand is None:
            self.todo(ins, "stl.operand", "FP/FN без бита памяти")
            return
        v = self.need_rlo(ins)
        if v is None:
            return
        bit = ins.operand
        notes = []
        if self.bl.member_section(bit) == "Temp":
            notes.append(self.note(ins, CHECK, "stl.edge_memory", f"бит памяти фронта {bit} во временной области"))
        v = self.freeze(ins, v)
        self.invalidate(ins, bit)
        tmp = self.temp(
            ins, "Edge", "Bool", f"сеть {ins.network}, строка {ins.line}: {'FP' if ins.token == 'Rise' else 'FN'}"
        )
        edge = and_(v, not_(atom(bit))) if ins.token == "Rise" else and_(not_(v), atom(bit))
        self.emit(f"{tmp} := {edge[0]};", ins, notes)
        self.emit(f"{bit} := {v[0]};", ins)
        self.s.terms, self.s.cur, self.s.fc = [], atom(tmp), True

    def assign(self, ins: StlInstr) -> None:
        if ins.operand is None:
            self.todo(ins, "stl.operand", "= без операнда")
            return
        v = self.need_rlo(ins)
        if v is None:
            return
        target = ins.operand
        if self.rlo_read_next(ins.index) and not is_simple(v):
            v = self.freeze(ins, v)
        self.s.fc, self.s.terms, self.s.cur, self.s.rlo_after = False, [], None, None
        self.invalidate(ins, target)
        self.emit(f"{target} := {v[0]};", ins)
        self.s.rlo_after = v if is_simple(v) and v[0] != target else atom(target)

    def set_reset(self, ins: StlInstr) -> None:
        if ins.operand is None:
            self.todo(ins, "stl.operand", "S/R без операнда")
            return
        if ins.operand.upper().startswith(("%T", "%C")) or ins.operand_scope in ("Timer", "Counter"):
            self.todo(ins, "s5.timer", "S/R таймера или счётчика S5 — P1")
            return
        v = self.need_rlo(ins)
        if v is None:
            return
        target = ins.operand
        if self.rlo_read_next(ins.index):
            v = self.freeze(ins, v)
        self.s.fc, self.s.terms, self.s.cur, self.s.rlo_after = False, [], None, None
        self.invalidate(ins, target)
        const = "TRUE" if ins.token == "S" else "FALSE"
        if v == TRUE:
            self.emit(f"{target} := {const};", ins)
        else:
            self.emit(f"IF {v[0]} THEN", ins)
            self.emit(f"   {target} := {const};", ins)
            self.emit("END_IF;", ins)
        self.s.fc, self.s.terms, self.s.cur = False, [], None
        self.s.rlo_after = v

    def load(self, ins: StlInstr) -> None:
        if ins.operand is None:
            self.todo(ins, "stl.operand", "L без операнда")
            return
        if ins.extra.upper() == "STW" or ins.operand.upper() in ("STW",):
            self.todo(ins, "stl.mode_b", "L STW — режим B (P1)")
            return
        if ins.operand.upper().startswith(("%T", "%C")) or ins.operand_scope in ("Timer", "Counter"):
            self.todo(ins, "s5.timer", "L таймера/счётчика S5 — P1")
            return
        if ins.operand_scope == "Address" and ins.operand.upper().startswith(("DB", "DI")):
            self.todo(ins, "stl.db_offset", "частично квалифицированный доступ к DB по смещению — P1")
            return
        self.s.accu2 = self.s.accu1
        self.s.accu1 = Val(atom(ins.operand), self.type_of(ins.operand))

    def transfer(self, ins: StlInstr) -> None:
        if ins.operand is None or self.s.accu1 is None:
            self.todo(ins, "stl.accu_unknown", "ACCU1 не определён символьно")
            return
        if ins.extra.upper() == "STW" or ins.operand.upper() == "STW":
            self.todo(ins, "stl.mode_b", "T STW — режим B (P1)")
            return
        target = ins.operand
        text, notes = self.convert(ins, self.s.accu1, self.type_of(target))
        if any(n.severity == TODO for n in notes):
            todo = next(n for n in notes if n.severity == TODO)
            self.emit(f'"STL_T"(); // {self.source_text(ins)}', ins, [todo])
            return
        self.invalidate(ins, target)
        self.emit(f"{target} := {text};", ins, notes)

    def compare(self, ins: StlInstr, op: str, typ: str) -> None:
        a, b = self.s.accu2, self.s.accu1
        if a is None or b is None:
            self.todo(ins, "stl.accu_unknown", "ACCU1/ACCU2 не определены")
            return
        self.s.terms, self.s.cur, self.s.fc = [], cmp_(op, a.ex, b.ex), True
        del typ

    def math(self, ins: StlInstr, op: str, typ: str) -> None:
        a, b = self.s.accu2, self.s.accu1
        if a is None or b is None:
            self.todo(ins, "stl.accu_unknown", "ACCU1/ACCU2 не определены")
            return
        notes = []
        if typ == "INT" and ("DINT" in (a.type, b.type) or "DWORD" in (a.type, b.type)):
            notes.append(
                self.note(ins, CHECK, "stl.accu_high", f"{op}I с 32-битным операндом: меняется только ACCU1-L")
            )
        if op == "/" and typ in ("INT", "DINT"):
            self.mark(ins, AUTO, "stl.math")
        self.s.accu1 = Val(arith(op, a.ex, b.ex), typ)
        self.pending.extend(notes)

    def call(self, ins: StlInstr) -> None:
        call = ins.call
        assert call is not None
        args: list[str] = []
        ret = ""
        for name, section, _typ, operand in call.params:
            if operand is None:
                continue
            if section in ("Output",):
                args.append(f"{name} => {operand}")
                self.invalidate(ins, operand)
            elif section == "Return" or name.upper() == "RET_VAL":
                ret = operand
            else:
                args.append(f"{name} := {operand}")
        if call.kind == "Instruction" and not call.instance:
            # инструкция-функция (NORM_X, SCALE_X, LIMIT ...): результат — параметр Ret_Val
            callee = call.name
        elif call.kind in ("Instruction", "FB"):
            if not call.instance:
                self.todo(ins, "stl.call", f"CALL {call.name} без экземпляра")
                return
            callee = call.instance
            if call.instance_scope == "GlobalVariable" and call.kind == "Instruction":
                callee = f"{call.instance}.{call.name}"
        else:
            callee = call.name if call.name.startswith('"') else f'"{call.name}"'
        text = f"{callee}({', '.join(args)});"
        if ret:
            text = f"{ret} := {text}"
        notes: list[LowerNote] = []
        if self.bl.profile == "s7-1500":
            notes.append(
                self.note(
                    ins,
                    CHECK,
                    "stl.call_registers_1500",
                    "S7-1500: после CALL слово состояния и ACCU не определены (FAQ 67655405)",
                )
            )
        self.emit(text, ins, notes)
        self.s.fc, self.s.terms, self.s.cur = False, [], None
        self.s.rlo_after, self.s.accu1, self.s.accu2 = UNKNOWN, None, None

    # -- структура переходов ------------------------------------------------------------
    def target(self, ins: StlInstr) -> int | None:
        return self.labels.get(ins.operand or "")

    def closed(self, lo: int, hi: int) -> bool:
        """Участок [lo, hi) без переходов наружу и без входов внутрь (кроме своего начала)."""
        for ins in self.instrs:
            t = self.target(ins) if ins.token in _JUMPS or ins.token == "LOOP" else None
            if t is None:
                continue
            inside_src = lo <= ins.index < hi
            inside_dst = lo < t < hi
            if inside_src and not (lo <= t <= hi):
                return False
            if not inside_src and inside_dst:
                return False
        return True

    def reducible(self) -> bool:
        for ins in self.instrs:
            if ins.token in _JUMPS:
                t = self.target(ins)
                if t is None:
                    return False
            if ins.token in ("JL", "LOOP") or (ins.token in _JUMPS and (self.target(ins) or 0) < ins.index):
                return False
        return True

    def emit_range(self, lo: int, hi: int) -> None:
        i = lo
        while i < hi:
            ins = self.instrs[i]
            if ins.index in self.net_titles and self.net_titles[ins.index].start == ins.index:
                net = self.net_titles[ins.index]
                self.emit(f"// Сеть {net.number}" + (f": {net.title}" if net.title else ""), ins)
            if ins.token in ("JC", "JCN"):
                t = self.target(ins)
                assert t is not None
                rlo = self.need_rlo(ins)
                if rlo is None:
                    i += 1
                    continue
                self.mark(ins, AUTO, "stl.jump_structured")
                cond = rlo if ins.token == "JCN" else not_(rlo)
                else_end = self.else_branch(i, t, hi)
                saved = self.snapshot()
                self.emit(f"IF {cond[0]} THEN // {self.source_text(ins)}", ins)
                body_start = len(self.out)
                self.s.fc, self.s.terms, self.s.cur, self.s.rlo_after = False, [], None, TRUE
                then_end = t if else_end is None else self.prev_real(t)
                self.emit_range(i + 1, then_end)
                self.indent_from(body_start)
                if else_end is not None:
                    self.mark(self.instrs[then_end], AUTO, "stl.jump_structured")
                    self.emit("ELSE", self.instrs[then_end])
                    else_start = len(self.out)
                    self.restore(saved)
                    self.s.fc, self.s.terms, self.s.cur, self.s.rlo_after = False, [], None, TRUE
                    self.emit_range(t, else_end)
                    self.indent_from(else_start)
                self.emit("END_IF;", ins)
                self.join()
                i = else_end if else_end is not None else t
                continue
            if ins.token == "JU":
                t = self.target(ins)
                assert t is not None
                self.mark(ins, CHECK, "stl.jump_dead")
                note = self.note(
                    ins, CHECK, "stl.jump_dead", f"{self.source_text(ins)}: участок до метки не выполняется"
                )
                self.emit(f"// {self.source_text(ins)}: строки до метки недостижимы и не переводятся", ins)
                self.out[-1].notes.append(note)
                for skipped in self.instrs[i + 1 : t]:
                    self.mark(skipped, CHECK, "stl.jump_dead")
                i = t
                continue
            self.lift(ins)
            i += 1

    def else_branch(self, i: int, t: int, hi: int) -> int | None:
        """JCN t … JU u; t: … u: → IF/ELSE; возвращает u или None."""
        j = self.prev_real(t)
        if j <= i:
            return None
        ju = self.instrs[j]
        if ju.token != "JU":
            return None
        u = self.target(ju)
        if u is None or not (t < u <= hi):
            return None
        if not self.closed(t, u):
            return None
        return u

    def prev_real(self, t: int) -> int:
        j = t - 1
        while j >= 0 and self.instrs[j].token in ("COMMENT", "EMPTY_LINE"):
            j -= 1
        return j

    def snapshot(self) -> State:
        s = self.s
        return State(s.fc, list(s.terms), s.cur, s.rlo_after, list(s.stack), s.accu1, s.accu2)

    def restore(self, st: State) -> None:
        self.s = State(st.fc, list(st.terms), st.cur, st.rlo_after, list(st.stack), st.accu1, st.accu2)

    def join(self) -> None:
        """Точка слияния после IF: RLO = 1 после прыжка, на другом пути — что угодно → не определён."""
        self.s.fc, self.s.terms, self.s.cur = False, [], None
        self.s.rlo_after = UNKNOWN
        self.s.accu1 = None
        self.s.accu2 = None

    def indent_from(self, start: int) -> None:
        self.out[start:] = indent(self.out[start:])

    # -- автомат pc ---------------------------------------------------------------------
    def emit_pc(self, reason: str) -> None:
        """Несводимый поток: базовые блоки → CASE iStlPc в WHILE xStlRun; состояние между блоками — во временных."""
        first = self.instrs[0]
        leaders = sorted({0, *self.labels.values(), *(ins.index + 1 for ins in self.instrs if ins.token in _JUMPS)})
        leaders = [x for x in leaders if x < len(self.instrs)]
        pc = self.bl.temp("iStlPc", "Int", "номер базового блока (автомат переходов STL)")
        run = self.bl.temp("xStlRun", "Bool", "автомат переходов STL работает")
        rlo = self.bl.temp("xStlRlo", "Bool", "RLO между базовыми блоками")
        note = self.note(first, CHECK, "stl.jump_pc", f"переходы STL переведены автоматом CASE: {reason}")
        self.emit(f"{pc} := 0;", first, [note])
        self.emit(f"{run} := TRUE;", first)
        self.emit(f"WHILE {run} DO", first)
        self.emit(f"   CASE {pc} OF", first)
        index_of = {start: n for n, start in enumerate(leaders)}
        for n, start in enumerate(leaders):
            end = leaders[n + 1] if n + 1 < len(leaders) else len(self.instrs)
            self.emit(f"      {n}:", self.instrs[start])
            body_start = len(self.out)
            self.s = State(fc=False, rlo_after=atom(rlo))
            last = self.instrs[end - 1]
            for ins in self.instrs[start:end]:
                if ins.index in self.net_titles:
                    net = self.net_titles[ins.index]
                    self.emit(f"// Сеть {net.number}" + (f": {net.title}" if net.title else ""), ins)
                if ins.token in _JUMPS:
                    continue
                self.lift(ins)
            nxt = index_of.get(end)
            if last.token in _JUMPS:
                t = self.target(last)
                self.mark(last, CHECK, "stl.jump_pc")
                tgt = index_of.get(t) if t is not None else None
                if last.token == "JU":
                    self.emit(f"{pc} := {tgt};", last)
                else:
                    v = self.value()
                    cond = v if last.token == "JC" else not_(v)
                    self.emit(f"IF {cond[0]} THEN", last)
                    self.emit(f"   {pc} := {tgt};", last)
                    self.emit("ELSE", last)
                    self.emit(f"   {pc} := {nxt if nxt is not None else -1};", last)
                    self.emit("END_IF;", last)
                    self.emit(f"{rlo} := TRUE;", last)
            else:
                v = self.value()
                if v != UNKNOWN and v[0] != rlo.lstrip("#") and v[0] != rlo:
                    self.emit(f"{rlo} := {v[0]};", last)
                self.emit(f"{pc} := {nxt if nxt is not None else -1};", last)
            self.out[body_start:] = indent(self.out[body_start:], 3)
        self.emit("   ELSE", first)
        self.emit(f"      {run} := FALSE;", first)
        self.emit("   END_CASE;", first)
        self.emit("END_WHILE;", first)

    def run(self) -> list[LLine]:
        if not self.instrs:
            return []
        if self.mode == "pc":
            self.emit_pc("ключ --stl-jumps pc")
        elif self.reducible():
            self.emit_range(0, len(self.instrs))
        else:
            self.emit_pc("поток несводим к IF/REPEAT")
        for ins in self.instrs:
            status, rule = self.status.get(ins.index, (AUTO, rule_of(ins.token).rule))
            if ins.token in ("COMMENT", "EMPTY_LINE"):
                continue
            self.bl.unit("instruction", status, rule, ins.trace)
        return self.out


def _scl_type(type_name: str) -> str:
    up = type_name.upper()
    names = {"INT": "Int", "DINT": "DInt", "REAL": "Real", "WORD": "Word", "DWORD": "DWord", "BOOL": "Bool"}
    names.update({"BYTE": "Byte", "TIME": "Time", "ANY": "Int"})
    return names.get(up, type_name)


def lower_stl_units(bl: BlockLower, units: list[XUnit]) -> None:
    """Подряд идущие сети STL → один StlBlock (состояние машины переходит между сетями) → строки SCL."""
    block = StlBlock()
    for unit in units:
        if unit.body is not None:
            add_statement_list(block, unit.body, unit.number, unit.title, unit.comment)
    lifter = StlLifter(bl, block, bl.stl_jumps)
    bl.lines.extend(lifter.run())


__all__ = ["StlLifter", "lower_stl_units"]
