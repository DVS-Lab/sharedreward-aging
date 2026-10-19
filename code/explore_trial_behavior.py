#!/usr/bin/env python3
"""Exploratory RT/guess-sequence analysis; never edits source data or eligibility.

Primary sample: existing ratings-eligible participants, task-ready runs only.
Current RT: run fixed effects. Lagged RT/choice: run fixed effects for RF1,
block fixed effects and within-block transitions for ds003745. Cluster inference
by participant. Form lagged variables BEFORE filtering responses or RTs.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from analyze_raw_ratings import ROOT, KEYS, load_ratings, demographics, holm
from audit_ratings_qc import RATINGS_POLICY

PARTNERS = {1: 'computer', 2: 'stranger', 3: 'friend'}
OUTCOMES = {1: 'punish', 2: 'neutral', 3: 'reward'}


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(obj)
    finally:
        sys.path.pop(0)
    return obj


def read(path):
    return pd.read_csv(path, sep='\t', dtype=str, keep_default_na=False)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def event_rows_match(generated, published):
    if len(generated) != len(published): return False
    for expected, observed in zip(generated, published):
        if expected[2] != observed[2] or not np.allclose([float(expected[0]), float(expected[1])], [float(observed[0]), float(observed[1])], atol=2e-6, rtol=0):
            return False
        if expected[3] == 'n/a':
            if observed[3] != 'n/a': return False
        elif not np.isclose(float(expected[3]), float(observed[3]), atol=2e-6, rtol=0):
            return False
    return True


def check_counts(trials, audit):
    checks = {'n_trials': len(trials), 'n_missed_trials': sum(t['missed'] for t in trials)}
    for partner in PARTNERS.values():
        for outcome in OUTCOMES.values():
            checks[f'n_event_{partner}_{outcome}'] = sum(not t['missed'] and t['partner'] == partner and t['outcome'] == outcome for t in trials)
    for key, value in checks.items():
        if value != int(audit[key]):
            raise ValueError(f'Canonical event QC mismatch {key}: raw {value}, audited {audit[key]}')


def collect(args, people):
    rf = module(args.rf1_upstream/'code/convert_behavior.py', 'rt_upstream_converter')
    old = module(args.srndna_root/'code/recover_sub144_sharedreward_events.py', 'rt_sub144_recovery')
    runs = read(ROOT/'logs/records/analysis-run-dispositions.tsv')
    runs = runs[runs.disposition.eq('task_ready')].merge(people[KEYS], on=KEYS, validate='many_to_one')
    audit = read(ROOT/'logs/records/fulltrial-event-qc-run-level.tsv')
    audit['run'] = audit.run.astype(int)
    if audit.duplicated(KEYS+['session', 'run']).any():
        raise ValueError('Duplicate event QC key')
    audits = audit.set_index(KEYS+['session', 'run'])
    rows, sources = [], []
    for unit in runs.itertuples():
        key = (unit.dataset, unit.subject, unit.session, int(unit.run))
        selected_session = ''
        if unit.dataset == 'rf1':
            res = rf.resolve_sources(args.rf1_behavior, unit.subject, unit.session, 'sharedreward', [1, 2])[int(unit.run)]
            if res.status != 'available':
                raise ValueError(f'{key}: unresolved raw source {res}')
            path = res.path
            converted = rf.convert_source('sharedreward', path)
            raw, _, _ = rf._trial_rows(rf._read_delimited(path, ','), 'decision_onset', 'Shared Reward')
            # Match by onset, not a guessed source row index after interrupted trials.
            lookup = {float(r['decision_onset']): r for r in raw}
            if len(lookup) != len(raw):
                raise ValueError(f'{key}: duplicate decision onsets')
            decisions = [r for r in converted.rows if r['trial_type'] in ('friend_face', 'stranger_face', 'computer_non-face', 'missed_decision')]
            selected = [lookup[float(r['onset'])] for r in decisions]
            fingerprint = converted.trial_fingerprint
            event_path = None
        else:
            path = args.srndna_root/'stimuli/psychopy/logs'/unit.subject/f'sub-{unit.subject}_task-sharedreward_run-{int(unit.run)-1}_raw.csv'
            if unit.subject == '144':
                selected = old.read_logged_sessions(path)[1]
                selected_session = 2
                event_path = args.srndna_root/'bids/sub-144/func'/f'sub-144_task-sharedreward_run-{int(unit.run):02d}_events.tsv'
            else:
                event_path = args.ds_bids/f'sub-{unit.subject}/func/sub-{unit.subject}_task-sharedreward_run-{int(unit.run):02d}_events.tsv'
            # Verify every trial's timing, RT, condition and block against BIDS.
            with event_path.open(newline='') as f:
                reader = csv.reader(f, delimiter='\t'); next(reader); published = list(reader)
            if unit.subject != '144':
                # Some older logs contain a repeated session header. Select only
                # the unique complete session matching every published BIDS row.
                with path.open(encoding='utf-8-sig', newline='') as f: raw_rows = list(csv.reader(f))
                header = raw_rows[0]; starts = [i for i,r in enumerate(raw_rows) if r == header]
                matches = []
                for number, start in enumerate(starts, 1):
                    stop = starts[number] if number < len(starts) else len(raw_rows)
                    segment = raw_rows[start+1:stop]
                    if len(segment) != 72 or any(len(r)!=len(header) for r in segment): continue
                    candidate = [dict(zip(header,r)) for r in segment]
                    if event_rows_match(old.make_event_rows(candidate), published): matches.append((number,candidate))
                if len(matches) != 1: raise ValueError(f'{key}: need unique BIDS-matched session; found {len(matches)}')
                selected_session, selected = matches[0]
            if not event_rows_match(old.make_event_rows(selected), published):
                raise ValueError(f'{key}: canonical BIDS mismatch')
            fingerprint = digest(event_path)
        trial_rows = []
        for index, r in enumerate(selected):
            if int(float(r['TrialNumber'])) != index+1:
                raise ValueError(f'{key}: trial numbering gap/reset; do not bridge a possible missing trial or run')
            response = int(float(r['resp'])); missed = response == 0
            allowed = (0, 1, 2) if unit.dataset == 'rf1' else (0, 2, 3)
            if response not in allowed:
                raise ValueError(f'{key}: unexpected response button {response}')
            rt = np.nan if missed else float(r['rt'])
            if not missed and (not np.isfinite(rt) or rt <= 0 or rt > 3):
                raise ValueError(f'{key}: invalid RT {rt}')
            onset = float(r['decision_onset']); end = float(r['outcome_offset'])
            if not np.isfinite([onset, end]).all() or end <= onset:
                raise ValueError(f'{key}: invalid timing')
            trial_rows.append(dict(dataset=unit.dataset, subject=unit.subject, session=unit.session, run=int(unit.run),
                trial=index+1, onset=onset, outcome_end=end, rt_s=rt, missed=int(missed),
                partner=PARTNERS[int(float(r['Partner']))], outcome='miss' if missed else OUTCOMES[int(float(r['Feedback']))],
                response=np.nan if missed else response, block=int(float(r['Blockn'])) if unit.dataset == 'ds003745' else 0,
                block_reward=int(float(r['BlockType'])) % 2 == 0 if unit.dataset == 'ds003745' else False))
        if not np.all(np.diff([t['onset'] for t in trial_rows]) > 0):
            raise ValueError(f'{key}: nonmonotonic trial order')
        check_counts(trial_rows, audits.loc[key])
        rows.extend(trial_rows)
        sources.append(dict(dataset=unit.dataset, subject=unit.subject, session=unit.session, run=int(unit.run),
            n_trials=len(trial_rows), path=str(path), sha256=digest(path), canonical_trial_fingerprint=fingerprint,
            selected_logged_session=selected_session,
            bids_path=str(event_path) if event_path else '', bids_sha256=digest(event_path) if event_path else '',
            verification='per-trial BIDS match' if event_path else 'upstream canonical conversion + all condition/miss counts match current QC'))
    d = pd.DataFrame(rows).merge(people[KEYS+['age', 'sex']], on=KEYS, validate='many_to_one')
    return add_lags(d), pd.DataFrame(sources)


def add_lags(data):
    d = data.sort_values(KEYS+['session', 'run', 'trial']).copy()
    d['person'] = d.dataset+':'+d.subject
    d['run_id'] = d.person+':'+d.session+':'+d.run.astype(str)
    g = d.groupby('run_id', sort=False)
    for col in ('rt_s', 'response', 'missed', 'partner', 'outcome', 'block', 'outcome_end', 'trial'):
        d['prev_'+col] = g[col].shift(1)
    d['consecutive'] = d.trial.sub(d.prev_trial).eq(1)
    d['same_block'] = d.block.eq(d.prev_block)
    d['partner_switch'] = d.partner.ne(d.prev_partner).astype(float)
    d['choice_switch'] = np.where(d.response.notna() & d.prev_response.notna(), d.response.ne(d.prev_response).astype(float), np.nan)
    d['feedback_gap_s'] = d.onset-d.prev_outcome_end
    d['progress'] = (d.trial-1)/(g.trial.transform('max')-1)
    d['lag_group'] = np.where(d.dataset.eq('ds003745'), d.run_id+':block'+d.block.astype(str), d.run_id)
    return d


def absorbed_fit(y, x, groups, clusters):
    """OLS with absorbed intercepts and participant-cluster CR1 covariance."""
    frame = x.copy(); frame['_y'] = np.asarray(y, float)
    centered = frame-frame.groupby(np.asarray(groups)).transform('mean')
    a = centered[x.columns].to_numpy(float); b = centered['_y'].to_numpy(float)
    # A regressor constant within all fixed-effect groups contributes no information.
    keep = np.max(np.abs(a), axis=0) > 1e-10
    a = a[:, keep]; names = list(x.columns[keep])
    if not np.isfinite(a).all() or not np.isfinite(b).all() or np.linalg.matrix_rank(a) != a.shape[1]:
        raise ValueError('Nonfinite or rank-deficient design')
    bread = np.linalg.inv(a.T@a); beta = bread@a.T@b; resid = b-a@beta
    scores = pd.DataFrame(a*resid[:, None]).groupby(np.asarray(clusters)).sum().to_numpy()
    n = len(b); ng = len(scores); k = a.shape[1]+pd.Series(groups).nunique()
    if ng < 20 or n <= k: raise ValueError('Insufficient clusters or residual degrees of freedom')
    cov = bread@scores.T@scores@bread * ng/(ng-1) * (n-1)/(n-k)
    return dict(beta=beta, cov=cov, names=names, n=n, clusters=ng, df=ng-1,
                fixed_effect_groups=pd.Series(groups).nunique(), parameters=k)


def test_contrast(fit, weights, family, label, scale):
    v = np.zeros(len(fit['names']))
    for name, weight in weights.items():
        if name not in fit['names']: raise ValueError(f'Unestimable contrast term {name}')
        v[fit['names'].index(name)] = weight
    effect = v@fit['beta']; se = np.sqrt(v@fit['cov']@v); crit = stats.t.ppf(.975, fit['df'])
    low, high = effect-crit*se, effect+crit*se
    return dict(family=family, comparison=label, n_trials=fit['n'], n_people=fit['clusters'],
                estimate=effect, se_cluster=se, ci95_low=low, ci95_high=high,
                p=2*stats.t.sf(abs(effect/se), fit['df']), df=fit['df'], scale=scale,
                percent_change=100*np.expm1(effect) if scale == 'logRT' else 100*effect,
                percent_low=100*np.expm1(low) if scale == 'logRT' else 100*low,
                percent_high=100*np.expm1(high) if scale == 'logRT' else 100*high)


def fit_models(d, people, minimum_rt):
    rows = []; inventories = []
    demo = people.drop_duplicates(KEYS)
    rf_mix = demo.dataset.eq('rf1').mean()
    sex_mix = {s: demo.sex.eq(s).mean() for s in ('M', 'O')}
    response = d[d.rt_s.ge(minimum_rt) & d.rt_s.gt(0)].copy()
    age = (response.age-50)/10
    x = pd.DataFrame(index=response.index)
    for p in ('friend', 'stranger'):
        x[p] = response.partner.eq(p).astype(float)
        x['age_'+p] = age*x[p]
        x['dataset_'+p] = (response.dataset.eq('rf1').astype(float)-rf_mix)*x[p]
        for s in ('M', 'O'):
            x['sex'+s+'_'+p] = (response.sex.eq(s).astype(float)-sex_mix[s])*x[p]
    x['progress'] = response.progress; x['progress2'] = response.progress**2
    x['older_block_reward'] = response.block_reward.astype(float)
    fit = absorbed_fit(np.log(response.rt_s), x, response.run_id, response.person)
    inventories.append(dict(model='current_partner_RT', **{k:v for k,v in fit.items() if k not in ('beta','cov')}))
    for p, q in (('friend','stranger'), ('friend','computer'), ('stranger','computer')):
        for prefix, suffix in (('', ' at age 50'), ('age_', ' age slope per decade')):
            weights = {prefix+p:1}
            if q != 'computer': weights[prefix+q] = -1
            rows.append(test_contrast(fit, weights, 'current_partner_RT', p+' minus '+q+suffix, 'logRT'))
    age_rows = []
    for p, q in (('friend','stranger'), ('friend','computer'), ('stranger','computer')):
        for a in np.linspace(d.age.min(), d.age.max(), 100):
            weights = {p:1, 'age_'+p:(a-50)/10}
            if q != 'computer': weights.update({q:-1,'age_'+q:-(a-50)/10})
            prediction = test_contrast(fit, weights, 'current_partner_age_plot', p+' minus '+q, 'logRT')
            prediction['age'] = a; age_rows.append(prediction)
    # Select genuine adjacent responses only; never bridge a miss or an RT rejection.
    lag = d[d.consecutive & d.rt_s.ge(minimum_rt) & d.rt_s.gt(0) & d.prev_rt_s.ge(minimum_rt) & d.prev_rt_s.gt(0)
            & (d.dataset.eq('rf1') | d.same_block) & d.prev_outcome.isin(['reward','punish','neutral'])].copy()
    if (lag.feedback_gap_s < 0).any(): raise ValueError('Next decision precedes previous outcome offset')
    x = pd.DataFrame(index=lag.index)
    x['previous_loss'] = lag.prev_outcome.eq('punish').astype(float)
    x['previous_neutral'] = lag.prev_outcome.eq('neutral').astype(float)
    x['loss_age'] = x.previous_loss*(lag.age-50)/10
    x['loss_dataset'] = x.previous_loss*(lag.dataset.eq('rf1').astype(float)-rf_mix)
    for p in ('friend', 'stranger'):
        x['previous_'+p] = lag.prev_partner.eq(p).astype(float)
        x['current_'+p] = lag.partner.eq(p).astype(float)
        x['loss_'+p] = x.previous_loss*(x['previous_'+p]-1/3)
    x['partner_switch'] = lag.partner_switch
    x['previous_logRT'] = np.log(lag.prev_rt_s)
    x['feedback_gap_s'] = lag.feedback_gap_s
    x['progress'] = lag.progress; x['progress2'] = lag.progress**2
    for name, y, scale in (('post_outcome_RT', np.log(lag.rt_s), 'logRT'),
                            ('post_outcome_guess_switch', lag.choice_switch, 'probability')):
        fit = absorbed_fit(y, x, lag.lag_group, lag.person)
        inventories.append(dict(model=name, **{k:v for k,v in fit.items() if k not in ('beta','cov')}))
        contrasts = [('loss minus win (equal partner weights, age 50)', {'previous_loss':1}),
                     ('loss minus win age slope per decade', {'loss_age':1}),
                     ('loss effect: friend minus stranger', {'loss_friend':1,'loss_stranger':-1}),
                     ('loss effect: friend minus computer', {'loss_friend':1}),
                     ('loss effect: stranger minus computer', {'loss_stranger':1}),
                     ('loss effect: RF1 minus ds003745', {'loss_dataset':1})]
        for label, weights in contrasts:
            rows.append(test_contrast(fit, weights, name, label, scale))
        # Derived partner-specific loss effects for figures, not additional testing claims.
        for p in ('friend', 'stranger', 'computer'):
            weights = {'previous_loss':1, 'loss_friend':(p=='friend')-1/3, 'loss_stranger':(p=='stranger')-1/3}
            rows.append(test_contrast(fit, weights, name+'_plot', 'previous partner '+p, scale))
    table = pd.DataFrame(rows)
    table['p_holm_family'] = np.nan
    for family in table.family.unique():
        if family.endswith('_plot'): continue
        ix = table.family.eq(family); table.loc[ix, 'p_holm_family'] = holm(table.loc[ix, 'p'])
    table['p_holm_all18'] = np.nan
    primary = ~table.family.str.endswith('_plot')
    table.loc[primary, 'p_holm_all18'] = holm(table.loc[primary, 'p'])
    table['minimum_rt_s'] = minimum_rt
    return table, inventories, pd.DataFrame(age_rows)


def summaries(d, output):
    d.groupby('dataset').agg(n_trials=('trial','size'), n_people=('person','nunique'), n_runs=('run_id','nunique'),
        misses=('missed','sum'), miss_fraction=('missed','mean'), median_rt_s=('rt_s','median'), mean_rt_s=('rt_s','mean')).to_csv(output/'inventory.tsv',sep='\t')
    counts = d.groupby(['dataset','partner']).agg(n_trials=('trial','size'), misses=('missed','sum'), miss_fraction=('missed','mean'), median_rt_s=('rt_s','median'))
    counts.to_csv(output/'partner-descriptives.tsv',sep='\t')
    # Descriptive next-trial omission rates retain current misses, unlike RT models.
    eligible = d[d.consecutive & (d.dataset.eq('rf1') | d.same_block) & d.prev_outcome.isin(['reward','punish','neutral'])]
    eligible.groupby(['dataset','prev_outcome']).agg(n_trials=('trial','size'), misses=('missed','sum'),
        miss_fraction=('missed','mean'), switch_fraction=('choice_switch','mean')).to_csv(output/'post-outcome-descriptives.tsv',sep='\t')
    d.groupby('dataset').rt_s.quantile([0,.001,.01,.5,.99,.999,1]).to_csv(output/'rt-quantiles.tsv',sep='\t')


def plot(d, tests, output):
    fig, axes = plt.subplots(1,3,figsize=(15,5.8))
    fig.subplots_adjust(left=.06,right=.98,bottom=.29,top=.76,wspace=.42)
    names = ['friend','stranger','computer']; colors = ['#326B9F','#C07A32','#338574']
    person = d[d.rt_s.ge(.15)].groupby(['person','partner']).rt_s.median().unstack().dropna()
    for j,(p,c) in enumerate(zip(names,colors)):
        axes[0].bar(j,person[p].mean(),yerr=person[p].std(ddof=1)/np.sqrt(len(person)),color=c,capsize=4)
    axes[0].set(xticks=range(3),xticklabels=[p.title() for p in names],ylabel='Median RT per person (seconds)',ylim=(0,None))
    axes[0].set_title('Current partner\nDescriptive mean ± SEM',fontsize=13)
    for ax, family, title, unit in zip(axes[1:], ['post_outcome_RT_plot','post_outcome_guess_switch_plot'],
                                      ['Next-trial RT after loss vs win','Next-guess switching after loss vs win'],
                                      ['RT change (%)','Switch probability change (percentage points)']):
        for j,(p,c) in enumerate(zip(names,colors)):
            row=tests[(tests.family==family)&(tests.comparison=='previous partner '+p)].iloc[0]
            ax.errorbar(j,row.percent_change,yerr=[[row.percent_change-row.percent_low],[row.percent_high-row.percent_change]],
                        fmt='o',color=c,markersize=8,capsize=5,lw=2)
        ax.axhline(0,color='#8D969D',lw=1,ls=':')
        ax.set(xticks=range(3),xticklabels=[p.title() for p in names],xlabel='Previous partner',ylabel=unit)
        ax.set_title(title+'\nAdjusted estimate and 95% CI',fontsize=12)
    for ax in axes:
        ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',color='#E7EBEE');ax.set_axisbelow(True)
    fig.suptitle('Exploratory trial behavior: response speed and next guesses',fontsize=20,y=.95)
    fig.text(.06,.16,'Existing behavioral eligibility; RT ≥150 ms. Lag models use adjacent responses, with no crossing of runs or older-dataset blocks.',fontsize=10)
    fig.text(.06,.105,'Lag estimates at age 50, pooled dataset mix; control previous RT, current/previous partner, partner switching, trial position and feedback-to-decision interval.',fontsize=9.5)
    fig.text(.06,.05,'Participant-clustered uncertainty; older-dataset block fixed effects. Outcomes were predetermined: switching is not evidence of adaptive learning.',fontsize=10)
    for ext in ('png','svg'): fig.savefig(output/f'exploratory-trial-behavior.{ext}',dpi=200)
    plt.close(fig)
    person.to_csv(output/'participant-partner-median-rt.tsv',sep='\t')


def plot_age(predictions, output):
    fig, ax = plt.subplots(figsize=(9,6))
    fig.subplots_adjust(left=.12,right=.97,top=.82,bottom=.24)
    for label,color,style in zip(['friend minus stranger','friend minus computer','stranger minus computer'],
                                  ['#326B9F','#338574','#C07A32'],['-','--','-.']):
        d = predictions[predictions.comparison.eq(label)]
        ax.plot(d.age,d.percent_change,color=color,linestyle=style,lw=2.5,label=label.title())
        ax.fill_between(d.age,d.percent_low,d.percent_high,color=color,alpha=.13,linewidth=0)
    ax.axhline(0,color='#8D969D',ls=':',lw=1)
    ax.set(xlabel='Age (years)',ylabel='Relative RT difference (%)',xticks=[20,40,60,80])
    ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',color='#E7EBEE');ax.set_axisbelow(True)
    ax.legend(frameon=False,fontsize=11)
    fig.suptitle('Exploratory age differences in partner-related RT',fontsize=18,y=.95)
    fig.text(.12,.13,'Negative values: faster responses to the first-named partner.',fontsize=11)
    fig.text(.12,.08,'Run fixed effects; dataset/sex-adjusted partner contrasts; participant-clustered 95% CIs.',fontsize=10)
    fig.text(.12,.035,'RT ≥150 ms. Age slopes are exploratory; confidence bands are pointwise, not simultaneous.',fontsize=10)
    for ext in ('png','svg'): fig.savefig(output/f'partner-RT-age.{ext}',dpi=200)
    plt.close(fig)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rf1-upstream',type=Path,default=ROOT.parent/'rf1-sra-linux2')
    p.add_argument('--rf1-behavior',type=Path,default=ROOT.parent/'rf1-sra/stimuli')
    p.add_argument('--srndna-root',type=Path,default=ROOT.parent/'srndna-datapaper')
    p.add_argument('--ds-bids',type=Path,default=ROOT/'bids')
    p.add_argument('--output-dir',type=Path,default=ROOT/'qc/trial-behavior-exploratory')
    args = p.parse_args(); args.output_dir.mkdir(parents=True,exist_ok=True)
    people = load_ratings(ROOT/'logs/records/ratings-qc-subject-level.tsv',ROOT/'logs/records/analysis-subject-dispositions.tsv')
    people = people.merge(pd.concat([demographics(args.rf1_upstream/'bids/participants.tsv','rf1'), demographics(ROOT/'participants-srndna.tsv','ds003745')]),on=KEYS,validate='one_to_one')
    if not (people.age.between(18,110)&people.sex.isin(['F','M','O'])).all(): raise ValueError('Incomplete demographics')
    d, sources = collect(args, people)
    sources.to_csv(args.output_dir/'source-audit.tsv',sep='\t',index=False)
    print('Source-verified runs:',len(sources),'Trials:',len(d),'People:',d.person.nunique(),flush=True)
    summaries(d,args.output_dir)
    results=[]; specifications={}
    for threshold in (.15,0.0):
        result, inventory, age_predictions = fit_models(d,people,threshold);results.append(result);specifications[str(threshold)]=inventory
        if threshold == .15:
            age_predictions.to_csv(args.output_dir/'partner-RT-age-predictions.tsv',sep='\t',index=False)
            plot_age(age_predictions,args.output_dir)
        print(result[~result.family.str.endswith('_plot')].to_string(index=False),flush=True)
    pd.concat(results,ignore_index=True).to_csv(args.output_dir/'model-tests.tsv',sep='\t',index=False)
    plot(d,results[0],args.output_dir)
    # Keep the large trial derivative local/ignored; commit only audit and summaries.
    trial_path = ROOT/'derivatives/behavioral-exploratory/trials.tsv'
    trial_path.parent.mkdir(parents=True,exist_ok=True);d.to_csv(trial_path,sep='\t',index=False)
    inputs = [Path(__file__),ROOT/'logs/records/analysis-run-dispositions.tsv',ROOT/'logs/records/fulltrial-event-qc-run-level.tsv',
        ROOT/'logs/records/ratings-qc-subject-level.tsv',ROOT/'logs/records/analysis-subject-dispositions.tsv',
        args.rf1_upstream/'code/convert_behavior.py',args.rf1_upstream/'bids/participants.tsv',ROOT/'participants-srndna.tsv',
        args.srndna_root/'code/recover_sub144_sharedreward_events.py',ROOT/'code/analyze_raw_ratings.py',ROOT/'code/audit_ratings_qc.py']
    meta=dict(exploratory=True, ratings_policy=RATINGS_POLICY, n_ratings_eligible=len(people),n_people_with_task_ready_runs=d.person.nunique(),
        rt_filter='Primary >=150 ms, sensitivity all positive responded RTs; misses never assigned sentinel RT. Neither filter bridges trials.',
        model='Log RT with run intercepts; lag RT and binary guess-switch linear probability model with RF1 run / ds003745 block intercepts; participant-cluster CR1 SE, t df=clusters-1.',
        age='Age centered at 50, per decade. Main age/sex/dataset offsets absorbed by run or block. Current-partner effects include age/dataset/sex interactions. Lag effects include age and dataset interactions; no sex interaction.',
        sequence='Lagged variables formed before filtering. No crossing run boundaries; ds003745 lag tests additionally exclude block boundaries. Neutral feedback is retained as a nuisance category.',
        multiplicity='Both Holm within each six-test model family and Holm across all 18 exploratory tests; separately for primary and explicitly labeled all-positive-RT sensitivity. Plot-derived estimates are descriptive contrasts, not additional significance claims.',
        limitations=['Exploration following ratings analyses, not confirmatory.',
            'Eligibility deliberately matches ratings analysis; not all task performers. MRI QC exclusions not added.',
            'RF1 raw source uses current upstream conversion and count checks; canonical BIDS files are not local, so RF1 per-trial BIDS hash equivalence is not independently established.',
            'Task code differs: older RT timestamps before response display flip, RF1 after display flip; decision windows 2.5 vs 2.8 seconds.',
            'Predetermined outcomes and different block/event designs preclude interpreting switching as task accuracy or optimal learning.',
            'Lag age moderation assumes common age modulation across partners; no higher-order interaction search.'],
        specifications=specifications, local_trial_derivative=str(trial_path),trial_sha256=digest(trial_path),
        rt_below_150ms=int((d.rt_s<.15).sum()),sources=[dict(path=str(f),sha256=digest(f)) for f in inputs])
    (args.output_dir/'provenance.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('CHECK PASSED: source counts verified; exploratory analyses and primary/sensitivity outputs complete.')


if __name__ == '__main__': main()
