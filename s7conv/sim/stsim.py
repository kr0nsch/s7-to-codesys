"""Минимальный интерпретатор ST для проверки сконвертированного кода без CODESYS (stsim).

До выпуска 1.1.0 модуль лежал в s7conv/tests/stsim.py; этот путь остаётся реэкспортом для соседних проектов.

Исполняет объекты раскладки (`src/`, `tests/`) — ФБ, функции, GVL, структуры — тем же разборщиком
операторов, что и конвертер (CODESYS ST по синтаксису операторов — это SCL без `#`). Поддерживается
подмножество, которого достаточно блокам со сценариями, слою S7Compat и сгенерированным наборам coUnit:
присваивания (в том числе бит `w.3`), IF/CASE/FOR/WHILE/REPEAT/EXIT/CONTINUE/RETURN, вызовы ФБ, функций и
методов набора, массивы, структуры, литералы TIME и 16#, стандартные функции (LIMIT, MIN, MAX, ABS,
преобразования `X_TO_Y`), R_TRIG, F_TRIG (семантика — параметр: S7 или МЭК с M = FALSE), SR, RS,
CTU, CTD, CTUD библиотеки Standard (модели — `builtin_flipflop`, `builtin_counter`), coUnit
(`TEST`, `TEST_FINISHED`, `AssertEquals_*`, `AssertTrue/False`).

Типы по объявлению: целые и битовые — с переполнением по разрядности, TIME — 32 бита без знака (мс),
REAL — округление до float32 при присваивании, STRING — обрезка по длине. Это модель CODESYS, а не
CODESYS: результат симуляции — предварительная проверка; окончательная — прогон в Control Win.
"""

from __future__ import annotations

import math
import re
import struct
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from s7conv.layout import L
from s7conv.nodes import (
    ArrayInit,
    Assign,
    Binary,
    Call,
    CallStmt,
    Case,
    CaseRange,
    CommentStmt,
    Continue,
    Empty,
    Exit,
    Expr,
    For,
    Ident,
    If,
    Index,
    Literal,
    Member,
    Region,
    Repeat,
    Return,
    Slice,
    Stmt,
    Unary,
    While,
)
from s7conv.parser import Parser, parse_statements

F_TRIG_S7 = "s7"  # Q = NOT CLK AND CLK прошлого вызова; до первого вызова — FALSE (спада на первом вызове нет)
F_TRIG_IEC_M_FALSE = "iec"  # Q := NOT CLK AND NOT M; M := NOT CLK; M = FALSE (ложный спад на первом вызове)

_SIGNED = {"SINT": 8, "INT": 16, "DINT": 32, "LINT": 64}
_UNSIGNED = {"USINT": 8, "UINT": 16, "UDINT": 32, "ULINT": 64, "BYTE": 8, "WORD": 16, "DWORD": 32, "LWORD": 64}
_DURATION_RE = re.compile(r"(?i)(\d+(?:\.\d+)?)(ms|d|h|m|s)")


class SimError(Exception):
    """Конструкция вне поддерживаемого подмножества или ошибка исполнения."""


class _ExitLoop(Exception):
    pass


class _ContinueLoop(Exception):
    pass


class _ReturnPou(Exception):
    pass


@dataclass(frozen=True)
class TypeSpec:
    name: str  # BOOL, INT, STRING, ARRAY, UDT_X, FB_X ...
    length: int = 80  # STRING(n)
    low: int = 0  # ARRAY[low..high]
    high: int = 0
    elem: TypeSpec | None = None


_ARRAY_RE = re.compile(r"(?is)ARRAY\s*\[\s*(-?\w+)\s*\.\.\s*(-?\w+)\s*\]\s*OF\s+(.+)")
_STRING_RE = re.compile(r"(?i)(W?STRING)\s*(?:\(\s*(\d+)\s*\))?$")


@dataclass
class Arr:
    spec: TypeSpec
    items: list[Any]

    def index(self, i: int) -> int:
        if not self.spec.low <= i <= self.spec.high:
            raise SimError(f"индекс {i} вне [{self.spec.low}..{self.spec.high}]")
        return i - self.spec.low


@dataclass
class Obj:
    """Экземпляр ФБ, структура или GVL: переменные (имя в нижнем регистре) и их типы."""

    type_name: str
    kind: str  # fb | struct | gvl
    vars: dict[str, Any] = field(default_factory=dict)
    types: dict[str, TypeSpec] = field(default_factory=dict)
    sections: dict[str, str] = field(default_factory=dict)
    state: dict[str, Any] = field(default_factory=dict)  # память встроенных ФБ (R_TRIG ...)


