#!/usr/bin/env python3
"""
compute_psc_all_copes.py

Compute ROI percent signal change (%SC) for *all* COPEs in every first-level FEAT
directory for every subject under:

    <project_root>/derivatives/fsl/sub-*

This script is intentionally opinionated / hard-coded for reproducibility:
  - Only the ROI path is configurable.
  - Height (H) is taken from an isolated-event Vest file shipped next to this script:
        <code_dir>/single-event.mat
    We use /PPheights (preferred) or (max-min) of the isolated EV column.
  - Scaling is done on a common scale across everything:
        scale_factor_for_contrast = 100 * H / contrast_fix
    where contrast_fix enforces Mumford-style contrast normalization:
        fix = max(sum(positive weights), abs(sum(negative weights)))   (or sum of one-sided weights)

  - %SC image definition (voxelwise):
        psc = cope * scale_factor / mean_func
    ROI summary: mean PSC within ROI mask

Output:
  - CSV written to: <project_root>/derivatives/psc/psc_<roi_stem>.csv
    containing one row per (subject, feat_dir, cope/contrast).
  - JSON log of skipped items: <project_root>/derivatives/psc/psc_<roi_stem>_skipped.json

Requirements:
  - FSL available on PATH: fslmaths, fslstats
  - ROI mask in the same space as cope and mean_func images

Run (from anywhere):
  python compute_psc_all_copes.py --roi ../derivatives/rois/my_roi_mask.nii.gz
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ----------------------------
# Hard-coded project structure
# ----------------------------
SCRIPT_PATH = Path(__file__).resolve()
CODE_DIR = SCRIPT_PATH.parent
PROJECT_ROOT = CODE_DIR.parent  # .../sharedreward-aging
FSL_DIR = PROJECT_ROOT / "derivatives" / "fsl"
OUT_DIR = PROJECT_ROOT / "derivatives" / "psc"

# Isolated-event Vest file (ships with this script)
ISOLATED_EVENT_MAT = CODE_DIR / "single-event.mat"
ISOLATED_COL_1INDEXED = 1  # column in single-event.mat to use (1-based)

# ----------------------------
# Helpers
# ----------------------------
def run_cmd(cmd: List[str]) -> str:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(
            "Command failed:\n  {}\n\nSTDOUT:\n{}\n\nSTDERR:\n{}".format(
                " ".join(cmd), p.stdout, p.stderr
            )
        )
    return p.stdout.strip()

def read_vest_header_and_matrix(path: Path) -> Tuple[Dict, List[List[float]]]:
    header: Dict = {}
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()

    start = None
    for i, line in enumerate(lines):
        s = line.strip()
        if not s:
            continue
        if s == "/Matrix":
            start = i + 1
            break
        if s.startswith("/NumWaves"):
            header["NumWaves"] = int(s.split()[-1])
        elif s.startswith("/NumPoints"):
            header["NumPoints"] = int(s.split()[-1])
        elif s.startswith("/PPheights"):
            parts = s.split()
            header["PPheights"] = [float(x) for x in parts[1:]]

    if start is None:
        raise ValueError(f"Could not find /Matrix in Vest file: {path}")

    mat: List[List[float]] = []
    for line in lines[start:]:
        s = line.strip()
        if not s:
            continue
        mat.append([float(x) for x in s.split()])

    if not mat:
        raise ValueError(f"No matrix rows found in Vest file: {path}")

    return header, mat

def isolated_height_from_vest(path: Path, col_1indexed: int) -> Tuple[float, str]:
    """
    Preferred: use /PPheights[col] (Vest convention: max-min of each column).
    Fallback: compute max-min from the /Matrix.
    """
    header, mat = read_vest_header_and_matrix(path)
    num_waves = header.get("NumWaves", len(mat[0]))
    if col_1indexed < 1 or col_1indexed > num_waves:
        raise ValueError(f"isolated-col must be in [1, {num_waves}] (got {col_1indexed})")

    col = col_1indexed - 1
    pp = header.get("PPheights", None)
    if pp and len(pp) == num_waves:
        return float(pp[col]), "ppheight_header"

    vals = [row[col] for row in mat]
    return float(max(vals) - min(vals)), "range(max-min)"

def parse_design_con(design_con: Path) -> Dict:
    """
    Parse design.con for:
      - NumWaves
      - NumContrasts
      - ContrastNameN
      - weights (matrix rows)
    """
    lines = design_con.read_text(encoding="utf-8", errors="ignore").splitlines()

    num_waves = None
    num_cons = None
    names: Dict[int, str] = {}
    matrix_start = None

    for i, line in enumerate(lines):
        m = re.match(r"\s*/NumWaves\s+(\d+)", line)
        if m:
            num_waves = int(m.group(1))
        m = re.match(r"\s*/NumContrasts\s+(\d+)", line)
        if m:
            num_cons = int(m.group(1))
        m = re.match(r"\s*/ContrastName(\d+)\s+(.*)", line)
        if m:
            names[int(m.group(1))] = m.group(2).strip()
        if line.strip() == "/Matrix":
            matrix_start = i + 1
            break

    if num_waves is None or num_cons is None or matrix_start is None:
        raise ValueError(f"Could not parse NumWaves/NumContrasts//Matrix in {design_con}")

    weights: List[List[float]] = []
    for j in range(num_cons):
        row = lines[matrix_start + j].strip().split()
        if len(row) != num_waves:
            raise ValueError(
                f"Expected {num_waves} weights on row {j+1}, got {len(row)} in {design_con}"
            )
        weights.append([float(x) for x in row])

    return {"num_waves": num_waves, "num_cons": num_cons, "names": names, "weights": weights}

def contrast_fix(w: List[float]) -> float:
    """
    Mumford-style contrast fix so positive weights sum to +1 and negative sum to -1.
    Returns the divisor (e.g., [1 1 -1 -1] => 2).
    """
    pos_sum = sum(x for x in w if x > 0)
    neg_sum = abs(sum(x for x in w if x < 0))
    if pos_sum > 0 and neg_sum > 0:
        return max(pos_sum, neg_sum)
    if pos_sum > 0:
        return pos_sum
    if neg_sum > 0:
        return neg_sum
    return 1.0

def compute_roi_psc_mean(cope_img: Path, mean_img: Path, roi: Path, scale_factor: float) -> float:
    """
    Create a temporary %SC image and return mean PSC within ROI.
    """
    fd, tmp_psc = tempfile.mkstemp(suffix="_psc.nii.gz")
    os.close(fd)
    tmp_psc_path = Path(tmp_psc)
    try:
        run_cmd(["fslmaths", str(cope_img), "-mul", str(scale_factor), "-div", str(mean_img), str(tmp_psc_path)])
        out = run_cmd(["fslstats", str(tmp_psc_path), "-k", str(roi), "-M"])
        return float(out)
    finally:
        try:
            tmp_psc_path.unlink()
        except Exception:
            pass

def is_valid_feat_dir(d: Path) -> bool:
    """
    Strict validity checks to avoid processing accidental higher-level outputs:
      - mean_func.nii.gz
      - design.con
      - stats/cope*.nii.gz
    """
    if not d.is_dir():
        return False
    if not (d / "mean_func.nii.gz").exists():
        return False
    if not (d / "design.con").exists():
        return False
    stats = d / "stats"
    if not stats.exists():
        return False
    return any(stats.glob("cope*.nii*"))

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--roi", required=True, help="ROI mask NIfTI path. Relative paths resolve relative to code/ directory.")
    args = ap.parse_args()

    if not FSL_DIR.exists():
        raise FileNotFoundError(f"Could not find derivatives/fsl at: {FSL_DIR}")

    if not ISOLATED_EVENT_MAT.exists():
        raise FileNotFoundError(
            f"Expected isolated-event Vest file next to script: {ISOLATED_EVENT_MAT}\n"
            "Place single-event.mat in the code/ directory alongside this script."
        )

    roi_path = Path(args.roi)
    if not roi_path.is_absolute():
        roi_path = (CODE_DIR / roi_path).resolve()
    if not roi_path.exists():
        raise FileNotFoundError(f"ROI not found: {roi_path}")

    H, H_src = isolated_height_from_vest(ISOLATED_EVENT_MAT, ISOLATED_COL_1INDEXED)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUT_DIR / f"psc_{roi_path.stem}.csv"
    skip_json = OUT_DIR / f"psc_{roi_path.stem}_skipped.json"

    rows: List[Dict] = []
    skipped: List[Dict] = []

    for sub_dir in sorted(FSL_DIR.glob("sub-*")):
        if not sub_dir.is_dir():
            continue
        subj = sub_dir.name

        feat_dirs = sorted([p for p in sub_dir.rglob("*.feat") if is_valid_feat_dir(p)])
        if not feat_dirs:
            skipped.append({"subject": subj, "reason": "no_valid_feat_dirs"})
            continue

        for feat_dir in feat_dirs:
            design_con = feat_dir / "design.con"
            mean_img = feat_dir / "mean_func.nii.gz"
            stats_dir = feat_dir / "stats"

            try:
                con = parse_design_con(design_con)
            except Exception as e:
                skipped.append({"subject": subj, "feat": str(feat_dir), "reason": f"design.con_parse_error: {e}"})
                continue

            num_cons = con["num_cons"]

            for c in range(1, num_cons + 1):
                cope_img = stats_dir / f"cope{c}.nii.gz"
                if not cope_img.exists():
                    skipped.append({"subject": subj, "feat": str(feat_dir), "cope": c, "reason": "cope_missing"})
                    continue

                w = con["weights"][c - 1]
                cfix = contrast_fix(w)
                scale_factor = 100.0 * H / cfix

                try:
                    psc_mean = compute_roi_psc_mean(cope_img, mean_img, roi_path, scale_factor)
                except Exception as e:
                    skipped.append({"subject": subj, "feat": str(feat_dir), "cope": c, "reason": f"psc_error: {e}"})
                    continue

                feat_rel = str(feat_dir.relative_to(PROJECT_ROOT)) if PROJECT_ROOT in feat_dir.parents else str(feat_dir)
                roi_rel = str(roi_path.relative_to(PROJECT_ROOT)) if PROJECT_ROOT in roi_path.parents else str(roi_path)

                rows.append({
                    "subject": subj,
                    "feat_relpath": feat_rel,
                    "cope_idx": c,
                    "contrast_name": con["names"].get(c, ""),
                    "contrast_fix": cfix,
                    "H_common": H,
                    "H_source": H_src,
                    "scale_factor": scale_factor,
                    "psc_mean": psc_mean,
                    "roi": roi_rel,
                })

    fieldnames = [
        "subject", "feat_relpath", "cope_idx", "contrast_name",
        "contrast_fix", "H_common", "H_source", "scale_factor", "psc_mean", "roi"
    ]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    with open(skip_json, "w", encoding="utf-8") as f:
        json.dump(skipped, f, indent=2)

    print(f"Wrote {len(rows)} rows to: {out_csv}")
    print(f"Wrote {len(skipped)} skipped records to: {skip_json}")
    print(f"Common height H = {H} ({H_src}) from {ISOLATED_EVENT_MAT}")

if __name__ == "__main__":
    main()
