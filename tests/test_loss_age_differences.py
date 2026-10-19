import sys
import unittest
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'code'))
from analyze_raw_ratings import CELLS, age_design, holm
from analyze_loss_rating_age import loss_tests, plot_loss_age
from plot_rating_age import age_predictions


class LossAgeDifferences(unittest.TestCase):
    def test_plot_matches_sex_adjusted_model_and_creates_outputs(self):
        rng=np.random.default_rng(881);n=90
        d=pd.DataFrame(dict(age=rng.uniform(18,88,n),sex=['F','M','O']*30,
                            dataset=['rf1','ds003745']*45))
        d[CELLS]=rng.normal(-2,1,(n,6))
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp); frame=plot_loss_age(d,output)
            for name,col in zip(['Friend','Stranger','Computer'],[5,3,1]):
                sub=frame[frame.partner.eq(name)]
                means,lo,hi,slopes=age_predictions(d,sub.age.to_numpy())
                np.testing.assert_allclose(sub.adjusted_mean,means[:,col])
                np.testing.assert_allclose(sub.ci95_low,lo[:,col])
                np.testing.assert_allclose(sub.ci95_high,hi[:,col])
                np.testing.assert_allclose(sub.points_per_decade,slopes[col])
            self.assertEqual(len(frame),540)
            self.assertTrue((output/'loss-ratings-by-age-sex-adjusted.png').is_file())
            self.assertTrue((output/'loss-ratings-by-age-sex-adjusted.svg').is_file())

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
