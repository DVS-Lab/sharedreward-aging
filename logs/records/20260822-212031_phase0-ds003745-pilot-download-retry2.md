# Run Record: phase0-ds003745-pilot-download-retry2

- Timestamp: 20260822-212031
- Branch: main
- Commit: a5f60dd
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260822-212031_phase0-ds003745-pilot-download-retry2.log`
- Command exit: 0
- Check exit: 0
- Summary: CHECK PASSED: all pilot imaging inputs are locally available.

## Command

```bash
bash code/get_ds003745.sh --subject 104 --subject 105 --subject 140 --subject 141 
```

## Check

```bash
bash -c $'\n    source code/project_config.sh\n    missing=0\n\n    for subject in 104 105 140 141; do\n      required=(\n        "sub-${subject}/anat/sub-${subject}_T1w.nii.gz"\n        "sub-${subject}/func/sub-${subject}_task-sharedreward_run-01_bold.nii.gz"\n        "sub-${subject}/func/sub-${subject}_task-sharedreward_run-02_bold.nii.gz"\n        "sub-${subject}/fmap/sub-${subject}_magnitude1.nii.gz"\n        "sub-${subject}/fmap/sub-${subject}_magnitude2.nii.gz"\n        "sub-${subject}/fmap/sub-${subject}_phasediff.nii.gz"\n      )\n\n      for relative_path in "${required[@]}"; do\n        if [[ -s "${DS003745_ROOT}/${relative_path}" ]]; then\n          printf "OK: %s\\n" "$relative_path"\n        else\n          printf "MISSING: %s\\n" "$relative_path"\n          missing=1\n        fi\n      done\n    done\n\n    (( missing == 0 )) || exit 1\n    echo "CHECK PASSED: all pilot imaging inputs are locally available."\n  ' 
```

## Log

```text
RUN START: 20260822-212031
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main a5f60dd
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: bash code/get_ds003745.sh --subject 104 --subject 105 --subject 140 --subject 141 

git -C /ZPOOL/data/projects/sharedreward-aging/sourcedata/ds003745 checkout 2.1.1 
HEAD is now at cc3fee633f [OpenNeuro] Recorded changes
datalad -C /ZPOOL/data/projects/sharedreward-aging/sourcedata/ds003745 get -d . sub-104/anat sub-104/func/sub-104_task-sharedreward_run-01_bold.nii.gz sub-104/func/sub-104_task-sharedreward_run-02_bold.nii.gz sub-104/fmap 
get(ok): sub-104/func/sub-104_task-sharedreward_run-01_bold.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-104/func/sub-104_task-sharedreward_run-02_bold.nii.gz (file) [from s3-PUBLIC...]
action summary:
  get (notneeded: 2, ok: 2)
datalad -C /ZPOOL/data/projects/sharedreward-aging/sourcedata/ds003745 get -d . sub-105/anat sub-105/func/sub-105_task-sharedreward_run-01_bold.nii.gz sub-105/func/sub-105_task-sharedreward_run-02_bold.nii.gz sub-105/fmap 
get(ok): sub-105/func/sub-105_task-sharedreward_run-02_bold.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-105/fmap/sub-105_magnitude1.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-105/fmap/sub-105_magnitude2.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-105/fmap/sub-105_phasediff.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-105/anat/sub-105_T1w.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-105/anat/sub-105_T2w.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-105/func/sub-105_task-sharedreward_run-01_bold.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-105/fmap (directory)
get(ok): sub-105/anat (directory)
action summary:
  get (ok: 9)
datalad -C /ZPOOL/data/projects/sharedreward-aging/sourcedata/ds003745 get -d . sub-140/anat sub-140/func/sub-140_task-sharedreward_run-01_bold.nii.gz sub-140/func/sub-140_task-sharedreward_run-02_bold.nii.gz sub-140/fmap 
get(ok): sub-140/func/sub-140_task-sharedreward_run-02_bold.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-140/anat/sub-140_T1w.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-140/anat/sub-140_T2w.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-140/func/sub-140_task-sharedreward_run-01_bold.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-140/fmap/sub-140_magnitude1.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-140/fmap/sub-140_magnitude2.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-140/fmap/sub-140_phasediff.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-140/anat (directory)
get(ok): sub-140/fmap (directory)
action summary:
  get (ok: 9)
