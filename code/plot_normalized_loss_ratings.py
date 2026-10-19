#!/usr/bin/env python3
"""Compare raw, person-centered and person-z-scored loss-rating age curves."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analyze_raw_ratings import ROOT, KEYS, CELLS, demographics, load_ratings
from audit_ratings_qc import RATINGS_POLICY
from analyze_loss_rating_age import PARTNERS, loss_tests
from plot_rating_age import age_predictions

METHODS = ['raw', 'person_centered', 'person_zscored']


def transform(data, method):
    """Equal-weight six-cell profile; sample SD (ddof=1), never losses only."""
    if method not in METHODS:
        raise ValueError(f'Unknown normalization: {method}')
    values = data[CELLS].to_numpy(float)
    if not np.isfinite(values).all():
        raise ValueError('Six finite ratings required for every participant')
    result = data.copy()
    if method == 'raw':
        return result
    centered = values-values.mean(axis=1, keepdims=True)
    if method == 'person_centered':
        result[CELLS] = centered
    else:
        sd = values.std(axis=1, ddof=1, keepdims=True)
        if (sd <= 1e-12).any():
            raise ValueError('Zero within-person SD: no silent participant exclusion')
        result[CELLS] = centered/sd
    return result


def comparison(data, output):
    ages = np.linspace(data.age.min(), data.age.max(), 180)
    fig, axes = plt.subplots(1, 3, figsize=(14, 6.0), sharex=True)
    fig.subplots_adjust(left=.065, right=.985, top=.78, bottom=.25, wspace=.28)
    titles = ['Raw ratings', 'Person-mean centered', 'Within-person z-scores']
    ylabels = ['Rating points', 'Points relative to own six-rating mean', 'Within-person SD units']
    colors = ['#326B9F', '#C07A32', '#338574']
    predictions, tests = [], []
    for ax, method, title, ylabel in zip(axes, METHODS, titles, ylabels):
        frame = transform(data, method)
        means, low, high, slopes = age_predictions(frame, ages)
        table = loss_tests(frame)
        table = table[table.sex_adjusted.eq(True)].copy()
        table.insert(0, 'normalization', method)
        table.rename(columns={'points_per_decade':'units_per_decade'}, inplace=True)
        table['units'] = 'within_person_SD' if method == 'person_zscored' else 'rating_points'
        tests.append(table)
        for name, col, color, style in zip(PARTNERS, [5,3,1], colors, ['-','--','-.']):
            ax.fill_between(ages, low[:,col], high[:,col], color=color, alpha=.16, linewidth=0)
            ax.plot(ages, means[:,col], color=color, linestyle=style, lw=2.6, label=name)
            for i, age in enumerate(ages):
                predictions.append(dict(normalization=method, partner=name, n=len(data), age=age,
                    adjusted_mean=means[i,col], ci95_low=low[i,col], ci95_high=high[i,col]))
        ax.set(xlabel='Age (years)', ylabel=ylabel, xlim=(ages.min(), ages.max()))
        ax.set_title(title, fontsize=13, fontweight='bold', loc='left')
        ax.set_xticks([20,40,60,80]); ax.spines[['top','right']].set_visible(False)
        ax.grid(axis='y', color='#E6EAED', lw=.8); ax.set_axisbelow(True)
        if method == 'person_zscored':
            ax.set_ylim(-1.7,0); ax.set_yticks([-1.5,-1,-.5,0])
        else:
            ax.set_ylim(-4,0); ax.set_yticks([-4,-3,-2,-1,0])
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='center', bbox_to_anchor=(.5,.835), ncol=3, frameon=False)
    fig.suptitle('Loss ratings across age: within-person normalization', fontsize=20, y=.97)
    fig.text(.5,.905,f'Same {len(data)} participants, behavioral exclusions, dataset and recorded-sex adjustment',
             ha='center',fontsize=11,color='#505A63')
    fig.text(.065,.14,'Centering subtracts each person’s mean across all six ratings. Z-scoring also divides by their six-rating sample SD.',fontsize=10)
    fig.text(.065,.095,'Shading: pointwise HC3 95% confidence intervals for adjusted means. Note the different units in the right panel.',fontsize=10)
    fig.text(.065,.05,'Exclusions are evaluated on raw ratings before normalization. These sensitivity analyses do not replace the raw-rating primary model.',fontsize=9.5)
    for ext in ('png','svg'):
        fig.savefig(output/f'loss-ratings-normalization-comparison.{ext}',dpi=180)
    plt.close(fig)
    tests = pd.concat(tests,ignore_index=True)
    predictions = pd.DataFrame(predictions)
    tests.to_csv(output/'loss-age-tests.tsv',sep='\t',index=False)
    predictions.to_csv(output/'loss-age-predictions.tsv',sep='\t',index=False)
    return tests


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',type=Path,default=ROOT/'qc/ratings-normalized')
    args=p.parse_args()
    sources=[ROOT/'logs/records/ratings-qc-subject-level.tsv', ROOT/'logs/records/analysis-subject-dispositions.tsv',
             ROOT.parent/'rf1-sra-linux2/bids/participants.tsv',ROOT/'participants-srndna.tsv']
    data=load_ratings(*sources[:2])
    data=data.merge(pd.concat([demographics(sources[2],'rf1'),demographics(sources[3],'ds003745')]),
                    on=KEYS,how='left',validate='one_to_one').sort_values(KEYS)
    if not (data.age.between(18,110) & data.sex.isin(['F','M','O'])).all():
        raise ValueError('Complete demographics required; no silent sample change')
    args.output_dir.mkdir(parents=True,exist_ok=True)
    tests=comparison(data,args.output_dir)
    # Centering removes a common offset but must not alter paired loss contrasts.
    raw=tests[tests.normalization.eq('raw') & tests.family.eq('paired_loss_slope_differences')]
    centered=tests[tests.normalization.eq('person_centered') & tests.family.eq('paired_loss_slope_differences')]
    np.testing.assert_allclose(raw[['units_per_decade','se_hc3','p']],centered[['units_per_decade','se_hc3','p']],atol=1e-10)
    sources += [Path(__file__),ROOT/'code/analyze_raw_ratings.py',ROOT/'code/audit_ratings_qc.py',
                ROOT/'code/plot_rating_age.py',ROOT/'code/analyze_loss_rating_age.py']
    meta=dict(n=len(data),sample_by_dataset=data.groupby('dataset').size().to_dict(),ratings_policy=RATINGS_POLICY,
        normalization='Within each participant, equally weight all six partner x outcome cell means. Center by six-cell mean; z-score by six-cell sample SD (ddof=1). No pooling of SDs, no loss-only normalization.',
        exclusions='Applied to raw ratings first. Identical sample for all three models; zero SD fails explicitly. No imaging QC exclusions.',
        model='Intercept + centered continuous age per decade + dataset + recorded sex; condition-specific coefficients, paired HC3 covariance.',
        inference='Pointwise t confidence intervals. Holm over three pairwise loss-slope tests within each normalization; separately over three individual loss slopes. Exploratory, not experiment-wide correction.',
        interpretation='Centering targets relative rating level; z-scoring also adjusts scale spread. Normalization may remove response-style differences and substantive between-person differences; no claim to identify pure response bias.',
        primary_model_changed=False,
        sources=[dict(path=str(f.resolve()),sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sources])
    (args.output_dir/'provenance.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps(meta,indent=2)); print(tests.to_string(index=False))
    print('CHECK PASSED: normalized loss plots and paired slope tests, same sample and raw-rating exclusions.')


if __name__=='__main__':
    main()
