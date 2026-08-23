# Run Record: phase0-ds003745-rf1-grid-resampling-pilot

- Timestamp: 20260823-121537
- Branch: main
- Commit: b1307c0
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260823-121537_phase0-ds003745-rf1-grid-resampling-pilot.log`
- Command exit: 0
- Check exit: none
- Summary: CHECK PASSED: every ds003745 run has verified RF1-grid BOLD and mask outputs.

## Command

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/run_resampling_batch.py --manifest logs/runlists/ds003745-resampling-pilot.tsv --jobs 1 --log-dir logs/ds003745-resampling-pilot 
```

## Log

```text
RUN START: 20260823-121537
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main b1307c0
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/run_resampling_batch.py --manifest logs/runlists/ds003745-resampling-pilot.tsv --jobs 1 --log-dir logs/ds003745-resampling-pilot 

RF1-grid resampling plan: 1 run unit(s), jobs=1, overwrite=false
Reference: /ZPOOL/data/projects/rf1-sra-sharedreward/resources/rf1_MNI152NLin6Asym_reference_grid.nii.gz
Per-unit logs: logs/ds003745-resampling-pilot
START: sub-106 run-01
DONE: sub-106 run-01
Run units scheduled: 1
Run units completed: 1
Run units failed: 0
CHECK PASSED: every ds003745 run has verified RF1-grid BOLD and mask outputs.

COMMAND EXIT: 0
```
