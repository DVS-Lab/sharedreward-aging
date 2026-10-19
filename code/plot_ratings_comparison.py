#!/usr/bin/env python3
"""Matched raw/z-scored rating bars and friend-minus-stranger age contrasts."""
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
from plot_normalized_loss_ratings import transform
from plot_normalized_rating_gaps import difference_predictions
from plot_rating_gaps import gap_analysis


def bar_summary(data):
    values = data[CELLS].to_numpy(float)
    if not np.isfinite(values).all() or len(data) < 2:
        raise ValueError('Complete six-cell ratings and at least two people required')
    return pd.DataFrame(dict(partner=np.repeat(['Computer', 'Stranger', 'Friend'], 2),
                             outcome=['Win', 'Loss'] * 3, n=len(data),
                             mean=values.mean(axis=0), sem=values.std(axis=0, ddof=1)/np.sqrt(len(data))))


def plot_version(data, method, output):
    d = transform(data, method)
    normalized = method == 'person_zscored'
    name = 'normalized' if normalized else 'raw'
    units = 'within-person SD' if normalized else 'rating points'
    bars = bar_summary(d)
    ages = np.linspace(d.age.min(), d.age.max(), 180)
    mean, low, high, dots, slope = difference_predictions(d, ages)
    _, _, _, tests = gap_analysis(d, ages)
    test = tests.loc[tests.comparison.eq('Friend minus Stranger')].iloc[0]
    np.testing.assert_allclose(slope, test.points_per_decade, atol=1e-12)
    fig, (ax, scatter) = plt.subplots(1, 2, figsize=(14, 7.6), gridspec_kw={'width_ratios': [1, 1.15]})
    fig.subplots_adjust(left=.075, right=.975, top=.77, bottom=.26, wspace=.32)
    colors = ['#287CA0', '#D17A43']
    for j, label in enumerate(['Win', 'Loss']):
        rows = bars[bars.outcome.eq(label)]
        ax.bar(np.arange(3)+(j-.5)*.34, rows['mean'], width=.32, yerr=rows['sem'],
               capsize=4, color=colors[j], label=label, error_kw={'elinewidth': 1.4})
    ax.axhline(0, color='#64717A', lw=1)
    ax.set_xticks(np.arange(3), ['Computer', 'Stranger', 'Friend'])
    ax.set_ylabel('Rating (within-person z-score)' if normalized else 'Rating (raw scale)')
    ax.set_xlabel('Partner')
    ax.set_ylim((-1.5, 2) if normalized else (-5, 5))
    ax.legend(frameon=False, ncol=2, loc='upper left', fontsize=12)
    ax.set_title('A   Ratings by partner and outcome', loc='left', fontsize=15, pad=16)
    scatter.scatter(d.age, dots, s=24, color='#68747D', alpha=.35, edgecolors='none', zorder=2)
    scatter.axhline(0, color='#8D969D', lw=.9, ls=':', zorder=1)
    scatter.fill_between(ages, low, high, color=colors[0], alpha=.20, linewidth=0, zorder=3)
    scatter.plot(ages, mean, color=colors[0], lw=3, zorder=4)
    margin = .05 * (max(dots.max(), high.max())-min(dots.min(), low.min()))
    scatter.set_ylim(min(dots.min(), low.min())-margin, max(dots.max(), high.max())+margin)
    scatter.set(xlabel='Age (years)', ylabel=f'Friend − stranger win–loss difference\n({units})',
                xlim=(ages.min()-1, ages.max()+1), xticks=[20, 40, 60, 80])
    scatter.set_title('B   Does the friend advantage decrease with age?', loc='left', fontsize=14, pad=16)
    for panel in (ax, scatter):
        panel.spines[['top', 'right']].set_visible(False)
        panel.tick_params(labelsize=12)
        panel.xaxis.label.set_size(13); panel.yaxis.label.set_size(13)
        panel.grid(axis='y', color='#E7EBEE', lw=.8); panel.set_axisbelow(True)
    fig.suptitle('Post-task subjective ratings: '+('within-person normalized' if normalized else 'raw'), fontsize=23, y=.96)
    fig.text(.5, .89, f'N = {len(data)}  ·  Same behavioral exclusions and participants in both versions', ha='center', fontsize=13, color='#4F5C67')
    fig.text(.075, .175, f'Age slope: {slope:+.3f} {units}/decade   '
             f'(95% CI {test.ci95_low:+.3f} to {test.ci95_high:+.3f})   |   Uncorrected p = {test.p:.3f}', fontsize=12.5)
    fig.text(.075, .12, 'Bars: pooled means ± between-person SEM. Right: (friend win − friend loss) − (stranger win − stranger loss).', fontsize=10.5)
    fig.text(.075, .075, 'Age model adjusts for dataset and recorded sex. Dots adjusted to the sample’s covariate mix; shading: HC3 95% confidence band.', fontsize=10.5)
    fig.text(.075, .03, 'Normalization: each person’s six ratings centered and divided by their sample SD before forming contrasts.' if normalized else
             'Raw ratings are not centered or rescaled within participants. The age model and exclusions match the normalized version.', fontsize=10.5)
    for ext in ('png', 'svg'):
        fig.savefig(output/f'{name}-ratings-bars-age-contrast.{ext}', dpi=220)
    plt.close(fig)
    bars.insert(0, 'scale', name)
    tests.insert(0, 'scale', name)
    tests['slope_units'] = units+'/decade'
    predictions = pd.DataFrame(dict(scale=name, age=ages, adjusted_mean=mean, ci95_low=low, ci95_high=high))
    return bars, tests, predictions


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir', type=Path, default=ROOT/'qc/ratings-comparison')
    args = p.parse_args()
    sources = [ROOT/'logs/records/ratings-qc-subject-level.tsv', ROOT/'logs/records/analysis-subject-dispositions.tsv',
               ROOT.parent/'rf1-sra-linux2/bids/participants.tsv', ROOT/'participants-srndna.tsv']
    data = load_ratings(*sources[:2]).merge(pd.concat([demographics(sources[2], 'rf1'), demographics(sources[3], 'ds003745')]),
                                          on=KEYS, how='left', validate='one_to_one').sort_values(KEYS)
    if not (data.age.between(18, 110) & data.sex.isin(['F', 'M', 'O'])).all():
        raise ValueError('Complete demographics required; no silent sample change')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = [plot_version(data, method, args.output_dir) for method in ('raw', 'person_zscored')]
    for i, filename in enumerate(['bar-summary.tsv', 'age-tests.tsv', 'age-predictions.tsv']):
        pd.concat([r[i] for r in results], ignore_index=True).to_csv(args.output_dir/filename, sep='\t', index=False)
    sources += [Path(__file__)] + [ROOT/'code'/f for f in ['analyze_raw_ratings.py', 'audit_ratings_qc.py',
                'plot_normalized_loss_ratings.py', 'plot_normalized_rating_gaps.py', 'plot_rating_gaps.py']]
    meta = dict(n=len(data), sample_by_dataset=data.groupby('dataset').size().to_dict(), ratings_policy=RATINGS_POLICY,
        exclusions='Applied to raw ratings before normalization; within-partner loss > win excludes, equality allowed.',
        normalization='Within-person six-cell z-score using sample SD (ddof=1), then form contrasts. No second normalization.',
        model='Intercept + centered age/10 + dataset + recorded sex (F reference, M/O offsets). Paired contrast, HC3 t inference.',
        bars='Pooled descriptive means and between-person SEM; not model-adjusted.',
        scatter='Dots and fitted line adjusted to empirical dataset/sex mix; pointwise HC3 95% CI; all observations shown.',
        p_values='Two-sided uncorrected p displayed. age-tests.tsv also retains Holm correction over three paired comparisons per scale.',
        interpretation='User states a directional substantive prediction. These plots do not establish a preregistered normalization choice. Neither pipeline nor primary raw-rating policy changed.',
        sources=[dict(path=str(f.resolve()), sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sources])
    (args.output_dir/'provenance.json').write_text(json.dumps(meta, indent=2)+'\n')
    print(json.dumps(meta, indent=2))
    for _, tests, _ in results:
        print(tests[tests.comparison.eq('Friend minus Stranger')].to_string(index=False))
    print('CHECK PASSED: matched raw and normalized rating figures generated on the same sample.')


if __name__ == '__main__':
    main()
