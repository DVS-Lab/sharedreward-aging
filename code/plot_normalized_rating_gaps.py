#!/usr/bin/env python3
"""Slide-ready normalized win-loss age curves and direct paired slope tests."""
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

from analyze_raw_ratings import ROOT, KEYS, CELLS, age_design, demographics, load_ratings
from audit_ratings_qc import RATINGS_POLICY
from plot_normalized_loss_ratings import transform
from plot_rating_gaps import GAPS, PARTNERS, COLORS, gap_analysis


def difference_predictions(data, ages):
    """Friend-minus-stranger gap, with paired HC3 uncertainty and adjusted dots."""
    x=age_design(data)
    y=data[CELLS].to_numpy(float)@(GAPS[0]-GAPS[1])
    bread=np.linalg.inv(x.T@x);beta=bread@x.T@y
    residual=y-x@beta;h=np.sum((x@bread)*x,axis=1)
    g=np.tile(x.mean(axis=0),(len(ages),1))
    g[:,1]=(np.asarray(ages)-data.age.mean())/10
    mean=g@beta
    se=np.sqrt((g@bread@x.T)**2 @ (residual/(1-h))**2)
    critical=stats.t.ppf(.975,len(data)-x.shape[1])
    # Hold dataset/sex at the same empirical mix as the marginal fitted curve.
    adjusted=y-(x[:,2:]-x[:,2:].mean(axis=0))@beta[2:]
    return mean,mean-critical*se,mean+critical*se,adjusted,beta[1]


