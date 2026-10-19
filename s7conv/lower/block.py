"""Блок SimaticML → текст SCL (интерфейс + понижённые сети) с трассой строк и пометками понижения.

Результат разбирает parser.py 1.0.0: дальше блок идёт по пути SCL (эмиттер, отчёт, генератор тестов).
Для каждой строки синтезированного текста известно, откуда она: «интерфейс, Input.xStart»,
«сеть 3, UId 27», «сеть 2 (SCL), строка 4». Номера строк — ключи Lowering.trace и Lowering.notes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from s7conv.frontends.simaticml import XBlock, XDocument, XMember, XUnit, tokens_text
from s7conv.ir.net import build_network
from s7conv.lower.common import AUTO, CHECK, TODO, BlockLower, LLine
from s7conv.lower.net_to_ast import lower_networks
from s7conv.nodes import Lowering, LowerNote

LANG_NAMES = {"LAD_IEC": "LAD", "FBD_IEC": "FBD"}
_SECTION_KW = {
    "Input": "VAR_INPUT",
    "Output": "VAR_OUTPUT",
    "InOut": "VAR_IN_OUT",
    "Static": "VAR",
    "Temp": "VAR_TEMP",
    "Constant": "VAR CONSTANT",
}
_BLOCK_KW = {
    "FB": "FUNCTION_BLOCK",
    "FC": "FUNCTION",
    "OB": "ORGANIZATION_BLOCK",
    "GlobalDB": "DATA_BLOCK",
    "InstanceDB": "DATA_BLOCK",
    "ArrayDB": "DATA_BLOCK",
    "PlcStruct": "TYPE",
}
KIND_LABEL = {
    "FB": "SW.Blocks.FB",
    "FC": "SW.Blocks.FC",
    "OB": "SW.Blocks.OB",
    "GlobalDB": "SW.Blocks.GlobalDB",
    "InstanceDB": "SW.Blocks.InstanceDB",
    "ArrayDB": "SW.Blocks.ArrayDB",
    "PlcStruct": "SW.Types.PlcStruct",
}


@dataclass
class LowerOptions:
    cpu: str | None = None  # s7-300 | s7-1500 | None (выводится из MemoryLayout)
    stl_jumps: str = "structured"  # structured | pc


@dataclass
class _Out:
    lines: list[LLine] = field(default_factory=list)

    def add(self, text: str, trace: str, notes: list[LowerNote] | None = None) -> None:
        self.lines.append(LLine(text, trace, notes or []))


def block_lang(blk: XBlock) -> str:
    lang = LANG_NAMES.get(blk.lang.upper(), blk.lang.upper())
    if blk.kind in ("GlobalDB", "InstanceDB", "ArrayDB"):
        return "DB"
    if blk.kind == "PlcStruct":
        return "UDT"
    return lang or "LAD"


def profile_of(blk: XBlock, options: LowerOptions) -> tuple[str, list[LowerNote]]:
    """Профиль CPU: явный --cpu или по MemoryLayout (Optimized — S7-1200/1500)."""
    optimized = blk.memory_layout.lower() == "optimized"
    if options.cpu is None:
        return ("s7-1500" if optimized else "s7-300"), []
    notes = []
    if options.cpu == "s7-300" and optimized:
        notes.append(
            LowerNote(
                CHECK,
                "xml.profile_mismatch",
                "блок с оптимизированным доступом (S7-1200/1500), а профиль --cpu s7-300",
            )
        )
    return options.cpu, notes


def _comment_lines(text: str, prefix: str = "//") -> list[str]:
    return [f"{prefix}{line}".rstrip() for line in text.splitlines() if line.strip()]


def _member_lines(m: XMember, ind: str, trace: str, out: _Out) -> None:
    comment = f"   // {m.comment}" if m.comment else ""
    if m.datatype.lower() == "struct" or (m.members and m.datatype.lower().startswith("struct")):
        out.add(f"{ind}{m.name} : Struct{comment}", trace)
        for sub in m.members:
            _member_lines(sub, ind + "   ", f"{trace}.{sub.name}", out)
        out.add(f"{ind}END_STRUCT;", trace)
        return
    init = f" := {m.start_value}" if m.start_value not in (None, "") else ""
    out.add(f"{ind}{_name(m.name)} : {m.datatype}{init};{comment}", trace)


def _name(name: str) -> str:
    return name if name.replace("_", "a").isalnum() and not name[0].isdigit() else f'"{name}"'


def _interface(blk: XBlock, out: _Out, temps: list[tuple[str, str, str]]) -> None:
    temps_done = False
    for sec in blk.sections:
        if sec.name in ("Return", "None", "Base") or (not sec.members and sec.name != "Temp"):
            continue
        kw = _SECTION_KW.get(sec.name)
        if kw is None:
            continue
        groups: list[tuple[str, list[XMember]]]
        if sec.name == "Static":
            plain = [m for m in sec.members if m.remanence != "Retain"]
            retain = [m for m in sec.members if m.remanence == "Retain"]
            groups = [(kw, plain), ("VAR RETAIN", retain)]
        else:
            groups = [(kw, sec.members)]
        for keyword, members in groups:
            extra = temps if sec.name == "Temp" else []
            temps_done = temps_done or sec.name == "Temp"
            if not members and not extra:
                continue
            out.add(f"   {keyword}", f"интерфейс, {sec.name}")
            for m in members:
                _member_lines(m, "      ", f"интерфейс, {sec.name}.{m.name}", out)
            for name, typ, comment in extra:
                out.add(f"      {name} : {typ};   // {comment}", "временные понижения")
            out.add("   END_VAR", f"интерфейс, {sec.name}")
    if temps and not temps_done:
        out.add("   VAR_TEMP", "временные понижения")
        for name, typ, comment in temps:
            out.add(f"      {name} : {typ};   // {comment}", "временные понижения")
        out.add("   END_VAR", "временные понижения")


def _scl_unit(bl: BlockLower, unit: XUnit) -> None:
    assert unit.body is not None
    text = tokens_text(unit.body)
    title = f": {unit.title}" if unit.title else ""
    bl.emit(f"// Сеть {unit.number} (SCL){title}", f"сеть {unit.number} (SCL)")
    for n, line in enumerate(text.splitlines(), start=1):
        bl.emit(line, f"сеть {unit.number} (SCL), строка {n}")
    bl.unit("network", AUTO, "scl.network", f"сеть {unit.number} (SCL)")


def _empty_unit(bl: BlockLower, unit: XUnit) -> None:
    title = f": {unit.title}" if unit.title else ""
    bl.emit(f"// Сеть {unit.number}{title} — пустая", f"сеть {unit.number}")


def lower_block(blk: XBlock, registry: dict[str, XBlock], options: LowerOptions) -> tuple[list[LLine], BlockLower]:
    """Блок → строки SCL (с трассой); BlockLower — единицы учёта, пометки, объекты поддержки."""
    lang = block_lang(blk)
    profile, profile_notes = profile_of(blk, options)
    bl = BlockLower(block=blk, lang=lang, registry=registry, profile=profile, stl_jumps=options.stl_jumps)
    bl.block_notes.extend(profile_notes)
    kw = _BLOCK_KW[blk.kind]
    out = _Out()
    head_trace = f"{KIND_LABEL[blk.kind]} «{blk.name}»"
    if blk.kind in ("FB", "FC", "OB"):
        _lower_body(bl)
    # заголовок
    ret = ""
    if blk.kind == "FC":
        ret_sec = blk.section("Return")
        ret_type = ret_sec.members[0].datatype if ret_sec and ret_sec.members else "Void"
        ret = f" : {ret_type}"
    if blk.kind == "PlcStruct":
        out.add(f'TYPE "{blk.name}"', head_trace)
    else:
        out.add(f'{kw} "{blk.name}"{ret}', head_trace)
    if blk.title:
        out.add(f"TITLE = {blk.title}", head_trace)
    if blk.memory_layout:
        optimized = "TRUE" if blk.memory_layout.lower() == "optimized" else "FALSE"
        out.add(f"{{ S7_Optimized_Access := '{optimized}' }}", head_trace)
    if blk.author:
        out.add(f"AUTHOR : {blk.author}", head_trace)
    if blk.family:
        out.add(f"FAMILY : {blk.family}", head_trace)
    out.add(f"VERSION : {blk.version or '0.1'}", head_trace)
    for comment_line in _comment_lines(blk.comment):
        out.add(comment_line, head_trace)
    if blk.kind == "PlcStruct":
        out.add("   STRUCT", head_trace)
        for sec in blk.sections:
            for m in sec.members:
                _member_lines(m, "      ", f"тип, {m.name}", out)
        out.add("   END_STRUCT;", head_trace)
        out.add("END_TYPE", head_trace)
        return out.lines, bl
    if blk.kind == "InstanceDB":
        out.add(f'"{blk.instance_of}"', head_trace)
        out.add("BEGIN", head_trace)
        out.add("END_DATA_BLOCK", head_trace)
        return out.lines, bl
    temps = [(t.name, t.type, t.comment) for t in bl.temps]
    _interface(blk, out, temps)
    out.add("BEGIN", head_trace)
    if blk.kind in ("FB", "FC", "OB"):
        first = True
        for line in bl.lines:
            notes = list(line.notes)
            if first and bl.block_notes and line.text.strip() and not line.text.strip().startswith("//"):
                notes = bl.block_notes + notes
                first = False
            out.lines.append(LLine(line.text if not line.text else "   " + line.text, line.trace, notes))
        if first and bl.block_notes:
            out.add("   ;", head_trace, list(bl.block_notes))
    end = {"FB": "END_FUNCTION_BLOCK", "FC": "END_FUNCTION", "OB": "END_ORGANIZATION_BLOCK"}.get(
        blk.kind, "END_DATA_BLOCK"
    )
    out.add(end, head_trace)
    return out.lines, bl


def _lower_body(bl: BlockLower) -> None:
    """Сети блока по языкам: подряд идущие сети LAD/FBD понижаются вместе (прыжки между сетями)."""
    from s7conv.lower.stl_lift import lower_stl_units

    blk = bl.block
    group: list[XUnit] = []
    stl_group: list[XUnit] = []

    def flush() -> None:
        if group:
            lower_networks(
                bl, [build_network(u.body, u.number, u.lang, u.title, u.comment) for u in group if u.body is not None]
            )
            group.clear()
        if stl_group:
            lower_stl_units(bl, list(stl_group))
            stl_group.clear()

    for unit in blk.units:
        kind = unit.body_kind
        if kind == "FlgNet":
            if stl_group:
                flush()
            group.append(unit)
            continue
        if kind == "StatementList":
            if group:
                flush()
            stl_group.append(unit)
            continue
        flush()
        if kind == "StructuredText":
            _scl_unit(bl, unit)
        elif not kind:
            _empty_unit(bl, unit)
        else:
            note = LowerNote(
                TODO, "xml.unit_unsupported", f"сеть {unit.number}: язык {unit.lang} ({kind}) не поддерживается"
            )
            bl.emit(f'"{kind}"(); // сеть {unit.number}, {unit.lang}', f"сеть {unit.number}", [note])
            bl.unit("network", TODO, "xml.unit_unsupported", f"сеть {unit.number}")
    flush()


def lower_document(
    doc: XDocument, registry: dict[str, XBlock], options: LowerOptions
) -> tuple[str, Lowering, set[str]]:
    """Документ → (текст SCL, происхождение строк, объекты поддержки S7Compat)."""
    lowering = Lowering(source_kind="simaticml")
    texts: list[str] = []
    support: set[str] = set()
    for blk in doc.blocks:
        lines, bl = lower_block(blk, registry, options)
        support |= bl.support
        lowering.langs[blk.name.lower()] = bl.lang
        lowering.strategies[blk.name.lower()] = "st"
        version = f", пространство имён {blk.interface_ns}" if blk.interface_ns else ""
        lowering.origin[blk.name.lower()] = f'{bl.lang}, {KIND_LABEL[blk.kind]} "{blk.name}"{version}'
        lowering.units.extend(bl.units)
        for line in lines:
            texts.append(line.text)
            n = len(texts)
            lowering.trace[n] = line.trace
            if line.notes:
                lowering.notes[n] = list(line.notes)
        texts.append("")
    return "\n".join(texts), lowering, support


__all__ = ["KIND_LABEL", "LANG_NAMES", "LowerOptions", "block_lang", "lower_block", "lower_document", "profile_of"]
