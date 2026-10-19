import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize, special

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'code'))
from analyze_raw_ratings import CELLS, age_design, age_fit
from check_ratings_ceiling import fractional_fit, endpoint_summary, slope_tables
from plot_rating_gaps import GAPS


class CeilingSensitivity(unittest.TestCase):
    def sample(self):
        rng=np.random.default_rng(129);n=120
        d=pd.DataFrame(dict(age=rng.uniform(18,88,n),sex=['F','M','O']*40,
                            dataset=['rf1','ds003745']*60))
        shared=rng.normal(size=(n,1))
        d[CELLS]=np.clip(np.rint(shared+rng.normal(size=(n,6))*2+np.arange(6)), -5,5)
        return d

    def test_fractional_endpoint_fit_and_paired_delta_covariance(self):
        d=self.sample();x=age_design(d);y=d[CELLS].to_numpy()
        slope,cov,coef=fractional_fit(x,y)
        self.assertTrue((y==5).any())
        independent=[]
        for j,b in enumerate(coef):
            response=(y[:,j]+5)/10
            result=optimize.minimize(lambda q: np.sum(np.logaddexp(0,x@q)-response*(x@q)),
                np.zeros(x.shape[1]),jac=lambda q:x.T@(special.expit(x@q)-response),
                method='BFGS',options={'gtol':1e-7})
            np.testing.assert_allclose(result.x,b,atol=2e-6)
            def effect(q):
                p=special.expit(x@q)
                return 10*q[1]*np.mean(p*(1-p))
            delta=np.eye(len(b))*1e-5
            gradient=np.array([(effect(b+step)-effect(b-step))/2e-5 for step in delta])
            mu=special.expit(x@b)
            information=x.T@np.diag(mu*(1-mu))@x
            independent.append(((response-mu)[:,None]*x)@np.linalg.inv(information)@gradient)
            self.assertAlmostEqual(slope[j],effect(b))
        influence=np.column_stack(independent)
        np.testing.assert_allclose(cov,influence.T@influence*len(d)/(len(d)-x.shape[1]),rtol=1e-6,atol=1e-10)
        c=GAPS[0]-GAPS[1]
        self.assertGreater(float(c@cov@c),0)
        self.assertGreater(abs(cov[0,1]),1e-6)

    def test_same_sample_and_exact_ols_gap_decomposition(self):
        d=self.sample();table,endpoints=slope_tables(d)
        self.assertTrue(table.n.eq(len(d)).all())
        self.assertTrue(endpoints.n.eq(len(d)).all())
        for sex in (True,False):
            b,cov,_=age_fit(d,sex)
            s=table[table.method.eq('OLS_HC3') & table.sex_adjusted.eq(sex)]
            friend=s[s.comparison.eq('Friend')].iloc[0]
            self.assertAlmostEqual(friend.points_per_decade,b[4]-b[5])
            self.assertAlmostEqual(friend.se,np.sqrt(GAPS[0]@cov@GAPS[0]))

    def test_endpoint_counts_and_age_boundaries(self):
        d=pd.DataFrame(dict(age=[18,39,40,59,60,88]))
        d[CELLS]=np.tile([5,-5,4,-4,5,5],(6,1))
        s=endpoint_summary(d)
        self.assertTrue(s[s.age_group.ne('All ages')].n.eq(2).all())
        row=s[s.age_group.eq('All ages') & s.condition.eq('Friend win') & s.endpoint.eq('ceiling')].iloc[0]
        self.assertEqual(row['count'],6);self.assertEqual(row.percent,100)
        self.assertLess(row.ci95_low,100)
        self.assertAlmostEqual(row.ci95_high,100)


if __name__=='__main__':
    unittest.main()
