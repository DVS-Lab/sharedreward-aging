#!/usr/bin/env python3
"""Summarize a consolidated Phase-0 run-level harmonization TSV."""
from __future__ import annotations
import argparse,csv,statistics
from collections import defaultdict
from pathlib import Path
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();rows=list(csv.DictReader(a.input.open(),delimiter='\t'));groups=defaultdict(list)
 for r in rows:groups[r.get('dataset','unknown')].append(r)
 lines=['# Phase 0 harmonization characterization','',f'Run rows: {len(rows)}','']
 for dataset,rs in sorted(groups.items()):
  lines.extend([f'## {dataset}','',f'Runs: {len(rs)}',''])
  for field in ('pre_resample_smoothness','post_resample_preblur_smoothness','post_blur_smoothness','tsnr_pre_resample','tsnr_post_resample','tsnr_post_blur','mean_fd','coverage_pct'):
   vals=[float(r[field]) for r in rs if r.get(field) not in ('',None,'n/a','NA')]
   if vals:lines.append(f'- {field}: median {statistics.median(vals):.4f}; range {min(vals):.4f}–{max(vals):.4f}; n={len(vals)}')
  warnings=[r.get('warnings','') for r in rs if r.get('warnings','')];lines.append(f'- warning rows: {len(warnings)}');lines.append('')
 lines.extend(['## Gate status','','Production target approved 2026-08-23: 6 mm total classic FWHM. Require complete achieved-smoothness QC before FEAT; ACF remains diagnostic here and should be estimated from model residuals for cluster-based inference.',''])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text('\n'.join(lines));print(f'Report: {a.output}');return 0
if __name__=='__main__':raise SystemExit(main())
