"""The handoff gate ignores neutral outputs, not model integrity."""
import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import nibabel as nib
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
import audit_group_readiness as audit
from model_provenance import snapshot, STAMP


class GroupReadiness(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.reference = nib.Nifti1Image(np.ones((2, 2, 2)), np.eye(4))
        self.primary = [i for i, _, _ in audit.selected_contrasts()]

    def image(self, path, values=None, affine=None):
        path.parent.mkdir(parents=True, exist_ok=True)
        nib.save(nib.Nifti1Image(np.ones((2, 2, 2)) if values is None else values,
                               np.eye(4) if affine is None else affine), path)

    def model(self, kind):
        directory = self.root / kind
        directory.mkdir()
        ppi = kind != "act"
        width, count = (21, 29) if ppi else (10, 28)
        settings = {f"fmri({k})": str(v) for k, v in {
            "conmask1_1": 0, "smooth": 0, "featwatcher_yn": 0,
            "evs_real": width, "evs_orig": width,
            "ncon_real": count, "ncon_orig": count}.items()}
        settings.update({f"fmri(tempfilt_yn{i})": "0" for i in range(1, width + 1)})
        weights = np.full((count, width), np.nan)  # Out-of-scope contrasts deliberately unusable.
        for i, name, w in audit.selected_contrasts():
            vector = [0.] * 11 + w if ppi else w
            weights[i - 1] = vector
            for mode in ("orig", "real"):
                settings[f"fmri(conname_{mode}.{i})"] = name
                for j, value in enumerate(vector, 1):
                    settings[f"fmri(con_{mode}{i}.{j})"] = str(value)
        self.write_settings(directory, settings)
        self.write_matrix(directory / "design.mat", np.eye(width))
        self.write_matrix(directory / "design.con", weights)
        return directory, settings

    def write_settings(self, directory, settings):
        (directory / "design.fsf").write_text("".join(f'set {k} "{v}"\n' for k, v in settings.items()))

    def write_matrix(self, path, values):
        with path.open("w") as handle:
            handle.write("/Matrix\n")
            np.savetxt(handle, values)

    def test_selection_uses_coefficients_not_all_label(self):
        self.assertEqual(self.primary, [i for i in range(1, 29) if i not in (7, 8, 9, 20, 21, 22)])
        self.assertIn(23, self.primary)  # F-(S+C)all has NO neutral weights.
        self.assertEqual(len(self.primary), 22)

    def test_both_designs_ignore_neutral_and_phys_rows(self):
        for kind in ("act", "ppi_seed-vs"):
            directory, _ = self.model(kind)
            audit.check_l1_design(directory, kind)

    def test_actual_contrast_matrix_change_fails(self):
        directory, _ = self.model("act")
        c = audit.matrix(directory / "design.con")
        c[0, 6] = 1  # Add a neutral coefficient despite an unchanged condition label.
        self.write_matrix(directory / "design.con", c)
        with self.assertRaisesRegex(ValueError, "actual design.con"):
            audit.check_l1_design(directory, "act")

    def test_nonestimable_primary_fails(self):
        directory, _ = self.model("act")
        x = np.eye(10)
        x[:, 0] = 0
        self.write_matrix(directory / "design.mat", x)
        with self.assertRaisesRegex(ValueError, "not estimable"):
            audit.check_l1_design(directory, "act")

    def test_temporal_ev_filter_fails(self):
        directory, settings = self.model("act")
        settings["fmri(tempfilt_yn7)"] = "1"
        self.write_settings(directory, settings)
        with self.assertRaisesRegex(ValueError, "temporal EV filter"):
            audit.check_l1_design(directory, "act")

    def test_neutral_maps_not_required_but_bad_primary_variance_fails(self):
        directory = self.root / "maps"
        self.image(directory / "mask.nii.gz")
        for i in self.primary:
            for name in ("cope", "varcope", "zstat"):
                self.image(directory / f"stats/{name}{i}.nii.gz")
        audit.check_maps(directory, self.primary, self.reference)
        self.image(directory / "stats/varcope10.nii.gz", -np.ones((2, 2, 2)))
        with self.assertRaisesRegex(ValueError, "variance"):
            audit.check_maps(directory, self.primary, self.reference)

    def test_wrong_affine_and_nonfinite_fail(self):
        path = self.root / "test.nii.gz"
        affine = np.eye(4)
        affine[0, 3] = 1
        self.image(path, affine=affine)
        with self.assertRaisesRegex(ValueError, "affine"):
            audit.image_data(path, self.reference)
        directory = self.root / "maps"
        self.image(directory / "mask.nii.gz")
        self.image(directory / "stats/cope1.nii.gz", np.full((2, 2, 2), np.nan))
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            audit.check_maps(directory, [1], self.reference)

    def test_manifests_reject_duplicate_and_changed_retained_runs(self):
        row = dict(dataset="ds003745", subject="144", session="", run="01",
                   input="bold", mask="mask", confounds="confounds", harmonized_events="events")
        subject = dict(dataset="ds003745", subject="144", session="", n_runs="1", runs="1")
        audit.validate_manifests([row], [subject])
        with self.assertRaisesRegex(ValueError, "duplicate L1"):
            audit.validate_manifests([row, dict(row, run="1")], [subject])
        with self.assertRaisesRegex(ValueError, "retained-run mismatch"):
            audit.validate_manifests([row], [dict(subject, runs="2")])

    def test_provenance_ignores_deleted_neutral_parent_map_only(self):
        directory = self.root / "l2"
        directory.mkdir()
        source = self.root / "source.txt"
        source.write_text("input")
        primary = self.root / "stats/cope1.nii.gz"
        neutral = self.root / "stats/cope7.nii.gz"
        self.image(primary)
        self.image(neutral)
        (directory / STAMP).write_text(json.dumps(snapshot("l2", "act", [source], [primary, neutral], [])))
        neutral.unlink()
        audit.check_stamp(directory, "l2", "act", self.primary)
        source.write_text("changed")
        with self.assertRaisesRegex(ValueError, "changed model input"):
            audit.check_stamp(directory, "l2", "act", self.primary)

    def test_l2_fixed_effects_and_parent_identity(self):
        directory = self.root / "l2"
        directory.mkdir()
        parents = [self.root / "run1", self.root / "run2"]
        settings = {"fmri(mixed_yn)": "3", "fmri(npts)": "2", "fmri(evs_real)": "1",
                    "fmri(evs_orig)": "1", "feat_files(1)": str(parents[0]), "feat_files(2)": str(parents[1])}
        for i in self.primary:
            settings[f"fmri(copeinput.{i})"] = "1"
        images = []
        for parent in parents:
            parent.mkdir()
            (parent / STAMP).write_text("parent provenance tested separately")
            for i in self.primary:
                for name in ("cope", "varcope"):
                    path = parent / f"stats/{name}{i}.nii.gz"
                    self.image(path)
                    images.append(path)
        (directory / STAMP).write_text(json.dumps(snapshot("l2", "act", [p / STAMP for p in parents], images, parents)))
        for i in self.primary:
            cope = directory / f"cope{i}.feat"
            self.image(cope / "mask.nii.gz")
            self.write_matrix(cope / "design.mat", np.ones((2, 1)))
            self.write_matrix(cope / "design.con", np.ones((1, 1)))
            for name in ("cope", "varcope", "zstat"):
                self.image(cope / f"stats/{name}1.nii.gz")
        self.write_settings(directory, settings)
        audit.check_l2(directory, parents, "act", self.reference, self.primary)
        settings["fmri(mixed_yn)"] = "2"
        self.write_settings(directory, settings)
        with self.assertRaisesRegex(ValueError, "fixed effects"):
            audit.check_l2(directory, parents, "act", self.reference, self.primary)
        settings["fmri(mixed_yn)"] = "3"
        settings["feat_files(1)"] = str(parents[1])
        self.write_settings(directory, settings)
        with self.assertRaisesRegex(ValueError, "retained L1"):
            audit.check_l2(directory, parents, "act", self.reference, self.primary)

    def test_event_content_not_just_file_existence(self):
        events = self.root / "events.tsv"
        with events.open("w") as handle:
            writer = csv.DictWriter(handle, fieldnames=["trial_type", "onset", "duration"], delimiter="\t")
            writer.writeheader()
            writer.writerow(dict(trial_type="event_friend_reward", onset=1, duration=2))
        settings = {}
        for i, name in enumerate(audit.EV_NAMES, 1):
            path = self.root / f"{name}.txt"
            present = name == "event_friend_reward"
            path.write_text("1\t2\t1\n" if present else "")
            settings[f"fmri(custom{i})"] = str(path)
            settings[f"fmri(shape{i})"] = "3" if present else "10"
        audit.check_events(settings, {"harmonized_events": str(events)})
        (self.root / "event_friend_reward.txt").write_text("1.5\t2\t1\n")
        with self.assertRaisesRegex(ValueError, "differs from current"):
            audit.check_events(settings, {"harmonized_events": str(events)})

    def test_cli_one_run_passthrough_and_missing_model_reports(self):
        reference = self.root / "reference.nii.gz"
        self.image(reference)
        bold = self.root / "bold.nii.gz"
        nib.save(nib.Nifti1Image(np.ones((2, 2, 2, 30)), np.eye(4)), bold)
        mask = self.root / "mask.nii.gz"
        self.image(mask)
        confounds = self.root / "confounds.tsv"
        np.savetxt(confounds, np.zeros((30, 1)))
        events = self.root / "events.tsv"
        events.write_text("trial_type\tonset\tduration\n" + "".join(
            f"{name}\t{i}\t1\n" for i, name in enumerate(audit.EV_NAMES)))
        row = dict(dataset="ds003745", subject="144", session="", run="1", input=str(bold),
                   mask=str(mask), confounds=str(confounds), harmonized_events=str(events))
        subject = dict(dataset="ds003745", subject="144", session="", n_runs="1", runs="1")
        root = self.root / "fsl"
        for kind in ("act", "ppi_seed-vs"):
            original, settings = self.model(kind)
            directory = audit.l1_path(root, row, kind)
            directory.parent.mkdir(parents=True, exist_ok=True)
            original.rename(directory)
            width = 10 if kind == "act" else 21
            self.write_matrix(directory / "design.mat", np.pad(np.eye(width), ((0, 30-width), (0, 0))))
            settings["feat_files(1)"] = str(bold)
            settings["confoundev_files(1)"] = str(confounds)
            evs = []
            for i, name in enumerate(audit.EV_NAMES, 1):
                ev = self.root / f"{name}.txt"
                ev.write_text(f"{i-1}\t1\t1\n")
                settings[f"fmri(custom{i})"] = str(ev)
                settings[f"fmri(shape{i})"] = "3"
                evs.append(ev)
            self.write_settings(directory, settings)
            (directory / STAMP).write_text(json.dumps(snapshot("l1", kind, [confounds, *evs], [bold, mask], [])))
            self.image(directory / "mask.nii.gz")
            for i in self.primary:
                for name in ("cope", "varcope", "zstat"):
                    self.image(directory / f"stats/{name}{i}.nii.gz")
        l1, l2 = self.root / "l1.tsv", self.root / "l2.tsv"
        audit.write_table(l1, [row], list(row))
        audit.write_table(l2, [subject], list(subject))
        command = [sys.executable, "-B", str(Path(audit.__file__)), "--l1-manifest", str(l1),
                   "--subject-manifest", str(l2), "--fsl-root", str(root), "--reference", str(reference)]
        report = self.root / "pass"
        result = subprocess.run(command + ["--report-dir", str(report)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(len(audit.read_table(report / "verified-pre-QC-candidates.tsv")), 44)
        self.assertTrue(json.loads((report / "summary.json").read_text())["computational_gate_passed"])
        # Missing live output must NOT be replaced by an archived lookalike.
        path = audit.l1_path(root, row, "act")
        path.rename(self.root / "archived.feat")
        report = self.root / "missing"
        result = subprocess.run(command + ["--report-dir", str(report)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(audit.read_table(report / "l1-audit.tsv")[0]["status"], "missing")
        self.assertFalse(json.loads((report / "summary.json").read_text())["computational_gate_passed"])


if __name__ == "__main__":
    unittest.main()
