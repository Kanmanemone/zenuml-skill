#!/usr/bin/env node
// scope=document, format=pdf: convert a whole Markdown file to PDF, with any embedded
// diagrams inserted as vector SVG (so their text stays selectable/copyable) rather than
// as raster images. Deterministic — never reasons about the document/diagram content.
// Usage: node export-document-pdf.js <targetFile.md> [outputFile.pdf] [--layout single|paginated]
//
// Pipeline (see research.md, "User Story 2 파이프라인" Decision):
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
import puppeteer from "puppeteer";
import { runMmdc } from "./lib/run-mmdc.js";
import { inlineSvgImages } from "./lib/inline-svg.js";
import { ensureExportDir } from "./lib/export-dir.js";

// Headless Chromium falls back to generic/bitmap-ish substitutes for the bare
// "sans-serif"/"monospace" CSS keywords depending on what fonts are actually
// registered on the host OS. Naming real fonts explicitly (with Windows/macOS/
// Linux + Korean-CJK coverage, generic keyword last) keeps rendering legible
// across environments instead of relying on whatever substitute Chromium picks.
const BODY_FONT_STACK =
  '"Segoe UI", -apple-system, "Apple SD Gothic Neo", "Noto Sans KR", "Malgun Gothic", Helvetica, Arial, sans-serif';
const CODE_FONT_STACK =
  '"Cascadia Mono", Consolas, "D2Coding", "Noto Sans Mono CJK KR", Menlo, Monaco, monospace';

const SUPPORTED_LAYOUTS = ["single", "paginated"];
// Wider than the body's own 900px max-width (plus its 2rem/32px side margins) so that
// max-width is always fully reached before we measure content size for "single" layout —
// otherwise a narrower default viewport would cap the measured width below 900px.
const SINGLE_PAGE_VIEWPORT_WIDTH = 1000;

function fail(message, code = 1) {
  console.error(message);
  process.exit(code);
}

function toFileUrl(filePath) {
  return `file://${path.resolve(filePath).replace(/\\/g, "/")}`;
}

async function main() {
  const args = process.argv.slice(2);
  const layoutFlagIndex = args.indexOf("--layout");
  let layout = "paginated";
  if (layoutFlagIndex !== -1) {
    layout = args[layoutFlagIndex + 1];
    args.splice(layoutFlagIndex, 2);
  }
  const [targetFile, outputFileArg] = args;

  if (!targetFile) {
    fail("Usage: node export-document-pdf.js <targetFile.md> [outputFile.pdf] [--layout single|paginated]", 2);
  }
  if (!SUPPORTED_LAYOUTS.includes(layout)) {
    fail(`Unsupported --layout "${layout}" — must be one of: ${SUPPORTED_LAYOUTS.join(", ")}.`, 2);
  }
  if (!fs.existsSync(targetFile)) {
    fail(`Target file not found: ${targetFile}`);
  }
  if (!/\.(md|markdown)$/i.test(targetFile)) {
    fail(`Unsupported file type: ${targetFile} — only .md/.markdown files are supported.`);
  }

  const outputFile =
    outputFileArg ||
    path.join(
      ensureExportDir(targetFile),
      path.basename(targetFile).replace(/\.(md|markdown)$/i, ".pdf"),
    );
  const workDir = fs.mkdtempSync(path.join(os.tmpdir(), "export-document-pdf-"));

  try {
    // --- Stage 1: extract each diagram to SVG; get back Markdown with image references ---
    const stageMdFile = path.join(workDir, "stage.md");
    const stage1 = runMmdc(["-i", targetFile, "-o", stageMdFile, "-e", "svg"]);

    if (stage1.spawnError) {
      fail(`Failed to run mermaid-cli: ${stage1.spawnError.message}`);
    }
    if (stage1.status !== 0) {
      fail(
        `mermaid-cli reported an error while extracting diagrams from "${targetFile}":\n${stage1.combinedOutput}`,
      );
    }
    if (!fs.existsSync(stageMdFile)) {
      fail(`mermaid-cli did not produce an intermediate Markdown file:\n${stage1.combinedOutput}`);
    }

    // --- Stage 2: Markdown -> HTML, inline the extracted SVGs, print to PDF ---
    const stageMarkdown = fs.readFileSync(stageMdFile, "utf-8");
    const md = new MarkdownIt({ html: true });
    const bodyHtml = inlineSvgImages(md.render(stageMarkdown), workDir);

    const fullHtml = `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { font-family: ${BODY_FONT_STACK}; max-width: 900px; margin: 2rem auto; line-height: 1.5; }
  svg { max-width: 100%; height: auto; }
  pre { background: #f5f5f5; padding: 0.75rem; overflow-x: auto; }
  code { font-family: ${CODE_FONT_STACK}; background: #f0f0f0; padding: 0.15em 0.35em; border-radius: 3px; }
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

    const browser = await puppeteer.launch({ headless: "shell" });
    try {
      const page = await browser.newPage();
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
      await browser.close();
    }
  } finally {
    // --- Cleanup temporary intermediates (stage Markdown, extracted SVGs, stage HTML) ---
    fs.rmSync(workDir, { recursive: true, force: true });
  }

  if (!fs.existsSync(outputFile)) {
    fail(`PDF generation reported success but no output file was found at ${outputFile}`);
  }

  console.log(outputFile);
}

main();
