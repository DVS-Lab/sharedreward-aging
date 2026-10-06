#!/usr/bin/env python3
"""Seed or refresh the reviewed Shared Reward run/subject exclusion ledger.

The ledger holds one row per unit x criterion. Each row records its evidence
and a disposition (exclude, retain, pending_review or not_applicable).
Rebuilding refreshes seeded evidence but keeps reviewer decisions on pending
rows, and keeps manually added rows as they are. Decided seeded rows whose
evidence has disappeared are kept and marked stale rather than dropped.
"""

from __future__ import annotations

import argparse
import csv
import re
import statistics
from collections import Counter
from pathlib import Path

from audit_ratings_qc import CELLS, RATINGS_POLICY, rating_exclusion_reasons
from build_analysis_cohort import (
    ROOT,
    is_true,
    normalize_run,
    read_tsv,
    run_key,
    sort_key,
    write_tsv,
)

FROZEN = ROOT / "logs/records/full-analysis-20260930-203949-441196"
LEDGER_FIELDS = (
    "ledger_id",
    "dataset",
    "subject",
    "session",
    "run",
    "scope",
    "applies_to",
    "criterion",
    "metric",
    "value",
    "threshold",
    "threshold_rule",
    "evidence",
    "origin",
    "evidence_status",
    "decision_basis",
    "disposition",
    "reviewer",
    "review_date",
    "rationale",
)
DECISION_FIELDS = ("disposition", "reviewer", "review_date", "rationale")
DISPOSITIONS = {"exclude", "retain", "pending_review", "not_applicable"}
APPLIES_TO = {"imaging_all", "ratings_qualified"}
DECISION_BASES = {"automatic_rule", "curated_record", "reviewer"}
# Mirrors code/audit_analysis_qc.py; thresholds are per dataset over all runs.
IQR_MULTIPLIER = 1.5
IQR_CRITERIA = (
    ("low_tsnr_iqr_outlier", "median_tsnr", "low"),
    ("high_mean_fd_iqr_outlier", "mean_fd_mm", "high"),
    ("low_coverage_iqr_outlier", "coverage_pct", "low"),
)
EXPECTED = {"runs": 768, "task_ready_runs": 744, "task_ready_subjects": 393}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# Units that predate this ledger and were never given a recorded reason.
PRIOR_REVIEW_ITEMS = (
    {
        "dataset": "rf1",
        "subject": "11012",
        "session": "01",
        "run": "1",
        "criterion": "prior_pipeline_removal_unrecorded",
        "evidence": "Feb 2026 pipeline (code/archive/exclusions-2026-02) switched "
        "this subject to an L1 run-2 passthrough in commit 71e1491; no reason recorded",
    },
)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-dispositions",
        type=Path,
        default=ROOT / "logs/records/analysis-run-dispositions.tsv",
    )
    parser.add_argument(
        "--analysis-qc",
        type=Path,
        default=ROOT / "logs/records/analysis-qc-run-level.tsv",
    )
    parser.add_argument(
        "--event-qc",
        type=Path,
        default=ROOT / "logs/records/fulltrial-event-qc-run-level.tsv",
    )
    parser.add_argument(
        "--curated-exclusions",
        type=Path,
        default=ROOT / "docs/curated_run_exclusions.tsv",
    )
    parser.add_argument(
        "--ratings-qc",
        type=Path,
        default=ROOT / "logs/records/ratings-qc-subject-level.tsv",
    )
    parser.add_argument(
        "--behavioral-eligibility",
        type=Path,
        default=ROOT / "qc/ratings-raw/behavioral-eligibility.tsv",
    )
    parser.add_argument("--l1-manifest", type=Path, default=FROZEN / "L1-task-ready.tsv")
    parser.add_argument("--l2-manifest", type=Path, default=FROZEN / "L2-task-ready.tsv")
    parser.add_argument(
        "--coverage-mosaics", type=Path, default=ROOT / "qc/coverage-mosaics"
    )
    parser.add_argument(
        "--ledger", type=Path, default=ROOT / "docs/exclusion_ledger.tsv"
    )
    parser.add_argument(
        "--threshold-output",
        type=Path,
        default=ROOT / "logs/records/exclusion-ledger/iqr-thresholds.tsv",
    )
    return parser.parse_args()


def ledger_id(row):
    parts = [row["dataset"], f"sub-{row['subject']}"]
    if row["session"]:
        parts.append(f"ses-{row['session']}")
    if row["run"] != "*":
        parts.append(f"run-{normalize_run(row['run'])}")
    return "_".join(parts + [row["criterion"]])


