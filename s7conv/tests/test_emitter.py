"""Эмиттер ST: каждое правило docs/MAPPING.md — типы, вызовы, DB, OB, адреса, пометки CHECK/TODO."""

from __future__ import annotations

from s7conv.emitter import Options, wrap_line
from s7conv.layout import L
from s7conv.tests.conftest import Converted, ConvertFn, fb

TAGS = (
    "Name;Path;Data Type;Logical Address;Comment\n"
    "Start;T;Bool;%I0.0;Пуск\n"
    "Level_Raw;T;Int;%IW64;Уровень\n"
    "Speed_Ref;T;Int;%QW80;\n"
    "Lamp;T;Bool;%Q2.0;\n"
    "Free_Tag;T;Real;;\n"
    "T_Old;T;Timer;%T5;\n"
)

# ---------------------------------------------------------------------------
# Типы и объявления
# ---------------------------------------------------------------------------


def test_elementary_types_and_strings(conv: ConvertFn) -> None:
    decls = """VAR
   a : Int; b : DInt; c : Real; d : LReal; e : Bool; f : Byte; g : Word; h : DWord;
   i : Time; j : Date_And_Time; k : String[20]; l : String; m : WString[5]; n : UDInt; o : Date; p : Time_Of_Day;
END_VAR"""
    r = conv(fb("", decls))
    decl = r.decl("FB_T")
    for line in [
        "a : INT;",
        "b : DINT;",
        "c : REAL;",
        "d : LREAL;",
        "e : BOOL;",
        "f : BYTE;",
        "g : WORD;",
        "h : DWORD;",
        "i : TIME;",
        "j : DT;",
        "k : STRING(20);",
        "l : STRING(254);",
        "m : WSTRING(5);",
        "n : UDINT;",
        "o : DATE;",
        "p : TOD;",
    ]:
        assert line in decl, line
    assert r.statuses()["check"] == 0


def test_s5time_is_time_with_check(conv: ConvertFn) -> None:
    r = conv(fb("#t := S5T#2s;", "VAR\n t : S5Time := S5T#1s;\nEND_VAR"))
    assert "t : TIME := T#1s;" in r.decl("FB_T")
    assert "MIGRATION-CHECK: S5Time → TIME" in r.decl("FB_T")
    assert r.code("FB_T") == ["t := T#2s;"]
    assert "type.s5time" in r.rules("check")


def test_unsupported_types_are_todo_with_original(conv: ConvertFn) -> None:
    r = conv(fb("", "VAR_INPUT\n v : Variant;\n stamp : DTL;\n p : Any;\nEND_VAR"))
    decl = r.decl("FB_T")
    assert "// MIGRATION-TODO: Variant" in decl and "// v : Variant;" in decl
    assert "// stamp : DTL;" in decl and "// p : Any;" in decl
    assert r.statuses()["todo"] == 3


def test_arrays_and_initializers(conv: ConvertFn) -> None:
    decls = "VAR\n a : Array[0..3] of Int := [1, 2, 2(0)];\n m : Array[1..2, 0..#N] of Bool;\nEND_VAR\nVAR CONSTANT\n N : Int := 3;\nEND_VAR"
    decl = conv(fb("", decls)).decl("FB_T")
    assert "a : ARRAY[0..3] OF INT := [1, 2, 2(0)];" in decl
    assert "m : ARRAY[1..2, 0..N] OF BOOL;" in decl


def test_inline_struct_becomes_dut(conv: ConvertFn) -> None:
    decls = "VAR\n cfg : Struct\n  x : Bool;\n  inner : Struct\n   y : Int;\n  END_STRUCT;\n END_STRUCT;\n arr : Array[1..2] of Struct\n  z : Real;\n END_STRUCT;\nEND_VAR"
    r = conv(fb("#cfg.inner.y := 1;", decls))
    assert "cfg : ST_FB_T_cfg;" in r.decl("FB_T")
    assert "arr : ARRAY[1..2] OF ST_FB_T_arr;" in r.decl("FB_T")
    assert "inner : ST_FB_T_cfg_inner;" in r.decl("ST_FB_T_cfg")
    assert "y : INT;" in r.decl("ST_FB_T_cfg_inner")
    assert r.obj("ST_FB_T_cfg").kind == L.KIND_DUT
    assert r.code("FB_T") == ["cfg.inner.y := 1;"]


def test_udt_becomes_dut_and_is_used_by_name(conv: ConvertFn) -> None:
    udt = 'TYPE "UDT_Cmd"\nVERSION : 0.1\n STRUCT\n  start : Bool;\n  mode : Int := 1;\n END_STRUCT;\nEND_TYPE\n'
    r = conv(udt, fb("#c.mode := 2;", 'VAR\n c : "UDT_Cmd";\nEND_VAR'))
    assert "TYPE UDT_Cmd :\nSTRUCT\n    start : BOOL;\n    mode : INT := 1;\nEND_STRUCT\nEND_TYPE" in r.decl("UDT_Cmd")
    assert "c : UDT_Cmd;" in r.decl("FB_T")


def test_keyword_names_are_renamed_with_check(conv: ConvertFn) -> None:
    r = conv(fb("#time := T#1s; #max := #time;", "VAR\n time : Time;\n max : Time;\nEND_VAR"))
    assert "time_ : TIME;" in r.decl("FB_T") and "max_ : TIME;" in r.decl("FB_T")
    assert r.code("FB_T") == ["time_ := T#1s;", "max_ := time_;"]
    assert "name.renamed" in r.rules("check")


def test_hmi_attributes_give_check_instruction_attrs_are_dropped(conv: ConvertFn) -> None:
    decls = "VAR\n a { ExternalAccessible := 'False'; ExternalVisible := 'False'} : Int;\n t {InstructionName := 'TON_TIME'; LibVersion := '1.0'} : TON_TIME;\nEND_VAR"
    r = conv(fb("", decls))
    assert "decl.hmi_access" in r.rules("check")
    assert "t : TON;" in r.decl("FB_T")
    assert "InstructionName" not in r.decl("FB_T")


