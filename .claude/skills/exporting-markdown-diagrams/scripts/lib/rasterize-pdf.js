// Render every page of a PDF to its own PNG file, inside the headless browser we already
// run (pdf.js draws each page to a <canvas>), so the PNGs share the PDF's exact layout and
// page breaks. pdf.js is an ES module with a worker, which browsers refuse to load from
// file://, so a throwaway HTTP server on 127.0.0.1 serves it (and the PDF) only for the
// duration of the call.

import path from "node:path";
import fs from "node:fs";
import http from "node:http";
import { fileURLToPath } from "node:url";

// scripts/lib/ -> scripts/node_modules/pdfjs-dist
const PDFJS_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "node_modules", "pdfjs-dist");

const MIME = {
  ".mjs": "text/javascript",
  ".js": "text/javascript",
  ".pdf": "application/pdf",
  ".html": "text/html; charset=utf-8",
  ".bcmap": "application/octet-stream",
  ".pfb": "application/octet-stream",
  ".ttf": "font/ttf",
};

const PAGE_HTML = `<!doctype html>
<html><head><meta charset="utf-8"></head><body>
<script type="module">
  import * as pdfjs from "/pdfjs/build/pdf.mjs";
  pdfjs.GlobalWorkerOptions.workerSrc = "/pdfjs/build/pdf.worker.mjs";
  window.__openPdf = async () => {
    window.__doc = await pdfjs.getDocument({
      url: "/doc.pdf",
      cMapUrl: "/pdfjs/cmaps/",
      cMapPacked: true,
      standardFontDataUrl: "/pdfjs/standard_fonts/",
    }).promise;
    return window.__doc.numPages;
  };
  window.__renderPage = async (pageNumber, scale) => {
    const page = await window.__doc.getPage(pageNumber);
    const viewport = page.getViewport({ scale });
    const width = Math.ceil(viewport.width);
    const height = Math.ceil(viewport.height);
    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    const context = canvas.getContext("2d");
    if (!context) return { error: "canvas context unavailable", width, height };
    await page.render({ canvasContext: context, viewport, canvas }).promise;
    const dataUrl = canvas.toDataURL("image/png");
    if (!dataUrl.startsWith("data:image/png;base64,")) {
      return { error: "canvas could not be encoded (likely too large)", width, height };
    }
    return { dataUrl, width, height };
  };
  window.__ready = true;
</script>
</body></html>`;

function startServer(pdfFile) {
  const server = http.createServer((req, res) => {
    const url = decodeURIComponent(new URL(req.url, "http://127.0.0.1").pathname);
    let filePath;
    if (url === "/" || url === "/render.html") {
      res.writeHead(200, { "Content-Type": MIME[".html"] });
      res.end(PAGE_HTML);
      return;
    } else if (url === "/doc.pdf") {
      filePath = pdfFile;
    } else if (url.startsWith("/pdfjs/")) {
      const resolved = path.resolve(PDFJS_ROOT, "." + url.slice("/pdfjs".length));
      if (!resolved.startsWith(PDFJS_ROOT + path.sep)) {
        res.writeHead(403);
        res.end();
        return;
      }
      filePath = resolved;
    }
    if (!filePath || !fs.existsSync(filePath)) {
      res.writeHead(404);
      res.end();
      return;
    }
    res.writeHead(200, { "Content-Type": MIME[path.extname(filePath)] ?? "application/octet-stream" });
    fs.createReadStream(filePath).pipe(res);
  });
  return new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => resolve(server));
  });
}

/**
 * Rasterize every page of `pdfFile` to PNG.
 * @param {import("puppeteer").Browser} browser
 * @param {string} pdfFile
 * @param {number} scale - output pixels per CSS pixel (same meaning as diagram PNG scale)
 * @param {(pageNumber: number, pageCount: number) => string} outputFileFor
 * @returns {Promise<string[]>} written PNG paths, in page order
 */
export async function rasterizePdf(browser, pdfFile, scale, outputFileFor) {
  const server = await startServer(pdfFile);
  const page = await browser.newPage();
  try {
    const { port } = server.address();
    await page.goto(`http://127.0.0.1:${port}/render.html`, { waitUntil: "load" });
    await page.waitForFunction(() => window.__ready === true);
    const pageCount = await page.evaluate(() => window.__openPdf());

    // PDF units are points (1/72 in); CSS pixels are 1/96 in.
    const pdfScale = (scale * 96) / 72;
    const written = [];
    for (let pageNumber = 1; pageNumber <= pageCount; pageNumber += 1) {
      const result = await page.evaluate((n, s) => window.__renderPage(n, s), pageNumber, pdfScale);
      if (result.error) {
        throw new Error(
          `Could not render page ${pageNumber} of ${pageCount} as a ${result.width}x${result.height}px PNG: ${result.error}.`,
        );
      }
      const outputFile = outputFileFor(pageNumber, pageCount);
      fs.writeFileSync(outputFile, Buffer.from(result.dataUrl.split(",")[1], "base64"));
      written.push(outputFile);
    }
    return written;
  } finally {
    await page.close();
    await new Promise((resolve) => server.close(resolve));
  }
}
