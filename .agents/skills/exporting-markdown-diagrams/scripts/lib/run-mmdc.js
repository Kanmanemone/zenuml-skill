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
import { loadSettings, SKILL_DIR } from "./settings.js";

const scriptsDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

// render.theme (007 FR-014c): the Mermaid config VS Code's built-in preview uses under Light+,
// or nothing for Mermaid's own default rendering. A diagram's own config still wins over it.
const THEME_FLAG = "--theme=";
const THEME_CONFIGS = {
  "vscode-light-plus": path.join(scriptsDir, "vscode-light-plus.json"),
  "mermaid-default": null,
};

/** Entry scripts read their positional arguments from this, so `--theme=` is never one. */
export function withoutThemeFlag(args) {
  return args.filter((arg) => !arg.startsWith(THEME_FLAG));
}

function themeArgs() {
  let theme = loadSettings(SKILL_DIR).values["render.theme"];
  const requested = process.argv.find((arg) => arg.startsWith(THEME_FLAG))?.slice(THEME_FLAG.length);
  if (requested !== undefined) {
    if (Object.hasOwn(THEME_CONFIGS, requested)) {
      theme = requested;
    } else {
      console.log(`⚙️ 설정 안내: 명령줄 \`render.theme\` 값 \`${requested}\`이 허용되지 않아 설정 값 \`${theme}\` 사용`);
    }
  }
  return THEME_CONFIGS[theme] ? ["-c", THEME_CONFIGS[theme]] : [];
}

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
  // Not installed locally yet — fall back to a one-off npx invocation of the same version range
  // package.json declares (never an unpinned "latest").
  const range = JSON.parse(fs.readFileSync(path.join(scriptsDir, "package.json"), "utf-8"))
    .dependencies["@mermaid-js/mermaid-cli"];
  return {
    command: process.platform === "win32" ? "npx.cmd" : "npx",
    baseArgs: ["--yes", `--package=@mermaid-js/mermaid-cli@${range}`, "mmdc"],
    shell: process.platform === "win32",
  };
}

/**
 * @param {string[]} args - mmdc CLI arguments, e.g. ["-i", inputFile, "-o", outputFile]
 * @returns {{ status: number, stdout: string, stderr: string, combinedOutput: string, spawnError: Error | undefined }}
 */
export function runMmdc(args) {
  const { command, baseArgs, shell } = resolveMmdc();
  const result = spawnSync(command, [...baseArgs, "-p", PUPPETEER_CONFIG_FILE, ...themeArgs(), ...args], {
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
