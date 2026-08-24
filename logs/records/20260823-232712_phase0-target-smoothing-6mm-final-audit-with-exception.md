# Run Record: phase0-target-smoothing-6mm-final-audit-with-exception

- Timestamp: 20260823-232712
- Branch: main
- Commit: aaeb171
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260823-232712_phase0-target-smoothing-6mm-final-audit-with-exception.log`
- Command exit: 0
- Check exit: none
- Summary: CHECK PASSED: every target-smoothed run passed geometry and smoothness QC or a bounded, documented run-specific exception.

## Command

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/audit_target_smoothing.py --manifest logs/runlists/target-smoothing-6mm-ready.tsv --output logs/records/target-smoothing-6mm-final-audit.tsv --missing-output logs/records/target-smoothing-6mm-final-missing.tsv --fail-on-incomplete 
```

## Log

```text
RUN START: 20260823-232712
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main aaeb171
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/audit_target_smoothing.py --manifest logs/runlists/target-smoothing-6mm-ready.tsv --output logs/records/target-smoothing-6mm-final-audit.tsv --missing-output logs/records/target-smoothing-6mm-final-missing.tsv --fail-on-incomplete 

Target-smoothed units checked: 765
Complete target-smoothed units: 765
Conventionally passing units: 764
Accepted QC exceptions: 1
Incomplete target-smoothed units: 0
  ds003745: n=100; classic mean=5.7749, median=5.7794, range=5.5219-5.9934; ACF-effective mean=8.6983, median=8.7008, range=8.3652-9.0837
  rf1: n=665; classic mean=5.8520, median=5.8542, range=5.2800-6.1602; ACF-effective mean=8.8007, median=8.7535, range=7.8540-9.8665
Consolidated audit: /ZPOOL/data/projects/sharedreward-aging/logs/records/target-smoothing-6mm-final-audit.tsv
Missing report: /ZPOOL/data/projects/sharedreward-aging/logs/records/target-smoothing-6mm-final-missing.tsv
ACCEPTED EXCEPTION rf1 sub-10657 ses-01 run-1: classic=5.27996 mm; accepted range=5.27-5.29 mm
CHECK PASSED: every target-smoothed run passed geometry and smoothness QC or a bounded, documented run-specific exception.

COMMAND EXIT: 0
```
