import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'code'))
from audit_l1_contrasts import audit
from render_pooled_fsf import SOURCES, candidate_contrasts, render


class ContrastAuditTest(unittest.TestCase):
    def fixture(self, directory, kind, empty=False):
        text = render(kind, SOURCES[kind], ROOT / 'templates/FULLTRIAL_CONTRAST_CANDIDATE.tsv')
        for i in (7, 8, 9):
            text = text.replace(f'SHAPE_EV{i}', '10' if empty and i == 8 else '3')
            text = text.replace(f'SHAPE_PPI{i+11}', '10' if empty and i == 8 else '4')
        (directory / 'design.fsf').write_text(text.replace('SHAPE_EV', '10'))
        weights = [w for _, w in candidate_contrasts(ROOT / 'templates/FULLTRIAL_CONTRAST_CANDIDATE.tsv')]
        c = np.array(weights) if kind == 'act' else np.array([[0.] * 11 + w for w in weights] + [[0.] * 10 + [1.] + [0.] * 10])
        x = np.eye(c.shape[1])
        if empty:
            x[:, 7] = 0
            if kind == 'ppi':
                x[:, 18] = 0
            c[7] = 0
        np.savetxt(directory / 'design.mat', x, header='/Matrix', comments='')
        np.savetxt(directory / 'design.con', c, header='/Matrix', comments='')

    def test_retained_ids_and_empty_neutral_reporting(self):
        for kind in ('act', 'ppi'):
            for empty in (False, True):
                with tempfile.TemporaryDirectory() as tmp:
                    d = Path(tmp)
                    self.fixture(d, kind, empty)
                    result = audit(d, kind)
                    self.assertEqual(result['ncontrasts'], 28 if kind == 'act' else 29)
                    self.assertEqual([r['cope'] for r in result['unsupported_neutral_contrasts']], [8, 20, 22] if empty else [])
                    self.assertEqual(result['fsl_zeroed_contrasts'], [8] if empty else [])

    def test_missing_switch_and_changed_weights_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            self.fixture(d, 'act')
            path = d / 'design.fsf'
            text = path.read_text()
            path.write_text(text.replace('set fmri(conmask1_1) 0', ''))
            with self.assertRaisesRegex(ValueError, 'conmask1_1'):
                audit(d, 'act')
            path.write_text(text.replace('set fmri(con_real10.1) -1', 'set fmri(con_real10.1) 1'))
            with self.assertRaisesRegex(ValueError, 'weights differ'):
                audit(d, 'act')
            path.write_text(text)
            c = np.loadtxt(d / 'design.con', skiprows=1)
            c[9, 0] = 1
            np.savetxt(d / 'design.con', c, header='/Matrix', comments='')
            with self.assertRaisesRegex(ValueError, 'design.con differs'):
                audit(d, 'act')

    def test_nonestimable_primary_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            self.fixture(d, 'act')
            x = np.eye(10)
            x[:, 0] = 0
            np.savetxt(d / 'design.mat', x, header='/Matrix', comments='')
            with self.assertRaisesRegex(ValueError, 'primary contrasts'):
                audit(d, 'act')
