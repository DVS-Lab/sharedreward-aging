#!/usr/bin/env python3
"""Raw six-cell ratings plot and exploratory continuous-age analysis.

One row per participant, six outcomes. No within-person standardization.
HC3 covariance retains the covariance of the six responses within a person.
Age slopes allow separate dataset/sex offsets for each condition. No MRI QC
exclusions are added. Missing demographic coverage fails unless explicitly allowed.
"""
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

ROOT = Path(__file__).resolve().parents[1]
KEYS = ["dataset", "subject"]
CELLS = [f"partner_{p}_trait_{t}_mean" for p in (1, 2, 3) for t in (0, 1)]
LABELS = [f"{p} {t}" for p in ("Computer", "Stranger", "Friend") for t in ("win", "loss")]


def read(path):
    return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)


def load_ratings(ratings_path, cohort_path):
    ratings, cohort = read(ratings_path), read(cohort_path)
    for frame in (ratings, cohort):
        if frame.duplicated(KEYS).any():
            raise ValueError("Expected one baseline row per dataset/subject; duplicate keys")
    cohort = cohort.loc[cohort.ratings_l2_ready.str.lower() == "true", KEYS]
    data = cohort.merge(ratings, on=KEYS, how="left", validate="one_to_one", indicator=True)
    if not data._merge.eq("both").all() or not data.exclude_subject.eq("false").all():
        raise ValueError("Ratings eligibility differs from the current cohort")
    data[CELLS] = data[CELLS].apply(pd.to_numeric, errors="raise")
    values = data[CELLS].to_numpy(float)
    if not len(data) or not np.isfinite(values).all() or (np.abs(values) > 5).any():
        raise ValueError("Missing/nonfinite/out-of-range raw ratings (expected -5 to +5)")
    return data


def demographics(path, dataset):
    data = read(path)
    data["subject"] = data.participant_id.str.removeprefix("sub-")
    data["dataset"] = dataset
    if data.duplicated(KEYS).any():
        raise ValueError(f"Duplicate demographics: {path}")
    data["age"] = pd.to_numeric(data.age, errors="coerce")
    data["sex"] = data.sex.str.strip().str.upper()
    return data[KEYS + ["age", "sex"]]


def holm(p):
    p = np.asarray(p); order = np.argsort(p); adjusted = np.empty(len(p))
    adjusted[order] = np.minimum(1, np.maximum.accumulate(p[order] * np.arange(len(p), 0, -1)))
    return adjusted


def age_design(data, adjust_sex=True):
    """Shared subject-level design for inference and marginal age plots."""
    columns = [np.ones(len(data)), (data.age.to_numpy(float) - data.age.mean()) / 10]
    if data.dataset.nunique() > 1:
        columns.append(data.dataset.eq("rf1").to_numpy(float))
    if adjust_sex:
        # Preserve recorded O (other); do not silently exclude or recode it.
        for level in sorted(data.sex.unique())[1:]:
            columns.append(data.sex.eq(level).to_numpy(float))
    x = np.column_stack(columns)
    if len(data) <= x.shape[1] + 6 or np.linalg.matrix_rank(x) != x.shape[1]:
        raise ValueError("Insufficient participants or rank-deficient age design")
    return x


def age_fit(data, adjust_sex=True):
    # All six outcomes have the same subject-level X, allowing an exact wide
    # multivariate fit rather than treating the six responses as independent.
    x = age_design(data, adjust_sex); y = data[CELLS].to_numpy(float)
    bread = np.linalg.inv(x.T @ x); beta = bread @ x.T @ y
    residual = y - x @ beta
    leverage = np.sum((x @ bread) * x, axis=1)
    influence = (x @ bread[:, 1])[:, None] * residual / (1 - leverage)[:, None]
    covariance = influence.T @ influence
    return beta[1], covariance, len(data) - x.shape[1]


