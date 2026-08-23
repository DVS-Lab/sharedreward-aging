# Run Record: target-smoothing-6mm-sanity-ds003745-sub-118-run-02

- Timestamp: 20260823-180533
- Branch: main
- Commit: 598679c
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260823-180533_target-smoothing-6mm-sanity-ds003745-sub-118-run-02.log`
- Command exit: 0
- Check exit: none
- Summary: COMMAND exit 0; CHECK none.

## Command

```bash
bash code/smooth_to_target.sh --input /ZPOOL/data/projects/sharedreward-aging/derivatives/harmonized/sub-118/func/sub-118_task-sharedreward_run-02_space-MNI152NLin6Asym_desc-rf1Grid_bold.nii.gz --mask /ZPOOL/data/projects/sharedreward-aging/derivatives/harmonized/sub-118/func/sub-118_task-sharedreward_run-02_space-MNI152NLin6Asym_desc-rf1Grid_mask.nii.gz --output /ZPOOL/data/projects/sharedreward-aging/derivatives/harmonized/sub-118/func/sub-118_task-sharedreward_run-02_space-MNI152NLin6Asym_desc-smoothToFWHM6_bold.nii.gz --qc-tsv /ZPOOL/data/projects/sharedreward-aging/derivatives/harmonized/sub-118/func/sub-118_task-sharedreward_run-02_space-MNI152NLin6Asym_desc-smoothToFWHM6_bold_smoothness.tsv --work-dir work/target-smoothing 
```

## Log

```text
RUN START: 20260823-180533
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main 598679c
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: bash code/smooth_to_target.sh --input /ZPOOL/data/projects/sharedreward-aging/derivatives/harmonized/sub-118/func/sub-118_task-sharedreward_run-02_space-MNI152NLin6Asym_desc-rf1Grid_bold.nii.gz --mask /ZPOOL/data/projects/sharedreward-aging/derivatives/harmonized/sub-118/func/sub-118_task-sharedreward_run-02_space-MNI152NLin6Asym_desc-rf1Grid_mask.nii.gz --output /ZPOOL/data/projects/sharedreward-aging/derivatives/harmonized/sub-118/func/sub-118_task-sharedreward_run-02_space-MNI152NLin6Asym_desc-smoothToFWHM6_bold.nii.gz --qc-tsv /ZPOOL/data/projects/sharedreward-aging/derivatives/harmonized/sub-118/func/sub-118_task-sharedreward_run-02_space-MNI152NLin6Asym_desc-smoothToFWHM6_bold_smoothness.tsv --work-dir work/target-smoothing 

++ 3dBlurToFWHM: AFNI version=AFNI_26.2.03 (Aug  4 2026) [64-bit]
++ Max number iterations set to 143
++ detrending blurmaster: 15 ref funcs, 202 time points
 + detrending of blurmaster complete
++ Output dataset /ZPOOL/data/projects/sharedreward-aging/work/target-smoothing/blur.XFCGqW/smoothed.nii.gz
++ 3dFWHMx: AFNI version=AFNI_26.2.03 (Aug  4 2026) [64-bit]
++ Authored by: The Bob
[7m*+ WARNING:[0m Using the 'Classic' Gaussian FWHM is not recommended :(
 +  The '-acf' method gives a FWHM estimate which is more robust;
 +  however, assuming the spatial correlation of FMRI noise has
 +  a Gaussian shape is not a good model.
++ Number of voxels in mask = 82050
++ detrending start: 15 baseline funcs, 202 time points
 + detrending done (0.00 CPU s thus far)
++ start Classic FWHM calculations
 + Classic FWHM done (0.00 CPU s thus far)
++ start ACF calculations out to radius = 17.97 mm
 + ACF done (0.00 CPU s thus far)
Smoothness: classic combined=5.99337 mm; ACF effective=9.08367 mm
Requested target: 6 mm
Runtime: 58 seconds
Output: /ZPOOL/data/projects/sharedreward-aging/derivatives/harmonized/sub-118/func/sub-118_task-sharedreward_run-02_space-MNI152NLin6Asym_desc-smoothToFWHM6_bold.nii.gz
QC: /ZPOOL/data/projects/sharedreward-aging/derivatives/harmonized/sub-118/func/sub-118_task-sharedreward_run-02_space-MNI152NLin6Asym_desc-smoothToFWHM6_bold_smoothness.tsv

COMMAND EXIT: 0
```
