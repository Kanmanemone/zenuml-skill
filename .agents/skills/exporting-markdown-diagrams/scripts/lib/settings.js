// Generic settings loader for this skill. Knows nothing about any specific option:
// everything it checks comes from the option definition in settings.schema.json, so
// adding, removing, or changing an option never requires editing this file.
//
// loadSettings(skillDir) -> { values: { "<dotted.key>": value, ... }, notices: [string, ...] }
//   - settings.jsonc missing           -> every default, no notice
//   - unreadable (bad JSON/not object)  -> every default, one notice
//   - key missing                      -> its default, no notice
//   - value breaks its type/constraint -> its default, one notice
//   - leaf key not in the definition   -> ignored, one notice

import path from "node:path";
import fs from "node:fs";
import { fileURLToPath } from "node:url";

const SETTINGS_FILE = "settings.jsonc";
const SCHEMA_FILE = "settings.schema.json";

// Remove // line comments and /* */ block comments, leaving string literals untouched
// (so values like "./exports" or URLs containing "//" survive).
export function stripJsonComments(text) {
  let out = "";
  let i = 0;
  let inString = false;
  while (i < text.length) {
    const ch = text[i];
    const next = text[i + 1];
    if (inString) {
      out += ch;
      if (ch === "\\") {
        out += next ?? "";
        i += 2;
        continue;
      }
      if (ch === '"') inString = false;
      i += 1;
    } else if (ch === '"') {
      inString = true;
      out += ch;
      i += 1;
    } else if (ch === "/" && next === "/") {
      while (i < text.length && text[i] !== "\n") i += 1;
    } else if (ch === "/" && next === "*") {
      i += 2;
      while (i < text.length && !(text[i] === "*" && text[i + 1] === "/")) i += 1;
      i += 2;
    } else {
      out += ch;
      i += 1;
    }
  }
  return out;
}

function isPlainObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function getPath(obj, dottedKey) {
  let node = obj;
  for (const part of dottedKey.split(".")) {
    if (!isPlainObject(node) || !Object.prototype.hasOwnProperty.call(node, part)) {
      return { found: false };
    }
    node = node[part];
  }
  return { found: true, value: node };
}

// Every leaf (non-object value) path in the user's file, e.g. "png.scale".
function leafPaths(obj, prefix = "") {
  const paths = [];
  for (const [key, value] of Object.entries(obj)) {
    const full = prefix ? `${prefix}.${key}` : key;
    if (isPlainObject(value)) paths.push(...leafPaths(value, full));
    else paths.push(full);
  }
  return paths;
}

function isValid(option, value) {
  switch (option.type) {
    case "enum":
      return option.values.includes(value);
    case "boolean":
      return typeof value === "boolean";
    case "number":
      return (
        typeof value === "number" &&
        Number.isFinite(value) &&
        (option.min === undefined || value > option.min)
      );
    case "relativePath":
      return (
        typeof value === "string" &&
        value.trim() !== "" &&
        !/^[\\/~]/.test(value) &&
        !/^[A-Za-z]:/.test(value)
      );
    default:
      return false;
  }
}

function formatValue(value) {
  return typeof value === "string" ? value : JSON.stringify(value);
}

export function loadSettings(skillDir) {
  const schema = JSON.parse(fs.readFileSync(path.join(skillDir, SCHEMA_FILE), "utf-8"));
  const options = schema.options ?? [];
  const values = Object.fromEntries(options.map((option) => [option.key, option.default]));
  const notices = [];
  const notice = (text) => notices.push(`⚙️ 설정 안내: ${SETTINGS_FILE} — ${text}`);

  const settingsPath = path.join(skillDir, SETTINGS_FILE);
  if (!fs.existsSync(settingsPath)) {
    return { values, notices };
  }

  let user;
  try {
    user = JSON.parse(stripJsonComments(fs.readFileSync(settingsPath, "utf-8")));
  } catch {
    user = undefined;
  }
  if (!isPlainObject(user)) {
    notice("읽지 못해 모든 값을 기본값으로 사용");
    return { values, notices };
  }

  const known = new Set(options.map((option) => option.key));
  for (const option of options) {
    const { found, value } = getPath(user, option.key);
    if (!found) continue;
    if (isValid(option, value)) {
      values[option.key] = value;
    } else {
      notice(`\`${option.key}\` 값이 허용되지 않아 기본값 \`${formatValue(option.default)}\` 사용`);
    }
  }
  for (const leaf of leafPaths(user)) {
    if (!known.has(leaf)) notice(`알 수 없는 키 \`${leaf}\` 무시`);
  }

  return { values, notices };
}

// The skill directory is the parent of scripts/, wherever this file is imported from.
export const SKILL_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
