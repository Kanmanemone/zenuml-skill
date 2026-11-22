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
    text = re.sub(r"</?(b|s|strong)>", "", label)
    for mark in ("✨", "♻️", "♻", "🗑️", "🗑", "️"):
        text = text.replace(mark, "")
    name = text.split("&nbsp;")[-1].strip()
    return name[:-2] if name.endswith("()") else name


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
    """(file name, name without extension, language profile or None) of a link's file (research S10, S11)."""
    name = link.split("#")[0].split("?")[0].rsplit("/", 1)[-1]
    stem, _, ext = name.rpartition(".")
    return name, stem, LANG_BY_EXT.get(ext.lower())


def source_lang(link):
    """Info string of the code fences for a node's source (research S10, S11)."""
    name, _, lang = link_file(link)
    return lang["fence"] if lang else name.rpartition(".")[2].lower()


def locate_range(text, node, pick=None):
    """(span, reason, candidates, whole_file): the node's original range (research R5, S10, S11).
    A language with a profile: the declaration named like the node first. Any file: the whole file
    when the node names the file itself."""
    name, stem, lang = link_file(node["link"])
    span, reason, candidates = None, None, []
    if lang:
        span, reason, candidates = find_declaration(text, declaration_names(node), pick, lang)
        if span or candidates:
            return span, reason, candidates, False
    kotlin = lang is LANGS["kotlin"]
    if {node["id"], node["name"]} & ({name, stem} | ({stem + "Kt"} if kotlin else set())):
        return (1, len(text.rstrip("\n").split("\n"))), None, [], True
    if not lang:
        reason = "블록 구조를 모르는 원본은 파일 단위 노드만 원본 범위를 정할 수 있어 구체화하지 않음"
    return None, reason, [], False


# ---- declaration spans (research R5) ---------------------------------------------

def mask_code(text, lang=None, spans=None):
    """Same-length copy of source: strings and chars filled with `_` (so a line that ends in a string
    still ends in a token), comments blanked to spaces; newlines kept. `lang` is a language profile
    (research S11, default Kotlin); `spans`, when given, collects (start, end) of every string."""
    lang = lang or LANGS["kotlin"]
    out = list(text)
    n = len(text)
    quotes = lang["strings"]
    line_marks = lang["line"]
    block = lang["block"]

    def blank(a, b, fill=" "):
        for k in range(a, b):
            if out[k] != "\n":
                out[k] = fill

    def string_at(i):
        for q in quotes:
            if text.startswith(q[0], i):
                return q
        return None

    def comment_at(i):
        return any(text.startswith(m, i) for m in line_marks) or bool(block and text.startswith(block[0], i))

    def skip_string(i, q):
        """i at the opening delimiter; return index after the string, handling ${...} templates."""
        delim, close, multi, escape, template = q
        j = i + len(delim)
        while j < n:
            ch = text[j]
            if escape and ch == "\\":
                j += 2
                continue
            if text.startswith(close, j):
                j += len(close)
                if len(close) == 3:
                    while j < n and text[j] == close[0]:
                        j += 1
                return j
            if not multi and ch == "\n":
                return j
            if template and ch == "$" and j + 1 < n and text[j + 1] == "{":
                j = skip_code(j + 2, "}")
                continue
            j += 1
        return n

    def skip_code(i, closer):
        """Scan code until the matching closer; return index after it."""
        depth = 0
        while i < n:
            ch = text[i]
            q = string_at(i)
            if q:
                i = skip_string(i, q)
                continue
            if ch == "'" and lang["char"]:
                i = skip_char(i)
                continue
            if comment_at(i):
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
        if lang["char"] == "guarded" and (j >= n or text[j] != "'" or not (j == i + 2 or (text[i + 1] == "\\" and j - i <= 12))):
            return i + 1  # not a char literal (Rust lifetime, Scala symbol): leave it as code
        return min(j + 1, n)

    def skip_comment(i):
        if any(text.startswith(m, i) for m in line_marks):
            j = text.find("\n", i)
            return n if j < 0 else j
        opener, closer = block
        depth, j = 0, i
        while j < n:
            if text.startswith(opener, j) and (lang["nest"] or depth == 0):
                depth += 1
                j += len(opener)
            elif text.startswith(closer, j):
                depth -= 1
                j += len(closer)
                if depth == 0:
                    return j
            else:
                j += 1
        return n

    def regex_end(i):
        """JavaScript-like regex literal at i (a `/` where a value may start): index after it, or None."""
        k = i - 1
        while k >= 0 and text[k] in " \t":
            k -= 1
        word = re.search(r"(\w+)$", text[max(0, k - 10):k + 1]) if k >= 0 else None
        if not (k < 0 or text[k] in "(,=:[!&|?{};+-*%<>~^\n"
                or (word and word.group(1) in ("return", "typeof", "case", "do", "else", "in", "of", "void", "yield", "await"))):
            return None
        j, in_class = i + 1, False
        while j < n and text[j] != "\n":
            ch = text[j]
            if ch == "\\":
                j += 2
                continue
            if ch == "[":
                in_class = True
            elif ch == "]":
                in_class = False
            elif ch == "/" and not in_class:
                j += 1
                while j < n and (text[j].isalnum() or text[j] == "_"):
                    j += 1
                return j
            j += 1
        return None

    i = 0
    while i < n:
        ch = text[i]
        q = string_at(i)
        if q:
            j = skip_string(i, q)
            blank(i, j, "_")
            if spans is not None:
                spans.append((i, j))
            i = j
        elif ch == "/" and lang.get("regex") and not comment_at(i) and regex_end(i):
            j = regex_end(i)
            blank(i, j, "_")
            i = j
        elif ch == "'" and lang["char"]:
            j = skip_char(i)
            if j > i + 1 or lang["char"] != "guarded":
                blank(i, j, "_")
            i = j
        elif comment_at(i):
            j = skip_comment(i)
            blank(i, j)
            i = j
        else:
            i += 1
    return "".join(out)


