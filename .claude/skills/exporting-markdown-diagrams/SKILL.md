---
name: exporting-markdown-diagrams
description: Converts a Mermaid/ZenUML diagram already embedded in a Markdown file to SVG or PNG, or converts a whole Markdown file (diagrams included) to PDF with those diagrams embedded as selectable-text vector graphics — using bundled scripts only, never LLM reasoning, so output is deterministic and consistent across runs. Make sure to use this skill whenever the user asks to export, convert, save, download, or turn an existing diagram or Markdown document into an image or PDF file — including short asks like "이거 png로", "다이어그램 뽑아줘", "PDF로 만들어줘" — even if they don't spell out every detail; ask what's missing rather than skipping this skill. Do NOT use this to *generate* new diagram content — that is generating-zenuml-diagrams / generating-architecture-views's job. This skill only converts diagrams/documents that already exist.
---

# Exporting Markdown Diagrams

Converts a diagram embedded in a Markdown file to SVG/PNG, or a whole Markdown file to PDF. The conversion itself is always performed by a bundled script (`scripts/export-diagrams.js` or `scripts/export-document-pdf.js`) — never by reasoning through the diagram/document content yourself. Your job here is orchestration only: work out what the user wants, ask only what's genuinely missing, then invoke the right script and report its output.

## Workflow overview

1. Determine the target file, output format, and conversion scope from the request.
2. If format and/or scope are missing, ask — via a single `AskUserQuestion` call — for exactly the missing piece(s).
3. Dispatch to the script matching the confirmed scope (see "Scope: diagram-only" / "Scope: whole document" below).
4. Report the resulting file path(s). Never paste the script's raw output or a diagram's rendered content into the chat.

## Step 1 — Determine the request

From the user's message, work out three things:

- **targetFile**: the Markdown file to convert. If it can't be identified (no path given, no file matching a description found), say so and stop — don't guess a file.
- **format**: `svg` | `png` | `pdf`, only if the user's wording actually names one (e.g. "png로", "SVG로 뽑아줘", "PDF 파일로"). Don't infer a format from context that doesn't name one.
- **scope**: `diagram` (다이어그램만) | `document` (문서 전체), only if the wording actually distinguishes them (e.g. "이 다이어그램만" implies `diagram`; "문서 전체를"/"파일을 통째로" implies `document`). A bare "이거 변환해줘" with no such wording is unresolved, not defaulted.
- **pdfLayout** (only meaningful when `scope` is `document`): `single` (1페이지 단일) | `paginated` (표준 인쇄 규격), only if the wording actually names one (e.g. "한 페이지로", "안 잘리게" implies `single`; "인쇄용으로", "페이지 나눠서" implies `paginated`). Leave unresolved otherwise — never infer it from `scope`/`format` wording alone.

## Step 2 — Clarify missing details

Ask only for what's actually missing — never re-ask something already implied by the request.

`scope=document` only ever produces PDF (see "Scope: whole document" below — no other script exists for this scope), which changes how `format` factors in:

- **`scope` resolves to `document`** (given, or the user answers `문서 전체` to the scope question) **and no format was named, or `pdf` was named**: treat `format` as `pdf` automatically — never ask a separate format question for this scope.
- **`scope` resolves to `document` but the user explicitly named a different format** (e.g. "문서 전체를 png로"): don't silently substitute PDF for what they asked. Tell them whole-document export only produces PDF today, and ask whether PDF is acceptable instead — a single format-only question — rather than proceeding with a combination nothing implements.
- **Otherwise** (`scope` is `diagram`, or still unresolved), fall back to the general rule:
  - **Both `format` and `scope` missing**: make a single `AskUserQuestion` call whose `questions` array has exactly two entries — one for format, one for scope — presented together in one interaction. Never split this into two separate `AskUserQuestion` calls.
  - **Only `format` missing**: ask a single question for format alone.
  - **Only `scope` missing**: ask a single question for scope alone. If the answer is `문서 전체`, apply the `document`-scope rule above (format becomes `pdf`, no follow-up question).
  - **Neither missing**: skip straight to dispatch — no question at all.

Format question — options `SVG`, `PNG`, `PDF`. Scope question — options `다이어그램만`, `문서 전체`. When `scope` is still being asked and the request already leans toward a whole-file conversion (e.g. mentions "문서"), you may note in the option's description that whole-document export produces PDF — but still let the user pick freely; never pre-select for them.

```text
예시 — 형식·범위 둘 다 불분명한 "이거 변환해줘"에 대한 AskUserQuestion:
  questions: [
    { header: "출력 형식", question: "어떤 형식으로 변환할까요?", options: [SVG, PNG, PDF] },
    { header: "변환 범위", question: "다이어그램만 변환할까요, 문서 전체를 변환할까요?", options: [다이어그램만, 문서 전체] }
  ]
```

**Page layout for `scope=document`**: once `scope` is confirmed as `document` (whether it was given outright or just resolved from the question above) and `pdfLayout` is still unresolved, ask one more, separate `AskUserQuestion` — a follow-up round after the format/scope interaction, not folded into it — with options in this exact order: `1페이지 단일` first, `표준 인쇄 규격` second. Skip this question entirely when `scope` resolves to `diagram` — page layout has no meaning for a diagram-only export.

```text
예시 — scope=document가 확정된 뒤 pdfLayout이 아직 불분명할 때의 후속 AskUserQuestion:
  questions: [
    { header: "PDF 페이지 구성", question: "PDF 페이지를 어떻게 만들까요?", options: [
      { label: "1페이지 단일", description: "페이지 나눔 없이 문서 전체를 한 장에 담습니다." },
      { label: "표준 인쇄 규격", description: "A4 등 표준 용지 크기로 필요한 만큼 여러 페이지에 나눠 인쇄합니다(지금까지의 기본 방식)." }
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

Once `targetFile`, `scope=document` (format is always `pdf` for this scope), and `pdfLayout` are all confirmed (see "Step 2" above), run:

```text
node scripts/export-document-pdf.js <targetFile> "" --layout <single|paginated>
```

(The empty `""` positional keeps the script's default `exports/`-based output naming — pass a real path there only if the user asked for a specific output location.)

This script extracts every diagram in the document, embeds it back into the printed PDF as a real vector `<svg>` (not a linked image or a rasterized picture), and cleans up its own intermediate files — you don't need to manage temp files or call any other script for this scope. `single` prints the whole document onto one continuously tall page (no page breaks); `paginated` prints onto standard A4 pages, flowing content across as many as it needs. On success, it prints the PDF's path — report that back to the user. On failure, follow "Failure handling" above.