def test_uses_of_dropped_declarations_become_todo(conv: ConvertFn) -> None:
    """Оператор с переменной, объявление которой не перенесено, тоже TODO — без «необъявленных» имён в ST."""
    callee = fb("", "VAR_INPUT\n info : Variant;\n n : Int;\nEND_VAR", "FB_Log")
    body = (
        '#stamp := #stamp; #ok := TRUE; #lg(info := #ok, n := 1); #acc(IN := #ok, PT := T#1s); "DB_X".clock := #stamp;'
    )
    decls = 'VAR\n stamp : DTL; ok : Bool; lg : "FB_Log"; acc : TONR_TIME;\nEND_VAR'
    db = 'DATA_BLOCK "DB_X"\n VAR\n  clock : DTL;\n  v : Int;\n END_VAR\nBEGIN\nEND_DATA_BLOCK\n'
    r = conv(callee, db, fb(body, decls))
    assert r.code("FB_T") == ["ok := TRUE;", "lg(n := 1);"]
    assert {"decl.dropped_use", "call.param_dropped"} <= r.rules("todo")
    impl = r.impl("FB_T")
    assert "// #stamp := #stamp;" in impl and '// "DB_X".clock := #stamp;' in impl


def test_at_overlay_is_todo(conv: ConvertFn) -> None:
    r = conv(fb("", "VAR\n w : Word;\n bits AT w : Array[0..15] of Bool;\nEND_VAR"))
    assert "decl.at" in r.rules("todo")
    assert "// bits AT w : Array[0..15] of Bool;" in r.decl("FB_T")


def test_sections_fc_temp_retain_constant_db_specific(conv: ConvertFn) -> None:
    fc = 'FUNCTION "F_X" : Int\nVERSION : 0.1\n VAR_TEMP\n  t : Int;\n END_VAR\nBEGIN\n #F_X := 1;\nEND_FUNCTION\n'
    r = conv(
        fc,
        fb(
            "",
            "VAR RETAIN\n h : Real;\nEND_VAR\nVAR DB_SPECIFIC\n k : Int;\nEND_VAR\nVAR CONSTANT\n C : Int := 1;\nEND_VAR",
        ),
    )
    assert "FUNCTION F_X : INT\nVAR\n    t : INT;\nEND_VAR" in r.decl("F_X")
    assert r.code("F_X") == ["F_X := 1;"]
    decl = r.decl("FB_T")
    assert "VAR RETAIN\n    h : REAL;" in decl
    assert "VAR CONSTANT\n    C : INT := 1;" in decl
    assert "section.db_specific" in r.rules("check")


def test_void_function_has_no_return_type(conv: ConvertFn) -> None:
    r = conv('FUNCTION "F_V" : Void\nBEGIN\n;\nEND_FUNCTION\n')
    assert "\nFUNCTION F_V\n" in r.decl("F_V") + "\n"


def test_header_comment_follows_contributing_rules(conv: ConvertFn) -> None:
    text = '// file preamble\nFUNCTION_BLOCK "FB_H"\nTITLE = Pump\nAUTHOR : J\nVERSION : 1.2\n// block comment\nBEGIN\nEND_FUNCTION_BLOCK\n'
    decl = conv(text).decl("FB_H")
    head = decl.split("FUNCTION_BLOCK FB_H")[0]
    for word in ("Назначение: Pump", "Автор:      J", "Версия:     1.2", "Документ:   docs/", "block comment"):
        assert word in head, word
    assert "// file preamble" in head
    assert "// тело пустое" in conv(text).impl("FB_H")


# ---------------------------------------------------------------------------
# Выражения, операторы, вызовы
# ---------------------------------------------------------------------------


def test_locals_lose_hash_and_operators_map(conv: ConvertFn) -> None:
    body = "#x := #a & #b; #y := #i ** 2; #z := #i MOD 3; #w := NOT (#a OR #b) XOR #a;"
    decls = "VAR\n a : Bool; b : Bool; x : Bool; w : Bool;\n i : Real; y : Real; z : Int;\nEND_VAR"
    r = conv(fb(body, decls))
    assert r.code("FB_T") == [
        "x := a AND b;",
        "y := EXPT(i, 2);",
        "z := i MOD 3;",
        "w := NOT (a OR b) XOR a;",
    ]


def test_power_on_integers_needs_check(conv: ConvertFn) -> None:
    r = conv(fb("#i := #i ** 2;", "VAR\n i : Int;\nEND_VAR"))
    assert "expr.power" in r.rules("check")


def test_compound_assignment(conv: ConvertFn) -> None:
    r = conv(fb("#i += 1; #i *= #j + 1;", "VAR\n i : Int; j : Int;\nEND_VAR"))
    assert r.code("FB_T") == ["i := i + 1;", "i := i * (j + 1);"]


def test_all_statements_are_emitted(conv: ConvertFn) -> None:
    body = """
IF #a THEN #i := 1; ELSIF #b THEN #i := 2; ELSE #i := 3; END_IF;
CASE #i OF 1: #j := 1; 2, 3: #j := 2; 4..6: #j := 3; ELSE #j := 0; END_CASE;
FOR #k := 0 TO 9 BY 2 DO #j := #j + 1; IF #j > 5 THEN EXIT; END_IF; CONTINUE; END_FOR;
WHILE #j > 0 DO #j := #j - 1; END_WHILE;
REPEAT #j := #j + 1; UNTIL #j >= 3 END_REPEAT;
RETURN;
"""
    r = conv(fb(body, "VAR\n a : Bool; b : Bool; i : Int; j : Int; k : Int;\nEND_VAR"))
    assert r.code("FB_T") == [
        "IF a THEN",
        "i := 1;",
        "ELSIF b THEN",
        "i := 2;",
        "ELSE",
        "i := 3;",
        "END_IF",
        "CASE i OF",
        "1:",
        "j := 1;",
        "2, 3:",
        "j := 2;",
        "4..6:",
        "j := 3;",
        "ELSE",
        "j := 0;",
        "END_CASE",
        "FOR k := 0 TO 9 BY 2 DO",
        "j := j + 1;",
        "IF j > 5 THEN",
        "EXIT;",
        "END_IF",
        "CONTINUE;",
        "END_FOR",
        "WHILE j > 0 DO",
        "j := j - 1;",
        "END_WHILE",
        "REPEAT",
        "j := j + 1;",
        "UNTIL j >= 3",
        "END_REPEAT",
        "RETURN;",
    ]
    assert r.statuses() == {"auto": r.statuses()["auto"], "check": 0, "todo": 0}


