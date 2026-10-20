"""S7-GRAPH (SeqIR) → SFC CODESYS в PLCopen XML: POU SFC и ФБ-обёртка на ST с интерфейсом блока GRAPH.

Форма — как у импорта, проверенного в CODESYS 3.5.17.30 (`tools_project/cds_plcopen.py`): пространство
имён `http://www.plcopen.org/xml/tc6_0200`; условие перехода — `inVariable` с выражением ST (элемент
`<inline>` CODESYS при импорте пропускает); действия шага — `actionBlock` с IEC-квалификаторами N, D, L, P
над BOOL-переменными SFC; прыжок — `jumpStep`; ветви — `selection*`/`simultaneous*`; координаты 0,0.

Разделение (docs/STRATEGIES.md, docs/MAPPING_GRAPH.md):
- SFC `<Блок>_Sfc` — шаги и переходы GRAPH: наладчик видит активные шаги, их время и переходы в онлайне;
  каждое действие GRAPH — IEC-действие над флагом `x<Шаг>_<Квалификатор><номер>`, контроль шага — флаг
  `x<Шаг>_Active`; ошибка контроля приходит входом и блокирует переходы шага;
- обёртка `<Блок>` (ST) — интерфейс блока GRAPH: квитирование ACK_EF, вызов SFC (INIT_SQ → SFCInit), по флагам —
  действия GRAPH (N — пока флаг; общий операнд нескольких шагов — ИЛИ; S/R; C — И блокировка; событие S1 —
  по флагу P), защёлка контроля, ERR_FLT, постоперации.
IEC-действия выполняются ещё один раз после выключения шага, поэтому побочные эффекты (S/R, инструкции) — в
обёртке по флагам, а не в телах действий SFC. Переключение SFC — в конце цикла: действия нового шага видны со
следующего вызова (на вызов позже ST-двойника; наборы coUnit SFC — многоцикловые).
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from xml.sax.saxutils import escape, quoteattr

from s7conv.frontends.simaticml import XBlock
from s7conv.ir.net import build_network
from s7conv.ir.seq import Graph, SeqStep, Sequence, parse_graph, topology
from s7conv.lower.common import BlockLower
from s7conv.lower.net_to_ast import NetLowerer

NS = "http://www.plcopen.org/xml/tc6_0200"
XHTML = "http://www.w3.org/1999/xhtml"
_TYPES = {
    "BOOL": "BOOL",
    "BYTE": "BYTE",
    "WORD": "WORD",
    "DWORD": "DWORD",
    "SINT": "SINT",
    "INT": "INT",
    "DINT": "DINT",
    "USINT": "USINT",
    "UINT": "UINT",
    "UDINT": "UDINT",
    "REAL": "REAL",
    "LREAL": "LREAL",
    "TIME": "TIME",
}
_PURE = ("Contact", "Not", "O", "A", "X", "Eq", "Ne", "Gt", "Ge", "Lt", "Le")


class SfcError(Exception):
    """Конструкция GRAPH, которую вариант SFC не выражает (блок остаётся только ST-двойником)."""


@dataclass
class Var:
    name: str
    type: str
    init: str = ""
    comment: str = ""


@dataclass
class SfcResult:
    xml: str
    notes: list[str] = field(default_factory=list)  # что вариант SFC не переносит (для отчёта и README)


def iec_type(datatype: str) -> str:
    key = datatype.strip('"').upper()
    if key not in _TYPES:
        raise SfcError(f"тип {datatype} в варианте SFC не поддерживается")
    return _TYPES[key]


def _ident(step: SeqStep) -> str:
    return step.name if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", step.name) else f"S{step.number}"


# ---------------------------------------------------------------------------
# Условия: сеть LAD → выражение ST
# ---------------------------------------------------------------------------


def _implicit_ref(name: str) -> Callable[[re.Match[str]], str]:
    """Замена `#Шаг.X` / `#Шаг.T` неявной переменной шага SFC `Шаг.x` / `Шаг.t`."""

    def repl(m: re.Match[str]) -> str:
        return f"{name}.{m.group(1).lower()}"

    return repl


def condition_st(blk: XBlock, flgnet: object, names: dict[int, str], lang: str = "LAD") -> str:
    """Сеть условия GRAPH → выражение ST CODESYS (ссылки `#Шаг.T` → `Шаг.t`, неявная переменная SFC)."""
    net = build_network(flgnet, 0, lang)  # type: ignore[arg-type]
    for acc in net.accesses.values():
        for name in names.values():
            acc.text = re.sub(rf'#"?{re.escape(name)}"?\.(X|T)\b', _implicit_ref(name), acc.text)
    bl = BlockLower(block=blk, lang="GRAPH")
    lowerer = NetLowerer(bl, net)
    lowerer.cond_target = "@cond"
    for uid, part in net.parts.items():
        if part.name not in _PURE:
            lowerer.emit_part(uid)
    lines = [ln.text for ln in lowerer.lines if not ln.text.lstrip().startswith("//")]
    if len(lines) != 1 or not lines[0].startswith("@cond := "):
        raise SfcError("условие не сводится к одному выражению")
    return _strip_hash(lines[0][len("@cond := ") :].rstrip(";"))


def _strip_hash(text: str) -> str:
    """`#имя` → `имя`; `#` литералов (T#2S, 16#FF) остаётся."""
    return re.sub(r"(?<![A-Za-z0-9_])#", "", text)


def _st(text: str) -> str:
    """Текст SCL действия → ST CODESYS (имена без #)."""
    return _strip_hash(text).strip()


# ---------------------------------------------------------------------------
# PLCopen XML
# ---------------------------------------------------------------------------


class _Ids:
    def __init__(self) -> None:
        self.n = 0

    def next(self) -> int:
        self.n += 1
        return self.n


def _vars_xml(tag: str, variables: list[Var], ind: str) -> list[str]:
    if not variables:
        return []
    out = [f"{ind}<{tag}>"]
    for v in variables:
        out.append(f'{ind}  <variable name="{v.name}">')
        kind = f"<{v.type} />" if v.type in _TYPES.values() else f'<derived name="{v.type}" />'
        out.append(f"{ind}    <type>{kind}</type>")
        if v.init:
            out.append(f"{ind}    <initialValue><simpleValue value={quoteattr(v.init)} /></initialValue>")
        if v.comment:
            out.append(f'{ind}    <documentation><xhtml xmlns="{XHTML}">{escape(v.comment)}</xhtml></documentation>')
        out.append(f"{ind}  </variable>")
    out.append(f"{ind}</{tag}>")
    return out


def _cp_in(sources: list[int], ind: str) -> str:
    if not sources:
        return f"{ind}<connectionPointIn />"
    conns = "".join(f'<connection refLocalId="{s}" />' for s in sources)
    return f"{ind}<connectionPointIn>{conns}</connectionPointIn>"


def build_sfc(blk: XBlock) -> tuple[str, str, list[Var], list[Var], list[Var], list[str]]:
    """GRAPH → (тело SFC, тело обёртки ST, входы SFC, выходы SFC, переменные обёртки, пометки)."""
    units = [u for u in blk.units if u.body is not None]
    if len(units) != 1 or units[0].body_kind != "Graph":
        raise SfcError("в блоке не одна сеть GRAPH")
    graph: Graph = parse_graph(units[0].body)  # type: ignore[arg-type]
    if len(graph.sequences) != 1:
        raise SfcError("последовательностей не одна")
    seq: Sequence = graph.sequences[0]
    topo = topology(seq)
    if topo.issues:
        raise SfcError("; ".join(topo.issues))
    names = {s.number: _ident(s) for s in seq.steps}
    members = {m.name.upper(): m for s in blk.sections for m in s.members}
    notes: list[str] = []
    if graph.pre:
        raise SfcError("предоперации в варианте SFC не переносятся")
    limited = [f"S{s.number}" for s in seq.steps if s.max_time or s.warn_time]
    if limited:
        raise SfcError(f"предел времени шага ({', '.join(limited)}) в варианте SFC не переносится")
    sv_err = {s.number: f"{names[s.number]}_SvErr" for s in seq.steps if s.supervision is not None}
    # входы SFC: входы блока, которые читают условия переходов, и защёлки контроля
    sfc_in: list[Var] = [Var("SFCInit", "BOOL", comment="INIT_SQ: начальное состояние (флаг SFC)")]
    user_inputs = [
        m
        for s in blk.sections
        if s.name == "Input"
        for m in s.members
        if m.name.upper() not in ("INIT_SQ", "OFF_SQ", "ACK_EF")
    ]
    for m in user_inputs:
        sfc_in.append(Var(m.name, iec_type(m.datatype), m.start_value or "", m.comment))
    for n, var in sv_err.items():
        sfc_in.append(Var(var, "BOOL", comment=f"шаг S{n}: ошибка контроля (защёлка обёртки)"))
    sfc_out: list[Var] = []
    ids = _Ids()
    elements: list[str] = []
    ind = "            "
    # идентификаторы узлов
    step_id = {s.number: ids.next() for s in seq.steps}
    trans_id = {t.number: ids.next() for t in seq.transitions}
    branch_id = {b.number: ids.next() for b in seq.branches}
    branch_type = {b.number: b.type for b in seq.branches}

    def node_id(kind: str, number: int) -> int:
        return {"S": step_id, "T": trans_id, "B": branch_id}[kind][number]

    incoming: dict[tuple[str, int], list[int]] = {}
    jumps: list[tuple[int, str]] = []  # (переход, шаг-цель)
    for c in seq.connections:
        if c.link == "Jump" and c.src.kind == "T" and c.dst.kind == "S":
            jumps.append((c.src.number, names[c.dst.number]))
            continue
        if c.dst.kind == "END" or c.src.kind == "END":
            continue
        incoming.setdefault((c.dst.kind, c.dst.number), []).append(node_id(c.src.kind, c.src.number))
    # шаги и их действия
    wrap: list[str] = []
    writers: dict[str, list[tuple[str, str]]] = {}  # операнд → [(флаг в обёртке, блокировка)]
    has_init = "INIT_SQ" in members

    def ref(st: SeqStep, flag: str, kind: str) -> str:
        """Флаг действия в обёртке. Пока INIT_SQ, SFC (SFCInit) не выполняется: начальный шаг считается
        активным (N, S, R, контроль), остальные — выключенными, как у ST-двойника."""
        text = f"fbSfc.{flag}"
        if not has_init:
            return text
        if not st.init:
            return f"({text} AND NOT INIT_SQ)"
        if kind in ("N", "S", "R", "Active"):
            return f"({text} OR INIT_SQ)"
        notes.append(f"S{st.number}: действие {kind} начального шага при INIT_SQ — по флагу SFC (SFCInit)")
        return text

    for st in seq.steps:
        n = st.number
        sid = step_id[n]
        init = ' initialStep="true"' if st.init else ""
        elements += [
            f'{ind}<step localId="{sid}" name="{names[n]}"{init}>',
            f'{ind}  <position x="0" y="0" />',
            _cp_in(incoming.get(("S", n), []), ind + "  "),
            f'{ind}  <connectionPointOut formalParameter="sfc" />',
            f"{ind}</step>",
        ]
        il_expr = condition_st(blk, st.interlock, names) if st.interlock is not None else ""
        actions: list[tuple[str, str, str]] = []  # (квалификатор IEC, флаг, длительность)
        for a in st.actions:
            q = a.qualifier.upper()
            iec = "P" if a.event == "S1" else q if q in ("D", "L") else "N"
            flag = f"x{names[n]}_{q or 'N'}{a.index}" if iec == "N" else f"x{names[n]}_{iec}{a.index}"
            ilk = il_expr if a.interlock else ""
            if a.event == "S1" and q == "N" and not a.operand:
                actions.append(("P", flag, ""))
                wrap.append(f"IF {ref(st, flag, 'P')} THEN // S{n}: событие S1")
                wrap.append(f"    {_st(a.text)}")
                wrap.append("END_IF")
            elif a.event:
                raise SfcError(f"S{n}: событие {a.event} {q} в варианте SFC не переносится")
            elif q == "N" and a.operand:
                actions.append(("N", flag, ""))
                writers.setdefault(_st(a.operand), []).append((ref(st, flag, "N"), ilk))
            elif q in ("S", "R") and a.operand:
                actions.append(("N", flag, ""))
                cond = ref(st, flag, q) + (f" AND ({ilk})" if ilk else "")
                value = "TRUE" if q == "S" else "FALSE"
                wrap.append(f"IF {cond} THEN // S{n}: {q} {_st(a.operand)}")
                wrap.append(f"    {_st(a.operand)} := {value};")
                wrap.append("END_IF")
            elif q in ("D", "L") and a.operand and a.time:
                actions.append((q, flag, a.time))
                writers.setdefault(_st(a.operand), []).append((ref(st, flag, q), ilk))
            elif q == "N":
                raise SfcError(f"S{n}: инструкция без события (N) в варианте SFC не переносится")
            else:
                raise SfcError(f"S{n}: действие {q} в варианте SFC не переносится")
        if st.supervision is not None:
            actions.append(("N", f"x{names[n]}_Active", ""))
        if actions:
            bid = ids.next()
            elements += [
                f'{ind}<actionBlock localId="{bid}">',
                f'{ind}  <position x="0" y="0" />',
                f'{ind}  <connectionPointIn><connection refLocalId="{sid}" /></connectionPointIn>',
            ]
            for q, flag, duration in actions:
                aid = ids.next()
                dur = f' duration="{duration}"' if duration else ""
                elements += [
                    f'{ind}  <action localId="{aid}" qualifier="{q}"{dur}>',
                    f'{ind}    <relPosition x="0" y="0" />',
                    f'{ind}    <reference name="{flag}" />',
                    f"{ind}  </action>",
                ]
                sfc_out.append(Var(flag, "BOOL", comment=f"шаг S{n}: действие {q}"))
            elements.append(f"{ind}</actionBlock>")
    # переходы
    for link in topo.links:
        tr = seq.transition(link.number)
        tid = trans_id[link.number]
        if tr.net is None:
            raise SfcError(f"T{link.number}: нет сети условия")
        expr = condition_st(blk, tr.net, names, tr.lang)
        blocks = [f"NOT {sv_err[p]}" for p in link.preds if p in sv_err]
        if blocks:
            expr = f"({expr}) AND " + " AND ".join(blocks)
        vid = ids.next()
        elements += [
            f'{ind}<inVariable localId="{vid}">',
            f'{ind}  <position x="0" y="0" />',
            f"{ind}  <connectionPointOut />",
            f"{ind}  <expression>{escape(expr)}</expression>",
            f"{ind}</inVariable>",
            f'{ind}<transition localId="{tid}">',
            f'{ind}  <position x="0" y="0" />',
            _cp_in(incoming.get(("T", link.number), []), ind + "  "),
            f"{ind}  <connectionPointOut />",
            f'{ind}  <condition><connectionPointIn><connection refLocalId="{vid}" /></connectionPointIn></condition>',
            f"{ind}</transition>",
        ]
    # ветви
    tags = {
        "AltBegin": "selectionDivergence",
        "AltEnd": "selectionConvergence",
        "SimBegin": "simultaneousDivergence",
        "SimEnd": "simultaneousConvergence",
    }
    for b in seq.branches:
        tag = tags.get(b.type)
        if tag is None:
            raise SfcError(f"ветвь {b.type} не поддерживается")
        bid = branch_id[b.number]
        srcs = incoming.get(("B", b.number), [])
        elements += [f'{ind}<{tag} localId="{bid}">', f'{ind}  <position x="0" y="0" />']
        if b.type.endswith("End"):
            elements += [_cp_in([s], ind + "  ") for s in srcs]
            elements.append(f"{ind}  <connectionPointOut />")
        else:
            elements.append(_cp_in(srcs, ind + "  "))
            elements += [f'{ind}  <connectionPointOut formalParameter="{k}" />' for k in range(b.cardinality)]
        elements.append(f"{ind}</{tag}>")
    for tr_number, target in jumps:
        jid = ids.next()
        elements += [
            f'{ind}<jumpStep localId="{jid}" targetName="{target}">',
            f'{ind}  <position x="0" y="0" />',
            f'{ind}  <connectionPointIn><connection refLocalId="{trans_id[tr_number]}" /></connectionPointIn>',
            f"{ind}</jumpStep>",
        ]
    del branch_type
    # обёртка: операнды N/D/L — по флагам (несколько шагов — ИЛИ), затем контроль и постоперации
    body: list[str] = [
        "// Квитирование ошибок контроля (ACK_EF) и INIT_SQ — до вызова SFC: в этом цикле переход возможен"
    ]
    clears = [name for name in ("ACK_EF", "INIT_SQ") if name in members]
    if sv_err and clears:
        body.append(f"IF {' OR '.join(clears)} THEN")
        body += [f"    {var} := FALSE;" for var in sv_err.values()]
        body.append("END_IF")
    if "OFF_SQ" in members:
        notes.append("OFF_SQ: в SFC нет выключения всех шагов — вход обёртки не используется")
    args = ["SFCInit := INIT_SQ"] if "INIT_SQ" in members else ["SFCInit := FALSE"]
    args += [f"{m.name} := {m.name}" for m in user_inputs]
    args += [f"{var} := {var}" for var in sv_err.values()]
    body += _wrap_call("fbSfc", args)
    body.append("// Действия GRAPH по флагам IEC-действий SFC")
    order = []
    for st in seq.steps:
        for a in st.actions:
            if a.operand and not a.event and a.qualifier.upper() in ("N", "D", "L"):
                op = _st(a.operand)
                if op not in order:
                    order.append(op)
    for op in order:
        terms = [flag + (f" AND ({ilk})" if ilk else "") for flag, ilk in writers[op]]
        body.append(f"{op} := {' OR '.join(terms)};")
    body += wrap
    if sv_err:
        body.append("// Контроль шагов: ошибка защёлкивается до ACK_EF")
        for st in seq.steps:
            if st.supervision is not None:
                expr = condition_st(blk, st.supervision, names)
                body.append(f"IF {ref(st, f'x{names[st.number]}_Active', 'Active')} AND ({expr}) THEN")
                body.append(f"    {sv_err[st.number]} := TRUE;")
                body.append("END_IF")
        if "ERR_FLT" in members:
            body.append(f"ERR_FLT := {' OR '.join(sv_err.values())};")
    for k, (net, lang) in enumerate(graph.post, start=1):
        body.append(f"// Постоперация {k}")
        body += _plain_st(blk, net, lang)
    wrapper_vars = [Var("fbSfc", f"{blk.name}_Sfc", comment="последовательность SFC")]
    wrapper_vars += [Var(var, "BOOL", comment=f"шаг S{n}: ошибка контроля") for n, var in sv_err.items()]
    return "\n".join(elements), "\n".join(body), sfc_in, sfc_out, wrapper_vars, notes


def _wrap_call(name: str, args: list[str], width: int = 110) -> list[str]:
    """Вызов `name(a := a, b := b, …);` по строкам не длиннее width, продолжение — под первым аргументом."""
    lines: list[str] = []
    cur = f"{name}("
    for i, arg in enumerate(args):
        piece = arg + ("," if i < len(args) - 1 else ");")
        if cur.endswith("("):
            cur += piece
        elif len(cur) + 1 + len(piece) > width:
            lines.append(cur)
            cur = " " * (len(name) + 1) + piece
        else:
            cur += " " + piece
    if not args:
        cur += ");"
    lines.append(cur)
    return lines


def _plain_st(blk: XBlock, flgnet: object, lang: str) -> list[str]:
    net = build_network(flgnet, 0, lang)  # type: ignore[arg-type]
    bl = BlockLower(block=blk, lang="GRAPH")
    lowerer = NetLowerer(bl, net)
    for uid, part in net.parts.items():
        if part.name not in _PURE:
            lowerer.emit_part(uid)
    if bl.temps:
        raise SfcError("постоперация с временными переменными в варианте SFC не переносится")
    return [_strip_hash(ln.text) for ln in lowerer.lines if not ln.text.lstrip().startswith("//")]


def _interface(name: str, kind: str, sections: dict[str, list[Var]], ind: str) -> list[str]:
    out = [f"{ind}<interface>"]
    for tag in ("inputVars", "outputVars", "inOutVars", "localVars"):
        out += _vars_xml(tag, sections.get(tag, []), ind + "  ")
    out.append(f"{ind}</interface>")
    del name, kind
    return out


def sfc_project(blk: XBlock, source: str) -> SfcResult:
    """Проект PLCopen: POU SFC `<Блок>_Sfc` и ФБ-обёртка `<Блок>` на ST с интерфейсом блока GRAPH."""
    sfc_body, wrapper_body, sfc_in, sfc_out, wrapper_locals, notes = build_sfc(blk)
    ind = "      "
    sections = {"Input": "inputVars", "Output": "outputVars", "InOut": "inOutVars"}
    wrapper_sections: dict[str, list[Var]] = {"localVars": wrapper_locals}
    for sec in blk.sections:
        tag = sections.get(sec.name)
        if tag is None:
            continue
        wrapper_sections.setdefault(tag, [])
        for m in sec.members:
            wrapper_sections[tag].append(Var(m.name, iec_type(m.datatype), m.start_value or "", m.comment))
    sfc_name = f"{blk.name}_Sfc"
    head = (
        f"// Сгенерировано s7conv из {source} (S7-GRAPH, стратегия sfc):"
        + chr(10)
        + f"// SFC {sfc_name} и обёртка {blk.name} с интерфейсом блока GRAPH."
    )
    out = [
        '<?xml version="1.0" encoding="utf-8"?>',
        f'<project xmlns="{NS}">',
        '  <fileHeader companyName="s7-to-codesys" productName="s7conv" productVersion="1.2.0" '
        'creationDateTime="2026-10-20T00:00:00" />',
        f'  <contentHeader name="{blk.name}">',
        "    <coordinateInfo>",
        '      <fbd><scaling x="1" y="1" /></fbd>',
        '      <ld><scaling x="1" y="1" /></ld>',
        '      <sfc><scaling x="1" y="1" /></sfc>',
        "    </coordinateInfo>",
        "  </contentHeader>",
        "  <types>",
        "    <dataTypes />",
        "    <pous>",
        f'{ind}<pou name="{sfc_name}" pouType="functionBlock">',
        *_interface(sfc_name, "sfc", {"inputVars": sfc_in, "outputVars": sfc_out}, ind + "  "),
        f"{ind}  <body>",
        f"{ind}    <SFC>",
        sfc_body,
        f"{ind}    </SFC>",
        f"{ind}  </body>",
        f"{ind}  <addData>",
        f'{ind}    <data name="http://www.3s-software.com/plcopenxml/sfcsettings" handleUnknown="implementation">',
        f"{ind}      <SFCSettings>",
        f"{ind}        <Flags>",
        f'{ind}          <Init Declare="false" Use="true" />',
        f"{ind}        </Flags>",
        f"{ind}      </SFCSettings>",
        f"{ind}    </data>",
        f"{ind}  </addData>",
        f"{ind}</pou>",
        f'{ind}<pou name="{blk.name}" pouType="functionBlock">',
        *_interface(blk.name, "wrapper", wrapper_sections, ind + "  "),
        f"{ind}  <body>",
        f'{ind}    <ST><xhtml xmlns="{XHTML}">{escape(head + chr(10) + wrapper_body)}</xhtml></ST>',
        f"{ind}  </body>",
        f"{ind}</pou>",
        "    </pous>",
        "  </types>",
        "  <instances><configurations /></instances>",
        "</project>",
        "",
    ]
    return SfcResult("\n".join(out), notes)


__all__ = ["NS", "SfcError", "SfcResult", "Var", "build_sfc", "condition_st", "iec_type", "sfc_project"]
