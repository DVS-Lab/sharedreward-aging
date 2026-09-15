import csv
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "code/generate_l1_evs.py"
CONDITIONS = tuple(
    f"event_{partner}_{outcome}"
    for partner in ("computer", "friend", "stranger")
    for outcome in ("punish", "reward", "neutral")
)


def write_events(path, omitted):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("onset", "duration", "trial_type"),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        for number, condition in enumerate(CONDITIONS):
            if condition not in omitted:
                writer.writerow(
                    {"onset": number, "duration": 1, "trial_type": condition}
                )


def write_manifest(path, events):
    path.write_text(
        "dataset\tsubject\tsession\trun\tharmonized_events\n"
        f"ds003745\t104\t\t1\t{events}\n"
    )


class L1EVTest(unittest.TestCase):
    def test_empty_neutral_is_written_as_an_optional_empty_ev(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            events = root / "events.tsv"
            manifest = root / "manifest.tsv"
            output = root / "EVfiles"
            write_events(events, {"event_friend_neutral"})
            write_manifest(manifest, events)
            subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--manifest",
                    str(manifest),
                    "--output-root",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            ev_dir = output / "ds003745/sub-104/sharedreward/run-1"
            self.assertEqual((ev_dir / "event_friend_neutral.txt").read_text(), "")
            self.assertTrue((ev_dir / "event_friend_reward.txt").stat().st_size > 0)
            # Same-sized corrected content must not be mistaken for a complete EV.
            (ev_dir / "event_friend_reward.txt").write_text("9.000000\t1.000000\t1.0\n")
            retry = subprocess.run(["python3", str(SCRIPT), "--manifest", str(manifest),
                                    "--output-root", str(output)], capture_output=True, text=True)
            self.assertNotEqual(retry.returncode, 0)
            self.assertIn("stale EV content", retry.stderr)

    def test_empty_inferential_condition_still_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            events = root / "events.tsv"
            manifest = root / "manifest.tsv"
            write_events(events, {"event_friend_reward"})
            write_manifest(manifest, events)
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--manifest",
                    str(manifest),
                    "--output-root",
                    str(root / "EVfiles"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("empty inferential EVs", result.stderr)


if __name__ == "__main__":
    unittest.main()