datalad -C /ZPOOL/data/projects/sharedreward-aging/sourcedata/ds003745 get -d . sub-141/anat sub-141/func/sub-141_task-sharedreward_run-01_bold.nii.gz sub-141/func/sub-141_task-sharedreward_run-02_bold.nii.gz sub-141/fmap 
get(ok): sub-141/fmap/sub-141_magnitude1.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-141/fmap/sub-141_magnitude2.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-141/fmap/sub-141_phasediff.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-141/anat/sub-141_T1w.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-141/anat/sub-141_T2w.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-141/func/sub-141_task-sharedreward_run-02_bold.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-141/func/sub-141_task-sharedreward_run-01_bold.nii.gz (file) [from s3-PUBLIC...]
get(ok): sub-141/fmap (directory)
get(ok): sub-141/anat (directory)
action summary:
  get (ok: 9)

COMMAND EXIT: 0

CHECK COMMAND: bash -c $'\n    source code/project_config.sh\n    missing=0\n\n    for subject in 104 105 140 141; do\n      required=(\n        "sub-${subject}/anat/sub-${subject}_T1w.nii.gz"\n        "sub-${subject}/func/sub-${subject}_task-sharedreward_run-01_bold.nii.gz"\n        "sub-${subject}/func/sub-${subject}_task-sharedreward_run-02_bold.nii.gz"\n        "sub-${subject}/fmap/sub-${subject}_magnitude1.nii.gz"\n        "sub-${subject}/fmap/sub-${subject}_magnitude2.nii.gz"\n        "sub-${subject}/fmap/sub-${subject}_phasediff.nii.gz"\n      )\n\n      for relative_path in "${required[@]}"; do\n        if [[ -s "${DS003745_ROOT}/${relative_path}" ]]; then\n          printf "OK: %s\\n" "$relative_path"\n        else\n          printf "MISSING: %s\\n" "$relative_path"\n          missing=1\n        fi\n      done\n    done\n\n    (( missing == 0 )) || exit 1\n    echo "CHECK PASSED: all pilot imaging inputs are locally available."\n  ' 

OK: sub-104/anat/sub-104_T1w.nii.gz
OK: sub-104/func/sub-104_task-sharedreward_run-01_bold.nii.gz
OK: sub-104/func/sub-104_task-sharedreward_run-02_bold.nii.gz
OK: sub-104/fmap/sub-104_magnitude1.nii.gz
OK: sub-104/fmap/sub-104_magnitude2.nii.gz
OK: sub-104/fmap/sub-104_phasediff.nii.gz
OK: sub-105/anat/sub-105_T1w.nii.gz
OK: sub-105/func/sub-105_task-sharedreward_run-01_bold.nii.gz
OK: sub-105/func/sub-105_task-sharedreward_run-02_bold.nii.gz
OK: sub-105/fmap/sub-105_magnitude1.nii.gz
OK: sub-105/fmap/sub-105_magnitude2.nii.gz
OK: sub-105/fmap/sub-105_phasediff.nii.gz
OK: sub-140/anat/sub-140_T1w.nii.gz
OK: sub-140/func/sub-140_task-sharedreward_run-01_bold.nii.gz
OK: sub-140/func/sub-140_task-sharedreward_run-02_bold.nii.gz
OK: sub-140/fmap/sub-140_magnitude1.nii.gz
OK: sub-140/fmap/sub-140_magnitude2.nii.gz
OK: sub-140/fmap/sub-140_phasediff.nii.gz
OK: sub-141/anat/sub-141_T1w.nii.gz
OK: sub-141/func/sub-141_task-sharedreward_run-01_bold.nii.gz
OK: sub-141/func/sub-141_task-sharedreward_run-02_bold.nii.gz
OK: sub-141/fmap/sub-141_magnitude1.nii.gz
OK: sub-141/fmap/sub-141_magnitude2.nii.gz
OK: sub-141/fmap/sub-141_phasediff.nii.gz
CHECK PASSED: all pilot imaging inputs are locally available.

CHECK EXIT: 0
```
