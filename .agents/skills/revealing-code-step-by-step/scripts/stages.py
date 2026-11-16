#!/usr/bin/env python3
"""Deterministic half of the revealing-code-step-by-step skill.

    stages.py prepare <view.architecture.md> [--show=a,b] [--hide=a,b] [--output-dir=rel] [--pick=Id:n,...]
    stages.py build   <result dir>

Each command prints one line of JSON on stdout (prepare then prints each node's source with its unfold
units). Every code scene is built here from the source and work/outline.json; the model writes only the
situation prose (stage 1) and that one file. Errors go to stderr as one Korean line.
Exit codes: 0 ok, 2 bad input, 3 the scenes do not reach the source (build).
Python 3.9+, standard library only. See specs/010-stepwise-code-convergence/contracts/.
"""

import argparse
import difflib
import html
import json
import re
import shutil
import sys
import urllib.request
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
STAGES_FILE = SKILL_DIR / "stages.md"
PROMPT_FILE = SKILL_DIR / "stage1-prompt.md"
OUTLINE_FILE = "outline.json"
SETTINGS_FILE = "settings.jsonc"
SCHEMA_FILE = "settings.schema.json"


class InputError(Exception):
    """Bad input: reported on stderr, exit code 2."""


# ---- output ----------------------------------------------------------------------

def rel(path):
    """Project-relative path with forward slashes when possible (the cwd is the project root)."""
    path = Path(path).resolve()
    try:
        return path.relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def emit(obj):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(obj, ensure_ascii=False))


def write_text(path, text):
    """Write LF text that ends with exactly one newline."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text.rstrip("\n") + "\n")


def read_text(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read().replace("\r\n", "\n")


# ---- settings (same behavior as the other skills' loaders) -----------------------

def strip_json_comments(text):
    """Remove // and /* */ comments, leaving string literals untouched."""
    out, i, n, in_string = [], 0, len(text), False
    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if in_string:
            out.append(ch)
            if ch == "\\":
                out.append(nxt)
                i += 2
                continue
            if ch == '"':
                in_string = False
            i += 1
        elif ch == '"':
            in_string = True
            out.append(ch)
            i += 1
        elif ch == "/" and nxt == "/":
            while i < n and text[i] != "\n":
                i += 1
        elif ch == "/" and nxt == "*":
            i += 2
            while i < n and not (text[i] == "*" and i + 1 < n and text[i + 1] == "/"):
                i += 1
            i += 2
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def settings_notice(text):
    return "⚙️ 설정 안내: " + SETTINGS_FILE + " — " + text


def _get_path(obj, dotted_key):
    node = obj
    for part in dotted_key.split("."):
        if not isinstance(node, dict) or part not in node:
            return False, None
        node = node[part]
    return True, node


def _leaf_paths(obj, opaque, prefix=""):
    """Leaf keys of the settings object; keys in `opaque` (map-valued options) count as one leaf."""
    paths = []
    for key, value in obj.items():
        full = prefix + "." + key if prefix else key
        if isinstance(value, dict) and full not in opaque:
            paths.extend(_leaf_paths(value, opaque, full))
        else:
            paths.append(full)
    return paths


def _valid(option, value):
    kind = option.get("type")
    if kind == "relativePath":
        return (
            isinstance(value, str)
            and value.strip() != ""
            and value[:1] not in ("\\", "/", "~")
            and not (len(value) >= 2 and value[0].isalpha() and value[1] == ":")
        )
    if kind == "stageToggles":
        return isinstance(value, dict)  # per-stage checks happen in plan_stages
    return False


def load_settings(skill_dir=SKILL_DIR):
    with open(Path(skill_dir) / SCHEMA_FILE, encoding="utf-8") as f:
        options = json.load(f).get("options", [])
    values = {o["key"]: o["default"] for o in options}
    notices = []
    path = Path(skill_dir) / SETTINGS_FILE
    if not path.exists():
        return values, notices
    try:
        user = json.loads(strip_json_comments(path.read_text(encoding="utf-8")))
    except ValueError:
        user = None
    if not isinstance(user, dict):
        notices.append(settings_notice("읽지 못해 모든 값을 기본값으로 사용"))
        return values, notices
    opaque = {o["key"] for o in options if o.get("type") == "stageToggles"}
    for option in options:
        found, value = _get_path(user, option["key"])
        if not found:
            continue
        if _valid(option, value):
            values[option["key"]] = value
        else:
            default = option["default"]
            shown = default if isinstance(default, str) else json.dumps(default, ensure_ascii=False)
            notices.append(settings_notice("`" + option["key"] + "` 값이 허용되지 않아 기본값 `" + shown + "` 사용"))
    known = {o["key"] for o in options}
    for leaf in _leaf_paths(user, opaque):
        if leaf not in known:
            notices.append(settings_notice("알 수 없는 키 `" + leaf + "` 무시"))
    return values, notices


# ---- stage definition (stages.md) ------------------------------------------------

BECOMES = "- 원본과 같아지는 것:"
UNREVEALED = "- 아직 드러나지 않은 것:"
KIND = "- 표현:"
KINDS = ("prose", "outline", "unfold", "source")


def parse_stage_definition(path=STAGES_FILE):
    stages, current = [], None
    for line in read_text(path).split("\n"):
        if line.startswith("## "):
            current = {"nickname": line[3:].strip(), "becomes": None, "unrevealed": None, "kind": None}
            stages.append(current)
        elif current is not None:
            for head, field in ((BECOMES, "becomes"), (UNREVEALED, "unrevealed"), (KIND, "kind")):
                if line.startswith(head):
                    current[field] = line[len(head):].strip()
    # A `##` section with none of the fields is prose about the stages (e.g. how to change them), not a stage.
    stages = [s for s in stages if any(s[f] for f in ("becomes", "unrevealed", "kind"))]
    names = [s["nickname"] for s in stages]
    for name in names:
        if not name:
            raise InputError("stages.md에 별명이 빈 단계가 있음")
        if names.count(name) > 1:
            raise InputError("stages.md에 별명 `" + name + "`이 겹침")
    for s in stages:
        if s["kind"] not in KINDS:
            raise InputError("단계 표현은 %s 중 하나여야 함: %s" % (", ".join(KINDS), s["nickname"]))
        for head, field in ((BECOMES, "becomes"), (UNREVEALED, "unrevealed")):
            if not s[field]:
                raise InputError("stages.md의 `" + s["nickname"] + "` 단계에 `" + head + "` 항목이 없음")
    if [s["kind"] for s in stages] != list(KINDS):
        raise InputError("stages.md의 단계 표현은 prose, outline, unfold, source 순서로 하나씩이어야 함")
    return stages


