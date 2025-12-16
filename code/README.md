# SharedReward project scripts

This folder contains helper scripts for a Shared Reward fMRI project (OpenNeuro-style/BIDS layout) that cover: data download, BIDS event-file generation, preprocessing/QC (fMRIPrep, MRIQC, TE-DENOISE), FSL FEAT modeling (L1/L2/L3), and a few utilities for behavioral/covariate tables.

Most scripts assume a specific directory layout and include hard-coded paths (e.g., `/ZPOOL/...` or `/gpfs/...`). Start by editing the path variables near the top of each script to match your environment.

## Data acquisition and BIDS formatting

- `get_data.sh` — Installs OpenNeuro datasets via `datalad` (intended for pulling the raw BIDS datasets that the project analyzes).
- `ds003745-2.1.1.sh` — A long, auto-generated `curl` script that downloads many ds003745 files directly from OpenNeuro/S3 (useful when `datalad` is failing or you only want specific files).
- `convertSharedReward_BIDS.m` — MATLAB script that converts task log output into BIDS-style `events.tsv` files (and tracks basic counts like trials/misses).

## Preprocessing and denoising

- `fmriprep.sh` — Runs fMRIPrep (via Singularity) for one subject and writes outputs under `derivatives/fmriprep`.
- `run_fmriprep.sh` — Wrapper that runs `fmriprep.sh` across a subject list with simple concurrency limiting.
- `fmriprep-hpc.sh` — PBS/Torque job script that builds and launches many fMRIPrep participant commands on an HPC node using `torque-launch`.
- `sr-fmriprep-hpc.sh` — A project-specific variant of the HPC fMRIPrep launcher (same idea as `fmriprep-hpc.sh`, with paths/settings tuned for this dataset).
- `run_fmriprep-hpc.sh` — Submits the HPC fMRIPrep launcher in batches (chunks a subject list and `qsub`s multiple jobs).

- `mriqc.sh` — Runs MRIQC (via Singularity) for one subject to generate QC metrics for T1w and task BOLD.
- `run_mriqc.sh` — Wrapper that runs `mriqc.sh` across a subject list with limited parallel jobs.

- `tedana.sh` — Runs TEDANA for one subject/run using multi-echo fMRIPrep outputs, writes to `derivatives/tedana`, and logs missing inputs.
- `run_tedana.sh` — Wrapper that runs `tedana.sh` across subjects and both runs with simple concurrency limiting.
- `genTedanaConfounds.py` — Builds “FSL-ready” confound files by combining selected fMRIPrep regressors with TEDANA component regressors (e.g., rejected components).

## FSL FEAT modeling (Level 1/2/3)

- `L1stats-hpc.sh` — PBS/Torque script that generates FEAT `.fsf` files from templates and runs Level-1 FEAT models (activation and/or seed-based PPI, depending on settings).
- `run_L1stats-hpc.sh` — Batch-submission helper that chunks a subject list and submits `L1stats-hpc.sh` jobs with `qsub`.

- `L2stats.sh` — Runs Level-2 FEAT (within-subject fixed-effects across runs) for one subject and one analysis “type”, then deletes large intermediate files to save space.
- `run_L2stats.sh` — Wrapper that runs `L2stats.sh` across a subject list (and optional analysis types) with basic concurrency limiting.
- `L2stats-hpc.sh` — PBS/Torque version of the Level-2 FEAT runner that assembles `.fsf` files and executes them via `torque-launch`.
- `run_L2stats-hpc.sh` — Batch-submission helper that chunks subject lists and submits `L2stats-hpc.sh` jobs.

- `L3stats.sh` — Runs a single Level-3 FEAT group analysis for one cope/contrast (driven by template `.fsf` files and a “replace-me” path tag).
- `run_L3stats.sh` — Wrapper that loops over pre-specified copes/contrasts and runs `L3stats.sh` with basic concurrency limiting.
- `L3stats-hpc.sh` — PBS/Torque version of Level-3 FEAT that prepares `.fsf` files and launches them via `torque-launch`.
- `run_L3stats-hpc.sh` — Generates per-cope FEAT jobs for group analysis and writes them out in a launcher-friendly format (intended for HPC execution).