@dataclass
class PouDef:
    name: str
    kind: str  # program | function_block | function
    decls: list[L.VarDecl]
    body: list[Stmt]
    return_type: str | None = None
    extends: list[str] = field(default_factory=list)
    methods: dict[str, tuple[list[L.VarDecl], list[Stmt]]] = field(default_factory=dict)


@dataclass
class SuiteOutcome:
    registered: list[str] = field(default_factory=list)
    finished: set[str] = field(default_factory=set)
    failures: dict[str, list[str]] = field(default_factory=dict)
    asserts: int = 0


def _parse_body(text: str | None, where: str) -> list[Stmt]:
    stmts, issues = parse_statements(text or "")
    errors = [i for i in issues if i.severity == "error"]
    if errors:
        raise SimError(f"{where}: не разобрано: {errors[0].message} (строка {errors[0].line})")
    return stmts


class Sim:
    def __init__(self, objects: Sequence[L.StObject], f_trig: str = F_TRIG_S7) -> None:
        self.f_trig = f_trig
        self.pous: dict[str, PouDef] = {}
        self.structs: dict[str, list[L.VarDecl]] = {}
        self.gvls: dict[str, Obj] = {}
        self.time_ms = 0  # часы TIME() (тесты в реальном времени здесь не исполняются)
        self.outcome = SuiteOutcome()
        self._current_test = ""
        gvl_objects: list[L.StObject] = []
        for obj in objects:
            if obj.kind == L.KIND_DUT:
                tdecl = L.parse_type_decl(obj.decl)
                if tdecl is not None and tdecl.kind == "struct":
                    self.structs[obj.name.lower()] = list(tdecl.members)
            elif obj.kind == L.KIND_GVL:
                gvl_objects.append(obj)
            elif obj.kind == L.KIND_POU:
                header = obj.header or L.parse_header(obj.decl)
                decls = [d for b in L.parse_var_blocks(obj.decl) for d in b.decls]
                pou = PouDef(
                    name=obj.name,
                    kind=obj.pou_kind or "",
                    decls=decls,
                    body=_parse_body(obj.impl, obj.name),
                    return_type=header.return_type if header is not None else None,
                    extends=list(header.extends) if header is not None else [],
                )
                for m in obj.methods:
                    mdecls = [d for b in L.parse_var_blocks(m.decl) for d in b.decls]
                    pou.methods[m.name.lower()] = (mdecls, _parse_body(m.impl, f"{obj.name}.{m.name}"))
                self.pous[obj.name.lower()] = pou
        # GVL создаются при первом обращении: GVL с конструкциями вне подмножества (инициализаторы
        # структур в GVL_InstanceDBs) не мешают исполнять блоки, которые к ним не обращаются
        self._gvl_defs = {obj.name.lower(): obj for obj in gvl_objects}

    def gvl(self, key: str) -> Obj | None:
        if key not in self.gvls and key in self._gvl_defs:
            obj = self._gvl_defs[key]
            gvl = Obj(obj.name, "gvl")
            for block in L.parse_var_blocks(obj.decl):
                for d in block.decls:
                    self._declare(gvl, d)
            self.gvls[key] = gvl
        return self.gvls.get(key)

    # -- типы и значения -------------------------------------------------------------------------
    def type_of(self, text: str) -> TypeSpec:
        text = " ".join(text.split())
        m = _ARRAY_RE.match(text)
        if m:
            low, high = int(self.const_value(m.group(1))), int(self.const_value(m.group(2)))
            return TypeSpec("ARRAY", low=low, high=high, elem=self.type_of(m.group(3)))
        m = _STRING_RE.match(text)
        if m:
            return TypeSpec(m.group(1).upper(), length=int(m.group(2) or 80))
        upper = text.upper()
        if upper == "TOD":
            upper = "TIME_OF_DAY"
        return TypeSpec(upper if upper in _SIGNED or upper in _UNSIGNED or upper in _SCALARS else text)

    def const_value(self, text: str) -> Any:
        expr = Parser(text).expression()
        return self.eval(expr, Frame(self, None, {}, {}))

    def default(self, spec: TypeSpec) -> Any:
        name = spec.name.upper()
        if name == "BOOL":
            return False
        if name in _SIGNED or name in _UNSIGNED or name in ("TIME", "LTIME", "DATE", "TIME_OF_DAY", "DT"):
            return 0
        if name in ("REAL", "LREAL"):
            return 0.0
        if name in ("STRING", "WSTRING"):
            return ""
        if name == "ARRAY":
            assert spec.elem is not None
            return Arr(spec, [self.default(spec.elem) for _ in range(spec.high - spec.low + 1)])
        return self.new_object(spec.name)

    def new_object(self, type_name: str) -> Obj:
        key = type_name.lower()
        if key in self.structs:
            obj = Obj(type_name, "struct")
            for d in self.structs[key]:
                self._declare(obj, d)
            return obj
        if key in self.pous and self.pous[key].kind == L.POU_FUNCTION_BLOCK:
            return self.new_instance(type_name)
        if key in _BUILTIN_FBS:
            bool_spec, time_spec, word_spec = TypeSpec("BOOL"), TypeSpec("TIME"), TypeSpec("WORD")
            if key in _FLIPFLOPS:
                set_in, reset_in = _FLIPFLOPS[key]
                return Obj(
                    type_name.upper(),
                    "fb",
                    vars={set_in: False, reset_in: False, "q1": False},
                    types={set_in: bool_spec, reset_in: bool_spec, "q1": bool_spec},
                )
            if key in _COUNTERS:
                names = _COUNTERS[key]
                return Obj(
                    type_name.upper(),
                    "fb",
                    vars={n: (0 if n in ("pv", "cv") else False) for n in names},
                    types={n: (word_spec if n in ("pv", "cv") else bool_spec) for n in names},
                    state={"cu": False, "cd": False},
                )
            if key in ("r_trig", "f_trig"):
                return Obj(
                    type_name.upper(),
                    "fb",
                    vars={"clk": False, "q": False},
                    types={"clk": bool_spec, "q": bool_spec},
                    state={"m": False},
                )
            return Obj(
                type_name.upper(),
                "fb",
                vars={"in": False, "pt": 0, "q": False, "et": 0},
                types={"in": bool_spec, "pt": time_spec, "q": bool_spec, "et": time_spec},
                state={"prev": False, "start": 0, "run": False},
            )
        raise SimError(f"тип {type_name} не поддерживается")

    def new_instance(self, fb_name: str) -> Obj:
        pou = self.pous[fb_name.lower()]
        obj = Obj(pou.name, "fb")
        for d in pou.decls:
            if not d.section.startswith("VAR_TEMP"):
                self._declare(obj, d)
        return obj

    def _declare(self, obj: Obj, d: L.VarDecl) -> None:
        spec = self.type_of(d.type_text)
        for name in d.name_list:
            key = name.lower()
            obj.types[key] = spec
            obj.sections[key] = d.section
            obj.vars[key] = self.default(spec)
            if d.init_text is not None:
                obj.vars[key] = self.initial(d.init_text, spec, obj)

    def initial(self, text: str, spec: TypeSpec, scope: Obj | None) -> Any:
        value = Parser(text).initializer()
        if isinstance(value, ArrayInit):
            assert spec.elem is not None
            items: list[Any] = []
            for count, item in value.items:
                if isinstance(item, ArrayInit):
                    raise SimError("вложенный инициализатор массива не поддерживается")
                n = 1 if count is None else int(self.eval(count, Frame(self, scope, {}, {})))
                items.extend([coerce(self.eval(item, Frame(self, scope, {}, {})), spec.elem)] * n)
            arr = self.default(spec)
            assert isinstance(arr, Arr)
            arr.items[: len(items)] = items
            return arr
        return coerce(self.eval(value, Frame(self, scope, {}, {})), spec)

    # -- выражения --------------------------------------------------------------------------------
    def eval(self, e: Expr, fr: Frame) -> Any:
        if isinstance(e, Literal):
            return literal(e)
        if isinstance(e, Ident):
            return fr.read(e.name)
        if isinstance(e, Member):
            base = self.eval(e.base, fr) if not _is_namespace(e.base) else None
            if base is None:
                raise SimError(f"обращение {e.name} к пространству имён")
            if not isinstance(base, Obj) or e.name.lower() not in base.vars:
                raise SimError(f"нет элемента {e.name}")
            return base.vars[e.name.lower()]
        if isinstance(e, Index):
            base = self.eval(e.base, fr)
            if not isinstance(base, Arr) or len(e.indices) != 1:
                raise SimError("индекс не у одномерного массива")
            return base.items[base.index(int(self.eval(e.indices[0], fr)))]
        if isinstance(e, Slice):
            if e.size not in ("", "X"):
                raise SimError(f"срез .%{e.size} не поддерживается")
            return bool((int(self.eval(e.base, fr)) >> e.number) & 1)
        if isinstance(e, Unary):
            v = self.eval(e.operand, fr)
            if e.op == "NOT":
                if isinstance(v, bool):
                    return not v
                raise SimError("NOT для целых не поддерживается")
            return -v if e.op == "-" else v
        if isinstance(e, Binary):
            return self.binary(e, fr)
        if isinstance(e, Call):
            return self.call(e, fr)
        raise SimError(f"выражение {type(e).__name__} не поддерживается")

    def binary(self, e: Binary, fr: Frame) -> Any:
        op = "AND" if e.op == "&" else e.op
        a = self.eval(e.left, fr)
        b = self.eval(e.right, fr)
        if op in ("AND", "OR", "XOR"):
            if isinstance(a, bool) and isinstance(b, bool):
                return {"AND": a and b, "OR": a or b, "XOR": a != b}[op]
            return {"AND": int(a) & int(b), "OR": int(a) | int(b), "XOR": int(a) ^ int(b)}[op]
        if op == "=":
            return a == b
        if op == "<>":
            return a != b
        if op == "<":
            return a < b
        if op == ">":
            return a > b
        if op == "<=":
            return a <= b
        if op == ">=":
            return a >= b
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            if isinstance(a, int) and isinstance(b, int) and not isinstance(a, bool):
                q = abs(a) // abs(b)
                return q if (a >= 0) == (b >= 0) else -q
            return a / b
        if op == "MOD":
            return int(math.fmod(a, b))
        if op == "**":
            return float(a) ** float(b)
        raise SimError(f"операция {e.op} не поддерживается")

    # -- вызовы -----------------------------------------------------------------------------------
    def call(self, c: Call, fr: Frame) -> Any:
        callee = c.callee
        if isinstance(callee, Member) and isinstance(callee.base, Ident) and callee.base.name.lower() == "counit":
            return self.counit(callee.name.upper(), [self.eval(a.value, fr) for a in c.args])
        if isinstance(callee, Ident):
            name = callee.name
            key = name.lower()
            target = fr.lookup(name)
            if target is not None and isinstance(target, Obj) and target.kind == "fb":
                self.call_fb(target, c.args, fr)
                return None
            if fr.obj is not None and fr.obj.kind == "fb":
                pou = self.pous.get(fr.obj.type_name.lower())
                if pou is not None and key in pou.methods:
                    self.call_method(fr.obj, pou, key)
                    return None
                is_suite = pou is not None and any(e.lower() == "counit.fb_testsuite" for e in pou.extends)
                if is_suite and key.startswith("assert"):
                    return self.assertion(name, c.args, fr)
            if key in self.pous and self.pous[key].kind == L.POU_FUNCTION:
                return self.call_function(self.pous[key], c.args, fr)
            return builtin(self, name, [self.eval(a.value, fr) for a in c.args])
        if isinstance(callee, Member | Index):
            target = self.eval(callee, fr)
            if isinstance(target, Obj) and target.kind == "fb":
                self.call_fb(target, c.args, fr)
                return None
        raise SimError("вызов этого вида не поддерживается")

    def call_fb(self, inst: Obj, args: Sequence[Any], fr: Frame) -> None:
        outputs: list[tuple[Expr, str]] = []
        for a in args:
            if a.name is None:
                raise SimError(f"позиционный аргумент ФБ {inst.type_name}")
            if a.output:
                outputs.append((a.value, a.name.lower()))
                continue
            key = a.name.lower()
            if key not in inst.vars:
                raise SimError(f"{inst.type_name}: нет входа {a.name}")
            inst.vars[key] = coerce(self.eval(a.value, fr), inst.types[key])
        if inst.type_name.lower() in _BUILTIN_FBS:
            self.builtin_fb(inst)
        else:
            pou = self.pous[inst.type_name.lower()]
            self.run_body(pou.body, Frame(self, inst, *self.temps(pou.decls)))
        for target, key in outputs:
            fr.assign(target, inst.vars[key])

    def temps(self, decls: Sequence[L.VarDecl]) -> tuple[dict[str, Any], dict[str, TypeSpec]]:
        """VAR_TEMP ФБ: новые значения на каждый вызов."""
        values: dict[str, Any] = {}
        types: dict[str, TypeSpec] = {}
        for d in decls:
            if d.section.startswith("VAR_TEMP"):
                spec = self.type_of(d.type_text)
                for n in d.name_list:
                    types[n.lower()] = spec
                    values[n.lower()] = self.default(spec)
        return values, types

    def call_method(self, inst: Obj, pou: PouDef, key: str) -> None:
        decls, body = pou.methods[key]
        values: dict[str, Any] = {}
        types: dict[str, TypeSpec] = {}
        for d in decls:
            spec = self.type_of(d.type_text)
            for n in d.name_list:
                types[n.lower()] = spec
                values[n.lower()] = self.initial(d.init_text, spec, inst) if d.init_text else self.default(spec)
        self.run_body(body, Frame(self, inst, values, types))

    def call_function(self, pou: PouDef, args: Sequence[Any], fr: Frame) -> Any:
        values: dict[str, Any] = {}
        types: dict[str, TypeSpec] = {}
        inputs: list[str] = []
        for d in pou.decls:
            spec = self.type_of(d.type_text)
            for n in d.name_list:
                types[n.lower()] = spec
                values[n.lower()] = self.initial(d.init_text, spec, None) if d.init_text else self.default(spec)
                if d.section.startswith("VAR_INPUT"):
                    inputs.append(n.lower())
        ret = pou.name.lower()
        assert pou.return_type is not None
        types[ret] = self.type_of(pou.return_type)
        values[ret] = self.default(types[ret])
        for pos, a in enumerate(args):
            key = a.name.lower() if a.name else inputs[pos]
            values[key] = coerce(self.eval(a.value, fr), types[key])
        self.run_body(pou.body, Frame(self, None, values, types))
        return values[ret]

    def builtin_fb(self, inst: Obj) -> None:
        kind = inst.type_name.upper()
        if kind in ("TON", "TOF", "TP"):
            self.builtin_timer(inst, kind)
            return
        if kind.lower() in _FLIPFLOPS:
            builtin_flipflop(inst, kind)
            return
        if kind.lower() in _COUNTERS:
            builtin_counter(inst, kind)
            return
        clk = bool(inst.vars["clk"])
        if kind == "R_TRIG":
            inst.vars["q"] = clk and not inst.state["m"]
            inst.state["m"] = clk
        elif self.f_trig == F_TRIG_S7:
            inst.vars["q"] = (not clk) and inst.state["m"]
            inst.state["m"] = clk
        else:
            inst.vars["q"] = (not clk) and not inst.state["m"]
            inst.state["m"] = not clk

    def builtin_timer(self, inst: Obj, kind: str) -> None:
        """Модель TON/TOF/TP CODESYS Standard по МЭК 61131-3 (часы — time_ms); для тестов в реальном времени."""
        v, st = inst.vars, inst.state
        now, pt, in_ = self.time_ms, int(v["pt"]), bool(v["in"])

        def elapsed() -> int:
            return (now - int(st["start"])) & 0xFFFFFFFF

        if kind == "TON":
            if in_:
                if not st["prev"]:
                    st["start"] = now
                v["q"], v["et"] = elapsed() >= pt, min(elapsed(), pt)
            else:
                v["q"], v["et"] = False, 0
        elif kind == "TOF":
            if in_:
                v["q"], v["et"], st["run"] = True, 0, False
            elif st["prev"]:
                st["start"], st["run"] = now, True
            if st["run"]:
                if elapsed() >= pt:
                    v["q"], v["et"], st["run"] = False, pt, False
                else:
                    v["et"] = elapsed()
        else:
            if in_ and not st["prev"] and not v["q"]:
                st["start"], v["q"] = now, True
            if v["q"]:
                if elapsed() >= pt:
                    v["q"], v["et"] = False, pt
                else:
                    v["et"] = elapsed()
            if not in_ and not v["q"]:
                v["et"] = 0
        st["prev"] = in_

    # -- coUnit -----------------------------------------------------------------------------------
    def counit(self, name: str, args: list[Any]) -> Any:
        if name == "TEST":
            self._current_test = str(args[0])
            if self._current_test not in self.outcome.registered:
                self.outcome.registered.append(self._current_test)
            return None
        if name == "TEST_FINISHED":
            self.outcome.finished.add(self._current_test)
            return None
        raise SimError(f"coUnit.{name} не поддерживается")

    def assertion(self, name: str, args: Sequence[Any], fr: Frame) -> None:
        values = {a.name.lower(): self.eval(a.value, fr) for a in args if a.name}
        self.outcome.asserts += 1
        upper = name.upper()
        message = str(values.get("message", ""))
        if upper in ("ASSERTTRUE", "ASSERTFALSE"):
            ok = bool(values["condition"]) == (upper == "ASSERTTRUE")
            detail = f"Condition = {values['condition']}"
        else:
            expected, actual = values["expected"], values["actual"]
            if "delta" in values:
                ok = abs(float(actual) - float(expected)) <= float(values["delta"])
            else:
                ok = expected == actual
            detail = f"Expected {expected!r}, Actual {actual!r}"
        if not ok:
            self.outcome.failures.setdefault(self._current_test, []).append(f"{message}: {detail}")

    def run_suite(self, suite_name: str, cycles: int = 2, skip: Sequence[str] = (), cycle_ms: int = 10) -> SuiteOutcome:
        """Набор coUnit: экземпляр и вызовы тела каждый цикл, как у раннера; часы TIME() идут на cycle_ms."""
        self.outcome = SuiteOutcome()
        inst = self.new_instance(suite_name)
        pou = self.pous[suite_name.lower()]
        body = [s for s in pou.body if not _calls_method(s, skip)]
        for _ in range(cycles):
            self.run_body(body, Frame(self, inst, {}, {}))
            self.time_ms = (self.time_ms + cycle_ms) & 0xFFFFFFFF
        return self.outcome

    # -- операторы --------------------------------------------------------------------------------
    def run_body(self, body: Sequence[Stmt], fr: Frame) -> None:
        try:
            for s in body:
                self.stmt(s, fr)
        except _ReturnPou:
            return

    def stmt(self, s: Stmt, fr: Frame) -> None:
        if isinstance(s, Assign):
            if s.op != ":=":
                raise SimError(f"оператор {s.op}")
            fr.assign(s.target, self.eval(s.value, fr))
        elif isinstance(s, CallStmt):
            self.call(s.call, fr)
        elif isinstance(s, If):
            for cond, body in s.branches:
                if self.eval(cond, fr):
                    self.block(body, fr)
                    return
            if s.else_body is not None:
                self.block(s.else_body, fr)
        elif isinstance(s, Case):
            sel = self.eval(s.selector, fr)
            for clause in s.clauses:
                for lb in clause.labels:
                    hit = (
                        self.eval(lb.lo, fr) <= sel <= self.eval(lb.hi, fr)
                        if isinstance(lb, CaseRange)
                        else self.eval(lb, fr) == sel
                    )
                    if hit:
                        self.block(clause.body, fr)
                        return
            if s.else_body is not None:
                self.block(s.else_body, fr)
        elif isinstance(s, For):
            step = int(self.eval(s.step, fr)) if s.step is not None else 1
            fr.assign(s.var, self.eval(s.start, fr))
            end = self.eval(s.end, fr)
            while (self.eval(s.var, fr) <= end) if step > 0 else (self.eval(s.var, fr) >= end):
                try:
                    self.block(s.body, fr)
                except _ExitLoop:
                    break
                except _ContinueLoop:
                    pass
                fr.assign(s.var, self.eval(s.var, fr) + step)
        elif isinstance(s, While):
            while self.eval(s.cond, fr):
                try:
                    self.block(s.body, fr)
                except _ExitLoop:
                    break
                except _ContinueLoop:
                    continue
        elif isinstance(s, Repeat):
            while True:
                try:
                    self.block(s.body, fr)
                except _ExitLoop:
                    break
                except _ContinueLoop:
                    pass
                if self.eval(s.cond, fr):
                    break
        elif isinstance(s, Exit):
            raise _ExitLoop
        elif isinstance(s, Continue):
            raise _ContinueLoop
        elif isinstance(s, Return):
            raise _ReturnPou
        elif isinstance(s, Region):
            self.block(s.body, fr)
        elif isinstance(s, Empty | CommentStmt):
            return
        else:
            raise SimError(f"оператор {type(s).__name__} не поддерживается")

    def block(self, body: Sequence[Stmt], fr: Frame) -> None:
        for s in body:
            self.stmt(s, fr)


