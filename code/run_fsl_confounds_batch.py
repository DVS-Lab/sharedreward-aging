#!/usr/bin/env python3
"""Generate ds003745 FSL nuisance matrices with bounded concurrency."""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


SCRIPT = Path(__file__).with_name("generate_fsl_confounds.py")


def valid_existing(row):
    return all(
        Path(row[field]).is_file() and Path(row[field]).stat().st_size > 0
        for field in ("output_confounds", "output_metadata")
    )


def run_one(row, overwrite, log_dir):
    label = f"ds003745_sub-{row['subject']}_run-{row['run']}"
    if valid_existing(row) and not overwrite:
        return label, "verified existing", 0
    command = [
        sys.executable,
        str(SCRIPT),
        "--input",
        row["input_confounds"],
        "--output",
        row["output_confounds"],
        "--metadata",
        row["output_metadata"],
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / f"{label}.log").write_text(result.stdout + result.stderr)
    return label, "completed" if result.returncode == 0 else "failed", result.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--log-dir", required=True, type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    with args.manifest.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    required = {"subject", "run", "input_confounds", "output_confounds", "output_metadata"}
    if not rows or not required.issubset(rows[0]):
        raise SystemExit("ERROR: FSL nuisance manifest contract is incomplete")
    failures = 0
    counts = {"completed": 0, "verified existing": 0}
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = {
            executor.submit(run_one, row, args.overwrite, args.log_dir): row
            for row in rows
        }
        for future in as_completed(futures):
            label, status, code = future.result()
            print(f"{status.upper()}: {label}", flush=True)
            if code:
                failures += 1
            else:
                counts[status] += 1
    print(f"Units scheduled: {len(rows)}")
    print(f"Units newly completed: {counts['completed']}")
    print(f"Units verified existing: {counts['verified existing']}")
    print(f"Units failed: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
