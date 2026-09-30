#!/usr/bin/env python3
"""Logged post-10668 preparation and paired pooled L1/L2; no L3 or QC exclusions.

Run through run_logged.sh. Restart a failed model stage with --stage models
--prepared <printed receipt>; do not repeat preparation after starting FEAT.
"""
import argparse
import csv
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile

from audit_outputs import l1_path, l2_path
from model_provenance import fingerprint

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = Path(os.environ.get("RF1_SRA_LINUX2_ROOT", "/ZPOOL/data/projects/rf1-sra-linux2"))
RF1 = Path(os.environ.get("RF1_SHAREDREWARD_ROOT", "/ZPOOL/data/projects/rf1-sra-sharedreward"))
FSL = Path(os.environ.get("FSL_DERIVATIVES_ROOT", ROOT / "derivatives/fsl"))
QC_PYTHON = os.environ.get("QC_PYTHON", "/ZPOOL/data/tools/anaconda/tug87422/envs/tedana-26.0.3/bin/python")


def command(argv, cwd=ROOT, allowed=(0,)):
    argv = list(map(str, argv))
    print("COMMAND: " + shlex.join(argv), flush=True)
    result = subprocess.run(argv, cwd=cwd)
    if result.returncode not in allowed:
        raise RuntimeError(f"stage exited {result.returncode}: {shlex.join(argv)}")


def run(script, *args, allowed=(0,)):
    command((["bash"] if script.endswith(".sh") else [sys.executable]) +
            [ROOT / "code" / script, *args], allowed=allowed)


def table(path):
    with Path(path).open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return reader.fieldnames, list(reader)


def select_10668(source, output):
    fields, rows = table(source)
    selected = [r for r in rows if (r["dataset"], r["subject"], r["session"]) == ("rf1", "10668", "01")]
    if len(selected) != 2 or {int(r["run"]) for r in selected} != {1, 2}:
        raise ValueError("Refusing stale inventory: corrected 10668 must have exactly Shared Reward runs 1 and 2")
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(selected)
    return selected


def reviewed_cohort(l1, l2):
    _, rows = table(l1)
    runs = {(r["subject"], r["session"], int(r["run"])) for r in rows if r["dataset"] == "rf1"}
    if ("10657", "01", 1) in runs or ("10657", "01", 2) not in runs:
        raise ValueError("10657 run-1 exclusion/run-2 retention was not propagated")
    if not {("10668", "01", 1), ("10668", "01", 2)} <= runs:
        raise ValueError("Both corrected 10668 runs must be present; inspect task validity")
    _, subjects = table(l2)
    for subject, expected in (("10657", "2"), ("10668", "1,2")):
        matches = [r for r in subjects if (r["dataset"], r["subject"], r["session"]) == ("rf1", subject, "01")]
        if len(matches) != 1 or matches[0]["runs"] != expected:
            raise ValueError(f"Incorrect retained-run subject manifest for {subject}")
    print(f"Reviewed cohort: {len(rows)} runs; {len(subjects)} subject-sessions", flush=True)
    return rows


