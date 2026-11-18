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
    if "." not in path_part.rsplit("/", 1)[-1]:
        return None, "링크가 파일 하나를 가리키지 않아 구체화하지 않음"
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


def link_file(link):
    """(file name, name without extension, is Kotlin) of the file a link points at (research S10)."""
    name = link.split("#")[0].split("?")[0].rsplit("/", 1)[-1]
    stem, _, ext = name.rpartition(".")
    return name, stem, ext in ("kt", "kts")


def source_lang(link):
    """Info string of the code fences for a node's source (research S10)."""
    name, _, kotlin = link_file(link)
    return "kotlin" if kotlin else name.rpartition(".")[2].lower()


def locate_range(text, node, pick=None):
    """(span, reason, candidates, whole_file): the node's original range (research R5, S10).
    Kotlin: the declaration named like the node first. Any language: the whole file when the node
    names the file itself."""
    name, stem, kotlin = link_file(node["link"])
    span, reason, candidates = None, None, []
    if kotlin:
        span, reason, candidates = find_declaration(text, declaration_names(node), pick)
        if span or candidates:
            return span, reason, candidates, False
    if {node["id"], node["name"]} & ({name, stem} | ({stem + "Kt"} if kotlin else set())):
        return (1, len(text.rstrip("\n").split("\n"))), None, [], True
    if not kotlin:
        reason = "Kotlin이 아닌 원본은 파일 단위 노드만 원본 범위를 정할 수 있어 구체화하지 않음"
    return None, reason, [], False


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


HEADER = r"\b(?:class|interface|object|fun|typealias|val|var)\b[\w\s<>,.?*]*?(?<!\w)%s(?![\w])"
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


# ---- scope tree, steps and scenes (spec FR-004~005c, research S1~S6) --------------

DECL_HEAD = re.compile(r"^\s*(?:@\w+(?:\([^)]*\))?\s+)*(?:(?:private|protected|internal|public|override|open|abstract|"
                       r"suspend|const|lateinit|inline|operator|data|sealed|enum|inner)\s+)*(val|var|fun)\b")
ENDS_OPEN = re.compile(r"([=,(\[{.+\-*/:]|->|&&|\|\||\?:)\s*$")
STARTS_CLOSED = re.compile(r"^\s*(\.|\?\.|\?:|&&|\|\||\)|\]|->)")
CHAIN_LINK = re.compile(r"^\s*\??\.(?!\.)")
COMMENT_LINE = re.compile(r"^\s*(/\*|\*|//)")
ANNOTATION_LINE = re.compile(r"^\s*@[\w.:]+(\(.*\))?\s*$")
PARAM_HEAD = re.compile(r"^\s+(?:@\w+\s+)*(?:(?:private|protected|internal|public|override|open)\s+)*(?:val\s+|var\s+)?(\w+)\s*:")
LISTING_MARK = re.compile(r"(?:하고|이고|되고|며)\s")
MAX_SENTENCE = 45
MAX_SEP = 4


def _nesting(masked_line):
    return sum(masked_line.count(c) for c in "({[") - sum(masked_line.count(c) for c in ")}]")


def _raw_string_flags(lines, masked):
    """Per line: does it start / end inside a multi-line raw string (a `\"\"\"` that mask_code turned into `_`)."""
    in_raw, starts, ends = False, [], []
    for line, m in zip(lines, masked):
        starts.append(in_raw)
        k = line.find('"""')
        while k >= 0:
            if m[k] == "_":
                in_raw = not in_raw
                k += 3
                while k < len(line) and line[k] == '"':
                    k += 1
            else:
                k += 3
            k = line.find('"""', k)
        ends.append(in_raw)
    return starts, ends


