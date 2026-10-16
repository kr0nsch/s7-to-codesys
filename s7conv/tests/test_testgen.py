"""Генератор тестов coUnit по сценариям CSV (s7conv.testgen): формат, имена, текст ST, PRG_Tests."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from s7conv import corpus as C
from s7conv import mapping as M
from s7conv import testgen as TG
from s7conv.cli import main
from s7conv.emitter import Options
from s7conv.tests.conftest import REPO_ROOT, ConvertFn, fb

SCENARIOS = REPO_ROOT / "scenarios"

HEADER = "scenario,cycle,t_ms,in.a:BOOL,in.t:TIME,out.q:BOOL,out.v:REAL,tol.v,boundary,comment\n"


def read(body: str, header: str = HEADER) -> TG.ScenarioFile:
    return TG.read_scenarios(header + body, "scenarios/FB_T.csv")


# --- чтение CSV -----------------------------------------------------------------------------------------


def test_read_minimal_file() -> None:
    sf = read("S1,1,0,TRUE,T#100MS,FALSE,0.5,0.001,FALSE,старт\nS1,2,100,FALSE,,TRUE,1.0,0.001,TRUE,\n")
    assert sf.block == "FB_T"
    assert [(c.kind, c.path, c.type) for c in sf.columns] == [
        ("in", "a", "BOOL"),
        ("in", "t", "TIME"),
        ("out", "q", "BOOL"),
        ("out", "v", "REAL"),
        ("tol", "v", "REAL"),
    ]
    ((name, rows),) = sf.scenarios()
    assert name == "S1" and [r.t_ms for r in rows] == [0, 100]
    assert rows[1].inputs == {"a": "FALSE"} and rows[1].boundary and rows[0].comment == "старт"


@pytest.mark.parametrize(
    ("body", "fragment"),
    [
        ("S1,2,0,TRUE,T#1MS,TRUE,0.5,0.001,FALSE,\n", "cycle = 1"),
        ("S1,1,0,TRUE,T#1MS,TRUE,0.5,0.001,FALSE,\nS1,3,0,TRUE,T#1MS,TRUE,0.5,0.001,FALSE,\n", "без пропусков"),
        ("S1,1,0,TRUE,T#1MS,TRUE,0.5,0.001,FALSE,\nS1,2,-1,TRUE,T#1MS,TRUE,0.5,0.001,FALSE,\n", "не убывает"),
        ("S1,1,0,TRUE,,TRUE,0.5,0.001,FALSE,\n", "не все входы"),
        ("S1,1,0,YES,T#1MS,TRUE,0.5,0.001,FALSE,\n", "BOOL"),
        ("S1,1,0,TRUE,T#1S,TRUE,0.5,0.001,FALSE,\n", "TIME"),
        ("S1,1,0,TRUE,T#1MS,TRUE,1,0.001,FALSE,\n", "REAL"),
        ("S1,1,0,TRUE,T#1MS,TRUE,0.5,,FALSE,\n", "tol.v"),
        ("S1,1,0,TRUE,T#1MS,TRUE,0.5,-0.1,FALSE,\n", "допуск"),
        ("1x,1,0,TRUE,T#1MS,TRUE,0.5,0.001,FALSE,\n", "идентификатор"),
        ("S1,1,0,TRUE,T#1MS,TRUE,0.5,0.001,MAYBE,\n", "boundary"),
        ("S1,1,0,TRUE,T#1MS,TRUE,0.5,0.001,FALSE\n", "ячеек"),
        (
            "S1,1,0,TRUE,T#1MS,TRUE,0.5,0.001,FALSE,\nS2,1,0,TRUE,T#1MS,TRUE,0.5,0.001,FALSE,\n"
            "S1,1,0,TRUE,T#1MS,TRUE,0.5,0.001,FALSE,\n",
            "не подряд",
        ),
    ],
)
def test_read_rejects_format_errors(body: str, fragment: str) -> None:
    with pytest.raises(TG.ScenarioError, match=fragment):
        read(body)


@pytest.mark.parametrize(
    "header",
    [
        "scenario,cycle,t_ms,in.a:BOOL,boundary\n",
        "scenario,cycle,t_ms,in.a:CHAR,boundary,comment\n",
        "scenario,cycle,t_ms,out.v:REAL,boundary,comment\n",
        "scenario,cycle,t_ms,tol.v,out.v:REAL,boundary,comment\n",
        "scenario,cycle,t_ms,in.a:BOOL,in.a:BOOL,boundary,comment\n",
        "scenario,cycle,t_ms,x.a:BOOL,boundary,comment\n",
        "scenario,cycle,t_ms,in.a-b:BOOL,boundary,comment\n",
    ],
)
def test_read_rejects_bad_headers(header: str) -> None:
    with pytest.raises(TG.ScenarioError):
        TG.read_scenarios(header, "scenarios/FB_T.csv")


@pytest.mark.parametrize(
    ("cell", "type_name", "ok"),
    [
        ("16#00C1", "WORD", True),
        ("16#C1", "WORD", False),
        ("16#00c1", "WORD", False),
        ("-4864", "INT", True),
        ("-1", "UINT", False),
        ("0.125138889", "REAL", True),
        ("1e3", "REAL", False),
        ("T#3000MS", "TIME", True),
        ("AIR SCOUR", "STRING", True),
        ("it's", "STRING", False),
        ("Тест", "STRING", False),
    ],
)
def test_value_formats(cell: str, type_name: str, ok: bool) -> None:
    if ok:
        TG.check_value(cell, type_name)
    else:
        with pytest.raises(TG.ScenarioError):
            TG.check_value(cell, type_name)


def test_reader_agrees_with_reference_reader() -> None:
    """Читатель генератора и эталонный читатель формата (scenarios/reference) видят одни и те же данные."""
    scenario_lib = pytest.importorskip("scenario_lib")
    for path in sorted(SCENARIOS.glob("*.csv")):
        text = path.read_text(encoding="utf-8")
        mine = TG.read_scenarios(text, path.name)
        _columns, ref_rows = scenario_lib.read_csv(text)
        assert len(mine.rows) == len(ref_rows), path.name
        for row, ref in zip(mine.rows, ref_rows, strict=True):
            assert (row.scenario, row.cycle, row.t_ms, row.boundary) == (
                ref.scenario,
                ref.cycle,
                ref.t_ms,
                ref.boundary,
            )
            assert set(row.inputs) == set(ref.inputs) and set(row.outputs) == set(ref.outputs)


# --- имена ST по таблицам конвертера ---------------------------------------------------------------------

DECLS = (
    "VAR_INPUT\n R : Bool; go : Bool; sp : Real; mode : Int;\nEND_VAR\n"
    "VAR_OUTPUT\n out : Bool; st : Struct\n  code : Int;\n  txt : String[10];\n END_STRUCT;\n"
    " arr : Array[1..3] of Int;\nEND_VAR\nVAR\n hidden : Bool;\nEND_VAR"
)


def _result(conv: ConvertFn) -> object:
    return conv(fb("#out := #go;", DECLS)).result


def col(kind: str, path: str, type_name: str) -> TG.Column:
    return TG.Column(kind, path, type_name)


def test_resolve_applies_converter_renames_and_struct_fields(conv: ConvertFn) -> None:
    """R и ST — ключевые слова CODESYS: конвертер переименовал их в R_ и st_, генератор — так же."""
    result = conv(fb("#out := #go;", DECLS)).result
    assert TG.resolve(result, "FB_T", col("in", "R", "BOOL")) == TG.Target("R_", "BOOL")
    assert TG.resolve(result, "FB_T", col("out", "st.code", "INT")) == TG.Target("st_.code", "INT")
    assert TG.resolve(result, "FB_T", col("out", "st.txt", "STRING")) == TG.Target("st_.txt", "STRING")
    assert TG.resolve(result, "FB_T", col("out", "arr[2]", "INT")) == TG.Target("arr[2]", "INT")


@pytest.mark.parametrize(
    ("column", "fragment"),
    [
        (TG.Column("in", "out", "BOOL"), "VAR_OUTPUT"),
        (TG.Column("out", "go", "BOOL"), "VAR_INPUT"),
        (TG.Column("out", "hidden", "BOOL"), "ожидалась VAR_OUTPUT"),
        (TG.Column("in", "sp", "INT"), "тип"),
        (TG.Column("in", "nope", "BOOL"), "нет в интерфейсе"),
        (TG.Column("out", "st.nope", "INT"), "нет в интерфейсе"),
        (TG.Column("in", "mode[1]", "INT"), "не-массив"),
    ],
)
def test_resolve_errors(conv: ConvertFn, column: TG.Column, fragment: str) -> None:
    result = conv(fb("#out := #go;", DECLS)).result
    with pytest.raises(TG.ScenarioError, match=fragment):
        TG.resolve(result, "FB_T", column)


def test_resolve_unknown_block(conv: ConvertFn) -> None:
    result = conv(fb("#out := #go;", DECLS)).result
    with pytest.raises(TG.ScenarioError, match="не найден"):
        TG.resolve(result, "FB_Nope", col("in", "go", "BOOL"))


# --- текст набора ----------------------------------------------------------------------------------------


def test_generated_suite_text(conv: ConvertFn) -> None:
    result = conv(fb("#out := #go;", DECLS), options=Options(timers=M.S7COMPAT)).result
    sf = TG.read_scenarios(
        "scenario,cycle,t_ms,in.go:BOOL,in.sp:REAL,out.out:BOOL,out.st.txt:STRING,boundary,comment\n"
        "Run,1,0,TRUE,1.5,TRUE,AIR SCOUR,FALSE,пуск\n"
        "Run,2,200,TRUE,2.5,TRUE,AIR SCOUR,TRUE,на пороге\n",
        "scenarios/FB_T.csv",
    )
    suite = TG.generate_suite(sf, result)
    obj = suite.obj
    assert obj.name == "FB_T_ScenarioTest" and obj.folder == [TG.SCENARIO_FOLDER]
    assert "FUNCTION_BLOCK FB_T_ScenarioTest EXTENDS coUnit.FB_TestSuite" in obj.decl
    assert "fbRun : FB_T;" in obj.decl and "xRunDone : BOOL;" in obj.decl
    assert obj.decl.startswith(f"// {TG.AUTO_GENERATED}")
    (method,) = obj.methods
    body = method.impl or ""
    assert body.splitlines()[1:5] == [
        "coUnit.TEST('Run');",
        "IF NOT xRunDone THEN",
        "    xRunDone := TRUE;",
        "    GVL_S7Clock.xSimulation := TRUE;",
    ]
    assert "    GVL_S7Clock.tSimNow := T#200MS;" in body
    assert body.count("fbRun.go := TRUE;") == 1  # вход не изменился — второй раз не присваивается
    assert "fbRun.sp := 2.5;" in body
    assert "AssertEquals_STRING(Expected := 'AIR SCOUR', Actual := fbRun.st_.txt, Message := 'Run#2 st.txt');" in body
    assert "на пороге таймера" in body
    assert body.rstrip().endswith("    GVL_S7Clock.xSimulation := FALSE;\nEND_IF\ncoUnit.TEST_FINISHED();")
    assert suite.asserts == 4 and suite.tests == 1 and suite.rows == 2


def test_long_assert_lines_are_wrapped(conv: ConvertFn) -> None:
    result = conv(fb("#out := #go;", DECLS)).result
    sf = TG.read_scenarios(
        "scenario,cycle,t_ms,in.go:BOOL,out.st.code:INT,boundary,comment\n"
        "AVeryLongScenarioNameForWrappingChecks,1,0,TRUE,0,FALSE,\n",
        "scenarios/FB_T.csv",
    )
    obj = TG.generate_suite(sf, result).obj
    lines = (obj.methods[0].impl or "").splitlines()
    assert all(len(line) <= TG.MAX_LINE for line in lines)
    assert any(
        line.strip().startswith("Actual := fbAVeryLongScenarioNameForWrappingChecks.st_.code,") for line in lines
    )


def test_instance_names() -> None:
    assert TG.instance_name("FB_F_NormX_Test") == "fbF_NormXTest"
    assert TG.instance_name("FB_Motor_ScenarioTest") == "fbMotor_ScenarioTest"
    assert TG.instance_name("FB_S7Ton_Test") == "fbS7TonTest"


def test_prg_tests_lists_all_suites() -> None:
    prg = TG.generate_prg_tests(["FB_Motor_ScenarioTest"], ["FB_F_NormX_Test"])
    assert (
        "fbF_NormXTest : FB_F_NormX_Test;" in prg.decl and "fbMotor_ScenarioTest : FB_Motor_ScenarioTest;" in prg.decl
    )
    impl = prg.impl or ""
    assert "coUnit.RUN();" in impl
    assert "xAllFinished := fbF_NormXTest.AreAllTestsFinished()\n        AND fbMotor_ScenarioTest" in impl
    assert TG.generate_prg_tests([], []).impl is not None


# --- корпус: ожидаемые значения — из CSV ------------------------------------------------------------------


@pytest.fixture(scope="module")
def corpus_tests() -> TG.TestsBuild:
    return C.build(REPO_ROOT).tests


def test_every_csv_row_and_output_becomes_an_assert(corpus_tests: TG.TestsBuild) -> None:
    files = {sf.block: sf for sf in TG.scenario_files(SCENARIOS, REPO_ROOT)}
    assert {s.obj.name for s in corpus_tests.suites} == {f"{b}{TG.SUITE_SUFFIX}" for b in files}
    for suite in corpus_tests.suites:
        sf = files[suite.obj.name[: -len(TG.SUITE_SUFFIX)]]
        assert suite.asserts == sum(len(r.outputs) for r in sf.rows)
        assert [m.name for m in suite.obj.methods] == [name for name, _rows in sf.scenarios()]


ASSERT_RE = re.compile(
    r"Expected := (?P<exp>'[^']*'|[^,]+),\s*Actual := [^,]+,\s*(?:Delta := (?P<delta>[^,]+),\s*)?Message := '(?P<msg>[^']+)'"
)


def test_expected_values_are_copied_from_csv(corpus_tests: TG.TestsBuild) -> None:
    """Каждое Expected и Delta — текст ячейки CSV (а не значение, посчитанное по сконвертированному коду)."""
    files = {sf.block: sf for sf in TG.scenario_files(SCENARIOS, REPO_ROOT)}
    for suite in corpus_tests.suites:
        sf = files[suite.obj.name[: -len(TG.SUITE_SUFFIX)]]
        cells = {(r.scenario, r.cycle, p): (v, r.tolerances.get(p)) for r in sf.rows for p, v in r.outputs.items()}
        seen = 0
        for method in suite.obj.methods:
            text = " ".join(line.strip() for line in (method.impl or "").splitlines())
            for m in ASSERT_RE.finditer(text):
                scenario_cycle, path = m["msg"].split(" ")
                scenario, cycle = scenario_cycle.split("#")
                value, tol = cells[(scenario, int(cycle), path)]
                assert m["exp"].strip("'") == value and (m["delta"] or None) == tol, m["msg"]
                seen += 1
        assert seen == suite.asserts


def test_boundary_rows_are_checked(corpus_tests: TG.TestsBuild) -> None:
    text = "\n".join(m.impl or "" for s in corpus_tests.suites for m in s.obj.methods)
    assert text.count("на пороге таймера") == sum(
        1 for sf in TG.scenario_files(SCENARIOS, REPO_ROOT) for r in sf.rows if r.boundary
    )


def test_gen_tests_cli_check_matches_repository(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["gen-tests", str(SCENARIOS), "--out", str(REPO_ROOT / "tests"), "--check"]) == 0
    assert "наборов 6" in capsys.readouterr().out


def test_gen_tests_cli_writes_into_empty_dir(tmp_path: Path) -> None:
    out = tmp_path / "tests"
    assert main(["gen-tests", str(SCENARIOS), "--out", str(out), "-q"]) == 0
    assert (out / "POUs" / "Scenarios" / "FB_Motor_ScenarioTest" / "FB_Motor_ScenarioTest.decl.st").is_file()
    prg = (out / "POUs" / "PRG_Tests" / "PRG_Tests.decl.st").read_text(encoding="utf-8")
    assert "FB_F_NormX_Test" not in prg  # в пустом каталоге рукописных наборов нет
    assert main(["gen-tests", str(SCENARIOS), "--out", str(out), "--check", "-q"]) == 0


def test_gen_tests_cli_bad_scenarios(tmp_path: Path) -> None:
    bad = tmp_path / "sc"
    bad.mkdir()
    (bad / "FB_Motor.csv").write_text(
        "scenario,cycle,t_ms,in.nope:BOOL,boundary,comment\nS,1,0,TRUE,FALSE,\n", encoding="utf-8"
    )
    assert main(["gen-tests", str(bad), "--out", str(tmp_path / "tests")]) == 2


@pytest.mark.parametrize("name", ["Run_", "AreAllTestsFinished", "AssertSomething", "WHILE", "FB_init"])
def test_scenario_name_must_not_clash_with_suite_methods(name: str) -> None:
    body = f"{name},1,0,TRUE,T#1MS,TRUE,0.5,0.001,FALSE,\n"
    if name == "Run_":
        read(body)
        return
    with pytest.raises(TG.ScenarioError, match="занято"):
        read(body)