class Frame:
    """Область имён вызова: временные переменные, затем переменные экземпляра, затем GVL."""

    def __init__(self, sim: Sim, obj: Obj | None, values: dict[str, Any], types: dict[str, TypeSpec]) -> None:
        self.sim = sim
        self.obj = obj
        self.values = values
        self.types = types

    def lookup(self, name: str) -> Any:
        key = name.lower()
        if key in self.values:
            return self.values[key]
        if self.obj is not None and key in self.obj.vars:
            return self.obj.vars[key]
        return self.sim.gvl(key)

    def read(self, name: str) -> Any:
        value = self.lookup(name)
        if value is None:
            raise SimError(f"имя {name} не найдено")
        return value

    def _slot(self, target: Expr) -> tuple[dict[str, Any] | list[Any], Any, TypeSpec]:
        if isinstance(target, Ident):
            key = target.name.lower()
            if key in self.values:
                return self.values, key, self.types[key]
            if self.obj is not None and key in self.obj.vars:
                return self.obj.vars, key, self.obj.types[key]
            raise SimError(f"присваивание необъявленной {target.name}")
        if isinstance(target, Member):
            base = self.sim.eval(target.base, self)
            key = target.name.lower()
            if not isinstance(base, Obj) or key not in base.vars:
                raise SimError(f"нет элемента {target.name}")
            return base.vars, key, base.types[key]
        if isinstance(target, Index):
            base = self.sim.eval(target.base, self)
            if not isinstance(base, Arr):
                raise SimError("индекс не у массива")
            assert base.spec.elem is not None
            return base.items, base.index(int(self.sim.eval(target.indices[0], self))), base.spec.elem
        raise SimError(f"цель присваивания {type(target).__name__}")

    def assign(self, target: Expr, value: Any) -> None:
        if isinstance(target, Slice):
            if target.size not in ("", "X"):
                raise SimError("запись в срез")
            container, key, spec = self._slot(target.base)
            word = int(container[key])
            mask = 1 << target.number
            container[key] = coerce((word | mask) if value else (word & ~mask), spec)
            return
        container, key, spec = self._slot(target)
        container[key] = coerce(value, spec)


