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

# 003 FR-037: a node's source file name, drawn only by this style (GitHub ignores it). Mermaid's
# node box is 16px wider and 12px taller than its label box on each side; the offsets put the
# name just inside the 3px border.
SOURCE_BASE = """.node.srcFile foreignObject { overflow: visible; }
.node.srcFile .label foreignObject > div { position: relative; }
"""
SOURCE_RULE = (".srcFile.{color} .nodeLabel::before {{ content: \"{file}\"; position: absolute; top: -9px; {side}: -13px;"
               " font-size: 10px; line-height: 1; font-weight: normal; color: #9CA3AF; }}\n")

_BLOCKS = {"bottom": BOTTOM, "node": NODE}


def block_for(position, source_files=(), side="right"):
    """position: hover.position, or None for no panel rules. source_files: (color class, file name)."""
    rules = "".join(SOURCE_RULE.format(color=color, file=name.replace("\\", "\\\\").replace('"', '\\"'), side=side)
                    for color, name in source_files)
    return OPEN + _BLOCKS.get(position, "") + (SOURCE_BASE + rules if rules else "") + CLOSE
