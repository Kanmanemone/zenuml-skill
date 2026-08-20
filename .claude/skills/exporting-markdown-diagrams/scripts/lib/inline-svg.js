// Replace <img src="*.svg"> references in an HTML string with the literal contents of that
// SVG file, so a browser printing this HTML to PDF embeds it as a real <svg> element (vector,
// selectable text) instead of a linked raster-style image. See research.md, "User Story 2
// 파이프라인" Decision — mermaid-cli's own PDF output uses exactly this DOM-<svg>-then-page.pdf()
// path, which is why inlining here (rather than leaving a file link) is the verified-safe choice.

import fs from "node:fs";
import path from "node:path";

const IMG_SVG_TAG = /<img\b[^>]*\bsrc="([^"]+\.svg)"[^>]*\/?>/gi;
const XML_PROLOG = /^\s*<\?xml[^>]*\?>\s*/i;

/**
 * @param {string} html - HTML that may contain <img src="*.svg"> references
 * @param {string} baseDir - directory relative SVG `src` paths should be resolved against
 * @returns {string} the same HTML with every local *.svg image reference inlined as literal <svg> markup
 */
export function inlineSvgImages(html, baseDir) {
  return html.replace(IMG_SVG_TAG, (originalTag, src) => {
    if (/^([a-z]+:)?\/\//i.test(src) || src.startsWith("data:")) {
      // Remote or already-inline sources aren't produced by our own pipeline — leave untouched.
      return originalTag;
    }
    const svgPath = path.resolve(baseDir, src);
    if (!fs.existsSync(svgPath)) {
      return originalTag;
    }
    const svgMarkup = fs.readFileSync(svgPath, "utf-8").replace(XML_PROLOG, "");
    return svgMarkup;
  });
}
