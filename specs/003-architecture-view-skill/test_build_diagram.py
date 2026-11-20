import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).parents[2] / ".agents/skills/generating-architecture-views/scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from build_diagram import build  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