def test_region_becomes_comment_markers(conv: ConvertFn) -> None:
    r = conv(fb("REGION Pumps\n #a := TRUE;\nEND_REGION", "VAR\n a : Bool;\nEND_VAR"))
    assert r.impl("FB_T").splitlines() == ["// REGION Pumps", "a := TRUE;", "// END_REGION Pumps"]


def test_comments_are_preserved(conv: ConvertFn) -> None:
    body = "// leading\n#a := TRUE; // trailing\n(* block *)\n#a := FALSE;"
    impl = conv(fb(body, "VAR\n a : Bool;\nEND_VAR")).impl("FB_T")
    assert impl.splitlines() == ["// leading", "a := TRUE;  // trailing", "(* block *)", "a := FALSE;"]


def test_explicit_empty_statement_is_kept(conv: ConvertFn) -> None:
    """Пустой оператор SCL ';' переносится как есть, вместе с комментарием в строке."""
    r = conv(fb("IF #a THEN ; // ждать\nEND_IF;", "VAR\n a : Bool;\nEND_VAR"))
    assert r.impl("FB_T").splitlines() == ["IF a THEN", "    ;  // ждать", "END_IF"]


def test_empty_branch_gets_placeholder(conv: ConvertFn) -> None:
    r = conv(fb("IF #a THEN\nEND_IF;", "VAR\n a : Bool;\nEND_VAR"))
    assert r.impl("FB_T").splitlines() == ["IF a THEN", "    ; // нет операторов", "END_IF"]


def test_timers_edges_and_multi_instance(conv: ConvertFn) -> None:
    decls = "VAR\n t1 : TON_TIME; t2 : TOF_TIME; t3 : TP_TIME; rt : R_TRIG; f : F_TRIG; q : Bool; et : Time;\nEND_VAR"
    body = "#t1(IN := #q, PT := T#5s, ET => #et); #t2(IN := #t1.Q, PT := T#1s); #t3(IN := #rt.Q, PT := T#2s);\n#rt(CLK := #q); #f(CLK := #q); #q := #t2.Q AND #f.Q;"
    r = conv(fb(body, decls))
    decl = r.decl("FB_T")
    for line in ("t1 : TON;", "t2 : TOF;", "t3 : TP;", "rt : R_TRIG;", "f : F_TRIG;"):
        assert line in decl
    assert r.code("FB_T") == [
        "t1(IN := q, PT := T#5s, ET => et);",
        "t2(IN := t1.Q, PT := T#1s);",
        "t3(IN := rt.Q, PT := T#2s);",
        "rt(CLK := q);",
        "f(CLK := q);",
        "q := t2.Q AND f.Q;",
    ]
    # F_TRIG — единственная пометка: начальное состояние памяти фронта
    assert r.rules("check") == {"fb.f_trig"}


def test_counters_rename_inputs_with_check(conv: ConvertFn) -> None:
    r = conv(
        fb(
            "#c(CU := #x, R := #y, PV := 10); #d(CD := #x, LD := #y, PV := 5);",
            "VAR\n c : CTU_INT; d : CTD_DINT; x : Bool; y : Bool;\nEND_VAR",
        )
    )
    assert "c : CTU;" in r.decl("FB_T") and "d : CTD;" in r.decl("FB_T")
    assert r.code("FB_T") == ["c(CU := x, RESET := y, PV := 10);", "d(CD := x, LOAD := y, PV := 5);"]
    assert "fb.counter" in r.rules("check")


def test_flipflops_rename_inputs_and_outputs(conv: ConvertFn) -> None:
    """S7 SR (сброс главнее) → CODESYS RS, S7 RS (установка главнее) → CODESYS SR — крест-накрест."""
    r = conv(fb("#ff(S := #a, R1 := #b); #a := #ff.Q;", "VAR\n ff : SR; a : Bool; b : Bool;\nEND_VAR"))
    assert "ff : RS;" in r.decl("FB_T")
    assert r.code("FB_T") == ["ff(SET := a, RESET1 := b);", "a := ff.Q1;"]
    r = conv(fb("#ff(R := #a, S1 := #b); #a := #ff.Q;", "VAR\n ff : RS; a : Bool; b : Bool;\nEND_VAR"))
    assert "ff : SR;" in r.decl("FB_T")
    assert r.code("FB_T") == ["ff(RESET := a, SET1 := b);", "a := ff.Q1;"]


def test_iec_timer_variable_takes_type_from_call(conv: ConvertFn) -> None:
    r = conv(fb("#t.TON(IN := TRUE, PT := T#1s); #q := #t.Q;", "VAR\n t : IEC_TIMER; q : Bool;\nEND_VAR"))
    assert "t : TON;" in r.decl("FB_T")
    assert r.code("FB_T") == ["t(IN := TRUE, PT := T#1s);", "q := t.Q;"]


def test_tonr_is_todo(conv: ConvertFn) -> None:
    r = conv(fb("", "VAR\n acc : TONR_TIME;\nEND_VAR"))
    assert "type.unsupported" in r.rules("todo")


def test_norm_x_scale_x_to_support_functions(conv: ConvertFn) -> None:
    body = "#n := NORM_X(MIN := 0, VALUE := #raw, MAX := 27648); #v := SCALE_X(MIN := 0.0, VALUE := #n, MAX := 100.0);"
    r = conv(fb(body, "VAR\n raw : Int; n : Real; v : Real;\nEND_VAR"))
    assert r.code("FB_T") == [
        "n := F_NormX(rMin := 0, rValue := raw, rMax := 27648);",
        "v := F_ScaleX(rMin := 0.0, rValue := n, rMax := 100.0);",
    ]
    assert r.result.support == {"F_NormX", "F_ScaleX"}
    assert r.statuses()["check"] == 0


