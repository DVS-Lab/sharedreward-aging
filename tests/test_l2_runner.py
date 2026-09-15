import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class L2RunnerTest(unittest.TestCase):
    def test_manifest_separates_fixed_effects_from_one_run_passthrough(self):
        with tempfile.TemporaryDirectory() as temporary:
            manifest = Path(temporary) / "l2.tsv"
            manifest.write_text(
                "dataset\tsubject\tsession\tn_runs\truns\tsubject_level_strategy\n"
                "rf1\t10001\t01\t2\t1,2\tfixed_effects\n"
                "ds003745\t104\t\t1\t1\tl1_passthrough\n"
            )
            result = subprocess.run(
                ["python3", str(ROOT / "code/read_l2_manifest.py"), str(manifest)],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.stdout.strip(), "rf1|10001|01|1|2")
            self.assertIn("PASSTHROUGH\tds003745\t104\tnone\t1", result.stderr)

    def test_runtime_transform_preserves_fixed_effects_and_expands_copes(self):
        with tempfile.TemporaryDirectory() as temporary:
            temporary = Path(temporary)
            for kind, expected in (("act", 28), ("ppi", 29)):
                output = temporary / f"{kind}.fsf"
                subprocess.run(
                    [
                        "python3",
                        str(ROOT / "code/render_pooled_l2_fsf.py"),
                        "--type",
                        kind,
                        "--output",
                        str(output),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                text = output.read_text()
                self.assertIn("set fmri(mixed_yn) 3", text)
                self.assertIn("set fmri(smooth) 0", text)
                self.assertIn(f"set fmri(ncopeinputs) {expected}", text)
                self.assertIn(f"set fmri(copeinput.{expected}) 1", text)
                self.assertNotIn(f"set fmri(copeinput.{expected + 1})", text)


if __name__ == "__main__":
    unittest.main()
