---
name: revealing-code-step-by-step
description: Takes an architecture view file (.zenuml/<slug>.architecture.md, made by generating-architecture-views) and builds Markdown documents in which each node's Kotlin code can be paged through refinement steps — from minimal code invented from the view alone, step by step, to the node's exact source. Use when the user wants to understand how the components in a structural view are actually implemented, asks to see the code behind a view step by step, or names this skill. Do not use to create or edit architecture views, for sequence diagrams, or for non-Kotlin code.
---

# Revealing Code Step by Step

For every node in an architecture view, this skill produces one code box that pages through **refinement steps** (정제 단계): stage 1 is minimal Kotlin invented without seeing the source, each later stage makes exactly what its definition says match the source, and the last stage is the node's declaration cut verbatim from the source file. A bundled script does everything deterministic; you write only stage 1 (through a fresh subagent) and the middle stages.

## Workflow

1. **Python** — find a Python 3.9+ interpreter once: `python3`, then `python`, then `py -3` (on Windows: `python`, then `py -3`, then `python3`). None found: reply `Python 3.9 이상을 찾지 못해 정제 단계 문서를 만들지 않음` and stop.
2. **Prepare** — run `prepare` (see "Script").
3. **Stage 1** — launch the isolated subagent (see "Stage 1").
4. **Middle stages** — for k = 2 … g−1, run `begin k` and edit its files (see "Middle stages").
5. **Build** — run `build`, then reply (see "Reply").

## Script

Run it by full path without changing the working directory; paths are relative to the project root:

```text
<python> <this skill's directory>/scripts/stages.py prepare <view file> [--show=<nicknames>] [--hide=<nicknames>] [--output-dir=<relative path>] [--pick=<id>:<n>,...]
<python> <this skill's directory>/scripts/stages.py begin <result dir> <k>
<python> <this skill's directory>/scripts/stages.py build <result dir>
```

Each command prints one line of JSON. Exit code 2 means bad input (the one stderr line says why); exit code 3 (build only) means the last stage differs from the source.

- **prepare** reads the view, the stage definition (`stages.md`), and `settings.jsonc`, deletes and recreates `<result dir>` (`<view folder>/<output.directory>/<slug>.stages/`), cuts each node's source range into `work/original/<id>.kt`, and prints `dir`, `stages` (the stages this run generates: `work` number, `nickname`, `visible`, `display`/`of`, `becomes`, `unrevealed`, `notation`, `merged`), `notices`, and `nodes` (`id`, `name`, `stage1` path, `original` path, `range`, `contains`, `candidates`, `skip_reason`, `doc`). `g` below is the number of entries in `stages`.
- Exit 2 on prepare (not a view, no nodes, bad `stages.md`): tell the user the stderr line and stop.
- **Several declarations with the node's name** (overloads): that node has `candidates` (`pick`, `start_line`, `end_line`, `header`) and a `skip_reason` asking for a pick. Choose the one that carries the node's meaning in the view — the declaration its Responsibility, Collaboration, and edges describe (e.g. a `MemoScreen` whose edge is "hiltViewModel로 주입·uiState 구독" is the overload that takes the view model) — read the candidates' lines in the source to decide, then run `prepare` again with `--pick=<id>:<pick>` for every such node (plus the same `--show`/`--hide`/`--output-dir` as before). Do this before stage 1.

## Stage definition and settings

- The stages — how many, their order, nicknames, and what each one makes match the source — live only in `stages.md`. Never read `stages.md` or `settings.jsonc` yourself; use what `prepare` and `begin` print.
- `settings.jsonc` → `stages` turns stages on or off by nickname; `output.directory` sets where results go. The last stage (원본) is always shown. A stage turned off (other than the first) is not generated: its share arrives in the next generated stage's `merged`. A hidden first stage is still generated (it is the starting point) but not shown.
- **The request itself states a value** ("이번엔 의존 연결 단계는 빼고", "결과는 ./stages에"): pass `--hide=`/`--show=` (comma-separated nicknames) or `--output-dir=` for this run only. Never edit the settings file.

## Stage 1

Launch a **new** sub-agent that starts with no history of this conversation (Claude Code: the Agent tool with a general-purpose agent; other agents: their equivalent) — never a fork or any sub-agent that inherits this conversation, which may contain the source. Its prompt is exactly this template, filled in, and nothing else:

````text
You write stage 1 of a code walkthrough. You have never seen the real source code and must not try to.

Tools: use Read only for the architecture view file named below (in as many parts as it takes to
read all of it), and Write only for the paths listed below. Never read any other file. Do not use
Grep, Glob, Bash, or any web tool.

