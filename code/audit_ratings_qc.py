#!/usr/bin/env python3
"""Validate Shared Reward ratings cells and apply subject-level rules."""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
import statistics
from collections import defaultdict
from pathlib import Path


PARTNERS = (1, 2, 3)
TRAITS = (0, 1)
CELLS = tuple((partner, trait) for partner in PARTNERS for trait in TRAITS)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--missing-output", required=True, type=Path)
    parser.add_argument("--fail-on-incomplete", action="store_true")
    return parser.parse_args()


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def integer(value, label):
    number = float(str(value).strip())
    if not math.isfinite(number) or not number.is_integer():
        raise ValueError(f"invalid {label}: {value!r}")
    return int(number)


def response(value):
    number = float(str(value).strip())
    if not math.isfinite(number):
        raise ValueError(f"invalid response: {value!r}")
    return number


def evaluate(path):
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError("ratings file missing or empty")
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = set(reader.fieldnames or [])
    required = {"partner", "trait", "response"}
    if not rows or not required.issubset(fields):
        raise ValueError("ratings file lacks nonempty partner/trait/response data")
    values = defaultdict(list)
    for row_number, row in enumerate(rows, 2):
        try:
            cell = (integer(row["partner"], "partner"), integer(row["trait"], "trait"))
            value = response(row["response"])
        except (TypeError, ValueError) as error:
            raise ValueError(f"row {row_number}: {error}") from error
        if cell not in CELLS:
            raise ValueError(f"row {row_number}: unexpected partner/trait cell {cell}")
        values[cell].append(value)
    missing = [cell for cell in CELLS if not values[cell]]
    if missing:
        raise ValueError(
            "missing expected cells: "
            + ",".join(f"partner-{p}/trait-{t}" for p, t in missing)
        )
    means = {cell: statistics.mean(values[cell]) for cell in CELLS}
    win_sum = sum(means[(partner, 0)] for partner in PARTNERS)
    loss_sum = sum(means[(partner, 1)] for partner in PARTNERS)
    identical = len(set(means.values())) == 1
    reasons = []
    if identical:
        reasons.append("identical_ratings")
    # Equality is intentionally allowed: genuine indifference is not an exclusion.
    if loss_sum > win_sum:
        reasons.append("loss_sum_greater_than_win_sum")
    repeated = [cell for cell in CELLS if len(values[cell]) > 1]
    return {
        "ratings_file_sha256": sha256(path),
        "n_source_rows": len(rows),
        "means": means,
        "counts": {cell: len(values[cell]) for cell in CELLS},
        "win_sum": win_sum,
        "loss_sum": loss_sum,
        "identical_ratings": identical,
        "exclude_subject": bool(reasons),
        "exclusion_reason": ";".join(reasons),
        "review_flags": (
            "repeated_partner_trait_cells:" + ",".join(f"{p}-{t}" for p, t in repeated)
            if repeated
            else ""
        ),
    }


def write_tsv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    args = parse_args()
    with args.manifest.open(newline="") as handle:
        manifest = list(csv.DictReader(handle, delimiter="\t"))
    required = {"dataset", "subject", "ratings_file"}
    if not manifest or not required.issubset(manifest[0]):
        raise SystemExit("ERROR: ratings manifest contract is incomplete")
    complete, missing, seen = [], [], set()
    for unit in manifest:
        key = (unit["dataset"], unit["subject"])
        if key in seen:
            raise SystemExit(f"ERROR: duplicate ratings subject: {key}")
        seen.add(key)
        path = Path(unit["ratings_file"])
        try:
            result = evaluate(path)
            row = {
                "dataset": unit["dataset"],
                "subject": unit["subject"],
                "ratings_file": str(path.resolve()),
                "ratings_file_sha256": result["ratings_file_sha256"],
                "n_source_rows": result["n_source_rows"],
            }
            for partner, trait in CELLS:
                row[f"partner_{partner}_trait_{trait}_n"] = result["counts"][(partner, trait)]
                row[f"partner_{partner}_trait_{trait}_mean"] = result["means"][(partner, trait)]
            row.update(
                {
                    "win_sum": result["win_sum"],
                    "loss_sum": result["loss_sum"],
                    "identical_ratings": str(result["identical_ratings"]).lower(),
                    "exclude_subject": str(result["exclude_subject"]).lower(),
                    "exclusion_reason": result["exclusion_reason"],
                    "review_flags": result["review_flags"],
                }
            )
            complete.append(row)
        except (OSError, TypeError, ValueError) as error:
            missing.append(
                {
                    "dataset": unit["dataset"],
                    "subject": unit["subject"],
                    "ratings_file": str(path),
                    "problems": str(error),
                }
            )
    cell_fields = tuple(
        field
        for partner, trait in CELLS
        for field in (
            f"partner_{partner}_trait_{trait}_n",
            f"partner_{partner}_trait_{trait}_mean",
        )
    )
    output_fields = (
        "dataset",
        "subject",
        "ratings_file",
        "ratings_file_sha256",
        "n_source_rows",
    ) + cell_fields + (
        "win_sum",
        "loss_sum",
        "identical_ratings",
        "exclude_subject",
        "exclusion_reason",
        "review_flags",
    )
    complete.sort(key=lambda row: (row["dataset"], row["subject"]))
    missing.sort(key=lambda row: (row["dataset"], row["subject"]))
    write_tsv(args.output, output_fields, complete)
    write_tsv(
        args.missing_output,
        ("dataset", "subject", "ratings_file", "problems"),
        missing,
    )
    excluded = [row for row in complete if row["exclude_subject"] == "true"]
    reviews = [row for row in complete if row["review_flags"]]
    print(f"Ratings subjects checked: {len(manifest)}")
    print(f"Complete ratings subjects: {len(complete)}")
    print(f"Incomplete ratings subjects: {len(missing)}")
    print(f"Subject-level ratings exclusions: {len(excluded)}")
    print(f"Subjects with review flags: {len(reviews)}")
    print(f"Ratings audit: {args.output.resolve()}")
    print(f"Missing report: {args.missing_output.resolve()}")
    for row in missing[:20]:
        print(f"INCOMPLETE {row['dataset']} sub-{row['subject']}: {row['problems']}")
    if args.fail_on_incomplete and missing:
        return 1
    if not missing:
        print("CHECK PASSED: every ratings source has all six expected cells.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
