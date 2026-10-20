"""Эталон STL: машина S7-300 по справочнику STL S7-300/400 (AWL_e.pdf), независимо от lower/stl_lift.py.

Состояние: биты /FC, RLO, OR, STA, OV, OS, CC0, CC1, BR; два 32-битных аккумулятора; стек скобок (до 7
уровней: RLO, OR, функция). Правила:
- логика: первая проверка (/FC = 0) загружает RLO; A — AND; O — OR с «AND перед OR» (OR-бит хранит итог
  закрытых AND-групп, §1.x); O без операнда закрывает AND-группу; X — XOR; скобки сохраняют RLO, OR и
  функцию; =, S, R, FP/FN завершают цепочку (/FC := 0);
- L: ACCU2 := ACCU1, ACCU1 := операнд; ACCU1 перед загрузкой обнуляется — BYTE/WORD/INT дополняются нулями
  (§9.2); T пишет младшие биты ACCU1 нужной ширины;
- +I/-I/*I//I: только ACCU1-L и ACCU2-L, ACCU1-H не меняется, ACCU2 не меняется (2 ACCU, §7.3); OV/OS при
  переполнении; +D/-D/*D//D/MOD — 32 бита; сравнения ==I … ставят RLO как первая проверка (CC0/CC1);
- JC/JCN/JU — переходы к меткам; после JC/JCN: /FC := 0, RLO := 1 (§6.x);
- CALL TON/TOF/TP — таймер IEC с экземпляром, параметры по операндам.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from s7conv.frontends.simaticml import XBlock
from s7conv.ir.stl import StlBlock, StlInstr, add_statement_list
from s7conv.semantics.values import UNDEF, Memory, Timer, Value, type_key, wrap

_WIDTH = {"BOOL": 1, "BYTE": 8, "CHAR": 8, "INT": 16, "WORD": 16, "DINT": 32, "DWORD": 32, "TIME": 32, "REAL": 32}


class StlError(Exception):
    """Инструкция вне эталона — блок не сравнивается."""


@dataclass
class _Bracket:
    op: str
    rlo: bool
    or_bit: bool
    fc: bool


@dataclass
class Machine:
    fc: bool = False
    rlo: Value = False
    or_bit: bool = False
    group_open: bool = True
    ov: bool = False
    os: bool = False
    accu1: int = 0
    accu2: int = 0
    stack: list[_Bracket] = field(default_factory=list)


def _signed(value: int, bits: int) -> int:
    value &= (1 << bits) - 1
    return value - (1 << bits) if value >= 1 << (bits - 1) else value


class StlEvaluator:
    """Экземпляр блока STL: память и вызов `call(inputs, now_ms)`."""

    def __init__(self, block: XBlock, profile: str = "s7-300") -> None:
        self.block = block
        self.profile = profile
        self.mem = Memory()
        for sec in block.sections:
            for m in sec.members:
                self.mem.declare(m.name, m.datatype, m.start_value)
        self.code = StlBlock()
        for unit in block.units:
            if unit.body is None:
                continue
            if unit.body_kind != "StatementList":
                raise StlError(f"{block.name}: сеть {unit.number} не STL")
            add_statement_list(self.code, unit.body, unit.number, unit.title)
        self.labels = self.code.labels()
        self.writes: dict[str, str] = {}
        self.temps = [m.name.lower() for s in block.sections if s.name == "Temp" for m in s.members]
        self.m = Machine()

    # -- RLO ---------------------------------------------------------------------------
    def effective(self) -> Value:
        m = self.m
        if not m.fc:
            return m.rlo
        if m.rlo is UNDEF:
            return UNDEF
        return m.or_bit or (bool(m.rlo) if m.group_open else False)

    def logic(self, op: str, value: Value) -> None:
        m = self.m
        neg = op.endswith("N")
        base = op[:-1] if neg else op
        v = (not value) if neg and value is not UNDEF else value
        if not m.fc:
            m.fc, m.or_bit, m.rlo, m.group_open = True, False, v, True
            return
        if base == "A":
            m.rlo = v if not m.group_open else (UNDEF if UNDEF in (m.rlo, v) else bool(m.rlo) and bool(v))
            m.group_open = True
        elif base == "O":
            prev = self.effective()
            m.or_bit = bool(prev) if prev is not UNDEF else False
            m.rlo, m.group_open = v, True
        else:
            full = self.effective()
            m.or_bit, m.group_open = False, True
            m.rlo = UNDEF if UNDEF in (full, v) else bool(full) != bool(v)

    def finish(self, value: Value) -> None:
        self.m.fc, self.m.rlo, self.m.or_bit, self.m.group_open = False, value, False, True

    # -- аккумуляторы ---------------------------------------------------------------------
    def load_value(self, operand: str) -> int:
        value = self.mem.read(operand)
        typ = type_key(self.mem.type_of(operand)) if operand.startswith("#") else ""
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, float):
            import struct

            return int.from_bytes(struct.pack(">f", value), "big")
        width = _WIDTH.get(typ, 32 if not (-32768 <= int(value) <= 65535) else 16)
        return int(value) & ((1 << width) - 1)  # ACCU1 обнуляется: дополнение нулями

    def store_value(self, operand: str) -> None:
        typ = type_key(self.mem.type_of(operand))
        width = _WIDTH.get(typ, 32)
        raw = self.m.accu1 & ((1 << width) - 1)
        if typ == "REAL":
            import struct

            self.mem.write(operand, struct.unpack(">f", raw.to_bytes(4, "big"))[0])
            return
        self.mem.write(operand, wrap(raw if typ in ("WORD", "DWORD", "BYTE") else _signed(raw, width), typ))

    def math(self, op: str, typ: str) -> None:
        m = self.m
        if typ == "I":
            a, b = _signed(m.accu2, 16), _signed(m.accu1, 16)
            exact = self._op(op, a, b)
            m.ov = not -32768 <= exact <= 32767
            m.os = m.os or m.ov
            m.accu1 = (m.accu1 & 0xFFFF0000) | (exact & 0xFFFF)
        elif typ == "D":
            a, b = _signed(m.accu2, 32), _signed(m.accu1, 32)
            exact = self._op(op, a, b)
            m.ov = not -(2**31) <= exact <= 2**31 - 1
            m.os = m.os or m.ov
            m.accu1 = exact & 0xFFFFFFFF
        else:
            raise StlError(f"арифметика {op}{typ} эталоном не моделируется")

    @staticmethod
    def _op(op: str, a: int, b: int) -> int:
        if op == "ADD":
            return a + b
        if op == "SUB":
            return a - b
        if op == "MUL":
            return a * b
        if b == 0:
            raise StlError("деление на 0")
        q = abs(a) // abs(b)
        return q if (a >= 0) == (b >= 0) else -q

    def compare(self, op: str, typ: str) -> None:
        bits = 16 if typ == "I" else 32
        a, b = _signed(self.m.accu2, bits), _signed(self.m.accu1, bits)
        result = {"EQ": a == b, "NE": a != b, "GT": a > b, "GE": a >= b, "LT": a < b, "LE": a <= b}[op]
        self.m.fc, self.m.rlo, self.m.or_bit, self.m.group_open = True, result, False, True

    # -- исполнение ---------------------------------------------------------------------
    def call(self, inputs: dict[str, Value], now: int) -> None:
        for name in self.temps:
            self.mem.declare(name, self.mem.types[name])
        for name, value in inputs.items():
            self.mem.write(f"#{name}", value)
        pc = 0
        steps = 0
        code = self.code.instrs
        while pc < len(code):
            steps += 1
            if steps > 100_000:
                raise StlError("бесконечный цикл")
            ins = code[pc]
            nxt = self.step(ins, now)
            if nxt == -1:
                return
            pc = nxt if nxt is not None else pc + 1

    def write(self, operand: str, value: Value, ins: StlInstr) -> None:
        self.mem.write(operand, value)
        self.writes[operand.lstrip("#").lower()] = ins.trace

    def step(self, ins: StlInstr, now: int) -> int | None:
        t = ins.token
        m = self.m
        if t in ("COMMENT", "EMPTY_LINE", "NOP_0", "NOP_1", "BLD"):
            return None
        if t in ("A", "AN", "O", "ON", "X", "XN"):
            if ins.operand is None:
                if t == "O" and m.fc:
                    m.or_bit = bool(self.effective())
                    m.group_open = False
                    return None
                raise StlError(f"{ins.trace}: {t} без операнда")
            self.logic(t, self.mem.read(ins.operand))
            return None
        if t.endswith("_BRACK") and t != "MCR_BRACK":
            if len(m.stack) >= 7:
                raise StlError(f"{ins.trace}: стек скобок переполнен")
            m.stack.append(_Bracket(t[: -len("_BRACK")], bool(m.rlo), m.or_bit, m.fc))
            m.fc, m.or_bit, m.group_open = False, False, True
            return None
        if t == "BRACKET":
            inner = self.effective()
            br = m.stack.pop()
            m.rlo, m.or_bit, m.fc, m.group_open = br.rlo, br.or_bit, br.fc, True
            self.logic(br.op, inner)
            return None
        if t == "NEG":
            v = self.effective()
            if m.fc:
                m.rlo, m.or_bit, m.group_open = (UNDEF if v is UNDEF else not v), False, True
            else:
                m.rlo = UNDEF if v is UNDEF else not v
            return None
        if t in ("SET", "CLR"):
            self.finish(t == "SET")
            return None
        if t in ("Assign", "S", "R"):
            v = self.effective()
            assert ins.operand is not None
            if t == "Assign":
                self.write(ins.operand, v, ins)
            elif v is UNDEF:
                self.write(ins.operand, UNDEF, ins)
            elif v:
                self.write(ins.operand, t == "S", ins)
            self.finish(v)
            return None
        if t in ("Rise", "Fall"):
            assert ins.operand is not None
            v = self.effective()
            mem = bool(self.mem.read(ins.operand))
            edge = (bool(v) and not mem) if t == "Rise" else (not v and mem)
            self.write(ins.operand, bool(v), ins)
            m.fc, m.rlo, m.or_bit, m.group_open = True, edge, False, True
            return None
        if t == "L":
            assert ins.operand is not None
            m.accu2, m.accu1 = m.accu1, self.load_value(ins.operand)
            return None
        if t == "T":
            assert ins.operand is not None
            self.store_value(ins.operand)
            self.writes[ins.operand.lstrip("#").lower()] = ins.trace
            return None
        if t[:-2] in ("ADD", "SUB", "MUL", "DIV") and t[-2] == "_":
            self.math(t[:-2], t[-1])
            return None
        if t[:-2] in ("EQ", "NE", "GT", "GE", "LT", "LE") and t[-2] == "_":
            self.compare(t[:-2], t[-1])
            return None
        if t in ("JU", "JC", "JCN"):
            target = self.labels.get(ins.operand or "")
            if target is None:
                raise StlError(f"{ins.trace}: метка {ins.operand} не найдена")
            v = self.effective()
            jump = t == "JU" or (t == "JC" and v is True) or (t == "JCN" and v is False)
            if t != "JU":
                self.finish(True)
            return target if jump else None
        if t == "CALL" and ins.call is not None:
            self.call_instruction(ins, now)
            return None
        if t in ("BE", "BEU"):
            return -1
        if t == "BEC":
            v = self.effective()
            self.finish(True)
            return -1 if v else None
        raise StlError(f"{ins.trace}: инструкция {t} эталоном не моделируется")

    def call_instruction(self, ins: StlInstr, now: int) -> None:
        call = ins.call
        assert call is not None
        if call.kind != "Instruction" or call.name not in ("TON", "TOF", "TP"):
            raise StlError(f"{ins.trace}: CALL {call.name} эталоном не моделируется")
        inst = self.mem.instances.get(call.instance.lstrip("#").strip('"').lower())
        if not isinstance(inst, Timer):
            raise StlError(f"{ins.trace}: экземпляр {call.instance} не таймер")
        params = {name.upper(): operand for name, _s, _t, operand in call.params}
        in_op, pt_op = params.get("IN"), params.get("PT")
        in_ = bool(self.mem.read(in_op)) if in_op else False
        pt = int(self.mem.read(pt_op)) if pt_op else 0
        inst.call(now, in_, pt)
        for name in ("Q", "ET"):
            target = params.get(name)
            if target:
                self.write(target, inst.member(name), ins)
        # S7-1500: после CALL слово состояния и ACCU не определены (FAQ 67655405); S7-300 — BR = ENO
        self.m.fc = False
        self.m.rlo = UNDEF if self.profile == "s7-1500" else True

    def read(self, name: str) -> Value:
        return self.mem.read(f"#{name}")

    def outputs(self) -> dict[str, Value]:
        out: dict[str, Value] = {}
        for sec in self.block.sections:
            if sec.name in ("Output", "InOut", "Static"):
                for mem in sec.members:
                    key = mem.name.lower()
                    if key in self.mem.values:
                        out[mem.name] = self.mem.values[key]
                    elif key in self.mem.instances:
                        out[f"{mem.name}.Q"] = self.mem.instances[key].member("Q")
        return out


__all__ = ["Machine", "StlError", "StlEvaluator"]
