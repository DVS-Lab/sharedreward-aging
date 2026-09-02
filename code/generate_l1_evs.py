#!/usr/bin/env python3
"""Generate audited FSL three-column EVs from harmonized full-trial events."""

from __future__ import annotations

import argparse
import csv
import os
import tempfile
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONDITIONS = tuple(
    f"event_{partner}_{outcome}"
    for partner in ("computer", "friend", "stranger")
    for outcome in ("punish", "reward", "neutral")
)
ALL_EVS = CONDITIONS + ("missed_trial",)


def ev_directory(root: Path, row: dict[str, str]) -> Path:
    parts = [root, row["dataset"], f"sub-{row['subject']}"]
    if row["session"]:
        parts.append(f"ses-{row['session']}")
    return Path(*parts) / "sharedreward" / f"run-{int(row['run'])}"


def atomic_write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w") as handle:
            handle.write(text)
        Path(temporary).replace(path)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "derivatives/fsl/EVfiles",
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    with args.manifest.open(newline="") as handle:
        manifest = list(csv.DictReader(handle, delimiter="\t"))
    required = {"dataset", "subject", "session", "run", "harmonized_events"}
    if not manifest or not required.issubset(manifest[0]):
        raise SystemExit("ERROR: L1 manifest contract is incomplete")
    generated = verified = 0
    for unit in manifest:
        with Path(unit["harmonized_events"]).open(newline="") as handle:
            events = list(csv.DictReader(handle, delimiter="\t"))
        if not events or not {"onset", "duration", "trial_type"}.issubset(events[0]):
            raise SystemExit(
                f"ERROR: invalid harmonized events: {unit['harmonized_events']}"
            )
        grouped = defaultdict(list)
        for event in events:
            if event["trial_type"] in ALL_EVS:
                grouped[event["trial_type"]].append(
                    (float(event["onset"]), float(event["duration"]), 1.0)
                )
        empty = [condition for condition in CONDITIONS if not grouped[condition]]
        if empty:
            raise SystemExit(
                "ERROR: primary common-design run has empty substantive EVs: "
                f"{unit['dataset']} sub-{unit['subject']} run-{unit['run']}: "
                + ",".join(empty)
            )
        directory = ev_directory(args.output_root, unit)
        expected = [directory / f"{condition}.txt" for condition in ALL_EVS]
        if (
            not args.overwrite
            and all(path.is_file() for path in expected)
            and all(path.stat().st_size > 0 for path in expected[:-1])
        ):
            verified += 1
            continue
        for condition, path in zip(ALL_EVS, expected):
            text = "".join(
                f"{onset:.6f}\t{duration:.6f}\t{amplitude:.1f}\n"
                for onset, duration, amplitude in grouped[condition]
            )
            atomic_write(path, text)
        generated += 1
    print(f"L1 EV units: {len(manifest)}")
    print(f"Newly generated: {generated}")
    print(f"Verified existing: {verified}")
    print(f"EV root: {args.output_root.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
