"""The reviewed source-validity exclusion is run-scoped, never participant-wide."""
import csv
from pathlib import Path
import unittest


class ReviewedDisposition(unittest.TestCase):
    def test_10657_only_run1(self):
        path = Path(__file__).resolve().parents[1] / "docs/curated_run_exclusions.tsv"
        with path.open() as f:
            rows = [r for r in csv.DictReader(f, delimiter="\t") if r["dataset"] == "rf1" and r["subject"] == "10657"]
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]["session"], rows[0]["run"]), ("01", "1"))
        self.assertEqual(rows[0]["exclusion_reason"], "wrong_friend_name")