def plan_stages(stages, toggles, show, hide):
    """Which stages are shown (FR-009a). The last stage (source) is always shown."""
    notices = []
    names = [s["nickname"] for s in stages]
    last = names[-1]
    visible = {name: True for name in names}
    for name, value in toggles.items():
        if name == last:
            notices.append(settings_notice("마지막 단계 `" + name + "`는 항상 보이므로 무시"))
        elif name not in visible:
            notices.append(settings_notice("단계 정의에 없는 별명 `" + name + "` 무시"))
        elif not isinstance(value, bool):
            notices.append(settings_notice("`stages." + name + "` 값이 true/false가 아니어서 true 사용"))
        else:
            visible[name] = value
    for names_in_request, value in ((show, True), (hide, False)):
        for name in names_in_request:
            if name == last:
                if not value:
                    notices.append("⚙️ 요청 안내: 마지막 단계 `" + name + "`는 항상 보이므로 무시")
            elif name not in visible:
                notices.append("⚙️ 요청 안내: 단계 정의에 없는 별명 `" + name + "` 무시")
            else:
                visible[name] = value
    return [dict(s, visible=visible[s["nickname"]]) for s in stages], notices


# ---- view parsing (research R2) --------------------------------------------------

DECL_AT = re.compile(r'^\s*(\w+)@\{\s*label:\s*"(.*)"\s*\}\s*$')
DECL_BRACKET = re.compile(r'^\s*(\w+)\["(.*)"\]\s*$')
DECL_BARE = re.compile(r"^\s*(\w+)\s*$")
SUBGRAPH = re.compile(r'^\s*subgraph\s+(\w+)(?:\["(.*)"\])?\s*$')
CLICK_LINK = re.compile(r'^\s*click\s+(\w+)\s+"([^"]*)"')
CLICK_HOVER_ONLY = re.compile(r"^\s*click\s+\w+\s+hoverOnly\b")
NOT_NODES = {"end", "direction", "flowchart", "graph"}


def clean_name(label):
    text = label.replace("&nbsp;", " ")
    text = re.sub(r"</?(b|s|strong)>", "", text)
    for mark in ("✨", "♻️", "♻", "🗑️", "🗑", "️"):
        text = text.replace(mark, "")
    return text.strip()


def parse_view(text):
    lines = text.split("\n")
    try:
        heading = next(i for i, l in enumerate(lines) if l.strip() == "### Dependency")
    except StopIteration:
        raise InputError("구조 뷰 형식이 아님: `### Dependency` 제목이 없음")
    start = end = None
    for i in range(heading + 1, len(lines)):
        if lines[i].strip().startswith("### "):
            break
        if lines[i].strip() == "```mermaid":
            start = i
            for j in range(i + 1, len(lines)):
                if lines[j].strip() == "```":
                    end = j
                    break
            break
    if start is None or end is None:
        raise InputError("구조 뷰 형식이 아님: `### Dependency` 아래 Mermaid 코드 블록이 없음")
    i = start + 1
    if i < end and lines[i].strip() == "---":  # YAML config block
        i += 1
        while i < end and lines[i].strip() != "---":
            i += 1
        i += 1
    nodes, links, groups = {}, {}, []
    for line in lines[i:end]:
        stripped = line.strip()
        if not stripped or stripped.startswith("%%") or stripped.startswith("flowchart") or stripped.startswith("graph"):
            continue
        m = SUBGRAPH.match(line)
        if m:
            groups.append((m.group(1), m.group(2) or m.group(1)))
            continue
        if stripped == "end":
            if groups:
                groups.pop()
            continue
        if stripped.startswith("direction ") or stripped.startswith("class ") or stripped.startswith("classDef ") or stripped.startswith("linkStyle "):
            continue
        if stripped.startswith("click "):
            if CLICK_HOVER_ONLY.match(line):
                continue
            m = CLICK_LINK.match(line)
            if m:
                links[m.group(1)] = m.group(2)
            continue
        if re.match(r"^\s*\w+\s+(?:\w+@)?-->", line):  # edges carry no stage information
            continue
        for pattern in (DECL_AT, DECL_BRACKET, DECL_BARE):
            m = pattern.match(line)
            if m and m.group(1) not in NOT_NODES:
                node_id = m.group(1)
                if node_id not in nodes:
                    label = m.group(2) if m.lastindex and m.lastindex >= 2 else node_id
                    nodes[node_id] = {"id": node_id, "name": clean_name(label) or node_id,
                                      "order": len(nodes), "group_path": list(groups)}
                break
    if not nodes:
        raise InputError("구조 뷰에 노드가 하나도 없음")
    responsibilities = parse_responsibilities(lines)
    for node in nodes.values():
        node["link"] = links.get(node["id"])
        node["responsibility"] = responsibilities.get(node["name"], responsibilities.get(node["id"]))
    return list(nodes.values())


def parse_responsibilities(lines):
    """Name → `책임 (추상)` sentence from `#### 요소의 책임` (spec FR-015e). Unstated ones are left out."""
    found, names, inside = {}, [], False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            inside = stripped == "#### 요소의 책임"
            continue
        if not inside:
            continue
        if line.startswith("- "):
            names = re.findall(r"<strong>\[?(.+?)\]?(?:\([^)]*\))?</strong>", line)
            continue
        m = re.match(r"\s+- <strong>책임 \(추상\)</strong>:\s*(.*)", line)
        if m and m.group(1) and not m.group(1).startswith("설명에 명시되지 않음"):
            for name in names:
                found[name] = m.group(1).strip()
    return found


# ---- documents (FR-015c) ---------------------------------------------------------

