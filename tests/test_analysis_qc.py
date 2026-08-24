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
    def test_rf1_motion_qc_uses_named_fmriprep_table_not_feat_matrix(self):
        sys.path.insert(0, str(ROOT / "code"))
        try:
            from build_analysis_qc_manifest import motion_confounds_path
        finally:
            sys.path.pop(0)
        row = {
            "dataset": "rf1",
            "input_bold": (
                "/upstream/fmriprep/sub-100/ses-01/func/"
                "sub-100_ses-01_task-sharedreward_run-1_part-mag_"
                "space-MNI152NLin6Asym_desc-preproc_bold.nii.gz"
            ),
            "confounds": "/upstream/fsl/confounds_tedana/headerless.tsv",
        }
        self.assertEqual(
            str(motion_confounds_path(row)),
            "/upstream/fmriprep/sub-100/ses-01/func/"
            "sub-100_ses-01_task-sharedreward_run-1_part-mag_"
            "desc-confounds_timeseries.tsv",
        )

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
        try:
            import nibabel as nib
            import numpy as np
        except ImportError:
            self.skipTest("nibabel unavailable")
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
            files["bold"] = directory / "bold.nii.gz"
            files["bold"].write_text("bold")
            affine = np.eye(4)
            run_mask = np.zeros((5, 5, 4), dtype=np.uint8)
            run_mask.reshape(-1)[:90] = 1
            reference = np.ones((5, 5, 4), dtype=np.uint8)
            coverage = np.zeros((5, 5, 4), dtype=np.uint8)
            coverage.reshape(-1)[:80] = 1
            for name, data in (
                ("mask", run_mask),
                ("reference", reference),
                ("coverage", coverage),
            ):
                files[name] = directory / f"{name}.nii.gz"
                nib.save(nib.Nifti1Image(data, affine), files[name])
            confounds = directory / "confounds.tsv"
            confounds.write_text(
                "framewise_displacement\tstd_dvars\n"
                "n/a\tn/a\n0.1\t1.0\n0.6\t1.2\n"
            )
            output = directory / "qc.json"
            manifest = directory / "manifest.tsv"
            manifest.write_text(
                "dataset\tsubject\tsession\trun\tinput_bold\tinput_mask\treference_mask\tcoverage_mask\tconfounds\toutput_json\n"
                f"rf1\t100\t01\t1\t{files['bold']}\t{files['mask']}\t{files['reference']}\t{files['coverage']}\t{confounds}\t{output}\n"
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
            self.assertEqual(result["confounds_format"], "named_fmriprep_timeseries")
            self.assertEqual(result["confounds_rows"], 3)
            self.assertEqual(result["coverage_mask_voxels"], 80)
            self.assertEqual(result["coverage_overlap_voxels"], 80)
            self.assertEqual(result["coverage_pct"], 100.0)
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
            self.assertEqual(rows[0]["qc_flags"], "")
            self.assertIn("CHECK PASSED", audit.stdout)

    def test_coverage_eligible_mask_subtracts_resampled_exemption(self):
        try:
            import nibabel as nib
            import numpy as np
        except ImportError:
            self.skipTest("nibabel unavailable")
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            template = directory / "template.nii.gz"
            exemption = directory / "exemption.nii.gz"
            reference = directory / "reference.nii.gz"
            resampled = directory / "resampled.nii.gz"
            eligible = directory / "eligible.nii.gz"
            metadata = directory / "eligible.json"
            affine = np.eye(4)
            nib.save(nib.Nifti1Image(np.ones((3, 3, 3)), affine), template)
            exemption_data = np.zeros((3, 3, 3))
            exemption_data[0, :, :] = 1
            nib.save(nib.Nifti1Image(exemption_data, affine), exemption)
            nib.save(nib.Nifti1Image(np.zeros((3, 3, 3)), affine), reference)
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "code/create_coverage_eligible_mask.py"),
                    "--template-mask",
                    str(template),
                    "--exemption-mask",
                    str(exemption),
                    "--reference-grid",
                    str(reference),
                    "--resampled-exemption-output",
                    str(resampled),
                    "--eligible-mask-output",
                    str(eligible),
                    "--json-output",
                    str(metadata),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(int(np.asanyarray(nib.load(resampled).dataobj).sum()), 9)
            self.assertEqual(int(np.asanyarray(nib.load(eligible).dataobj).sum()), 18)
            provenance = json.loads(metadata.read_text())
            self.assertEqual(provenance["coverage_formula"], "run_mask_intersection_eligible_mask / eligible_mask")


if __name__ == "__main__":
    unittest.main()
