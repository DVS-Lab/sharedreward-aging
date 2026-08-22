import csv,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SCRIPT=ROOT/'code/convert_harmonized_events.py'
def rows(path):
 with path.open() as handle:return list(csv.DictReader(handle,delimiter='\t'))
class Events(unittest.TestCase):
 def test_ds003745_preserves_published_trial_timing_and_omits_blocks(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);src=d/'events.tsv';out=d/'out.tsv';src.write_text('onset\tduration\ttrial_type\n4.01635\t3.52807\tevent_computer_reward\n4.01635\t33.5\tblock_computer_reward\n40\t3.6\tmissed_trial\n');subprocess.run(['python3',str(SCRIPT),'--dataset','ds003745','--input',str(src),'--output',str(out)],check=True);r=rows(out);self.assertEqual([(x['onset'],x['duration'],x['trial_type']) for x in r],[('4.01635','3.52807','event_computer_reward'),('40','3.6','missed_trial')])
 def test_rf1_derives_decision_to_outcome_offset_and_miss(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);src=d/'events.tsv';out=d/'out.tsv';src.write_text('onset\tduration\ttrial_type\n1\t1.2\tfriend_face\n3\t1\tevent_friend_reward\n6\t2\tmissed_decision\n8.5\t1\tmissed_outcome\n');subprocess.run(['python3',str(SCRIPT),'--dataset','rf1','--input',str(src),'--output',str(out)],check=True);r=rows(out);self.assertEqual(r[0]['onset'],'1.000000');self.assertEqual(r[0]['duration'],'3.000000');self.assertEqual(r[1]['duration'],'3.500000');self.assertEqual(r[1]['trial_type'],'missed_trial')
 def test_rf1_partner_mismatch_fails(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);src=d/'events.tsv';out=d/'out.tsv';src.write_text('onset\tduration\ttrial_type\n1\t1\tfriend_face\n3\t1\tevent_stranger_reward\n');r=subprocess.run(['python3',str(SCRIPT),'--dataset','rf1','--input',str(src),'--output',str(out)],capture_output=True);self.assertNotEqual(r.returncode,0)
if __name__=='__main__':unittest.main()
