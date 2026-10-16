"""Разборщик: блоки TIA, секции, все операторы и формы выражений, приоритеты, восстановление после ошибок."""

from __future__ import annotations

import pytest

from s7conv.nodes import (
    AddressRef,
    Arg,
    ArrayInit,
    ArrayType,
    Assign,
    Binary,
    Block,
    Call,
    CallStmt,
    Case,
    CaseRange,
    CommentStmt,
    Continue,
    Empty,
    Exit,
    For,
    GlobalRef,
    Goto,
    Ident,
    If,
    Index,
    Label,
    Literal,
    LocalRef,
    Member,
    NamedType,
    Pragma,
    RawBlock,
    RawDecl,
    RawStmt,
    RefType,
    Region,
    Repeat,
    Return,
    Slice,
    StringType,
    StructType,
    Unary,
    VarDecl,
    While,
)
from s7conv.parser import ParseError, parse_expression, parse_source, parse_statements

# ---------------------------------------------------------------------------
# Выражения
# ---------------------------------------------------------------------------


def lit(text: str, kind: str = "int") -> Literal:
    return Literal(kind, text)


def test_precedence_mul_over_add() -> None:
    assert parse_expression("#a + #b * 2") == Binary("+", LocalRef("a"), Binary("*", LocalRef("b"), lit("2")))


def test_left_associativity() -> None:
    assert parse_expression("1 - 2 - 3") == Binary("-", Binary("-", lit("1"), lit("2")), lit("3"))


def test_power_binds_tighter_than_unary_minus() -> None:
    assert parse_expression("-2 ** 2") == Unary("-", Binary("**", lit("2"), lit("2")))


def test_power_with_signed_exponent() -> None:
    assert parse_expression("2 ** -1") == Binary("**", lit("2"), Unary("-", lit("1")))


def test_not_binds_tighter_than_and() -> None:
    assert parse_expression("NOT #a AND #b") == Binary("AND", Unary("NOT", LocalRef("a")), LocalRef("b"))


def test_logical_precedence_and_xor_or() -> None:
    expr = parse_expression("#a OR #b XOR #c AND #d")
    assert expr == Binary(
        "OR", LocalRef("a"), Binary("XOR", LocalRef("b"), Binary("AND", LocalRef("c"), LocalRef("d")))
    )


def test_ampersand_is_and_level() -> None:
    assert parse_expression("#a & #b OR #c") == Binary("OR", Binary("&", LocalRef("a"), LocalRef("b")), LocalRef("c"))


def test_comparison_levels() -> None:
    expr = parse_expression("#a < #b = #c >= #d")
    assert expr == Binary("=", Binary("<", LocalRef("a"), LocalRef("b")), Binary(">=", LocalRef("c"), LocalRef("d")))


def test_mod_is_multiplicative() -> None:
    assert parse_expression("#i MOD 3 + 1") == Binary("+", Binary("MOD", LocalRef("i"), lit("3")), lit("1"))


def test_parentheses_override() -> None:
    assert parse_expression("(#a + #b) * 2") == Binary("*", Binary("+", LocalRef("a"), LocalRef("b")), lit("2"))


@pytest.mark.parametrize(
    ("text", "kind"),
    [
        ("TRUE", "bool"),
        ("false", "bool"),
        ("42", "int"),
        ("3.14", "real"),
        ("'txt'", "string"),
        ("T#5s", "typed"),
        ("S5T#2s", "typed"),
        ("16#FF", "typed"),
        ("INT#-5", "typed"),
        ("DT#2024-01-31-12:30:00", "typed"),
    ],
)
def test_literals(text: str, kind: str) -> None:
    assert parse_expression(text) == Literal(kind, text)


def test_access_chain_member_index_slice() -> None:
    expr = parse_expression('"DB_Hmi".pump[#i + 1].startReq.%X0')
    assert expr == Slice(
        Member(Index(Member(GlobalRef("DB_Hmi"), "pump"), (Binary("+", LocalRef("i"), lit("1")),)), "startReq"),
        "X",
        0,
    )


