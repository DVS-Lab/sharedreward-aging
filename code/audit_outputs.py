#!/usr/bin/env python3
"""Audit pooled Shared Reward L1 or subject-level FEAT products."""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def unit_directory(root, dataset, subject, session):
    directory = root / dataset / f"sub-{subject}"
    return directory / f"ses-{session}" if session else directory


def l1_path(root, row, kind, run=None):
    run = str(int(run or row["run"]))
    return unit_directory(root, row["dataset"], row["subject"], row["session"]) / (
        f"L1_task-sharedreward_model-fulltrial_type-{kind}_run-{run}_sm-6.feat"
    )


def l2_path(root, row, kind):
    return unit_directory(root, row["dataset"], row["subject"], row["session"]) / (
        f"L2_task-sharedreward_model-fulltrial_type-{kind}_sm-6.gfeat"
    )


def cope_count(kind):
    return 28 if kind == "act" else 29


def l1_missing(path, ncopes):
    required = ["design.mat", "design.con", "mask.nii.gz", "cluster_mask_zstat1.nii.gz"]
    required.extend(f"stats/cope{number}.nii.gz" for number in range(1, ncopes + 1))
    required.extend(f"stats/zstat{number}.nii.gz" for number in range(1, ncopes + 1))
    return [relative for relative in required if not (path / relative).is_file()]


def l2_missing(path, ncopes):
    missing = []
    for number in range(1, ncopes + 1):
        prefix = path / f"cope{number}.feat"
        for relative in ("design.mat", "design.con", "stats/cope1.nii.gz", "stats/zstat1.nii.gz", "cluster_mask_zstat1.nii.gz"):
            if not (prefix / relative).is_file():
                missing.append(f"cope{number}.feat/{relative}")
    return missing


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--level", choices=("l1", "subject"), required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--type", required=True, dest="kind")
    parser.add_argument(
        "--fsl-root",
        type=Path,
        default=Path(os.environ.get("FSL_DERIVATIVES_ROOT", ROOT / "derivatives/fsl")),
    )
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.kind != "act" and not args.kind.startswith("ppi_seed-"):
        parser.error("--type must be act or ppi_seed-<seed>")
    with args.manifest.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    required = {"dataset", "subject", "session", *( ["run"] if args.level == "l1" else ["n_runs", "runs"] )}
    if not rows or not required.issubset(rows[0]):
        parser.error("manifest contract is incomplete")
    ncopes = cope_count(args.kind)
    report = []
    for row in rows:
        strategy = "l1"
        if args.level == "l1":
            output = l1_path(args.fsl_root, row, args.kind)
            missing = l1_missing(output, ncopes)
        else:
            runs = [value for value in row["runs"].split(",") if value]
            if int(row["n_runs"]) == 1:
                strategy = "l1_passthrough"
                output = l1_path(args.fsl_root, row, args.kind, runs[0])
                missing = l1_missing(output, ncopes)
            elif int(row["n_runs"]) == 2:
                strategy = "fixed_effects"
                output = l2_path(args.fsl_root, row, args.kind)
                missing = l2_missing(output, ncopes)
            else:
                output = Path("")
                missing = ["invalid_run_count"]
        if args.kind.startswith("ppi_seed-") and args.level == "l1":
            seed = args.kind.removeprefix("ppi_seed-")
            series = output.parent / f"ts_task-sharedreward_mask-{seed}_run-{int(row['run'])}.txt"
            if not series.is_file() or series.stat().st_size == 0:
                missing.append(f"time-series:{series}")
        if missing:
            report.append(
                {
                    "dataset": row["dataset"],
                    "subject": row["subject"],
                    "session": row["session"],
                    "run": row.get("run", ""),
                    "strategy": strategy,
                    "type": args.kind,
                    "output": str(output),
                    "missing": ",".join(missing),
                }
            )
    fields = ("dataset", "subject", "session", "run", "strategy", "type", "output", "missing")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(report)
    print(f"Manifest units checked: {len(rows)}")
    print(f"Fully complete units: {len(rows) - len(report)}")
    print(f"Incomplete units: {len(report)}")
    print(f"Completeness report: {args.output.resolve()}")
    if report:
        print(f"CHECK FAILED: {len(report)} unit(s) are incomplete.")
        return 1
    print(f"CHECK PASSED: all {len(rows)} {args.level} {args.kind} unit(s) are complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
