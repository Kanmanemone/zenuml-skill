#!/usr/bin/env node
// scope=diagram: convert the diagram(s) embedded in a Markdown file to SVG/PNG/PDF.
// Deterministic — shells out to mermaid-cli (mmdc); never reasons about diagram content.
// Usage: node export-diagrams.js <targetFile.md> <svg|png|pdf> [outputBase]

import path from "node:path";
import fs from "node:fs";
import { runMmdc } from "./lib/run-mmdc.js";
import { ensureExportDir } from "./lib/export-dir.js";

const SUPPORTED_FORMATS = ["svg", "png", "pdf"];
// Puppeteer deviceScaleFactor for PNG capture (~288 DPI-equivalent at the standard
// 96 CSS px/in baseline). mmdc resizes the viewport to the diagram's own bounding
// box before screenshotting (see research.md "PNG 해상도"), so this scale — not an
// explicit width/height — is what keeps PNGs sharp regardless of diagram size.
const PNG_SCALE = 3;

function fail(message, code = 1) {
  console.error(message);
  process.exit(code);
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function main() {
  const [, , targetFile, format, outputBaseArg] = process.argv;

  if (!targetFile || !format) {
    fail(
      "Usage: node export-diagrams.js <targetFile.md> <svg|png|pdf> [outputBase]",
      2,
    );
  }
  if (!SUPPORTED_FORMATS.includes(format)) {
    fail(`Unsupported format "${format}" — must be one of: ${SUPPORTED_FORMATS.join(", ")}.`, 2);
  }
  if (!fs.existsSync(targetFile)) {
    fail(`Target file not found: ${targetFile}`);
  }
  if (!/\.(md|markdown)$/i.test(targetFile)) {
    fail(`Unsupported file type: ${targetFile} — only .md/.markdown files are supported.`);
  }

  const outputBase =
    outputBaseArg ||
    path.join(
      ensureExportDir(targetFile),
      path.basename(targetFile).replace(/\.(md|markdown)$/i, ""),
    );
  const outputFile = `${outputBase}.${format}`;

  const mmdcArgs = ["-i", targetFile, "-o", outputFile];
  if (format === "png") {
    mmdcArgs.push("-s", String(PNG_SCALE));
  }
  const { status, combinedOutput, spawnError } = runMmdc(mmdcArgs);

  if (spawnError) {
    fail(`Failed to run mermaid-cli: ${spawnError.message}`);
  }
  if (status !== 0) {
    fail(`mermaid-cli reported an error while converting "${targetFile}":\n${combinedOutput}`);
  }
  // mermaid-cli logs this exact message (src/index.js) when the Markdown input has zero
  // diagram code fences — it exits 0 in that case, so we must check the log, not the exit code.
  if (/No mermaid charts found/i.test(combinedOutput)) {
    fail(`No diagrams found in ${targetFile} — nothing to convert.`);
  }

  // For Markdown input, mermaid-cli numbers each diagram it finds (out-1.svg, out-2.svg, ...),
  // even when there's exactly one. Collect whatever it actually produced.
  const dir = path.dirname(outputFile) || ".";
  const base = path.basename(outputFile, `.${format}`);
  const pattern = new RegExp(`^${escapeRegExp(base)}(-\\d+)?\\.${format}$`);
  const produced = fs
    .readdirSync(dir)
    .filter((entry) => pattern.test(entry))
    .map((entry) => path.join(dir, entry));

  if (produced.length === 0) {
    fail(
      `mermaid-cli reported success but no output file was found matching ${outputFile}:\n${combinedOutput}`,
    );
  }

  for (const file of produced) {
    console.log(file);
  }
}

main();
