# Run Record: phase0-ds003745-pilot-download-retry

- Timestamp: 20260822-210855
- Branch: main
- Commit: 3e47eb5
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260822-210855_phase0-ds003745-pilot-download-retry.log`
- Command exit: 1
- Check exit: none
- Summary: COMMAND exit 1; CHECK none.

## Command

```bash
bash code/get_ds003745.sh --subject 104 --subject 105 --subject 140 --subject 141 
```

## Log

```text
RUN START: 20260822-210855
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main 3e47eb5
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: bash code/get_ds003745.sh --subject 104 --subject 105 --subject 140 --subject 141 

git -C /ZPOOL/data/projects/sharedreward-aging/sourcedata/ds003745 checkout 2.1.1 
HEAD is now at cc3fee633f [OpenNeuro] Recorded changes
datalad -C /ZPOOL/data/projects/sharedreward-aging/sourcedata/ds003745 get -d . sub-104/anat sub-104/func/\*task-sharedreward\* sub-104/fmap 
get(impossible): sub-104/func/*task-sharedreward* [path does not exist]
get(ok): sub-104/fmap/sub-104_magnitude1.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-104/fmap/sub-104_magnitude2.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-104/fmap/sub-104_phasediff.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-104/anat/sub-104_T1w.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-104/anat/sub-104_T2w.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-104/fmap (directory)
get(ok): sub-104/anat (directory)
action summary:
  get (impossible: 1, ok: 7)

COMMAND EXIT: 1
```
