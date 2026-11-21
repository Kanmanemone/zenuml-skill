import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = (
    ROOT / ".agents/skills/generating-architecture-views/scripts/append_feedback.py",
    ROOT / ".agents/skills/generating-zenuml-diagrams/scripts/append_feedback.py",
)


def load(path: Path):
    spec = importlib.util.spec_from_file_location(path.parent.parent.name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class AppendFeedbackTest(unittest.TestCase):
    def test_log_contract_for_both_skills(self):
        for script in SCRIPTS:
            with self.subTest(script=script):
                module = load(script)
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    output = root / "result.md"
                    log = root / "log/result.md"
                    request = root / "request.txt"

                    output.write_text("first output\n", encoding="utf-8")
                    request.write_text("first request\n", encoding="utf-8")
                    self.assertEqual(
                        module.append_feedback(output, log, request, "new", "2026-11-21"),
                        1,
                    )
                    self.assertFalse(request.exists())
                    first_round = log.read_bytes()

                    output.write_text("second output\n", encoding="utf-8")
                    request.write_text("second request\n", encoding="utf-8")
                    self.assertEqual(
                        module.append_feedback(output, log, request, "append", "2026-11-22"),
                        2,
                    )
                    self.assertTrue(log.read_bytes().startswith(first_round))
                    self.assertEqual(
                        log.read_text(encoding="utf-8"),
                        "## Round 1 — 2026-11-21\n"
                        "**Request**: first request\n\n"
                        "**Response**:\nfirst output\n\n"
                        "## Round 2 — 2026-11-22\n"
                        "**Request**: second request\n\n"
                        "**Response**:\nsecond output\n",
                    )

    def test_append_without_current_log_starts_round_one(self):
        module = load(SCRIPTS[0])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "result.md"
            log = root / "new-location/result.md"
            request = root / "request.txt"
            output.write_text("output", encoding="utf-8")
            request.write_text("request", encoding="utf-8")

            self.assertEqual(
                module.append_feedback(output, log, request, "append", "2026-11-21"),
                1,
            )


if __name__ == "__main__":
    unittest.main()
