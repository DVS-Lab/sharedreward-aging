# Run Record: phase0-ratings-qc-full-retry

- Timestamp: 20260824-122016
- Branch: main
- Commit: 0811480
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260824-122016_phase0-ratings-qc-full-retry.log`
- Command exit: 0
- Check exit: 0
- Summary: CHECK PASSED: the ratings cohort audit has no unresolved source/schema failures.

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
RUN START: 20260824-122016
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main 0811480
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/build_ratings_qc_manifest.py --target-manifest logs/runlists/target-smoothing-6mm-ready.tsv --output logs/runlists/ratings-qc-ready.tsv --missing-output logs/records/ratings-source-unresolved.tsv 

Cohort subjects represented in ratings manifest: 397
Subjects with a resolved ratings source: 367
Subjects with no ratings source (registered exclusion): 30
Subjects requiring ratings-source resolution: 0
Ready manifest: /ZPOOL/data/projects/sharedreward-aging/logs/runlists/ratings-qc-ready.tsv
Missing/ambiguous report: /ZPOOL/data/projects/sharedreward-aging/logs/records/ratings-source-unresolved.tsv

COMMAND EXIT: 0

CHECK COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/audit_ratings_qc.py --manifest logs/runlists/ratings-qc-ready.tsv --output logs/records/ratings-qc-subject-level.tsv --missing-output logs/records/ratings-qc-incomplete.tsv --fail-on-incomplete 

Ratings subjects checked: 397
Complete ratings subjects: 397
Incomplete ratings subjects: 0
Subject-level ratings exclusions: 49
Subjects with review flags: 5
Ratings audit: /ZPOOL/data/projects/sharedreward-aging/logs/records/ratings-qc-subject-level.tsv
Missing report: /ZPOOL/data/projects/sharedreward-aging/logs/records/ratings-qc-incomplete.tsv
CHECK PASSED: the ratings cohort audit has no unresolved source/schema failures.

CHECK EXIT: 0
```