def split_items(lines, masked, lo, hi, raw):
    """Statements or members of the block lines lo..hi-1. Leading comments and own-line annotations
    belong to the next item; blank lines between items belong to no item."""
    starts_in_raw, ends_in_raw = raw
    items, cur, nest, comments, continues = [], None, 0, [], False
    for i in range(lo, hi):
        line, m = lines[i], masked[i]
        if starts_in_raw[i] and cur is not None:
            cur["lines"].append(i)
            nest += _nesting(m)
            continues = ends_in_raw[i] or nest > 0 or bool(ENDS_OPEN.search(m.rstrip()))
            continue
        if not line.strip():
            if cur is not None and (nest > 0 or continues):
                cur["lines"].append(i)
            continue
        if nest == 0 and not continues and (COMMENT_LINE.match(line)
                                            or (ANNOTATION_LINE.match(m) and _nesting(m) == 0)):
            comments.append(i)
            continue
        if cur is None or (nest == 0 and not continues and not STARTS_CLOSED.match(line)):
            cur = {"first": i, "lines": [], "comments": comments}
            comments = []
            items.append(cur)
        cur["lines"].append(i)
        nest += _nesting(m)
        continues = ends_in_raw[i] or nest > 0 or bool(ENDS_OPEN.search(m.rstrip()))
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
    return items


FILE_HEAD_LINE = re.compile(r"^\s*(?:$|//|/\*|\*|@file:|package\b|import\b)")


def analyse(text, whole_file=False):
    """Header end, parameter spans and the body's top-level items of one source range.
    whole_file: the range is a whole Kotlin file; its leading blank/comment/@file:/package/import
    lines are the header and every following line is body (research S10)."""
    lines = text.rstrip("\n").split("\n")
    masked = mask_code(text).rstrip("\n").split("\n")
    if whole_file:
        head = 0
        while head < len(lines) and FILE_HEAD_LINE.match(lines[head]):
            head += 1
        while head > 0 and COMMENT_LINE.match(lines[head - 1]):  # a comment right above the first item is its own
            head -= 1
        raw = _raw_string_flags(lines, masked)
        items = split_items(lines, masked, head, len(lines), raw)
        if not items:
            return {"lines": lines, "masked": masked, "body_open": None, "params": [], "items": []}
        return {"lines": lines, "masked": masked, "body_open": head - 1, "params": [], "items": items, "raw": raw}
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
        return {"lines": lines, "masked": masked, "body_open": None, "params": [], "items": []}
    raw = _raw_string_flags(lines, masked)
    items = split_items(lines, masked, body_open + 1, len(lines) - 1, raw)
    return {"lines": lines, "masked": masked, "body_open": body_open, "params": params, "items": items, "raw": raw}


def _depth_profile(masked):
    """Per line: bracket depth at its start, and the lowest depth it reaches."""
    start, low, d = [], [], 0
    for m in masked:
        start.append(d)
        lo = d
        for ch in m:
            if ch in "({[":
                d += 1
            elif ch in ")}]":
                d -= 1
                lo = min(lo, d)
        low.append(lo)
    return start, low


