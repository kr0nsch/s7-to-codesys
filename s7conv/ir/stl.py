"""StlIR: список инструкций STL S7 независимо от мнемоники.

Код операции — имя `StlToken` из XSD V21 (`SW.PlcBlocks.STL_v5.xsd`, 172 значения): `A`, `AN`, `A_BRACK`,
`Assign`, `JCN`, `ADD_I` ... XML даёт его напрямую, разборщик AWL переводит мнемонику EN/DE в те же имена
(docs/GRAMMAR.md, раздел AWL). Поэтому XML, AWL-EN и AWL-DE дают один и тот же StlIR.

Операнд — текст SCL (`#x`, `"DB".y`, `16#FF`, `T#2S`, `%M10.0`), метка перехода — имя, вызов — StlCall.
Трасса инструкции — номер сети и строки в ней (у STL в SimaticML нет UId).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

from s7conv.frontends.simaticml import _first, access_text, child, children, local, symbol_text, text_of


@dataclass
class StlCall:
    """CALL: пользовательский блок (CallInfo) или инструкция (Instruction: TON, TOF ...)."""

    name: str
    kind: str  # FB | FC | Instruction | SFB | SFC
    instance: str = ""  # #inst или "IDB"
    instance_scope: str = ""
    templates: dict[str, str] = field(default_factory=dict)
    params: list[tuple[str, str, str, str | None]] = field(default_factory=list)  # (имя, секция, тип, операнд)


@dataclass
class StlInstr:
    index: int
    network: int
    line: int  # строка в сети, с 1
    token: str  # имя StlToken XSD
    operand: str | None = None
    operand_scope: str = ""  # LocalVariable | GlobalVariable | LiteralConstant | TypedConstant | Label | ...
    label: str | None = None  # метка, объявленная на этой строке
    call: StlCall | None = None
    comment: str = ""
    extra: str = ""  # NOP 0/1, L STW: второй токен

    @property
    def trace(self) -> str:
        return f"сеть {self.network}, строка {self.line}"


@dataclass
class StlNetwork:
    number: int
    title: str = ""
    comment: str = ""
    start: int = 0  # индекс первой инструкции в StlBlock.instrs
    end: int = 0  # индекс после последней


@dataclass
class StlBlock:
    """Все сети STL блока подряд: состояние машины S7-300 (слово состояния, ACCU) переходит между сетями."""

    instrs: list[StlInstr] = field(default_factory=list)
    networks: list[StlNetwork] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)

    def labels(self) -> dict[str, int]:
        return {ins.label: ins.index for ins in self.instrs if ins.label}


def _call(el: ET.Element) -> StlCall:
    kind = local(el.tag)
    call = StlCall(name=el.get("Name", ""), kind="Instruction" if kind == "Instruction" else el.get("BlockType", "FC"))
    instance = child(el, "Instance")
    if instance is not None:
        call.instance_scope = instance.get("Scope", "")
        call.instance = symbol_text(instance, call.instance_scope)
    call.templates = {t.get("Name", ""): text_of(t) for t in children(el, "TemplateValue")}
    for p in children(el, "Parameter"):
        acc = child(p, "Access")
        call.params.append(
            (p.get("Name", ""), p.get("Section", ""), p.get("Type", ""), access_text(acc) if acc is not None else None)
        )
    return call


def _line_comment(el: ET.Element) -> str:
    texts = []
    for lc in children(el, "LineComment"):
        texts.append("".join((t.text or "") for t in lc if local(t.tag) == "Text").strip())
    return " ".join(t for t in texts if t)


def add_statement_list(block: StlBlock, el: ET.Element, number: int, title: str = "", comment: str = "") -> None:
    """StatementList одной сети → инструкции StlBlock (в конец)."""
    net = StlNetwork(number=number, title=title, comment=comment, start=len(block.instrs))
    for line, st in enumerate(children(el, "StlStatement"), start=1):
        token_el = child(st, "StlToken")
        token = token_el.get("Text", "") if token_el is not None else "EMPTY_LINE"
        ins = StlInstr(index=len(block.instrs), network=number, line=line, token=token)
        if token_el is not None:
            sub = child(token_el, "Token")
            if sub is not None:
                ins.extra = sub.get("Text", "")
        decl = child(st, "LabelDeclaration")
        if decl is not None:
            label = child(decl, "Label")
            if label is not None:
                ins.label = label.get("Name", "")
        acc = child(st, "Access")
        if acc is not None:
            ins.operand_scope = acc.get("Scope", "")
            call = _first(child(acc, "CallInfo"), child(acc, "Instruction"))
            if call is not None:
                ins.call = _call(call)
                ins.operand = ins.call.name
            else:
                ins.operand = access_text(acc)
        ins.comment = _line_comment(st)
        if token_el is not None:
            ins.comment = (ins.comment + " " + _line_comment(token_el)).strip()
        block.instrs.append(ins)
    net.end = len(block.instrs)
    block.networks.append(net)


__all__ = ["StlBlock", "StlCall", "StlInstr", "StlNetwork", "add_statement_list"]
