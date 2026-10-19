#!/usr/bin/env python3
"""Ceiling/floor diagnostics and recorded-sex sensitivity, same behavioral cohort.

Fractional-logit fits model the observed bounded mean, not an unobserved rating
beyond the scale. No ceiling responses are discarded or imputed.
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
from scipy import optimize, special, stats

from analyze_raw_ratings import ROOT, KEYS, CELLS, LABELS, age_design, age_fit, demographics, load_ratings, holm
from audit_ratings_qc import RATINGS_POLICY
from plot_rating_gaps import GAPS, PARTNERS, COLORS


def fractional_fit(x, y):
    """Six fractional logits; paired sandwich covariance of average age derivatives.

    y is raw -5..5. Scores are clustered by participant across the six fits.
    Delta-method gradients average over the observed (fixed) covariate sample.
    HC1 finite-sample multiplier n/(n-k); normal rather than t inference.
    """
    if not np.isfinite(y).all() or (np.abs(y) > 5).any():
        raise ValueError('Fractional response requires finite -5..5 ratings')
    n, k = x.shape
    estimates, influences, coefficients = [], [], []
    for response in ((y+5)/10).T:
        def objective(b):
            eta = x @ b
            return np.sum(np.logaddexp(0, eta)-response*eta)
        def score(b):
            return x.T @ (special.expit(x @ b)-response)
        def hessian(b):
            mu = special.expit(x @ b)
            return x.T @ (x*(mu*(1-mu))[:, None])
        fit = optimize.minimize(objective, np.zeros(k), jac=score, hess=hessian,
                                method='trust-exact', options={'gtol': 1e-9})
        b = fit.x
        # Near convergence, objective differences can round to zero before the
        # score tolerance is met. Polish the score with a Newton step, accepting
        # only a finite update that does not increase the objective materially.
        for _ in range(3):
            if np.max(np.abs(score(b))) < 1e-8:
                break
            candidate = b-np.linalg.solve(hessian(b),score(b))
            if not np.isfinite(candidate).all() or objective(candidate) > objective(b)+1e-10:
                break
            b = candidate
        if not np.isfinite(b).all() or np.max(np.abs(score(b))) > 1e-6:
            raise ValueError(f'Fractional fit did not converge: {fit.message}')
        mu = special.expit(x @ b); weight = mu*(1-mu)
        bread = np.linalg.inv(hessian(b))
        ame = 10*b[1]*weight.mean()
        gradient = 10*b[1]*np.mean((weight*(1-2*mu))[:,None]*x, axis=0)
        gradient[1] += 10*weight.mean()
        influence = ((response-mu)[:,None]*x) @ bread @ gradient
        estimates.append(ame); influences.append(influence); coefficients.append(b)
    influence = np.column_stack(influences)
    return np.asarray(estimates), influence.T @ influence*n/(n-k), np.asarray(coefficients)


def endpoint_summary(data):
    records = []
    groups = [('All ages', data)]
    for lo, hi in ((18,40),(40,60),(60,111)):
        groups.append((f'{lo}–{hi-1}' if hi < 111 else '60+', data[data.age.ge(lo) & data.age.lt(hi)]))
    for label, group in groups:
        for col, condition in zip(CELLS, LABELS):
            for endpoint, value in (('ceiling',5),('floor',-5)):
                n = len(group); count = int(group[col].eq(value).sum())
                if not n:
                    continue
                # Wilson interval for a descriptive, unadjusted proportion.
                z=stats.norm.ppf(.975); p=count/n; denominator=1+z*z/n
                center=(p+z*z/(2*n))/denominator
                half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/denominator
                records.append(dict(age_group=label,condition=condition,endpoint=endpoint,
                    n=n,count=count,percent=100*p,ci95_low=100*(center-half),ci95_high=100*(center+half)))
    return pd.DataFrame(records)


def slope_tables(data):
    rows = []
    def add(method, sex, slopes, cov, df):
        for family, names, weights in (
            ('six_condition_age_slopes', LABELS, np.eye(6)),
            ('partner_gap_age_slopes', PARTNERS, GAPS),
            ('paired_gap_slope_differences', ['Friend minus Stranger','Friend minus Computer','Stranger minus Computer'],
             np.array([GAPS[0]-GAPS[1],GAPS[0]-GAPS[2],GAPS[1]-GAPS[2]]))):
            family_rows=[]
            critical=stats.t.ppf(.975,df) if df else stats.norm.ppf(.975)
            for name, c in zip(names,weights):
                b=float(c@slopes); se=float(np.sqrt(c@cov@c))
                p=float(2*(stats.t.sf(abs(b/se),df) if df else stats.norm.sf(abs(b/se))))
                family_rows.append(dict(method=method,sex_adjusted=sex,family=family,comparison=name,n=len(data),
                    points_per_decade=b,se=se,ci95_low=b-critical*se,ci95_high=b+critical*se,p=p))
            for row,p in zip(family_rows,holm([r['p'] for r in family_rows])):
                row['p_holm_family']=float(p)
            rows.extend(family_rows)
        c=np.array([GAPS[0]-GAPS[1],GAPS[0]-GAPS[2]])
        delta=c@slopes; w=float(delta@np.linalg.solve(c@cov@c.T,delta))
        rows.append(dict(method=method,sex_adjusted=sex,family='joint_gap_slope_equality',
                    comparison='Age x partner on gap',n=len(data),chi2=w,df=2,p=float(stats.chi2.sf(w,2))))
    endpoint_rows=[]
    for sex in (True,False):
        x=age_design(data,sex)
        b,cov,df=age_fit(data,sex)
        add('OLS_HC3',sex,b,cov,df)
        b,cov,_=fractional_fit(x,data[CELLS].to_numpy(float))
        add('fractional_logit_AME_HC1',sex,b,cov,None)
        # Linear-probability HC3 diagnostic of endpoint prevalence, not a latent
        # rating model. Six tests: ceiling on each win, floor on each loss.
        binary=data.copy()
        for i,col in enumerate(CELLS):
            binary[col]=data[col].eq(5 if i%2==0 else -5).astype(float)
        b,cov,df=age_fit(binary,sex)
        varying=binary[CELLS].nunique().to_numpy()>1
        ps=np.full(6,np.nan)
        ps[varying]=2*stats.t.sf(abs(b[varying]/np.sqrt(np.diag(cov)[varying])),df)
        # Keep the planned six-test correction conservative; untestable constant
        # endpoints are reported unavailable, not as evidence for a null effect.
        adjusted=holm(np.where(varying,ps,1.))
        for i,condition in enumerate(LABELS):
            se=float(np.sqrt(cov[i,i])); critical=stats.t.ppf(.975,df)
            endpoint_rows.append(dict(sex_adjusted=sex,condition=condition,
                endpoint='ceiling' if i%2==0 else 'floor',n=len(data),
                status='estimated' if varying[i] else 'constant_endpoint_not_tested',
                percentage_points_per_decade=100*b[i] if varying[i] else np.nan,
                ci95_low=100*(b[i]-critical*se) if varying[i] else np.nan,
                ci95_high=100*(b[i]+critical*se) if varying[i] else np.nan,
                p=ps[i],p_holm_six=adjusted[i] if varying[i] else np.nan))
    return pd.DataFrame(rows),pd.DataFrame(endpoint_rows)


def plot(summary, results, output):
    fig,axes=plt.subplots(1,3,figsize=(15,5.8))
    fig.subplots_adjust(left=.065,right=.985,bottom=.24,top=.78,wspace=.46)
    ax=axes[0]
    for partner,color in zip(PARTNERS,COLORS):
        s=summary[summary.condition.eq(partner+' win') & summary.endpoint.eq('ceiling') & summary.age_group.ne('All ages')]
        ax.errorbar(np.arange(3),s.percent,yerr=[s.percent-s.ci95_low,s.ci95_high-s.percent],
                    marker='o',capsize=3,color=color,label=partner,lw=2)
    ax.set_xticks(range(3),['18–39','40–59','60+'])
    ax.set(xlabel='Age group (descriptive only)',ylabel='Win ratings at maximum (%)',ylim=(0,100))
    ax.set_title('A. Ceiling prevalence',loc='left',fontsize=12,fontweight='bold')
    ax.legend(frameon=False,fontsize=9)
    for axis,method,title in zip(axes[1:],['OLS_HC3','fractional_logit_AME_HC1'],
        ['B. Friend win, loss and gap','C. Bounded-response sensitivity']):
        for offset,sex,marker,label in [(-.10,True,'o','Dataset + recorded sex'),(.10,False,'s','Dataset only')]:
            s=results[results.method.eq(method) & results.sex_adjusted.eq(sex)]
            for j,name in enumerate(['Friend win','Friend loss','Friend']):
                row=s[s.comparison.eq(name)].iloc[0]
                axis.errorbar(row.points_per_decade,j+offset,
                    xerr=[[row.points_per_decade-row.ci95_low],[row.ci95_high-row.points_per_decade]],
                    fmt=marker,color='#326B9F' if sex else '#C07A32',capsize=3,
                    label=label if j==0 else None)
        axis.axvline(0,color='#777777',ls='--',lw=1)
        axis.set_yticks(range(3),['Win','Loss','Win − loss']);axis.set_ylim(2.5,-.7)
        axis.set_xlabel('Rating points per decade');axis.set_title(title,loc='left',fontsize=12,fontweight='bold')
        axis.set_xlim(-.46,.43)
    handles,labels=axes[1].get_legend_handles_labels()
    fig.legend(handles,labels,loc='center',bbox_to_anchor=(.66,.825),ncol=2,fontsize=9,frameon=False)
    for ax in axes:
        ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',color='#E8EBED');ax.set_axisbelow(True)
    fig.suptitle('Does the friend-win ceiling explain the age association?',fontsize=19,y=.96)
    fig.text(.5,.865,f'Same {int(results.n.iloc[0])} participants and primary behavioral exclusions in every model',ha='center',fontsize=11)
    fig.text(.065,.14,'A: unadjusted proportions with Wilson 95% CIs. B: linear slopes with HC3 95% CIs. C: fractional-logit average age derivatives.',fontsize=10)
    fig.text(.065,.095,'C uses paired participant-level robust covariance and 95% normal CIs. All age models use continuous age and a dataset indicator.',fontsize=10)
    fig.text(.065,.05,'Ceiling responses are retained. Bounded-response modeling cannot recover preferences hidden beyond the rating scale.',fontsize=10)
    for ext in ('png','svg'):
        fig.savefig(output/f'ceiling-sex-sensitivity.{ext}',dpi=180)
    plt.close(fig)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',type=Path,default=ROOT/'qc/ratings-raw/ceiling-sensitivity')
    args=p.parse_args()
    sources=[ROOT/'logs/records/ratings-qc-subject-level.tsv',ROOT/'logs/records/analysis-subject-dispositions.tsv',
             ROOT.parent/'rf1-sra-linux2/bids/participants.tsv',ROOT/'participants-srndna.tsv']
    data=load_ratings(*sources[:2]);eligibility=data.attrs['behavioral_eligibility']
    data=data.merge(pd.concat([demographics(sources[2],'rf1'),demographics(sources[3],'ds003745')]),
                    on=KEYS,how='left',validate='one_to_one').sort_values(KEYS)
    if not (data.age.between(18,110) & data.sex.isin(['F','M','O'])).all():
        raise ValueError('Complete age and recorded sex required; no silent complete-case change')
    output=args.output_dir;output.mkdir(parents=True,exist_ok=True)
    summary=endpoint_summary(data);results,endpoint_tests=slope_tables(data)
    summary.to_csv(output/'endpoint-prevalence.tsv',sep='\t',index=False)
    results.to_csv(output/'age-sensitivity-tests.tsv',sep='\t',index=False)
    endpoint_tests.to_csv(output/'endpoint-age-tests.tsv',sep='\t',index=False)
    plot(summary,results,output)
    sources += [Path(__file__),ROOT/'code/analyze_raw_ratings.py',ROOT/'code/audit_ratings_qc.py',ROOT/'code/plot_rating_gaps.py']
    meta=dict(n=len(data),sample_by_dataset=data.groupby('dataset').size().to_dict(),
        recorded_sex_counts=data.sex.value_counts().to_dict(),task_valid_n=len(eligibility),ratings_policy=RATINGS_POLICY,
        design='Intercept + centered continuous age per decade + RF1 dataset dummy; with/without recorded sex M/O dummy offsets (F reference).',
        exclusions='Same primary behavioral exclusions; no MRI QC, no exclusion of ceiling/floor responses.',
        bounded_sensitivity='Fractional logit of (rating+5)/10, endpoints included; average age derivative on original scale. Paired sandwich HC1 and delta method conditional on observed covariates; normal CIs.',
        endpoint_tests='Linear-probability HC3 slopes in percentage points/decade. Six tests (win ceilings and loss floors), Holm within each adjustment specification.',
        multiplicity='Separate exploratory Holm families of 6 condition slopes, 3 gaps, 3 paired gap differences per model; no experiment-wide claim.',
        limitations=['Does not identify latent preferences above/below scale boundaries.',
            'Bounded mean sensitivity is not an ordinal or censored-latent model.',
            'Response-based eligibility may affect associations; no causal aging interpretation.',
            'Recorded sex O category has only 3 participants; this is not a test of sex moderation or verified gender identity.'],
        reference='https://www.nber.org/papers/t0147',
        sources=[dict(path=str(f.resolve()),sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sources])
    (output/'provenance.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps(meta,indent=2))
    print(results[results.comparison.isin(['Friend win','Friend loss','Friend','Friend minus Stranger','Age x partner on gap'])].to_string(index=False))
    print(endpoint_tests[endpoint_tests.condition.str.startswith('Friend')].to_string(index=False))
    print('CHECK PASSED: ceiling/sex sensitivities completed on the identical primary behavioral sample.')


if __name__=='__main__':
    main()
