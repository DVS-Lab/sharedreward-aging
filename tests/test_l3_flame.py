"""Synthetic design/ratings/retained-run tests and optional real FSL smoke test."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import nibabel as nib
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
import run_L3stats as l3


class L3Tests(unittest.TestCase):
    def people(self, n=30):
        rng = np.random.default_rng(15)
        return pd.DataFrame(dict(dataset=["ds003745"]*(n//2)+["rf1"]*(n-n//2),
            subject=[str(i) for i in range(n)], session=[""]*n,
            age=rng.uniform(20, 80, n), retained_tsnr=rng.uniform(80, 200, n),
            retained_mean_fd_mm=rng.uniform(.03, .3, n), rating_score=rng.normal(size=n),
            ratings_eligible=["true"]*n))

    def test_design_no_sex_and_exact_covariates(self):
        for family in ("age", "age-ratings"):
            x, c, columns, names = l3.design(self.people(), family)
            self.assertEqual(columns[-4:], ["age_decades", "tsnr", "fdmean_mm", "dataset_rf1"])
            self.assertEqual(x.shape[1], 5 if family == "age" else 6)
            np.testing.assert_allclose(x[:, 1:-1].mean(axis=0), 0, atol=1e-12)
            self.assertEqual(len(c), 2 if family == "age" else 4)
            self.assertEqual(c[0, 1], 1)
            np.testing.assert_equal(c[1], -c[0])
            self.assertFalse(any("sex" in name for name in columns))

    def test_tsnr_retained_only(self):
        data = pd.DataFrame([dict(dataset="rf1", subject="1", session="01")])
        runs = pd.DataFrame([dict(data.iloc[0], run="1"), dict(data.iloc[0], run="2")])
        qc = pd.DataFrame([dict(data.iloc[0], run=str(i), stage="post_target_blur", median_tsnr=v)
                           for i, v in ((1, "100"), (2, "140"), (3, "999"))])
        self.assertEqual(l3.add_tsnr(data, runs, qc).retained_tsnr.iloc[0], 120)
        self.assertEqual(l3.add_tsnr(data, runs.iloc[:1], qc).retained_tsnr.iloc[0], 100)
        with self.assertRaises(ValueError):
            l3.add_tsnr(data, runs, qc.iloc[:1])

    def test_qc_outlier_cannot_enter_retained_manifest(self):
        runs = pd.DataFrame([dict(dataset="rf1", subject="1", session="01", run="1")])
        qc = runs.copy().assign(stage="post_target_blur", mean_fd_mm=.2, median_tsnr=100., coverage_pct=99.9)
        thresholds = pd.DataFrame([dict(dataset="rf1", metric=m, threshold=t, direction=d)
            for m,t,d in (("mean_fd_mm",.3659,"above"),("median_tsnr",32.8231,"below"),("coverage_pct",99.1488,"below"))])
        self.assertEqual(len(l3.verify_qc_exclusions(runs,qc,thresholds)),3)
        for metric, bad in (("mean_fd_mm",.5),("median_tsnr",20.),("coverage_pct",90.)):
            with self.assertRaises(ValueError):
                l3.verify_qc_exclusions(runs,qc.assign(**{metric:bad}),thresholds)

    def test_ratings_direction_and_rule(self):
        data = self.people()
        rows = data[["dataset", "subject"]].copy()
        rows["exclude_subject"] = "false"
        for p in (1, 2, 3):
            rows[f"partner_{p}_trait_0_mean"] = str(p)
            rows[f"partner_{p}_trait_1_mean"] = "-2"
        rows.loc[0, "partner_1_trait_1_mean"] = "5"  # Within-partner reversal.
        data.loc[1, "ratings_eligible"] = "false"
        rows.loc[2, "partner_1_trait_1_mean"] = "1"  # Equality allowed.
        selected, eligibility = l3.rating_cohort(data.drop(columns="rating_score"), rows)
        self.assertEqual(len(selected), 28)
        np.testing.assert_array_equal(selected.rating_score.to_numpy(), np.ones(28))
        self.assertTrue(eligibility.included.iloc[2])

    @unittest.skipUnless(shutil.which("feat_model"), "FSL unavailable")
    def test_real_feat_model_matrix(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for family in ("age", "age-ratings"):
                x, c, columns, names = l3.design(self.people(), family)
                fsf = root / f"{family}.fsf"
                fsf.write_text(l3.render(family, root / "out.gfeat", [root / f"i{i}.feat/stats/cope1.nii.gz" for i in range(len(x))],
                                        x, c, columns, names, root / "standard.nii.gz"))
                result = subprocess.run(["feat_model", str(fsf.with_suffix(""))], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
                np.testing.assert_allclose(l3.matrix(fsf.with_suffix(".mat")), x, atol=1e-5)
                np.testing.assert_array_equal(l3.matrix(fsf.with_suffix(".con")), c)
                settings = l3.fsf_settings(fsf)
                self.assertEqual(settings["fmri(mixed_yn)"], "2")
                self.assertEqual(settings["fmri(featwatcher_yn)"], "0")
                self.assertEqual(settings["fmri(smooth)"], "0")

    @unittest.skipUnless(os.environ.get("RUN_FSL_SMOKE") == "1", "Set RUN_FSL_SMOKE=1 for real FEAT fit")
    def test_real_feat_flame1(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            rng = np.random.default_rng(8)
            data = self.people(24)
            x, c, columns, names = l3.design(data, "age")
            reference = nib.Nifti1Image(np.ones((12, 12, 12)), np.diag([2., 2., 2., 1.]))
            ref = root / "reference.nii.gz"; nib.save(reference, ref)
            inputs = []
            for i in range(len(x)):
                original = root / f"original-{i}.feat"
                (original / "stats").mkdir(parents=True)
                for name, values in {
                    "stats/cope1.nii.gz": rng.normal(size=reference.shape) + .2*x[i, 1],
                    "stats/varcope1.nii.gz": np.ones(reference.shape),
                    "stats/tdof_t1.nii.gz": np.full(reference.shape, 100.),
                    "mask.nii.gz": np.ones(reference.shape),
                    "mean_func.nii.gz": rng.uniform(900, 1100, reference.shape),
                }.items():
                    nib.save(nib.Nifti1Image(values, reference.affine), original / name)
                (original / "design.con").write_text("/NumWaves 1\n/NumContrasts 1\n/PPheights 1\n/RequiredEffect 1\n/Matrix\n1\n")
                row = dict(cope_path=str(original / "stats/cope1.nii.gz"), varcope_path=str(original / "stats/varcope1.nii.gz"),
                           mask_path=str(original / "mask.nii.gz"), strategy="fixed_effects")
                inputs.append(l3.stage_input(row, root / "inputs" / f"input-{i}.feat", reference))
            fsf = root / "design.fsf"
            output = root / "out.gfeat"
            fsf.write_text(l3.render("age", output, inputs, x, c, columns, names, ref))
            result = subprocess.run(["bash", str(l3.ROOT / "code/L3stats.sh"), str(fsf)], capture_output=True, text=True)
            if result.returncode:
                print(result.stdout, result.stderr)
                for log in output.glob("**/logs/*"):
                    if log.is_file(): print(log, log.read_text(errors="replace")[-4000:])
            self.assertEqual(result.returncode, 0)
            self.assertEqual(len(l3.audit_fit(output, x, c, reference)), 2)


if __name__ == "__main__":
    unittest.main()
