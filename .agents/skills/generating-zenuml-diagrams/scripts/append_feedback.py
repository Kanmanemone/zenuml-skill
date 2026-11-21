"""Append one generated diagram to its feedback log without regenerating it."""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path
from typing import Optional

ROUND_RE = re.compile(r"^## Round (\d+) — ", re.MULTILINE)


def append_feedback(
    output_path: Path,
    log_path: Path,
    request_path: Path,
    mode: str,
    round_date: Optional[str] = None,
) -> int:
    resolved = {path.resolve() for path in (output_path, log_path, request_path)}
    if len(resolved) != 3:
        raise ValueError("output, log, and request paths must be different")

    output = output_path.read_text(encoding="utf-8")
    if not output:
        raise ValueError("output is empty")
    if not output.endswith("\n"):
        output += "\n"
    request = request_path.read_text(encoding="utf-8").strip()
    if not request:
        raise ValueError("request summary is empty")

    existing = ""
    if mode == "append" and log_path.exists():
        existing = log_path.read_text(encoding="utf-8")
    rounds = [int(value) for value in ROUND_RE.findall(existing)]
    round_number = max(rounds, default=0) + 1
    block = (
        f"## Round {round_number} — {round_date or date.today().isoformat()}\n"
        f"**Request**: {request}\n\n"
        f"**Response**:\n{output}"
    )

    log_path.parent.mkdir(parents=True, exist_ok=True)
    if existing:
        separator = "\n" if existing.endswith("\n") else "\n\n"
        with log_path.open("a", encoding="utf-8") as stream:
            stream.write(separator + block)
    else:
        log_path.write_text(block, encoding="utf-8")
    try:
        request_path.unlink()
    except OSError:
        pass
    return round_number


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("log", type=Path)
    parser.add_argument("request", type=Path)
    parser.add_argument("--mode", choices=("new", "append"), required=True)
    parser.add_argument("--date", dest="round_date")
    args = parser.parse_args()
    try:
        round_number = append_feedback(
            args.output, args.log, args.request, args.mode, args.round_date
        )
    except (OSError, ValueError) as exc:
        parser.exit(1, f"feedback log failed: {exc}\n")
    print(f"{args.log} (Round {round_number})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
