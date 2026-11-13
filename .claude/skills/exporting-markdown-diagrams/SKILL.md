---
name: exporting-markdown-diagrams
description: Converts a Mermaid/ZenUML diagram already embedded in a Markdown file to SVG or PNG, or converts a whole Markdown file (diagrams included) to PDF (diagrams embedded as selectable-text vector graphics) or to PNG — using bundled scripts only, never LLM reasoning, so output is deterministic and consistent across runs. Make sure to use this skill whenever the user asks to export, convert, save, download, or turn an existing diagram or Markdown document into an image or PDF file — including short asks like "이거 png로", "다이어그램 뽑아줘", "PDF로 만들어줘" — even if they don't spell out every detail; ask what's missing rather than skipping this skill. Do NOT use this to *generate* new diagram content — that is generating-zenuml-diagrams / generating-architecture-views's job. This skill only converts diagrams/documents that already exist.
---

# Exporting Markdown Diagrams

Converts a diagram embedded in a Markdown file to SVG/PNG/PDF, or a whole Markdown file to PDF or PNG. The conversion itself is always performed by a bundled script (`scripts/export-diagrams.js`, `scripts/export-document-pdf.js`, or `scripts/export-document-png.js`) — never by reasoning through the diagram/document content yourself. Your job here is orchestration only: work out what the user wants, ask only what's genuinely missing, then invoke the right script and report its output.

## Workflow overview

0. Read the settings (see "Settings" below).
1. Determine the target file, output format, and conversion scope from the request.
2. Fill whatever is missing from the settings' defaults, or ask — via a single `AskUserQuestion` call — for exactly the pieces still missing (see "Step 2").
3. Dispatch to the script matching the confirmed scope (see "Scope: diagram-only" / "Scope: whole document" below).
4. Report the resulting file path(s). Never paste the script's raw output or a diagram's rendered content into the chat.

## Settings

Before anything else in each run, from this skill's directory run:

```text
node scripts/read-settings.js
```