HEADER = r"\b(?:class|interface|object|fun|typealias|val|var)\b[\w\s<>,.?*]*?(?<!\w)%s(?![\w])"
CONTINUE_END = ("=", ",", ":", "(", "[", "->", ".", "+", "-", "*", "/", "&&", "||", "?:")
CONTINUE_START = (".", "?.", "?:", "&&", "||", ":", "=", "{", "where ")


def find_declaration(text, names, pick=None, lang=None):
    """(span, reason, candidates). span is (start_line, end_line), 1-based inclusive, or None.
    When the name is declared more than once (overloads), `pick` (1-based) chooses one; without it
    span is None and `candidates` lists them so the model can choose the semantically main one
    (spec FR-002). research R5; other languages than Kotlin through their profile, with the range
    check of research S11."""
    lang = lang or LANGS["kotlin"]
    kotlin = lang is LANGS["kotlin"]
    spans_of_strings = []
    masked = mask_code(text, lang, spans_of_strings)
    lines = text.split("\n")
    mlines = masked.split("\n")
    inside = None if kotlin else _line_starts_in_string(text, spans_of_strings)

    def lead(prev):
        if kotlin:
            return (prev.startswith("@") or prev.startswith("//") or prev.startswith("/*")
                    or prev.startswith("*") or prev.endswith("*/"))
        return bool(lang["lead"].search(prev))

    def span_at(pos):
        start = masked.count("\n", 0, pos)
        while start > 0:
            prev = lines[start - 1].strip()
            if prev and lead(prev):
                start -= 1
            else:
                break
        end = _declaration_end(masked, mlines, pos, lang, inside)
        return None if end is None else (start + 1, end + 1)

    for name in names:
        hits = []
        for header in lang["headers"]:  # a later header (Rust impl, Swift extension) only when none before it
            for m in re.compile(header % re.escape(name), re.M).finditer(masked):
                after = masked[m.end():m.end() + 40].lstrip(" ")
                if kotlin and after.startswith("."):
                    continue  # receiver type, not the declared name
                hits.append(m.start())
            if hits:
                break
        if not hits and lang["bare_fn"]:
            hits = _bare_function_hits(masked, name)
        if not hits:
            continue
        spans = [span_at(p) for p in hits]
        if not kotlin:
            kept = [(p, s) for p, s in zip(hits, spans) if s and _range_confirmed(lines, mlines, s, p, masked)]
            if not kept:
                return None, "원본 파일에서 " + name + " 선언 범위를 블록 구조로 확인하지 못해 구체화하지 않음", []
            kept = [(p, s) for i, (p, s) in enumerate(kept)  # a hit inside another hit's range is part of it
                    if not any(k != i and o[0] <= s[0] and s[1] <= o[1] and o != s for k, (_, o) in enumerate(kept))]
            hits, spans = [p for p, _ in kept], [s for _, s in kept]
        if len(spans) == 1:
            return spans[0], None, []
        candidates = [{"pick": i + 1, "start_line": a, "end_line": b,
                       "header": lines[masked.count("\n", 0, hits[i])].strip()}
                      for i, (a, b) in enumerate(spans)]
        if pick is not None and 1 <= pick <= len(spans):
            return spans[pick - 1], None, candidates
        return None, "원본 파일에 " + name + " 선언이 여럿 — --pick으로 하나를 골라야 함", candidates
    return None, "원본 파일에서 " + names[0] + " 선언을 찾지 못해 구체화하지 않음", []


