#!/usr/bin/env python3
"""Run measured target smoothing with bounded concurrency and safe restart."""

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
NUMERIC_FIELDS = (
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
    parser.add_argument("--log-dir", required=True, type=Path)
    parser.add_argument(
        "--work-root",
        type=Path,
        default=ROOT / "work/target-smoothing",
    )
    parser.add_argument("--tolerance-fraction", type=float, default=0.10)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--all-blurmaster",
        action="store_true",
        help=(
            "Pass AFNI -bmall so convergence uses every blurmaster volume. "
            "Reserve for reviewed run-level convergence exceptions."
        ),
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def unit_label(row):
    session = f"_ses-{row['session']}" if row["session"] else ""
    return f"{row['dataset']}_sub-{row['subject']}{session}_run-{row['run']}"


def read_manifest(path):
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if not reader.fieldnames or not set(REQUIRED_FIELDS).issubset(
            reader.fieldnames
        ):
            raise ValueError("manifest lacks required columns: " + ",".join(REQUIRED_FIELDS))
        rows = list(reader)
    if not rows:
        raise ValueError("manifest contains no target-smoothing units")
    seen = set()
    for row in rows:
        key = tuple(row[field] for field in REQUIRED_FIELDS[:4])
        if key in seen:
            raise ValueError(f"duplicate target-smoothing unit: {key}")
        seen.add(key)
        for field in ("input_bold", "input_mask"):
            if not Path(row[field]).is_file():
                raise ValueError(f"missing {field}: {row[field]}")
        try:
            target = float(row["target_fwhm_mm"])
        except ValueError as error:
            raise ValueError(f"invalid target for {key}") from error
        if target <= 0:
            raise ValueError(f"non-positive target for {key}")
        label = (f"{target:g}").replace(".", "p")
        if f"smoothToFWHM{label}" not in Path(row["output_bold"]).name:
            raise ValueError(f"output does not encode target for {key}")
        if Path(row["output_bold"]).resolve() == Path(row["input_bold"]).resolve():
            raise ValueError(f"output would overwrite input for {key}")
    return rows


def validate_result(row, tolerance):
    output = Path(row["output_bold"])
    qc = Path(row["output_qc"])
    if not output.is_file() or output.stat().st_size == 0:
        raise ValueError("missing output BOLD")
    if not qc.is_file() or qc.stat().st_size == 0:
        raise ValueError("missing output QC")
    with qc.open(newline="") as handle:
        results = list(csv.DictReader(handle, delimiter="\t"))
    if len(results) != 1:
        raise ValueError(f"expected one QC row; found {len(results)}")
    result = results[0]
    if Path(result.get("input", "")).resolve() != output.resolve():
        raise ValueError("QC input does not identify output BOLD")
    if Path(result.get("mask", "")).resolve() != Path(row["input_mask"]).resolve():
        raise ValueError("QC mask contract mismatch")
    for field in NUMERIC_FIELDS:
        try:
            value = float(result[field])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"invalid {field}") from error
        if value <= 0:
            raise ValueError(f"non-positive {field}: {value}")
    target = float(row["target_fwhm_mm"])
    achieved = float(result["classic_fwhm_combined"])
    lower, upper = target * (1 - tolerance), target * (1 + tolerance)
    if not lower <= achieved <= upper:
        raise ValueError(
            f"classic combined {achieved:g} outside {lower:g}-{upper:g} mm"
        )
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
    output = Path(row["output_bold"])
    qc = Path(row["output_qc"])
    log_path = args.log_dir / f"{label}.log"
    exists = output.exists() or qc.exists()
    if exists and not args.overwrite:
        try:
            validate_result(row, args.tolerance_fraction)
        except ValueError as error:
            return label, log_path, "invalid", f"{error}; review, then use --overwrite"
        return label, log_path, "verified", ""

    command = [
        "bash",
        str(ROOT / "code/smooth_to_target.sh"),
        "--input",
        row["input_bold"],
        "--mask",
        row["input_mask"],
        "--output",
        row["output_bold"],
        "--target",
        row["target_fwhm_mm"],
        "--qc-tsv",
        row["output_qc"],
        "--work-dir",
        str(args.work_root),
    ]
    if args.overwrite:
        command.append("--overwrite")
    if args.all_blurmaster:
        command.append("--all-blurmaster")
    if args.dry_run:
        return label, log_path, "dry-run", command_string(command)

    args.log_dir.mkdir(parents=True, exist_ok=True)
    args.work_root.mkdir(parents=True, exist_ok=True)
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
            return label, log_path, "failed", f"exit={result.returncode}"
        validate_result(row, args.tolerance_fraction)
        return label, log_path, "completed", ""
    except Exception as error:
        return label, log_path, "failed", str(error)


def main():
    args = parse_args()
    if args.jobs < 1:
        raise SystemExit("ERROR: --jobs must be a positive integer")
    if not 0 < args.tolerance_fraction < 1:
        raise SystemExit("ERROR: --tolerance-fraction must be between zero and one")
    if not args.manifest.is_file():
        raise SystemExit(f"ERROR: manifest not found: {args.manifest}")
    try:
        rows = read_manifest(args.manifest)
    except ValueError as error:
        raise SystemExit(f"ERROR: {error}") from error

    print(
        f"Target-smoothing plan: {len(rows)} unit(s), jobs={args.jobs}, "
        f"AFNI threads/job={os.environ.get('AFNI_OMP_NUM_THREADS', '4')}, "
        f"tolerance=±{args.tolerance_fraction * 100:g}%, "
        f"all-blurmaster={str(args.all_blurmaster).lower()}, "
        f"overwrite={str(args.overwrite).lower()}"
    )
    print(f"Per-unit logs: {args.log_dir}")
    if args.dry_run:
        invalid = 0
        for row in rows:
            label, _, status, detail = run_unit(row, args)
            if status == "verified":
                print(f"DRY RUN {label}: VERIFIED EXISTING")
            elif status == "dry-run":
                print(f"DRY RUN {label}: {detail}")
            else:
                invalid += 1
                print(f"ERROR: {label}: {status}: {detail}")
        return 1 if invalid else 0

    failures = []
    completed = 0
    verified = 0
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = {executor.submit(run_unit, row, args): row for row in rows}
        for future in as_completed(futures):
            label, log_path, status, detail = future.result()
            if status == "completed":
                completed += 1
                print(f"DONE: {label}")
            elif status == "verified":
                verified += 1
                print(f"VERIFIED EXISTING: {label}")
            else:
                failures.append((label, status, detail, log_path))
                print(f"ERROR: {label}: {status}: {detail} (log: {log_path})")
                for line in log_tail(log_path):
                    print(f"  {line}")
    print(f"Units scheduled: {len(rows)}")
    print(f"Units newly completed: {completed}")
    print(f"Units verified existing: {verified}")
    print(f"Units failed: {len(failures)}")
    if failures:
        return 1
    print("CHECK PASSED: every target-smoothed unit has valid achieved-smoothness QC.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
