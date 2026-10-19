#!/usr/bin/env python3
"""Pooled behavioral win-minus-loss gaps after the primary ratings exclusions."""
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

from analyze_raw_ratings import ROOT, KEYS, CELLS, age_design, age_fit, demographics, load_ratings, holm
from audit_ratings_qc import RATINGS_POLICY

PARTNERS = ['Friend', 'Stranger', 'Computer']
GAPS = np.array([[0,0,0,0,1,-1], [0,0,1,-1,0,0], [1,-1,0,0,0,0]], dtype=float)
COLORS = ['#326B9F', '#C07A32', '#338574']


def gap_analysis(data, ages, adjust_sex=True):
    x = age_design(data, adjust_sex=adjust_sex)
    y = data[CELLS].to_numpy(float) @ GAPS.T
    bread = np.linalg.inv(x.T @ x)
    beta = bread @ x.T @ y
    residual = y - x @ beta
    leverage = np.sum((x @ bread)*x, axis=1)
    if np.max(leverage) >= 1-1e-8:
        raise ValueError('Unit leverage prevents HC3 inference')
    adjusted_residual = residual / (1-leverage)[:,None]
    influence = (x @ bread[:,1])[:,None] * adjusted_residual
    cov = influence.T @ influence
    df = len(data)-x.shape[1]
    critical = stats.t.ppf(.975, df)
    six_slopes, six_cov, _ = age_fit(data, adjust_sex=adjust_sex)
    np.testing.assert_allclose(beta[1], GAPS @ six_slopes, atol=1e-12)
    np.testing.assert_allclose(cov, GAPS @ six_cov @ GAPS.T, atol=1e-12)
    g = np.tile(x.mean(axis=0), (len(ages),1))
    g[:,1] = (np.asarray(ages)-data.age.mean())/10
    mean = g @ beta
    se = np.sqrt((g @ bread @ x.T)**2 @ adjusted_residual**2)
    tests = []
    def test(family, name, weights):
        b = float(weights @ beta[1]); error = float(np.sqrt(weights @ cov @ weights))
        if not np.isfinite(error) or error <= 0:
            raise ValueError('Invalid gap slope standard error')
        return dict(family=family, comparison=name, n=len(data), points_per_decade=b,
                    se_hc3=error, ci95_low=b-critical*error, ci95_high=b+critical*error,
                    df=df, p=float(2*stats.t.sf(abs(b/error),df)))
    for i, name in enumerate(PARTNERS):
        tests.append(test('partner_age_slopes',name,np.eye(3)[i]))
    for i,j in ((0,1),(0,2),(1,2)):
        tests.append(test('paired_slope_differences',f'{PARTNERS[i]} minus {PARTNERS[j]}',np.eye(3)[i]-np.eye(3)[j]))
    for family in ('partner_age_slopes','paired_slope_differences'):
        members = [r for r in tests if r['family']==family]
        for row, p in zip(members,holm([r['p'] for r in members])):
            row['p_holm_family'] = float(p)
    c = np.array([[1,-1,0],[1,0,-1]])
    difference = c @ beta[1]
    w = float(difference @ np.linalg.solve(c @ cov @ c.T, difference))
    tests.append(dict(family='joint_slope_equality',comparison='Age x partner on win-minus-loss gap',
                      n=len(data),chi2=w,df=2,p=float(stats.chi2.sf(w,2))))
    return mean, mean-critical*se, mean+critical*se, pd.DataFrame(tests)