def test_multi_dim_index_and_quoted_member() -> None:
    assert parse_expression('#m[1, 2]."a b"') == Member(Index(LocalRef("m"), (lit("1"), lit("2"))), "a b", quoted=True)


def test_codesys_style_bit_access_is_slice() -> None:
    assert parse_expression("#w.3") == Slice(LocalRef("w"), "", 3)


def test_address_and_slice_on_address() -> None:
    assert parse_expression("%MW10.%X3") == Slice(AddressRef("%MW10"), "X", 3)


def test_named_and_output_arguments() -> None:
    expr = parse_expression("#tmr(IN := #run, PT := T#5s, ET => #elapsed)")
    assert expr == Call(
        LocalRef("tmr"),
        (Arg("IN", LocalRef("run")), Arg("PT", Literal("typed", "T#5s")), Arg("ET", LocalRef("elapsed"), True)),
    )


def test_positional_and_empty_calls() -> None:
    assert parse_expression("ABS(#x)") == Call(Ident("ABS"), (Arg(None, LocalRef("x")),))
    assert parse_expression('"Level_DB"()') == Call(GlobalRef("Level_DB"), ())


def test_generic_instance_method_call() -> None:
    expr = parse_expression('"Delay_DB".TON(IN := TRUE, PT := T#1s)')
    assert isinstance(expr, Call) and expr.callee == Member(GlobalRef("Delay_DB"), "TON")


@pytest.mark.parametrize("text", ["#a +", "(#a", "#a.", "#a[1", "THEN", "#a #b"])
def test_expression_errors(text: str) -> None:
    with pytest.raises(ParseError):
        parse_expression(text)


# ---------------------------------------------------------------------------
# Операторы
# ---------------------------------------------------------------------------


def one(text: str) -> object:
    body, issues = parse_statements(text)
    assert not issues, issues
    stmts = [s for s in body if not isinstance(s, CommentStmt)]
    assert len(stmts) == 1, stmts
    return stmts[0]


def test_assignment_and_compound_assignment() -> None:
    s = one("#a := #b;")
    assert isinstance(s, Assign) and s.op == ":=" and s.target == LocalRef("a")
    s = one("#count += 1;")
    assert isinstance(s, Assign) and s.op == "+="


def test_call_statement() -> None:
    s = one('"Motor1_DB"(start := TRUE);')
    assert isinstance(s, CallStmt) and s.call.callee == GlobalRef("Motor1_DB")


def test_if_elsif_else() -> None:
    s = one("IF #a THEN #x := 1; ELSIF #b THEN #x := 2; ELSIF #c THEN ; ELSE #x := 3; END_IF;")
    assert isinstance(s, If)
    assert [c for c, _ in s.branches] == [LocalRef("a"), LocalRef("b"), LocalRef("c")]
    assert isinstance(s.branches[2][1][0], Empty)
    assert s.else_body is not None and isinstance(s.else_body[0], Assign)


def test_case_with_lists_ranges_and_else() -> None:
    s = one(
        "CASE #step OF\n 0: #a := 1;\n 1, 3: #a := 2;\n 4..6, 10: #a := 3; #b := 4;\n -1: ;\nELSE\n #a := 0;\nEND_CASE;"
    )
    assert isinstance(s, Case)
    assert [c.labels for c in s.clauses] == [
        [lit("0")],
        [lit("1"), lit("3")],
        [CaseRange(lit("4"), lit("6")), lit("10")],
        [Unary("-", lit("1"))],
    ]
    assert len(s.clauses[2].body) == 2
    assert s.else_body is not None


def test_case_label_with_constant_and_else_colon() -> None:
    s = one("CASE #mode OF #MODE_AUTO: #x := 1; ELSE: #x := 2; END_CASE;")
    assert isinstance(s, Case) and s.clauses[0].labels == [LocalRef("MODE_AUTO")]


def test_for_with_and_without_by() -> None:
    s = one("FOR #i := 0 TO 9 BY 2 DO #a[#i] := 0; END_FOR;")
    assert isinstance(s, For) and s.step == lit("2")
    s = one("FOR #i := #n TO 1 DO EXIT; END_FOR;")
    assert isinstance(s, For) and s.step is None and isinstance(s.body[0], Exit)


