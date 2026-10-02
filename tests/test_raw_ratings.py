import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from analyze_raw_ratings import CELLS, age_fit, holm, load_ratings
from plot_rating_age import age_predictions
from audit_ratings_qc import rating_exclusion_reasons


class RawRatings(unittest.TestCase):
    def test_within_partner_rule_allows_ties_not_compensating_wins(self):
        equal = {(p,t): float(p) for p in (1,2,3) for t in (0,1)}
        self.assertEqual(rating_exclusion_reasons(equal), [])
        self.assertEqual(rating_exclusion_reasons({k: 0. for k in equal}), ["identical_ratings"])
        for partner in (1,2,3):
            means = {(p,t): (5. if t == 0 else -5.) for p,t in equal}
            means[(partner,0)], means[(partner,1)] = 1., 2.
            self.assertLess(sum(means[(p,1)] for p in (1,2,3)), sum(means[(p,0)] for p in (1,2,3)))
            self.assertEqual(rating_exclusion_reasons(means), [f"partner_{partner}_loss_greater_than_win"])

    def test_old_cohort_flag_cannot_restore_a_within_partner_violation(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            ratings = pd.DataFrame([dict(dataset='rf1',subject=str(i),exclude_subject='false',exclusion_reason='') for i in (1,2)])
            ratings[CELLS] = [[5,-5,5,-5,1,2], [5,-5,5,-5,2,2]]
            ratings.to_csv(temp/'ratings.tsv',sep='\t',index=False)
            pd.DataFrame([dict(dataset='rf1',subject=str(i),task_l2_ready='true',ratings_l2_ready='true') for i in (1,2)]).to_csv(temp/'cohort.tsv',sep='\t',index=False)
            data = load_ratings(temp/'ratings.tsv',temp/'cohort.tsv')
            self.assertEqual(data.subject.tolist(), ['2'])
            self.assertEqual(data.attrs['behavioral_eligibility'][0]['exclusion_reason'],'partner_3_loss_greater_than_win')

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

    def test_plot_predictions_match_marginal_fit_and_mean_covariance(self):
        from scipy import stats
        rng = np.random.default_rng(53); n = 120
        frame = pd.DataFrame(dict(age=rng.uniform(20,80,n), sex=['F','M','O']*40,
                                  dataset=['rf1','ds003745']*60))
        frame[CELLS] = rng.normal(size=(n,6)) + (frame.age.to_numpy()/100)[:,None]
        ages = np.array([30.,50.,70.])
        pred,lo,hi,slopes = age_predictions(frame, ages)
        x = np.column_stack([np.ones(n),(frame.age-frame.age.mean())/10,
                             frame.dataset.eq('rf1'),frame.sex.eq('M'),frame.sex.eq('O')]).astype(float)
        a = np.linalg.inv(x.T@x)@x.T
        y = frame[CELLS].to_numpy().mean(axis=1)
        b = a@y; residual = y-x@b; leverage = np.diag(x@a)
        covariance = (a*(residual/(1-leverage)))@(a*(residual/(1-leverage))).T
        g = x.mean(axis=0); g[1]=(50-frame.age.mean())/10
        self.assertAlmostEqual(pred[1,6],float(g@b))
        self.assertAlmostEqual(hi[1,6]-pred[1,6],float(stats.t.ppf(.975,n-5)*np.sqrt(g@covariance@g)))
        np.testing.assert_allclose(pred[:,6],pred[:,:6].mean(axis=1))
        np.testing.assert_allclose((pred[2]-pred[0])/4,slopes)
        np.testing.assert_allclose(lo+hi,2*pred)


if __name__ == '__main__':
    unittest.main()
