# zenuml-skill

**Language:** English | [한국어 (Korean)](README.ko.md)

A Claude Code project containing `generating-zenuml-diagrams`, a skill that turns a natural-language description of a process into accurate, clean [ZenUML](https://github.com/mermaid-js/zenuml-core) sequence diagram DSL — without inventing participants, messages, or control flow that weren't actually described.

## What's in here

```text
.agents/skills/generating-zenuml-diagrams/
├── SKILL.md          # skill instructions
└── references/
    └── syntax.md     # syntax reference
```

- **SKILL.md** — Generation rules, examples, anti-fluff self-check, ambiguity handling
- **references/syntax.md** — ZenUML DSL grammar reference, adapted from mermaid-js/zenuml-core (MIT)
- **`.zenuml/`** — created in your project root the first time you generate a diagram; that's where the output goes. Asking to change a diagram you just got updates that same file in place (no new file); the full history of what changed and why is kept in `.zenuml/log/`.

## How to use

> [!CAUTION]
> **Copy only the [`.agents/skills/generating-zenuml-diagrams/`](.agents/skills/generating-zenuml-diagrams/) folder — do NOT copy this whole project.**

1. Copy the [`.agents/skills/generating-zenuml-diagrams/`](.agents/skills/generating-zenuml-diagrams/) folder into your project's `.claude/skills/` directory (Claude Code), or `.agents/skills/` for Codex and other agents that read the [Agent Skills](https://agentskills.io) folder. In this repository the skills live in `.agents/skills/`, and `.claude/skills/<name>` are symlinks to them.
2. In Claude Code, run `/generating-zenuml-diagrams <describe your process>`.

**Example:**

```text
/generating-zenuml-diagrams the client calls Server.getData()
```

If a newly added skill doesn't show up under `/`, restart Claude Code, or run "Reload Window" from VS Code's Command Palette (`Ctrl+Shift+P`, `Cmd+Shift+P` on Mac) — skills are only scanned at session start.

## Optional add-ons

Each of these is a standalone skill — copy whichever you need into your `.claude/skills/` directory. Every skill (including the core one) reads a `settings.jsonc` in its own folder; edit it to change how that skill behaves — each option is explained in Korean comments right above it:

- **[`generating-architecture-views`](.agents/skills/generating-architecture-views/)** — adds a structural view (components, groups, dependencies). Want a specific Mermaid renderer (e.g. `elk`) for its Dependency diagrams? Say so in your request and it's added as `layout` in the diagram's YAML `config` (or set `dependency.renderer` in the skill's `settings.jsonc`); leave it unspecified and it won't be. In VS Code's Markdown preview, hovering a node in the Dependency diagram shows that node's Responsibility and the collaborations it depends on in a panel — no scrolling back and forth. A bundled Python script fills these panels from the view's own text after it's saved, so this costs no extra tokens; choose what goes in the panel and where it appears (bottom of the preview or right under the node) with the `hover` group in `settings.jsonc`, or turn it off with `hover.enabled`. GitHub and other viewers don't support it.
- **[`exporting-markdown-diagrams`](.agents/skills/exporting-markdown-diagrams/)** — converts a diagram to SVG/PNG, or a whole Markdown file to PDF (diagrams embedded as selectable-text vectors) or PNG, always through bundled scripts (mermaid-cli) — never LLM reasoning. Run `npm install` once inside its `scripts/` folder to fetch the dependencies those scripts use. Output lands in an `exports/` subdirectory next to the source file, created automatically.
- **[`revealing-code-step-by-step`](.agents/skills/revealing-code-step-by-step/)** — **requires a structural view made by `generating-architecture-views` first** (`.zenuml/<slug>.architecture.md`): it reads the view's nodes, source links, and Responsibility/Collaboration, so run that skill before this one. It takes the view and builds documents where each node's source code can be paged through *refinement steps*: a plain-language situation under the node's fixed responsibility line, then an outline showing every step as a numbered placeholder (inner steps indented under the one that holds them), then the source unfolded one layer at a time, so a call with several nested lambdas never lands in one scene. The script splits the source into a scope tree, prints each line once, and builds every code scene, so the agent only writes, scope by scope from the innermost, a purpose sentence and which children open together; the first situation is written by an isolated subagent. In VS Code's Markdown preview each node gets one box you flip with ← →; lines that changed from the previous step are colored like VS Code's git gutter (green added, blue changed, red triangle deleted) while syntax highlighting stays. The steps themselves live in the skill's `stages.md`, which also records how to change them without spending more tokens; `settings.jsonc` turns individual steps on or off (`stages`) and sets where the documents go (`output.directory`). GitHub and other viewers show every step in order instead of paging.

## Development

Each feature's spec/plan/tasks trail lives under [`specs/`](specs/).

### Skill folder layout

The skills live in [`.agents/skills/`](.agents/skills/) — the Agent Skills standard folder, which Codex and other agents read directly — and each `.claude/skills/<name>` is a symlink to it. When you change a skill, edit it under `.agents/skills/`.

### Cloning on Windows

Creating symlinks on Windows needs a permission. Without the setup below, `.claude/skills/<name>` checks out as a one-line text file holding the target path, and the skills don't show up in Claude Code (agents that read `.agents/skills`, such as Codex, are unaffected).

1. Turn on Developer Mode: Settings → System → For developers → Developer Mode. (Alternatively, run Git as Administrator.)
2. Clone with symlinks enabled:

   ```bash
   git clone -c core.symlinks=true https://github.com/Kanmanemone/zenuml-skill.git
   ```

   Git for Windows may turn symlink support on by itself once it detects Developer Mode, but passing `-c core.symlinks=true` makes sure.

Already cloned? Inside the repository run:

```bash
git config core.symlinks true
git checkout -- .claude/skills
```

Check: each skill name under `.claude/skills/` should open as a folder (a link) containing `SKILL.md`.

> You don't need any of this to use a single skill as described in "How to use": copying a folder from `.agents/skills/<name>` copies the real files.

## Requirements

- [Claude Code](https://claude.com/product/claude-code)
- No other dependencies for `generating-zenuml-diagrams` — it's a self-contained Markdown bundle with no runtime code
- `generating-architecture-views` uses [Python](https://www.python.org/) 3.9 or later already on your machine (found as `python3`, `python`, or `py -3`) for its node hover panels — the bundled script (`.agents/skills/generating-architecture-views/scripts/`) uses only the standard library, so there's nothing to install. Without Python, views are still generated, just without hover panels
- `revealing-code-step-by-step` needs [Python](https://www.python.org/) 3.9 or later on your machine for its bundled script (standard library only); without it, no documents are made. Kotlin sources are unfolded one layer at a time; in any language, a node that names its file (e.g. `colors.xml`) gets the whole file — shown right after the situation when it isn't Kotlin
- `exporting-markdown-diagrams` needs [Node.js](https://nodejs.org/) — its bundled scripts (`.agents/skills/exporting-markdown-diagrams/scripts/`) need `npm install` run once
