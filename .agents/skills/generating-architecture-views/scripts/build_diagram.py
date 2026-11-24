#!/usr/bin/env python3
"""Fill the fixed parts of an architecture view's Dependency diagram, in place.

The skill writes only the basic diagram: `flowchart LR`, node/group declarations, edges as
`Source -->|관계| Target`, `class <Id> crud*` lines for change marks, and `click` lines. This
script adds what follows from rules alone (references/templates.md, "Dependency template"):
the YAML config block (with `layout`), edge IDs `eN@`, one color class per node and one edge
class per source node (six Okabe-Ito colors in node declaration order, cycling), the four
section comments, the label-convention comment, the three `classDef crud*` lines, and the
three-line change-mark explanation when any CRUD class is used. From each `click` target it
marks linked nodes that are not the file itself with `class … srcFile` (apply_hover.py draws
their file name) and, for a node that is the file itself, drops the extension when
dependency.nodeNameFormat.fileExtensions is false. When dependency.faintNonUsageEdges is on, an edge
whose label is exactly 생성, 전달, or 타입 참조 (a non-usage dependency) gets a faint edge class in its
source color, is written before the solid edges so it is drawn beneath them, and adds one legend line.
When dependency.linkStyle is plain, the config's themeCSS makes linked node names keep the text color, without the resting underline.

Usage: python3 build_diagram.py <.zenuml/<slug>.architecture.md> [--layout=<renderer>]
       [--file-extensions=true|false] [--faint-edges=true|false] [--link-style=plain|link]
--layout is a renderer the request itself names; otherwise the dependency.renderer setting
decides (`elk` -> layout: elk, `default` -> no layout line). --file-extensions, --faint-edges, and
--link-style are values the request itself states; otherwise settings.jsonc decides.
Requires Python 3.9+, standard library only. Exits non-zero (file untouched) on any problem.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from apply_hover import file_name  # noqa: E402
from hover import settings as settings_mod  # noqa: E402
from hover.view_parser import clean_name, match_link_click  # noqa: E402

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
DECL = re.compile(r'^(\s*)(\w+)(?:@\{\s*label:\s*"(.*)"\s*\}|\["(.*)"\])?\s*$')
FILE_EXTENSIONS = "dependency.nodeNameFormat.fileExtensions"
FAINT_EDGES = "dependency.faintNonUsageEdges"
LINK_STYLE = "dependency.linkStyle"
FLAGS = {"--file-extensions=": FILE_EXTENSIONS, "--faint-edges=": FAINT_EDGES, "--link-style=": LINK_STYLE}
# link text inherits the node text color and drops the link underline, so a linked name looks like
# any other; the hover underline (009) sits on the outer .nodeLabel and still shows (003 FR-046)
LINK_RULE = " .node a, .node a:hover { color: inherit !important; text-decoration: none !important; }"
FAINT_LABELS = {"생성", "전달", "타입 참조"}
FAINT_LEGEND = "옅은 간선: 사용 외 의존 (생성·전달 등)"
STRUCTURE = re.compile(r"^\s*(subgraph\b|end\s*$|direction\b|flowchart\b|%%)")


class BuildError(Exception):
    pass


def class_base(node_id):
    return node_id[0].lower() + node_id[1:]


def label_sources(declarations, clicks, file_extensions):
    """Find linked nodes that need a source file name. A node whose label already is that file
    name is the file itself (the skill's fileExtensions judgment): no mark, and its extension goes
    when file_extensions is off. Every linked label is wrapped in an HTML link to the same target:
    VS Code's preview opens only HTML links, not the SVG link a `click` line makes (bug
    architecture-view-local-link-click). Returns (declarations, marked node ids)."""
    targets = {}
    for line in clicks:
        found = match_link_click(line)
        if found:
            targets[found[0]] = found[1]
    out, marked = [], []
    for line in declarations:
        m = DECL.match(line)
        if not m or m.group(2) not in targets:
            out.append(line)
            continue
        indent, node, target = m.group(1), m.group(2), targets[m.group(2)]
        name = file_name(target)
        label = m.group(3) or m.group(4) or node
        if clean_name(label) != name:
            marked.append(node)
        elif not file_extensions and "." in name:
            i = label.rindex(name)
            label = label[:i] + name.rsplit(".", 1)[0] + label[i + len(name):]
        href = target.replace("&", "&amp;").replace("'", "&#39;").replace('"', "&quot;")
        out.append(indent + node + "@{ label: \"<a href='" + href + "'>" + label + '</a>" }')
    return out, marked


def build(fence_lines, layout, file_extensions=True, faint_edges=False, link_style="link"):
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

    declarations, marked = label_sources(declarations, clicks, file_extensions)
    nodes = list(dict.fromkeys(declared + edge_nodes))
    while declarations and not declarations[-1].strip():
        declarations.pop()
    color = {node: PALETTE[i % len(PALETTE)] for i, node in enumerate(nodes)}

    faint = {i for i, edge in enumerate(edges) if faint_edges and edge[2].strip() in FAINT_LABELS}
    out = [("  layout: " + layout if c == "{layout}" else c) for c in CONFIG if c != "{layout}" or layout]
    if link_style == "plain":
        out = [c[:-1] + LINK_RULE + '"' if c.startswith("  themeCSS:") else c for c in out]
    if faint:  # keeps the legend line on one line (text nodes wrap at about 200px)
        out.insert(out.index("    curve: basis") + 1, "    wrappingWidth: 400")
    out += declarations + ["", "  %% ---- 엣지 ----"]
    by_source = {}
    # faint edges first: SVG draws later elements on top, so they lie beneath the solid ones
    for i in sorted(range(len(edges)), key=lambda i: i not in faint):
        indent, source, label, target = edges[i]
        if label.strip().startswith("@"):
            label = '"' + label.strip() + '"'  # mermaid 12.2 cannot parse an edge text that starts with `@`
        out.append("  " + source + " e" + str(i) + "@-->|" + label + "| " + target)
        by_source.setdefault(source, []).append(i)
    out += ["", "  %% ---- 노드 스타일 ----"]
    for node in nodes:
        out.append("  classDef " + class_base(node) + "Node stroke:" + color[node] + ",stroke-width:3px")
        out.append("  class " + node + " " + class_base(node) + "Node")
    if marked:
        out.append("  class " + ",".join(marked) + " srcFile")
    out += ["", "  %% ---- 엣지 스타일 (출발 노드 색과 동일) ----"]
    for source, ids in by_source.items():
        base, c = class_base(source), color[source]
        solid = sorted(i for i in ids if i not in faint)
        if solid:
            out.append("  classDef " + base + "Edge stroke:" + c + ",stroke-width:3.5px")
        if len(solid) < len(ids):
            out.append("  classDef " + base + "Faint stroke:" + c + "4D,stroke-width:3px,color:" + c + "80")
        out += ["  class e" + str(i) + " " + base + ("Faint" if i in faint else "Edge") for i in sorted(ids)]
    out += [""] + CRUD + [line.rstrip() for line in crud]
    legend = (["✨: 추가<br/>♻️: 변경<br/>🗑️: 삭제"] if crud else []) + ([FAINT_LEGEND] if faint else [])
    if legend:
        out.append('  CrudLegend@{ shape: text, label: "' + "<br/>".join(legend) + '" }')
    if clicks:
        out += [""] + [line.rstrip() for line in clicks]
    return out


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    layout = None
    values = settings_mod.load_settings()["values"]
    options = {option["key"]: option for option in settings_mod.load_schema()}
    for arg in list(args):
        if arg.startswith("--layout="):
            layout = arg[len("--layout="):]
            args.remove(arg)
        for flag, key in FLAGS.items():
            if arg.startswith(flag):
                raw = arg[len(flag):].strip()
                value = {"true": True, "false": False}.get(raw.lower(), raw)
                if settings_mod.is_valid(options[key], value):
                    values[key] = value
                else:
                    print(settings_mod.notice("명령줄 `" + key + "` 값이 허용되지 않아 설정 값 사용"))
                args.remove(arg)
    if len(args) != 1:
        print("usage: build_diagram.py <.zenuml/<slug>.architecture.md> [--layout=<renderer>]"
              " [--file-extensions=true|false] [--faint-edges=true|false] [--link-style=plain|link]", file=sys.stderr)
        return 2
    path = Path(args[0])
    if layout is None:
        layout = "elk" if values["dependency.renderer"] == "elk" else ""
    try:
        text = path.read_bytes().decode("utf-8")
        nl = "\r\n" if "\r\n" in text else "\n"
        lines = text.split(nl)
        start = lines.index("### Dependency")
        open_i = next(i for i in range(start, len(lines)) if lines[i].strip() == "```mermaid")
        close_i = next(i for i in range(open_i + 1, len(lines)) if lines[i].strip() == "```")
        built = build(lines[open_i + 1:close_i], layout, values[FILE_EXTENSIONS], values[FAINT_EDGES], values[LINK_STYLE])
    except (OSError, ValueError, StopIteration, BuildError) as e:
        print("다이어그램 서식 실패: " + str(e), file=sys.stderr)
        return 1
    lines[open_i + 1:close_i] = built
    path.write_bytes(nl.join(lines).encode("utf-8"))
    print("다이어그램 서식 적용: " + str(path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
