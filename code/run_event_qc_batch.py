#!/usr/bin/env python3
"""Create and QC model-specific full-trial events in parallel."""

from __future__ import annotations

import argparse
import csv
import json
import os
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import convert_harmonized_events as converter


IDENTIFIERS = ("dataset", "subject", "session", "run")
CONDITIONS = tuple(
    f"event_{partner}_{outcome}"
    for partner in ("computer", "friend", "stranger")
    for outcome in ("punish", "neutral", "reward")
)
REQUIRED = IDENTIFIERS + ("source_events", "harmonized_events", "output_json")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--log-dir", required=True, type=Path)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def summarize(rows, unit):
    counts = Counter(row["trial_type"] for row in rows)
    invalid = sorted(set(counts) - set(CONDITIONS) - {"missed_trial"})
    if invalid:
        raise ValueError("invalid harmonized trial types: " + ",".join(invalid))
    durations = [float(row["duration"]) for row in rows]
    if not rows or any(duration < 0 for duration in durations):
        raise ValueError("empty events or negative duration")
    missed = counts["missed_trial"]
    return {
        **{field: unit[field] for field in IDENTIFIERS},
        "source_events": str(Path(unit["source_events"]).resolve()),
        "harmonized_events": str(Path(unit["harmonized_events"]).resolve()),
        "n_trials": len(rows),
        "n_responded_trials": len(rows) - missed,
        "n_missed_trials": missed,
        "missed_trial_fraction": missed / len(rows),
        "trial_counts": {condition: counts[condition] for condition in CONDITIONS},
        "zero_count_conditions": [
            condition for condition in CONDITIONS if counts[condition] == 0
        ],
        "event_qc_definition_version": 1,
    }


def validate(unit):
    events = Path(unit["harmonized_events"])
    output = Path(unit["output_json"])
    if not events.is_file() or not output.is_file():
        raise ValueError("missing derivative pair")
    with events.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    expected = summarize(rows, unit)
    data = json.loads(output.read_text())
    for field in IDENTIFIERS + ("source_events", "harmonized_events"):
        if str(data[field]) != str(expected[field]):
            raise ValueError(f"{field}_contract")
    for field in (
        "n_trials",
        "n_responded_trials",
        "n_missed_trials",
        "trial_counts",
        "zero_count_conditions",
    ):
        if data[field] != expected[field]:
            raise ValueError(f"{field}_contract")
    if abs(float(data["missed_trial_fraction"]) - expected["missed_trial_fraction"]) > 1e-12:
        raise ValueError("missed_trial_fraction_contract")
    return data


def run_unit(unit, args):
    label = (
        f"{unit['dataset']}_sub-{unit['subject']}_"
        f"ses-{unit['session'] or 'none'}_run-{unit['run']}"
    )
    events = Path(unit["harmonized_events"])
    output = Path(unit["output_json"])
    log = args.log_dir / f"{label}.log"
    if unit["dataset"] not in {"rf1", "ds003745"}:
        return label, "failed", f"unsupported dataset: {unit['dataset']}"
    if (events.exists() or output.exists()) and not args.overwrite:
        try:
            validate(unit)
            return label, "existing", ""
        except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
            return label, "failed", f"invalid existing derivative ({error}); review and use --overwrite"
    events.parent.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    args.log_dir.mkdir(parents=True, exist_ok=True)
    event_tmp = Path(
        tempfile.NamedTemporaryFile(
            prefix=events.stem + ".", suffix=".tsv", dir=events.parent, delete=False
        ).name
    )
    json_tmp = Path(
        tempfile.NamedTemporaryFile(
            prefix=output.stem + ".", suffix=".json", dir=output.parent, delete=False
        ).name
    )
    try:
        source_rows = converter.read(Path(unit["source_events"]))
        rows = (
            converter.ds003745(source_rows)
            if unit["dataset"] == "ds003745"
            else converter.rf1(source_rows)
        )
        if not rows:
            raise ValueError("no model-specific full-trial rows generated")
        converter.write(event_tmp, rows)
        data = summarize(rows, unit)
        data["harmonized_events"] = str(events.resolve())
        json_tmp.write_text(json.dumps(data, indent=2) + "\n")
        os.replace(event_tmp, events)
        os.replace(json_tmp, output)
        validate(unit)
        log.write_text(
            f"Source: {Path(unit['source_events']).resolve()}\n"
            f"Harmonized: {events.resolve()}\n"
            f"Trials: {data['n_trials']}\n"
            f"Missed: {data['n_missed_trials']} ({100*data['missed_trial_fraction']:.3f}%)\n"
            f"Zero-count conditions: {','.join(data['zero_count_conditions']) or 'none'}\n"
        )
        return label, "completed", ""
    except Exception as error:
        log.write_text(f"ERROR: {error}\n")
        return label, "failed", str(error)
    finally:
        event_tmp.unlink(missing_ok=True)
        json_tmp.unlink(missing_ok=True)


def main():
    args = parse_args()
    if args.jobs < 1:
        raise SystemExit("ERROR: --jobs must be positive")
    with args.manifest.open(newline="") as handle:
        manifest = list(csv.DictReader(handle, delimiter="\t"))
    if not manifest or not set(REQUIRED).issubset(manifest[0]):
        raise SystemExit("ERROR: event-QC manifest contract is incomplete")
    print(
        f"Event-QC plan: {len(manifest)} unit(s), jobs={args.jobs}, "
        f"overwrite={str(args.overwrite).lower()}"
    )
    print(f"Per-unit logs: {args.log_dir}")
    counts = {"completed": 0, "existing": 0, "failed": 0}
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = [executor.submit(run_unit, unit, args) for unit in manifest]
        for future in as_completed(futures):
            label, status, detail = future.result()
            counts[status] += 1
            if status == "failed":
                print(f"ERROR: {label}: {detail}")
            else:
                print(f"{status.upper()}: {label}")
    print(f"Units scheduled: {len(manifest)}")
    print(f"Units newly completed: {counts['completed']}")
    print(f"Units verified existing: {counts['existing']}")
    print(f"Units failed: {counts['failed']}")
    if not counts["failed"]:
        print("CHECK PASSED: every harmonized event derivative is complete and valid.")
    return 1 if counts["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
