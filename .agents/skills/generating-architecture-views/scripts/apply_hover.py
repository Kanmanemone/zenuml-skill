#!/usr/bin/env python3
"""Fill (or remove) the node hover panels of an architecture view file, in place.

Deterministic: copies each node's Responsibility and its own Collaboration entries from
the file's body into the Dependency diagram's `click` tooltips, adds a non-navigating
`click Id hoverOnly "..."` line for nodes without a link (plus `,cursor:auto` on that
node's color class), and appends the fixed panel-shaping <style> block for hover.position.
When hover is off (or no node has content), it restores the pre-feature form instead.
The body itself is never changed. Running it twice with the same settings changes nothing.

Usage: python3 apply_hover.py <view.architecture.md>
         [--enabled=true|false] [--responsibility=abstract,concrete]
         [--collaboration=targets,boundary,rationale,questions] [--position=bottom|node]
The options override settings.jsonc for this run only (a value stated in the request).
Requires Python 3.9+, standard library only. Contract: specs/009-hover-detail-panel/contracts/.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hover import settings as settings_mod  # noqa: E402
from hover.panel_text import PanelBuilder  # noqa: E402
from hover.style_blocks import block_for  # noqa: E402
from hover.view_parser import (  # noqa: E402
    ViewFormatError,
    find_style_block,
    is_classdef,
    is_crud_classdef,
    is_hover_only_click,
    match_link_click,
    parse,
    replace_link_tooltip,
)

CURSOR = ",cursor:auto"
OVERRIDES = {
    "enabled": "hover.enabled",
    "responsibility": "hover.responsibility",
    "collaboration": "hover.collaboration",
    "position": "hover.position",
}


def fail(message, code):
    sys.stderr.write(message + "\n")
    sys.exit(code)


def parse_override(name, raw):
    if name == "enabled":
        return {"true": True, "false": False}.get(raw.strip().lower(), raw)
    if name in ("responsibility", "collaboration"):
        return [item.strip() for item in raw.split(",") if item.strip()] if raw.strip() else []
    return raw.strip()


def effective_settings(args):
    loaded = settings_mod.load_settings()
    values, notices = loaded["values"], list(loaded["notices"])
    options = {option["key"]: option for option in settings_mod.load_schema()}
    for name, key in OVERRIDES.items():
        raw = getattr(args, name)
        if raw is None:
            continue
        value = parse_override(name, raw)
        if settings_mod.is_valid(options[key], value):
            values[key] = value
        else:
            notices.append(settings_mod.notice("명령줄 `" + key + "` 값이 허용되지 않아 설정 값 사용"))
    return values, notices


def file_name(target):
    """Pre-feature tooltip: the target's last path segment (003 click rule)."""
    path = target.split("?", 1)[0].split("#", 1)[0].rstrip("/\\")
    return path.replace("\\", "/").rsplit("/", 1)[-1] or target


def strip_hover_marks(lines, fence_start, fence_end):
    """Remove hoverOnly lines, trailing blank lines inside the fence, and ,cursor:auto."""
    inside = []
    for line in lines[fence_start + 1:fence_end]:
        if is_hover_only_click(line):
            continue
        if line.rstrip().endswith(CURSOR) and line.lstrip().startswith("classDef "):
            line = line.rstrip()[: -len(CURSOR)]
        inside.append(line)
    while inside and inside[-1].strip() == "":
        inside.pop()
    return lines[: fence_start + 1] + inside + lines[fence_end:]


def strip_style_block(lines):
    found = find_style_block(lines)
    if not found:
        return lines
    start = found[0]
    while start > 0 and lines[start - 1].strip() == "":
        start -= 1
    return lines[:start]


def transform(text, values):
    view = parse(text)
    eol = view.eol
    lines = strip_style_block(strip_hover_marks(view.lines, view.fence_start, view.fence_end))
    view = parse(eol.join(lines) + (eol if view.final_newline else ""))
    lines = view.lines

    on = values["hover.enabled"] and (values["hover.responsibility"] or values["hover.collaboration"])
    builder = PanelBuilder(view, values["hover.responsibility"], values["hover.collaboration"])
    panels = {}
    if on:
        for node_id in view.nodes:
            panel = builder.panel(node_id)
            if panel:
                panels[node_id] = panel

    last_link = None
    for i in range(view.fence_start + 1, view.fence_end):
        found = match_link_click(lines[i])
        if not found:
            continue
        node_id, target, _ = found
        lines[i] = replace_link_tooltip(lines[i], panels.get(node_id, file_name(target)))
        last_link = i

    if panels:
        hover_only = [n for n in view.nodes.values() if n.link is None and n.id in panels]
        if hover_only:
            indent = "  "
            new_lines = [indent + 'click ' + n.id + ' hoverOnly "' + panels[n.id] + '"' for n in hover_only]
            if last_link is not None:
                lines[last_link + 1:last_link + 1] = new_lines
            else:
                crud = [i for i in range(view.fence_start + 1, view.fence_end) if is_crud_classdef(lines[i])]
                at = (crud[-1] if crud else view.fence_end - 1) + 1
                lines[at:at] = [""] + new_lines
            classes = {n.color_class for n in hover_only if n.color_class}
            for i, line in enumerate(lines):
                for name in classes:
                    if is_classdef(line, name):
                        lines[i] = line.rstrip() + CURSOR
        while lines and lines[-1].strip() == "":
            lines.pop()
        lines += [""] + block_for(values["hover.position"]).split("\n")

    result = eol.join(lines) + (eol if view.final_newline else "")
    return result, len(panels)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Fill or remove node hover panels in an architecture view file.")
    parser.add_argument("file")
    for name in OVERRIDES:
        parser.add_argument("--" + name)
    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit(1)

    path = Path(args.file)
    try:
        with open(path, encoding="utf-8", newline="") as f:
            original = f.read()
    except OSError as error:
        fail("읽을 수 없음: " + str(path) + " (" + str(error) + ")", 1)

    values, notices = effective_settings(args)
    try:
        result, count = transform(original, values)
    except ViewFormatError as error:
        fail("구조 뷰 형식이 아님: " + str(path) + " — " + str(error), 2)

    if result == original:
        print("변경 없음: " + str(path))
    else:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(result)
        if count:
            print("hover 적용: " + str(path) + " (노드 " + str(count) + "개에 패널, 위치 " + values["hover.position"] + ")")
        else:
            print("hover 해제: " + str(path))
    for line in notices:
        print(line)


if __name__ == "__main__":
    main()
