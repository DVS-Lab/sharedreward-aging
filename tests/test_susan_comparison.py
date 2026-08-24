import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SusanComparison(unittest.TestCase):
    def test_shell_matches_feat_susan_parameterization(self):
        script = (ROOT / "code/smooth_with_feat_susan.sh").read_text()
        self.assertIn("0.75*x", script)
        self.assertIn("x/2.3548200450309493", script)
        self.assertIn('3 1 1 "$mean_func" "$brightness"', script)
        self.assertIn('fslmaths "$susan_raw" -mas "$mask_abs"', script)

    def test_pilot_manifest_selects_highest_baseline_per_dataset(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            mask = directory / "mask.nii.gz"; mask.write_text("mask")
            target_rows = []
            baseline_rows = []
            for dataset, subject, session, run, baseline in (
                ("rf1", "100", "01", "1", "3.5"),
                ("rf1", "101", "01", "1", "4.5"),
                ("ds003745", "104", "", "01", "3.6"),
                ("ds003745", "118", "", "02", "4.0"),
            ):
                source = directory / f"{dataset}-{subject}-{run}-source.nii.gz"
                target = directory / f"{dataset}-{subject}-{run}_desc-smoothToFWHM6_bold.nii.gz"
                source.write_text("bold"); target.write_text("target")
                target_rows.append(
                    [dataset, subject, session, run, str(source), str(mask), str(target), str(target) + ".tsv", "6"]
                )
                stage = "pre_resample" if dataset == "rf1" else "post_resample_preblur"
                baseline_rows.append(
                    [dataset, subject, session, run, stage, str(source), str(mask), baseline]
                )
            target_manifest = directory / "targets.tsv"
            with target_manifest.open("w", newline="") as handle:
                writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
                writer.writerow(["dataset", "subject", "session", "run", "input_bold", "input_mask", "output_bold", "output_qc", "target_fwhm_mm"])
                writer.writerows(target_rows)
            baseline_audit = directory / "baseline.tsv"
            with baseline_audit.open("w", newline="") as handle:
                writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
                writer.writerow(["dataset", "subject", "session", "run", "stage", "input_bold", "input_mask", "classic_fwhm_combined"])
                writer.writerows(baseline_rows)
            ready, missing = directory / "ready.tsv", directory / "missing.tsv"
            result = subprocess.run(
                [sys.executable, str(ROOT / "code/build_susan_comparison_manifest.py"), "--target-manifest", str(target_manifest), "--baseline-audit", str(baseline_audit), "--rf1-sharedreward-root", str(directory / "rf1"), "--output", str(ready), "--missing-output", str(missing)],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            with ready.open(newline="") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual({(row["dataset"], row["subject"]) for row in rows}, {("rf1", "101"), ("ds003745", "118")})

    def test_audit_reports_kernel_and_total_target_separately(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            mask = directory / "mask.nii.gz"; mask.write_text("mask")
            images = {}
            qcs = {}
            values = {"baseline": 4.0, "afni": 6.0, "susan": 7.2}
            for method, value in values.items():
                image = directory / f"{method}.nii.gz"; image.write_text(method)
                qc = directory / f"{method}.tsv"
                qc.write_text(
                    "input\tmask\tclassic_fwhm_x\tclassic_fwhm_y\tclassic_fwhm_z\tclassic_fwhm_combined\tacf_a\tacf_b\tacf_c\tacf_effective_fwhm\tafni_version\n"
                    f"{image.resolve()}\t{mask.resolve()}\t{value}\t{value}\t{value}\t{value}\t.5\t3\t9\t9\tAFNI_TEST\n"
                )
                images[method], qcs[method] = image, qc
            manifest = directory / "manifest.tsv"
            metadata = directory / "susan-metadata.tsv"
            metadata.write_text(
                "input\tmask\toutput\tkernel_fwhm_mm\tspatial_sigma_mm\tmasked_median\tbrightness_threshold\tfsl_version\n"
                f"{images['baseline'].resolve()}\t{mask.resolve()}\t{images['susan'].resolve()}\t6\t2.54777\t1000\t750\tFSL_TEST\n"
            )
            manifest.write_text(
                "dataset\tsubject\tsession\trun\tbaseline_bold\tinput_mask\tafni_target_bold\tsusan_output_bold\tsusan_metadata\tbaseline_qc\tafni_target_qc\tsusan_output_qc\tkernel_fwhm_mm\n"
                f"rf1\t100\t01\t1\t{images['baseline']}\t{mask}\t{images['afni']}\t{images['susan']}\t{metadata}\t{qcs['baseline']}\t{qcs['afni']}\t{qcs['susan']}\t6\n"
            )
            output, missing = directory / "audit.tsv", directory / "missing.tsv"
            summary = directory / "summary.tsv"
            result = subprocess.run(
                [sys.executable, str(ROOT / "code/audit_susan_comparison.py"), "--manifest", str(manifest), "--output", str(output), "--missing-output", str(missing), "--summary-output", str(summary), "--fail-on-incomplete"],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("AFNI-total-target=6.0000", result.stdout)
            self.assertIn("SUSAN-kernel=7.2000", result.stdout)
            self.assertIn("Gaussian-quadrature expectation=7.2111", result.stdout)
            with output.open(newline="") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))
            susan = next(row for row in rows if row["method"] == "fsl_susan_kernel")
            self.assertEqual(susan["susan_masked_median"], "1000")
            self.assertEqual(susan["susan_brightness_threshold"], "750")
            self.assertTrue(summary.is_file())


if __name__ == "__main__":
    unittest.main()
