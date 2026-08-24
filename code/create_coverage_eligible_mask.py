#!/usr/bin/env python3
"""Create the RF1-grid historical coverage exemption and eligible mask."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template-mask", required=True, type=Path)
    parser.add_argument("--exemption-mask", required=True, type=Path)
    parser.add_argument("--reference-grid", required=True, type=Path)
    parser.add_argument("--resampled-exemption-output", required=True, type=Path)
    parser.add_argument("--eligible-mask-output", required=True, type=Path)
    parser.add_argument("--json-output", required=True, type=Path)
    return parser.parse_args()


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def nearest_resample(source, reference, np):
    source_data = np.asanyarray(source.dataobj) > 0
    target_shape = tuple(reference.shape[:3])
    target_indices = np.indices(target_shape, dtype=np.float64).reshape(3, -1)
    homogeneous = np.vstack(
        (target_indices, np.ones((1, target_indices.shape[1]), dtype=np.float64))
    )
    source_indices = np.rint(
        np.linalg.inv(source.affine) @ (reference.affine @ homogeneous)
    ).astype(int)[:3]
    valid = np.ones(source_indices.shape[1], dtype=bool)
    for axis, size in enumerate(source.shape):
        valid &= (source_indices[axis] >= 0) & (source_indices[axis] < size)
    output = np.zeros(source_indices.shape[1], dtype=bool)
    output[valid] = source_data[
        source_indices[0, valid],
        source_indices[1, valid],
        source_indices[2, valid],
    ]
    return output.reshape(target_shape)


def save_mask(path, data, reference, nib, np):
    header = reference.header.copy()
    header.set_data_dtype(np.uint8)
    image = nib.Nifti1Image(data.astype(np.uint8), reference.affine, header)
    qform, qcode = reference.get_qform(coded=True)
    sform, scode = reference.get_sform(coded=True)
    image.set_qform(qform, int(qcode))
    image.set_sform(sform, int(scode))
    path.parent.mkdir(parents=True, exist_ok=True)
    nib.save(image, str(path))


def world_extent(data, affine, np):
    indices = np.argwhere(data)
    homogeneous = np.column_stack((indices, np.ones(len(indices))))
    world = (affine @ homogeneous.T).T[:, :3]
    return {
        "minimum_mm": [float(value) for value in world.min(axis=0)],
        "maximum_mm": [float(value) for value in world.max(axis=0)],
    }


def main():
    args = parse_args()
    try:
        import nibabel as nib
        import numpy as np
    except ImportError as error:
        raise SystemExit(f"ERROR: nibabel and numpy are required: {error}") from error

    for path, label in (
        (args.template_mask, "template mask"),
        (args.exemption_mask, "historical exemption mask"),
        (args.reference_grid, "reference grid"),
    ):
        if not path.is_file() or path.stat().st_size == 0:
            raise SystemExit(f"ERROR: {label} not found or empty: {path}")
    template = nib.load(str(args.template_mask), mmap=True)
    exemption = nib.load(str(args.exemption_mask), mmap=True)
    reference = nib.load(str(args.reference_grid), mmap=True)
    if template.ndim != 3 or exemption.ndim != 3 or reference.ndim not in (3, 4):
        raise SystemExit("ERROR: masks must be 3D and the reference grid 3D or 4D")
    if tuple(template.shape) != tuple(reference.shape[:3]) or not np.allclose(
        template.affine, reference.affine, rtol=0.0, atol=1e-5
    ):
        raise SystemExit("ERROR: template mask does not match the reference grid")

    template_data = np.asanyarray(template.dataobj) > 0
    exemption_data = nearest_resample(exemption, reference, np)
    exemption_inside_template = exemption_data & template_data
    eligible_data = template_data & ~exemption_inside_template
    if not np.any(exemption_inside_template):
        raise SystemExit("ERROR: resampled exemption does not overlap the template mask")
    if not np.any(eligible_data):
        raise SystemExit("ERROR: coverage-eligible mask is empty")

    save_mask(args.resampled_exemption_output, exemption_data, reference, nib, np)
    save_mask(args.eligible_mask_output, eligible_data, reference, nib, np)
    qform, qcode = reference.get_qform(coded=True)
    sform, scode = reference.get_sform(coded=True)
    metadata = {
        "description": (
            "Coverage-eligible denominator preserving the historical Shared Reward "
            "cerebellum/posterior-brainstem exemption. Formula: RF1-grid TemplateFlow "
            "brain mask AND NOT nearest-neighbor-resampled historical exemption mask."
        ),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "template_mask": str(args.template_mask.resolve()),
        "template_mask_sha256": sha256(args.template_mask),
        "historical_exemption_mask": str(args.exemption_mask.resolve()),
        "historical_exemption_mask_sha256": sha256(args.exemption_mask),
        "reference_grid": str(args.reference_grid.resolve()),
        "reference_grid_sha256": sha256(args.reference_grid),
        "resampled_exemption_mask": str(args.resampled_exemption_output.resolve()),
        "resampled_exemption_mask_sha256": sha256(args.resampled_exemption_output),
        "eligible_coverage_mask": str(args.eligible_mask_output.resolve()),
        "eligible_coverage_mask_sha256": sha256(args.eligible_mask_output),
        "shape": list(reference.shape[:3]),
        "zooms_mm": [float(value) for value in reference.header.get_zooms()[:3]],
        "affine": reference.affine.tolist(),
        "qform_code": int(qcode),
        "sform_code": int(scode),
        "template_mask_voxels": int(template_data.sum()),
        "resampled_exemption_voxels": int(exemption_data.sum()),
        "exemption_inside_template_voxels": int(exemption_inside_template.sum()),
        "eligible_coverage_voxels": int(eligible_data.sum()),
        "resampled_exemption_world_extent": world_extent(
            exemption_data, reference.affine, np
        ),
        "interpolation": "nearest-neighbor",
        "coverage_formula": "run_mask_intersection_eligible_mask / eligible_mask",
        "tsnr_mask_policy": (
            "The full TemplateFlow mask remains the fixed tSNR reference; this "
            "eligible mask is used only for historical coverage comparability."
        ),
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Template mask voxels: {metadata['template_mask_voxels']}")
    print(
        "Exemption voxels inside template: "
        f"{metadata['exemption_inside_template_voxels']}"
    )
    print(f"Coverage-eligible voxels: {metadata['eligible_coverage_voxels']}")
    print(f"Resampled exemption: {args.resampled_exemption_output.resolve()}")
    print(f"Eligible coverage mask: {args.eligible_mask_output.resolve()}")
    print(f"Metadata: {args.json_output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