def test_scale_x_into_integer_gets_conversion_and_check(conv: ConvertFn) -> None:
    r = conv(fb("#out := SCALE_X(MIN := 0, VALUE := #n, MAX := 27648);", "VAR\n n : Real; out : Int;\nEND_VAR"))
    assert r.code("FB_T") == ["out := REAL_TO_INT(F_ScaleX(rMin := 0, rValue := n, rMax := 27648));"]
    assert "func.scale_x_int" in r.rules("check")


def test_builtins_named_to_positional(conv: ConvertFn) -> None:
    body = """#i := LIMIT(MN := 0, IN := #i, MX := 100);
#i := MIN(IN1 := #i, IN2 := 5);
#i := MAX(IN1 := 1, IN2 := 2, IN3 := 3);
#w := SHL(IN := #w, N := 2);
#txt := CONCAT(IN1 := #txt, IN2 := 'x');
#txt := MID(IN := #txt, L := 2, P := 1);
#rv := SQR(#rv);
#i := SEL(G := TRUE, IN0 := 1, IN1 := 2);
#rv := ABS(#rv);"""
    r = conv(fb(body, "VAR\n i : Int; w : Word; txt : String[10]; rv : Real;\nEND_VAR"))
    assert r.code("FB_T") == [
        "i := LIMIT(0, i, 100);",
        "i := MIN(i, 5);",
        "i := MAX(1, 2, 3);",
        "w := SHL(w, 2);",
        "txt := CONCAT(txt, 'x');",
        "txt := MID(txt, 2, 1);",
        "rv := rv * rv;",
        "i := SEL(TRUE, 1, 2);",
        "rv := ABS(rv);",
    ]


def test_builtin_missing_parameter_is_todo(conv: ConvertFn) -> None:
    r = conv(fb("#i := LIMIT(MN := 0, IN := #i);", "VAR\n i : Int;\nEND_VAR"))
    assert "call.param" in r.rules("todo")


def test_conversions_and_round(conv: ConvertFn) -> None:
    body = "#rv := INT_TO_REAL(#i); #i := REAL_TO_INT(#rv); #d := ROUND(#rv); #dw := REAL_TO_DWORD(#rv); #t := S5TI_TIM(#s5);"
    r = conv(fb(body, "VAR\n i : Int; rv : Real; d : DInt; dw : DWord; t : Time; s5 : S5Time;\nEND_VAR"))
    assert r.code("FB_T") == [
        "rv := INT_TO_REAL(i);",
        "i := REAL_TO_INT(rv);",
        "d := REAL_TO_DINT(rv);",
        "dw := REAL_TO_DWORD(rv);",
        "t := s5;",
    ]
    assert {"conv.round", "func.round", "conv.bitcast", "conv.s5time"} <= r.rules("check")


def test_unsupported_function_is_todo_with_commented_original(conv: ConvertFn) -> None:
    r = conv(fb("#w := PEEK_WORD(area := 16#84, dbNumber := 1, byteOffset := 0);", "VAR\n w : Word;\nEND_VAR"))
    impl = r.impl("FB_T")
    assert "// MIGRATION-TODO: PEEK_WORD: нет прямого аналога" in impl
    assert "// #w := PEEK_WORD(area := 16#84, dbNumber := 1, byteOffset := 0);" in impl
    assert r.code("FB_T") == []


def test_goto_label_eno_pragma(conv: ConvertFn) -> None:
    r = conv(fb("GOTO lbl;\nlbl: #a := TRUE;\nENO := FALSE;\n{ pragma }", "VAR\n a : Bool;\nEND_VAR"))
    assert {"stmt.goto", "stmt.label", "expr.eno"} <= r.rules("todo")
    assert "stmt.pragma" in r.rules("check")
    assert r.code("FB_T") == ["a := TRUE;"]


def test_unparsed_statement_is_todo(conv: ConvertFn) -> None:
    r = conv(fb("#a := := 1;\n#a := TRUE;", "VAR\n a : Bool;\nEND_VAR"))
    impl = r.impl("FB_T")
    assert "// MIGRATION-TODO: оператор не разобран" in impl and "// #a := := 1;" in impl
    assert r.code("FB_T") == ["a := TRUE;"]


def test_slices(conv: ConvertFn) -> None:
    body = "#w.%X3 := TRUE; #b := #dw.%B1; #lw := #dw.%W0;"
    r = conv(fb(body, "VAR\n w : Word; b : Byte; dw : DWord; lw : Word;\nEND_VAR"))
    assert r.code("FB_T") == ["w.3 := TRUE;", "b := DWORD_TO_BYTE(SHR(dw, 8));", "lw := DWORD_TO_WORD(dw);"]
    assert "expr.slice_read" in r.rules("check")
    r = conv(fb("#dw.%B1 := 16#FF;", "VAR\n dw : DWord;\nEND_VAR"))
    assert "expr.slice_write" in r.rules("todo")


def test_function_block_internal_access_check(conv: ConvertFn) -> None:
    inner = fb(
        "#out := #in;",
        "VAR_INPUT\n in : Bool;\nEND_VAR\nVAR_OUTPUT\n out : Bool;\nEND_VAR\nVAR\n stat : Int;\nEND_VAR",
        "FB_In",
    )
    outer = fb(
        "#i(in := TRUE); #q := #i.out; #n := #i.stat;", 'VAR\n i : "FB_In"; q : Bool; n : Int;\nEND_VAR', "FB_Out"
    )
    r = conv(inner, outer)
    assert r.code("FB_Out") == ["i(in := TRUE);", "q := i.out;", "n := i.stat;"]
    assert "access.fb_static" in r.rules("check")


