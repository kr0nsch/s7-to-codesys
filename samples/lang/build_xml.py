"""Сборка корпуса SimaticML (samples/lang/*.xml) из закоммиченного описания блоков (samples/lang/blocks.py).

XML — артефакт в git: правка руками запрещена, как и у прочего сгенерированного. Сборка детерминирована:
UId элементов — по порядку создания с 21 (как в экспортах TIA), провода — после элементов, текст —
UTF-8, LF, отступ два пробела. Пространства имён — по версии TIA (`--tia V21`, по умолчанию V21).

    python samples/lang/build_xml.py           # записать samples/lang/*.xml
    python samples/lang/build_xml.py --check   # сравнить с файлами (код 1, если отличаются)

Формат сверен с XSD V21 (`SW.PlcBlocks.LADFBD_v5`, `STL_v5`, `SCL_v4`, `InterfaceSections_v5`) — тест
s7conv/tests/test_lang_xsd.py валидирует каждый фрагмент; внешней оболочки Document/SW.Blocks.* в XSD
нет, она повторяет открытые экспорты (samples/lang/EXTERNAL.json).
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

HERE = Path(__file__).resolve().parent
SW = "http://www.siemens.com/automation/Openness/SW"
# Пространства имён по версиям TIA: Interface и FlgNet V21 — из экспортов lad-cookbook (V21), STL и SCL —
# по номеру файла XSD своей версии (STL_v5, SCL_v4) [M]
NAMESPACES: dict[str, dict[str, str]] = {
    "V21": {
        "Interface": f"{SW}/Interface/v5",
        "FlgNet": f"{SW}/NetworkSource/FlgNet/v5",
        "StatementList": f"{SW}/NetworkSource/StatementList/v5",
        "StructuredText": f"{SW}/NetworkSource/StructuredText/v4",
    },
}
DEFAULT_TIA = "V21"
CULTURE = "ru-RU"

# ---------------------------------------------------------------------------
# Описание блока
# ---------------------------------------------------------------------------


@dataclass
class Member:
    name: str
    datatype: str
    comment: str = ""
    start: str | None = None
    retain: bool = False
    offset: int | None = None
    version: str = ""
    members: list[Member] = field(default_factory=list)


@dataclass
class Section:
    name: str  # Input, Output, InOut, Static, Temp, Constant, Return, None
    members: list[Member] = field(default_factory=list)


@dataclass
class Unit:
    """Сеть: язык и тело (FlgNet/StatementList/StructuredText — строки XML без пространства имён)."""

    lang: str
    title: str
    comment: str
    kind: str  # FlgNet | StatementList | StructuredText
    body: list[str]


@dataclass
class Block:
    kind: str  # FB | FC | OB | GlobalDB | InstanceDB | PlcStruct
    name: str
    number: int
    lang: str = "LAD"
    title: str = ""
    comment: str = ""
    layout: str = "Optimized"
    author: str = "WTP2"
    family: str = ""
    version: str = "0.1"
    sections: list[Section] = field(default_factory=list)
    units: list[Unit] = field(default_factory=list)
    instance_of: str = ""


# ---------------------------------------------------------------------------
# Операнды
# ---------------------------------------------------------------------------

_TYPED_RE = re.compile(r"^(T|TIME|S5T|S5TIME|LT|D|DATE|TOD|DT|C|INT|DINT|WORD|DWORD|BYTE|REAL|LREAL|\d+)#", re.I)


def _components(path: str) -> list[str]:
    return [p.strip('"') for p in re.findall(r'"[^"]*"|[^.]+', path)]


def access_xml(text: str, uid: int | None, ind: str) -> list[str]:
    """Операнд SCL (#x.y, "DB".x, T#2S, 16#FF, 1, TRUE, метка) → <Access>."""
    u = f' UId="{uid}"' if uid is not None else ""
    if text.startswith("#"):
        comps = "".join(f'<Component Name="{escape(c)}" />' for c in _components(text[1:]))
        return [f'{ind}<Access Scope="LocalVariable"{u}><Symbol>{comps}</Symbol></Access>']
    if text.startswith('"'):
        comps = "".join(f'<Component Name="{escape(c)}" />' for c in _components(text))
        return [f'{ind}<Access Scope="GlobalVariable"{u}><Symbol>{comps}</Symbol></Access>']
    if text.startswith("label:"):
        return [f'{ind}<Access Scope="Label"{u}><Label Name="{escape(text[6:])}" /></Access>']
    if _TYPED_RE.match(text):
        return [
            f'{ind}<Access Scope="TypedConstant"{u}><Constant><ConstantValue>{escape(text)}</ConstantValue>'
            "</Constant></Access>"
        ]
    ctype = "Bool" if text.upper() in ("TRUE", "FALSE") else ("Real" if "." in text else "Int")
    return [
        f'{ind}<Access Scope="LiteralConstant"{u}><Constant><ConstantType>{ctype}</ConstantType>'
        f"<ConstantValue>{escape(text)}</ConstantValue></Constant></Access>"
    ]


# ---------------------------------------------------------------------------
# LAD/FBD: построитель сети
# ---------------------------------------------------------------------------

Src = tuple[int, str] | str  # (uid, пин) | "rail"


class Net:
    """Сеть FlgNet: элементы и операнды получают UId по порядку создания, провода — после них."""

    def __init__(self, title: str, comment: str = "", lang: str = "LAD") -> None:
        self.title = title
        self.comment = comment
        self.lang = lang
        self.items: list[tuple[int, str, dict[str, object]]] = []  # (uid, вид, данные)
        self.links: dict[object, list[tuple[str, object]]] = {}  # источник -> приёмники (порядок вставки)
        self.labels: list[str] = []
        self.uid = 21

    def _next(self) -> int:
        uid = self.uid
        self.uid += 1
        return uid

    def access(self, text: str) -> int:
        uid = self._next()
        self.items.append((uid, "access", {"text": text}))
        return uid

    def part(
        self,
        name: str,
        *,
        negated: Sequence[str] = (),
        templates: Sequence[tuple[str, str, str]] = (),
        instance: str = "",
        disabled_eno: bool = False,
        version: str = "",
        equation: str = "",
        call: dict[str, object] | None = None,
    ) -> int:
        uid = self._next()
        data: dict[str, object] = {
            "name": name,
            "negated": list(negated),
            "templates": list(templates),
            "instance": instance,
            "disabled_eno": disabled_eno,
            "version": version,
            "equation": equation,
            "call": call,
        }
        self.items.append((uid, "call" if call is not None else "part", data))
        return uid

    def wire(self, src: Src | int, *sinks: tuple[int, str] | int) -> None:
        """Провод: источник (шина "rail", пин (uid, имя) или операнд uid) → приёмники (пины или операнды)."""
        key: object = src
        self.links.setdefault(key, [])
        for sink in sinks:
            self.links[key].append(("pin", sink) if isinstance(sink, tuple) else ("ident", sink))

    def open(self, src: tuple[int, str]) -> None:
        """Свободный выход (OpenCon): ET таймера, Q без приёмника."""
        self.links.setdefault(src, []).append(("open", self._next()))

    # -- помощники LAD -------------------------------------------------------------------
    def contact(self, src: Src, var: str, neg: bool = False) -> tuple[int, str]:
        acc = self.access(var)
        c = self.part("Contact", negated=["operand"] if neg else [])
        self.wire(src, (c, "in"))
        self.wire(acc, (c, "operand"))
        return (c, "out")

    def coil(self, src: Src, var: str, kind: str = "Coil") -> int:
        acc = self.access(var)
        c = self.part(kind)
        self.wire(src, (c, "in"))
        self.wire(acc, (c, "operand"))
        return c

    def orr(self, *srcs: Src) -> tuple[int, str]:
        o = self.part("O", templates=[("Card", "Cardinality", str(len(srcs)))])
        for n, s in enumerate(srcs, start=1):
            self.wire(s, (o, f"in{n}"))
        return (o, "out")

    def gate(self, name: str, *ins: str | Src, negated: Sequence[int] = ()) -> tuple[int, str]:
        """Блок FBD A/O/X: входы — операнды (#x) или выходы других элементов; negated — номера входов."""
        accs = [self.access(i) if isinstance(i, str) and i != "rail" else None for i in ins]
        g = self.part(name, negated=[f"in{n}" for n in negated], templates=[("Card", "Cardinality", str(len(ins)))])
        for n, (i, acc) in enumerate(zip(ins, accs, strict=True), start=1):
            if acc is not None:
                self.wire(acc, (g, f"in{n}"))
            else:
                assert not isinstance(i, str) or i == "rail"
                self.wire(i, (g, f"in{n}"))
        return (g, "out")

    def operand_in(self, part: int, pin: str, var: str) -> None:
        self.wire(self.access(var), (part, pin))

    def operand_out(self, part: int, pin: str, var: str) -> None:
        self.wire((part, pin), self.access(var))

    # -- XML -----------------------------------------------------------------------------
    def xml(self, ns: str, ind: str) -> list[str]:
        out = [f'{ind}<FlgNet xmlns="{ns}">']
        i2, i3 = ind + "  ", ind + "    "
        if self.labels:
            out.append(f"{i2}<Labels>")
            out += [f'{i3}<LabelDeclaration><Label Name="{escape(lb)}" /></LabelDeclaration>' for lb in self.labels]
            out.append(f"{i2}</Labels>")
        out.append(f"{i2}<Parts>")
        for uid, kind, data in self.items:
            if kind == "access":
                out += access_xml(str(data["text"]), uid, i3)
            elif kind == "call":
                out += self._call_xml(uid, data, i3)
            else:
                out += self._part_xml(uid, data, i3)
        out.append(f"{i2}</Parts>")
        out.append(f"{i2}<Wires>")
        wire_uid = self.uid
        for src, sinks in self.links.items():
            ends = [self._end(src, source=True)] + [self._end(s, source=False) for s in sinks]
            out.append(f'{i3}<Wire UId="{wire_uid}">{"".join(ends)}</Wire>')
            wire_uid += 1
        out.append(f"{i2}</Wires>")
        out.append(f"{ind}</FlgNet>")
        return out

    @staticmethod
    def _end(item: object, source: bool) -> str:
        if item == "rail":
            return "<Powerrail />"
        if source:
            if isinstance(item, tuple):
                return f'<NameCon UId="{item[0]}" Name="{item[1]}" />'
            return f'<IdentCon UId="{item}" />'
        assert isinstance(item, tuple)
        kind, target = item
        if kind == "pin":
            assert isinstance(target, tuple)
            return f'<NameCon UId="{target[0]}" Name="{target[1]}" />'
        if kind == "open":
            return f'<OpenCon UId="{target}" />'
        return f'<IdentCon UId="{target}" />'

    @staticmethod
    def _part_children(data: dict[str, object], ind: str) -> list[str]:
        out: list[str] = []
        if data["instance"]:
            text = str(data["instance"])
            scope = "LocalVariable" if text.startswith("#") else "GlobalVariable"
            comps = "".join(f'<Component Name="{escape(c)}" />' for c in _components(text.lstrip("#")))
            out.append(f'{ind}<Instance Scope="{scope}">{comps}</Instance>')
        if data["equation"]:
            out.append(f"{ind}<Equation>{escape(str(data['equation']))}</Equation>")
        for name, typ, value in data["templates"]:  # type: ignore[attr-defined]
            out.append(f'{ind}<TemplateValue Name="{name}" Type="{typ}">{escape(value)}</TemplateValue>')
        for pin in data["negated"]:  # type: ignore[attr-defined]
            out.append(f'{ind}<Negated Name="{pin}" />')
        return out

    def _part_xml(self, uid: int, data: dict[str, object], ind: str) -> list[str]:
        attrs = f'Name="{data["name"]}"'
        if data["version"]:
            attrs += f' Version="{data["version"]}"'
        attrs += f' UId="{uid}"'
        if data["disabled_eno"]:
            attrs += ' DisabledENO="true"'
        kids = self._part_children(data, ind + "  ")
        if not kids:
            return [f"{ind}<Part {attrs} />"]
        return [f"{ind}<Part {attrs}>", *kids, f"{ind}</Part>"]

    def _call_xml(self, uid: int, data: dict[str, object], ind: str) -> list[str]:
        call = data["call"]
        assert isinstance(call, dict)
        out = [f'{ind}<Call UId="{uid}">', f'{ind}  <CallInfo Name="{call["name"]}" BlockType="{call["type"]}">']
        if call.get("instance"):
            text = str(call["instance"])
            scope = "LocalVariable" if text.startswith("#") else "GlobalVariable"
            comps = "".join(f'<Component Name="{escape(c)}" />' for c in _components(text.lstrip("#")))
            out.append(f'{ind}    <Instance Scope="{scope}">{comps}</Instance>')
        for name, section, typ in call["params"]:
            out.append(f'{ind}    <Parameter Name="{name}" Section="{section}" Type="{typ}" />')
        out += [f"{ind}  </CallInfo>", f"{ind}</Call>"]
        return out


# ---------------------------------------------------------------------------
# STL: построитель списка инструкций
# ---------------------------------------------------------------------------


class Stl:
    """Список инструкций STL: StlToken — имя токена XSD (A, AN, A_BRACK, JCN, ADD_I ...), операнд — Access."""

    def __init__(self, title: str, comment: str = "") -> None:
        self.title = title
        self.comment = comment
        self.lines: list[str] = []

    def op(self, token: str, operand: str | None = None, label: str | None = None, comment: str = "") -> Stl:
        parts = []
        if label:
            parts.append(f'<LabelDeclaration><Label Name="{escape(label)}" /></LabelDeclaration>')
        parts.append(f'<StlToken Text="{token}" />')
        if comment:
            parts.append(f"<LineComment><Text>{escape(comment)}</Text></LineComment>")
        if operand is not None:
            parts.append(access_xml(operand, None, "")[0])
        self.lines.append(f"<StlStatement>{''.join(parts)}</StlStatement>")
        return self

    def note(self, text: str) -> Stl:
        """Строка-комментарий STL."""
        comment = f"<LineComment><Text>{escape(text)}</Text></LineComment>"
        self.lines.append(f'<StlStatement><StlToken Text="COMMENT" />{comment}</StlStatement>')
        return self

    def call_instruction(
        self,
        name: str,
        instance: str,
        templates: Sequence[tuple[str, str, str]],
        params: Sequence[tuple[str, str, str, str | None]],
        version: str = "1.0",
    ) -> Stl:
        """CALL инструкции с экземпляром (TON, TOF ...): параметры (имя, секция, тип, операнд или None)."""
        comps = "".join(f'<Component Name="{escape(c)}" />' for c in _components(instance.lstrip("#")))
        scope = "LocalVariable" if instance.startswith("#") else "GlobalVariable"
        inner = [f'<Instruction Name="{name}" Version="{version}">']
        inner += [f'<TemplateValue Name="{n}" Type="{t}">{escape(v)}</TemplateValue>' for n, t, v in templates]
        inner.append(f'<Instance Scope="{scope}">{comps}</Instance>')
        for pname, section, typ, operand in params:
            if operand is None:
                inner.append(f'<Parameter Name="{pname}" Section="{section}" Type="{typ}" />')
            else:
                acc = access_xml(operand, None, "")[0]
                inner.append(f'<Parameter Name="{pname}" Section="{section}" Type="{typ}">{acc}</Parameter>')
        inner.append("</Instruction>")
        self.lines.append(
            f'<StlStatement><StlToken Text="CALL" /><Access Scope="Call">{"".join(inner)}</Access></StlStatement>'
        )
        return self

    def xml(self, ns: str, ind: str) -> list[str]:
        return [
            f'{ind}<StatementList xmlns="{ns}">',
            *[f"{ind}  {line}" for line in self.lines],
            f"{ind}</StatementList>",
        ]


# ---------------------------------------------------------------------------
# SCL в XML: токены StructuredText
# ---------------------------------------------------------------------------

_SCL_TOKEN_RE = re.compile(
    r"(?P<nl>\n)|(?P<ws>[ \t]+)|(?P<cmt>//[^\n]*)"
    r"|(?P<local>#[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)"
    r"|(?P<typed>(?:T|TIME|S5T|INT|DINT|WORD|DWORD|BYTE|REAL|\d+)#[A-Za-z0-9_.#]+)"
    r"|(?P<num>\d+(?:\.\d+)?)"
    r"|(?P<word>[A-Za-z_][A-Za-z0-9_]*)"
    r"|(?P<op>:=|=>|<=|>=|<>|[-+*/=<>();,\[\]])",
    re.I,
)


class Scl:
    """Сеть SCL: текст → StructuredText (Token, Blank, NewLine, Access, CallInfo/Instruction)."""

    def __init__(self, title: str, text: str, comment: str = "", instances: dict[str, str] | None = None) -> None:
        self.title = title
        self.comment = comment
        self.text = text.strip("\n")
        self.instances = instances or {}  # #имя экземпляра -> инструкция (TON) или FB

    def xml(self, ns: str, ind: str) -> list[str]:
        pieces: list[str] = []
        tokens = list(_SCL_TOKEN_RE.finditer(self.text))
        pos = 0
        i = 0
        while i < len(tokens):
            m = tokens[i]
            if m.start() != pos:
                raise ValueError(f"SCL: не разобрано {self.text[pos : m.start()]!r}")
            pos = m.end()
            kind = m.lastgroup
            value = m.group(0)
            if kind == "nl":
                pieces.append("<NewLine />")
            elif kind == "ws":
                pieces.append(f'<Blank Num="{len(value)}" />' if len(value) > 1 else "<Blank />")
            elif kind == "cmt":
                pieces.append(f"<LineComment><Text>{escape(value[2:])}</Text></LineComment>")
            elif kind == "local":
                nxt = tokens[i + 1] if i + 1 < len(tokens) else None
                if value in self.instances and nxt is not None and nxt.group(0) == "(":
                    call, i, pos = self._call(value, tokens, i + 1)
                    pieces.append(call)
                    i += 1
                    continue
                pieces.append(access_xml(value, None, "")[0])
            elif kind in ("typed", "num"):
                pieces.append(access_xml(value, None, "")[0])
            elif kind == "word" and value.upper() in ("TRUE", "FALSE"):
                pieces.append(access_xml(value.upper(), None, "")[0])
            else:
                pieces.append(f"<Token Text={quoteattr(value)} />")
            i += 1
        if pos != len(self.text):
            raise ValueError(f"SCL: не разобран хвост {self.text[pos:]!r}")
        return [f'{ind}<StructuredText xmlns="{ns}">', *[f"{ind}  {p}" for p in pieces], f"{ind}</StructuredText>"]

    def _call(self, inst: str, tokens: list[re.Match[str]], i: int) -> tuple[str, int, int]:
        """`#inst(A := x, B := y)` → Access Scope=Call с Instruction/CallInfo и Parameter."""
        target = self.instances[inst]
        comps = "".join(f'<Component Name="{escape(c)}" />' for c in _components(inst[1:]))
        head = (
            f'<Instruction Name="{target}">'
            if target.isupper()
            else f'<CallInfo Name="{escape(target)}" BlockType="FB">'
        )
        close = "</Instruction>" if target.isupper() else "</CallInfo>"
        out = [f'<Access Scope="Call">{head}<Instance Scope="LocalVariable">{comps}</Instance><Token Text="(" />']
        depth = 1
        i += 1
        param: list[str] | None = None
        while i < len(tokens):
            m = tokens[i]
            value, kind = m.group(0), m.lastgroup
            if value == "(":
                depth += 1
            elif value == ")":
                depth -= 1
                if depth == 0:
                    if param is not None:
                        out.append("".join(param) + "</Parameter>")
                    out.append(f'<Token Text=")" />{close}</Access>')
                    return "".join(out), i, m.end()
            if depth == 1 and value == ",":
                if param is not None:
                    out.append("".join(param) + "</Parameter>")
                    param = None
                out.append('<Token Text="," />')
            elif depth == 1 and param is None and kind == "word":
                param = [f'<Parameter Name="{value}">']
            elif param is not None:
                if kind == "ws":
                    param.append("<Blank />")
                elif kind in ("local", "typed", "num"):
                    param.append(access_xml(value, None, "")[0])
                else:
                    param.append(f"<Token Text={quoteattr(value)} />")
            elif kind == "ws":
                out.append("<Blank />")
            i += 1
        raise ValueError(f"SCL: незакрытый вызов {inst}")


# ---------------------------------------------------------------------------
# Документ
# ---------------------------------------------------------------------------


def _member_xml(m: Member, ind: str) -> list[str]:
    attrs = f'Name="{escape(m.name)}" Datatype={quoteattr(m.datatype)}'
    if m.version:
        attrs += f' Version="{m.version}"'
    if m.retain:
        attrs += ' Remanence="Retain"'
    kids: list[str] = []
    if m.offset is not None:
        kids.append(
            f'{ind}  <AttributeList><IntegerAttribute Name="Offset" Informative="true" SystemDefined="true">'
            f"{m.offset}</IntegerAttribute></AttributeList>"
        )
    for sub in m.members:
        kids += _member_xml(sub, ind + "  ")
    if m.comment:
        kids.append(
            f'{ind}  <Comment><MultiLanguageText Lang="{CULTURE}">{escape(m.comment)}</MultiLanguageText></Comment>'
        )
    if m.start is not None:
        kids.append(f"{ind}  <StartValue>{escape(m.start)}</StartValue>")
    if not kids:
        return [f"{ind}<Member {attrs} />"]
    return [f"{ind}<Member {attrs}>", *kids, f"{ind}</Member>"]


def _text_object(composition: str, text: str, ids: list[int], ind: str) -> list[str]:
    a, b = ids[0], ids[0] + 1
    ids[0] += 2
    return [
        f'{ind}<MultilingualText ID="{a:X}" CompositionName="{composition}">',
        f"{ind}  <ObjectList>",
        f'{ind}    <MultilingualTextItem ID="{b:X}" CompositionName="Items">',
        f"{ind}      <AttributeList>",
        f"{ind}        <Culture>{CULTURE}</Culture>",
        f"{ind}        <Text>{escape(text)}</Text>",
        f"{ind}      </AttributeList>",
        f"{ind}    </MultilingualTextItem>",
        f"{ind}  </ObjectList>",
        f"{ind}</MultilingualText>",
    ]


_KIND_TAG = {
    "FB": "SW.Blocks.FB",
    "FC": "SW.Blocks.FC",
    "OB": "SW.Blocks.OB",
    "GlobalDB": "SW.Blocks.GlobalDB",
    "InstanceDB": "SW.Blocks.InstanceDB",
    "PlcStruct": "SW.Types.PlcStruct",
}


def render(block: Block, tia: str = DEFAULT_TIA) -> str:
    """Блок → документ SimaticML (текст)."""
    ns = NAMESPACES[tia]
    tag = _KIND_TAG[block.kind]
    out = [
        '<?xml version="1.0" encoding="utf-8"?>',
        "<!-- s7-to-codesys, корпус всех языков: собрано samples/lang/build_xml.py из samples/lang/blocks.py, "
        "руками не править -->",
        "<Document>",
        f'  <Engineering version="{tia}" />',
        f'  <{tag} ID="0">',
        "    <AttributeList>",
    ]
    if block.kind in ("FB", "FC", "OB", "GlobalDB", "InstanceDB"):
        out.append("      <AutoNumber>false</AutoNumber>")
    if block.kind != "PlcStruct":
        out.append(f"      <HeaderAuthor>{escape(block.author)}</HeaderAuthor>")
        out.append(f"      <HeaderFamily>{escape(block.family)}</HeaderFamily>")
        out.append(f"      <HeaderVersion>{escape(block.version)}</HeaderVersion>")
    if block.instance_of:
        out.append(f"      <InstanceOfName>{escape(block.instance_of)}</InstanceOfName>")
        out.append("      <InstanceOfType>FB</InstanceOfType>")
    out.append("      <Interface>")
    out.append(f'        <Sections xmlns="{ns["Interface"]}">')
    for sec in block.sections:
        if not sec.members:
            out.append(f'          <Section Name="{sec.name}" />')
            continue
        out.append(f'          <Section Name="{sec.name}">')
        for m in sec.members:
            out += _member_xml(m, "            ")
        out.append("          </Section>")
    out.append("        </Sections>")
    out.append("      </Interface>")
    if block.kind != "PlcStruct":
        out.append(f"      <MemoryLayout>{block.layout}</MemoryLayout>")
    out.append(f"      <Name>{escape(block.name)}</Name>")
    out.append(f"      <Number>{block.number}</Number>")
    if block.kind in ("FB", "FC", "OB"):
        out.append(f"      <ProgrammingLanguage>{block.lang}</ProgrammingLanguage>")
        out.append("      <SetENOAutomatically>false</SetENOAutomatically>")
    elif block.kind in ("GlobalDB", "InstanceDB"):
        out.append("      <ProgrammingLanguage>DB</ProgrammingLanguage>")
    out.append("    </AttributeList>")
    out.append("    <ObjectList>")
    ids = [1]
    if block.comment:
        out += _text_object("Comment", block.comment, ids, "      ")
    for unit in block.units:
        cu = ids[0]
        ids[0] += 1
        out.append(f'      <SW.Blocks.CompileUnit ID="{cu:X}" CompositionName="CompileUnits">')
        out.append("        <AttributeList>")
        out.append("          <NetworkSource>")
        out += unit.body
        out.append("          </NetworkSource>")
        out.append(f"          <ProgrammingLanguage>{unit.lang}</ProgrammingLanguage>")
        out.append("        </AttributeList>")
        out.append("        <ObjectList>")
        out += _text_object("Comment", unit.comment, ids, "          ")
        out += _text_object("Title", unit.title, ids, "          ")
        out.append("        </ObjectList>")
        out.append("      </SW.Blocks.CompileUnit>")
    out += _text_object("Title", block.title or block.name, ids, "      ")
    out.append("    </ObjectList>")
    out.append(f"  </{tag}>")
    out.append("</Document>")
    return "\n".join(out) + "\n"


def lad_unit(net: Net, tia: str = DEFAULT_TIA) -> Unit:
    return Unit(net.lang, net.title, net.comment, "FlgNet", net.xml(NAMESPACES[tia]["FlgNet"], "            "))


def stl_unit(stl: Stl, tia: str = DEFAULT_TIA) -> Unit:
    return Unit(
        "STL", stl.title, stl.comment, "StatementList", stl.xml(NAMESPACES[tia]["StatementList"], "            ")
    )


def scl_unit(scl: Scl, tia: str = DEFAULT_TIA) -> Unit:
    return Unit(
        "SCL", scl.title, scl.comment, "StructuredText", scl.xml(NAMESPACES[tia]["StructuredText"], "            ")
    )


def build(tia: str = DEFAULT_TIA) -> dict[str, str]:
    """Все файлы корпуса: {имя файла: текст}."""
    sys.path.insert(0, str(HERE))
    try:
        import blocks  # samples/lang/blocks.py
    finally:
        sys.path.pop(0)
    return {f"{b.name}.xml": render(b, tia) for b in blocks.all_blocks(tia)}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Сборка корпуса SimaticML samples/lang из samples/lang/blocks.py")
    parser.add_argument("--check", action="store_true", help="сравнить с файлами, ничего не писать (код 1 — устарело)")
    parser.add_argument("--tia", default=DEFAULT_TIA, choices=sorted(NAMESPACES), help="версия пространств имён")
    parser.add_argument("--out", default=str(HERE), help="каталог результата")
    args = parser.parse_args(argv)
    files = build(args.tia)
    out = Path(args.out)
    stale = []
    for name, text in sorted(files.items()):
        path = out / name
        if args.check:
            if not path.is_file() or path.read_bytes() != text.encode("utf-8"):
                stale.append(name)
        else:
            path.write_bytes(text.encode("utf-8"))
    extra = sorted(p.name for p in out.glob("*.xml") if p.name not in files)
    if args.check:
        for name in stale:
            print(f"build_xml --check: устарел {name}")
        for name in extra:
            print(f"build_xml --check: лишний {name}")
        if stale or extra:
            return 1
        print(f"build_xml --check: файлов {len(files)}, совпадают")
        return 0
    for name in extra:
        (out / name).unlink()
    print(f"build_xml: записано файлов {len(files)} в {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
