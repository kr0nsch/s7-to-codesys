"""S7-GRAPH: SeqIR и топология, ST-двойник (правила цикла), эталон, вариант SFC в PLCopen XML."""

from __future__ import annotations

import copy
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from s7conv import corpus as C
from s7conv import equiv as E
from s7conv import pipeline as P
from s7conv.cli import EXIT_OK, main
from s7conv.emitter import Options
from s7conv.frontends.simaticml import XBlock, parse_document
from s7conv.ir.seq import Graph, parse_graph, topology
from s7conv.layout import L
from s7conv.lower.block import LowerOptions, lower_document
from s7conv.mapping import S7COMPAT
from s7conv.plcopen import graph_sfc
from s7conv.plcopen.sfc import NS, SfcError, sfc_project
from s7conv.sim.stsim import F_TRIG_S7, Sim
from s7conv.tests.conftest import REPO_ROOT

LANG = REPO_ROOT / "samples" / "lang"
SCENARIOS = REPO_ROOT / "scenarios" / "lang"
SAMPLES = str(LANG)
sys.path.insert(0, SAMPLES)
import blocks as corpus  # noqa: E402  samples/lang/blocks.py
import build_xml as B  # noqa: E402  samples/lang/build_xml.py

sys.path.remove(SAMPLES)

Q = f"{{{NS}}}"


def xblock(blk: B.Block | None = None) -> XBlock:
    blk = blk or corpus.backwash_graph()
    return parse_document(B.render(blk), f"{blk.name}.xml").blocks[0]


def graph_of(xb: XBlock) -> Graph:
    unit = next(u for u in xb.units if u.body_kind == "Graph")
    assert unit.body is not None
    return parse_graph(unit.body)


def twin_lines(blk: B.Block, tmp: Path) -> list[str]:
    path = tmp / f"{blk.name}.xml"
    path.write_text(B.render(blk), encoding="utf-8")
    result, _ = P.run(P.collect_inputs([str(path)]), Options(timers=S7COMPAT))
    obj = next(o for o in result.objects if o.name == blk.name)
    assert obj.impl is not None
    return [ln.strip() for ln in obj.impl.splitlines() if ln.strip() and not ln.strip().startswith("//")]


def priority_block(sfc_breaker: B.GAction | None = None, pre: bool = False, limit: str | None = None) -> B.Block:
    """Шаг с двумя альтернативами, условия которых могут быть истинны одновременно (приоритет левой ветви)."""
    actions = [B.GAction("N", "#xA")]
    if sfc_breaker is not None:
        actions.append(sfc_breaker)
    seq = B.GSequence(
        "Альтернативы",
        steps=[
            B.GStep(1, "Wait", init=True, actions=[B.GAction("N", "#xIdle")]),
            B.GStep(2, "Left", actions=actions, max_time=limit),
            B.GStep(3, "Right", actions=[B.GAction("N", "#xB")]),
        ],
        transitions=[
            B.GTransition(1, "GoLeft", corpus._cond("Влево", ("#xL", False))),
            B.GTransition(2, "GoRight", corpus._cond("Вправо", ("#xR", False))),
            B.GTransition(3, "BackL", corpus._cond("Назад", ("#xBack", False))),
            B.GTransition(4, "BackR", corpus._cond("Назад", ("#xBack", False))),
        ],
        branches=[B.GBranch(1, "AltBegin", 2)],
        connections=[
            (("S", 1), ("B", 1, 0, None), "Direct"),
            (("B", 1, None, 0), ("T", 1), "Direct"),
            (("B", 1, None, 1), ("T", 2), "Direct"),
            (("T", 1), ("S", 2), "Direct"),
            (("T", 2), ("S", 3), "Direct"),
            (("S", 2), ("T", 3), "Direct"),
            (("S", 3), ("T", 4), "Direct"),
            (("T", 3), ("S", 1), "Jump"),
            (("T", 4), ("S", 1), "Jump"),
        ],
    )
    pre_nets = []
    if pre:
        net = B.Net("Пред")
        net.coil(net.contact("rail", "#xL"), "#xSeen")
        pre_nets.append(net)
    inputs = [B.Member(n, "Bool") for n in ("INIT_SQ", "xL", "xR", "xBack")]
    outputs = [B.Member(n, "Bool") for n in ("xIdle", "xA", "xB", "xSeen")]
    return B.Block(
        "FB",
        "FB_AltPriority",
        130,
        lang="GRAPH",
        sections=[B.Section("Input", inputs), B.Section("Output", outputs), B.Section("Static")],
        units=[B.graph_unit(seq, pre=pre_nets)],
    )


