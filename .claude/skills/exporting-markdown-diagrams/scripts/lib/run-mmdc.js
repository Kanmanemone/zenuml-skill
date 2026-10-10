// Shared helper for invoking mermaid-cli (mmdc) from either export script.
// Runs its actual JS entrypoint via the current Node binary rather than the installed
// .cmd/.sh shim — avoids Windows' spawnSync EINVAL on shims (and the shell:true argument-
// escaping footgun that would otherwise be needed to work around it).
// Always passes the skill's shared browser launch settings (`-p`, see browser-config.js), so
// mmdc's browser matches ours and doesn't pop up a terminal window on Windows.

import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";
import fs from "node:fs";
import { PUPPETEER_CONFIG_FILE } from "./browser-config.js";

const scriptsDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function resolveMmdc() {
  const cliEntry = path.join(
    scriptsDir,
    "node_modules",
    "@mermaid-js",
    "mermaid-cli",
    "src",
    "cli.js",
  );
  if (fs.existsSync(cliEntry)) {
    return { command: process.execPath, baseArgs: [cliEntry], shell: false };
  }
  // Not installed locally yet — fall back to a one-off npx invocation of the same pinned package.
  return {
    command: process.platform === "win32" ? "npx.cmd" : "npx",
    baseArgs: ["--yes", "--package=@mermaid-js/mermaid-cli", "mmdc"],
    shell: process.platform === "win32",
  };
}

/**
 * @param {string[]} args - mmdc CLI arguments, e.g. ["-i", inputFile, "-o", outputFile]
 * @returns {{ status: number, stdout: string, stderr: string, combinedOutput: string, spawnError: Error | undefined }}
 */
export function runMmdc(args) {
  const { command, baseArgs, shell } = resolveMmdc();
  const result = spawnSync(command, [...baseArgs, "-p", PUPPETEER_CONFIG_FILE, ...args], {
    encoding: "utf-8",
    shell,
    windowsHide: true,
  });
  const stdout = result.stdout ?? "";
  const stderr = result.stderr ?? "";
  return {
    status: result.status ?? 1,
    stdout,
    stderr,
    combinedOutput: `${stdout}${stderr}`,
    spawnError: result.error,
  };
}
