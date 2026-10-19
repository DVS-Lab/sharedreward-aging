#!/usr/bin/env python3
"""Exploratory partner switching and fixed RT additions to ratings regressions.

No covariate selection by p-value. Raw rating targets primary; normalized
targets sensitivity. Source trial derivative and behavioral eligibility fixed.
"""
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

from analyze_raw_ratings import ROOT, KEYS, CELLS, age_design, holm, load_ratings
from explore_trial_behavior import absorbed_fit, test_contrast
from plot_next_trial_rt_age import PARTNERS, select_pairs, lag_design, loss_weights, joint_test
from plot_normalized_loss_ratings import transform
from plot_rating_gaps import GAPS

FEATURES = ['overall_logRT', 'friend_minus_stranger_logRT', 'loss_minus_win_logRT']
SWITCH_FEATURE = 'switch_minus_stay_loss_effect'


def switch_design(lag, demo):
    if not lag.dataset.eq('rf1').all():
        raise ValueError('Switch inference is RF1-only: older data have no within-block switches')
    x = lag_design(lag, demo).drop(columns='loss_dataset')
    switch = lag.partner_switch.astype(float); age = (lag.age-50)/10
    x['switch_age'] = switch*age
    x['loss_switch'] = x.previous_loss*switch
    x['loss_switch_age'] = x.previous_loss*switch*age
    for p in ('friend','stranger'):
        previous = lag.prev_partner.eq(p).astype(float)-1/3
        x['switch_'+p] = switch*previous
        x['loss_switch_'+p] = x.previous_loss*switch*previous
    return x


def switching_weights(partner=None, switched=0, difference=False):
    weights = {} if difference else loss_weights(partner)
    weights['loss_switch'] = 1 if difference else switched
    if partner is not None:
        for p in ('friend','stranger'):
            weights['loss_switch_'+p] = (float(partner == p)-1/3)*(1 if difference else switched)
    return weights


def analyze_switch(d, demo, threshold):
    lag = select_pairs(d, threshold)
    counts = lag.groupby(['dataset','partner_switch','prev_partner','prev_outcome']).agg(
        n_pairs=('person','size'), n_people=('person','nunique')).reset_index()
    lag = lag[lag.dataset.eq('rf1')].copy(); people = demo[demo.dataset.eq('rf1')]
    x = switch_design(lag, people)
    fit = absorbed_fit(np.log(lag.rt_s), x, lag.lag_group, lag.person)
    tests = [test_contrast(fit, switching_weights(difference=True), 'interaction',
                          'Loss effect: switch minus stay at age 50', 'logRT'),
             joint_test(fit, ['loss_switch_friend','loss_switch_stranger'],
                        'Loss by switch by previous partner at age 50'),
             test_contrast(fit, {'loss_switch_age':1}, 'interaction',
                           'Loss by switch age slope per decade', 'logRT')]
    estimates = []
    for partner in [None]+PARTNERS:
        for state in (0,1):
            row = test_contrast(fit, switching_weights(partner,state), 'conditional_loss',
                (partner or 'equal partner average')+': '+('switch' if state else 'stay'), 'logRT')
            row.update(previous_partner=partner or 'average', transition='switch' if state else 'stay')
            estimates.append(row)
        if partner is not None:
            tests.append(test_contrast(fit, switching_weights(partner,difference=True),
                'partner_switch_difference', partner+': loss effect switch minus stay', 'logRT'))
    tests = pd.DataFrame(tests); tests['p_holm_six'] = holm(tests.p)
    tests['minimum_rt_s'] = threshold
    estimates = pd.DataFrame(estimates); estimates['minimum_rt_s'] = threshold
    return tests, estimates, counts, fit


