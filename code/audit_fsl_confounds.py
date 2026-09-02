#!/usr/bin/env python3
"""Audit ds003745 headerless FSL nuisance matrices against BOLD volumes."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


FIELDS = ("dataset", "subject", "session", "run", "rows", "columns", "problems")


def matrix_shape(path: Path) -> tuple[int, int]:
    rows = []
    with path.open(newline="") as handle:
        for row_number, row in enumerate(csv.reader(handle, delimiter="\t"), 1):
            if not row:
                raise ValueError(f"empty row {row_number}")
            values = [float(value) for value in row]
            if not all(math.isfinite(value) for value in values):
                raise ValueError(f"non-finite value in row {row_number}")
            rows.append(values)
    if not rows or len({len(row) for row in rows}) != 1:
        raise ValueError("empty or ragged matrix")
    return len(rows), len(rows[0])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--fail-on-incomplete", action="store_true")
    args = parser.parse_args()
    try:
        import nibabel as nib
    except ImportError as error:
        raise SystemExit(f"ERROR: nibabel is required: {error}") from error
    with args.manifest.open(newline="") as handle:
        manifest = list(csv.DictReader(handle, delimiter="\t"))
    complete, report = 0, []
    for unit in manifest:
        identifiers = {field: unit[field] for field in FIELDS[:4]}
        problems = []
        rows = columns = 0
        try:
            matrix = Path(unit["output_confounds"])
            metadata_path = Path(unit["output_metadata"])
            rows, columns = matrix_shape(matrix)
            volumes = nib.load(unit["input_bold"], mmap=True).shape[3]
            metadata = json.loads(metadata_path.read_text())
            if rows != volumes:
                problems.append(f"rows_{rows}_ne_volumes_{volumes}")
            if int(metadata["Rows"]) != rows or int(metadata["Columns"]) != columns:
                problems.append("metadata_shape_mismatch")
            if metadata["Source"] != str(Path(unit["input_confounds"]).resolve()):
                problems.append("metadata_source_mismatch")
        except (IndexError, KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
            problems.append(f"invalid_output:{error}")
        if not problems:
            complete += 1
        report.append(
            {**identifiers, "rows": rows, "columns": columns, "problems": ";".join(problems)}
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(report)
    incomplete = len(manifest) - complete
    print(f"FSL nuisance units checked: {len(manifest)}")
    print(f"Complete units: {complete}")
    print(f"Incomplete units: {incomplete}")
    print(f"Audit: {args.output.resolve()}")
    if not incomplete:
        print("CHECK PASSED: every ds003745 FSL nuisance matrix is numeric and volume-aligned.")
    return 1 if args.fail_on_incomplete and incomplete else 0


if __name__ == "__main__":
    raise SystemExit(main())