def make_row(unit, criterion, **fields):
    row = {field: "" for field in LEDGER_FIELDS}
    row.update(
        dataset=unit["dataset"],
        subject=unit["subject"],
        session=unit.get("session", ""),
        run=unit.get("run", "*"),
        criterion=criterion,
        origin="seeded",
        evidence_status="current",
    )
    row.update(fields)
    row["scope"] = "subject" if row["run"] == "*" else "run"
    row["ledger_id"] = ledger_id(row)
    return row


def check_counts(dispositions, l1, l2):
    observed = {
        "runs": len(dispositions),
        "task_ready_runs": sum(r["disposition"] == "task_ready" for r in dispositions),
        "task_ready_subjects": len(l2),
    }
    if observed != EXPECTED or len(l1) != EXPECTED["task_ready_runs"]:
        raise SystemExit(f"ERROR: inventory {observed} (L1 {len(l1)}) != {EXPECTED}")
    ready = {run_key(r) for r in dispositions if r["disposition"] == "task_ready"}
    if ready != {run_key(r) for r in l1}:
        raise SystemExit("ERROR: task_ready dispositions differ from frozen L1 manifest")


def iqr_thresholds(qc):
    thresholds, summary = {}, []
    for dataset in sorted({r["dataset"] for r in qc}):
        subset = [r for r in qc if r["dataset"] == dataset]
        for criterion, metric, side in IQR_CRITERIA:
            values = [float(r[metric]) for r in subset]
            q1, _, q3 = statistics.quantiles(values, n=4, method="inclusive")
            iqr = q3 - q1
            limit = q1 - IQR_MULTIPLIER * iqr if side == "low" else q3 + IQR_MULTIPLIER * iqr
            thresholds[(dataset, criterion)] = (metric, side, limit)
            n_flagged = sum(v < limit if side == "low" else v > limit for v in values)
            summary.append(
                {
                    "dataset": dataset,
                    "criterion": criterion,
                    "metric": metric,
                    "population": "all_runs",
                    "n_runs": len(values),
                    "q1": f"{q1:.6g}",
                    "q3": f"{q3:.6g}",
                    "iqr_multiplier": IQR_MULTIPLIER,
                    "direction": "below" if side == "low" else "above",
                    "threshold": f"{limit:.6g}",
                    "n_flagged": n_flagged,
                }
            )
    return thresholds, summary


def imaging_rows(qc, dispositions, thresholds, mosaics):
    status = {run_key(r): r["disposition"] for r in dispositions}
    rows = []
    for unit in qc:
        recorded = set(filter(None, unit["qc_flags"].split(";")))
        derived = set()
        for criterion, metric, side in IQR_CRITERIA:
            _, _, limit = thresholds[(unit["dataset"], criterion)]
            value = float(unit[metric])
            if not (value < limit if side == "low" else value > limit):
                continue
            derived.add(criterion)
            evidence = [
                "logs/records/analysis-qc-run-level.tsv",
                f"high_motion_fraction={float(unit['high_motion_fraction']):.3f}",
                f"max_fd_mm={float(unit['max_fd_mm']):.3f}",
            ]
            stem = (
                f"{unit['dataset']}_sub-{unit['subject']}_ses-{unit['session']}"
                f"_run-{normalize_run(unit['run'])}_coverage-"
            )
            evidence += [
                f"qc/coverage-mosaics/{p.name}" for p in mosaics if p.name.startswith(stem)
            ]
            task_excluded = status[run_key(unit)] != "task_ready"
            rows.append(
                make_row(
                    unit,
                    criterion,
                    applies_to="imaging_all",
                    metric=metric,
                    value=f"{value:.6g}",
                    threshold=f"{limit:.6g}",
                    threshold_rule=(
                        f"{'Q1-' if side == 'low' else 'Q3+'}{IQR_MULTIPLIER}xIQR, "
                        "per dataset, all runs"
                    ),
                    evidence="; ".join(evidence),
                    decision_basis="reviewer",
                    disposition="not_applicable" if task_excluded else "pending_review",
                    rationale="run already task-excluded" if task_excluded else "",
                )
            )
        if derived != recorded:
            raise SystemExit(
                f"ERROR: recomputed flags {sorted(derived)} != recorded "
                f"{sorted(recorded)} for {run_key(unit)}"
            )
    return rows