def person_features(d, demo, threshold=.15):
    valid = d[d.rt_s.ge(threshold)&d.rt_s.gt(0)].copy()
    valid['log_rt'] = np.log(valid.rt_s)
    current = valid.groupby(KEYS+['partner']).log_rt.mean().unstack().reindex(columns=PARTNERS)
    lag = select_pairs(d, threshold).assign(log_rt=lambda a:np.log(a.rt_s))
    previous = lag.groupby(KEYS+['prev_partner','prev_outcome']).log_rt.mean().unstack(['prev_partner','prev_outcome'])
    features = current[[]].copy()
    features[FEATURES[0]] = current.mean(axis=1, skipna=False)
    features[FEATURES[1]] = current.friend-current.stranger
    effects = pd.DataFrame({p:previous[(p,'punish')]-previous[(p,'reward')] for p in PARTNERS})
    features[FEATURES[2]] = effects.mean(axis=1, skipna=False)
    rf = lag[lag.dataset.eq('rf1')].groupby(KEYS+['partner_switch','prev_outcome']).log_rt.mean().unstack(['partner_switch','prev_outcome'])
    switching = (rf[(1.,'punish')]-rf[(1.,'reward')])-(rf[(0.,'punish')]-rf[(0.,'reward')])
    features[SWITCH_FEATURE] = switching
    result = demo.merge(features.reset_index(),on=KEYS,how='left',validate='one_to_one').sort_values(KEYS).reset_index(drop=True)
    if not np.isfinite(result[FEATURES].to_numpy()).all():
        raise ValueError('Missing RT summary; no silent sample dropping')
    if not np.isfinite(result.loc[result.dataset.eq('rf1'),SWITCH_FEATURE]).all():
        raise ValueError('Missing RF1 switching summary')
    if result.loc[result.dataset.eq('ds003745'),SWITCH_FEATURE].notna().any():
        raise ValueError('Older switching feature must remain missing, never imputed zero')
    return result


def hc3_fit(x,y):
    if not np.isfinite(x).all() or not np.isfinite(y).all() or np.linalg.matrix_rank(x)!=x.shape[1]:
        raise ValueError('Invalid regression inputs')
    bread=np.linalg.inv(x.T@x); beta=bread@x.T@y; residual=y-x@beta
    leverage=np.sum((x@bread)*x,axis=1)
    if (leverage>=1-1e-8).any(): raise ValueError('Unit leverage')
    influence=(x@bread)*(residual/(1-leverage))[:,None]
    covariance=influence.T@influence; df=len(y)-x.shape[1]
    r2=1-residual@residual/np.sum((y-y.mean())**2)
    return beta,covariance,df,r2,1-(1-r2)*(len(y)-1)/df


def cv_folds(data, repeats=20, seed=20261019):
    """Same participant folds across models; balance rare recorded-sex levels."""
    rng=np.random.default_rng(seed); out=[]
    for repeat in range(repeats):
        fold=np.zeros(len(data),int)
        for _,ix in data.groupby(['dataset','sex']).indices.items():
            ix=np.asarray(ix).copy();rng.shuffle(ix)
            fold[ix]=(np.arange(len(ix))+rng.integers(10))%10
        out.append(fold)
    return out


def cv_rmse(base, features, y, folds):
    results=[]
    for fold in folds:
        prediction=np.full(len(y),np.nan)
        for k in range(10):
            train=fold!=k;test=~train
            if not test.any(): continue
            xtrain=base[train];xtest=base[test]
            if features.shape[1]:
                mean=features[train].mean(axis=0);sd=features[train].std(axis=0,ddof=1)
                if (sd<=1e-12).any(): raise ValueError('Constant training feature')
                xtrain=np.column_stack([xtrain,(features[train]-mean)/sd])
                xtest=np.column_stack([xtest,(features[test]-mean)/sd])
            if np.linalg.matrix_rank(xtrain)!=xtrain.shape[1]: raise ValueError('Rank deficient CV training fold')
            prediction[test]=xtest@np.linalg.lstsq(xtrain,y[train],rcond=None)[0]
        if not np.isfinite(prediction).all():raise ValueError('Incomplete CV predictions')
        results.append(np.sqrt(np.mean((y-prediction)**2)))
    return np.asarray(results)


