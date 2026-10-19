#!/usr/bin/env python3
"""Pooled FEAT/FLAME 1 age and matched-ratings models; never reruns L1/L2."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"
os.environ["FSLSUB_PARALLEL"] = "1"

import nibabel as nib
from nibabel.processing import resample_from_to
import numpy as np
import pandas as pd
from analyze_raw_ratings import read, holm
from audit_ratings_qc import rating_exclusion_reasons
from audit_group_readiness import matrix, selected_contrasts, fsf_settings
from run_preliminary_age import (ROOT, KEY, KINDS, ROI_FILES, cohort, require, sha,
                                 save_json, image_values, hc3_age, plt)

CONTRASTS = {10: "rew-pun", 11: "F-S", 12: "F-C", 14: "F-S (rew-pun)",
             16: "F-C (rew-pun)", 17: "F-S (rew)"}
TEMPLATES = {family: ROOT / f"templates/L3_template_pooled_{family}_flame1.fsf"
             for family in ("age", "age-ratings")}


def verify_qc_exclusions(runs, qc, thresholds):
    """Check frozen dataset-specific rules, never recompute cutoffs on survivors."""
    def key(row):
        return tuple(str(row[k]) for k in KEY) + (int(row["run"]),)
    retained = {key(row) for row in runs.to_dict("records")}
    current = qc[qc.stage.eq("post_target_blur")]
    summary = []
    expected = {(dataset, metric) for dataset in runs.dataset.unique()
                for metric in ("mean_fd_mm", "median_tsnr", "coverage_pct")}
    require(set(zip(thresholds.dataset, thresholds.metric)) == expected
            and len(thresholds) == len(expected), "Incomplete/duplicate QC thresholds")
    for row in thresholds.to_dict("records"):
        subset = current[current.dataset.eq(row["dataset"])]
        values = pd.to_numeric(subset[row["metric"]], errors="raise")
        require(np.isfinite(values).all(), "Nonfinite QC metric")
        threshold = float(row["threshold"])
        require(row["direction"] in ("above", "below"), "Invalid QC direction")
        flagged = subset[values.gt(threshold) if row["direction"] == "above" else values.lt(threshold)]
        overlap = [key(unit) for unit in flagged.to_dict("records") if key(unit) in retained]
        require(not overlap, f"QC-outlier runs retained: {row['metric']}: {overlap}")
        summary.append(dict(dataset=row["dataset"], metric=row["metric"], threshold=threshold,
                            direction=row["direction"], flagged_runs=len(flagged), retained_flagged_runs=0))
    return summary


def add_tsnr(data, runs, qc):
    """Mean of per-run median whole-brain tSNR over retained runs only."""
    runs, qc = runs.copy(), qc[qc.stage == "post_target_blur"].copy()
    for frame in (runs, qc):
        frame["run_number"] = frame.run.astype(int)
    keys = KEY + ["run_number"]
    require(not qc.duplicated(keys).any(), "Duplicate tSNR QC rows")
    joined = runs[keys].merge(qc[keys + ["median_tsnr"]], on=keys, how="left", validate="one_to_one")
    joined["median_tsnr"] = pd.to_numeric(joined.median_tsnr, errors="raise")
    require(np.isfinite(joined.median_tsnr).all() and (joined.median_tsnr > 0).all(), "Missing/invalid tSNR")
    means = joined.groupby(KEY, dropna=False).median_tsnr.mean().reset_index(name="retained_tsnr")
    return data.merge(means, on=KEY, validate="one_to_one")


def rating_cohort(data, ratings):
    require(not ratings.duplicated(["dataset", "subject"]).any(), "Duplicate ratings")
    joined = data.merge(ratings, on=["dataset", "subject"], how="left", validate="one_to_one")
    eligible, reasons = [], []
    for _, row in joined.iterrows():
        reason = []
        if str(row.ratings_eligible).lower() != "true":
            reason.append("imaging_ledger_ratings_ineligible")
        if str(row.get("exclude_subject", "")).lower() != "false":
            reason.append("ratings_audit_ineligible_or_missing")
        if not reason:
            means = {(p, t): float(row[f"partner_{p}_trait_{t}_mean"])
                     for p in (1, 2, 3) for t in (0, 1)}
            reason.extend(rating_exclusion_reasons(means))
        eligible.append(not reason)
        reasons.append(";".join(reason))
    eligibility = joined[KEY].copy()
    eligibility["included"] = eligible
    eligibility["reason"] = reasons
    selected = joined.loc[eligible].copy()
    require(len(selected) > 10, "Too few ratings-eligible subjects")
    # Source coding is Computer=1, Stranger=2, Friend=3; trait 0=win.
    selected["rating_score"] = (selected.partner_3_trait_0_mean.astype(float)
                                - selected.partner_2_trait_0_mean.astype(float))
    return selected, eligibility


def design(data, family):
    columns = {"intercept": np.ones(len(data))}
    if family == "age-ratings":
        columns["friend_win_minus_stranger_win_rating"] = data.rating_score - data.rating_score.mean()
    columns["age_decades"] = (data.age - data.age.mean()) / 10
    columns["tsnr"] = data.retained_tsnr - data.retained_tsnr.mean()
    columns["fdmean_mm"] = data.retained_mean_fd_mm - data.retained_mean_fd_mm.mean()
    columns["dataset_rf1"] = data.dataset.eq("rf1").astype(float)
    require(data.dataset.nunique() == 2, "Both datasets are required")
    x = np.column_stack(list(columns.values())).astype(float)
    require(np.isfinite(x).all() and np.linalg.matrix_rank(x) == x.shape[1], "Nonfinite/rank-deficient L3 design")
    require(len(data) > x.shape[1] + 10, "Insufficient residual degrees of freedom")
    indices = [1] if family == "age" else [1, 2]
    c = np.zeros((len(indices)*2, x.shape[1]))
    names = []
    for i, col in enumerate(indices):
        c[2*i, col], c[2*i+1, col] = 1, -1
        names.extend([list(columns)[col] + "_positive", list(columns)[col] + "_negative"])
    return x, c, list(columns), names


def quote(value):
    value = str(value)
    require(not any(c in value for c in ('"', '$', '[', ']', '\\', '\n', '\r')), "Unsafe Tcl value")
    return '"' + value + '"'


def render(family, output, inputs, x, c, columns, names, standard):
    text = TEMPLATES[family].read_text()
    replacements = {"OUTPUT": str(output), "N": str(len(inputs)), "EVS": str(x.shape[1]),
                    "CONS": str(len(c)), "STANDARD": str(standard)}
    for key, value in replacements.items():
        quote(value)
        text = text.replace(f"@{key}@", value)
    require("@" not in text, "Unresolved template placeholder")
    lines = [text]
    for i, path in enumerate(inputs, 1):
        lines += [f"set feat_files({i}) {quote(path)}", f"set fmri(groupmem.{i}) 1"]
        for j, value in enumerate(x[i-1], 1):
            lines.append(f"set fmri(evg{i}.{j}) {value:.12g}")
    for j, name in enumerate(columns, 1):
        for key, value in {f"evtitle{j}": quote(name), f"shape{j}": 2, f"convolve{j}": 0,
                           f"convolve_phase{j}": 0, f"tempfilt_yn{j}": 0, f"deriv_yn{j}": 0,
                           f"custom{j}": '"dummy"'}.items():
            lines.append(f"set fmri({key}) {value}")
        for k in range(x.shape[1]+1):
            lines.append(f"set fmri(ortho{j}.{k}) 0")
    for i, name in enumerate(names, 1):
        for mode in ("orig", "real"):
            lines += [f"set fmri(conpic_{mode}.{i}) 1", f"set fmri(conname_{mode}.{i}) {quote(name)}"]
            for j, value in enumerate(c[i-1], 1):
                lines.append(f"set fmri(con_{mode}{i}.{j}) {value:g}")
        for j in range(1, len(c)+1):
            lines.append(f"set fmri(conmask{i}_{j}) 0")
    return "\n".join(lines) + "\n"


def ordered(candidates, data, kind, cope):
    subset = candidates[(candidates.type == kind) & (candidates.cope.astype(int) == cope)]
    require(not subset.duplicated(KEY).any(), "Duplicate candidate input")
    rows = data[KEY + ["runs"]].merge(subset, on=KEY, how="left", validate="one_to_one", suffixes=("_retained", ""))
    require(rows.cope_path.notna().all() and rows.contrast.eq(CONTRASTS[cope]).all(), "Wrong/missing COPE")
    for row in rows.to_dict("records"):
        require(set(map(int, row["runs"].split(","))) == set(map(int, row["runs_retained"].split(","))), "Retained runs differ")
    return rows


def input_dof(row, reference):
    cope = Path(row["cope_path"])
    number = int(re.fullmatch(r"cope(\d+)\.nii\.gz", cope.name)[1])
    original = cope.parent.parent
    dof = original / f"stats/tdof_t{number}.nii.gz"
    if dof.is_file():
        return image_values(dof, reference), dof
    scalar = original / "stats/dof"
    require(row["strategy"] == "l1_passthrough", f"Missing fixed-effects DOF map: {dof}")
    value = float(scalar.read_text().strip())
    require(np.isfinite(value) and value > 0, f"Invalid L1 DOF: {scalar}: {value}")
    return np.full(reference.shape[:3], value, dtype=np.float32), scalar


def audit_dof_inputs(rows, reference, common, destination):
    """Inspect all subjects, preserving the ordinary FEAT mask and input values."""
    require(common.any(), "Empty group mask")
    records = []
    for row in rows.to_dict("records"):
        item = {k: row.get(k, "") for k in (*KEY, "runs", "cope", "strategy", "cope_path")}
        item.update(status="verified", problem="", common_mask_voxels=int(common.sum()))
        try:
            individual = image_values(row["mask_path"], reference) > 0
            require(not (common & ~individual).any(), "Group mask extends outside input mask")
            dof, path = input_dof(row, reference)
            var = image_values(row["varcope_path"], reference)
            invalid = dof <= 0
            item.update(dof_source=str(path), individual_mask_voxels=int(individual.sum()),
                        min_dof_in_common=float(dof[common].min()), max_dof_in_common=float(dof[common].max()),
                        nonpositive_dof_in_individual=int((invalid & individual).sum()),
                        nonpositive_dof_in_common=int((invalid & common).sum()),
                        nonpositive_dof_outside_common=int((invalid & individual & ~common).sum()),
                        nonpositive_dof_with_positive_varcope_in_common=int((invalid & common & (var > 0)).sum()))
            require(not (invalid & common).any(), f"Nonpositive DOF inside group mask: {path}")
        except (ValueError, OSError) as error:
            item.update(status="failed", problem=str(error))
        records.append(item)
    result = pd.DataFrame(records).fillna("")
    result.to_csv(destination, sep="\t", index=False)
    return result


def stage_input(row, folder, reference, common=None):
    """Read-only symlink adapters for already-standard-space maps, not new fits.

    design.lev tells FEAT not to re-register these verified RF1-grid inputs.
    Exact COPE/VARCOPE/DOF, original contrast scaling and mean_func are preserved.
    """
    cope, varcope, mask = (Path(row[k]) for k in ("cope_path", "varcope_path", "mask_path"))
    original = cope.parent.parent
    number = int(re.fullmatch(r"cope(\d+)\.nii\.gz", cope.name)[1])
    folder.mkdir(parents=True)
    (folder / "stats").mkdir()
    for source, dest in ((cope, folder / "stats" / cope.name), (varcope, folder / "stats" / varcope.name),
                         (mask, folder / "mask.nii.gz")):
        image_values(source, reference)
        dest.symlink_to(source.resolve(strict=True))
    dof = original / f"stats/tdof_t{number}.nii.gz"
    individual = image_values(mask, reference) > 0
    scope = individual if common is None else common
    require(scope.any() and not (scope & ~individual).any(), "Invalid group mask")
    values, dof_source = input_dof(row, reference)
    require((values[scope] > 0).all(), f"Nonpositive DOF inside analysis mask: {dof_source}")
    if dof.is_file():
        (folder / "stats" / dof.name).symlink_to(dof.resolve())
    else:
        nib.save(nib.Nifti1Image(values, reference.affine),
                 folder / "stats" / dof.name)
    for name in ("design.con", "design.lcon"):
        if (original / name).is_file():
            shutil.copy2(original / name, folder / name)
    require((folder / "design.con").is_file(), "Missing contrast scaling")
    for name in ("mean_func.nii.gz", "example_func.nii.gz"):
        source = original / name
        if not source.is_file():
            source = original / "mean_func.nii.gz"
        image_values(source, reference)
        (folder / name).symlink_to(source.resolve(strict=True))
    (folder / "design.lev").write_text("2\n")
    save_json(folder / "input-adapter.json", dict(role="standard-space input adapter, not a refit", source=row))
    return folder / "stats" / cope.name


def run_command(cmd, log=None):
    print("COMMAND: " + " ".join(map(str, cmd)), flush=True)
    subprocess.run(list(map(str, cmd)), check=True, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT if log else None)


def audit_fit(output, x, c, reference, expected_mask=None):
    stats = output / "cope1.feat"
    require(np.allclose(matrix(stats / "design.mat"), x, atol=1e-5, rtol=1e-6), "Fitted design differs")
    require(np.array_equal(matrix(stats / "design.con"), c), "Fitted contrasts differ")
    settings = fsf_settings(output / "design.fsf")
    require(settings["fmri(mixed_yn)"] == "2", "Not FLAME 1")
    mask = image_values(stats / "mask.nii.gz", reference) > 0
    require(mask.any(), "Empty group mask")
    if expected_mask is not None:
        require(np.array_equal(mask, expected_mask), "Fitted mask differs from audited group mask")
    summary = []
    for i in range(1, len(c)+1):
        for name in ("cope", "varcope", "zstat"):
            values = image_values(stats / f"stats/{name}{i}.nii.gz", reference)
            if name == "varcope":
                require((values[mask] >= 0).all() and (values[mask] > 0).any(), "Invalid FLAME variance")
        cluster = image_values(stats / f"cluster_mask_zstat{i}.nii.gz", reference)
        cluster_table(stats, i)
        summary.append(dict(contrast=i, surviving_voxels=int((cluster>0).sum()),
                            max_abs_z=float(np.max(np.abs(values[mask])))))
    return summary


def cluster_table(stats, number):
    # Higher-level FEAT reports cluster coordinates in standard space.
    for suffix in ("_std", ""):
        path = stats / f"cluster_zstat{number}{suffix}.txt"
        if path.is_file():
            return path
    raise ValueError(f"Missing cluster table: {stats}, zstat{number}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", choices=("plan", "roi", "inputs", "wholebrain", "all"), default="plan")
    p.add_argument("--label", required=True)
    p.add_argument("--jobs", type=int, default=4)
    p.add_argument("--with-ratings", action="store_true")
    p.add_argument("--mask-allowance", type=Path)
    p.add_argument("--ledger-dir", type=Path, default=ROOT / "logs/records/exclusion-ledger")
    p.add_argument("--qc", type=Path, default=ROOT / "logs/records/analysis-qc-run-level.tsv")
    p.add_argument("--ratings", type=Path, default=ROOT / "logs/records/ratings-qc-subject-level.tsv")
    p.add_argument("--rf1-participants", type=Path, default=ROOT.parent / "rf1-sra-linux2/bids/participants.tsv")
    p.add_argument("--ds-participants", type=Path, default=ROOT / "participants-srndna.tsv")
    p.add_argument("--reference", type=Path, default=ROOT.parent / "rf1-sra-sharedreward/resources/rf1_MNI152NLin6Asym_reference_grid.nii.gz")
    args = p.parse_args()
    require(re.fullmatch(r"[A-Za-z0-9_-]+", args.label) and 1 <= args.jobs <= 8, "Invalid label/jobs")
    out = ROOT / "derivatives/fsl/L3-preliminary" / args.label
    report = ROOT / "logs/records/L3-preliminary" / args.label
    require(not out.exists() and not report.exists(), "Use a new label; never overwrites output")
    data = cohort(args.ledger_dir, args.rf1_participants, args.ds_participants, args.qc)
    data = add_tsnr(data, read(args.ledger_dir / "retained-L1.tsv"), read(args.qc))
    qc_exclusions = verify_qc_exclusions(read(args.ledger_dir / "retained-L1.tsv"), read(args.qc),
                                         read(args.ledger_dir / "iqr-thresholds.tsv"))
    out.mkdir(parents=True); report.mkdir(parents=True)
    cohorts = {"age": data}
    if args.with_ratings:
        cohorts["age-ratings"], eligibility = rating_cohort(data, read(args.ratings))
        eligibility.to_csv(out / "ratings-eligibility.tsv", sep="\t", index=False)
    specs = []
    for family, people in cohorts.items():
        x, c, columns, names = design(people, family)
        people.to_csv(out / f"{family}-subject-design.tsv", sep="\t", index=False)
        for kind in KINDS:
            for cope in (CONTRASTS if family == "age" else (17,)):
                specs.append(dict(family=family, kind=kind, cope=cope, n=len(people), columns=columns, names=names))
    sources = [Path(__file__), ROOT / "code/L3stats.sh", *TEMPLATES.values(), args.qc,
               args.rf1_participants, args.ds_participants, args.ledger_dir / "retained-L1.tsv",
               args.ledger_dir / "retained-L2.tsv", args.ledger_dir / "provenance.json",
               args.ledger_dir / "iqr-thresholds.tsv", ROOT / "code/run_preliminary_age.py",
               ROOT / "code/audit_ratings_qc.py", ROOT / "code/analyze_raw_ratings.py",
               ROOT / "docs/exclusion_ledger.tsv", ROOT / "code/audit_group_readiness.py", *ROI_FILES.values()]
    if args.with_ratings: sources.append(args.ratings)
    if args.mask_allowance: sources.append(args.mask_allowance)
    plan = dict(stage=args.stage, engine="FEAT FLAME1", specifications=specs,
                qc_exclusion_verification=qc_exclusions,
                tsnr="mean of retained-run whole-brain median tSNR from smoothed FEAT-input QC",
                fd="valid-FD-volume-weighted mean over retained runs", robust_outliers=False,
                inference="Z>3.1, cluster p<0.05 per signed map; no across-model multiplicity correction",
                sources=[dict(path=str(path), sha256=sha(path)) for path in sources])
    save_json(report / "plan.json", plan)
    print(f"Plan: {len(data)} imaging participants; {len(specs)} FEAT models; stage={args.stage}", flush=True)
    if args.stage == "plan": return
    for tool in (("feat", "flameo", "feat_model") if args.stage in ("wholebrain", "all") else ()):
        require(shutil.which(tool) is not None, f"Missing FSL tool: {tool}")
    run_command([sys.executable, ROOT / "code/audit_group_readiness.py", "--l1-manifest",
        args.ledger_dir / "retained-L1.tsv", "--subject-manifest", args.ledger_dir / "retained-L2.tsv",
        "--reference", args.reference, "--fsl-root", ROOT / "derivatives/fsl", "--report-dir", report / "readiness"] +
        (["--mask-allowance", args.mask_allowance] if args.mask_allowance else []))
    readiness = json.loads((report / "readiness/summary.json").read_text())
    require(readiness["computational_gate_passed"], "Readiness failed")
    require(all(sha(item["path"]) == item["sha256"] for item in plan["sources"]), "Inputs changed during audit")
    plan["provisional"] = readiness["provisional"]
    plan["mask_provenance_warnings"] = readiness["mask_provenance_warnings"]
    save_json(report / "plan.json", plan)
    candidates = read(report / "readiness/verified-pre-QC-candidates.tsv")
    reference = nib.load(args.reference)
    jobs, prepared, roi_rows = [], [], []
    for spec in specs:
        family, kind, cope = spec["family"], spec["kind"], spec["cope"]
        people = cohorts[family]
        x, c, columns, names = design(people, family)
        rows = ordered(candidates, people, kind, cope)
        folder = out / f"{family}_{kind}_cope-{cope}"
        folder.mkdir()
        rows.to_csv(folder / "ordered-inputs.tsv", sep="\t", index=False)
        common = np.ones(reference.shape[:3], dtype=bool)
        for row in rows.to_dict("records"): common &= image_values(row["mask_path"], reference)>0
        require(common.any(), f"Empty group mask: {folder.name}")
        if args.stage in ("all", "roi"):
            for name, path in ROI_FILES.items():
                if kind != "act" and name == "VS": continue
                mask = resample_from_to(nib.load(path), (reference.shape[:3], reference.affine), order=0).get_fdata()>0
                full_n = int(mask.sum()); mask &= common
                require(mask.any(), f"Empty ROI: {name}")
                y = np.array([image_values(path, reference)[mask].mean() for path in rows.cope_path])
                result = hc3_age(x, y)
                result["beta"] = result.pop("beta_per_decade")
                roi_rows.append(dict(family=family, kind=kind, cope=cope, roi=name, n=len(people),
                                     predictor=columns[1], roi_voxels=int(mask.sum()), full_roi_voxels=full_n, **result))
                private = people[KEY].copy(); private["mean_cope"] = y
                private.to_csv(folder / f"roi-{name}-values.tsv", sep="\t", index=False)
        prepared.append((spec, folder, rows, x, c, columns, names, common))
    if roi_rows:
        roi = pd.DataFrame(roi_rows)
        for family in roi.family.unique():
            pick = roi.family.eq(family)
            roi.loc[pick, "p_holm_within_family"] = holm(roi.loc[pick, "p_two_sided"].to_numpy())
        roi.to_csv(report / "roi-results.tsv", sep="\t", index=False)
        plot_dir = ROOT / "qc/L3-preliminary" / args.label
        plot_dir.mkdir(parents=True)
        for family in roi.family.unique():
            subset = roi[roi.family.eq(family)].reset_index(drop=True)
            fig, ax = plt.subplots(figsize=(10, max(3, .35*len(subset)+1.5)))
            y = np.arange(len(subset))
            ax.errorbar(subset.beta, y,
                        xerr=np.vstack([subset.beta-subset.ci95_low, subset.ci95_high-subset.beta]), fmt="o")
            ax.set_yticks(y, [f"{r.kind} | {r.roi} | COPE{r.cope} {CONTRASTS[r.cope]}"
                             for r in subset.itertuples()])
            ax.invert_yaxis(); ax.axvline(0, color="gray", linewidth=1)
            ax.set_xlabel("COPE change per decade" if family == "age" else "COPE change per raw rating-difference unit")
            ax.set_title(f"Preliminary pooled {family}: adjusted ROI estimates, HC3 95% CI")
            fig.tight_layout(); fig.savefig(plot_dir / f"{family}-roi.png", dpi=170); plt.close(fig)
        save_json(report / "roi-completion.json", dict(complete=True, roi_tests=len(roi_rows),
                  provisional=readiness["provisional"], wholebrain_complete=False))
        print(f"ROI COMPLETE: {len(roi_rows)} tests saved before whole-brain preparation.", flush=True)
    if args.stage != "roi":
        input_failures = []
        for spec, folder, rows, x, c, columns, names, common in prepared:
            diagnostic = audit_dof_inputs(rows, reference, common, report / f"{folder.name}_dof-inputs.tsv")
            failed = diagnostic[diagnostic.status.eq("failed")]
            for item in failed.to_dict("records"):
                input_failures.append(dict(model=folder.name, **item))
                print(f"INPUT ERROR: {folder.name}: {item['problem']} (COPE: {item['cope_path']})", flush=True)
            print(f"DOF AUDIT: {folder.name}: {len(diagnostic)} inputs; {len(failed)} failures", flush=True)
        save_json(report / "input-completion.json", dict(complete=not input_failures,
                  models_checked=len(prepared), failures=input_failures))
        if input_failures:
            save_json(report / "completion.json", dict(complete=False, stage=args.stage,
                provisional=readiness["provisional"], completed_models=0, expected_models=len(prepared),
                roi_tests=len(roi_rows), failure_stage="input_dof", failures=input_failures))
            raise ValueError(f"{len(input_failures)} input DOF failures; see {report}/input-completion.json; no FEAT models launched")
        if args.stage == "inputs":
            print("CHECK PASSED: all requested group-mask DOF input audits; no FEAT models launched.", flush=True)
            return
        for spec, folder, rows, x, c, columns, names, common in prepared:
            inputs = [stage_input(row, folder / "inputs" / f"input-{i:04d}.feat", reference, common)
                      for i, row in enumerate(rows.to_dict("records"))]
            output, fsf = folder / "L3.gfeat", folder / "design.fsf"
            fsf.write_text(render(spec["family"], output, inputs, x, c, columns, names, args.reference))
            run_command(["feat_model", fsf.with_suffix("")])
            require(np.allclose(matrix(fsf.with_suffix(".mat")), x, atol=1e-5, rtol=1e-6), "Rendered matrix differs")
            require(np.array_equal(matrix(fsf.with_suffix(".con")), c), "Rendered contrasts differ")
            jobs.append((spec, fsf, output, x, c, common))
    def execute(job):
        spec, fsf, output, x, c, common = job
        with (fsf.parent / "feat.log").open("w") as log:
            run_command(["bash", ROOT / "code/L3stats.sh", fsf], log)
        results = audit_fit(output, x, c, reference, common)
        save_json(report / f"{fsf.parent.name}.json", dict(spec, output=str(output), results=results))
        for i in range(1, len(c)+1):
            shutil.copy2(cluster_table(output / "cope1.feat", i), report / f"{fsf.parent.name}_zstat{i}_clusters.txt")
        return spec
    done, failed = [], []
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(execute, job): job[0] for job in jobs}
        for future in as_completed(futures):
            try:
                done.append(future.result()); print(f"DONE: {done[-1]}", flush=True)
            except Exception as error:
                failed.append(dict(spec=futures[future], error=str(error)))
                print(f"ERROR: {failed[-1]}", flush=True)
    save_json(report / "completion.json", dict(complete=not failed, stage=args.stage,
        provisional=readiness["provisional"], completed_models=len(done), expected_models=len(jobs),
        roi_tests=len(roi_rows), failures=failed))
    require(not failed, "Incomplete FEAT models; inspect feat.log in the affected model directory")
    print("CHECK PASSED: requested FEAT/FLAME1 and/or ROI stage complete.", flush=True)


if __name__ == "__main__":
    main()