def task_rows(dispositions, event_qc, curated):
    events = {run_key(r): r for r in event_qc}
    curated_by_reason = {}
    for row in curated:
        curated_by_reason[(row["dataset"], row["subject"], row["exclusion_reason"])] = row
    rows = []
    for unit in dispositions:
        for reason in filter(None, unit["task_exclusion_reasons"].split(";")):
            fields = dict(applies_to="imaging_all", disposition="exclude")
            if reason == "missed_trials_gt_25pct":
                fields.update(
                    metric="missed_trial_fraction",
                    value=f"{float(events[run_key(unit)]['missed_trial_fraction']):.4g}",
                    threshold="0.25",
                    threshold_rule="strictly greater than 25% of trials",
                    evidence="logs/records/fulltrial-event-qc-run-level.tsv",
                    decision_basis="automatic_rule",
                    reviewer="rule:docs/EXCLUSION_POLICY.md",
                    rationale="poor task compliance",
                )
            elif reason == "source_excluded_missing_events":
                fields.update(
                    evidence="logs/records/analysis-run-dispositions.tsv; "
                    "logs/runlists/fulltrial-event-qc-missing.tsv (Linux2)",
                    decision_basis="automatic_rule",
                    reviewer="rule:docs/EXCLUSION_POLICY.md",
                    rationale="source events file missing; run cannot be modeled",
                )
            else:
                source = curated_by_reason.get((unit["dataset"], unit["subject"], reason))
                if source is None:
                    raise SystemExit(f"ERROR: unrecognized task exclusion {reason}")
                fields.update(
                    evidence="docs/curated_run_exclusions.tsv",
                    decision_basis="curated_record",
                    reviewer=source["source"],
                    rationale=source["note"],
                )
            rows.append(make_row(unit, reason, **fields))
    return rows


def ratings_rows(ratings_qc, eligibility, subjects):
    ratings = {(r["dataset"], r["subject"]): r for r in ratings_qc}
    rows = []
    for unit in eligibility:
        key = (unit["dataset"], unit["subject"])
        if unit["ratings_policy"] != RATINGS_POLICY:
            raise SystemExit(f"ERROR: unexpected ratings policy for {key}")
        source = ratings[key]
        if source["exclusion_reason"] in {"", "loss_sum_greater_than_win_sum"}:
            # Re-derive per-partner reasons rather than copying the old aggregate label.
            means = {
                (p, t): float(source[f"partner_{p}_trait_{t}_mean"]) for p, t in CELLS
            }
            reasons = rating_exclusion_reasons(means)
            values = ",".join(f"p{p}t{t}={means[(p, t)]:g}" for p, t in CELLS)
        else:
            reasons, values = source["exclusion_reason"].split(";"), ""
        if bool(reasons) == is_true(unit["primary_included"]):
            raise SystemExit(f"ERROR: derived ratings reasons disagree with {key}")
        for reason in reasons:
            rows.append(
                make_row(
                    {**unit, "session": subjects[key]},
                    f"ratings_{reason}",
                    applies_to="ratings_qualified",
                    metric="raw rating means (partner 1/2/3=computer/stranger/friend; "
                    "trait 0/1=win/loss)" if values else "",
                    value=values,
                    threshold_rule=RATINGS_POLICY,
                    evidence="qc/ratings-raw/behavioral-eligibility.tsv; "
                    "logs/records/ratings-qc-subject-level.tsv",
                    decision_basis="automatic_rule",
                    disposition="exclude",
                    reviewer="rule:docs/RAW_RATINGS_ANALYSIS.md",
                    rationale="baseline ratings; not an imaging-gate exclusion",
                )
            )
    return rows


def validate(rows, run_keys, subject_keys):
    seen = Counter(r["ledger_id"] for r in rows)
    duplicates = [key for key, count in seen.items() if count > 1]
    if duplicates:
        raise SystemExit(f"ERROR: duplicate ledger_id: {duplicates[:5]}")
    problems = []
    for row in rows:
        label = row["ledger_id"]
        if row["disposition"] not in DISPOSITIONS:
            problems.append(f"{label}: disposition {row['disposition']!r}")
        if row["applies_to"] not in APPLIES_TO:
            problems.append(f"{label}: applies_to {row['applies_to']!r}")
        if row["decision_basis"] not in DECISION_BASES:
            problems.append(f"{label}: decision_basis {row['decision_basis']!r}")
        if row["origin"] not in {"seeded", "manual"}:
            problems.append(f"{label}: origin {row['origin']!r}")
        unit = (row["dataset"], row["subject"], row["session"])
        if row["run"] == "*":
            if unit not in subject_keys:
                problems.append(f"{label}: matches no subject (check dataset/subject/session)")
        elif (*unit, normalize_run(row["run"])) not in run_keys:
            problems.append(f"{label}: matches no run (check dataset/subject/session/run)")
        if row["disposition"] == "pending_review" and (row["reviewer"] or row["review_date"]):
            problems.append(f"{label}: pending row has a reviewer/date")
        needs_review = row["decision_basis"] == "reviewer" or row["origin"] == "manual"
        if needs_review and row["disposition"] in {"exclude", "retain"}:
            if not (row["reviewer"] and DATE.match(row["review_date"]) and row["rationale"]):
                problems.append(f"{label}: decision needs reviewer, YYYY-MM-DD date, rationale")
    if problems:
        raise SystemExit("ERROR: invalid ledger rows:\n  " + "\n  ".join(problems))