def build_tree(text, whole_file=False):
    """The scope tree of one source range (research S1), or None when the declaration has no body.

    {"root": [own line, ...], "root_children": [node id, ...], "body_open": n,
     "nodes": [{"lines": [...], "children": [...], "parent": id or -1, "first": n}, ...],   # preorder ids; first = subtree's first line
     "attached": [{"name", "kind": "param"|"member", "lines": [...]}, ...]}     # lines 0-based
    Attached: parameters, and root members that are private or state with one code line.
    """
    info = analyse(text, whole_file)
    if info["body_open"] is None:
        return None
    lines, masked, raw = info["lines"], info["masked"], info["raw"]
    start, low = _depth_profile(masked)

    def opener(p, base):
        """The last bracket that line p leaves open at depth `base`."""
        d, last = start[p], None
        for ch in masked[p]:
            if ch in "({[":
                if d == base:
                    last = ch
                d += 1
            elif ch in ")}]":
                d -= 1
        return last

    def split_args(lo, hi):
        level = start[lo]
        args, cur, pending, after_comma = [], None, [], True
        for j in range(lo, hi):
            line = lines[j]
            if not line.strip():
                if cur is not None and start[j] > level:
                    cur["lines"].append(j)
                continue
            if start[j] == level and (cur is None or after_comma):
                if COMMENT_LINE.match(line):
                    pending.append(j)
                    continue
                cur = {"first": j, "lines": [j], "comments": pending, "trailing": []}
                pending = []
                args.append(cur)
            elif cur is None:
                cur = {"first": j, "lines": [j], "comments": pending, "trailing": []}
                pending = []
                args.append(cur)
            else:
                cur["lines"].append(j)
            end = start[j + 1] if j + 1 < len(start) else 0
            after_comma = end == level and masked[j].rstrip().endswith(",")
        if pending and args:
            args[-1]["trailing"] = pending
        merged = []
        for a in args:  # consecutive one-line arguments are one node
            one = len([j for j in a["lines"] if lines[j].strip()]) == 1
            if one and merged and merged[-1]["one"]:
                m = merged[-1]
                m["lines"] += a["lines"]
                m["comments"] += a["comments"] + m["trailing"]
                m["trailing"] = a["trailing"]
            else:
                merged.append(dict(a, one=one))
        return merged

    def subtree(n):
        out = set(n["lines"])
        for c in n["children"]:
            out |= subtree(c)
        return out

    def children_of(code, first):
        base = start[first]
        links = [j for j in code if j != first and start[j] == base and low[j] <= base and CHAIN_LINK.match(lines[j])]
        if links:
            ends = links[1:] + [code[-1] + 1]
            return [make([j for j in code if a <= j < b], [], a) for a, b in zip(links, ends)]
        kids, j = [], code[0]
        while j <= code[-1]:
            if low[j] > base and j != first:
                k = j
                while k + 1 <= code[-1] and low[k + 1] > base:
                    k += 1
                if opener(j - 1, base) == "{":
                    kids += [make(it["lines"], it["comments"] + it["trailing"], it["first"])
                             for it in split_items(lines, masked, j, k + 1, raw)]
                else:
                    kids += [make(a["lines"], a["comments"] + a["trailing"], a["first"]) for a in split_args(j, k + 1)]
                j = k + 1
            else:
                j += 1
        return kids

    def make(code, extra, first):
        code = sorted(code)
        kids = children_of(code, first) if len(code) > 1 else []
        covered = set().union(*[subtree(k) for k in kids]) if kids else set()
        own = (set(code) | set(extra)) - covered
        if len(kids) == 1:  # single-child chain: no layer of its own
            own |= kids[0]["lines"]
            kids = kids[0]["children"]
        return {"lines": own, "children": kids}

    items = info["items"]
    # Only one-line private members and one-line state attach; a multi-line member is a root child.
    attaches = [(it["private"] or it["state"]) and len(it["lines"]) == 1 for it in items]
    anchors = [it for it, a in zip(items, attaches) if not a] or items[:1]
    groups = []
    for it in anchors:
        prev = groups[-1] if groups else None
        if (prev and it["bodyless"] and prev[-1]["bodyless"] and prev[-1]["kind"] == it["kind"]
                and items.index(prev[-1]) == items.index(it) - 1):
            prev.append(it)
        else:
            groups.append([it])
    root_children = []
    for g in groups:
        if len(g) == 1:
            it = g[0]
            root_children.append(make(it["lines"], it["comments"] + it["trailing"], it["first"]))
        else:
            root_children.append({"lines": set(j for it in g for j in it["comments"] + it["lines"] + it["trailing"]),
                                  "children": []})
    attached = [{"name": p["name"], "kind": "param", "lines": list(p["lines"])} for p in info["params"]]
    anchored = {id(it) for g in groups for it in g}
    attached += [{"name": it["name"], "kind": "member", "lines": sorted(it["comments"] + it["lines"] + it["trailing"])}
                 for it in items if id(it) not in anchored]
    covered = set().union(*[subtree(k) for k in root_children]) if root_children else set()
    taken = covered | {j for a in attached for j in a["lines"]}
    root = set(range(len(lines))) - taken
    if len(root_children) == 1:
        root |= root_children[0]["lines"]
        root_children = root_children[0]["children"]

    nodes = []

    def flatten(n, parent):
        nid = len(nodes)
        nodes.append({"lines": sorted(n["lines"]), "children": [], "parent": parent, "first": min(subtree(n))})
        nodes[nid]["children"] = [flatten(c, nid) for c in n["children"]]
        return nid
    tree = {"root": sorted(root), "root_children": [flatten(c, -1) for c in root_children],
            "body_open": info["body_open"], "nodes": nodes, "attached": attached}
    owners = tree["root"] + [j for n in nodes for j in n["lines"]] + [j for a in attached for j in a["lines"]]
    if sorted(owners) != list(range(len(lines))):
        raise SourceMismatch("스코프 트리가 원본 범위의 줄을 정확히 한 번씩 덮지 않음(스크립트 버그)")
    return tree


def tree_children(tree, scope):
    return tree["root_children"] if scope == "R" else tree["nodes"][scope]["children"]


