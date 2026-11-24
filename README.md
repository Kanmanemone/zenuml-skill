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
> **Install only the skill folders under [`.agents/skills/`](.agents/skills/) — do NOT copy this whole project.**

There are four skills; each works on its own, except that `revealing-code-step-by-step` reads the views `generating-architecture-views` makes. "Optional add-ons" below explains them in detail.

- **[`generating-zenuml-diagrams`](.agents/skills/generating-zenuml-diagrams/)** — Turns a process you describe in plain words into a [ZenUML](https://github.com/mermaid-js/zenuml-core) sequence diagram, without inventing participants or messages you didn't mention. Needs nothing else.
- **[`generating-architecture-views`](.agents/skills/generating-architecture-views/)** — Draws a structural view of a system — components, groups, dependencies — with each component's responsibility and links to its source. Uses Python 3.9+ (optional) for hover panels.
- **[`exporting-markdown-diagrams`](.agents/skills/exporting-markdown-diagrams/)** — Turns a diagram in a Markdown file into SVG/PNG, or the whole file into PDF/PNG, through bundled scripts. Needs Node.js; its npm packages are installed into its `scripts/` folder by the install command, or by the skill on first use.
- **[`revealing-code-step-by-step`](.agents/skills/revealing-code-step-by-step/)** — Walks through the code behind a structural view one layer at a time, from a plain-language situation to the original source. Needs Python 3.9+ and a view made by `generating-architecture-views`.

Install them either way below, then run one (see "Running a skill").

### Install by downloading and copying

1. Download [the repository as a ZIP](https://github.com/Kanmanemone/zenuml-skill/archive/refs/heads/main.zip) (or **Code → Download ZIP** on GitHub) and unzip it.
2. In the unzipped folder, open `.agents/skills/` and copy the folder of each skill you want — all four for everything — into your project's `.claude/skills/` (Claude Code) or `.agents/skills/` (Codex and other agents that read the [Agent Skills](https://agentskills.io) folder).
   - Folders whose names start with `.` are hidden in macOS Finder; press `Cmd+Shift+.` to show them.
   - Copy from `.agents/skills/`, not `.claude/skills/`: in this repository `.claude/skills/<name>` are links, which a ZIP doesn't keep.

### Install from the terminal

Paste one of the commands below in your project's root folder. Each downloads its skill(s) into `.agents/skills/` and links each from `.claude/skills/<name>`, so Claude Code and other agents read the same files — the same layout as this repository.

#### 1. All skills

**macOS / Linux**

```bash
t=; curl -fsSL -o z.tgz https://github.com/Kanmanemone/zenuml-skill/archive/refs/heads/main.tar.gz && mkdir -p .agents && t=$(mktemp -d .agents/zenuml-tmp.XXXXXX) && { tar -xzf z.tgz -C "$t" --strip-components=3 zenuml-skill-main/.agents/skills || { rm -rf "$t"; t=; }; }; rm -f z.tgz
if [ -n "$t" ]; then mkdir -p .agents/skills .claude/skills; for s in $(ls "$t"); do if [ -d .agents/skills/$s ]; then mkdir -p .agents/skills-backup && mv .agents/skills/$s .agents/skills-backup/$s-$(date +%Y%m%d%H%M%S); fi; mv "$t/$s" .agents/skills/$s && ln -sfn ../../.agents/skills/$s .claude/skills/$s; done; rm -rf "$t"; fi
if [ -d .agents/skills/exporting-markdown-diagrams/scripts ] && command -v npm >/dev/null; then npm ci --no-audit --no-fund --prefix .agents/skills/exporting-markdown-diagrams/scripts; fi
```

**Windows (PowerShell)**

```powershell
$t = $null; curl.exe -fsSL -o z.tgz https://github.com/Kanmanemone/zenuml-skill/archive/refs/heads/main.tar.gz; if ($?) { $t = (mkdir ".agents\zenuml-tmp-$(New-Guid)").FullName; tar -xzf z.tgz -C $t --strip-components=3 zenuml-skill-main/.agents/skills; if (!$?) { rmdir -Recurse $t; $t = $null }; del z.tgz }
if ($t) { mkdir -Force .agents\skills, .claude\skills >$null; foreach ($s in (dir $t -Directory).Name) { if (Test-Path .agents\skills\$s) { mkdir -Force .agents\skills-backup >$null; move .agents\skills\$s .agents\skills-backup\$s-$(Get-Date -f yyyyMMddHHmmss) }; move $t\$s .agents\skills\$s; cmd /c "rmdir .claude\skills\$s 2>nul & (mklink /D .claude\skills\$s ..\..\.agents\skills\$s 2>nul || mklink /J .claude\skills\$s .agents\skills\$s) >nul" }; rmdir -Recurse $t }
if ((Test-Path .agents\skills\exporting-markdown-diagrams\scripts) -and (Get-Command npm.cmd -ErrorAction SilentlyContinue)) { npm.cmd ci --no-audit --no-fund --prefix .agents\skills\exporting-markdown-diagrams\scripts }
```

#### 2. `generating-zenuml-diagrams`

**macOS / Linux**

```bash
t=; curl -fsSL -o z.tgz https://github.com/Kanmanemone/zenuml-skill/archive/refs/heads/main.tar.gz && mkdir -p .agents && t=$(mktemp -d .agents/zenuml-tmp.XXXXXX) && { tar -xzf z.tgz -C "$t" --strip-components=3 zenuml-skill-main/.agents/skills/generating-zenuml-diagrams || { rm -rf "$t"; t=; }; }; rm -f z.tgz
if [ -n "$t" ]; then mkdir -p .agents/skills .claude/skills; for s in $(ls "$t"); do if [ -d .agents/skills/$s ]; then mkdir -p .agents/skills-backup && mv .agents/skills/$s .agents/skills-backup/$s-$(date +%Y%m%d%H%M%S); fi; mv "$t/$s" .agents/skills/$s && ln -sfn ../../.agents/skills/$s .claude/skills/$s; done; rm -rf "$t"; fi
```

**Windows (PowerShell)**

```powershell
$t = $null; curl.exe -fsSL -o z.tgz https://github.com/Kanmanemone/zenuml-skill/archive/refs/heads/main.tar.gz; if ($?) { $t = (mkdir ".agents\zenuml-tmp-$(New-Guid)").FullName; tar -xzf z.tgz -C $t --strip-components=3 zenuml-skill-main/.agents/skills/generating-zenuml-diagrams; if (!$?) { rmdir -Recurse $t; $t = $null }; del z.tgz }
if ($t) { mkdir -Force .agents\skills, .claude\skills >$null; foreach ($s in (dir $t -Directory).Name) { if (Test-Path .agents\skills\$s) { mkdir -Force .agents\skills-backup >$null; move .agents\skills\$s .agents\skills-backup\$s-$(Get-Date -f yyyyMMddHHmmss) }; move $t\$s .agents\skills\$s; cmd /c "rmdir .claude\skills\$s 2>nul & (mklink /D .claude\skills\$s ..\..\.agents\skills\$s 2>nul || mklink /J .claude\skills\$s .agents\skills\$s) >nul" }; rmdir -Recurse $t }
```

#### 3. `generating-architecture-views`

**macOS / Linux**

```bash
t=; curl -fsSL -o z.tgz https://github.com/Kanmanemone/zenuml-skill/archive/refs/heads/main.tar.gz && mkdir -p .agents && t=$(mktemp -d .agents/zenuml-tmp.XXXXXX) && { tar -xzf z.tgz -C "$t" --strip-components=3 zenuml-skill-main/.agents/skills/generating-architecture-views || { rm -rf "$t"; t=; }; }; rm -f z.tgz
if [ -n "$t" ]; then mkdir -p .agents/skills .claude/skills; for s in $(ls "$t"); do if [ -d .agents/skills/$s ]; then mkdir -p .agents/skills-backup && mv .agents/skills/$s .agents/skills-backup/$s-$(date +%Y%m%d%H%M%S); fi; mv "$t/$s" .agents/skills/$s && ln -sfn ../../.agents/skills/$s .claude/skills/$s; done; rm -rf "$t"; fi
```

**Windows (PowerShell)**

```powershell
$t = $null; curl.exe -fsSL -o z.tgz https://github.com/Kanmanemone/zenuml-skill/archive/refs/heads/main.tar.gz; if ($?) { $t = (mkdir ".agents\zenuml-tmp-$(New-Guid)").FullName; tar -xzf z.tgz -C $t --strip-components=3 zenuml-skill-main/.agents/skills/generating-architecture-views; if (!$?) { rmdir -Recurse $t; $t = $null }; del z.tgz }
if ($t) { mkdir -Force .agents\skills, .claude\skills >$null; foreach ($s in (dir $t -Directory).Name) { if (Test-Path .agents\skills\$s) { mkdir -Force .agents\skills-backup >$null; move .agents\skills\$s .agents\skills-backup\$s-$(Get-Date -f yyyyMMddHHmmss) }; move $t\$s .agents\skills\$s; cmd /c "rmdir .claude\skills\$s 2>nul & (mklink /D .claude\skills\$s ..\..\.agents\skills\$s 2>nul || mklink /J .claude\skills\$s .agents\skills\$s) >nul" }; rmdir -Recurse $t }
```

#### 4. `exporting-markdown-diagrams`

**macOS / Linux**

```bash
t=; curl -fsSL -o z.tgz https://github.com/Kanmanemone/zenuml-skill/archive/refs/heads/main.tar.gz && mkdir -p .agents && t=$(mktemp -d .agents/zenuml-tmp.XXXXXX) && { tar -xzf z.tgz -C "$t" --strip-components=3 zenuml-skill-main/.agents/skills/exporting-markdown-diagrams || { rm -rf "$t"; t=; }; }; rm -f z.tgz
if [ -n "$t" ]; then mkdir -p .agents/skills .claude/skills; for s in $(ls "$t"); do if [ -d .agents/skills/$s ]; then mkdir -p .agents/skills-backup && mv .agents/skills/$s .agents/skills-backup/$s-$(date +%Y%m%d%H%M%S); fi; mv "$t/$s" .agents/skills/$s && ln -sfn ../../.agents/skills/$s .claude/skills/$s; done; rm -rf "$t"; fi
if [ -d .agents/skills/exporting-markdown-diagrams/scripts ] && command -v npm >/dev/null; then npm ci --no-audit --no-fund --prefix .agents/skills/exporting-markdown-diagrams/scripts; fi
```

**Windows (PowerShell)**

```powershell
$t = $null; curl.exe -fsSL -o z.tgz https://github.com/Kanmanemone/zenuml-skill/archive/refs/heads/main.tar.gz; if ($?) { $t = (mkdir ".agents\zenuml-tmp-$(New-Guid)").FullName; tar -xzf z.tgz -C $t --strip-components=3 zenuml-skill-main/.agents/skills/exporting-markdown-diagrams; if (!$?) { rmdir -Recurse $t; $t = $null }; del z.tgz }
if ($t) { mkdir -Force .agents\skills, .claude\skills >$null; foreach ($s in (dir $t -Directory).Name) { if (Test-Path .agents\skills\$s) { mkdir -Force .agents\skills-backup >$null; move .agents\skills\$s .agents\skills-backup\$s-$(Get-Date -f yyyyMMddHHmmss) }; move $t\$s .agents\skills\$s; cmd /c "rmdir .claude\skills\$s 2>nul & (mklink /D .claude\skills\$s ..\..\.agents\skills\$s 2>nul || mklink /J .claude\skills\$s .agents\skills\$s) >nul" }; rmdir -Recurse $t }
if ((Test-Path .agents\skills\exporting-markdown-diagrams\scripts) -and (Get-Command npm.cmd -ErrorAction SilentlyContinue)) { npm.cmd ci --no-audit --no-fund --prefix .agents\skills\exporting-markdown-diagrams\scripts }
```

#### 5. `revealing-code-step-by-step`

**macOS / Linux**

```bash
t=; curl -fsSL -o z.tgz https://github.com/Kanmanemone/zenuml-skill/archive/refs/heads/main.tar.gz && mkdir -p .agents && t=$(mktemp -d .agents/zenuml-tmp.XXXXXX) && { tar -xzf z.tgz -C "$t" --strip-components=3 zenuml-skill-main/.agents/skills/revealing-code-step-by-step || { rm -rf "$t"; t=; }; }; rm -f z.tgz
if [ -n "$t" ]; then mkdir -p .agents/skills .claude/skills; for s in $(ls "$t"); do if [ -d .agents/skills/$s ]; then mkdir -p .agents/skills-backup && mv .agents/skills/$s .agents/skills-backup/$s-$(date +%Y%m%d%H%M%S); fi; mv "$t/$s" .agents/skills/$s && ln -sfn ../../.agents/skills/$s .claude/skills/$s; done; rm -rf "$t"; fi
```

**Windows (PowerShell)**

```powershell
$t = $null; curl.exe -fsSL -o z.tgz https://github.com/Kanmanemone/zenuml-skill/archive/refs/heads/main.tar.gz; if ($?) { $t = (mkdir ".agents\zenuml-tmp-$(New-Guid)").FullName; tar -xzf z.tgz -C $t --strip-components=3 zenuml-skill-main/.agents/skills/revealing-code-step-by-step; if (!$?) { rmdir -Recurse $t; $t = $null }; del z.tgz }
if ($t) { mkdir -Force .agents\skills, .claude\skills >$null; foreach ($s in (dir $t -Directory).Name) { if (Test-Path .agents\skills\$s) { mkdir -Force .agents\skills-backup >$null; move .agents\skills\$s .agents\skills-backup\$s-$(Get-Date -f yyyyMMddHHmmss) }; move $t\$s .agents\skills\$s; cmd /c "rmdir .claude\skills\$s 2>nul & (mklink /D .claude\skills\$s ..\..\.agents\skills\$s 2>nul || mklink /J .claude\skills\$s .agents\skills\$s) >nul" }; rmdir -Recurse $t }
```

Each command does three things, so pasting it again is also how you update a skill:

1. It downloads the latest version and unpacks it into a temporary folder under `.agents/`. If either step fails, it stops without changing anything.
2. It moves the skill's current folder, if there is one, to `.agents/skills-backup/<name>-<date-time>`, then moves the fresh skill into `.agents/skills/<name>`, so files removed from this repository don't linger. Nothing is deleted: files you added to the skill folder and your `settings.jsonc` edits stay in that backup.
3. It links `.claude/skills/<name>` to that folder again.

- The all-skills command installs every skill the repository has at that moment, so a skill added later comes with the next update, while a skill later removed from this repository stays in your project until you delete it.
- After an update, copy any settings you changed back from the backup, and delete backups you no longer need. They sit outside `.agents/skills/`, so agents don't load them as duplicate skills.
- Updating `exporting-markdown-diagrams` moves its `node_modules` to the backup too; the update command installs them again when npm is available, and otherwise the skill does on first use.
- On Windows the command first tries a relative symbolic link (`mklink /D`), which needs Developer Mode or administrator rights. If that fails, it creates a directory junction (`mklink /J`) instead, which needs no permission but stores an absolute path, so after moving the project folder, paste the command again.

### Running a skill

In Claude Code, run `/generating-zenuml-diagrams <describe your process>`.

**Example:**

```text
/generating-zenuml-diagrams the client calls Server.getData()
```

If a newly added skill doesn't show up under `/`, restart Claude Code, or run "Reload Window" from VS Code's Command Palette (`Ctrl+Shift+P`, `Cmd+Shift+P` on Mac) — skills are only scanned at session start.

## Optional add-ons

Each of these is a standalone skill with its own install command in "How to use" (command 1 there installs them all). Every skill (including the core one) reads a `settings.jsonc` in its own folder; edit it to change how that skill behaves — each option is explained in Korean comments right above it:

- **[`generating-architecture-views`](.agents/skills/generating-architecture-views/)** — adds a structural view (components, groups, dependencies). Want a specific Mermaid renderer (e.g. `elk`) for its Dependency diagrams? Say so in your request and it's added as `layout` in the diagram's YAML `config` (or set `dependency.renderer` in the skill's `settings.jsonc`); leave it unspecified and it won't be. In VS Code's Markdown preview, hovering a node in the Dependency diagram shows that node's Responsibility and the collaborations it depends on in a panel — no scrolling back and forth. A bundled Python script fills these panels from the view's own text after it's saved, so this costs no extra tokens; choose what goes in the panel and where it appears (bottom of the preview or right under the node) with the `hover` group in `settings.jsonc`, or turn it off with `hover.enabled`. GitHub and other viewers don't support it.
- **[`exporting-markdown-diagrams`](.agents/skills/exporting-markdown-diagrams/)** — converts a diagram to SVG/PNG, or a whole Markdown file to PDF (diagrams embedded as selectable-text vectors) or PNG, always through bundled scripts (mermaid-cli) — never LLM reasoning. The npm packages those scripts use are installed into its `scripts/` folder from the lock file — by the install command when npm is available, otherwise by the skill on its first run, without asking. Output lands in an `exports/` subdirectory next to the source file, created automatically.
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

> You don't need any of this to use the skills as described in "How to use": its command downloads the real files, and on Windows, when it can't create a symbolic link, it falls back to a directory junction, which needs no permission.

## Requirements

- [Claude Code](https://claude.com/product/claude-code)
- No other dependencies for `generating-zenuml-diagrams` — it's a self-contained Markdown bundle with no runtime code
- `generating-architecture-views` uses [Python](https://www.python.org/) 3.9 or later already on your machine (found as `python3`, `python`, or `py -3`) for its node hover panels — the bundled script (`.agents/skills/generating-architecture-views/scripts/`) uses only the standard library, so there's nothing to install. Without Python, views are still generated, just without hover panels
- `revealing-code-step-by-step` needs [Python](https://www.python.org/) 3.9 or later on your machine for its bundled script (standard library only); without it, no documents are made. Sources whose block structure the script knows — brace languages (Kotlin, Java, Scala, Groovy, Swift, C#, Go, Rust, Dart, JavaScript, TypeScript, C, C++) and Python — are unfolded one layer at a time; a node that names its file (e.g. `colors.xml`) gets the whole file, shown right after the situation for markup, data files and other languages
- `exporting-markdown-diagrams` needs [Node.js](https://nodejs.org/) — its bundled scripts (`.agents/skills/exporting-markdown-diagrams/scripts/`) get their npm packages installed automatically (by the install command, or on first use)
