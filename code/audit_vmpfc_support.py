#!/usr/bin/env python3
"""Read-only attribution of vmPFC coverage loss in existing L3 model inputs.

Uses original participant mask/VARCOPE paths, NOT common-mask FEAT adapters.
Does not fit a model, change masks, or create exclusion recommendations.
"""
import argparse
import json
from pathlib import Path

import nibabel as nib
from nibabel.processing import resample_from_to
import numpy as np
import pandas as pd

from run_preliminary_age import ROOT, KEY, ROI_FILES, require, image_values, sha, save_json, plt


def audit_model(folder, reference, roi, map_dir):
    table = folder / "ordered-inputs.tsv"
    rows = pd.read_csv(table, sep="\t", dtype=str, keep_default_na=False)
    require(len(rows) > 1, f"Insufficient participants: {table}")
    require(not rows.duplicated(KEY).any(), f"Duplicate participants: {table}")
    require(roi.any(), "Empty vmPFC ROI")
    # Reject adapters explicitly: these have already been restricted to common support.
    for column in ("mask_path", "varcope_path"):
        for path in rows[column]:
            require("inputs" not in Path(path).parts, f"Use original inputs, not adapter: {path}")
    counters = {}
    roi_masks, roi_supports, records, fingerprints = [], [], [], []
    for row in rows.to_dict("records"):
        paths = [Path(row[k]) for k in ("mask_path", "varcope_path")]
        before = [sha(path) for path in paths]
        mask = image_values(paths[0], reference) > 0
        var = image_values(paths[1], reference)
        require(mask.any(), f"Empty original mask: {paths[0]}")
        require((var[mask] >= 0).all(), f"Negative VARCOPE inside original mask: {paths[1]}")
        support = mask & (var > 0)
        require(before == [sha(path) for path in paths], f"Input changed while reading: {paths}")
        fingerprints.extend(dict(path=str(path), sha256=digest) for path, digest in zip(paths, before))
        for group in ("pooled", row["dataset"]):
            require(group in ("pooled", "rf1", "ds003745"), f"Unexpected dataset: {group}")
            if group not in counters:
                counters[group] = [0, np.zeros(mask.shape, dtype=np.uint32), np.zeros(mask.shape, dtype=np.uint32)]
            counters[group][0] += 1
            counters[group][1] += mask
            counters[group][2] += support
        rm, rs = mask[roi], support[roi]
        roi_masks.append(rm); roi_supports.append(rs)
        record = {key: row.get(key, "") for key in (*KEY, "runs", "strategy", "cope", "mask_path", "varcope_path")}
        record.update(model=folder.name, full_roi_voxels=int(roi.sum()),
                      mask_roi_voxels=int(rm.sum()), supported_roi_voxels=int(rs.sum()),
                      mask_coverage_pct=float(100*rm.mean()), supported_coverage_pct=float(100*rs.mean()),
                      additional_zero_variance_roi_voxels=int((rm & ~rs).sum()))
        records.append(record)
    n, mask_count, support_count = counters["pooled"]
    directory, effective = mask_count == n, support_count == n
    for filename, expected in (("directory-mask.nii.gz", directory), ("analysis-mask.nii.gz", effective)):
        actual = image_values(folder / filename, reference) > 0
        require(np.array_equal(actual, expected), f"Original inputs do not reproduce saved {filename}: {folder}")
    for values, field in ((np.array(roi_masks), "mask"), (np.array(roi_supports), "support")):
        missing_count = (~values).sum(axis=0)
        for index, record in enumerate(records):
            # Descriptive attribution only: voxels regained if this participant alone were omitted.
            record[f"unique_{field}_loss_voxels"] = int(((~values[index]) & (missing_count == 1)).sum())
    map_dir.mkdir(parents=True)
    nib.save(nib.Nifti1Image(roi.astype(np.uint8), reference.affine), map_dir / "vmpfc-roi.nii.gz")
    summaries = []
    for group, (count, mc, sc) in counters.items():
        for name, array in (("mask-frequency", mc/count), ("support-frequency", sc/count)):
            nib.save(nib.Nifti1Image(array.astype(np.float32), reference.affine), map_dir / f"{group}_{name}.nii.gz")
        subset = [r for r in records if group == "pooled" or r["dataset"] == group]
        summary = dict(model=folder.name, dataset=group, participants=count,
                       full_roi_voxels=int(roi.sum()), common_mask_roi_voxels=int(((mc == count) & roi).sum()),
                       common_support_roi_voxels=int(((sc == count) & roi).sum()),
                       additional_variance_loss_roi_voxels=int(((mc == count) & (sc < count) & roi).sum()))
        for field in ("mask", "supported"):
            values = [r[f"{field}_coverage_pct"] for r in subset]
            for label, func in (("min", np.min), ("median", np.median), ("max", np.max)):
                summary[f"individual_{field}_{label}_pct"] = float(func(values))
        summaries.append(summary)
    return records, summaries, dict(ordered_inputs_sha256=sha(table), inputs=fingerprints,
                                    saved_masks={f: sha(folder/f) for f in ("directory-mask.nii.gz", "analysis-mask.nii.gz")})