def assign_documents(nodes, slug):
    """Set node['doc'] and return [(doc name, title)] in order (data-model Document)."""
    has_groups = any(n["group_path"] for n in nodes)
    if len(nodes) <= 5 or not has_groups:
        for n in nodes:
            n["doc"], n["doc_depth"] = "all.md", 0
        return [("all.md", slug)]
    counts = {}
    for n in nodes:
        if n["group_path"]:
            top = n["group_path"][0]
            counts[top] = counts.get(top, 0) + 1
    docs = []
    for n in nodes:
        top = n["group_path"][0] if n["group_path"] else None
        if top is not None and counts[top] >= 3:
            n["doc"], n["doc_depth"] = top[0] + ".md", 1
            if (n["doc"], top[1]) not in docs:
                docs.append((n["doc"], top[1]))
        else:
            n["doc"], n["doc_depth"] = "others.md", 0
    if any(n["doc"] == "others.md" for n in nodes):
        docs.append(("others.md", "기타"))
    return docs


# ---- reading sources (research R8) -----------------------------------------------

GITHUB_BLOB = re.compile(r"^https://github\.com/([^/]+)/([^/]+)/blob/(.+)$")


def read_source(link, view_dir):
    """(text, None) or (None, skip reason)."""
    if not link:
        return None, "원본 위치가 없어 구체화하지 않음"
    if link.endswith("/"):
        return None, "링크가 파일 하나를 가리키지 않아 구체화하지 않음"
    path_part = link.split("#")[0].split("?")[0]
    if not (path_part.endswith(".kt") or path_part.endswith(".kts")):
        if "." not in path_part.rsplit("/", 1)[-1]:
            return None, "링크가 파일 하나를 가리키지 않아 구체화하지 않음"
        return None, "원본이 Kotlin이 아니어서 구체화하지 않음"
    try:
        if link.startswith("http://") or link.startswith("https://"):
            m = GITHUB_BLOB.match(path_part)
            url = "https://raw.githubusercontent.com/%s/%s/%s" % m.groups() if m else path_part
            with urllib.request.urlopen(url, timeout=20) as r:
                data = r.read()
        else:
            target = (view_dir / path_part).resolve()
            if target.is_dir():
                return None, "링크가 파일 하나를 가리키지 않아 구체화하지 않음"
            data = target.read_bytes()
    except Exception as e:  # noqa: BLE001 — any failure means "unreadable"
        return None, "원본을 읽을 수 없어 구체화하지 않음 (" + type(e).__name__ + ")"
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None, "원본을 UTF-8로 읽을 수 없어 구체화하지 않음"
    if text.startswith("﻿"):
        text = text[1:]
    return text.replace("\r\n", "\n"), None


# ---- declaration spans (research R5) ---------------------------------------------

def mask_code(text):
    """Same-length copy of Kotlin source: strings and chars filled with `_` (so a line that ends in
    a string still ends in a token), comments blanked to spaces; newlines kept."""
    out = list(text)
    n = len(text)

    def blank(a, b, fill=" "):
        for k in range(a, b):
            if out[k] != "\n":
                out[k] = fill

    def skip_string(i):
        """i at opening quote(s); return index after the string, handling ${...} templates."""
        raw = text.startswith('"""', i)
        j = i + (3 if raw else 1)
        while j < n:
            if raw and text.startswith('"""', j):
                j += 3
                while j < n and text[j] == '"':
                    j += 1
                return j
            ch = text[j]
            if not raw and ch == "\\":
                j += 2
                continue
            if not raw and ch == '"':
                return j + 1
            if not raw and ch == "\n":
                return j
            if ch == "$" and j + 1 < n and text[j + 1] == "{":
                j = skip_code(j + 2, "}")
                continue
            j += 1
        return n

    def skip_code(i, closer):
        """Scan code until the matching closer; return index after it."""
        depth = 0
        while i < n:
            ch = text[i]
            if ch == '"':
                i = skip_string(i)
                continue
            if ch == "'":
                i = skip_char(i)
                continue
            if text.startswith("//", i) or text.startswith("/*", i):
                i = skip_comment(i)
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                if depth == 0 and closer == "}":
                    return i + 1
                depth -= 1
            i += 1
        return n

    def skip_char(i):
        j = i + 1
        while j < n and text[j] != "'" and text[j] != "\n":
            j += 2 if text[j] == "\\" else 1
        return min(j + 1, n)

    def skip_comment(i):
        if text.startswith("//", i):
            j = text.find("\n", i)
            return n if j < 0 else j
        depth, j = 0, i
        while j < n:
            if text.startswith("/*", j):
                depth += 1
                j += 2
            elif text.startswith("*/", j):
                depth -= 1
                j += 2
                if depth == 0:
                    return j
            else:
                j += 1
        return n

    i = 0
    while i < n:
        ch = text[i]
        if ch == '"':
            j = skip_string(i)
            blank(i, j, "_")
            i = j
        elif ch == "'":
            j = skip_char(i)
            blank(i, j, "_")
            i = j
        elif text.startswith("//", i) or text.startswith("/*", i):
            j = skip_comment(i)
            blank(i, j)
            i = j
        else:
            i += 1
    return "".join(out)


HEADER = r"\b(?:class|interface|object|fun|typealias|val|var)\b[\w\s<>,.?*]*?(?<![\w.])%s(?![\w])"
CONTINUE_END = ("=", ",", ":", "(", "[", "->", ".", "+", "-", "*", "/", "&&", "||", "?:")
CONTINUE_START = (".", "?.", "?:", "&&", "||", ":", "=", "{", "where ")


def find_declaration(text, names, pick=None):
    """(span, reason, candidates). span is (start_line, end_line), 1-based inclusive, or None.
    When the name is declared more than once (overloads), `pick` (1-based) chooses one; without it
    span is None and `candidates` lists them so the model can choose the semantically main one
    (spec FR-002). research R5."""
    masked = mask_code(text)
    lines = text.split("\n")
    mlines = masked.split("\n")

    def span_of(m):
        pos = m.start()
        start = masked.count("\n", 0, pos)
        while start > 0:
            prev = lines[start - 1].strip()
            if prev and (prev.startswith("@") or prev.startswith("//") or prev.startswith("/*")
                         or prev.startswith("*") or prev.endswith("*/")):
                start -= 1
            else:
                break
        return start + 1, _declaration_end(masked, mlines, pos) + 1

    for name in names:
        pattern = re.compile(HEADER % re.escape(name))
        hits = []
        for m in pattern.finditer(masked):
            after = masked[m.end():m.end() + 40].lstrip(" ")
            if after.startswith("."):
                continue  # receiver type, not the declared name
            hits.append(m)
        if not hits:
            continue
        spans = [span_of(m) for m in hits]
        if len(spans) == 1:
            return spans[0], None, []
        candidates = [{"pick": i + 1, "start_line": a, "end_line": b,
                       "header": lines[masked.count("\n", 0, hits[i].start())].strip()}
                      for i, (a, b) in enumerate(spans)]
        if pick is not None and 1 <= pick <= len(spans):
            return spans[pick - 1], None, candidates
        return None, "원본 파일에 " + name + " 선언이 여럿 — --pick으로 하나를 골라야 함", candidates
    return None, "원본 파일에서 " + names[0] + " 선언을 찾지 못해 구체화하지 않음", []


