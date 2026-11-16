#!/usr/bin/env python3
"""Deterministic half of the revealing-code-step-by-step skill.

    stages.py prepare <view.architecture.md> [--show=a,b] [--hide=a,b] [--output-dir=rel] [--pick=Id:n,...]
    stages.py begin   <result dir> <k>
    stages.py apply   <result dir> <k>
    stages.py build   <result dir>

Each command prints one line of JSON on stdout (begin then prints the stage's code). Errors go to stderr
as one Korean line.
Exit codes: 0 ok, 2 bad input, 3 the last stage differs from the source (build).
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
from collections import Counter
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
STAGES_FILE = SKILL_DIR / "stages.md"
PROMPT_FILE = SKILL_DIR / "stage1-prompt.md"
EDITS_FILE = "edits.txt"
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
NOTATION = "- 보조 표기:"


def parse_stage_definition(path=STAGES_FILE):
    stages, current = [], None
    for line in read_text(path).split("\n"):
        if line.startswith("## "):
            current = {"nickname": line[3:].strip(), "becomes": None, "unrevealed": None, "notation": None}
            stages.append(current)
        elif current is not None:
            for head, field in ((BECOMES, "becomes"), (UNREVEALED, "unrevealed"), (NOTATION, "notation")):
                if line.startswith(head):
                    current[field] = line[len(head):].strip()
    if len(stages) < 2:
        raise InputError("stages.md에 단계가 2개 이상 있어야 함")
    names = [s["nickname"] for s in stages]
    for name in names:
        if not name:
            raise InputError("stages.md에 별명이 빈 단계가 있음")
        if names.count(name) > 1:
            raise InputError("stages.md에 별명 `" + name + "`이 겹침")
    for s in stages:
        for head, field in ((BECOMES, "becomes"), (UNREVEALED, "unrevealed")):
            if not s[field]:
                raise InputError("stages.md의 `" + s["nickname"] + "` 단계에 `" + head + "` 항목이 없음")
    return stages


def plan_stages(stages, toggles, show, hide):
    """Decide which stages are generated and shown (research R13)."""
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

    generated, pending = [], []
    for index, stage in enumerate(stages):
        first, is_last = index == 0, index == len(stages) - 1
        if not (first or is_last or visible[stage["nickname"]]):
            pending.append({"nickname": stage["nickname"], "becomes": stage["becomes"], "notation": stage["notation"]})
            continue
        entry = dict(stage)
        entry["visible"] = True if is_last else visible[stage["nickname"]]
        entry["merged"] = pending
        pending = []
        generated.append(entry)
    shown = [s for s in generated if s["visible"]]
    for work, s in enumerate(generated, start=1):
        s["work"] = work
        s["display"] = shown.index(s) + 1 if s["visible"] else None
        s["of"] = len(shown)
    return generated, notices


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
    for node in nodes.values():
        node["link"] = links.get(node["id"])
    return list(nodes.values())


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
    generated, stage_notices = plan_stages(stages, values["stages"], split_list(args.show), split_list(args.hide))
    picks = {}
    for item in split_list(args.pick):
        node_id, _, number = item.partition(":")
        if not number.isdigit():
            raise InputError("--pick은 `노드Id:번호` 형식이어야 함: " + item)
        picks[node_id.strip()] = int(number)
    notices += stage_notices

    slug = view.name[: -len(".architecture.md")]
    result_dir = (view.parent / output_dir / (slug + ".stages")).resolve()
    if result_dir.exists():
        shutil.rmtree(result_dir)
    (result_dir / "work" / "original").mkdir(parents=True)

    docs = assign_documents(nodes, slug)
    view_dir = view.parent.resolve()
    spans = {}
    for node in nodes:
        node["stage1"] = rel(result_dir / "work" / "01" / (node["id"] + ".kt"))
        node["original"] = node["range"] = node["skip_reason"] = None
        node["contains"], node["candidates"] = [], []
        node["pick"] = picks.get(node["id"])
        text, reason = read_source(node["link"], view_dir)
        if text is not None:
            span, reason, node["candidates"] = find_declaration(text, declaration_names(node), node["pick"])
            if span:
                lines = text.split("\n")
                code = "\n".join(lines[span[0] - 1: span[1]])
                original = result_dir / "work" / "original" / (node["id"] + ".kt")
                write_text(original, code)
                node["original"] = rel(original)
                node["range"] = {"source": node["link"], "start_line": span[0], "end_line": span[1]}
                spans[node["id"]] = (node["link"], span)
        node["skip_reason"] = reason
    for node in nodes:
        if node["id"] not in spans:
            continue
        source, (a, b) = spans[node["id"]]
        node["contains"] = [other for other, (src, (c, d)) in spans.items()
                            if other != node["id"] and src == source and a <= c and d <= b and (c, d) != (a, b)]

    manifest = {"view": rel(view), "slug": slug, "dir": rel(result_dir), "docs": docs,
                "stages": generated, "notices": notices, "nodes": nodes}
    write_text(manifest_path(result_dir), json.dumps(manifest, ensure_ascii=False, indent=1))
    prompt = write_stage1_prompt(result_dir, view_text, generated[0], nodes)
    pick = [{"id": n["id"], "source": n["link"] if re.match(r"https?://", n["link"]) else rel(view_dir / n["link"].split("#")[0]),
             "candidates": n["candidates"]}
            for n in nodes if n["candidates"] and n["skip_reason"]]
    emit({"dir": rel(result_dir), "stage1_prompt": prompt.as_posix(), "middle": list(range(2, len(generated))),
          "pick": pick})


def write_stage1_prompt(result_dir, view_text, stage, nodes):
    """The whole stage-1 subagent prompt in one file: template + stage 1 + nodes + the view itself."""
    node_lines = "\n".join("- %s (%s) → %s" % (n["id"], n["name"], Path(n["stage1"]).resolve().as_posix())
                           for n in nodes)
    text = (read_text(PROMPT_FILE)
            .replace("{stage}", "%s — %s / %s" % (stage["nickname"], stage["becomes"], stage["unrevealed"]))
            .replace("{nodes}", node_lines)
            .replace("{view}", view_text.rstrip("\n")))
    path = (Path(result_dir) / "work" / "stage1-prompt.md").resolve()
    write_text(path, text)
    return path


# ---- begin -----------------------------------------------------------------------

def work_dir(result_dir, k):
    return Path(result_dir) / "work" / ("%02d" % k)


def cmd_begin(args):
    result_dir = Path(args.dir)
    manifest = load_manifest(result_dir)
    stages = manifest["stages"]
    g, k = len(stages), args.k
    if not 2 <= k <= g - 1:
        raise InputError("begin 단계 번호는 2~%d여야 함(받은 값: %d)" % (g - 1, k))
    if not work_dir(result_dir, k - 1).is_dir():
        raise InputError("직전 단계 폴더가 없음: " + rel(work_dir(result_dir, k - 1)))
    if work_dir(result_dir, k).exists():
        raise InputError("이미 시작한 단계임(지난 단계는 다시 만들지 않음): " + rel(work_dir(result_dir, k)))
    # Stage 1 is written for every node (build shows it for skipped nodes too); later stages only for the rest.
    expected = [n for n in manifest["nodes"] if k == 2 or not n["skip_reason"]]
    missing = [rel(work_dir(result_dir, k - 1) / (n["id"] + ".kt")) for n in expected
               if not (work_dir(result_dir, k - 1) / (n["id"] + ".kt")).is_file()]
    if missing:
        raise InputError("직전 단계 파일이 없음: " + ", ".join(missing))
    edits = Path(result_dir) / "work" / EDITS_FILE
    if edits.exists():
        edits.unlink()
    blocks = []
    for node in manifest["nodes"]:
        if node["skip_reason"]:
            continue
        dst = work_dir(result_dir, k) / (node["id"] + ".kt")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(work_dir(result_dir, k - 1) / (node["id"] + ".kt"), dst)
        inner = " · 안에 든 노드: " + ", ".join(node["contains"]) if node["contains"] else ""
        blocks.append("===== %s · %d단계%s =====\n%s" % (node["id"], k, inner, read_text(dst).rstrip("\n")))
        if k == 2:
            blocks.append("===== %s · 원본 =====\n%s" % (node["id"], read_text(Path(result_dir) / "work" / "original" / (node["id"] + ".kt")).rstrip("\n")))
    s = stages[k - 1]
    emit({"stage": k, "nickname": s["nickname"], "becomes": s["becomes"], "unrevealed": s["unrevealed"],
          "notation": s["notation"], "merged": s["merged"], "edits": rel(edits)})
    print("\n" + "\n\n".join(blocks))


# ---- apply -----------------------------------------------------------------------

def parse_edits(text):
    """Blocks of `<<<<<<< <id>` / old lines / `=======` / new lines / `>>>>>>>`."""
    blocks, cur, part = [], None, None
    for number, line in enumerate(text.split("\n"), start=1):
        if cur is None:
            m = re.fullmatch(r"<<<<<<< (\S+)\s*", line)
            if m:
                cur, part = {"id": m.group(1), "old": [], "new": []}, "old"
            elif line.strip():
                raise InputError("%s %d번째 줄이 블록 밖에 있음: %s" % (EDITS_FILE, number, line))
            continue
        if line == "=======" and part == "old":
            part = "new"
        elif line == ">>>>>>>" and part == "new":
            blocks.append((cur["id"], "\n".join(cur["old"]), "\n".join(cur["new"])))
            cur = None
        else:
            cur[part].append(line)
    if cur is not None:
        raise InputError("%s의 %s 블록이 >>>>>>>로 닫히지 않음" % (EDITS_FILE, cur["id"]))
    return blocks


def source_lines(text, wanted):
    """Stripped lines of `text` that are in `wanted`, with multiplicity."""
    return Counter(line.strip() for line in text.split("\n") if line.strip() in wanted)


def check_stage(result_dir, manifest, k):
    """Mechanical checks of stage k against stage k-1 (rules: names stay, source lines never go back)."""
    warnings = []
    for node in manifest["nodes"]:
        if node["skip_reason"]:
            continue
        cur = read_text(work_dir(result_dir, k) / (node["id"] + ".kt"))
        prev = read_text(work_dir(result_dir, k - 1) / (node["id"] + ".kt"))
        wanted = {line.strip() for line in read_text(Path(result_dir) / "work" / "original" / (node["id"] + ".kt")).split("\n") if re.search(r"\w", line)}
        for line in source_lines(prev, wanted) - source_lines(cur, wanted):
            warnings.append("%s: 앞 단계에 있던 원본 줄이 사라지거나 바뀜: %s" % (node["id"], line))
        if not any(re.search(r"\b%s\b" % re.escape(name), cur) for name in declaration_names(node)):
            warnings.append("%s: 노드 이름이 코드에 없음" % node["id"])
    return warnings


def cmd_apply(args):
    result_dir = Path(args.dir)
    manifest = load_manifest(result_dir)
    g, k = len(manifest["stages"]), args.k
    if not 2 <= k <= g - 1 or not work_dir(result_dir, k).is_dir():
        raise InputError("시작하지 않은 단계임(먼저 begin %d): %s" % (k, rel(work_dir(result_dir, k))))
    if work_dir(result_dir, k + 1).exists():
        raise InputError("다음 단계가 이미 시작되어 이 단계는 바꿀 수 없음: " + rel(work_dir(result_dir, k)))
    edits_path = result_dir / "work" / EDITS_FILE
    if not edits_path.is_file():
        raise InputError("바꿀 내용 파일이 없음: " + rel(edits_path))
    nodes = {n["id"]: n for n in manifest["nodes"] if not n["skip_reason"]}
    texts, errors = {}, []
    for i, (node_id, old, new) in enumerate(parse_edits(read_text(edits_path)), start=1):
        if node_id not in nodes:
            errors.append("%d번째 블록: 구체화하는 노드가 아님(%s)" % (i, node_id))
            continue
        path = work_dir(result_dir, k) / (node_id + ".kt")
        text = texts.get(node_id, read_text(path))
        count = text.count(old) if old else 0
        if count != 1:
            errors.append("%d번째 블록(%s): 바꿀 글이 %d번 나옴(정확히 1번이어야 함)" % (i, node_id, count))
            continue
        if new == "" and text.count(old + "\n") == 1:
            text = text.replace(old + "\n", "", 1)  # deleting whole lines removes them, not just their text
        else:
            text = text.replace(old, new, 1)
        texts[node_id] = text
    if errors:
        raise InputError("아무것도 바꾸지 않음 — " + "; ".join(errors))
    for node_id, text in texts.items():
        write_text(work_dir(result_dir, k) / (node_id + ".kt"), text)
    edits_path.unlink()
    emit({"stage": k, "changed": sorted(texts), "warnings": check_stage(result_dir, manifest, k)})


# ---- build: base box (research R6) -----------------------------------------------

BASE_CSS = """.stages { border: 1px solid rgba(128,128,128,.4); border-radius: 6px; padding: 0 1em; margin-bottom: 1em; }
.stages > input { position: absolute; opacity: 0; pointer-events: none; }
.stages > .stage { display: none; }
{STAGE_RULES}
.stages .head { display: flex; align-items: center; gap: .4em; padding: .5em 0 .2em; font-weight: 600; }
.stages .head .name { flex: 1; }
.stages .nav { display: inline-block; width: 2.2em; height: 1.8em; line-height: 1.8em; text-align: center; border: 1px solid rgba(128,128,128,.5); border-radius: 4px; font-weight: 400; cursor: pointer; user-select: none; }
.stages span.nav { opacity: .3; cursor: default; }
.stages .note { padding: 0 0 .5em; opacity: .8; }
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


