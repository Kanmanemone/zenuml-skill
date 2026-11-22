"""Read an architecture view file (.zenuml/<slug>.architecture.md) into plain data.

Relies on the fixed file shape the skill writes (SKILL.md "Output file", Step 2):
a `### Dependency` heading with one Mermaid fence, then `### Responsibility` and
`### Collaboration` (each optionally wrapped in a <details> box). Nothing here edits text.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


class ViewFormatError(Exception):
    """The file is not an architecture view (no Mermaid fence under `### Dependency`)."""


@dataclass
class Node:
    id: str
    name: str
    order: int
    color_class: Optional[str] = None
    link: Optional[str] = None
    source_file: bool = False  # marked `class … srcFile` by build_diagram.py (003 FR-037)


@dataclass
class Edge:
    source: str
    target: str
    label: str


@dataclass
class ResponsibilityEntry:
    names: List[str]
    abstract: Optional[str] = None
    concrete: Optional[str] = None


@dataclass
class CollaborationEntry:
    subject: str
    kind: str  # "oneWay" | "mutual"
    object_text: str
    object_names: List[str]
    details: Dict[str, List[str]] = field(default_factory=dict)  # boundary/rationale/questions


@dataclass
class View:
    lines: List[str]
    eol: str
    final_newline: bool
    fence_start: int
    fence_end: int
    nodes: Dict[str, Node]
    edges: List[Edge]
    has_responsibility: bool
    has_collaboration: bool
    responsibilities: List[ResponsibilityEntry]
    collaborations: List[CollaborationEntry]


# ---- Dependency fence -------------------------------------------------------------

_DECL_BARE = re.compile(r"^\s*(\w+)\s*$")
_DECL_AT = re.compile(r'^\s*(\w+)@\{\s*label:\s*"(.*)"\s*\}\s*$')
_DECL_BRACKET = re.compile(r'^\s*(\w+)\["(.*)"\]\s*$')
_EDGE = re.compile(r"^\s*(\w+)\s+e\d+@-->\|([^|]*)\|\s*(\w+)\s*$")
_CLASS = re.compile(r"^\s*class\s+([\w,]+)\s+(\w+)\s*$")
_CLASSDEF = re.compile(r"^\s*classDef\s+(\w+)\s")
_CLICK_LINK = re.compile(r'^(\s*click\s+(\w+)\s+")([^"]*)("\s+")([^"]*)("\s*)$')
_CLICK_HOVER_ONLY = re.compile(r'^\s*click\s+\w+\s+hoverOnly\s+"[^"]*"\s*$')
_EDGE_SECTION = "%% ---- 엣지 ----"
_NOT_NODES = {"end"}


def clean_name(label):
    """Display name from a node label: drop change-mark prefixes and inline markup."""
    text = re.sub(r"</?(b|s|strong)>", "", label)
    for mark in ("✨", "♻️", "♻", "🗑️", "🗑", "️"):
        text = text.replace(mark, "")
    name = text.split("&nbsp;")[-1].strip()
    return name[:-2] if name.endswith("()") else name


def find_fence(lines):
    """(start, end) line indexes of the Mermaid fence under `### Dependency`."""
    try:
        heading = next(i for i, line in enumerate(lines) if line.strip() == "### Dependency")
    except StopIteration:
        raise ViewFormatError("`### Dependency` 제목이 없음")
    for i in range(heading + 1, len(lines)):
        if lines[i].strip().startswith("### "):
            break
        if lines[i].strip() == "```mermaid":
            for j in range(i + 1, len(lines)):
                if lines[j].strip() == "```":
                    return i, j
            break
    raise ViewFormatError("`### Dependency` 아래 Mermaid 코드 블록이 없음")


def _parse_fence(lines, start, end):
    nodes = {}
    edges = []
    i = start + 1
    if i < end and lines[i].strip() == "---":  # YAML frontmatter
        i += 1
        while i < end and lines[i].strip() != "---":
            i += 1
        i += 1
    in_decls = True
    for k in range(i, end):
        raw = lines[k]
        text = raw.strip()
        if text == _EDGE_SECTION:
            in_decls = False
            continue
        if in_decls:
            if not text or text.startswith(("%%", "flowchart", "subgraph", "direction")):
                continue
            m = _DECL_AT.match(raw) or _DECL_BRACKET.match(raw)
            if m:
                nid, name = m.group(1), clean_name(m.group(2))
            else:
                m = _DECL_BARE.match(raw)
                if not m or m.group(1) in _NOT_NODES:
                    continue
                nid, name = m.group(1), m.group(1)
            if nid not in nodes:
                nodes[nid] = Node(nid, name or nid, len(nodes))
            continue
        m = _EDGE.match(raw)
        if m:
            label = m.group(2).strip()
            if len(label) >= 2 and label[0] == label[-1] == '"':
                label = label[1:-1]  # build_diagram quotes a label that starts with `@`
            edges.append(Edge(m.group(1), m.group(3), label))
            continue
        m = _CLASS.match(raw)
        if m and m.group(2) == "srcFile":
            for nid in m.group(1).split(","):
                if nid in nodes:
                    nodes[nid].source_file = True
            continue
        if m and not m.group(2).startswith("crud"):
            for nid in m.group(1).split(","):
                if nid in nodes and nodes[nid].color_class is None:
                    nodes[nid].color_class = m.group(2)
            continue
        m = _CLICK_LINK.match(raw)
        if m and m.group(2) in nodes:
            nodes[m.group(2)].link = m.group(3)
    return nodes, edges


# ---- Body sections ----------------------------------------------------------------

_STRONG = re.compile(r"<strong>(.*?)</strong>")
_MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_DETAIL_TITLES = {
    "책임의 경계": "boundary",
    "분리 이유 & 합리성 평가": "rationale",
    "내가 할 수 있는 질문": "questions",
}


def plain(markdown):
    """Text only: drop <strong>, Markdown links (keep their text), and backticks."""
    text = _MD_LINK.sub(r"\1", markdown)
    text = re.sub(r"</?strong>", "", text)
    return text.replace("`", "").strip()


def _section(lines, heading):
    """Line range (start, end) after a `### heading`, or None if absent."""
    for i, line in enumerate(lines):
        if line.strip() == heading:
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("### ") or lines[j].strip().startswith("<style>"):
                    return i + 1, j
            return i + 1, len(lines)
    return None


def _subsection(lines, rng, heading):
    if rng is None:
        return []
    start, end = rng
    for i in range(start, end):
        if lines[i].strip() == heading:
            out = []
            for j in range(i + 1, end):
                if lines[j].startswith(("#### ", "### ")) or lines[j].strip() == "</details>":
                    break
                out.append(lines[j])
            return out
    return []


def _top_items(block):
    """Split a bullet block into (first line, [nested lines]) per top-level `- ` item."""
    items = []
    for line in block:
        if line.startswith("- "):
            items.append((line[2:], []))
        elif items and line.startswith("  "):
            items[-1][1].append(line)
    return items


def _parse_responsibilities(lines, rng):
    entries = []
    for head, sub in _top_items(_subsection(lines, rng, "#### 요소의 책임")):
        names = [plain(s) for s in _STRONG.findall(head)]
        if not names:
            continue
        entry = ResponsibilityEntry(names)
        for line in sub:
            m = re.match(r"^\s{2}- <strong>(책임 \(추상\)|역할 \(구체\))</strong>:\s*(.*)$", line)
            if m:
                if m.group(1).startswith("책임"):
                    entry.abstract = m.group(2).strip()
                else:
                    entry.concrete = m.group(2).strip()
        entries.append(entry)
    return entries


def _parse_collaborations(lines, rng):
    entries = []
    for head, sub in _top_items(_subsection(lines, rng, "#### 요소 간 비교")):
        names = [plain(s) for s in _STRONG.findall(head)]
        if not names:
            continue
        text = plain(head)
        subject = names[0]
        m = re.match(r"^(.+?)(?:와|과) (.+?)(?:은|는) 서로 의존한다\.?$", text)
        if m and m.group(1).strip() == subject:
            entry = CollaborationEntry(subject, "mutual", m.group(2).strip(), names[1:2])
        else:
            m = re.match(r"^(.+?)(?:은|는) (.+)에 의존한다\.?$", text)
            if not m or m.group(1).strip() != subject:
                continue
            entry = CollaborationEntry(subject, "oneWay", m.group(2).strip(), names[1:])
        current = None
        for line in sub:
            m = re.match(r"^\s{2}- <strong>(.+?)</strong>\s*$", line)
            if m:
                current = _DETAIL_TITLES.get(m.group(1))
                if current:
                    entry.details[current] = []
                continue
            m = re.match(r"^\s{4}- (.*)$", line)
            if m and current:
                entry.details[current].append(m.group(1).strip())
        entries.append(entry)
    return entries


# ---- Panel-shaping block at the end of the file -------------------------------------

def find_style_block(lines):
    """Inclusive range of the trailing wrapped or legacy hover style block."""
    k = len(lines) - 1
    while k >= 0 and lines[k].strip() == "":
        k -= 1
    if k < 0:
        return None
    if lines[k].strip() == "</details>":
        for s in range(k, -1, -1):
            if lines[s].strip() == '<details class="zenuml-hover-style">':
                body = "\n".join(lines[s:k + 1])
                return (s, k) if "div.mermaidTooltip" in body or ".srcFile" in body else None
        return None
    if lines[k].strip() == "</style>":
        for s in range(k, -1, -1):
            if lines[s].strip() == "<style>":
                body = "\n".join(lines[s:k + 1])
                return (s, k) if "div.mermaidTooltip" in body else None
    return None


# ---- Entry point ------------------------------------------------------------------

def split_lines(text):
    eol = "\r\n" if "\r\n" in text else "\n"
    final_newline = text.endswith("\n")
    body = text[: -len(eol)] if text.endswith(eol) else text
    return body.split(eol), eol, final_newline


def parse(text):
    lines, eol, final_newline = split_lines(text)
    start, end = find_fence(lines)
    nodes, edges = _parse_fence(lines, start, end)
    resp_rng = _section(lines, "### Responsibility")
    collab_rng = _section(lines, "### Collaboration")
    return View(
        lines=lines,
        eol=eol,
        final_newline=final_newline,
        fence_start=start,
        fence_end=end,
        nodes=nodes,
        edges=edges,
        has_responsibility=resp_rng is not None,
        has_collaboration=collab_rng is not None,
        responsibilities=_parse_responsibilities(lines, resp_rng),
        collaborations=_parse_collaborations(lines, collab_rng),
    )


def is_hover_only_click(line):
    return bool(_CLICK_HOVER_ONLY.match(line))


def match_link_click(line) -> Optional[Tuple[str, str, str]]:
    """(node id, target, tooltip) for a linked `click` line, else None."""
    m = _CLICK_LINK.match(line)
    return (m.group(2), m.group(3), m.group(5)) if m else None


def replace_link_tooltip(line, tooltip):
    m = _CLICK_LINK.match(line)
    return m.group(1) + m.group(3) + m.group(4) + tooltip + m.group(6)


def is_classdef(line, name):
    m = _CLASSDEF.match(line)
    return bool(m and m.group(1) == name)


def is_crud_classdef(line):
    m = _CLASSDEF.match(line)
    return bool(m and m.group(1).startswith("crud"))