def _declaration_end(masked, mlines, pos):
    """0-based line where the declaration that starts at `pos` ends."""
    depth = brace = 0
    body = False
    i, n = pos, len(masked)
    while i < n:
        ch = masked[i]
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        elif ch == "{":
            if depth == 0 and brace == 0:
                body = True
            brace += 1
        elif ch == "}":
            brace -= 1
            if body and brace == 0:
                return masked.count("\n", 0, i)
        elif ch == "\n" and depth == 0 and brace == 0 and not body:
            line_no = masked.count("\n", 0, i)
            current = mlines[line_no].rstrip()
            following = next((l.strip() for l in mlines[line_no + 1:] if l.strip()), "")
            if not current.endswith(CONTINUE_END) and not following.startswith(CONTINUE_START):
                return line_no
        i += 1
    return masked.count("\n")


# ---- unfold units and scenes (spec FR-004~005b) ----------------------------------

MAX_UNFOLDS = 4
DECL_HEAD = re.compile(r"^\s*(?:@\w+(?:\([^)]*\))?\s+)*(?:(?:private|protected|internal|public|override|open|abstract|"
                       r"suspend|const|lateinit|inline|operator|data|sealed|enum|inner)\s+)*(val|var|fun)\b")
ENDS_OPEN = re.compile(r"([=,(\[{.+\-*/:]|->|&&|\|\||\?:)\s*$")
STARTS_CLOSED = re.compile(r"^\s*(\.|\?\.|\?:|&&|\|\||\)|\]|->)")
COMMENT_LINE = re.compile(r"^\s*(/\*|\*|//)")
PARAM_HEAD = re.compile(r"^\s+(?:@\w+\s+)*(?:(?:private|protected|internal|public|override|open)\s+)*(?:val\s+|var\s+)?(\w+)\s*:")


def _nesting(masked_line):
    return sum(masked_line.count(c) for c in "({[") - sum(masked_line.count(c) for c in ")}]")


def analyse(text):
    """Header end, parameter spans and the body's top-level items of one source range."""
    lines = text.rstrip("\n").split("\n")
    masked = mask_code(text).rstrip("\n").split("\n")
    depth, body_open, params = 0, None, []
    for i, m in enumerate(masked):
        start_depth = depth
        if COMMENT_LINE.match(lines[i]) and depth == 0:
            continue
        for ch in m:
            if ch in "([":
                depth += 1
            elif ch in ")]":
                depth -= 1
            elif ch == "{" and depth == 0:
                body_open = i
                break
        if body_open is not None:
            break
        p = PARAM_HEAD.match(lines[i]) if start_depth == 1 else None
        if p:
            params.append({"name": p.group(1), "lines": [i]})
        elif start_depth > 1 and params and params[-1]["lines"][-1] == i - 1:
            params[-1]["lines"].append(i)
    if body_open is None or not lines[-1].strip().startswith("}"):
        return {"lines": lines, "body_open": None, "params": [], "items": []}
    body_close = len(lines) - 1
    items, cur, nest, comments, continues = [], None, 0, [], False
    for i in range(body_open + 1, body_close):
        line, m = lines[i], masked[i]
        if not line.strip():
            continue
        if nest == 0 and not continues and COMMENT_LINE.match(line):
            comments.append(i)
            continue
        if cur is None or (nest == 0 and not continues and not STARTS_CLOSED.match(line)):
            cur = {"first": i, "lines": [], "comments": comments}
            comments = []
            items.append(cur)
        cur["lines"].append(i)
        nest += _nesting(m)
        continues = nest > 0 or bool(ENDS_OPEN.search(m.rstrip()))
    if comments and items:
        items[-1]["trailing"] = comments
    for it in items:
        head, code = lines[it["first"]], "\n".join(masked[j] for j in it["lines"])
        name = re.search(r"\b(?:val|var|fun|class|interface|object)\s+(?:<[^>]*>\s*)?(?:\w+\.)?(\w+)", head) or re.search(r"(\w+)", head)
        it["name"] = name.group(1) if name else "?"
        it["private"] = bool(re.search(r"\bprivate\b", head))
        it["state"] = bool(re.match(r"^\s*(?:private\s+)?var\b", head)) and len(it["lines"]) == 1
        flat = code
        for _ in range(4):
            flat = re.sub(r"\([^()]*\)", "", flat)
        it["bodyless"] = bool(DECL_HEAD.match(head)) and "{" not in code and "=" not in flat
        it["kind"] = "fun" if re.search(r"\bfun\b", head) else "prop"
        it.setdefault("trailing", [])
    return {"lines": lines, "body_open": body_open, "params": params, "items": items}


def make_units(info):
    """Unfold units (spec FR-005a): public members or statements in source order, the rest attached."""
    lines, items = info["lines"], info["items"]
    if not items:
        return []

    def uses(unit, name):
        return any(re.search(r"\b%s\b" % re.escape(name), lines[j]) for it in unit["members"] + unit["attached"]
                   for j in it["lines"])
    anchors = [it for it in items if not it["private"] and not it["state"]] or items[:1]
    units = []
    for it in anchors:
        prev = units[-1] if units else None
        if (prev and it["bodyless"] and prev["bodyless"] and prev["kind"] == it["kind"]
                and items.index(prev["members"][-1]) == items.index(it) - 1):
            prev["members"].append(it)
            continue
        units.append({"members": [it], "attached": [], "params": [], "bodyless": it["bodyless"], "kind": it["kind"]})
    placed = {id(m) for u in units for m in u["members"]}
    for it in items:
        if id(it) not in placed:
            owner = next((u for u in units if uses(u, it["name"])), units[0])
            owner["attached"].append(it)
    for p in info["params"]:
        owner = next((u for u in units if uses(u, p["name"])), units[0])
        owner["params"].append(p)

    def size(u):
        return sum(len(it["lines"]) for it in u["members"] + u["attached"])
    while len(units) > MAX_UNFOLDS:
        k = min(range(len(units) - 1), key=lambda i: size(units[i]) + size(units[i + 1]))
        a, b = units[k], units.pop(k + 1)
        for key in ("members", "attached", "params"):
            a[key] += b[key]
    return units


