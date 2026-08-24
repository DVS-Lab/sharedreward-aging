#!/usr/bin/env python3
"""Select matched RF1/ds003745 runs for AFNI-target versus FEAT-SUSAN QC."""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_STAGE = {"rf1": "pre_resample", "ds003745": "post_resample_preblur"}
FIELDS = (
    "dataset", "subject", "session", "run", "baseline_bold", "input_mask",
    "afni_target_bold", "susan_output_bold", "susan_metadata", "baseline_qc",
    "afni_target_qc", "susan_output_qc", "kernel_fwhm_mm",
)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-manifest", required=True, type=Path)
    parser.add_argument(
        "--baseline-audit", type=Path,
        default=ROOT / "logs/records/phase0-baseline-smoothness.tsv",
    )
    parser.add_argument("--scope", choices=("pilot", "all"), default="pilot")
    parser.add_argument("--kernel-fwhm", default="6")
    parser.add_argument(
        "--rf1-sharedreward-root", type=Path,
        default=Path(os.environ.get("RF1_SHAREDREWARD_ROOT", "/ZPOOL/data/projects/rf1-sra-sharedreward")),
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--missing-output", required=True, type=Path)
    return parser.parse_args()


def read_tsv(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def key(row):
    return tuple(row[field] for field in ("dataset", "subject", "session", "run"))


def label_number(value):
    numeric = float(value)
    if numeric <= 0:
        raise ValueError("kernel FWHM must be positive")
    return f"{numeric:g}", f"{numeric:g}".replace(".", "p")


def owner_root(dataset, rf1_root):
    return rf1_root if dataset == "rf1" else ROOT


def main():
    args = parse_args()
    if not args.target_manifest.is_file() or not args.baseline_audit.is_file():
        raise SystemExit("ERROR: target manifest and baseline audit are required")
    try:
        kernel, kernel_label = label_number(args.kernel_fwhm)
    except ValueError as error:
        raise SystemExit(f"ERROR: {error}") from error
    targets = read_tsv(args.target_manifest)
    baselines = [
        row for row in read_tsv(args.baseline_audit)
        if ANALYSIS_STAGE.get(row.get("dataset")) == row.get("stage")
    ]
    baseline_by_key = {key(row): row for row in baselines}
    candidates = []
    for target in targets:
        baseline = baseline_by_key.get(key(target))
        if baseline is None:
            continue
        if Path(target["input_bold"]).resolve() != Path(baseline["input_bold"]).resolve():
            raise SystemExit(f"ERROR: baseline input contract mismatch: {key(target)}")
        candidates.append((target, baseline))
    if args.scope == "pilot":
        selected = []
        for dataset in sorted(ANALYSIS_STAGE):
            subset = [pair for pair in candidates if pair[0]["dataset"] == dataset]
            if not subset:
                raise SystemExit(f"ERROR: no comparison candidates for {dataset}")
            selected.append(max(subset, key=lambda pair: float(pair[1]["classic_fwhm_combined"])))
    else:
        selected = candidates

    ready, missing = [], []
    for target, baseline in selected:
        identifiers = {field: target[field] for field in FIELDS[:4]}
        required = {
            "baseline_bold": Path(target["input_bold"]),
            "input_mask": Path(target["input_mask"]),
            "afni_target_bold": Path(target["output_bold"]),
        }
        problems = [name for name, path in required.items() if not path.is_file() or path.stat().st_size == 0]
        if problems:
            missing.append({**identifiers, "missing": ",".join(problems)})
            continue
        owner = owner_root(target["dataset"], args.rf1_sharedreward_root)
        afni_name = Path(target["output_bold"]).name
        target_label = f"{float(target['target_fwhm_mm']):g}".replace(".", "p")
        target_token = f"smoothToFWHM{target_label}"
        susan_name = afni_name.replace(target_token, f"susanKernelFWHM{kernel_label}")
        if susan_name == afni_name:
            raise SystemExit(f"ERROR: AFNI target label not found in output: {afni_name}")
        session_dir = f"ses-{target['session']}" if target["session"] else ""
        parts = [owner, "derivatives/smoothing-validation", f"sub-{target['subject']}"]
        if session_dir:
            parts.append(session_dir)
        susan_output = Path(*map(str, parts)) / "func" / susan_name
        unit = "_".join(
            filter(None, [target["dataset"], f"sub-{target['subject']}", session_dir, f"run-{target['run']}"])
        )
        qc_root = ROOT / "derivatives/qc/smoothing-method-comparison"
        ready.append({
            **identifiers,
            "baseline_bold": str(required["baseline_bold"].resolve()),
            "input_mask": str(required["input_mask"].resolve()),
            "afni_target_bold": str(required["afni_target_bold"].resolve()),
            "susan_output_bold": str(susan_output.resolve()),
            "susan_metadata": str(susan_output.resolve()).removesuffix(".nii.gz") + "_susan.tsv",
            "baseline_qc": str((qc_root / f"{unit}_method-baseline.tsv").resolve()),
            "afni_target_qc": str((qc_root / f"{unit}_method-afniTarget.tsv").resolve()),
            "susan_output_qc": str((qc_root / f"{unit}_method-susanKernel.tsv").resolve()),
            "kernel_fwhm_mm": kernel,
        })
    ready.sort(key=key); missing.sort(key=key)
    write_tsv(args.output, FIELDS, ready)
    write_tsv(args.missing_output, FIELDS[:4] + ("missing",), missing)
    print(f"Comparison scope: {args.scope}")
    print(f"SUSAN nominal kernel FWHM: {kernel} mm")
    print(f"Ready comparison units: {len(ready)}")
    for row in ready:
        baseline = baseline_by_key[key(row)]
        print(f"  {row['dataset']} sub-{row['subject']} ses-{row['session'] or 'none'} run-{row['run']}: baseline classic={baseline['classic_fwhm_combined']} mm")
    print(f"Incomplete comparison units: {len(missing)}")
    print(f"Ready manifest: {args.output.resolve()}")
    print(f"Missing report: {args.missing_output.resolve()}")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
