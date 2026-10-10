// Shared helper: make an SVG's viewBox cover everything it actually draws, then optionally
// rasterize/print it. Needed because some renderers (observed: zenuml-core via mermaid-cli)
// compute the root viewBox without accounting for every element — e.g. message comments
// drawn to the right of the rightmost lifeline — so mmdc's own SVG/PNG/PDF output clips them.
// The geometry is measured by the browser (getBBox), never guessed, and the SVG markup is
// patched in place (root tag attributes only) rather than re-serialized from the DOM.
//
// Text width depends on which browser measures it (chrome-headless-shell and full Chrome
// resolve generic font families differently), so callers must pass the same browser
// instance they render with — see research.md, "측정 브라우저 = 렌더 브라우저".

import fs from "node:fs";

// Extra room (in SVG user units) added only on a side where content actually overflowed,
// so strokes/antialiasing at the very edge of the overflowing content aren't cut off.
const OVERFLOW_PADDING = 16;
// getBBox() of text/strokes routinely pokes a fraction of a unit past a correctly sized
// viewBox (seen on plain mermaid sequence diagrams). Ignore overflow up to this much so
// diagrams that were never clipped come out byte-for-byte unchanged.
const OVERFLOW_TOLERANCE = 1;

const ROOT_SVG_TAG = /<svg\b[^>]*>/i;

function readViewBox(svgMarkup) {
  const rootTag = svgMarkup.match(ROOT_SVG_TAG)?.[0] ?? "";
  const match = rootTag.match(/\bviewBox="([^"]+)"/i);
  if (!match) return null;
  const [x, y, width, height] = match[1].trim().split(/[\s,]+/).map(Number);
  return [x, y, width, height].every(Number.isFinite) ? { x, y, width, height } : null;
}

function patchRootTag(svgMarkup, { x, y, width, height }) {
  return svgMarkup.replace(ROOT_SVG_TAG, (rootTag) => {
    let patched = rootTag.replace(/\bviewBox="[^"]*"/i, `viewBox="${x} ${y} ${width} ${height}"`);
    // mermaid writes `style="max-width: <viewBox width>px; ..."` on the root; keep it in sync,
    // or the widened diagram would still be squeezed to the old width when displayed.
    patched = patched.replace(/max-width:\s*[\d.]+px/i, `max-width: ${width}px`);
    return patched;
  });
}

async function withSvgPage(browser, svgMarkup, viewport, fn) {
  const page = await browser.newPage();
  try {
    if (viewport) await page.setViewport(viewport);
    await page.setContent(
      `<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:0;background:white">${svgMarkup}</body></html>`,
      { waitUntil: "load" },
    );
    return await fn(page);
  } finally {
    await page.close();
  }
}

/**
 * Widens the root viewBox of `svgPath` (in place) so it covers the SVG's full drawn bounding box.
 * Leaves the file byte-for-byte untouched when nothing overflows.
 *
 * @param {import("puppeteer").Browser} browser
 * @param {string} svgPath
 * @returns {Promise<{ changed: boolean, before: object|null, after: object|null }>}
 */
export async function fitSvgFile(browser, svgPath) {
  const svgMarkup = fs.readFileSync(svgPath, "utf-8");
  const before = readViewBox(svgMarkup);
  if (!before) return { changed: false, before: null, after: null };

  const bbox = await withSvgPage(browser, svgMarkup, null, (page) =>
    page.evaluate(() => {
      const box = document.querySelector("svg").getBBox();
      return { x: box.x, y: box.y, width: box.width, height: box.height };
    }),
  );

  const beforeRight = before.x + before.width;
  const beforeBottom = before.y + before.height;
  const bboxRight = bbox.x + bbox.width;
  const bboxBottom = bbox.y + bbox.height;
  const left =
    bbox.x < before.x - OVERFLOW_TOLERANCE ? Math.floor(bbox.x - OVERFLOW_PADDING) : before.x;
  const top =
    bbox.y < before.y - OVERFLOW_TOLERANCE ? Math.floor(bbox.y - OVERFLOW_PADDING) : before.y;
  const right =
    bboxRight > beforeRight + OVERFLOW_TOLERANCE ? Math.ceil(bboxRight + OVERFLOW_PADDING) : beforeRight;
  const bottom =
    bboxBottom > beforeBottom + OVERFLOW_TOLERANCE ? Math.ceil(bboxBottom + OVERFLOW_PADDING) : beforeBottom;

  const after = { x: left, y: top, width: right - left, height: bottom - top };
  const changed =
    after.x !== before.x || after.y !== before.y || after.width !== before.width || after.height !== before.height;
  if (changed) {
    fs.writeFileSync(svgPath, patchRootTag(svgMarkup, after), "utf-8");
  }
  return { changed, before, after };
}

// Loads `svgPath` into a page whose viewport matches its viewBox, with the root <svg> pinned
// to exactly that many CSS px (no max-width squeeze), then hands the page to `fn`.
async function withSizedSvgPage(browser, svgPath, deviceScaleFactor, fn) {
  const svgMarkup = fs.readFileSync(svgPath, "utf-8");
  const viewBox = readViewBox(svgMarkup);
  const width = Math.ceil(viewBox?.width ?? 800);
  const height = Math.ceil(viewBox?.height ?? 600);
  await withSvgPage(browser, svgMarkup, { width, height, deviceScaleFactor }, async (page) => {
    await page.evaluate(
      (w, h) => {
        const root = document.querySelector("svg");
        root.setAttribute("width", `${w}px`);
        root.setAttribute("height", `${h}px`);
        root.style.maxWidth = "none";
        root.style.display = "block";
      },
      width,
      height,
    );
    await fn(page, { width, height });
  });
}

/** Renders `svgPath` at its viewBox size to `pngPath`, at `scale`× device pixels, on white. */
export async function svgFileToPng(browser, svgPath, pngPath, scale) {
  await withSizedSvgPage(browser, svgPath, scale, async (page) => {
    const root = await page.$("svg");
    await root.screenshot({ path: pngPath });
  });
}

/** Prints `svgPath` to a single PDF page sized exactly to the SVG's viewBox (vector, like mmdc --pdfFit). */
export async function svgFileToPdf(browser, svgPath, pdfPath) {
  await withSizedSvgPage(browser, svgPath, 1, async (page, { width, height }) => {
    await page.pdf({
      path: pdfPath,
      printBackground: true,
      width: `${width}px`,
      height: `${height}px`,
      pageRanges: "1-1",
    });
  });
}
