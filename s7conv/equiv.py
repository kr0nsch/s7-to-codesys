"""Эквивалентность: эталон S7 (s7conv/semantics) против интерпретатора ST (stsim) на сконвертированном коде.

`s7conv equiv <вход> [--scenarios DIR] [--random N --seed S]`: одни входы по вызовам подаются эталону
(поток питания LAD/FBD, машина STL S7-300) и экземпляру сконвертированного ФБ в stsim; после каждого вызова
сравниваются все выходы и статика. Блоки одного семейства (scenarios/<...>/aliases.json — например,
FB_Starter на LAD, FBD, STL и SCL) дополнительно сравниваются между собой: перевод SCL сверяется с эталоном
LAD того же семейства. Первое расхождение — с трассой до сети и UId (LAD/FBD) или строки (STL), код 1.

Время: таймеры сконвертированного кода — S7Compat (`--timers s7compat`), часы GVL_S7Clock ставятся на t_ms
вызова; эталон получает те же t_ms. «Эквивалентно» значит «на сценариях и случайных входах по модели», не
формальное доказательство (docs/EQUIVALENCE.md).
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeAlias

from s7conv import mapping as M
from s7conv import pipeline as P
from s7conv import testgen as TG
from s7conv.emitter import ConversionResult, Options
from s7conv.frontends.simaticml import XBlock, parse_document
from s7conv.semantics.net_eval import EvalError, NetEvaluator
from s7conv.semantics.stl_machine import StlError, StlEvaluator
from s7conv.semantics.values import UNDEF, Value, type_key
from s7conv.sim.stsim import Frame, Obj, Sim, coerce

SEQUENCE_LENGTH = 25
Sequence: TypeAlias = tuple[str, list[tuple[int, dict[str, Value]]]]  # (имя, [(t_ms, входы)])
_TIME_STEPS = (0, 100, 300, 700, 1500, 2600)


@dataclass
class Divergence:
    block: str
    source: str  # «сценарий StartStop, вызов 3» или «случайная последовательность 7, вызов 12»
    variable: str
    reference: Value
    translated: Value
    trace: str
    other: str = "эталон S7"

    def format(self) -> str:
        return (
            f"{self.block}: {self.source}: {self.variable} — {self.other} {self.reference!r}, "
            f"ST {self.translated!r} (последняя запись в эталоне: {self.trace or 'нет'})"
        )


@dataclass
class BlockReport:
    block: str
    lang: str
    reference: str  # «эталон LAD», «эталон STL», «семейство FB_Starter (эталон FB_StarterLad)»
    scenario_calls: int = 0
    random_calls: int = 0
    divergence: Divergence | None = None
    skipped: str = ""


@dataclass
class EquivReport:
    blocks: list[BlockReport] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(b.divergence is None for b in self.blocks)


# ---------------------------------------------------------------------------
# Входы
# ---------------------------------------------------------------------------


def cell_value(text: str, type_name: str) -> Value:
    if type_name == "BOOL":
        return text == "TRUE"
    if type_name == "TIME":
        m = re.fullmatch(r"T#(\d+)MS", text)
        return int(m.group(1)) if m else 0
    if type_name in ("REAL", "LREAL"):
        return float(text)
    if text.startswith("16#"):
        return int(text[3:], 16)
    return int(text)


def scenario_sequences(scenarios: Path | None, block: str, family: str) -> list[Sequence]:
    """Сценарии CSV блока (или его семейства по aliases.json): [(имя, [(t_ms, входы)])]."""
    if scenarios is None or not scenarios.is_dir():
        return []
    out: list[Sequence] = []
    for name in dict.fromkeys((block, family)):
        path = scenarios / f"{name}.csv"
        if not path.is_file():
            continue
        sf = TG.read_scenarios(path.read_bytes().decode("utf-8"), path.as_posix())
        types = {c.path: c.type for c in sf.columns if c.kind == "in"}
        for scenario, rows in sf.scenarios():
            seq = [(r.t_ms, {p: cell_value(v, types[p]) for p, v in r.inputs.items()}) for r in rows]
            out.append((scenario, seq))
        break
    return out


def random_sequences(block: XBlock, count: int, seed: int) -> list[Sequence]:
    """Случайные входы: последовательности по SEQUENCE_LENGTH вызовов, каждая — с новых экземпляров."""
    rng = random.Random(seed)
    inputs = [
        (m.name, type_key(m.datatype), m.start_value) for s in block.sections if s.name == "Input" for m in s.members
    ]
    out: list[Sequence] = []
    done = 0
    n = 0
    while done < count:
        n += 1
        length = min(SEQUENCE_LENGTH, count - done)
        seq: list[tuple[int, dict[str, Value]]] = []
        t = 0
        for _ in range(length):
            t += rng.choice(_TIME_STEPS)
            values: dict[str, Value] = {}
            for name, typ, _start in inputs:
                if typ == "BOOL":
                    values[name] = rng.random() < 0.35
                elif typ == "TIME":
                    values[name] = rng.choice((500, 1000, 2000))
                elif typ in ("INT", "DINT"):
                    values[name] = rng.choice((rng.randint(-20, 160), rng.randint(0, 700), 32767, -32768, 0))
                elif typ in ("REAL", "LREAL"):
                    values[name] = round(rng.uniform(-10.0, 110.0), 3)
            seq.append((t, values))
        out.append((f"случайная последовательность {n}", seq))
        done += length
    return out


# ---------------------------------------------------------------------------
# Переведённый ФБ в stsim
# ---------------------------------------------------------------------------


class Translated:
    def __init__(self, sim: Sim, result: ConversionResult, block: str) -> None:
        self.sim = sim
        self.scope = result.scopes[block.lower()]
        sym = result.project.block(block) if result.project is not None else None
        assert sym is not None
        self.pou = sim.pous[sym.st_name.lower()]
        self.inst = sim.new_instance(sym.st_name)

    def st(self, name: str) -> str:
        var = self.scope.get(name.lower())
        return (var.st_name if var is not None else name).lower()

    def call(self, inputs: dict[str, Value], now: int) -> None:
        clock = self.sim.gvl("gvl_s7clock")
        if clock is not None:
            clock.vars["xsimulation"] = True
            clock.vars["tsimnow"] = now & 0xFFFFFFFF
        for name, value in inputs.items():
            key = self.st(name)
            self.inst.vars[key] = coerce(value, self.inst.types[key])
        self.sim.time_ms = now & 0xFFFFFFFF
        self.sim.run_body(self.pou.body, Frame(self.sim, self.inst, *self.sim.temps(self.pou.decls)))

    def read(self, name: str) -> Value:
        base, _, member = name.partition(".")
        value: Any = self.inst.vars.get(self.st(base))
        if member and isinstance(value, Obj):
            value = value.vars.get(member.lower())
        return value


def _same(a: Value, b: Value) -> bool:
    if isinstance(a, float) or isinstance(b, float):
        return abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(a)))
    return bool(a == b)


# ---------------------------------------------------------------------------
# Прогон
# ---------------------------------------------------------------------------


def _reference(blk: XBlock, registry: dict[str, XBlock], cpu: str | None) -> NetEvaluator | StlEvaluator:
    lang = blk.lang.upper()
    if lang in ("LAD", "FBD", "LAD_IEC", "FBD_IEC"):
        return NetEvaluator(blk, registry)
    if lang == "STL":
        profile = cpu or ("s7-1500" if blk.memory_layout.lower() == "optimized" else "s7-300")
        return StlEvaluator(blk, profile)
    raise EvalError(f"эталона для {lang} нет")


def run_equiv(
    paths: list[str],
    scenarios: Path | None = None,
    random_calls: int = 0,
    seed: int = 20261019,
    cpu: str | None = None,
    stl_jumps: str = "structured",
) -> EquivReport:
    inputs = P.collect_inputs(paths)
    options = Options(timers=M.S7COMPAT, cpu=cpu, stl_jumps=stl_jumps)
    result, _files = P.run(inputs, options)
    registry: dict[str, XBlock] = {}
    for path in inputs.xml:
        for blk in parse_document(P.read_source(path), str(path)).blocks:
            registry.setdefault(blk.name.lower(), blk)
    objects = list(result.objects) + P.support_objects(sorted(result.support))
    aliases = TG.load_aliases(scenarios) if scenarios is not None and scenarios.is_dir() else {}
    family_of = {member.lower(): fam for fam, members in aliases.items() for member in members}
    report = EquivReport()
    for blk in registry.values():
        if blk.kind != "FB":
            continue
        family = family_of.get(blk.name.lower(), blk.name)
        rep = BlockReport(blk.name, blk.lang.upper(), "")
        report.blocks.append(rep)
        ref_block = blk
        if blk.lang.upper() == "SCL":
            members = [m for m in aliases.get(family, []) if m.lower() != blk.name.lower()]
            anchor = next(
                (
                    registry[m.lower()]
                    for m in members
                    if m.lower() in registry and registry[m.lower()].lang.upper() in ("LAD", "FBD", "STL")
                ),
                None,
            )
            if anchor is None:
                rep.skipped = "SCL без эталона: блок проверяют сценарии и тесты coUnit"
                continue
            ref_block = anchor
            rep.reference = f"семейство {family}: эталон {anchor.name} ({anchor.lang.upper()})"
        else:
            rep.reference = f"эталон {blk.lang.upper()}"
        sequences = [(f"сценарий {n}", s, True) for n, s in scenario_sequences(scenarios, blk.name, family)]
        sequences += [(n, s, False) for n, s in random_sequences(blk, random_calls, seed)] if random_calls else []
        try:
            for source, seq, is_scenario in sequences:
                ref = _reference(ref_block, registry, cpu)
                st = Translated(Sim(objects), result, blk.name)
                for k, (t_ms, values) in enumerate(seq, start=1):
                    ref.call(values, t_ms)
                    st.call(values, t_ms)
                    if is_scenario:
                        rep.scenario_calls += 1
                    else:
                        rep.random_calls += 1
                    for name, expected in ref.outputs().items():
                        if expected is UNDEF:
                            continue
                        actual = st.read(name)
                        if not _same(expected, actual):
                            writes = ref.trace.writes if isinstance(ref, NetEvaluator) else ref.writes
                            rep.divergence = Divergence(
                                blk.name,
                                f"{source}, вызов {k}",
                                name,
                                expected,
                                actual,
                                writes.get(name.lower(), ""),
                                f"эталон {ref_block.name}",
                            )
                            break
                    if rep.divergence:
                        break
                if rep.divergence:
                    break
        except (EvalError, StlError, KeyError) as exc:
            rep.skipped = f"эталон не применим: {exc}"
    return report


__all__ = ["BlockReport", "Divergence", "EquivReport", "random_sequences", "run_equiv", "scenario_sequences"]
