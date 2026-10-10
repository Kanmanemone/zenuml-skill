// Shared headless-browser launch settings for every browser this skill starts — both the ones
// mermaid-cli launches (passed via `mmdc -p`, see run-mmdc.js) and our own puppeteer.launch()
// calls — kept in one JSON file because mmdc only accepts Puppeteer settings as a file.
//
// `headless: true` runs the GUI-subsystem chrome binary instead of chrome-headless-shell, a
// console-subsystem binary that pops up a terminal window on Windows for every launch.
// `--lang=en-US` keeps generic font families (e.g. `sans-serif`) resolving exactly as they do in
// chrome-headless-shell; without it chrome follows the OS UI locale and text widths change.
// Both measured — see specs/006-hide-console-windows/research.md.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const PUPPETEER_CONFIG_FILE = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
  "puppeteer-config.json",
);

export const BROWSER_LAUNCH_OPTIONS = JSON.parse(fs.readFileSync(PUPPETEER_CONFIG_FILE, "utf-8"));
