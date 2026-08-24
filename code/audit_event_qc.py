#!/usr/bin/env python3
"""Audit missed trials and condition support in harmonized full-trial events."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


IDENTIFIERS = ("dataset", "subject", "session", "run")
CONDITIONS = tuple(
    f"event_{partner}_{outcome}"
    for partner in ("computer", "friend", "stranger")
    for outcome in ("punish", "neutral", "reward")
)
RUN_FIELDS = IDENTIFIERS + (
    "source_events",
    "harmonized_events",
    "n_trials",
    "n_responded_trials",
    "n_missed_trials",
    "missed_trial_fraction",
) + tuple(f"n_{condition}" for condition in CONDITIONS) + (
    "zero_count_conditions",
    "exclude_run",
    "exclusion_reason",
)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--subject-output", required=True, type=Path)
    parser.add_argument("--missing-output", required=True, type=Path)
    parser.add_argument("--missed-trial-threshold", type=float, default=0.25)
    parser.add_argument("--fail-on-incomplete", action="store_true")
    return parser.parse_args()


def write_tsv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def validate(unit):
    output = Path(unit["output_json"])
    events = Path(unit["harmonized_events"])
    if not output.is_file() or not events.is_file():
        raise ValueError("missing derivative pair")
    data = json.loads(output.read_text())
    for field in IDENTIFIERS:
        if str(data[field]) != str(unit[field]):
            raise ValueError(f"{field}_contract")
    for result_field, unit_field in (
        ("source_events", "source_events"),
        ("harmonized_events", "harmonized_events"),
    ):
        if Path(data[result_field]).resolve() != Path(unit[unit_field]).resolve():
            raise ValueError(f"{result_field}_contract")
    counts = data["trial_counts"]
    if set(counts) != set(CONDITIONS):
        raise ValueError("trial_count_contract")
    if int(data["n_responded_trials"]) != sum(int(counts[x]) for x in CONDITIONS):
        raise ValueError("responded_trial_contract")
    if int(data["n_trials"]) != int(data["n_responded_trials"]) + int(data["n_missed_trials"]):
        raise ValueError("total_trial_contract")
    fraction = int(data["n_missed_trials"]) / int(data["n_trials"])
    if abs(float(data["missed_trial_fraction"]) - fraction) > 1e-12:
        raise ValueError("missed_fraction_contract")
    return data


def main():
    args = parse_args()
    if not 0 <= args.missed_trial_threshold < 1:
        raise SystemExit("ERROR: --missed-trial-threshold must be in [0, 1)")
    with args.manifest.open(newline="") as handle:
        manifest = list(csv.DictReader(handle, delimiter="\t"))
    required = set(IDENTIFIERS) | {
        "source_events",
        "harmonized_events",
        "output_json",
    }
    if not manifest or not required.issubset(manifest[0]):
        raise SystemExit("ERROR: event-QC manifest contract is incomplete")

    complete, missing = [], []
    for unit in manifest:
        identifiers = {field: unit[field] for field in IDENTIFIERS}
        try:
            data = validate(unit)
            fraction = float(data["missed_trial_fraction"])
            exclude = fraction > args.missed_trial_threshold
            complete.append(
                {
                    **identifiers,
                    "source_events": data["source_events"],
                    "harmonized_events": data["harmonized_events"],
                    "n_trials": data["n_trials"],
                    "n_responded_trials": data["n_responded_trials"],
                    "n_missed_trials": data["n_missed_trials"],
                    "missed_trial_fraction": fraction,
                    **{
                        f"n_{condition}": data["trial_counts"][condition]
                        for condition in CONDITIONS
                    },
                    "zero_count_conditions": ";".join(data["zero_count_conditions"]),
                    "exclude_run": str(exclude).lower(),
                    "exclusion_reason": (
                        f"missed_trials_gt_{100*args.missed_trial_threshold:g}pct"
                        if exclude
                        else ""
                    ),
                }
            )
        except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
            missing.append({**identifiers, "problems": f"invalid_event_qc:{error}"})

    complete.sort(key=lambda row: tuple(str(row[field]) for field in IDENTIFIERS))
    missing.sort(key=lambda row: tuple(str(row[field]) for field in IDENTIFIERS))
    write_tsv(args.output, RUN_FIELDS, complete)
    write_tsv(args.missing_output, IDENTIFIERS + ("problems",), missing)

    grouped = defaultdict(list)
    for row in complete:
        grouped[(row["dataset"], row["subject"])].append(row)
    subjects = []
    for (dataset, subject), rows in sorted(grouped.items()):
        excluded = sum(row["exclude_run"] == "true" for row in rows)
        usable = len(rows) - excluded
        subjects.append(
            {
                "dataset": dataset,
                "subject": subject,
                "n_runs": len(rows),
                "excluded_runs": excluded,
                "usable_runs": usable,
                "exclude_subject": str(usable == 0).lower(),
            }
        )
    write_tsv(
        args.subject_output,
        ("dataset", "subject", "n_runs", "excluded_runs", "usable_runs", "exclude_subject"),
        subjects,
    )

    excluded_runs = [row for row in complete if row["exclude_run"] == "true"]
    zero_condition_runs = [row for row in complete if row["zero_count_conditions"]]
    excluded_subjects = [row for row in subjects if row["exclude_subject"] == "true"]
    print(f"Event-QC units checked: {len(manifest)}")
    print(f"Complete event-QC units: {len(complete)}")
    print(f"Incomplete event-QC units: {len(missing)}")
    print(
        f"Runs excluded for >{100*args.missed_trial_threshold:g}% missed trials: "
        f"{len(excluded_runs)}"
    )
    print(f"Runs with one or more zero-count modeled conditions: {len(zero_condition_runs)}")
    print(f"Subjects with zero usable runs: {len(excluded_subjects)}")
    counts = Counter(row["dataset"] for row in complete)
    for dataset, count in sorted(counts.items()):
        rows = [row for row in complete if row["dataset"] == dataset]
        missed = sum(int(row["n_missed_trials"]) for row in rows)
        trials = sum(int(row["n_trials"]) for row in rows)
        print(
            f"  {dataset}: n={count}; missed={missed}/{trials} "
            f"({100*missed/trials:.3f}%)"
        )
    print(f"Run-level audit: {args.output.resolve()}")
    print(f"Subject-level audit: {args.subject_output.resolve()}")
    print(f"Missing report: {args.missing_output.resolve()}")
    for row in missing[:20]:
        print(
            f"INCOMPLETE {row['dataset']} sub-{row['subject']} "
            f"ses-{row['session'] or 'none'} run-{row['run']}: {row['problems']}"
        )
    if args.fail_on_incomplete and missing:
        return 1
    if not missing:
        print("CHECK PASSED: every run has valid harmonized full-trial event QC.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
