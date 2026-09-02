#!/usr/bin/env python3
"""Build the ds003745 named-confounds to FSL-matrix conversion contract."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIELDS = (
    "dataset",
    "subject",
    "session",
    "run",
    "input_bold",
    "input_confounds",
    "output_confounds",
    "output_metadata",
)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--analysis-qc",
        type=Path,
        default=ROOT / "logs/records/analysis-qc-run-level.tsv",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "derivatives/fsl/confounds_fmriprep",
    )
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def output_paths(root: Path, row: dict[str, str]) -> tuple[Path, Path]:
    run = f"{int(row['run']):02d}"
    stem = f"sub-{row['subject']}_task-sharedreward_run-{run}_desc-FSLConfounds"
    directory = root / f"sub-{row['subject']}" / "func"
    return directory / f"{stem}.tsv", directory / f"{stem}.json"


def main():
    args = parse_args()
    with args.analysis_qc.open(newline="") as handle:
        source = list(csv.DictReader(handle, delimiter="\t"))
    required = {"dataset", "subject", "session", "run", "input", "confounds"}
    if not source or not required.issubset(source[0]):
        raise SystemExit("ERROR: analysis-QC table lacks the required fields")
    rows = []
    seen = set()
    for row in source:
        if row["dataset"] != "ds003745":
            continue
        key = tuple(row[field] for field in ("dataset", "subject", "session", "run"))
        if key in seen:
            raise SystemExit(f"ERROR: duplicate ds003745 nuisance unit: {key}")
        seen.add(key)
        output, metadata = output_paths(args.output_root, row)
        rows.append(
            {
                **{field: row[field] for field in FIELDS[:4]},
                "input_bold": str(Path(row["input"]).resolve()),
                "input_confounds": str(Path(row["confounds"]).resolve()),
                "output_confounds": str(output.resolve()),
                "output_metadata": str(metadata.resolve()),
            }
        )
    if not rows:
        raise SystemExit("ERROR: no ds003745 units in analysis-QC table")
    rows.sort(key=lambda row: tuple(row[field] for field in FIELDS[:4]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"ds003745 FSL nuisance units: {len(rows)}")
    print(f"Manifest: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
