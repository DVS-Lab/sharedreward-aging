import csv
import importlib.util
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_characterization_manifest", ROOT / "code/build_characterization_manifest.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CharacterizationInventoryTest(unittest.TestCase):
    def test_rf1_is_pinned_to_complete_sharedreward_session_01_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_qc = root / "run_qc.tsv"
            fields = ("subject", "session", "task", "run", "qc_complete")
            with run_qc.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
                writer.writeheader()
                writer.writerows(
                    [
                        {"subject": "100", "session": "01", "task": "sharedreward", "run": "1", "qc_complete": "TRUE"},
                        {"subject": "100", "session": "02", "task": "sharedreward", "run": "1", "qc_complete": "TRUE"},
                        {"subject": "100", "session": "01", "task": "trust", "run": "1", "qc_complete": "TRUE"},
                        {"subject": "101", "session": "01", "task": "sharedreward", "run": "2", "qc_complete": "FALSE"},
                    ]
                )
            args = Namespace(
                rf1_run_qc=run_qc,
                rf1_fmriprep_root=root / "fmriprep",
                rf1_confounds_root=root / "confounds",
            )
            captured = []

            def capture(ready, missing, identifiers, paths):
                captured.append((identifiers, paths))

            with patch.object(MODULE, "add_row", side_effect=capture):
                MODULE.rf1_rows(args, [], [])
            self.assertEqual(len(captured), 1)
            identifiers, paths = captured[0]
            self.assertEqual(identifiers["subject"], "100")
            self.assertEqual(identifiers["session"], "01")
            self.assertIn("ses-01", str(paths["input_bold"]))


if __name__ == "__main__":
    unittest.main()
