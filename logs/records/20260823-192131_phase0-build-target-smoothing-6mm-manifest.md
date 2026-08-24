# Run Record: phase0-build-target-smoothing-6mm-manifest

- Timestamp: 20260823-192131
- Branch: main
- Commit: e0264d3
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260823-192131_phase0-build-target-smoothing-6mm-manifest.log`
- Command exit: 0
- Check exit: none
- Summary: COMMAND exit 0; CHECK none.

## Command

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/build_target_smoothing_manifest.py --output logs/runlists/target-smoothing-6mm-ready.tsv --missing-output logs/runlists/target-smoothing-6mm-missing.tsv 
```

## Log

```text
RUN START: 20260823-192131
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main e0264d3
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/build_target_smoothing_manifest.py --output logs/runlists/target-smoothing-6mm-ready.tsv --missing-output logs/runlists/target-smoothing-6mm-missing.tsv 

Target classic FWHM: 6 mm
Ready target-smoothing units: 765
  ds003745: 100
  rf1: 665
Incomplete target-smoothing units: 0
Ready manifest: /ZPOOL/data/projects/sharedreward-aging/logs/runlists/target-smoothing-6mm-ready.tsv
Missing report: /ZPOOL/data/projects/sharedreward-aging/logs/runlists/target-smoothing-6mm-missing.tsv

COMMAND EXIT: 0
```
