#!/usr/bin/env node
// scope=diagram: convert the diagram(s) embedded in a Markdown file to SVG/PNG/PDF.
// Deterministic — shells out to mermaid-cli (mmdc); never reasons about diagram content.
// Usage: node export-diagrams.js <targetFile.md> <svg|png|pdf> [outputBase]
//
// Pipeline:
//   1. mmdc always renders every diagram to SVG first, into a temp dir.
//   2. Each SVG's root viewBox is widened to its real drawn bounding box (lib/fit-svg.js) —
//      some renderers (zenuml) compute a viewBox that clips content such as message comments.
//   3. The fitted SVG is copied out (svg), screenshotted (png) or printed (pdf) by our own
//      headless browser, instead of letting mmdc produce png/pdf from the clipped geometry.

import path from "node:path";
import fs from "node:fs";
import os from "node:os";
import puppeteer from "puppeteer";
import { runMmdc } from "./lib/run-mmdc.js";
import { ensureExportDir } from "./lib/export-dir.js";
import { fitSvgFile, svgFileToPng, svgFileToPdf } from "./lib/fit-svg.js";

const SUPPORTED_FORMATS = ["svg", "png", "pdf"];
// Puppeteer deviceScaleFactor for PNG capture (~288 DPI-equivalent at the standard
// 96 CSS px/in baseline). The viewport is sized to the fitted viewBox itself before
// screenshotting — never squeezed into a fixed page width — so this scale, not an
// explicit width/height, is what keeps PNGs sharp regardless of diagram size.
const PNG_SCALE = 3;

function fail(message, code = 1) {
  console.error(message);
  process.exit(code);
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

async function main() {
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
  const outputDir = path.dirname(outputBase) || ".";
  const base = path.basename(outputBase);
  fs.mkdirSync(outputDir, { recursive: true });

  const workDir = fs.mkdtempSync(path.join(os.tmpdir(), "export-diagrams-"));
  // fail() exits via process.exit, which skips `finally` blocks — clean up on exit instead.
  process.on("exit", () => fs.rmSync(workDir, { recursive: true, force: true }));

  // --- Stage 1: every diagram -> SVG in the temp dir ---
  const { status, combinedOutput, spawnError } = runMmdc([
    "-i",
    targetFile,
    "-o",
    path.join(workDir, `${base}.svg`),
  ]);

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
  // even when there's exactly one. Collect whatever it actually produced, in diagram order.
  // The temp dir is fresh, so nothing left over from an earlier run can sneak in.
  const pattern = new RegExp(`^${escapeRegExp(base)}(?:-(\\d+))?\\.svg$`);
  const svgFiles = fs
    .readdirSync(workDir)
    .map((entry) => ({ entry, match: entry.match(pattern) }))
    .filter(({ match }) => match)
    .sort((a, b) => Number(a.match[1] ?? 0) - Number(b.match[1] ?? 0))
    .map(({ entry }) => entry);

  if (svgFiles.length === 0) {
    fail(
      `mermaid-cli reported success but no SVG was produced for ${targetFile}:\n${combinedOutput}`,
    );
  }

  // --- Stage 2: fit each SVG's viewBox to its content, then emit the requested format ---
  // Same launch mode mmdc uses, so the text we measure is laid out exactly as mmdc laid it out.
  const produced = [];
  const browser = await puppeteer.launch({ headless: "shell" });
  try {
    for (const svgName of svgFiles) {
      const svgPath = path.join(workDir, svgName);
      await fitSvgFile(browser, svgPath);

      const outputFile = path.join(outputDir, svgName.replace(/\.svg$/i, `.${format}`));
      if (format === "svg") {
        fs.copyFileSync(svgPath, outputFile);
      } else if (format === "png") {
        await svgFileToPng(browser, svgPath, outputFile, PNG_SCALE);
      } else {
        await svgFileToPdf(browser, svgPath, outputFile);
      }
      produced.push(outputFile);
    }
  } finally {
    await browser.close();
  }

  for (const file of produced) {
    if (!fs.existsSync(file)) {
      fail(`Conversion reported success but no output file was found at ${file}`);
    }
    console.log(file);
  }
}

main().catch((error) => fail(`Diagram export failed: ${error?.stack ?? error}`));
