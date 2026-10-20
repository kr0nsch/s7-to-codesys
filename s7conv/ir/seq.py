"""SeqIR: последовательность S7-GRAPH (SimaticML `Graph`, XSD Graph_v6) — шаги, переходы, ветви и связи.

Из `<Graph>`: постоянные операции (PreOperations/PostOperations — сети LAD/FBD), последовательности
(`Sequence`: `Steps`, `Transitions`, `Branches`, `Connections`). У шага — действия (`Action`: квалификатор,
событие, блокировка, текст SCL из Token/Access), контроль (`Supervision`) и блокировка (`Interlock`) —
сети LAD с катушками SvCoil/IlCoil; у перехода — сеть с катушкой TrCoil.

Топология (`Topology`): для каждого перехода — шаги-предшественники и шаги-преемники через ветви:
AltBegin (выбор: приоритет — порядок выходов ветви), SimBegin (параллельно), SimEnd (синхронизация:
переход ждёт все входные шаги), AltEnd (слияние), связь Jump (прыжок к шагу), EndConnection (конец
последовательности). Номера выходов и входов ветви (`BranchRef Out/In`) — с нуля [M].
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

from s7conv.frontends.simaticml import access_text, child, children, local, tokens_text

COND_COILS = ("TrCoil", "SvCoil", "IlCoil")


@dataclass
class SeqAction:
    qualifier: str  # N S R D L ON OFF TL TD TR TF CS CU CD CR или ""
    event: str  # S1 S0 V1 V0 L0 L1 A1 R1 или ""
    interlock: bool
    text: str  # операнд (#x) или инструкция SCL
    operand: str = ""  # для D/L и простых N/S/R: операнд
    time: str = ""  # для D/L: константа времени
    index: int = 0  # номер действия в шаге, с 1


@dataclass
class SeqStep:
    number: int
    name: str
    init: bool = False
    actions: list[SeqAction] = field(default_factory=list)
    supervision: ET.Element | None = None  # FlgNet с SvCoil или None
    interlock: ET.Element | None = None  # FlgNet с IlCoil или None
    max_time: str | None = None
    warn_time: str | None = None


@dataclass
class SeqTransition:
    number: int
    name: str
    net: ET.Element | None
    lang: str = "LAD"


@dataclass
class SeqBranch:
    number: int
    type: str
    cardinality: int


@dataclass(frozen=True)
class Node:
    kind: str  # S | T | B | END
    number: int = 0
    port: int | None = None  # In (куда) или Out (откуда) ветви


@dataclass
class SeqConnection:
    src: Node
    dst: Node
    link: str  # Direct | Jump


@dataclass
class Sequence:
    title: str = ""
    steps: list[SeqStep] = field(default_factory=list)
    transitions: list[SeqTransition] = field(default_factory=list)
    branches: list[SeqBranch] = field(default_factory=list)
    connections: list[SeqConnection] = field(default_factory=list)

    def step(self, number: int) -> SeqStep:
        return next(s for s in self.steps if s.number == number)

    def transition(self, number: int) -> SeqTransition:
        return next(t for t in self.transitions if t.number == number)


@dataclass
class Graph:
    pre: list[tuple[ET.Element, str]] = field(default_factory=list)  # (FlgNet, язык)
    sequences: list[Sequence] = field(default_factory=list)
    post: list[tuple[ET.Element, str]] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)


def _flgnet(el: ET.Element | None) -> ET.Element | None:
    if el is None:
        return None
    net = child(el, "FlgNet")
    if net is None:
        return None
    parts = child(net, "Parts")
    return net if parts is not None and len(list(parts)) else None


def _action(el: ET.Element, index: int) -> SeqAction:
    pieces = [c for c in el if local(c.tag) in ("Access", "Token", "Blank", "NewLine")]
    text = tokens_text(el).strip()
    act = SeqAction(
        qualifier=el.get("Qualifier", ""),
        event=el.get("Event", ""),
        interlock=el.get("Interlock", "false").lower() == "true",
        text=text,
        index=index,
    )
    accesses = [c for c in pieces if local(c.tag) == "Access"]
    tokens = [c.get("Text", "") for c in pieces if local(c.tag) == "Token"]
    if accesses and tokens == [","] and len(accesses) == 2:
        act.operand, act.time = access_text(accesses[0]), access_text(accesses[1])
    elif len(accesses) == 1 and not tokens:
        act.operand = access_text(accesses[0])
    return act


def _node(el: ET.Element | None, attr: str) -> Node:
    if el is None:
        return Node("END")
    for c in el:
        name = local(c.tag)
        if name == "StepRef":
            return Node("S", int(c.get("Number", "0")))
        if name == "TransitionRef":
            return Node("T", int(c.get("Number", "0")))
        if name == "BranchRef":
            port = c.get(attr)
            return Node("B", int(c.get("Number", "0")), int(port) if port not in (None, "") else None)
        if name == "EndConnection":
            return Node("END")
    return Node("END")


def _sequence(el: ET.Element) -> Sequence:
    seq = Sequence(title=" ".join(t.strip() for t in el.itertext() if False))
    for st in children(child(el, "Steps"), "Step"):
        step = SeqStep(
            number=int(st.get("Number", "0")),
            name=st.get("Name", ""),
            init=st.get("Init", "false").lower() == "true",
            max_time=st.get("MaximumStepTime"),
            warn_time=st.get("WarningTime"),
        )
        for k, a in enumerate(children(child(st, "Actions"), "Action"), start=1):
            step.actions.append(_action(a, k))
        step.supervision = _flgnet(child(child(st, "Supervisions"), "Supervision"))
        step.interlock = _flgnet(child(child(st, "Interlocks"), "Interlock"))
        seq.steps.append(step)
    for tr in children(child(el, "Transitions"), "Transition"):
        seq.transitions.append(
            SeqTransition(
                int(tr.get("Number", "0")), tr.get("Name", ""), _flgnet(tr), tr.get("ProgrammingLanguage", "LAD")
            )
        )
    for br in children(child(el, "Branches"), "Branch"):
        seq.branches.append(SeqBranch(int(br.get("Number", "0")), br.get("Type", ""), int(br.get("Cardinality", "0"))))
    for con in children(child(el, "Connections"), "Connection"):
        link = child(con, "LinkType")
        seq.connections.append(
            SeqConnection(
                _node(child(con, "NodeFrom"), "Out"),
                _node(child(con, "NodeTo"), "In"),
                (link.text or "Direct").strip() if link is not None else "Direct",
            )
        )
    return seq


def parse_graph(el: ET.Element) -> Graph:
    """<Graph> → Graph (последовательности и постоянные операции)."""
    g = Graph()
    for tag, target in (("PreOperations", g.pre), ("PostOperations", g.post)):
        for op in children(child(el, tag), "PermanentOperation"):
            net = _flgnet(op)
            if net is not None:
                target.append((net, op.get("ProgrammingLanguage", "LAD")))
    for seq_el in children(el, "Sequence"):
        g.sequences.append(_sequence(seq_el))
    return g


# ---------------------------------------------------------------------------
# Топология
# ---------------------------------------------------------------------------


@dataclass
class TransitionLink:
    number: int
    preds: list[int]  # шаги-предшественники (все должны быть активны)
    succs: list[int]  # шаги-преемники (активируются)
    priority: int = 0  # порядок среди альтернатив одного шага (0 — первый слева)
    end: bool = False  # после перехода последовательность заканчивается (EndConnection)


@dataclass
class Topology:
    links: list[TransitionLink] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)

    def link(self, number: int) -> TransitionLink:
        return next(t for t in self.links if t.number == number)


def topology(seq: Sequence) -> Topology:
    """Переходы с предшественниками и преемниками через ветви."""
    branches = {b.number: b for b in seq.branches}
    out_edges: dict[tuple[str, int], list[SeqConnection]] = {}
    in_edges: dict[tuple[str, int], list[SeqConnection]] = {}
    for c in seq.connections:
        out_edges.setdefault((c.src.kind, c.src.number), []).append(c)
        in_edges.setdefault((c.dst.kind, c.dst.number), []).append(c)
    topo = Topology()

    def preds_of(node: Node, seen: frozenset[tuple[str, int]] = frozenset()) -> list[int]:
        key = (node.kind, node.number)
        if key in seen:
            topo.issues.append(f"цикл связей через {node.kind}{node.number}")
            return []
        found: list[int] = []
        for c in in_edges.get(key, []):
            if c.src.kind == "S":
                found.append(c.src.number)
            elif c.src.kind == "B":
                br = branches.get(c.src.number)
                if br is None:
                    topo.issues.append(f"ветвь {c.src.number} не описана")
                    continue
                found += preds_of(Node("B", br.number), seen | {key})
            elif c.src.kind == "T":
                topo.issues.append(f"переход T{c.src.number} связан с переходом без шага")
        return found

    def succs_of(node: Node, seen: frozenset[tuple[str, int]] = frozenset()) -> tuple[list[int], bool]:
        key = (node.kind, node.number)
        if key in seen:
            topo.issues.append(f"цикл связей через {node.kind}{node.number}")
            return [], False
        found: list[int] = []
        end = False
        for c in out_edges.get(key, []):
            if c.dst.kind == "S":
                found.append(c.dst.number)
            elif c.dst.kind == "B":
                more, more_end = succs_of(Node("B", c.dst.number), seen | {key})
                found += more
                end = end or more_end
            elif c.dst.kind == "END":
                end = True
            else:
                topo.issues.append(f"{node.kind}{node.number} связан с переходом T{c.dst.number} без шага")
        return found, end

    for tr in seq.transitions:
        node = Node("T", tr.number)
        preds = preds_of(node)
        succs, end = succs_of(node)
        priority = 0
        for c in in_edges.get(("T", tr.number), []):
            branch = branches.get(c.src.number) if c.src.kind == "B" else None
            if branch is not None and branch.type == "AltBegin":
                priority = c.src.port or 0
        if not preds:
            topo.issues.append(f"переход T{tr.number} без шага-предшественника")
        if not succs and not end:
            topo.issues.append(f"переход T{tr.number} без шага-преемника")
        topo.links.append(TransitionLink(tr.number, sorted(set(preds)), sorted(set(succs)), priority, end))
    topo.links.sort(key=lambda t: (min(t.preds) if t.preds else 0, t.priority, t.number))
    return topo


__all__ = [
    "COND_COILS",
    "Graph",
    "Node",
    "SeqAction",
    "SeqBranch",
    "SeqConnection",
    "SeqStep",
    "SeqTransition",
    "Sequence",
    "Topology",
    "TransitionLink",
    "parse_graph",
    "topology",
]
