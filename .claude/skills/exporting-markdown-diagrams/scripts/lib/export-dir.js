// Shared helper for computing the default output directory for either export script.
// Keeps generated files out of the source Markdown's own directory: converted files land
// in the `output.directory` setting, resolved relative to the source file's directory
// (default "./exports" — i.e. an exports/ subdirectory next to the source file).

import path from "node:path";
import fs from "node:fs";

/**
 * @param {string} targetFile - path to the source Markdown file being converted
 * @param {string} outputDirectory - relative path from the source file's directory
 * @returns {string} the resolved output directory, created if missing
 */
export function ensureExportDir(targetFile, outputDirectory = "./exports") {
  const dir = path.resolve(path.dirname(targetFile), outputDirectory);
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}
