#!/usr/bin/env python3
"""Read-only, pre-QC verification of pooled non-neutral L1/group input maps.

Writes reports only. Never launches FEAT, changes models, or selects exclusions.
Neutral contrast numbering is preserved; neutral maps and PPI phys COPE29 are
outside this task-inference gate. Neutral EVs still belong to the fitted design.
"""

import argparse
import csv
import io
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

import nibabel as nib
import numpy as np

from audit_l1_contrasts import matrix
from audit_outputs import l1_path, l2_path
from model_provenance import CONTRACT, STAMP, fingerprint
from render_pooled_fsf import ROOT, candidate_contrasts

CONTRASTS = ROOT / "templates/FULLTRIAL_CONTRAST_CANDIDATE.tsv"
EV_NAMES = [f"event_{p}_{o}" for p in ("computer", "friend", "stranger")
            for o in ("punish", "reward")]
EV_NAMES += [f"event_{p}_neutral" for p in ("computer", "friend", "stranger")]
EV_NAMES += ["missed_trial"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def selected_contrasts():
    # Test actual neutral coefficients, NOT contrast names (e.g. "all").
    return [(i, name, weights) for i, (name, weights) in
            enumerate(candidate_contrasts(CONTRASTS), 1) if not any(weights[6:9])]


def read_table(path):
    with Path(path).open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def subject_key(row):
    require(row["dataset"] in ("rf1", "ds003745"), "unknown dataset")
    require(bool(re.fullmatch(r"\d+", row["subject"])), "invalid subject ID")
    require(row["session"] == "" or bool(re.fullmatch(r"\d+", row["session"])),
            "invalid session (use empty for ds003745)")
    return row["dataset"], row["subject"], row["session"]


def validate_manifests(l1, subjects):
    require(l1 and subjects, "empty manifest; cannot certify an empty cohort")
    seen, expected = set(), defaultdict(set)
    for row in l1:
        key, run = subject_key(row), int(row["run"])
        require(run in (1, 2), "expected run 1 or 2")
        require((*key, run) not in seen, f"duplicate L1 run: {key} {run}")
        seen.add((*key, run))
        expected[key].add(run)
        for field in ("input", "mask", "confounds", "harmonized_events"):
            require(bool(row.get(field)), f"missing manifest field {field}: {key}")
    seen_subjects = set()
    for row in subjects:
        key = subject_key(row)
        runs = [int(x) for x in row["runs"].split(",")]
        require(key not in seen_subjects, f"duplicate subject-session: {key}")
        seen_subjects.add(key)
        require(len(runs) == len(set(runs)) == int(row["n_runs"]), f"invalid runs: {key}")
        require(set(runs) == expected.get(key), f"L1/L2 retained-run mismatch: {key}")
    require(seen_subjects == set(expected), "L1/L2 subject inventory mismatch")


def fsf_settings(path):
    return {key: value.strip().strip('"') for key, value in re.findall(
        r"^set\s+(\S+)\s+([^\n]+)", path.read_text(), re.M)}


def check_stamp(directory, level, kind, primary, parents=(), required_inputs=(), required_images=()):
    data = json.loads((directory / STAMP).read_text())
    require((data["contract"], data["level"], data["type"]) == (CONTRACT, level, kind),
            "unverified model contract/type; investigate provenance, not an automatic rerun")
    require(data["inputs"] and data["images"], "empty provenance inventory")
    require([str(Path(p).resolve()) for p in data["parents"]] ==
            [str(Path(p).resolve()) for p in parents], "provenance parents differ from retained runs")
    for field, required in (("inputs", required_inputs), ("images", required_images)):
        recorded = {str(Path(item["path"]).resolve()) for item in data[field]}
        require({str(Path(p).resolve()) for p in required} <= recorded,
                f"provenance omits expected {field}")
    for item in data["inputs"]:
        require(fingerprint(item["path"]) == item, f"changed model input: {item['path']}")
    for item in data["images"]:
        if level == "l2":
            match = re.search(r"/(?:var)?cope(\d+)\.nii\.gz$", item["path"])
            require(match is not None, f"unexpected L2 image provenance: {item['path']}")
            if int(match[1]) not in primary:
                continue  # Neutral/phys output absence does not block task inference.
        require(fingerprint(item["path"], True) == item, f"changed image input: {item['path']}")


def check_events(settings, row):
    events = read_table(row["harmonized_events"])
    require(events, "empty harmonized event table")
    grouped = defaultdict(list)
    for event in events:
        require(event["trial_type"] in EV_NAMES, "unexpected harmonized event type")
        grouped[event["trial_type"]].append((float(event["onset"]), float(event["duration"]), 1.))
    paths = []
    for i, name in enumerate(EV_NAMES, 1):
        path = Path(settings[f"fmri(custom{i})"])
        expected = np.array(grouped[name]).reshape(-1, 3)
        text = path.read_text().strip()
        actual = np.loadtxt(io.StringIO(text), ndmin=2) if text else np.empty((0, 3))
        require(actual.shape == expected.shape and
                np.allclose(actual, expected, atol=0.00000051, rtol=0),
                f"EV differs from current harmonized events: {name}")
        require(settings[f"fmri(shape{i})"] == ("3" if len(expected) else "10"),
                f"EV shape inconsistent with events: {name}")
        paths.append(path)
    return paths


def check_l1_design(directory, kind):
    settings = fsf_settings(directory / "design.fsf")
    ppi = kind != "act"
    width, count = (21, 29) if ppi else (10, 28)
    for key, value in {"conmask1_1": 0, "smooth": 0, "featwatcher_yn": 0,
                       "evs_real": width, "evs_orig": width,
                       "ncon_real": count, "ncon_orig": count}.items():
        require(float(settings[f"fmri({key})"]) == value, f"unexpected {key}")
    for i in range(1, width + 1):
        require(settings[f"fmri(tempfilt_yn{i})"] == "0", f"temporal EV filter enabled: {i}")
    x, c = matrix(directory / "design.mat"), matrix(directory / "design.con")
    require(x.shape[1] >= width and c.shape == (count, x.shape[1]), "design dimensions mismatch")
    require(np.isfinite(x).all(), "nonfinite design matrix")
    projection = np.linalg.pinv(x) @ x
    for i, name, weights in selected_contrasts():
        vector = ([0.] * 11 + weights) if ppi else weights
        intended = np.pad(vector, (0, x.shape[1] - width))
        for mode in ("orig", "real"):
            require(settings[f"fmri(conname_{mode}.{i})"] == name, f"COPE{i} name/number differs")
            actual = [float(settings[f"fmri(con_{mode}{i}.{j})"]) for j in range(1, width + 1)]
            require(np.allclose(actual, vector, atol=1e-8, rtol=0), f"COPE{i} FSF coefficients differ")
        require(np.allclose(c[i-1], intended, atol=1e-8, rtol=0), f"COPE{i} actual design.con differs")
        require(np.max(np.abs(intended - intended @ projection)) <= 1e-5,
                f"COPE{i} non-neutral hypothesis not estimable")
    return settings, x.shape[0]


def image_data(path, reference):
    image = nib.load(str(path))
    require(image.shape == reference.shape[:3], f"not a reference-grid 3D image: {path}")
    require(np.allclose(image.affine, reference.affine, atol=1e-4, rtol=0), f"affine mismatch: {path}")
    return image.get_fdata(dtype=np.float32)


def check_maps(directory, numbers, reference):
    mask = image_data(directory / "mask.nii.gz", reference)
    require(np.isfinite(mask).all() and (mask > 0).any(), f"invalid/empty model mask: {directory}")
    mask = mask > 0
    for number in numbers:
        for name in ("cope", "varcope", "zstat"):
            path = directory / f"stats/{name}{number}.nii.gz"
            values = image_data(path, reference)[mask]
            require(np.isfinite(values).all(), f"nonfinite in-mask data: {path}")
            if name == "varcope":
                require((values >= 0).all() and (values > 0).any(), f"invalid in-mask variance: {path}")


def check_l1(directory, row, kind, reference, primary):
    settings, nvol = check_l1_design(directory, kind)
    require(Path(settings["feat_files(1)"]).resolve() == Path(row["input"]).resolve(),
            "model BOLD differs from manifest")
    confounds = Path(settings["confoundev_files(1)"])
    require(confounds.resolve() == Path(row["confounds"]).resolve(), "model confounds differ from manifest")
    evs = check_events(settings, row)
    check_stamp(directory, "l1", kind, primary, required_inputs=[confounds, *evs],
                required_images=[row["input"], row["mask"]])
    bold = nib.load(row["input"])
    require(len(bold.shape) == 4 and bold.shape[3] == nvol, "BOLD/design volume mismatch")
    nuisance = np.loadtxt(confounds, ndmin=2)
    require(nuisance.shape[0] == nvol and np.isfinite(nuisance).all(), "invalid nuisance matrix")
    check_maps(directory, primary, reference)


def check_l2(directory, parents, kind, reference, primary):
    settings = fsf_settings(directory / "design.fsf")
    for key, value in {"mixed_yn": 3, "npts": 2, "evs_real": 1, "evs_orig": 1}.items():
        require(float(settings[f"fmri({key})"]) == value, f"not expected two-run fixed effects: {key}")
    actual = [Path(settings[f"feat_files({i})"]).resolve() for i in (1, 2)]
    require(actual == [p.resolve() for p in parents], "L2 inputs differ from retained L1 runs/order")
    images = [p / f"stats/{name}{i}.nii.gz" for p in parents for i in primary for name in ("cope", "varcope")]
    check_stamp(directory, "l2", kind, primary, parents, [p / STAMP for p in parents], images)
    for i in primary:
        require(settings[f"fmri(copeinput.{i})"] == "1", f"L2 COPE{i} not selected")
        cope = directory / f"cope{i}.feat"
        x, c = matrix(cope / "design.mat"), matrix(cope / "design.con")
        require(x.shape == (2, 1) and np.allclose(x, 1) and
                c.shape == (1, 1) and np.allclose(c, 1), f"COPE{i}: unexpected fixed-effects design")
        check_maps(cope, [1], reference)


def checked(path, function):
    if not path.is_dir():
        return "missing", "expected model directory absent"
    try:
        function()
        return "verified", ""
    except (OSError, ValueError, KeyError, IndexError, nib.filebasedimages.ImageFileError,
            np.linalg.LinAlgError) as error:
        return "unverified", str(error)


def write_table(path, rows, fields):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--l1-manifest", type=Path, default=ROOT / "logs/runlists/L1-task-ready.tsv")
    parser.add_argument("--subject-manifest", type=Path, default=ROOT / "logs/runlists/L2-task-ready.tsv")
    parser.add_argument("--fsl-root", type=Path, default=Path(os.environ.get("FSL_DERIVATIVES_ROOT", ROOT / "derivatives/fsl")))
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path, required=True, help="New directory; existing reports are never overwritten")
    parser.add_argument("--ppi-seed", default="vs")
    args = parser.parse_args()
    require(bool(re.fullmatch(r"[a-z0-9_-]+", args.ppi_seed)), "invalid seed label")
    l1, subjects = read_table(args.l1_manifest), read_table(args.subject_manifest)
    validate_manifests(l1, subjects)
    reference = nib.load(str(args.reference))
    primary = [i for i, _, _ in selected_contrasts()]
    args.report_dir.mkdir(parents=True, exist_ok=False)
    kinds = ("act", f"ppi_seed-{args.ppi_seed}")
    results, subject_results, candidates, cache = [], [], [], {}
    print(f"Read-only audit: {len(l1)} retained runs; {len(subjects)} subject-sessions; both activation/PPI", flush=True)
    print(f"Primary COPE IDs: {primary}; neutral-weighted contrasts and PPI phys excluded.", flush=True)
    for row in l1:
        for kind in kinds:
            path = l1_path(args.fsl_root, row, kind)
            status, problem = checked(path, lambda: check_l1(path, row, kind, reference, primary))
            cache[(*subject_key(row), int(row["run"]), kind)] = status
            results.append(dict(row, type=kind, path=str(path), status=status, problem=problem))
        if len(results) % 100 == 0:
            print(f"L1 models checked: {len(results)}", flush=True)
    for row in subjects:
        runs = [int(x) for x in row["runs"].split(",")]
        for kind in kinds:
            parents = [l1_path(args.fsl_root, row, kind, run) for run in runs]
            strategy = "l1_passthrough" if len(runs) == 1 else "fixed_effects"
            path = parents[0] if len(runs) == 1 else l2_path(args.fsl_root, row, kind)
            status, problem = ("verified", "") if len(runs) == 1 else checked(
                path, lambda: check_l2(path, parents, kind, reference, primary))
            bad = [run for run in runs if cache[(*subject_key(row), run, kind)] != "verified"]
            if bad:
                status, problem = "unverified", f"unverified retained L1 runs {bad}; {problem}"
            subject_results.append(dict(row, type=kind, strategy=strategy, path=str(path), status=status, problem=problem))
            if status == "verified":
                for i, name, _ in selected_contrasts():
                    base, number = (path, i) if len(runs) == 1 else (path / f"cope{i}.feat", 1)
                    candidates.append(dict(row, type=kind, cope=i, contrast=name, strategy=strategy,
                        cope_path=str(base / f"stats/cope{number}.nii.gz"),
                        varcope_path=str(base / f"stats/varcope{number}.nii.gz"), mask_path=str(base / "mask.nii.gz")))
    keys = ["dataset", "subject", "session", "type"]
    write_table(args.report_dir / "l1-audit.tsv", results, keys + ["run", "status", "problem", "path", "imaging_qc_flags"])
    write_table(args.report_dir / "subject-audit.tsv", subject_results, keys + ["runs", "strategy", "status", "problem", "path"])
    write_table(args.report_dir / "verified-pre-QC-candidates.tsv", candidates,
                keys + ["runs", "strategy", "cope", "contrast", "cope_path", "varcope_path", "mask_path", "ratings_eligible"])
    summary = {"contract": CONTRACT, "primary_cope_ids": primary,
        "ignored_neutral_cope_ids": [i for i in range(1, 29) if i not in primary],
        "ppi_phys_cope29_in_scope": False,
        "inputs": [fingerprint(p) for p in (args.l1_manifest, args.subject_manifest, CONTRASTS, Path(__file__))],
        "reference": fingerprint(args.reference), "fsl_root": str(args.fsl_root.resolve()),
        "expected_runs": len(l1), "expected_subject_sessions": len(subjects),
        "counts": {}, "limitations": ["Computational verification is not final QC or cohort approval.",
            "Ratings, imaging exclusions, covariates, seed provenance and L3 inference require adjudication.",
            "Image-input provenance uses recorded size/mtime, not full 4D content hashing.",
            "EVs compared to current harmonized events; this does not re-audit raw behavioral sources.",
            "Canonical pooled output paths only; absent models may exist elsewhere and require inventory review.",
            "Unverified models are not an instruction to rerun; review the reported cause first."]}
    for level, rows in (("l1", results), ("subject", subject_results)):
        summary["counts"][level] = dict(Counter(r["status"] for r in rows))
        summary["counts"][level + "_by_dataset_type_status"] = dict(Counter(
            f"{r['dataset']}/{r['type']}/{r['status']}" for r in rows))
        print(f"{level}: {summary['counts'][level]}", flush=True)
    passed = all(r["status"] == "verified" for r in results + subject_results)
    summary["computational_gate_passed"] = passed
    (args.report_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"Reports: {args.report_dir.resolve()}")
    print("CHECK PASSED: primary computational inputs verified; final QC still separate." if passed else
          "CHECK INCOMPLETE: review reports before handoff; no model files were changed.")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
