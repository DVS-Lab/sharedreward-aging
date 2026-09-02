#!/usr/bin/env python3
"""Build the cross-dataset Phase 0 smoothness/tSNR input contract."""

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
    "stage",
    "input_bold",
    "input_mask",
    "confounds",
)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rf1-run-qc",
        type=Path,
        default=Path(
            os.environ.get(
                "RF1_RUN_QC",
                "/ZPOOL/data/projects/rf1-sra-linux2/qc/run_qc.tsv",
            )
        ),
        help=(
            "Authoritative rf1-sra-linux2 run inventory. Only complete "
            "session-01 Shared Reward rows are eligible."
        ),
    )
    parser.add_argument(
        "--rf1-fmriprep-root",
        type=Path,
        default=Path(
            os.environ.get(
                "RF1_FMRIPREP_ROOT",
                "/ZPOOL/data/projects/rf1-sra-linux2/derivatives/fmriprep",
            )
        ),
    )
    parser.add_argument(
        "--rf1-confounds-root",
        type=Path,
        default=Path(
            os.environ.get(
                "RF1_CONFOUNDS_ROOT",
                "/ZPOOL/data/projects/rf1-sra-linux2/derivatives/fsl/"
                "confounds_tedana",
            )
        ),
        help=(
            "Authoritative RF1 TedanaPlusConfounds derivative root. "
            "Files are expected under sub-<ID>/ and are not duplicated here."
        ),
    )
    parser.add_argument(
        "--ds-resampling-manifest",
        type=Path,
        default=ROOT / "logs/runlists/ds003745-resampling-ready.tsv",
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--missing-output", required=True, type=Path)
    return parser.parse_args()


def nonempty(path):
    return path.is_file() and path.stat().st_size > 0


def unique_nonempty(directory, pattern):
    matches = sorted(
        path
        for path in directory.glob(pattern)
        if path.is_file() and path.stat().st_size > 0
    )
    return (matches[0] if len(matches) == 1 else None), len(matches)


def bold_mask_grids_match(bold, mask, affine_atol=1e-5):
    try:
        import nibabel as nib
        import numpy as np
    except ImportError as error:
        raise RuntimeError(f"nibabel and numpy are required: {error}") from error
    bold_image = nib.load(str(bold), mmap=True)
    mask_image = nib.load(str(mask), mmap=True)
    return (
        bold_image.ndim == 4
        and mask_image.ndim == 3
        and tuple(bold_image.shape[:3]) == tuple(mask_image.shape)
        and bool(
            np.allclose(
                bold_image.affine,
                mask_image.affine,
                rtol=0.0,
                atol=affine_atol,
            )
        )
    )


def add_row(ready, missing, identifiers, paths):
    problems = [name for name, path in paths.items() if not nonempty(path)]
    if not problems:
        try:
            if not bold_mask_grids_match(paths["input_bold"], paths["input_mask"]):
                problems.append("BOLD-mask geometry")
        except (OSError, RuntimeError, ValueError):
            problems.append("unreadable BOLD/mask")
    if problems:
        missing.append({**identifiers, "missing": ",".join(problems)})
    else:
        ready.append(
            {
                **identifiers,
                "input_bold": str(paths["input_bold"].resolve()),
                "input_mask": str(paths["input_mask"].resolve()),
                "confounds": str(paths["confounds"].resolve()),
            }
        )


def rf1_rows(args, ready, missing):
    if not nonempty(args.rf1_run_qc):
        raise ValueError(f"authoritative RF1 run QC is missing: {args.rf1_run_qc}")
    with args.rf1_run_qc.open(newline="") as handle:
        inventory = list(csv.DictReader(handle, delimiter="\t"))
    required = {"subject", "session", "task", "run", "qc_complete"}
    if not inventory or not required.issubset(inventory[0]):
        raise ValueError("authoritative RF1 run QC lacks required columns")
    selected = [
        row
        for row in inventory
        if row["task"] == "sharedreward"
        and row["session"] == "01"
        and row["qc_complete"].strip().lower() == "true"
    ]
    if not selected:
        raise ValueError(f"no complete RF1 session-01 Shared Reward rows: {args.rf1_run_qc}")
    seen = set()
    for source in selected:
        key = (source["subject"], source["session"], str(int(source["run"])))
        if key in seen:
            raise ValueError(f"duplicate authoritative RF1 run: {key}")
        seen.add(key)
        stem = (
            f"sub-{key[0]}_ses-{key[1]}_task-sharedreward_run-{key[2]}"
        )
        func = (
            args.rf1_fmriprep_root
            / f"sub-{key[0]}"
            / f"ses-{key[1]}"
            / "func"
        )
        bold = func / (
            f"{stem}_part-mag_space-MNI152NLin6Asym_desc-preproc_bold.nii.gz"
        )
        identifiers = {
            "dataset": "rf1",
            "subject": key[0],
            "session": key[1],
            "run": key[2],
            "stage": "pre_resample",
        }
        confounds = (
            args.rf1_confounds_root
            / f"sub-{identifiers['subject']}"
            / f"{stem}_desc-TedanaPlusConfounds.tsv"
        )
        add_row(
            ready,
            missing,
            identifiers,
            {
                "input_bold": bold,
                "input_mask": func
                / f"{stem}_part-mag_space-MNI152NLin6Asym_desc-brain_mask.nii.gz",
                "confounds": confounds,
            },
        )


def ds003745_rows(args, ready, missing):
    with args.ds_resampling_manifest.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    required = {
        "subject",
        "run",
        "input_bold",
        "input_mask",
        "output_bold",
        "output_mask",
    }
    if not rows or not required.issubset(rows[0]):
        raise ValueError(
            "ds003745 resampling manifest lacks required columns: "
            + ",".join(sorted(required))
        )
    seen = set()
    for row in rows:
        key = (row["subject"], row["run"])
        if key in seen:
            raise ValueError(
                f"duplicate ds003745 resampling unit: sub-{key[0]} run-{key[1]}"
            )
        seen.add(key)
        source_bold = Path(row["input_bold"])
        source_prefix = source_bold.name.split("_space-", 1)[0]
        confounds, count = unique_nonempty(
            source_bold.parent,
            f"{source_prefix}*desc-confounds_timeseries.tsv",
        )
        if confounds is None:
            confounds = source_bold.parent / f"missing-confounds-found-{count}.tsv"
        base = {
            "dataset": "ds003745",
            "subject": row["subject"],
            "session": "",
            "run": row["run"],
        }
        add_row(
            ready,
            missing,
            {**base, "stage": "pre_resample"},
            {
                "input_bold": source_bold,
                "input_mask": Path(row["input_mask"]),
                "confounds": confounds,
            },
        )
        add_row(
            ready,
            missing,
            {**base, "stage": "post_resample_preblur"},
            {
                "input_bold": Path(row["output_bold"]),
                "input_mask": Path(row["output_mask"]),
                "confounds": confounds,
            },
        )


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


def sort_key(row):
    return (
        row["dataset"],
        row["subject"],
        row["session"],
        row["run"],
        row["stage"],
    )


def main():
    args = parse_args()
    if not args.ds_resampling_manifest.is_file():
        raise SystemExit(
            f"ERROR: ds003745 resampling manifest not found: "
            f"{args.ds_resampling_manifest}"
        )
    ready = []
    missing = []
    try:
        rf1_rows(args, ready, missing)
        ds003745_rows(args, ready, missing)
    except ValueError as error:
        raise SystemExit(f"ERROR: {error}") from error
    ready.sort(key=sort_key)
    missing.sort(key=sort_key)
    write_tsv(args.output, FIELDS, ready)
    write_tsv(
        args.missing_output,
        FIELDS[:5] + ("missing",),
        missing,
    )
    counts = Counter((row["dataset"], row["stage"]) for row in ready)
    print(f"Ready characterization units: {len(ready)}")
    for (dataset, stage), count in sorted(counts.items()):
        print(f"  {dataset} {stage}: {count}")
    print(f"Incomplete characterization units: {len(missing)}")
    print(f"Ready manifest: {args.output.resolve()}")
    print(f"Missing report: {args.missing_output.resolve()}")
    for row in missing[:20]:
        print(
            f"INCOMPLETE {row['dataset']} sub-{row['subject']} "
            f"ses-{row['session'] or 'none'} run-{row['run']} "
            f"{row['stage']}: {row['missing']}"
        )
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
