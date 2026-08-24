import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import nibabel as nib
import numpy as np


ROOT = Path(__file__).resolve().parents[1]


class CoverageMosaics(unittest.TestCase):
    def test_low_coverage_run_creates_mosaic_and_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            affine = np.diag([2.0, 2.0, 2.0, 1.0])
            bold = np.ones((12, 13, 10, 4), dtype=np.float32)
            bold += np.arange(12, dtype=np.float32)[:, None, None, None]
            eligible = np.ones((12, 13, 10), dtype=np.uint8)
            run_mask = eligible.copy()
            run_mask[:, :3, :] = 0
            bold_path = directory / "bold.nii.gz"
            run_path = directory / "run-mask.nii.gz"
            eligible_path = directory / "eligible.nii.gz"
            nib.save(nib.Nifti1Image(bold, affine), bold_path)
            nib.save(nib.Nifti1Image(run_mask, affine), run_path)
            nib.save(nib.Nifti1Image(eligible, affine), eligible_path)
            audit = directory / "audit.tsv"
            fields = (
                "dataset", "subject", "session", "run", "input", "mask",
                "coverage_mask", "coverage_pct",
            )
            with audit.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
                writer.writeheader()
                writer.writerow(
                    {
                        "dataset": "rf1", "subject": "100", "session": "01",
                        "run": "1", "input": bold_path, "mask": run_path,
                        "coverage_mask": eligible_path, "coverage_pct": "76.9",
                    }
                )
            output_dir = directory / "mosaics"
            summary = directory / "summary.tsv"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "code/plot_coverage_mosaics.py"),
                    "--input", str(audit),
                    "--output-dir", str(output_dir),
                    "--dataset", "rf1",
                    "--coverage-below", "95",
                    "--slices", "4",
                    "--summary-output", str(summary),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            mosaics = list(output_dir.glob("*.png"))
            self.assertEqual(len(mosaics), 1)
            self.assertGreater(mosaics[0].stat().st_size, 1000)
            with summary.open(newline="") as handle:
                row = next(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual(row["subject"], "100")
            self.assertGreater(int(row["missing_eligible_voxels"]), 0)


if __name__ == "__main__":
    unittest.main()
