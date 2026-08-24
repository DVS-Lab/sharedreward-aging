#!/usr/bin/env python3
"""Resample a standard-space brain mask onto the exact RF1 analysis grid."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-mask", required=True, type=Path)
    parser.add_argument("--reference-grid", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--json-output", required=True, type=Path)
    return parser.parse_args()


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    args = parse_args()
    try:
        import nibabel as nib
        import numpy as np
    except ImportError as error:
        raise SystemExit(f"ERROR: nibabel and numpy are required: {error}") from error

    source = nib.load(str(args.source_mask), mmap=True)
    reference = nib.load(str(args.reference_grid), mmap=True)
    if source.ndim != 3:
        raise SystemExit(f"ERROR: source mask must be 3D: {args.source_mask}")
    if reference.ndim not in (3, 4):
        raise SystemExit(f"ERROR: reference grid must be 3D or 4D: {args.reference_grid}")
    source_data = np.asanyarray(source.dataobj) > 0
    if not np.any(source_data):
        raise SystemExit("ERROR: source mask is empty")

    target_shape = tuple(reference.shape[:3])
    target_indices = np.indices(target_shape, dtype=np.float64).reshape(3, -1)
    target_homogeneous = np.vstack(
        (target_indices, np.ones((1, target_indices.shape[1]), dtype=np.float64))
    )
    world = reference.affine @ target_homogeneous
    source_indices = np.rint(np.linalg.inv(source.affine) @ world).astype(int)[:3]
    valid = np.ones(source_indices.shape[1], dtype=bool)
    for axis, size in enumerate(source.shape):
        valid &= (source_indices[axis] >= 0) & (source_indices[axis] < size)
    output_flat = np.zeros(source_indices.shape[1], dtype=np.uint8)
    output_flat[valid] = source_data[
        source_indices[0, valid],
        source_indices[1, valid],
        source_indices[2, valid],
    ]
    output_data = output_flat.reshape(target_shape)
    if not np.any(output_data):
        raise SystemExit("ERROR: resampled common analysis mask is empty")

    header = reference.header.copy()
    header.set_data_dtype(np.uint8)
    image = nib.Nifti1Image(output_data, reference.affine, header)
    qform, qcode = reference.get_qform(coded=True)
    sform, scode = reference.get_sform(coded=True)
    image.set_qform(qform, int(qcode))
    image.set_sform(sform, int(scode))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    nib.save(image, str(args.output))

    metadata = {
        "description": (
            "TemplateFlow MNI152NLin6Asym brain mask resampled by nearest-neighbor "
            "index mapping to the authoritative RF1 analysis grid."
        ),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_mask": str(args.source_mask.resolve()),
        "source_mask_sha256": sha256(args.source_mask),
        "reference_grid": str(args.reference_grid.resolve()),
        "reference_grid_sha256": sha256(args.reference_grid),
        "output": str(args.output.resolve()),
        "output_sha256": sha256(args.output),
        "shape": list(target_shape),
        "zooms_mm": [float(value) for value in reference.header.get_zooms()[:3]],
        "affine": reference.affine.tolist(),
        "qform_code": int(qcode),
        "sform_code": int(scode),
        "mask_voxels": int(output_data.sum()),
        "interpolation": "nearest-neighbor",
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Common analysis mask voxels: {metadata['mask_voxels']}")
    print(f"Mask: {args.output.resolve()}")
    print(f"Metadata: {args.json_output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
