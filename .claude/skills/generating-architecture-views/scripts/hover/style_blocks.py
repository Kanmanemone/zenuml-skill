"""The fixed hover-panel <style> blocks, one per hover.position value.

Source of truth: the verified test documents in docs/hover-tooltip-test/ —
  bottom -> inline-style.md, node -> node-25em.md.
If the CSS changes, change it there and here together. Stored with "\n" line endings;
the caller converts to the target file's line ending.
"""

BOTTOM = """<style>
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
.node.clickable:hover .nodeLabel {
  text-decoration: underline;
}
</style>"""

NODE = """<style>
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
</style>"""

_BLOCKS = {"bottom": BOTTOM, "node": NODE}


def block_for(position):
    return _BLOCKS[position]