def test_fc_call_with_outputs_and_in_out(conv: ConvertFn) -> None:
    fc = 'FUNCTION "FC_Stat" : Int\n VAR_INPUT\n  x : Real;\n END_VAR\n VAR_OUTPUT\n  avg : Real;\n END_VAR\n VAR_IN_OUT\n  buf : Array[1..8] of Real;\n END_VAR\nBEGIN\n #FC_Stat := 0;\nEND_FUNCTION\n'
    body = '#n := "FC_Stat"(x := 1.0, avg => #a, buf := #b);'
    r = conv(fc, fb(body, "VAR\n n : Int; a : Real; b : Array[1..8] of Real;\nEND_VAR"))
    assert r.code("FB_T") == ["n := FC_Stat(x := 1.0, avg => a, buf := b);"]


def test_unknown_function_and_parameter_checks(conv: ConvertFn) -> None:
    r = conv(fb("#a := MyLibFunc(1); #a := ABS(1);", "VAR\n a : Int;\nEND_VAR"))
    assert "call.unknown" in r.rules("check")


def test_undeclared_local_is_check(conv: ConvertFn) -> None:
    r = conv(fb("#ghost := 1;"))
    assert "name.undeclared" in r.rules("check")


# ---------------------------------------------------------------------------
# DB, глобальные символы, адреса
# ---------------------------------------------------------------------------

DB_TEXT = """DATA_BLOCK "DB_Plant"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1
   VAR
      level : Real;
      mode : Int := 1;
      cfg : "UDT_Cfg";
      steps : Array[1..3] of Real;
   END_VAR
   VAR RETAIN
      total : LReal;
   END_VAR
BEGIN
   mode := 2;
   cfg.high := 16.0;
   steps[1] := 0.5;
   steps[2] := 1.5;
END_DATA_BLOCK
"""
UDT_TEXT = 'TYPE "UDT_Cfg"\nVERSION : 0.1\n STRUCT\n  low : Real;\n  high : Real := 100.0;\n END_STRUCT;\nEND_TYPE\n'


def test_global_db_becomes_qualified_gvl_with_retain_and_begin_values(conv: ConvertFn) -> None:
    r = conv(UDT_TEXT, DB_TEXT, fb('"DB_Plant".level := 1.0; "DB_Plant".total := "DB_Plant".total + 1.0;'))
    gvl = r.obj("DB_Plant")
    assert gvl.kind == L.KIND_GVL
    decl = gvl.decl
    assert "{attribute 'qualified_only'}\nVAR_GLOBAL\n" in decl
    assert "mode : INT := 2;" in decl
    assert "cfg : UDT_Cfg := (high := 16.0);" in decl
    assert "steps : ARRAY[1..3] OF REAL := [0.5, 1.5, 0.0];" in decl  # остальное — значение по умолчанию
    assert "VAR_GLOBAL RETAIN\n    total : LREAL;\nEND_VAR" in decl
    assert r.code("FB_T") == ["DB_Plant.level := 1.0;", "DB_Plant.total := DB_Plant.total + 1.0;"]


def test_retain_as_persistent_option(conv: ConvertFn) -> None:
    r = conv(UDT_TEXT, DB_TEXT, options=Options(retain_mode="persistent"))
    assert "VAR_GLOBAL PERSISTENT RETAIN" in r.decl("DB_Plant")
    assert "db.persistent" in r.rules("check")
    # проверено в CODESYS 3.5.17.30: PERSISTENT в обычном GVL без объекта Persistent Variables — C0244
    assert "C0244" in r.decl("DB_Plant")


def test_standard_db_without_non_retain_is_retain(conv: ConvertFn) -> None:
    text = "DATA_BLOCK \"DB_S\"\n{ S7_Optimized_Access := 'FALSE' }\nVERSION : 0.1\n VAR\n  a : Int;\n END_VAR\nBEGIN\nEND_DATA_BLOCK\n"
    r = conv(text)
    assert "VAR_GLOBAL RETAIN\n    a : INT;" in r.decl("DB_S")
    assert {"block.non_optimized", "db.retain_standard"} <= r.rules("check")


def test_standard_instance_and_typed_dbs_without_non_retain_are_retain(conv: ConvertFn) -> None:
    """Правило стандартного DB (без NON_RETAIN — реманентный целиком) действует и для экземплярных и
    типизированных DB: раньше они молча попадали в нереманентный VAR_GLOBAL."""
    legacy = (
        "FUNCTION_BLOCK \"FB_Old\"\n{ S7_Optimized_Access := 'FALSE' }\nVERSION : 0.1\n"
        "VAR_INPUT\n x : Int;\nEND_VAR\nBEGIN\nEND_FUNCTION_BLOCK\n"
    )
    modern = fb("", "VAR_INPUT\n y : Int;\nEND_VAR", "FB_New")
    dbs = (
        'DATA_BLOCK "DB_Old1" "FB_Old"\nBEGIN\nEND_DATA_BLOCK\n'  # стандартный ФБ: экземпляр стандартный
        'DATA_BLOCK "DB_Old2"\nNON_RETAIN\n"FB_Old"\nBEGIN\nEND_DATA_BLOCK\n'
        'DATA_BLOCK "DB_New1" "FB_New"\nBEGIN\nEND_DATA_BLOCK\n'
        'DATA_BLOCK "DB_Typed"\n{ S7_Optimized_Access := \'FALSE\' }\n"UDT_Cfg"\nBEGIN\nEND_DATA_BLOCK\n'
    )
    r = conv(UDT_TEXT, legacy, modern, dbs)
    gvl = r.decl("GVL_InstanceDBs")
    normal, _, retained = gvl.partition("VAR_GLOBAL RETAIN")
    assert "DB_Old1 : FB_Old;" in retained and "DB_Typed : UDT_Cfg;" in retained
    assert "DB_Old2 : FB_Old;" in normal and "DB_New1 : FB_New;" in normal
    notes = [n for n in r.notes if n.rule == "db.retain_standard"]
    assert sorted(n.block for n in notes) == ["DB_Old1", "DB_Typed"]
    persistent = conv(UDT_TEXT, legacy, dbs, modern, options=Options(retain_mode="persistent"))
    assert "VAR_GLOBAL PERSISTENT RETAIN" in persistent.decl("GVL_InstanceDBs")