def tree_scopes(tree):
    """Scopes in post-order; the root ("R") is last."""
    out = []

    def walk(n):
        for c in tree["nodes"][n]["children"]:
            walk(c)
        if tree["nodes"][n]["children"]:
            out.append(n)
    for c in tree["root_children"]:
        walk(c)
    return out + ["R"] if tree["root_children"] else []


def subtree_lines(tree, n):
    out = list(tree["nodes"][n]["lines"])
    for c in tree["nodes"][n]["children"]:
        out += subtree_lines(tree, c)
    return out


def scope_listing(node, code, tree):
    """The node's source once, scope by scope in post-order (contract: scope list)."""
    lines = code.rstrip("\n").split("\n")
    scopes = tree_scopes(tree)
    number = {s: k for k, s in enumerate(scopes, 1)}
    out = ["===== %s · 책임: %s · 스코프 %d개 =====" % (node["id"], node.get("responsibility") or "없음", len(scopes))]
    shown = []
    for s in scopes:
        parent = "루트" if s == "R" else ("부모 #%d" % number[tree["nodes"][s]["parent"]] if tree["nodes"][s]["parent"] >= 0 else "부모 #%d" % number["R"])
        out.append("--- #%d (%s)" % (number[s], parent))
        rows = {}
        for k, c in enumerate(tree_children(tree, s), 1):
            if tree["nodes"][c]["children"]:
                first = tree["nodes"][c]["first"]
                rows[first] = (str(k), re.match(r"^\s*", lines[first]).group(0) + "⟨#%d⟩" % number[c])
            else:
                for i, j in enumerate(sorted(tree["nodes"][c]["lines"])):
                    rows[j] = (str(k) if i == 0 else "", lines[j])
                    shown.append(j)
        own = tree["root"] if s == "R" else tree["nodes"][s]["lines"]
        for j in own:
            rows[j] = ("-", lines[j])
            shown.append(j)
        if s == "R":
            for a in tree["attached"]:
                for j in a["lines"]:
                    rows[j] = ("=", lines[j])
                    shown.append(j)
        out += ["%2s| %s" % rows[j] for j in sorted(rows)]
    if sorted(shown) != list(range(len(lines))):
        raise SourceMismatch("%s: 스코프 목록이 원본의 줄을 정확히 한 번씩 보이지 않음(스크립트 버그)" % node["id"])
    return "\n".join(out)


def same_sentence(a, b):
    return re.sub(r"[\s.]", "", a or "") == re.sub(r"[\s.]", "", b or "")


def sentence_problem(text, responsibility):
    if not isinstance(text, str) or not text.strip() or "\n" in text:
        return "문장이 비었거나 한 줄이 아님"
    text = text.strip()
    if len(text) > MAX_SENTENCE:
        return "문장이 %d자를 넘음(%d자): %s" % (MAX_SENTENCE, len(text), text)
    if "⟨" in text or "⟩" in text:
        return "문장에 ⟨⟩가 있음: " + text
    if "," in text or LISTING_MARK.search(text):
        return "두 가지 이상을 잇거나 나열함(쉼표·~하고·~며): " + text
    if same_sentence(text, responsibility):
        return "책임 한 줄과 같음: " + text
    return None


