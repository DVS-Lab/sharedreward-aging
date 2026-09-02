import csv
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


class SmoothnessWorkflow(unittest.TestCase):
    def test_log_tail_is_bounded_and_preserves_diagnostic(self):
        import importlib.util

        script = ROOT / "code/run_smoothness_batch.py"
        spec = importlib.util.spec_from_file_location("smoothness_batch", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "unit.log"
            log.write_text("\n".join(f"line {number}" for number in range(30)))
            tail = module.log_tail(log)
        self.assertEqual(len(tail), 20)
        self.assertEqual(tail[0], "line 10")
        self.assertEqual(tail[-1], "line 29")

    def test_characterization_manifest_contains_three_required_stages(self):
        try:
            import nibabel as nib
        except ImportError:
            self.skipTest("nibabel unavailable")
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            rf1 = directory / "rf1-fmriprep"
            rf1_confounds_root = directory / "rf1-confounds-tedana"
            rf1_func = rf1 / "sub-100/ses-01/func"
            rf1_func.mkdir(parents=True)
            rf1_stem = "sub-100_ses-01_task-sharedreward_run-1"
            rf1_bold = rf1_func / (
                rf1_stem
                + "_part-mag_space-MNI152NLin6Asym_desc-preproc_bold.nii.gz"
            )
            rf1_mask = rf1_func / (
                rf1_stem
                + "_part-mag_space-MNI152NLin6Asym_desc-brain_mask.nii.gz"
            )
            rf1_confounds = (
                rf1_confounds_root
                / "sub-100"
                / (rf1_stem + "_desc-TedanaPlusConfounds.tsv")
            )
            rf1_confounds.parent.mkdir(parents=True)
            affine = np.diag([2.7, 2.7, 2.97, 1.0])
            nib.save(
                nib.Nifti1Image(
                    np.ones((3, 4, 5, 6), dtype=np.float32), affine
                ),
                rf1_bold,
            )
            nib.save(
                nib.Nifti1Image(np.ones((3, 4, 5), dtype=np.uint8), affine),
                rf1_mask,
            )
            rf1_confounds.write_text("x")
            rf1_run_qc = directory / "run_qc.tsv"
            rf1_run_qc.write_text(
                "subject\tsession\ttask\trun\tqc_complete\n"
                "100\t01\tsharedreward\t1\tTRUE\n"
            )

            ds_func = directory / "ds/sub-104/func"
            ds_func.mkdir(parents=True)
            ds_stem = "sub-104_task-sharedreward_run-01"
            ds_bold = ds_func / (
                ds_stem + "_space-MNI152NLin6Asym_desc-preproc_bold.nii.gz"
            )
            ds_mask = ds_func / (
                ds_stem + "_space-MNI152NLin6Asym_desc-brain_mask.nii.gz"
            )
            ds_confounds = ds_func / (ds_stem + "_desc-confounds_timeseries.tsv")
            ds_out_bold = directory / "harmonized/bold.nii.gz"
            ds_out_mask = directory / "harmonized/mask.nii.gz"
            ds_out_bold.parent.mkdir()
            for bold in (ds_bold, ds_out_bold):
                nib.save(
                    nib.Nifti1Image(
                        np.ones((3, 4, 5, 6), dtype=np.float32), affine
                    ),
                    bold,
                )
            for mask in (ds_mask, ds_out_mask):
                nib.save(
                    nib.Nifti1Image(
                        np.ones((3, 4, 5), dtype=np.uint8), affine
                    ),
                    mask,
                )
            ds_confounds.write_text("x")
            ds_manifest = directory / "resampling.tsv"
            ds_manifest.write_text(
                "subject\trun\tinput_bold\tinput_mask\toutput_bold\toutput_mask\n"
                f"104\t01\t{ds_bold}\t{ds_mask}\t{ds_out_bold}\t{ds_out_mask}\n"
            )
            ready = directory / "ready.tsv"
            missing = directory / "missing.tsv"
            result = subprocess.run(
                [
                    "python3",
                    str(ROOT / "code/build_characterization_manifest.py"),
                    "--rf1-run-qc",
                    str(rf1_run_qc),
                    "--rf1-fmriprep-root",
                    str(rf1),
                    "--rf1-confounds-root",
                    str(rf1_confounds_root),
                    "--ds-resampling-manifest",
                    str(ds_manifest),
                    "--output",
                    str(ready),
                    "--missing-output",
                    str(missing),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            with ready.open(newline="") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual(len(rows), 3)
            self.assertEqual(
                {(row["dataset"], row["stage"]) for row in rows},
                {
                    ("rf1", "pre_resample"),
                    ("ds003745", "pre_resample"),
                    ("ds003745", "post_resample_preblur"),
                },
            )
            self.assertIn("Ready characterization units: 3", result.stdout)
            rf1_row = next(row for row in rows if row["dataset"] == "rf1")
            self.assertEqual(rf1_row["confounds"], str(rf1_confounds.resolve()))

    def test_batch_result_is_atomic_validated_and_restartable(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            fake_root = directory / "authoritative"
            fake_code = fake_root / "code"
            fake_code.mkdir(parents=True)
            fake_tool = fake_code / "measure_smoothness.sh"
            fake_tool.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                "input=; mask=; output=\n"
                "while (( $# )); do\n"
                "  case \"$1\" in\n"
                "    --input) input=\"$2\"; shift 2 ;;\n"
                "    --mask) mask=\"$2\"; shift 2 ;;\n"
                "    --output-tsv) output=\"$2\"; shift 2 ;;\n"
                "    --work-dir) shift 2 ;;\n"
                "  esac\n"
                "done\n"
                "printf 'input\\tmask\\tclassic_fwhm_x\\tclassic_fwhm_y\\tclassic_fwhm_z\\tclassic_fwhm_combined\\tacf_a\\tacf_b\\tacf_c\\tacf_effective_fwhm\\tafni_version\\n' > \"$output\"\n"
                "printf '%s\\t%s\\t3\\t4\\t5\\t4\\t1\\t2\\t3\\t4.5\\tAFNI_TEST\\n' \"$input\" \"$mask\" >> \"$output\"\n"
            )
            fake_tool.chmod(0o755)
            bold = directory / "bold.nii.gz"
            mask = directory / "mask.nii.gz"
            bold.write_text("bold")
            mask.write_text("mask")
            manifest = directory / "manifest.tsv"
            manifest.write_text(
                "dataset\tsubject\tsession\trun\tstage\tinput_bold\tinput_mask\tconfounds\n"
                f"rf1\t100\t01\t1\tpre_resample\t{bold}\t{mask}\tunused.tsv\n"
            )
            output_dir = directory / "results"
            command = [
                sys.executable,
                str(ROOT / "code/run_smoothness_batch.py"),
                "--manifest",
                str(manifest),
                "--jobs",
                "1",
                "--output-dir",
                str(output_dir),
                "--log-dir",
                str(directory / "logs"),
                "--work-root",
                str(directory / "work"),
            ]
            environment = os.environ.copy()
            environment["RF1_SHAREDREWARD_ROOT"] = str(fake_root)
            first = subprocess.run(
                command,
                env=environment,
                capture_output=True,
                text=True,
            )
            logs = "\n".join(
                path.read_text()
                for path in (directory / "logs").glob("*.log")
            )
            self.assertEqual(
                first.returncode,
                0,
                first.stdout + first.stderr + logs,
            )
            self.assertIn("Units newly completed: 1", first.stdout)
            result_files = list(output_dir.glob("*.tsv"))
            self.assertEqual(len(result_files), 1)
            self.assertFalse(list(output_dir.glob(".*.tsv")))
            second = subprocess.run(
                command,
                env=environment,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("Units verified existing: 1", second.stdout)

    def test_audit_consolidates_complete_result(self):
        try:
            import nibabel as nib
        except ImportError:
            self.skipTest("nibabel unavailable")
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            affine = np.diag([2.7, 2.7, 2.97, 1.0])
            bold = directory / "bold.nii.gz"
            mask = directory / "mask.nii.gz"
            nib.save(
                nib.Nifti1Image(
                    np.zeros((3, 4, 5, 6), dtype=np.float32), affine
                ),
                bold,
            )
            nib.save(
                nib.Nifti1Image(np.ones((3, 4, 5), dtype=np.uint8), affine),
                mask,
            )
            manifest = directory / "manifest.tsv"
            manifest.write_text(
                "dataset\tsubject\tsession\trun\tstage\tinput_bold\tinput_mask\tconfounds\n"
                f"rf1\t100\t01\t1\tpre_resample\t{bold}\t{mask}\tunused.tsv\n"
            )
            results = directory / "results"
            results.mkdir()
            result = results / "rf1_sub-100_ses-01_run-1_stage-pre_resample.tsv"
            result.write_text(
                "input\tmask\tclassic_fwhm_x\tclassic_fwhm_y\tclassic_fwhm_z\tclassic_fwhm_combined\tacf_a\tacf_b\tacf_c\tacf_effective_fwhm\tafni_version\n"
                f"{bold.resolve()}\t{mask.resolve()}\t3\t4\t5\t4\t1\t2\t3\t4.5\tAFNI_TEST\n"
            )
            output = directory / "summary.tsv"
            missing = directory / "missing.tsv"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "code/audit_smoothness.py"),
                    "--manifest",
                    str(manifest),
                    "--result-dir",
                    str(results),
                    "--output",
                    str(output),
                    "--missing-output",
                    str(missing),
                    "--fail-on-incomplete",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("Complete smoothness units: 1", completed.stdout)
            with output.open(newline="") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual(rows[0]["n_volumes"], "6")
            self.assertEqual(rows[0]["classic_fwhm_combined"], "4")


if __name__ == "__main__":
    unittest.main()