def plot(data, output):
    normalized=transform(data,'person_zscored')
    ages=np.linspace(data.age.min(),data.age.max(),180)
    mean,lo,hi,tests=gap_analysis(normalized,ages)
    diff,dl,du,dots,slope=difference_predictions(normalized,ages)
    np.testing.assert_allclose(diff,mean[:,0]-mean[:,1],atol=1e-12)
    test=tests[tests.comparison.eq('Friend minus Stranger')].iloc[0]
    np.testing.assert_allclose(slope,test.points_per_decade,atol=1e-12)
    fig,(ax,contrast)=plt.subplots(1,2,figsize=(14,7.3),gridspec_kw={'width_ratios':[1.08,1]})
    fig.subplots_adjust(left=.075,right=.975,top=.76,bottom=.25,wspace=.30)
    for j,(name,color,style) in enumerate(zip(PARTNERS,COLORS,['-','--','-.'])):
        ax.fill_between(ages,lo[:,j],hi[:,j],color=color,alpha=.16,linewidth=0)
        ax.plot(ages,mean[:,j],color=color,lw=3,linestyle=style,label=name)
    ax.set(ylabel='Win − loss (within-person SD units)',ylim=(0,3))
    ax.set_yticks([0,1,2,3]);ax.legend(frameon=False,fontsize=12,loc='lower left')
    ax.set_title('Win–loss separation by partner',loc='left',fontsize=15,fontweight='bold',pad=15)
    contrast.scatter(data.age,dots,s=22,color='#68747D',alpha=.28,edgecolors='none',zorder=2)
    contrast.axhline(0,color='#8D969D',lw=.8,ls=':',zorder=1)
    contrast.fill_between(ages,dl,du,color=COLORS[0],alpha=.20,linewidth=0,zorder=3)
    contrast.plot(ages,diff,color=COLORS[0],lw=3,zorder=4)
    contrast.set_ylabel('Friend gap − stranger gap\n(within-person SD units)')
    contrast.set_ylim(min(dots.min(),dl.min())-.12,max(dots.max(),du.max())+.12)
    contrast.set_title('Direct friend–stranger comparison',loc='left',fontsize=15,fontweight='bold',pad=15)
    for panel in (ax,contrast):
        panel.set(xlabel='Age (years)',xlim=(ages.min(),ages.max()))
        panel.set_xticks([20,40,60,80]);panel.tick_params(labelsize=12)
        panel.xaxis.label.set_size(13);panel.yaxis.label.set_size(13)
        panel.spines[['top','right']].set_visible(False)
        panel.grid(axis='y',color='#E7EBEE',lw=.8);panel.set_axisbelow(True)
    fig.suptitle('Post-task ratings: normalized win–loss differences',fontsize=23,y=.97)
    fig.text(.5,.89,f'N = {len(data)}  ·  Behavioral exclusions applied  ·  Adjusted for dataset and recorded sex',
             ha='center',fontsize=13,color='#4F5C67')
    fig.text(.075,.16,f'Friend − stranger age slope: {slope:+.3f} SD/decade  '
             f'(95% CI {test.ci95_low:+.3f} to {test.ci95_high:+.3f}); '
             f'uncorrected p = {test.p:.3f}, Holm p = {test.p_holm_family:.3f}.',fontsize=12)
    fig.text(.075,.10,'Each person’s six ratings are z-scored together before computing win − loss. Shading: pointwise HC3 95% confidence intervals.',fontsize=10.5)
    fig.text(.075,.055,'Right-hand dots are participant contrasts adjusted to the sample’s dataset/sex mix; no jitter. Holm correction covers three paired slope tests.',fontsize=10.5)
    for extension in ('png','svg'):
        fig.savefig(output/f'normalized-win-loss-age.{extension}',dpi=200)
    plt.close(fig)
    tests=tests.rename(columns={'points_per_decade':'within_person_SD_per_decade'})
    tests.to_csv(output/'normalized-win-loss-age-tests.tsv',sep='\t',index=False)
    rows=[]
    for j,name in enumerate(PARTNERS):
        rows.extend(dict(comparison=name,age=a,adjusted_mean=mean[i,j],ci95_low=lo[i,j],ci95_high=hi[i,j]) for i,a in enumerate(ages))
    rows.extend(dict(comparison='Friend minus Stranger',age=a,adjusted_mean=diff[i],ci95_low=dl[i],ci95_high=du[i]) for i,a in enumerate(ages))
    pd.DataFrame(rows).to_csv(output/'normalized-win-loss-age-predictions.tsv',sep='\t',index=False)
    return tests


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',type=Path,default=ROOT/'qc/ratings-normalized')
    args=p.parse_args()
    sources=[ROOT/'logs/records/ratings-qc-subject-level.tsv',ROOT/'logs/records/analysis-subject-dispositions.tsv',
             ROOT.parent/'rf1-sra-linux2/bids/participants.tsv',ROOT/'participants-srndna.tsv']
    data=load_ratings(*sources[:2]).merge(pd.concat([demographics(sources[2],'rf1'),demographics(sources[3],'ds003745')]),
                                       on=KEYS,how='left',validate='one_to_one').sort_values(KEYS)
    if not (data.age.between(18,110)&data.sex.isin(['F','M','O'])).all():
        raise ValueError('Complete demographics required; no silent sample change')
    args.output_dir.mkdir(parents=True,exist_ok=True)
    tests=plot(data,args.output_dir)
    sources += [Path(__file__),ROOT/'code/analyze_raw_ratings.py',ROOT/'code/audit_ratings_qc.py',
                ROOT/'code/plot_normalized_loss_ratings.py',ROOT/'code/plot_rating_gaps.py']
    meta=dict(n=len(data),sample_by_dataset=data.groupby('dataset').size().to_dict(),ratings_policy=RATINGS_POLICY,
        normalization='Each participant: (rating - mean of six partner x outcome cells) / sample SD of six cells (ddof=1). Normalize once, then compute each partner win-minus-loss gap. No second normalization of gaps.',
        model='Intercept + continuous centered age per decade + dataset + recorded sex (F reference, M/O dummy offsets); same participants in every outcome.',
        inference='Paired wide OLS HC3 covariance, pointwise t CIs; direct differences of slopes. One 2-df joint slope-equality Wald test. Raw p and separate Holm families for three slopes and three paired differences.',
        right_panel='(Friend win - Friend loss) - (Stranger win - Stranger loss), in within-person SD units. Dots remove fitted dataset/sex contributions relative to empirical means, preserving age effect and residual.',
        historical_slide='Current adjusted N318 analysis; not a replication of the supplied historical N205 correlation or its unspecified normalization.',
        primary_raw_model_changed=False,
        sources=[dict(path=str(f.resolve()),sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sources])
    (args.output_dir/'normalized-win-loss-provenance.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps(meta,indent=2));print(tests.to_string(index=False))
    print('CHECK PASSED: normalized partner gaps and paired age-slope contrasts generated.')


if __name__=='__main__':
    main()
