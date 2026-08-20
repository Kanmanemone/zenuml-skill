// Shared helper for computing the default output directory for either export script.
// Keeps generated files out of the source Markdown's own directory: all diagrams/documents
// converted from files in one directory land together under that directory's exports/ subdir.

import path from "node:path";
import fs from "node:fs";

/**
 * @param {string} targetFile - path to the source Markdown file being converted
 * @returns {string} the `<dirname(targetFile)>/exports` directory, created if missing
 */
export function ensureExportDir(targetFile) {
  const dir = path.join(path.dirname(targetFile), "exports");
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}