def unit_lines(unit):
    """1-based range lines that belong to a unit (members, attached members, parameters, their comments)."""
    out = set()
    for it in unit["members"] + unit["attached"]:
        out.update(j + 1 for j in it["comments"] + it["lines"] + it["trailing"])
    for p in unit["params"]:
        out.update(j + 1 for j in p["lines"])
    return sorted(out)


def unit_label(unit):
    names = [it["name"] for it in unit["members"]]
    extra = [it["name"] for it in unit["attached"]] + [p["name"] for p in unit["params"]]
    return ", ".join(names) + (" (+ " + ", ".join(extra) + ")" if extra else "")


def render_scene(info, units, placeholders, folds, revealed):
    """Code of the outline (revealed=0) or of the revealed-th unfold. Folds are 1-based (from, to, text)."""
    lines, items, body_open = info["lines"], info["items"], info["body_open"]
    shown = {id(it) for u in units[:revealed] for it in u["members"] + u["attached"]}
    shown_params = {p["lines"][0] for u in units[:revealed] for p in u["params"]}
    param_line = {j: p for p in info["params"] for j in p["lines"]}
    anchor = {id(u["members"][0]): n for n, u in enumerate(units)}
    out, hidden_run = [], False
    for i in range(body_open + 1):
        p = param_line.get(i)
        if p and p["lines"][0] not in shown_params:
            if not hidden_run:
                out.append(re.match(r"^\s*", lines[i]).group(0) + "..." + ("," if shown_params else ""))
                hidden_run = True
            continue
        hidden_run = False if not p or i == p["lines"][0] else hidden_run
        out.append(lines[i])
    fold_at = {f[0] - 1: f for f in folds}
    prev_kind, prev_end = "header", body_open

    def gap(first):
        return any(not lines[j].strip() for j in range(prev_end + 1, first))
    for it in items:
        if id(it) in shown:
            block = it["comments"] + it["lines"] + it["trailing"]
            if prev_kind == "placeholder" or gap(min(block)):
                out.append("")
            skip_to = -1
            for j in it["comments"] + it["lines"]:
                if j <= skip_to:
                    continue
                if j in fold_at:
                    out.append(re.match(r"^\s*", lines[j]).group(0) + "⟨" + fold_at[j][2] + "⟩")
                    skip_to = fold_at[j][1] - 1
                    continue
                out.append(lines[j])
            out += [lines[j] for j in it["trailing"]]
            prev_kind, prev_end = "code", max(block)
        elif id(it) in anchor:
            if prev_kind == "code":
                out.append("")
            out.append(re.match(r"^\s*", lines[it["first"]]).group(0) + "⟨" + placeholders[anchor[id(it)]] + "⟩")
            prev_kind, prev_end = "placeholder", it["lines"][-1]
    if prev_kind == "code" and gap(len(lines) - 1):
        out.append("")
    out.append(lines[-1])
    return "\n".join(out) + "\n"


def same_sentence(a, b):
    return re.sub(r"[\s.]", "", a or "") == re.sub(r"[\s.]", "", b or "")


def check_outline(node, units, info, entry):
    """Reject bad model input for one node (spec FR-005b). Returns (placeholders, folds as tuples)."""
    nid = node["id"]
    if not isinstance(entry, dict):
        raise InputError("%s에 %s 항목이 없음" % (OUTLINE_FILE, nid))
    placeholders = entry.get("placeholders")
    if not isinstance(placeholders, list) or len(placeholders) != len(units):
        raise InputError("%s의 자리표시자는 단위 수와 같은 %d개여야 함" % (nid, len(units)))
    for n, text in enumerate(placeholders, 1):
        if not isinstance(text, str) or not text.strip() or "⟨" in text or "⟩" in text or "\n" in text:
            raise InputError("%s의 %d번째 자리표시자가 비었거나 한 줄 문장이 아님" % (nid, n))
        if same_sentence(text, node.get("responsibility")):
            raise InputError("%s의 %d번째 자리표시자가 책임 한 줄과 같음" % (nid, n))
    folds, used = [], set()
    owner = {}
    for u, unit in enumerate(units):
        for it in unit["members"] + unit["attached"]:
            for j in it["lines"]:
                owner[j + 1] = (u, id(it), it["lines"][0] + 1)
    for f in entry.get("folds") or []:
        try:
            a, b, text = int(f["from"]), int(f["to"]), f["text"]
        except (TypeError, KeyError, ValueError):
            raise InputError("%s의 접기는 {from, to, text} 형식이어야 함" % nid)
        if not isinstance(text, str) or not text.strip() or "\n" in text:
            raise InputError("%s의 %d~%d줄 접기 문장이 비었음" % (nid, a, b))
        span = range(a, b + 1)
        homes = {owner.get(j, (None, None, None))[:2] for j in span}
        if a > b or len(homes) != 1 or None in next(iter(homes)) or a == owner[a][2]:
            raise InputError("%s의 %d~%d줄 접기가 한 멤버의 본문 안에 있지 않음" % (nid, a, b))
        if used & set(span):
            raise InputError("%s의 %d~%d줄 접기가 다른 접기와 겹침" % (nid, a, b))
        used |= set(span)
        folds.append((a, b, text.strip()))
    return [p.strip() for p in placeholders], folds


# ---- prepare ---------------------------------------------------------------------

def manifest_path(result_dir):
    return Path(result_dir) / "work" / "manifest.json"


def load_manifest(result_dir):
    path = manifest_path(result_dir)
    if not path.exists():
        raise InputError("작업 폴더가 아님(먼저 prepare를 실행): " + rel(path))
    return json.loads(read_text(path))


def split_list(value):
    return [v.strip() for v in value.split(",") if v.strip()] if value else []


def declaration_names(node):
    """Names to look for: the node Id, then the display name when it is an identifier."""
    names = [node["id"]]
    if node["name"] != node["id"] and re.fullmatch(r"[A-Za-z_]\w*", node["name"]):
        names.append(node["name"])
    return names


