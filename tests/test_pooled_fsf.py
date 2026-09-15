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
    def test_active_templates_disable_per_ev_temporal_filtering(self):
        for path in ROOT.joinpath("templates").glob("*.fsf"):
            enabled = re.findall(
                r"^set fmri\(tempfilt_yn\d+\)\s+1$",
                path.read_text(),
                re.MULTILINE,
            )
            self.assertEqual(enabled, [], path.name)

    def test_activation_is_narrow_fulltrial_contract(self):
        text = MODULE.render(
            "act",
            MODULE.SOURCES["act"],
            ROOT / "templates/FULLTRIAL_CONTRAST_CANDIDATE.tsv",
        )
        self.assertEqual(setting(text, "smooth"), "0")
        self.assertEqual(setting(text, "featwatcher_yn"), "0")
        self.assertEqual(setting(text, "evs_orig"), "10")
        self.assertEqual(setting(text, "ncon_orig"), "22")
        self.assertEqual(setting(text, "tempfilt_yn7"), "0")
        self.assertEqual(setting(text, "convolve10"), "3")
        self.assertEqual(setting(text, "shape10"), "SHAPE_EV")
        self.assertEqual(setting(text, "custom1"), '"EVDIRevent_computer_punish.txt"')
        self.assertIsNone(setting(text, "evtitle11"))
        self.assertEqual(setting(text, "conname_real.21"), '"F-S (pun)"')
        self.assertEqual(setting(text, "conname_real.22"), '"F-C (pun)"')
        for contrast in range(1, 23):
            for neutral_ev in (7, 8, 9):
                self.assertEqual(setting(text, f"con_real{contrast}.{neutral_ev}"), "0")

    def test_ppi_uses_10_psych_phys_and_10_interactions(self):
        text = MODULE.render(
            "ppi",
            MODULE.SOURCES["ppi"],
            ROOT / "templates/FULLTRIAL_CONTRAST_CANDIDATE.tsv",
        )
        self.assertEqual(setting(text, "smooth"), "0")
        self.assertEqual(setting(text, "evs_orig"), "21")
        self.assertEqual(setting(text, "ncon_orig"), "23")
        self.assertEqual(setting(text, "evtitle11"), '"phys"')
        self.assertEqual(setting(text, "evtitle21"), '"miss"')
        self.assertIsNone(setting(text, "evtitle22"))
        self.assertEqual(setting(text, "con_real1.12"), "1")
        self.assertEqual(setting(text, "con_real23.11"), "1")
        for contrast in range(1, 23):
            for neutral_interaction in (18, 19, 20):
                self.assertEqual(
                    setting(text, f"con_real{contrast}.{neutral_interaction}"), "0"
                )


if __name__ == "__main__":
    unittest.main()
