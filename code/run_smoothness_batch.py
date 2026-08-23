#!/usr/bin/env python3
"""Measure Phase 0 baseline smoothness with bounded, restartable AFNI jobs."""

from __future__ import annotations

import argparse
import csv
import os
import shlex
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FIELDS = (
    "dataset",
    "subject",
    "session",
    "run",
    "stage",
    "input_bold",
    "input_mask",
)
RESULT_NUMERIC_FIELDS = (
    "classic_fwhm_x",
    "classic_fwhm_y",
    "classic_fwhm_z",
    "classic_fwhm_combined",
    "acf_a",
    "acf_b",
    "acf_c",
    "acf_effective_fwhm",
)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "derivatives/qc/smoothness/run-level",
    )
    parser.add_argument("--log-dir", required=True, type=Path)
    parser.add_argument(
        "--work-root",
        type=Path,
        default=ROOT / "work/phase0-smoothness",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def unit_label(row):
    session = f"_ses-{row['session']}" if row["session"] else ""
    return (
        f"{row['dataset']}_sub-{row['subject']}{session}_run-{row['run']}_"
        f"stage-{row['stage']}"
    )


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
        key = tuple(row[field] for field in REQUIRED_FIELDS[:5])
        if key in seen:
            raise ValueError(f"duplicate characterization unit: {key}")
        seen.add(key)
        for field in ("input_bold", "input_mask"):
            if not Path(row[field]).is_file():
                raise ValueError(f"missing {field}: {row[field]}")
    if not rows:
        raise ValueError("manifest contains no characterization units")
    return rows


def read_valid_result(path, row):
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError("missing result")
    with path.open(newline="") as handle:
        results = list(csv.DictReader(handle, delimiter="\t"))
    if len(results) != 1:
        raise ValueError(f"expected one result row; found {len(results)}")
    result = results[0]
    expected_input = Path(row["input_bold"]).resolve()
    expected_mask = Path(row["input_mask"]).resolve()
    actual_input = Path(result.get("input", "")).resolve()
    actual_mask = Path(result.get("mask", "")).resolve()
    if actual_input != expected_input or actual_mask != expected_mask:
        raise ValueError(
            "result input/mask contract mismatch: "
            f"input={str(actual_input)!r} expected={str(expected_input)!r}; "
            f"mask={str(actual_mask)!r} expected={str(expected_mask)!r}"
        )
    for field in RESULT_NUMERIC_FIELDS:
        try:
            value = float(result[field])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"invalid {field}") from error
        if value <= 0:
            raise ValueError(f"non-positive {field}: {value}")
    return result


def command_string(command):
    return " ".join(shlex.quote(part) for part in command)


def log_tail(path, lines=20):
    try:
        content = path.read_text(errors="replace").splitlines()
    except OSError as error:
        return [f"unable to read per-unit log: {error}"]
    return content[-lines:] or ["per-unit log is empty"]


def run_unit(row, args):
    label = unit_label(row)
    output = args.output_dir / f"{label}.tsv"
    log_path = args.log_dir / f"{label}.log"
    if output.exists() and not args.overwrite:
        try:
            read_valid_result(output, row)
        except ValueError as error:
            return label, output, log_path, "invalid", str(error)
        return label, output, log_path, "verified", ""

    command_display = [
        "bash",
        str(ROOT / "code/measure_smoothness.sh"),
        "--input",
        row["input_bold"],
        "--mask",
        row["input_mask"],
        "--output-tsv",
        "<atomic-temp-tsv>",
        "--work-dir",
        str(args.work_root),
    ]
    if args.dry_run:
        return label, output, log_path, "dry-run", command_string(command_display)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.log_dir.mkdir(parents=True, exist_ok=True)
    args.work_root.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{label}.", suffix=".tsv", dir=args.output_dir
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    command = command_display.copy()
    command[command.index("<atomic-temp-tsv>")] = str(temporary)
    environment = os.environ.copy()
    environment.setdefault("AFNI_OMP_NUM_THREADS", "4")
    try:
        with log_path.open("w") as log:
            log.write(f"COMMAND: {command_string(command)}\n")
            log.flush()
            result = subprocess.run(
                command,
                env=environment,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
            )
        if result.returncode:
            return label, output, log_path, "failed", f"exit={result.returncode}"
        read_valid_result(temporary, row)
        os.replace(temporary, output)
        return label, output, log_path, "completed", ""
    except Exception as error:
        return label, output, log_path, "failed", str(error)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    args = parse_args()
    if args.jobs < 1:
        raise SystemExit("ERROR: --jobs must be a positive integer")
    if not args.manifest.is_file():
        raise SystemExit(f"ERROR: manifest not found: {args.manifest}")
    try:
        rows = read_manifest(args.manifest)
    except ValueError as error:
        raise SystemExit(f"ERROR: {error}") from error

    print(
        f"Baseline smoothness plan: {len(rows)} unit(s), jobs={args.jobs}, "
        f"AFNI threads/job={os.environ.get('AFNI_OMP_NUM_THREADS', '4')}, "
        f"overwrite={str(args.overwrite).lower()}"
    )
    print(f"Run-level results: {args.output_dir}")
    print(f"Per-unit logs: {args.log_dir}")
    if args.dry_run:
        for row in rows:
            label, _, _, _, command = run_unit(row, args)
            print(f"DRY RUN {label}: {command}")
        return 0

    failures = []
    completed = 0
    verified = 0
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = {executor.submit(run_unit, row, args): row for row in rows}
        for future in as_completed(futures):
            label, _, log_path, status, detail = future.result()
            if status == "completed":
                completed += 1
                print(f"DONE: {label}")
            elif status == "verified":
                verified += 1
                print(f"VERIFIED EXISTING: {label}")
            else:
                failures.append((label, status, detail, log_path))
                print(
                    f"ERROR: {label}: {status}: {detail} "
                    f"(log: {log_path})"
                )
                print(f"LOG TAIL: {label}")
                for line in log_tail(log_path):
                    print(f"  {line}")
    print(f"Units scheduled: {len(rows)}")
    print(f"Units newly completed: {completed}")
    print(f"Units verified existing: {verified}")
    print(f"Units failed: {len(failures)}")
    if failures:
        return 1
    print("CHECK PASSED: every baseline smoothness unit has a validated result.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
