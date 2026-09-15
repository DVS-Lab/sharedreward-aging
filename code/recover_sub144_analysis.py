#!/usr/bin/env python3
"""Refresh event QC/cohorts and optionally rerun only corrected ds003745 sub-144."""

import argparse
import csv
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

from audit_outputs import l1_missing, l1_path, l2_missing, l2_path

ROOT = Path(__file__).resolve().parents[1]


def run(script, *args):
    command = (["bash"] if script.endswith(".sh") else [sys.executable]) + [str(ROOT / "code" / script), *map(str, args)]
    print("COMMAND: " + shlex.join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def prepare_cohort(records, lists, ds_confounds_root):
    # The full cohort requires these derived matrices even for a sub-144 pilot.
    # Reuse the established conversion policy; do not recompute RF1 confounds.
    manifest = lists / "ds003745-fsl-confounds.tsv"
    run("build_fsl_confounds_manifest.py", "--output", manifest,
        "--output-root", ds_confounds_root)
    run("run_fsl_confounds_batch.py", "--manifest", manifest, "--jobs", "8",
        "--log-dir", ROOT / "logs/ds003745-fsl-confounds")
    run("audit_fsl_confounds.py", "--manifest", manifest,
        "--output", records / "ds003745-fsl-confounds-audit.tsv", "--fail-on-incomplete")
    run("build_analysis_cohort.py", "--ds-confounds-root", ds_confounds_root)


def select_manifest(source, destination, level):
    with source.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = reader.fieldnames
        rows = [row for row in reader if row["dataset"] == "ds003745" and row["subject"] == "144"]
    if any(row["session"] for row in rows):
        raise ValueError("unexpected sub-144 session")
    if level == "l1" and (not rows or not {int(r["run"]) for r in rows}.issubset({1, 2}) or len({r["run"] for r in rows}) != len(rows)):
        raise ValueError("sub-144 has no eligible run or an invalid run contract; inspect dispositions before proceeding")
    if level == "l2" and len(rows) != 1:
        raise ValueError("expected exactly one sub-144 subject-level row")
    with destination.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    print(f"Selected {level}: {len(rows)} row(s): {destination}", flush=True)
    return rows


def archive_incomplete(output, problems, fsl_root, backup):
    if output.exists() and problems:
        # Exact generated model paths only. Keep prior derivatives recoverable.
        relative = output.relative_to(fsl_root)
        if output.is_symlink() or not output.resolve().is_relative_to(fsl_root.resolve()):
            raise ValueError(f"refusing to move linked/out-of-root output: {output}")
        destination = backup / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        output.rename(destination)
        print(f"ARCHIVED (recoverable): {output} -> {destination}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-models", action="store_true", help="After preparation, archive stale sub-144 models and run paired activation/PPI, then fixed effects and audits")
    args = parser.parse_args()
    os.chdir(ROOT)
    records, lists = ROOT / "logs/records", ROOT / "logs/runlists"
    records.mkdir(parents=True, exist_ok=True); lists.mkdir(parents=True, exist_ok=True)
    lock = (lists / ".sub144-recovery.lock").open("a")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    fsl_root = Path(os.environ.get("FSL_DERIVATIVES_ROOT", ROOT / "derivatives/fsl")).absolute()
    ev_root = Path(os.environ.get("EVFILES_ROOT", fsl_root / "EVfiles"))
    event_manifest = lists / "fulltrial-event-qc-ready.tsv"
    # Full event refresh is cheap and also upgrades source-content provenance.
    # Imaging, masks, smoothing and source BIDS are never modified here.
    run("build_event_qc_manifest.py", "--output", event_manifest,
        "--missing-output", lists / "fulltrial-event-qc-missing.tsv")
    run("run_event_qc_batch.py", "--manifest", event_manifest, "--overwrite", "--jobs", "4",
        "--log-dir", ROOT / "logs/events-sub144-recovery")
    run("audit_event_qc.py", "--manifest", event_manifest,
        "--output", records / "fulltrial-event-qc-run-level.tsv",
        "--subject-output", records / "fulltrial-event-qc-subject-level.tsv",
        "--missing-output", records / "fulltrial-event-qc-missing.tsv", "--fail-on-incomplete")
    prepare_cohort(records, lists, fsl_root / "confounds_fmriprep")
    l1 = lists / "L1-sub144-recovered.tsv"
    l2 = lists / "L2-sub144-recovered.tsv"
    l1_rows = select_manifest(lists / "L1-task-ready.tsv", l1, "l1")
    l2_rows = select_manifest(lists / "L2-task-ready.tsv", l2, "l2")
    # Preserve the exact selected input inventory in Git, not just an ignored runlist.
    (records / "sub144-recovery-selected-inputs.json").write_text(json.dumps({"l1": l1_rows, "subject": l2_rows}, indent=2) + "\n")
    run("generate_l1_evs.py", "--manifest", l1, "--output-root", ev_root, "--overwrite")
    if not args.run_models:
        print("PREPARATION PASSED. No imaging or FEAT products changed. Use --run-models for the scoped rerun.")
        return
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    backup = fsl_root / "replaced-models" / f"sub144-{stamp}"
    # Archive old subject estimates before changing their L1 parents.
    for kind in ("act", "ppi_seed-vs"):
        count = 28 if kind == "act" else 29
        output = l2_path(fsl_root, l2_rows[0], kind)
        problems = l2_missing(output, count)
        if int(l2_rows[0]["n_runs"]) != 2:
            problems.append("now_one_run_passthrough")
        archive_incomplete(output, problems, fsl_root, backup)
        for row in l1_rows:
            output = l1_path(fsl_root, row, kind)
            archive_incomplete(output, l1_missing(output, count), fsl_root, backup)
    run("run_L1stats.sh", "--manifest", l1, "--ppi-seed", "vs", "--parallel-types", "--jobs", "2",
        "--log-dir", ROOT / "logs" / f"L1-sub144-{stamp}")
    for kind in ("act", "ppi_seed-vs"):
        run("audit_outputs.py", "--level", "l1", "--manifest", l1, "--type", kind,
            "--output", records / f"sub144-L1-{kind}-completeness.tsv")
    run("run_L2stats.sh", "--manifest", l2, "--ppi-seed", "vs", "--parallel-types", "--jobs", "1",
        "--log-dir", ROOT / "logs" / f"L2-sub144-{stamp}")
    for kind in ("act", "ppi_seed-vs"):
        run("audit_outputs.py", "--level", "subject", "--manifest", l2, "--type", kind,
            "--output", records / f"sub144-subject-{kind}-completeness.tsv")
    print("CHECK PASSED: corrected sub-144 activation and provisional VS PPI, including subject-level outputs.")


if __name__ == "__main__":
    main()