# ---------------------------------------------------------------------------
# SeqIR и топология
# ---------------------------------------------------------------------------


def test_seq_ir_reads_steps_actions_branches_and_jump() -> None:
    graph = graph_of(xblock())
    assert len(graph.sequences) == 1 and len(graph.post) == 1 and not graph.pre
    seq = graph.sequences[0]
    assert [(s.number, s.name, s.init) for s in seq.steps][:2] == [(1, "Idle", True), (2, "Drain", False)]
    drain = seq.step(2)
    assert [(a.qualifier, a.event, a.operand) for a in drain.actions] == [
        ("N", "", "#xDrainValve"),
        ("S", "", "#xWashActive"),
        ("N", "S1", ""),
    ]
    assert drain.supervision is not None and seq.step(4).interlock is not None
    air = seq.step(3).actions[1]
    assert (air.qualifier, air.operand, air.time) == ("D", "#xAirValve", "T#2S")
    assert sorted(b.type for b in seq.branches) == ["AltBegin", "AltEnd", "SimBegin", "SimEnd"]
    assert [(c.src.number, c.dst.number) for c in seq.connections if c.link == "Jump"] == [(6, 1)]


def test_topology_links_alternatives_parallel_branches_and_jump() -> None:
    topo = topology(graph_of(xblock()).sequences[0])
    assert topo.issues == []
    assert (topo.link(2).preds, topo.link(2).succs, topo.link(2).priority) == ([2], [3, 4], 0)
    assert (topo.link(3).preds, topo.link(3).succs, topo.link(3).priority) == ([2], [5], 1)
    assert (topo.link(4).preds, topo.link(4).succs) == ([3, 4], [6])
    assert topo.link(5).succs == [6] and topo.link(6).succs == [1]


def test_topology_reports_transition_without_predecessor() -> None:
    blk = priority_block()
    graph = graph_of(xblock(blk))
    broken = copy.deepcopy(graph.sequences[0])
    broken.connections = [c for c in broken.connections if not (c.dst.kind == "T" and c.dst.number == 3)]
    assert any("T3 без шага-предшественника" in issue for issue in topology(broken).issues)


# ---------------------------------------------------------------------------
# ST-двойник
# ---------------------------------------------------------------------------


def test_twin_follows_graph_cycle_order(tmp_path: Path) -> None:
    """Порядок цикла (ASSUMPTIONS L18–L22): прошлое состояние до INIT, квитирование до переходов, время шага,
    переходы без ошибки контроля, сначала выключение, затем включение шагов; приоритет левой альтернативы."""
    lines = twin_lines(corpus.backwash_graph(), tmp_path)
    text = "\n".join(lines)

    def at(fragment: str) -> int:
        return next(i for i, ln in enumerate(lines) if fragment in ln)

    assert at("xDrain_Prev := Drain_X;") < at("IF INIT_SQ OR NOT GraphInitDone THEN") < at("IF ACK_EF THEN")
    assert at("IF ACK_EF THEN") < at("Drain_T := F_S7TimeDiff(tGraphNow, Drain_Start);") < at("xT1_Fire :=")
    assert "xT2_Fire := Drain_X AND xT2_Cond AND NOT xGraphHold AND NOT Drain_SvErr;" in text
    assert "xT4_Fire := Air_X AND Rinse_X AND xT4_Cond AND NOT xGraphHold;" in text
    deactivate = next(i for i in range(len(lines) - 1) if lines[i] == "IF xT2_Fire THEN" and "FALSE" in lines[i + 1])
    activate = next(i for i in range(len(lines) - 1) if lines[i] == "IF xT2_Fire THEN" and "TRUE" in lines[i + 1])
    assert deactivate < activate


