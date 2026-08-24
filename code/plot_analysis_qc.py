#!/usr/bin/env python3
"""Create simple cross-dataset post-smoothing tSNR/motion/coverage QC plots."""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from pathlib import Path


LABELS = {"ds003745": "ds003745", "rf1": "RF1"}
COLORS = {"ds003745": "#4477AA", "rf1": "#CC6677"}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError as error:
        raise SystemExit(f"ERROR: matplotlib and numpy are required: {error}") from error
    with args.input.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    metrics = (
        ("median_tsnr", "Median whole-brain tSNR", "tSNR"),
        ("mean_fd_mm", "Mean framewise displacement", "FD (mm)"),
        ("high_motion_fraction", "High-motion volume fraction", "Fraction FD > 0.5 mm"),
        ("coverage_pct", "Common-mask coverage", "Coverage (%)"),
    )
    required = {"dataset"} | {metric[0] for metric in metrics}
    if not rows or not required.issubset(rows[0]):
        raise SystemExit("ERROR: analysis-QC audit contract is incomplete")
    datasets = ("ds003745", "rf1")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    figure, axes = plt.subplots(2, 2, figsize=(10, 7.5), constrained_layout=True)
    for axis, (field, title, ylabel) in zip(axes.flat, metrics):
        means, sems = [], []
        for dataset in datasets:
            values = [float(row[field]) for row in rows if row["dataset"] == dataset]
            if not values:
                raise SystemExit(f"ERROR: no {field} values for {dataset}")
            means.append(statistics.mean(values))
            sd = statistics.stdev(values) if len(values) > 1 else 0.0
            sems.append(sd / math.sqrt(len(values)))
        x = np.arange(2)
        bars = axis.bar(
            x,
            means,
            yerr=sems,
            capsize=4,
            color=[COLORS[dataset] for dataset in datasets],
            edgecolor="black",
            linewidth=0.6,
        )
        axis.set_xticks(x, [LABELS[dataset] for dataset in datasets])
        axis.set_title(title)
        axis.set_ylabel(ylabel)
        axis.spines[["top", "right"]].set_visible(False)
        axis.grid(axis="y", alpha=0.22, linewidth=0.7)
        for bar, mean in zip(bars, means):
            axis.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{mean:.3g}",
                ha="center",
                va="bottom",
                fontsize=9,
            )
    figure.suptitle("Post-smoothing Shared Reward analysis-input QC (mean ± SEM)")
    overview = args.output_dir / "analysis-input-qc_mean-sem.png"
    figure.savefig(overview, dpi=180)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(7.5, 5.8), constrained_layout=True)
    for dataset in datasets:
        subset = [row for row in rows if row["dataset"] == dataset]
        axis.scatter(
            [float(row["mean_fd_mm"]) for row in subset],
            [float(row["median_tsnr"]) for row in subset],
            s=16,
            alpha=0.55,
            color=COLORS[dataset],
            edgecolors="none",
            label=f"{LABELS[dataset]} (n={len(subset)})",
        )
    axis.set_xlabel("Mean framewise displacement (mm)")
    axis.set_ylabel("Median whole-brain tSNR")
    axis.set_title("tSNR versus motion")
    axis.spines[["top", "right"]].set_visible(False)
    axis.grid(alpha=0.22, linewidth=0.7)
    axis.legend(frameon=False)
    scatter = args.output_dir / "tsnr-vs-mean-fd.png"
    figure.savefig(scatter, dpi=180)
    plt.close(figure)
    print(f"QC overview: {overview.resolve()}")
    print(f"tSNR-motion plot: {scatter.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