def cmd_prepare(args):
    view = Path(args.view)
    if not view.name.endswith(".architecture.md") or not view.is_file():
        raise InputError("구조 뷰 파일(*.architecture.md)이 아님: " + str(view))
    view_text = read_text(view)
    nodes = parse_view(view_text)
    stages = parse_stage_definition()
    values, notices = load_settings()
    output_dir = values["output.directory"]
    if args.output_dir is not None:
        if not _valid({"type": "relativePath"}, args.output_dir):
            raise InputError("--output-dir는 구조 뷰 폴더 기준 상대 경로여야 함: " + args.output_dir)
        output_dir = args.output_dir
    planned, stage_notices = plan_stages(stages, values["stages"], split_list(args.show), split_list(args.hide))
    picks = {}
    for item in split_list(args.pick):
        node_id, _, number = item.partition(":")
        if not number.isdigit():
            raise InputError("--pick은 `노드Id:번호` 형식이어야 함: " + item)
        picks[node_id.strip()] = int(number)
    notices += stage_notices

    slug = view.name[: -len(".architecture.md")]
    result_dir = (view.parent / output_dir / (slug + ".stages")).resolve()
    if result_dir in view.resolve().parents:
        raise InputError("결과 폴더가 입력 구조 뷰와 겹침: " + str(result_dir))
    if result_dir.exists():
        shutil.rmtree(result_dir)
    (result_dir / "work" / "original").mkdir(parents=True)

    docs = assign_documents(nodes, slug)
    view_dir = view.parent.resolve()
    listing = []
    for node in nodes:
        node["stage1"] = rel(result_dir / "work" / "01" / (node["id"] + ".kt"))
        node["original"] = node["range"] = node["skip_reason"] = None
        node["candidates"], node["units"] = [], []
        node["pick"] = picks.get(node["id"])
        text, reason = read_source(node["link"], view_dir)
        if text is not None:
            span, reason, node["candidates"] = find_declaration(text, declaration_names(node), node["pick"])
            if span:
                code = "\n".join(text.split("\n")[span[0] - 1: span[1]])
                original = result_dir / "work" / "original" / (node["id"] + ".kt")
                write_text(original, code)
                node["original"] = rel(original)
                node["range"] = {"source": node["link"], "start_line": span[0], "end_line": span[1]}
                units = make_units(analyse(code))
                node["units"] = [{"names": unit_label(u), "lines": unit_lines(u)} for u in units]
                listing.append(source_listing(node, code))
        node["skip_reason"] = reason

    manifest = {"view": rel(view), "slug": slug, "dir": rel(result_dir), "docs": docs,
                "stages": planned, "notices": notices, "nodes": nodes}
    write_text(manifest_path(result_dir), json.dumps(manifest, ensure_ascii=False, indent=1))
    prompt = write_stage1_prompt(result_dir, view_text, planned[0], nodes)
    pick = [{"id": n["id"], "source": n["link"] if re.match(r"https?://", n["link"]) else rel(view_dir / n["link"].split("#")[0]),
             "candidates": n["candidates"]}
            for n in nodes if n["candidates"] and n["skip_reason"]]
    emit({"dir": rel(result_dir), "stage1_prompt": prompt.as_posix(),
          "outline": rel(result_dir / "work" / OUTLINE_FILE), "pick": pick,
          "stages": [{"nickname": s["nickname"], "kind": s["kind"], "visible": s["visible"]} for s in planned]})
    if listing and not pick:
        print("\n" + "\n\n".join(listing))


def source_listing(node, code):
    """The node's source once, each line tagged with its unit number (`-` = outline header or blank)."""
    tag = {j: str(n) for n, u in enumerate(node["units"], 1) for j in u["lines"]}
    head = "===== %s · 책임: %s · 단위 %d개 =====" % (node["id"], node.get("responsibility") or "없음", len(node["units"]))
    units = ["--- 단위 %d: %s" % (n, u["names"]) for n, u in enumerate(node["units"], 1)]
    body = ["%3d %s| %s" % (j, tag.get(j, "-"), line) for j, line in enumerate(code.split("\n"), 1)]
    return "\n".join([head] + units + body)


def write_stage1_prompt(result_dir, view_text, stage, nodes):
    """The whole stage-1 subagent prompt in one file. Mermaid `click` lines only repeat the view's sections."""
    node_lines = "\n".join("- %s (%s) → %s" % (n["id"], n["name"], Path(n["stage1"]).resolve().as_posix())
                           for n in nodes)
    view_lines = [line for line in view_text.rstrip("\n").split("\n") if not line.strip().startswith("click ")]
    text = (read_text(PROMPT_FILE)
            .replace("{stage}", "%s — %s / %s" % (stage["nickname"], stage["becomes"], stage["unrevealed"]))
            .replace("{nodes}", node_lines)
            .replace("{view}", "\n".join(view_lines)))
    path = (Path(result_dir) / "work" / "stage1-prompt.md").resolve()
    write_text(path, text)
    return path


def work_dir(result_dir, k):
    return Path(result_dir) / "work" / ("%02d" % k)


# ---- build: base box (research R6) -----------------------------------------------

BASE_CSS = """.resp { margin: 0 0 .6em; padding: .4em .8em; border-left: 3px solid rgba(128,128,128,.5); background: rgba(128,128,128,.08); border-radius: 0 4px 4px 0; }
.resp .label { font-weight: 600; margin-right: .4em; opacity: .75; }
.stages { border: 1px solid rgba(128,128,128,.4); border-radius: 6px; padding: 0 1em; margin-bottom: 1em; }
.stages > input { position: absolute; opacity: 0; pointer-events: none; }
.stages > .stage { display: none; }
{STAGE_RULES}
.stages .head { display: flex; align-items: center; gap: .4em; padding: .5em 0 .2em; font-weight: 600; }
.stages .head .name { flex: 1; }
.stages .nav { display: inline-block; width: 2.2em; height: 1.8em; line-height: 1.8em; text-align: center; border: 1px solid rgba(128,128,128,.5); border-radius: 4px; font-weight: 400; cursor: pointer; user-select: none; }
.stages span.nav { opacity: .3; cursor: default; }
.stages .note { padding: 0 0 .5em; opacity: .8; }
.stages .scene { padding: .5em 0 1em; max-width: 65ch; }
.stages .code { max-height: min(30lh, 70vh); overflow: auto; margin-bottom: 1em; }
.stages .code pre { margin: 0; overflow: visible; width: max-content; min-width: 100%; box-sizing: border-box; }
.stages .code pre, .stages .code pre code { white-space: pre; word-break: normal; }"""