_SCALARS = frozenset({"BOOL", "REAL", "LREAL", "TIME", "LTIME", "DATE", "TIME_OF_DAY", "DT"})
# Бистабильные элементы Standard: вход установки, вход сброса (выход — Q1)
_FLIPFLOPS = {"sr": ("set1", "reset"), "rs": ("set", "reset1")}
# Счётчики Standard: входы и выходы (PV и CV — WORD)
_COUNTERS = {
    "ctu": ("cu", "reset", "pv", "q", "cv"),
    "ctd": ("cd", "load", "pv", "q", "cv"),
    "ctud": ("cu", "cd", "reset", "load", "pv", "qu", "qd", "cv"),
}
_WORD_MAX = 0xFFFF
_BUILTIN_FBS = frozenset({"r_trig", "f_trig", "ton", "tof", "tp", *_FLIPFLOPS, *_COUNTERS})


def builtin_flipflop(inst: Obj, kind: str) -> None:
    """SR и RS CODESYS Standard 3.5.17.0 (standard.chm, «SR (FB)», «RS (FB)»).

    SR — приоритет установки: Q1 := SET1 OR (NOT RESET AND Q1).
    RS — приоритет сброса: Q1 := NOT RESET1 AND (SET OR Q1).
    Справка называет входы «Rising edge», но формулы — по уровню (МЭК 61131-3, 2.5.2.3.1); уровень
    подтверждает тест FB_StandardFlipFlop_Test.SrSetHeldReappliesAfterReset в Control Win.
    Независимо от mapping.py: модель описывает CODESYS, а не перевод S7.
    """
    v = inst.vars
    if kind.upper() == "SR":
        v["q1"] = bool(v["set1"]) or (not v["reset"] and bool(v["q1"]))
    else:
        v["q1"] = (not v["reset1"]) and (bool(v["set"]) or bool(v["q1"]))


