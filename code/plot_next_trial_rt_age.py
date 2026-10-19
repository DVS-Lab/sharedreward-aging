#!/usr/bin/env python3
"""Exploratory age-by-previous-feedback-by-previous-partner RT analysis."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from analyze_raw_ratings import ROOT, KEYS, age_design, holm
from explore_trial_behavior import absorbed_fit, test_contrast

PARTNERS = ['friend', 'stranger', 'computer']
CELLS = [p+'_'+o for p in PARTNERS for o in ('reward', 'punish')]


def select_pairs(d, threshold):
    """Use existing lag columns: filtering never creates a new adjacency."""
    lag = d[d.consecutive & d.rt_s.ge(threshold) & d.rt_s.gt(0)
            & d.prev_rt_s.ge(threshold) & d.prev_rt_s.gt(0)
            & (d.dataset.eq('rf1') | d.same_block)
            & d.prev_outcome.isin(['reward', 'punish'])].copy()
    if (lag.feedback_gap_s < 0).any():
        raise ValueError('Next decision precedes previous outcome offset')
    return lag


def summarize(lag, demo):
    lag = lag.assign(cell=lag.prev_partner+'_'+lag.prev_outcome, log_rt=np.log(lag.rt_s))
    counts = lag.groupby(KEYS+['cell']).size().unstack().reindex(columns=CELLS)
    means = lag.groupby(KEYS+['cell']).log_rt.mean().unstack().reindex(columns=CELLS)
    data = demo.merge(means, on=KEYS, how='left', validate='one_to_one').sort_values(KEYS)
    if not np.isfinite(data[CELLS].to_numpy()).all():
        raise ValueError('Missing participant feedback/partner cells; no silent dropping')
    return data, counts


def absolute_curves(data, ages):
    """Shared X and paired six-cell outcomes; equal weight per participant."""
    x = age_design(data); y = data[CELLS].to_numpy(float)
    bread = np.linalg.inv(x.T@x); beta = bread@x.T@y
    residual = (y-x@beta)/(1-np.sum((x@bread)*x, axis=1))[:, None]
    g = np.tile(x.mean(axis=0), (len(ages), 1))
    g[:, 1] = (np.asarray(ages)-data.age.mean())/10
    predicted = g@beta; se = np.sqrt((g@bread@x.T)**2@residual**2)
    df = len(data)-x.shape[1]; critical = stats.t.ppf(.975, df)
    rows = []
    for j, cell in enumerate(CELLS):
        partner, outcome = cell.split('_')
        for i, age in enumerate(ages):
            rows.append(dict(previous_partner=partner, previous_outcome=outcome, age=age,
                geometric_rt_s=np.exp(predicted[i, j]),
                ci95_low_s=np.exp(predicted[i, j]-critical*se[i, j]),
                ci95_high_s=np.exp(predicted[i, j]+critical*se[i, j])))
    return pd.DataFrame(rows)


def lag_design(lag, demo):
    age = (lag.age-50)/10
    x = pd.DataFrame(index=lag.index)
    x['previous_loss'] = lag.prev_outcome.eq('punish').astype(float)
    x['loss_age'] = x.previous_loss*age
    x['loss_dataset'] = x.previous_loss*(lag.dataset.eq('rf1').astype(float)-demo.dataset.eq('rf1').mean())
    for sex in ('M', 'O'):
        x['loss_sex_'+sex] = x.previous_loss*(lag.sex.eq(sex).astype(float)-demo.sex.eq(sex).mean())
    for partner in ('friend', 'stranger'):
        # Centering makes the main loss effect an equal-partner average.
        previous = lag.prev_partner.eq(partner).astype(float)-1/3
        x['previous_'+partner] = previous
        x['previous_age_'+partner] = previous*age
        x['loss_'+partner] = x.previous_loss*previous
        x['loss_age_'+partner] = x.previous_loss*previous*age
        x['current_'+partner] = lag.partner.eq(partner).astype(float)
        x['current_age_'+partner] = x['current_'+partner]*age
    x['partner_switch'] = lag.partner_switch
    x['previous_logRT'] = np.log(lag.prev_rt_s)
    x['feedback_gap_s'] = lag.feedback_gap_s
    x['progress'] = lag.progress; x['progress2'] = lag.progress**2
    return x


def loss_weights(partner=None, age=50, slope=False):
    prefix = 'loss_age_' if slope else 'loss_'
    weights = {'loss_age' if slope else 'previous_loss': 1}
    if partner is not None:
        for p in ('friend', 'stranger'):
            weights[prefix+p] = float(partner == p)-1/3
    if not slope:
        weights['loss_age'] = (age-50)/10
        if partner is not None:
            for p in ('friend', 'stranger'):
                weights['loss_age_'+p] = (float(partner == p)-1/3)*(age-50)/10
    return weights


def joint_test(fit, names, label):
    c = np.eye(len(fit['names']))[[fit['names'].index(n) for n in names]]
    b = c@fit['beta']; covariance = c@fit['cov']@c.T
    f = float(b@np.linalg.solve(covariance, b)/len(names))
    return dict(family='global', comparison=label, n_trials=fit['n'], n_people=fit['clusters'],
                f_statistic=f, df_num=len(names), df=fit['df'], p=stats.f.sf(f, len(names), fit['df']))


def lag_tests(fit, ages):
    rows = [test_contrast(fit, loss_weights(), 'global', 'Loss minus win at age 50', 'logRT'),
            test_contrast(fit, loss_weights(slope=True), 'global', 'Loss minus win age slope per decade', 'logRT'),
            joint_test(fit, ['loss_friend', 'loss_stranger'], 'Previous outcome by previous partner at age 50'),
            joint_test(fit, ['loss_age_friend', 'loss_age_stranger'], 'Age by previous outcome by previous partner')]
    for p in PARTNERS:
        rows.append(test_contrast(fit, loss_weights(p), 'partner_loss', p+' loss minus win at age 50', 'logRT'))
        rows.append(test_contrast(fit, loss_weights(p, slope=True), 'partner_loss_age', p+' loss minus win age slope per decade', 'logRT'))
    for p, q in (('friend', 'stranger'), ('friend', 'computer'), ('stranger', 'computer')):
        weights = {k:loss_weights(p, slope=True)[k]-loss_weights(q, slope=True)[k]
                   for k in loss_weights(p, slope=True)}
        rows.append(test_contrast(fit, weights, 'paired_loss_age', p+' minus '+q+' loss-age slope', 'logRT'))
    tests = pd.DataFrame(rows)
    tests['p_holm_all13'] = holm(tests.p)
    for family in tests.family.unique():
        ix = tests.family.eq(family); tests.loc[ix, 'p_holm_family'] = holm(tests.loc[ix, 'p'])
    predictions = []
    for p in PARTNERS:
        for age in ages:
            row = test_contrast(fit, loss_weights(p, age), 'plot', p, 'logRT')
            row.update(age=age, previous_partner=p); predictions.append(row)
    return tests, pd.DataFrame(predictions)


def plot(absolute, relative, n, output):
    fig, axes = plt.subplots(1, 3, figsize=(13, 5.7), sharex=True, sharey=True)
    fig.subplots_adjust(left=.08, right=.98, top=.76, bottom=.26, wspace=.12)
    for ax, partner in zip(axes, PARTNERS):
        for outcome, color, label, style in [('reward', '#326B9F', 'After win', '-'),
                                             ('punish', '#C46935', 'After loss', '--')]:
            d = absolute[absolute.previous_partner.eq(partner) & absolute.previous_outcome.eq(outcome)]
            ax.plot(d.age, d.geometric_rt_s, color=color, label=label, lw=2.8, ls=style)
            ax.fill_between(d.age, d.ci95_low_s, d.ci95_high_s, color=color, alpha=.16, linewidth=0)
        ax.set(title='Previous partner: '+partner.title(), xlabel='Age (years)', xticks=[20,40,60,80])
        ax.spines[['top','right']].set_visible(False); ax.grid(axis='y', color='#E7EBEE'); ax.set_axisbelow(True)
    axes[0].set_ylabel('Next-trial RT (seconds; geometric mean)')
    axes[0].legend(frameon=False)
    fig.suptitle('Response time after wins and losses across age', fontsize=21, y=.96)
    fig.text(.5, .86, f'N = {n}  ·  Basic behavioral exclusions  ·  Dataset and recorded sex adjusted', ha='center', fontsize=12)
    fig.text(.08, .15, 'Outcome and partner refer to trial t; response time is measured on trial t+1. Bands: pointwise 95% CIs.', fontsize=10)
    fig.text(.08, .095, 'Equal-participant mean-log-RT models. Valid adjacent responses only; no crossing runs or older-dataset blocks.', fontsize=10)
    fig.text(.08, .04, 'These absolute curves do not condition on previous RT; the separate trial-level model tests post-loss speeding.', fontsize=10)
    for ext in ('png','svg'): fig.savefig(output/f'next-trial-RT-age.{ext}', dpi=220)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 6))
    fig.subplots_adjust(left=.13, right=.97, top=.80, bottom=.25)
    for p, color, style in zip(PARTNERS, ['#326B9F','#C07A32','#338574'], ['-','--','-.']):
        d = relative[relative.previous_partner.eq(p)]
        ax.plot(d.age, d.percent_change, color=color, ls=style, lw=2.6, label=p.title())
        ax.fill_between(d.age, d.percent_low, d.percent_high, color=color, alpha=.13, linewidth=0)
    ax.axhline(0, color='#707A83', ls=':', lw=1)
    ax.set(xlabel='Age (years)', ylabel='Next-trial RT: loss versus win (%)', xticks=[20,40,60,80])
    ax.spines[['top','right']].set_visible(False); ax.grid(axis='y', color='#E7EBEE'); ax.set_axisbelow(True)
    ax.legend(title='Previous partner', frameon=False)
    fig.suptitle('Does post-loss speeding change with age?', fontsize=20, y=.95)
    fig.text(.13, .87, 'Adjusted trial-level estimates · Participant-clustered 95% confidence bands', fontsize=11)
    fig.text(.13, .14, 'Negative values: faster responses after losses. Full age × outcome × previous-partner model.', fontsize=10)
    fig.text(.13, .085, 'Controls previous RT, current partner, timing and trial position; run/block fixed effects.', fontsize=10)
    fig.text(.13, .03, 'Exploratory cross-sectional associations; dataset/sex-standardized contrasts. RT ≥150 ms.', fontsize=10)
    for ext in ('png','svg'): fig.savefig(output/f'post-loss-speeding-age.{ext}', dpi=220)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trials', type=Path, default=ROOT/'derivatives/behavioral-exploratory/trials.tsv')
    parser.add_argument('--output-dir', type=Path, default=ROOT/'qc/trial-behavior-exploratory')
    args = parser.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    parent = ROOT/'qc/trial-behavior-exploratory/provenance.json'
    meta = json.loads(parent.read_text())
    if hashlib.sha256(args.trials.read_bytes()).hexdigest() != meta['trial_sha256']:
        raise ValueError('Trial derivative differs from source-verified provenance')
    d = pd.read_csv(args.trials, sep='\t', dtype={'dataset':str, 'subject':str, 'session':str})
    demo = d[KEYS+['age','sex']].drop_duplicates()
    if demo.duplicated(KEYS).any() or len(demo) != meta['n_ratings_eligible']:
        raise ValueError('Demographic/eligibility mismatch')
    ages = np.linspace(demo.age.min(), demo.age.max(), 160)
    all_tests = []; inventory = []
    for threshold in (.15, 0.0):
        lag = select_pairs(d, threshold); data, counts = summarize(lag, demo)
        absolute = absolute_curves(data, ages)
        x = lag_design(lag, demo)
        fit = absorbed_fit(np.log(lag.rt_s), x, lag.lag_group, lag.person)
        tests, relative = lag_tests(fit, ages)
        tests['minimum_rt_s'] = threshold; all_tests.append(tests)
        inventory.append(dict(minimum_rt_s=threshold, min_cell_count=int(counts.min().min()),
                              **{k:v for k,v in fit.items() if k not in ('beta','cov')}))
        print('Minimum RT:', threshold, 'Pairs:', len(lag), 'Participants:', len(data), flush=True)
        print(tests.to_string(index=False), flush=True)
        if threshold == .15:
            plot(absolute, relative, len(data), args.output_dir)
            for name, frame in [('predictions',absolute), ('adjusted-loss-predictions',relative),
                                ('participant-mean-logRT',data), ('cell-counts',counts.reset_index())]:
                frame.to_csv(args.output_dir/f'next-trial-RT-age-{name}.tsv', sep='\t', index=False)
            pd.DataFrame(fit['cov'], index=fit['names'], columns=fit['names']).to_csv(args.output_dir/'next-trial-RT-age-model-covariance.tsv', sep='\t')
            pd.DataFrame(dict(term=fit['names'], estimate=fit['beta'])).to_csv(args.output_dir/'next-trial-RT-age-model-coefficients.tsv', sep='\t', index=False)
    pd.concat(all_tests, ignore_index=True).to_csv(args.output_dir/'next-trial-RT-age-tests.tsv', sep='\t', index=False)
    report = dict(exploratory=True, ratings_policy=meta['ratings_policy'], trial_sha256=meta['trial_sha256'],
        absolute_plot='Six mean-log-RT outcomes per participant (previous partner by previous win/loss), age/10 + dataset + sex with intercept; equal participant weights; HC3 pointwise t confidence bands; exponentiated to geometric seconds. No previous-RT adjustment in this descriptive plot.',
        inferential_model='log(next RT) ~ previous loss * previous partner * age/10 (age centered 50), current partner * age/10, previous log RT, partner switch, feedback gap, progress + progress squared, loss * dataset, loss * sex; RF1 run / older dataset run-block fixed intercepts absorb age, sex and dataset main effects. Participant-cluster CR1 covariance; t(df=participants-1), omnibus Wald F(2,participants-1).',
        contrasts='Equal previous-partner weights for overall loss and loss-age effects; dataset and sex held at empirical participant mix. Partner effect tests at age 50. Three-way omnibus tests equality of partner-specific loss-age slopes.',
        selection='Existing basic behavioral eligibility; real adjacent positive responses at/above150ms primary; all-positive sensitivity. Previous neutral omitted, never bridged. No run crossing; older dataset restricted within blocks. Current misses and invalid current/previous RT excluded. No additional MRI QC selection.',
        differences_from_earlier='New explicitly requested three-way interaction with lower-order terms. Wins/losses only (earlier model retained neutral nuisance); added current-partner age and loss-sex adjustments. Earlier outputs are preserved, not overwritten.',
        multiplicity='13 exploratory tests; uncorrected p, Holm across all13 and within four global / three partner effects / three partner age effects / three paired age differences. Sensitivity corrected separately. No correction can make this follow-up confirmatory.',
        limitations=['Cross-sectional, not within-person aging.', 'Conditional on adjacent valid responses and ratings eligibility; not all task performers.',
                     'Some participant cells are sparse; report counts and retain equal-person descriptive weighting.',
                     'Different block/event tasks and RT implementations; outcomes predetermined, so RT is not uniquely learning or valuation.',
                     'RF1 raw-source count checks do not independently establish per-trial BIDS hash equivalence.'],
        inventory=inventory, sources=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
            for p in (parent,Path(__file__),ROOT/'code/analyze_raw_ratings.py',ROOT/'code/explore_trial_behavior.py')])
    (args.output_dir/'next-trial-RT-age-provenance.json').write_text(json.dumps(report, indent=2)+'\n')
    print('CHECK PASSED: all participants retained, adjacency preserved, full interaction tested.')


if __name__ == '__main__':
    main()
