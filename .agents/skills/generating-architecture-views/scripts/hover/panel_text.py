"""Build one node's hover-panel text (the `click` tooltip) from the view's own body.

Format (spec FR-011, FR-012; data-model.md "NodePanel"):
  <b>{node name}</b><br/>
  {Responsibility lines, in hover.responsibility order, joined by <br/>}
  <br/><br/>                              (only when both parts exist)
  {Collaboration: the node's own dependencies only, in body order}
"""

import re

from .view_parser import clean_name

RESPONSIBILITY_LABELS = {"abstract": "책임 (추상)", "concrete": "역할 (구체)"}
DETAIL_LABELS = {
    "boundary": "책임의 경계",
    "rationale": "분리 이유 &amp; 합리성 평가",
    "questions": "내가 할 수 있는 질문",
}

_TOKEN = re.compile(r"(`[^`]*`)|(</?strong>)|\[([^\]]*)\]\([^)]*\)")


def _escape(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def to_html(markdown):
    """Body Markdown fragment -> tooltip HTML (research R8). Never contains a `"`."""
    out = []
    pos = 0
    for m in _TOKEN.finditer(markdown):
        out.append(_escape(markdown[pos:m.start()]))
        if m.group(1):
            out.append("<code>" + _escape(m.group(1)[1:-1]) + "</code>")
        elif m.group(2):
            out.append(m.group(2).replace("strong", "b"))
        else:
            out.append(to_html(m.group(3)))
        pos = m.end()
    out.append(_escape(markdown[pos:]))
    return "".join(out)


class PanelBuilder:
    def __init__(self, view, responsibility_items, collaboration_items):
        self.view = view
        self.r_items = list(responsibility_items) if view.has_responsibility else []
        self.c_items = list(collaboration_items) if view.has_collaboration else []
        self.by_name = {}
        for node in view.nodes.values():
            self.by_name.setdefault(node.id, node.id)
            self.by_name.setdefault(node.name, node.id)
        # Body names keep the base name while file-node labels keep the extension (003 FR-036);
        # added last so an exact declaration name still wins.
        for node in view.nodes.values():
            stem, dot, ext = node.name.rpartition(".")
            if dot and stem and ext:
                self.by_name.setdefault(stem, node.id)

    def node_id(self, name):
        # body names follow the node-label rule too, so `drag()` finds the `drag()` node
        return self.by_name.get(clean_name(name))

    # -- Responsibility ------------------------------------------------------------

    def _responsibility(self, node_id):
        if not self.r_items:
            return []
        for entry in self.view.responsibilities:
            if node_id in [self.node_id(name) for name in entry.names]:
                lines = []
                for item in self.r_items:
                    text = entry.abstract if item == "abstract" else entry.concrete
                    if text:
                        lines.append("<b>" + RESPONSIBILITY_LABELS[item] + "</b>: " + to_html(text))
                return lines
        return []

    # -- Collaboration -------------------------------------------------------------

    def _out_labels(self, source, targets):
        return {e.label for e in self.view.edges if e.source == source and e.target in targets}

    def _relation(self, node_id, entry, other, own_entries):
        """Edge label for this panel's node (research R7); None if not unique."""
        if entry.kind == "mutual":  # always the edge leaving this panel's node
            labels = self._out_labels(node_id, {self.node_id(other)})
        else:
            targets = {self.node_id(name) for name in entry.object_names} - {None}
            if not targets:  # collective phrase: edges not claimed by the node's other entries
                claimed = set()
                for other in own_entries:
                    if other is not entry:
                        claimed |= {self.node_id(n) for n in other.object_names}
                targets = {e.target for e in self.view.edges if e.source == node_id} - claimed
            labels = self._out_labels(node_id, targets)
        return labels.pop() if len(labels) == 1 else None

    def _own_entries(self, node_id):
        own = []
        for entry in self.view.collaborations:
            subject = self.node_id(entry.subject)
            if entry.kind == "oneWay" and subject == node_id:
                own.append((entry, entry.object_text))
            elif entry.kind == "mutual":
                partner = self.node_id(entry.object_text)
                if subject == node_id:
                    own.append((entry, entry.object_text))
                elif partner == node_id:
                    own.append((entry, entry.subject))
        return own

    def _collaboration(self, node_id):
        if not self.c_items:
            return []
        own = self._own_entries(node_id)
        own_entries = [entry for entry, _ in own if entry.kind == "oneWay"]
        details = [item for item in self.c_items if item != "targets"]
        blocks = []
        for entry, other in own:
            relation = self._relation(node_id, entry, other, own_entries)
            if entry.kind == "mutual":
                head = to_html(other) + "와 서로 의존한다"
            else:
                head = to_html(other) + "에 의존한다"
            if relation:
                head += " (" + to_html(relation) + ")"
            lines = ["<b>" + head + "</b>"]
            for item in details:
                paragraph = " ".join(to_html(x) for x in entry.details.get(item, []))
                if paragraph:
                    lines.append("<b>" + DETAIL_LABELS[item] + "</b>: " + paragraph)
            blocks.append("<br/>".join(lines))
        return blocks

    # -- Panel ----------------------------------------------------------------------

    def panel(self, node_id):
        """Tooltip text for one node, or None when neither part has content."""
        parts = []
        responsibility = self._responsibility(node_id)
        if responsibility:
            parts.append("<br/>".join(responsibility))
        blocks = self._collaboration(node_id)
        if blocks:
            has_details = any(item != "targets" for item in self.c_items)
            parts.append(("<br/><br/>" if has_details else "<br/>").join(blocks))
        if not parts:
            return None
        node = self.view.nodes[node_id]
        return "<b>" + to_html(node.name) + "</b><br/>" + "<br/><br/>".join(parts)
