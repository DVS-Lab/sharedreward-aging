# Run Record: phase0-rebuild-analysis-qc-corrected-coverage

- Timestamp: 20260824-102229
- Branch: main
- Commit: edd95bc
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260824-102229_phase0-rebuild-analysis-qc-corrected-coverage.log`
- Command exit: 0
- Check exit: none
- Summary: COMMAND exit 0; CHECK none.

## Command

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/build_analysis_qc_manifest.py --output logs/runlists/analysis-qc-ready.tsv --missing-output logs/runlists/analysis-qc-missing.tsv 
```

## Log

```text
RUN START: 20260824-102229
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main edd95bc
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/build_analysis_qc_manifest.py --output logs/runlists/analysis-qc-ready.tsv --missing-output logs/runlists/analysis-qc-missing.tsv 

Ready post-smoothing analysis-QC units: 765
  ds003745: 100
  rf1: 665
Incomplete analysis-QC units: 0
Ready manifest: /ZPOOL/data/projects/sharedreward-aging/logs/runlists/analysis-qc-ready.tsv
Missing report: /ZPOOL/data/projects/sharedreward-aging/logs/runlists/analysis-qc-missing.tsv

COMMAND EXIT: 0
```