def preserve(path, destination, move=False):
    if not path.exists():
        return
    if path.is_symlink() or destination.exists():
        raise ValueError(f"Refusing linked source or occupied backup: {path}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if move:
        path.rename(destination)
    else:
        shutil.copy2(path, destination)
    print(f"PRESERVED {'and retired' if move else 'before refresh'}: {path} -> {destination}", flush=True)


def retire_reviewed_models(backup):
    # Only the explicitly corrected/excluded run scopes; never blanket --overwrite.
    for subject, runs in (("10668", (1, 2)), ("10657", (1,))):
        row = dict(dataset="rf1", subject=subject, session="01")
        for kind in ("act", "ppi_seed-vs"):
            paths = [l2_path(FSL, row, kind)] + [l1_path(FSL, row, kind, r) for r in runs]
            for path in paths:
                if not path.resolve().is_relative_to(FSL.resolve()):
                    raise ValueError(f"Linked/out-of-root model: {path}")
                preserve(path, backup / "models" / path.relative_to(FSL), move=True)


def prepare(records, tag):
    lists = ROOT / "logs/runlists"
    lists.mkdir(parents=True, exist_ok=True)
    canonical = ROOT / "logs/records"
    # Validate the corrected upstream inputs without rerunning any preprocessing.
    command([QC_PYTHON, UPSTREAM / "code/repair_10668.py", "check-products",
             "--inventory", UPSTREAM / "work/sharedreward-source-validity-20260916-000438/inventory.json",
             "--behavior-root", "/ZPOOL/data/projects/rf1-sra/stimuli"], cwd=UPSTREAM)
    for script in ("build_run_qc.py", "build_events_qc.py"):
        command(["bash", UPSTREAM / "code/run_logged.sh", "--label", f"sharedreward-refresh-{tag}-{script[:-3]}",
                 "--include-full-log", "--", QC_PYTHON, UPSTREAM / "code" / script, "build", "--overwrite",
                 "--check", QC_PYTHON, UPSTREAM / "code" / script, "check"], cwd=UPSTREAM)
    characterization = lists / "phase0-characterization-ready.tsv"
    target = lists / "target-smoothing-6mm-ready.tsv"
    run("build_characterization_manifest.py", "--output", characterization,
        "--missing-output", lists / "phase0-characterization-missing.tsv")
    run("build_target_smoothing_manifest.py", "--output", target,
        "--missing-output", lists / "target-smoothing-6mm-missing.tsv")
    repair_target = records / "10668-target-smoothing.tsv"
    selected = select_10668(target, repair_target)
    backup = ROOT / "derivatives/analysis_refresh_archive" / tag
    retire_reviewed_models(backup)
    for row in selected:
        for field in ("output_bold", "output_qc"):
            path = Path(row[field])
            if not path.resolve().is_relative_to((RF1 / "derivatives/harmonized").resolve()):
                raise ValueError(f"Unexpected repaired derivative destination: {path}")
            preserve(path, backup / "smoothed" / path.name)
    run("run_target_smoothing_batch.py", "--manifest", repair_target, "--jobs", "2", "--overwrite",
        "--log-dir", ROOT / "logs" / tag / "smoothing", "--work-root", ROOT / "work" / tag)
    run("audit_target_smoothing.py", "--manifest", target,
        "--output", canonical / "target-smoothing-current-audit.tsv",
        "--missing-output", canonical / "target-smoothing-current-missing.tsv", "--fail-on-incomplete")
    qc = lists / "analysis-qc-ready.tsv"
    run("build_analysis_qc_manifest.py", "--output", qc, "--missing-output", lists / "analysis-qc-missing.tsv")
    repair_qc = records / "10668-analysis-qc.tsv"
    select_10668(qc, repair_qc)
    for manifest, extra, label in ((repair_qc, ["--overwrite"], "qc-repaired"), (qc, [], "qc-all")):
        run("run_analysis_qc_batch.py", "--manifest", manifest, "--jobs", "4",
            "--log-dir", ROOT / "logs" / tag / label, *extra)
    run("audit_analysis_qc.py", "--manifest", qc,
        "--output", canonical / "analysis-qc-run-level.tsv",
        "--summary-output", canonical / "analysis-qc-summary.tsv",
        "--subject-output", canonical / "analysis-qc-subject-level.tsv",
        "--missing-output", canonical / "analysis-qc-missing.tsv", "--fail-on-incomplete")
    events = lists / "fulltrial-event-qc-ready.tsv"
    run("build_event_qc_manifest.py", "--output", events, "--missing-output", lists / "fulltrial-event-qc-missing.tsv")
    run("run_event_qc_batch.py", "--manifest", events, "--overwrite", "--jobs", "4",
        "--log-dir", ROOT / "logs" / tag / "events")
    run("audit_event_qc.py", "--manifest", events, "--output", canonical / "fulltrial-event-qc-run-level.tsv",
        "--subject-output", canonical / "fulltrial-event-qc-subject-level.tsv",
        "--missing-output", canonical / "fulltrial-event-qc-missing.tsv", "--fail-on-incomplete")
    nuisance = lists / "ds003745-fsl-confounds.tsv"
    run("build_fsl_confounds_manifest.py", "--output", nuisance)
    run("run_fsl_confounds_batch.py", "--manifest", nuisance, "--jobs", "4", "--log-dir", ROOT / "logs" / tag / "confounds")
    run("audit_fsl_confounds.py", "--manifest", nuisance, "--output", canonical / "ds003745-fsl-confounds-audit.tsv", "--fail-on-incomplete")
    ratings = lists / "ratings-qc-ready.tsv"
    run("build_ratings_qc_manifest.py", "--output", ratings, "--missing-output", lists / "ratings-qc-missing.tsv")
    run("audit_ratings_qc.py", "--manifest", ratings, "--output", canonical / "ratings-qc-subject-level.tsv",
        "--missing-output", canonical / "ratings-qc-invalid.tsv", "--fail-on-incomplete")
    run("build_analysis_cohort.py")
    if table(lists / "L1-model-review-hold.tsv")[1]:
        raise ValueError("Unexpected inferential-condition holds; review L1-model-review-hold.tsv before launch")
    # Freeze small, tracked copies rather than relying on mutable ignored lists.
    l1, l2 = records / "L1-task-ready.tsv", records / "L2-task-ready.tsv"
    shutil.copy2(lists / l1.name, l1); shutil.copy2(lists / l2.name, l2)
    rows = reviewed_cohort(l1, l2)
    run("generate_l1_evs.py", "--manifest", l1, "--output-root",
        os.environ.get("EVFILES_ROOT", str(FSL / "EVfiles")), "--overwrite")
    receipt = records / "prepared.json"
    small = {l1, l2, ROOT / "docs/curated_run_exclusions.tsv"}
    images = set()
    for row in rows:
        small.update(Path(row[k]) for k in ("confounds", "source_events", "harmonized_events"))
        images.update(Path(row[k]) for k in ("input", "mask"))
    receipt.write_text(json.dumps(dict(l1=str(l1), l2=str(l2),
        inputs=[fingerprint(p) for p in sorted(small)],
        images=[fingerprint(p, True) for p in sorted(images)]), indent=2) + "\n")
    print(f"PREPARATION PASSED. Model-only restart: --stage models --prepared {receipt}", flush=True)
    return receipt


def check_receipt(receipt):
    data = json.loads(receipt.read_text())
    for group in ("inputs", "images"):
        for item in data[group]:
            if item != fingerprint(item["path"], group == "images"):
                raise ValueError(f"Prepared input changed: {item['path']}")
    reviewed_cohort(Path(data["l1"]), Path(data["l2"]))
    return data


def prepare_seed_caches(manifest):
    """Use the worker's NN/usesqform recipe serially, avoiding run-1/run-2 races."""
    import nibabel as nib
    import numpy as np
    source = ROOT / "masks/seed-vs.nii.gz"
    seed = nib.load(source)
    _, rows = table(manifest)
    grids = {}
    def same_grid(left, right):
        return left.shape[:3] == right.shape[:3] and np.allclose(left.affine, right.affine, atol=1e-5, rtol=0)
    for row in rows:
        bold = nib.load(row["input"])
        key = row["dataset"], row["subject"]
        if key in grids:
            if not same_grid(grids[key], bold):
                raise ValueError(f"Cannot share seed cache across differing run grids: {key}")
            continue
        grids[key] = bold
        if same_grid(seed, bold):
            continue
        cached = FSL / "resampled_masks" / key[0] / f"sub-{key[1]}" / "seed-vs_space-RF1Grid.nii.gz"
        if cached.is_file() and cached.stat().st_mtime >= source.stat().st_mtime and same_grid(nib.load(cached), bold):
            continue
        cached.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="seed-prepare-", dir=cached.parent) as tmp:
            reference, output = Path(tmp) / "reference.nii.gz", Path(tmp) / "seed.nii.gz"
            command(["fslroi", row["input"], reference, "0", "1"])
            command(["flirt", "-in", source, "-ref", reference, "-applyxfm", "-usesqform",
                     "-interp", "nearestneighbour", "-out", output])
            image = nib.load(output)
            values = np.asarray(image.dataobj)
            if not same_grid(image, bold) or not np.isfinite(values).all() or not np.any(values):
                raise ValueError(f"Invalid resampled VS seed: {key}")
            output.replace(cached)
    print(f"VS seed caches prepared serially for {len(grids)} subjects", flush=True)


