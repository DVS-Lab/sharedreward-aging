#!/usr/bin/env python3
"""Compute post-smoothing tSNR, motion, and fixed-mask coverage in parallel."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import statistics
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IDENTIFIERS = ("dataset", "subject", "session", "run")
REQUIRED_FIELDS = IDENTIFIERS + (
    "input_bold",
    "input_mask",
    "reference_mask",
    "confounds",
    "output_json",
)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--log-dir", required=True, type=Path)
    parser.add_argument("--high-motion-fd", type=float, default=0.5)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def numeric(value):
    if value is None or value.strip().lower() in {"", "n/a", "na", "nan"}:
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def confound_metrics(path, n_volumes, threshold):
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)
        fields = reader.fieldnames or []
    if len(rows) != n_volumes:
        raise ValueError(f"confound_rows={len(rows)} but n_volumes={n_volumes}")
    if "framewise_displacement" not in fields:
        raise ValueError("missing framewise_displacement column")
    fd = [numeric(row["framewise_displacement"]) for row in rows]
    fd_values = [value for value in fd if value is not None]
    if not fd_values:
        raise ValueError("no finite framewise_displacement values")
    high_motion = sum(value > threshold for value in fd_values)
    dvars_values = []
    if "std_dvars" in fields:
        dvars_values = [
            value
            for value in (numeric(row["std_dvars"]) for row in rows)
            if value is not None
        ]
    nonsteady_fields = [field for field in fields if field.startswith("non_steady_state_outlier")]
    nonsteady_volumes = sum(
        any((numeric(row.get(field)) or 0) > 0 for field in nonsteady_fields)
        for row in rows
    )
    return {
        "confounds_rows": len(rows),
        "confounds_format": "named_fmriprep_timeseries",
        "fd_valid_values": len(fd_values),
        "mean_fd_mm": statistics.mean(fd_values),
        "median_fd_mm": statistics.median(fd_values),
        "max_fd_mm": max(fd_values),
        "high_motion_fd_threshold_mm": threshold,
        "high_motion_volumes": high_motion,
        "high_motion_fraction": high_motion / n_volumes,
        "nonsteady_state_volumes": nonsteady_volumes,
        "mean_std_dvars": statistics.mean(dvars_values) if dvars_values else None,
        "max_std_dvars": max(dvars_values) if dvars_values else None,
    }


def validate_result(path, unit):
    data = json.loads(path.read_text())
    contracts = (
        ("input", "input_bold"),
        ("mask", "input_mask"),
        ("reference_mask", "reference_mask"),
        ("confounds", "confounds"),
    )
    for result_field, unit_field in contracts:
        if Path(data[result_field]).resolve() != Path(unit[unit_field]).resolve():
            raise ValueError(f"{result_field}_contract")
    for field in IDENTIFIERS:
        if str(data[field]) != str(unit[field]):
            raise ValueError(f"{field}_contract")
    positive = (
        "n_volumes",
        "tr_seconds",
        "reference_mask_voxels",
        "analysis_mask_voxels",
        "valid_voxels",
        "median_tsnr",
    )
    for field in positive:
        if float(data[field]) <= 0:
            raise ValueError(f"nonpositive_{field}")
    for field in ("coverage_pct", "valid_coverage_pct"):
        if not 0 < float(data[field]) <= 100:
            raise ValueError(f"invalid_{field}")
    if int(data["confounds_rows"]) != int(data["n_volumes"]):
        raise ValueError("confound_volume_contract")
    if data.get("confounds_format", "named_fmriprep_timeseries") != "named_fmriprep_timeseries":
        raise ValueError("confound_format_contract")
    return data


def run_unit(unit, args):
    label = (
        f"{unit['dataset']}_sub-{unit['subject']}_"
        f"ses-{unit['session'] or 'none'}_run-{unit['run']}"
    )
    output = Path(unit["output_json"])
    log = args.log_dir / f"{label}.log"
    if output.is_file() and not args.overwrite:
        try:
            data = validate_result(output, unit)
            if int(data.get("qc_definition_version", 1)) < 2:
                data.update(
                    confound_metrics(
                        Path(unit["confounds"]),
                        int(data["n_volumes"]),
                        args.high_motion_fd,
                    )
                )
                data["qc_definition_version"] = 2
                temporary = output.with_name(f".{output.name}.upgrade-{os.getpid()}")
                temporary.write_text(json.dumps(data, indent=2) + "\n")
                validate_result(temporary, unit)
                os.replace(temporary, output)
                return label, "completed", "upgraded QC provenance without rereading BOLD"
            return label, "existing", ""
        except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
            return label, "failed", f"invalid existing output ({error}); review and use --overwrite"
    output.parent.mkdir(parents=True, exist_ok=True)
    args.log_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    temporary = tempfile.NamedTemporaryFile(
        prefix=output.stem + ".", suffix=".json", dir=output.parent, delete=False
    )
    temporary.close()
    temp_path = Path(temporary.name)
    try:
        command = [
            sys.executable,
            str(ROOT / "code/compute_tsnr.py"),
            "--input",
            unit["input_bold"],
            "--mask",
            unit["input_mask"],
            "--reference-mask",
            unit["reference_mask"],
            "--output-json",
            str(temp_path),
            "--dataset",
            unit["dataset"],
            "--subject",
            unit["subject"],
            "--session",
            unit["session"],
            "--run",
            unit["run"],
            "--stage",
            "post_target_blur",
        ]
        completed = subprocess.run(command, capture_output=True, text=True)
        log.write_text(
            "COMMAND: " + " ".join(command) + "\n\n" + completed.stdout + completed.stderr
        )
        if completed.returncode:
            raise RuntimeError(f"tSNR command exit={completed.returncode}")
        data = json.loads(temp_path.read_text())
        data.update(
            {
                field: unit[field] for field in IDENTIFIERS
            }
        )
        data["confounds"] = str(Path(unit["confounds"]).resolve())
        data.update(
            confound_metrics(
                Path(unit["confounds"]), int(data["n_volumes"]), args.high_motion_fd
            )
        )
        data["runtime_seconds"] = time.monotonic() - started
        data["qc_definition_version"] = 2
        temp_path.write_text(json.dumps(data, indent=2) + "\n")
        validate_result(temp_path, unit)
        os.replace(temp_path, output)
        return label, "completed", ""
    except Exception as error:
        if not log.exists():
            log.write_text(f"ERROR: {error}\n")
        else:
            with log.open("a") as handle:
                handle.write(f"\nERROR: {error}\n")
        return label, "failed", str(error)
    finally:
        temp_path.unlink(missing_ok=True)


def main():
    args = parse_args()
    if args.jobs < 1:
        raise SystemExit("ERROR: --jobs must be positive")
    if args.high_motion_fd <= 0:
        raise SystemExit("ERROR: --high-motion-fd must be positive")
    with args.manifest.open(newline="") as handle:
        manifest = list(csv.DictReader(handle, delimiter="\t"))
    if not manifest or not set(REQUIRED_FIELDS).issubset(manifest[0]):
        raise SystemExit("ERROR: analysis-QC manifest contract is incomplete")
    print(
        f"Analysis-QC plan: {len(manifest)} unit(s), jobs={args.jobs}, "
        f"high-motion FD>{args.high_motion_fd:g} mm, overwrite={str(args.overwrite).lower()}"
    )
    print(f"Per-unit logs: {args.log_dir}")
    counts = {"completed": 0, "existing": 0, "failed": 0}
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = {executor.submit(run_unit, unit, args): unit for unit in manifest}
        for future in as_completed(futures):
            label, status, detail = future.result()
            counts[status] += 1
            if status == "failed":
                print(f"ERROR: {label}: {detail}")
            else:
                print(f"{status.upper()}: {label}")
    print(f"Units scheduled: {len(manifest)}")
    print(f"Units newly completed: {counts['completed']}")
    print(f"Units verified existing: {counts['existing']}")
    print(f"Units failed: {counts['failed']}")
    if not counts["failed"]:
        print("CHECK PASSED: every analysis-QC JSON is complete and contract-valid.")
    return 1 if counts["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
