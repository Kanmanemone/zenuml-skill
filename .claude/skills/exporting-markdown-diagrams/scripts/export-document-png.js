#!/usr/bin/env node
// scope=document, format=png: convert a whole Markdown file to PNG. The document is first
// rendered to a temporary PDF with exactly the same pipeline as export-document-pdf.js,
// then each PDF page is rasterized — so the PNGs share the PDF's look and page breaks.
// Deterministic — never reasons about the document/diagram content.
// Usage: node export-document-png.js <targetFile.md> [outputBase] [--layout single|paginated]
//   single    -> <outputBase>.png (one tall image)
//   paginated -> <outputBase>-page-1.png, <outputBase>-page-2.png, ... (one per A4 page)

import path from "node:path";
import fs from "node:fs";
import os from "node:os";
import puppeteer from "puppeteer";
import { BROWSER_LAUNCH_OPTIONS } from "./lib/browser-config.js";
import { ensureExportDir } from "./lib/export-dir.js";
import { loadSettings, SKILL_DIR } from "./lib/settings.js";
import { renderDocumentPdf, SUPPORTED_LAYOUTS } from "./lib/document-pdf.js";
import { rasterizePdf } from "./lib/rasterize-pdf.js";

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
  const [targetFile, outputBaseArg] = args;

  if (!targetFile) {
    fail("Usage: node export-document-png.js <targetFile.md> [outputBase] [--layout single|paginated]", 2);
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
  let outputBase = outputBaseArg
    ? outputBaseArg.replace(/\.png$/i, "")
    : path.join(
        ensureExportDir(targetFile, settings["output.directory"]),
        path.basename(targetFile).replace(/\.(md|markdown)$/i, ""),
      );
  fs.mkdirSync(path.dirname(path.resolve(outputBase)), { recursive: true });

  const workDir = fs.mkdtempSync(path.join(os.tmpdir(), "export-document-png-"));
  let written;
  const browser = await puppeteer.launch(BROWSER_LAUNCH_OPTIONS);
  try {
    const pdfFile = path.join(workDir, "document.pdf");
    await renderDocumentPdf(browser, targetFile, layout, pdfFile);
    written = await rasterizePdf(browser, pdfFile, settings["png.scale"], (pageNumber) =>
      layout === "single" ? `${outputBase}.png` : `${outputBase}-page-${pageNumber}.png`,
    );
  } finally {
    await browser.close();
    fs.rmSync(workDir, { recursive: true, force: true });
  }

  for (const file of written) {
    if (!fs.existsSync(file)) {
      fail(`PNG generation reported success but no output file was found at ${file}`);
    }
    console.log(file);
  }
}

main().catch((error) => fail(error?.message ?? String(error)));
