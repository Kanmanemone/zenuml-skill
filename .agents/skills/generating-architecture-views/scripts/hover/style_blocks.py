"""The fixed hover-panel <style> blocks, one per hover.position value.

Source of truth: the verified test documents in docs/hover-tooltip-test/ —
  wrapper/bottom -> details-wrapped-style.md, node -> node-25em.md.
If the CSS changes, change it there and here together. Stored with "\n" line endings;
the caller converts to the target file's line ending.
"""

OPEN = """<details class="zenuml-hover-style">
<summary>이 문서에 적용되지 못한 &lt;style&gt; 코드 (<a href="https://github.github.com/gfm/#disallowed-raw-html-extension-">관련 GFM 공식 문서</a>)</summary>

<style>
.zenuml-hover-style {
  display: none;
}
"""
CLOSE = """</style>

</details>"""

BOTTOM = """div.mermaidTooltip {
  position: fixed !important;
  top: auto !important;
  left: 12px !important;
  right: 12px;
  bottom: 12px;
  max-width: none !important;
  max-height: calc(100vh - 24px);
  overflow: hidden;
  text-align: left !important;
  font-size: 14px !important;
  columns: 25em;
  column-gap: 2em;
}
div.mermaidTooltip::before {
  content: "";
  float: left;
  height: 3lh;
  overflow: hidden;
}
.node.clickable:hover .nodeLabel {
  text-decoration: underline;
}
"""

NODE = """div.mermaidTooltip {
  max-width: 25em !important;
  width: max-content;
  text-align: left !important;
  position-try-fallbacks: --stay-inside;
}
html {
  position: relative;
}
html:not(:has(g.node.hover)) div.mermaidTooltip {
  display: none;
}
@position-try --stay-inside {
  left: auto;
  right: 12px;
}
.node.clickable:hover .nodeLabel {
  text-decoration: underline;
}
"""

# 003 FR-037: a node's source file name on its top border, drawn only by this style (GitHub
# ignores it). The node box is larger than its label box by 16px/12px per side in Mermaid's `neo`
# look and 30px/15px in `classic` (VS Code preview), so offsets differ per look; a linked node
# carries `data-look` on its wrapping <a>, other nodes on themselves. The background is the
# variable VS Code uses for node fill, so it hides the border line behind the text in any theme.
SOURCE_BASE = """.node.srcFile foreignObject { overflow: visible; }
.node.srcFile .label foreignObject > div { position: relative; }
.node.srcFile .nodeLabel::before { position: absolute; top: -18px; {neo}; font-size: 10px; line-height: 1; font-weight: normal; font-style: italic; white-space: nowrap; padding: 1px 2px; background-color: var(--vscode-editorWidget-background, #ffffff); }
[data-look="classic"] .node.srcFile .nodeLabel::before, .node.srcFile[data-look="classic"] .nodeLabel::before { top: -21px;{classic} }
"""
PLACES = {  # position -> (neo, classic) offsets
    "right": ("right: -5px", " right: -19px;"),
    "left": ("left: -5px", " left: -19px;"),
    "center": ("left: 50%; transform: translateX(-50%)", ""),
}

_BLOCKS = {"bottom": BOTTOM, "node": NODE}


def _css_string(text):
    return text.replace("\\", "\\\\").replace('"', '\\"')


def block_for(position, source_files=(), side="right"):
    """position: hover.position, or None for no panel rules.
    source_files: (color class, file name, border color or None) per node; side: sourceFile.position."""
    rules = "".join('.srcFile.' + color + ' .nodeLabel::before { content: "' + _css_string(name) + '";'
                    + (" color: " + stroke + ";" if stroke else "") + " }\n"
                    for color, name, stroke in source_files)
    neo, classic = PLACES[side]
    base = SOURCE_BASE.replace("{neo}", neo).replace("{classic}", classic) if rules else ""
    return OPEN + _BLOCKS.get(position, "") + base + rules + CLOSE
