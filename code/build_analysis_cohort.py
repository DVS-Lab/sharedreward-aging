#!/usr/bin/env python3
"""Freeze task-valid and ratings-qualified Shared Reward analysis manifests."""

from __future__ import annotations

import argparse
import csv
import os
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IDENTIFIERS = ("dataset", "subject", "session", "run")
L1_FIELDS = IDENTIFIERS + (
    "input",
    "mask",
    "confounds",
    "source_events",
    "harmonized_events",
    "missed_trial_fraction",
    "zero_count_conditions",
    "imaging_qc_flags",
    "ratings_eligible",
    "ratings_exclusion_reason",
)
DISPOSITION_FIELDS = IDENTIFIERS + (
    "disposition",
    "task_exclusion_reasons",
    "review_hold_reasons",
    "zero_count_conditions",
    "imaging_qc_flags",
    "ratings_eligible",
    "ratings_exclusion_reason",
)
L2_FIELDS = (
    "dataset",
    "subject",
    "session",
    "n_runs",
    "runs",
    "subject_level_strategy",
    "ratings_eligible",
    "ratings_exclusion_reason",
)
SUBJECT_FIELDS = (
    "dataset",
    "subject",
    "session",
    "n_imaging_runs",
    "n_task_ready_runs",
    "task_ready_runs",
    "n_task_excluded_runs",
    "task_excluded_runs",
    "n_review_hold_runs",
    "review_hold_runs",
    "task_l2_ready",
    "ratings_eligible",
    "ratings_exclusion_reason",
    "ratings_l2_ready",
)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rf1-confounds-root",
        type=Path,
        default=Path(
            os.environ.get(
                "RF1_CONFOUNDS_ROOT",
                "/ZPOOL/data/projects/rf1-sra-linux2/derivatives/fsl/"
                "confounds_tedana",
            )
        ),
    )
    parser.add_argument(
        "--ds-confounds-root",
        type=Path,
        default=ROOT / "derivatives/fsl/confounds_fmriprep",
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
        "--event-source-missing",
        type=Path,
        default=ROOT / "logs/runlists/fulltrial-event-qc-missing.tsv",
    )
    parser.add_argument(
        "--ratings-qc",
        type=Path,
        default=ROOT / "logs/records/ratings-qc-subject-level.tsv",
    )
    parser.add_argument(
        "--curated-exclusions",
        type=Path,
        default=ROOT / "docs/curated_run_exclusions.tsv",
    )
    parser.add_argument(
        "--l1-task-output",
        type=Path,
        default=ROOT / "logs/runlists/L1-task-ready.tsv",
    )
    parser.add_argument(
        "--l1-ratings-output",
        type=Path,
        default=ROOT / "logs/runlists/L1-ratings-ready.tsv",
    )
    parser.add_argument(
        "--l1-review-output",
        type=Path,
        default=ROOT / "logs/runlists/L1-model-review-hold.tsv",
    )
    parser.add_argument(
        "--run-disposition-output",
        type=Path,
        default=ROOT / "logs/records/analysis-run-dispositions.tsv",
    )
    parser.add_argument(
        "--l2-task-output",
        type=Path,
        default=ROOT / "logs/runlists/L2-task-ready.tsv",
    )
    parser.add_argument(
        "--l2-ratings-output",
        type=Path,
        default=ROOT / "logs/runlists/L2-ratings-ready.tsv",
    )
    parser.add_argument(
        "--subject-output",
        type=Path,
        default=ROOT / "logs/records/analysis-subject-dispositions.tsv",
    )
    return parser.parse_args()


def read_tsv(path: Path, required: set[str]) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    fields = set(rows[0]) if rows else set()
    if not rows or not required.issubset(fields):
        missing = ",".join(sorted(required - fields))
        raise ValueError(f"{path}: missing required fields: {missing or 'no data rows'}")
    return rows


