#!/usr/bin/env python3
"""Audit ds003745 Shared Reward fMRIPrep outputs and build a retry manifest."""

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
    parser.add_argument(
        "--fmriprep-root",
        type=Path,
        default=ROOT / "derivatives/fmriprep",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--retry-manifest", type=Path)
    parser.add_argument("--fail-on-incomplete", action="store_true")
    return parser.parse_args()


def normalize_subject(value):
    value = value.strip()
    return value[4:] if value.startswith("sub-") else value


def require_one_nonempty(directory, pattern, label, missing):
    matches = list(directory.glob(pattern)) if directory.is_dir() else []
    nonempty = [path for path in matches if path.is_file() and path.stat().st_size]
    if len(nonempty) != 1:
        missing.append(f"{label}[found={len(nonempty)}]")


def main():
    args = parse_args()
    with args.participants.open(newline="") as handle:
        participants = list(csv.DictReader(handle, delimiter="\t"))

    required = {"participant_id", "age", "sex", "group"}
    if not participants or not required.issubset(participants[0]):
        raise SystemExit(
            f"ERROR: participants table lacks required columns: {args.participants}"
        )

    audit_rows = []
    retry_rows = []
    for participant in participants:
        subject = normalize_subject(participant["participant_id"])
        subject_root = args.fmriprep_root / f"sub-{subject}"
        func_root = subject_root / "func"
        missing = []

        report = args.fmriprep_root / f"sub-{subject}.html"
        if not report.is_file() or report.stat().st_size == 0:
            missing.append("report")

        for run in ("01", "02"):
            prefix = f"sub-{subject}_task-sharedreward_run-{run}"
            require_one_nonempty(
                func_root,
                f"{prefix}*space-MNI152NLin6Asym*desc-preproc_bold.nii.gz",
                f"run-{run}:preproc_bold",
                missing,
            )
            require_one_nonempty(
                func_root,
                f"{prefix}*space-MNI152NLin6Asym*desc-brain_mask.nii.gz",
                f"run-{run}:brain_mask",
                missing,
            )
            require_one_nonempty(
                func_root,
                f"{prefix}*desc-confounds_timeseries.tsv",
                f"run-{run}:confounds",
                missing,
            )

        status = "complete" if not missing else "incomplete"
        audit_rows.append(
            {
                "subject": subject,
                "status": status,
                "missing": ",".join(missing),
            }
        )
        if missing:
            retry_rows.append(
                {
                    "subject": subject,
                    "age": participant["age"],
                    "sex": participant["sex"],
                    "group": participant["group"],
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("subject", "status", "missing"),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(audit_rows)

    if args.retry_manifest:
        args.retry_manifest.parent.mkdir(parents=True, exist_ok=True)
        with args.retry_manifest.open("w", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=("subject", "age", "sex", "group"),
                delimiter="\t",
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(retry_rows)

    complete = len(audit_rows) - len(retry_rows)
    print(f"Participants checked: {len(audit_rows)}")
    print(f"Complete participants: {complete}")
    print(f"Incomplete participants: {len(retry_rows)}")
    print(f"Audit: {args.output.resolve()}")
    if args.retry_manifest:
        print(f"Retry manifest: {args.retry_manifest.resolve()}")
    for row in audit_rows:
        if row["status"] == "incomplete":
            print(f"INCOMPLETE sub-{row['subject']}: {row['missing']}")

    if args.fail_on_incomplete and retry_rows:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
