# Run Record: phase0-create-historical-coverage-eligible-mask

- Timestamp: 20260824-102210
- Branch: main
- Commit: edd95bc
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260824-102210_phase0-create-historical-coverage-eligible-mask.log`
- Command exit: 0
- Check exit: none
- Summary: COMMAND exit 0; CHECK none.

## Command

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/create_coverage_eligible_mask.py --template-mask /ZPOOL/data/projects/sharedreward-aging/resources/tpl-MNI152NLin6Asym_space-RF1Grid_desc-brain_mask.nii.gz --exemption-mask masks/cerebellum-brainstem_mask.nii.gz --reference-grid /ZPOOL/data/projects/rf1-sra-sharedreward/resources/rf1_MNI152NLin6Asym_reference_grid.nii.gz --resampled-exemption-output /ZPOOL/data/projects/sharedreward-aging/resources/tpl-MNI152NLin6Asym_space-RF1Grid_desc-coverageExemption_mask.nii.gz --eligible-mask-output /ZPOOL/data/projects/sharedreward-aging/resources/tpl-MNI152NLin6Asym_space-RF1Grid_desc-coverageEligible_mask.nii.gz --json-output resources/tpl-MNI152NLin6Asym_space-RF1Grid_desc-coverageEligible_mask.json 
```

## Log

```text
RUN START: 20260824-102210
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main edd95bc
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/create_coverage_eligible_mask.py --template-mask /ZPOOL/data/projects/sharedreward-aging/resources/tpl-MNI152NLin6Asym_space-RF1Grid_desc-brain_mask.nii.gz --exemption-mask masks/cerebellum-brainstem_mask.nii.gz --reference-grid /ZPOOL/data/projects/rf1-sra-sharedreward/resources/rf1_MNI152NLin6Asym_reference_grid.nii.gz --resampled-exemption-output /ZPOOL/data/projects/sharedreward-aging/resources/tpl-MNI152NLin6Asym_space-RF1Grid_desc-coverageExemption_mask.nii.gz --eligible-mask-output /ZPOOL/data/projects/sharedreward-aging/resources/tpl-MNI152NLin6Asym_space-RF1Grid_desc-coverageEligible_mask.nii.gz --json-output resources/tpl-MNI152NLin6Asym_space-RF1Grid_desc-coverageEligible_mask.json 

Template mask voxels: 84542
Exemption voxels inside template: 9203
Coverage-eligible voxels: 75339
Resampled exemption: /ZPOOL/data/projects/sharedreward-aging/resources/tpl-MNI152NLin6Asym_space-RF1Grid_desc-coverageExemption_mask.nii.gz
Eligible coverage mask: /ZPOOL/data/projects/sharedreward-aging/resources/tpl-MNI152NLin6Asym_space-RF1Grid_desc-coverageEligible_mask.nii.gz
Metadata: /ZPOOL/data/projects/sharedreward-aging/resources/tpl-MNI152NLin6Asym_space-RF1Grid_desc-coverageEligible_mask.json

COMMAND EXIT: 0
```
