#!/usr/bin/env node
// scope=document, format=pdf: convert a whole Markdown file to PDF, with any embedded
// diagrams inserted as vector SVG (so their text stays selectable/copyable) rather than
// as raster images. Deterministic — never reasons about the document/diagram content.
// Usage: node export-document-pdf.js <targetFile.md> [outputFile.pdf] [--layout single|paginated]
//
// The pipeline itself lives in lib/document-pdf.js (shared with export-document-png.js).

import path from "node:path";
import fs from "node:fs";
import puppeteer from "puppeteer";
import { BROWSER_LAUNCH_OPTIONS } from "./lib/browser-config.js";
import { ensureExportDir } from "./lib/export-dir.js";
import { loadSettings, SKILL_DIR } from "./lib/settings.js";
import { renderDocumentPdf, SUPPORTED_LAYOUTS } from "./lib/document-pdf.js";

function fail(message, code = 1) {
  console.error(message);
  process.exit(code);
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

  const { values: settings } = loadSettings(SKILL_DIR);
  const outputFile =
    outputFileArg ||
    path.join(
      ensureExportDir(targetFile, settings["output.directory"]),
      path.basename(targetFile).replace(/\.(md|markdown)$/i, ".pdf"),
    );

  const browser = await puppeteer.launch(BROWSER_LAUNCH_OPTIONS);
  try {
    await renderDocumentPdf(browser, targetFile, layout, outputFile);
  } finally {
    await browser.close();
  }

  console.log(outputFile);
}

main().catch((error) => fail(error?.message ?? String(error)));
