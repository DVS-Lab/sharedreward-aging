#!/usr/bin/env python3
"""Build the frozen 765-run post-smoothing tSNR/motion/coverage QC contract."""

from __future__ import annotations

import argparse
import csv
import os
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIELDS = (
    "dataset",
    "subject",
    "session",
    "run",
    "input_bold",
    "input_mask",
    "reference_mask",
    "confounds",
    "output_json",
)
ANALYSIS_STAGE = {"rf1": "pre_resample", "ds003745": "post_resample_preblur"}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target-manifest",
        type=Path,
        default=ROOT / "logs/runlists/target-smoothing-6mm-ready.tsv",
    )
    parser.add_argument(
        "--characterization-manifest",
        type=Path,
        default=ROOT / "logs/runlists/phase0-characterization-ready.tsv",
    )
    parser.add_argument(
        "--reference-mask",
        type=Path,
        default=Path(
            os.environ.get(
                "COMMON_ANALYSIS_MASK",
                ROOT
                / "resources/tpl-MNI152NLin6Asym_space-RF1Grid_desc-brain_mask.nii.gz",
            )
        ),
    )
    parser.add_argument(
        "--qc-root",
        type=Path,
        default=ROOT / "derivatives/qc/analysis-input/run-level",
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


def output_path(root, row):
    session = f"_ses-{row['session']}" if row["session"] else ""
    name = (
        f"sub-{row['subject']}{session}_task-sharedreward_run-{row['run']}_"
        "space-MNI152NLin6Asym_desc-smoothToFWHM6_analysisQC.json"
    )
    parts = [root, row["dataset"], f"sub-{row['subject']}"]
    if row["session"]:
        parts.append(f"ses-{row['session']}")
    return Path(*parts) / "func" / name


def main():
    args = parse_args()
    for path, label in (
        (args.target_manifest, "target manifest"),
        (args.characterization_manifest, "characterization manifest"),
        (args.reference_mask, "common analysis mask"),
    ):
        if not nonempty(path):
            raise SystemExit(f"ERROR: {label} not found or empty: {path}")
    with args.target_manifest.open(newline="") as handle:
        targets = list(csv.DictReader(handle, delimiter="\t"))
    with args.characterization_manifest.open(newline="") as handle:
        characterization = list(csv.DictReader(handle, delimiter="\t"))
    target_required = {"dataset", "subject", "session", "run", "output_bold", "input_mask"}
    characterization_required = {
        "dataset",
        "subject",
        "session",
        "run",
        "stage",
        "confounds",
    }
    if not targets or not target_required.issubset(targets[0]):
        raise SystemExit("ERROR: target manifest contract is incomplete")
    if not characterization or not characterization_required.issubset(characterization[0]):
        raise SystemExit("ERROR: characterization manifest contract is incomplete")

    confounds = {}
    for row in characterization:
        if row["stage"] != ANALYSIS_STAGE.get(row["dataset"]):
            continue
        key = tuple(row[field] for field in ("dataset", "subject", "session", "run"))
        if key in confounds:
            raise SystemExit(f"ERROR: duplicate analysis-stage confounds unit: {key}")
        confounds[key] = Path(row["confounds"])

    ready, missing = [], []
    seen = set()
    for row in targets:
        identifiers = {field: row[field] for field in FIELDS[:4]}
        key = tuple(identifiers.values())
        if key in seen:
            raise SystemExit(f"ERROR: duplicate target QC unit: {key}")
        seen.add(key)
        paths = {
            "input_bold": Path(row["output_bold"]),
            "input_mask": Path(row["input_mask"]),
            "reference_mask": args.reference_mask,
            "confounds": confounds.get(key, Path("missing-confounds.tsv")),
        }
        problems = [name for name, path in paths.items() if not nonempty(path)]
        if problems:
            missing.append({**identifiers, "missing": ",".join(problems)})
            continue
        ready.append(
            {
                **identifiers,
                **{name: str(path.resolve()) for name, path in paths.items()},
                "output_json": str(output_path(args.qc_root, row).resolve()),
            }
        )

    sort_key = lambda row: tuple(row[field] for field in FIELDS[:4])
    ready.sort(key=sort_key)
    missing.sort(key=sort_key)
    write_tsv(args.output, FIELDS, ready)
    write_tsv(args.missing_output, FIELDS[:4] + ("missing",), missing)
    counts = Counter(row["dataset"] for row in ready)
    print(f"Ready post-smoothing analysis-QC units: {len(ready)}")
    for dataset, count in sorted(counts.items()):
        print(f"  {dataset}: {count}")
    print(f"Incomplete analysis-QC units: {len(missing)}")
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
