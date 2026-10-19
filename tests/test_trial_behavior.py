import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.sandwich_covariance import cov_cluster

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'code'))
from explore_trial_behavior import absorbed_fit, add_lags, check_counts


class TrialBehavior(unittest.TestCase):
    def test_absorbed_matches_explicit_fixed_effects_and_cluster_covariance(self):
        rng = np.random.default_rng(4109)
        n = 900
        cluster = np.repeat(np.arange(30), 30)
        group = np.repeat(np.arange(90), 10)
        x = pd.DataFrame(rng.normal(size=(n, 3)), columns=['a', 'b', 'c'])
        y = x.to_numpy()@np.array([.1, .2, -.3])+rng.normal(size=90)[group]+rng.normal(size=n)
        result = absorbed_fit(y, x, group, cluster)
        dummy = pd.get_dummies(group, dtype=float).to_numpy()
        explicit = sm.OLS(y, np.column_stack([x, dummy])).fit()
        np.testing.assert_allclose(result['beta'], explicit.params[:3], atol=1e-12)
        np.testing.assert_allclose(result['cov'], cov_cluster(explicit, cluster)[:3, :3], atol=1e-12)
        self.assertEqual(result['df'], 29)

    def test_misses_and_block_boundaries_are_not_bridged(self):
        d = pd.DataFrame(dict(dataset=['ds003745']*5, subject=['104']*5, session=['']*5,
            run=[1,1,1,1,2], trial=[1,2,3,4,1], block=[1,1,1,2,1],
            onset=[1.,5.,9.,40.,1.], outcome_end=[4.,8.,12.,43.,4.],
            rt_s=[1.,np.nan,1.1,1.2,1.3], response=[2,np.nan,3,2,3],
            missed=[0,1,0,0,0], partner=['friend']*5,
            outcome=['reward','miss','punish','reward','reward']))
        out = add_lags(d)
        self.assertEqual(out.iloc[2].prev_outcome, 'miss')
        self.assertTrue(np.isnan(out.iloc[2].prev_rt_s))
        self.assertFalse(out.iloc[3].same_block)
        self.assertFalse(out.iloc[4].consecutive)
        self.assertTrue(np.isnan(out.iloc[4].prev_rt_s))

    def test_event_count_mismatch_fails(self):
        with self.assertRaises(ValueError):
            check_counts([], {'n_trials':1})


if __name__ == '__main__': unittest.main()
