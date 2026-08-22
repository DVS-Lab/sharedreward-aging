#!/usr/bin/env python3
"""Create model-specific full-trial Shared Reward events without editing BIDS."""
from __future__ import annotations
import argparse,csv
from pathlib import Path

PARTNER_DECISION={'computer_non-face':'computer','friend_face':'friend','stranger_face':'stranger'}
VALID_OUTCOMES={f'event_{p}_{o}' for p in ('computer','friend','stranger') for o in ('punish','neutral','reward')}
def num(v,label):
 try:return float(v)
 except ValueError:raise ValueError(f'invalid {label}: {v!r}')
def read(path):
 with path.open(newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w',newline='') as h:
  w=csv.DictWriter(h,fieldnames=['onset','duration','trial_type','source_representation'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def ds003745(rows):
 out=[]
 for r in rows:
  t=r['trial_type']
  if t in VALID_OUTCOMES or t=='missed_trial':
   duration=num(r['duration'],'duration');num(r['onset'],'onset')
   if duration<0:raise ValueError('negative duration')
   out.append({'onset':r['onset'],'duration':r['duration'],'trial_type':t,'source_representation':'published_full_trial'})
 return sorted(out,key=lambda r:float(r['onset']))
def rf1(rows):
 ordered=sorted(rows,key=lambda r:(num(r['onset'],'onset'),0 if r['trial_type'] in PARTNER_DECISION or r['trial_type']=='missed_decision' else 1))
 out=[];pending=None
 for r in ordered:
  t=r['trial_type'];on=num(r['onset'],'onset');dur=num(r['duration'],'duration');end=on+dur
  if dur<0:raise ValueError(f'negative duration for {t}')
  if t in PARTNER_DECISION or t=='missed_decision':
   if pending is not None:raise ValueError(f'unpaired decision before {t} at {on}')
   pending=(t,on)
  elif t in VALID_OUTCOMES or t=='missed_outcome':
   if pending is None:raise ValueError(f'outcome without decision: {t} at {on}')
   decision,don=pending
   if t=='missed_outcome':
    if decision!='missed_decision':raise ValueError('missed_outcome is not paired with missed_decision')
    label='missed_trial'
   else:
    partner=t.split('_')[1]
    if PARTNER_DECISION.get(decision)!=partner:raise ValueError(f'partner mismatch: {decision} then {t}')
    label=t
   if on<don:raise ValueError(f'invalid phase order: {decision} then {t}')
   out.append({'onset':f'{don:.6f}','duration':f'{end-don:.6f}','trial_type':label,'source_representation':'derived_decision_to_outcome_offset'})
   pending=None
 if pending is not None:raise ValueError(f'unpaired final decision: {pending[0]}')
 return out
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--dataset',required=True,choices=('rf1','ds003745'));p.add_argument('--input',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();rows=read(a.input);required={'onset','duration','trial_type'}
 if not rows or not required.issubset(rows[0]):p.error('input must contain onset, duration, trial_type')
 out=ds003745(rows) if a.dataset=='ds003745' else rf1(rows)
 if not out:p.error('no model-specific full-trial rows generated')
 write(a.output,out);print(f'Wrote {len(out)} {a.dataset} full-trial rows: {a.output}');return 0
if __name__=='__main__':raise SystemExit(main())
