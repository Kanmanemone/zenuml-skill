import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).parents[2] / ".agents/skills/generating-zenuml-diagrams"
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from apply_style import BLOCK, apply  # noqa: E402
from read_settings import load_settings, strip_json_comments  # noqa: E402

FENCE = "```mermaid\nzenuml\nA.run() {\n  // state = 1\n  B.go()\n}\n```\n"


class ApplyStyleTest(unittest.TestCase):
    def test_readable_appends_one_block_after_the_fence(self):
        out = apply(FENCE, "readable")
        self.assertTrue(out.startswith(FENCE))
        self.assertEqual(1, out.count('<details class="zenuml-style">'))
        self.assertTrue(out.endswith(BLOCK))

    def test_reapplying_replaces_instead_of_duplicating(self):
        once = apply(FENCE, "readable")
        self.assertEqual(once, apply(once, "readable"))

    def test_default_style_removes_the_block_and_keeps_the_fence(self):
        self.assertEqual(FENCE, apply(apply(FENCE, "readable"), "zenuml-default"))
        self.assertEqual(FENCE, apply(FENCE, "zenuml-default"))

    def test_command_line_value_overrides_setting_and_bad_value_falls_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "flow.md"
            path.write_text(FENCE, encoding="utf-8")
            script = str(SKILL_DIR / "scripts/apply_style.py")
            run = lambda *args: subprocess.run([sys.executable, script, str(path), *args],
                                               capture_output=True, text=True, encoding="utf-8")
            run("--style=zenuml-default")
            self.assertEqual(FENCE, path.read_text(encoding="utf-8"))
            result = run("--style=fancy")
            self.assertIn("⚙️ 설정 안내", result.stdout)
            expected = apply(FENCE, load_settings(SKILL_DIR)["values"]["diagram.style"])
            self.assertEqual(expected, path.read_text(encoding="utf-8"))

    def test_shipped_setting_matches_schema_default(self):
        options = json.loads((SKILL_DIR / "settings.schema.json").read_text(encoding="utf-8"))["options"]
        default = next(o["default"] for o in options if o["key"] == "diagram.style")
        shipped = json.loads(strip_json_comments((SKILL_DIR / "settings.jsonc").read_text(encoding="utf-8")))
        self.assertEqual(default, shipped["diagram"]["style"])
        self.assertEqual([], load_settings(SKILL_DIR)["notices"])


if __name__ == "__main__":
    unittest.main()
