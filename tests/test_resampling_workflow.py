import csv
import os
import subprocess
import sys
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

    def test_worker_uses_wsinc5_for_bold_and_nn_for_mask(self):
        try:
            import nibabel as nib
        except ImportError:
            self.skipTest("nibabel unavailable")
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            fake_bin = directory / "bin"
            fake_bin.mkdir()
            fake_resample = fake_bin / "3dresample"
            fake_resample.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                "input=\"\"; output=\"\"; rmode=\"\"\n"
                "while (( $# )); do\n"
                "  case \"$1\" in\n"
                "    -input) input=\"$2\"; shift 2 ;;\n"
                "    -prefix) output=\"$2\"; shift 2 ;;\n"
                "    -rmode) rmode=\"$2\"; shift 2 ;;\n"
                "    *) shift 2 ;;\n"
                "  esac\n"
                "done\n"
                "[[ \"$rmode\" == NN ]] || { echo 'expected NN' >&2; exit 41; }\n"
                "[[ ! -e \"$output\" ]] || { echo 'prefix exists' >&2; exit 42; }\n"
                "cp \"$input\" \"$output\"\n"
            )
            fake_resample.chmod(0o755)
            fake_allineate = fake_bin / "3dAllineate"
            fake_allineate.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                "input=\"\"; output=\"\"; matrix=\"\"; final=\"\"\n"
                "while (( $# )); do\n"
                "  case \"$1\" in\n"
                "    -input) input=\"$2\"; shift 2 ;;\n"
                "    -prefix) output=\"$2\"; shift 2 ;;\n"
                "    -1Dmatrix_apply) matrix=\"$2\"; shift 2 ;;\n"
                "    -final) final=\"$2\"; shift 2 ;;\n"
                "    *) shift 2 ;;\n"
                "  esac\n"
                "done\n"
                "[[ \"$matrix\" == IDENTITY ]] || { echo 'expected identity' >&2; exit 43; }\n"
                "[[ \"$final\" == wsinc5 ]] || { echo 'expected wsinc5' >&2; exit 44; }\n"
                "[[ ! -e \"$output\" ]] || { echo 'prefix exists' >&2; exit 45; }\n"
                "cp \"$input\" \"$output\"\n"
            )
            fake_allineate.chmod(0o755)
            affine = np.diag([2.7, 2.7, 2.97, 1.0])
            reference = directory / "reference.nii.gz"
            input_bold = directory / "input_bold.nii.gz"
            input_mask = directory / "input_mask.nii.gz"
            output_bold = directory / "outputs/output_bold.nii.gz"
            output_mask = directory / "outputs/output_mask.nii.gz"
            mask_image = nib.Nifti1Image(
                np.ones((3, 4, 5), dtype=np.uint8), affine
            )
            bold_image = nib.Nifti1Image(
                np.ones((3, 4, 5, 2), dtype=np.float32), affine
            )
            nib.save(mask_image, reference)
            nib.save(mask_image, input_mask)
            nib.save(bold_image, input_bold)
            environment = os.environ.copy()
            environment["PATH"] = f"{fake_bin}:{environment['PATH']}"
            environment["REFERENCE_GRID"] = str(reference)
            environment["IMAGING_PYTHON"] = sys.executable
            for kind, input_path, output_path in (
                ("bold", input_bold, output_bold),
                ("mask", input_mask, output_mask),
            ):
                subprocess.run(
                    [
                        "bash",
                        str(ROOT / "code/resample_to_rf1_grid.sh"),
                        "--input",
                        str(input_path),
                        "--kind",
                        kind,
                        "--output",
                        str(output_path),
                    ],
                    env=environment,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertTrue(output_path.is_file())
                self.assertTrue(
                    output_path.with_name(
                        output_path.name.removesuffix(".nii.gz") + "_grid.json"
                    ).is_file()
                )
            self.assertFalse(list(output_mask.parent.glob(".resample.*")))


if __name__ == "__main__":
    unittest.main()
