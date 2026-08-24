# Run Record: phase0-ratings-qc-full

- Timestamp: 20260824-105058
- Branch: main
- Commit: d7ca3c7
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260824-105058_phase0-ratings-qc-full.log`
- Command exit: 1
- Check exit: skipped
- Summary: COMMAND exit 1; CHECK skipped.

## Command

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/build_ratings_qc_manifest.py --target-manifest logs/runlists/target-smoothing-6mm-ready.tsv --output logs/runlists/ratings-qc-ready.tsv --missing-output logs/records/ratings-source-unresolved.tsv 
```

## Check

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/audit_ratings_qc.py --manifest logs/runlists/ratings-qc-ready.tsv --output logs/records/ratings-qc-subject-level.tsv --missing-output logs/records/ratings-qc-incomplete.tsv --fail-on-incomplete 
```

## Log

```text
RUN START: 20260824-105058
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main d7ca3c7
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/build_ratings_qc_manifest.py --target-manifest logs/runlists/target-smoothing-6mm-ready.tsv --output logs/runlists/ratings-qc-ready.tsv --missing-output logs/records/ratings-source-unresolved.tsv 

Cohort subjects represented in ratings manifest: 396
Subjects with a resolved ratings source: 366
Subjects with no ratings source (registered exclusion): 30
Subjects requiring ratings-source resolution: 1
Ready manifest: /ZPOOL/data/projects/sharedreward-aging/logs/runlists/ratings-qc-ready.tsv
Missing/ambiguous report: /ZPOOL/data/projects/sharedreward-aging/logs/records/ratings-source-unresolved.tsv
INCOMPLETE ds003745 sub-104: ambiguous_ratings_files:2

COMMAND EXIT: 1
CHECK SKIPPED: command failed.
```
