#!/usr/bin/env node
// Print this skill's resolved settings and any settings notices as one line of JSON:
//   {"values": {"<dotted.key>": value, ...}, "notices": ["⚙️ 설정 안내: ...", ...]}
// SKILL.md runs this first to decide which questions to ask and relays the notices.
// Settings problems never fail this script — it always exits 0.

import { loadSettings, SKILL_DIR } from "./lib/settings.js";

console.log(JSON.stringify(loadSettings(SKILL_DIR)));
