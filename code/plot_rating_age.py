#!/usr/bin/env python3
"""Pre-QC pooled raw-rating age plots using the existing adjusted linear model."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from analyze_raw_ratings import ROOT, KEYS, CELLS, LABELS, age_design, age_fit, demographics, load_ratings
from audit_ratings_qc import RATINGS_POLICY


def age_predictions(data, ages):
    """Marginal means at the observed dataset/sex mix; pointwise HC3 t intervals.

    The seventh response is each person's mean across six cells, not six
    independent responses. Fitting it directly retains within-person covariance.
    """
    x = age_design(data)
    y = data[CELLS].to_numpy(float)
    y = np.column_stack([y, y.mean(axis=1)])
    bread = np.linalg.inv(x.T @ x)
    beta = bread @ x.T @ y
    residual = y - x @ beta
    leverage = np.sum((x @ bread) * x, axis=1)
    g = np.tile(x.mean(axis=0), (len(ages), 1))
    g[:, 1] = (np.asarray(ages) - data.age.mean()) / 10
    predicted = g @ beta
    weights = g @ bread @ x.T
    se = np.sqrt(weights**2 @ (residual / (1-leverage)[:, None])**2)
    critical = stats.t.ppf(.975, len(data)-x.shape[1])
    # Guard against accidental divergence from the inferential model.
    np.testing.assert_allclose(beta[1, :6], age_fit(data)[0], rtol=1e-11, atol=1e-12)
    return predicted, predicted-critical*se, predicted+critical*se, beta[1]


def plot(data, output):
    ages = np.linspace(data.age.min(), data.age.max(), 180)
    means, lower, upper, slopes = age_predictions(data, ages)
    # Horizontal jitter only, shared across panels, never used for fitting.
    jitter = np.random.default_rng(20261001).uniform(-.35, .35, len(data))
    scatter_age = data.age.to_numpy(float) + jitter
    colors = ["#337AA1", "#D77A4A"]
    fig, axes = plt.subplots(2, 3, figsize=(12.5, 8.8), sharex=True, sharey=True)
    fig.subplots_adjust(left=.075, right=.985, bottom=.17, top=.85, hspace=.30, wspace=.12)

    def draw(ax, response, column, color):
        ax.scatter(scatter_age, response, s=20, color="#626B73", alpha=.27,
                   edgecolors="none", zorder=2)
        ax.fill_between(ages, lower[:, column], upper[:, column], color=color, alpha=.22, zorder=3)
        ax.plot(ages, means[:, column], color=color, lw=2.6, zorder=4)
        ax.axhline(0, color="#ADB3B8", lw=.8, zorder=1)
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_xlim(16, 91); ax.set_xticks([20, 40, 60, 80])
        ax.tick_params(labelsize=10)
        ax.grid(axis="y", color="#E8EBED", lw=.6, zorder=0)

    for partner in range(3):
        for outcome in range(2):
            column = partner*2+outcome
            ax = axes[outcome, partner]
            draw(ax, data[CELLS[column]], column, colors[outcome])
            ax.set_title(LABELS[column].replace("win", "Win").replace("loss", "Loss"), fontsize=13)
            ax.set_ylim(-5.45, 5.45); ax.set_yticks([-5, -2.5, 0, 2.5, 5])
            if outcome == 1:
                ax.set_xlabel("Age (years)", fontsize=11)
    axes[0, 0].set_ylabel("Raw rating", fontsize=12)
    axes[1, 0].set_ylabel("Raw rating", fontsize=12)
    fig.suptitle("Shared Reward ratings across age", fontsize=20, y=.97)
    fig.text(.5, .91, f"Pooled sample, n = {len(data)} · Preliminary, before Cooper's imaging-QC exclusions",
             ha="center", fontsize=11, color="#525B63")
    caption = ("Points: individual raw ratings (horizontal jitter ±0.35 years for visibility).\n"
               "Lines: pooled linear trends adjusted for dataset and recorded sex; bands: pointwise 95% confidence intervals.\n"
               "Primary within-partner ratings rule; predictions average over the sample's dataset/sex mix. No z-scoring.")
    fig.text(.5, .045, caption, ha="center", va="center", fontsize=10, linespacing=1.6)
    for extension in ("png", "svg"):
        fig.savefig(output / f"raw-ratings-by-age-six-panels.{extension}", dpi=170)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.0, 6.4))
    fig.subplots_adjust(left=.105, right=.96, bottom=.23, top=.79)
    response = data[CELLS].mean(axis=1)
    draw(ax, response, 6, "#397C68")
    # Mean-rating view uses its own explicitly labeled scale, covering every point.
    ax.set_ylim(min(-.1, response.min()-.25, lower[:, 6].min()-.2),
                max(response.max()+.25, upper[:, 6].max()+.2))
    ax.set_ylabel("Mean raw rating across six conditions", fontsize=11)
    ax.set_xlabel("Age (years)", fontsize=11)
    fig.suptitle("Overall rating level across age", fontsize=19, y=.97)
    fig.text(.5, .91, f"Pooled sample, n = {len(data)} · Preliminary, before imaging-QC exclusions", ha="center", fontsize=11)
    _, slope_cov, df = age_fit(data)
    c = np.ones(6)/6
    slope_se = np.sqrt(c @ slope_cov @ c)
    delta = stats.t.ppf(.975, df)*slope_se
    fig.text(.5, .85, f"Adjusted slope: {slopes[6]:+.3f} points per decade  (95% CI {slopes[6]-delta:.3f} to {slopes[6]+delta:.3f})",
             ha="center", fontsize=11, color="#28604F")
    fig.text(.5, .07, "Each point is one participant's mean of the six raw ratings.\n"
             "Line adjusts for dataset and recorded sex; band is a pointwise 95% confidence interval.\n"
             "Horizontal jitter ±0.35 years for visibility. Note the different y-axis scale from the six-panel figure.",
             ha="center", fontsize=9.8, linespacing=1.6)
    for extension in ("png", "svg"):
        fig.savefig(output / f"raw-ratings-by-age-overall.{extension}", dpi=170)
    plt.close(fig)
    rows = []
    for j, condition in enumerate(LABELS+["Mean across six conditions"]):
        for i, age in enumerate(ages):
            rows.append(dict(condition=condition, age=age, adjusted_mean=means[i, j],
                             ci95_low=lower[i, j], ci95_high=upper[i, j], n=len(data)))
    pd.DataFrame(rows).to_csv(output / "age-plot-predictions.tsv", sep="\t", index=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ratings", type=Path, default=ROOT/"logs/records/ratings-qc-subject-level.tsv")
    parser.add_argument("--cohort", type=Path, default=ROOT/"logs/records/analysis-subject-dispositions.tsv")
    parser.add_argument("--rf1-participants", type=Path, default=ROOT.parent/"rf1-sra-linux2/bids/participants.tsv")
    parser.add_argument("--ds-participants", type=Path, default=ROOT/"participants-srndna.tsv")
    parser.add_argument("--output-dir", type=Path, default=ROOT/"qc/ratings-raw")
    args = parser.parse_args()
    data = load_ratings(args.ratings, args.cohort)
    demo = pd.concat([demographics(args.rf1_participants,"rf1"), demographics(args.ds_participants,"ds003745")])
    data = data.merge(demo, on=KEYS, how="left", validate="one_to_one").sort_values(KEYS)
    if not (data.age.between(18,110) & data.sex.isin(["F","M","O"])).all():
        raise ValueError("Complete age/sex coverage is required for these full-cohort plots")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    plot(data, args.output_dir)
    sources = [args.ratings,args.cohort,args.rf1_participants,args.ds_participants,
               Path(__file__),ROOT/"code/analyze_raw_ratings.py",ROOT/"code/audit_ratings_qc.py"]
    metadata = dict(n=len(data), status="preliminary_before_imaging_QC", pooled=True,
        ratings_policy=RATINGS_POLICY,
        age_range=[float(data.age.min()),float(data.age.max())],
        prediction="Age varied across observed range; dataset/sex covariates fixed at sample means, equivalent to empirical marginal standardization for this additive linear model.",
        uncertainty="HC3 pointwise 95% t confidence intervals for adjusted mean, not prediction intervals or simultaneous bands.",
        points="Unadjusted raw ratings, no participant IDs; horizontal display jitter only, seed 20261001, +/-0.35 years.",
        sources=[dict(path=str(f.resolve()),sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sources])
    (args.output_dir/"age-plots-provenance.json").write_text(json.dumps(metadata,indent=2)+"\n")
    print(f"Created two pooled age figures (PNG/SVG): n={len(data)}, complete demographics; {RATINGS_POLICY}.")
    print(f"Output directory: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
