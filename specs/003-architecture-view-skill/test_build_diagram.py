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

    def test_marks_linked_declarations_and_links_their_labels(self):
        out = build(self.VIEW, "")

        self.assertIn('  Memo_kt@{ label: "<a href=\'../src/Memo.kt\'>Memo.kt</a>" }', out)
        self.assertIn('  Memo@{ label: "<a href=\'../src/Memo.kt\'>Memo</a>" }', out)
        self.assertIn('  save@{ label: "<a href=\'https://example.com/blob/main/src/Store.kt#L10\'>✨&nbsp;<b>save()</b></a>" }', out)
        self.assertIn("  Plain", out)  # no link, untouched
        self.assertIn("  class Memo,save srcFile", out)
        self.assertFalse(any("srcFile" in line for line in out if "label" in line or "themeCSS" in line))

    def test_file_extension_off_strips_only_the_file_node(self):
        out = build(self.VIEW, "", file_extensions=False)

        self.assertIn('  Memo_kt@{ label: "<a href=\'../src/Memo.kt\'>Memo</a>" }', out)
        self.assertIn("  class Memo,save srcFile", out)

    def test_link_target_quotes_are_escaped_and_names_still_read(self):
        # VS Code's preview opens only HTML links, so every linked label carries one
        # (bug architecture-view-local-link-click); the name readers must look through it.
        from hover.view_parser import clean_name

        view = ["flowchart LR", "  A", "  B", "", "  A -->|호출| B", "",
                '  click A "https://example.com/a?x=1&y=it\'s" "a"']
        out = build(view, "")
        self.assertIn('  A@{ label: "<a href=\'https://example.com/a?x=1&amp;y=it&#39;s\'>A</a>" }', out)
        self.assertEqual(clean_name("<a href='../x.kt'>♻️&nbsp;<b>fun&nbsp;Foo()</b></a>"), "Foo")

    def _hover(self, text=None, **values):
        from apply_hover import transform

        if text is None:
            text = "### Dependency\n\n```mermaid\n" + "\n".join(build(self.VIEW, "", file_extensions=False)) + "\n```\n"
        settings = load_settings(SCRIPT_DIR.parent)["values"]
        settings.update({"hover.enabled": False, "dependency.sourceFile.enabled": True,
                         "dependency.sourceFile.position": "right"}, **values)
        return transform(text, settings)[0]

    def test_style_block_draws_names_for_marked_nodes_only(self):
        out = self._hover()
        style = out[out.index('<details class="zenuml-hover-style">'):]

        # node rules: file name in the node's own border color (classDef stroke)
        self.assertIn('.srcFile.memoNode .nodeLabel::before { content: "Memo.kt"; color: #56B4E9; }', style)
        self.assertIn('.srcFile.saveNode .nodeLabel::before { content: "Store.kt"; color: #009E73; }', style)
        # shared rule once: on the top border, node-fill background, italic; classic look overrides offsets
        self.assertEqual(1, style.count("top: -18px; right: -5px;"))
        self.assertIn("font-style: italic;", style)
        self.assertIn("background-color: var(--vscode-editorWidget-background, #ffffff);", style)
        self.assertIn('[data-look="classic"] .node.srcFile .nodeLabel::before, .node.srcFile[data-look="classic"]'
                      " .nodeLabel::before { top: -21px; right: -19px; }", style)
        self.assertNotIn("memo_ktNode .nodeLabel", style)
        self.assertNotIn("div.mermaidTooltip", style)
        self.assertEqual(out, self._hover(out))

    def test_left_center_and_disabled(self):
        left = self._hover(**{"dependency.sourceFile.position": "left"})
        self.assertIn("top: -18px; left: -5px;", left)
        self.assertIn("{ top: -21px; left: -19px; }", left)
        center = self._hover(**{"dependency.sourceFile.position": "center"})
        self.assertIn("top: -18px; left: 50%; transform: translateX(-50%);", center)
        self.assertIn("{ top: -21px; }", center)
        self.assertNotIn("<details", self._hover(**{"dependency.sourceFile.enabled": False}))

    def _panels(self, nodes, names):
        """Hover-on result for a view whose body headings use base names."""
        body = "\n".join("- <strong>" + n + "</strong>\n  - <strong>책임 (추상)</strong>: " + n + " 책임\n"
                         "  - <strong>역할 (구체)</strong>: 설명에 명시되지 않음" for n in names)
        text = ("### Dependency\n\n```mermaid\n" + "\n".join(build(["flowchart LR"] + nodes, "")) + "\n```\n\n"
                "### Responsibility\n\n#### 요소의 책임\n\n" + body + "\n")
        return self._hover(text, **{"hover.enabled": True})

    def test_hover_matches_file_node_by_base_name(self):
        out = self._panels(['  SearchViewModelKt@{ label: "SearchViewModel.kt" }', "  Repo", "",
                            "  SearchViewModelKt -->|호출| Repo",
                            '  click SearchViewModelKt "../a/SearchViewModel.kt" "SearchViewModel.kt"'],
                           ["SearchViewModel"])
        click = next(l for l in out.splitlines() if l.strip().startswith("click SearchViewModelKt "))
        self.assertIn("SearchViewModel 책임", click)

    def test_exact_declaration_name_wins_over_file_stem(self):
        out = self._panels(['  Memo_kt@{ label: "Memo.kt" }', "  Memo", "", "  Memo_kt -->|선언| Memo",
                            '  click Memo_kt "../src/Memo.kt" "Memo.kt"', '  click Memo "../src/Memo.kt" "Memo.kt"'],
                           ["Memo"])
        memo = next(l for l in out.splitlines() if l.strip().startswith("click Memo "))
        file_node = next(l for l in out.splitlines() if l.strip().startswith("click Memo_kt "))
        self.assertIn("Memo 책임", memo)
        self.assertNotIn("Memo 책임", file_node)

if __name__ == "__main__":
    unittest.main()
