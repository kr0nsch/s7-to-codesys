"""SimaticML → понижение LAD/FBD/STL/SCL → ST: разбор, правила M3/M4, трасса, пометки."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from s7conv import pipeline as P
from s7conv.emitter import Options, convert
from s7conv.frontends.simaticml import SimaticMLError, parse_document
from s7conv.lower.block import LowerOptions, lower_document
from s7conv.symbols import Project
from s7conv.tests.conftest import REPO_ROOT

LANG = REPO_ROOT / "samples" / "lang"
SAMPLES = str(LANG)
sys.path.insert(0, SAMPLES)
import blocks as corpus  # noqa: E402  samples/lang/blocks.py
import build_xml as B  # noqa: E402  samples/lang/build_xml.py

sys.path.remove(SAMPLES)


def lower(*blocks: B.Block, cpu: str | None = None, jumps: str = "structured") -> str:
    docs = [parse_document(B.render(b), f"{b.name}.xml") for b in blocks]
    registry = {blk.name.lower(): blk for d in docs for blk in d.blocks}
    return "\n".join(lower_document(d, registry, LowerOptions(cpu=cpu, stl_jumps=jumps))[0] for d in docs)


def body(text: str, block: str | None = None) -> list[str]:
    if block is not None:
        text = text[text.index(f'"{block}"') :]
    start = text.index("BEGIN") + len("BEGIN")
    end = text.index("END_FUNCTION")
    return [ln.strip() for ln in text[start:end].splitlines() if ln.strip() and not ln.strip().startswith("//")]


def st_body(*blocks: B.Block, name: str, timers: str = "standard", jumps: str = "structured") -> list[str]:
    files = []
    for b in blocks:
        path = Path(f"{b.name}.xml")
        doc = parse_document(B.render(b), str(path))
        registry = {blk.name.lower(): blk for blk in doc.blocks}
        text, lowering, _ = lower_document(doc, registry, LowerOptions(stl_jumps=jumps))
        from s7conv.parser import parse_source

        sf = parse_source(text, str(path))
        sf.lowering = lowering
        files.append(sf)
    result = convert(files, Project(), Options(timers=timers))
    obj = next(o for o in result.objects if o.name == name)
    assert obj.impl is not None
    return [ln.strip() for ln in obj.impl.splitlines() if ln.strip() and not ln.strip().startswith("//")]


def fb(name: str, units: list[B.Unit], members: list[B.Member], lang: str = "LAD") -> B.Block:
    return B.Block("FB", name, 1, lang=lang, sections=[B.Section("Static", members)], units=units)


BOOLS = [B.Member(n, "Bool") for n in ("a", "b", "c", "q", "m", "s", "r")]
INTS = [B.Member(n, "Int") for n in ("i1", "i2", "iOut")]


# ---------------------------------------------------------------------------
# Разбор SimaticML
# ---------------------------------------------------------------------------


def test_document_header_interface_and_units() -> None:
    doc = parse_document((LANG / "FB_StarterLad.xml").read_text(encoding="utf-8"), "FB_StarterLad.xml")
    blk = doc.blocks[0]
    assert (blk.kind, blk.name, blk.number, blk.lang, blk.memory_layout) == (
        "FB",
        "FB_StarterLad",
        101,
        "LAD",
        "Optimized",
    )
    assert [s.name for s in blk.sections][:2] == ["Input", "Output"]
    assert blk.member_type("tFeedbackTime") == "Time"
    assert len(blk.units) == 4 and blk.units[0].body_kind == "FlgNet"
    assert {"Interface/v5", "NetworkSource/FlgNet/v5"} <= doc.namespaces
    assert doc.engineering == "V21"


def test_doctype_and_entities_are_rejected() -> None:
    with pytest.raises(SimaticMLError, match="DOCTYPE"):
        parse_document('<!DOCTYPE x [<!ENTITY e "boom">]><Document>&e;</Document>', "evil.xml")


def test_broken_xml_becomes_raw_block_not_crash(tmp_path: Path) -> None:
    bad = tmp_path / "bad.xml"
    bad.write_text("<Document><SW.Blocks.FB>", encoding="utf-8")
    files = P.parse_xml([bad])
    assert files[0].issues and files[0].blocks[0].reason  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# LAD/FBD (M3)
# ---------------------------------------------------------------------------


def test_series_and_branches_give_and_or() -> None:
    n = B.Net("x")
    n.coil(n.contact(n.orr(n.contact("rail", "#a"), n.contact("rail", "#b")), "#c", neg=True), "#q")
    assert body(lower(fb("FB_X", [B.lad_unit(n)], BOOLS))) == ["#q := (#a OR #b) AND NOT #c;"]


def test_set_reset_coils_and_negated_coil() -> None:
    n = B.Net("x")
    n.coil(n.contact("rail", "#a"), "#q", "SCoil")
    n2 = B.Net("y")
    n2.coil(n2.contact("rail", "#b"), "#q", "RCoil")
    assert body(lower(fb("FB_X", [B.lad_unit(n), B.lad_unit(n2)], BOOLS))) == [
        "IF #a THEN",
        "#q := TRUE;",
        "END_IF;",
        "IF #b THEN",
        "#q := FALSE;",
        "END_IF;",
    ]


@pytest.mark.parametrize(("kind", "first", "second"), [("SR", "TRUE", "FALSE"), ("RS", "FALSE", "TRUE")])
def test_flipflop_with_operand_keeps_s7_order(kind: str, first: str, second: str) -> None:
    """SR — сначала S, потом R1 (сброс главнее); RS — сначала R, потом S1 (установка главнее)."""
    n = B.Net("x")
    ff = n.part(kind)
    pins = ("s", "r1") if kind == "SR" else ("r", "s1")
    n.wire(n.contact("rail", "#a"), (ff, pins[0]))
    n.wire(n.contact("rail", "#b"), (ff, pins[1]))
    n.operand_in(ff, "operand", "#m")
    n.coil((ff, "q"), "#q")
    assert body(lower(fb("FB_X", [B.lad_unit(n)], BOOLS))) == [
        "IF #a THEN",
        f"#m := {first};",
        "END_IF;",
        "IF #b THEN",
        f"#m := {second};",
        "END_IF;",
        "#q := #m;",
    ]


def test_pbox_uses_explicit_memory_bit() -> None:
    n = B.Net("x")
    p = n.part("PBox")
    n.wire(n.contact("rail", "#a"), (p, "in"))
    n.operand_in(p, "bit", "#m")
    n.coil((p, "out"), "#q")
    assert body(lower(fb("FB_X", [B.lad_unit(n)], BOOLS))) == [
        "#xNet1_1 := #a AND NOT #m;",
        "#m := #a;",
        "#q := #xNet1_1;",
    ]


def test_edge_memory_in_temp_is_flagged() -> None:
    n = B.Net("x")
    p = n.part("PBox")
    n.wire(n.contact("rail", "#a"), (p, "in"))
    n.operand_in(p, "bit", "#tmpBit")
    n.coil((p, "out"), "#q")
    blk = B.Block(
        "FB",
        "FB_X",
        1,
        sections=[B.Section("Static", BOOLS), B.Section("Temp", [B.Member("tmpBit", "Bool")])],
        units=[B.lad_unit(n)],
    )
    assert "lad.edge_memory" in lower_rules(blk)


def lower_rules(*blocks: B.Block) -> set[str]:
    docs = [parse_document(B.render(b), f"{b.name}.xml") for b in blocks]
    registry = {blk.name.lower(): blk for d in docs for blk in d.blocks}
    rules: set[str] = set()
    for d in docs:
        _text, low, _ = lower_document(d, registry, LowerOptions())
        rules |= {n.rule for notes in low.notes.values() for n in notes}
        rules |= {u.rule for u in low.units if u.status != "auto"}
    return rules


def test_compare_with_pre_and_move_with_en() -> None:
    n = B.Net("x")
    gt = n.part("Gt")
    n.wire(n.contact("rail", "#a"), (gt, "pre"))
    n.operand_in(gt, "in1", "#i1")
    n.operand_in(gt, "in2", "#i2")
    mv = n.part("Move", disabled_eno=True, templates=[("Card", "Cardinality", "1")])
    n.wire((gt, "out"), (mv, "en"))
    n.operand_in(mv, "in", "#i1")
    n.operand_out(mv, "out1", "#iOut")
    assert body(lower(fb("FB_X", [B.lad_unit(n)], BOOLS + INTS))) == [
        "IF #a AND (#i1 > #i2) THEN",
        "#iOut := #i1;",
        "END_IF;",
    ]


def test_add_with_connected_eno_uses_s7compat_before_write() -> None:
    n = B.Net("x")
    add = n.part("Add", templates=[("SrcType", "Type", "Int"), ("Card", "Cardinality", "2")])
    n.wire(n.contact("rail", "#a"), (add, "en"))
    n.operand_in(add, "in1", "#iOut")
    n.operand_in(add, "in2", "1")
    n.operand_out(add, "out", "#iOut")
    n.coil((add, "eno"), "#q")
    lines = body(lower(fb("FB_X", [B.lad_unit(n)], BOOLS + INTS)))
    assert lines == [
        "#xNet1_1 := #a AND F_S7EnoAddInt(#iOut, 1);",
        "IF #a THEN",
        "#iOut := #iOut + 1;",
        "END_IF;",
        "#q := #xNet1_1;",
    ]


def test_call_chain_eno_equals_en_for_plain_lad_callee() -> None:
    callee = B.Block(
        "FC",
        "FC_Plain",
        2,
        sections=[B.Section("Input", [B.Member("iIn", "Int")]), B.Section("Return", [B.Member("Ret_Val", "Int")])],
        units=[],
    )
    n = B.Net("x")
    params = [("iIn", "Input", "Int"), ("Ret_Val", "Return", "Int")]
    c1 = n.part("Call", call={"name": "FC_Plain", "type": "FC", "params": params})
    n.wire(n.contact("rail", "#a"), (c1, "en"))
    n.operand_in(c1, "iIn", "#i1")
    n.operand_out(c1, "Ret_Val", "#i2")
    c2 = n.part("Call", call={"name": "FC_Plain", "type": "FC", "params": params})
    n.wire((c1, "eno"), (c2, "en"))
    n.operand_in(c2, "iIn", "#i2")
    n.operand_out(c2, "Ret_Val", "#iOut")
    n.coil((c2, "eno"), "#q")
    blk = fb("FB_X", [B.lad_unit(n)], BOOLS + INTS)
    assert body(lower(callee, blk), "FB_X")[-7:] == [
        "IF #a THEN",
        '#i2 := "FC_Plain"(iIn := #i1);',
        "END_IF;",
        "IF #a THEN",
        '#iOut := "FC_Plain"(iIn := #i2);',
        "END_IF;",
        "#q := #a;",
    ]
    assert "lad.call_eno" not in lower_rules(callee, blk)


def test_forward_jump_over_networks_becomes_if() -> None:
    j = B.Net("jump")
    jmp = j.part("Jump")
    j.wire(j.contact("rail", "#a"), (jmp, "in"))
    j.operand_in(jmp, "operand", "label:L1")
    n2 = B.Net("skipped")
    n2.coil(n2.contact("rail", "#b"), "#q")
    n3 = B.Net("target")
    n3.labels.append("L1")
    n3.coil(n3.contact("rail", "#c"), "#m")
    assert body(lower(fb("FB_X", [B.lad_unit(x) for x in (j, n2, n3)], BOOLS))) == [
        "#xNet1_1 := #a;",
        "IF NOT #xNet1_1 THEN // прыжок к L1: сети 2–2 выполняются без прыжка",
        "#q := #b;",
        "END_IF;",
        "#m := #c;",
    ]


def test_unknown_part_is_todo_with_uid() -> None:
    n = B.Net("x")
    weird = n.part("FancyBox")
    n.wire(n.contact("rail", "#a"), (weird, "in"))
    blk = fb("FB_X", [B.lad_unit(n)], BOOLS)
    assert "lad.unknown_part" in lower_rules(blk)
    text = lower(blk)
    assert '"FancyBox"(in := #a);' in text


def test_unverified_vocabulary_is_at_most_check() -> None:
    """Элемент уровня L (форма XML не подтверждена экспортом) не может быть «автоматически»."""
    n = B.Net("x", lang="FBD")
    n.coil(n.gate("A", "#a", "#b"), "#q")
    assert "fbd.vocab_unverified" in lower_rules(fb("FB_X", [B.lad_unit(n)], BOOLS, lang="FBD"))


# ---------------------------------------------------------------------------
# STL (M4)
# ---------------------------------------------------------------------------


def stl_fb(*stls: B.Stl, members: list[B.Member] | None = None, layout: str = "Standard") -> B.Block:
    return B.Block(
        "FB",
        "FB_S",
        1,
        lang="STL",
        layout=layout,
        sections=[B.Section("Static", members or (BOOLS + INTS))],
        units=[B.stl_unit(s) for s in stls],
    )


def test_stl_and_before_or_and_brackets() -> None:
    s = B.Stl("x")
    s.op("A", "#a").op("O", "#b").op("A", "#c").op("Assign", "#q")
    s.op("A_BRACK").op("O", "#a").op("O", "#b").op("BRACKET").op("A", "#c").op("Assign", "#m")
    s.op("A", "#a").op("A", "#b").op("O").op("A", "#c").op("AN", "#q").op("Assign", "#r")
    assert body(lower(stl_fb(s))) == [
        "#q := #a OR #b AND #c;",
        "#m := (#a OR #b) AND #c;",
        "#r := #a AND #b OR #c AND NOT #q;",
    ]


def test_stl_reused_rlo_is_frozen_before_write() -> None:
    s = B.Stl("x")
    s.op("A", "#a").op("AN", "#q").op("Assign", "#q").op("Assign", "#m")
    assert body(lower(stl_fb(s))) == ["#xRlo1_1 := #a AND NOT #q;", "#q := #xRlo1_1;", "#m := #xRlo1_1;"]


def test_stl_load_transfer_and_int_arithmetic() -> None:
    s = B.Stl("x")
    s.op("L", "#i1").op("L", "#i2").op("ADD_I").op("T", "#iOut")
    s.op("L", "#i1").op("L", "#i2").op("SUB_I").op("T", "#i1")
    assert body(lower(stl_fb(s))) == ["#iOut := #i1 + #i2;", "#i1 := #i1 - #i2;"]


def test_stl_compare_is_first_check() -> None:
    s = B.Stl("x")
    s.op("A", "#a").op("L", "#i1").op("L", "#i2").op("GT_I").op("A", "#b").op("Assign", "#q")
    assert body(lower(stl_fb(s))) == ["#q := (#i1 > #i2) AND #b;"]


def test_stl_zero_extension_is_check() -> None:
    members = [B.Member("w", "Word"), B.Member("di", "DInt")]
    s = B.Stl("x").op("L", "#w").op("T", "#di")
    assert body(lower(stl_fb(s, members=members))) == ["#di := WORD_TO_DINT(#w);"]
    assert "stl.zero_extend" in lower_rules(stl_fb(s, members=members))


def test_stl_fp_jcn_label_becomes_if_without_jmp() -> None:
    s = B.Stl("x")
    s.op("A", "#a").op("Rise", "#m").op("JCN", "label:M1").op("L", "#iOut").op("L", "1").op("ADD_I")
    s.op("T", "#iOut").op("NOP_0", label="M1")
    lines = body(lower(stl_fb(s)))
    assert lines == [
        "#xEdge1_1 := #a AND NOT #m;",
        "#m := #a;",
        "IF #xEdge1_1 THEN // JCN M1",
        "#iOut := #iOut + 1;",
        "END_IF;",
    ]
    assert not any("JMP" in ln for ln in lines)


def test_stl_if_else_pattern() -> None:
    s = B.Stl("x")
    s.op("A", "#a").op("JCN", "label:ELSE").op("SET").op("Assign", "#q").op("JU", "label:END")
    s.op("CLR", label="ELSE").op("Assign", "#q").op("NOP_0", label="END")
    assert body(lower(stl_fb(s))) == ["IF #a THEN // JCN ELSE", "#q := TRUE;", "ELSE", "#q := FALSE;", "END_IF;"]


def test_stl_pc_mode_is_case_in_while() -> None:
    s = B.Stl("x")
    s.op("A", "#a").op("JCN", "label:M1").op("SET").op("Assign", "#q").op("NOP_0", label="M1")
    lines = body(lower(stl_fb(s), jumps="pc"))
    assert lines[:4] == ["#iStlPc := 0;", "#xStlRun := TRUE;", "WHILE #xStlRun DO", "CASE #iStlPc OF"]
    assert "stl.jump_pc" in {n.rule for n in _notes(stl_fb(s), "pc")}


def _notes(blk: B.Block, jumps: str) -> list:  # type: ignore[type-arg]
    doc = parse_document(B.render(blk), "x.xml")
    _t, low, _ = lower_document(doc, {b.name.lower(): b for b in doc.blocks}, LowerOptions(stl_jumps=jumps))
    return [n for notes in low.notes.values() for n in notes]


def test_stl_backward_jump_falls_back_to_pc() -> None:
    s = B.Stl("x")
    s.op("L", "#i1", label="TOP").op("L", "1").op("ADD_I").op("T", "#i1").op("A", "#a").op("JC", "label:TOP")
    assert "CASE #iStlPc OF" in body(lower(stl_fb(s)))


def test_stl_mode_b_instructions_are_todo_until_p1() -> None:
    s = B.Stl("x").op("A", "OV").op("Assign", "#q")
    assert "stl.mode_b" in lower_rules(stl_fb(s))


def test_stl_profile_from_memory_layout_and_mismatch_warning() -> None:
    s = B.Stl("x").op("A", "#a").op("Assign", "#q")
    assert "xml.profile_mismatch" in {n.rule for n in _notes_cpu(stl_fb(s, layout="Optimized"), "s7-300")}
    assert not _notes_cpu(stl_fb(s, layout="Standard"), "s7-300")


def _notes_cpu(blk: B.Block, cpu: str) -> list:  # type: ignore[type-arg]
    doc = parse_document(B.render(blk), "x.xml")
    _t, low, _ = lower_document(doc, {b.name.lower(): b for b in doc.blocks}, LowerOptions(cpu=cpu))
    return [n for notes in low.notes.values() for n in notes]


# ---------------------------------------------------------------------------
# Сквозь эмиттер: ST, трасса в пометках
# ---------------------------------------------------------------------------


def test_note_in_st_points_to_network_and_uid() -> None:
    n = B.Net("x")
    p = n.part("PBox")
    n.wire(n.contact("rail", "#a"), (p, "in"))
    n.operand_in(p, "bit", "#tmpBit")
    n.coil((p, "out"), "#q")
    blk = B.Block(
        "FB",
        "FB_Trace",
        1,
        sections=[B.Section("Static", BOOLS), B.Section("Temp", [B.Member("tmpBit", "Bool")])],
        units=[B.lad_unit(n)],
    )
    path = Path("FB_Trace.xml")
    doc = parse_document(B.render(blk), str(path))
    text, lowering, _ = lower_document(doc, {b.name.lower(): b for b in doc.blocks}, LowerOptions())
    from s7conv.parser import parse_source

    sf = parse_source(text, str(path))
    sf.lowering = lowering
    result = convert([sf], Project(), Options())
    impl = next(o for o in result.objects if o.name == "FB_Trace").impl or ""
    assert "(FB_Trace.xml, сеть 1, UId 21)" in impl


def test_scl_network_from_xml_gives_same_st_as_scl_source() -> None:
    """FB_StarterScl: сеть SCL из SimaticML и тот же текст в .scl дают одно тело ST."""
    xml_lines = st_body(corpus.starter_scl(), name="FB_StarterScl")
    from s7conv.tests.conftest import convert_texts

    decls = (
        "VAR_INPUT\n xStart : Bool; xStop : Bool; xInterlock : Bool := TRUE; xFeedback : Bool;"
        " tFeedbackTime : Time := T#2S; xReset : Bool;\nEND_VAR\nVAR_OUTPUT\n xRun : Bool; xFault : Bool;"
        " iStarts : Int;\nEND_VAR\nVAR\n xRunMem : Bool; xEdgeMem : Bool; tonFeedback : TON_TIME;\nEND_VAR"
    )
    src = f'FUNCTION_BLOCK "FB_StarterScl"\nVERSION : 0.1\n{decls}\nBEGIN\n{corpus.STARTER_SCL}\nEND_FUNCTION_BLOCK\n'
    scl = convert_texts({"FB_StarterScl.scl": src})
    assert xml_lines == scl.code("FB_StarterScl")


def test_corpus_xml_is_reproducible(capsys: pytest.CaptureFixture[str]) -> None:
    assert B.main(["--check"]) == 0, capsys.readouterr().out


def test_limit_counter_return_and_calculate_boxes() -> None:
    n = B.Net("limit")
    lim = n.part("Limit")
    n.wire("rail", (lim, "en"))
    n.operand_in(lim, "mn", "0")
    n.operand_in(lim, "in", "#i1")
    n.operand_in(lim, "mx", "100")
    n.operand_out(lim, "out", "#iOut")
    c = B.Net("ctu")
    ctu = c.part("CTU", instance="#ctuCount")
    c.wire(c.contact("rail", "#a"), (ctu, "CU"))
    c.operand_in(ctu, "R", "#b")
    c.operand_in(ctu, "PV", "10")
    c.coil((ctu, "Q"), "#q")
    calc = B.Net("calc")
    cl = calc.part("Calculate", equation="IN1 + IN2 * 2")
    calc.wire("rail", (cl, "en"))
    calc.operand_in(cl, "in1", "#i1")
    calc.operand_in(cl, "in2", "#i2")
    calc.operand_out(cl, "out", "#iOut")
    r = B.Net("ret")
    ret = r.part("Return")
    r.wire(r.contact("rail", "#c"), (ret, "in"))
    members = BOOLS + INTS + [B.Member("ctuCount", "CTU_INT")]
    lines = body(lower(fb("FB_X", [B.lad_unit(x) for x in (n, c, calc, r)], members)))
    assert lines == [
        "#iOut := LIMIT(MN := 0, IN := #i1, MX := 100);",
        "#ctuCount(CU := #a, R := #b, PV := 10);",
        "#q := #ctuCount.Q;",
        "#iOut := #i1 + #i2 * 2;",
        "IF #c THEN",
        "RETURN;",
        "END_IF;",
    ]


def test_stl_block_end_instructions() -> None:
    s = B.Stl("x").op("A", "#a").op("BEC").op("SET").op("Assign", "#q").op("BEU").op("CLR").op("Assign", "#q")
    assert body(lower(stl_fb(s))) == ["IF #a THEN", "RETURN;", "END_IF;", "#q := TRUE;", "RETURN;", "#q := FALSE;"]


def test_stl_int_arithmetic_on_dint_reads_low_word_only() -> None:
    members = [B.Member("di", "DInt"), B.Member("i", "Int")]
    s = B.Stl("x").op("L", "#di").op("L", "#i").op("ADD_I").op("T", "#i")
    assert "stl.accu_high" in lower_rules(stl_fb(s, members=members))


def test_stl_edge_memory_in_temp_is_flagged() -> None:
    s = B.Stl("x").op("A", "#a").op("Rise", "#tmpBit").op("Assign", "#q")
    blk = B.Block(
        "FB",
        "FB_S",
        1,
        lang="STL",
        layout="Standard",
        sections=[B.Section("Static", BOOLS), B.Section("Temp", [B.Member("tmpBit", "Bool")])],
        units=[B.stl_unit(s)],
    )
    assert "stl.edge_memory" in lower_rules(blk)


def test_stl_dint_real_arithmetic_and_compare() -> None:
    members = [B.Member(n, "DInt") for n in ("d1", "d2", "dOut")] + [B.Member(n, "Real") for n in ("r1", "r2", "rOut")]
    members += [B.Member("q", "Bool")]
    s = B.Stl("x")
    s.op("L", "#d1").op("L", "#d2").op("MUL_D").op("T", "#dOut")
    s.op("L", "#r1").op("L", "#r2").op("DIV_R").op("T", "#rOut")
    s.op("L", "#d1").op("L", "#d2").op("MOD_D").op("T", "#dOut")
    s.op("L", "#r1").op("L", "#r2").op("GE_R").op("Assign", "#q")
    assert body(lower(stl_fb(s, members=members))) == [
        "#dOut := #d1 * #d2;",
        "#rOut := #r1 / #r2;",
        "#dOut := #d1 MOD #d2;",
        "#q := #r1 >= #r2;",
    ]
