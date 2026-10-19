"""The provisional exception cannot waive BOLD, model-input, or later changes."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
import audit_group_readiness as audit
from model_provenance import CONTRACT, STAMP

POLICY = Path(__file__).resolve().parents[1] / "resources/age-mask-allowance-20261018.json"


class AllowanceTests(unittest.TestCase):
    def test_exact_policy_and_no_precision_loss(self):
        entries = audit.load_mask_allowance(POLICY)
        self.assertEqual(len(entries), 10)
        first = next(iter(entries.values()))
        self.assertEqual(first["current"]["mtime_ns"], 1792209915915993310)
        self.assertEqual(audit.load_mask_allowance(None), {})

    def test_scope_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            data = json.loads(POLICY.read_text())
            data["changes"][0]["recorded"]["path"] = "/some/bold.nii.gz"
            data["changes"][0]["current"]["path"] = "/some/bold.nii.gz"
            path = Path(temp) / "policy.json"
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "outside reviewed scope"):
                audit.load_mask_allowance(path)

    def test_opt_in_records_warning_and_preserves_stamp(self):
        entries = audit.load_mask_allowance(POLICY)
        entry = next(iter(entries.values()))
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            stamp = directory / STAMP
            stamp.write_text(json.dumps(dict(contract=CONTRACT, level="l1", type="act",
                inputs=[dict(path="input", sha256="original")], images=[entry["recorded"]], parents=[])))
            before = stamp.read_bytes()
            def current(path, image=False):
                return entry["current"] if image else dict(path="input", sha256="original")
            warnings = []
            with patch.object(audit, "fingerprint", side_effect=current):
                with self.assertRaisesRegex(ValueError, "changed image"):
                    audit.check_stamp(directory, "l1", "act", [10])
                audit.check_stamp(directory, "l1", "act", [10], mask_allowance=entries,
                                  allowed_mask=entry["recorded"]["path"], warnings=warnings)
                # Even an approved fingerprint cannot be waived in the BOLD role.
                with self.assertRaisesRegex(ValueError, "changed image"):
                    audit.check_stamp(directory, "l1", "act", [10], mask_allowance=entries,
                                      allowed_mask="different-mask.nii.gz", warnings=[])
            self.assertEqual(len(warnings), 1)
            self.assertEqual(warnings[0]["current"], entry["current"])
            self.assertEqual(stamp.read_bytes(), before)
            changed = copy.deepcopy(entry["current"])
            changed["mtime_ns"] += 1
            with patch.object(audit, "fingerprint", side_effect=lambda p, image=False:
                              changed if image else dict(path="input", sha256="original")):
                with self.assertRaisesRegex(ValueError, "changed image"):
                    audit.check_stamp(directory, "l1", "act", [10], mask_allowance=entries,
                                      allowed_mask=entry["recorded"]["path"], warnings=[])
            with patch.object(audit, "fingerprint", return_value=dict(path="input", sha256="changed")):
                with self.assertRaisesRegex(ValueError, "changed model input"):
                    audit.check_stamp(directory, "l1", "act", [10], mask_allowance=entries,
                                      allowed_mask=entry["recorded"]["path"], warnings=[])


if __name__ == "__main__":
    unittest.main()
