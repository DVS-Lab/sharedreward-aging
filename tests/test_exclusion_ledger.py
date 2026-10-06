import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import nibabel as nib
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

import apply_ledger_decisions  # noqa: E402
import build_exclusion_ledger as builder  # noqa: E402
import resolve_exclusion_ledger as resolver  # noqa: E402


def ledger_row(subject, run, criterion, disposition="pending_review", **fields):
    unit = {"dataset": "rf1", "subject": subject, "session": "01", "run": run}
    row = builder.make_row(
        unit,
        criterion,
        applies_to="imaging_all",
        decision_basis="reviewer",
        disposition=disposition,
    )
    row.update(fields)
    return row


RUN_KEYS = {("rf1", "1", "01", "1"), ("rf1", "1", "01", "2"), ("rf1", "2", "01", "1")}
SUBJECT_KEYS = {key[:3] for key in RUN_KEYS}


class LedgerValidation(unittest.TestCase):
    def test_unmatched_and_incomplete_rows_fail(self):
        typo = ledger_row("9", "1", "manual_x", "exclude", origin="manual",
                          reviewer="R", review_date="2026-10-05", rationale="r")
        incomplete = ledger_row("1", "1", "manual_y", "exclude", origin="manual")
        incomplete["decision_basis"] = ""
        with self.assertRaises(SystemExit) as raised:
            builder.validate([typo, incomplete], RUN_KEYS, SUBJECT_KEYS)
        message = str(raised.exception)
        self.assertIn("matches no run", message)
        self.assertIn("decision_basis ''", message)
        self.assertIn("needs reviewer", message)

    def test_merge_keeps_decisions_notes_and_manual_rows(self):
        decided = ledger_row("1", "1", "high_mean_fd_iqr_outlier", "exclude",
                             reviewer="R", review_date="2026-10-05", rationale="rule")
        noted = ledger_row("1", "2", "low_coverage_iqr_outlier", rationale="borderline")
        manual = ledger_row("2", "*", "manual_visual_qc", "exclude", origin="manual",
                            reviewer="R", review_date="2026-10-05", rationale="artifact")
        seeded = [
            ledger_row("1", "1", "high_mean_fd_iqr_outlier"),
            ledger_row("1", "2", "low_coverage_iqr_outlier"),
        ]
        merged = {row["ledger_id"]: row for row in builder.merge(seeded, [decided, noted, manual])}
        self.assertEqual(merged[decided["ledger_id"]]["disposition"], "exclude")
        self.assertEqual(merged[noted["ledger_id"]]["rationale"], "borderline")
        self.assertIn(manual["ledger_id"], merged)


class DecisionFiles(unittest.TestCase):
    def test_decisions_apply_once_and_only_to_pending_rows(self):
        ledger = [ledger_row("1", "1", "high_mean_fd_iqr_outlier")]
        decision = {"ledger_id": ledger[0]["ledger_id"], "disposition": "exclude",
                    "reviewer": "R", "review_date": "2026-10-05", "rationale": "rule"}
        apply_ledger_decisions.apply(ledger, [decision])
        self.assertEqual(ledger[0]["disposition"], "exclude")
        with self.assertRaises(SystemExit):
            apply_ledger_decisions.apply(ledger, [decision])
        with self.assertRaises(SystemExit):
            apply_ledger_decisions.apply(ledger, [{**decision, "ledger_id": "missing"}])


