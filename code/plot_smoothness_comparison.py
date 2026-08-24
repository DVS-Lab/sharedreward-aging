#!/usr/bin/env python3
"""Plot mean classic smoothness with run-level SEM by dataset and method."""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path


METHOD_LABELS = {
    "baseline": "Baseline",
    "afni_total_target": "AFNI total target",
    "fsl_susan_kernel": "FEAT-equivalent SUSAN",
}
DATASET_LABELS = {"ds003745": "ds003745", "rf1": "RF1"}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--summary-output", required=True, type=Path)
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
    required = {"dataset", "method", "classic_fwhm_combined"}
    if not rows or not required.issubset(rows[0]):
        raise SystemExit("ERROR: SUSAN comparison audit contract is incomplete")
    grouped = defaultdict(list)
    for row in rows:
        if row["dataset"] not in DATASET_LABELS or row["method"] not in METHOD_LABELS:
            raise SystemExit(f"ERROR: unexpected dataset/method: {row['dataset']}/{row['method']}")
        grouped[(row["dataset"], row["method"])].append(
            float(row["classic_fwhm_combined"])
        )

    datasets = ("ds003745", "rf1")
    methods = tuple(METHOD_LABELS)
    summary = []
    for dataset in datasets:
        for method in methods:
            values = grouped[(dataset, method)]
            if not values:
                raise SystemExit(f"ERROR: no values for {dataset}/{method}")
            sd = statistics.stdev(values) if len(values) > 1 else 0.0
            summary.append(
                {
                    "dataset": dataset,
                    "method": method,
                    "n_runs": len(values),
                    "mean_classic_fwhm_mm": statistics.mean(values),
                    "sd_classic_fwhm_mm": sd,
                    "sem_classic_fwhm_mm": sd / math.sqrt(len(values)),
                }
            )
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    with args.summary_output.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=summary[0],
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(summary)

    figure, axis = plt.subplots(figsize=(9.2, 5.6), constrained_layout=True)
    x = np.arange(len(methods), dtype=float)
    width = 0.34
    colors = {"ds003745": "#4477AA", "rf1": "#CC6677"}
    for index, dataset in enumerate(datasets):
        subset = [row for row in summary if row["dataset"] == dataset]
        positions = x + (index - 0.5) * width
        means = [row["mean_classic_fwhm_mm"] for row in subset]
        sems = [row["sem_classic_fwhm_mm"] for row in subset]
        bars = axis.bar(
            positions,
            means,
            width=width,
            yerr=sems,
            capsize=4,
            color=colors[dataset],
            edgecolor="black",
            linewidth=0.6,
            label=f"{DATASET_LABELS[dataset]} (n={subset[0]['n_runs']} runs)",
        )
        for bar, mean in zip(bars, means):
            axis.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.13,
                f"{mean:.2f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )
    axis.axhline(6, color="#333333", linestyle="--", linewidth=1, label="6-mm target/kernel")
    axis.set_xticks(x, [METHOD_LABELS[method] for method in methods])
    axis.set_ylabel("Measured classic combined FWHM (mm)")
    axis.set_title("Shared Reward smoothness comparison (mean ± SEM across runs)")
    axis.set_ylim(0, 9.3)
    axis.spines[["top", "right"]].set_visible(False)
    axis.grid(axis="y", alpha=0.22, linewidth=0.7)
    axis.legend(frameon=False, loc="upper left", ncols=3, fontsize=9)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, dpi=180)
    plt.close(figure)
    print(f"Summary: {args.summary_output.resolve()}")
    print(f"Plot: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
