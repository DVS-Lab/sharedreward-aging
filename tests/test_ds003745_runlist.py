import csv
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Ds003745Runlist(unittest.TestCase):
    def test_builds_deterministic_runlist_with_exclusions(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            participants = directory / "participants.tsv"
            output = directory / "runlist.tsv"
            participants.write_text(
                "participant_id\tage\tsex\tgroup\n"
                "sub-104\t20\tM\tcontrol\n"
                "sub-105\t21\tF\tcontrol\n"
                "sub-140\t68\tM\tcontrol\n"
            )
            result = subprocess.run(
                [
                    "python3",
                    str(ROOT / "code/build_ds003745_runlist.py"),
                    "--participants",
                    str(participants),
                    "--exclude-subject",
                    "sub-105",
                    "--output",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            with output.open(newline="") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual([row["subject"] for row in rows], ["104", "140"])
            self.assertIn("Runlist participants: 2", result.stdout)


if __name__ == "__main__":
    unittest.main()