def merge(seeded, existing):
    """Keep reviewer decisions and manual rows across evidence refreshes."""
    previous = {r["ledger_id"]: r for r in existing}
    merged = []
    for row in seeded:
        old = previous.pop(row["ledger_id"], None)
        if old and row["decision_basis"] == "reviewer" and row["disposition"] == "pending_review":
            # Carries decisions and any working notes left on still-pending rows.
            row.update({field: old[field] for field in DECISION_FIELDS})
        merged.append(row)
    for old in previous.values():
        if old["origin"] == "manual":
            merged.append(old)
        elif old["decision_basis"] == "reviewer" and old["disposition"] != "pending_review":
            merged.append({**old, "evidence_status": "stale"})
            print(f"WARNING: kept decided row whose evidence disappeared: {old['ledger_id']}")
        else:
            print(f"NOTE: dropped seeded row no longer supported: {old['ledger_id']}")
    return merged


def main():
    args = parse_args()
    dispositions = read_tsv(args.run_dispositions, {"disposition", "task_exclusion_reasons"})
    qc = read_tsv(args.analysis_qc, {"qc_flags", "coverage_pct", "mean_fd_mm"})
    event_qc = read_tsv(args.event_qc, {"missed_trial_fraction"})
    curated = read_tsv(args.curated_exclusions, {"exclusion_reason", "source", "note"})
    ratings_qc = read_tsv(args.ratings_qc, {"exclusion_reason"})
    eligibility = read_tsv(args.behavioral_eligibility, {"primary_included"})
    l1 = read_tsv(args.l1_manifest, {"input"})
    l2 = read_tsv(args.l2_manifest, {"runs", "subject_level_strategy"})
    check_counts(dispositions, l1, l2)
    if {run_key(r) for r in qc} != {run_key(r) for r in dispositions}:
        raise SystemExit("ERROR: analysis QC and dispositions cover different runs")
    qc_inputs = {run_key(r): r["input"] for r in qc}
    if any(qc_inputs[run_key(r)] != r["input"] for r in l1):
        raise SystemExit("ERROR: QC evidence was measured on different inputs than L1")
    subjects = {(r["dataset"], r["subject"]): r["session"] for r in l2}
    if {(r["dataset"], r["subject"]) for r in eligibility} != set(subjects):
        raise SystemExit("ERROR: behavioral eligibility does not cover the L2 subjects")

    thresholds, summary = iqr_thresholds(qc)
    mosaics = sorted(args.coverage_mosaics.glob("*.png"))
    seeded = task_rows(dispositions, event_qc, curated)
    seeded += imaging_rows(qc, dispositions, thresholds, mosaics)
    for item in PRIOR_REVIEW_ITEMS:
        seeded.append(
            make_row(
                item,
                item["criterion"],
                applies_to="imaging_all",
                evidence=item["evidence"],
                decision_basis="reviewer",
                disposition="pending_review",
            )
        )
    seeded += ratings_rows(ratings_qc, eligibility, subjects)

    existing = read_tsv(args.ledger, {"ledger_id"}) if args.ledger.is_file() else []
    rows = merge(seeded, existing)
    run_keys = {run_key(r) for r in dispositions}
    validate(rows, run_keys, {key[:3] for key in run_keys})
    rows.sort(key=lambda r: (r["applies_to"], *sort_key(r), r["criterion"]))
    write_tsv(args.ledger, LEDGER_FIELDS, rows)
    write_tsv(args.threshold_output, list(summary[0]), summary)

    counts = Counter((r["applies_to"], r["criterion"], r["disposition"]) for r in rows)
    for (applies_to, criterion, disposition), n in sorted(counts.items()):
        print(f"{n:4d}  {applies_to:17s} {criterion:42s} {disposition}")
    print(f"wrote {len(rows)} rows to {args.ledger}")


if __name__ == "__main__":
    main()
