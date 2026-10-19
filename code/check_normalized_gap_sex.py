#!/usr/bin/env python3
"""Same-sample normalized win-loss slope comparisons with/without recorded sex."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from analyze_raw_ratings import ROOT, KEYS, CELLS, age_design, demographics, load_ratings
from audit_ratings_qc import RATINGS_POLICY
from plot_normalized_loss_ratings import transform
from plot_rating_gaps import GAPS, gap_analysis


def main():
    sources=[ROOT/'logs/records/ratings-qc-subject-level.tsv', ROOT/'logs/records/analysis-subject-dispositions.tsv',
             ROOT.parent/'rf1-sra-linux2/bids/participants.tsv', ROOT/'participants-srndna.tsv']
    data=load_ratings(*sources[:2]).merge(pd.concat([demographics(sources[2],'rf1'),demographics(sources[3],'ds003745')]),
                                       on=KEYS,how='left',validate='one_to_one').sort_values(KEYS)
    if not (data.age.between(18,110)&data.sex.isin(['F','M','O'])).all():
        raise ValueError('Complete demographics required; no silent sample change')
    normalized=transform(data,'person_zscored')
    tables=[]
    for sex in (True,False):
        _,_,_,table=gap_analysis(normalized,[data.age.mean()],adjust_sex=sex)
        table.insert(0,'sex_adjusted',sex)
        # Verify against independent direct regression on the paired difference.
        x=age_design(normalized,sex);a=np.linalg.inv(x.T@x)@x.T
        y=normalized[CELLS].to_numpy()@(GAPS[0]-GAPS[1])
        beta=a@y;residual=y-x@beta;h=np.diag(x@a)
        cov=(a*(residual/(1-h)))@(a*(residual/(1-h))).T
        row=table[table.comparison.eq('Friend minus Stranger')].iloc[0]
        np.testing.assert_allclose(row.points_per_decade,beta[1],atol=1e-12)
        np.testing.assert_allclose(row.se_hc3**2,cov[1,1],atol=1e-12)
        tables.append(table)
    result=pd.concat(tables,ignore_index=True).rename(columns={'points_per_decade':'within_person_SD_per_decade'})
    output=ROOT/'qc/ratings-normalized';output.mkdir(parents=True,exist_ok=True)
    result.to_csv(output/'normalized-gap-sex-sensitivity.tsv',sep='\t',index=False)
    sources += [Path(__file__),ROOT/'code/analyze_raw_ratings.py',ROOT/'code/audit_ratings_qc.py',
                ROOT/'code/plot_normalized_loss_ratings.py',ROOT/'code/plot_rating_gaps.py']
    meta=dict(n=len(data),sample_by_dataset=data.groupby('dataset').size().to_dict(),ratings_policy=RATINGS_POLICY,
        normalization='Same six-cell within-participant z-scores (sample SD, ddof=1) in both fits, computed after raw-rating exclusions.',
        model='Intercept, continuous centered age/10, RF1 dataset dummy; with/without M/O recorded-sex offsets (F reference).',
        inference='Paired HC3 t tests and 95% CIs. Raw p and Holm over three paired comparisons within each specification; separate Holm family for three individual partner gap slopes.',
        primary_model_changed=False,
        sources=[dict(path=str(f.resolve()),sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sources])
    (output/'normalized-gap-sex-provenance.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps(meta,indent=2));print(result.to_string(index=False))
    print('CHECK PASSED: both normalized gap models use the same sample and match direct difference-score regressions.')


if __name__=='__main__':
    main()
