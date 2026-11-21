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
FORMAT_KEYS = ("declarationMarkers", "fileExtensions", "functionParentheses")


def schema_defaults(skill_dir):
    options = json.loads((skill_dir / "settings.schema.json").read_text(encoding="utf-8"))["options"]
    return {option["key"]: option["default"] for option in options}


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
        defaults = schema_defaults(skill_dir)  # the schema is the only source of default values

        loaded = load_settings(skill_dir)
        self.assertEqual([], loaded["notices"])
        dependency = json.loads(strip_json_comments(
            (skill_dir / "settings.jsonc").read_text(encoding="utf-8")
        ))["dependency"]
        self.assertEqual(
            {name: defaults["dependency.nodeNameFormat." + name] for name in FORMAT_KEYS},
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

        defaults = schema_defaults(skill_dir)
        for name in FORMAT_KEYS:
            key = "dependency.nodeNameFormat." + name
            self.assertEqual(defaults[key], loaded["values"][key])
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


class SourceFileTagTest(unittest.TestCase):
    # The file node and the class inside it share the base name; only the class gets a tag.
    VIEW = [
        "flowchart LR",
        '  Memo_kt@{ label: "Memo.kt" }',
        "  Memo",
        '  save@{ label: "✨&nbsp;<b>save()</b>" }',
        "  Plain",
        "",
        "  Memo_kt -->|선언| Memo",
        "  Memo -->|호출| save",
        "  save -->|호출| Plain",
        "",
        '  click Memo_kt "../src/Memo.kt" "Memo.kt"',
        '  click Memo "../src/Memo.kt" "Memo.kt"',
        '  click save "https://example.com/blob/main/src/Store.kt#L10" "Store.kt"',
    ]

    def test_tags_linked_declarations_but_not_the_file_itself(self):
        out = build(self.VIEW, "", "right")

        self.assertIn('  Memo_kt@{ label: "Memo.kt" }', out)
        self.assertIn('  Memo@{ label: "<span class=srcFile>Memo.kt</span>Memo" }', out)
        self.assertIn('  save@{ label: "<span class=srcFile>Store.kt</span>✨&nbsp;<b>save()</b>" }', out)
        self.assertIn("  Plain", out)
        self.assertIn("text-align: right;", next(line for line in out if "themeCSS" in line))

    def test_left_position_and_disabled_tag(self):
        self.assertIn("text-align: left;", next(line for line in build(self.VIEW, "", "left") if "themeCSS" in line))
        plain = build(self.VIEW, "", "")
        self.assertFalse(any("srcFile" in line for line in plain))

    def test_file_extension_off_strips_only_the_file_node(self):
        out = build(self.VIEW, "", "right", file_extensions=False)

        self.assertIn('  Memo_kt@{ label: "Memo" }', out)
        self.assertIn('  Memo@{ label: "<span class=srcFile>Memo.kt</span>Memo" }', out)

    def test_hover_reads_the_base_name_through_the_tag(self):
        from hover.view_parser import clean_name

        self.assertEqual("save", clean_name("<span class=srcFile>Store.kt</span>✨&nbsp;<b>save()</b>"))


if __name__ == "__main__":
    unittest.main()
