# Run Record: phase0-ds003745-build-resampling-manifest

- Timestamp: 20260823-120647
- Branch: main
- Commit: 0119ba2
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260823-120647_phase0-ds003745-build-resampling-manifest.log`
- Command exit: 0
- Check exit: none
- Summary: COMMAND exit 0; CHECK none.

## Command

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/build_resampling_manifest.py --output logs/runlists/ds003745-resampling-ready.tsv --missing-output logs/runlists/ds003745-resampling-missing.tsv 
```

## Log

```text
RUN START: 20260823-120647
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main 0119ba2
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/build_resampling_manifest.py --output logs/runlists/ds003745-resampling-ready.tsv --missing-output logs/runlists/ds003745-resampling-missing.tsv 

Participants considered: 50
Ready run units: 100
Incomplete run units: 0
Ready manifest: /ZPOOL/data/projects/sharedreward-aging/logs/runlists/ds003745-resampling-ready.tsv
Missing report: /ZPOOL/data/projects/sharedreward-aging/logs/runlists/ds003745-resampling-missing.tsv

COMMAND EXIT: 0
```
