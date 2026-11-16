// Whole-document Markdown -> PDF pipeline, shared by export-document-pdf.js and
// export-document-png.js (which rasterizes this PDF, so both formats share one rendering).
// Deterministic — never reasons about the document/diagram content.
//
// Pipeline (see 004 research.md, "User Story 2 파이프라인" Decision):
//   1. mermaid-cli extracts each diagram to its own SVG file and rewrites the Markdown's
//      diagram code fences into image references pointing at those files.
//   2. That intermediate Markdown is rendered to HTML, the SVG image references are inlined
//      as literal <svg> markup (mermaid-cli's own PDF output uses this exact DOM-<svg>-then-
//      page.pdf() path, which is why it's the verified way to keep diagrams as real vectors),
//      and the result is printed to PDF via a headless browser.

import path from "node:path";
import fs from "node:fs";
import os from "node:os";
import MarkdownIt from "markdown-it";
import { runMmdc } from "./run-mmdc.js";
import { inlineSvgImages } from "./inline-svg.js";
import { fitSvgFile } from "./fit-svg.js";

// Sourced verbatim from VS Code's own Markdown preview stylesheet — not a hand-picked
// stack — so the PDF's body/code text matches what VS Code's Markdown preview actually
// renders, rather than headless Chromium's generic "sans-serif"/"monospace" substitute
// (<VS Code install>/resources/app/extensions/markdown-language-features/media/
// markdown.css, `html, body` and `code` rules). Those rules read
// `var(--markdown-font-family, <fallback>)` / `var(--vscode-editor-font-family,
// <fallback>)` — VS Code injects the resolved `markdown.preview.fontFamily` /
// `editor.fontFamily` setting into those custom properties, so what's actually
// rendered is that setting's value if customized, or this exact fallback list
// otherwise (confirmed against `markdown.preview.fontFamily`'s own schema default,
// which matches the body fallback verbatim). We have no such settings/CSS vars here,
// so we use the fallback list directly — the same list VS Code falls back to.
const BODY_FONT_STACK =
  '-apple-system, BlinkMacSystemFont, "Segoe WPC", "Segoe UI", system-ui, "Ubuntu", "Droid Sans", sans-serif';
const BODY_FONT_SIZE = "14px";
const BODY_LINE_HEIGHT = "22px";
const CODE_FONT_STACK =
  '"SF Mono", Monaco, Menlo, Consolas, "Ubuntu Mono", "Liberation Mono", "DejaVu Sans Mono", "Courier New", monospace';

export const SUPPORTED_LAYOUTS = ["single", "paginated"];
// Wider than the body's own 900px max-width (plus its 2rem/32px side margins) so that
// max-width is always fully reached before we measure content size for "single" layout —
// otherwise a narrower default viewport would cap the measured width below 900px.
const SINGLE_PAGE_VIEWPORT_WIDTH = 1000;

// Add `open` to every <details> opening tag that doesn't already have it — collapsible
// blocks can't be clicked open in a PDF (or an image of it), so print them all open.
function openAllDetails(html) {
  return html.replace(/<details(?![^>]*\bopen\b)(\s[^>]*)?>/gi, (match, attrs = "") => `<details open${attrs}>`);
}

function toFileUrl(filePath) {
  return `file://${path.resolve(filePath).replace(/\\/g, "/")}`;
}

/**
 * Render a whole Markdown file to a PDF at `outputFile`. Throws an Error (with the
 * reason in its message) on any failure; temporary intermediates are always removed.
 * @param {import("puppeteer").Browser} browser
 * @param {string} targetFile
 * @param {"single"|"paginated"} layout
 * @param {string} outputFile
 */
