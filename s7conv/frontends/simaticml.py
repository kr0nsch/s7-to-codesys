"""Разбор SimaticML — XML экспорта блоков TIA Portal Openness (только stdlib: xml.etree).

Документ — `<Document>` с одним или несколькими `SW.Blocks.FB|FC|OB|GlobalDB|InstanceDB|ArrayDB` и
`SW.Types.PlcStruct` (V15.1–V21; внешней оболочки в XSD нет — формат сверен с открытыми экспортами из
samples/lang/EXTERNAL.json). Интерфейс — `Sections/Section/Member` (пространство имён `Interface/vN`),
тело — единицы компиляции `SW.Blocks.CompileUnit` со своим `ProgrammingLanguage`: `FlgNet` (LAD/FBD),
`StatementList` (STL), `StructuredText` (SCL), `Graph` (GRAPH).

Пространства имён разных версий TIA различаются только номером (`FlgNet/v4`, `FlgNet/v5`): разборщик
сравнивает локальные имена элементов и записывает встреченные пространства в XDocument.namespaces —
по ним docs/SIMATICML_VERSIONS.md и тесты сверяют, что подтверждено XSD своей версии.

Безопасность: документы с DOCTYPE или объявлениями сущностей отклоняются до разбора.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

OPENNESS_NS = "http://www.siemens.com/automation/Openness/SW/"
BLOCK_TAGS = {
    "SW.Blocks.FB": "FB",
    "SW.Blocks.FC": "FC",
    "SW.Blocks.OB": "OB",
    "SW.Blocks.GlobalDB": "GlobalDB",
    "SW.Blocks.InstanceDB": "InstanceDB",
    "SW.Blocks.ArrayDB": "ArrayDB",
    "SW.Types.PlcStruct": "PlcStruct",
}
BODY_KINDS = ("FlgNet", "StatementList", "StructuredText", "Graph")
PREFERRED_CULTURES = ("ru-RU", "en-US", "en-GB", "de-DE")
_FORBIDDEN_RE = re.compile(r"<!\s*(DOCTYPE|ENTITY)", re.IGNORECASE)
_PLAIN_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")


class SimaticMLError(Exception):
    """Документ не является SimaticML или небезопасен (DOCTYPE, сущности)."""


# ---------------------------------------------------------------------------
# Модель документа
# ---------------------------------------------------------------------------


@dataclass
class XMember:
    """Член интерфейса: Datatype — как в TIA (Bool, Int, "UDT_X", Array[0..3] of Int, Struct)."""

    name: str
    datatype: str
    remanence: str = "NonRetain"
    start_value: str | None = None
    comment: str = ""
    members: list[XMember] = field(default_factory=list)
    version: str = ""
    offset: int | None = None
    attributes: dict[str, str] = field(default_factory=dict)


@dataclass
class XSection:
    name: str  # Input | Output | InOut | Static | Temp | Constant | Return | None
    members: list[XMember] = field(default_factory=list)


@dataclass
class XUnit:
    """Единица компиляции (сеть): язык, заголовок, комментарий и тело-элемент XML."""

    number: int
    lang: str
    title: str = ""
    comment: str = ""
    body: ET.Element | None = None
    body_kind: str = ""  # FlgNet | StatementList | StructuredText | Graph | "" (пустая сеть)
    namespace: str = ""  # NetworkSource/FlgNet/v5 ...


@dataclass
class XBlock:
    kind: str  # FB | FC | OB | GlobalDB | InstanceDB | ArrayDB | PlcStruct
    name: str
    number: int | None = None
    lang: str = ""
    memory_layout: str = ""
    set_eno: bool = False
    title: str = ""
    comment: str = ""
    author: str = ""
    family: str = ""
    version: str = ""
    sections: list[XSection] = field(default_factory=list)
    units: list[XUnit] = field(default_factory=list)
    instance_of: str = ""
    instance_of_type: str = ""
    interface_ns: str = ""

    def section(self, name: str) -> XSection | None:
        return next((s for s in self.sections if s.name == name), None)

    def member_type(self, name: str) -> str | None:
        """Тип члена верхнего уровня интерфейса по имени (без учёта регистра)."""
        for sec in self.sections:
            for m in sec.members:
                if m.name.lower() == name.lower():
                    return m.datatype
        return None

    def member_section(self, name: str) -> str | None:
        for sec in self.sections:
            for m in sec.members:
                if m.name.lower() == name.lower():
                    return sec.name
        return None


@dataclass
class XDocument:
    path: str
    engineering: str = ""
    blocks: list[XBlock] = field(default_factory=list)
    namespaces: set[str] = field(default_factory=set)
    issues: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Помощники XML
# ---------------------------------------------------------------------------


def local(tag: str) -> str:
    """Локальное имя элемента без пространства имён."""
    return tag.rsplit("}", 1)[-1]


def namespace(tag: str) -> str:
    """Пространство имён Openness без общего префикса: NetworkSource/FlgNet/v5, Interface/v5."""
    if tag.startswith("{"):
        uri = tag[1:].split("}", 1)[0]
        return uri[len(OPENNESS_NS) :] if uri.startswith(OPENNESS_NS) else uri
    return ""


def child(el: ET.Element | None, name: str) -> ET.Element | None:
    if el is None:
        return None
    return next((c for c in el if local(c.tag) == name), None)


def _first(*items: ET.Element | None) -> ET.Element | None:
    """Первый не None (у Element без детей bool() ложен — `or` для элементов не годится)."""
    return next((x for x in items if x is not None), None)


def children(el: ET.Element | None, name: str) -> list[ET.Element]:
    if el is None:
        return []
    return [c for c in el if local(c.tag) == name]


def text_of(el: ET.Element | None) -> str:
    return (el.text or "").strip() if el is not None else ""


def multilingual(texts: dict[str, str]) -> str:
    """Текст на предпочтительном языке (ru-RU, en-US, ...), иначе первый непустой."""
    for culture in PREFERRED_CULTURES:
        if texts.get(culture):
            return texts[culture]
    return next((v for v in texts.values() if v), "")


def comment_text(el: ET.Element | None) -> str:
    """`<Comment><MultiLanguageText Lang="ru-RU">...` → текст."""
    if el is None:
        return ""
    texts = {m.get("Lang", ""): (m.text or "").strip() for m in children(el, "MultiLanguageText")}
    return multilingual(texts)


def object_text(object_list: ET.Element | None, composition: str) -> str:
    """`<MultilingualText CompositionName="Title|Comment">` из ObjectList блока или сети."""
    for mt in children(object_list, "MultilingualText"):
        if mt.get("CompositionName") != composition:
            continue
        texts: dict[str, str] = {}
        for item in children(child(mt, "ObjectList"), "MultilingualTextItem"):
            attrs = child(item, "AttributeList")
            texts[text_of(child(attrs, "Culture"))] = text_of(child(attrs, "Text"))
        return multilingual(texts)
    return ""


def scl_name(name: str) -> str:
    """Имя компонента в синтаксисе SCL: простое — как есть, иначе в кавычках."""
    return name if _PLAIN_NAME_RE.match(name) else f'"{name}"'


# ---------------------------------------------------------------------------
# Разбор
# ---------------------------------------------------------------------------


def looks_like_simaticml(text: str) -> bool:
    head = text[:4096]
    return "<Document" in head or any(tag in text for tag in BLOCK_TAGS)


def _attribute_list(el: ET.Element | None) -> dict[str, str]:
    """AttributeList члена: BooleanAttribute/IntegerAttribute/StringAttribute по Name."""
    result: dict[str, str] = {}
    for a in list(el) if el is not None else []:
        name = a.get("Name")
        if name:
            result[name] = (a.text or "").strip()
    return result


def _member(el: ET.Element) -> XMember:
    attrs = _attribute_list(child(el, "AttributeList"))
    offset = attrs.get("Offset")
    m = XMember(
        name=el.get("Name", ""),
        datatype=el.get("Datatype", ""),
        remanence=el.get("Remanence", "NonRetain"),
        version=el.get("Version", ""),
        comment=comment_text(child(el, "Comment")),
        attributes=attrs,
        offset=int(offset) if offset and offset.lstrip("-").isdigit() else None,
    )
    start = child(el, "StartValue")
    if start is not None:
        m.start_value = (start.text or "").strip() or start.get("ConstantName")
    m.members = [_member(c) for c in children(el, "Member")]
    return m


def _sections(sections_el: ET.Element | None) -> list[XSection]:
    result: list[XSection] = []
    for sec in children(sections_el, "Section"):
        result.append(XSection(sec.get("Name", ""), [_member(m) for m in children(sec, "Member")]))
    return result


def _unit(el: ET.Element, number: int, doc: XDocument) -> XUnit:
    attrs = child(el, "AttributeList")
    unit = XUnit(number=number, lang=text_of(child(attrs, "ProgrammingLanguage")))
    objects = child(el, "ObjectList")
    unit.title = object_text(objects, "Title")
    unit.comment = object_text(objects, "Comment")
    source = child(attrs, "NetworkSource")
    if source is not None:
        body = next(iter(source), None)
        if body is not None:
            unit.body = body
            unit.body_kind = local(body.tag)
            unit.namespace = namespace(body.tag)
            if unit.namespace:
                doc.namespaces.add(unit.namespace)
    return unit


def _block(el: ET.Element, kind: str, doc: XDocument) -> XBlock:
    attrs = child(el, "AttributeList")

    def a(name: str) -> str:
        return text_of(child(attrs, name))

    number = a("Number")
    blk = XBlock(
        kind=kind,
        name=a("Name"),
        number=int(number) if number.isdigit() else None,
        lang=a("ProgrammingLanguage"),
        memory_layout=a("MemoryLayout"),
        set_eno=a("SetENOAutomatically").lower() == "true",
        author=a("HeaderAuthor"),
        family=a("HeaderFamily"),
        version=a("HeaderVersion"),
        instance_of=a("InstanceOfName"),
        instance_of_type=a("InstanceOfType"),
    )
    interface = child(attrs, "Interface")
    sections_el = child(interface, "Sections")
    if sections_el is not None:
        blk.interface_ns = namespace(sections_el.tag)
        if blk.interface_ns:
            doc.namespaces.add(blk.interface_ns)
        blk.sections = _sections(sections_el)
    objects = child(el, "ObjectList")
    blk.title = object_text(objects, "Title")
    blk.comment = object_text(objects, "Comment")
    for n, cu in enumerate(children(objects, "SW.Blocks.CompileUnit"), start=1):
        blk.units.append(_unit(cu, n, doc))
    if not blk.name:
        doc.issues.append(f"{local(el.tag)} без имени (AttributeList/Name)")
    return blk


def parse_document(text: str, path: str = "") -> XDocument:
    """Документ SimaticML → блоки; ошибки формата — SimaticMLError."""
    if _FORBIDDEN_RE.search(text):
        raise SimaticMLError(f"{path}: DOCTYPE и объявления сущностей в SimaticML не допускаются")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise SimaticMLError(f"{path}: XML не разбирается ({exc})") from exc
    doc = XDocument(path=path)
    if local(root.tag) != "Document":
        raise SimaticMLError(f"{path}: корневой элемент {local(root.tag)}, ожидался Document (SimaticML)")
    engineering = child(root, "Engineering")
    doc.engineering = engineering.get("version", "") if engineering is not None else ""
    for el in root:
        kind = BLOCK_TAGS.get(local(el.tag))
        if kind is not None:
            doc.blocks.append(_block(el, kind, doc))
        elif local(el.tag) not in ("Engineering", "DocumentInfo"):
            doc.issues.append(f"элемент {local(el.tag)} не поддерживается — пропущен")
    if not doc.blocks:
        doc.issues.append("в документе нет блоков SW.Blocks.* / SW.Types.PlcStruct")
    return doc


# ---------------------------------------------------------------------------
# Access → текст SCL
# ---------------------------------------------------------------------------

_AREA = {
    "Input": "I",
    "Output": "Q",
    "Memory": "M",
    "PeripheryInput": "I",
    "PeripheryOutput": "Q",
    "Timer": "T",
    "Counter": "C",
    "DB": "DB",
    "DI": "DI",
    "Local": "L",
}
_SIZE = {
    "Bool": "X",
    "Byte": "B",
    "Char": "B",
    "SInt": "B",
    "USInt": "B",
    "Word": "W",
    "Int": "W",
    "UInt": "W",
    "S5Time": "W",
    "Date": "W",
    "DWord": "D",
    "DInt": "D",
    "UDInt": "D",
    "Real": "D",
    "Time": "D",
    "Time_Of_Day": "D",
}


def address_text(el: ET.Element) -> str:
    """`<Address Area="Input" Type="Bool" BitOffset="3"/>` → %I0.3; Word → %IW..., DB → %DB10.DBW4."""
    area = el.get("Area", "")
    typ = el.get("Type", "")
    offset = int(el.get("BitOffset", "0") or 0)
    block = el.get("BlockNumber")
    letter = _AREA.get(area, area)
    if area in ("Timer", "Counter"):
        return f"%{letter}{offset}"
    size = _SIZE.get(typ, "")
    byte, bit = divmod(offset, 8)
    periphery = ":P" if area.startswith("Periphery") else ""
    if (block is not None and area in ("DB", "DI")) or (block is not None and area == "None"):
        prefix = f"%DB{block}." if block is not None else ""
        if size == "X" or not size:
            return f"{prefix}DBX{byte}.{bit}"
        return f"{prefix}DB{size}{byte}"
    if size == "X" or not size:
        return f"%{letter}{byte}.{bit}{periphery}"
    return f"%{letter}{size}{byte}{periphery}"


def _component_text(comp: ET.Element) -> str:
    text = scl_name(comp.get("Name", ""))
    indices = [access_text(a) for a in children(comp, "Access")]
    if indices:
        text += "[" + ", ".join(indices) + "]"
    slice_mod = comp.get("SliceAccessModifier", "undef")
    if slice_mod and slice_mod != "undef":
        text += f".%{slice_mod[0].upper()}{slice_mod[1:]}"
    return text


def symbol_text(sym: ET.Element, scope: str) -> str:
    """Symbol → `#a.b[1]` (локальная) или `"DB".a` (глобальная)."""
    parts = []
    for c in sym:
        name = local(c.tag)
        if name == "Component":
            parts.append(_component_text(c))
        elif name == "Address":
            parts.append(address_text(c))
    if not parts:
        return ""
    if scope == "GlobalVariable":
        first = parts[0]
        first = first if first.startswith('"') or first.startswith("%") else f'"{first}"'
        return ".".join([first, *parts[1:]])
    if scope == "LocalVariable":
        return "#" + ".".join(parts)
    return ".".join(parts)


def constant_text(const: ET.Element, scope: str) -> str:
    value = text_of(child(const, "ConstantValue"))
    name = const.get("Name")
    if scope == "GlobalConstant" and name:
        return f'"{name}"'
    if scope == "LocalConstant" and name:
        return f"#{name}"
    if not value and name:
        return name
    return value


def access_text(el: ET.Element) -> str:
    """Операнд `<Access Scope=...>` → выражение SCL; для вызовов и меток — имя."""
    scope = el.get("Scope", "")
    for c in el:
        name = local(c.tag)
        if name == "Symbol":
            return symbol_text(c, scope)
        if name == "Constant":
            return constant_text(c, scope)
        if name == "Address":
            return address_text(c)
        if name == "Label":
            return c.get("Name", "")
        if name == "PredefinedVariable":
            return c.get("Name", "ENO")
        if name == "Statusword":
            return c.get("Combination", "")
        if name == "Expression":
            return tokens_text(c)
        if name in ("CallInfo", "Instruction"):
            return c.get("Name", "")
        if name == "DataType":
            return text_of(c)
    return ""


# ---------------------------------------------------------------------------
# StructuredText (сети SCL) → текст SCL
# ---------------------------------------------------------------------------


def _call_text(el: ET.Element) -> str:
    """CallInfo/Instruction в сети SCL: имя, затем токены и параметры как есть."""
    name = el.get("Name", "")
    instance = child(el, "Instance")
    if instance is not None:
        head = symbol_text(instance, instance.get("Scope", "LocalVariable")) or _instance_text(instance)
    elif el.get("BlockType") == "FC" or local(el.tag) == "Instruction":
        head = name if _PLAIN_NAME_RE.match(name) and local(el.tag) == "Instruction" else f'"{name}"'
    else:
        head = f'"{name}"'
    rest = "".join(_scl_piece(c) for c in el if local(c.tag) != "Instance")
    return head + rest


def _instance_text(instance: ET.Element) -> str:
    comps = [_component_text(c) for c in instance if local(c.tag) == "Component"]
    if instance.get("Scope") == "GlobalVariable" and comps:
        return ".".join([f'"{comps[0]}"' if not comps[0].startswith('"') else comps[0], *comps[1:]])
    return "#" + ".".join(comps)


def _scl_piece(c: ET.Element) -> str:
    name = local(c.tag)
    if name == "Token":
        return c.get("Text", "")
    if name == "Blank":
        return " " * int(c.get("Num", "1") or 1)
    if name == "NewLine":
        return "\n" * int(c.get("Num", "1") or 1)
    if name == "LineComment":
        body = "".join((t.text or "") for t in c if local(t.tag) == "Text")
        if c.get("NoClosingBracket") == "true" or not body.startswith("(*"):
            return "//" + body
        return body
    if name == "Comment":
        return "(*" + comment_text(c) + "*)"
    if name == "Text":
        return c.text or ""
    if name == "Access":
        call = _first(child(c, "CallInfo"), child(c, "Instruction"))
        if call is not None:
            return _call_text(call)
        return access_text(c)
    if name == "Parameter":
        return c.get("Name", "") + "".join(_scl_piece(x) for x in c)
    if name in ("IntegerAttribute", "StringAttribute", "BooleanAttribute", "DateAttribute"):
        return ""
    return ""


def tokens_text(el: ET.Element) -> str:
    """Последовательность Token/Blank/NewLine/Access/... → текст SCL."""
    return "".join(_scl_piece(c) for c in el)


__all__ = [
    "BLOCK_TAGS",
    "BODY_KINDS",
    "OPENNESS_NS",
    "SimaticMLError",
    "XBlock",
    "XDocument",
    "XMember",
    "XSection",
    "XUnit",
    "access_text",
    "address_text",
    "child",
    "children",
    "comment_text",
    "local",
    "looks_like_simaticml",
    "namespace",
    "parse_document",
    "scl_name",
    "symbol_text",
    "text_of",
    "tokens_text",
]
