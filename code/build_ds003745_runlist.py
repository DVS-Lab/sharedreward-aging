#!/usr/bin/env python3
"""Build a deterministic ds003745 participant runlist from pinned metadata."""

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--participants",
        type=Path,
        default=ROOT / "sourcedata/ds003745/participants.tsv",
    )
    parser.add_argument("--exclude-subject", action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def normalize_subject(value):
    value = value.strip()
    return value[4:] if value.startswith("sub-") else value


def main():
    args = parse_args()
    excluded = {normalize_subject(value) for value in args.exclude_subject}

    with args.participants.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    required = {"participant_id", "age", "sex", "group"}
    if not rows or not required.issubset(rows[0]):
        raise SystemExit(
            f"ERROR: participants table lacks required columns: {args.participants}"
        )

    output_rows = []
    seen = set()
    for row in rows:
        subject = normalize_subject(row["participant_id"])
        if not subject or subject in seen:
            raise SystemExit(f"ERROR: invalid or duplicate participant: {subject!r}")
        seen.add(subject)
        if subject in excluded:
            continue
        output_rows.append(
            {
                "subject": subject,
                "age": row["age"],
                "sex": row["sex"],
                "group": row["group"],
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("subject", "age", "sex", "group"),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Participants in pinned table: {len(rows)}")
    print(f"Excluded participants: {len(excluded & seen)}")
    print(f"Runlist participants: {len(output_rows)}")
    print(f"Runlist: {args.output.resolve()}")


if __name__ == "__main__":
    main()
