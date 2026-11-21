---
name: generating-architecture-views
description: Generate an evidence-based structural view of components, responsibilities, and actual dependencies from a natural-language system description. Use for architecture or component-relationship questions, not runtime sequence or call-order diagrams.
---

# Generating Architecture Views

Produce one architecture-view Markdown file and reply with its link. Do not add
follow-up offers or unrelated artifacts.

## Workflow

1. Run `scripts/read_settings.py` and use its resolved `values`.
2. Classify purpose, static/dynamic kind, and initial/regeneration/colliding slug.
3. Read [references/templates.md](references/templates.md), then generate
   Dependency, Responsibility, and Collaboration from stated evidence only.
4. Check the result against "Evidence and checks" below.
5. Save, format, log, and apply hover in the order under "Saving".

Read [references/examples.md](references/examples.md) only when the templates do
not settle an unusual grouping, link, or consolidation case.

## Scripts and settings

Run scripts from the project root by full path without changing directory. Find
Python 3.9+ once per run: on Windows try `python`, `py -3`, `python3`; elsewhere
try `python3`, `python`, `py -3`.

Run `read_settings.py` fresh on every request. Never read or edit
`settings.jsonc` or `settings.schema.json` yourself. If Python or the script is
unavailable, read only schema defaults and add
`⚙️ 설정 안내: settings.jsonc 설정 스크립트를 실행하지 못해 모든 값을 기본값으로 사용`.
Collect script notice lines without duplicates for the final response.

A value stated in the current request overrides the matching setting for that
request only. Earlier request overrides do not carry into regeneration.

## Classification

### Purpose

Use an explicit or clearly implied purpose. Ask only when it is genuinely
unclear: onboarding, troubleshooting, or another purpose the user describes.
An ambiguous or absent answer defaults to onboarding with a short notice. If no
components are identifiable, ask which system or process to show instead.

Purpose does not change the three output sections.

### Static or dynamic

- Dynamic: the request asks what a commit, PR, diff, or refactor added, changed,
  or removed. Mark only changes the description identifies.
- Static: every other request. Do not add change marks.

Decide without asking unless the intended kind is genuinely ambiguous.

### File request

- A follow-up refining the view just shown regenerates and overwrites that view.
- A self-contained new request creates a new slug.
- An unrelated request colliding with an existing slug uses `-2`, `-3`, etc.
- If conversation context cannot distinguish these, ask before writing.

## Evidence and links

Use only components, groups, dependencies, responsibilities, changes, and source
locations the description states or clearly implies. Never add structure to make
the result feel complete. A chain A→B→C stays two edges, never an A→C shortcut.

Create a group only from an explicit layer/domain or a shared
name-prefix/namespace signal. Without a grouping signal, draw no `subgraph`.

Keep these source facts separate: base name, original declaration keyword(s),
final file extension, and whether the declaration is a function. Never infer
them from a language keyword or extension list. Apply the three
`dependency.nodeNameFormat` booleans independently:

- `declarationMarkers`: verified original keyword(s), only for declarations
  inside a file.
- `fileExtensions`: verified final extension, only when the node is the file.
- `functionParentheses`: `()` exactly once, only for a verified function.

Their shipped defaults are `false`, `true`, and `true`.

These settings change Dependency labels only. IDs, link targets, hover content,
and Responsibility/Collaboration names remain unchanged.

Resolve a link once and reuse it everywhere that name heads an entry:

1. A stated or clearly implied local path, relative to `.zenuml/`; groups use an
   evident common parent folder.
2. A stated repository URL; groups use the folder URL.
3. Otherwise plain text. Never fabricate a path or URL and never search the
   codebase merely to discover one.

When actual code is available, first inspect it and distill a natural-language
description with concrete paths, identifiers, declarations, and relationships;
then generate from that evidence.

## Sections

The exact Mermaid and prose shapes live in
[references/templates.md](references/templates.md). Preserve these invariants:

- Dependency always appears and has exactly one plain caption derived only from
  request keywords.
- A hidden Responsibility or Collaboration setting removes that section.
- Every visible group and element has both responsibility levels, using the
  specified unknown phrase when evidence is absent.
- Collaboration includes only directly connected element pairs and group pairs
  with a crossing edge. Direction, consolidation thresholds, nested fields, and
  optional questions follow the template.
- Every bold field/name uses `<strong>`, and every code identifier is backticked.
- Do not truncate long sections or invent components to reduce their size.

## Evidence and checks

Before saving, fix every violation:

1. No invented component, group, dependency, responsibility, change, or link.
2. Diagram is the basic form expected by `build_diagram.py`; no generated config,
   edge IDs, color classes, comments, or CRUD definitions were handwritten.
3. Static views have no change marks; dynamic views mark exactly stated changes.
4. Node-name settings affect only their verified fact and only Dependency labels.
5. Responsibility covers every visible group/element; consolidation meets its
   template condition.
6. Collaboration contains only real connected pairs, correct direction and
   required nested fields, with no duplicate pair.
7. All repeated names reuse the same resolved link; the caption is unique.
8. Section display settings, request classification, and allowed response content
   match this request.
9. The result is structural, not a runtime sequence or call-order diagram.

## Output file

Write `.zenuml/<slug>.architecture.md` with, in order, `### Dependency` and each
visible `### Responsibility` / `### Collaboration` section. Their plain,
collapsed, and expanded forms follow the template. Apart from section content
and script additions, add no renderer notes, layout explanations, warnings, or
other meta commentary.

With filesystem access, the chat response contains only:

- the relative file link;
- a necessary clarification;
- the onboarding-default notice;
- collected script notices or skip/failure notices.

Without filesystem access, return the three sections directly and skip saving.

## Saving

For a completed view, in this order:

1. Write `.zenuml/<slug>.architecture.md`.
2. Run `build_diagram.py <view>`; add `--layout=<value>` only when this request
   names a renderer. On failure, keep the basic view and report the prescribed
   `⚙️ 다이어그램 서식 건너뜀: <reason>` line.
3. Write only the relevant-turn request summary to a temporary UTF-8 text file.
   Resolve the log as `<log.directory>/<slug>.architecture.md`, then run
   `append_feedback.py <view> <resolved log path> <request file>
   --mode=<new|append>`. Use `new` for initial/colliding requests and `append`
   for regeneration; the helper starts Round 1 when the current log is absent.
   It consumes the request file and copies the saved view, so never rewrite the
   view into the log yourself on success. If it fails, read
   [references/feedback-log.md](references/feedback-log.md) and preserve the
   same log manually.
4. When hover is enabled and either hover content list is non-empty, run
   `apply_hover.py <view>` with only current-request overrides. It copies content
   from the saved sections; never write panel text yourself. A hover-only refresh
   runs this script without regeneration or a log round.
5. Reply with the file link and allowed notices.

The log captures the file after diagram formatting and before hover injection.
Changing `log.directory` never moves old logs; regeneration at a new location
starts Round 1 there.

For hover overrides, pass only values the current request states: `--enabled`,
`--responsibility`, `--collaboration`, or `--position`. A request for questions
in hover also enables `collaboration.questions` for that request because hover
can only copy questions present in the body. If Python is absent or hover fails,
keep the formatted view and report one `⚙️ hover 건너뜀: <reason>` line.

## Out of scope

- Runtime sequence, call-order, or behavior-flow diagrams.
- Class, deployment, or other structural diagram types outside Dependency,
  Responsibility, and Collaboration.
- Comparisons between concepts not identified as groups or elements.

State the boundary briefly without proposing a workaround or another artifact.
