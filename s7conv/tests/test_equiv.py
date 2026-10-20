"""Эквивалентность: эталон S7 против stsim на сконвертированном коде; эталон независим; мутации ловятся."""

from __future__ import annotations

import ast
import random
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from s7conv import equiv as E
from s7conv.cli import EXIT_OK, EXIT_THRESHOLD, main
from s7conv.emitter import Options, convert
from s7conv.frontends.simaticml import parse_document
from s7conv.lower import net_to_ast, stl_lift
from s7conv.lower.block import LowerOptions, lower_document
from s7conv.parser import parse_source
from s7conv.semantics.net_eval import NetEvaluator
from s7conv.semantics.stl_machine import StlEvaluator
from s7conv.sim.stsim import Frame, Sim
from s7conv.symbols import Project
from s7conv.tests.conftest import REPO_ROOT

LANG = REPO_ROOT / "samples" / "lang"
SCENARIOS = REPO_ROOT / "scenarios" / "lang"
sys.path.insert(0, str(LANG))
import build_xml as B  # noqa: E402

sys.path.remove(str(LANG))

FORBIDDEN = {"s7conv.lower", "s7conv.emitter", "s7conv.plcopen", "s7conv.mapping"}


def test_semantics_does_not_import_the_translator() -> None:
    """Эталон не должен делить код с понижением и эмиттером (общий только разбор XML)."""
    for path in (REPO_ROOT / "s7conv" / "semantics").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                assert not any(name == f or name.startswith(f + ".") for f in FORBIDDEN), (path.name, name)


@pytest.mark.parametrize("jumps", ["structured", "pc"])
def test_corpus_has_no_divergences(jumps: str) -> None:
    report = E.run_equiv([str(LANG)], SCENARIOS, random_calls=200, seed=20261019, stl_jumps=jumps)
    names = {b.block for b in report.blocks}
    assert {"FB_StarterLad", "FB_StarterFbd", "FB_StarterStl", "FB_StarterScl", "FB_PumpInterlockLad"} <= names
    for b in report.blocks:
        assert not b.skipped, (b.block, b.skipped)
        assert b.divergence is None, b.divergence.format()
        assert b.scenario_calls > 0 and b.random_calls == 200


def test_equiv_cli_exit_codes(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["equiv", str(LANG), "--scenarios", str(SCENARIOS), "--random", "25"]) == EXIT_OK
    assert "без расхождений" in capsys.readouterr().out