def test_twin_left_alternative_wins(tmp_path: Path) -> None:
    text = "\n".join(twin_lines(priority_block(), tmp_path))
    assert "xT1_Fire := Wait_X AND xT1_Cond AND NOT xGraphHold;" in text
    assert "xT2_Fire := Wait_X AND xT2_Cond AND NOT xGraphHold AND NOT xT1_Fire;" in text


def test_graph_condition_coils_become_st_assignments() -> None:
    """Катушки TrCoil/SvCoil/IlCoil: сеть условия → присваивание временной переменной; элемент уровня L —
    переход и шаг «требуют проверки»; единицы учёта GRAPH — шаг и переход, постоперация — сеть."""
    doc = parse_document(B.render(corpus.backwash_graph()), "FB_BackwashGraph.xml")
    text, low, _ = lower_document(doc, {b.name.lower(): b for b in doc.blocks}, LowerOptions())
    assert "#xT2_Cond := #xLevelLow AND NOT #xShortWash;" in text
    assert "#xT4_Cond := #Air_T >= T#10S;" in text
    kinds = {(u.kind, u.status, u.rule) for u in low.units}
    assert ("transition", "check", "lad.vocab_unverified") in kinds
    assert ("step", "check", "graph.supervision") in kinds
    assert ("network", "auto", "lad.network") in kinds
    assert sum(u.kind == "step" for u in low.units) == 6 and sum(u.kind == "transition" for u in low.units) == 6


def test_twin_and_reference_agree_on_scenarios_and_random_calls() -> None:
    report = E.run_equiv([str(LANG / "FB_BackwashGraph.xml")], SCENARIOS, random_calls=300, seed=20261020)
    (block,) = report.blocks
    assert block.lang == "GRAPH" and not block.skipped
    assert block.divergence is None, block.divergence.format()
    assert block.scenario_calls == 46 and block.random_calls == 300


def test_alternative_priority_matches_reference(tmp_path: Path) -> None:
    path = tmp_path / "FB_AltPriority.xml"
    path.write_text(B.render(priority_block()), encoding="utf-8")
    report = E.run_equiv([str(path)], None, random_calls=400, seed=7)
    (block,) = report.blocks
    assert block.divergence is None, block.divergence.format()


@pytest.fixture(scope="module")
def objects() -> list[L.StObject]:
    return list(L.scan(str(REPO_ROOT), "src").objects) + list(L.scan(str(REPO_ROOT), "tests").objects)


def _mutate(objs: list[L.StObject], old: str, new: str, count: int = 1) -> list[L.StObject]:
    result = copy.deepcopy(objs)
    twin = next(o for o in result if o.name == "FB_BackwashGraph")
    assert twin.impl is not None and old in twin.impl
    twin.impl = twin.impl.replace(old, new, count)
    return result


def test_shared_multicycle_suite_passes_on_twin(objects: list[L.StObject]) -> None:
    """Набор tests/POUs/Graph — тот же, что проходит вариант SFC в CODESYS (tools_project/cds_plcopen.py)."""
    out = Sim(objects, f_trig=F_TRIG_S7).run_suite("FB_BackwashGraph_SeqTest", cycles=3)
    assert out.failures == {}, out.failures
    assert out.finished == set(out.registered) and len(out.registered) == 5


