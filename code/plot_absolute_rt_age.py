#!/usr/bin/env python3
"""Equal-participant absolute RT age curves and paired partner slope tests.

Uses the verified trial derivative; complements, does not replace, run-fixed-
effect analyses. Mean log RT per person/partner is back-transformed for plotting.
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

from analyze_raw_ratings import ROOT, KEYS, age_design, holm

PARTNERS = ['friend', 'stranger', 'computer']


def summarize(trials, threshold=.15):
    demo = trials[KEYS+['age','sex']].drop_duplicates()
    if demo.duplicated(KEYS).any(): raise ValueError('Inconsistent demographics within participant')
    valid = trials[trials.rt_s.ge(threshold) & trials.rt_s.gt(0)].copy()
    valid['log_rt'] = np.log(valid.rt_s)
    means = valid.groupby(KEYS+['partner']).log_rt.mean().unstack()
    out = demo.merge(means, on=KEYS, how='left', validate='one_to_one').sort_values(KEYS)
    if not np.isfinite(out[PARTNERS].to_numpy()).all():
        raise ValueError('All participants must contribute all three partners; no silent dropping')
    return out


def fit(data, ages):
    x = age_design(data); y = data[PARTNERS].to_numpy(float)
    bread = np.linalg.inv(x.T@x); beta = bread@x.T@y
    residual = y-x@beta; leverage = np.sum((x@bread)*x, axis=1)
    adjusted_residual = residual/(1-leverage)[:,None]
    influence = (x@bread[:,1])[:,None]*adjusted_residual
    covariance = influence.T@influence
    df = len(data)-x.shape[1]; critical = stats.t.ppf(.975,df)
    g = np.tile(x.mean(axis=0),(len(ages),1)); g[:,1]=(np.asarray(ages)-data.age.mean())/10
    predicted = g@beta
    se = np.sqrt((g@bread@x.T)**2@adjusted_residual**2)
    results = []
    contrasts = [('overall_age','Mean across partners',np.ones(3)/3)]
    contrasts += [('partner_age',p,np.eye(3)[i]) for i,p in enumerate(PARTNERS)]
    contrasts += [('paired_age_difference',PARTNERS[i]+' minus '+PARTNERS[j],np.eye(3)[i]-np.eye(3)[j])
                  for i,j in ((0,1),(0,2),(1,2))]
    for family,label,v in contrasts:
        b = v@beta[1]; stderr = np.sqrt(v@covariance@v)
        lo,hi = b-critical*stderr,b+critical*stderr
        results.append(dict(family=family,comparison=label,n=len(data),log_rt_per_decade=b,se_hc3=stderr,
            ci95_low=lo,ci95_high=hi,percent_per_decade=100*np.expm1(b),percent_low=100*np.expm1(lo),
            percent_high=100*np.expm1(hi),df=df,p=2*stats.t.sf(abs(b/stderr),df)))
    c = np.array([[1,-1,0],[1,0,-1]])
    b = c@beta[1]; cov = c@covariance@c.T
    chi2 = float(b@np.linalg.solve(cov,b))
    results.append(dict(family='joint_age_partner',comparison='All partner age slopes equal',n=len(data),
                        chi2=chi2,df=2,p=stats.chi2.sf(chi2,2)))
    tests = pd.DataFrame(results); tests['p_holm_family']=np.nan
    for family in ('partner_age','paired_age_difference'):
        ix=tests.family.eq(family); tests.loc[ix,'p_holm_family']=holm(tests.loc[ix,'p'])
    rows=[]
    for j,p in enumerate(PARTNERS):
        for i,a in enumerate(ages):
            rows.append(dict(partner=p,age=a,geometric_rt_s=np.exp(predicted[i,j]),
                             ci95_low_s=np.exp(predicted[i,j]-critical*se[i,j]),
                             ci95_high_s=np.exp(predicted[i,j]+critical*se[i,j])))
    return pd.DataFrame(rows),tests


def plot(predictions, n, output):
    fig,ax=plt.subplots(figsize=(9,6.5));fig.subplots_adjust(left=.115,right=.97,top=.81,bottom=.23)
    for p,color,style in zip(PARTNERS,['#326B9F','#C07A32','#338574'],['-','--','-.']):
        d=predictions[predictions.partner.eq(p)]
        ax.fill_between(d.age,d.ci95_low_s,d.ci95_high_s,color=color,alpha=.16,linewidth=0)
        ax.plot(d.age,d.geometric_rt_s,color=color,lw=3,linestyle=style,label=p.title())
    ax.set(xlabel='Age (years)',ylabel='Response time (seconds; geometric mean)',xticks=[20,40,60,80])
    ax.tick_params(labelsize=12);ax.xaxis.label.set_size(13);ax.yaxis.label.set_size(13)
    ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',color='#E7EBEE');ax.set_axisbelow(True)
    ax.legend(frameon=False,fontsize=12,loc='upper left')
    fig.suptitle('Response time across age by partner',fontsize=22,y=.96)
    fig.text(.5,.885,f'N = {n}  ·  Behavioral exclusions applied  ·  Dataset and recorded sex adjusted',ha='center',fontsize=12,color='#4F5C67')
    fig.text(.115,.125,'Each participant contributes one mean log RT per partner; curves are back-transformed to seconds.',fontsize=10)
    fig.text(.115,.075,'Bands: pointwise HC3 95% confidence intervals. RT ≥150 ms; misses excluded, not assigned timeout RTs.',fontsize=10)
    fig.text(.115,.025,'Exploratory participant-level model; equal participant weighting. Curves reflect the sample’s dataset/sex mix.',fontsize=10)
    for ext in ('png','svg'): fig.savefig(output/f'absolute-RT-age.{ext}',dpi=220)
    plt.close(fig)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--trials',type=Path,default=ROOT/'derivatives/behavioral-exploratory/trials.tsv')
    p.add_argument('--output-dir',type=Path,default=ROOT/'qc/trial-behavior-exploratory')
    a=p.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    parent=ROOT/'qc/trial-behavior-exploratory/provenance.json'
    meta=json.loads(parent.read_text())
    if hashlib.sha256(a.trials.read_bytes()).hexdigest()!=meta['trial_sha256']:
        raise ValueError('Trial file does not match verified exploration provenance; regenerate source audit')
    trials=pd.read_csv(a.trials,sep='\t',dtype={'dataset':str,'subject':str,'session':str})
    results=[]
    for threshold in (.15,0.0):
        data=summarize(trials,threshold)
        if len(data)!=meta['n_ratings_eligible']: raise ValueError('Sample differs from verified ratings cohort')
        predictions,tests=fit(data,np.linspace(data.age.min(),data.age.max(),180))
        tests['minimum_rt_s']=threshold;results.append(tests)
        if threshold==.15:
            plot(predictions,len(data),a.output_dir)
            predictions.to_csv(a.output_dir/'absolute-RT-age-predictions.tsv',sep='\t',index=False)
            data[KEYS+['age','sex']+PARTNERS].to_csv(a.output_dir/'participant-partner-mean-logRT.tsv',sep='\t',index=False)
        print(tests.to_string(index=False))
    pd.concat(results,ignore_index=True).to_csv(a.output_dir/'absolute-RT-age-tests.tsv',sep='\t',index=False)
    report=dict(n=len(data),ratings_policy=meta['ratings_policy'],exploratory=True,
        response='Mean log RT across valid responded trials for each participant/partner; equal participant weighting. Geometric means after exponentiation, not arithmetic mean RT.',
        model='Separate partner outcomes: intercept + centered age/10 + dataset + recorded sex; shared participant-level X; HC3 covariance preserves paired slope dependencies.',
        estimand='Overall age coefficient averages the three partner log-RT age slopes. Paired tests compare slopes directly; joint 2-df Wald chi-square tests equality.',
        plotting='Covariates held at empirical dataset/sex mix; pointwise 95% t intervals back-transformed to seconds. Not individual prediction intervals.',
        distinction='Complement to trial-level run-fixed-effect model: estimates between-person overall age association, but does not control trial position/block context; not a replacement for earlier partner-effect tests.',
        multiplicity='Uncorrected p plus Holm within three partner slopes and within three paired slope differences; overall and joint tests shown separately. Threshold sensitivity explicitly labeled.',
        trial_sha256=meta['trial_sha256'],sources=[dict(path=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in (parent,Path(__file__),ROOT/'code/analyze_raw_ratings.py')])
    (a.output_dir/'absolute-RT-age-provenance.json').write_text(json.dumps(report,indent=2)+'\n')
    print('CHECK PASSED: absolute RT curves and paired slope tests use the same verified participants.')


if __name__=='__main__':main()
