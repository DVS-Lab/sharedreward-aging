#!/usr/bin/env python3
"""Audit and summarize post-smoothing tSNR, motion, and common-mask coverage."""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path


IDENTIFIERS = ("dataset", "subject", "session", "run")
METRICS = ("median_tsnr", "mean_fd_mm", "high_motion_fraction", "coverage_pct")
OUTPUT_FIELDS = IDENTIFIERS + (
    "stage",
    "input",
    "mask",
    "reference_mask",
    "coverage_mask",
    "confounds",
    "confounds_format",
    "confounds_rows",
    "fd_valid_values",
    "n_volumes",
    "tr_seconds",
    "run_mask_voxels",
    "reference_mask_voxels",
    "analysis_mask_voxels",
    "valid_voxels",
    "tsnr_reference_coverage_pct",
    "tsnr_valid_coverage_pct",
    "coverage_mask_voxels",
    "coverage_overlap_voxels",
    "coverage_pct",
    "coverage_definition",
    "valid_coverage_pct",
    "mean_tsnr",
    "median_tsnr",
    "mean_fd_mm",
    "median_fd_mm",
    "max_fd_mm",
    "high_motion_fd_threshold_mm",
    "high_motion_volumes",
    "high_motion_fraction",
    "nonsteady_state_volumes",
    "mean_std_dvars",
    "max_std_dvars",
    "qc_flags",
)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--summary-output", required=True, type=Path)
    parser.add_argument("--subject-output", required=True, type=Path)
    parser.add_argument("--missing-output", required=True, type=Path)
    parser.add_argument(
        "--coverage-warning-pct",
        type=float,
        help="Optional descriptive flag; not part of the preregistered IQR exclusions.",
    )
    parser.add_argument(
        "--high-motion-warning-fraction",
        type=float,
        help="Optional descriptive flag; not part of the preregistered IQR exclusions.",
    )
    parser.add_argument("--iqr-multiplier", type=float, default=1.5)
    parser.add_argument("--fail-on-incomplete", action="store_true")
    parser.add_argument("--fail-on-qc-flags", action="store_true")
    return parser.parse_args()


def write_tsv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def percentile(values, fraction):
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def metric_summary(dataset, metric, values, iqr_multiplier):
    q1 = percentile(values, 0.25)
    q3 = percentile(values, 0.75)
    iqr = q3 - q1
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    return {
        "dataset": dataset,
        "metric": metric,
        "n_runs": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "sd": sd,
        "sem": sd / math.sqrt(len(values)),
        "minimum": min(values),
        "q1": q1,
        "q3": q3,
        "maximum": max(values),
        "iqr_lower": q1 - iqr_multiplier * iqr,
        "iqr_upper": q3 + iqr_multiplier * iqr,
    }


def validate_json(path, unit):
    data = json.loads(path.read_text())
    for field in IDENTIFIERS:
        if str(data[field]) != str(unit[field]):
            raise ValueError(f"{field}_contract")
    for result_field, manifest_field in (
        ("input", "input_bold"),
        ("mask", "input_mask"),
        ("reference_mask", "reference_mask"),
        ("coverage_mask", "coverage_mask"),
        ("confounds", "confounds"),
    ):
        if Path(data[result_field]).resolve() != Path(unit[manifest_field]).resolve():
            raise ValueError(f"{result_field}_contract")
    if int(data["confounds_rows"]) != int(data["n_volumes"]):
        raise ValueError("confound_volume_contract")
    if data["confounds_format"] != "named_fmriprep_timeseries":
        raise ValueError("confound_format_contract")
    for field in (
        "median_tsnr",
        "mean_tsnr",
        "n_volumes",
        "tr_seconds",
        "coverage_mask_voxels",
        "coverage_overlap_voxels",
    ):
        if float(data[field]) <= 0:
            raise ValueError(f"nonpositive_{field}")
    for field in ("coverage_pct", "valid_coverage_pct"):
        if not 0 < float(data[field]) <= 100:
            raise ValueError(f"invalid_{field}")
    return data