def plot_summary(summary, destination):
    pooled = summary[summary.dataset.eq("pooled")]
    y = np.arange(len(pooled))
    fig, axes = plt.subplots(1, 2, figsize=(13, max(4, .4*len(pooled)+2)), sharey=True)
    for ax, field, title in zip(axes, ("mask", "supported"), ("Original directory mask", "Mask AND positive VARCOPE")):
        common = "mask" if field == "mask" else "support"
        ax.barh(y, 100*pooled[f"common_{common}_roi_voxels"]/pooled.full_roi_voxels,
                color="#437a9f", label="All-participant intersection")
        ax.plot(pooled[f"individual_{field}_median_pct"], y, "o", color="#d26935", label="Participant median")
        ax.set_xlim(0, 101); ax.set_xlabel("Full anatomical vmPFC ROI covered (%)")
        ax.set_title(title); ax.legend(loc="lower left", fontsize=8)
    axes[0].set_yticks(y, pooled.model); axes[0].invert_yaxis()
    fig.suptitle("Coverage diagnostic only — no new exclusions")
    fig.tight_layout(); fig.savefig(destination, dpi=160); plt.close(fig)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--analysis-root", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path, help="New tracked text/plot report directory")
    p.add_argument("--map-dir", required=True, type=Path, help="New ignored derivatives directory for frequency NIfTIs")
    p.add_argument("--model", action="append", help="Optional model directory name; repeatable; default all")
    p.add_argument("--roi", type=Path, default=ROI_FILES["vmPFC"])
    p.add_argument("--reference", type=Path, default=ROOT.parent / "rf1-sra-sharedreward/resources/rf1_MNI152NLin6Asym_reference_grid.nii.gz")
    args = p.parse_args()
    folders = sorted(path.parent for path in args.analysis_root.glob("*/ordered-inputs.tsv"))
    if args.model:
        require(set(args.model) <= {f.name for f in folders}, "Requested model not found")
        folders = [f for f in folders if f.name in args.model]
    require(folders, "No original ordered-inputs.tsv files found")
    require(not args.output_dir.exists() and not args.map_dir.exists(), "Use fresh report/map directories")
    reference = nib.load(args.reference)
    original_roi = nib.load(args.roi)
    require(np.isfinite(original_roi.get_fdata()).all(), "Nonfinite ROI")
    roi = resample_from_to(original_roi, (reference.shape[:3], reference.affine), order=0).get_fdata() > 0
    args.output_dir.mkdir(parents=True); args.map_dir.mkdir(parents=True)
    provenance = dict(script_sha256=sha(__file__), analysis_root=str(args.analysis_root),
                      reference=dict(path=str(args.reference), sha256=sha(args.reference)),
                      roi=dict(path=str(args.roi), sha256=sha(args.roi)), interpolation="nearest-neighbor",
                      policy="Descriptive original-input coverage only; no exclusion or mask changes", models={})
    records, summaries, failures = [], [], []
    for folder in folders:
        print(f"AUDIT: {folder.name}", flush=True)
        try:
            rec, summary, fingerprints = audit_model(folder, reference, roi, args.map_dir / folder.name)
            records.extend(rec); summaries.extend(summary); provenance["models"][folder.name] = fingerprints
            print(f"VERIFIED: {folder.name}: {len(rec)} original participant inputs; saved group masks reproduced", flush=True)
        except Exception as error:
            failures.append(dict(model=folder.name, error=str(error)))
            print(f"ERROR: {folder.name}: {error}", flush=True)
    pd.DataFrame(records).to_csv(args.output_dir / "participant-coverage.tsv", sep="\t", index=False)
    summary = pd.DataFrame(summaries)
    summary.to_csv(args.output_dir / "model-coverage-summary.tsv", sep="\t", index=False)
    save_json(args.output_dir / "provenance.json", provenance)
    if len(summary): plot_summary(summary, args.output_dir / "vmpfc-coverage-summary.png")
    save_json(args.output_dir / "completion.json", dict(complete=not failures, expected_models=len(folders),
              verified_models=len(provenance["models"]), participant_model_rows=len(records), failures=failures))
    require(not failures, "Coverage diagnostic incomplete; inspect completion.json")
    print("CHECK PASSED: original masks and variance support reproduce every requested group mask. No exclusions changed.", flush=True)


if __name__ == "__main__":
    main()