def render_box(node_id, slides, diff_layers):
    """Base box. slides: [(title, note, code)]; diff_layers: [markup or None] (added after the code)."""
    n = len(slides)
    out = ['<div class="stages">', ""]
    for k in range(1, n + 1):
        out.append('<input type="radio" name="%s" id="%s-%d" class="s%d"%s>' % (node_id, node_id, k, k, " checked" if k == 1 else ""))
    out.append("")
    for k, (title, note, code) in enumerate(slides, start=1):
        prev = '<label class="nav" for="%s-%d">←</label>' % (node_id, k - 1) if k > 1 else '<span class="nav">←</span>'
        nxt = '<label class="nav" for="%s-%d">→</label>' % (node_id, k + 1) if k < n else '<span class="nav">→</span>'
        out += ['<div class="stage s%d">' % k, "",
                '<div class="head"><span class="name">%s</span>%s%s</div>' % (html.escape(title, quote=False), prev, nxt),
                *(['<div class="note">%s</div>' % html.escape(note, quote=False)] if note else []), "",
                '<div class="code">', "", fence(code), ""]
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

def stage_code(result_dir, manifest, node, stage):
    if stage["work"] == len(manifest["stages"]):
        return read_text(Path(result_dir) / "work" / "original" / (node["id"] + ".kt"))
    return read_text(work_dir(result_dir, stage["work"]) / (node["id"] + ".kt"))


