---
name: revealing-code-step-by-step
description: Takes an architecture view file (.zenuml/<slug>.architecture.md, made by generating-architecture-views) and builds Markdown documents in which each node's Kotlin code can be paged through refinement steps — from minimal code invented from the view alone, step by step, to the node's exact source. Use when the user wants to understand how the components in a structural view are actually implemented, asks to see the code behind a view step by step, or names this skill. Do not use to create or edit architecture views, for sequence diagrams, or for non-Kotlin code.
---

# Revealing Code Step by Step

Each node of an architecture view gets one code box that pages through **refinement steps** (정제 단계): stage 1 is Kotlin invented from the view alone, each middle stage makes one more aspect match the source, and the last stage is the node's declaration cut verbatim from the source. `scripts/stages.py` does everything deterministic — source ranges, the stage-1 prompt, copying stages, applying edits, checking them, diff coloring, documents, and the reply. Your only jobs are choosing overloads, launching the stage-1 subagent, and writing the middle-stage edits.

Never read `stages.md`, `settings.jsonc`, or the work files yourself; the script prints what you need.

## Running the script

Find a Python 3.9+ interpreter once: `python3`, `python`, `py -3` (on Windows: `python`, `py -3`, `python3`). None: reply `Python 3.9 이상을 찾지 못해 정제 단계 문서를 만들지 않음` and stop.

Run `<python> <this skill's directory>/scripts/stages.py <command> …` from the project root, without changing directory. Each command prints one JSON line (`begin` then prints code). Exit 2 = bad input, and the single stderr line says why.

## Workflow

### 1. Prepare

```text
prepare <view file> [--show=<nicknames>] [--hide=<nicknames>] [--output-dir=<path>] [--pick=<id>:<n>,...]
```

- Add `--hide`/`--show` (comma-separated stage nicknames) or `--output-dir` only when the request itself asks for it (e.g. "이번엔 의존 연결 단계는 빼고", "결과는 ./stages에"). Never edit the settings file.
- Output: `dir` (result dir), `stage1_prompt`, `middle` (the stage numbers k to run in step 3), `pick`.
- Exit 2: tell the user the stderr line and stop.
- **`pick` is not empty** (several declarations share a node's name): for each entry, choose the candidate that carries the node's meaning in the view — the declaration its Responsibility, Collaboration, and edges describe (e.g. for an edge "hiltViewModel로 주입·uiState 구독", the overload that takes the view model). The `header` lines usually settle it; otherwise read those line ranges of `source`. Then run `prepare` again with the same options plus `--pick=<id>:<pick>` for every entry.

### 2. Stage 1

Launch a **new** subagent with no history of this conversation (Claude Code: Agent tool, general-purpose) — never a fork or anything that inherits this conversation, which may contain the source. Its whole prompt:

```text
Read <stage1_prompt> (in as many parts as it takes) and do exactly what it says. Read no other file.
```

The file already holds the instructions, the stage-1 definition, the target paths, and the view. If you cannot start such a subagent, reply `격리된 서브에이전트를 쓸 수 없어 정제 단계 문서를 만들지 않음` and stop — never write stage 1 yourself.

### 3. Middle stages

For each k in `middle`, in order:

1. `begin <dir> k` — copies stage k−1 to stage k. The JSON gives this stage's `becomes`, `unrevealed`, `notation`, and `merged` (shares of turned-off stages that this stage takes on), plus the `edits` path. Then it prints each node's current code (`===== <id> · k단계 =====`). At k = 2 it also prints each node's source range (`===== <id> · 원본 =====`); keep using those for later stages. Exit 2 listing stage-1 paths means the subagent missed them: launch it again, then rerun.
2. Write all changes for this stage into the `edits` file as blocks, then run `apply <dir> k`:

   ```text
   <<<<<<< <node id>
   exact current text (whole lines, or part of one line)
   =======
   replacement text (empty = delete those lines)
   >>>>>>>
   ```

   Each old text must occur exactly once in that node's file; blocks for one node apply in order. If any block fails, nothing changes — fix the file and rerun `apply`. No change needed at this stage: skip `apply`.
3. `apply` prints `warnings` (a source line from the previous stage that disappeared or changed, a node name that is gone). Fix each with another edits file + `apply` before the next `begin`; once the next stage starts, this one cannot change.

**Rules for the edits**

1. **Only this stage's share.** Make exactly `becomes` (and every `merged` entry's `becomes`) match the source, applying exactly the `notation`. Never pull a later aspect forward or leave this stage's aspect for later.
2. **Align revealed names everywhere.** When a real name (function, property, type) appears at this stage, rename every invented name for the same thing in the other nodes' files at this stage too. Only the name changes; the rest of that call follows its own node's stages.
3. **Only climb the ladder.** Every part moves up, never down: `...` (hidden) → `⟨description⟩` (described) → partial source like `call(a, ...)` → source. A source line once shown never changes or hides again. `⟨⟩` are U+27E8 and U+27E9.

   ```kotlin
   fun place(order: Order): Receipt {
       ⟨주문이 비었는지 확인하고 합계를 구함⟩      // described
       inventory.reserve(order.id)              // source, from now on unchanged
       AuditLog.record(⟨주문 번호와 합계로 만든 글⟩)  // partial source
   }
   ```

4. **Stage 2 replaces invented code.** Invented bodies and members from stage 1 become `⟨what that code did⟩` or `...`; from then on the box shows only source or clearly-not-source marks. An invented line that equals a source line character for character stays as it is.
5. **Annotations go with their declaration.** The node's own annotations, modifiers, kind (class, interface, object, …), and supertypes appear together; a member's annotations appear with that member. Annotation arguments long enough to be implementation stay `...` until a later stage.
6. **Fold nested nodes.** A node whose header says `안에 든 노드: <ids>` keeps those nodes' code folded as `⟨<inner node name>⟩` until the last stage (the inner node has its own box).
7. **Change nothing else.**

### 4. Build

`build <dir>`:

- Exit 2 (missing work file): copy each listed file from the same node's previous stage, apply that stage's rules, rerun.
- Exit 3: the source changed during the run, or the script has a bug. Do not touch work files; tell the user the stderr line.
- Exit 0: the chat response is exactly the `reply` value, nothing else.
