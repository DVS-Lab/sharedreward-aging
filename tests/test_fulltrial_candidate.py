import csv,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Candidate(unittest.TestCase):
 def test_contract_is_full_trial_only(self):
  with (ROOT/'templates/FULLTRIAL_EV_ORDER.tsv').open() as h:evs=list(csv.DictReader(h,delimiter='\t'))
  self.assertEqual(len(evs),10);self.assertEqual(evs[-1]['trial_type'],'missed_trial');self.assertNotIn('friend_face',{r['trial_type'] for r in evs})
  with (ROOT/'templates/FULLTRIAL_CONTRAST_CANDIDATE.tsv').open() as h:cons=list(csv.DictReader(h,delimiter='\t'))
  self.assertEqual(len(cons),22)
  self.assertEqual([int(row['candidate_cope']) for row in cons],list(range(1,23)))
  for row in cons:
   weights=[float(value) for value in row['weights_ev1_to_ev10'].split(',')]
   self.assertEqual(len(weights),10)
   self.assertEqual(weights[6:10],[0,0,0,0],row['contrast_name'])
if __name__=='__main__':unittest.main()
