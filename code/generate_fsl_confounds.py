#!/usr/bin/env python3
"""Create one headerless FSL matrix matching the RF1 base-confound policy."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path


BASE_COLUMNS = (
    "a_comp_cor_00",
    "a_comp_cor_01",
    "a_comp_cor_02",
    "a_comp_cor_03",
    "a_comp_cor_04",
    "a_comp_cor_05",
    "trans_x",
    "trans_y",
    "trans_z",
    "rot_x",
    "rot_y",
    "rot_z",
    "framewise_displacement",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(input_path: Path) -> tuple[list[str], list[list[float]]]:
    with input_path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = reader.fieldnames or []
        source = list(reader)
    if not source:
        raise ValueError("named fMRIPrep confounds table has no data rows")
    selected = [column for column in BASE_COLUMNS if column in fields]
    selected.extend(column for column in fields if column.startswith("cosine"))
    selected.extend(
        column for column in fields if column.startswith("non_steady_state")
    )
    missing_base = [column for column in BASE_COLUMNS if column not in fields]
    if missing_base:
        raise ValueError("missing required base columns: " + ",".join(missing_base))
    matrix = []
    for row_number, row in enumerate(source, 2):
        values = []
        for column in selected:
            raw = row[column].strip()
            if not raw or raw.lower() in {"n/a", "na", "nan"}:
                value = 0.0
            else:
                try:
                    value = float(raw)
                except ValueError as error:
                    raise ValueError(
                        f"row {row_number} column {column} is not numeric: {raw!r}"
                    ) from error
                if not math.isfinite(value):
                    value = 0.0
            values.append(value)
        matrix.append(values)
    return selected, matrix


def atomic_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w") as handle:
            handle.write(text)
        Path(temporary).replace(path)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--metadata", required=True, type=Path)
    args = parser.parse_args()
    selected, matrix = build(args.input)
    lines = ["\t".join(format(value, ".17g") for value in row) for row in matrix]
    atomic_text(args.output, "\n".join(lines) + "\n")
    metadata = {
        "Description": "Headerless nuisance matrix for FSL FEAT.",
        "Source": str(args.input.resolve()),
        "SourceSHA256": sha256(args.input),
        "Rows": len(matrix),
        "Columns": len(selected),
        "ColumnNamesInOrder": selected,
        "SelectionPolicy": (
            "RF1 genTedanaConfounds.py base fMRIPrep columns plus cosine and "
            "non-steady-state regressors; rejected TEDANA ICA components are "
            "not applicable to single-echo ds003745."
        ),
        "MissingOrNonFiniteValues": "replaced with zero",
    }
    atomic_text(args.metadata, json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    print(
        f"Wrote {len(matrix)} x {len(selected)} FSL nuisance matrix: "
        f"{args.output.resolve()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
