#!/usr/bin/env python3
"""Apply a reviewed decision file to pending rows of the exclusion ledger.

A decision file lists ledger_id, disposition, reviewer, review_date and
rationale. It is kept in docs/exclusion_decisions/ as the record of what was
decided together. Only pending_review rows can be decided; changing an
earlier decision means editing the ledger by hand in a reviewed commit.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from build_analysis_cohort import ROOT, read_tsv, write_tsv
from build_exclusion_ledger import DATE, LEDGER_FIELDS

DECISION_FIELDS = ("ledger_id", "disposition", "reviewer", "review_date", "rationale")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("decisions", type=Path)
    parser.add_argument("--ledger", type=Path, default=ROOT / "docs/exclusion_ledger.tsv")
    return parser.parse_args()


def apply(ledger, decisions):
    rows = {row["ledger_id"]: row for row in ledger}
    problems = []
    for decision in decisions:
        label = decision["ledger_id"]
        row = rows.get(label)
        if row is None:
            problems.append(f"{label}: not in ledger")
        elif row["disposition"] != "pending_review":
            problems.append(f"{label}: already {row['disposition']}")
        elif decision["disposition"] not in {"exclude", "retain", "not_applicable"}:
            problems.append(f"{label}: disposition {decision['disposition']!r}")
        elif not (
            decision["reviewer"]
            and DATE.match(decision["review_date"])
            and decision["rationale"]
        ):
            problems.append(f"{label}: needs reviewer, YYYY-MM-DD date, rationale")
    if len({d["ledger_id"] for d in decisions}) != len(decisions):
        problems.append("decision file repeats a ledger_id")
    if problems:
        raise SystemExit("ERROR: decisions not applied:\n  " + "\n  ".join(problems))
    for decision in decisions:
        rows[decision["ledger_id"]].update(
            {field: decision[field] for field in DECISION_FIELDS[1:]}
        )
    return ledger


def main():
    args = parse_args()
    ledger = read_tsv(args.ledger, set(LEDGER_FIELDS))
    decisions = read_tsv(args.decisions, set(DECISION_FIELDS))
    write_tsv(args.ledger, LEDGER_FIELDS, apply(ledger, decisions))
    print(f"applied {len(decisions)} decisions from {args.decisions}")


if __name__ == "__main__":
    main()