BARE_FUNCTION = r"(?m)^[ \t]*([^\n;{}=()]*?)(?<![\w.$#])%s[ \t]*\("
NOT_A_DECLARATION = re.compile(r"(?:^|\s)(?:new|return|throw|await|yield|else|case|goto|delete)$")
BODY_AFTER_PARAMS = re.compile(r"[^;{}\n()=]*(?:\n[ \t]*)?\{")


def _bare_function_hits(masked, name):
    """Line starts of keyword-less function declarations (C-family methods, constructors): the name,
    its parameters, then a body `{` before any `;` (research S11). Calls never have that body."""
    hits = []
    for m in re.compile(BARE_FUNCTION % re.escape(name)).finditer(masked):
        if NOT_A_DECLARATION.search(m.group(1).strip()):
            continue
        j, depth = m.end() - 1, 0
        while j < len(masked):
            if masked[j] in "([":
                depth += 1
            elif masked[j] in ")]":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if j < len(masked) and BODY_AFTER_PARAMS.match(masked, j + 1):
            hits.append(m.start())
    return hits


def _line_starts_in_string(text, spans):
    """Per line: does it start inside a multi-line string (research S11)."""
    flags, offset, k = [], 0, 0
    for line in text.split("\n"):
        while k < len(spans) and spans[k][1] <= offset:
            k += 1
        flags.append(k < len(spans) and spans[k][0] < offset < spans[k][1])
        offset += len(line) + 1
    return flags


def _indent(line):
    return len(line) - len(line.lstrip())


def _range_confirmed(lines, mlines, span, pos, masked):
    """Outside Kotlin a found range is used only when the block structure confirms it (research S11):
    brackets balance without going negative, and the next code line is not deeper than the head."""
    a, b = span[0] - 1, span[1] - 1
    depth = 0
    for i in range(a, b + 1):
        for ch in mlines[i]:
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
                if depth < 0:
                    return False
    if depth:
        return False
    head = masked.count("\n", 0, pos)
    following = next((m for m in mlines[b + 1:] if m.strip()), None)
    return following is None or _indent(following) <= _indent(mlines[head])


def _declaration_end(masked, mlines, pos, lang=None, inside=None):
    """0-based line where the declaration that starts at `pos` ends; None (outside Kotlin) when the
    end cannot be found."""
    lang = lang or LANGS["kotlin"]
    if lang["family"] == "indent":
        return _indent_declaration_end(mlines, masked.count("\n", 0, pos), inside)
    kotlin = lang is LANGS["kotlin"]
    cont_end, cont_start, semi = lang["cont_end"], lang["cont_start"], lang["semi"]
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
        elif ch == ";" and semi and depth == 0 and brace == 0 and not body:
            return masked.count("\n", 0, i)
        elif ch == "\n" and depth == 0 and brace == 0 and not body and not semi:
            line_no = masked.count("\n", 0, i)
            current = mlines[line_no].rstrip()
            following = next((l.strip() for l in mlines[line_no + 1:] if l.strip()), "")
            if not current.endswith(cont_end) and not following.startswith(cont_start):
                return line_no
        i += 1
    if kotlin or (not semi and not body and depth == 0 and brace == 0):
        return masked.count("\n")
    return None


def _indent_declaration_end(mlines, head, inside):
    """Indentation languages: the head statement (to a line ending in `:` at bracket depth 0, or the
    end of an assignment), then every deeper or blank line after it (research S11)."""
    depth, end = 0, None
    for i in range(head, len(mlines)):
        depth += _nesting(mlines[i])
        if depth <= 0 and not mlines[i].rstrip().endswith("\\"):
            end = i
            break
    if end is None:
        return None
    if not mlines[end].rstrip().endswith(":"):
        return end
    base, last = _indent(mlines[head]), end
    for i in range(end + 1, len(mlines)):
        if inside and inside[i]:
            last = i
            continue
        if not mlines[i].strip():
            continue
        if _indent(mlines[i]) <= base:
            break
        last = i
    return last


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


# ---- language profiles (research S11) ----------------------------------------------
# One scanner, many languages: every syntax fact the scanner needs is a value here. Kotlin points at
# the constants above, so Kotlin results do not change.

