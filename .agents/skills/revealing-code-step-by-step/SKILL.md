---
name: revealing-code-step-by-step
description: Reveal source behind an architecture view one scope at a time, from a plain-language outline to exact code. Use for implementation walkthroughs, not for creating diagrams.
---

# Revealing Code Step by Step

Each node gets one pager of **refinement steps** (정제 단계): a situation paragraph, an **outline** (the real declaration head with every step as `⟨n. sentence⟩`, inner steps indented under the one that holds them — the forest), one **unfold** per step that opens one layer of exact source (the trees), and the source when the last visible scene is not already the source. The node's responsibility sentence from the view stays fixed above the pager.

`scripts/stages.py` owns scope parsing, numbering, scenes, validation, and rendering.
Write only `outline.json`: each scope's purpose and which children open now or
later. An isolated subagent writes stage 1. Never write scene code or read
`stages.md`, settings, or work files; the script prints what is needed. Do not add
question captions or rhetorical prompts.

## Running the script

Find a Python 3.9+ interpreter once: `python3`, `python`, `py -3` (on Windows: `python`, `py -3`, `python3`). None: reply `Python 3.9 이상을 찾지 못해 정제 단계 문서를 만들지 않음` and stop.

Run `<python> <this skill's directory>/scripts/stages.py <command> …` from the project root, without changing directory. Each command prints one JSON line. Exit 2 = bad input; each stderr line names one problem.

## Workflow

### 1. Prepare

```text
prepare <view file> [--show=<nicknames>] [--hide=<nicknames>] [--output-dir=<path>] [--pick=<id>:<n>,...]
```

- Add `--hide`/`--show` (comma-separated stage nicknames) or `--output-dir` only when the request itself asks for it (e.g. "이번엔 펼치기 단계는 빼고", "결과는 ./stages에"). Never edit the settings file.
- Output: `dir`, `stage1_prompt`, `outline` (the path you will write), `pick`, `stages`. Then, for each node with scopes, one block `===== <id> · 책임: … · 스코프 k개 =====` and its scopes innermost first (`--- #n (부모 #m)`, the root last). In a scope every source line is tagged: `-` the scope's own line, a number the first line of child `n` (a leaf child continues on untagged lines; a child scope is folded to `⟨#k⟩`, already written above), `=` a one-line declaration that attaches itself where it is first used (root only, never grouped; multi-line private members are ordinary children). Each source line appears once in the whole output. Rebuilding replaces the result directory; preserve any user-created preview copies before running it.
- Exit 2: tell the user the stderr line and stop.
- **`pick` is not empty** (several declarations share a node's name): for each entry, choose the candidate that carries the node's meaning in the view — the declaration its Responsibility, Collaboration, and edges describe (e.g. for an edge "hiltViewModel로 주입·uiState 구독", the overload that takes the view model). The `header` lines usually settle it; otherwise read those line ranges of `source`. Then run `prepare` again with the same options plus `--pick=<id>:<pick>` for every entry. The source blocks are printed only once `pick` is empty.

### 2. Stage 1

Launch a **new** subagent with no history of this conversation (Claude Code: Agent tool, general-purpose) — never a fork or anything that inherits this conversation, which may contain the source. Its whole prompt:

```text
Read <stage1_prompt> (in as many parts as it takes) and do exactly what it says. Read no other file.
```

The file already holds the instructions, the stage-1 definition, the target paths, and the view. If you cannot start such a subagent, reply `격리된 서브에이전트를 쓸 수 없어 정제 단계 문서를 만들지 않음` and stop — never write stage 1 yourself.

### 3. Outline input

From the scope blocks printed by `prepare`, write the `outline` file once: per node, one array entry per scope in the printed order (innermost first, root last), **one scope per line**.

```json
{"<node id>": [
  {"s": "<purpose sentence>", "with": [3, 4], "sep": [{"ids": [1, 2], "s": "<sentence for this group>"}]},
  {"sep": [{"ids": [1, 2, 3], "s": "<sentence>"}, {"ids": [4]}]}
]}
```

Go through the scopes in order and decide one scope at a time from its lines alone; a folded `⟨#k⟩` means the sentence you already wrote for scope `#k`.

- **`s`** (every scope but the root): what the scope is *for*, one Korean sentence ending in `~한다.`, at most 45 characters. Write the purpose, never a list of what the children do — not "A를 구하고, B를 그리고, C를 비운다." but "불릿이 텍스트와 겹치지 않게 그릴 자리를 마련한다." No comma, no second action joined by `~하고`·`~며`; if it only fits as two actions, find the purpose above them. No identifiers the scope does not show, no `⟨⟩`, not the `책임` line.
- **`with`** (optional, never on the root): children that open together with this scope because they are short and obvious (plain pass-through arguments, one-line calls).
- **`sep`**: groups of the other children, each kept as one `⟨n. s⟩` and unfolded later — at most 4 per scope. Put children that tell one story in one group, even when they are not adjacent. Each group needs `s` (same rules), except a group of one child scope, which may omit it and reuse that scope's `s`. Aim for groups a reader can take in at once, without splitting what belongs together.
- Every child number appears exactly once across `with` and `sep`. Nodes without a block need no entry.

### 4. Build

`build <dir>`:

- Exit 2: a stage-1 file or the outline input is missing or wrong. Missing stage-1 files: launch the subagent again. Otherwise each line names one `<id> 스코프 #<n>`; fix only those scope lines in `outline.json` and rerun.
- Exit 3: the source changed during the run, or the script has a bug. Do not touch work files; tell the user the stderr line.
- Exit 0: the chat response is exactly the `reply` value, nothing else.
