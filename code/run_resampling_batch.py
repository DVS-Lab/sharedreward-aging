#!/usr/bin/env python3
"""Resample ds003745 BOLD/mask pairs onto the RF1 grid with bounded concurrency."""

from __future__ import annotations

import argparse
import csv
import os
import shlex
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FIELDS = (
    "subject",
    "run",
    "input_bold",
    "input_mask",
    "output_bold",
    "output_mask",
)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument(
        "--reference",
        type=Path,
        default=Path(
            os.environ.get(
                "REFERENCE_GRID",
                "/ZPOOL/data/projects/rf1-sra-sharedreward/resources/"
                "rf1_MNI152NLin6Asym_reference_grid.nii.gz",
            )
        ),
    )
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--log-dir", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def read_manifest(path):
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if not reader.fieldnames or not set(REQUIRED_FIELDS).issubset(
            reader.fieldnames
        ):
            raise ValueError(
                "manifest lacks required columns: " + ",".join(REQUIRED_FIELDS)
            )
        rows = list(reader)
    seen = set()
    for row in rows:
        key = (row["subject"], row["run"])
        if not all(row[field] for field in REQUIRED_FIELDS):
            raise ValueError(f"empty required value for sub-{key[0]} run-{key[1]}")
        if key in seen:
            raise ValueError(f"duplicate manifest unit: sub-{key[0]} run-{key[1]}")
        seen.add(key)
        for field in ("input_bold", "input_mask"):
            if not Path(row[field]).is_file():
                raise ValueError(f"missing {field}: {row[field]}")
    if not rows:
        raise ValueError("manifest contains no run units")
    return rows


def grid_json_path(output):
    value = str(output)
    if value.endswith(".nii.gz"):
        return Path(value[:-7] + "_grid.json")
    return Path(value + "_grid.json")


def command_string(command):
    return " ".join(shlex.quote(part) for part in command)


def run_unit(row, args):
    subject = row["subject"]
    run = row["run"]
    log_path = args.log_dir / f"sub-{subject}_run-{run}.log"
    env = os.environ.copy()
    env["REFERENCE_GRID"] = str(args.reference.resolve())
    commands = []
    for kind in ("bold", "mask"):
        input_path = row[f"input_{kind}"]
        output_path = Path(row[f"output_{kind}"])
        if output_path.exists() and not args.overwrite:
            command = [
                env.get("IMAGING_PYTHON", "python3"),
                str(ROOT / "code/check_grid.py"),
                "--reference",
                str(args.reference),
                "--image",
                str(output_path),
                "--json-output",
                str(grid_json_path(output_path)),
            ]
            action = "VERIFY EXISTING"
        else:
            command = [
                "bash",
                str(ROOT / "code/resample_to_rf1_grid.sh"),
                "--input",
                input_path,
                "--kind",
                kind,
                "--output",
                str(output_path),
            ]
            if args.overwrite:
                command.append("--overwrite")
            action = "RESAMPLE"
        commands.append((action, command))

    if args.dry_run:
        return subject, run, log_path, commands, None

    args.log_dir.mkdir(parents=True, exist_ok=True)
    with log_path.open("w") as log:
        for action, command in commands:
            log.write(f"{action}: {command_string(command)}\n")
            log.flush()
            result = subprocess.run(
                command,
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
            )
            if result.returncode:
                return subject, run, log_path, commands, result.returncode
    return subject, run, log_path, commands, 0


def main():
    args = parse_args()
    if args.jobs < 1:
        raise SystemExit("ERROR: --jobs must be a positive integer")
    if not args.manifest.is_file():
        raise SystemExit(f"ERROR: manifest not found: {args.manifest}")
    if not args.reference.is_file():
        raise SystemExit(f"ERROR: reference grid not found: {args.reference}")
    try:
        rows = read_manifest(args.manifest)
    except ValueError as error:
        raise SystemExit(f"ERROR: {error}") from error

    print(
        f"RF1-grid resampling plan: {len(rows)} run unit(s), jobs={args.jobs}, "
        f"overwrite={str(args.overwrite).lower()}"
    )
    print(f"Reference: {args.reference.resolve()}")
    print(f"Per-unit logs: {args.log_dir}")

    if args.dry_run:
        for row in rows:
            subject, run, _, commands, _ = run_unit(row, args)
            for action, command in commands:
                print(
                    f"DRY RUN sub-{subject} run-{run} {action}: "
                    f"{command_string(command)}"
                )
        return 0

    failures = []
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = {}
        for row in rows:
            print(f"START: sub-{row['subject']} run-{row['run']}")
            future = executor.submit(run_unit, row, args)
            futures[future] = (row["subject"], row["run"])
        for future in as_completed(futures):
            subject, run = futures[future]
            try:
                _, _, log_path, _, status = future.result()
            except Exception as error:  # defensive boundary for a batch worker
                failures.append((subject, run, str(error)))
                print(f"ERROR: sub-{subject} run-{run}: {error}")
                continue
            if status:
                failures.append((subject, run, f"exit={status}; log={log_path}"))
                print(
                    f"ERROR: failed resampling unit: sub-{subject} run-{run} "
                    f"(log: {log_path})"
                )
            else:
                print(f"DONE: sub-{subject} run-{run}")

    print(f"Run units scheduled: {len(rows)}")
    print(f"Run units completed: {len(rows) - len(failures)}")
    print(f"Run units failed: {len(failures)}")
    if failures:
        return 1
    print(
        "CHECK PASSED: every ds003745 run has verified RF1-grid "
        "BOLD and mask outputs."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