export async function renderDocumentPdf(browser, targetFile, layout, outputFile) {
  const workDir = fs.mkdtempSync(path.join(os.tmpdir(), "export-document-pdf-"));
  try {
    // --- Stage 1: extract each diagram to SVG; get back Markdown with image references ---
    const stageMdFile = path.join(workDir, "stage.md");
    const stage1 = runMmdc(["-i", targetFile, "-o", stageMdFile, "-e", "svg"]);

    if (stage1.spawnError) {
      throw new Error(`Failed to run mermaid-cli: ${stage1.spawnError.message}`);
    }
    if (stage1.status !== 0) {
      throw new Error(
        `mermaid-cli reported an error while extracting diagrams from "${targetFile}":\n${stage1.combinedOutput}`,
      );
    }
    if (!fs.existsSync(stageMdFile)) {
      throw new Error(`mermaid-cli did not produce an intermediate Markdown file:\n${stage1.combinedOutput}`);
    }

    // --- Stage 1.5: widen each extracted SVG's viewBox to its real drawn bounding box ---
    // (some renderers, e.g. zenuml, compute a viewBox that clips content such as comments).
    // Measured in the same browser that prints the PDF, so text widths match.
    for (const entry of fs.readdirSync(workDir)) {
      if (/\.svg$/i.test(entry)) {
        await fitSvgFile(browser, path.join(workDir, entry));
      }
    }

    // --- Stage 2: Markdown -> HTML, inline the extracted SVGs, print to PDF ---
    const stageMarkdown = fs.readFileSync(stageMdFile, "utf-8");
    const md = new MarkdownIt({ html: true });
    const bodyHtml = openAllDetails(inlineSvgImages(md.render(stageMarkdown), workDir));

    const fullHtml = `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { font-family: ${BODY_FONT_STACK}; font-size: ${BODY_FONT_SIZE}; line-height: ${BODY_LINE_HEIGHT}; max-width: 900px; margin: 2rem auto; }
  svg { max-width: 100%; height: auto; }
  pre { background: #f5f5f5; padding: 0.75rem; overflow-x: auto; }
  code { font-family: ${CODE_FONT_STACK}; font-size: 1em; line-height: 1.357em; background: #f0f0f0; padding: 0.15em 0.35em; border-radius: 3px; }
  pre code { background: none; padding: 0; border-radius: 0; }
</style>
</head>
<body>
${bodyHtml}
</body>
</html>
`;

    const stageHtmlFile = path.join(workDir, "stage.html");
    fs.writeFileSync(stageHtmlFile, fullHtml, "utf-8");

    const page = await browser.newPage();
    try {
      if (layout === "single") {
        // Match mmdc's own --pdfFit approach: measure the actually-rendered content size
        // and hand that straight to page.pdf() as the page's own width/height, rather than
        // fitting content into a fixed paper size. pageRanges pins it to one page in case
        // sub-pixel rounding would otherwise spill a sliver onto a second page.
        await page.setViewport({ width: SINGLE_PAGE_VIEWPORT_WIDTH, height: 800 });
        await page.goto(toFileUrl(stageHtmlFile), { waitUntil: "networkidle0" });
        const { width, height } = await page.evaluate(() => ({
          width: document.documentElement.scrollWidth,
          height: document.documentElement.scrollHeight,
        }));
        await page.pdf({
          path: outputFile,
          printBackground: true,
          width: `${width}px`,
          height: `${height}px`,
          pageRanges: "1-1",
        });
      } else {
        await page.goto(toFileUrl(stageHtmlFile), { waitUntil: "networkidle0" });
        await page.pdf({
          path: outputFile,
          format: "A4",
          printBackground: true,
          margin: { top: "1cm", bottom: "1cm", left: "1cm", right: "1cm" },
        });
      }
    } finally {
      await page.close();
    }
  } finally {
    // --- Cleanup temporary intermediates (stage Markdown, extracted SVGs, stage HTML) ---
    fs.rmSync(workDir, { recursive: true, force: true });
  }

  if (!fs.existsSync(outputFile)) {
    throw new Error(`PDF generation reported success but no output file was found at ${outputFile}`);
  }
}
