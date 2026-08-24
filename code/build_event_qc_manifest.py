#!/usr/bin/env python3
"""Build the frozen source-to-harmonized Shared Reward event QC contract."""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIELDS = (
    "dataset",
    "subject",
    "session",
    "run",
    "source_events",
    "harmonized_events",
    "output_json",
)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target-manifest",
        type=Path,
        default=ROOT / "logs/runlists/target-smoothing-6mm-ready.tsv",
    )
    parser.add_argument(
        "--rf1-bids-root",
        type=Path,
        default=Path(
            os.environ.get("RF1_BIDS_ROOT", "/ZPOOL/data/projects/rf1-sra-linux2/bids")
        ),
    )
    parser.add_argument(
        "--ds003745-root",
        type=Path,
        default=Path(
            os.environ.get("DS003745_ROOT", ROOT / "sourcedata/ds003745")
        ),
    )
    parser.add_argument(
        "--event-root",
        type=Path,
        default=ROOT / "derivatives/harmonized/events",
    )
    parser.add_argument(
        "--qc-root",
        type=Path,
        default=ROOT / "derivatives/qc/events/run-level",
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--missing-output", required=True, type=Path)
    return parser.parse_args()


def nonempty(path):
    return path.is_file() and path.stat().st_size > 0


def run_label(row):
    return f"{int(row['run']):02d}" if row["dataset"] == "ds003745" else row["run"]


def derivative_path(root, row, suffix):
    run = run_label(row)
    session = f"_ses-{row['session']}" if row["session"] else ""
    name = (
        f"sub-{row['subject']}{session}_task-sharedreward_run-{run}_"
        f"desc-fullTrial_{suffix}"
    )
    parts = [root, row["dataset"], f"sub-{row['subject']}"]
    if row["session"]:
        parts.append(f"ses-{row['session']}")
    return Path(*parts) / "func" / name


def source_path(args, row):
    run = run_label(row)
    if row["dataset"] == "rf1":
        prefix = (
            f"sub-{row['subject']}_ses-{row['session']}_"
            f"task-sharedreward_run-{run}"
        )
        return (
            args.rf1_bids_root
            / f"sub-{row['subject']}"
            / f"ses-{row['session']}"
            / "func"
            / f"{prefix}_events.tsv"
        )
    if row["dataset"] == "ds003745":
        prefix = f"sub-{row['subject']}_task-sharedreward_run-{run}"
        return (
            args.ds003745_root
            / f"sub-{row['subject']}"
            / "func"
            / f"{prefix}_events.tsv"
        )
    raise ValueError(f"unsupported dataset: {row['dataset']}")


def write_tsv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    args = parse_args()
    if not nonempty(args.target_manifest):
        raise SystemExit(f"ERROR: target manifest not found: {args.target_manifest}")
    with args.target_manifest.open(newline="") as handle:
        targets = list(csv.DictReader(handle, delimiter="\t"))
    required = {"dataset", "subject", "session", "run"}
    if not targets or not required.issubset(targets[0]):
        raise SystemExit("ERROR: target manifest contract is incomplete")

    ready, missing, seen = [], [], set()
    for row in targets:
        identifiers = {field: row[field] for field in FIELDS[:4]}
        key = tuple(identifiers.values())
        if key in seen:
            raise SystemExit(f"ERROR: duplicate event QC unit: {key}")
        seen.add(key)
        try:
            source = source_path(args, row)
        except ValueError as error:
            raise SystemExit(f"ERROR: {error}") from error
        if not nonempty(source):
            missing.append({**identifiers, "problems": "missing_source_events"})
            continue
        ready.append(
            {
                **identifiers,
                "source_events": str(source.resolve()),
                "harmonized_events": str(
                    derivative_path(args.event_root, row, "events.tsv").resolve()
                ),
                "output_json": str(
                    derivative_path(args.qc_root, row, "eventQC.json").resolve()
                ),
            }
        )

    key = lambda row: tuple(str(row[field]) for field in FIELDS[:4])
    ready.sort(key=key)
    missing.sort(key=key)
    write_tsv(args.output, FIELDS, ready)
    write_tsv(args.missing_output, FIELDS[:4] + ("problems",), missing)
    print(f"Ready event-QC units: {len(ready)}")
    print(f"Incomplete event-QC units: {len(missing)}")
    print(f"Ready manifest: {args.output.resolve()}")
    print(f"Missing report: {args.missing_output.resolve()}")
    for row in missing[:20]:
        print(
            f"INCOMPLETE {row['dataset']} sub-{row['subject']} "
            f"ses-{row['session'] or 'none'} run-{row['run']}: {row['problems']}"
        )
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
