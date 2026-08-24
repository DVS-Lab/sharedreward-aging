#!/usr/bin/env python3
"""Audit target-smoothed BOLD geometry and achieved classic/ACF smoothness."""

from __future__ import annotations

import argparse
import csv
import statistics
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXCEPTIONS = ROOT / "docs/smoothing_qc_exceptions.tsv"


RESULT_FIELDS = (
    "classic_fwhm_x",
    "classic_fwhm_y",
    "classic_fwhm_z",
    "classic_fwhm_combined",
    "acf_a",
    "acf_b",
    "acf_c",
    "acf_effective_fwhm",
    "afni_version",
)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--missing-output", required=True, type=Path)
    parser.add_argument(
        "--exceptions",
        type=Path,
        default=DEFAULT_EXCEPTIONS,
        help="Tracked, run-specific QC exceptions with bounded acceptance ranges",
    )
    parser.add_argument("--tolerance-fraction", type=float, default=0.10)
    parser.add_argument("--fail-on-incomplete", action="store_true")
    return parser.parse_args()


def write_tsv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def load_exceptions(path):
    required = {
        "dataset",
        "subject",
        "session",
        "run",
        "problem",
        "expected_target_fwhm_mm",
        "accepted_classic_min_mm",
        "accepted_classic_max_mm",
        "rationale",
        "evidence",
    }
    if not path.is_file():
        raise SystemExit(f"ERROR: smoothing QC exception file does not exist: {path}")
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise SystemExit("ERROR: smoothing QC exception contract is incomplete")
        rows = list(reader)

    exceptions = {}
    for row in rows:
        key = tuple(row[field] for field in ("dataset", "subject", "session", "run", "problem"))
        if key in exceptions:
            raise SystemExit(f"ERROR: duplicate smoothing QC exception: {key}")
        if row["problem"] != "classic_outside_tolerance":
            raise SystemExit(f"ERROR: unsupported smoothing QC exception problem: {row['problem']}")
        try:
            target = float(row["expected_target_fwhm_mm"])
            accepted_min = float(row["accepted_classic_min_mm"])
            accepted_max = float(row["accepted_classic_max_mm"])
        except ValueError as error:
            raise SystemExit(f"ERROR: invalid smoothing QC exception numeric value: {key}") from error
        if target <= 0 or accepted_min <= 0 or accepted_max < accepted_min:
            raise SystemExit(f"ERROR: invalid smoothing QC exception range: {key}")
        if not row["rationale"].strip() or not row["evidence"].strip():
            raise SystemExit(f"ERROR: smoothing QC exception lacks rationale/evidence: {key}")
        evidence = Path(row["evidence"])
        if not evidence.is_absolute():
            evidence = ROOT / evidence
        if not evidence.is_file():
            raise SystemExit(f"ERROR: smoothing QC exception evidence does not exist: {evidence}")
        exceptions[key] = {
            **row,
            "target": target,
            "accepted_min": accepted_min,
            "accepted_max": accepted_max,
        }
    return exceptions