def builtin_counter(inst: Obj, kind: str) -> None:
    """CTU, CTD, CTUD CODESYS Standard 3.5.17.0 (standard.chm, «CTU (FB)», «CTD (FB)», «CTUD (FB)»).

    Фронт CU/CD — внутренняя память экземпляра; RESET и LOAD — по уровню. CTU: RESET → CV := 0, иначе
    по фронту CU CV := CV + 1, пока CV < 65535 (WORD); Q := CV >= PV. CTD: LOAD → CV := PV, иначе по
    фронту CD CV := CV - 1, пока CV > 0; Q := CV = 0. CTUD: RESET главнее LOAD; при одновременных фронтах
    CU и CD действуют оба (+1 и -1). Предел 65535 и одновременные фронты справка не описывает — их
    проверяют тесты FB_StandardCounter_Test в Control Win.
    """
    v, st = inst.vars, inst.state
    upper = kind.upper()
    cu_edge = cd_edge = False
    if "cu" in v:
        cu_edge = bool(v["cu"]) and not st["cu"]
        st["cu"] = bool(v["cu"])
    if "cd" in v:
        cd_edge = bool(v["cd"]) and not st["cd"]
        st["cd"] = bool(v["cd"])
    cv = int(v["cv"])
    if upper == "CTU":
        if v["reset"]:
            cv = 0
        elif cu_edge and cv < _WORD_MAX:
            cv += 1
        v["q"] = cv >= int(v["pv"])
    elif upper == "CTD":
        if v["load"]:
            cv = int(v["pv"])
        elif cd_edge and cv > 0:
            cv -= 1
        v["q"] = cv == 0
    else:
        if v["reset"]:
            cv = 0
        elif v["load"]:
            cv = int(v["pv"])
        else:
            if cu_edge and cv < _WORD_MAX:
                cv += 1
            if cd_edge and cv > 0:
                cv -= 1
        v["qu"] = cv >= int(v["pv"])
        v["qd"] = cv == 0
    v["cv"] = cv


