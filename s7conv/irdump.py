"""`s7conv ir <файл> --format json` — дамп промежуточного представления SimaticML с трассой.

Для каждого блока: интерфейс (секции и члены) и сети: LAD/FBD — NetIR (операнды и элементы с UId, провода
«источник → приёмники»), STL — StlIR (инструкции с номером сети и строки, токен XSD, операнд, метка,
вызов), SCL — текст сети. Вывод детерминирован (сортировка ключей, LF).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from s7conv.frontends.simaticml import XBlock, XUnit, parse_document, tokens_text
from s7conv.ir.net import End, build_network
from s7conv.ir.stl import StlBlock, add_statement_list
from s7conv.pipeline import display_path, read_source


def _end(e: End) -> dict[str, Any]:
    if e.kind == "rail":
        return {"kind": "rail"}
    if e.kind == "pin":
        return {"kind": "pin", "uid": e.uid, "pin": e.pin}
    return {"kind": e.kind, "uid": e.uid}


def _unit(unit: XUnit) -> dict[str, Any]:
    base: dict[str, Any] = {"network": unit.number, "lang": unit.lang, "title": unit.title, "kind": unit.body_kind}
    if unit.body is None:
        return base
    if unit.body_kind == "FlgNet":
        net = build_network(unit.body, unit.number, unit.lang, unit.title)
        base["accesses"] = [
            {"uid": a.uid, "scope": a.scope, "text": a.text, "trace": f"сеть {unit.number}, UId {a.uid}"}
            for a in net.accesses.values()
        ]
        base["parts"] = [
            {
                "uid": p.uid,
                "name": p.name,
                "negated": sorted(p.negated),
                "templates": p.templates,
                "instance": p.instance,
                "call": (
                    {"name": p.call.name, "type": p.call.block_type, "params": [list(x) for x in p.call.params]}
                    if p.call
                    else None
                ),
                "trace": f"сеть {unit.number}, UId {p.uid}",
            }
            for p in net.parts.values()
        ]
        base["wires"] = [{"uid": w.uid, "from": _end(w.source), "to": [_end(s) for s in w.sinks]} for w in net.wires]
        base["labels"] = net.labels
        base["issues"] = net.issues
    elif unit.body_kind == "StatementList":
        block = StlBlock()
        add_statement_list(block, unit.body, unit.number, unit.title)
        base["instructions"] = [
            {
                "line": i.line,
                "token": i.token,
                "operand": i.operand,
                "scope": i.operand_scope,
                "label": i.label,
                "call": (
                    {
                        "name": i.call.name,
                        "kind": i.call.kind,
                        "instance": i.call.instance,
                        "params": [list(x) for x in i.call.params],
                    }
                    if i.call
                    else None
                ),
                "trace": i.trace,
            }
            for i in block.instrs
        ]
    elif unit.body_kind == "StructuredText":
        base["text"] = tokens_text(unit.body)
    return base


def _block(blk: XBlock) -> dict[str, Any]:
    return {
        "kind": blk.kind,
        "name": blk.name,
        "number": blk.number,
        "lang": blk.lang,
        "memory_layout": blk.memory_layout,
        "interface_namespace": blk.interface_ns,
        "sections": [
            {
                "name": s.name,
                "members": [{"name": m.name, "type": m.datatype, "start": m.start_value} for m in s.members],
            }
            for s in blk.sections
        ],
        "networks": [_unit(u) for u in blk.units],
    }


def dump(paths: list[Path]) -> list[dict[str, Any]]:
    out = []
    for path in paths:
        doc = parse_document(read_source(path), str(path))
        out.append(
            {
                "file": display_path(path),
                "engineering": doc.engineering,
                "namespaces": sorted(doc.namespaces),
                "issues": doc.issues,
                "blocks": [_block(b) for b in doc.blocks],
            }
        )
    return out


def dump_json(paths: list[Path]) -> str:
    return json.dumps(dump(paths), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


__all__ = ["dump", "dump_json"]