def test_supervision_blocking_mutation_is_caught(objects: list[L.StObject]) -> None:
    """Без «NOT Drain_SvErr» переходы из шага с ошибкой контроля срабатывают: падают сценарий и общий набор."""
    mutated = _mutate(objects, " AND NOT Drain_SvErr", "", count=-1)
    scenario = Sim(mutated, f_trig=F_TRIG_S7).run_suite("FB_BackwashGraph_ScenarioTest", cycles=3)
    assert "Supervision" in scenario.failures
    suite = Sim(mutated, f_trig=F_TRIG_S7).run_suite("FB_BackwashGraph_SeqTest", cycles=3)
    assert "SupervisionHoldsUntilAck" in suite.failures


def test_s1_event_every_cycle_mutation_is_caught(objects: list[L.StObject]) -> None:
    """Событие S1 только при активации: мутация «каждый цикл, пока шаг активен» ломает счётчик промывок."""
    twin = next(o for o in objects if o.name == "FB_BackwashGraph")
    assert twin.impl is not None
    old = next(ln for ln in twin.impl.splitlines() if ln.startswith("xDrain_S1 :="))
    mutated = _mutate(objects, old, "xDrain_S1 := Drain_X;")
    scenario = Sim(mutated, f_trig=F_TRIG_S7).run_suite("FB_BackwashGraph_ScenarioTest", cycles=3)
    assert len(scenario.failures) == 6  # iWashCount проверяется во всех сценариях
    suite = Sim(mutated, f_trig=F_TRIG_S7).run_suite("FB_BackwashGraph_SeqTest", cycles=3)
    assert sorted(suite.failures) == ["InitResets", "ShortWashCycle"]


# ---------------------------------------------------------------------------
# Вариант SFC (PLCopen XML)
# ---------------------------------------------------------------------------


def test_sfc_project_has_steps_transitions_actions_and_wrapper() -> None:
    xml = sfc_project(xblock(), "samples/lang/FB_BackwashGraph.xml").xml
    root = ET.fromstring(xml)
    pous = {p.get("name"): p for p in root.iter(f"{Q}pou")}
    assert list(pous) == ["FB_BackwashGraph_Sfc", "FB_BackwashGraph"]
    sfc = pous["FB_BackwashGraph_Sfc"].find(f"{Q}body/{Q}SFC")
    assert sfc is not None
    steps = {s.get("name"): s.get("initialStep") for s in sfc.iter(f"{Q}step")}
    assert steps == {
        n: ("true" if n == "Idle" else None) for n in ("Idle", "Drain", "Air", "Rinse", "QuickRinse", "Refill")
    }
    assert len(list(sfc.iter(f"{Q}transition"))) == 6
    exprs = [e.text or "" for e in sfc.iter(f"{Q}expression")]
    assert "(xLevelLow AND NOT xShortWash) AND NOT Drain_SvErr" in exprs
    assert "Air.t >= T#10S" in exprs
    assert "<inline" not in xml  # CODESYS 3.5.17.30 пропускает inline-условия при импорте
    qualifiers = {(a.get("qualifier"), a.get("duration")) for a in sfc.iter(f"{Q}action")}
    assert {("N", None), ("D", "T#2S"), ("P", None)} <= qualifiers
    assert [j.get("targetName") for j in sfc.iter(f"{Q}jumpStep")] == ["Idle"]
    assert {e.tag.removeprefix(Q) for e in sfc} >= {"selectionDivergence", "simultaneousDivergence"}
    assert 'Init Declare="false" Use="true"' in xml
    wrapper = "".join(pous["FB_BackwashGraph"].itertext())
    for fragment in (
        "fbSfc(SFCInit := INIT_SQ",
        "xReady := (fbSfc.xIdle_N1 OR INIT_SQ);",
        "xDrainValve := (fbSfc.xDrain_N1 AND NOT INIT_SQ);",
        "IF ACK_EF OR INIT_SQ THEN",
        "ERR_FLT := Drain_SvErr;",
        "xValvesBusy := xDrainValve OR xInletValve;",
    ):
        assert fragment in wrapper, fragment


