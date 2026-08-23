#!/usr/bin/env python3
"""Audit ds003745 harmonized BOLD/mask outputs against the RF1 reference grid."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np


REQUIRED_FIELDS = ("subject", "run", "output_bold", "output_mask")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--affine-atol", type=float, default=1e-5)
    parser.add_argument("--fail-on-incomplete", action="store_true")
    return parser.parse_args()


def grid_problems(reference, image, nib, atol):
    problems = []
    if reference.shape[:3] != image.shape[:3]:
        problems.append("shape")
    if not np.allclose(
        reference.header.get_zooms()[:3],
        image.header.get_zooms()[:3],
        rtol=0.0,
        atol=atol,
    ):
        problems.append("voxel_sizes")
    if not np.allclose(reference.affine, image.affine, rtol=0.0, atol=atol):
        problems.append("affine")
    if nib.aff2axcodes(reference.affine) != nib.aff2axcodes(image.affine):
        problems.append("orientation")
    return problems


def main():
    args = parse_args()
    if args.affine_atol <= 0:
        raise SystemExit("ERROR: --affine-atol must be positive")
    try:
        import nibabel as nib
    except ImportError as error:
        raise SystemExit(f"ERROR: nibabel is required: {error}") from error

    if not args.reference.is_file():
        raise SystemExit(f"ERROR: reference grid not found: {args.reference}")
    reference = nib.load(args.reference, mmap=True)
    with args.manifest.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if not reader.fieldnames or not set(REQUIRED_FIELDS).issubset(
            reader.fieldnames
        ):
            raise SystemExit(
                "ERROR: manifest lacks required columns: "
                + ",".join(REQUIRED_FIELDS)
            )
        manifest_rows = list(reader)
    if not manifest_rows:
        raise SystemExit("ERROR: manifest contains no run units")

    audit_rows = []
    for row in manifest_rows:
        problems = []
        for kind in ("bold", "mask"):
            path = Path(row[f"output_{kind}"])
            if not path.is_file() or path.stat().st_size == 0:
                problems.append(f"missing_{kind}")
                continue
            try:
                image = nib.load(path, mmap=True)
                if kind == "bold" and image.ndim != 4:
                    problems.append("bold_not_4d")
                if kind == "mask" and image.ndim != 3:
                    problems.append("mask_not_3d")
                problems.extend(
                    f"{kind}_{problem}"
                    for problem in grid_problems(
                        reference, image, nib, args.affine_atol
                    )
                )
            except (OSError, ValueError) as error:
                problems.append(f"unreadable_{kind}:{error}")
        audit_rows.append(
            {
                "subject": row["subject"],
                "run": row["run"],
                "status": "complete" if not problems else "incomplete",
                "problems": ",".join(problems),
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("subject", "run", "status", "problems"),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(audit_rows)

    incomplete = [row for row in audit_rows if row["status"] != "complete"]
    print(f"Run units checked: {len(audit_rows)}")
    print(f"Complete run units: {len(audit_rows) - len(incomplete)}")
    print(f"Incomplete run units: {len(incomplete)}")
    print(f"Audit: {args.output.resolve()}")
    for row in incomplete:
        print(
            f"INCOMPLETE sub-{row['subject']} run-{row['run']}: "
            f"{row['problems']}"
        )
    if args.fail_on_incomplete and incomplete:
        return 1
    if not incomplete:
        print(
            "CHECK PASSED: every harmonized ds003745 BOLD and mask "
            "matches the RF1 grid."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
