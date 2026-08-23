#!/usr/bin/env python3
"""Audit target-smoothed BOLD geometry and achieved classic/ACF smoothness."""

from __future__ import annotations

import argparse
import csv
import statistics
from collections import Counter
from pathlib import Path


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


def main():
    args = parse_args()
    if not 0 < args.tolerance_fraction < 1:
        raise SystemExit("ERROR: --tolerance-fraction must be between zero and one")
    try:
        import nibabel as nib
        import numpy as np
    except ImportError as error:
        raise SystemExit(f"ERROR: nibabel and numpy are required: {error}") from error
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
    for row in manifest:
        problems = []
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
                **{field: result[field] for field in RESULT_FIELDS},
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
    ) + RESULT_FIELDS
    write_tsv(args.output, output_fields, complete)
    write_tsv(
        args.missing_output,
        ("dataset", "subject", "session", "run", "problems"),
        missing,
    )
    print(f"Target-smoothed units checked: {len(manifest)}")
    print(f"Complete target-smoothed units: {len(complete)}")
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
    if args.fail_on_incomplete and missing:
        return 1
    if not missing:
        print("CHECK PASSED: every target-smoothed run passed geometry and smoothness QC.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
