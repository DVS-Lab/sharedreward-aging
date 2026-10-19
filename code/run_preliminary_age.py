#!/usr/bin/env python3
"""Exploratory pooled age associations after Cooper's recorded imaging exclusions.

Plan is read-only except for a new output/report directory. Independent ROI and
wholebrain stages each audit first; all runs both. Never refits FEAT.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_name] = "1"

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
from nibabel.processing import resample_from_to
import numpy as np
import pandas as pd
import scipy
from scipy import stats

from analyze_raw_ratings import demographics, holm, read
from audit_group_readiness import validate_manifests

ROOT = Path(__file__).resolve().parents[1]
KEY = ["dataset", "subject", "session"]
COPES = {10: "rew-pun", 11: "F-S", 12: "F-C", 14: "F-S (rew-pun)", 16: "F-C (rew-pun)"}
KINDS = ("act", "ppi_seed-vs")
ROI_FILES = {"VS": ROOT / "masks/seed-vs.nii.gz",
             "vmPFC": ROOT / "masks/VMPFC-mask-neurovault-resliced-bin.nii.gz"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def cohort(ledger_dir, rf1_participants, ds_participants, qc_path):
    provenance = json.loads((ledger_dir / "provenance.json").read_text())
    require(provenance["ledger_sha256"] == sha(ROOT / provenance["ledger"]),
            "Exclusion ledger changed: regenerate and review retained manifests first")
    require(provenance["n_pending_imaging_rows"] == 0 and provenance["pending_as"] == "fail",
            "Unresolved imaging decisions; no silent pending-as-retain")
    subjects, runs = read(ledger_dir / "retained-L2.tsv"), read(ledger_dir / "retained-L1.tsv")
    validate_manifests(runs.to_dict("records"), subjects.to_dict("records"))
    require(not subjects.duplicated(["dataset", "subject"]).any(),
            "Repeated sessions require a repeated-measures model, not independent rows")
    demo = pd.concat([demographics(rf1_participants, "rf1"), demographics(ds_participants, "ds003745")])
    data = subjects.merge(demo, on=["dataset", "subject"], how="left", validate="one_to_one")
    require(data.age.notna().all() and np.isfinite(data.age).all() and data.age.between(18, 110).all(),
            "Missing/invalid canonical age; no automatic subject dropping")
    require(data.sex.isin(["F", "M", "O"]).all(), "Missing/unknown recorded sex; no imputation")
    qc = read(qc_path)
    qc = qc[qc.stage == "post_target_blur"].copy()
    for frame in (qc, runs):
        frame["run_number"] = frame.run.astype(int)
    join = KEY + ["run_number"]
    require(not qc.duplicated(join).any(), "Duplicate run-level motion rows")
    motion = runs[join].merge(qc[join + ["mean_fd_mm", "fd_valid_values"]], on=join,
                             how="left", validate="one_to_one")
    for col in ("mean_fd_mm", "fd_valid_values"):
        motion[col] = pd.to_numeric(motion[col], errors="raise")
        require(np.isfinite(motion[col]).all(), "Missing/nonfinite retained-run motion")
    require((motion.mean_fd_mm >= 0).all() and (motion.fd_valid_values > 0).all(), "Invalid FD inputs")
    motion["fd_sum"] = motion.mean_fd_mm * motion.fd_valid_values
    totals = motion.groupby(KEY, dropna=False)[["fd_sum", "fd_valid_values"]].sum().reset_index()
    totals["retained_mean_fd_mm"] = totals.fd_sum / totals.fd_valid_values
    data = data.merge(totals[KEY + ["retained_mean_fd_mm"]], on=KEY, validate="one_to_one")
    return data.sort_values(KEY).reset_index(drop=True)


def design(data):
    columns = {"intercept": np.ones(len(data)),
               "age_decades_centered": (data.age.to_numpy() - data.age.mean()) / 10,
               "dataset_rf1": data.dataset.eq("rf1").to_numpy(float)}
    require(data.dataset.nunique() == 2, "This specification requires both datasets")
    for sex in sorted(data.sex.unique())[1:]:
        columns[f"sex_{sex}"] = data.sex.eq(sex).to_numpy(float)
    columns["retained_mean_fd_centered"] = data.retained_mean_fd_mm - data.retained_mean_fd_mm.mean()
    x = np.column_stack(list(columns.values())).astype(float)
    require(np.isfinite(x).all() and np.linalg.matrix_rank(x) == x.shape[1], "Invalid/rank-deficient design")
    require(len(data) > x.shape[1] + 10, "Insufficient residual degrees of freedom")
    return x, list(columns)


def hc3_age(x, y, column=1):
    """HC3 inference for a selected coefficient; legacy result key retained."""
    bread = np.linalg.inv(x.T @ x)
    beta = bread @ x.T @ y
    residual = y - x @ beta
    leverage = np.sum((x @ bread) * x, axis=1)
    require(np.max(leverage) < 1 - 1e-8, "Unit leverage prevents HC3 inference")
    influence = (x @ bread[:, column]) * residual / (1 - leverage)
    se = float(np.sqrt(influence @ influence))
    require(se > 0 and np.isfinite(se), "Degenerate ROI standard error")
    df = x.shape[0] - x.shape[1]
    critical = stats.t.ppf(.975, df)
    return dict(beta_per_decade=float(beta[column]), se_hc3=se,
                ci95_low=float(beta[column] - critical * se), ci95_high=float(beta[column] + critical * se),
                p_two_sided=float(2 * stats.t.sf(abs(beta[column] / se), df)), df=df)


def vest(path, array, contrast=False):
    rows, columns = array.shape
    header = f"/NumWaves\t{columns}\n/Num{'Contrasts' if contrast else 'Points'}\t{rows}\n/Matrix\n"
    with Path(path).open("w") as handle:
        handle.write(header)
        np.savetxt(handle, array, fmt="%.12g", delimiter="\t")


def command(args, log=None):
    print("COMMAND: " + " ".join(map(str, args)), flush=True)
    subprocess.run(list(map(str, args)), cwd=ROOT, check=True, stdout=log, stderr=subprocess.STDOUT if log else None)


def image_values(path, reference):
    img = nib.load(str(path))
    require(img.shape == reference.shape[:3] and np.allclose(img.affine, reference.affine, atol=1e-4, rtol=0),
            f"Image grid mismatch: {path}")
    values = img.get_fdata(dtype=np.float32)
    require(np.isfinite(values).all(), f"Nonfinite image: {path}")
    return values


def ordered_candidates(candidates, data, kind, cope):
    subset = candidates[(candidates.type == kind) & (candidates.cope.astype(int) == cope)]
    require(len(subset) == len(data) and not subset.duplicated(KEY).any(), "Wrong model inventory")
    rows = data[KEY + ["runs"]].merge(subset, on=KEY, how="left", validate="one_to_one", suffixes=("_retained", ""))
    require(rows.cope_path.notna().all() and rows.contrast.eq(COPES[cope]).all(), "Wrong/missing contrast")
    for row in rows.to_dict("records"):
        require({int(r) for r in row["runs"].split(",")} == {int(r) for r in row["runs_retained"].split(",")},
                "Model uses excluded run(s)")
    return rows


def prepare_model(rows, data, x, reference, folder, roi_masks, kind, cope, build_stack=True):
    folder.mkdir()
    common = np.ones(reference.shape[:3], dtype=bool)
    for row in rows.to_dict("records"):
        common &= image_values(row["mask_path"], reference) > 0
    require(common.any(), f"Empty common model mask: {kind} COPE{cope}")
    nib.save(nib.Nifti1Image(common.astype(np.uint8), reference.affine), folder / "mask.nii.gz")
    # Memory-mapped array limits RAM while retaining exact subject/design order.
    matrix = (np.lib.format.open_memmap(folder / "merged.npy", mode="w+", dtype="float32",
                                      shape=(*common.shape, len(rows))) if build_stack else None)
    rois = {name: mask & common for name, mask in roi_masks.items() if kind == "act" or name != "VS"}
    for name, mask in rois.items():
        require(mask.any(), f"No common coverage in ROI {name}")
    values = {name: [] for name in rois}
    for i, row in enumerate(rows.to_dict("records")):
        volume = image_values(row["cope_path"], reference)
        if matrix is not None:
            matrix[..., i] = np.where(common, volume, 0)
        for name, mask in rois.items():
            values[name].append(float(volume[mask].mean()))
    if matrix is not None:
        matrix.flush()
        nib.save(nib.Nifti1Image(matrix, reference.affine), folder / "copes.nii.gz")
        del matrix
        (folder / "merged.npy").unlink()  # Only this newly generated scratch array.
    roi_rows = []
    for name, y in values.items():
        roi_rows.append(dict(type=kind, cope=cope, contrast=COPES[cope], roi=name, n=len(y),
            roi_grid_voxels=int(roi_masks[name].sum()), common_roi_voxels=int(rois[name].sum()),
            common_roi_fraction=float(rois[name].sum() / roi_masks[name].sum()), **hc3_age(x, np.asarray(y))))
    private = data.copy()
    for name, y in values.items():
        private[f"mean_cope_{name}"] = y
    if values:
        private.to_csv(folder / "roi-subject-values.tsv", sep="\t", index=False)
    rows.to_csv(folder / "ordered-inputs.tsv", sep="\t", index=False)
    return roi_rows, dict(type=kind, cope=cope, contrast=COPES[cope], mask_voxels=int(common.sum()))


def randomise_model(folder, output, executable, permutations, seed):
    with (folder / "randomise.log").open("w") as log:
        command([executable, "-i", folder / "copes.nii.gz", "-o", folder / "age",
                 "-m", folder / "mask.nii.gz", "-d", output / "design.mat", "-t", output / "design.con",
                 "-e", output / "design.grp", "-T", "-n", permutations, f"--seed={seed}"], log)
    mask_image = nib.load(str(folder / "mask.nii.gz"))
    mask = mask_image.get_fdata() > 0
    results = []
    for number, direction in ((1, "positive"), (2, "negative")):
        corrected = image_values(folder / f"age_tfce_corrp_tstat{number}.nii.gz", mask_image)
        require(((corrected[mask] >= 0) & (corrected[mask] <= 1)).all(), "Invalid randomise corrected probabilities")
        # FSL corrp images are 1-p. Bonferroni over ten models and two directions.
        family_p = np.minimum(1., (1. - corrected) * (len(COPES) * len(KINDS) * 2))
        family_corrp = np.where(mask, 1. - family_p, 0).astype(np.float32)
        nib.save(nib.Nifti1Image(family_corrp, mask_image.affine), folder / f"age_family_corrp_tstat{number}.nii.gz")
        results.append(dict(direction=direction, min_p_voxelwise_fwe=float((1-corrected[mask]).min()),
                            min_p_across_20_maps=float(family_p[mask].min()),
                            voxels_p05_across_20_maps=int((family_p[mask] <= .05).sum())))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("plan", "roi", "wholebrain", "all"), default="plan")
    parser.add_argument("--mask-allowance", type=Path, help="Explicit provisional upstream-mask policy JSON")
    parser.add_argument("--label", required=True)
    parser.add_argument("--ledger-dir", type=Path, default=ROOT / "logs/records/exclusion-ledger")
    parser.add_argument("--rf1-participants", type=Path, default=ROOT.parent / "rf1-sra-linux2/bids/participants.tsv")
    parser.add_argument("--ds-participants", type=Path, default=ROOT / "participants-srndna.tsv")
    parser.add_argument("--qc", type=Path, default=ROOT / "logs/records/analysis-qc-run-level.tsv")
    parser.add_argument("--reference", type=Path, default=ROOT.parent / "rf1-sra-sharedreward/resources/rf1_MNI152NLin6Asym_reference_grid.nii.gz")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--permutations", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20261018)
    args = parser.parse_args()
    require(re.fullmatch(r"[A-Za-z0-9_-]+", args.label), "Unsafe label")
    require(1 <= args.jobs <= 10 and args.permutations >= 5000 and args.seed > 0, "Invalid execution settings")
    output = ROOT / "derivatives/preliminary-age" / args.label
    report = ROOT / "logs/records/preliminary-age" / args.label
    require(not output.exists() and not report.exists(), "Use a new label; outputs are never overwritten")
    data = cohort(args.ledger_dir, args.rf1_participants, args.ds_participants, args.qc)
    x, names = design(data)
    output.mkdir(parents=True)
    report.mkdir(parents=True)
    data.to_csv(output / "subject-design.tsv", sep="\t", index=False)
    vest(output / "design.mat", x)
    c = np.zeros((2, x.shape[1])); c[:, 1] = [1, -1]
    vest(output / "design.con", c, contrast=True)
    vest(output / "design.grp", np.where(data.dataset.eq("rf1"), 2, 1)[:, None])
    sources = [args.ledger_dir / name for name in ("provenance.json", "retained-L1.tsv", "retained-L2.tsv")]
    sources += [ROOT / "docs/exclusion_ledger.tsv", args.rf1_participants, args.ds_participants, args.qc,
                args.reference, Path(__file__), ROOT / "code/audit_group_readiness.py",
                ROOT / "templates/FULLTRIAL_CONTRAST_CANDIDATE.tsv", *ROI_FILES.values()]
    if args.mask_allowance:
        sources.append(args.mask_allowance)
    plan = dict(status="plan_only", n=len(data), retained_runs=int(data.n_runs.astype(int).sum()),
        n_by_dataset=data.groupby("dataset").size().to_dict(),
        age_by_dataset={k: dict(n=len(v), min=float(v.age.min()), max=float(v.age.max()), mean=float(v.age.mean()))
                        for k, v in data.groupby("dataset")},
        design_columns=names, age_center=float(data.age.mean()), fd_center=float(data.retained_mean_fd_mm.mean()),
        design_condition_number=float(np.linalg.cond(x)), contrasts=COPES, kinds=KINDS,
        permutations=args.permutations, seed=args.seed, jobs=args.jobs, stage=args.stage,
        mask_allowance=str(args.mask_allowance) if args.mask_allowance else None,
        method="Pooled common age slope; dataset, recorded sex, retained-volume-weighted mean FD; subject equal-weight OLS",
        roi_policy="VS activation; vmPFC activation and PPI. Existing provisional masks; common coverage; HC3; Holm 15 tests.",
        wholebrain_policy="Dataset-blocked randomise TFCE; positive and negative age; Bonferroni across 20 FWE-corrected maps",
        limitations=["Exploratory cross-sectional associations, not causal aging or a final preregistered L3 model.",
                     "Provisional seed/ROI provenance is not an independent confirmation claim.",
                     "Permutation inference assumes within-dataset exchangeability of nuisance-adjusted errors; dataset offsets/blocks do not guarantee homoscedasticity.",
                     "Equal subject weighting does not use varcope precision; differing retained-run reliability warrants sensitivity analysis.",
                     "Common-coverage masks restrict anatomical interpretation; ROI coverage fractions must be reviewed.",
                     "PPI is task-dependent coupling, not resting connectivity or directionality; full-trial is not phase-resolved."],
        git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        versions=dict(python=sys.version, numpy=np.__version__, scipy=scipy.__version__, nibabel=nib.__version__),
        sources=[dict(path=str(p), sha256=sha(p)) for p in sources])
    save_json(report / "plan.json", plan)
    n_maps = 0 if args.stage == "roi" else 10
    n_rois = 0 if args.stage == "wholebrain" else 15
    print(f"Age analysis plan ({args.stage}): {len(data)} people; {plan['retained_runs']} runs; "
          f"{n_maps} whole-brain models; {n_rois} ROI tests", flush=True)
    print(f"Design: {names}; private outputs: {output}; reports: {report}", flush=True)
    if args.stage == "plan":
        print("PLAN ONLY: no imaging models run or validated.")
        return
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[var] = "1"
    executable = shutil.which("randomise")
    require(executable or args.stage == "roi", "FSL randomise not on PATH")
    os.environ["FSLOUTPUTTYPE"] = "NIFTI_GZ"
    fsl_version_file = Path(os.environ.get("FSLDIR", "/usr/local/fsl")) / "etc/fslversion"
    require(fsl_version_file.is_file(), "FSLDIR/etc/fslversion unavailable; initialize FSL first")
    save_json(report / "fsl-environment.json", dict(randomise=executable,
        fsl_version=fsl_version_file.read_text().strip(), threads_per_process=1, FSLOUTPUTTYPE="NIFTI_GZ"))
    command([sys.executable, ROOT / "code/audit_group_readiness.py",
             "--l1-manifest", args.ledger_dir / "retained-L1.tsv",
             "--subject-manifest", args.ledger_dir / "retained-L2.tsv",
             "--fsl-root", ROOT / "derivatives/fsl", "--reference", args.reference,
             "--report-dir", report / "readiness"] +
            (["--mask-allowance", args.mask_allowance] if args.mask_allowance else []))
    readiness = json.loads((report / "readiness/summary.json").read_text())
    require(readiness["computational_gate_passed"], "Readiness failed; no analysis launched")
    plan["status"] = "provisional_existing_feat" if readiness["provisional"] else "verified_inputs"
    plan["provisional"] = readiness["provisional"]
    plan["mask_provenance_warnings"] = readiness["mask_provenance_warnings"]
    save_json(report / "plan.json", plan)
    require(all(sha(p["path"]) == p["sha256"] for p in plan["sources"]),
            "Input specification changed during audit; use a fresh run label")
    candidates = read(report / "readiness/verified-pre-QC-candidates.tsv")
    reference = nib.load(str(args.reference))
    roi_masks = {}
    for name, path in (ROI_FILES.items() if args.stage != "wholebrain" else []):
        image = nib.load(str(path))
        require(len(image.shape) == 3 and np.isfinite(image.get_fdata()).all(), "Invalid ROI")
        roi_masks[name] = resample_from_to(image, (reference.shape[:3], reference.affine), order=0).get_fdata() > 0
        require(roi_masks[name].any(), f"Empty reference-grid ROI: {name}")
        nib.save(nib.Nifti1Image(roi_masks[name].astype(np.uint8), reference.affine), output / f"roi-{name}.nii.gz")
    roi_results, model_info = [], []
    for kind in KINDS:
        for cope in COPES:
            folder = output / f"{kind}_cope-{cope}"
            rows = ordered_candidates(candidates, data, kind, cope)
            roi, info = prepare_model(rows, data, x, reference, folder, roi_masks, kind, cope,
                                      build_stack=args.stage != "roi")
            roi_results.extend(roi)
            model_info.append((folder, info))
            print(f"Prepared {folder.name}: common mask {info['mask_voxels']} voxels", flush=True)
    if args.stage != "wholebrain":
        write_roi_results(roi_results, report, readiness["provisional"])
    if args.stage == "roi":
        save_json(report / "completion.json", dict(complete=True, stage="roi", roi_tests=len(roi_results),
            finished_maps=0, provisional=readiness["provisional"], plan_sha256=sha(report / "plan.json")))
        print("CHECK PASSED: ROI age analysis complete (15 tests); no whole-brain permutations requested.", flush=True)
        return
    results, failures = [], []
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(randomise_model, folder, output, executable, args.permutations, args.seed): (folder, info)
                   for folder, info in model_info}
        for future in as_completed(futures):
            folder, info = futures[future]
            try:
                results.extend(dict(info, **row) for row in future.result())
                print(f"DONE: {folder.name}", flush=True)
            except Exception as error:
                failures.append(dict(model=folder.name, error=str(error)))
                print(f"ERROR: {folder.name}: {error}", flush=True)
    pd.DataFrame(results).to_csv(report / "wholebrain-age-summary.tsv", sep="\t", index=False)
    save_json(report / "completion.json", dict(complete=not failures and len(results) == 20,
        stage=args.stage, provisional=readiness["provisional"], roi_tests=len(roi_results),
        finished_maps=len(results), failures=failures,
        randomise_executable=executable, readiness=readiness["counts"], plan_sha256=sha(report / "plan.json")))
    require(not failures and len(results) == 20, "Incomplete randomise models; inspect per-model logs, do not rerun FEAT")
    print(f"CHECK PASSED: age analysis complete (20 signed maps, {len(roi_results)} ROI tests).", flush=True)


def write_roi_results(roi_results, report, provisional=False):
    roi = pd.DataFrame(roi_results)
    require(len(roi) == 15, "Unexpected ROI family size")
    roi["p_holm_15"] = holm(roi.p_two_sided)
    roi.to_csv(report / "roi-age-results.tsv", sep="\t", index=False)
    fig, ax = plt.subplots(figsize=(9, 8))
    positions = np.arange(len(roi))
    ax.errorbar(roi.beta_per_decade, positions,
                xerr=np.vstack([roi.beta_per_decade-roi.ci95_low, roi.ci95_high-roi.beta_per_decade]), fmt="o", capsize=3)
    ax.set_yticks(positions, [f"{r.type} | {r.roi} | {r.contrast}" for r in roi.itertuples()])
    ax.axvline(0, color="gray", linestyle="--"); ax.invert_yaxis()
    ax.set_xlabel("COPE change per decade (HC3 pointwise 95% CI; not percent signal change)")
    ax.set_title("Exploratory pooled age associations | provisional ROIs" +
                 ("\nUpstream mask provenance review pending" if provisional else ""))
    fig.tight_layout(); fig.savefig(report / "roi-age-effects.png", dpi=180); plt.close(fig)


if __name__ == "__main__":
    main()
