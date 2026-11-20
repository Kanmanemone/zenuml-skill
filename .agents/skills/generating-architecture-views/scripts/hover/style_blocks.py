"""The fixed hover-panel <style> blocks, one per hover.position value.

Source of truth: the verified test documents in docs/hover-tooltip-test/ —
  wrapper/bottom -> details-wrapped-style.md, node -> node-25em.md.
If the CSS changes, change it there and here together. Stored with "\n" line endings;
the caller converts to the target file's line ending.
"""

OPEN = """<details class="zenuml-hover-style">
<summary>이 문서에 적용되지 못한 &lt;style&gt; 코드 (<a href="https://github.github.com/gfm/#disallowed-raw-html-extension-">관련 GFM 공식 문서</a>)</summary>

<style>"""
CLOSE = """</style>

</details>"""

BOTTOM = OPEN + """
.zenuml-hover-style {
  display: none;
}
div.mermaidTooltip {
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
""" + CLOSE

NODE = OPEN + """
.zenuml-hover-style {
  display: none;
}
div.mermaidTooltip {
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
""" + CLOSE

_BLOCKS = {"bottom": BOTTOM, "node": NODE}


def block_for(position):
    return _BLOCKS[position]
