---
name: revealing-code-step-by-step
description: Builds a gradual Kotlin walkthrough from an architecture view — a plain-language situation under a fixed responsibility line, then an outline listing what the node does, then one of those jobs unfolded into exact source at a time. Use to understand the implementation behind a structural view step by step. Not for creating architecture views, sequence diagrams, or non-Kotlin source.
---

# Revealing Code Step by Step

Each node gets one pager of **refinement steps** (정제 단계): a situation paragraph, an **outline** (the real declaration head with one `⟨placeholder⟩` per job the node does — the forest), one **unfold** per job showing that job's exact source (the trees), and the source. The node's responsibility sentence from the view stays fixed above the pager.

`scripts/stages.py` does everything deterministic: it splits each node's source into unfold units, builds every code scene, checks your input, and renders the documents. You write only one small `outline.json` with a placeholder sentence per unit and optional folds; an isolated subagent writes stage 1. Never write scene code. Never read `stages.md`, `settings.jsonc`, or the work files yourself; the script prints what you need. Do not add question captions or rhetorical prompts to the documents.

## Running the script

Find a Python 3.9+ interpreter once: `python3`, `python`, `py -3` (on Windows: `python`, `py -3`, `python3`). None: reply `Python 3.9 이상을 찾지 못해 정제 단계 문서를 만들지 않음` and stop.

Run `<python> <this skill's directory>/scripts/stages.py <command> …` from the project root, without changing directory. Each command prints one JSON line. Exit 2 = bad input, and the single stderr line says why.

## Workflow

### 1. Prepare

```text
prepare <view file> [--show=<nicknames>] [--hide=<nicknames>] [--output-dir=<path>] [--pick=<id>:<n>,...]
```

- Add `--hide`/`--show` (comma-separated stage nicknames) or `--output-dir` only when the request itself asks for it (e.g. "이번엔 펼치기 단계는 빼고", "결과는 ./stages에"). Never edit the settings file.
- Output: `dir`, `stage1_prompt`, `outline` (the path you will write), `pick`, `stages`. Then, for each node with source, one block: `===== <id> · 책임: … · 단위 k개 =====`, the unit list, and the node's source with each line tagged `<line> <unit>| ` (`-` = outline header or blank). Rebuilding replaces the result directory; preserve any user-created preview copies before running it.
- Exit 2: tell the user the stderr line and stop.
- **`pick` is not empty** (several declarations share a node's name): for each entry, choose the candidate that carries the node's meaning in the view — the declaration its Responsibility, Collaboration, and edges describe (e.g. for an edge "hiltViewModel로 주입·uiState 구독", the overload that takes the view model). The `header` lines usually settle it; otherwise read those line ranges of `source`. Then run `prepare` again with the same options plus `--pick=<id>:<pick>` for every entry. The source blocks are printed only once `pick` is empty.

### 2. Stage 1

Launch a **new** subagent with no history of this conversation (Claude Code: Agent tool, general-purpose) — never a fork or anything that inherits this conversation, which may contain the source. Its whole prompt:

```text
Read <stage1_prompt> (in as many parts as it takes) and do exactly what it says. Read no other file.
```

The file already holds the instructions, the stage-1 definition, the target paths, and the view. If you cannot start such a subagent, reply `격리된 서브에이전트를 쓸 수 없어 정제 단계 문서를 만들지 않음` and stop — never write stage 1 yourself.

### 3. Outline input

From the source blocks printed by `prepare`, write the `outline` file once:

```json
{
  "<node id>": {
    "placeholders": ["<one Korean sentence per unit, in unit order>"],
    "folds": [{"from": 13, "to": 18, "text": "<what the folded lines do>"}]
  }
}
```

- **Placeholders:** exactly one per unit, describing what that unit does for the reader. Do not repeat the `책임` line; split it. No identifiers that the unit does not show, no `⟨⟩`.
- **Folds** (optional): lines inside one member's body that are detail rather than the point of the job (e.g. a loading/subscription policy). They show as `⟨text⟩` in the unfolds and open in the source scene. Never fold a member's first line.
- Nodes with `단위 0개` need no entry.

### 4. Build

`build <dir>`:

- Exit 2: a stage-1 file or the outline input is missing or wrong (count, empty or repeated sentence, a fold outside one member). Missing stage-1 files: launch the subagent again. Otherwise fix `outline.json` and rerun.
- Exit 3: the source changed during the run, or the script has a bug. Do not touch work files; tell the user the stderr line.
- Exit 0: the chat response is exactly the `reply` value, nothing else.