DIFF_CSS = """.stages .code { position: relative; }
.stages .code > pre.diff { position: absolute; top: 0; left: 0; background: transparent; pointer-events: none; color: transparent; }
.stages pre.diff code { color: transparent; background: transparent; min-width: 100%; }
.stages pre.diff span { display: inline-block; width: 100%; min-height: 1lh; vertical-align: top; position: relative; margin-left: -.6em; padding-left: .6em; }
.stages pre.diff .add { background: oklch(0.7 0.13 150 / 10%); box-shadow: inset 4px 0 0 oklch(0.74 0.13 152); }
.stages pre.diff .mod { background: oklch(0.7 0.13 245 / 10%); box-shadow: inset 4px 0 0 oklch(0.52 0.19 260); }
.stages pre.diff .del::before, .stages pre.diff .del-after::after { content: ""; position: absolute; left: 0; border: 5px solid transparent; border-left-color: oklch(0.65 0.19 25); }
.stages pre.diff .del::before { top: -5px; }
.stages pre.diff .del-after::after { bottom: -5px; }"""


def fence(code):
    longest = max((len(m) for m in re.findall(r"`+", code)), default=0)
    ticks = "`" * max(3, longest + 1)
    return ticks + "kotlin\n" + code.rstrip("\n") + "\n" + ticks


def note_for(changed):
    return "" if changed else "이 단계에서는 달라진 것이 없음"


def render_box(node_id, slides, diff_layers, kinds=None):
    """Base box. slides: [(title, note, code)]; diff_layers: [markup or None] (added after the code)."""
    n = len(slides)
    kinds = kinds or ["code"] * n
    out = ['<div class="stages">', ""]
    for k in range(1, n + 1):
        out.append('<input type="radio" name="%s" id="%s-%d" class="s%d"%s>' % (node_id, node_id, k, k, " checked" if k == 1 else ""))
    out.append("")
    for k, (title, note, code) in enumerate(slides, start=1):
        prev = '<label class="nav" for="%s-%d">←</label>' % (node_id, k - 1) if k > 1 else '<span class="nav">←</span>'
        nxt = '<label class="nav" for="%s-%d">→</label>' % (node_id, k + 1) if k < n else '<span class="nav">→</span>'
        out += ['<div class="stage s%d">' % k, "",
                '<div class="head"><span class="name">%s</span>%s%s</div>' % (html.escape(title, quote=False), prev, nxt),
                *(['<div class="note">%s</div>' % html.escape(note, quote=False)] if note else []), ""]
        if kinds[k - 1] == "prose":
            out += ['<div class="scene"><p>%s</p></div>' % html.escape(code.strip(), quote=False).replace("\n", "<br>"), "", "</div>", ""]
            continue
        out += ['<div class="code">', "", fence(code), ""]
        if diff_layers[k - 1]:
            out += [diff_layers[k - 1], ""]
        out += ["</div>", "", "</div>", ""]
    out.append("</div>")
    return "\n".join(out)


# ---- build: diff layer (research R7) — knows nothing about the base box ----------

def diff_lines(prev, cur):
    """Per line of `cur`: a set of add / mod / del / del-after (VS Code git gutter rules)."""
    a, b = prev.rstrip("\n").split("\n"), cur.rstrip("\n").split("\n")
    kinds = [set() for _ in b]
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        if tag == "insert":
            for j in range(j1, j2):
                kinds[j].add("add")
            continue
        paired = min(i2 - i1, j2 - j1) if tag == "replace" else 0
        for j in range(j1, j1 + paired):
            kinds[j].add("mod")
        for j in range(j1 + paired, j2):
            kinds[j].add("add")
        if (i2 - i1) > paired:
            if j2 < len(b):
                kinds[j2].add("del")
            else:
                kinds[-1].add("del-after")
    return kinds


def render_diff_layer(code, kinds):
    lines = code.rstrip("\n").split("\n")
    spans = "".join('<span%s>%s</span>\n' % ((' class="%s"' % " ".join(sorted(k))) if k else "",
                                             html.escape(line, quote=False)) for line, k in zip(lines, kinds))
    return '<pre class="diff" aria-hidden="true"><code>' + spans + "</code></pre>"


def strip_diff_layer(doc):
    """The document with the diff layer removed (contract §3 boundary check)."""
    doc = re.sub(r'\n<pre class="diff" aria-hidden="true"><code>.*?</code></pre>\n', "", doc, flags=re.S)
    return doc.replace("\n\n<style>\n" + DIFF_CSS + "\n</style>\n", "\n")


# ---- build -----------------------------------------------------------------------

def node_scenes(result_dir, manifest, node, outline):
    """[(title, kind, content)] of one node's pager, numbered per node (spec FR-015)."""
    stages = {s["kind"]: s for s in manifest["stages"]}
    prose = read_text(work_dir(result_dir, 1) / (node["id"] + ".kt")).strip()
    scenes = [(stages["prose"]["nickname"], "prose", prose)] if stages["prose"]["visible"] else []
    if not node["skip_reason"]:
        original = read_text(Path(result_dir) / "work" / "original" / (node["id"] + ".kt"))
        info = analyse(original)
        units = make_units(info)
        if units:
            placeholders, folds = check_outline(node, units, info, outline.get(node["id"]))
            if render_scene(info, units, placeholders, [], len(units)).rstrip("\n") != original.rstrip("\n"):
                raise SourceMismatch("%s: 모든 단위를 펼친 장면이 원본 범위와 다름" % node["id"])
            if stages["outline"]["visible"]:
                scenes.append((stages["outline"]["nickname"], "code", render_scene(info, units, placeholders, folds, 0)))
            if stages["unfold"]["visible"]:
                for k in range(1, len(units) + 1):
                    title = "%s %d/%d — %s" % (stages["unfold"]["nickname"], k, len(units), placeholders[k - 1])
                    scenes.append((title, "code", render_scene(info, units, placeholders, folds, k)))
        last_code = next((c for _, kind, c in reversed(scenes) if kind == "code"), None)
        if last_code is None or last_code.rstrip("\n") != original.rstrip("\n"):
            scenes.append((stages["source"]["nickname"], "code", original))
    return scenes


