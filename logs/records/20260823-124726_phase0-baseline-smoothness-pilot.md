# Run Record: phase0-baseline-smoothness-pilot

- Timestamp: 20260823-124726
- Branch: main
- Commit: 4f69acc
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260823-124726_phase0-baseline-smoothness-pilot.log`
- Command exit: 1
- Check exit: skipped
- Summary: COMMAND exit 1; CHECK skipped.

## Command

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/run_smoothness_batch.py --manifest logs/runlists/phase0-characterization-pilot.tsv --jobs 3 --output-dir derivatives/qc/smoothness/run-level --log-dir logs/smoothness-pilot --work-root work/phase0-smoothness 
```

## Check

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/audit_smoothness.py --manifest logs/runlists/phase0-characterization-pilot.tsv --result-dir derivatives/qc/smoothness/run-level --output logs/records/phase0-baseline-smoothness-pilot.tsv --missing-output logs/records/phase0-baseline-smoothness-pilot-missing.tsv --fail-on-incomplete 
```

## Log

```text
RUN START: 20260823-124726
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main 4f69acc
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/run_smoothness_batch.py --manifest logs/runlists/phase0-characterization-pilot.tsv --jobs 3 --output-dir derivatives/qc/smoothness/run-level --log-dir logs/smoothness-pilot --work-root work/phase0-smoothness 

Baseline smoothness plan: 3 unit(s), jobs=3, AFNI threads/job=4, overwrite=false
Run-level results: derivatives/qc/smoothness/run-level
Per-unit logs: logs/smoothness-pilot
ERROR: ds003745_sub-104_run-01_stage-post_resample_preblur: failed: exit=1 (log: logs/smoothness-pilot/ds003745_sub-104_run-01_stage-post_resample_preblur.log)
ERROR: ds003745_sub-104_run-01_stage-pre_resample: failed: exit=1 (log: logs/smoothness-pilot/ds003745_sub-104_run-01_stage-pre_resample.log)
ERROR: rf1_sub-10317_ses-01_run-1_stage-pre_resample: failed: exit=1 (log: logs/smoothness-pilot/rf1_sub-10317_ses-01_run-1_stage-pre_resample.log)
Units scheduled: 3
Units newly completed: 0
Units verified existing: 0
Units failed: 3

COMMAND EXIT: 1
CHECK SKIPPED: command failed.
```
