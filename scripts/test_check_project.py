"""Fault-injection checks against isolated copies; never alter the actual website."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_project.py"


class CheckerFaultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Windows sandbox tokens cannot enter Python's special mode-0700 temp
        # directories. Inherit the existing temp ACL instead.
        cls.temp_root = Path(tempfile.gettempdir()).resolve()
        cls.fixture = cls.temp_root / ("an3-check-" + uuid.uuid4().hex)
        cls.fixture.mkdir(mode=0o777)
        cls.addClassCleanup(cls.cleanup_fixture)
        for directory in ("en", "assets", "vendor"):
            shutil.copytree(ROOT / directory, cls.fixture / directory)
        shutil.copy2(ROOT / "index.html", cls.fixture / "index.html")

    @classmethod
    def cleanup_fixture(cls):
        target = cls.fixture.resolve()
        if target.parent != cls.temp_root or not re.fullmatch(r"an3-check-[0-9a-f]{32}", target.name):
            raise RuntimeError("unexpected fixture cleanup path")
        shutil.rmtree(target)

    def run_checker(self):
        result = subprocess.run([sys.executable, "-B", str(CHECKER), "--root", str(self.fixture), "--json"], text=True, encoding="utf-8", capture_output=True, timeout=60)
        self.assertIn(result.returncode, (0, 1), result.stderr)
        return result.returncode, json.loads(result.stdout)

    def mutation(self, relative, transform, expected_check):
        path = self.fixture / relative
        original = path.read_bytes()
        changed = transform(original.decode("utf-8"))
        self.assertNotEqual(changed, original.decode("utf-8"), "mutation was not applied")
        try:
            path.write_text(changed, encoding="utf-8")
            code, report = self.run_checker()
            self.assertEqual(code, 1, report)
            self.assertTrue(any(expected_check in row["name"] and row["status"] == "fail" for row in report["checks"]), report)
        finally:
            path.write_bytes(original)

    def test_current_bilingual_baseline_passes(self):
        code, report = self.run_checker()
        self.assertEqual(code, 0, report)
        self.assertEqual(report["passed"], report["total"])

    def test_invalid_javascript_is_rejected(self):
        self.mutation("index.html", lambda s: s.replace("const CONTENT_UNITS =", "const CONTENT_UNITS !", 1), "JavaScript syntax")

    def test_missing_qr_reference_is_rejected(self):
        self.mutation("en/index.html", lambda s: s.replace("../assets/qr-anku.png", "../assets/missing.png"), "local resources")

    def test_missing_anchor_is_rejected(self):
        self.mutation("index.html", lambda s: s.replace("</body>", '<a href="#missing-anchor">test</a></body>'), "anchors")

    def test_duplicate_html_id_is_rejected(self):
        self.mutation("index.html", lambda s: s.replace("</body>", '<i id="network"></i></body>'), "HTML / language / IDs")

    def test_bilingual_seed_drift_is_rejected(self):
        self.mutation("en/index.html", lambda s: re.sub(r'("seed":\s*)(\d+)', lambda m: m[1] + str(int(m[2]) + 1), s, count=1), "bilingual data")

    def test_english_removed_about_item_is_rejected(self):
        self.mutation("en/index.html", lambda s: s.replace('"id": "1-3"', '"id": "1-2"'), "content units")

    def test_merged_sources_are_required(self):
        self.mutation("en/index.html", lambda s: s.replace('"AN1:发展历程"', '"missing-source"', 1), "bilingual data")

    def test_chinese_publication_hint_is_required(self):
        self.mutation("index.html", lambda s: s.replace('查阅更多见公众号', 'missing-hint'), "language routes")

    def test_reordered_technology_ids_are_rejected(self):
        self.mutation("index.html", lambda s: s.replace('"id": "2-3"', '"id": "swap"').replace('"id": "2-2"', '"id": "2-3"').replace('"id": "swap"', '"id": "2-2"'), "content units")

    def test_reintroduced_removed_id_is_rejected(self):
        self.mutation("index.html", lambda s: s.replace('"id": "2-3"', '"id": "2-4"'), "content units")

    def test_wrong_section_with_same_counts_is_rejected(self):
        def swap_sections(text):
            text = text.replace('"sectionId": "technology"', '"sectionId": "swap"', 1)
            text = text.replace('"sectionId": "pipeline"', '"sectionId": "technology"', 1)
            return text.replace('"sectionId": "swap"', '"sectionId": "pipeline"', 1)
        self.mutation("index.html", swap_sections, "content units")

    def test_broken_language_route_is_rejected(self):
        self.mutation("index.html", lambda s: s.replace("location.href='./en/'", "location.href='./missing/'"), "language routes")

    def test_remote_runtime_script_is_rejected_without_fetching(self):
        self.mutation("index.html", lambda s: s.replace("</head>", '<script src="https://invalid.example/remote.js"></script></head>'), "local resources")


if __name__ == "__main__":
    unittest.main()