def _private_keyword(head, name):
    return bool(re.search(r"\bprivate\b", head))


def _private_swift(head, name):
    return bool(re.search(r"\b(?:private|fileprivate)\b", head))


# Name-based rules apply to declarations only: a statement inside a function body is never a member.
def _private_python(head, name):
    declared = re.match(r"^\s*(?:(?:async\s+)?(?:def|class)\s+\w|\w+\s*(?::[^=]*)?=(?!=))", head)
    return bool(declared) and name.startswith("_") and not (name.startswith("__") and name.endswith("__"))


def _private_dart(head, name):
    return name.startswith("_") and not head.lstrip().startswith(name)


def _private_go(head, name):
    return bool(re.match(r"^\s*(?:func|var|const|type)\b", head)) and name[:1].islower()


def _private_rust(head, name):
    return bool(re.match(r"^\s*(?:(?:async|unsafe|const|extern)\s+)*(?:fn|struct|enum|static|type|trait|mod|union)\b", head))


def _private_js(head, name):
    return head.lstrip().startswith("#") or bool(re.search(r"\bprivate\b", head))


def _never(head, name):
    return False


DQ = ('"', '"', False, True, False)          # (open, close, multi-line, backslash escapes, ${} templates)
SQ = ("'", "'", False, True, False)
TDQ = ('"""', '"""', True, True, False)
TSQ = ("'''", "'''", True, True, False)
KEYWORD_NAME = (r"\b(?:class|interface|enum|struct|record|object|trait|protocol|extension|actor|fun|fn|func|function|def|"
                r"val|var|let|const|type|typealias|mod|namespace)\s+(?:\([^)]*\)\s*)?(?:<[^>]*>\s*)?(?:\w+\.)?(\w+)")
GENERIC_NAMES = [KEYWORD_NAME, r"(\w+)\s*\(", r"(\w+)\s*(?:[=;:]|$)"]
PARAM_FIRST = re.compile(r"^\s+(?:@\w+(?:\([^)]*\))?\s+)*(?:(?:private|protected|public|internal|readonly|override|open|mut|"
                         r"ref|out|in|inout|final|const|let|var|val|required)\s+|this\.)*[*&]{0,2}(\w+)")
PARAM_LAST = re.compile(r"^\s+.*?(\w+)\s*(?:=[^,]*)?,?\s*$")
BRACE_LEAD = re.compile(r"^(?:@|//|/\*|\*)|\*/$")
GENERIC_FN = re.compile(r"\b(?:fun|fn|func|function|def)\b|\w\s*\(")
GENERIC_SIGNATURE = re.compile(r"^[^=]*\w\s*\(")
NO_ANNOTATION = re.compile(r"(?!)")


def _brace(fence, exts, headers, strings, **extra):
    profile = {"fence": fence, "exts": exts, "family": "brace", "headers": headers, "strings": strings,
               "line": ("//",), "block": ("/*", "*/"), "nest": False, "char": "guarded", "bare_fn": False,
               "semi": False, "cont_end": CONTINUE_END + ("=>", "|", "&"),
               "cont_start": CONTINUE_START + ("extends ", "implements ", "|", "&"),
               "lead": BRACE_LEAD, "comment_line": COMMENT_LINE, "annotation_line": ANNOTATION_LINE,
               "param": PARAM_FIRST, "names": GENERIC_NAMES, "private": _private_keyword, "state": None,
               "fn": GENERIC_FN, "decl_head": GENERIC_SIGNATURE,
               "file_head": re.compile(r"^\s*(?:package|import)\b")}
    profile.update(extra)
    return profile


def _kw(words, filler=r"\s+"):
    return r"\b(?:%s)\b%s(?<![\w])%%s(?![\w])" % (words, filler)