def test_while_repeat_continue_return() -> None:
    s = one("WHILE #i < 10 DO #i += 1; CONTINUE; END_WHILE;")
    assert isinstance(s, While) and isinstance(s.body[1], Continue)
    s = one("REPEAT #i := #i - 1; UNTIL #i <= 0 END_REPEAT;")
    assert isinstance(s, Repeat) and s.cond == Binary("<=", LocalRef("i"), lit("0"))
    assert isinstance(one("RETURN;"), Return)


def test_repeat_until_with_semicolon() -> None:
    s = one("REPEAT #i := 1; UNTIL TRUE; END_REPEAT;")
    assert isinstance(s, Repeat)


def test_region_goto_label_pragma_empty() -> None:
    s = one("REGION Start logic\n #a := 1;\nEND_REGION")
    assert isinstance(s, Region) and s.name == "Start logic" and len(s.body) == 1
    assert isinstance(one("GOTO lblExit;"), Goto)
    assert isinstance(one("lblExit:"), Label)
    assert isinstance(one("{ some pragma }"), Pragma)
    assert isinstance(one(";"), Empty)


def test_missing_semicolon_before_end_is_tolerated() -> None:
    s = one("IF #a THEN #x := 1 END_IF;")
    assert isinstance(s, If)


def test_statement_recovery_keeps_following_statements() -> None:
    body, issues = parse_statements("#a := ;\n#b := 2;\nIF #c THEN #d := := 1; END_IF;\n#e := 3;")
    kinds = [type(s).__name__ for s in body]
    assert kinds == ["RawStmt", "Assign", "If", "Assign"]
    assert len(issues) == 2
    inner = body[2]
    assert isinstance(inner, If) and isinstance(inner.branches[0][1][0], RawStmt)


def test_broken_compound_is_skipped_to_its_end() -> None:
    body, issues = parse_statements("IF #a THEN\n IF #b = THEN #x := 1; END_IF;\n#y := 2;\nEND_IF;\n#z := 3;")
    assert isinstance(body[0], If)
    raw = body[0].branches[0][1][0]
    assert isinstance(raw, RawStmt) and raw.text.startswith("IF #b =") and raw.text.endswith("END_IF;")
    assert isinstance(body[1], Assign)
    assert issues


def test_multiple_assignment_is_raw() -> None:
    body, issues = parse_statements("#a := #b := 1;")
    assert len(issues) == 1
    assert isinstance(body[0], RawStmt) and "множественное" in body[0].reason


def test_comments_are_attached() -> None:
    body, _ = parse_statements("// leading\n#a := 1; // trailing\n#b := 2;\n// closing")
    assert [c.text for c in body[0].comments] == ["// leading"]
    assert [c.text for c in body[0].trailing] == ["// trailing"]
    assert isinstance(body[-1], CommentStmt) and body[-1].comments[0].text == "// closing"


def test_comments_inside_multiline_call_are_kept() -> None:
    body, _ = parse_statements("#t(IN := #a, // first\n   PT := T#1s);")
    assert [c.text for c in body[0].comments] == ["// first"]


# ---------------------------------------------------------------------------
# Блоки
# ---------------------------------------------------------------------------

FB_TEXT = """// преамбула файла
FUNCTION_BLOCK "FB_Pump"
TITLE = Pump control
{ S7_Optimized_Access := 'TRUE' }
AUTHOR : WTP
FAMILY : Pumps
NAME : PUMP
VERSION : 1.0
// комментарий блока
   VAR_INPUT
      start { ExternalAccessible := 'False'} : Bool;   // пуск
      a, b : Int := 5;
      cfg : "UDT_Cfg";
      txt : String[20];
      wtxt : WString;
   END_VAR
   VAR_OUTPUT
      run : Bool;
   END_VAR
   VAR_IN_OUT
      io : Word;
   END_VAR
   VAR
      tmr {InstructionName := 'TON_TIME'; LibVersion := '1.0'} : TON_TIME;
      arr : Array[0..3, 1..2] of Real := [8(0.0)];
      dyn : Array[*] of Int;
      st : Struct
         x : Bool;
      END_STRUCT;
      ref : REF_TO Int;
   END_VAR
   VAR RETAIN
      hours : Real;
   END_VAR
   VAR_TEMP
      i : Int;
   END_VAR
   VAR CONSTANT
      MAX_N : Int := 10;
   END_VAR

BEGIN
   #run := #start;
END_FUNCTION_BLOCK
"""


