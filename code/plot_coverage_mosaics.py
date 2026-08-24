#!/usr/bin/env python3
"""Plot low-coverage run masks over their final mean-BOLD backgrounds."""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--dataset", default="rf1")
    parser.add_argument("--coverage-below", type=float, default=95.0)
    parser.add_argument("--slices", type=int, default=6)
    parser.add_argument("--summary-output", required=True, type=Path)
    return parser.parse_args()


def source_path(path):
    return Path(os.path.abspath(path))


def matching_geometry(first, second, np):
    return tuple(first.shape[:3]) == tuple(second.shape[:3]) and np.allclose(
        first.affine, second.affine, rtol=0.0, atol=1e-5
    )


def select_slices(missing, eligible, count, np):
    coordinates = np.where(missing)[2]
    if not coordinates.size:
        coordinates = np.where(eligible)[2]
    low, high = int(coordinates.min()), int(coordinates.max())
    requested = min(count, high - low + 1)
    selected = sorted(
        set(int(round(value)) for value in np.linspace(low, high, requested))
    )
    if len(selected) < requested:
        counts = np.count_nonzero(missing, axis=(0, 1))
        for index in np.argsort(counts)[::-1]:
            index = int(index)
            if low <= index <= high and index not in selected:
                selected.append(index)
            if len(selected) == requested:
                break
    return sorted(selected)


def crop_bounds(eligible, padding, np):
    x, y, _ = np.where(eligible)
    return (
        slice(max(0, int(x.min()) - padding), min(eligible.shape[0], int(x.max()) + padding + 1)),
        slice(max(0, int(y.min()) - padding), min(eligible.shape[1], int(y.max()) + padding + 1)),
    )


def plot_unit(row, output_dir, slice_count, plt, np, nib):
    bold_path = Path(row["input"])
    run_mask_path = Path(row["mask"])
    coverage_mask_path = Path(row["coverage_mask"])
    for path in (bold_path, run_mask_path, coverage_mask_path):
        if not path.is_file():
            raise ValueError(f"missing input: {path}")

    bold_image = nib.load(str(bold_path), mmap=True)
    run_image = nib.load(str(run_mask_path), mmap=True)
    coverage_image = nib.load(str(coverage_mask_path), mmap=True)
    if bold_image.ndim != 4 or run_image.ndim != 3 or coverage_image.ndim != 3:
        raise ValueError("expected 4D BOLD and two 3D masks")
    if not matching_geometry(bold_image, run_image, np) or not matching_geometry(
        bold_image, coverage_image, np
    ):
        raise ValueError("BOLD/run-mask/coverage-mask geometry mismatch")

    mean_bold = np.nanmean(np.asanyarray(bold_image.dataobj, dtype=np.float32), axis=3)
    run_mask = np.asanyarray(run_image.dataobj) > 0
    eligible = np.asanyarray(coverage_image.dataobj) > 0
    missing = eligible & ~run_mask
    if not np.any(run_mask) or not np.any(eligible):
        raise ValueError("empty run or coverage mask")
    slices = select_slices(missing, eligible, slice_count, np)
    x_slice, y_slice = crop_bounds(eligible, 2, np)
    intensities = mean_bold[run_mask & np.isfinite(mean_bold)]
    low, high = np.percentile(intensities, (2, 98))
    if not high > low:
        low, high = float(np.nanmin(mean_bold)), float(np.nanmax(mean_bold))

    columns = 3
    rows = (len(slices) + columns - 1) // columns
    figure, axes = plt.subplots(rows, columns, figsize=(11, 3.8 * rows), squeeze=False)
    for axis, z_index in zip(axes.flat, slices):
        background = np.rot90(mean_bold[x_slice, y_slice, z_index])
        mask_slice = np.rot90(run_mask[x_slice, y_slice, z_index])
        eligible_slice = np.rot90(eligible[x_slice, y_slice, z_index])
        axis.imshow(background, cmap="gray", vmin=low, vmax=high, interpolation="nearest")
        overlay = np.zeros((*mask_slice.shape, 4), dtype=float)
        overlay[mask_slice] = (0.9, 0.0, 0.0, 0.24)
        axis.imshow(overlay, interpolation="nearest")
        if np.any(mask_slice) and not np.all(mask_slice):
            axis.contour(mask_slice, levels=[0.5], colors=["#d7191c"], linewidths=0.8)
        if np.any(eligible_slice) and not np.all(eligible_slice):
            axis.contour(
                eligible_slice,
                levels=[0.5],
                colors=["#ffd92f"],
                linewidths=0.7,
                linestyles="dashed",
            )
        world_z = float(bold_image.affine.dot((0, 0, z_index, 1))[2])
        axis.set_title(f"axial z={world_z:.1f} mm (index {z_index})", fontsize=10)
        axis.axis("off")
    for axis in axes.flat[len(slices) :]:
        axis.axis("off")

    session = row["session"] or "none"
    coverage = float(row["coverage_pct"])
    figure.suptitle(
        f"{row['dataset']} sub-{row['subject']} ses-{session} run-{row['run']} — "
        f"coverage {coverage:.2f}%\n"
        "red: run brain mask; dashed yellow: coverage-eligible boundary",
        fontsize=13,
    )
    figure.tight_layout(rect=(0, 0, 1, 0.93))
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / (
        f"{row['dataset']}_sub-{row['subject']}_ses-{session}_run-{row['run']}_"
        f"coverage-{coverage:.2f}.png"
    )
    figure.savefig(output, dpi=180, facecolor="white")
    plt.close(figure)
    return {
        "dataset": row["dataset"],
        "subject": row["subject"],
        "session": row["session"],
        "run": row["run"],
        "coverage_pct": row["coverage_pct"],
        "missing_eligible_voxels": int(np.count_nonzero(missing)),
        "slice_indices": ",".join(str(index) for index in slices),
        "input": str(source_path(bold_path)),
        "mask": str(source_path(run_mask_path)),
        "coverage_mask": str(source_path(coverage_mask_path)),
        "mosaic": str(source_path(output)),
    }


def main():
    args = parse_args()
    if args.slices < 1:
        raise SystemExit("ERROR: --slices must be positive")
    if not 0 < args.coverage_below <= 100:
        raise SystemExit("ERROR: --coverage-below must be in (0, 100]")
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import nibabel as nib
        import numpy as np
    except ImportError as error:
        raise SystemExit(f"ERROR: matplotlib, nibabel, and numpy are required: {error}")

    with args.input.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    required = {"dataset", "subject", "session", "run", "input", "mask", "coverage_mask", "coverage_pct"}
    if not rows or not required.issubset(rows[0]):
        raise SystemExit("ERROR: analysis-QC audit contract is incomplete")
    selected = [
        row
        for row in rows
        if row["dataset"] == args.dataset
        and float(row["coverage_pct"]) < args.coverage_below
    ]
    if not selected:
        raise SystemExit("ERROR: no runs match the coverage selection")

    results = []
    for row in selected:
        try:
            result = plot_unit(row, args.output_dir, args.slices, plt, np, nib)
        except (OSError, TypeError, ValueError) as error:
            raise SystemExit(
                f"ERROR: {row['dataset']} sub-{row['subject']} "
                f"run-{row['run']}: {error}"
            ) from error
        results.append(result)
        print(f"Mosaic: {result['mosaic']}")

    fields = tuple(results[0])
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    with args.summary_output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(results)
    print(f"Coverage mosaics created: {len(results)}")
    print(f"Summary: {args.summary_output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