It prints one line of JSON: `values` (every option resolved from `settings.schema.json` and the user's `settings.jsonc` — missing file or keys fall back to defaults, invalid values fall back per key, unknown keys are ignored) and `notices`. Use `values` for the conversation decisions below. Put each string in `notices`, unchanged, on its own line at the end of the chat response — never anywhere else, and don't add other remarks about settings. Never edit `settings.jsonc` yourself. The conversion scripts read the same settings on their own (output location, PNG scale), so don't pass those values to them.

A value the user states in the request always wins over the settings for that request.

## Step 1 — Determine the request

From the user's message, work out three things:

- **targetFile**: the Markdown file to convert. If it can't be identified (no path given, no file matching a description found), say so and stop — don't guess a file.
- **format**: `svg` | `png` | `pdf`, only if the user's wording actually names one (e.g. "png로", "SVG로 뽑아줘", "PDF 파일로"). Don't infer a format from context that doesn't name one.
- **scope**: `diagram` (다이어그램만) | `document` (문서 전체), only if the wording actually distinguishes them (e.g. "이 다이어그램만" implies `diagram`; "문서 전체를"/"파일을 통째로" implies `document`). A bare "이거 변환해줘" with no such wording is unresolved, not defaulted.
- **pdfLayout** (only meaningful when `scope` is `document`): `single` (1페이지 단일) | `paginated` (표준 인쇄 규격), only if the wording actually names one (e.g. "한 페이지로", "안 잘리게" implies `single`; "인쇄용으로", "페이지 나눠서" implies `paginated`). Leave unresolved otherwise — never infer it from `scope`/`format` wording alone.

## Step 2 — Clarify missing details

Ask only for what's actually missing — never re-ask something already implied by the request. The settings decide how a missing piece gets resolved (`values` from "Settings"):

- **`questions.enabled` is `false`**: don't ask. Fill each missing piece from its default — `defaults.format` for format, `defaults.scope` for scope, `defaults.pdfLayout` for pdfLayout — then apply the rules below as if the user had said it. Only a piece whose default is `none` (nothing to fill it with) is still asked, using the rules below, without any " (기본값)" mark.
- **`questions.enabled` is `true`**: ask exactly as below. In every question, append ` (기본값)` to the end of the `label` of the option that matches that question's default (`defaults.format` → `SVG`/`PNG`/`PDF` for `svg`/`png`/`pdf`; `defaults.scope` → `다이어그램만`/`문서 전체` for `diagram`/`document`; `defaults.pdfLayout` → `1페이지 단일`/`표준 인쇄 규격` for `single`/`paginated`). Which option gets it comes only from the settings; when the default is `none`, no option gets it. Never move or reorder options to mark the default.

`scope=document` produces PDF or PNG only — there is no whole-document SVG (see "Scope: whole document" below) — which changes how `format` factors in:

- **`scope` resolves to `document` and the request named `pdf` or `png`**: use it.
- **`scope` resolves to `document` and the request named `svg`**: don't silently substitute another format. Tell the user whole-document SVG isn't supported, then ask a single format question with only `PDF` and `PNG`.
- **`scope` resolves to `document` and no format was named**: if questions are off and `defaults.format` is `pdf` or `png`, use it. Otherwise (questions on, or `defaults.format` is `svg`/`none`) ask a single format question with only `PDF` and `PNG` — mark ` (기본값)` only when `defaults.format` is `pdf` or `png`.
- **Otherwise** (`scope` is `diagram`, or still unresolved), fall back to the general rule:
  - **Both `format` and `scope` missing**: make a single `AskUserQuestion` call whose `questions` array has exactly two entries — one for format, one for scope — presented together in one interaction. Never split this into two separate `AskUserQuestion` calls.
  - **Only `format` missing**: ask a single question for format alone.
  - **Only `scope` missing**: ask a single question for scope alone. If the answer is `문서 전체`, apply the `document`-scope rules above (the format already named still applies; `svg` gets the not-supported notice and a PDF/PNG question).
  - **Neither missing**: skip straight to dispatch — no question at all.

Format question — options `SVG`, `PNG`, `PDF` (only `PDF`, `PNG` once `scope` is `document`). Scope question — options `다이어그램만`, `문서 전체`. When format and scope are asked together and the user might pick `문서 전체`, you may note in the scope option's description that whole-document export produces PDF or PNG — but still let the user pick freely; the only marking is the settings-driven " (기본값)" above. If they end up with `문서 전체` + `SVG`, apply the `svg` rule above.

```text
예시 — 형식·범위 둘 다 불분명한 "이거 변환해줘"에 대한 AskUserQuestion:
  questions: [
    { header: "출력 형식", question: "어떤 형식으로 변환할까요?", options: [SVG, PNG, PDF] },
    { header: "변환 범위", question: "다이어그램만 변환할까요, 문서 전체를 변환할까요?", options: [다이어그램만, 문서 전체] }
  ]
```

```text
예시 — 같은 요청에서 questions.enabled=true, defaults.format="png", defaults.scope="none"일 때:
  questions: [
    { header: "출력 형식", question: "어떤 형식으로 변환할까요?", options: [SVG, PNG (기본값), PDF] },
    { header: "변환 범위", question: "다이어그램만 변환할까요, 문서 전체를 변환할까요?", options: [다이어그램만, 문서 전체] }
  ]
```

**Page layout for `scope=document`** (applies to both PDF and PNG): once `scope` is confirmed as `document` (whether it was given outright, resolved from the question above, or filled from `defaults.scope`) and `pdfLayout` is still unresolved (not in the request, and not filled from `defaults.pdfLayout` because questions are off), ask one more, separate `AskUserQuestion` — a follow-up round after the format/scope interaction, not folded into it — with options in this exact order: `1페이지 단일` first, `표준 인쇄 규격` second. Skip this question entirely when `scope` resolves to `diagram` — page layout has no meaning for a diagram-only export.

```text
예시 — scope=document가 확정된 뒤 pdfLayout이 아직 불분명할 때의 후속 AskUserQuestion:
  questions: [
    { header: "페이지 구성", question: "페이지를 어떻게 나눌까요?", options: [
      { label: "1페이지 단일", description: "페이지 나눔 없이 문서 전체를 한 장(PNG면 세로로 긴 이미지 한 장)에 담습니다." },
      { label: "표준 인쇄 규격", description: "A4 용지 크기로 필요한 만큼 나눕니다(PNG면 페이지마다 이미지 한 장)." }
    ] }
  ]
```

## Renderer preservation

The diagram source (everything inside its code fence, including any `%%{init: ...}%%` renderer directive such as `defaultRenderer`) is passed to the script **exactly as written** — never parsed, rewritten, or re-serialized by you first. Don't add logic here to detect or branch on renderer directives; the bundled script hands the raw source straight to the renderer, which is what makes preserving them automatic rather than something to implement.

## Failure handling

If the target file doesn't exist, isn't Markdown, contains no diagram when `scope=diagram` was requested, or the script itself fails (missing tool, renderer error, unsupported diagram syntax), report that failure to the user plainly — quote what the script/tool reported. Never paper over a failure by generating a description or approximation of what the output "would have looked like." A failed conversion stays failed; it does not silently fall back to LLM reasoning.

## Scope: diagram-only

Once `targetFile`, `format`, and `scope=diagram` are all confirmed, run:

```text
node scripts/export-diagrams.js <targetFile> <format>
```

This handles every diagram in the file on its own — if the file has more than one, the script (via `mmdc`) numbers and converts each one; you don't need to locate or split diagrams yourself, and you don't need a separate code path for a single-diagram vs. multi-diagram file. If the user named a specific diagram, still run the script over the whole file and then point to the matching numbered output rather than trying to extract just that one diagram beforehand.

On success, the script prints one output file path per line — report those paths back to the user (a short prose line or list, not a code dump of their contents). On failure, it exits non-zero and prints the reason to stderr — follow "Failure handling" above.

## Scope: whole document

Once `targetFile`, `scope=document`, `format` (`pdf` or `png`), and `pdfLayout` are all confirmed (see "Step 2" above), run the matching script:

```text
node scripts/export-document-pdf.js <targetFile> "" --layout <single|paginated>   # format=pdf
node scripts/export-document-png.js <targetFile> "" --layout <single|paginated>   # format=png
```

(The empty `""` positional keeps the script's default output naming in the `output.directory` setting's location — pass a real path there only if the user asked for a specific output location.)

This script extracts every diagram in the document, embeds it back into the printed PDF as a real vector `<svg>` (not a linked image or a rasterized picture), and cleans up its own intermediate files — you don't need to manage temp files or call any other script for this scope. `single` prints the whole document onto one continuously tall page (no page breaks); `paginated` prints onto standard A4 pages, flowing content across as many as it needs. Collapsible `<details>` blocks are always printed open, so their content is never hidden in the PDF; the source file isn't changed. On success, it prints the PDF's path — report that back to the user. On failure, follow "Failure handling" above.

The PNG script renders the document exactly as the PDF script would (same layout, fonts, and page breaks, collapsible blocks open) and then turns each page into a PNG at the `png.scale` resolution: `single` gives one tall image `<name>.png`; `paginated` gives `<name>-page-1.png`, `<name>-page-2.png`, … — one per A4 page. A document with no diagrams is fine for either script. On success it prints one path per line — report them back. If an image can't be produced (e.g. a very long document is too tall for one `single` image), it fails with the reason — report that as is under "Failure handling"; never switch to another format or layout on your own.
