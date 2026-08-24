#!/usr/bin/env python3
"""Validate Shared Reward ratings cells and apply subject-level rules."""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
import os
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


def source_path(path):
    """Return an absolute source-tree path without dereferencing annex symlinks."""
    return Path(os.path.abspath(path))


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
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        source_rows = list(reader)
        fields = {field.strip().casefold(): field for field in (reader.fieldnames or [])}
    required = {"partner", "trait"}
    response_field = fields.get("response") or fields.get("rating")
    if not source_rows or not required.issubset(fields) or response_field is None:
        raise ValueError("ratings file lacks nonempty partner/trait/response data")
    blocks = [[]]
    for row in source_rows:
        # Four authoritative RF1 files contain pre- and post-scan blocks
        # separated by a repeated CSV header. Recognize the boundary from its
        # labels rather than deleting a fixed number of rows.
        if (
            str(row.get(fields["partner"], "")).strip().casefold() == "partner"
            and str(row.get(fields["trait"], "")).strip().casefold() == "trait"
            and str(row.get(response_field, "")).strip().casefold()
            in {"rating", "response"}
        ):
            if blocks[-1]:
                blocks.append([])
            continue
        blocks[-1].append(row)
    blocks = [block for block in blocks if block]
    if not blocks:
        raise ValueError("ratings file contains no data blocks")
    rows = blocks[-1]
    values = defaultdict(list)
    for row_number, row in enumerate(rows, 1):
        try:
            cell = (
                integer(row[fields["partner"]], "partner"),
                integer(row[fields["trait"]], "trait"),
            )
            value = response(row[response_field])
        except (TypeError, ValueError) as error:
            raise ValueError(f"selected-block row {row_number}: {error}") from error
        if cell not in CELLS:
            raise ValueError(
                f"selected-block row {row_number}: unexpected partner/trait cell {cell}"
            )
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
        "n_source_rows": len(source_rows),
        "n_rating_blocks": len(blocks),
        "selected_rating_block": len(blocks),
        "n_selected_rows": len(rows),
        "means": means,
        "counts": {cell: len(values[cell]) for cell in CELLS},
        "win_sum": win_sum,
        "loss_sum": loss_sum,
        "identical_ratings": identical,
        "exclude_subject": bool(reasons),
        "exclusion_reason": ";".join(reasons),
        "review_flags": ";".join(
            flag
            for flag in (
                (
                    f"selected_last_complete_block:{len(blocks)}_of_{len(blocks)}"
                    if len(blocks) > 1
                    else ""
                ),
                (
                    "repeated_partner_trait_cells:"
                    + ",".join(f"{p}-{t}" for p, t in repeated)
                    if repeated
                    else ""
                ),
            )
            if flag
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
        source_resolution = unit.get("source_resolution", "")
        candidate_count = unit.get("candidate_count", "")
        candidate_files = unit.get("candidate_files", "")
        source_value = unit["ratings_file"].strip()
        if not source_value and source_resolution == "missing":
            complete.append(
                {
                    "dataset": unit["dataset"],
                    "subject": unit["subject"],
                    "ratings_file": "",
                    "source_resolution": source_resolution,
                    "candidate_count": candidate_count,
                    "candidate_files": candidate_files,
                    "ratings_file_sha256": "",
                    "n_source_rows": 0,
                    "n_rating_blocks": 0,
                    "selected_rating_block": "",
                    "n_selected_rows": 0,
                    **{
                        field: ""
                        for partner, trait in CELLS
                        for field in (
                            f"partner_{partner}_trait_{trait}_n",
                            f"partner_{partner}_trait_{trait}_mean",
                        )
                    },
                    "win_sum": "",
                    "loss_sum": "",
                    "identical_ratings": "",
                    "exclude_subject": "true",
                    "exclusion_reason": "missing_ratings_file",
                    "review_flags": "",
                }
            )
            continue
        path = Path(source_value)
        if path.is_file() and path.stat().st_size == 0:
            complete.append(
                {
                    "dataset": unit["dataset"],
                    "subject": unit["subject"],
                    "ratings_file": str(source_path(path)),
                    "source_resolution": source_resolution,
                    "candidate_count": candidate_count,
                    "candidate_files": candidate_files,
                    "ratings_file_sha256": sha256(path),
                    "n_source_rows": 0,
                    "n_rating_blocks": 0,
                    "selected_rating_block": "",
                    "n_selected_rows": 0,
                    **{
                        field: ""
                        for partner, trait in CELLS
                        for field in (
                            f"partner_{partner}_trait_{trait}_n",
                            f"partner_{partner}_trait_{trait}_mean",
                        )
                    },
                    "win_sum": "",
                    "loss_sum": "",
                    "identical_ratings": "",
                    "exclude_subject": "true",
                    "exclusion_reason": "empty_ratings_file",
                    "review_flags": "",
                }
            )
            continue
        try:
            result = evaluate(path)
            row = {
                "dataset": unit["dataset"],
                "subject": unit["subject"],
                "ratings_file": str(source_path(path)),
                "source_resolution": source_resolution,
                "candidate_count": candidate_count,
                "candidate_files": candidate_files,
                "ratings_file_sha256": result["ratings_file_sha256"],
                "n_source_rows": result["n_source_rows"],
                "n_rating_blocks": result["n_rating_blocks"],
                "selected_rating_block": result["selected_rating_block"],
                "n_selected_rows": result["n_selected_rows"],
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
        "source_resolution",
        "candidate_count",
        "candidate_files",
        "ratings_file_sha256",
        "n_source_rows",
        "n_rating_blocks",
        "selected_rating_block",
        "n_selected_rows",
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
        print("CHECK PASSED: the ratings cohort audit has no unresolved source/schema failures.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
