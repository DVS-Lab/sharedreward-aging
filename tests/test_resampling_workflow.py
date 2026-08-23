import csv
import subprocess
import tempfile
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


class ResamplingWorkflow(unittest.TestCase):
    def make_sources(self, root, subject, runs=("01", "02")):
        func = root / f"sub-{subject}/func"
        func.mkdir(parents=True, exist_ok=True)
        for run in runs:
            prefix = f"sub-{subject}_task-sharedreward_run-{run}"
            (func / f"{prefix}_space-MNI152NLin6Asym_desc-preproc_bold.nii.gz").write_text(
                "bold"
            )
            (func / f"{prefix}_space-MNI152NLin6Asym_desc-brain_mask.nii.gz").write_text(
                "mask"
            )

    def test_manifest_is_run_level_and_reports_missing_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            participants = directory / "participants.tsv"
            fmriprep = directory / "fmriprep"
            harmonized = directory / "harmonized"
            ready = directory / "ready.tsv"
            missing = directory / "missing.tsv"
            participants.write_text(
                "participant_id\tage\tsex\tgroup\n"
                "sub-104\t20\tM\tyounger\n"
                "sub-105\t70\tF\tolder\n"
            )
            self.make_sources(fmriprep, "104")
            self.make_sources(fmriprep, "105", runs=("01",))

            result = subprocess.run(
                [
                    "python3",
                    str(ROOT / "code/build_resampling_manifest.py"),
                    "--participants",
                    str(participants),
                    "--fmriprep-root",
                    str(fmriprep),
                    "--harmonized-root",
                    str(harmonized),
                    "--output",
                    str(ready),
                    "--missing-output",
                    str(missing),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            with ready.open(newline="") as handle:
                ready_rows = list(csv.DictReader(handle, delimiter="\t"))
            with missing.open(newline="") as handle:
                missing_rows = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual(len(ready_rows), 3)
            self.assertEqual(
                [(row["subject"], row["run"]) for row in missing_rows],
                [("105", "02")],
            )
            self.assertTrue(
                ready_rows[0]["output_bold"].endswith(
                    "_desc-rf1Grid_bold.nii.gz"
                )
            )

    def test_dry_run_validates_manifest_without_writing_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            input_bold = directory / "bold.nii.gz"
            input_mask = directory / "mask.nii.gz"
            reference = directory / "reference.nii.gz"
            output_bold = directory / "out/bold.nii.gz"
            output_mask = directory / "out/mask.nii.gz"
            manifest = directory / "manifest.tsv"
            for path in (input_bold, input_mask, reference):
                path.write_text("placeholder")
            manifest.write_text(
                "subject\trun\tinput_bold\tinput_mask\toutput_bold\toutput_mask\n"
                f"104\t01\t{input_bold}\t{input_mask}\t{output_bold}\t{output_mask}\n"
            )
            result = subprocess.run(
                [
                    "python3",
                    str(ROOT / "code/run_resampling_batch.py"),
                    "--manifest",
                    str(manifest),
                    "--reference",
                    str(reference),
                    "--jobs",
                    "2",
                    "--log-dir",
                    str(directory / "logs"),
                    "--dry-run",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("RF1-grid resampling plan: 1 run unit(s)", result.stdout)
            self.assertIn("DRY RUN sub-104 run-01 RESAMPLE", result.stdout)
            self.assertFalse(output_bold.exists())
            self.assertFalse(output_mask.exists())

    def test_audit_requires_complete_matching_bold_and_mask_grids(self):
        try:
            import nibabel as nib
        except ImportError:
            self.skipTest("nibabel unavailable")
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            affine = np.diag([2.7, 2.7, 2.97, 1.0])
            reference = directory / "reference.nii.gz"
            bold = directory / "bold.nii.gz"
            mask = directory / "mask.nii.gz"
            manifest = directory / "manifest.tsv"
            audit = directory / "audit.tsv"
            nib.save(
                nib.Nifti1Image(np.zeros((3, 4, 5), dtype=np.uint8), affine),
                reference,
            )
            nib.save(
                nib.Nifti1Image(np.zeros((3, 4, 5, 2), dtype=np.float32), affine),
                bold,
            )
            nib.save(
                nib.Nifti1Image(np.ones((3, 4, 5), dtype=np.uint8), affine),
                mask,
            )
            manifest.write_text(
                "subject\trun\toutput_bold\toutput_mask\n"
                f"104\t01\t{bold}\t{mask}\n"
            )
            result = subprocess.run(
                [
                    "python3",
                    str(ROOT / "code/audit_resampling.py"),
                    "--manifest",
                    str(manifest),
                    "--reference",
                    str(reference),
                    "--output",
                    str(audit),
                    "--fail-on-incomplete",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("Complete run units: 1", result.stdout)
            self.assertIn("CHECK PASSED", result.stdout)

            bad_affine = affine.copy()
            bad_affine[0, 3] = 0.5
            nib.save(
                nib.Nifti1Image(
                    np.zeros((3, 4, 5, 2), dtype=np.float32), bad_affine
                ),
                bold,
            )
            result = subprocess.run(
                [
                    "python3",
                    str(ROOT / "code/audit_resampling.py"),
                    "--manifest",
                    str(manifest),
                    "--reference",
                    str(reference),
                    "--output",
                    str(audit),
                    "--fail-on-incomplete",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("bold_affine", audit.read_text())


if __name__ == "__main__":
    unittest.main()