C_FAMILY_FILLER = r"[\w\s<>,.?*\[\]&:]*?"
JS_HEAD = re.compile(r"""^\s*(?:import\b|export\s*(?:\*|\{)|['"]use [\w ]+['"];?\s*$)""")
LANGS = {
    "kotlin": {"fence": "kotlin", "exts": ("kt", "kts"), "family": "brace", "headers": [HEADER],
               "strings": [('"""', '"""', True, False, True), ('"', '"', False, True, True)],
               "line": ("//",), "block": ("/*", "*/"), "nest": True, "char": "kotlin", "bare_fn": False,
               "semi": False, "cont_end": CONTINUE_END, "cont_start": CONTINUE_START, "lead": None,
               "comment_line": COMMENT_LINE, "annotation_line": ANNOTATION_LINE, "param": PARAM_HEAD,
               "names": [r"\b(?:val|var|fun|class|interface|object)\s+(?:<[^>]*>\s*)?(?:\w+\.)?(\w+)"],
               "private": _private_keyword, "state": re.compile(r"^\s*(?:private\s+)?var\b"),
               "fn": re.compile(r"\bfun\b"), "decl_head": DECL_HEAD,
               "file_head": re.compile(r"^\s*(?:package|import)\b")},
    "java": _brace("java", ("java",), [_kw("class|interface|enum|record|@interface")], [TDQ, DQ],
                   bare_fn=True, semi=True, param=PARAM_LAST),
    "scala": _brace("scala", ("scala", "sc"), [_kw("class|object|trait|def|val|var|type|enum|given")],
                    [('"""', '"""', True, False, False), DQ], nest=True, state=re.compile(r"^\s*(?:private\s+)?var\b")),
    "groovy": _brace("groovy", ("groovy", "gradle"), [_kw("class|interface|enum|trait|def")],
                     [TSQ, ('"""', '"""', True, True, True), ('"', '"', False, True, True), SQ], char=None,
                     bare_fn=True, param=PARAM_LAST),
    "swift": _brace("swift", ("swift",), [_kw("class|struct|enum|protocol|actor|func|var|let|typealias"), _kw("extension")],
                    [TDQ, DQ], nest=True, char=None, private=_private_swift,
                    state=re.compile(r"^\s*(?:(?:private|fileprivate)\s+)?var\b"),
                    file_head=re.compile(r"^\s*(?:@testable\s+)?import\b")),
    "csharp": _brace("csharp", ("cs",), [_kw("class|interface|struct|enum|record|delegate|namespace|event", r"[\w\s<>,.?\[\]]*?")],
                     [('"""', '"""', True, False, False), ('@"', '"', True, False, False), DQ], bare_fn=True,
                     semi=True, param=PARAM_LAST, lead=re.compile(r"^(?:\[|//|/\*|\*)|\*/$"),
                     annotation_line=re.compile(r"^\s*\[[^\]]*\]\s*$"),
                     file_head=re.compile(r"^\s*(?:(?:global\s+)?using\b(?!\s*\()|namespace\s+[\w.]+\s*;)")),
    "go": _brace("go", ("go",), [_kw("type|func|var|const", r"\s+(?:\([^)\n]*\)\s*)?")],
                 [("`", "`", True, False, False), DQ], private=_private_go, annotation_line=NO_ANNOTATION,
                 names=[r"\bfunc\s+(?:\([^)]*\)\s*)?(\w+)"] + GENERIC_NAMES),
    "rust": _brace("rust", ("rs",), [_kw("struct|enum|trait|fn|type|const|static|mod|union|macro_rules!", r"[\w\s<>,.?*&:'!]*?"),
                                    _kw("impl", r"[\w\s<>,.?*&:'!]*?")],
                   [('"', '"', True, True, False)], nest=True, semi=True, private=_private_rust,
                   lead=re.compile(r"^(?:#!?\[|//|/\*|\*)|\*/$"), annotation_line=re.compile(r"^\s*#!?\[.*\]\s*$"),
                   file_head=re.compile(r"^\s*(?:pub(?:\([^)]*\))?\s+)?(?:use\b|extern\s+crate\b|mod\s+\w+\s*;)")),
    "dart": _brace("dart", ("dart",), [_kw("class|mixin|enum|extension|typedef")],
                   [('"""', '"""', True, True, True), ("'''", "'''", True, True, True), ('"', '"', False, True, True),
                    ("'", "'", False, True, True)], nest=True, char=None, bare_fn=True, semi=True,
                   param=PARAM_LAST, private=_private_dart,
                   file_head=re.compile(r"^\s*(?:import|export|library|part)\b")),
    "javascript": _brace("javascript", ("js", "jsx", "mjs", "cjs"), [_kw(r"class|function\*?|const|let|var")],
                         [("`", "`", True, True, True), DQ, SQ], char=None, bare_fn=True, private=_private_js,
                         file_head=JS_HEAD, regex=True),
    "typescript": _brace("typescript", ("ts", "tsx", "mts", "cts"),
                         [_kw(r"class|interface|enum|type|namespace|module|function\*?|const|let|var")],
                         [("`", "`", True, True, True), DQ, SQ], char=None, bare_fn=True, private=_private_js,
                         file_head=JS_HEAD, regex=True),
    "c": _brace("c", ("c", "h"), [_kw("struct|enum|union|typedef", r"[\w\s*]*?")], [DQ], bare_fn=True, semi=True,
                param=PARAM_LAST, private=_never, annotation_line=NO_ANNOTATION,
                file_head=re.compile(r"^\s*#\s*(?:include|import|pragma)\b")),
    "cpp": _brace("cpp", ("cpp", "cc", "cxx", "hpp", "hh", "hxx"), [_kw("class|struct|enum|union|namespace", r"\s+(?:class\s+)?")],
                  [DQ], bare_fn=True, semi=True, param=PARAM_LAST, private=_never, annotation_line=NO_ANNOTATION,
                  lead=re.compile(r"^(?:template\b|//|/\*|\*)|\*/$"),
                  file_head=re.compile(r"^\s*(?:#\s*(?:include|import|pragma)\b|using\s+namespace\b)")),
    "python": {"fence": "python", "exts": ("py", "pyi"), "family": "indent",
               "headers": [r"^[ \t]*(?:async[ \t]+)?(?:def|class)[ \t]+%s(?![\w])", r"^%s[ \t]*(?::[^=\n]*)?=(?!=)"],
               "strings": [TDQ, TSQ, DQ, SQ], "line": ("#",), "block": None, "nest": False, "char": None,
               "bare_fn": False, "semi": False, "cont_end": (), "cont_start": (),
               "lead": re.compile(r"^(?:@|#)"), "comment_line": re.compile(r"^\s*#"),
               "annotation_line": re.compile(r"^\s*@[\w.]+(\(.*\))?\s*$"), "param": PARAM_FIRST,
               "names": [r"^\s*(?:async\s+)?(?:def|class)\s+(\w+)", r"^\s*(\w+)\s*(?::[^=]*)?="],
               "private": _private_python, "state": None, "fn": re.compile(r"\bdef\b"), "decl_head": None,
               "file_head": re.compile(r"^\s*(?:import|from)\b")},
}
LANG_BY_EXT = {ext: profile for profile in LANGS.values() for ext in profile["exts"]}