def models(receipt, records, tag, jobs, l2_jobs):
    data = check_receipt(receipt)
    def audit(label, require_l1=False, require_all=False):
        report = records / label
        run("audit_group_readiness.py", "--l1-manifest", data["l1"], "--subject-manifest", data["l2"],
            "--fsl-root", FSL, "--reference", RF1 / "resources/rf1_MNI152NLin6Asym_reference_grid.nii.gz",
            "--report-dir", report, allowed=(0, 1))
        summary = json.loads((report / "summary.json").read_text())
        counts = summary["counts"]["l1"]
        if counts.get("unverified", 0) or (require_l1 and counts.get("missing", 0)):
            raise ValueError(f"L1 audit needs review; no blanket overwrites: {report}")
        if require_all and not summary["computational_gate_passed"]:
            raise ValueError(f"Final primary-output verification incomplete: {report}")
    audit("before-models")
    prepare_seed_caches(data["l1"])
    run("run_L1stats.sh", "--manifest", data["l1"], "--ppi-seed", "vs", "--parallel-types",
        "--jobs", str(jobs), "--log-dir", ROOT / "logs" / tag / "L1")
    audit("after-L1", require_l1=True)
    run("run_L2stats.sh", "--manifest", data["l2"], "--ppi-seed", "vs", "--parallel-types",
        "--jobs", str(l2_jobs), "--log-dir", ROOT / "logs" / tag / "L2")
    audit("final", require_l1=True, require_all=True)
    print("CHECK PASSED: pooled activation/VS-PPI L1 and subject outputs verified. Cooper QC/L3 decisions remain separate.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("prepare", "models", "all"), default="all")
    parser.add_argument("--prepared", type=Path)
    parser.add_argument("--jobs", type=int, default=25)
    parser.add_argument("--l2-jobs", type=int, default=5)
    parser.add_argument("--confirm-idle", action="store_true", help="Operator confirms no concurrent analysis/input writers")
    args = parser.parse_args()
    if not args.confirm_idle or min(args.jobs, args.l2_jobs) < 1:
        parser.error("Require --confirm-idle and positive job counts")
    if (args.stage == "models") != (args.prepared is not None):
        parser.error("--prepared is required only with --stage models")
    os.chdir(ROOT)
    # Keep AFNI's curated bin directory ahead of the incomplete Conda package.
    # Shell workers must still use the same imaging Python as this launcher.
    python3 = shutil.which("python3")
    if not python3 or Path(python3).resolve() != Path(sys.executable).resolve():
        raise ValueError("Activate the imaging environment so python3 matches the launcher interpreter")
    # Cap nested pools; the two-run smoothing refresh has its own AFNI limit.
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS", "FSLSUB_PARALLEL"):
        os.environ[key] = "1"
    for name in ("feat", "fslval", "fslnvols", "fslmeants", "flirt", "fslroi", "3dBlurToFWHM", "3dFWHMx"):
        if not shutil.which(name):
            raise ValueError(f"Required executable missing: {name}")
    # Prevent competing copies of this launcher, not unrelated user processes.
    (ROOT / "logs").mkdir(exist_ok=True)
    with (ROOT / "logs/.full-analysis.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        tag = "full-analysis-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
        records = ROOT / "logs/records" / tag
        records.mkdir(parents=True)
        print(f"Records: {records}\nL1 FEAT ceiling: {2*args.jobs}; L2 FEAT ceiling: {2*args.l2_jobs}", flush=True)
        receipt = prepare(records, tag) if args.stage != "models" else args.prepared
        if args.stage != "prepare":
            models(receipt, records, tag, args.jobs, args.l2_jobs)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError) as error:
        raise SystemExit(f"ERROR: {error}. Stopped; no later analysis stage launched.")
