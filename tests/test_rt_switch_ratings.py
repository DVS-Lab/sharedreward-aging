import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from analyze_rt_switch_ratings import (switch_design,switching_weights,hc3_fit,cv_folds,cv_rmse,
    person_features,FEATURES,SWITCH_FEATURE)
from explore_trial_behavior import absorbed_fit, test_contrast
from plot_next_trial_rt_age import PARTNERS, joint_test


class RTSwitchRatings(unittest.TestCase):
    def test_switch_contrasts_against_explicit_fixed_effect_regression(self):
        rng=np.random.default_rng(910);n=42;m=60
        demo=pd.DataFrame(dict(dataset=['rf1']*n,age=rng.uniform(18,90,n),sex=['F','M','O']*14))
        d=demo.loc[demo.index.repeat(m)].reset_index(drop=True)
        d['partner']=rng.choice(PARTNERS,len(d));d['prev_partner']=rng.choice(PARTNERS,len(d))
        d['prev_outcome']=rng.choice(['reward','punish'],len(d));d['prev_rt_s']=rng.uniform(.2,2,len(d))
        d['partner_switch']=d.partner.ne(d.prev_partner).astype(float)
        d['feedback_gap_s']=rng.uniform(.5,4,len(d));d['progress']=np.tile(np.linspace(0,1,m),n)
        x=switch_design(d,demo);groups=np.repeat(np.arange(n),m)
        y=rng.normal(size=len(d))+x.to_numpy()@rng.normal(0,.03,x.shape[1])
        fitted=absorbed_fit(y,x,groups,groups)
        explicit=pd.concat([x,pd.get_dummies(groups,prefix='fe',dtype=float)],axis=1)
        reference=sm.OLS(y,explicit).fit(cov_type='cluster',cov_kwds={'groups':groups},use_t=True)
        np.testing.assert_allclose(fitted['beta'],reference.params.iloc[:x.shape[1]],atol=1e-12)
        np.testing.assert_allclose(fitted['cov'],reference.cov_params().iloc[:x.shape[1],:x.shape[1]],atol=1e-12)
        for p in PARTNERS:
            # Finite difference: (loss-win when switch) - (loss-win when stay).
            rows=d.iloc[[0]*4].copy();rows['age']=50;rows['prev_partner']=p
            rows['prev_outcome']=['punish','reward','punish','reward'];rows['partner_switch']=[1,1,0,0]
            rows['partner']=[next(q for q in PARTNERS if q!=p)]*2+[p]*2
            design=switch_design(rows,demo)
            delta=design.iloc[0]-design.iloc[1]-design.iloc[2]+design.iloc[3]
            weights=switching_weights(p,difference=True);v=np.array([weights.get(k,0) for k in x.columns])
            np.testing.assert_allclose(delta,v,atol=1e-12)
            result=test_contrast(fitted,weights,'test',p,'logRT')
            self.assertAlmostEqual(result['p'],float(reference.t_test(np.r_[v,np.zeros(n)]).pvalue))
        c=np.zeros((2,explicit.shape[1]))
        for i,name in enumerate(['loss_switch_friend','loss_switch_stranger']):c[i,explicit.columns.get_loc(name)]=1
        result=joint_test(fitted,['loss_switch_friend','loss_switch_stranger'],'joint')
        self.assertAlmostEqual(result['p'],float(reference.f_test(c).pvalue))

    def test_ratings_hc3_matches_statsmodels(self):
        rng=np.random.default_rng(9);x=np.column_stack([np.ones(100),rng.normal(size=(100,5))]);y=rng.normal(size=100)
        b,c,df,r2,adj=hc3_fit(x,y);model=sm.OLS(y,x).fit(cov_type='HC3',use_t=True)
        np.testing.assert_allclose(b,model.params);np.testing.assert_allclose(c,model.cov_params())
        self.assertEqual(df,model.df_resid);self.assertAlmostEqual(r2,model.rsquared);self.assertAlmostEqual(adj,model.rsquared_adj)

    def test_folds_and_training_only_scaling(self):
        rng=np.random.default_rng(1);n=90
        data=pd.DataFrame(dict(dataset=['rf1','ds003745']*45,sex=['F','M','O']*30))
        folds=cv_folds(data,repeats=2);again=cv_folds(data,repeats=2)
        for a,b in zip(folds,again):np.testing.assert_array_equal(a,b)
        base=np.column_stack([np.ones(n),rng.normal(size=n)]);f=rng.normal(size=(n,2));y=rng.normal(size=n)
        result=cv_rmse(base,f,y,folds)
        for j,fold in enumerate(folds):
            prediction=np.zeros(n)
            for k in range(10):
                train=fold!=k;test=~train
                x=np.column_stack([base,f])
                prediction[test]=x[test]@sm.OLS(y[train],x[train]).fit().params
            self.assertAlmostEqual(result[j],np.sqrt(np.mean((y-prediction)**2)))

    def test_features_preserve_missing_switches_in_older_dataset(self):
        rows=[]
        for dataset in ('rf1','ds003745'):
            for p in PARTNERS:
                for outcome in ('reward','punish'):
                    for switch in ([0.,1.] if dataset=='rf1' else [0.]):
                        rows.append(dict(dataset=dataset,subject='1',partner=p,prev_partner=p,prev_outcome=outcome,
                            rt_s=np.exp(.1*(outcome=='punish')+.05*switch*(outcome=='punish')),
                            prev_rt_s=1.,consecutive=True,same_block=True,feedback_gap_s=1.,partner_switch=switch))
        d=pd.DataFrame(rows);demo=pd.DataFrame(dict(dataset=['rf1','ds003745'],subject=['1','1'],age=[40,50],sex=['F','M']))
        result=person_features(d,demo).set_index('dataset')
        self.assertTrue(np.isfinite(result[FEATURES].to_numpy()).all())
        self.assertTrue(np.isnan(result.loc['ds003745',SWITCH_FEATURE]))
        self.assertAlmostEqual(result.loc['rf1',SWITCH_FEATURE],.05)
        with self.assertRaises(ValueError):switch_design(d,demo)


if __name__=='__main__':unittest.main()
