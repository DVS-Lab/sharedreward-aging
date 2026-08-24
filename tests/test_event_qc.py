import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class EventQc(unittest.TestCase):
    def test_strictly_more_than_25pct_excludes_run_not_subject_with_usable_run(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            target = directory / "target.tsv"
            rows = []
            for run, missed in (("01", 1), ("02", 2)):
                source = (
                    directory
                    / "sub-104"
                    / "func"
                    / f"sub-104_task-sharedreward_run-{run}_events.tsv"
                )
                source.parent.mkdir(parents=True, exist_ok=True)
                events = [
                    ("1", "3.5", "event_computer_reward"),
                    ("5", "3.5", "event_friend_reward"),
                    ("9", "3.5", "missed_trial"),
                    ("13", "3.5", "missed_trial" if missed == 2 else "event_stranger_reward"),
                ]
                source.write_text(
                    "onset\tduration\ttrial_type\n"
                    + "".join("\t".join(event) + "\n" for event in events)
                )
                rows.append((run, source))
            target.write_text(
                "dataset\tsubject\tsession\trun\n"
                + "".join(f"ds003745\t104\t\t{run}\n" for run, _ in rows)
            )
            manifest = directory / "manifest.tsv"
            missing_build = directory / "missing-build.tsv"
            build = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "code/build_event_qc_manifest.py"),
                    "--target-manifest",
                    str(target),
                    "--ds003745-root",
                    str(directory),
                    "--event-root",
                    str(directory / "harmonized"),
                    "--qc-root",
                    str(directory / "qc"),
                    "--output",
                    str(manifest),
                    "--missing-output",
                    str(missing_build),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            batch = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "code/run_event_qc_batch.py"),
                    "--manifest",
                    str(manifest),
                    "--jobs",
                    "2",
                    "--log-dir",
                    str(directory / "logs"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(batch.returncode, 0, batch.stdout + batch.stderr)
            run_output = directory / "run.tsv"
            subject_output = directory / "subject.tsv"
            audit = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "code/audit_event_qc.py"),
                    "--manifest",
                    str(manifest),
                    "--output",
                    str(run_output),
                    "--subject-output",
                    str(subject_output),
                    "--missing-output",
                    str(directory / "missing.tsv"),
                    "--fail-on-incomplete",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(audit.returncode, 0, audit.stdout + audit.stderr)
            with run_output.open(newline="") as handle:
                runs = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual([row["exclude_run"] for row in runs], ["false", "true"])
            with subject_output.open(newline="") as handle:
                subjects = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual(subjects[0]["usable_runs"], "1")
            self.assertEqual(subjects[0]["exclude_subject"], "false")


if __name__ == "__main__":
    unittest.main()
