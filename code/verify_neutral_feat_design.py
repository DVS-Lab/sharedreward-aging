#!/usr/bin/env python3
"""Exercise real FSL feat_model, including empty nuisance EVs, without running FEAT."""

import argparse
import io
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from render_pooled_fsf import ROOT, SOURCES, render


def matrix(path):
    return np.loadtxt(io.StringIO(path.read_text().split("/Matrix\n", 1)[1]), ndmin=2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    executable = shutil.which("feat_model")
    if not executable:
        parser.error("feat_model unavailable: load FSL")
    results = []
    with tempfile.TemporaryDirectory(prefix="neutral-feat-design-") as temporary:
        directory = Path(temporary)
        rng = np.random.default_rng(144)
        np.savetxt(directory / "phys.txt", rng.normal(size=255))
        np.savetxt(directory / "confounds.txt", rng.normal(size=(255, 2)))
        names = [f"event_{p}_{o}" for p in ("computer", "friend", "stranger") for o in ("punish", "reward")]
        neutral = [f"event_{p}_neutral" for p in ("computer", "friend", "stranger")]
        for i, name in enumerate(names):
            (directory / f"{name}.txt").write_text("".join(f"{12+i*7+j*65}\t4\t1\n" for j in range(6)))
        # Empty neutral nuisance EVs must not invalidate reward/punishment contrasts.
        for empty_neutral in (True, False):
            for i, name in enumerate(neutral):
                (directory / f"{name}.txt").write_text("" if empty_neutral else f"{430+i*12}\t4\t1\n")
            for empty_miss in (True, False):
                (directory / "missed_trial.txt").write_text("" if empty_miss else "475\t4\t1\n")
                for kind in ("act", "ppi"):
                    text = render(kind, SOURCES[kind], ROOT / "templates/FULLTRIAL_CONTRAST_CANDIDATE.tsv")
                    substitutions = {
                        "OUTPUT": str(directory / "unused"), "NVOLUMES": "255", "TR_INFO": "2",
                        "CONFOUNDEVS": str(directory / "confounds.txt"), "DATA": str(directory / "unused.nii.gz"),
                        "EVDIR": str(directory) + "/", "MISSED_TRIAL": str(directory / "missed_trial.txt"),
                        "PHYS": str(directory / "phys.txt"), "SHAPE_EV": "10" if empty_miss else "3",
                    }
                    substitutions.update({f"SHAPE_EV{i}": "10" if empty_neutral else "3" for i in (7, 8, 9)})
                    substitutions.update({f"SHAPE_PPI{i}": "10" if empty_neutral else "4" for i in (18, 19, 20)})
                    for key in sorted(substitutions, key=len, reverse=True):
                        text = text.replace(key, substitutions[key])
                    design = directory / "design"
                    design.with_suffix(".fsf").write_text(text)
                    result = subprocess.run([executable, str(design), str(directory / "confounds.txt")],
                                            env={**os.environ, "FSLOUTPUTTYPE": "NIFTI_GZ"},
                                            capture_output=True, text=True)
                    if result.returncode:
                        raise RuntimeError(f"{kind}, empty neutral={empty_neutral}, empty miss={empty_miss}: {result.stdout}\n{result.stderr}")
                    x, c = matrix(design.with_suffix(".mat")), matrix(design.with_suffix(".con"))
                    if not np.isfinite(x).all() or not np.isfinite(c).all():
                        raise ValueError("nonfinite design or contrasts")
                    error = float(np.max(np.abs(c - c @ np.linalg.pinv(x) @ x)))
                    if error > 1e-5:
                        raise ValueError(f"non-estimable {kind} contrast: projection error {error}")
                    if c.shape[0] != (22 if kind == "act" else 23):
                        raise ValueError("unexpected contrast count")
                    if empty_neutral and (np.any(x[:, 6:9]) or (kind == "ppi" and np.any(x[:, 17:20]))):
                        raise ValueError("empty neutral columns not zero")
                    results.append({"type": kind, "empty_neutral": empty_neutral, "empty_miss": empty_miss,
                                    "design_shape": list(x.shape), "contrasts": len(c), "rank": int(np.linalg.matrix_rank(x)),
                                    "maximum_estimability_error": error, "stderr": result.stderr})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"feat_model": executable, "cases": results}, indent=2) + "\n")
    print(f"PASS: {len(results)} real feat_model cases; finite matrices and every active contrast estimable.\nReport: {args.output}")


if __name__ == "__main__":
    main()
