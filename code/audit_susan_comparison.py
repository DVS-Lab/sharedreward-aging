#!/usr/bin/env python3
"""Consolidate AFNI measurements for baseline, AFNI-target, and SUSAN output."""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from pathlib import Path


METHODS = (
    ("baseline", "baseline_bold", "baseline_qc"),
    ("afni_total_target", "afni_target_bold", "afni_target_qc"),
    ("fsl_susan_kernel", "susan_output_bold", "susan_output_qc"),
)
RESULT_FIELDS = ("classic_fwhm_x", "classic_fwhm_y", "classic_fwhm_z", "classic_fwhm_combined", "acf_a", "acf_b", "acf_c", "acf_effective_fwhm", "afni_version")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--missing-output", required=True, type=Path)
    parser.add_argument("--summary-output", type=Path)
    parser.add_argument("--fail-on-incomplete", action="store_true")
    return parser.parse_args()


def write_tsv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main():
    args = parse_args()
    with args.manifest.open(newline="") as handle: manifest = list(csv.DictReader(handle, delimiter="\t"))
    complete, missing, pairs = [], [], {}
    for unit in manifest:
        unit_key = tuple(unit[field] for field in ("dataset", "subject", "session", "run"))
        problems = []
        susan_metadata = None
        try:
            with Path(unit["susan_metadata"]).open(newline="") as handle:
                metadata_rows = list(csv.DictReader(handle, delimiter="\t"))
            if len(metadata_rows) != 1:
                raise ValueError(f"metadata_rows={len(metadata_rows)}")
            susan_metadata = metadata_rows[0]
            metadata_contracts = (
                ("input", "baseline_bold"),
                ("mask", "input_mask"),
                ("output", "susan_output_bold"),
            )
            for metadata_field, manifest_field in metadata_contracts:
                if Path(susan_metadata[metadata_field]).resolve() != Path(unit[manifest_field]).resolve():
                    raise ValueError(f"metadata_{metadata_field}_contract")
            if abs(float(susan_metadata["kernel_fwhm_mm"]) - float(unit["kernel_fwhm_mm"])) > 1e-9:
                raise ValueError("metadata_kernel_contract")
            for field in ("spatial_sigma_mm", "masked_median", "brightness_threshold"):
                if float(susan_metadata[field]) <= 0:
                    raise ValueError(f"nonpositive_metadata_{field}")
        except (KeyError, OSError, TypeError, ValueError) as error:
            problems.append(f"invalid_susan_metadata:{error}")
        for method, image_field, qc_field in METHODS:
            image, qc = Path(unit[image_field]), Path(unit[qc_field])
            if not image.is_file() or not qc.is_file():
                problems.append(f"missing_{method}"); continue
            try:
                with qc.open(newline="") as handle: rows = list(csv.DictReader(handle, delimiter="\t"))
                if len(rows) != 1: raise ValueError(f"qc_rows={len(rows)}")
                result = rows[0]
                if Path(result["input"]).resolve() != image.resolve(): raise ValueError("input_contract")
                if Path(result["mask"]).resolve() != Path(unit["input_mask"]).resolve(): raise ValueError("mask_contract")
                for field in RESULT_FIELDS[:-1]:
                    if float(result[field]) <= 0: raise ValueError(f"nonpositive_{field}")
                row = {field: unit[field] for field in ("dataset", "subject", "session", "run")}
                susan_fields = {
                    "nominal_kernel_fwhm_mm": "",
                    "susan_spatial_sigma_mm": "",
                    "susan_masked_median": "",
                    "susan_brightness_threshold": "",
                    "fsl_version": "",
                }
                if method == "fsl_susan_kernel" and susan_metadata is not None:
                    susan_fields = {
                        "nominal_kernel_fwhm_mm": susan_metadata["kernel_fwhm_mm"],
                        "susan_spatial_sigma_mm": susan_metadata["spatial_sigma_mm"],
                        "susan_masked_median": susan_metadata["masked_median"],
                        "susan_brightness_threshold": susan_metadata["brightness_threshold"],
                        "fsl_version": susan_metadata["fsl_version"],
                    }
                row.update({"method": method, "image": str(image.resolve()), "mask": str(Path(unit["input_mask"]).resolve()), **susan_fields, **{field: result[field] for field in RESULT_FIELDS}})
                complete.append(row); pairs.setdefault(unit_key, {})[method] = row
            except (KeyError, OSError, TypeError, ValueError) as error:
                problems.append(f"invalid_{method}:{error}")
        if problems:
            missing.append({"dataset": unit["dataset"], "subject": unit["subject"], "session": unit["session"], "run": unit["run"], "problems": ",".join(problems)})
    fields = (
        "dataset", "subject", "session", "run", "method", "image", "mask",
        "nominal_kernel_fwhm_mm", "susan_spatial_sigma_mm",
        "susan_masked_median", "susan_brightness_threshold", "fsl_version",
    ) + RESULT_FIELDS
    write_tsv(args.output, fields, complete)
    write_tsv(args.missing_output, ("dataset", "subject", "session", "run", "problems"), missing)
    print(f"Comparison units checked: {len(manifest)}")
    print(f"Complete method measurements: {len(complete)} of {3*len(manifest)}")
    print(f"Incomplete units: {len(missing)}")
    pair_summaries = []
    for key, methods in sorted(pairs.items()):
        if len(methods) != 3: continue
        baseline = float(methods["baseline"]["classic_fwhm_combined"])
        afni = float(methods["afni_total_target"]["classic_fwhm_combined"])
        susan = float(methods["fsl_susan_kernel"]["classic_fwhm_combined"])
        kernel = float(methods["fsl_susan_kernel"]["nominal_kernel_fwhm_mm"])
        gaussian_expected = math.sqrt(baseline**2 + kernel**2)
        effective_added = math.sqrt(max(0.0, susan**2 - baseline**2))
        pair_summaries.append({
            "dataset": key[0], "baseline": baseline, "afni": afni,
            "susan": susan, "gaussian_expected": gaussian_expected,
            "effective_added": effective_added, "susan_minus_afni": susan-afni,
        })
        if len(manifest) <= 20:
            print(f"  {key[0]} sub-{key[1]} ses-{key[2] or 'none'} run-{key[3]}: baseline={baseline:.4f}; AFNI-total-target={afni:.4f}; SUSAN-kernel={susan:.4f}; Gaussian-quadrature expectation={gaussian_expected:.4f}; SUSAN effective-added={effective_added:.4f}; SUSAN-minus-AFNI={susan-afni:+.4f} mm")
    summary_rows = []
    for dataset in sorted({row["dataset"] for row in pair_summaries}):
        subset = [row for row in pair_summaries if row["dataset"] == dataset]
        summary = {"dataset": dataset, "n": str(len(subset))}
        for name in ("baseline", "afni", "susan", "gaussian_expected", "effective_added", "susan_minus_afni"):
            values = [row[name] for row in subset]
            summary.update({
                f"{name}_mean": f"{statistics.mean(values):.8g}",
                f"{name}_median": f"{statistics.median(values):.8g}",
                f"{name}_min": f"{min(values):.8g}",
                f"{name}_max": f"{max(values):.8g}",
            })
        summary_rows.append(summary)
        print(
            f"  {dataset} summary: n={len(subset)}; "
            f"baseline mean={summary['baseline_mean']}; "
            f"AFNI-total mean={summary['afni_mean']}; "
            f"SUSAN mean={summary['susan_mean']}; "
            f"SUSAN-minus-AFNI mean={summary['susan_minus_afni_mean']} mm; "
            f"SUSAN effective-added mean={summary['effective_added_mean']} mm"
        )
    if args.summary_output:
        summary_fields = ("dataset", "n") + tuple(
            f"{name}_{stat}"
            for name in ("baseline", "afni", "susan", "gaussian_expected", "effective_added", "susan_minus_afni")
            for stat in ("mean", "median", "min", "max")
        )
        write_tsv(args.summary_output, summary_fields, summary_rows)
        print(f"Summary: {args.summary_output.resolve()}")
    print(f"Audit: {args.output.resolve()}")
    print(f"Missing report: {args.missing_output.resolve()}")
    if args.fail_on_incomplete and missing: return 1
    if not missing: print("CHECK PASSED: both datasets have complete three-method comparisons.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
