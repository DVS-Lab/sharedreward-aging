#!/usr/bin/env python3

from pathlib import Path
import re
import sys

import pandas as pd
from natsort import natsorted


FMRIPREP_DIR = Path("../derivatives/fmriprep")
TEDANA_DIR = Path("../derivatives/tedana")
OUT_DIR = Path("../derivatives/fsl/confounds_tedana")

# Keep this True only if your downstream model is NOT doing its own high-pass filtering.
# fMRIPrep warns against combining cosine regressors with a separate high-pass filter.
INCLUDE_COSINE = True
N_ACOMPCOR = 6


def leading_nss_count(confounds_df: pd.DataFrame) -> int:
    """Return the number of consecutive non-steady-state volumes at run start."""
    nss_cols = [c for c in confounds_df.columns if c.startswith("non_steady_state_outlier")]
    if not nss_cols:
        return 0

    flags = (
        confounds_df[nss_cols]
        .fillna(0)
        .astype(float)
        .gt(0)
        .any(axis=1)
        .to_numpy()
    )

    n_dummy = 0
    for flag in flags:
        if flag:
            n_dummy += 1
        else:
            break
    return n_dummy


def parse_metric_file(metric_file: Path):
    """Extract subject, session, task, and run from a tedana metrics filename."""
    name = metric_file.name
    run_match = re.search(r"_run-([^_]+)_desc-tedana_metrics\.tsv$", name)
    task_match = re.search(r"_task-([^_]+)_run-", name)
    if run_match is None or task_match is None:
        raise ValueError(f"Could not parse task/run from {metric_file}")

    sub = metric_file.parent.parent.name
    ses = metric_file.parent.name
    task = task_match.group(1)
    run = run_match.group(1)
    return sub, ses, task, run


def get_rejected_component_timeseries(metrics_df: pd.DataFrame, mixing_df: pd.DataFrame) -> pd.DataFrame:
    """Return the rejected tedana component time series."""
    rejected_components = metrics_df.loc[
        metrics_df["classification"].astype(str).str.lower() == "rejected", "Component"
    ].tolist()

    missing = [component for component in rejected_components if component not in mixing_df.columns]
    if missing:
        raise ValueError(f"Rejected components not found in ICA mixing matrix: {missing}")

    if not rejected_components:
        return pd.DataFrame(index=mixing_df.index)

    return mixing_df[rejected_components].copy()


def trim_or_validate_mixing(mixing_df: pd.DataFrame, n_confounds: int, n_dummy: int) -> pd.DataFrame:
    """
    Align ICA mixing rows with the post-dummy-scan confounds length.

    If tedana was run with --dummy-scans, ICA_mixing.tsv will already be shortened.
    If tedana was run without --dummy-scans, trim it here so downstream FSL confounds line up.
    """
    if len(mixing_df) == (n_confounds - n_dummy):
        return mixing_df.reset_index(drop=True)
    if len(mixing_df) == n_confounds:
        return mixing_df.iloc[n_dummy:].reset_index(drop=True)

    raise ValueError(
        "ICA_mixing row count does not match either the full confounds length "
        f"({n_confounds}) or the trimmed length ({n_confounds - n_dummy})."
    )


def main() -> int:
    metric_files = natsorted(TEDANA_DIR.rglob("*desc-tedana_metrics.tsv"))
    if not metric_files:
        print("No tedana metrics files found.")
        return 0

    for metric_file in metric_files:
        try:
            sub, ses, task, run = parse_metric_file(metric_file)
        except ValueError as exc:
            print(f"Skipping {metric_file}: {exc}")
            continue

        prefix = metric_file.name.replace("_desc-tedana_metrics.tsv", "")
        mixing_file = metric_file.with_name(metric_file.name.replace("tedana_metrics.tsv", "ICA_mixing.tsv"))
        confounds_file = FMRIPREP_DIR / sub / ses / "func" / f"{sub}_{ses}_task-{task}_run-{run}_desc-confounds_timeseries.tsv"

        if not confounds_file.exists():
            print(f"Missing fMRIPrep confounds for {sub} {ses} run-{run}: {confounds_file}")
            continue
        if not mixing_file.exists():
            print(f"Missing ICA mixing file for {sub} {ses} run-{run}: {mixing_file}")
            continue

        print(f"Making confounds: {sub} {ses} task-{task} run-{run}")

        fmriprep_confounds = pd.read_csv(confounds_file, sep="\t")
        metrics_df = pd.read_csv(metric_file, sep="\t")
        mixing_df = pd.read_csv(mixing_file, sep="\t")

        n_dummy = leading_nss_count(fmriprep_confounds)
        mixing_df = trim_or_validate_mixing(mixing_df, n_confounds=len(fmriprep_confounds), n_dummy=n_dummy)
        fmriprep_confounds = fmriprep_confounds.iloc[n_dummy:].reset_index(drop=True)

        a_compcor = [f"a_comp_cor_{i:02d}" for i in range(N_ACOMPCOR) if f"a_comp_cor_{i:02d}" in fmriprep_confounds.columns]
        cosine = sorted([col for col in fmriprep_confounds.columns if col.startswith("cosine")]) if INCLUDE_COSINE else []
        motion = [col for col in ["trans_x", "trans_y", "trans_z", "rot_x", "rot_y", "rot_z"] if col in fmriprep_confounds.columns]
        fd = [col for col in ["framewise_displacement"] if col in fmriprep_confounds.columns]

        selected_cols = a_compcor + cosine + motion + fd
        nuisance_df = fmriprep_confounds[selected_cols].copy()
        nuisance_df = nuisance_df.fillna(0)

        rejected_df = get_rejected_component_timeseries(metrics_df, mixing_df)
        rejected_df = rejected_df.reset_index(drop=True)

        if len(nuisance_df) != len(rejected_df):
            raise ValueError(
                f"Row mismatch for {sub} {ses} task-{task} run-{run}: "
                f"nuisance={len(nuisance_df)}, rejected_components={len(rejected_df)}"
            )

        confounds_df = pd.concat([nuisance_df.reset_index(drop=True), rejected_df], axis=1)

        outdir = OUT_DIR / sub
        outdir.mkdir(parents=True, exist_ok=True)
        outname = outdir / f"{sub}_{ses}_task-{task}_run-{run}_desc-TedanaPlusConfounds.tsv"
        confounds_df.to_csv(outname, index=False, header=False, sep="\t")

    return 0


if __name__ == "__main__":
    sys.exit(main())
