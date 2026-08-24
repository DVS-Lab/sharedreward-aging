#!/usr/bin/env python3
"""Apply FEAT-equivalent SUSAN and measure all comparison images with AFNI."""

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
REQUIRED = (
    "dataset", "subject", "session", "run", "baseline_bold", "input_mask",
    "afni_target_bold", "susan_output_bold", "susan_metadata", "baseline_qc",
    "afni_target_qc", "susan_output_qc", "kernel_fwhm_mm",
)
NUMERIC = ("classic_fwhm_x", "classic_fwhm_y", "classic_fwhm_z", "classic_fwhm_combined", "acf_a", "acf_b", "acf_c", "acf_effective_fwhm")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--log-dir", required=True, type=Path)
    parser.add_argument("--work-root", type=Path, default=ROOT / "work/susan-comparison")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def command_text(command):
    return " ".join(shlex.quote(value) for value in command)


def read_qc(path, expected_input, mask):
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"missing QC: {path}")
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 1:
        raise ValueError(f"expected one QC row in {path}; found {len(rows)}")
    row = rows[0]
    if Path(row.get("input", "")).resolve() != Path(expected_input).resolve():
        raise ValueError(f"QC input mismatch: {path}")
    if Path(row.get("mask", "")).resolve() != Path(mask).resolve():
        raise ValueError(f"QC mask mismatch: {path}")
    for field in NUMERIC:
        if float(row[field]) <= 0:
            raise ValueError(f"invalid {field} in {path}")


def validate_susan_metadata(path, row):
    path = Path(path)
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"missing SUSAN metadata: {path}")
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 1:
        raise ValueError(f"expected one metadata row; found {len(rows)}")
    metadata = rows[0]
    contracts = (
        ("input", "baseline_bold"),
        ("mask", "input_mask"),
        ("output", "susan_output_bold"),
    )
    for metadata_field, manifest_field in contracts:
        if Path(metadata.get(metadata_field, "")).resolve() != Path(row[manifest_field]).resolve():
            raise ValueError(f"SUSAN metadata {metadata_field} contract mismatch")
    if abs(float(metadata["kernel_fwhm_mm"]) - float(row["kernel_fwhm_mm"])) > 1e-9:
        raise ValueError("SUSAN metadata kernel contract mismatch")
    for field in ("spatial_sigma_mm", "masked_median", "brightness_threshold"):
        if float(metadata[field]) <= 0:
            raise ValueError(f"invalid SUSAN metadata {field}")


def measure(image, mask, qc, work_root, environment, log, overwrite):
    qc = Path(qc)
    if qc.exists() and not overwrite:
        read_qc(qc, image, mask); return "verified"
    qc.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=f".{qc.stem}.", suffix=".tsv", dir=qc.parent)
    os.close(descriptor); temporary = Path(name)
    command = ["bash", str(ROOT / "code/measure_smoothness.sh"), "--input", image, "--mask", mask, "--output-tsv", str(temporary), "--work-dir", str(work_root)]
    try:
        log.write(f"COMMAND: {command_text(command)}\n"); log.flush()
        result = subprocess.run(command, env=environment, stdout=log, stderr=subprocess.STDOUT, text=True)
        if result.returncode:
            raise RuntimeError(f"smoothness measurement exit={result.returncode}")
        read_qc(temporary, image, mask); os.replace(temporary, qc); return "completed"
    finally:
        temporary.unlink(missing_ok=True)


def run_unit(row, args):
    session = f"_ses-{row['session']}" if row["session"] else ""
    label = f"{row['dataset']}_sub-{row['subject']}{session}_run-{row['run']}"
    log_path = args.log_dir / f"{label}.log"
    output = Path(row["susan_output_bold"]); metadata = Path(row["susan_metadata"])
    environment = os.environ.copy(); environment.setdefault("AFNI_OMP_NUM_THREADS", "4")
    args.log_dir.mkdir(parents=True, exist_ok=True); args.work_root.mkdir(parents=True, exist_ok=True)
    try:
        with log_path.open("w") as log:
            if (output.exists() or metadata.exists()) and not args.overwrite:
                if not output.is_file() or not metadata.is_file():
                    raise ValueError("partial SUSAN output/metadata pair; review and use --overwrite")
                validate_susan_metadata(metadata, row)
                log.write("VERIFIED EXISTING SUSAN output/metadata pair\n")
            else:
                command = ["bash", str(ROOT / "code/smooth_with_feat_susan.sh"), "--input", row["baseline_bold"], "--mask", row["input_mask"], "--output", row["susan_output_bold"], "--kernel-fwhm", row["kernel_fwhm_mm"], "--metadata-tsv", row["susan_metadata"], "--work-dir", str(args.work_root)]
                if args.overwrite: command.append("--overwrite")
                log.write(f"COMMAND: {command_text(command)}\n"); log.flush()
                result = subprocess.run(command, env=environment, stdout=log, stderr=subprocess.STDOUT, text=True)
                if result.returncode: raise RuntimeError(f"SUSAN exit={result.returncode}")
                validate_susan_metadata(metadata, row)
            for image_field, qc_field in (("baseline_bold", "baseline_qc"), ("afni_target_bold", "afni_target_qc"), ("susan_output_bold", "susan_output_qc")):
                measure(row[image_field], row["input_mask"], row[qc_field], args.work_root, environment, log, args.overwrite)
        return label, log_path, None
    except Exception as error:
        return label, log_path, str(error)


def main():
    args = parse_args()
    if args.jobs < 1: raise SystemExit("ERROR: --jobs must be positive")
    with args.manifest.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if not reader.fieldnames or not set(REQUIRED).issubset(reader.fieldnames):
            raise SystemExit("ERROR: comparison manifest contract is incomplete")
        rows = list(reader)
    if not rows: raise SystemExit("ERROR: no comparison units")
    for row in rows:
        for field in ("baseline_bold", "input_mask", "afni_target_bold"):
            if not Path(row[field]).is_file(): raise SystemExit(f"ERROR: missing {field}: {row[field]}")
    print(f"SUSAN comparison plan: {len(rows)} unit(s), jobs={args.jobs}")
    failures = []
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = [executor.submit(run_unit, row, args) for row in rows]
        for future in as_completed(futures):
            label, log_path, error = future.result()
            if error:
                failures.append(label); print(f"ERROR: {label}: {error} (log: {log_path})")
            else: print(f"DONE: {label}")
    print(f"Units completed: {len(rows)-len(failures)}")
    print(f"Units failed: {len(failures)}")
    if failures: return 1
    print("CHECK PASSED: all SUSAN comparison images and AFNI measurements are complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
