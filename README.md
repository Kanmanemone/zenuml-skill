# zenuml-skill

**Language:** English | [한국어 (Korean)](README.ko.md)

A Claude Code project containing `generating-zenuml-diagrams`, a skill that turns a natural-language description of a process into accurate, clean [ZenUML](https://github.com/mermaid-js/zenuml-core) sequence diagram DSL — without inventing participants, messages, or control flow that weren't actually described.

## What's in here

```text
.claude/skills/generating-zenuml-diagrams/
├── SKILL.md          # skill instructions
└── references/
    └── syntax.md     # syntax reference
```

- **SKILL.md** — Generation rules, examples, anti-fluff self-check, ambiguity handling
- **references/syntax.md** — ZenUML DSL grammar reference, adapted from mermaid-js/zenuml-core (MIT)
- **`.zenuml/`** — created in your project root the first time you generate a diagram; that's where the output goes. Asking to change a diagram you just got updates that same file in place (no new file); the full history of what changed and why is kept in `.zenuml/log/`.

## How to use

> [!CAUTION]
> **Copy only the [`.claude/skills/generating-zenuml-diagrams/`](.claude/skills/generating-zenuml-diagrams/) folder — do NOT copy this whole project.**

1. Copy the [`.claude/skills/generating-zenuml-diagrams/`](.claude/skills/generating-zenuml-diagrams/) folder into your project's `.claude/skills/` directory.
2. In Claude Code, run `/generating-zenuml-diagrams <describe your process>`.

**Example:**

```text
/generating-zenuml-diagrams the client calls Server.getData()
```

If a newly added skill doesn't show up under `/`, restart Claude Code, or run "Reload Window" from VS Code's Command Palette (`Ctrl+Shift+P`, `Cmd+Shift+P` on Mac) — skills are only scanned at session start.

## Optional add-ons

Copy these into your `.claude/skills/` directory alongside the core skill:

- **[`generating-architecture-views`](.claude/skills/generating-architecture-views/)** — adds a structural view (components, groups, dependencies). Want a specific Mermaid renderer (e.g. `elk`) for its Dependency diagrams? Say so in your request and it's added to the `%%{init}%%` block; leave it unspecified and it won't be.
- **[`exporting-markdown-diagrams`](.claude/skills/exporting-markdown-diagrams/)** — converts a diagram to SVG/PNG, or a whole Markdown file to PDF (diagrams embedded as selectable-text vectors), always through bundled scripts (mermaid-cli) — never LLM reasoning. Run `npm install` once inside its `scripts/` folder to fetch the dependencies those scripts use. Output lands in an `exports/` subdirectory next to the source file, created automatically.

## Development history

Built through the [Spec Kit](https://github.com/github/spec-kit) spec-driven development pipeline. The list below is in build order. Each feature's full spec/plan/tasks trail lives under `specs/`:

1. [`specs/001-zenuml-diagram-skill/`](specs/001-zenuml-diagram-skill/) — the core skill described above
2. [`specs/002-diagram-feedback-log/`](specs/002-diagram-feedback-log/) — regenerate a diagram in place and keep a log of what changed and why
3. [`specs/003-architecture-view-skill/`](specs/003-architecture-view-skill/) — a companion `generating-architecture-views` skill that adds a structural view (components, groups, dependencies) and can hand off into the sequence diagram above
4. [`specs/004-exporting-markdown-diagrams/`](specs/004-exporting-markdown-diagrams/) — a script-based `exporting-markdown-diagrams` skill that converts a diagram to SVG/PNG or a whole Markdown file to PDF (diagrams embedded as selectable-text vectors), collecting output into an `exports/` subdirectory next to the source file, with zero LLM inference in the conversion step itself

## Requirements

- [Claude Code](https://claude.com/product/claude-code)
- No other dependencies for `generating-zenuml-diagrams` / `generating-architecture-views` — those are self-contained Markdown bundles with no runtime code
- `exporting-markdown-diagrams` needs [Node.js](https://nodejs.org/) — its bundled scripts (`.claude/skills/exporting-markdown-diagrams/scripts/`) need `npm install` run once
