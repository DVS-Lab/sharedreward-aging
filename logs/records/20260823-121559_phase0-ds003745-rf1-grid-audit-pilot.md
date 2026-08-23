# Run Record: phase0-ds003745-rf1-grid-audit-pilot

- Timestamp: 20260823-121559
- Branch: main
- Commit: b1307c0
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260823-121559_phase0-ds003745-rf1-grid-audit-pilot.log`
- Command exit: 0
- Check exit: none
- Summary: CHECK PASSED: every harmonized ds003745 BOLD and mask matches the RF1 grid.

## Command

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/audit_resampling.py --manifest logs/runlists/ds003745-resampling-pilot.tsv --reference /ZPOOL/data/projects/rf1-sra-sharedreward/resources/rf1_MNI152NLin6Asym_reference_grid.nii.gz --output logs/records/ds003745-rf1-grid-audit-pilot.tsv --fail-on-incomplete 
```

## Log

```text
RUN START: 20260823-121559
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main b1307c0
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/audit_resampling.py --manifest logs/runlists/ds003745-resampling-pilot.tsv --reference /ZPOOL/data/projects/rf1-sra-sharedreward/resources/rf1_MNI152NLin6Asym_reference_grid.nii.gz --output logs/records/ds003745-rf1-grid-audit-pilot.tsv --fail-on-incomplete 

Run units checked: 1
Complete run units: 1
Incomplete run units: 0
Audit: /ZPOOL/data/projects/sharedreward-aging/logs/records/ds003745-rf1-grid-audit-pilot.tsv
CHECK PASSED: every harmonized ds003745 BOLD and mask matches the RF1 grid.

COMMAND EXIT: 0
```
