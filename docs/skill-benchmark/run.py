"""Measure token use and time of the generating skills with headless Claude Code.

Each run copies this repository's skills into a fresh temporary project, sends one fixed
request with `claude -p`, and appends one row per run to results.md next to this file.

Usage: python docs/skill-benchmark/run.py <label> [--runs N] [--ref <git ref>] [--skill <name>]
--ref measures the skills as they were at that commit instead of the working tree.
"""

import argparse
import io
import json
import shutil
import subprocess
import tarfile
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = Path(__file__).with_name("results.md")
MODEL = "claude-opus-5-5"
SKILLS = ["generating-architecture-views", "generating-zenuml-diagrams"]
CASES = {
    "generating-architecture-views": (
        "/generating-architecture-views 주문 처리 시스템의 구조를 보여줘. "
        "OrderController가 주문 요청을 받아 OrderService를 호출한다. "
        "OrderService는 InventoryRepository로 재고를 확인하고 PaymentService로 결제한다. "
        "PaymentService는 외부 PG API를 호출하고, 결제가 끝나면 NotificationService가 메일을 보낸다."
    ),
    "generating-zenuml-diagrams": (
        "/generating-zenuml-diagrams 로그인 흐름을 그려줘. "
        "사용자가 LoginController에 아이디와 비밀번호를 보낸다. "
        "LoginController는 AuthService에 인증을 요청하고, AuthService는 UserRepository에서 사용자를 찾는다. "
        "비밀번호가 맞으면 TokenService가 토큰을 만들어 돌려주고, 틀리면 401을 돌려준다."
    ),
}
HEADER = ("| label | skill | run | input | cache read | cache write | output | turns | seconds | outputs | denied |\n"
          "|---|---|---|---|---|---|---|---|---|---|---|\n")


def copy_skills(project, ref):
    for name in SKILLS:
        if ref:
            archive = subprocess.run(["git", "archive", ref, ".claude/skills/" + name],
                                     cwd=ROOT, capture_output=True, check=True).stdout
            with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
                tar.extractall(project)
        else:
            shutil.copytree(ROOT / ".claude" / "skills" / name, project / ".claude" / "skills" / name,
                            ignore=shutil.ignore_patterns("__pycache__", "node_modules"))


def run_once(skill, prompt, ref):
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp)
        copy_skills(project, ref)
        start = time.time()
        proc = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "json", "--model", MODEL,
             "--no-session-persistence", "--permission-mode", "acceptEdits",
             "--allowedTools", "Bash", "PowerShell"],
            cwd=project, capture_output=True, text=True, encoding="utf-8")
        seconds = time.time() - start
        outputs = len(list((project / ".zenuml").glob("*.md")))
    data = json.loads(proc.stdout)
    usage = data["usage"]
    return [usage.get("input_tokens", 0), usage.get("cache_read_input_tokens", 0),
            usage.get("cache_creation_input_tokens", 0), usage.get("output_tokens", 0),
            data.get("num_turns", 0), round(seconds), outputs, len(data.get("permission_denials", []))]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("label")
    parser.add_argument("--runs", type=int, default=2)
    parser.add_argument("--ref")
    parser.add_argument("--skill", choices=SKILLS, help="measure only this skill")
    args = parser.parse_args()
    if not RESULTS.exists():
        RESULTS.write_text("# Skill benchmark results\n\n" + HEADER, encoding="utf-8")
    for skill in [args.skill] if args.skill else SKILLS:
        for i in range(1, args.runs + 1):
            row = run_once(skill, CASES[skill], args.ref)
            line = "| " + " | ".join(str(x) for x in [args.label, skill, i] + row) + " |\n"
            with RESULTS.open("a", encoding="utf-8") as f:
                f.write(line)
            print(line, end="", flush=True)


if __name__ == "__main__":
    main()