@pytest.mark.parametrize(
    ("breaker", "pre", "reason"),
    [
        (None, True, "предоперации"),
        (B.GAction("N", "#xA := TRUE;", event="S0"), False, "событие S0"),
        (B.GAction("N", "#xA := NOT #xA;"), False, "инструкция без события"),
    ],
)
def test_sfc_variant_is_skipped_with_reason(tmp_path: Path, breaker: B.GAction | None, pre: bool, reason: str) -> None:
    """Что SFC не выражает, не подменяется: блок остаётся ST-двойником, причина — в предупреждении."""
    path = tmp_path / "FB_AltPriority.xml"
    path.write_text(B.render(priority_block(breaker, pre)), encoding="utf-8")
    out = graph_sfc([path])
    assert out.files == {}
    assert reason in out.skipped["FB_AltPriority"]
    with pytest.raises(SfcError):
        sfc_project(xblock(priority_block(breaker, pre)), "x.xml")


def test_step_time_limit_is_todo_not_silently_dropped(tmp_path: Path) -> None:
    """MaximumStepTime не переводится: у шага MIGRATION-TODO, вариант SFC не строится."""
    blk = priority_block(limit="T#5S")
    doc = parse_document(B.render(blk), "FB_AltPriority.xml")
    _text, low, _ = lower_document(doc, {b.name.lower(): b for b in doc.blocks}, LowerOptions())
    step = next(u for u in low.units if u.kind == "step" and u.trace.endswith("шаг S2"))
    assert (step.status, step.rule) == ("todo", "graph.step_time_limits")
    path = tmp_path / "FB_AltPriority.xml"
    path.write_text(B.render(blk), encoding="utf-8")
    assert "предел времени шага (S2)" in graph_sfc([path]).skipped["FB_AltPriority"]


def test_build_corpus_writes_sfc_variant_into_managed_folder() -> None:
    built = C.build(REPO_ROOT)
    rel = f"{C.LANG_PLCOPEN_REL}/FB_BackwashGraph.xml"
    assert built.lang_files[rel] == sfc_project(xblock(), "samples/lang/FB_BackwashGraph.xml").xml
    assert C.LANG_PLCOPEN_REL in built.managed
    assert [k for k in built.lang_files if k.startswith("plcopen/")] == [rel]


def test_convert_cli_writes_plcopen(tmp_path: Path) -> None:
    out, plc = tmp_path / "out", tmp_path / "plc"
    args = ["convert", str(LANG / "FB_BackwashGraph.xml"), "--out", str(out), "--plcopen", str(plc), "-q"]
    assert main(args) == EXIT_OK
    assert (plc / "FB_BackwashGraph.xml").read_text(encoding="utf-8").startswith('<?xml version="1.0"')
    assert (out / "src" / "POUs" / "FB_BackwashGraph" / "FB_BackwashGraph.impl.st").is_file()


def test_ir_dump_shows_sequence_and_topology() -> None:
    """`s7conv ir` для сети GRAPH: шаги с действиями, переходы, ветви, связи и топология переходов."""
    from s7conv import irdump

    (doc,) = irdump.dump([LANG / "FB_BackwashGraph.xml"])
    (net,) = doc["blocks"][0]["networks"]
    assert (net["kind"], net["post_operations"], net["pre_operations"]) == ("Graph", 1, 0)
    (seq,) = net["sequences"]
    assert [s["name"] for s in seq["steps"]] == ["Idle", "Drain", "Air", "Rinse", "QuickRinse", "Refill"]
    assert seq["steps"][1]["supervision"] and seq["steps"][3]["interlock"]
    assert seq["steps"][2]["actions"][1] == {
        "qualifier": "D",
        "event": "",
        "interlock": False,
        "operand": "#xAirValve",
        "text": "#xAirValve,T#2S",
        "time": "T#2S",
    }
    links = {k["number"]: (k["preds"], k["succs"], k["priority"]) for k in seq["links"]}
    assert links[2] == ([2], [3, 4], 0) and links[3] == ([2], [5], 1) and links[4] == ([3, 4], [6], 0)
    assert any(c["link"] == "Jump" for c in seq["connections"]) and seq["issues"] == []
