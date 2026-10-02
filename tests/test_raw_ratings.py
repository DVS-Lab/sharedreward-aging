import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from analyze_raw_ratings import CELLS, age_fit, holm, load_ratings


class RawRatings(unittest.TestCase):
    def test_holm_preserves_input_order(self):
        np.testing.assert_allclose(holm([.04, .001, .02]), [.04, .003, .04])

    def test_wide_fit_matches_subject_contrast_and_preserves_age_effect(self):
        rng = np.random.default_rng(42)
        n = 120
        frame = pd.DataFrame(dict(age=rng.uniform(20,80,n), sex=np.where(np.arange(n)%2,'F','M'),
                                  dataset=np.where(np.arange(n)%3,'rf1','ds003745')))
        y = rng.normal(size=(n,6)) + ((frame.age.to_numpy()-50)/10)[:,None] * np.arange(6)[None,:]/10
        frame[CELLS] = y
        b, covariance, df = age_fit(frame)
        # Independent HC3 calculation on one participant-level contrast.
        c = np.array([0,0,-1,1,1,-1.])
        x = np.column_stack([np.ones(n),(frame.age-frame.age.mean())/10,frame.dataset.eq('rf1'),frame.sex.eq('M')]).astype(float)
        inv = np.linalg.inv(x.T@x); a = inv@x.T; residual = y@c-x@(a@y@c)
        h = np.diag(x@a)
        variance = ((a[1]*residual/(1-h))**2).sum()
        self.assertAlmostEqual(float(c@covariance@c), variance)
        self.assertAlmostEqual(float(c@b), float((a@y@c)[1]))
        self.assertEqual(df,n-4)
        # Add an age trend shared by all cells; raw analysis must retain it.
        shifted = frame.copy(); shifted[CELLS] += ((frame.age-frame.age.mean())/10).to_numpy()[:,None]*.5
        b2, _, _ = age_fit(shifted)
        np.testing.assert_allclose(b2-b,.5)

    def test_current_cohort_has_six_raw_values_per_person(self):
        root = Path(__file__).resolve().parents[1]
        data = load_ratings(root/'logs/records/ratings-qc-subject-level.tsv',root/'logs/records/analysis-subject-dispositions.tsv')
        self.assertFalse(data.duplicated(['dataset','subject']).any())
        self.assertEqual(data[CELLS].shape[1],6)
        self.assertGreater(np.abs(data[CELLS].mean(axis=1)).sum(),1)

    def test_other_recorded_sex_is_retained_as_category(self):
        rng = np.random.default_rng(1); n = 60
        frame = pd.DataFrame(dict(age=rng.uniform(20,80,n), sex=['F','M','O']*20,
                                  dataset=['rf1']*n))
        frame[CELLS] = rng.normal(size=(n,6))
        _, _, df = age_fit(frame)
        self.assertEqual(df, n-4)  # intercept, age, M and O; all 60 retained


if __name__ == '__main__':
    unittest.main()