def tests(data, scope, adjust_sex=True):
    slopes, covariance, df = age_fit(data, adjust_sex)
    omnibus = float(slopes @ np.linalg.solve(covariance, slopes))
    results = [{"scope": scope, "test": "any_age_association", "n": len(data),
                "chi2": omnibus, "df": 6, "p": float(stats.chi2.sf(omnibus, 6))}]
    # Marginal age effect and age interactions in the 3 partners x 2 outcomes.
    contrasts = {
        "overall_mean": np.ones((1, 6)) / 6,
        "age_x_outcome": np.array([[1, -1, 1, -1, 1, -1]]) / 3,
        "age_x_partner": np.array([[-1, -1, 0, 0, 1, 1], [0, 0, -1, -1, 1, 1]]) / 2,
        "age_x_partner_x_outcome": np.array([[-1, 1, 0, 0, 1, -1], [0, 0, -1, 1, 1, -1]]),
    }
    for name, c in contrasts.items():
        b, v = c @ slopes, c @ covariance @ c.T
        w = float(b @ np.linalg.solve(v, b)); k = len(c)
        results.append({"scope": scope, "test": name, "n": len(data), "chi2": w,
                        "df": k, "p": float(stats.chi2.sf(w, k))})
        if k == 1:
            se = float(np.sqrt(v[0, 0])); critical = float(stats.t.ppf(.975, df))
            results[-1].update(points_per_decade=float(b[0]), se_hc3=se,
                               ci95_low=float(b[0])-critical*se, ci95_high=float(b[0])+critical*se)
    for row, p in zip(results[1:], holm([r["p"] for r in results[1:]])):
        row["p_holm_four_age_terms"] = float(p)
    se = np.sqrt(np.diag(covariance)); critical = stats.t.ppf(.975, df)
    cells = pd.DataFrame({"scope": scope, "condition": LABELS, "n": len(data),
        "points_per_decade": slopes, "se_hc3": se, "ci95_low": slopes-critical*se,
        "ci95_high": slopes+critical*se, "df_t": df, "p": 2*stats.t.sf(np.abs(slopes/se), df)})
    cells["p_holm_six_cells"] = holm(cells.p)
    return results, cells


