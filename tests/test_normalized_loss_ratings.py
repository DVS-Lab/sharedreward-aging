import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from analyze_raw_ratings import CELLS
from plot_normalized_loss_ratings import transform
from analyze_loss_rating_age import loss_tests


class NormalizedRatings(unittest.TestCase):
    def data(self):
        rng=np.random.default_rng(432)
        d=pd.DataFrame(dict(age=rng.uniform(18,88,90),sex=['F','M','O']*30,
                            dataset=['rf1','ds003745']*45))
        d[CELLS]=rng.normal(size=(90,6))
        return d

    def test_six_cell_normalization_and_affine_invariance(self):
        d=self.data(); centered=transform(d,'person_centered'); z=transform(d,'person_zscored')
        np.testing.assert_allclose(centered[CELLS].mean(axis=1),0,atol=1e-12)
        np.testing.assert_allclose(z[CELLS].mean(axis=1),0,atol=1e-12)
        np.testing.assert_allclose(z[CELLS].std(axis=1,ddof=1),1,atol=1e-12)
        shifted=d.copy(); shifted[CELLS]=d[CELLS]*3+7
        np.testing.assert_allclose(transform(shifted,'person_zscored')[CELLS],z[CELLS],atol=1e-12)
        self.assertTrue(np.abs(z[CELLS].iloc[:,[1,3,5]].mean(axis=1)).max()>.1)
        pd.testing.assert_frame_equal(transform(d,'raw'),d)

    def test_centering_preserves_paired_comparisons(self):
        d=self.data()
        raw=loss_tests(d); centered=loss_tests(transform(d,'person_centered'))
        for table in (raw,centered):
            self.assertTrue(table.n.eq(len(d)).all())
        cols=['points_per_decade','se_hc3','p']
        np.testing.assert_allclose(raw.loc[raw.family.eq('paired_loss_slope_differences'),cols],
            centered.loc[centered.family.eq('paired_loss_slope_differences'),cols],atol=1e-10)

    def test_zero_sd_fails_without_dropping_subject(self):
        d=self.data();d.loc[0,CELLS]=2
        with self.assertRaisesRegex(ValueError,'Zero within-person SD'):
            transform(d,'person_zscored')


if __name__=='__main__':
    unittest.main()