def test_instance_and_typed_dbs_go_to_instances_gvl(conv: ConvertFn) -> None:
    motor = fb(
        "#run := #start;",
        "VAR_INPUT\n start : Bool;\n delay : Time;\nEND_VAR\nVAR_OUTPUT\n run : Bool;\nEND_VAR",
        "FB_Motor",
    )
    dbs = (
        'DATA_BLOCK "DB_M1"\nNON_RETAIN\n"FB_Motor"\nBEGIN\n delay := T#5S;\nEND_DATA_BLOCK\n'
        'DATA_BLOCK "DB_C" "UDT_Cfg"\nBEGIN\n low := 4.0;\nEND_DATA_BLOCK\n'
        'DATA_BLOCK "T_DB"\nIEC_TIMER\nBEGIN\nEND_DATA_BLOCK\n'
    )
    main = 'ORGANIZATION_BLOCK "Main"\nBEGIN\n"DB_M1"(start := TRUE);\n"T_DB".TON(IN := "DB_M1".run, PT := T#1s);\n"DB_C".high := 5.0;\nEND_ORGANIZATION_BLOCK\n'
    r = conv(UDT_TEXT, motor, dbs, main)
    gvl = r.decl("GVL_InstanceDBs")
    assert "DB_M1 : FB_Motor := (delay := T#5S);" in gvl
    assert "DB_C : UDT_Cfg := (low := 4.0);" in gvl
    assert "T_DB : TON;" in gvl
    assert r.code("PRG_Main") == [
        "GVL_InstanceDBs.DB_M1(start := TRUE);",
        "GVL_InstanceDBs.T_DB(IN := GVL_InstanceDBs.DB_M1.run, PT := T#1s);",
        "GVL_InstanceDBs.DB_C.high := 5.0;",
    ]


def test_instance_db_inferred_from_name_when_source_missing(conv: ConvertFn) -> None:
    motor = fb("", "VAR_INPUT\n start : Bool;\nEND_VAR", "FB_Motor")
    r = conv(motor, 'ORGANIZATION_BLOCK "Main"\nBEGIN\n"FB_Motor_DB"(start := TRUE);\nEND_ORGANIZATION_BLOCK\n')
    assert "FB_Motor_DB : FB_Motor;" in r.decl("GVL_InstanceDBs")
    assert "db.implicit_instance" in r.rules("check")


def test_unknown_db_member_access_is_todo(conv: ConvertFn) -> None:
    r = conv(fb('"Nowhere".x := 1;'))
    assert "sym.unknown_db" in r.rules("todo")


def test_tags_and_direct_addresses_share_io_layer(conv: ConvertFn) -> None:
    body = '#a := "Start" AND %I0.0; %Q2.0 := #a; #n := %IW64; "Speed_Ref" := #n; %M10.1 := TRUE; #m := %MW11;'
    r = conv(fb(body, "VAR\n a : Bool; n : Int; m : Word;\nEND_VAR"), tags=TAGS)
    assert r.code("FB_T") == [
        "a := GVL_IO.Start AND GVL_IO.Start;",
        "GVL_IO.Lamp := a;",
        "n := GVL_IO.Level_Raw;",
        "GVL_IO.Speed_Ref := n;",
        "GVL_Markers.M10_1 := TRUE;",
        "m := GVL_Markers.MW11;",
    ]
    io = r.decl("GVL_IO")
    assert "Start AT %IX0.0 : BOOL; // S7 %I0.0; Пуск" in io
    assert "Level_Raw AT %IW32 : INT; // S7 %IW64; Уровень" in io
    assert "Speed_Ref AT %QW40 : INT;" in io
    markers = r.decl("GVL_Markers")
    assert "M10_1 AT %MX10.1 : BOOL;" in markers
    assert "MW11 : WORD; // S7 %MW11" in markers  # не выровнен — без AT
    assert "addr.unaligned" in r.rules("check")


def test_overlapping_word_and_bit_addresses_are_checked(conv: ConvertFn) -> None:
    r = conv(fb("%MW10 := 16#1; %M10.0 := TRUE;"))
    assert "addr.overlap" in r.rules("check")


def test_peripheral_and_db_absolute_addresses_are_todo(conv: ConvertFn) -> None:
    r = conv(fb("#n := %IW272:P; %DB30.DBW0 := 1;", "VAR\n n : Int;\nEND_VAR"))
    assert {"addr.peripheral", "addr.unsupported"} <= r.rules("todo")


def test_unknown_symbol_declared_with_inferred_type(conv: ConvertFn) -> None:
    r = conv(fb('"Alarm" := NOT #ok; #r := "Gain" * 2.0;', "VAR\n ok : Bool; r : Real;\nEND_VAR"))
    tags = r.decl("GVL_Tags")
    assert "Alarm : BOOL;" in tags and "Gain : REAL;" in tags
    assert "sym.unknown" in r.rules("check")


def test_free_tag_and_s5_timer_tag(conv: ConvertFn) -> None:
    r = conv(fb('#r := "Free_Tag"; #t := "T_Old";', "VAR\n r : Real; t : Int;\nEND_VAR"), tags=TAGS)
    assert "Free_Tag : REAL;" in r.decl("GVL_Tags")
    assert "tag.s5" in r.rules("todo")


# ---------------------------------------------------------------------------
# OB → PROGRAM и задачи
# ---------------------------------------------------------------------------