def ratings_models(data):
    rows=[]; coefficients=[]; folds_audit=[]; cv_rows=[]
    specs=[('baseline',[]),('overall_RT',[FEATURES[0]]),('social_RT',[FEATURES[1]]),
           ('post_loss_RT',[FEATURES[2]]),('all_three_RT',FEATURES)]
    for scope, sample in [('pooled',data),('RF1_switch_sensitivity',data[data.dataset.eq('rf1')])]:
        sample=sample.reset_index(drop=True);base=age_design(sample); folds=cv_folds(sample)
        for repeat,fold in enumerate(folds):
            for i,k in enumerate(fold):
                folds_audit.append(dict(scope=scope,repeat=repeat,fold=k,dataset=sample.dataset.iloc[i],subject=sample.subject.iloc[i]))
        use_specs=specs if scope=='pooled' else [('baseline',[]),('all_three_RT',FEATURES),('all_four_RT',FEATURES+[SWITCH_FEATURE])]
        for normalization in ('raw','person_zscored'):
            ratings=transform(sample,normalization)[CELLS].to_numpy(float)
            outcomes={'friend_gap':ratings@GAPS[0], 'friend_minus_stranger_gap':ratings@(GAPS[0]-GAPS[1])}
            for outcome,y in outcomes.items():
                base_cv=cv_rmse(base,np.empty((len(sample),0)),y,folds)
                previous=None
                for spec,features in use_specs:
                    f=sample[features].to_numpy(float)
                    z=(f-f.mean(axis=0))/f.std(axis=0,ddof=1) if features else f
                    x=np.column_stack([base,z]);b,cov,df,r2,adj=hc3_fit(x,y)
                    se=np.sqrt(cov[1,1]);crit=stats.t.ppf(.975,df)
                    cv=cv_rmse(base,f,y,folds)
                    row=dict(scope=scope,normalization=normalization,outcome=outcome,model=spec,n=len(sample),
                        age_slope_per_decade=b[1],age_ci95_low=b[1]-crit*se,age_ci95_high=b[1]+crit*se,
                        age_p=2*stats.t.sf(abs(b[1]/se),df),r_squared=r2,adjusted_r_squared=adj,
                        cv_rmse_mean=cv.mean(),cv_rmse_change_vs_baseline=(cv-base_cv).mean(),df=df)
                    if features:
                        k=len(features);v=b[-k:];c=cov[-k:,-k:];w=float(v@np.linalg.solve(c,v)/k)
                        row.update(rt_block_f=w,rt_block_df_num=k,rt_block_p=stats.f.sf(w,k,df))
                        for j,name in enumerate(features):
                            i=base.shape[1]+j;error=np.sqrt(cov[i,i])
                            coefficients.append(dict(scope=scope,normalization=normalization,outcome=outcome,model=spec,
                                feature=name,coefficient_per_between_person_SD=b[i],ci95_low=b[i]-crit*error,
                                ci95_high=b[i]+crit*error,p=2*stats.t.sf(abs(b[i]/error),df)))
                    if spec=='all_four_RT':
                        error=np.sqrt(cov[-1,-1]);row['switch_increment_p']=2*stats.t.sf(abs(b[-1]/error),df)
                        row['cv_rmse_change_vs_three_RT']=float((cv-previous).mean())
                    for repeat,value in enumerate(cv):cv_rows.append(dict(scope=scope,normalization=normalization,
                        outcome=outcome,model=spec,repeat=repeat,rmse=value,change_vs_baseline=value-base_cv[repeat]))
                    rows.append(row);previous=cv
    results=pd.DataFrame(rows)
    for scope in results.scope.unique():
        for norm in results.normalization.unique():
            ix=results.scope.eq(scope)&results.normalization.eq(norm)
            tests=ix&results.rt_block_p.notna()
            results.loc[tests,'rt_block_p_holm']=holm(results.loc[tests,'rt_block_p'])
            results.loc[ix,'age_p_holm_models_targets']=holm(results.loc[ix,'age_p'])
    return results,pd.DataFrame(coefficients),pd.DataFrame(folds_audit),pd.DataFrame(cv_rows)


