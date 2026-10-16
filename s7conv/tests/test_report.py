"""Отчёт конвертации: подсчёт статусов по файлам и видам, Markdown и HTML."""

from __future__ import annotations

import re
from html.parser import HTMLParser

from s7conv import report as R
from s7conv.emitter import Options
from s7conv.tests.conftest import ConvertFn, fb

SOURCE = fb(
    "#a := TRUE;\n#t := S5T#1s;\nGOTO x;\n#a := FALSE;",
    "VAR\n a : Bool;\n t : S5Time;\n v : Variant;\nEND_VAR",
)


class _Checker(HTMLParser):
    """Минимальная проверка корректности HTML: парные теги, нет скриптов извне."""

    VOID = frozenset({"meta", "br", "link", "img", "input", "hr"})

    def __init__(self) -> None:
        super().__init__()
        self.stack: list[str] = []
        self.errors: list[str] = []
        self.external: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in ("src", "href") and value and value.startswith("http"):
                self.external.append(value)
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"</{tag}> при открытом {self.stack[-1] if self.stack else None}")
            return
        self.stack.pop()


def test_totals_by_status_and_category(conv: ConvertFn) -> None:
    r = conv(SOURCE)
    tot = R.totals(R.all_items(r.result))
    assert (tot.auto, tot.check, tot.todo) == (4, 2, 2)
    assert tot.total == 8 and round(tot.pct(tot.auto)) == 50
    stmts = R.totals(i for i in R.all_items(r.result) if i.category == "stmt")
    assert (stmts.auto, stmts.check, stmts.todo) == (2, 1, 1)


def test_rule_summary_counts(conv: ConvertFn) -> None:
    r = conv(SOURCE)
    todo = R.rule_summary(r.result, "todo")
    assert {rule for rule, _name, _count in todo} == {"type.unsupported", "stmt.goto"}
    check = {rule: count for rule, _n, count in R.rule_summary(r.result, "check")}
    assert check == {"type.s5time": 2}


def test_markdown_report_lists_files_lines_and_reasons(conv: ConvertFn) -> None:
    md = R.render_markdown(conv(SOURCE).result, ["t0.scl"])
    assert md.startswith("# Отчёт конвертации SCL → ST CODESYS")
    assert "| Конструкций | 8 |" in md
    assert "| `t0.scl` | 1 | 8 | 4 | 2 | 2 | 50 % |" in md
    assert re.search(r"\| 11 \| ✕ не поддерживается \| FB_T \| `stmt.goto` \| GOTO", md)
    assert "## Не поддерживается — причины" in md and "## Требует проверки — причины" in md
    assert md.endswith("\n") and "\r" not in md


def test_markdown_report_states_s7compat_layer_and_modes(conv: ConvertFn) -> None:
    """«Автоматически» через рукописные объекты S7Compat — отчёт называет режимы и объекты, а не молчит."""
    src = fb(
        "#t(IN := #x, PT := T#1s);\n#n := NORM_X(MIN := 0, VALUE := #raw, MAX := 27648);",
        "VAR\n t : TON_TIME; x : Bool; raw : Int; n : Real;\nEND_VAR",
    )
    result = conv(src, options=Options(timers="s7compat")).result
    md = R.render_markdown(result, ["t0.scl"])
    assert "<code>FB_S7Ton</code>" in R.render_html(result, ["t0.scl"])
    assert "## Слой совместимости S7Compat" in md
    assert "таймеры TON/TOF/TP — `s7compat`" in md and "F_TRIG — `standard`" in md
    for name in ("F_NormX", "FB_S7Ton", "F_S7Now", "GVL_S7Clock"):
        assert f"`{name}`" in md, name
    plain = R.render_markdown(conv(SOURCE).result, ["t0.scl"])
    assert "## Слой совместимости S7Compat" in plain and "объекты S7Compat не нужны" in plain
    assert "таймеры TON/TOF/TP — `standard`" in plain


def test_markdown_escapes_pipes(conv: ConvertFn) -> None:
    md = R.render_markdown(conv(fb("", "", "FB_P")).result, ["a|b.scl"])
    assert "`a\\|b.scl`" in md


def test_html_report_is_self_contained_and_well_formed(conv: ConvertFn) -> None:
    html_text = R.render_html(conv(SOURCE).result, ["t0.scl"])
    checker = _Checker()
    checker.feed(html_text)
    assert not checker.errors and not checker.stack, checker.errors
    assert not checker.external
    assert "<title>Отчёт конвертации SCL</title>" in html_text
    assert "prefers-color-scheme: dark" in html_text
    assert html_text.count('class="seg s-') >= 3
    assert "stmt.goto" in html_text and "&lt;" not in "".join(R.STATUS_LABEL.values())


def test_reports_are_deterministic(conv: ConvertFn) -> None:
    a = conv(SOURCE).result
    b = conv(SOURCE).result
    assert R.render_markdown(a, ["x"]) == R.render_markdown(b, ["x"])
    assert R.render_html(a, ["x"]) == R.render_html(b, ["x"])


def test_empty_report(conv: ConvertFn) -> None:
    r = conv(fb("", "", "FB_Empty"))
    md = R.render_markdown(r.result, ["e.scl"])
    assert "OB в исходниках нет." in md and "Нет." in md
