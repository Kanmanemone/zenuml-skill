#!/usr/bin/env node
// scope=document, format=pdf: convert a whole Markdown file to PDF, with any embedded
// diagrams inserted as vector SVG (so their text stays selectable/copyable) rather than
// as raster images. Deterministic — never reasons about the document/diagram content.
// Usage: node export-document-pdf.js <targetFile.md> [outputFile.pdf]
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

function fail(message, code = 1) {
  console.error(message);
  process.exit(code);
}

function toFileUrl(filePath) {
  return `file://${path.resolve(filePath).replace(/\\/g, "/")}`;
}

async function main() {
  const [, , targetFile, outputFileArg] = process.argv;

  if (!targetFile) {
    fail("Usage: node export-document-pdf.js <targetFile.md> [outputFile.pdf]", 2);
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
  body { font-family: sans-serif; max-width: 900px; margin: 2rem auto; line-height: 1.5; }
  svg { max-width: 100%; height: auto; }
  pre { background: #f5f5f5; padding: 0.75rem; overflow-x: auto; }
  code { font-family: monospace; }
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
      await page.goto(toFileUrl(stageHtmlFile), { waitUntil: "networkidle0" });
      await page.pdf({
        path: outputFile,
        format: "A4",
        printBackground: true,
        margin: { top: "1cm", bottom: "1cm", left: "1cm", right: "1cm" },
      });
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
