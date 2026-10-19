#!/usr/bin/env python3
"""Direct paired tests of partner differences in loss-rating age slopes."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from analyze_raw_ratings import ROOT, KEYS, CELLS, age_fit, demographics, load_ratings, holm
from audit_ratings_qc import RATINGS_POLICY

PARTNERS = ['Friend', 'Stranger', 'Computer']
LOSS_WEIGHTS = np.eye(6)[[5, 3, 1]]
PAIR_NAMES = ['Friend minus Stranger', 'Friend minus Computer', 'Stranger minus Computer']
PAIR_WEIGHTS = np.array([LOSS_WEIGHTS[0]-LOSS_WEIGHTS[1],
                         LOSS_WEIGHTS[0]-LOSS_WEIGHTS[2],
                         LOSS_WEIGHTS[1]-LOSS_WEIGHTS[2]])


def loss_tests(data):
    rows = []
    for sex in (True, False):
        slopes, covariance, df = age_fit(data, adjust_sex=sex)
        critical = stats.t.ppf(.975, df)
        for family, names, weights in (
            ('individual_loss_age_slopes', PARTNERS, LOSS_WEIGHTS),
            ('paired_loss_slope_differences', PAIR_NAMES, PAIR_WEIGHTS)):
            group = []
            for name, c in zip(names, weights):
                estimate = float(c @ slopes)
                se = float(np.sqrt(c @ covariance @ c))
                if not np.isfinite(se) or se <= 0:
                    raise ValueError('Invalid slope comparison variance')
                group.append(dict(sex_adjusted=sex, family=family, comparison=name,
                    n=len(data), points_per_decade=estimate, se_hc3=se,
                    ci95_low=estimate-critical*se, ci95_high=estimate+critical*se,
                    df_t=df, p=float(2*stats.t.sf(abs(estimate/se), df))))
            for row, p in zip(group, holm([r['p'] for r in group])):
                row['p_holm_three'] = float(p)
            rows.extend(group)
        c = PAIR_WEIGHTS[:2]
        difference = c @ slopes
        w = float(difference @ np.linalg.solve(c @ covariance @ c.T, difference))
        rows.append(dict(sex_adjusted=sex, family='joint_loss_slope_equality',
            comparison='Age x partner for losses', n=len(data), chi2=w, df_chi2=2,
            p=float(stats.chi2.sf(w, 2))))
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT/'qc/ratings-raw/loss-age-comparisons')
    args = parser.parse_args()
    sources = [ROOT/'logs/records/ratings-qc-subject-level.tsv',
               ROOT/'logs/records/analysis-subject-dispositions.tsv',
               ROOT.parent/'rf1-sra-linux2/bids/participants.tsv', ROOT/'participants-srndna.tsv']
    data = load_ratings(*sources[:2])
    data = data.merge(pd.concat([demographics(sources[2], 'rf1'), demographics(sources[3], 'ds003745')]),
                      on=KEYS, how='left', validate='one_to_one').sort_values(KEYS)
    if not (data.age.between(18, 110) & data.sex.isin(['F', 'M', 'O'])).all():
        raise ValueError('Complete demographic coverage required; no silent sample change')
    results = loss_tests(data)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output_dir/'loss-age-tests.tsv', sep='\t', index=False)
    sources += [Path(__file__), ROOT/'code/analyze_raw_ratings.py', ROOT/'code/audit_ratings_qc.py']
    meta = dict(n=len(data), sample_by_dataset=data.groupby('dataset').size().to_dict(),
        recorded_sex_counts=data.sex.value_counts().to_dict(), ratings_policy=RATINGS_POLICY,
        design='Intercept + continuous centered age per decade + dataset dummy, with/without recorded-sex M/O offsets (F reference).',
        inference='Wide multivariate OLS with HC3 covariance retaining within-participant covariance; paired slope differences with t CIs/tests. Joint 2-df Wald chi-square test.',
        multiplicity='Holm across all three pairwise partner loss-slope comparisons within each specification. Separately Holm across three individual loss slopes. Exploratory follow-up, not experiment-wide control.',
        interpretation='Positive loss slope means less negative ratings at older ages. Positive Friend-minus-X slope means a larger age slope for Friend than X.',
        exclusions='Unchanged primary behavior-only sample; no imaging QC or extra ceiling/floor exclusions.',
        limitations=['Cross-sectional, not causal age effects.', 'Loss floors and response-based eligibility remain interpretive limitations.',
                     'Failure to reject slope differences is not evidence of equivalence.'],
        sources=[dict(path=str(p.resolve()), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sources])
    (args.output_dir/'provenance.json').write_text(json.dumps(meta, indent=2)+'\n')
    print(json.dumps(meta, indent=2))
    print(results.to_string(index=False))
    print('CHECK PASSED: direct paired loss-slope tests completed with and without recorded sex.')


if __name__ == '__main__':
    main()