def _nesting(masked_line):
    return sum(masked_line.count(c) for c in "({[") - sum(masked_line.count(c) for c in ")}]")


def _string_flags(text, lang):
    """Per line: does it start / end inside a multi-line string (mask_code's string spans, research S11)."""
    spans = []
    mask_code(text, lang, spans)
    starts, ends, offset, k = [], [], 0, 0
    for line in text.rstrip("\n").split("\n"):
        end = offset + len(line)
        while k < len(spans) and spans[k][1] <= offset:
            k += 1
        starts.append(k < len(spans) and spans[k][0] < offset < spans[k][1])
        j = k
        while j < len(spans) and spans[j][1] <= end:
            j += 1
        ends.append(j < len(spans) and spans[j][0] < end < spans[j][1])
        offset = end + 1
    return starts, ends


def _item_facts(items, lines, masked, lang):
    for it in items:
        head, code = lines[it["first"]], "\n".join(masked[j] for j in it["lines"])
        name = next((m for m in (re.search(p, head) for p in lang["names"]) if m), None) or re.search(r"(\w+)", head)
        it["name"] = name.group(1) if name else "?"
        it["private"] = lang["private"](head, it["name"])
        it["state"] = bool(lang["state"] and lang["state"].match(head)) and len(it["lines"]) == 1
        flat = code
        for _ in range(4):
            flat = re.sub(r"\([^()]*\)", "", flat)
        it["bodyless"] = bool(lang["decl_head"] and lang["decl_head"].match(head)) and "{" not in code and "=" not in flat
        it["kind"] = "fun" if lang["fn"].search(head) else "prop"
        it.setdefault("trailing", [])
    return items


def split_items(lines, masked, lo, hi, raw, lang=None):
    """Statements or members of the block lines lo..hi-1. Leading comments and own-line annotations
    belong to the next item; blank lines between items belong to no item."""
    lang = lang or LANGS["kotlin"]
    if lang["family"] == "indent":
        return split_items_indent(lines, masked, lo, hi, raw, lang)
    comment_line, annotation_line = lang["comment_line"], lang["annotation_line"]
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
        if nest == 0 and not continues and (comment_line.match(line)
                                            or (annotation_line.match(m) and _nesting(m) == 0)):
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
    return _item_facts(items, lines, masked, lang)


CLAUSE_LINE = re.compile(r"^\s*(?:elif|else|except|finally)\b")


