import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AnalysisQc(unittest.TestCase):
    def test_common_mask_uses_reference_grid_and_nearest_neighbor(self):
        try:
            import nibabel as nib
            import numpy as np
        except ImportError:
            self.skipTest("nibabel unavailable")
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            source = directory / "source.nii.gz"
            reference = directory / "reference.nii.gz"
            output = directory / "common.nii.gz"
            metadata = directory / "common.json"
            source_data = np.zeros((4, 4, 4), dtype=np.uint8)
            source_data[1:3, 1:3, 1:3] = 1
            nib.save(nib.Nifti1Image(source_data, np.eye(4)), source)
            reference_affine = np.diag([2, 2, 2, 1])
            nib.save(nib.Nifti1Image(np.zeros((2, 2, 2)), reference_affine), reference)
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "code/create_common_analysis_mask.py"),
                    "--source-mask",
                    str(source),
                    "--reference-grid",
                    str(reference),
                    "--output",
                    str(output),
                    "--json-output",
                    str(metadata),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            image = nib.load(output)
            self.assertEqual(image.shape, (2, 2, 2))
            self.assertTrue(np.allclose(image.affine, reference_affine))
            self.assertGreater(int(np.asanyarray(image.dataobj).sum()), 0)
            self.assertEqual(json.loads(metadata.read_text())["interpolation"], "nearest-neighbor")

    def test_batch_and_audit_preserve_tsnr_motion_coverage_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            fake_root = directory / "rf1"
            fake_code = fake_root / "code"
            fake_code.mkdir(parents=True)
            fake_tool = fake_code / "compute_tsnr.py"
            fake_tool.write_text(
                "import argparse,json\n"
                "from pathlib import Path\n"
                "p=argparse.ArgumentParser();\n"
                "for x in ('input','mask','reference_mask','output_json','dataset','subject','session','run','stage'): p.add_argument('--'+x.replace('_','-'),required=x not in ('session',))\n"
                "a=p.parse_args();o={'dataset':a.dataset,'subject':a.subject,'session':a.session or '',"
                "'run':a.run,'stage':a.stage,'definition':'temporal mean / sample temporal SD (ddof=1)',"
                "'input':str(Path(a.input).resolve()),'mask':str(Path(a.mask).resolve()),"
                "'reference_mask':str(Path(a.reference_mask).resolve()),'n_volumes':3,'tr_seconds':2.0,"
                "'run_mask_voxels':90,'reference_mask_voxels':100,'analysis_mask_voxels':90,"
                "'mask_voxels':90,'valid_voxels':90,'coverage_pct':90.0,'valid_coverage_pct':90.0,"
                "'mean_tsnr':50.0,'median_tsnr':45.0};Path(a.output_json).write_text(json.dumps(o))\n"
            )
            files = {}
            for name in ("bold", "mask", "reference"):
                files[name] = directory / f"{name}.nii.gz"
                files[name].write_text(name)
            confounds = directory / "confounds.tsv"
            confounds.write_text(
                "framewise_displacement\tstd_dvars\n"
                "n/a\tn/a\n0.1\t1.0\n0.6\t1.2\n"
            )
            output = directory / "qc.json"
            manifest = directory / "manifest.tsv"
            manifest.write_text(
                "dataset\tsubject\tsession\trun\tinput_bold\tinput_mask\treference_mask\tconfounds\toutput_json\n"
                f"rf1\t100\t01\t1\t{files['bold']}\t{files['mask']}\t{files['reference']}\t{confounds}\t{output}\n"
            )
            environment = os.environ.copy()
            environment["RF1_SHAREDREWARD_ROOT"] = str(fake_root)
            batch = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "code/run_analysis_qc_batch.py"),
                    "--manifest",
                    str(manifest),
                    "--jobs",
                    "1",
                    "--log-dir",
                    str(directory / "logs"),
                ],
                env=environment,
                capture_output=True,
                text=True,
            )
            self.assertEqual(batch.returncode, 0, batch.stdout + batch.stderr)
            result = json.loads(output.read_text())
            self.assertEqual(result["mean_fd_mm"], 0.35)
            self.assertEqual(result["high_motion_volumes"], 1)
            self.assertAlmostEqual(result["high_motion_fraction"], 1 / 3)

            run_output = directory / "run.tsv"
            summary = directory / "summary.tsv"
            subjects = directory / "subjects.tsv"
            missing = directory / "missing.tsv"
            audit = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "code/audit_analysis_qc.py"),
                    "--manifest",
                    str(manifest),
                    "--output",
                    str(run_output),
                    "--summary-output",
                    str(summary),
                    "--subject-output",
                    str(subjects),
                    "--missing-output",
                    str(missing),
                    "--fail-on-incomplete",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(audit.returncode, 0, audit.stdout + audit.stderr)
            with run_output.open(newline="") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual(rows[0]["median_tsnr"], "45.0")
            self.assertIn("high_motion_fraction_above_20pct", rows[0]["qc_flags"])
            self.assertIn("CHECK PASSED", audit.stdout)


if __name__ == "__main__":
    unittest.main()
