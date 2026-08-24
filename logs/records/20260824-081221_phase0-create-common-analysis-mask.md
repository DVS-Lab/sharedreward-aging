# Run Record: phase0-create-common-analysis-mask

- Timestamp: 20260824-081221
- Branch: main
- Commit: 3e3ab68
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260824-081221_phase0-create-common-analysis-mask.log`
- Command exit: 0
- Check exit: none
- Summary: COMMAND exit 0; CHECK none.

## Command

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/create_common_analysis_mask.py --source-mask /ZPOOL/data/tools/templateflow/tpl-MNI152NLin6Asym/tpl-MNI152NLin6Asym_res-02_desc-brain_mask.nii.gz --reference-grid /ZPOOL/data/projects/rf1-sra-sharedreward/resources/rf1_MNI152NLin6Asym_reference_grid.nii.gz --output /ZPOOL/data/projects/sharedreward-aging/resources/tpl-MNI152NLin6Asym_space-RF1Grid_desc-brain_mask.nii.gz --json-output resources/tpl-MNI152NLin6Asym_space-RF1Grid_desc-brain_mask.json 
```

## Log

```text
RUN START: 20260824-081221
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main 3e3ab68
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/create_common_analysis_mask.py --source-mask /ZPOOL/data/tools/templateflow/tpl-MNI152NLin6Asym/tpl-MNI152NLin6Asym_res-02_desc-brain_mask.nii.gz --reference-grid /ZPOOL/data/projects/rf1-sra-sharedreward/resources/rf1_MNI152NLin6Asym_reference_grid.nii.gz --output /ZPOOL/data/projects/sharedreward-aging/resources/tpl-MNI152NLin6Asym_space-RF1Grid_desc-brain_mask.nii.gz --json-output resources/tpl-MNI152NLin6Asym_space-RF1Grid_desc-brain_mask.json 

Common analysis mask voxels: 84542
Mask: /ZPOOL/data/projects/sharedreward-aging/resources/tpl-MNI152NLin6Asym_space-RF1Grid_desc-brain_mask.nii.gz
Metadata: /ZPOOL/data/projects/sharedreward-aging/resources/tpl-MNI152NLin6Asym_space-RF1Grid_desc-brain_mask.json

COMMAND EXIT: 0
```
