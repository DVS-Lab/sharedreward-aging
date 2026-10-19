import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'code'))
from plot_next_trial_rt_age import (CELLS, PARTNERS, absolute_curves, select_pairs,
    summarize, lag_design, loss_weights, joint_test)
from analyze_raw_ratings import age_design
from explore_trial_behavior import absorbed_fit, test_contrast


class NextTrialRT(unittest.TestCase):
    def test_six_absolute_curves_match_independent_hc3(self):
        rng = np.random.default_rng(911); n=90
        d=pd.DataFrame(dict(age=rng.uniform(18,90,n),sex=['F','M','O']*30,dataset=['rf1','ds003745']*45))
        d[CELLS]=rng.normal(size=(n,6))+.01*d.age.to_numpy()[:,None]
        ages=np.array([20,50,80]); predictions=absolute_curves(d,ages); x=age_design(d)
        g=np.tile(x.mean(axis=0),(3,1));g[:,1]=(ages-d.age.mean())/10
        for cell in CELLS:
            p,o=cell.split('_'); model=sm.OLS(d[cell],x).fit(cov_type='HC3',use_t=True)
            rows=predictions[predictions.previous_partner.eq(p)&predictions.previous_outcome.eq(o)]
            np.testing.assert_allclose(np.log(rows.geometric_rt_s),g@model.params)
            se=np.sqrt(np.einsum('ij,jk,ik->i',g,model.cov_params(),g))
            np.testing.assert_allclose(np.log(rows.ci95_high_s),g@model.params+stats.t.ppf(.975,n-x.shape[1])*se)

    def test_selection_does_not_bridge_misses_neutral_or_blocks(self):
        d=pd.DataFrame(dict(consecutive=[True,True,True,False,True,True],rt_s=[1]*6,
            prev_rt_s=[1,np.nan,1,1,1,1],dataset=['rf1']*4+['ds003745']*2,
            same_block=[True]*4+[False,True],prev_outcome=['reward','punish','neutral','reward','reward','punish'],feedback_gap_s=[1]*6))
        self.assertEqual(list(select_pairs(d,.15).index),[0,5])

    def test_missing_cells_fail(self):
        lag=pd.DataFrame(dict(dataset=['rf1'],subject=['1'],prev_partner=['friend'],prev_outcome=['reward'],rt_s=[1.]))
        demo=pd.DataFrame(dict(dataset=['rf1'],subject=['1'],age=[40],sex=['F']))
        with self.assertRaises(ValueError): summarize(lag,demo)

    def test_interaction_weights_and_covariance_against_explicit_fe(self):
        rng=np.random.default_rng(39); n=48; m=30; total=n*m
        demo=pd.DataFrame(dict(age=rng.uniform(18,90,n),sex=['F','M','O']*16,dataset=['rf1','ds003745']*24))
        lag=demo.loc[demo.index.repeat(m)].reset_index(drop=True)
        lag['prev_outcome']=rng.choice(['reward','punish'],total)
        lag['prev_partner']=rng.choice(PARTNERS,total);lag['partner']=rng.choice(PARTNERS,total)
        lag['prev_rt_s']=rng.uniform(.2,2,total);lag['feedback_gap_s']=rng.uniform(.5,3,total)
        lag['progress']=np.tile(np.linspace(0,1,m),n)
        lag['partner_switch']=lag.partner.ne(lag.prev_partner).astype(float)
        x=lag_design(lag,demo); groups=np.repeat(np.arange(n),m)
        y=rng.normal(size=total)+x.to_numpy()@rng.normal(0,.03,x.shape[1])
        fit=absorbed_fit(y,x,groups,groups)
        explicit=pd.concat([x,pd.get_dummies(groups,prefix='fe',dtype=float)],axis=1)
        reference=sm.OLS(y,explicit).fit(cov_type='cluster',cov_kwds={'groups':groups},use_t=True)
        np.testing.assert_allclose(fit['beta'],reference.params.iloc[:x.shape[1]],atol=1e-12)
        np.testing.assert_allclose(fit['cov'],reference.cov_params().iloc[:x.shape[1],:x.shape[1]],atol=1e-12)
        for p in PARTNERS:
            # Loss-minus-win difference of actual rows equals the requested contrast.
            example=lag.iloc[[0,0]].copy();example['prev_partner']=p;example['age']=70
            example['prev_outcome']=['punish','reward']
            dx=lag_design(example,demo).iloc[0]-lag_design(example,demo).iloc[1]
            dx[['loss_dataset','loss_sex_M','loss_sex_O']]=0
            w=loss_weights(p,70)
            v=np.array([w.get(k,0) for k in x.columns])
            np.testing.assert_allclose(v,dx)
            full=np.r_[v,np.zeros(n)]
            result=test_contrast(fit,w,'test',p,'logRT')
            self.assertAlmostEqual(result['p'],float(reference.t_test(full).pvalue))
        names=['loss_age_friend','loss_age_stranger']
        c=np.zeros((2,len(explicit.columns)))
        for j,name in enumerate(names):c[j,explicit.columns.get_loc(name)]=1
        result=joint_test(fit,names,'test')
        self.assertAlmostEqual(result['p'],float(reference.f_test(c).pvalue))


if __name__=='__main__':unittest.main()
