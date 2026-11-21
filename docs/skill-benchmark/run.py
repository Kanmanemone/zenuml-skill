"""Measure token use and time of the generating skills with headless Claude Code.

Each run copies this repository's skills into a fresh temporary project, sends one fixed
request with `claude -p`, and appends one row per run to results.md next to this file.

Usage: python docs/skill-benchmark/run.py <label> [--runs N] [--ref <git ref>] [--skill <name>]
--ref measures the skills as they were at that commit instead of the working tree.
--static compares SKILL.md sizes for all four skills without invoking a model.
"""

import argparse
import io
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = Path(__file__).with_name("results.md")
SKILLS = [
    "generating-architecture-views",
    "generating-zenuml-diagrams",
    "exporting-markdown-diagrams",
    "revealing-code-step-by-step",
]
RUNTIME_SKILLS = SKILLS[:2]
CASES = {
    "generating-architecture-views": (
        "Use the generating-architecture-views skill. 신규 팀원 온보딩 목적으로 주문 처리 시스템의 구조를 보여줘. "
        "OrderController가 주문 요청을 받아 OrderService를 호출한다. "
        "OrderService는 InventoryRepository로 재고를 확인하고 PaymentService로 결제한다. "
        "PaymentService는 외부 PG API를 호출하고, 결제가 끝나면 NotificationService가 메일을 보낸다."
    ),
    "generating-zenuml-diagrams": (
        "Use the generating-zenuml-diagrams skill. 로그인 흐름을 그려줘. "
        "사용자가 LoginController에 아이디와 비밀번호를 보낸다. "
        "LoginController는 AuthService에 인증을 요청하고, AuthService는 UserRepository에서 사용자를 찾는다. "
        "비밀번호가 맞으면 TokenService가 토큰을 만들어 돌려주고, 틀리면 401을 돌려준다."
    ),
}
HEADER = ("| label | skill | run | input | cache read | cache write | output | turns | seconds | outputs | denied |\n"
          "|---|---|---|---|---|---|---|---|---|---|---|\n")


def copy_skills(project, ref):
    for name in RUNTIME_SKILLS:
        if ref:
            archive = subprocess.run(["git", "archive", ref, ".agents/skills/" + name],
                                     cwd=ROOT, capture_output=True, check=True).stdout
            with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
                tar.extractall(project)
            shutil.copytree(project / ".agents" / "skills" / name,
                            project / ".claude" / "skills" / name,
                            ignore=shutil.ignore_patterns("__pycache__", "node_modules"))
        else:
            shutil.copytree(ROOT / ".agents" / "skills" / name, project / ".claude" / "skills" / name,
                            ignore=shutil.ignore_patterns("__pycache__", "node_modules"))


def run_once(skill, prompt, ref, model):
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp)
        copy_skills(project, ref)
        start = time.time()
        command = ["claude", "-p", prompt, "--output-format", "json",
                   "--no-session-persistence", "--permission-mode", "acceptEdits",
                   "--allowedTools", "Bash", "PowerShell"]
        if model:
            command[5:5] = ["--model", model]
        proc = subprocess.run(
            command,
            cwd=project, capture_output=True, text=True, encoding="utf-8")
        seconds = time.time() - start
        output_paths = list((project / ".zenuml").glob("*.md"))
        outputs = len(output_paths)
        valid = outputs == 1
        if valid:
            output = output_paths[0].read_text(encoding="utf-8")
            if skill == "generating-architecture-views":
                required = ("### Dependency", "### Responsibility", "### Collaboration", "```mermaid")
            else:
                required = ("```mermaid", "zenuml")
            valid = all(value in output for value in required)
        logs = list((project / ".zenuml" / "log").glob("*.md"))
        valid = valid and len(logs) == 1 and "## Round 1" in logs[0].read_text(encoding="utf-8")
        outputs = 1 if valid else 0
    data = json.loads(proc.stdout)
    usage = data.get("usage", {})
    if proc.returncode or data.get("is_error") or not any(
        usage.get(key, 0) for key in (
            "input_tokens", "cache_read_input_tokens",
            "cache_creation_input_tokens", "output_tokens"
        )
    ):
        raise RuntimeError(data.get("result") or proc.stderr or "Claude run failed")
    if not outputs:
        print("invalid run: " + data.get("result", "no result"), file=sys.stderr)
    return [usage.get("input_tokens", 0), usage.get("cache_read_input_tokens", 0),
            usage.get("cache_creation_input_tokens", 0), usage.get("output_tokens", 0),
            data.get("num_turns", 0), round(seconds), outputs, len(data.get("permission_denials", []))]


def skill_text(name, ref):
    path = f".agents/skills/{name}/SKILL.md"
    if ref:
        return subprocess.run(
            ["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True,
            text=True, encoding="utf-8", check=True
        ).stdout
    return (ROOT / path).read_text(encoding="utf-8")


def static_row(name, ref):
    text = skill_text(name, ref)
    description = next(
        line.removeprefix("description:").strip()
        for line in text.splitlines() if line.startswith("description:")
    )
    body = text.split("---", 2)[2]
    return [len(description), len(body), len(body.split()), len(body.splitlines())]


def print_static(ref):
    print("| skill | version | description chars | body chars | body words | body lines |")
    print("|---|---|---:|---:|---:|---:|")
    for name in SKILLS:
        if ref:
            print("| " + " | ".join(map(str, [name, ref] + static_row(name, ref))) + " |")
        print("| " + " | ".join(map(str, [name, "working-tree"] + static_row(name, None))) + " |")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("label")
    parser.add_argument("--runs", type=int, default=2)
    parser.add_argument("--ref")
    parser.add_argument("--skill", choices=SKILLS, help="measure only this skill")
    parser.add_argument("--static", action="store_true", help="compare SKILL.md sizes only")
    parser.add_argument("--model", help="Claude model override; default uses the CLI default")
    args = parser.parse_args()
    if args.static:
        print_static(args.ref)
        return
    if args.skill and args.skill not in RUNTIME_SKILLS:
        parser.error("runtime benchmark is available for the two generating skills")
    if not RESULTS.exists():
        RESULTS.write_text("# Skill benchmark results\n\n" + HEADER, encoding="utf-8")
    for skill in [args.skill] if args.skill else RUNTIME_SKILLS:
        for i in range(1, args.runs + 1):
            row = run_once(skill, CASES[skill], args.ref, args.model)
            line = "| " + " | ".join(str(x) for x in [args.label, skill, i] + row) + " |\n"
            with RESULTS.open("a", encoding="utf-8") as f:
                f.write(line)
            print(line, end="", flush=True)


if __name__ == "__main__":
    main()