def write_tsv(path: Path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def normalize_run(value: str) -> str:
    value = value.strip()
    if value == "*":
        return value
    try:
        return str(int(value))
    except ValueError:
        return value


def run_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (
        row["dataset"].strip(),
        row["subject"].strip(),
        row.get("session", "").strip(),
        normalize_run(row["run"]),
    )


def subject_key(row: dict[str, str]) -> tuple[str, str]:
    return row["dataset"].strip(), row["subject"].strip()


def sort_key(row: dict[str, str]):
    def sortable(value):
        try:
            return (0, int(value))
        except (TypeError, ValueError):
            return (1, str(value))

    return (
        row.get("dataset", ""),
        sortable(row.get("subject", "")),
        row.get("session", ""),
        sortable(normalize_run(row.get("run", ""))),
    )


def indexed(rows, key_function, label):
    result = {}
    for row in rows:
        key = key_function(row)
        if key in result:
            raise ValueError(f"duplicate {label} key: {key}")
        result[key] = row
    return result


def is_true(value: str) -> bool:
    return value.strip().lower() == "true"


def fsl_confounds_path(args, row: dict[str, str]) -> Path:
    subject = row["subject"]
    run = normalize_run(row["run"])
    if row["dataset"] == "rf1":
        session = row["session"]
        return args.rf1_confounds_root / f"sub-{subject}" / (
            f"sub-{subject}_ses-{session}_task-sharedreward_run-{run}_"
            "desc-TedanaPlusConfounds.tsv"
        )
    if row["dataset"] == "ds003745":
        run_label = f"{int(run):02d}"
        return args.ds_confounds_root / f"sub-{subject}" / "func" / (
            f"sub-{subject}_task-sharedreward_run-{run_label}_"
            "desc-FSLConfounds.tsv"
        )
    raise ValueError(f"unsupported dataset for FSL confounds: {row['dataset']}")


def build(args):
    analysis = read_tsv(
        args.analysis_qc,
        set(IDENTIFIERS) | {"input", "mask", "confounds", "qc_flags"},
    )
    events = read_tsv(
        args.event_qc,
        set(IDENTIFIERS)
        | {
            "source_events",
            "harmonized_events",
            "missed_trial_fraction",
            "zero_count_conditions",
            "exclude_run",
            "exclusion_reason",
        },
    )
    event_missing = read_tsv(
        args.event_source_missing, set(IDENTIFIERS) | {"problems"}
    )
    ratings = read_tsv(
        args.ratings_qc,
        {"dataset", "subject", "exclude_subject", "exclusion_reason"},
    )
    curated = read_tsv(
        args.curated_exclusions,
        set(IDENTIFIERS) | {"exclusion_reason", "source", "note"},
    )

    analysis_index = indexed(analysis, run_key, "analysis")
    event_index = indexed(events, run_key, "event")
    missing_index = indexed(event_missing, run_key, "event-source-missing")
    ratings_index = indexed(ratings, subject_key, "ratings")

    overlap = set(event_index) & set(missing_index)
    if overlap:
        raise ValueError(f"event QC and source-missing overlap: {sorted(overlap)[:5]}")
    event_inventory = set(event_index) | set(missing_index)
    if set(analysis_index) != event_inventory:
        added = sorted(event_inventory - set(analysis_index))[:10]
        unresolved = sorted(set(analysis_index) - event_inventory)[:10]
        raise ValueError(
            "analysis/event inventory mismatch; "
            f"not_in_analysis={added}; unresolved_analysis_runs={unresolved}"
        )
    analysis_subjects = {subject_key(row) for row in analysis}
    if analysis_subjects != set(ratings_index):
        missing_ratings = sorted(analysis_subjects - set(ratings_index))[:10]
        extra_ratings = sorted(set(ratings_index) - analysis_subjects)[:10]
        raise ValueError(
            "analysis/ratings subject inventory mismatch; "
            f"missing_ratings={missing_ratings}; extra_ratings={extra_ratings}"
        )

    curated_index = defaultdict(list)
    for row in curated:
        key = run_key(row)
        matched = False
        for analysis_key in analysis_index:
            if all(
                expected == "*" or expected == observed
                for expected, observed in zip(key, analysis_key)
            ):
                curated_index[analysis_key].append(row)
                matched = True
        if not matched:
            raise ValueError(f"curated exclusion matches no analysis runs: {key}")

    task_ready, ratings_ready, review, dispositions = [], [], [], []
    by_subject_session = defaultdict(list)
    for key, base in sorted(analysis_index.items(), key=lambda item: sort_key(item[1])):
        rating = ratings_index[subject_key(base)]
        rating_eligible = not is_true(rating["exclude_subject"])
        rating_reason = rating["exclusion_reason"].strip()
        exclusion_reasons = []
        hold_reasons = []
        event = event_index.get(key)

        if key in missing_index:
            exclusion_reasons.append("source_excluded_missing_events")
        else:
            if is_true(event["exclude_run"]):
                exclusion_reasons.append(event["exclusion_reason"])
            if event["zero_count_conditions"].strip() and not exclusion_reasons:
                hold_reasons.append("model_review_zero_count_conditions")
        for curated_row in curated_index.get(key, []):
            exclusion_reasons.append(curated_row["exclusion_reason"].strip())

        if exclusion_reasons:
            disposition = "task_excluded"
        elif hold_reasons:
            disposition = "model_review_hold"
        else:
            disposition = "task_ready"

        l1_row = {
            **{field: base[field] for field in IDENTIFIERS},
            "input": base["input"],
            "mask": base["mask"],
            "confounds": str(fsl_confounds_path(args, base).resolve()),
            "source_events": event["source_events"] if event else "",
            "harmonized_events": event["harmonized_events"] if event else "",
            "missed_trial_fraction": event["missed_trial_fraction"] if event else "",
            "zero_count_conditions": event["zero_count_conditions"] if event else "",
            "imaging_qc_flags": base["qc_flags"],
            "ratings_eligible": str(rating_eligible).lower(),
            "ratings_exclusion_reason": rating_reason,
        }
        if disposition == "task_ready":
            confounds = Path(l1_row["confounds"])
            if not confounds.is_file() or confounds.stat().st_size == 0:
                raise ValueError(
                    "task-ready run lacks its FSL nuisance matrix: "
                    f"{key}: {confounds}"
                )
        disposition_row = {
            **{field: base[field] for field in IDENTIFIERS},
            "disposition": disposition,
            "task_exclusion_reasons": ";".join(dict.fromkeys(exclusion_reasons)),
            "review_hold_reasons": ";".join(dict.fromkeys(hold_reasons)),
            "zero_count_conditions": l1_row["zero_count_conditions"],
            "imaging_qc_flags": base["qc_flags"],
            "ratings_eligible": l1_row["ratings_eligible"],
            "ratings_exclusion_reason": rating_reason,
        }
        dispositions.append(disposition_row)
        by_subject_session[(key[0], key[1], key[2])].append(disposition_row)
        if disposition == "task_ready":
            task_ready.append(l1_row)
            if rating_eligible:
                ratings_ready.append(l1_row)
        elif disposition == "model_review_hold":
            review.append(l1_row)

    subject_rows, l2_task, l2_ratings = [], [], []
    for (dataset, subject, session), rows in sorted(
        by_subject_session.items(), key=lambda item: sort_key(item[1][0])
    ):
        ready_runs = [row["run"] for row in rows if row["disposition"] == "task_ready"]
        excluded_runs = [
            row["run"] for row in rows if row["disposition"] == "task_excluded"
        ]
        held_runs = [
            row["run"] for row in rows if row["disposition"] == "model_review_hold"
        ]
        rating = ratings_index[(dataset, subject)]
        rating_eligible = not is_true(rating["exclude_subject"])
        rating_reason = rating["exclusion_reason"].strip()
        l2_row = {
            "dataset": dataset,
            "subject": subject,
            "session": session,
            "n_runs": len(ready_runs),
            "runs": ",".join(ready_runs),
            "subject_level_strategy": (
                "fixed_effects" if len(ready_runs) == 2 else "l1_passthrough"
            ),
            "ratings_eligible": str(rating_eligible).lower(),
            "ratings_exclusion_reason": rating_reason,
        }
        if ready_runs:
            l2_task.append(l2_row)
            if rating_eligible:
                l2_ratings.append(l2_row)
        subject_rows.append(
            {
                "dataset": dataset,
                "subject": subject,
                "session": session,
                "n_imaging_runs": len(rows),
                "n_task_ready_runs": len(ready_runs),
                "task_ready_runs": ",".join(ready_runs),
                "n_task_excluded_runs": len(excluded_runs),
                "task_excluded_runs": ",".join(excluded_runs),
                "n_review_hold_runs": len(held_runs),
                "review_hold_runs": ",".join(held_runs),
                "task_l2_ready": str(bool(ready_runs)).lower(),
                "ratings_eligible": str(rating_eligible).lower(),
                "ratings_exclusion_reason": rating_reason,
                "ratings_l2_ready": str(bool(ready_runs) and rating_eligible).lower(),
            }
        )

    write_tsv(args.l1_task_output, L1_FIELDS, task_ready)
    write_tsv(args.l1_ratings_output, L1_FIELDS, ratings_ready)
    write_tsv(args.l1_review_output, L1_FIELDS, review)
    write_tsv(args.run_disposition_output, DISPOSITION_FIELDS, dispositions)
    write_tsv(args.l2_task_output, L2_FIELDS, l2_task)
    write_tsv(args.l2_ratings_output, L2_FIELDS, l2_ratings)
    write_tsv(args.subject_output, SUBJECT_FIELDS, subject_rows)

    task_excluded = sum(row["disposition"] == "task_excluded" for row in dispositions)
    print(f"Imaging-ready runs considered: {len(analysis)}")
    print(f"Task-ready L1 runs: {len(task_ready)}")
    print(f"Task-excluded runs: {task_excluded}")
    print(f"Model-review holds: {len(review)}")
    print(f"Task-ready L2 subject-sessions: {len(l2_task)}")
    print(f"Ratings-qualified L1 runs: {len(ratings_ready)}")
    print(f"Ratings-qualified L2 subject-sessions: {len(l2_ratings)}")
    for path in (
        args.l1_task_output,
        args.l1_ratings_output,
        args.l1_review_output,
        args.run_disposition_output,
        args.l2_task_output,
        args.l2_ratings_output,
        args.subject_output,
    ):
        print(f"Wrote: {path.resolve()}")


def main():
    args = parse_args()
    try:
        build(args)
    except (OSError, ValueError) as error:
        raise SystemExit(f"ERROR: {error}") from error
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