OBS = """ORGANIZATION_BLOCK "Main"
TITLE = "Main Program Sweep (Cycle)"
   VAR_INPUT
      Initial_Call : Bool;
      Remanence : Bool;
   END_VAR
BEGIN
   IF #Initial_Call THEN
      "DB_H".x := 1;
   END_IF;
END_ORGANIZATION_BLOCK
ORGANIZATION_BLOCK "Cyclic interrupt"
BEGIN
   "DB_H".x := 2;
END_ORGANIZATION_BLOCK
ORGANIZATION_BLOCK "Startup"
BEGIN
   "DB_H".x := 0;
   RETURN;
END_ORGANIZATION_BLOCK
ORGANIZATION_BLOCK "Hardware interrupt"
BEGIN
   ;
END_ORGANIZATION_BLOCK
DATA_BLOCK "DB_H"
   VAR
      x : Int;
   END_VAR
BEGIN
END_DATA_BLOCK
"""


def test_obs_become_programs_and_tasks(conv: ConvertFn) -> None:
    cfg: dict[str, object] = {"Cyclic interrupt": {"number": 35, "kind": "cyclic", "interval_ms": 100}}
    r = conv(OBS, options=Options(ob_config=cfg))
    assert {"PRG_Main", "PRG_Cyclic_interrupt", "PRG_Startup", "PRG_Hardware_interrupt"} <= set(r.objects)
    assert r.code("PRG_Main") == [
        "Initial_Call := NOT xS7convFirstCycleDone;",
        "xS7convFirstCycleDone := TRUE;",
        "IF Initial_Call THEN",
        "DB_H.x := 1;",
        "END_IF",
    ]
    assert r.code("PRG_Startup") == [
        "IF NOT xS7convStartupDone THEN",
        "xS7convStartupDone := TRUE;",
        "DB_H.x := 0;",
        "RETURN;",
        "END_IF",
    ]
    tasks = r.result.tasks_json()["tasks"]
    assert tasks == [
        {
            "name": "MainTask",
            "type": "cyclic",
            "interval_ms": 10,
            "priority": 15,
            "pous": ["PRG_Startup", "PRG_Main"],
            "sources": ["Startup (OB100)", "Main (OB1)"],
        },
        {
            "name": "Task_OB35",
            "type": "cyclic",
            "interval_ms": 100,
            "priority": 1,
            "pous": ["PRG_Cyclic_interrupt"],
            "sources": ["Cyclic interrupt (OB35)"],
        },
    ]
    assert {"ob.start_info", "ob.initial_call", "ob.startup"} <= r.rules("check")
    assert "ob.event" in r.rules("todo")


EVENT_OB = """ORGANIZATION_BLOCK "Diagnostic error interrupt"
   VAR_INPUT
      IO_State : Word;
      Channel : UInt;
   END_VAR
BEGIN
   "DB_H".x := UINT_TO_INT(#Channel);
END_ORGANIZATION_BLOCK
ORGANIZATION_BLOCK "Cyclic interrupt"
   VAR_INPUT
      Event_Count : Int;
   END_VAR
BEGIN
   "DB_H".x := #Event_Count;
END_ORGANIZATION_BLOCK
DATA_BLOCK "DB_H"
   VAR
      x : Int;
   END_VAR
BEGIN
END_DATA_BLOCK
"""


def test_event_ob_start_info_stays_input(conv: ConvertFn) -> None:
    """Событийный OB вызывает рукописный обработчик события и передаёт стартовую информацию параметрами:
    в VAR программы извне записать нельзя (CODESYS 3.5.17.30: C0037). У циклического OB входы — VAR."""
    r = conv(EVENT_OB)
    event = r.decl("PRG_Diagnostic_error_interrupt")
    assert "VAR_INPUT\n    IO_State : WORD;" in event and "Channel : UINT;" in event
    assert "оставлены VAR_INPUT" in event
    cyclic = r.decl("PRG_Cyclic_interrupt")
    assert "VAR_INPUT" not in cyclic and "VAR\n    Event_Count : INT;" in cyclic
    assert [n.rule for n in r.notes if n.rule == "ob.start_info"] == ["ob.start_info", "ob.start_info"]
    assert "ob.event" in r.rules("todo")


def test_freewheeling_main_task_option(conv: ConvertFn) -> None:
    r = conv(OBS, options=Options(main_task="freewheeling"))
    main = r.result.tasks_json()["tasks"]
    assert isinstance(main, list) and main[0]["type"] == "freewheeling" and main[0]["interval_ms"] == 10


# ---------------------------------------------------------------------------
# Оформление
# ---------------------------------------------------------------------------


def test_wrap_line_splits_call_arguments() -> None:
    line = "    GVL_InstanceDBs.DB_P101(" + ", ".join(f"param{i} := value_number_{i}" for i in range(6)) + ");  // c"
    wrapped = wrap_line(line)
    assert len(wrapped) == 6
    assert all(len(w) <= 120 for w in wrapped)
    assert wrapped[1].startswith(" " * len("    GVL_InstanceDBs.DB_P101("))
    assert wrapped[-1].endswith(");  // c")


def test_wrap_line_splits_long_boolean() -> None:
    line = "x := " + " AND ".join(f"condition_number_{i}" for i in range(9)) + ";"
    wrapped = wrap_line(line)
    assert len(wrapped) > 1 and all(len(w) <= 120 for w in wrapped)
    assert "".join(w.strip() + " " for w in wrapped).split() == line.split()


def test_wrap_line_keeps_strings_and_short_lines() -> None:
    assert wrap_line("a := 1;") == ["a := 1;"]
    text = "s := CONCAT('" + "x, " * 40 + "', y);"
    assert wrap_line(text)[0].startswith("s := CONCAT('x, x, ")


def test_generated_code_has_no_tabs_and_ascii_identifiers(conv: ConvertFn) -> None:
    r = conv(fb("\t#a := TRUE;\t// tab", "VAR\n\ta : Bool;\nEND_VAR"))
    for obj in r.result.objects:
        for text in (obj.decl, obj.impl or ""):
            assert "\t" not in text


# ---------------------------------------------------------------------------
# Семантика S7 ↔ CODESYS: расхождения, которые нельзя переносить молча
# ---------------------------------------------------------------------------


def _stmt_statuses(r: Converted) -> list[str]:
    return [i.status for f in r.result.files for i in f.items if i.category == "stmt"]


