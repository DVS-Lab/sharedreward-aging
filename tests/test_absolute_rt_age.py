import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from plot_absolute_rt_age import fit, PARTNERS, summarize
from analyze_raw_ratings import age_design


class AbsoluteRTAge(unittest.TestCase):
    def test_curves_and_paired_slopes_match_direct_regressions(self):
        rng=np.random.default_rng(8924);n=120
        d=pd.DataFrame(dict(age=rng.uniform(18,90,n),sex=['F','M','O']*40,dataset=['rf1','ds003745']*60))
        d[PARTNERS]=rng.normal(size=(n,3))+.01*d.age.to_numpy()[:,None]
        ages=np.array([20,50,80]);pred,table=fit(d,ages);x=age_design(d)
        g=np.tile(x.mean(axis=0),(3,1));g[:,1]=(ages-d.age.mean())/10
        for partner in PARTNERS:
            model=sm.OLS(d[partner],x).fit(cov_type='HC3',use_t=True)
            p=pred[pred.partner.eq(partner)]
            np.testing.assert_allclose(np.log(p.geometric_rt_s),g@model.params)
            se=np.sqrt(np.einsum('ij,jk,ik->i',g,model.cov_params(),g))
            np.testing.assert_allclose(np.log(p.ci95_high_s),g@model.params+stats.t.ppf(.975,n-x.shape[1])*se)
        model=sm.OLS(d.friend-d.stranger,x).fit(cov_type='HC3',use_t=True)
        row=table[table.comparison.eq('friend minus stranger')].iloc[0]
        self.assertAlmostEqual(row.log_rt_per_decade,model.params.iloc[1])
        self.assertAlmostEqual(row.p,model.pvalues.iloc[1])

    def test_missing_partner_is_not_silently_dropped(self):
        d=pd.DataFrame(dict(dataset=['rf1']*2,subject=['10402']*2,age=[50]*2,sex=['F']*2,
                            partner=['friend','stranger'],rt_s=[.8,.9]))
        with self.assertRaises((ValueError,KeyError)):summarize(d)


if __name__=='__main__':unittest.main()