def _is_namespace(e: Expr) -> bool:
    return isinstance(e, Ident) and e.name.lower() in ("counit",)


def _calls_method(s: Stmt, names: Sequence[str]) -> bool:
    return (
        isinstance(s, CallStmt)
        and isinstance(s.call.callee, Ident)
        and s.call.callee.name.lower() in {n.lower() for n in names}
    )


def coerce(value: Any, spec: TypeSpec) -> Any:
    name = spec.name.upper()
    if name == "BOOL":
        return bool(value)
    if name in _SIGNED:
        bits = _SIGNED[name]
        v = int(value) & ((1 << bits) - 1)
        return v - (1 << bits) if v >= 1 << (bits - 1) else v
    if name in _UNSIGNED or name == "TIME":
        bits = _UNSIGNED.get(name, 32)
        return int(value) & ((1 << bits) - 1)
    if name == "REAL":
        return struct.unpack("f", struct.pack("f", float(value)))[0]
    if name == "LREAL":
        return float(value)
    if name in ("STRING", "WSTRING"):
        return str(value)[: spec.length]
    return value


def literal(e: Literal) -> Any:
    if e.kind == "bool":
        return e.text.upper() == "TRUE"
    if e.kind == "int":
        return int(e.text.replace("_", ""))
    if e.kind == "real":
        return float(e.text.replace("_", ""))
    if e.kind == "string":
        return e.text[1:-1].replace("$'", "'").replace("$$", "$")
    head, _, body = e.text.partition("#")
    upper = head.upper()
    if upper.isdigit():
        return int(body.replace("_", ""), int(upper))
    if upper in ("T", "TIME"):
        total = 0.0
        for amount, unit in _DURATION_RE.findall(body):
            total += float(amount) * {"d": 86400000, "h": 3600000, "m": 60000, "s": 1000, "ms": 1}[unit.lower()]
        return int(total)
    if upper in _SIGNED or upper in _UNSIGNED:
        return literal(Literal("typed" if "#" in body else "int", body))
    if upper in ("REAL", "LREAL"):
        return float(body)
    raise SimError(f"литерал {e.text} не поддерживается")


def builtin(sim: Sim, name: str, args: list[Any]) -> Any:
    upper = name.upper()
    if upper == "TIME" and not args:
        return sim.time_ms
    if upper == "LIMIT":
        lo, v, hi = args
        return max(lo, min(v, hi))
    if upper == "MIN":
        return min(args)
    if upper == "MAX":
        return max(args)
    if upper == "ABS":
        return abs(args[0])
    if upper == "SQRT":
        return math.sqrt(args[0])
    if "_TO_" in upper:
        dst = upper.split("_TO_", 1)[1]
        value = args[0]
        if dst in _SIGNED or dst in _UNSIGNED:
            # REAL_TO_<целое> в CODESYS округляет к ближайшему (сверить); здесь — round
            value = round(value) if isinstance(value, float) else int(value)
        return coerce(value, TypeSpec(dst))
    raise SimError(f"функция {name} не поддерживается")


__all__ = [
    "F_TRIG_IEC_M_FALSE",
    "F_TRIG_S7",
    "Arr",
    "Frame",
    "Obj",
    "PouDef",
    "Sim",
    "SimError",
    "SuiteOutcome",
    "TypeSpec",
    "builtin",
    "builtin_counter",
    "builtin_flipflop",
    "coerce",
    "literal",
]
