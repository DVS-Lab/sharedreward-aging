import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class L1RunnerTest(unittest.TestCase):
    def test_render_only_activation_and_ppi_resolve_the_pooled_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake_bin = root / "bin"
            fake_bin.mkdir()
            (fake_bin / "fslnvols").write_text("#!/usr/bin/env bash\necho 2\n")
            (fake_bin / "fslval").write_text(
                "#!/usr/bin/env bash\n"
                "[[ \"$2\" == pixdim4 ]] && { echo 2.0; exit; }\n"
                "echo 3\n"
            )
            (fake_bin / "fslmeants").write_text(
                "#!/usr/bin/env bash\n"
                "while (( $# )); do [[ \"$1\" == -o ]] && { out=\"$2\"; shift 2; } || shift; done\n"
                "printf '1\\n2\\n' > \"$out\"\n"
            )
            for command in fake_bin.iterdir():
                command.chmod(0o755)
            bold = root / "bold.nii.gz"; mask = root / "mask.nii.gz"; confounds = root / "confounds.tsv"
            bold.write_text("bold"); mask.write_text("mask"); confounds.write_text("0\n0\n")
            fsl_root = root / "fsl"
            ev_dir = fsl_root / "EVfiles/ds003745/sub-104/sharedreward/run-1"
            ev_dir.mkdir(parents=True)
            conditions = (
                "event_computer_punish", "event_computer_reward",
                "event_friend_punish", "event_friend_reward",
                "event_stranger_punish", "event_stranger_reward",
                "event_computer_neutral", "event_friend_neutral", "event_stranger_neutral",
            )
            for condition in conditions:
                (ev_dir / f"{condition}.txt").write_text("0\t1\t1\n")
            (ev_dir / "missed_trial.txt").write_text("")
            env = {
                **os.environ,
                "PATH": f"{fake_bin}:{os.environ['PATH']}",
                "FSL_DERIVATIVES_ROOT": str(fsl_root),
                "EVFILES_ROOT": str(fsl_root / "EVfiles"),
            }
            common = [
                "bash", str(ROOT / "code/L1stats.sh"), "ds003745", "104", "none", "1",
            ]
            options = ["--bold", str(bold), "--mask", str(mask), "--confounds", str(confounds), "--render-only"]
            subprocess.run(common + ["0"] + options, env=env, check=True, capture_output=True, text=True)
            unit_dir = fsl_root / "ds003745/sub-104"
            activation = unit_dir / "L1_ds003745_sub-104_task-sharedreward_model-fulltrial_type-act_run-1.fsf"
            activation_text = activation.read_text()
            self.assertNotIn("TR_INFO", activation_text)
            self.assertIn("set fmri(smooth) 0", activation_text)
            self.assertIn("set fmri(shape10) 10", activation_text)
            activation_feat = unit_dir / "L1_task-sharedreward_model-fulltrial_type-act_run-1_sm-6.feat"
            activation_feat.mkdir()
            (activation_feat / "mask.nii.gz").write_text("mask")
            subprocess.run(common + ["vs"] + options, env=env, check=True, capture_output=True, text=True)
            ppi = unit_dir / "L1_ds003745_sub-104_task-sharedreward_model-fulltrial_type-ppi_seed-vs_run-1.fsf"
            ppi_text = ppi.read_text()
            self.assertNotIn("PHYS", ppi_text)
            self.assertIn("set fmri(ncon_orig) 29", ppi_text)


if __name__ == "__main__":
    unittest.main()
