#!/usr/bin/env python3
"""Consolidate and audit Phase 0 run-level baseline smoothness results."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_FIELDS = (
    "classic_fwhm_x",
    "classic_fwhm_y",
    "classic_fwhm_z",
    "classic_fwhm_combined",
    "acf_a",
    "acf_b",
    "acf_c",
    "acf_effective_fwhm",
    "afni_version",
)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument(
        "--result-dir",
        type=Path,
        default=ROOT / "derivatives/qc/smoothness/run-level",
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--missing-output", required=True, type=Path)
    parser.add_argument("--fail-on-incomplete", action="store_true")
    return parser.parse_args()


def unit_label(row):
    session = f"_ses-{row['session']}" if row["session"] else ""
    return (
        f"{row['dataset']}_sub-{row['subject']}{session}_run-{row['run']}_"
        f"stage-{row['stage']}"
    )


def write_tsv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    args = parse_args()
    try:
        import nibabel as nib
    except ImportError as error:
        raise SystemExit(f"ERROR: nibabel is required: {error}") from error
    with args.manifest.open(newline="") as handle:
        manifest = list(csv.DictReader(handle, delimiter="\t"))
    required = {
        "dataset",
        "subject",
        "session",
        "run",
        "stage",
        "input_bold",
        "input_mask",
    }
    if not manifest or not required.issubset(manifest[0]):
        raise SystemExit(
            "ERROR: characterization manifest lacks required columns: "
            + ",".join(sorted(required))
        )

    complete = []
    missing = []
    for row in manifest:
        label = unit_label(row)
        result_path = args.result_dir / f"{label}.tsv"
        problems = []
        result = None
        if not result_path.is_file() or result_path.stat().st_size == 0:
            problems.append("missing_result")
        else:
            try:
                with result_path.open(newline="") as handle:
                    results = list(csv.DictReader(handle, delimiter="\t"))
                if len(results) != 1:
                    problems.append(f"result_rows={len(results)}")
                else:
                    result = results[0]
                    if Path(result.get("input", "")).resolve() != Path(
                        row["input_bold"]
                    ).resolve():
                        problems.append("input_contract")
                    if Path(result.get("mask", "")).resolve() != Path(
                        row["input_mask"]
                    ).resolve():
                        problems.append("mask_contract")
                    for field in RESULT_FIELDS[:-1]:
                        if float(result[field]) <= 0:
                            problems.append(f"nonpositive_{field}")
            except (KeyError, OSError, TypeError, ValueError) as error:
                problems.append(f"invalid_result:{error}")

        header = None
        if not problems:
            try:
                header = nib.load(row["input_bold"], mmap=True)
                if header.ndim != 4:
                    problems.append("input_not_4d")
            except (OSError, ValueError) as error:
                problems.append(f"unreadable_input:{error}")

        identifiers = {
            field: row[field]
            for field in ("dataset", "subject", "session", "run", "stage")
        }
        if problems:
            missing.append({**identifiers, "problems": ",".join(problems)})
            continue
        zooms = header.header.get_zooms()
        complete.append(
            {
                **identifiers,
                "input_bold": str(Path(row["input_bold"]).resolve()),
                "input_mask": str(Path(row["input_mask"]).resolve()),
                "voxel_size_x": f"{zooms[0]:.8g}",
                "voxel_size_y": f"{zooms[1]:.8g}",
                "voxel_size_z": f"{zooms[2]:.8g}",
                "n_volumes": str(header.shape[3]),
                "tr_seconds": f"{zooms[3]:.8g}",
                **{field: result[field] for field in RESULT_FIELDS},
            }
        )

    complete_fields = (
        "dataset",
        "subject",
        "session",
        "run",
        "stage",
        "input_bold",
        "input_mask",
        "voxel_size_x",
        "voxel_size_y",
        "voxel_size_z",
        "n_volumes",
        "tr_seconds",
    ) + RESULT_FIELDS
    write_tsv(args.output, complete_fields, complete)
    write_tsv(
        args.missing_output,
        ("dataset", "subject", "session", "run", "stage", "problems"),
        missing,
    )
    counts = Counter((row["dataset"], row["stage"]) for row in complete)
    print(f"Smoothness units checked: {len(manifest)}")
    print(f"Complete smoothness units: {len(complete)}")
    for (dataset, stage), count in sorted(counts.items()):
        print(f"  {dataset} {stage}: {count}")
    print(f"Incomplete smoothness units: {len(missing)}")
    print(f"Consolidated table: {args.output.resolve()}")
    print(f"Missing report: {args.missing_output.resolve()}")
    for row in missing[:20]:
        print(
            f"INCOMPLETE {row['dataset']} sub-{row['subject']} "
            f"ses-{row['session'] or 'none'} run-{row['run']} "
            f"{row['stage']}: {row['problems']}"
        )
    if args.fail_on_incomplete and missing:
        return 1
    if not missing:
        print("CHECK PASSED: all baseline smoothness results are complete and valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