def plots(estimates, results, output):
    fig,ax=plt.subplots(figsize=(8.5,5.5));fig.subplots_adjust(left=.13,right=.97,top=.78,bottom=.25)
    for state,color,offset,label in [('stay','#326B9F',-.12,'Partner stays'),('switch','#C46935',.12,'Partner switches')]:
        d=estimates[estimates.transition.eq(state)].set_index('previous_partner').loc[PARTNERS]
        ax.errorbar(np.arange(3)+offset,d.percent_change,
            yerr=np.array([d.percent_change-d.percent_low,d.percent_high-d.percent_change]),
            fmt='o',capsize=5,color=color,label=label,markersize=7,lw=2)
    ax.axhline(0,color='#818B93',lw=1,ls=':');ax.set(xticks=range(3),xticklabels=[p.title() for p in PARTNERS],
        xlabel='Previous partner',ylabel='Next-trial RT: loss versus win (%)')
    ax.legend(frameon=False);ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',color='#E7EBEE');ax.set_axisbelow(True)
    fig.suptitle('Post-loss speeding: partner stays or switches?',fontsize=20,y=.96)
    fig.text(.5,.86,'RF1 only · N = 285 · Adjusted estimates at age 50 with 95% CIs',ha='center',fontsize=11)
    fig.text(.13,.14,'Negative values: faster after losses. Previous RT, current partner, timing and run effects controlled.',fontsize=9)
    fig.text(.13,.08,'Older-dataset partners stay constant within blocks; block boundaries are not treated as switches.',fontsize=9)
    fig.text(.13,.03,'Exploratory follow-up; same basic behavioral eligibility and adjacent-response safeguards.',fontsize=9)
    for ext in ('png','svg'):fig.savefig(output/f'post-loss-partner-switch.{ext}',dpi=200)
    plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12,5.8),sharey=True)
    fig.subplots_adjust(left=.23,right=.97,top=.78,bottom=.24,wspace=.16)
    names=['baseline','overall_RT','social_RT','post_loss_RT','all_three_RT']
    labels=['Original model','+ Overall RT','+ Friend–stranger RT','+ Post-loss RT','+ All three RT measures']
    for ax,target,title in zip(axes,['friend_gap','friend_minus_stranger_gap'],['Friend win–loss gap','Friend gap minus stranger gap']):
        d=results[results.scope.eq('pooled')&results.normalization.eq('raw')&results.outcome.eq(target)].set_index('model').loc[names]
        ax.errorbar(d.age_slope_per_decade,np.arange(5),xerr=np.array([d.age_slope_per_decade-d.age_ci95_low,d.age_ci95_high-d.age_slope_per_decade]),fmt='o',capsize=4,color='#326B9F',lw=2)
        ax.axvline(0,color='#818B93',lw=1,ls=':');ax.set(yticks=range(5),yticklabels=labels,xlabel='Rating points per decade',title=title)
        ax.spines[['top','right']].set_visible(False);ax.grid(axis='x',color='#E7EBEE');ax.set_axisbelow(True)
    axes[0].invert_yaxis()
    fig.suptitle('Do RT covariates change the ratings age effects?',fontsize=20,y=.96)
    fig.text(.5,.86,'Raw ratings · Same 318 participants · Dataset and recorded sex adjusted',ha='center',fontsize=11)
    fig.text(.10,.13,'Points: age coefficients; bars: HC3 95% confidence intervals. Fixed exploratory model set; no p-value selection.',fontsize=10)
    fig.text(.10,.065,'RT summaries are measured during the task, not established confounders. Adjustment changes the age estimand.',fontsize=10)
    for ext in ('png','svg'):fig.savefig(output/f'ratings-age-with-RT.{ext}',dpi=200)
    plt.close(fig)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',type=Path,default=ROOT/'qc/trial-behavior-exploratory/switch-ratings')
    args=p.parse_args();out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    parent=ROOT/'qc/trial-behavior-exploratory/provenance.json'
    meta=json.loads(parent.read_text());trial=ROOT/'derivatives/behavioral-exploratory/trials.tsv'
    if hashlib.sha256(trial.read_bytes()).hexdigest()!=meta['trial_sha256']:raise ValueError('Trial provenance mismatch')
    d=pd.read_csv(trial,sep='\t',dtype={'dataset':str,'subject':str,'session':str})
    demo=d[KEYS+['age','sex']].drop_duplicates()
    if demo.duplicated(KEYS).any() or len(demo)!=meta['n_ratings_eligible']:raise ValueError('Demographic mismatch')
    tests=[];estimates=[];inventories=[]
    for threshold in (.15,0.):
        table,means,counts,fit=analyze_switch(d,demo,threshold)
        tests.append(table);estimates.append(means)
        inventories.append(dict(minimum_rt_s=threshold,**{k:v for k,v in fit.items() if k not in ('beta','cov')}))
        print(table.to_string(index=False),flush=True)
        if threshold==.15:counts.to_csv(out/'transition-counts.tsv',sep='\t',index=False)
    pd.concat(tests).to_csv(out/'switch-tests.tsv',sep='\t',index=False)
    pd.concat(estimates).to_csv(out/'switch-estimates.tsv',sep='\t',index=False)
    features=person_features(d,demo)
    ratings_paths=[ROOT/'logs/records/ratings-qc-subject-level.tsv',ROOT/'logs/records/analysis-subject-dispositions.tsv']
    ratings=load_ratings(*ratings_paths)[KEYS+CELLS]
    data=features.merge(ratings,on=KEYS,how='outer',validate='one_to_one',indicator=True)
    if not data._merge.eq('both').all():raise ValueError('RT and ratings cohorts differ; no silent dropping')
    results,coefficients,folds,cv=ratings_models(data)
    for name,frame in [('participant-RT-features',features),('ratings-model-comparisons',results),
                       ('ratings-RT-coefficients',coefficients),('ratings-CV-folds',folds),('ratings-CV-results',cv)]:
        frame.to_csv(out/f'{name}.tsv',sep='\t',index=False)
    plots(estimates[0],results,out)
    print(results.to_string(index=False),flush=True)
    sources=[parent,*ratings_paths,Path(__file__),ROOT/'code/plot_next_trial_rt_age.py',ROOT/'code/explore_trial_behavior.py',
             ROOT/'code/analyze_raw_ratings.py',ROOT/'code/plot_normalized_loss_ratings.py',ROOT/'code/plot_rating_gaps.py']
    provenance=dict(exploratory=True,ratings_policy=meta['ratings_policy'],trial_sha256=meta['trial_sha256'],
        switching='RF1 only. Extend previous age*outcome*previous-partner model with switch*previous-partner, switch*age, loss*switch, loss*switch*previous-partner, loss*switch*age. All lower-order terms retained. Run FE; participant-cluster CR1 t/F inference. Previous partner contrasts at age50. No age*loss*switch*partner four-way interaction.',
        switch_multiplicity='Six planned follow-up tests, raw p and Holm6. Conditional cell estimates shown with pointwise CIs, not additional significance claims. All-positive RT sensitivity separately corrected.',
        feature_definitions={'overall_logRT':'Equal mean of three current-partner mean log RTs.',
            'friend_minus_stranger_logRT':'Current friend mean log RT minus current stranger mean log RT.',
            'loss_minus_win_logRT':'Equal average across three previous partners of mean next-trial log RT after loss minus after win.',
            SWITCH_FEATURE:'RF1 only: loss-minus-win mean next log RT when partner switches minus the same when partner stays; averages actual previous-partner composition within each cell.'},
        features_caveat='Descriptive individual differences, not participant coefficients from the adjusted population model. No outcome-based feature selection. Measurement error/unequal trial counts not modeled; associations conditional on these noisy summaries, not mediation.',
        ratings='Same318; raw primary, person-zscored six-rating profile sensitivity (ddof1). Two fixed targets: friend win-loss gap and friend-minus-stranger gap difference. Base age/10+dataset+sex. Add overall RT, social RT, post-loss RT separately and jointly. RF1-only sensitivity base, three RT and all four including switch-specific measure; never impute older switches.',
        ratings_inference='HC3 t age/feature tests and robust Wald F for added RT block. Holm block tests across two targets/four extensions within each raw/normalized pooled scope; RF1 scope separately. All age-model-target p also Holm adjusted within scope/normalization. No favorable-model selection; primary ratings model unchanged.',
        prediction='20 repeats of 10-fold participant CV, seed20261019, dataset/sex-stratified folds shared across models/outcomes. RT centering/scaling learned only on training participants. Mean held-out RMSE and change vs same-scope baseline; no significance test treating folds as independent.',
        limitations=['Switch analysis cannot be pooled across incompatible block/event designs.', 'No additional imaging exclusions. Previous neutral and invalid adjacent responses omitted without bridging.',
                     'Task RT can be age-related, so adding it changes the estimand and may overadjust; this is not causal mediation.',
                     'Response-based behavioral eligibility, exploratory multiplicity and bounded ratings remain limitations.',
                     'Reused same dataset for exploratory hypothesis generation; held-out prediction within it is not external validation.'],
        inventory=inventories,sources=[dict(path=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sources])
    (out/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    print('CHECK PASSED: switching and ratings models complete; original models and exclusions unchanged.')


if __name__=='__main__':main()
