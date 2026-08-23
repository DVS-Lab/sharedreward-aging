import csv
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FmriprepAudit(unittest.TestCase):
    def test_reports_complete_and_incomplete_participants(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            participants = directory / "participants.tsv"
            derivatives = directory / "fmriprep"
            audit = directory / "audit.tsv"
            retry = directory / "retry.tsv"
            participants.write_text(
                "participant_id\tage\tsex\tgroup\n"
                "sub-104\t20\tM\tcontrol\n"
                "sub-105\t21\tF\tcontrol\n"
            )
            (derivatives / "sub-104/func").mkdir(parents=True)
            (derivatives / "sub-104.html").write_text("report")
            for run in ("01", "02"):
                prefix = f"sub-104_task-sharedreward_run-{run}"
                for suffix in (
                    "space-MNI152NLin6Asym_desc-preproc_bold.nii.gz",
                    "space-MNI152NLin6Asym_desc-brain_mask.nii.gz",
                    "desc-confounds_timeseries.tsv",
                ):
                    (derivatives / "sub-104/func" / f"{prefix}_{suffix}").write_text("x")

            result = subprocess.run(
                [
                    "python3",
                    str(ROOT / "code/audit_fmriprep_ds003745.py"),
                    "--participants",
                    str(participants),
                    "--fmriprep-root",
                    str(derivatives),
                    "--output",
                    str(audit),
                    "--retry-manifest",
                    str(retry),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            with audit.open(newline="") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual([row["status"] for row in rows], ["complete", "incomplete"])
            with retry.open(newline="") as handle:
                retries = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual([row["subject"] for row in retries], ["105"])
            self.assertIn("Complete participants: 1", result.stdout)
            self.assertIn("Incomplete participants: 1", result.stdout)


if __name__ == "__main__":
    unittest.main()
