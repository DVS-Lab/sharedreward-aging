import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "generate_fsl_confounds", ROOT / "code/generate_fsl_confounds.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FSLConfoundsTest(unittest.TestCase):
    def test_rf1_base_policy_and_zero_fill(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "confounds.tsv"
            fields = list(MODULE.BASE_COLUMNS) + ["cosine00", "non_steady_state_outlier00", "junk"]
            with path.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
                writer.writeheader()
                writer.writerow({field: ("n/a" if field == "framewise_displacement" else "1") for field in fields})
                writer.writerow({field: "2" for field in fields})
            selected, matrix = MODULE.build(path)
            self.assertEqual(selected, fields[:-1])
            self.assertEqual(len(matrix), 2)
            self.assertEqual(matrix[0][selected.index("framewise_displacement")], 0.0)

    def test_missing_base_column_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "confounds.tsv"
            path.write_text("trans_x\n0\n")
            with self.assertRaisesRegex(ValueError, "missing required base columns"):
                MODULE.build(path)


if __name__ == "__main__":
    unittest.main()