def split_items_indent(lines, masked, lo, hi, raw, lang):
    """Indentation languages (research S11): statements of the block lines lo..hi-1 at the block's
    indentation. Deeper lines, lines inside brackets or after `\\`, and `elif`/`else`/`except`/
    `finally` belong to the item above; `#` comments and `@` decorators to the item below."""
    starts_in_raw, ends_in_raw = raw
    items, cur, nest, comments, pending, continues, base, deco = [], None, 0, [], [], False, None, 0
    for i in range(lo, hi):
        line, m = lines[i], masked[i]
        if not line.strip():
            if cur is not None:
                pending.append(i)
            continue
        if base is None:
            base = _indent(line)
        if deco > 0:  # inside a multi-line decorator
            comments.append(i)
            deco += _nesting(m)
            continue
        if cur is not None and (starts_in_raw[i] or nest > 0 or continues or _indent(line) > base
                                or CLAUSE_LINE.match(line)):
            cur["lines"] += pending + [i]
        elif lang["comment_line"].match(line) or m.lstrip().startswith("@"):
            comments.append(i)
            deco = max(0, _nesting(m)) if m.lstrip().startswith("@") else 0
            pending = []
            continue
        else:
            cur = {"first": i, "lines": [i], "comments": comments}
            comments, nest = [], 0
            items.append(cur)
        pending = []
        nest += _nesting(m)
        continues = ends_in_raw[i] or nest > 0 or m.rstrip().endswith("\\")
    if comments and items:
        items[-1]["trailing"] = comments
    return _item_facts(items, lines, masked, lang)


def analyse(text, whole_file=False, lang=None):
    """Header end, parameter spans and the body's top-level items of one source range.
    whole_file: the range is a whole file; its leading items that are file head (package, import, …)
    are the header and every later item is body (research S10, S11)."""
    lang = lang or LANGS["kotlin"]
    lines = text.rstrip("\n").split("\n")
    masked = mask_code(text, lang).rstrip("\n").split("\n")
    raw = _string_flags(text, lang)
    empty = {"lines": lines, "masked": masked, "body_open": None, "params": [], "items": []}
    if whole_file:
        items = split_items(lines, masked, 0, len(lines), raw, lang)
        k = 0
        while k < len(items) and lang["file_head"].match(lines[items[k]["first"]]):
            k += 1
        if k == len(items):
            return empty
        head_end = max([j for it in items[:k] for j in it["lines"] + it["comments"] + it["trailing"]], default=-1)
        return {"lines": lines, "masked": masked, "body_open": head_end, "params": [], "items": items[k:], "raw": raw}
    indent = lang["family"] == "indent"
    depth, body_open, params, deco = 0, None, [], 0
    for i, m in enumerate(masked):
        start_depth = depth
        if lang["comment_line"].match(lines[i]) and depth == 0:
            continue
        if indent:
            if depth == 0 and (deco or m.lstrip().startswith("@")):
                deco = 1
            depth += _nesting(m)
            if deco:
                deco = 0 if depth == 0 else 1
                continue
            if depth == 0 and m.rstrip().endswith(":") and not m.rstrip().endswith("\\"):
                body_open = i
                break
        else:
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
        p = lang["param"].match(lines[i]) if start_depth == 1 else None
        if p:
            params.append({"name": p.group(1), "lines": [i]})
        elif start_depth > 1 and params and params[-1]["lines"][-1] == i - 1:
            params[-1]["lines"].append(i)
    if indent:
        if body_open is None or body_open == len(lines) - 1:
            return empty
        items = split_items(lines, masked, body_open + 1, len(lines), raw, lang)
    else:
        if body_open is None or not lines[-1].strip().startswith("}"):
            return empty
        items = split_items(lines, masked, body_open + 1, len(lines) - 1, raw, lang)
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


