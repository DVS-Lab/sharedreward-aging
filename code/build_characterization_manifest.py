#!/usr/bin/env python3
"""Build the cross-dataset Phase 0 smoothness/tSNR input contract."""

from __future__ import annotations

import argparse
import csv
import os
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RF1_BOLD_RE = re.compile(
    r"^sub-(?P<subject>[^_]+)_ses-(?P<session>[^_]+)_"
    r"task-sharedreward_run-(?P<run>[^_]+)_part-mag_"
    r"space-MNI152NLin6Asym_desc-preproc_bold\.nii\.gz$"
)
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


def add_row(ready, missing, identifiers, paths):
    problems = [name for name, path in paths.items() if not nonempty(path)]
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
    pattern = (
        "sub-*/ses-*/func/"
        "sub-*_ses-*_task-sharedreward_run-*_part-mag_"
        "space-MNI152NLin6Asym_desc-preproc_bold.nii.gz"
    )
    bolds = sorted(args.rf1_fmriprep_root.glob(pattern))
    if not bolds:
        raise ValueError(
            f"no canonical RF1 Shared Reward BOLD files: {args.rf1_fmriprep_root}"
        )
    for bold in bolds:
        match = RF1_BOLD_RE.match(bold.name)
        if not match:
            raise ValueError(f"unrecognized RF1 BOLD name: {bold}")
        identifiers = {
            "dataset": "rf1",
            "subject": match.group("subject"),
            "session": match.group("session"),
            "run": match.group("run"),
            "stage": "pre_resample",
        }
        stem = (
            f"sub-{identifiers['subject']}_ses-{identifiers['session']}_"
            f"task-sharedreward_run-{identifiers['run']}"
        )
        func = bold.parent
        add_row(
            ready,
            missing,
            identifiers,
            {
                "input_bold": bold,
                "input_mask": func
                / f"{stem}_part-mag_space-MNI152NLin6Asym_desc-brain_mask.nii.gz",
                "confounds": func / f"{stem}_desc-confounds_timeseries.tsv",
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
