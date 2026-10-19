"""Known-mask/variance-loss attribution, unchanged sources and CLI smoke test."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import nibabel as nib
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
import audit_vmpfc_support as diagnostic


class CoverageTests(unittest.TestCase):
    def setup_inputs(self, root):
        ref = nib.Nifti1Image(np.ones((3,3,3)), np.eye(4))
        folder = root / "analysis/age_act_cope-10"
        folder.mkdir(parents=True)
        rows, masks, supports = [], [], []
        for i in range(3):
            mask = np.ones(ref.shape)
            var = np.ones(ref.shape)
            if i == 0: mask.flat[0] = 0  # Unique mask loss.
            if i < 2: var.flat[1] = 0  # Shared variance loss.
            if i == 2: var.flat[2] = 0  # Unique variance loss.
            maskpath, varpath = root/f"mask{i}.nii.gz", root/f"var{i}.nii.gz"
            nib.save(nib.Nifti1Image(mask, ref.affine), maskpath)
            nib.save(nib.Nifti1Image(var, ref.affine), varpath)
            rows.append(dict(dataset="ds003745" if i == 0 else "rf1", subject=str(i), session="",
                             mask_path=str(maskpath), varcope_path=str(varpath), runs="1,2", strategy="l2"))
            masks.append(mask>0); supports.append((mask>0)&(var>0))
        pd.DataFrame(rows).to_csv(folder/"ordered-inputs.tsv", sep="\t", index=False)
        for name, values in (("directory-mask", masks), ("analysis-mask", supports)):
            nib.save(nib.Nifti1Image(np.logical_and.reduce(values).astype(np.uint8), ref.affine), folder/f"{name}.nii.gz")
        return folder, ref

    def test_attribution_frequencies_and_unchanged_sources(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); folder, ref = self.setup_inputs(root)
            before = {str(f): diagnostic.sha(f) for f in root.glob("*.nii.gz")}
            rec, summaries, provenance = diagnostic.audit_model(folder, ref, np.ones(ref.shape,bool), root/"maps")
            pooled = summaries[0]
            self.assertEqual(pooled["common_mask_roi_voxels"], 26)
            self.assertEqual(pooled["common_support_roi_voxels"], 24)
            self.assertEqual(pooled["additional_variance_loss_roi_voxels"], 2)
            self.assertEqual([r["unique_mask_loss_voxels"] for r in rec], [1,0,0])
            self.assertEqual([r["unique_support_loss_voxels"] for r in rec], [1,0,1])
            freq = nib.load(root/"maps/pooled_support-frequency.nii.gz").get_fdata().ravel()
            np.testing.assert_allclose(freq[:3], [2/3,1/3,2/3], atol=1e-7)
            self.assertEqual(before, {str(f): diagnostic.sha(f) for f in root.glob("*.nii.gz")})
            self.assertEqual(len(provenance["inputs"]), 6)

    def test_fail_on_nonfinite_mismatch_duplicate_and_adapter(self):
        for problem in ("nonfinite", "grid", "saved_mask", "duplicate", "adapter"):
            with self.subTest(problem=problem), tempfile.TemporaryDirectory() as temp:
                root=Path(temp); folder, ref=self.setup_inputs(root)
                if problem in ("nonfinite", "grid"):
                    values=np.ones(ref.shape); affine=ref.affine.copy()
                    if problem == "nonfinite": values.flat[5]=np.nan
                    else: affine[0,3]=1
                    nib.save(nib.Nifti1Image(values,affine),root/"var0.nii.gz")
                elif problem == "saved_mask": nib.save(ref,folder/"analysis-mask.nii.gz")
                else:
                    frame=pd.read_csv(folder/"ordered-inputs.tsv",sep="\t",dtype=str,keep_default_na=False)
                    if problem == "duplicate": frame=pd.concat([frame,frame.iloc[:1]])
                    else: frame.loc[0,"mask_path"]="/some/inputs/input-1.feat/mask.nii.gz"
                    frame.to_csv(folder/"ordered-inputs.tsv",sep="\t",index=False)
                with self.assertRaises(ValueError):
                    diagnostic.audit_model(folder,ref,np.ones(ref.shape,bool),root/"maps")

    def test_cli_and_plot(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); folder,ref=self.setup_inputs(root)
            nib.save(ref,root/"ref.nii.gz")
            command=[sys.executable, diagnostic.__file__, "--analysis-root", str(folder.parent),
                     "--reference",str(root/"ref.nii.gz"),"--roi",str(root/"ref.nii.gz"),
                     "--output-dir",str(root/"reports"),"--map-dir",str(root/"maps")]
            result=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            complete=json.loads((root/"reports/completion.json").read_text())
            self.assertTrue(complete["complete"])
            self.assertEqual(complete["participant_model_rows"],3)
            self.assertTrue((root/"reports/vmpfc-coverage-summary.png").is_file())
            self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)


if __name__ == "__main__":
    unittest.main()
