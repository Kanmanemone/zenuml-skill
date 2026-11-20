#!/usr/bin/env python3
"""Fill the fixed parts of an architecture view's Dependency diagram, in place.

The skill writes only the basic diagram: `flowchart LR`, node/group declarations, edges as
`Source -->|관계| Target`, `class <Id> crud*` lines for change marks, and `click` lines. This
script adds what follows from rules alone (references/templates.md, "Dependency template"):
the YAML config block (with `layout`), edge IDs `eN@`, one color class per node and one edge
class per source node (six Okabe-Ito colors in node declaration order, cycling), the four
section comments, the label-convention comment, the three `classDef crud*` lines, and the
three-line change-mark explanation when any CRUD class is used.

Usage: python3 build_diagram.py <.zenuml/<slug>.architecture.md> [--layout=<renderer>]
--layout is a renderer the request itself names; otherwise the dependency.renderer setting
decides (`elk` -> layout: elk, `default` -> no layout line).
Requires Python 3.9+, standard library only. Exits non-zero (file untouched) on any problem.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hover.settings import load_settings  # noqa: E402

PALETTE = ["#E69F00", "#56B4E9", "#009E73", "#0072B2", "#D55E00", "#CC79A7"]
CONFIG = [
    "---",
    "config:",
    "{layout}",
    "  flowchart:",
    "    curve: basis",
    "    nodeSpacing: 45",
    "    rankSpacing: 70",
    "    titleTopMargin: 25",
    '  themeCSS: ".cluster-label text { font-size: 20px !important; font-weight: 700 !important; }'
    ' .edgeLabel, .edgeLabel p { background-color: transparent !important; }'
    ' .labelBkg { background-color: color-mix(in srgb, var(--vscode-editor-background, #ffffff) 70%,'
    ' transparent) !important; }"',
    "---",
]
CRUD = [
    "  %% ---- CRUD 표시 (테두리 색은 건드리지 않음) ----",
    "  %% 라벨: ✨&nbsp;<b>추가</b> · ♻️&nbsp;변경 · 🗑️&nbsp;<s>삭제</s>",
    "  classDef crudCreate stroke-width:5px",
    "  classDef crudUpdate stroke-dasharray:12 4 2 4",
    "  classDef crudDelete stroke-dasharray:5 10,color:#6B7280",
]
EDGE = re.compile(r"^(\s*)([A-Za-z_]\w*)\s*-->\s*\|([^|]*)\|\s*([A-Za-z_]\w*)\s*$")
CRUD_CLASS = re.compile(r"^\s*class\s+\S+\s+crud(Create|Update|Delete)\s*$")
NODE = re.compile(r"^\s*([A-Za-z_]\w*)")
STRUCTURE = re.compile(r"^\s*(subgraph\b|end\s*$|direction\b|flowchart\b|%%)")


class BuildError(Exception):
    pass


def class_base(node_id):
    return node_id[0].lower() + node_id[1:]


def build(fence_lines, layout):
    """fence_lines: the lines between ```mermaid and ```. Returns the completed lines."""
    if any(re.search(r"\be\d+@-->", line) for line in fence_lines):
        raise BuildError("다이어그램에 이미 엣지 ID가 있음")
    declarations, edges, crud, clicks = [], [], [], []
    declared, edge_nodes = [], []
    for line in fence_lines:
        stripped = line.strip()
        match = EDGE.match(line)
        if match:
            edges.append(match.groups())
            edge_nodes += [match.group(2), match.group(4)]
        elif CRUD_CLASS.match(line):
            crud.append(line)
        elif stripped.startswith("click "):
            clicks.append(line)
        elif stripped.startswith("---") or stripped.startswith("config:"):
            raise BuildError("다이어그램에 이미 설정 블록이 있음")
        elif edges and stripped:
            raise BuildError("엣지 뒤에서 알 수 없는 줄: " + stripped)
        else:
            declarations.append(line)
            if stripped and not STRUCTURE.match(line):
                declared.append(NODE.match(line).group(1))
    if not edges:
        raise BuildError("엣지가 없음")

    nodes = list(dict.fromkeys(declared + edge_nodes))
    while declarations and not declarations[-1].strip():
        declarations.pop()
    color = {node: PALETTE[i % len(PALETTE)] for i, node in enumerate(nodes)}

    out = [("  layout: " + layout if c == "{layout}" else c) for c in CONFIG if c != "{layout}" or layout]
    out += declarations + ["", "  %% ---- 엣지 ----"]
    by_source = {}
    for i, (indent, source, label, target) in enumerate(edges):
        if label.strip().startswith("@"):
            label = '"' + label.strip() + '"'  # mermaid 12.2 cannot parse an edge text that starts with `@`
        out.append("  " + source + " e" + str(i) + "@-->|" + label + "| " + target)
        by_source.setdefault(source, []).append(i)
    out += ["", "  %% ---- 노드 스타일 ----"]
    for node in nodes:
        out.append("  classDef " + class_base(node) + "Node stroke:" + color[node] + ",stroke-width:3px")
        out.append("  class " + node + " " + class_base(node) + "Node")
    out += ["", "  %% ---- 엣지 스타일 (출발 노드 색과 동일) ----"]
    for source, ids in by_source.items():
        out.append("  classDef " + class_base(source) + "Edge stroke:" + color[source] + ",stroke-width:3.5px")
        out += ["  class e" + str(i) + " " + class_base(source) + "Edge" for i in ids]
    out += [""] + CRUD + [line.rstrip() for line in crud]
    if crud:
        out.append('  CrudLegend@{ shape: text, label: "✨: 추가<br/>♻️: 변경<br/>🗑️: 삭제" }')
    if clicks:
        out += [""] + [line.rstrip() for line in clicks]
    return out


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    layout = None
    for arg in list(args):
        if arg.startswith("--layout="):
            layout = arg[len("--layout="):]
            args.remove(arg)
    if len(args) != 1:
        print("usage: build_diagram.py <.zenuml/<slug>.architecture.md> [--layout=<renderer>]", file=sys.stderr)
        return 2
    path = Path(args[0])
    if layout is None:
        layout = "elk" if load_settings()["values"]["dependency.renderer"] == "elk" else ""
    try:
        text = path.read_bytes().decode("utf-8")
        nl = "\r\n" if "\r\n" in text else "\n"
        lines = text.split(nl)
        start = lines.index("### Dependency")
        open_i = next(i for i in range(start, len(lines)) if lines[i].strip() == "```mermaid")
        close_i = next(i for i in range(open_i + 1, len(lines)) if lines[i].strip() == "```")
        built = build(lines[open_i + 1:close_i], layout)
    except (OSError, ValueError, StopIteration, BuildError) as e:
        print("다이어그램 서식 실패: " + str(e), file=sys.stderr)
        return 1
    lines[open_i + 1:close_i] = built
    path.write_bytes(nl.join(lines).encode("utf-8"))
    print("다이어그램 서식 적용: " + str(path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