def main():
    args = parse_args()
    if not 0 < args.tolerance_fraction < 1:
        raise SystemExit("ERROR: --tolerance-fraction must be between zero and one")
    try:
        import nibabel as nib
        import numpy as np
    except ImportError as error:
        raise SystemExit(f"ERROR: nibabel and numpy are required: {error}") from error
    exceptions = load_exceptions(args.exceptions)
    with args.manifest.open(newline="") as handle:
        manifest = list(csv.DictReader(handle, delimiter="\t"))
    required = {
        "dataset",
        "subject",
        "session",
        "run",
        "input_bold",
        "input_mask",
        "output_bold",
        "output_qc",
        "target_fwhm_mm",
    }
    if not manifest or not required.issubset(manifest[0]):
        raise SystemExit("ERROR: target-smoothing manifest contract is incomplete")

    complete = []
    missing = []
    accepted_exceptions = []
    for row in manifest:
        problems = []
        accepted_exception = None
        output = Path(row["output_bold"])
        mask = Path(row["input_mask"])
        qc = Path(row["output_qc"])
        result = None
        if not output.is_file() or output.stat().st_size == 0:
            problems.append("missing_output_bold")
        if not qc.is_file() or qc.stat().st_size == 0:
            problems.append("missing_output_qc")
        if not problems:
            try:
                output_image = nib.load(str(output), mmap=True)
                mask_image = nib.load(str(mask), mmap=True)
                if output_image.ndim != 4:
                    problems.append("output_not_4d")
                if mask_image.ndim != 3:
                    problems.append("mask_not_3d")
                if tuple(output_image.shape[:3]) != tuple(mask_image.shape):
                    problems.append("shape_mismatch")
                if not np.allclose(
                    output_image.affine, mask_image.affine, rtol=0, atol=1e-5
                ):
                    problems.append("affine_mismatch")
            except (OSError, ValueError) as error:
                problems.append(f"unreadable_nifti:{error}")
            try:
                with qc.open(newline="") as handle:
                    results = list(csv.DictReader(handle, delimiter="\t"))
                if len(results) != 1:
                    problems.append(f"qc_rows={len(results)}")
                else:
                    result = results[0]
                    if Path(result.get("input", "")).resolve() != output.resolve():
                        problems.append("qc_input_contract")
                    if Path(result.get("mask", "")).resolve() != mask.resolve():
                        problems.append("qc_mask_contract")
                    for field in RESULT_FIELDS[:-1]:
                        if float(result[field]) <= 0:
                            problems.append(f"nonpositive_{field}")
                    target = float(row["target_fwhm_mm"])
                    achieved = float(result["classic_fwhm_combined"])
                    lower = target * (1 - args.tolerance_fraction)
                    upper = target * (1 + args.tolerance_fraction)
                    if not lower <= achieved <= upper:
                        key = (
                            row["dataset"],
                            row["subject"],
                            row["session"],
                            row["run"],
                            "classic_outside_tolerance",
                        )
                        exception = exceptions.get(key)
                        if (
                            exception is not None
                            and abs(target - exception["target"]) <= 1e-6
                            and exception["accepted_min"] <= achieved <= exception["accepted_max"]
                        ):
                            accepted_exception = exception
                        else:
                            problems.append("classic_outside_tolerance")
            except (KeyError, OSError, TypeError, ValueError) as error:
                problems.append(f"invalid_qc:{error}")

        identifiers = {field: row[field] for field in ("dataset", "subject", "session", "run")}
        if problems:
            missing.append({**identifiers, "problems": ",".join(problems)})
            continue
        complete.append(
            {
                **identifiers,
                "input_bold": str(Path(row["input_bold"]).resolve()),
                "input_mask": str(mask.resolve()),
                "output_bold": str(output.resolve()),
                "target_fwhm_mm": row["target_fwhm_mm"],
                "qc_status": (
                    "accepted_exception" if accepted_exception else "pass"
                ),
                "accepted_exception": (
                    accepted_exception["problem"] if accepted_exception else ""
                ),
                "exception_rationale": (
                    accepted_exception["rationale"] if accepted_exception else ""
                ),
                "exception_evidence": (
                    accepted_exception["evidence"] if accepted_exception else ""
                ),
                **{field: result[field] for field in RESULT_FIELDS},
            }
        )
        if accepted_exception:
            accepted_exceptions.append(
                {
                    **identifiers,
                    "achieved": float(result["classic_fwhm_combined"]),
                    "exception": accepted_exception,
                }
            )

    output_fields = (
        "dataset",
        "subject",
        "session",
        "run",
        "input_bold",
        "input_mask",
        "output_bold",
        "target_fwhm_mm",
        "qc_status",
        "accepted_exception",
        "exception_rationale",
        "exception_evidence",
    ) + RESULT_FIELDS
    write_tsv(args.output, output_fields, complete)
    write_tsv(
        args.missing_output,
        ("dataset", "subject", "session", "run", "problems"),
        missing,
    )
    print(f"Target-smoothed units checked: {len(manifest)}")
    print(f"Complete target-smoothed units: {len(complete)}")
    print(f"Conventionally passing units: {len(complete) - len(accepted_exceptions)}")
    print(f"Accepted QC exceptions: {len(accepted_exceptions)}")
    print(f"Incomplete target-smoothed units: {len(missing)}")
    counts = Counter(row["dataset"] for row in complete)
    for dataset, count in sorted(counts.items()):
        subset = [row for row in complete if row["dataset"] == dataset]
        classic = [float(row["classic_fwhm_combined"]) for row in subset]
        acf = [float(row["acf_effective_fwhm"]) for row in subset]
        print(
            f"  {dataset}: n={count}; classic mean={statistics.mean(classic):.4f}, "
            f"median={statistics.median(classic):.4f}, "
            f"range={min(classic):.4f}-{max(classic):.4f}; "
            f"ACF-effective mean={statistics.mean(acf):.4f}, "
            f"median={statistics.median(acf):.4f}, range={min(acf):.4f}-{max(acf):.4f}"
        )
    print(f"Consolidated audit: {args.output.resolve()}")
    print(f"Missing report: {args.missing_output.resolve()}")
    for row in missing[:20]:
        print(
            f"INCOMPLETE {row['dataset']} sub-{row['subject']} "
            f"ses-{row['session'] or 'none'} run-{row['run']}: {row['problems']}"
        )
    for row in accepted_exceptions:
        exception = row["exception"]
        print(
            f"ACCEPTED EXCEPTION {row['dataset']} sub-{row['subject']} "
            f"ses-{row['session'] or 'none'} run-{row['run']}: "
            f"classic={row['achieved']:.5f} mm; "
            f"accepted range={exception['accepted_min']:.2f}-{exception['accepted_max']:.2f} mm"
        )
    if args.fail_on_incomplete and missing:
        return 1
    if not missing:
        print(
            "CHECK PASSED: every target-smoothed run passed geometry and smoothness QC "
            "or a bounded, documented run-specific exception."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