def plot(data, output):
    ages = np.linspace(data.age.min(),data.age.max(),180)
    means,low,high,tests = gap_analysis(data,ages)
    slopes=tests[tests.family.eq('partner_age_slopes')].reset_index(drop=True)
    fig,(ax,forest)=plt.subplots(1,2,figsize=(12,5.8),gridspec_kw={'width_ratios':[1.65,1]})
    fig.subplots_adjust(left=.075,right=.98,top=.79,bottom=.24,wspace=.31)
    for j,(name,color) in enumerate(zip(PARTNERS,COLORS)):
        ax.fill_between(ages,low[:,j],high[:,j],color=color,alpha=.15)
        ax.plot(ages,means[:,j],color=color,lw=2.7,label=name)
        row=slopes.iloc[j]
        forest.errorbar(row.points_per_decade,j,
            xerr=[[row.points_per_decade-row.ci95_low],[row.ci95_high-row.points_per_decade]],
            fmt='o',color=color,markersize=7,capsize=4,lw=2)
    ax.set(xlabel='Age (years)',ylabel='Adjusted win − loss rating',ylim=(0,10),xlim=(18,89))
    ax.set_xticks([20,40,60,80]); ax.legend(frameon=False,loc='upper right')
    ax.set_title('Rating separation',loc='left',fontsize=12,fontweight='bold')
    forest.axvline(0,color='#7C858C',lw=1,linestyle='--')
    forest.set_yticks(range(3),PARTNERS); forest.invert_yaxis(); forest.set_ylim(2.6,-.6)
    forest.set_xlabel('Change in win − loss per decade')
    forest.set_title('Age slopes and 95% CIs',loc='left',fontsize=12,fontweight='bold')
    for panel in (ax,forest):
        panel.spines[['top','right']].set_visible(False)
        panel.grid(axis='y' if panel is ax else 'x',color='#E8EBED',lw=.7)
        panel.set_axisbelow(True)
    fig.suptitle('Win–loss rating separation across age',fontsize=20,y=.97)
    fig.text(.5,.875,f'Pooled behavior-only sample, N = {len(data)} | Primary ratings exclusions applied',
             ha='center',fontsize=11,color='#505A63')
    fig.text(.075,.13,'Larger gaps mean greater separation between win and loss ratings; a negative slope means a narrowing gap.',fontsize=10)
    fig.text(.075,.085,'Raw ratings, not z-scores. Models adjust for dataset and recorded sex; bands and intervals are pointwise HC3 95% CIs.',fontsize=9.5)
    fig.text(.075,.04,'Exclude missing/incomplete/all-identical ratings and any within-partner loss > win; equality allowed. MRI QC exclusions are not applied.',fontsize=9)
    for extension in ('png','svg'):
        fig.savefig(output/f'win-loss-gap-by-age.{extension}',dpi=180)
    plt.close(fig)
    predictions=pd.DataFrame([dict(partner=name,age=float(age),adjusted_gap=means[i,j],
                              ci95_low=low[i,j],ci95_high=high[i,j],n=len(data))
                             for j,name in enumerate(PARTNERS) for i,age in enumerate(ages)])
    predictions.to_csv(output/'win-loss-gap-age-predictions.tsv',sep='\t',index=False)
    tests.to_csv(output/'win-loss-gap-age-tests.tsv',sep='\t',index=False)
    return tests


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ratings',type=Path,default=ROOT/'logs/records/ratings-qc-subject-level.tsv')
    p.add_argument('--cohort',type=Path,default=ROOT/'logs/records/analysis-subject-dispositions.tsv')
    p.add_argument('--rf1-participants',type=Path,default=ROOT.parent/'rf1-sra-linux2/bids/participants.tsv')
    p.add_argument('--ds-participants',type=Path,default=ROOT/'participants-srndna.tsv')
    p.add_argument('--output-dir',type=Path,default=ROOT/'qc/ratings-raw')
    args=p.parse_args()
    data=load_ratings(args.ratings,args.cohort)
    eligibility=pd.DataFrame(data.attrs['behavioral_eligibility'])
    demo=pd.concat([demographics(args.rf1_participants,'rf1'),demographics(args.ds_participants,'ds003745')])
    data=data.merge(demo,on=KEYS,how='left',validate='one_to_one').sort_values(KEYS)
    if not (data.age.between(18,110) & data.sex.isin(['F','M','O'])).all():
        raise ValueError('Complete age/sex coverage required; no silent demographic exclusions')
    args.output_dir.mkdir(parents=True,exist_ok=True)
    tests=plot(data,args.output_dir)
    sources=[args.ratings,args.cohort,args.rf1_participants,args.ds_participants,Path(__file__),
             ROOT/'code/analyze_raw_ratings.py',ROOT/'code/audit_ratings_qc.py']
    meta=dict(n=len(data),sample_by_dataset=data.groupby('dataset').size().to_dict(),
              task_valid_n=len(eligibility),excluded_n=int(eligibility.primary_included.eq('false').sum()),
              ratings_policy=RATINGS_POLICY,imaging_exclusions_applied=False,
              difference='raw win minus raw loss within each participant and partner',
              method='Pooled continuous age per decade, dataset and recorded sex; HC3 with within-person covariance retained.',
              tests='Holm over 3 partner age slopes; separately Holm over 3 paired slope differences; one 2-df joint slope-equality Wald test.',
              uncertainty='Pointwise 95% t intervals, not simultaneous bands.',
              limitations=['Exploratory cross-sectional associations, not causal aging.',
                           'Response-based exclusions and bounded ratings can affect associations.'],
              sources=[dict(path=str(f.resolve()),sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sources])
    (args.output_dir/'win-loss-gap-provenance.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps(meta,indent=2))
    print(tests.to_string(index=False))
    print('CHECK PASSED: partner gap figures and paired age-slope tests generated with primary behavioral exclusions.')


if __name__=='__main__':
    main()
