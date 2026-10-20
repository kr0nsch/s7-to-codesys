"""PLCopen XML (TC6 2.0, пространство имён CODESYS tc6_0200) для графических стратегий: S7-GRAPH → SFC."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SfcFiles:
    """Варианты SFC блоков GRAPH: {имя блока: текст PLCopen XML}; блоки, для которых SFC не строится, — причины."""

    files: dict[str, str] = field(default_factory=dict)
    skipped: dict[str, str] = field(default_factory=dict)
    notes: dict[str, list[str]] = field(default_factory=dict)


def graph_sfc(paths: list[Path], base: Path | None = None) -> SfcFiles:
    """Для каждого блока S7-GRAPH из файлов SimaticML — проект PLCopen с SFC `<Блок>_Sfc` и обёрткой `<Блок>`.

    Блоки других языков пропускаются молча; блок GRAPH вне подмножества SFC (docs/MAPPING_GRAPH.md) —
    в skipped с причиной (ST-двойник строится всегда).
    """
    from s7conv.frontends.simaticml import SimaticMLError, parse_document
    from s7conv.pipeline import display_path, read_source
    from s7conv.plcopen.sfc import SfcError, sfc_project

    out = SfcFiles()
    for path in paths:
        try:
            doc = parse_document(read_source(path), str(path))
        except SimaticMLError:
            continue  # ошибка разбора уже в отчёте конвертации
        source = display_path(path, base)
        for blk in doc.blocks:
            if not any(u.body_kind == "Graph" for u in blk.units):
                continue
            try:
                result = sfc_project(blk, source)
            except SfcError as exc:
                out.skipped[blk.name] = str(exc)
                continue
            out.files[blk.name] = result.xml
            out.notes[blk.name] = list(result.notes)
    return out


__all__ = ["SfcFiles", "graph_sfc"]
