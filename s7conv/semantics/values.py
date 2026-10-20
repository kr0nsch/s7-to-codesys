"""Значения и память эталона S7: литералы, разрядность типов, таймеры и счётчики IEC.

Модели — по справочникам Siemens (таймеры IEC TON/TOF/TP и счётчики CTU/CTD/CTUD — LAD S7-300/400,
s7kop__b.pdf, гл. 11–12; поведение IEC 61131-3), а не по слою S7Compat и не по stsim.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

Value = Any


class Undefined:
    """⊥: значение не определено (S7-1500: RLO после смены языка, ACCU после CALL — FAQ 67655405)."""

    _instance: Undefined | None = None

    def __new__(cls) -> Undefined:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "⊥"


UNDEF = Undefined()

_SIGNED = {"SINT": 8, "INT": 16, "DINT": 32, "LINT": 64}
_UNSIGNED = {"USINT": 8, "UINT": 16, "UDINT": 32, "ULINT": 64, "BYTE": 8, "WORD": 16, "DWORD": 32, "LWORD": 64}
_DURATION_RE = re.compile(r"(?i)(\d+(?:\.\d+)?)(ms|d|h|m|s)")


def type_key(datatype: str) -> str:
    """Тип члена SimaticML → ключ эталона: INT, DINT, BOOL, TIME, REAL, TON_TIME ..."""
    return datatype.strip('"').split("[")[0].upper()


def wrap(value: Value, datatype: str) -> Value:
    """Значение в разрядности типа (целые — с переносом, как запись в память S7)."""
    if value is UNDEF:
        return UNDEF
    key = type_key(datatype)
    if key == "BOOL":
        return bool(value)
    if key in _SIGNED:
        bits = _SIGNED[key]
        v = int(value) & ((1 << bits) - 1)
        return v - (1 << bits) if v >= 1 << (bits - 1) else v
    if key in _UNSIGNED:
        return int(value) & ((1 << _UNSIGNED[key]) - 1)
    if key == "TIME":
        v = int(value) & 0xFFFFFFFF
        return v - (1 << 32) if v >= 1 << 31 else v
    if key in ("REAL", "LREAL"):
        return float(value)
    return value


def default(datatype: str) -> Value:
    key = type_key(datatype)
    if key == "BOOL":
        return False
    if key in ("REAL", "LREAL"):
        return 0.0
    if key in _SIGNED or key in _UNSIGNED or key in ("TIME", "S5TIME", "DATE", "TIME_OF_DAY"):
        return 0
    if key.startswith(("STRING", "WSTRING")):
        return ""
    return None


def parse_literal(text: str) -> Value | None:
    """Литерал S7 (TRUE, 12, -3, 1.5, T#2S, 16#FF, W#16#FF, L#5, INT#3) → значение; не литерал — None."""
    t = text.strip()
    up = t.upper()
    if up in ("TRUE", "FALSE"):
        return up == "TRUE"
    if re.fullmatch(r"-?\d+", t):
        return int(t)
    if re.fullmatch(r"-?\d+\.\d*(E[-+]?\d+)?", up):
        return float(t)
    if "#" not in t:
        return None
    head, _, body = up.rpartition("#")
    head = head.split("#")[-1] if head.count("#") else head
    if up.startswith(("T#", "TIME#")):
        total = 0.0
        for amount, unit in _DURATION_RE.findall(body):
            total += float(amount) * {"d": 86400000, "h": 3600000, "m": 60000, "s": 1000, "ms": 1}[unit.lower()]
        return int(total)
    if head.isdigit():
        return int(body.replace("_", ""), int(head))
    if head in ("L", "DINT", "INT", "SINT", "LINT", "UINT", "UDINT", "USINT"):
        return int(body)
    if head in ("REAL", "LREAL"):
        return float(body)
    return None


# ---------------------------------------------------------------------------
# Таймеры и счётчики IEC (экземпляры)
# ---------------------------------------------------------------------------


@dataclass
class Timer:
    """TON/TOF/TP IEC с явными часами (мс)."""

    kind: str
    q: bool = False
    et: int = 0
    prev_in: bool = False
    start: int = 0
    running: bool = False

    def call(self, now: int, in_: bool, pt: int) -> None:
        if self.kind == "TON":
            if in_:
                if not self.prev_in:
                    self.start = now
                elapsed = now - self.start
                self.q = elapsed >= pt
                self.et = min(elapsed, pt)
            else:
                self.q, self.et = False, 0
        elif self.kind == "TOF":
            if in_:
                self.q, self.et, self.running = True, 0, False
            elif self.prev_in:
                self.start, self.running = now, True
            if not in_ and self.running:
                elapsed = now - self.start
                if elapsed >= pt:
                    self.q, self.et, self.running = False, pt, False
                else:
                    self.et = elapsed
        else:  # TP
            if in_ and not self.prev_in and not self.q:
                self.start, self.q = now, True
            if self.q:
                elapsed = now - self.start
                if elapsed >= pt:
                    self.q, self.et = False, pt
                else:
                    self.et = elapsed
            if not in_ and not self.q:
                self.et = 0
        self.prev_in = in_

    def member(self, name: str) -> Value:
        return {"Q": self.q, "ET": self.et}[name.upper()]


@dataclass
class Counter:
    """CTU/CTD/CTUD IEC S7: счёт по фронту, R и LD — по уровню (s7kop__b.pdf, гл. 12)."""

    kind: str
    cv: int = 0
    q: bool = False
    qu: bool = False
    qd: bool = False
    prev_cu: bool = False
    prev_cd: bool = False

    def call(self, args: dict[str, Value]) -> None:
        cu, cd = bool(args.get("CU", False)), bool(args.get("CD", False))
        r, ld, pv = bool(args.get("R", False)), bool(args.get("LD", False)), int(args.get("PV", 0))
        up, down = cu and not self.prev_cu, cd and not self.prev_cd
        self.prev_cu, self.prev_cd = cu, cd
        if self.kind == "CTU":
            self.cv = 0 if r else self.cv + (1 if up and self.cv < 32767 else 0)
            self.q = self.cv >= pv
        elif self.kind == "CTD":
            self.cv = pv if ld else self.cv - (1 if down and self.cv > -32768 else 0)
            self.q = self.cv <= 0
        else:
            if r:
                self.cv = 0
            elif ld:
                self.cv = pv
            else:
                self.cv += (1 if up else 0) - (1 if down else 0)
            self.qu, self.qd = self.cv >= pv, self.cv <= 0

    def member(self, name: str) -> Value:
        return {"CV": self.cv, "Q": self.q, "QU": self.qu, "QD": self.qd}[name.upper()]


INSTANCE_TYPES = {"TON_TIME": "TON", "TOF_TIME": "TOF", "TP_TIME": "TP", "TON": "TON", "TOF": "TOF", "TP": "TP"}
COUNTER_TYPES = {"CTU": "CTU", "CTD": "CTD", "CTUD": "CTUD", "CTU_INT": "CTU", "CTD_INT": "CTD", "CTUD_INT": "CTUD"}


@dataclass
class Memory:
    """Переменные экземпляра блока: имя (в нижнем регистре) → значение и тип; экземпляры таймеров/счётчиков."""

    values: dict[str, Value] = field(default_factory=dict)
    types: dict[str, str] = field(default_factory=dict)
    instances: dict[str, Timer | Counter] = field(default_factory=dict)

    def declare(self, name: str, datatype: str, start: str | None = None) -> None:
        key = name.lower()
        tkey = type_key(datatype)
        self.types[key] = datatype
        if tkey in INSTANCE_TYPES:
            self.instances[key] = Timer(INSTANCE_TYPES[tkey])
            return
        if tkey in COUNTER_TYPES:
            self.instances[key] = Counter(COUNTER_TYPES[tkey])
            return
        value = parse_literal(start) if start else None
        self.values[key] = wrap(value, datatype) if value is not None else default(datatype)

    def read(self, operand: str) -> Value:
        lit = parse_literal(operand)
        if lit is not None:
            return lit
        name = operand.lstrip("#").strip('"')
        base, _, member = name.partition(".")
        key = base.lower()
        if member:
            inst = self.instances.get(key)
            if inst is None:
                raise KeyError(f"эталон: нет экземпляра {base}")
            return inst.member(member)
        if key not in self.values:
            raise KeyError(f"эталон: нет переменной {operand}")
        return self.values[key]

    def write(self, operand: str, value: Value) -> None:
        name = operand.lstrip("#").strip('"')
        key = name.lower()
        if key not in self.values:
            raise KeyError(f"эталон: запись в необъявленную {operand}")
        self.values[key] = wrap(value, self.types[key])

    def type_of(self, operand: str) -> str:
        key = operand.lstrip("#").strip('"').split(".")[0].lower()
        return self.types.get(key, "")


__all__ = [
    "COUNTER_TYPES",
    "INSTANCE_TYPES",
    "UNDEF",
    "Counter",
    "Memory",
    "Timer",
    "Undefined",
    "Value",
    "default",
    "parse_literal",
    "type_key",
    "wrap",
]
