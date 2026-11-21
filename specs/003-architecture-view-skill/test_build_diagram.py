import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).parents[2] / ".agents/skills/generating-architecture-views/scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from build_diagram import build  # noqa: E402
from hover.settings import load_settings, strip_json_comments  # noqa: E402


BASE = ["flowchart LR", "  A", "  B", "", "  A -->|호출| B"]
LEGEND = '  CrudLegend@{ shape: text, label: "✨: 추가<br/>♻️: 변경<br/>🗑️: 삭제" }'


class CrudLegendTest(unittest.TestCase):
    def test_omits_legend_without_change_marks(self):
        self.assertNotIn(LEGEND, build(BASE, ""))

    def test_adds_all_three_lines_for_any_change_mark(self):
        for crud_class in ("crudCreate", "crudUpdate", "crudDelete"):
            with self.subTest(crud_class=crud_class):
                result = build(BASE + ["", f"  class A {crud_class}"], "")

                self.assertEqual(1, result.count(LEGEND))


class NodeNameFormatSettingsTest(unittest.TestCase):
    def test_shipped_settings_and_defaults_use_one_format_family(self):
        skill_dir = SCRIPT_DIR.parent
        expected = {
            "dependency.nodeNameFormat.declarationMarkers": False,
            "dependency.nodeNameFormat.fileExtensions": True,
            "dependency.nodeNameFormat.functionParentheses": True,
        }

        loaded = load_settings(skill_dir)
        self.assertEqual(expected, {key: loaded["values"][key] for key in expected})
        dependency = json.loads(strip_json_comments(
            (skill_dir / "settings.jsonc").read_text(encoding="utf-8")
        ))["dependency"]
        self.assertEqual(
            {"declarationMarkers": False, "fileExtensions": True, "functionParentheses": True},
            dependency["nodeNameFormat"],
        )
        self.assertNotIn("nodeMarkers", dependency)
        self.assertNotIn("functionParentheses", dependency)

    def test_removed_flat_keys_are_ignored_with_notices(self):
        skill_dir = SCRIPT_DIR.parent
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "settings.schema.json").write_text(
                (skill_dir / "settings.schema.json").read_text(encoding="utf-8"), encoding="utf-8"
            )
            (root / "settings.jsonc").write_text(
                '{"dependency":{"nodeMarkers":true,"functionParentheses":false}}', encoding="utf-8"
            )

            loaded = load_settings(root)

        self.assertFalse(loaded["values"]["dependency.nodeNameFormat.declarationMarkers"])
        self.assertTrue(loaded["values"]["dependency.nodeNameFormat.fileExtensions"])
        self.assertTrue(loaded["values"]["dependency.nodeNameFormat.functionParentheses"])
        self.assertTrue(any("dependency.nodeMarkers" in notice for notice in loaded["notices"]))
        self.assertTrue(any("dependency.functionParentheses" in notice for notice in loaded["notices"]))

    def test_all_format_setting_combinations_are_independent(self):
        skill_dir = SCRIPT_DIR.parent
        schema = (skill_dir / "settings.schema.json").read_text(encoding="utf-8")
        keys = ("declarationMarkers", "fileExtensions", "functionParentheses")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "settings.schema.json").write_text(schema, encoding="utf-8")
            for mask in range(8):
                expected = {key: bool(mask & (1 << i)) for i, key in enumerate(keys)}
                (root / "settings.jsonc").write_text(
                    json.dumps({"dependency": {"nodeNameFormat": expected}}), encoding="utf-8"
                )

                loaded = load_settings(root)

                self.assertEqual(
                    expected,
                    {key: loaded["values"]["dependency.nodeNameFormat." + key] for key in keys},
                )
                self.assertEqual([], loaded["notices"])


if __name__ == "__main__":
    unittest.main()