def build_tree(text, whole_file=False, lang=None):
    """The scope tree of one source range (research S1), or None when the declaration has no body.

    {"root": [own line, ...], "root_children": [node id, ...], "body_open": n,
     "nodes": [{"lines": [...], "children": [...], "parent": id or -1, "first": n}, ...],   # preorder ids; first = subtree's first line
     "attached": [{"name", "kind": "param"|"member", "lines": [...]}, ...]}     # lines 0-based
    Attached: parameters, and root members that are private or state with one code line.
    """
    lang = lang or LANGS["kotlin"]
    indent_family = lang["family"] == "indent"
    info = analyse(text, whole_file, lang)
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
                if lang["comment_line"].match(line):
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
        def inner(j):
            if low[j] > base:
                return True
            return indent_family and (not lines[j].strip() or _indent(lines[j]) > _indent(lines[first]))

        kids, j = [], code[0]
        while j <= code[-1]:
            if j != first and inner(j):
                k = j
                while k + 1 <= code[-1] and inner(k + 1):
                    k += 1
                block = masked[j - 1].rstrip().endswith(":") if indent_family else opener(j - 1, base) == "{"
                if block:
                    kids += [make(it["lines"], it["comments"] + it["trailing"], it["first"])
                             for it in split_items(lines, masked, j, k + 1, raw, lang)]
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
    if not text.endswith("다."):
        return "문장이 '다.'로 끝나지 않음: " + text
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
        pat = re.compile(r"(?<!\w)%s(?!\w)" % re.escape(a["name"]))
        k = -1 if pat.search(root_text) else next((i for i, t in enumerate(texts) if pat.search(t)), None)
        found.append(k)
    for _ in tree["attached"]:  # a member used only by other members follows its first user
        for i, a in enumerate(tree["attached"]):
            pat = re.compile(r"(?<!\w)%s(?!\w)" % re.escape(a["name"]))
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
    """Scope tree of a node's original range; none for a source without a language profile (FR-017a)."""
    lang = link_file(node["link"])[2]
    if not lang:
        return None
    return build_tree(code, whole_file=bool(node["range"].get("whole_file")), lang=lang)


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
    # A hidden first stage is never shown and nothing builds on it, so no isolated worker is needed (spec FR-009a).
    prompt = write_stage1_prompt(result_dir, view_text, planned[0], nodes) if planned[0]["visible"] else None
    pick = [{"id": n["id"], "source": n["link"] if re.match(r"https?://", n["link"]) else rel(view_dir / n["link"].split("#")[0]),
             "candidates": n["candidates"]}
            for n in nodes if n["candidates"] and n["skip_reason"]]
    emit({"dir": rel(result_dir), "stage1_prompt": prompt and prompt.as_posix(),
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

STYLE_SUMMARY = '이 문서에 적용되지 못한 &lt;style&gt; 코드 (<a href="https://github.github.com/gfm/#disallowed-raw-html-extension-">관련 GFM 공식 문서</a>)'

BASE_CSS = """.zenuml-stepwise-style { display: none; }
.resp { margin: 0 0 .6em; padding: .4em .8em; border-left: 3px solid rgba(128,128,128,.5); background: rgba(128,128,128,.08); border-radius: 0 4px 4px 0; }
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
    scenes = []
    if stages["prose"]["visible"]:
        scenes.append((stages["prose"]["nickname"], "prose", read_text(work_dir(result_dir, 1) / (node["id"] + ".kt")).strip()))
    if not node["skip_reason"]:
        original = read_text(Path(result_dir) / "work" / "original" / (node["id"] + ".kt"))
        tree = node_tree(node, original)
        if tree != node.get("tree"):
            raise SourceMismatch("%s: prepare 뒤에 원본 범위가 바뀜" % node["id"])
        if tree and tree["root_children"]:
            steps = plan_steps(tree, parsed[node["id"]])
            lines = original.rstrip("\n").split("\n")
            at = attach_steps(tree, steps, lines, mask_code(original, link_file(node["link"])[2]).rstrip("\n").split("\n"))
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
        parts += ['<details class="zenuml-stepwise-style">', "<summary>" + STYLE_SUMMARY + "</summary>", "",
                  "<style>", BASE_CSS.replace("{STAGE_RULES}", rules), "</style>", ""]
        if with_diff:
            parts += ["<style>", DIFF_CSS, "</style>", ""]
        parts += ["</details>", ""]
        docs_text[doc] = "\n".join(parts)
    return docs_text, unchanged, counts


def extract_last_stage(doc_text, node_id, last):
    m = re.search(r'<input type="radio" name="%s" id="%s-1"' % (re.escape(node_id), re.escape(node_id)), doc_text)
    if not m:
        return None
    m2 = re.compile(r'<div class="stage s%d">.*?<div class="code">\n\n(`{3,})[\w+.#-]*\n(.*?)\n\1\n' % last, re.S).search(doc_text, m.end())
    return m2.group(2) if m2 else None


def load_outline(result_dir, manifest):
    needed = manifest["stages"][0]["visible"]
    missing = [rel(work_dir(result_dir, 1) / (n["id"] + ".kt")) for n in manifest["nodes"]
               if needed and not (work_dir(result_dir, 1) / (n["id"] + ".kt")).is_file()]
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
