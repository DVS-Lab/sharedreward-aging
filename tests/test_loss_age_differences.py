import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'code'))
from analyze_raw_ratings import CELLS, age_design, holm
from analyze_loss_rating_age import loss_tests


class LossAgeDifferences(unittest.TestCase):
    def test_matches_direct_subject_difference_hc3_in_both_models(self):
        rng = np.random.default_rng(192)
        n = 120
        d = pd.DataFrame(dict(age=rng.uniform(18,88,n), sex=['F','M','O']*40,
                             dataset=['rf1','ds003745']*60))
        d[CELLS] = rng.normal(size=(n,6)) + rng.normal(size=(n,1))
        result = loss_tests(d)
        self.assertTrue(result.n.eq(n).all())
        for sex in (True, False):
            x = age_design(d,sex); a = np.linalg.inv(x.T@x)@x.T
            y = d[CELLS[5]].to_numpy()-d[CELLS[3]].to_numpy()
            b = a@y; h = np.diag(x@a); residual = y-x@b
            v = (a*(residual/(1-h)))@(a*(residual/(1-h))).T
            r = result[result.sex_adjusted.eq(sex) & result.comparison.eq('Friend minus Stranger')].iloc[0]
            self.assertAlmostEqual(r.points_per_decade,b[1])
            self.assertAlmostEqual(r.se_hc3,np.sqrt(v[1,1]))
            self.assertAlmostEqual(r.p,2*stats.t.sf(abs(b[1]/np.sqrt(v[1,1])),n-x.shape[1]))
            pairs = result[result.sex_adjusted.eq(sex) & result.family.eq('paired_loss_slope_differences')]
            np.testing.assert_allclose(pairs.p_holm_three,holm(pairs.p.to_numpy()))
            joint = result[result.sex_adjusted.eq(sex) & result.family.eq('joint_loss_slope_equality')].iloc[0]
            self.assertEqual(joint.df_chi2,2)


if __name__ == '__main__':
    unittest.main()