def test_old_sr_mapping_mutation_is_caught(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Мутация «старое SR→SR»: SR с операндом в порядке RS (установка последней) — equiv находит расхождение."""
    original = net_to_ast.NetLowerer.do_flipflop

    def swapped(self: net_to_ast.NetLowerer, uid: int, part: object) -> None:
        part.name = {"SR": "RS", "RS": "SR"}[part.name]  # type: ignore[attr-defined]
        pins = {"s": "s1", "r1": "r", "s1": "s", "r": "r1"}
        self.net._drivers = {(u, pins.get(p, p) if u == uid else p): v for (u, p), v in self.net._drivers.items()}
        original(self, uid, part)  # type: ignore[arg-type]

    monkeypatch.setattr(net_to_ast.NetLowerer, "do_flipflop", swapped)
    report = E.run_equiv([str(LANG / "FB_StarterLad.xml")], SCENARIOS, random_calls=0)
    div = report.blocks[0].divergence
    assert div is not None and div.variable in ("xRun", "xRunMem")
    assert "StartAndStopTogether" in div.source
    assert main(["equiv", str(LANG / "FB_StarterLad.xml"), "--scenarios", str(SCENARIOS)]) == EXIT_THRESHOLD
    assert "РАСХОЖДЕНИЕ" in capsys.readouterr().out


def _block_dir(tmp: Path, block: B.Block) -> Path:
    path = tmp / f"{block.name}.xml"
    path.write_text(B.render(block), encoding="utf-8")
    return path


def test_eno_mutation_is_caught(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """ENO ADD при 32767 + 1: эталон ENO = 0; мутация «ENO = EN» даёт расхождение на случайных входах."""
    n = B.Net("add")
    add = n.part("Add", templates=[("SrcType", "Type", "Int"), ("Card", "Cardinality", "2")])
    n.wire(n.contact("rail", "#xEn"), (add, "en"))
    n.operand_in(add, "in1", "#iA")
    n.operand_in(add, "in2", "1")
    n.operand_out(add, "out", "#iSum")
    n.coil((add, "eno"), "#xOk")
    blk = B.Block(
        "FB",
        "FB_EnoProbe",
        1,
        sections=[
            B.Section("Input", [B.Member("xEn", "Bool"), B.Member("iA", "Int")]),
            B.Section("Output", [B.Member("iSum", "Int"), B.Member("xOk", "Bool")]),
        ],
        units=[B.lad_unit(n)],
    )
    path = _block_dir(tmp_path, blk)
    clean = E.run_equiv([str(path)], None, random_calls=300, seed=1)
    assert clean.blocks[0].divergence is None
    monkeypatch.setattr(net_to_ast, "_ENO_FUNCS", set())
    mutated = E.run_equiv([str(path)], None, random_calls=300, seed=1)
    div = mutated.blocks[0].divergence
    assert div is not None and div.variable == "xOk"


def test_zero_extension_mutation_is_caught(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """L INT → T DINT: S7 дополняет нулями (-1 → 65535); мутация «знаковое расширение» — расхождение."""
    s = B.Stl("ext").op("L", "#iIn").op("T", "#diOut")
    blk = B.Block(
        "FB",
        "FB_ExtProbe",
        1,
        lang="STL",
        layout="Standard",
        sections=[B.Section("Input", [B.Member("iIn", "Int")]), B.Section("Output", [B.Member("diOut", "DInt")])],
        units=[B.stl_unit(s)],
    )
    path = _block_dir(tmp_path, blk)
    assert E.run_equiv([str(path)], None, random_calls=200, seed=3).blocks[0].divergence is None
    original = stl_lift.StlLifter.convert

    def sign_extend(self: stl_lift.StlLifter, ins: object, val: stl_lift.Val, target: str) -> tuple[str, list]:  # type: ignore[type-arg]
        text, notes = original(self, ins, val, target)  # type: ignore[arg-type]
        return (f"{val.type}_TO_{target}({val.ex[0]})", notes) if "zero_extend" in str(notes) else (text, notes)

    monkeypatch.setattr(stl_lift.StlLifter, "convert", sign_extend)
    div = E.run_equiv([str(path)], None, random_calls=200, seed=3).blocks[0].divergence
    assert div is not None and div.variable == "diOut"


# ---------------------------------------------------------------------------
# Свойства: случайные цепочки STL и сети LAD — эталон против понижения
# ---------------------------------------------------------------------------

VARS = ("#a", "#b", "#c", "#d")
BOOLS = [B.Member(v[1:], "Bool") for v in VARS] + [B.Member("q", "Bool"), B.Member("m", "Bool")]


def _translated(block: B.Block) -> tuple[Sim, object, list]:  # type: ignore[type-arg]
    path = Path(f"{block.name}.xml")
    doc = parse_document(B.render(block), str(path))
    text, lowering, _ = lower_document(doc, {b.name.lower(): b for b in doc.blocks}, LowerOptions())
    sf = parse_source(text, str(path))
    sf.lowering = lowering
    result = convert([sf], Project(), Options())
    sim = Sim(list(result.objects))
    return sim, sim.new_instance(block.name), doc.blocks


def _run_both(block: B.Block, ref_cls: Callable[[Any], Any], vectors: list[dict[str, bool]]) -> None:
    sim, inst, blocks = _translated(block)
    ref = ref_cls(blocks[0])
    pou = sim.pous[block.name.lower()]
    for vec in vectors:
        ref.call(vec, 0)
        for k, v in vec.items():
            inst.vars[k.lower()] = v  # type: ignore[attr-defined]
        sim.run_body(pou.body, Frame(sim, inst, *sim.temps(pou.decls)))  # type: ignore[arg-type]
        for name in ("q", "m"):
            assert ref.read(name) == inst.vars[name], (name, vec)  # type: ignore[attr-defined]


@st.composite
def stl_chain(draw: st.DrawFn) -> list[tuple[str, str | None]]:
    """Цепочка STL: логика, скобки (до 7 уровней), O без операнда, NOT; в конце = q и S/R m."""
    ops: list[tuple[str, str | None]] = []
    depth = 0
    for _ in range(draw(st.integers(1, 14))):
        kind = draw(st.sampled_from(["logic", "logic", "logic", "open", "close", "or", "not"]))
        if kind == "logic":
            ops.append((draw(st.sampled_from(["A", "AN", "O", "ON", "X", "XN"])), draw(st.sampled_from(VARS))))
        elif kind == "open" and depth < 7:
            ops.append((draw(st.sampled_from(["A_BRACK", "AN_BRACK", "O_BRACK", "ON_BRACK", "X_BRACK"])), None))
            ops.append((draw(st.sampled_from(["A", "O"])), draw(st.sampled_from(VARS))))
            depth += 1
        elif kind == "close" and depth > 0:
            ops.append(("BRACKET", None))
            depth -= 1
        elif kind == "or":
            ops.append(("O", None))
            ops.append(("A", draw(st.sampled_from(VARS))))
        elif kind == "not":
            ops.append(("NEG", None))
    ops += [("BRACKET", None)] * depth
    ops.insert(0, ("A", "#a"))
    ops += [("Assign", "#q"), ("A", "#b"), ("S", "#m"), ("A", "#c"), ("R", "#m")]
    return ops


@settings(max_examples=60, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(stl_chain())
def test_random_stl_chains_match_machine(chain: list[tuple[str, str | None]]) -> None:
    s = B.Stl("chain")
    for token, operand in chain:
        s.op(token, operand)
    blk = B.Block(
        "FB", "FB_Chain", 1, lang="STL", layout="Standard", sections=[B.Section("Static", BOOLS)], units=[B.stl_unit(s)]
    )
    rng = random.Random(len(chain))
    vectors = [{v[1:]: rng.random() < 0.5 for v in VARS} for _ in range(12)]
    _run_both(blk, lambda b: StlEvaluator(b, "s7-300"), vectors)


@st.composite
def lad_network(draw: st.DrawFn) -> B.Net:
    """Сеть LAD: последовательные и параллельные контакты (до трёх уровней), катушка q и SR на m."""
    n = B.Net("random")

    def series(src: object, depth: int) -> tuple[int, str]:
        out = src
        for _ in range(draw(st.integers(1, 3))):
            if depth < 3 and draw(st.booleans()):
                branches = [series(out, depth + 1) for _ in range(draw(st.integers(2, 3)))]
                out = n.orr(*branches)
            else:
                out = n.contact(out, draw(st.sampled_from(VARS)), neg=draw(st.booleans()))  # type: ignore[arg-type]
        return out  # type: ignore[return-value]

    n.coil(series("rail", 0), "#q")
    sr = n.part(draw(st.sampled_from(["SR", "RS"])))
    first, second = ("s", "r1") if n.items[-1][2]["name"] == "SR" else ("r", "s1")
    n.wire(series("rail", 1), (sr, first))
    n.wire(n.contact("rail", draw(st.sampled_from(VARS))), (sr, second))
    n.operand_in(sr, "operand", "#m")
    return n


@settings(max_examples=60, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(lad_network())
def test_random_lad_networks_match_power_flow(net: B.Net) -> None:
    blk = B.Block("FB", "FB_Net", 1, sections=[B.Section("Static", BOOLS)], units=[B.lad_unit(net)])
    rng = random.Random(len(net.items))
    vectors = [{v[1:]: rng.random() < 0.5 for v in VARS} for _ in range(12)]
    _run_both(blk, NetEvaluator, vectors)
