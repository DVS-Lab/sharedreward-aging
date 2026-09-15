import hashlib
import json
import subprocess
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
import build_event_qc_manifest as source
import model_provenance as provenance
from recover_sub144_analysis import archive_incomplete, select_manifest
import recover_sub144_analysis as recovery
from run_event_qc_batch import summarize, validate


class RecoveryTest(unittest.TestCase):
    def test_cohort_preparation_generates_and_audits_confounds_first(self):
        with patch.object(recovery, "run") as run:
            root = Path("/synthetic")
            recovery.prepare_cohort(root / "records", root / "lists", root / "custom-confounds")
            calls = [call.args for call in run.call_args_list]
            self.assertEqual([call[0] for call in calls], [
                "build_fsl_confounds_manifest.py", "run_fsl_confounds_batch.py",
                "audit_fsl_confounds.py", "build_analysis_cohort.py"])
            self.assertEqual(calls[0][-1], root / "custom-confounds")
            self.assertNotIn("--overwrite", calls[1])
            self.assertIn("--fail-on-incomplete", calls[2])
            self.assertEqual(calls[3], ("build_analysis_cohort.py", "--ds-confounds-root", root / "custom-confounds"))

    def test_failed_confounds_audit_prevents_cohort_freeze(self):
        error = subprocess.CalledProcessError(1, "audit_fsl_confounds.py")
        with patch.object(recovery, "run", side_effect=[None, None, error]) as run:
            with self.assertRaises(subprocess.CalledProcessError):
                recovery.prepare_cohort(Path("/records"), Path("/lists"), Path("/confounds"))
            self.assertEqual(run.call_count, 3)

    def test_sub144_requires_verified_repair_but_other_subjects_unchanged(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            args = SimpleNamespace(ds003745_root=root / "old", srndna_datapaper_root=root / "upstream")
            row = dict(dataset="ds003745", subject="144", session="", run="1")
            with self.assertRaisesRegex(ValueError, "requires hash-verified"):
                source.source_path(args, row)
            repaired = args.srndna_datapaper_root / "bids/sub-144/func/sub-144_task-sharedreward_run-01_events.tsv"
            repaired.parent.mkdir(parents=True)
            repaired.write_text("verified repair")
            digest = hashlib.sha256(repaired.read_bytes()).hexdigest()
            with patch.dict(source.SUB144_SHA256, {"01": digest}):
                self.assertEqual(source.source_path(args, row), repaired)
                repaired.write_text("unexpected revision")
                with self.assertRaises(ValueError):
                    source.source_path(args, row)
            row["subject"] = "143"
            self.assertEqual(source.source_path(args, row), args.ds003745_root / "sub-143/func/sub-143_task-sharedreward_run-01_events.tsv")

    def test_source_content_change_invalidates_existing_event_qc(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            unit = dict(dataset="ds003745", subject="144", session="", run="01",
                        source_events=str(root / "source.tsv"), harmonized_events=str(root / "events.tsv"), output_json=str(root / "qc.json"))
            Path(unit["source_events"]).write_text("original")
            Path(unit["harmonized_events"]).write_text("onset\tduration\ttrial_type\n0\t3.5\tevent_computer_reward\n")
            rows = [dict(onset="0", duration="3.5", trial_type="event_computer_reward")]
            Path(unit["output_json"]).write_text(json.dumps(summarize(rows, unit)))
            validate(unit)
            Path(unit["source_events"]).write_text("corrected")
            with self.assertRaisesRegex(ValueError, "source_sha256"):
                validate(unit)

    def test_missing_stamp_old_contrasts_and_changed_inputs_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "model.feat"; output.mkdir()
            ev = root / "ev.txt"; ev.write_text("0 3.5 1\n")
            image = root / "bold.nii.gz"; image.write_bytes(b"image")
            (output / "design.con").write_text("/NumContrasts 22\n/Matrix\n")
            with self.assertRaises(OSError):
                provenance.validate_model(output, "l1", "act")
            stamp = output / provenance.STAMP
            stamp.write_text(json.dumps(provenance.snapshot("l1", "act", [ev], [image], [])))
            provenance.validate_model(output, "l1", "act")
            (output / "design.con").write_text("/NumContrasts 28\n/Matrix\n")
            with self.assertRaisesRegex(ValueError, "contrast count"):
                provenance.validate_model(output, "l1", "act")
            (output / "design.con").write_text("/NumContrasts 22\n/Matrix\n")
            ev.write_text("1 3.5 1\n")
            with self.assertRaisesRegex(ValueError, "inputs changed"):
                provenance.validate_model(output, "l1", "act")

    def test_l2_cannot_reuse_stale_l1_parent(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            parent = root / "parent.feat"; parent.mkdir()
            stamp = root / "l2.json"
            stamp.write_text(json.dumps(provenance.snapshot("l2", "act", [], [], [parent])))
            with self.assertRaises(OSError):
                provenance.validate_stamp(stamp, "l2", "act")

    def test_archive_preserves_original_and_rejects_links(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "ds003745/sub-144/old.feat"; output.mkdir(parents=True)
            (output / "keep.txt").write_text("old model")
            archive_incomplete(output, ["stale"], root, root / "backup")
            self.assertEqual((root / "backup/ds003745/sub-144/old.feat/keep.txt").read_text(), "old model")
            output.symlink_to(root / "backup/ds003745/sub-144/old.feat", target_is_directory=True)
            with self.assertRaises(ValueError):
                archive_incomplete(output, ["stale"], root, root / "another")

    def test_selection_is_scoped_and_does_not_restore_excluded_run(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = root / "ready.tsv"
            manifest.write_text("dataset\tsubject\tsession\trun\nds003745\t143\t\t1\nds003745\t144\t\t2\nrf1\t144\t01\t1\n")
            selected = select_manifest(manifest, root / "selected.tsv", "l1")
            self.assertEqual([(r["dataset"], r["subject"], r["run"]) for r in selected], [("ds003745", "144", "2")])


if __name__ == "__main__":
    unittest.main()