def build_documents(result_dir, manifest, with_diff=True):
    stages = manifest["stages"]
    unchanged, docs_text = {}, {}
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
            if node["skip_reason"]:
                parts += ["⚠️ " + node["skip_reason"], ""]
                first = stages[0]
                code = read_text(work_dir(result_dir, 1) / (node["id"] + ".kt"))
                slides = [("1단계: %s (1/1)" % first["nickname"], note_for(True), code)]
                parts += [render_box(node["id"], slides, [None]), ""]
                continue
            slides, layers, prev = [], [], None
            for s in stages:
                code = stage_code(result_dir, manifest, node, s)
                if not s["visible"]:
                    prev = None  # the first visible stage after a hidden first stage gets no diff layer
                    continue
                changed = prev is None or code != prev
                if prev is not None and not changed:
                    unchanged.setdefault(s["nickname"], []).append(node["id"])
                title = "%d단계: %s (%d/%d)" % (s["display"], s["nickname"], s["display"], s["of"])
                slides.append((title, note_for(changed), code))
                layers.append(render_diff_layer(code, diff_lines(prev, code)) if with_diff and prev is not None and changed else None)
                prev = code
            max_slides = max(max_slides, len(slides))
            parts += [render_box(node["id"], slides, layers), ""]
        rules = "\n".join(".stages > input.s%d:checked ~ .stage.s%d { display: block; }" % (k, k) for k in range(1, max_slides + 1))
        parts += ["<style>", BASE_CSS.replace("{STAGE_RULES}", rules), "</style>", ""]
        if with_diff:
            parts += ["<style>", DIFF_CSS, "</style>", ""]
        docs_text[doc] = "\n".join(parts)
    return docs_text, unchanged