def plot_ratings(data, output):
    summaries = []
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.8), sharey=True)
    colors = ["#337AA1", "#D77A4A"]
    for ax, scope in zip(axes, ("Pooled", "rf1", "ds003745")):
        subset = data if scope == "Pooled" else data.loc[data.dataset.eq(scope)]
        values = subset[CELLS].to_numpy(float)
        means, sem = values.mean(axis=0), values.std(axis=0, ddof=1)/np.sqrt(len(values))
        x = np.array([0, .36, 1, 1.36, 2, 2.36])
        ax.bar(x, means, yerr=sem, capsize=3, width=.32, color=colors*3,
               error_kw={"linewidth": 1}, zorder=3)
        ax.axhline(0, color="#555555", lw=.8)
        ax.set_xticks([.18, 1.18, 2.18], ["Computer", "Stranger", "Friend"])
        title = {"Pooled": "Both datasets", "rf1": "RF1", "ds003745": "Earlier dataset"}[scope]
        ax.set_title(f"{title} (n = {len(subset)})", fontsize=12)
        ax.set_ylim(-5.4, 5.4); ax.set_yticks([-5, -2.5, 0, 2.5, 5])
        ax.spines[["top", "right"]].set_visible(False)
        for label, mean, error in zip(LABELS, means, sem):
            summaries.append(dict(scope=scope, condition=label, n=len(subset), mean=mean, sem=error))
    axes[0].set_ylabel("Raw rating (-5 negative to +5 positive)")
    from matplotlib.patches import Patch
    fig.legend([Patch(color=c) for c in colors], ["Win", "Loss"], loc="upper center", ncol=2, frameon=False,
               bbox_to_anchor=(.5, .935))
    fig.suptitle("Shared Reward post-scan ratings", fontsize=17, y=.995)
    fig.text(.5, .025, "Mean ± between-participant SEM; one six-cell rating profile per participant.\n"
             "Current task-valid, ratings-qualified cohort; before Cooper's imaging-QC exclusions.", ha="center", fontsize=10)
    fig.tight_layout(rect=(0, .10, 1, .86))
    for extension in ("png", "svg"):
        fig.savefig(output / f"raw-ratings-six-conditions.{extension}", dpi=180)
    plt.close(fig)
    pd.DataFrame(summaries).to_csv(output / "raw-ratings-means-sem.tsv", sep="\t", index=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ratings", type=Path, default=ROOT / "logs/records/ratings-qc-subject-level.tsv")
    p.add_argument("--cohort", type=Path, default=ROOT / "logs/records/analysis-subject-dispositions.tsv")
    p.add_argument("--rf1-participants", type=Path, default=ROOT.parent / "rf1-sra-linux2/bids/participants.tsv")
    p.add_argument("--ds-participants", type=Path, default=ROOT / "participants-srndna.tsv")
    p.add_argument("--allow-partial-age", action="store_true")
    p.add_argument("--age-source-label", default="canonical upstream RF1 baseline demographics")
    p.add_argument("--output-dir", type=Path, default=ROOT / "qc/ratings-raw")
    p.add_argument("--private-dir", type=Path, default=ROOT / "derivatives/behavioral/raw-ratings")
    args = p.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True); args.private_dir.mkdir(parents=True, exist_ok=True)
    data = load_ratings(args.ratings, args.cohort)
    plot_ratings(data, args.output_dir)
    print(f"Raw six-cell plot: {len(data)} participants, no rating standardization.", flush=True)
    age = pd.concat([demographics(args.rf1_participants, "rf1"), demographics(args.ds_participants, "ds003745")])
    data = data.merge(age, on=KEYS, how="left", validate="one_to_one")
    keep = data.age.notna() & data.age.between(18, 110) & data.sex.isin(["F", "M", "O"])
    data.loc[~keep, KEYS + ["age", "sex"]].to_csv(args.private_dir / "missing-demographics.tsv", sep="\t", index=False)
    if not keep.all() and not args.allow_partial_age:
        raise ValueError(f"Plot complete, age analysis stopped: {int((~keep).sum())} missing/invalid demographics. Do not silently use the historical age subset.")
    model = data.loc[keep].copy()
    model[KEYS + ["age", "sex"] + CELLS].to_csv(args.private_dir / "analysis-input.tsv", sep="\t", index=False)
    all_tests, all_cells = [], []
    for scope, subset, adjust in (("pooled_dataset_sex_adjusted", model, True),
                                  ("pooled_dataset_adjusted", model, False),
                                  ("rf1_sex_adjusted", model.loc[model.dataset.eq("rf1")], True),
                                  ("ds003745_sex_adjusted", model.loc[model.dataset.eq("ds003745")], True)):
        test, cell = tests(subset, scope, adjust)
        all_tests.extend(test); all_cells.append(cell)
    pd.DataFrame(all_tests).to_csv(args.output_dir / "age-tests.tsv", sep="\t", index=False)
    pd.concat(all_cells).to_csv(args.output_dir / "age-slopes.tsv", sep="\t", index=False)
    evidence = dict(status="preliminary_partial_demographics" if not keep.all() else "exploratory_full_demographics",
        ratings_n=len(data), age_model_n=len(model), missing_demographics=int((~keep).sum()),
        age_source_label=args.age_source_label,
        sample_by_dataset={d: dict(n=len(g), min_age=float(g.age.min()), max_age=float(g.age.max())) for d,g in model.groupby("dataset")},
        method="Six-outcome subject-level OLS; continuous age per decade; dataset and recorded-sex offsets separately per cell; cross-outcome HC3 covariance; joint Wald chi-square tests; cell slope t intervals; Holm within stated families.",
        limitations=["Cross-sectional age association is not causal aging.", "No final imaging QC exclusions.",
                      "Ratings eligibility retains the existing identical/loss>win rules; response-based selection may affect associations.",
                      "Bounded ratings/ceiling effects and linear age specification require sensitivity review before publication.",
                      "Main plot includes all ratings-qualified participants, not only those with local ages."],
        sources=[dict(path=str(f.resolve()),sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in
                 (args.ratings,args.cohort,args.rf1_participants,args.ds_participants,Path(__file__))])
    (args.output_dir / "provenance.json").write_text(json.dumps(evidence, indent=2)+"\n")
    print(json.dumps(evidence, indent=2))
    print(pd.DataFrame(all_tests).to_string(index=False))


if __name__ == "__main__":
    main()
