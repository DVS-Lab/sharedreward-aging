import csv
import importlib.util
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_analysis_cohort", ROOT / "code/build_analysis_cohort.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def write_tsv(path, fields, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def read_tsv(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


class CohortTest(unittest.TestCase):
    def test_source_misses_task_invalid_ratings_and_review_are_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            analysis = root / "analysis.tsv"
            events = root / "events.tsv"
            missing = root / "missing.tsv"
            ratings = root / "ratings.tsv"
            curated = root / "curated.tsv"
            ids = [
                ("rf1", "11969", "01", "1"),
                ("rf1", "11969", "01", "2"),
                ("rf1", "12020", "01", "1"),
                ("rf1", "12020", "01", "2"),
                ("rf1", "12041", "01", "1"),
                ("rf1", "11539", "01", "1"),
                ("rf1", "11539", "01", "2"),
                ("rf1", "10606", "01", "1"),
                ("rf1", "11201", "01", "1"),
            ]
            write_tsv(
                analysis,
                MODULE.IDENTIFIERS + ("input", "mask", "confounds", "qc_flags"),
                [
                    {
                        "dataset": d,
                        "subject": s,
                        "session": se,
                        "run": r,
                        "input": f"bold-{s}-{r}",
                        "mask": f"mask-{s}-{r}",
                        "confounds": f"confounds-{s}-{r}",
                        "qc_flags": "",
                    }
                    for d, s, se, r in ids
                ],
            )
            event_rows = []
            missing_keys = {("rf1", "11969", "01", "1"), ("rf1", "11969", "01", "2"), ("rf1", "12020", "01", "1")}
            for d, s, se, r in ids:
                if (d, s, se, r) in missing_keys:
                    continue
                event_rows.append(
                    {
                        "dataset": d,
                        "subject": s,
                        "session": se,
                        "run": r,
                        "source_events": f"source-{s}-{r}",
                        "harmonized_events": f"events-{s}-{r}",
                        "missed_trial_fraction": "0.3" if s == "12041" else "0",
                        "zero_count_conditions": "event_friend_neutral" if s == "11201" else "",
                        "exclude_run": "true" if s == "12041" else "false",
                        "exclusion_reason": "missed_trials_gt_25pct" if s == "12041" else "",
                    }
                )
            write_tsv(
                events,
                MODULE.IDENTIFIERS
                + (
                    "source_events",
                    "harmonized_events",
                    "missed_trial_fraction",
                    "zero_count_conditions",
                    "exclude_run",
                    "exclusion_reason",
                ),
                event_rows,
            )
            write_tsv(
                missing,
                MODULE.IDENTIFIERS + ("problems",),
                [
                    {"dataset": d, "subject": s, "session": se, "run": r, "problems": "missing_source_events"}
                    for d, s, se, r in sorted(missing_keys)
                ],
            )
            write_tsv(
                ratings,
                ("dataset", "subject", "exclude_subject", "exclusion_reason"),
                [
                    {
                        "dataset": "rf1",
                        "subject": subject,
                        "exclude_subject": "true" if subject == "10606" else "false",
                        "exclusion_reason": "missing_ratings_file" if subject == "10606" else "",
                    }
                    for subject in sorted({row[1] for row in ids})
                ],
            )
            write_tsv(
                curated,
                MODULE.IDENTIFIERS + ("exclusion_reason", "source", "note"),
                [{"dataset": "rf1", "subject": "11539", "session": "01", "run": "*", "exclusion_reason": "wrong_friend_photo", "source": "notes", "note": "invalid"}],
            )
            paths = {name: root / f"{name}.tsv" for name in ("l1_task", "l1_ratings", "l1_review", "dispositions", "l2_task", "l2_ratings", "subjects")}
            args = Namespace(
                analysis_qc=analysis,
                event_qc=events,
                event_source_missing=missing,
                ratings_qc=ratings,
                curated_exclusions=curated,
                l1_task_output=paths["l1_task"],
                l1_ratings_output=paths["l1_ratings"],
                l1_review_output=paths["l1_review"],
                run_disposition_output=paths["dispositions"],
                l2_task_output=paths["l2_task"],
                l2_ratings_output=paths["l2_ratings"],
                subject_output=paths["subjects"],
            )
            MODULE.build(args)

            task = {(row["subject"], row["run"]) for row in read_tsv(paths["l1_task"])}
            self.assertIn(("12020", "2"), task)
            self.assertNotIn(("12020", "1"), task)
            self.assertIn(("10606", "1"), task)
            self.assertNotIn(("11539", "1"), task)
            self.assertNotIn(("12041", "1"), task)
            self.assertEqual({row["subject"] for row in read_tsv(paths["l1_review"])}, {"11201"})
            self.assertNotIn("10606", {row["subject"] for row in read_tsv(paths["l1_ratings"])})
            l2 = {row["subject"]: row for row in read_tsv(paths["l2_task"])}
            self.assertNotIn("11969", l2)
            self.assertEqual(l2["12020"]["runs"], "2")
            self.assertNotIn("11539", l2)
            self.assertNotIn("12041", l2)
            self.assertNotIn("11201", l2)


if __name__ == "__main__":
    unittest.main()
