#!/usr/bin/env python3
"""Resolve the exclusion ledger into retained-run manifests and a rebuild list.

Applies imaging_all `exclude` rows to the frozen task-ready L1/L2 manifests.
pending_review rows are treated according to --pending; summary.tsv always
reports both the retain and exclude bounds so their impact stays visible.
Ratings rows only set ratings_eligible and never remove imaging runs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path

from build_analysis_cohort import (
    L2_FIELDS,
    ROOT,
    is_true,
    normalize_run,
    read_tsv,
    run_key,
    sort_key,
    write_tsv,
)
from build_exclusion_ledger import FROZEN

FAMILIES = ("fulltrial_act", "fulltrial_ppi_seed-vs")
RF1_FAMILIES = ("rf1_phase_resolved_act",)
STATUS_FIELDS = (
    "dataset",
    "subject",
    "session",
    "frozen_runs",
    "frozen_strategy",
    "retained_runs",
    "strategy",
    "change",
    "imaging_exclusions",
    "pending_reviews",
    "ratings_eligible",
    "rebuild_families",
)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=ROOT / "docs/exclusion_ledger.tsv")
    parser.add_argument("--l1-manifest", type=Path, default=FROZEN / "L1-task-ready.tsv")
    parser.add_argument("--l2-manifest", type=Path, default=FROZEN / "L2-task-ready.tsv")
    parser.add_argument(
        "--analysis-qc",
        type=Path,
        default=ROOT / "logs/records/analysis-qc-run-level.tsv",
    )
    parser.add_argument(
        "--l1-audit", type=Path, default=FROZEN / "final/l1-audit.tsv"
    )
    parser.add_argument(
        "--candidates",
        type=Path,
        default=FROZEN / "final/verified-pre-QC-candidates.tsv",
    )
    parser.add_argument(
        "--pending",
        choices=("retain", "exclude", "fail"),
        default="retain",
        help="how pending_review imaging rows are applied (use fail for final inputs)",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "logs/records/exclusion-ledger"
    )
    return parser.parse_args()


def excluded_runs(ledger, l1, pending):
    """Map each task-ready run key to the ledger_ids that remove it."""
    dispositions = {"exclude", "pending_review"} if pending == "exclude" else {"exclude"}
    by_subject = defaultdict(list)
    for row in l1:
        by_subject[(row["dataset"], row["subject"], row["session"])].append(run_key(row))
    removed = defaultdict(list)
    for row in ledger:
        if row["applies_to"] != "imaging_all" or row["disposition"] not in dispositions:
            continue
        unit = (row["dataset"], row["subject"], row["session"])
        if row["run"] == "*":
            targets = by_subject.get(unit, [])
        else:
            targets = [key for key in by_subject.get(unit, []) if key[3] == normalize_run(row["run"])]
        for key in targets:
            removed[key].append(row["ledger_id"])
    return removed


def resolve(ledger, l1, l2, pending):
    removed = excluded_runs(ledger, l1, pending)
    retained_l1 = [row for row in l1 if run_key(row) not in removed]
    pending_ids = defaultdict(list)
    for row in ledger:
        if row["applies_to"] == "imaging_all" and row["disposition"] == "pending_review":
            pending_ids[(row["dataset"], row["subject"], row["session"])].append(row["ledger_id"])
    ratings_excluded = {
        (row["dataset"], row["subject"])
        for row in ledger
        if row["applies_to"] == "ratings_qualified" and row["disposition"] == "exclude"
    }
    runs_left = defaultdict(list)
    for row in retained_l1:
        runs_left[(row["dataset"], row["subject"], row["session"])].append(row["run"])
    removed_by_subject = defaultdict(list)
    for key, ids in removed.items():
        removed_by_subject[key[:3]].extend(ids)

    status, retained_l2 = [], []
    for frozen in l2:
        unit = (frozen["dataset"], frozen["subject"], frozen["session"])
        runs = sorted(runs_left.get(unit, []), key=lambda run: int(normalize_run(run)))
        strategy = {0: "", 1: "l1_passthrough"}.get(len(runs), "fixed_effects")
        frozen_runs = frozen["runs"].split(",")
        if not runs:
            change = "subject_removed"
        elif runs != frozen_runs:
            change = "runs_removed"
        else:
            change = "unchanged"
        families = ()
        if change == "runs_removed":
            families = FAMILIES + (RF1_FAMILIES if frozen["dataset"] == "rf1" else ())
        ratings_ok = (frozen["dataset"], frozen["subject"]) not in ratings_excluded
        status.append(
            {
                "dataset": frozen["dataset"],
                "subject": frozen["subject"],
                "session": frozen["session"],
                "frozen_runs": frozen["runs"],
                "frozen_strategy": frozen["subject_level_strategy"],
                "retained_runs": ",".join(runs),
                "strategy": strategy,
                "change": change,
                "imaging_exclusions": ";".join(sorted(set(removed_by_subject.get(unit, [])))),
                "pending_reviews": ";".join(sorted(pending_ids.get(unit, []))),
                "ratings_eligible": str(ratings_ok).lower(),
                "rebuild_families": ";".join(families),
            }
        )
        if runs:
            retained_l2.append(
                {
                    "dataset": frozen["dataset"],
                    "subject": frozen["subject"],
                    "session": frozen["session"],
                    "n_runs": len(runs),
                    "runs": ",".join(runs),
                    "subject_level_strategy": strategy,
                    "ratings_eligible": str(ratings_ok).lower(),
                    # Superseded flag kept for schema compatibility with L2 tooling.
                    "ratings_exclusion_reason": "" if ratings_ok else "see docs/exclusion_ledger.tsv",
                }
            )
    return retained_l1, retained_l2, status


def verified_l1(l1_audit):
    """Map (dataset, subject, session, type, run) to its verified L1 .feat path."""
    return {
        (r["dataset"], r["subject"], r["session"], r["type"], normalize_run(r["run"])): r["path"]
        for r in l1_audit
        if r["status"] == "verified"
    }


def passthrough_paths(feat, cope):
    return {
        "cope_path": f"{feat}/stats/cope{cope}.nii.gz",
        "varcope_path": f"{feat}/stats/varcope{cope}.nii.gz",
        "mask_path": f"{feat}/mask.nii.gz",
    }


def filter_candidates(candidates, status, l1_feats):
    """Keep frozen COPE paths only for subjects whose runs are unchanged.

    A subject reduced to one run is re-pointed at that run's verified L1 COPE,
    as for the existing passthrough subjects; any other change needs a rebuild.
    """
    by_subject = {(r["dataset"], r["subject"], r["session"]): r for r in status}
    rows = []
    for row in candidates:
        subject = by_subject[(row["dataset"], row["subject"], row["session"])]
        if subject["change"] == "subject_removed":
            continue
        row = {**row, "ratings_eligible": subject["ratings_eligible"]}
        row["input_status"] = "frozen_valid"
        if subject["change"] == "runs_removed":
            row.update(runs=subject["retained_runs"], strategy=subject["strategy"])
            key = (row["dataset"], row["subject"], row["session"], row["type"],
                   normalize_run(subject["retained_runs"]))
            if subject["strategy"] == "l1_passthrough" and key in l1_feats:
                row.update(passthrough_paths(l1_feats[key], row["cope"]))
                row["input_status"] = "l1_passthrough_verified"
            else:
                row.update(cope_path="", varcope_path="", mask_path="",
                           input_status="requires_rebuild")
        rows.append(row)
    return rows


def pending_units(ledger, analysis_qc):
    """Analysis-QC rows for runs that still have pending imaging reviews."""
    criteria = defaultdict(list)
    for row in ledger:
        if row["applies_to"] == "imaging_all" and row["disposition"] == "pending_review":
            criteria[run_key(row)].append(row["criterion"])
    return [
        {**row, "pending_criteria": ";".join(sorted(criteria[run_key(row)]))}
        for row in sorted(analysis_qc, key=sort_key)
        if run_key(row) in criteria
    ]


def summarize(status, retained_l1, pending):
    rows = []
    for dataset in sorted({row["dataset"] for row in status}) + ["all"]:
        subset = [r for r in status if dataset in ("all", r["dataset"])]
        kept = [r for r in subset if r["change"] != "subject_removed"]
        rows.append(
            {
                "pending_as": pending,
                "dataset": dataset,
                "frozen_subjects": len(subset),
                "retained_runs": sum(dataset in ("all", r["dataset"]) for r in retained_l1),
                "retained_subjects": len(kept),
                "fixed_effects": sum(r["strategy"] == "fixed_effects" for r in kept),
                "l1_passthrough": sum(r["strategy"] == "l1_passthrough" for r in kept),
                "subjects_runs_removed": sum(r["change"] == "runs_removed" for r in subset),
                "subjects_removed": sum(r["change"] == "subject_removed" for r in subset),
                "retained_ratings_eligible": sum(is_true(r["ratings_eligible"]) for r in kept),
            }
        )
    return rows


def display(path: Path) -> str:
    path = path.resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def provenance(args, ledger):
    digest = hashlib.sha256(args.ledger.read_bytes()).hexdigest()
    try:
        commit = subprocess.run(
            ["git", "-C", str(ROOT), "log", "-1", "--format=%H", "--", str(args.ledger)],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "-C", str(ROOT), "status", "--porcelain", "--", str(args.ledger)],
                capture_output=True, text=True, check=True,
            ).stdout.strip()
        )
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = "", True
    return {
        "ledger": display(args.ledger),
        "ledger_sha256": digest,
        "ledger_last_commit": commit,
        "ledger_uncommitted_changes": dirty,
        "l1_manifest": display(args.l1_manifest),
        "l2_manifest": display(args.l2_manifest),
        "candidates": display(args.candidates),
        "l1_audit": display(args.l1_audit),
        "analysis_qc": display(args.analysis_qc),
        "pending_as": args.pending,
        "n_pending_imaging_rows": sum(
            r["applies_to"] == "imaging_all" and r["disposition"] == "pending_review"
            for r in ledger
        ),
    }


def main():
    args = parse_args()
    ledger = read_tsv(args.ledger, {"ledger_id", "applies_to", "disposition"})
    l1 = read_tsv(args.l1_manifest, {"input"})
    l2 = read_tsv(args.l2_manifest, {"runs", "subject_level_strategy"})
    pending = [
        r["ledger_id"]
        for r in ledger
        if r["applies_to"] == "imaging_all" and r["disposition"] == "pending_review"
    ]
    if args.pending == "fail" and pending:
        raise SystemExit(f"ERROR: {len(pending)} imaging rows are still pending_review")

    retained_l1, retained_l2, status = resolve(ledger, l1, l2, args.pending)
    summary = summarize(status, retained_l1, args.pending)
    for bound in ("retain", "exclude"):
        if bound != args.pending:
            other_l1, _, other = resolve(ledger, l1, l2, bound)
            summary += summarize(other, other_l1, bound)

    out = args.output_dir
    write_tsv(out / "retained-L1.tsv", list(l1[0]), sorted(retained_l1, key=sort_key))
    write_tsv(out / "retained-L2.tsv", L2_FIELDS, retained_l2)
    write_tsv(out / "subject-status.tsv", STATUS_FIELDS, status)
    rebuild = [
        {"dataset": r["dataset"], "subject": r["subject"], "session": r["session"],
         "family": family, "runs": r["retained_runs"], "strategy": r["strategy"],
         "action": "repoint_to_verified_l1" if r["strategy"] == "l1_passthrough"
         else "rebuild_fixed_effects_l2"}
        for r in status
        for family in filter(None, r["rebuild_families"].split(";"))
    ]
    write_tsv(out / "rebuild-list.tsv",
              ("dataset", "subject", "session", "family", "runs", "strategy", "action"),
              rebuild)
    l1_feats = verified_l1(read_tsv(args.l1_audit, {"type", "status", "path"}))
    candidates = read_tsv(args.candidates, {"type", "cope", "cope_path", "ratings_eligible"})
    write_tsv(
        out / "candidates.tsv",
        list(candidates[0]) + ["input_status"],
        filter_candidates(candidates, status, l1_feats),
    )
    analysis_qc = read_tsv(args.analysis_qc, {"mask", "coverage_mask", "coverage_pct"})
    units = pending_units(ledger, analysis_qc)
    write_tsv(out / "pending-review-units.tsv", list(analysis_qc[0]) + ["pending_criteria"], units)
    write_tsv(out / "summary.tsv", list(summary[0]), summary)
    (out / "provenance.json").write_text(json.dumps(provenance(args, ledger), indent=2) + "\n")

    for row in summary:
        print("\t".join(f"{k}={v}" for k, v in row.items()))
    print(f"pending imaging reviews: {len(pending)}; rebuild entries: {len(rebuild)}")


if __name__ == "__main__":
    main()