def main():
    args = parse_args()
    if args.coverage_warning_pct is not None and not 0 < args.coverage_warning_pct <= 100:
        raise SystemExit("ERROR: --coverage-warning-pct must be in (0, 100]")
    if (
        args.high_motion_warning_fraction is not None
        and not 0 <= args.high_motion_warning_fraction <= 1
    ):
        raise SystemExit("ERROR: --high-motion-warning-fraction must be in [0, 1]")
    if args.iqr_multiplier <= 0:
        raise SystemExit("ERROR: --iqr-multiplier must be positive")
    with args.manifest.open(newline="") as handle:
        manifest = list(csv.DictReader(handle, delimiter="\t"))
    required = set(IDENTIFIERS) | {
        "input_bold",
        "input_mask",
        "reference_mask",
        "coverage_mask",
        "confounds",
        "output_json",
    }
    if not manifest or not required.issubset(manifest[0]):
        raise SystemExit("ERROR: analysis-QC manifest contract is incomplete")

    complete, missing = [], []
    for unit in manifest:
        identifiers = {field: unit[field] for field in IDENTIFIERS}
        output = Path(unit["output_json"])
        if not output.is_file() or output.stat().st_size == 0:
            missing.append({**identifiers, "problems": "missing_output_json"})
            continue
        try:
            data = validate_json(output, unit)
            complete.append(
                {
                    field: ("" if data.get(field) is None else data.get(field, ""))
                    for field in OUTPUT_FIELDS[:-1]
                }
            )
        except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
            missing.append({**identifiers, "problems": f"invalid_output_json:{error}"})

    summaries = []
    thresholds = {}
    for dataset in sorted({row["dataset"] for row in complete}):
        subset = [row for row in complete if row["dataset"] == dataset]
        for metric in METRICS:
            values = [float(row[metric]) for row in subset]
            summary = metric_summary(dataset, metric, values, args.iqr_multiplier)
            summaries.append(summary)
            thresholds[(dataset, metric)] = summary

    flagged = []
    for row in complete:
        flags = []
        if (
            args.coverage_warning_pct is not None
            and float(row["coverage_pct"]) < args.coverage_warning_pct
        ):
            flags.append(f"coverage_below_{args.coverage_warning_pct:g}pct")
        if (
            args.high_motion_warning_fraction is not None
            and float(row["high_motion_fraction"]) > args.high_motion_warning_fraction
        ):
            flags.append(
                f"high_motion_fraction_above_{100*args.high_motion_warning_fraction:g}pct"
            )
        if float(row["median_tsnr"]) < thresholds[(row["dataset"], "median_tsnr")]["iqr_lower"]:
            flags.append("low_tsnr_iqr_outlier")
        if float(row["mean_fd_mm"]) > thresholds[(row["dataset"], "mean_fd_mm")]["iqr_upper"]:
            flags.append("high_mean_fd_iqr_outlier")
        if float(row["coverage_pct"]) < thresholds[(row["dataset"], "coverage_pct")]["iqr_lower"]:
            flags.append("low_coverage_iqr_outlier")
        row["qc_flags"] = ";".join(flags)
        if flags:
            flagged.append(row)

    complete.sort(key=lambda row: tuple(str(row[field]) for field in IDENTIFIERS))
    missing.sort(key=lambda row: tuple(str(row[field]) for field in IDENTIFIERS))
    write_tsv(args.output, OUTPUT_FIELDS, complete)
    write_tsv(
        args.summary_output,
        (
            "dataset",
            "metric",
            "n_runs",
            "mean",
            "median",
            "sd",
            "sem",
            "minimum",
            "q1",
            "q3",
            "maximum",
            "iqr_lower",
            "iqr_upper",
        ),
        summaries,
    )
    write_tsv(
        args.missing_output,
        IDENTIFIERS + ("problems",),
        missing,
    )

    subjects = defaultdict(list)
    for row in complete:
        subjects[(row["dataset"], row["subject"])].append(row)
    subject_rows = []
    for (dataset, subject), rows in sorted(subjects.items()):
        subject_rows.append(
            {
                "dataset": dataset,
                "subject": subject,
                "n_runs": len(rows),
                "mean_median_tsnr": statistics.mean(float(row["median_tsnr"]) for row in rows),
                "mean_fd_mm": statistics.mean(float(row["mean_fd_mm"]) for row in rows),
                "mean_high_motion_fraction": statistics.mean(
                    float(row["high_motion_fraction"]) for row in rows
                ),
                "minimum_coverage_pct": min(float(row["coverage_pct"]) for row in rows),
                "flagged_runs": sum(bool(row["qc_flags"]) for row in rows),
            }
        )
    write_tsv(
        args.subject_output,
        (
            "dataset",
            "subject",
            "n_runs",
            "mean_median_tsnr",
            "mean_fd_mm",
            "mean_high_motion_fraction",
            "minimum_coverage_pct",
            "flagged_runs",
        ),
        subject_rows,
    )

    print(f"Analysis-QC units checked: {len(manifest)}")
    print(f"Complete analysis-QC units: {len(complete)}")
    print(f"Incomplete analysis-QC units: {len(missing)}")
    print(f"Runs with review flags: {len(flagged)}")
    counts = Counter(row["dataset"] for row in complete)
    for dataset, count in sorted(counts.items()):
        subset = [row for row in complete if row["dataset"] == dataset]
        print(
            f"  {dataset}: n={count}; median tSNR mean="
            f"{statistics.mean(float(row['median_tsnr']) for row in subset):.3f}; "
            f"mean FD={statistics.mean(float(row['mean_fd_mm']) for row in subset):.4f} mm; "
            f"coverage mean={statistics.mean(float(row['coverage_pct']) for row in subset):.3f}%"
        )
    print(f"Run-level audit: {args.output.resolve()}")
    print(f"Dataset summary: {args.summary_output.resolve()}")
    print(f"Subject summary: {args.subject_output.resolve()}")
    print(f"Missing report: {args.missing_output.resolve()}")
    for row in missing[:20]:
        print(
            f"INCOMPLETE {row['dataset']} sub-{row['subject']} "
            f"ses-{row['session'] or 'none'} run-{row['run']}: {row['problems']}"
        )
    for row in flagged[:20]:
        print(
            f"REVIEW {row['dataset']} sub-{row['subject']} "
            f"ses-{row['session'] or 'none'} run-{row['run']}: {row['qc_flags']}"
        )
    if args.fail_on_incomplete and missing:
        return 1
    if args.fail_on_qc_flags and flagged:
        return 1
    if not missing:
        print("CHECK PASSED: every analysis input has complete tSNR, motion, and coverage QC.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
