"""Generic settings loader for this skill.

Same behavior as exporting-markdown-diagrams/scripts/lib/settings.js, in Python. It knows
nothing about any specific option: everything it checks comes from the option definition
in settings.schema.json, so adding or changing an option never requires editing this file.

load_settings(skill_dir) -> {"values": {"<dotted.key>": value, ...}, "notices": [str, ...]}
  - settings.jsonc missing           -> every default, no notice
  - unreadable (bad JSON/not object)  -> every default, one notice
  - key missing                      -> its default, no notice
  - value breaks its type/constraint -> its default, one notice
  - leaf key not in the definition   -> ignored, one notice
"""

import json
from pathlib import Path

SETTINGS_FILE = "settings.jsonc"
SCHEMA_FILE = "settings.schema.json"

# The skill directory is the parent of scripts/, wherever this module is imported from.
SKILL_DIR = Path(__file__).resolve().parent.parent.parent


def strip_json_comments(text):
    """Remove // line comments and /* */ block comments, leaving string literals untouched."""
    out = []
    i = 0
    n = len(text)
    in_string = False
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


def _get_path(obj, dotted_key):
    node = obj
    for part in dotted_key.split("."):
        if not isinstance(node, dict) or part not in node:
            return False, None
        node = node[part]
    return True, node


def _leaf_paths(obj, prefix=""):
    paths = []
    for key, value in obj.items():
        full = prefix + "." + key if prefix else key
        if isinstance(value, dict):
            paths.extend(_leaf_paths(value, full))
        else:
            paths.append(full)
    return paths


def is_valid(option, value):
    kind = option.get("type")
    if kind == "enum":
        return isinstance(value, str) and value in option["values"]
    if kind == "boolean":
        return isinstance(value, bool)
    if kind == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False
        return "min" not in option or value > option["min"]
    if kind == "relativePath":
        return (
            isinstance(value, str)
            and value.strip() != ""
            and value[:1] not in ("\\", "/", "~")
            and not (len(value) >= 2 and value[0].isalpha() and value[1] == ":")
        )
    if kind == "itemList":
        return (
            isinstance(value, list)
            and all(isinstance(item, str) and item in option["items"] for item in value)
            and len(set(value)) == len(value)
        )
    return False


def format_value(value):
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def notice(text):
    return "⚙️ 설정 안내: " + SETTINGS_FILE + " — " + text


def invalid_notice(option):
    return notice(
        "`" + option["key"] + "` 값이 허용되지 않아 기본값 `" + format_value(option["default"]) + "` 사용"
    )


def load_schema(skill_dir=SKILL_DIR):
    with open(Path(skill_dir) / SCHEMA_FILE, encoding="utf-8") as f:
        return json.load(f).get("options", [])


def load_settings(skill_dir=SKILL_DIR):
    options = load_schema(skill_dir)
    values = {option["key"]: option["default"] for option in options}
    notices = []

    settings_path = Path(skill_dir) / SETTINGS_FILE
    if not settings_path.exists():
        return {"values": values, "notices": notices}

    try:
        user = json.loads(strip_json_comments(settings_path.read_text(encoding="utf-8")))
    except ValueError:
        user = None
    if not isinstance(user, dict):
        notices.append(notice("읽지 못해 모든 값을 기본값으로 사용"))
        return {"values": values, "notices": notices}

    known = set()
    for option in options:
        known.add(option["key"])
        found, value = _get_path(user, option["key"])
        if not found:
            continue
        if is_valid(option, value):
            values[option["key"]] = value
        else:
            notices.append(invalid_notice(option))
    for leaf in _leaf_paths(user):
        if leaf not in known:
            notices.append(notice("알 수 없는 키 `" + leaf + "` 무시"))

    return {"values": values, "notices": notices}