def test_time_subtraction_is_checked(conv: ConvertFn) -> None:
    """TIME в S7 со знаком (DINT мс), в CODESYS без знака: отрицательная разность переполняется."""
    body = "#d := #t1 - #t2;\n#d := #t1 + #t2;\n#d := #ton.ET - T#1s;\n#d -= #t2;\n#n := #n - 1;\n#d := -#t1;"
    decls = "VAR\n t1 : Time; t2 : Time; d : Time; n : Int; ton : TON_TIME;\nEND_VAR"
    r = conv(fb(body, decls))
    assert r.code("FB_T") == [
        "d := t1 - t2;",
        "d := t1 + t2;",
        "d := ton.ET - T#1s;",
        "d := d - t2;",
        "n := n - 1;",
        "d := -t1;",
    ]
    assert _stmt_statuses(r) == ["check", "auto", "check", "check", "auto", "check"]
    assert "expr.time_sub" in r.rules("check")
    assert "// MIGRATION-CHECK: вычитание TIME" in r.impl("FB_T")


def test_integer_division_by_variable_is_checked(conv: ConvertFn) -> None:
    """Целое деление на 0: в CODESYS исключение (останов задачи), в S7 CPU работает дальше."""
    body = (
        "#q := #a / #b;\n#q := #a MOD #b;\n#q := #a / 2;\n#q := #a MOD #N;\n#x := #x / #x;\n#q /= #b;\n"
        "#q := #a / (#N - 1);"
    )
    decls = "VAR\n a : Int; b : Int; q : Int; x : Real;\nEND_VAR\nVAR CONSTANT\n N : Int := 4;\nEND_VAR"
    r = conv(fb(body, decls))
    assert r.code("FB_T") == [
        "q := a / b;",
        "q := a MOD b;",
        "q := a / 2;",
        "q := a MOD N;",
        "x := x / x;",
        "q := q / b;",
        "q := a / (N - 1);",
    ]
    assert _stmt_statuses(r) == ["check", "check", "auto", "auto", "auto", "check", "auto"]
    assert "expr.div_int" in r.rules("check")
    assert "CheckDivDInt" in r.impl("FB_T")


def test_string_index_access_is_todo(conv: ConvertFn) -> None:
    """S7: s[i] — CHAR, нумерация с 1; CODESYS: s[i] — BYTE (код символа). Молча переносить нельзя."""
    decls = "VAR\n txt : String[10];\n c : Char;\n a : Array[1..3] of Int;\n i : Int;\nEND_VAR"
    r = conv(fb("#c := #txt[2];\n#txt[1] := 'x';\n#i := #a[2];", decls))
    assert r.code("FB_T") == ["i := a[2];"]
    assert "expr.string_index" in r.rules("todo")
    assert _stmt_statuses(r) == ["todo", "todo", "auto"]


def test_scale_x_into_integer_parameter_and_typed_variant_get_conversion(conv: ConvertFn) -> None:
    """SCALE_X с целым OUT не только в присваивании: параметр ФБ и типизированный вариант SCALE_X_INT."""
    callee = fb("", "VAR_INPUT\n sp : Int;\n rsp : Real;\nEND_VAR", "FB_Drive")
    body = (
        "#drv(sp := SCALE_X(MIN := 0, VALUE := #n, MAX := 27648), rsp := SCALE_X(MIN := 0.0, VALUE := #n, MAX := 1.0));\n"
        "#k := SCALE_X_INT(MIN := 0, VALUE := #n, MAX := 100);"
    )
    decls = 'VAR\n drv : "FB_Drive";\n n : Real;\n k : Int;\nEND_VAR'
    r = conv(callee, fb(body, decls))
    assert r.code("FB_T") == [
        "drv(sp := REAL_TO_INT(F_ScaleX(rMin := 0, rValue := n, rMax := 27648)),",
        "rsp := F_ScaleX(rMin := 0.0, rValue := n, rMax := 1.0));",
        "k := REAL_TO_INT(F_ScaleX(rMin := 0, rValue := n, rMax := 100));",
    ]
    notes = [n for n in r.notes if n.rule == "func.scale_x_int"]
    assert len(notes) == 2


def test_sqr_is_exact_product_for_plain_operand(conv: ConvertFn) -> None:
    """SQR(x) = x * x; EXPT(x, 2.0) при отрицательном x в CODESYS не проверен — только для выражений с вызовом."""
    body = "#y := SQR(#x);\n#y := SQR(#x - #z);\n#y := SQR(ABS(#x));"
    r = conv(fb(body, "VAR\n x : Real; y : Real; z : Real;\nEND_VAR"))
    assert r.code("FB_T") == ["y := x * x;", "y := (x - z) * (x - z);", "y := EXPT(ABS(x), 2.0);"]
    assert _stmt_statuses(r) == ["auto", "auto", "check"]
    assert "func.sqr" in r.rules("check")


def test_startup_and_initial_call_notes_state_stop_start_difference(conv: ConvertFn) -> None:
    """Флаг первого цикла не сбрасывается командой Stop → Start CODESYS, а OB100 S7 выполняется при каждом STOP → RUN."""
    r = conv(OBS)
    by_rule = {n.rule: n.message for n in r.notes}
    for rule in ("ob.startup", "ob.initial_call"):
        assert "Stop" in by_rule[rule] and "Start" in by_rule[rule], by_rule[rule]
        assert "Reset" in by_rule[rule], by_rule[rule]


def test_round_of_lreal_keeps_lreal_precision(conv: ConvertFn) -> None:
    """ROUND(LReal) → LREAL_TO_DINT: REAL_TO_DINT сначала сузил бы LREAL до REAL (24 бита мантиссы)."""
    r = conv(fb("#d := ROUND(#lr);\n#d := ROUND(#rv);", "VAR\n d : DInt; lr : LReal; rv : Real;\nEND_VAR"))
    assert r.code("FB_T") == ["d := LREAL_TO_DINT(lr);", "d := REAL_TO_DINT(rv);"]
    assert "func.round" in r.rules("check")
