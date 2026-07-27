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
- **`.zenuml/`** — created in your project root the first time you generate a diagram; that's where the output goes.

## How to use

> [!CAUTION]
> **Copy only the [`.claude/skills/generating-zenuml-diagrams/`](.claude/skills/generating-zenuml-diagrams/) folder — do NOT copy this whole project.**

1. Copy the [`.claude/skills/generating-zenuml-diagrams/`](.claude/skills/generating-zenuml-diagrams/) folder into your project's `.claude/skills/` directory.
2. In Claude Code, run `/generating-zenuml-diagrams <describe your process>`.

**Example:**

```text
/generating-zenuml-diagrams the client calls Server.getData()
```

**Skill not showing up when you type `/`?** Restart/reload Claude Code — in VS Code, open the Command Palette (`Ctrl+Shift+P`, or `Cmd+Shift+P` on Mac), type "Reload Window", and press Enter. Skills under `.claude/skills/` are scanned at session start, so one added mid-session won't appear until the next reload.

## How it was built

This skill went through the [Spec Kit](https://github.com/github/spec-kit) assess → specify → plan → tasks → implement → converge pipeline. The full trail is preserved:

- `.specify/assessments/zenuml-skill/` — intake, research, problem definition, concept, and the go/no-go decision that justified building this skill
- `specs/001-zenuml-diagram-skill/` — spec, implementation plan, research decisions, data model, interface contract, quickstart validation, and the task breakdown

## Requirements

- [Claude Code](https://claude.com/product/claude-code)
- No other dependencies — the skill is a self-contained Markdown bundle with no runtime code
