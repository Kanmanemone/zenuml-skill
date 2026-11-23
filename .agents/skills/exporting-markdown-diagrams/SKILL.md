---
name: exporting-markdown-diagrams
description: Export diagrams already embedded in Markdown to SVG, PNG, or PDF, or a whole Markdown document to PDF or PNG. Use for conversion or download requests, not for generating diagram content.
---

# Exporting Markdown Diagrams

Orchestrate the bundled scripts only. Never reinterpret, redraw, or approximate
the diagram/document with model reasoning.

## Workflow

1. Run `node scripts/read-settings.js` from this skill directory and use its
   resolved `values`. Add returned notices unchanged to the final response.
2. Identify the Markdown target, format, scope, and document layout from the
   request. A current-request value overrides settings.
3. Apply configured defaults. If anything remains unresolved, read
   [references/questions.md](references/questions.md) and ask all missing choices
   together.
4. Run exactly one matching export script and report its output path(s), not raw
   script output or rendered contents.

Never edit `settings.jsonc`. Conversion scripts read output directory, PNG
scale, and `render.theme` themselves, so do not pass those setting values
manually. Only when the request itself states the look, append
`--theme=vscode-light-plus` (as in the VS Code Light+ preview) or
`--theme=mermaid-default` (plain Mermaid rendering) to the script command.

## Request fields

- `targetFile`: an identifiable existing Markdown file. If none can be found,
  stop instead of guessing.
- `format`: `svg`, `png`, or `pdf` only when stated or resolved by settings.
- `scope`: `diagram` or `document` only when stated or resolved by settings.
- `pdfLayout`: `single` or `paginated`, required only for document scope.

Do not infer an unstated format, scope, or layout from unrelated context.

## Diagram-only export

Run:

```text
node scripts/export-diagrams.js <targetFile> <svg|png|pdf>
```

The script handles every diagram and its numbering. Even when the user names one
diagram, run the file once and point to the matching numbered output instead of
extracting it yourself.

Pass every diagram fence to the script unchanged, including YAML config,
`%%{init}%%`, and renderer directives. Never parse or reserialize it first.

## Whole-document export

Whole-document SVG is unsupported. Once format and layout are resolved, run one:

```text
node scripts/export-document-pdf.js <targetFile> "" --layout <single|paginated>
node scripts/export-document-png.js <targetFile> "" --layout <single|paginated>
```

Keep the empty output-position argument unless the user requested a specific
path. The scripts render all diagrams, keep diagram text as vector content in
PDF, open `<details>` while printing, and clean their intermediate files.

`single` produces one continuous page; `paginated` uses A4 pages. Document PNG
uses the same layout and turns each page into an image at configured scale:
`single` yields one image, while `paginated` yields numbered page images. A
document without diagrams remains valid.

## Failures

If the target is missing/not Markdown, diagram scope finds no diagram, the format
and scope conflict, or a tool/renderer fails, report the actual reason plainly.
Never switch format/layout, fabricate an approximation, or fall back to model
reasoning.
