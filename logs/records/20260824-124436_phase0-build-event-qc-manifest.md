# Run Record: phase0-build-event-qc-manifest

- Timestamp: 20260824-124436
- Branch: main
- Commit: 0811480
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260824-124436_phase0-build-event-qc-manifest.log`
- Command exit: 1
- Check exit: none
- Summary: COMMAND exit 1; CHECK none.

## Command

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/build_event_qc_manifest.py --target-manifest logs/runlists/target-smoothing-6mm-ready.tsv --output logs/runlists/event-qc-ready.tsv --missing-output logs/records/event-qc-source-missing.tsv 
```

## Log

```text
RUN START: 20260824-124436
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main 0811480
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/build_event_qc_manifest.py --target-manifest logs/runlists/target-smoothing-6mm-ready.tsv --output logs/runlists/event-qc-ready.tsv --missing-output logs/records/event-qc-source-missing.tsv 

Ready event-QC units: 758
Incomplete event-QC units: 7
Ready manifest: /ZPOOL/data/projects/sharedreward-aging/logs/runlists/event-qc-ready.tsv
Missing report: /ZPOOL/data/projects/sharedreward-aging/logs/records/event-qc-source-missing.tsv
INCOMPLETE rf1 sub-11450 ses-01 run-2: missing_source_events
INCOMPLETE rf1 sub-11969 ses-01 run-1: missing_source_events
INCOMPLETE rf1 sub-11969 ses-01 run-2: missing_source_events
INCOMPLETE rf1 sub-11984 ses-01 run-1: missing_source_events
INCOMPLETE rf1 sub-12020 ses-01 run-1: missing_source_events
INCOMPLETE rf1 sub-12036 ses-01 run-2: missing_source_events
INCOMPLETE rf1 sub-12037 ses-01 run-2: missing_source_events

COMMAND EXIT: 1
```
