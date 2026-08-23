# Run Record: phase0-build-characterization-manifest-corrected

- Timestamp: 20260823-124636
- Branch: main
- Commit: 4f69acc
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260823-124636_phase0-build-characterization-manifest-corrected.log`
- Command exit: 0
- Check exit: none
- Summary: COMMAND exit 0; CHECK none.

## Command

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/build_characterization_manifest.py --output logs/runlists/phase0-characterization-ready.tsv --missing-output logs/runlists/phase0-characterization-missing.tsv 
```

## Log

```text
RUN START: 20260823-124636
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main 4f69acc
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/build_characterization_manifest.py --output logs/runlists/phase0-characterization-ready.tsv --missing-output logs/runlists/phase0-characterization-missing.tsv 

Ready characterization units: 865
  ds003745 post_resample_preblur: 100
  ds003745 pre_resample: 100
  rf1 pre_resample: 665
Incomplete characterization units: 0
Ready manifest: /ZPOOL/data/projects/sharedreward-aging/logs/runlists/phase0-characterization-ready.tsv
Missing report: /ZPOOL/data/projects/sharedreward-aging/logs/runlists/phase0-characterization-missing.tsv

COMMAND EXIT: 0
```