class SourceMismatch(Exception):
    """The scenes cannot reach the source: exit code 3."""


def build_documents(result_dir, manifest, outline, with_diff=True):
    unchanged, docs_text, counts = {}, {}, {}
    max_slides = 1
    for doc, title in manifest["docs"]:
        parts = ["# %s — 정제 단계" % title, ""]
        current_path = None
        for node in [n for n in manifest["nodes"] if n["doc"] == doc]:
            group_path = [g[1] for g in node["group_path"][node["doc_depth"]:]]
            if group_path and group_path != current_path:
                parts += ["## " + " / ".join(group_path), ""]
            current_path = group_path
            parts += ["### " + node["name"], ""]
            if node.get("responsibility"):
                parts += ['<div class="resp"><span class="label">책임</span> %s</div>' % html.escape(node["responsibility"], quote=False), ""]
            if node["skip_reason"]:
                parts += ["⚠️ " + node["skip_reason"], ""]
            scenes = node_scenes(result_dir, manifest, node, outline)
            slides, layers, kinds, prev = [], [], [], None
            for number, (name, kind, content) in enumerate(scenes, start=1):
                changed = kind != "code" or prev is None or content != prev
                if not changed:
                    unchanged.setdefault(name, []).append(node["id"])
                slides.append(("%d단계: %s (%d/%d)" % (number, name, number, len(scenes)), note_for(changed), content))
                layers.append(render_diff_layer(content, diff_lines(prev, content))
                              if with_diff and kind == "code" and prev is not None and changed else None)
                kinds.append(kind)
                prev = content if kind == "code" else prev
            counts[node["id"]] = len(scenes)
            max_slides = max(max_slides, len(slides))
            parts += [render_box(node["id"], slides, layers, kinds), ""]
        rules = "\n".join(".stages > input.s%d:checked ~ .stage.s%d { display: block; }" % (k, k) for k in range(1, max_slides + 1))
        parts += ["<style>", BASE_CSS.replace("{STAGE_RULES}", rules), "</style>", ""]
        if with_diff:
            parts += ["<style>", DIFF_CSS, "</style>", ""]
        docs_text[doc] = "\n".join(parts)
    return docs_text, unchanged, counts


def extract_last_stage(doc_text, node_id, last):
    m = re.search(r'<input type="radio" name="%s" id="%s-1"' % (re.escape(node_id), re.escape(node_id)), doc_text)
    if not m:
        return None
    m2 = re.compile(r'<div class="stage s%d">.*?<div class="code">\n\n(`{3,})kotlin\n(.*?)\n\1\n' % last, re.S).search(doc_text, m.end())
    return m2.group(2) if m2 else None


def load_outline(result_dir, manifest):
    missing = [rel(work_dir(result_dir, 1) / (n["id"] + ".kt")) for n in manifest["nodes"]
               if not (work_dir(result_dir, 1) / (n["id"] + ".kt")).is_file()]
    if missing:
        raise InputError("1단계 파일이 없음: " + ", ".join(missing))
    path = Path(result_dir) / "work" / OUTLINE_FILE
    if not any(n["units"] for n in manifest["nodes"] if not n["skip_reason"]):
        return {}
    if not path.is_file():
        raise InputError("펼치기 입력이 없음: " + rel(path))
    try:
        outline = json.loads(read_text(path))
    except ValueError as e:
        raise InputError("%s가 JSON이 아님: %s" % (rel(path), e))
    if not isinstance(outline, dict):
        raise InputError("%s는 노드 Id를 키로 하는 객체여야 함" % rel(path))
    return outline


def cmd_build(args):
    result_dir = Path(args.dir)
    manifest = load_manifest(result_dir)
    outline = load_outline(result_dir, manifest)
    try:
        docs_text, unchanged, counts = build_documents(result_dir, manifest, outline)
    except SourceMismatch as e:
        print(str(e), file=sys.stderr)
        sys.exit(3)
    paths = []
    for doc, _ in manifest["docs"]:
        path = result_dir / doc
        write_text(path, docs_text[doc])
        paths.append(rel(path))

    # FR-010: re-read the documents and compare the last stage with the source, read again.
    view_dir = Path(manifest["view"]).parent.resolve()
    mismatches, verified = [], 0
    for node in manifest["nodes"]:
        if node["skip_reason"]:
            continue
        written = extract_last_stage(read_text(result_dir / node["doc"]), node["id"], counts[node["id"]])
        text, reason = read_source(node["link"], view_dir)
        expected = None
        if text is not None:
            span, reason, _ = find_declaration(text, declaration_names(node), node.get("pick"))
            if span:
                expected = "\n".join(text.split("\n")[span[0] - 1: span[1]])
        if written is None or expected is None or written.rstrip("\n") != expected.rstrip("\n"):
            a = (written or "").split("\n")
            b = (expected or "").split("\n")
            first = next((i + 1 for i in range(max(len(a), len(b))) if i >= len(a) or i >= len(b) or a[i] != b[i]), 1)
            mismatches.append("%s(%d번째 줄%s)" % (node["id"], first, "" if expected is not None else ", " + str(reason)))
        else:
            verified += 1
    if mismatches:
        print("마지막 단계가 원본 범위와 다름: " + ", ".join(mismatches), file=sys.stderr)
        sys.exit(3)
    skipped = [{"node": n["id"], "reason": n["skip_reason"]} for n in manifest["nodes"] if n["skip_reason"]]
    reply = (["📄 [%s](%s)" % (title, path) for (_, title), path in zip(manifest["docs"], paths)]
             + ["⚠️ %s: %s" % (s["node"], s["reason"]) for s in skipped] + manifest["notices"])
    emit({"docs": paths, "unchanged": unchanged, "skipped": skipped, "verified": verified,
          "notices": manifest["notices"], "reply": "\n".join(reply)})


# ---- entry -----------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(prog="stages.py")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("view")
    p.add_argument("--show")
    p.add_argument("--hide")
    p.add_argument("--output-dir", dest="output_dir")
    p.add_argument("--pick")
    bd = sub.add_parser("build")
    bd.add_argument("dir")
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    try:
        {"prepare": cmd_prepare, "build": cmd_build}[args.command](args)
    except InputError as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