def extract_last_stage(doc_text, node_id, last):
    m = re.search(r'<input type="radio" name="%s" id="%s-1"' % (re.escape(node_id), re.escape(node_id)), doc_text)
    if not m:
        return None
    m2 = re.compile(r'<div class="stage s%d">.*?<div class="code">\n\n(`{3,})kotlin\n(.*?)\n\1\n' % last, re.S).search(doc_text, m.end())
    return m2.group(2) if m2 else None


def cmd_build(args):
    result_dir = Path(args.dir)
    manifest = load_manifest(result_dir)
    stages = manifest["stages"]
    g = len(stages)
    missing = []
    for node in manifest["nodes"]:
        if not (work_dir(result_dir, 1) / (node["id"] + ".kt")).is_file():
            missing.append(rel(work_dir(result_dir, 1) / (node["id"] + ".kt")))
        if node["skip_reason"]:
            continue
        for k in range(2, g):
            f = work_dir(result_dir, k) / (node["id"] + ".kt")
            if not f.is_file():
                missing.append(rel(f))
    if missing:
        raise InputError("작업 파일이 없음: " + ", ".join(missing))

    docs_text, unchanged = build_documents(result_dir, manifest)
    paths = []
    for doc, _ in manifest["docs"]:
        path = result_dir / doc
        write_text(path, docs_text[doc])
        paths.append(rel(path))

    # FR-010: re-read the documents and compare the last stage with the source, read again.
    view_dir = Path(manifest["view"]).parent.resolve()
    shown_last = stages[-1]["display"]
    mismatches, verified = [], 0
    for node in manifest["nodes"]:
        if node["skip_reason"]:
            continue
        written = extract_last_stage(read_text(result_dir / node["doc"]), node["id"], shown_last)
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
    b = sub.add_parser("begin")
    b.add_argument("dir")
    b.add_argument("k", type=int)
    a = sub.add_parser("apply")
    a.add_argument("dir")
    a.add_argument("k", type=int)
    bd = sub.add_parser("build")
    bd.add_argument("dir")
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    try:
        {"prepare": cmd_prepare, "begin": cmd_begin, "apply": cmd_apply, "build": cmd_build}[args.command](args)
    except InputError as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
