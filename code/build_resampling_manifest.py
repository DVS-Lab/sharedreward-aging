#!/usr/bin/env python3
"""Build a deterministic ds003745-to-RF1-grid resampling manifest."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--participants",
        type=Path,
        default=ROOT / "sourcedata/ds003745/participants.tsv",
    )
    parser.add_argument(
        "--fmriprep-root",
        type=Path,
        default=ROOT / "derivatives/fmriprep",
    )
    parser.add_argument(
        "--harmonized-root",
        type=Path,
        default=ROOT / "derivatives/harmonized",
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--missing-output", required=True, type=Path)
    return parser.parse_args()


def normalize_subject(value):
    value = value.strip()
    return value[4:] if value.startswith("sub-") else value


def unique_nonempty(directory, pattern):
    if not directory.is_dir():
        return None, 0
    matches = sorted(
        path
        for path in directory.glob(pattern)
        if path.is_file() and path.stat().st_size > 0
    )
    return (matches[0] if len(matches) == 1 else None), len(matches)


def main():
    args = parse_args()
    with args.participants.open(newline="") as handle:
        participants = list(csv.DictReader(handle, delimiter="\t"))
    if not participants or "participant_id" not in participants[0]:
        raise SystemExit(
            f"ERROR: participants table lacks participant_id: {args.participants}"
        )

    ready = []
    missing = []
    seen = set()
    for participant in participants:
        subject = normalize_subject(participant["participant_id"])
        if not subject or subject in seen:
            raise SystemExit(f"ERROR: invalid or duplicate participant: {subject!r}")
        seen.add(subject)
        func_root = args.fmriprep_root / f"sub-{subject}/func"
        output_root = args.harmonized_root / f"sub-{subject}/func"
        for run in ("01", "02"):
            prefix = f"sub-{subject}_task-sharedreward_run-{run}"
            bold, n_bold = unique_nonempty(
                func_root,
                f"{prefix}*space-MNI152NLin6Asym*desc-preproc_bold.nii.gz",
            )
            mask, n_mask = unique_nonempty(
                func_root,
                f"{prefix}*space-MNI152NLin6Asym*desc-brain_mask.nii.gz",
            )
            problems = []
            if bold is None:
                problems.append(f"preproc_bold[found={n_bold}]")
            if mask is None:
                problems.append(f"brain_mask[found={n_mask}]")
            if problems:
                missing.append(
                    {
                        "subject": subject,
                        "run": run,
                        "missing": ",".join(problems),
                    }
                )
                continue

            output_stem = output_root / (
                f"{prefix}_space-MNI152NLin6Asym_desc-rf1Grid"
            )
            ready.append(
                {
                    "subject": subject,
                    "run": run,
                    "input_bold": str(bold.resolve()),
                    "input_mask": str(mask.resolve()),
                    "output_bold": str(output_stem) + "_bold.nii.gz",
                    "output_mask": str(output_stem) + "_mask.nii.gz",
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "subject",
                "run",
                "input_bold",
                "input_mask",
                "output_bold",
                "output_mask",
            ),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(ready)

    args.missing_output.parent.mkdir(parents=True, exist_ok=True)
    with args.missing_output.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("subject", "run", "missing"),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(missing)

    print(f"Participants considered: {len(participants)}")
    print(f"Ready run units: {len(ready)}")
    print(f"Incomplete run units: {len(missing)}")
    print(f"Ready manifest: {args.output.resolve()}")
    print(f"Missing report: {args.missing_output.resolve()}")
    if missing:
        for row in missing:
            print(
                f"INCOMPLETE sub-{row['subject']} run-{row['run']}: "
                f"{row['missing']}"
            )
        raise SystemExit(1)


if __name__ == "__main__":
    main()
