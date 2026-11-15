#!/usr/bin/env python3
"""Print this skill's resolved settings and any settings notices as one line of JSON:
  {"values": {"<dotted.key>": value, ...}, "notices": ["⚙️ 설정 안내: ...", ...]}
SKILL.md runs this first and relays the notices. Settings problems never fail this
script — it always exits 0. Requires Python 3.9+, standard library only.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hover.settings import load_settings  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
print(json.dumps(load_settings(), ensure_ascii=False))
