#!/usr/bin/env python3
"""Freeze the analysis-ready cross-dataset target-smoothing contract."""

from __future__ import annotations

import argparse
import csv
import os
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIELDS = (
    "dataset",
    "subject",
    "session",
    "run",
    "input_bold",
    "input_mask",
    "output_bold",
    "output_qc",
    "target_fwhm_mm",
)
ANALYSIS_STAGES = {
    ("rf1", "pre_resample"),
    ("ds003745", "post_resample_preblur"),
}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--characterization-manifest",
        type=Path,
        default=ROOT / "logs/runlists/phase0-characterization-ready.tsv",
    )
    parser.add_argument(
        "--rf1-sharedreward-root",
        type=Path,
        default=Path(
            os.environ.get(
                "RF1_SHAREDREWARD_ROOT",
                "/ZPOOL/data/projects/rf1-sra-sharedreward",
            )
        ),
    )
    parser.add_argument(
        "--target",
        default=os.environ.get("TARGET_FWHM_MM", "6"),
        help="Total measured classic FWHM target in millimeters.",
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--missing-output", required=True, type=Path)
    return parser.parse_args()


def target_value_and_label(value):
    try:
        target = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError(f"invalid target: {value}") from error
    if not target.is_finite() or target <= 0:
        raise ValueError(f"target must be positive: {value}")
    normalized = format(target.normalize(), "f")
    label = normalized.replace(".", "p")
    return normalized, label


def write_tsv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def output_path(row, label, rf1_root):
    subject = row["subject"]
    run = row["run"]
    if row["dataset"] == "rf1":
        session = row["session"]
        name = (
            f"sub-{subject}_ses-{session}_task-sharedreward_run-{run}_"
            f"space-MNI152NLin6Asym_desc-smoothToFWHM{label}_bold.nii.gz"
        )
        return (
            rf1_root
            / "derivatives/harmonized"
            / f"sub-{subject}"
            / f"ses-{session}"
            / "func"
            / name
        )
    if row["dataset"] == "ds003745":
        name = (
            f"sub-{subject}_task-sharedreward_run-{run}_"
            f"space-MNI152NLin6Asym_desc-smoothToFWHM{label}_bold.nii.gz"
        )
        return ROOT / "derivatives/harmonized" / f"sub-{subject}" / "func" / name
    raise ValueError(f"unsupported dataset: {row['dataset']}")


def main():
    args = parse_args()
    if not args.characterization_manifest.is_file():
        raise SystemExit(
            f"ERROR: characterization manifest not found: "
            f"{args.characterization_manifest}"
        )
    try:
        target, label = target_value_and_label(args.target)
    except ValueError as error:
        raise SystemExit(f"ERROR: {error}") from error
    with args.characterization_manifest.open(newline="") as handle:
        source = list(csv.DictReader(handle, delimiter="\t"))
    required = {
        "dataset",
        "subject",
        "session",
        "run",
        "stage",
        "input_bold",
        "input_mask",
    }
    if not source or not required.issubset(source[0]):
        raise SystemExit(
            "ERROR: characterization manifest lacks required columns: "
            + ",".join(sorted(required))
        )

    ready = []
    missing = []
    seen = set()
    for row in source:
        if (row["dataset"], row["stage"]) not in ANALYSIS_STAGES:
            continue
        key = (row["dataset"], row["subject"], row["session"], row["run"])
        if key in seen:
            raise SystemExit(f"ERROR: duplicate target-smoothing unit: {key}")
        seen.add(key)
        problems = [
            field
            for field in ("input_bold", "input_mask")
            if not Path(row[field]).is_file() or Path(row[field]).stat().st_size == 0
        ]
        identifiers = {field: row[field] for field in FIELDS[:4]}
        if problems:
            missing.append({**identifiers, "missing": ",".join(problems)})
            continue
        output = output_path(row, label, args.rf1_sharedreward_root).resolve()
        ready.append(
            {
                **identifiers,
                "input_bold": str(Path(row["input_bold"]).resolve()),
                "input_mask": str(Path(row["input_mask"]).resolve()),
                "output_bold": str(output),
                "output_qc": str(output).removesuffix(".nii.gz")
                + "_smoothness.tsv",
                "target_fwhm_mm": target,
            }
        )

    ready.sort(key=lambda row: tuple(row[field] for field in FIELDS[:4]))
    missing.sort(key=lambda row: tuple(row[field] for field in FIELDS[:4]))
    write_tsv(args.output, FIELDS, ready)
    write_tsv(args.missing_output, FIELDS[:4] + ("missing",), missing)
    counts = Counter(row["dataset"] for row in ready)
    print(f"Target classic FWHM: {target} mm")
    print(f"Ready target-smoothing units: {len(ready)}")
    for dataset, count in sorted(counts.items()):
        print(f"  {dataset}: {count}")
    print(f"Incomplete target-smoothing units: {len(missing)}")
    print(f"Ready manifest: {args.output.resolve()}")
    print(f"Missing report: {args.missing_output.resolve()}")
    for row in missing[:20]:
        print(
            f"INCOMPLETE {row['dataset']} sub-{row['subject']} "
            f"ses-{row['session'] or 'none'} run-{row['run']}: {row['missing']}"
        )
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
