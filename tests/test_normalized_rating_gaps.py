import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from analyze_raw_ratings import CELLS, age_design
from plot_rating_gaps import gap_analysis, GAPS
from plot_normalized_loss_ratings import transform
from plot_normalized_rating_gaps import difference_predictions


class NormalizedGaps(unittest.TestCase):
    def test_sex_adjustment_toggle_preserves_sample_and_direct_test(self):
        rng=np.random.default_rng(997);n=120
        d=pd.DataFrame(dict(age=rng.uniform(18,88,n),sex=['F','M','O']*40,
                            dataset=['rf1','ds003745']*60))
        d[CELLS]=rng.normal(size=(n,6))
        z=transform(d,'person_zscored')
        for sex in (True,False):
            _,_,_,table=gap_analysis(z,[30,60],adjust_sex=sex)
            self.assertTrue(table.n.eq(n).all())
            x=age_design(z,sex);a=np.linalg.inv(x.T@x)@x.T
            y=z[CELLS].to_numpy()@(GAPS[0]-GAPS[1]);b=a@y
            residual=y-x@b;h=np.diag(x@a)
            cov=(a*(residual/(1-h)))@(a*(residual/(1-h))).T
            row=table[table.comparison.eq('Friend minus Stranger')].iloc[0]
            self.assertAlmostEqual(row.points_per_decade,b[1])
            self.assertEqual(row.df,n-x.shape[1])
            self.assertAlmostEqual(row.p,2*stats.t.sf(abs(b[1]/np.sqrt(cov[1,1])),n-x.shape[1]))

    def test_normalized_gaps_and_direct_difference_prediction(self):
        rng=np.random.default_rng(278);n=120
        d=pd.DataFrame(dict(age=rng.uniform(18,88,n),sex=['F','M','O']*40,
                            dataset=['rf1','ds003745']*60))
        d[CELLS]=rng.normal(size=(n,6))
        z=transform(d,'person_zscored')
        np.testing.assert_allclose(z[CELLS].to_numpy()@GAPS.T,
            (d[CELLS].to_numpy()@GAPS.T)/d[CELLS].std(axis=1,ddof=1).to_numpy()[:,None])
        ages=np.array([25.,45.,65.,85.])
        mean,lo,hi,dots,slope=difference_predictions(z,ages)
        means,_,_,tests=gap_analysis(z,ages)
        np.testing.assert_allclose(mean,means[:,0]-means[:,1])
        row=tests[tests.comparison.eq('Friend minus Stranger')].iloc[0]
        self.assertAlmostEqual(slope,row.points_per_decade)
        x=age_design(z);y=z[CELLS].to_numpy()@(GAPS[0]-GAPS[1]);a=np.linalg.inv(x.T@x)@x.T
        beta=a@y;residual=y-x@beta;h=np.diag(x@a)
        cov=(a*(residual/(1-h)))@(a*(residual/(1-h))).T
        g=np.tile(x.mean(axis=0),(len(ages),1));g[:,1]=(ages-d.age.mean())/10
        widths=stats.t.ppf(.975,n-x.shape[1])*np.sqrt(np.einsum('ij,jk,ik->i',g,cov,g))
        np.testing.assert_allclose(hi-mean,widths);np.testing.assert_allclose(lo,mean-widths)
        np.testing.assert_allclose(dots,residual+beta[0]+x[:,1]*beta[1]+x[:,2:].mean(axis=0)@beta[2:])
        self.assertAlmostEqual(row.se_hc3,np.sqrt(cov[1,1]))


if __name__=='__main__':
    unittest.main()
