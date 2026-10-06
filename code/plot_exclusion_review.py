#!/usr/bin/env python3
"""Plot the run-level QC distributions behind the exclusion-ledger review.

Every task-ready run is one dot, colored by its ledger state for that metric
(pending review, not flagged), or as excluded in every panel once any
imaging criterion excludes it. Dashed lines are the per-dataset IQR
cutoffs recorded in logs/records/exclusion-ledger/iqr-thresholds.tsv.
Coverage is drawn as the uncovered share of the eligible mask on a log axis,
because rf1 coverage sits at the 100% ceiling. The last panel orders rf1 runs
by subject ID to show the shift in coverage across the enrollment sequence.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from build_analysis_cohort import ROOT, read_tsv, run_key

SURFACE, INK, MUTED, GRID = "#fcfcfb", "#1f1f1e", "#8a8a86", "#e4e4e0"
STATES = (
    ("not flagged", "#b9b9b4"),
    ("pending review", "#eb6834"),
    ("excluded", "#2a78d6"),
)
PANELS = (
    ("high_mean_fd_iqr_outlier", "mean_fd_mm", "Mean framewise displacement (mm)"),
    ("low_tsnr_iqr_outlier", "median_tsnr", "Median tSNR of final FEAT input"),
    ("low_coverage_iqr_outlier", "coverage_pct", "Eligible mask not covered (%, log)"),
)
DATASETS = ("rf1", "ds003745")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    records = ROOT / "logs/records"
    parser.add_argument("--analysis-qc", type=Path, default=records / "analysis-qc-run-level.tsv")
    parser.add_argument("--run-dispositions", type=Path, default=records / "analysis-run-dispositions.tsv")
    parser.add_argument("--ledger", type=Path, default=ROOT / "docs/exclusion_ledger.tsv")
    parser.add_argument(
        "--thresholds", type=Path, default=records / "exclusion-ledger/iqr-thresholds.tsv"
    )
    parser.add_argument("--output", type=Path, default=ROOT / "qc/exclusion-review_distributions.png")
    return parser.parse_args()


def uncovered(value):
    # Floor at 0.01% so fully covered runs stay on the log axis.
    return max(100.0 - value, 0.01)


def main():
    args = parse_args()
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    ready = {
        run_key(r)
        for r in read_tsv(args.run_dispositions, {"disposition"})
        if r["disposition"] == "task_ready"
    }
    runs = [r for r in read_tsv(args.analysis_qc, {"coverage_pct"}) if run_key(r) in ready]
    ledger = [
        r for r in read_tsv(args.ledger, {"criterion", "disposition"})
        if r["applies_to"] == "imaging_all" and r["run"] != "*"
    ]
    # A run excluded for any criterion shows as excluded in every panel.
    excluded = {run_key(r) for r in ledger if r["disposition"] == "exclude"}
    state = {
        (run_key(r), r["criterion"]): "pending review"
        for r in ledger
        if r["disposition"] == "pending_review"
    }
    state.update({(key, c): "excluded" for key in excluded for c, _, _ in PANELS})
    cutoffs = {
        (r["dataset"], r["criterion"]): float(r["threshold"])
        for r in read_tsv(args.thresholds, {"threshold"})
    }
    colors = dict(STATES)
    rng = np.random.default_rng(0)

    plt.rcParams.update({"font.size": 9, "text.color": INK, "axes.labelcolor": INK,
                         "xtick.color": MUTED, "ytick.color": MUTED})
    figure = plt.figure(figsize=(11, 8.2), facecolor=SURFACE)
    grid = figure.add_gridspec(2, 3, height_ratios=(1, 1.15), hspace=0.42, wspace=0.18)

    def style(axis):
        axis.set_facecolor(SURFACE)
        for side in ("top", "right", "left"):
            axis.spines[side].set_visible(False)
        axis.spines["bottom"].set_color(MUTED)
        axis.grid(axis="x", color=GRID, linewidth=0.6)
        axis.set_axisbelow(True)

    for column, (criterion, metric, title) in enumerate(PANELS):
        axis = figure.add_subplot(grid[0, column])
        style(axis)
        for row_index, dataset in enumerate(DATASETS):
            subset = [r for r in runs if r["dataset"] == dataset]
            for label, color in STATES:
                points = [
                    r for r in subset
                    if state.get((run_key(r), criterion), "not flagged") == label
                ]
                if not points:
                    continue
                values = [float(r[metric]) for r in points]
                if metric == "coverage_pct":
                    values = [uncovered(v) for v in values]
                y = row_index + rng.uniform(-0.28, 0.28, len(values))
                axis.scatter(values, y, s=9 if label == "not flagged" else 16,
                             color=color, linewidths=0, alpha=0.75 if label == "not flagged" else 1)
            cutoff = cutoffs[(dataset, criterion)]
            if metric == "coverage_pct":
                cutoff = uncovered(cutoff)
            axis.plot([cutoff, cutoff], [row_index - 0.4, row_index + 0.4],
                      color=INK, linestyle=(0, (3, 2)), linewidth=1)
        if metric == "coverage_pct":
            axis.set_xscale("log")
        axis.set_yticks(range(len(DATASETS)), list(DATASETS) if column == 0 else [])
        axis.tick_params(axis="y", length=0, labelcolor=INK)
        axis.set_ylim(-0.6, len(DATASETS) - 0.4)
        axis.set_title(title, loc="left", fontsize=9.5, color=INK)

    axis = figure.add_subplot(grid[1, :])
    style(axis)
    axis.grid(axis="y", color=GRID, linewidth=0.6)
    rf1 = sorted((r for r in runs if r["dataset"] == "rf1"), key=lambda r: int(r["subject"]))
    order = {subject: i for i, subject in enumerate(dict.fromkeys(r["subject"] for r in rf1))}
    criterion = "low_coverage_iqr_outlier"
    for label, color in STATES:
        points = [r for r in rf1 if state.get((run_key(r), criterion), "not flagged") == label]
        axis.scatter([order[r["subject"]] for r in points],
                     [uncovered(float(r["coverage_pct"])) for r in points],
                     s=9 if label == "not flagged" else 18, color=color, linewidths=0,
                     alpha=0.75 if label == "not flagged" else 1, label=label)
    axis.axhline(uncovered(cutoffs[("rf1", criterion)]), color=INK,
                 linestyle=(0, (3, 2)), linewidth=1, label="IQR cutoff")
    axis.set_yscale("log")
    subjects = list(order)
    ticks = list(range(0, len(subjects), 40))
    axis.set_xticks(ticks, [subjects[i] for i in ticks])
    axis.set_xlabel("rf1 subject ID (sorted)", color=MUTED)
    axis.set_ylabel("Eligible mask not covered (%)", color=MUTED)
    axis.set_title("rf1 coverage across the subject sequence (each dot is a run; color = ledger state)",
                   loc="left", fontsize=9.5)
    legend = axis.legend(loc="upper left", frameon=False, ncol=4, fontsize=8.5)
    for text in legend.get_texts():
        text.set_color(INK)

    figure.suptitle(
        "Run-level QC distributions behind the exclusion-ledger review "
        f"({len(runs)} task-ready runs; dashed = per-dataset IQR cutoff)",
        x=0.06, ha="left", fontsize=11, color=INK,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, dpi=160, facecolor=SURFACE, bbox_inches="tight")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
