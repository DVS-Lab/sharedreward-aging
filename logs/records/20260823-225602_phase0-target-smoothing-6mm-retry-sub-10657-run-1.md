# Run Record: phase0-target-smoothing-6mm-retry-sub-10657-run-1

- Timestamp: 20260823-225602
- Branch: main
- Commit: 2a1a86d
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260823-225602_phase0-target-smoothing-6mm-retry-sub-10657-run-1.log`
- Command exit: 1
- Check exit: skipped
- Summary: COMMAND exit 1; CHECK skipped.

## Command

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/run_target_smoothing_batch.py --manifest logs/runlists/target-smoothing-6mm-retry-sub-10657-run-1.tsv --jobs 1 --overwrite --log-dir logs/target-smoothing-6mm-retry-sub-10657-run-1 --work-root work/target-smoothing-6mm-retry-sub-10657-run-1 
```

## Check

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/audit_target_smoothing.py --manifest logs/runlists/target-smoothing-6mm-retry-sub-10657-run-1.tsv --output logs/records/target-smoothing-6mm-retry-sub-10657-run-1.tsv --missing-output logs/records/target-smoothing-6mm-retry-sub-10657-run-1-missing.tsv --fail-on-incomplete 
```

## Log

```text
RUN START: 20260823-225602
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main 2a1a86d
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/run_target_smoothing_batch.py --manifest logs/runlists/target-smoothing-6mm-retry-sub-10657-run-1.tsv --jobs 1 --overwrite --log-dir logs/target-smoothing-6mm-retry-sub-10657-run-1 --work-root work/target-smoothing-6mm-retry-sub-10657-run-1 

Target-smoothing plan: 1 unit(s), jobs=1, AFNI threads/job=4, tolerance=±10%, overwrite=true
Per-unit logs: logs/target-smoothing-6mm-retry-sub-10657-run-1
ERROR: rf1_sub-10657_ses-01_run-1: failed: classic combined 5.28041 outside 5.4-6.6 mm (log: logs/target-smoothing-6mm-retry-sub-10657-run-1/rf1_sub-10657_ses-01_run-1.log)
   + detrending of blurmaster complete
  ++ Output dataset /ZPOOL/data/projects/sharedreward-aging/work/target-smoothing-6mm-retry-sub-10657-run-1/blur.JdGJQH/smoothed.nii.gz
  ++ 3dFWHMx: AFNI version=AFNI_26.2.03 (Aug  4 2026) [64-bit]
  ++ Authored by: The Bob
  [7m*+ WARNING:[0m Using the 'Classic' Gaussian FWHM is not recommended :(
   +  The '-acf' method gives a FWHM estimate which is more robust;
   +  however, assuming the spatial correlation of FMRI noise has
   +  a Gaussian shape is not a good model.
  ++ Number of voxels in mask = 101624
  ++ detrending start: 19 baseline funcs, 255 time points
   + detrending done (0.00 CPU s thus far)
  ++ start Classic FWHM calculations
   + Classic FWHM done (0.00 CPU s thus far)
  ++ start ACF calculations out to radius = 15.84 mm
   + ACF done (0.00 CPU s thus far)
  Smoothness: classic combined=5.28041 mm; ACF effective=7.85496 mm
  Requested target: 6 mm
  Runtime: 116 seconds
  Output: /ZPOOL/data/projects/rf1-sra-sharedreward/derivatives/harmonized/sub-10657/ses-01/func/sub-10657_ses-01_task-sharedreward_run-1_space-MNI152NLin6Asym_desc-smoothToFWHM6_bold.nii.gz
  QC: /ZPOOL/data/projects/rf1-sra-sharedreward/derivatives/harmonized/sub-10657/ses-01/func/sub-10657_ses-01_task-sharedreward_run-1_space-MNI152NLin6Asym_desc-smoothToFWHM6_bold_smoothness.tsv
Units scheduled: 1
Units newly completed: 0
Units verified existing: 0
Units failed: 1

COMMAND EXIT: 1
CHECK SKIPPED: command failed.
```