def check_outline(node, tree, entry):
    """Errors (one line each) and the parsed scope entries of one node (spec FR-005b, research S4·S5)."""
    nid, scopes = node["id"], tree_scopes(tree)
    if not isinstance(entry, list) or len(entry) != len(scopes):
        return ["%s: %s 항목은 스코프 %d개의 배열이어야 함" % (nid, OUTLINE_FILE, len(scopes))], None
    errors, parsed = [], {}
    for k, (s, e) in enumerate(zip(scopes, entry), 1):
        where = "%s 스코프 #%d" % (nid, k)
        kids = tree_children(tree, s)
        if not isinstance(e, dict):
            errors.append(where + ": 객체가 아님")
            continue
        if s == "R" and ("s" in e or "with" in e):
            errors.append(where + ": 루트에는 s·with를 쓰지 않음")
        sentence = e.get("s")
        if s != "R":
            problem = sentence_problem(sentence, node.get("responsibility"))
            if problem:
                errors.append(where + ": " + problem)
        with_ids, seps = e.get("with") or [], e.get("sep") or []
        if not isinstance(with_ids, list) or not isinstance(seps, list) or not all(isinstance(g, dict) for g in seps):
            errors.append(where + ": with는 번호 배열, sep은 {ids, s} 배열이어야 함")
            continue
        if len(seps) > MAX_SEP:
            errors.append(where + ": 따로 남기는 묶음이 %d개를 넘음(%d개)" % (MAX_SEP, len(seps)))
        used = list(with_ids) + [i for g in seps for i in (g.get("ids") or [])]
        if not all(isinstance(i, int) and not isinstance(i, bool) for i in used):
            errors.append(where + ": 자식 번호는 정수여야 함")
            continue
        missing = [i for i in range(1, len(kids) + 1) if i not in used]
        extra = sorted({i for i in used if used.count(i) > 1 or not 1 <= i <= len(kids)})
        if missing or extra:
            errors.append(where + ": 자식 1~%d을 정확히 한 번씩 덮어야 함(빠짐 %s, 중복·없는 번호 %s)" % (len(kids), missing, extra))
            continue
        groups = []
        for g in seps:
            ids = [kids[i - 1] for i in g.get("ids") or []]
            if not ids:
                errors.append(where + ": 빈 묶음")
                continue
            text = g.get("s")
            if text is None and len(ids) == 1 and tree["nodes"][ids[0]]["children"]:
                groups.append((ids, None))
                continue
            problem = sentence_problem(text, node.get("responsibility"))
            if problem:
                errors.append(where + ": 묶음 %s의 %s" % (g.get("ids"), problem))
                continue
            groups.append((ids, text.strip()))
        parsed[s] = {"s": (sentence or "").strip(), "with": [kids[i - 1] for i in with_ids], "sep": groups}
    return errors, parsed


def plan_steps(tree, parsed):
    """Steps in unfold order (research S6): [{"nodes", "title", "parent", "depth"}]."""
    def first(n):
        return tree["nodes"][n]["first"]

    def closure(ids):
        out = []
        for x in ids:
            out.append(x)
            if x in parsed:
                out += closure(parsed[x]["with"])
        return out
    steps = []

    def visit(owners, parent, depth):
        pending = [g for x in owners if x in parsed for g in parsed[x]["sep"]]
        pending.sort(key=lambda g: min(first(n) for n in g[0]))
        for ids, title in pending:
            steps.append({"nodes": closure(ids), "title": title or parsed[ids[0]]["s"], "parent": parent, "depth": depth})
            visit(steps[-1]["nodes"], len(steps) - 1, depth + 1)
    visit(["R"], None, 0)
    return steps


def attach_steps(tree, steps, lines, masked):
    """Step index where each attached declaration first appears (-1 = already in the outline)."""
    body_open = tree["body_open"]
    texts = [" ".join(masked[j] for n in st["nodes"] for j in tree["nodes"][n]["lines"]) for st in steps]
    root_text = " ".join(masked[j] for j in tree["root"] if j > body_open)
    found = []
    for a in tree["attached"]:
        pat = re.compile(r"\b%s\b" % re.escape(a["name"]))
        k = -1 if pat.search(root_text) else next((i for i, t in enumerate(texts) if pat.search(t)), None)
        found.append(k)
    for _ in tree["attached"]:  # a member used only by other members follows its first user
        for i, a in enumerate(tree["attached"]):
            pat = re.compile(r"\b%s\b" % re.escape(a["name"]))
            users = [found[o] for o, b in enumerate(tree["attached"]) if o != i and found[o] is not None
                     and pat.search(" ".join(masked[j] for j in b["lines"]))]
            if users and (found[i] is None or min(users) < found[i]):
                found[i] = min(users)
    return [0 if k is None else k for k in found]


