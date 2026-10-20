"""NetIR: сеть LAD/FBD S7 как граф (SimaticML `FlgNet`).

Узлы — операнды (`Access`), элементы (`Part`: Contact, Coil, Add, TON, ...) и вызовы (`Call`); рёбра —
провода (`Wire`) с концами `Powerrail`, `IdentCon` (операнд), `NameCon` (пин элемента), `OpenCon`
(свободный выход). В проводе первый конец — источник, остальные — приёмники: так устроены все открытые
экспорты (samples/lang/EXTERNAL.json); XSD порядок не задаёт [M].

Словарь имён Part и пинов XSD не ограничивает (`SimaticName`, `xs:string`) — правила их перевода и
происхождение каждой строки описаны в docs/MAPPING_LADFBD.md.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

from s7conv.frontends.simaticml import (
    access_text,
    child,
    children,
    comment_text,
    local,
    symbol_text,
    text_of,
)

RAIL = "rail"
IDENT = "ident"
PIN = "pin"
OPEN = "open"


@dataclass(frozen=True)
class End:
    """Конец провода: шина питания, операнд (uid), пин элемента (uid, pin) или свободный выход."""

    kind: str
    uid: int = 0
    pin: str = ""


@dataclass
class NAccess:
    uid: int
    scope: str
    text: str  # операнд в синтаксисе SCL: #x, "DB".y, T#5s, 16#FF, %I0.0, имя метки


@dataclass
class NCallInfo:
    name: str
    block_type: str  # FB | FC
    instance: str = ""  # текст SCL экземпляра: #inst или "IDB"
    instance_scope: str = ""
    params: list[tuple[str, str, str]] = field(default_factory=list)  # (имя, секция, тип)

    def param(self, name: str) -> tuple[str, str, str] | None:
        return next((p for p in self.params if p[0].lower() == name.lower()), None)


@dataclass
class NPart:
    uid: int
    name: str
    version: str = ""
    negated: frozenset[str] = frozenset()
    templates: dict[str, str] = field(default_factory=dict)
    instance: str = ""
    instance_scope: str = ""
    equation: str = ""
    disabled_eno: bool = False
    call: NCallInfo | None = None
    comment: str = ""

    @property
    def card(self) -> int:
        value = self.templates.get("Card") or self.templates.get("card") or "2"
        return int(value) if value.isdigit() else 2


@dataclass
class Wire:
    uid: int
    ends: list[End]

    @property
    def source(self) -> End:
        return self.ends[0]

    @property
    def sinks(self) -> list[End]:
        return self.ends[1:]


@dataclass
class Network:
    number: int
    lang: str
    title: str = ""
    comment: str = ""
    accesses: dict[int, NAccess] = field(default_factory=dict)
    parts: dict[int, NPart] = field(default_factory=dict)  # порядок XML
    wires: list[Wire] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    _drivers: dict[tuple[int, str], End] = field(default_factory=dict, repr=False)
    _fanout: dict[End, list[End]] = field(default_factory=dict, repr=False)

    def index(self) -> None:
        """Карты «приёмник → источник» и «источник → приёмники»; дубли и висячие концы — в issues."""
        self._drivers.clear()
        self._fanout.clear()
        for w in self.wires:
            if not w.ends:
                self.issues.append(f"провод UId {w.uid} пустой")
                continue
            src = w.source
            if src.kind == IDENT and src.uid not in self.accesses:
                self.issues.append(f"провод UId {w.uid}: операнд UId {src.uid} не найден")
                continue
            if src.kind == PIN and src.uid not in self.parts:
                self.issues.append(f"провод UId {w.uid}: элемент UId {src.uid} не найден")
                continue
            for sink in w.sinks:
                if sink.kind == IDENT and sink.uid not in self.accesses:
                    self.issues.append(f"провод UId {w.uid}: операнд UId {sink.uid} не найден")
                    continue
                if sink.kind == PIN:
                    if sink.uid not in self.parts:
                        self.issues.append(f"провод UId {w.uid}: элемент UId {sink.uid} не найден")
                        continue
                    key = (sink.uid, sink.pin.lower())
                    if key in self._drivers:
                        self.issues.append(f"пин {sink.pin} элемента UId {sink.uid} подключён дважды")
                    self._drivers[key] = src
                elif sink.kind == IDENT:
                    key = (sink.uid, "")
                    self._drivers.setdefault(key, src)
                self._fanout.setdefault(src, []).append(sink)

    def driver(self, uid: int, pin: str) -> End | None:
        """Источник сигнала на входе pin элемента uid (None — вход не подключён)."""
        return self._drivers.get((uid, pin.lower()))

    def sinks_of(self, uid: int, pin: str) -> list[End]:
        """Приёмники выхода pin элемента uid (без свободных выходов OpenCon)."""
        found: list[End] = []
        for src, sinks in self._fanout.items():
            if src.kind == PIN and src.uid == uid and src.pin.lower() == pin.lower():
                found.extend(s for s in sinks if s.kind != OPEN)
        return found

    def connected(self, uid: int, pin: str) -> bool:
        return bool(self.sinks_of(uid, pin))

    def operand(self, uid: int, pin: str = "operand") -> NAccess | None:
        """Операнд, подключённый к пину (катушка, контакт, бит памяти фронта, вход блока)."""
        src = self.driver(uid, pin)
        if src is not None and src.kind == IDENT:
            return self.accesses.get(src.uid)
        for sink in self.sinks_of(uid, pin):
            if sink.kind == IDENT:
                return self.accesses.get(sink.uid)
        return None

    def pins(self, uid: int) -> set[str]:
        """Все пины элемента, упомянутые в проводах (в нижнем регистре)."""
        found = {pin for (u, pin) in self._drivers if u == uid}
        found |= {src.pin.lower() for src in self._fanout if src.kind == PIN and src.uid == uid}
        return found


# ---------------------------------------------------------------------------
# Разбор FlgNet
# ---------------------------------------------------------------------------


def _uid(el: ET.Element) -> int:
    raw = el.get("UId", "0") or "0"
    return int(raw) if raw.lstrip("-").isdigit() else 0


def _call_info(el: ET.Element) -> NCallInfo:
    info = NCallInfo(name=el.get("Name", ""), block_type=el.get("BlockType", ""))
    instance = child(el, "Instance")
    if instance is not None:
        info.instance_scope = instance.get("Scope", "")
        info.instance = symbol_text(instance, info.instance_scope)
    for p in children(el, "Parameter"):
        info.params.append((p.get("Name", ""), p.get("Section", ""), p.get("Type", "")))
    return info


def _part(el: ET.Element) -> NPart:
    part = NPart(uid=_uid(el), name=el.get("Name", "") if local(el.tag) == "Part" else "Call")
    part.version = el.get("Version", "")
    part.disabled_eno = el.get("DisabledENO", "false").lower() == "true"
    part.negated = frozenset(n.get("Name", "").lower() for n in children(el, "Negated"))
    part.templates = {t.get("Name", ""): text_of(t) for t in children(el, "TemplateValue")}
    instance = child(el, "Instance")
    if instance is not None:
        part.instance_scope = instance.get("Scope", "")
        part.instance = symbol_text(instance, part.instance_scope)
    equation = child(el, "Equation")
    if equation is not None:
        part.equation = text_of(equation)
    call = child(el, "CallInfo")
    if call is not None:
        part.call = _call_info(call)
    part.comment = comment_text(child(el, "Comment"))
    return part


def _end(el: ET.Element) -> End | None:
    name = local(el.tag)
    if name == "Powerrail":
        return End(RAIL)
    if name == "IdentCon":
        return End(IDENT, _uid(el))
    if name == "NameCon":
        return End(PIN, _uid(el), el.get("Name", ""))
    if name == "OpenCon":
        return End(OPEN, _uid(el))
    return None


def build_network(flgnet: ET.Element, number: int, lang: str, title: str = "", comment: str = "") -> Network:
    """FlgNet → Network: операнды, элементы, провода, метки."""
    net = Network(number=number, lang=lang, title=title, comment=comment)
    for decl in children(child(flgnet, "Labels"), "LabelDeclaration"):
        label = child(decl, "Label")
        if label is not None:
            net.labels.append(label.get("Name", ""))
    parts_el = child(flgnet, "Parts")
    for el in list(parts_el) if parts_el is not None else []:
        name = local(el.tag)
        if name == "Access":
            net.accesses[_uid(el)] = NAccess(_uid(el), el.get("Scope", ""), access_text(el))
        elif name in ("Part", "Call"):
            part = _part(el)
            if part.uid in net.parts or part.uid in net.accesses:
                net.issues.append(f"UId {part.uid} повторяется")
            net.parts[part.uid] = part
    for w in children(child(flgnet, "Wires"), "Wire"):
        ends = [e for e in (_end(c) for c in w) if e is not None]
        net.wires.append(Wire(_uid(w), ends))
    net.index()
    return net


__all__ = ["IDENT", "OPEN", "PIN", "RAIL", "End", "NAccess", "NCallInfo", "NPart", "Network", "Wire", "build_network"]
