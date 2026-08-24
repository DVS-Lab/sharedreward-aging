#!/usr/bin/env python3
"""Discover one explicit Shared Reward ratings source per cohort subject."""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("dataset", "subject", "ratings_file")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target-manifest",
        type=Path,
        default=ROOT / "logs/runlists/target-smoothing-6mm-ready.tsv",
    )
    parser.add_argument(
        "--ds-ratings-root",
        type=Path,
        default=Path(
            os.environ.get(
                "DS003745_RATINGS_ROOT",
                ROOT / "sourcedata/ds003745/stimuli/psychopy/logs",
            )
        ),
    )
    parser.add_argument(
        "--rf1-ratings-root",
        type=Path,
        default=Path(
            os.environ.get(
                "RF1_RATINGS_ROOT",
                ROOT / "stimuli/Scan-Card_Guessing_Game/logs-cleaned",
            )
        ),
    )
    parser.add_argument(
        "--ratings-map",
        type=Path,
        help="Optional explicit dataset/subject/ratings_file map resolving ambiguity.",
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--missing-output", required=True, type=Path)
    return parser.parse_args()


def nonempty(path):
    return path.is_file() and path.stat().st_size > 0


def write_tsv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def load_map(path):
    if path is None:
        return {}
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if not rows or not set(FIELDS).issubset(rows[0]):
        raise ValueError("ratings map must contain dataset, subject, ratings_file")
    mapping = {}
    for row in rows:
        key = (row["dataset"], row["subject"])
        if key in mapping:
            raise ValueError(f"duplicate ratings-map subject: {key}")
        mapping[key] = Path(row["ratings_file"])
    return mapping


def discover(root, subject):
    patterns = (
        f"{subject}/sub{subject}_SR-Ratings-*.csv",
        f"{subject}/sub-{subject}_SR-Ratings-*.csv",
        f"sub-{subject}/sub{subject}_SR-Ratings-*.csv",
        f"sub-{subject}/sub-{subject}_SR-Ratings-*.csv",
    )
    candidates = set()
    for pattern in patterns:
        candidates.update(path for path in root.glob(pattern) if nonempty(path))
    return sorted(candidates)


def main():
    args = parse_args()
    if not nonempty(args.target_manifest):
        raise SystemExit(f"ERROR: target manifest not found: {args.target_manifest}")
    try:
        mapping = load_map(args.ratings_map)
    except (OSError, ValueError) as error:
        raise SystemExit(f"ERROR: {error}") from error
    with args.target_manifest.open(newline="") as handle:
        targets = list(csv.DictReader(handle, delimiter="\t"))
    if not targets or not {"dataset", "subject"}.issubset(targets[0]):
        raise SystemExit("ERROR: target manifest contract is incomplete")
    subjects = sorted({(row["dataset"], row["subject"]) for row in targets})
    ready, missing = [], []
    for dataset, subject in subjects:
        key = (dataset, subject)
        if key in mapping:
            candidates = [mapping[key]] if nonempty(mapping[key]) else []
            problem = "mapped_ratings_file_missing_or_empty" if not candidates else ""
        else:
            root = args.ds_ratings_root if dataset == "ds003745" else args.rf1_ratings_root
            candidates = discover(root, subject)
            problem = "missing_or_unretrieved_ratings_file"
        if len(candidates) == 1:
            ready.append(
                {
                    "dataset": dataset,
                    "subject": subject,
                    "ratings_file": str(candidates[0].resolve()),
                }
            )
        else:
            if len(candidates) > 1:
                problem = f"ambiguous_ratings_files:{len(candidates)}"
            missing.append(
                {
                    "dataset": dataset,
                    "subject": subject,
                    "problems": problem,
                    "candidate_files": ";".join(str(path.resolve()) for path in candidates),
                }
            )
    write_tsv(args.output, FIELDS, ready)
    write_tsv(
        args.missing_output,
        ("dataset", "subject", "problems", "candidate_files"),
        missing,
    )
    print(f"Subjects with one explicit ratings source: {len(ready)}")
    print(f"Subjects requiring ratings-source resolution: {len(missing)}")
    print(f"Ready manifest: {args.output.resolve()}")
    print(f"Missing/ambiguous report: {args.missing_output.resolve()}")
    for row in missing[:20]:
        print(
            f"INCOMPLETE {row['dataset']} sub-{row['subject']}: {row['problems']}"
        )
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
