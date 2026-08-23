# Run Record: phase0-baseline-smoothness-pilot-retry

- Timestamp: 20260823-125131
- Branch: main
- Commit: 56292e8
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260823-125131_phase0-baseline-smoothness-pilot-retry.log`
- Command exit: 0
- Check exit: 0
- Summary: CHECK PASSED: all baseline smoothness results are complete and valid.

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
RUN START: 20260823-125131
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main 56292e8
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/run_smoothness_batch.py --manifest logs/runlists/phase0-characterization-pilot.tsv --jobs 3 --output-dir derivatives/qc/smoothness/run-level --log-dir logs/smoothness-pilot --work-root work/phase0-smoothness 

Baseline smoothness plan: 3 unit(s), jobs=3, AFNI threads/job=4, overwrite=false
Run-level results: derivatives/qc/smoothness/run-level
Per-unit logs: logs/smoothness-pilot
DONE: ds003745_sub-104_run-01_stage-pre_resample
DONE: ds003745_sub-104_run-01_stage-post_resample_preblur
DONE: rf1_sub-10317_ses-01_run-1_stage-pre_resample
Units scheduled: 3
Units newly completed: 3
Units verified existing: 0
Units failed: 0
CHECK PASSED: every baseline smoothness unit has a validated result.

COMMAND EXIT: 0

CHECK COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/audit_smoothness.py --manifest logs/runlists/phase0-characterization-pilot.tsv --result-dir derivatives/qc/smoothness/run-level --output logs/records/phase0-baseline-smoothness-pilot.tsv --missing-output logs/records/phase0-baseline-smoothness-pilot-missing.tsv --fail-on-incomplete 

Smoothness units checked: 3
Complete smoothness units: 3
  ds003745 post_resample_preblur: 1
  ds003745 pre_resample: 1
  rf1 pre_resample: 1
Incomplete smoothness units: 0
Consolidated table: /ZPOOL/data/projects/sharedreward-aging/logs/records/phase0-baseline-smoothness-pilot.tsv
Missing report: /ZPOOL/data/projects/sharedreward-aging/logs/records/phase0-baseline-smoothness-pilot-missing.tsv
CHECK PASSED: all baseline smoothness results are complete and valid.

CHECK EXIT: 0
```
