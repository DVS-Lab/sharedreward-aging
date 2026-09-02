import importlib.util
import re
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "render_pooled_fsf", ROOT / "code/render_pooled_fsf.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def setting(text, key):
    match = re.search(rf"^set fmri\({re.escape(key)}\)\s+(.+)$", text, re.MULTILINE)
    return match.group(1) if match else None


class PooledFSFTest(unittest.TestCase):
    def test_activation_is_narrow_fulltrial_contract(self):
        text = MODULE.render(
            "act",
            MODULE.SOURCES["act"],
            ROOT / "templates/FULLTRIAL_CONTRAST_CANDIDATE.tsv",
        )
        self.assertEqual(setting(text, "smooth"), "0")
        self.assertEqual(setting(text, "featwatcher_yn"), "0")
        self.assertEqual(setting(text, "evs_orig"), "10")
        self.assertEqual(setting(text, "ncon_orig"), "28")
        self.assertEqual(setting(text, "convolve10"), "3")
        self.assertEqual(setting(text, "shape10"), "SHAPE_EV")
        self.assertIsNone(setting(text, "evtitle11"))
        self.assertEqual(setting(text, "conname_real.27"), '"F-S (pun)"')

    def test_ppi_uses_10_psych_phys_and_10_interactions(self):
        text = MODULE.render(
            "ppi",
            MODULE.SOURCES["ppi"],
            ROOT / "templates/FULLTRIAL_CONTRAST_CANDIDATE.tsv",
        )
        self.assertEqual(setting(text, "smooth"), "0")
        self.assertEqual(setting(text, "evs_orig"), "21")
        self.assertEqual(setting(text, "ncon_orig"), "29")
        self.assertEqual(setting(text, "evtitle11"), '"phys"')
        self.assertEqual(setting(text, "evtitle21"), '"miss"')
        self.assertIsNone(setting(text, "evtitle22"))
        self.assertEqual(setting(text, "con_real1.12"), "1")
        self.assertEqual(setting(text, "con_real29.11"), "1")


if __name__ == "__main__":
    unittest.main()
