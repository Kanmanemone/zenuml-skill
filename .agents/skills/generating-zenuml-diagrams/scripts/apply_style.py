#!/usr/bin/env python3
"""Add or remove the readable style block at the end of a generated ZenUML Markdown file
(001 FR-016). The block is fixed: VS Code Light+ code colors for the same meanings, opaque
comments, a halo behind text, and no size changes, since ZenUML lays text out at fixed sizes.

Usage: python3 apply_style.py <.zenuml/<slug>.md> [--style=readable|zenuml-default]
--style is a value the request itself states; otherwise diagram.style in settings.jsonc decides.
Requires Python 3.9+, standard library only. Never touches the diagram code fence.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from read_settings import is_valid, load_schema, load_settings, notice  # noqa: E402

KEY = "diagram.style"
BLOCK = """<details class="zenuml-style">
<summary>이 문서에 적용되지 못한 &lt;style&gt; 코드</summary>

<style>
.zenuml-style { display: none; }
.participant-label { font-size: 14px !important; }
.message-label { fill: #000000 !important; font-weight: 600; }
.fragment-label { fill: #AF00DB !important; }
.fragment-condition { fill: #001080 !important; opacity: 1 !important; transform: translateX(6px); }
.comment-text { fill: #008000 !important; opacity: 1 !important; }
.seq-number { fill: #237893 !important; font-weight: 400 !important; }
.message-label, .fragment-label, .fragment-condition, .comment-text, .seq-number, .return-label {
  paint-order: stroke; stroke: var(--vscode-editor-background, #ffffff); stroke-width: 4px; stroke-linejoin: round;
}
</style>

</details>
"""
EXISTING = re.compile(r'\n*<details class="zenuml-style">.*?</details>\n*', re.S)


def apply(text, style):
    """text uses \n line ends. Returns it without any style block, plus the block when readable."""
    text = EXISTING.sub("\n", text).rstrip("\n") + "\n"
    return text + "\n" + BLOCK if style == "readable" else text


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    style = load_settings()["values"][KEY]
    for arg in list(args):
        if arg.startswith("--style="):
            value = arg[len("--style="):].strip()
            option = next(o for o in load_schema() if o["key"] == KEY)
            if is_valid(option, value):
                style = value
            else:
                print(notice("명령줄 `" + KEY + "` 값이 허용되지 않아 설정 값 사용"))
            args.remove(arg)
    if len(args) != 1:
        print("usage: apply_style.py <.zenuml/<slug>.md> [--style=readable|zenuml-default]", file=sys.stderr)
        return 2
    path = Path(args[0])
    try:
        raw = path.read_bytes().decode("utf-8")
    except (OSError, ValueError) as e:
        print("스타일 적용 실패: " + str(e), file=sys.stderr)
        return 1
    nl = "\r\n" if "\r\n" in raw else "\n"
    path.write_bytes(apply(raw.replace("\r\n", "\n"), style).replace("\n", nl).encode("utf-8"))
    print("스타일 적용(" + style + "): " + str(path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
