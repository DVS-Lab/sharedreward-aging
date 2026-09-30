import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
import run_full_analysis as workflow


def write_table(path, fields, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t")
        writer.writeheader(); writer.writerows(rows)


class FullAnalysis(unittest.TestCase):
    def test_seed_resampling_is_once_per_subject_and_restartable(self):
        import nibabel as nib
        import numpy as np
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / "masks").mkdir()
            seed = root / "masks/seed-vs.nii.gz"
            nib.save(nib.Nifti1Image(np.ones((2, 2, 2)), np.eye(4) * [2, 2, 2, 1]), seed)
            bold = root / "bold.nii.gz"
            nib.save(nib.Nifti1Image(np.ones((3, 3, 3, 2)), np.eye(4)), bold)
            manifest = root / "manifest.tsv"
            write_table(manifest, ("dataset", "subject", "run", "input"), [
                dict(dataset="rf1", subject="10668", run=str(run), input=str(bold)) for run in (1, 2)])
            def fake_command(argv):
                if argv[0] == "flirt":
                    nib.save(nib.Nifti1Image(np.ones((3, 3, 3)), np.eye(4)), argv[-1])
            with patch.object(workflow, "ROOT", root), patch.object(workflow, "FSL", root / "fsl"), patch.object(workflow, "command", side_effect=fake_command) as commands:
                workflow.prepare_seed_caches(manifest)
                workflow.prepare_seed_caches(manifest)
            self.assertEqual(commands.call_count, 2)
            self.assertIn("nearestneighbour", commands.call_args_list[1].args[0])

    def test_repair_selection_requires_both_runs_and_exact_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, dest = root / "all.tsv", root / "selected.tsv"
            fields = ("dataset", "subject", "session", "run")
            rows = [dict(zip(fields, ("rf1", "10668", "01", "1")))]
            write_table(source, fields, rows)
            with self.assertRaisesRegex(ValueError, "stale inventory"):
                workflow.select_10668(source, dest)
            rows.append(dict(zip(fields, ("rf1", "10668", "01", "2"))))
            rows.append(dict(zip(fields, ("rf1", "10668", "02", "1"))))
            write_table(source, fields, rows)
            self.assertEqual(len(workflow.select_10668(source, dest)), 2)

    def test_only_reviewed_models_are_retired_and_recoverable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fsl, backup = root / "fsl", root / "backup"
            paths = {}
            for subject in ("10657", "10668", "144"):
                for run in (1, 2):
                    row = dict(dataset="rf1", subject=subject, session="01", run=run)
                    path = workflow.l1_path(fsl, row, "act")
                    path.mkdir(parents=True); (path / "marker").write_text("preserved")
                    paths[subject, run] = path
            with patch.object(workflow, "FSL", fsl):
                workflow.retire_reviewed_models(backup)
            for key in (("10657", 1), ("10668", 1), ("10668", 2)):
                self.assertFalse(paths[key].exists())
                self.assertEqual((backup / "models" / paths[key].relative_to(fsl) / "marker").read_text(), "preserved")
            self.assertTrue(paths["10657", 2].exists())
            self.assertTrue(paths["144", 1].exists())

    def test_changed_prepared_input_blocks_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); value = root / "input"; value.write_text("old")
            receipt = root / "prepared.json"
            receipt.write_text(json.dumps(dict(inputs=[workflow.fingerprint(value)], images=[])))
            value.write_text("changed")
            with self.assertRaisesRegex(ValueError, "Prepared input changed"):
                workflow.check_receipt(receipt)

    def test_models_are_paired_and_l2_waits_for_l1_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); calls = []
            def fake_run(script, *args, **kwargs):
                calls.append((script, args))
                if script == "audit_group_readiness.py":
                    report = args[args.index("--report-dir") + 1]
                    report.mkdir()
                    (report / "summary.json").write_text(json.dumps({"counts": {"l1": {"verified": 4}}, "computational_gate_passed": True}))
            with patch.object(workflow, "check_receipt", return_value={"l1": "l1.tsv", "l2": "l2.tsv"}), patch.object(workflow, "run", side_effect=fake_run), patch.object(workflow, "prepare_seed_caches") as caches:
                workflow.models(root / "receipt", root, "test", 25, 5)
            caches.assert_called_once_with("l1.tsv")
            self.assertEqual([c[0] for c in calls], ["audit_group_readiness.py", "run_L1stats.sh", "audit_group_readiness.py", "run_L2stats.sh", "audit_group_readiness.py"])
            for script, args in calls:
                if script.startswith("run_L"):
                    self.assertIn("--parallel-types", args)
                    self.assertNotIn("--overwrite", args)

    def test_unverified_existing_model_blocks_launch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); calls = []
            def fake_run(script, *args, **kwargs):
                calls.append(script)
                report = args[args.index("--report-dir") + 1]
                report.mkdir()
                (report / "summary.json").write_text(json.dumps({"counts": {"l1": {"unverified": 1}}, "computational_gate_passed": False}))
            with patch.object(workflow, "check_receipt", return_value={"l1": "l1.tsv", "l2": "l2.tsv"}), patch.object(workflow, "run", side_effect=fake_run):
                with self.assertRaisesRegex(ValueError, "no blanket overwrites"):
                    workflow.models(root / "receipt", root, "test", 25, 5)
            self.assertEqual(calls, ["audit_group_readiness.py"])


if __name__ == "__main__":
    unittest.main()