def test_function_block_header_sections_and_types() -> None:
    sf = parse_source(FB_TEXT)
    assert not sf.issues
    blk = sf.blocks[0]
    assert isinstance(blk, Block)
    assert (blk.kind, blk.name, blk.quoted, blk.title) == ("FUNCTION_BLOCK", "FB_Pump", True, "Pump control")
    assert blk.props == {"AUTHOR": "WTP", "FAMILY": "Pumps", "NAME": "PUMP", "VERSION": "1.0"}
    assert blk.attributes == {"S7_Optimized_Access": "TRUE"}
    assert [c.text for c in blk.preamble] == ["// преамбула файла"]
    assert [c.text for c in blk.comments] == ["// комментарий блока"]
    assert [(s.kind, s.modifiers) for s in blk.sections] == [
        ("VAR_INPUT", []),
        ("VAR_OUTPUT", []),
        ("VAR_IN_OUT", []),
        ("VAR", []),
        ("VAR", ["RETAIN"]),
        ("VAR_TEMP", []),
        ("VAR", ["CONSTANT"]),
    ]
    inputs = [d for d in blk.sections[0].items if isinstance(d, VarDecl)]
    assert inputs[0].attributes == {"ExternalAccessible": "False"}
    assert inputs[0].trailing[0].text == "// пуск"
    assert inputs[1].names == ["a", "b"] and inputs[1].init == lit("5")
    assert inputs[2].type == NamedType("UDT_Cfg", quoted=True)
    assert inputs[3].type == StringType(False, lit("20"))
    assert inputs[4].type == StringType(True, None)
    stat = [d for d in blk.sections[3].items if isinstance(d, VarDecl)]
    assert stat[0].type == NamedType("TON_TIME")
    assert stat[1].type == ArrayType(((lit("0"), lit("3")), (lit("1"), lit("2"))), NamedType("Real"))
    assert stat[1].init == ArrayInit(((lit("8"), Literal("real", "0.0")),))
    assert stat[2].type == ArrayType((None,), NamedType("Int"))
    assert isinstance(stat[3].type, StructType)
    assert stat[4].type == RefType(NamedType("Int"))


def test_function_with_return_type_and_void() -> None:
    sf = parse_source(
        'FUNCTION "F_A" : Real\nBEGIN\n#F_A := 1.0;\nEND_FUNCTION\nFUNCTION "F_B" : Void\nBEGIN\nEND_FUNCTION\n'
    )
    a, b = sf.blocks
    assert isinstance(a, Block) and a.return_type == NamedType("Real")
    assert isinstance(b, Block) and b.return_type == NamedType("Void")


