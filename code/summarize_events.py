#!/usr/bin/env python3
"""Write per-run event parity/QC summaries for canonical or harmonized TSVs."""
import argparse,csv
from collections import Counter
from pathlib import Path
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--dataset',required=True);p.add_argument('--input',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();rows=list(csv.DictReader(a.input.open(),delimiter='\t'));types=Counter(r['trial_type'] for r in rows);timings=[(float(r['onset']),float(r['duration'])) for r in rows];bad=sum(d<0 for _,d in timings);out={'dataset':a.dataset,'file':str(a.input),'n_rows':len(rows),'n_trials':sum(v for k,v in types.items() if k.startswith('event_') or k=='missed_trial'),'n_decision_events':sum(v for k,v in types.items() if k in ('computer_non-face','friend_face','stranger_face')),'n_outcome_events':sum(v for k,v in types.items() if k.startswith('event_')),'n_missed_decision':types['missed_decision'],'n_missed_outcome':types['missed_outcome'],'n_missed_trial':types['missed_trial'],'computer':sum(v for k,v in types.items() if 'computer' in k),'friend':sum(v for k,v in types.items() if 'friend' in k),'stranger':sum(v for k,v in types.items() if 'stranger' in k),'reward':sum(v for k,v in types.items() if k.endswith('_reward')),'neutral':sum(v for k,v in types.items() if k.endswith('_neutral')),'punish':sum(v for k,v in types.items() if k.endswith('_punish')),'first_onset':min((x for x,_ in timings),default=''),'last_offset':max((x+d for x,d in timings),default=''),'negative_durations':bad}
 a.output.parent.mkdir(parents=True,exist_ok=True);exists=a.output.exists() and a.output.stat().st_size>0
 with a.output.open('a',newline='') as h:w=csv.DictWriter(h,fieldnames=out.keys(),delimiter='\t',lineterminator='\n');(None if exists else w.writeheader());w.writerow(out)
 print(out);return 0 if bad==0 else 1
if __name__=='__main__':raise SystemExit(main())
