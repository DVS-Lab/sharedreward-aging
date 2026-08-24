import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def write_ratings(path, values):
    path.write_text(
        "trial,partner,trait,ran,order,response\n"
        + "".join(
            f"{index},{partner},{trait},1,{index},{response}\n"
            for index, (partner, trait, response) in enumerate(values, 1)
        )
    )


def write_original_ratings(path, values):
    path.write_text(
        "TrialNumber,Partner,Trait,ran,order,Rating\n"
        + "".join(
            f"{index},{partner},{trait},1,{index},{rating}\n"
            for index, (partner, trait, rating) in enumerate(values, 1)
        )
    )


class RatingsQc(unittest.TestCase):
    def test_original_schema_and_missing_subject_are_audited(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            original = directory / "original.csv"
            values = [
                (1, 0, 3), (1, 1, -3), (2, 0, 2),
                (2, 1, -2), (3, 0, 4), (3, 1, -4),
            ]
            write_original_ratings(original, values)
            manifest = directory / "manifest.tsv"
            manifest.write_text(
                "dataset\tsubject\tratings_file\tsource_resolution\t"
                "candidate_count\tcandidate_files\n"
                f"rf1\t100\t{original}\tunique\t1\t{original}\n"
                "rf1\t101\t\tmissing\t0\t\n"
            )
            output = directory / "ratings.tsv"
            missing = directory / "missing.tsv"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "code/audit_ratings_qc.py"),
                    "--manifest", str(manifest),
                    "--output", str(output),
                    "--missing-output", str(missing),
                    "--fail-on-incomplete",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with output.open(newline="") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual(rows[0]["exclude_subject"], "false")
            self.assertEqual(rows[1]["exclude_subject"], "true")
            self.assertEqual(rows[1]["exclusion_reason"], "missing_ratings_file")

    def test_repeated_header_selects_validated_final_block(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            ratings = directory / "pre-post.csv"
            pre = [
                (1, 0, -3), (1, 1, 0), (2, 0, 0),
                (2, 1, 0), (3, 0, 0), (3, 1, 0),
            ]
            post = [
                (1, 0, 5), (1, 1, -5), (2, 0, 4),
                (2, 1, -4), (3, 0, 3), (3, 1, -3),
            ]
            header = "TrialNumber,Partner,Trait,ran,order,Rating\n"
            body = lambda values: "".join(
                f"{i},{p},{t},1,{i},{v}\n"
                for i, (p, t, v) in enumerate(values, 1)
            )
            ratings.write_text(header + body(pre) + header + body(post))
            manifest = directory / "manifest.tsv"
            manifest.write_text(
                "dataset\tsubject\tratings_file\n"
                f"rf1\t100\t{ratings}\n"
            )
            output = directory / "ratings.tsv"
            missing = directory / "missing.tsv"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "code/audit_ratings_qc.py"),
                    "--manifest", str(manifest),
                    "--output", str(output),
                    "--missing-output", str(missing),
                    "--fail-on-incomplete",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with output.open(newline="") as handle:
                row = next(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual(row["n_rating_blocks"], "2")
            self.assertEqual(row["selected_rating_block"], "2")
            self.assertEqual(row["partner_1_trait_0_mean"], "5.0")
            self.assertEqual(row["review_flags"], "selected_last_complete_block:2_of_2")
    def test_equality_is_allowed_but_loss_greater_than_win_is_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            equal = directory / "equal.csv"
            loss_greater = directory / "loss-greater.csv"
            incomplete = directory / "incomplete.csv"
            write_ratings(
                equal,
                [
                    (1, 0, 1),
                    (1, 1, 2),
                    (2, 0, 2),
                    (2, 1, 2),
                    (3, 0, 3),
                    (3, 1, 2),
                ],
            )
            write_ratings(
                loss_greater,
                [
                    (1, 0, 1),
                    (1, 1, 2),
                    (2, 0, 1),
                    (2, 1, 2),
                    (3, 0, 1),
                    (3, 1, 2),
                ],
            )
            write_ratings(
                incomplete,
                [(1, 0, 1), (1, 1, 2), (2, 0, 1), (2, 1, 2), (3, 0, 1)],
            )
            manifest = directory / "manifest.tsv"
            manifest.write_text(
                "dataset\tsubject\tratings_file\n"
                f"rf1\t100\t{equal}\n"
                f"rf1\t101\t{loss_greater}\n"
                f"rf1\t102\t{incomplete}\n"
            )
            output = directory / "ratings.tsv"
            missing = directory / "missing.tsv"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "code/audit_ratings_qc.py"),
                    "--manifest",
                    str(manifest),
                    "--output",
                    str(output),
                    "--missing-output",
                    str(missing),
                    "--fail-on-incomplete",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            with output.open(newline="") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual(rows[0]["win_sum"], rows[0]["loss_sum"])
            self.assertEqual(rows[0]["exclude_subject"], "false")
            self.assertEqual(rows[1]["exclude_subject"], "true")
            self.assertEqual(
                rows[1]["exclusion_reason"], "loss_sum_greater_than_win_sum"
            )
            with missing.open(newline="") as handle:
                failures = list(csv.DictReader(handle, delimiter="\t"))
            self.assertIn("missing expected cells", failures[0]["problems"])


if __name__ == "__main__":
    unittest.main()