Read the whole architecture view file. For every node listed, write minimal Kotlin code to the given path:
- Declare the node under exactly the name given.
- Show each dependency in the view as the source node's code using the target node.
- Add no dependency the view doesn't show; add nothing beyond what shows the node's responsibility
  and its dependencies — no explanatory comments, error handling, configuration, or extras.
- Identifiers that appear in the view may be used. Every other name (functions, fields, parameters,
  types) is yours to invent; if one matches the real code, that must be coincidence.

Stage definition: <stages[0].nickname> — <stages[0].becomes> / <stages[0].unrevealed>

Nodes and paths:
<one line per node: "<id> (<name>) → <stage1 path>">

Architecture view file: <absolute path of the view file>
````

The view file is the only thing the subagent may read: it is exactly the input FR-003 allows, and pointing to it instead of pasting it saves output tokens.

When it returns, check that every `stage1` path exists. If your agent cannot start such a fresh sub-agent, reply `격리된 서브에이전트를 쓸 수 없어 정제 단계 문서를 만들지 않음` and stop — never write stage 1 yourself.

## Middle stages

For each k from 2 to g−1, in order:

1. Run `begin <result dir> k`. It copies stage k−1 into stage k and prints this stage's `becomes`, `unrevealed`, `notation`, `merged` (shares of stages turned off before it), and `files`.
2. Read each file and its source range (`work/original/<id>.kt`), then change only the parts the rules below call for — never rewrite a whole file, so that nothing you didn't mean to change can drift. Use the Edit tool, or, when there are many changes, any tool that replaces an exact text occurring exactly once in the file and fails otherwise (one call can then carry many replacements).
3. Before the next `begin`, check every file of this stage against the rules and fix it. A stage cannot be changed once the next one has started.

Nodes with a `skip_reason` stay at stage 1; `begin` does not copy them.

**Rules**

1. **Only this stage's share.** Make exactly `becomes` (plus every `merged` entry's `becomes`) match the source, and apply exactly the `notation` lines. Never pull a later aspect forward, never leave this stage's aspect for later.
2. **Align revealed names everywhere.** When a real name (function, property, type) appears at this stage, change every invented name that refers to the same thing in the other nodes' files at this same stage. Only the name changes; the rest of that call follows its own node's stages. Nodes with a `skip_reason` are left alone.
3. **Only climb the ladder.** Each part of the code moves up, never down: `...` (hidden) → `⟨description⟩` (described) → partial source like `call(a, ...)` → source. Never change the characters of a source line already shown, and never hide one again. `⟨⟩` are U+27E8 and U+27E9.

   ```kotlin
   fun place(order: Order): Receipt {
       ⟨주문이 비었는지 확인하고 합계를 구함⟩      // described
       inventory.reserve(order.id)              // source, from now on unchanged
       AuditLog.record(⟨주문 번호와 합계로 만든 글⟩)  // partial source
   }
   ```

4. **Stage 2 replaces invented code.** At stage 2, invented bodies and members from stage 1 become `⟨what that code did⟩` or `...`; from then on the box shows only source or clearly-not-source marks. An invented line that happens to equal a line of the source range character for character is a coincidence: leave it as it is.
5. **Annotations go with their declaration.** An annotation is part of the declaration it sits on, so it appears in the stage that reveals that declaration: the node's own annotations, modifiers, kind (class, interface, object, …), and supertypes together at the declaration stage; a member's annotations with that member. If an annotation's arguments are long enough to be implementation, reveal its declaration part and leave those arguments as `...` until a later stage.
6. **Fold nested nodes.** A node whose `contains` lists other nodes keeps their code folded as `⟨<inner node name>⟩` in its own file until the last stage (each inner node has its own box).
7. **Keep the rest.** Anything not covered by rules 1–6 stays exactly as `begin` copied it.

## Reply

Run `build <result dir>`:

- Exit 2 (missing work file): the stderr line lists the paths. Copy each from the same node's file one stage earlier, apply that stage's rules, then build again.
- Exit 3: the source changed while you worked, or the script has a bug. Do not edit work files; tell the user the stderr line.
- Success: a node with nothing to change at some stage is normal — that stage simply shows no colored lines for it.

The chat response holds only:

📄 [<doc title>](<doc path>) — one line per document in `docs`

plus, only when they apply: one line per `skipped` node (`⚠️ <node>: <reason>`), and every `notices` line.

## Self-check

Before replying, confirm without narrating:

- The stage-1 prompt held nothing but the template, filled in — no source code, paths' contents, or facts read earlier — and the subagent read no file but the view.
- Every node keeps its view name in every stage.
- Every middle stage followed rules 1–7.
- The reply holds only the allowed lines.