class Resolver(unittest.TestCase):
    def setUp(self):
        self.l1 = [
            {"dataset": "rf1", "subject": "1", "session": "01", "run": "1", "input": "a"},
            {"dataset": "rf1", "subject": "1", "session": "01", "run": "2", "input": "b"},
            {"dataset": "rf1", "subject": "2", "session": "01", "run": "1", "input": "c"},
        ]
        self.l2 = [
            {"dataset": "rf1", "subject": "1", "session": "01", "runs": "1,2",
             "subject_level_strategy": "fixed_effects"},
            {"dataset": "rf1", "subject": "2", "session": "01", "runs": "1",
             "subject_level_strategy": "l1_passthrough"},
        ]

    def test_exclusions_drive_strategy_and_rebuilds(self):
        ledger = [
            ledger_row("1", "2", "high_mean_fd_iqr_outlier", "exclude"),
            ledger_row("2", "1", "low_coverage_iqr_outlier"),
        ]
        retained, l2, status = resolver.resolve(ledger, self.l1, self.l2, "retain")
        self.assertEqual([row["input"] for row in retained], ["a", "c"])
        first = status[0]
        self.assertEqual((first["retained_runs"], first["strategy"], first["change"]),
                         ("1", "l1_passthrough", "runs_removed"))
        self.assertIn("rf1_phase_resolved_act", first["rebuild_families"])
        self.assertEqual(len(l2), 2)
        _, l2, status = resolver.resolve(ledger, self.l1, self.l2, "exclude")
        self.assertEqual(status[1]["change"], "subject_removed")
        self.assertEqual(len(l2), 1)

    def test_ratings_rows_never_remove_runs(self):
        ratings = builder.make_row(
            {"dataset": "rf1", "subject": "1", "session": "01"},
            "ratings_identical_ratings",
            applies_to="ratings_qualified",
            decision_basis="automatic_rule",
            disposition="exclude",
        )
        retained, l2, _ = resolver.resolve([ratings], self.l1, self.l2, "retain")
        self.assertEqual(len(retained), 3)
        self.assertEqual(l2[0]["ratings_eligible"], "false")

    def test_candidates_repoint_single_run_subjects_to_verified_l1(self):
        ledger = [ledger_row("1", "2", "high_mean_fd_iqr_outlier", "exclude")]
        _, _, status = resolver.resolve(ledger, self.l1, self.l2, "retain")
        candidates = [
            {"dataset": "rf1", "subject": subject, "session": "01", "type": "act",
             "runs": runs, "strategy": "s", "cope": "4", "cope_path": "p",
             "varcope_path": "v", "mask_path": "m", "ratings_eligible": "true"}
            for subject, runs in (("1", "1,2"), ("2", "1"))
        ]
        feats = resolver.verified_l1([
            {"dataset": "rf1", "subject": "1", "session": "01", "type": "act",
             "run": "1", "status": "verified", "path": "/l1/run-1.feat"},
        ])
        rows = resolver.filter_candidates(candidates, status, feats)
        self.assertEqual(rows[0]["input_status"], "l1_passthrough_verified")
        self.assertEqual(rows[0]["cope_path"], "/l1/run-1.feat/stats/cope4.nii.gz")
        self.assertEqual(rows[0]["runs"], "1")
        self.assertEqual(rows[1]["input_status"], "frozen_valid")
        # Without a verified L1 the subject must be rebuilt, never left on old paths.
        rows = resolver.filter_candidates(candidates, status, {})
        self.assertEqual(rows[0]["input_status"], "requires_rebuild")
        self.assertEqual(rows[0]["cope_path"], "")


class RoiCoverage(unittest.TestCase):
    def test_roi_coverage_and_missing_location(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            affine = np.diag([2.0, 2.0, 2.0, 1.0])
            eligible = np.ones((10, 10, 10), dtype=np.uint8)
            run_mask = eligible.copy()
            run_mask[:, :, :2] = 0  # lose the two most inferior slices
            roi = np.zeros((10, 10, 10), dtype=np.uint8)
            roi[4:6, 4:6, 1:3] = 1  # half the ROI sits in a lost slice
            paths = {}
            for name, data in (("run", run_mask), ("eligible", eligible), ("roi", roi)):
                paths[name] = directory / f"{name}.nii.gz"
                nib.save(nib.Nifti1Image(data, affine), paths[name])
            table = directory / "units.tsv"
            with table.open("w", newline="") as handle:
                writer = csv.writer(handle, delimiter="\t")
                writer.writerow(["dataset", "subject", "session", "run", "mask", "coverage_mask"])
                writer.writerow(["rf1", "1", "01", "1", paths["run"], paths["eligible"]])
            output = directory / "out.tsv"
            result = subprocess.run(
                [sys.executable, str(ROOT / "code/audit_roi_coverage.py"),
                 "--input", str(table), "--roi", f"vs={paths['roi']}",
                 "--output", str(output)],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with output.open(newline="") as handle:
                row = next(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual(row["vs_voxels"], "8")
            self.assertEqual(float(row["vs_coverage_pct"]), 50.0)
            self.assertEqual(int(row["missing_eligible_voxels"]), 200)
            self.assertEqual(float(row["missing_z_max_mm"]), 2.0)


if __name__ == "__main__":
    unittest.main()
