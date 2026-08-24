# Run Record: phase0-target-smoothing-6mm-final-audit

- Timestamp: 20260823-225106
- Branch: main
- Commit: 2a1a86d
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260823-225106_phase0-target-smoothing-6mm-final-audit.log`
- Command exit: 1
- Check exit: none
- Summary: COMMAND exit 1; CHECK none.

## Command

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/audit_target_smoothing.py --manifest logs/runlists/target-smoothing-6mm-ready.tsv --output logs/records/target-smoothing-6mm-final-audit.tsv --missing-output logs/records/target-smoothing-6mm-final-missing.tsv --fail-on-incomplete 
```

## Log

```text
RUN START: 20260823-225106
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main 2a1a86d
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/audit_target_smoothing.py --manifest logs/runlists/target-smoothing-6mm-ready.tsv --output logs/records/target-smoothing-6mm-final-audit.tsv --missing-output logs/records/target-smoothing-6mm-final-missing.tsv --fail-on-incomplete 

Target-smoothed units checked: 765
Complete target-smoothed units: 764
Incomplete target-smoothed units: 1
  ds003745: n=100; classic mean=5.7749, median=5.7794, range=5.5219-5.9934; ACF-effective mean=8.6983, median=8.7008, range=8.3652-9.0837
  rf1: n=664; classic mean=5.8529, median=5.8543, range=5.4327-6.1602; ACF-effective mean=8.8021, median=8.7537, range=8.0673-9.8665
Consolidated audit: /ZPOOL/data/projects/sharedreward-aging/logs/records/target-smoothing-6mm-final-audit.tsv
Missing report: /ZPOOL/data/projects/sharedreward-aging/logs/records/target-smoothing-6mm-final-missing.tsv
INCOMPLETE rf1 sub-10657 ses-01 run-1: classic_outside_tolerance

COMMAND EXIT: 1
```