def test_data_blocks_all_forms() -> None:
    text = """DATA_BLOCK "DB_G"
{ S7_Optimized_Access := 'FALSE' }
VERSION : 0.1
NON_RETAIN
   VAR
      label : String;
      a : Int;
   END_VAR
BEGIN
   a := 5;
END_DATA_BLOCK
DATA_BLOCK "IDB_1"
VERSION : 0.1
NON_RETAIN
"FB_Motor"
BEGIN
END_DATA_BLOCK
DATA_BLOCK "IDB_2" "FB_Motor"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1
BEGIN
   feedbackTime := T#5S;
END_DATA_BLOCK
DATA_BLOCK "T_DB"
IEC_TIMER
BEGIN
END_DATA_BLOCK
DATA_BLOCK DB10
   STRUCT
      x : Int;
   END_STRUCT;
BEGIN
END_DATA_BLOCK
"""
    sf = parse_source(text)
    assert not sf.issues, sf.issues
    g, i1, i2, t, classic = sf.blocks
    assert isinstance(g, Block) and g.flags == ["NON_RETAIN"] and g.db_type is None
    assert [d.names for d in g.sections[0].items if isinstance(d, VarDecl)] == [["label"], ["a"]]
    assert len(g.body) == 1
    assert isinstance(i1, Block) and i1.db_type == NamedType("FB_Motor", quoted=True)
    assert isinstance(i2, Block) and i2.db_type == NamedType("FB_Motor", quoted=True)
    assert i2.attributes == {"S7_Optimized_Access": "TRUE"} and i2.props["VERSION"] == "0.1"
    assert isinstance(t, Block) and t.db_type == NamedType("IEC_TIMER")
    assert isinstance(classic, Block) and classic.struct is not None and not classic.quoted


def test_udt_and_organization_block() -> None:
    sf = parse_source(
        'TYPE "UDT_A"\nVERSION : 0.1\n   STRUCT\n      x : Bool;\n   END_STRUCT;\nEND_TYPE\n'
        'ORGANIZATION_BLOCK "Main"\nTITLE = "Main Program Sweep (Cycle)"\nVERSION : 0.1\n'
        "   VAR_INPUT\n      Initial_Call : Bool;\n   END_VAR\nBEGIN\n;\nEND_ORGANIZATION_BLOCK\n"
    )
    udt, ob = sf.blocks
    assert isinstance(udt, Block) and udt.struct is not None and len(udt.struct.decls) == 1
    assert isinstance(ob, Block) and ob.title == "Main Program Sweep (Cycle)"


def test_classic_const_and_label_sections() -> None:
    sf = parse_source(
        "FUNCTION_BLOCK FB1\nCONST\n   N := 10;\nEND_CONST\nLABEL\n   lbl;\nEND_LABEL\nBEGIN\nEND_FUNCTION_BLOCK\n"
    )
    blk = sf.blocks[0]
    assert isinstance(blk, Block)
    assert blk.sections[0].kind == "CONST" and isinstance(blk.sections[0].items[0], VarDecl)
    assert isinstance(blk.sections[1].items[0], RawDecl)


def test_broken_declaration_is_raw_and_block_continues() -> None:
    sf = parse_source(
        'FUNCTION_BLOCK "F"\nVAR_INPUT\n   a : Int\n   b : Bool;\nEND_VAR\nBEGIN\n#b := TRUE;\nEND_FUNCTION_BLOCK\n'
    )
    blk = sf.blocks[0]
    assert isinstance(blk, Block)
    items = blk.sections[0].items
    assert isinstance(items[0], RawDecl)
    assert isinstance(blk.body[0], Assign)
    assert sf.issues


def test_broken_block_header_becomes_raw_block() -> None:
    sf = parse_source('FUNCTION_BLOCK 123\nBEGIN\nEND_FUNCTION_BLOCK\nFUNCTION "F" : Int\nBEGIN\nEND_FUNCTION\n')
    assert isinstance(sf.blocks[0], RawBlock) and isinstance(sf.blocks[1], Block)


def test_text_outside_blocks_is_reported() -> None:
    sf = parse_source('garbage here;\nFUNCTION "F" : Int\nBEGIN\nEND_FUNCTION\n')
    assert isinstance(sf.blocks[0], RawBlock) and sf.blocks[0].reason == "текст вне блока"
    assert isinstance(sf.blocks[1], Block)


def test_spans_are_line_accurate() -> None:
    sf = parse_source(
        'FUNCTION_BLOCK "F"\nBEGIN\n   #a := 1;\n   IF #b THEN\n      #c := 2;\n   END_IF;\nEND_FUNCTION_BLOCK\n'
    )
    blk = sf.blocks[0]
    assert isinstance(blk, Block)
    assert (blk.span.line, blk.span.end_line) == (1, 7)
    assert [(s.span.line, s.span.end_line) for s in blk.body] == [(3, 3), (4, 6)]
