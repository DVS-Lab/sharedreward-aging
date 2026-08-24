# Run Record: phase0-susan-vs-afni-6mm-pilot

- Timestamp: 20260823-204219
- Branch: main
- Commit: 67d5d25
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260823-204219_phase0-susan-vs-afni-6mm-pilot.log`
- Command exit: 0
- Check exit: 0
- Summary: CHECK PASSED: both datasets have complete three-method comparisons.

## Command

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/run_susan_comparison.py --manifest logs/runlists/susan-vs-afni-6mm-pilot.tsv --jobs 2 --log-dir logs/susan-vs-afni-6mm-pilot --work-root work/susan-vs-afni-6mm-pilot 
```

## Check

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/audit_susan_comparison.py --manifest logs/runlists/susan-vs-afni-6mm-pilot.tsv --output logs/records/susan-vs-afni-6mm-pilot.tsv --missing-output logs/records/susan-vs-afni-6mm-pilot-missing.tsv --fail-on-incomplete 
```

## Log

```text
RUN START: 20260823-204219
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main 67d5d25
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/run_susan_comparison.py --manifest logs/runlists/susan-vs-afni-6mm-pilot.tsv --jobs 2 --log-dir logs/susan-vs-afni-6mm-pilot --work-root work/susan-vs-afni-6mm-pilot 

SUSAN comparison plan: 2 unit(s), jobs=2
DONE: ds003745_sub-118_run-02
DONE: rf1_sub-11720_ses-01_run-1
Units completed: 2
Units failed: 0
CHECK PASSED: all SUSAN comparison images and AFNI measurements are complete.

COMMAND EXIT: 0

CHECK COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/audit_susan_comparison.py --manifest logs/runlists/susan-vs-afni-6mm-pilot.tsv --output logs/records/susan-vs-afni-6mm-pilot.tsv --missing-output logs/records/susan-vs-afni-6mm-pilot-missing.tsv --fail-on-incomplete 

Comparison units checked: 2
Complete method measurements: 6 of 6
Incomplete units: 0
  ds003745 sub-118 ses-none run-02: baseline=4.0187; AFNI-total-target=5.9934; SUSAN-kernel=8.8640; Gaussian-quadrature expectation=7.2215; SUSAN effective-added=7.9006; SUSAN-minus-AFNI=+2.8706 mm
  rf1 sub-11720 ses-01 run-1: baseline=4.6190; AFNI-total-target=5.7278; SUSAN-kernel=10.1081; Gaussian-quadrature expectation=7.5720; SUSAN effective-added=8.9910; SUSAN-minus-AFNI=+4.3803 mm
Audit: /ZPOOL/data/projects/sharedreward-aging/logs/records/susan-vs-afni-6mm-pilot.tsv
Missing report: /ZPOOL/data/projects/sharedreward-aging/logs/records/susan-vs-afni-6mm-pilot-missing.tsv
CHECK PASSED: both datasets have complete three-method comparisons.

CHECK EXIT: 0
```