- `L2paths.sh` — Utility that prints the paths to existing Level-1 cope images for a list of subjects (handy when building higher-level input lists).
- `L3paths.sh` — Utility that prints the paths to subject-level cope images (from L2 `.gfeat` when present, otherwise from L1) for use as Level-3 inputs.

## QC and sanity checks

- `checkmask.sh` — Computes FEAT mask voxel counts for each subject and compares them to a standard MNI brain mask to estimate coverage.
- `checkzstats.sh` — Runs `fslstats -R` on a list of NIfTI files (e.g., z-stats) to quickly spot extreme or invalid ranges.
- `cleanL1-linuxbox.sh` — Post-processing cleanup for Level-1 FEAT folders (fixes registration matrices for fMRIPrep-aligned data and deletes large intermediate files).

- `fdmean_conf.py` — Extracts and prints mean framewise displacement from fMRIPrep confounds TSVs, organized by subject/run.
- `fdmean_avg.py` — Extracts and prints `fd_mean` values from MRIQC JSON outputs (one entry per file/participant/run).
- `fdmean_outliers.R` — Reads a motion summary CSV and visualizes the distribution/outliers (with a simple SRNDNA vs RF1 split based on subject-ID length).

- `tsnr_stan.sh` — Computes tSNR from preprocessed BOLD in standard space and reports the mean tSNR within a ventral striatum mask.

- `gen_missingevs.sh` — Creates placeholder EV text files (contents `0 0 0`) so FEAT models still run when a condition has no events.
- `empty_ev_check.py` — Scans EV files and outputs a coded table indicating which EVs contain real events versus placeholders.
- `missingtrials.py` — Summarizes EV row counts and missed-trial counts per subject/run and writes a CSV that can support exclusion/QC decisions.

- `extract-flip.py` — Extracts FlipAngle values from BIDS JSON sidecars and writes a CSV with a simple “coded” flag for unusual values.

## Anatomical alignment and DeepBrainNet

- `flirt.sh` — Skull-strips each subject’s T1w using the fMRIPrep brain mask and affine-registers it to an MNI template (to create inputs for DeepBrainNet).
- `run_flirt.sh` — Wrapper that runs `flirt.sh` across a subject list with basic concurrency limiting.
- `deepbrain.sh` — Runs DeepBrainNet’s testing script on the aligned anatomical images and writes outputs under `derivatives/deepbrain`.

## Behavioral logs and covariates

- `transform_logs.py` — Reformats raw rating-log CSVs into a consistent column structure and writes them into a “reformatted” directory.
- `gen_covariates.py` — Collects rating logs and merges them with participant metadata (e.g., age) as a starting point for building covariates.
- `justcombinethem.py` — Joins an existing “combined logs” table to participant metadata and writes an updated combined CSV (e.g., with age included).

- `sr_behavioral.R` — Computes and plots average rating responses (with SEM) by partner condition and trait.
- `sr_behavioral-age.R` — Creates difference-score variables and sets up summaries intended for age-related behavioral analyses.

- `sharedreward-covariates.ipynb` — Notebook used to assemble, QA-check, and reshape covariate tables that align with group-model input files.
- `new-covs.ipynb` — Exploratory notebook for testing/visualizing candidate covariates (e.g., distributions, standardization, correlations).

## HPC transfer helpers

- `transferbids-hpc.sh` — Uses `rsync` to copy selected BIDS subject folders from a local path to an HPC destination (prompts for an AccessNet ID).
- `transferL1-hpc.sh` — Uses `rsync` to copy fMRIPrep derivatives and `events.tsv` files to an HPC destination (one subject at a time).
