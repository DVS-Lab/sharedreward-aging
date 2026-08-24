import csv
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TargetSmoothingWorkflow(unittest.TestCase):
    def test_manifest_selects_only_analysis_ready_stages_and_owner_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            bold = directory / "bold.nii.gz"
            mask = directory / "mask.nii.gz"
            bold.write_text("bold")
            mask.write_text("mask")
            characterization = directory / "characterization.tsv"
            characterization.write_text(
                "dataset\tsubject\tsession\trun\tstage\tinput_bold\tinput_mask\tconfounds\n"
                f"rf1\t100\t01\t1\tpre_resample\t{bold}\t{mask}\tx\n"
                f"ds003745\t104\t\t01\tpre_resample\t{bold}\t{mask}\tx\n"
                f"ds003745\t104\t\t01\tpost_resample_preblur\t{bold}\t{mask}\tx\n"
            )
            ready = directory / "ready.tsv"
            missing = directory / "missing.tsv"
            rf1_root = directory / "rf1-analysis"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "code/build_target_smoothing_manifest.py"),
                    "--characterization-manifest",
                    str(characterization),
                    "--rf1-sharedreward-root",
                    str(rf1_root),
                    "--target",
                    "6",
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
            self.assertEqual(len(rows), 2)
            self.assertEqual({row["dataset"] for row in rows}, {"rf1", "ds003745"})
            rf1 = next(row for row in rows if row["dataset"] == "rf1")
            ds = next(row for row in rows if row["dataset"] == "ds003745")
            self.assertTrue(rf1["output_bold"].startswith(str(rf1_root.resolve())))
            self.assertTrue(ds["output_bold"].startswith(str(ROOT.resolve())))
            self.assertIn("smoothToFWHM6", rf1["output_bold"])
            self.assertIn("smoothToFWHM6", ds["output_bold"])
            self.assertIn("Ready target-smoothing units: 2", result.stdout)

    def test_batch_validates_and_restarts_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            fake_root = directory / "authoritative"
            fake_code = fake_root / "code"
            fake_code.mkdir(parents=True)
            tool = fake_code / "smooth_to_target.sh"
            tool.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                "input=; mask=; output=; qc=\n"
                "while (( $# )); do\n"
                "  case \"$1\" in\n"
                "    --input) input=\"$2\"; shift 2 ;;\n"
                "    --mask) mask=\"$2\"; shift 2 ;;\n"
                "    --output) output=\"$2\"; shift 2 ;;\n"
                "    --qc-tsv) qc=\"$2\"; shift 2 ;;\n"
                "    --target|--work-dir) shift 2 ;;\n"
                "    --overwrite|--all-blurmaster) shift ;;\n"
                "  esac\n"
                "done\n"
                "mkdir -p \"$(dirname \"$output\")\" \"$(dirname \"$qc\")\"\n"
                "cp \"$input\" \"$output\"\n"
                "printf 'input\\tmask\\tclassic_fwhm_x\\tclassic_fwhm_y\\tclassic_fwhm_z\\tclassic_fwhm_combined\\tacf_a\\tacf_b\\tacf_c\\tacf_effective_fwhm\\tafni_version\\n' > \"$qc\"\n"
                "printf '%s\\t%s\\t6\\t6\\t6\\t6\\t.5\\t3\\t9\\t9\\tAFNI_TEST\\n' \"$output\" \"$mask\" >> \"$qc\"\n"
            )
            tool.chmod(0o755)
            bold = directory / "bold.nii.gz"
            mask = directory / "mask.nii.gz"
            output = directory / "sub-100_desc-smoothToFWHM6_bold.nii.gz"
            qc = directory / "sub-100_desc-smoothToFWHM6_bold_smoothness.tsv"
            bold.write_text("bold")
            mask.write_text("mask")
            manifest = directory / "manifest.tsv"
            manifest.write_text(
                "dataset\tsubject\tsession\trun\tinput_bold\tinput_mask\toutput_bold\toutput_qc\ttarget_fwhm_mm\n"
                f"rf1\t100\t01\t1\t{bold}\t{mask}\t{output}\t{qc}\t6\n"
            )
            command = [
                sys.executable,
                str(ROOT / "code/run_target_smoothing_batch.py"),
                "--manifest",
                str(manifest),
                "--jobs",
                "1",
                "--log-dir",
                str(directory / "logs"),
                "--work-root",
                str(directory / "work"),
                "--all-blurmaster",
            ]
            environment = os.environ.copy()
            environment["RF1_SHAREDREWARD_ROOT"] = str(fake_root)
            first = subprocess.run(
                command, env=environment, capture_output=True, text=True
            )
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertIn("Units newly completed: 1", first.stdout)
            logs = "\n".join(path.read_text() for path in (directory / "logs").glob("*.log"))
            self.assertIn("--all-blurmaster", logs)
            second = subprocess.run(
                command,
                env=environment,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("Units verified existing: 1", second.stdout)

    def test_audit_reports_complete_geometry_and_smoothness(self):
        try:
            import nibabel as nib
            import numpy as np
        except ImportError:
            self.skipTest("nibabel unavailable")
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            affine = np.diag([2.7, 2.7, 2.97, 1.0])
            source = directory / "source.nii.gz"
            output = directory / "output.nii.gz"
            mask = directory / "mask.nii.gz"
            nib.save(nib.Nifti1Image(np.zeros((3, 4, 5, 6)), affine), source)
            nib.save(nib.Nifti1Image(np.zeros((3, 4, 5, 6)), affine), output)
            nib.save(nib.Nifti1Image(np.ones((3, 4, 5)), affine), mask)
            qc = directory / "qc.tsv"
            qc.write_text(
                "input\tmask\tclassic_fwhm_x\tclassic_fwhm_y\tclassic_fwhm_z\tclassic_fwhm_combined\tacf_a\tacf_b\tacf_c\tacf_effective_fwhm\tafni_version\n"
                f"{output.resolve()}\t{mask.resolve()}\t6\t6\t6\t6\t.5\t3\t9\t9\tAFNI_TEST\n"
            )
            manifest = directory / "manifest.tsv"
            manifest.write_text(
                "dataset\tsubject\tsession\trun\tinput_bold\tinput_mask\toutput_bold\toutput_qc\ttarget_fwhm_mm\n"
                f"rf1\t100\t01\t1\t{source}\t{mask}\t{output}\t{qc}\t6\n"
            )
            summary = directory / "summary.tsv"
            missing = directory / "missing.tsv"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "code/audit_target_smoothing.py"),
                    "--manifest",
                    str(manifest),
                    "--output",
                    str(summary),
                    "--missing-output",
                    str(missing),
                    "--fail-on-incomplete",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Complete target-smoothed units: 1", result.stdout)
            self.assertIn("Conventionally passing units: 1", result.stdout)
            self.assertIn("Accepted QC exceptions: 0", result.stdout)
            self.assertIn("ACF-effective mean=9.0000", result.stdout)

    def test_audit_accepts_only_a_bounded_documented_exception(self):
        try:
            import nibabel as nib
            import numpy as np
        except ImportError:
            self.skipTest("nibabel unavailable")
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            affine = np.diag([2.7, 2.7, 2.97, 1.0])
            source = directory / "source.nii.gz"
            output = directory / "output.nii.gz"
            mask = directory / "mask.nii.gz"
            nib.save(nib.Nifti1Image(np.zeros((3, 4, 5, 6)), affine), source)
            nib.save(nib.Nifti1Image(np.zeros((3, 4, 5, 6)), affine), output)
            nib.save(nib.Nifti1Image(np.ones((3, 4, 5)), affine), mask)
            qc = directory / "qc.tsv"
            qc.write_text(
                "input\tmask\tclassic_fwhm_x\tclassic_fwhm_y\tclassic_fwhm_z\tclassic_fwhm_combined\tacf_a\tacf_b\tacf_c\tacf_effective_fwhm\tafni_version\n"
                f"{output.resolve()}\t{mask.resolve()}\t5.2\t5.3\t5.4\t5.28\t.5\t3\t8\t8\tAFNI_TEST\n"
            )
            manifest = directory / "manifest.tsv"
            manifest.write_text(
                "dataset\tsubject\tsession\trun\tinput_bold\tinput_mask\toutput_bold\toutput_qc\ttarget_fwhm_mm\n"
                f"rf1\t10657\t01\t1\t{source}\t{mask}\t{output}\t{qc}\t6\n"
            )
            evidence = directory / "evidence.md"
            evidence.write_text("Independent overwrite retries reproduced the result.\n")
            exceptions = directory / "exceptions.tsv"
            exceptions.write_text(
                "dataset\tsubject\tsession\trun\tproblem\texpected_target_fwhm_mm\taccepted_classic_min_mm\taccepted_classic_max_mm\trationale\tevidence\n"
                f"rf1\t10657\t01\t1\tclassic_outside_tolerance\t6\t5.27\t5.29\tStable test exception.\t{evidence}\n"
            )
            summary = directory / "summary.tsv"
            missing = directory / "missing.tsv"
            command = [
                sys.executable,
                str(ROOT / "code/audit_target_smoothing.py"),
                "--manifest",
                str(manifest),
                "--output",
                str(summary),
                "--missing-output",
                str(missing),
                "--exceptions",
                str(exceptions),
                "--fail-on-incomplete",
            ]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Conventionally passing units: 0", result.stdout)
            self.assertIn("Accepted QC exceptions: 1", result.stdout)
            self.assertIn("ACCEPTED EXCEPTION rf1 sub-10657", result.stdout)
            with summary.open(newline="") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual(rows[0]["qc_status"], "accepted_exception")

            qc.write_text(
                "input\tmask\tclassic_fwhm_x\tclassic_fwhm_y\tclassic_fwhm_z\tclassic_fwhm_combined\tacf_a\tacf_b\tacf_c\tacf_effective_fwhm\tafni_version\n"
                f"{output.resolve()}\t{mask.resolve()}\t5.1\t5.1\t5.1\t5.10\t.5\t3\t8\t8\tAFNI_TEST\n"
            )
            rejected = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(rejected.returncode, 1, rejected.stdout + rejected.stderr)
            self.assertIn("Incomplete target-smoothed units: 1", rejected.stdout)


if __name__ == "__main__":
    unittest.main()
