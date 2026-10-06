#!/usr/bin/env python3
"""Measure ROI coverage and where coverage-eligible voxels are lost, per run.

For each run in an analysis-QC-shaped table this reports:
- the percentage of each ROI mask (resampled nearest-neighbour to the run-mask
  grid, as for the coverage exemption) that the run mask covers;
- the world-z range and median of the coverage-eligible voxels the run mask
  misses, which shows whether lost coverage sits inferiorly (OFC/temporal) or
  superiorly (vertex).

This is review evidence for coverage flags. It is not a registered exclusion
rule and does not choose the PPI seed.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from create_coverage_eligible_mask import nearest_resample

IDENTIFIERS = ("dataset", "subject", "session", "run")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument(
        "--roi",
        action="append",
        required=True,
        metavar="NAME=PATH",
        help="ROI mask; repeat for several (e.g. vs=masks/seed-vs.nii.gz)",
    )
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def parse_rois(values):
    rois = {}
    for value in values:
        name, separator, path = value.partition("=")
        if not separator or not name or not path:
            raise SystemExit(f"ERROR: --roi must be NAME=PATH: {value!r}")
        if name in rois:
            raise SystemExit(f"ERROR: duplicate ROI name: {name}")
        rois[name] = Path(path)
    return rois


def same_grid(first, second, np):
    return tuple(first.shape[:3]) == tuple(second.shape[:3]) and np.allclose(
        first.affine, second.affine, rtol=0.0, atol=1e-5
    )


def measure(row, rois, nib, np, cache):
    run_image = nib.load(row["mask"], mmap=True)
    eligible_image = nib.load(row["coverage_mask"], mmap=True)
    if not same_grid(run_image, eligible_image, np):
        raise ValueError("run mask and coverage mask grids differ")
    run_mask = np.asanyarray(run_image.dataobj) > 0
    eligible = np.asanyarray(eligible_image.dataobj) > 0
    result = {field: row[field] for field in IDENTIFIERS}
    result["coverage_pct"] = row.get("coverage_pct", "")

    missing = np.argwhere(eligible & ~run_mask)
    result["missing_eligible_voxels"] = len(missing)
    if len(missing):
        homogeneous = np.column_stack((missing, np.ones(len(missing))))
        z = (run_image.affine @ homogeneous.T)[2]
        result.update(
            missing_z_min_mm=f"{z.min():.1f}",
            missing_z_median_mm=f"{np.median(z):.1f}",
            missing_z_max_mm=f"{z.max():.1f}",
        )
    else:
        result.update(missing_z_min_mm="", missing_z_median_mm="", missing_z_max_mm="")

    grid = (tuple(run_image.shape[:3]), run_image.affine.tobytes())
    for name, path in rois.items():
        key = (name, grid)
        if key not in cache:
            cache[key] = nearest_resample(nib.load(str(path), mmap=True), run_image, np)
        roi = cache[key]
        if not np.any(roi):
            raise ValueError(f"ROI {name} is empty on the run grid")
        covered = int(np.count_nonzero(roi & run_mask))
        result[f"{name}_voxels"] = int(np.count_nonzero(roi))
        result[f"{name}_coverage_pct"] = f"{100 * covered / np.count_nonzero(roi):.4f}"
    return result


def main():
    args = parse_args()
    rois = parse_rois(args.roi)
    try:
        import nibabel as nib
        import numpy as np
    except ImportError as error:
        raise SystemExit(f"ERROR: nibabel and numpy are required: {error}") from error
    for name, path in rois.items():
        if not path.is_file():
            raise SystemExit(f"ERROR: ROI {name} not found: {path}")

    with args.input.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    required = set(IDENTIFIERS) | {"mask", "coverage_mask"}
    if not rows or not required.issubset(rows[0]):
        raise SystemExit("ERROR: input needs dataset/subject/session/run/mask/coverage_mask")

    results, cache = [], {}
    for row in rows:
        try:
            results.append(measure(row, rois, nib, np, cache))
        except (OSError, ValueError) as error:
            raise SystemExit(
                f"ERROR: {row['dataset']} sub-{row['subject']} run-{row['run']}: {error}"
            ) from error

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(results[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(results)
    print(f"ROI coverage rows: {len(results)} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
