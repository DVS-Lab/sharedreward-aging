# Run Record: phase0-rf1-low-coverage-mosaics

- Timestamp: 20260824-152215
- Branch: main
- Commit: ab4bd3e
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260824-152215_phase0-rf1-low-coverage-mosaics.log`
- Command exit: 0
- Check exit: none
- Summary: COMMAND exit 0; CHECK none.

## Command

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/plot_coverage_mosaics.py --input logs/records/analysis-qc-run-level.tsv --dataset rf1 --coverage-below 95 --slices 6 --output-dir qc/coverage-mosaics --summary-output logs/records/coverage-mosaics.tsv 
```

## Log

```text
RUN START: 20260824-152215
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main ab4bd3e
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/plot_coverage_mosaics.py --input logs/records/analysis-qc-run-level.tsv --dataset rf1 --coverage-below 95 --slices 6 --output-dir qc/coverage-mosaics --summary-output logs/records/coverage-mosaics.tsv 

Mosaic: /ZPOOL/data/projects/sharedreward-aging/qc/coverage-mosaics/rf1_sub-11472_ses-01_run-1_coverage-92.42.png
Mosaic: /ZPOOL/data/projects/sharedreward-aging/qc/coverage-mosaics/rf1_sub-11719_ses-01_run-1_coverage-88.60.png
Mosaic: /ZPOOL/data/projects/sharedreward-aging/qc/coverage-mosaics/rf1_sub-11960_ses-01_run-1_coverage-89.16.png
Mosaic: /ZPOOL/data/projects/sharedreward-aging/qc/coverage-mosaics/rf1_sub-11960_ses-01_run-2_coverage-80.74.png
Coverage mosaics created: 4
Summary: /ZPOOL/data/projects/sharedreward-aging/logs/records/coverage-mosaics.tsv

COMMAND EXIT: 0
```
