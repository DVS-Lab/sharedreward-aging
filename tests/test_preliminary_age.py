"""Synthetic checks; no participant data or FSL installation required."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import nibabel as nib
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from run_preliminary_age import design, hc3_age, ordered_candidates, prepare_model, randomise_model, vest


class AgeTests(unittest.TestCase):
    def sample(self):
        rng = np.random.default_rng(33)
        return pd.DataFrame(dict(dataset=["ds003745"]*20+["rf1"]*40,
            subject=[str(i) for i in range(60)], session=[""]*60, runs=["1"]*60,
            age=rng.uniform(20, 80, 60), sex=["F", "M", "O"]*20,
            retained_mean_fd_mm=rng.uniform(.03, .2, 60)))

    def test_design_and_hc3(self):
        data = self.sample()
        x, names = design(data)
        self.assertEqual(names, ["intercept", "age_decades_centered", "dataset_rf1", "sex_M", "sex_O", "retained_mean_fd_centered"])
        y = x @ np.array([2., .6, 1., .2, -.2, .7]) + np.sin(np.arange(60))*.05
        result = hc3_age(x, y)
        self.assertAlmostEqual(result["beta_per_decade"], .6, places=2)
        self.assertLess(result["ci95_low"], .6)
        self.assertGreater(result["ci95_high"], .6)
        self.assertLess(result["p_two_sided"], .001)

    def test_rank_failure(self):
        data = self.sample(); data["retained_mean_fd_mm"] = .1
        with self.assertRaisesRegex(ValueError, "rank-deficient"):
            design(data)

    def test_candidate_order_and_excluded_runs(self):
        data = self.sample()
        candidates = data[["dataset", "subject", "session", "runs"]].copy()
        candidates["type"] = "act"; candidates["cope"] = "10"
        candidates["contrast"] = "rew-pun"; candidates["cope_path"] = candidates.subject
        rows = ordered_candidates(candidates.iloc[::-1], data, "act", 10)
        self.assertEqual(rows.subject.tolist(), data.subject.tolist())
        candidates.loc[0, "runs"] = "1,2"
        with self.assertRaisesRegex(ValueError, "excluded"):
            ordered_candidates(candidates, data, "act", 10)

    def test_merged_order_roi_and_coverage(self):
        data = self.sample(); x, _ = design(data)
        y = .6*x[:, 1] + np.sin(np.arange(60))*.05
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            reference = nib.Nifti1Image(np.zeros((2, 2, 2)), np.eye(4))
            full = np.ones((2, 2, 2), dtype=bool)
            mask = full.copy(); mask[0, 0, 0] = False
            nib.save(nib.Nifti1Image(mask.astype(np.uint8), np.eye(4)), root / "mask.nii.gz")
            rows = []
            for i in range(60):
                path = root / f"cope-{i}.nii.gz"
                nib.save(nib.Nifti1Image(np.full((2, 2, 2), y[i]), np.eye(4)), path)
                rows.append(dict(cope_path=str(path), mask_path=str(root / "mask.nii.gz")))
            roi, info = prepare_model(pd.DataFrame(rows), data, x, reference, root / "model",
                                      {"VS": full, "vmPFC": full}, "ppi_seed-vs", 10)
            self.assertEqual(len(roi), 1)  # No PPI-in-seed ROI test.
            self.assertEqual(roi[0]["roi"], "vmPFC")
            self.assertEqual(roi[0]["common_roi_fraction"], 7/8)
            self.assertEqual(info["mask_voxels"], 7)
            merged = nib.load(root / "model/copes.nii.gz").get_fdata()
            np.testing.assert_allclose(merged[1, 1, 1], y, atol=1e-6)
            np.testing.assert_equal(merged[0, 0, 0], 0)

    def test_fsl_probability_direction_and_family_correction(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            nib.save(nib.Nifti1Image(np.ones((2, 2, 2)), np.eye(4)), root / "mask.nii.gz")
            def fake_command(*args):
                for i, p in ((1, .001), (2, .01)):
                    nib.save(nib.Nifti1Image(np.full((2, 2, 2), 1-p), np.eye(4)), root / f"age_tfce_corrp_tstat{i}.nii.gz")
            with patch("run_preliminary_age.command", side_effect=fake_command):
                rows = randomise_model(root, root, "randomise", 5000, 1)
            self.assertAlmostEqual(rows[0]["min_p_across_20_maps"], .02, places=5)
            self.assertEqual(rows[0]["voxels_p05_across_20_maps"], 8)
            self.assertEqual(rows[1]["voxels_p05_across_20_maps"], 0)
            vest(root / "design.con", np.array([[0, 1, 0], [0, -1, 0]]), contrast=True)
            self.assertIn("/NumContrasts\t2", (root / "design.con").read_text())


if __name__ == "__main__":
    unittest.main()
