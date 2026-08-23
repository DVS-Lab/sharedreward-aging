# Run Record: phase0-build-characterization-manifest

- Timestamp: 20260823-123822
- Branch: main
- Commit: d991508
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260823-123822_phase0-build-characterization-manifest.log`
- Command exit: 1
- Check exit: none
- Summary: COMMAND exit 1; CHECK none.

## Command

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/build_characterization_manifest.py --output logs/runlists/phase0-characterization-ready.tsv --missing-output logs/runlists/phase0-characterization-missing.tsv 
```

## Log

```text
RUN START: 20260823-123822
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main d991508
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/build_characterization_manifest.py --output logs/runlists/phase0-characterization-ready.tsv --missing-output logs/runlists/phase0-characterization-missing.tsv 

Ready characterization units: 200
  ds003745 post_resample_preblur: 100
  ds003745 pre_resample: 100
Incomplete characterization units: 665
Ready manifest: /ZPOOL/data/projects/sharedreward-aging/logs/runlists/phase0-characterization-ready.tsv
Missing report: /ZPOOL/data/projects/sharedreward-aging/logs/runlists/phase0-characterization-missing.tsv
INCOMPLETE rf1 sub-10317 ses-01 run-1 pre_resample: confounds
INCOMPLETE rf1 sub-10317 ses-01 run-2 pre_resample: confounds
INCOMPLETE rf1 sub-10369 ses-01 run-1 pre_resample: confounds
INCOMPLETE rf1 sub-10369 ses-01 run-2 pre_resample: confounds
INCOMPLETE rf1 sub-10402 ses-01 run-1 pre_resample: confounds
INCOMPLETE rf1 sub-10402 ses-01 run-2 pre_resample: confounds
INCOMPLETE rf1 sub-10418 ses-01 run-1 pre_resample: confounds
INCOMPLETE rf1 sub-10418 ses-01 run-2 pre_resample: confounds
INCOMPLETE rf1 sub-10462 ses-01 run-1 pre_resample: confounds
INCOMPLETE rf1 sub-10478 ses-01 run-1 pre_resample: confounds
INCOMPLETE rf1 sub-10478 ses-01 run-2 pre_resample: confounds
INCOMPLETE rf1 sub-10486 ses-01 run-1 pre_resample: confounds
INCOMPLETE rf1 sub-10486 ses-01 run-2 pre_resample: confounds
INCOMPLETE rf1 sub-10529 ses-01 run-1 pre_resample: confounds
INCOMPLETE rf1 sub-10529 ses-01 run-2 pre_resample: confounds
INCOMPLETE rf1 sub-10541 ses-01 run-1 pre_resample: confounds
INCOMPLETE rf1 sub-10541 ses-01 run-2 pre_resample: confounds
INCOMPLETE rf1 sub-10559 ses-01 run-1 pre_resample: confounds
INCOMPLETE rf1 sub-10559 ses-01 run-2 pre_resample: confounds
INCOMPLETE rf1 sub-10572 ses-01 run-1 pre_resample: confounds

COMMAND EXIT: 1
```