def render_steps_scene(tree, lines, steps, attached_at, upto):
    """Code of the outline (upto=0) or of the upto-th unfold."""
    nodes = tree["nodes"]
    step_of = {n: i for i, st in enumerate(steps) for n in st["nodes"]}
    revealed = {n for st in steps[:upto] for n in st["nodes"]}
    owner = {j: ("R", None) for j in tree["root"]}
    for i, a in enumerate(tree["attached"]):
        for j in a["lines"]:
            owner[j] = (a["kind"], i)
    for n, nd in enumerate(nodes):
        for j in nd["lines"]:
            owner[j] = ("N", n)
    shown_params = any(a["kind"] == "param" and attached_at[i] < upto for i, a in enumerate(tree["attached"]))

    def chain(n):
        out = []
        while n >= 0:
            out.append(n)
            n = nodes[n]["parent"]
        return out[::-1]
    items, last_top, hidden_params = [], None, False
    for j, line in enumerate(lines):
        kind, ref = owner[j]
        if kind == "param":
            if attached_at[ref] < upto:
                items.append(("line", line, j))
                hidden_params = False
            elif not hidden_params:
                items.append(("line", re.match(r"^\s*", line).group(0) + "..." + ("," if shown_params else ""), None))
                hidden_params = True
            last_top = None
            continue
        hidden_params = False
        if kind == "member":
            if attached_at[ref] < upto:
                items.append(("line", line, j))
            last_top = None
            continue
        top = None if kind == "R" else next((x for x in chain(ref) if x not in revealed), None)
        if top is None:
            items.append(("line", line, j))
            last_top = None
            continue
        if top == last_top:
            continue
        last_top = top
        k = len(items) - 1
        while k >= 0 and items[k][0] == "line" and not items[k][1].strip():
            k -= 1
        prev = items[k] if k >= 0 else None
        if prev and prev[0] == "ph" and nodes[prev[1][0]]["parent"] == nodes[top]["parent"] and step_of[prev[1][0]] == step_of[top]:
            del items[k + 1:]
            prev[1].append(top)
            continue
        first = nodes[top]["first"]
        items.append(("ph", [top], re.match(r"^\s*", lines[first]).group(0)))
    out = []
    for it in items:
        if it[0] == "line":
            out.append((it[1], it[2]))
            continue
        group, indent = it[1], it[2]
        n = step_of[group[0]]
        out.append((indent + "⟨%d. %s⟩" % (n + 1, steps[n]["title"]), None))
        inside = set()
        for g in group:
            inside |= set(subtree_lines(tree, g))
        for k in range(n + 1, len(steps)):
            if min(j for x in steps[k]["nodes"] for j in nodes[x]["lines"]) in inside:
                pad = "    " * (steps[k]["depth"] - steps[n]["depth"])
                out.append((indent + pad + "⟨%d. %s⟩" % (k + 1, steps[k]["title"]), None))
    clean = []
    for idx, (text, src) in enumerate(out):  # drop blank lines left over by hidden code
        if not text.strip() and src is not None:
            prev = clean[-1] if clean else None
            nxt = out[idx + 1] if idx + 1 < len(out) else None
            if prev and not prev[0].strip() and prev[1] != src - 1:
                continue
            if nxt and nxt[0].strip()[:1] in ("}", ")") and nxt[1] != src + 1:
                continue
            if prev and prev[0].rstrip()[-1:] in ("{", "(") and prev[1] != src - 1:
                continue
        clean.append((text, src))
    kept = [(t, src) for i, (t, src) in enumerate(clean)  # a blank left right above a closing line by hidden code
            if t.strip() or src is None or i + 1 >= len(clean)
            or not (clean[i + 1][0].strip()[:1] in ("}", ")") and clean[i + 1][1] != src + 1)]
    return "\n".join(t for t, _ in kept) + "\n"


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


def node_tree(node, code):
    """Scope tree of a node's original range; none for a source that is not Kotlin (FR-017a)."""
    if not link_file(node["link"])[2]:
        return None
    return build_tree(code, whole_file=bool(node["range"].get("whole_file")))


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
        node["candidates"], node["tree"] = [], None
        node["pick"] = picks.get(node["id"])
        text, reason = read_source(node["link"], view_dir)
        if text is not None:
            span, reason, node["candidates"], whole = locate_range(text, node, node["pick"])
            if span:
                code = "\n".join(text.split("\n")[span[0] - 1: span[1]])
                original = result_dir / "work" / "original" / (node["id"] + ".kt")
                write_text(original, code)
                node["original"] = rel(original)
                node["range"] = {"source": node["link"], "start_line": span[0], "end_line": span[1]}
                if whole:
                    node["range"]["whole_file"] = True
                node["tree"] = node_tree(node, code)
                if node["tree"] and node["tree"]["root_children"]:
                    listing.append(scope_listing(node, code, node["tree"]))
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


def fence(code, lang="kotlin"):
    longest = max((len(m) for m in re.findall(r"`+", code)), default=0)
    ticks = "`" * max(3, longest + 1)
    return ticks + lang + "\n" + code.rstrip("\n") + "\n" + ticks


def note_for(changed):
    return "" if changed else "이 단계에서는 달라진 것이 없음"


def render_box(node_id, slides, diff_layers, kinds=None, lang="kotlin"):
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
        out += ['<div class="code">', "", fence(code, lang), ""]
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

def node_scenes(result_dir, manifest, node, parsed):
    """[(title, kind, content)] of one node's pager, numbered per node (spec FR-015)."""
    stages = {s["kind"]: s for s in manifest["stages"]}
    prose = read_text(work_dir(result_dir, 1) / (node["id"] + ".kt")).strip()
    scenes = [(stages["prose"]["nickname"], "prose", prose)] if stages["prose"]["visible"] else []
    if not node["skip_reason"]:
        original = read_text(Path(result_dir) / "work" / "original" / (node["id"] + ".kt"))
        tree = node_tree(node, original)
        if tree != node.get("tree"):
            raise SourceMismatch("%s: prepare 뒤에 원본 범위가 바뀜" % node["id"])
        if tree and tree["root_children"]:
            steps = plan_steps(tree, parsed[node["id"]])
            lines = original.rstrip("\n").split("\n")
            at = attach_steps(tree, steps, lines, mask_code(original).rstrip("\n").split("\n"))
            if render_steps_scene(tree, lines, steps, at, len(steps)).rstrip("\n") != original.rstrip("\n"):
                raise SourceMismatch("%s: 모든 단계를 연 장면이 원본 범위와 다름" % node["id"])
            if stages["outline"]["visible"]:
                scenes.append((stages["outline"]["nickname"], "code", render_steps_scene(tree, lines, steps, at, 0)))
            if stages["unfold"]["visible"]:
                for k in range(1, len(steps) + 1):
                    title = "%s %d/%d — %s" % (stages["unfold"]["nickname"], k, len(steps), steps[k - 1]["title"])
                    scenes.append((title, "code", render_steps_scene(tree, lines, steps, at, k)))
        last_code = next((c for _, kind, c in reversed(scenes) if kind == "code"), None)
        if last_code is None or last_code.rstrip("\n") != original.rstrip("\n"):
            scenes.append((stages["source"]["nickname"], "code", original))
    return scenes


class SourceMismatch(Exception):
    """The scenes cannot reach the source: exit code 3."""


def build_documents(result_dir, manifest, parsed, with_diff=True):
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
            scenes = node_scenes(result_dir, manifest, node, parsed)
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
            parts += [render_box(node["id"], slides, layers, kinds, source_lang(node["link"]) if node["link"] else "kotlin"), ""]
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
    m2 = re.compile(r'<div class="stage s%d">.*?<div class="code">\n\n(`{3,})[\w+.#-]*\n(.*?)\n\1\n' % last, re.S).search(doc_text, m.end())
    return m2.group(2) if m2 else None


def load_outline(result_dir, manifest):
    missing = [rel(work_dir(result_dir, 1) / (n["id"] + ".kt")) for n in manifest["nodes"]
               if not (work_dir(result_dir, 1) / (n["id"] + ".kt")).is_file()]
    if missing:
        raise InputError("1단계 파일이 없음: " + ", ".join(missing))
    path = Path(result_dir) / "work" / OUTLINE_FILE
    if not any(n.get("tree") and n["tree"]["root_children"] for n in manifest["nodes"] if not n["skip_reason"]):
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
    errors, parsed = [], {}
    for node in manifest["nodes"]:
        if node["skip_reason"] or not (node.get("tree") and node["tree"]["root_children"]):
            continue
        if node["id"] not in outline:
            errors.append("%s: %s에 항목이 없음" % (node["id"], OUTLINE_FILE))
            continue
        node_errors, parsed[node["id"]] = check_outline(node, node["tree"], outline[node["id"]])
        errors += node_errors
    if errors:
        raise InputError("\n".join(errors))
    try:
        docs_text, unchanged, counts = build_documents(result_dir, manifest, parsed)
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
            span, reason, _, _ = locate_range(text, node, node.get("pick"))
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
    except SourceMismatch as e:
        print(str(e), file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
