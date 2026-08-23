# Run Record: phase0-ds003745-rf1-grid-resampling

- Timestamp: 20260823-120728
- Branch: main
- Commit: 0119ba2
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260823-120728_phase0-ds003745-rf1-grid-resampling.log`
- Command exit: 1
- Check exit: none
- Summary: COMMAND exit 1; CHECK none.

## Command

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/run_resampling_batch.py --manifest logs/runlists/ds003745-resampling-ready.tsv --jobs 8 --log-dir logs/ds003745-resampling-current 
```

## Log

```text
RUN START: 20260823-120728
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main 0119ba2
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/run_resampling_batch.py --manifest logs/runlists/ds003745-resampling-ready.tsv --jobs 8 --log-dir logs/ds003745-resampling-current 

RF1-grid resampling plan: 100 run unit(s), jobs=8, overwrite=false
Reference: /ZPOOL/data/projects/rf1-sra-sharedreward/resources/rf1_MNI152NLin6Asym_reference_grid.nii.gz
Per-unit logs: logs/ds003745-resampling-current
START: sub-106 run-01
START: sub-106 run-02
START: sub-109 run-01
START: sub-109 run-02
START: sub-104 run-01
START: sub-104 run-02
START: sub-110 run-01
START: sub-110 run-02
START: sub-105 run-01
START: sub-105 run-02
START: sub-108 run-01
START: sub-108 run-02
START: sub-107 run-01
START: sub-107 run-02
START: sub-111 run-01
START: sub-111 run-02
START: sub-112 run-01
START: sub-112 run-02
START: sub-113 run-01
START: sub-113 run-02
START: sub-115 run-01
START: sub-115 run-02
START: sub-116 run-01
START: sub-116 run-02
START: sub-117 run-01
START: sub-117 run-02
START: sub-118 run-01
START: sub-118 run-02
START: sub-120 run-01
START: sub-120 run-02
START: sub-121 run-01
START: sub-121 run-02
START: sub-122 run-01
START: sub-122 run-02
START: sub-124 run-01
START: sub-124 run-02
START: sub-125 run-01
START: sub-125 run-02
START: sub-126 run-01
START: sub-126 run-02
START: sub-127 run-01
START: sub-127 run-02
START: sub-128 run-01
START: sub-128 run-02
START: sub-129 run-01
START: sub-129 run-02
START: sub-130 run-01
START: sub-130 run-02
START: sub-131 run-01
START: sub-131 run-02
START: sub-132 run-01
START: sub-132 run-02
START: sub-133 run-01
START: sub-133 run-02
START: sub-134 run-01
START: sub-134 run-02
START: sub-135 run-01
START: sub-135 run-02
START: sub-136 run-01
START: sub-136 run-02
START: sub-137 run-01
START: sub-137 run-02
START: sub-138 run-01
START: sub-138 run-02
START: sub-140 run-01
START: sub-140 run-02
START: sub-141 run-01
START: sub-141 run-02
START: sub-142 run-01
START: sub-142 run-02
START: sub-143 run-01
START: sub-143 run-02
START: sub-144 run-01
START: sub-144 run-02
START: sub-145 run-01
START: sub-145 run-02
START: sub-147 run-01
START: sub-147 run-02
START: sub-149 run-01
START: sub-149 run-02
START: sub-150 run-01
START: sub-150 run-02
START: sub-151 run-01
START: sub-151 run-02
START: sub-152 run-01
START: sub-152 run-02
START: sub-153 run-01
START: sub-153 run-02
START: sub-154 run-01
START: sub-154 run-02
START: sub-156 run-01
START: sub-156 run-02
START: sub-155 run-01
START: sub-155 run-02
START: sub-157 run-01
START: sub-157 run-02
START: sub-158 run-01
START: sub-158 run-02
START: sub-159 run-01
START: sub-159 run-02
ERROR: failed resampling unit: sub-106 run-02 (log: logs/ds003745-resampling-current/sub-106_run-02.log)
ERROR: failed resampling unit: sub-109 run-02 (log: logs/ds003745-resampling-current/sub-109_run-02.log)
ERROR: failed resampling unit: sub-106 run-01 (log: logs/ds003745-resampling-current/sub-106_run-01.log)
ERROR: failed resampling unit: sub-110 run-02 (log: logs/ds003745-resampling-current/sub-110_run-02.log)
ERROR: failed resampling unit: sub-109 run-01 (log: logs/ds003745-resampling-current/sub-109_run-01.log)
ERROR: failed resampling unit: sub-110 run-01 (log: logs/ds003745-resampling-current/sub-110_run-01.log)
ERROR: failed resampling unit: sub-104 run-02 (log: logs/ds003745-resampling-current/sub-104_run-02.log)
ERROR: failed resampling unit: sub-104 run-01 (log: logs/ds003745-resampling-current/sub-104_run-01.log)
ERROR: failed resampling unit: sub-107 run-01 (log: logs/ds003745-resampling-current/sub-107_run-01.log)
ERROR: failed resampling unit: sub-108 run-01 (log: logs/ds003745-resampling-current/sub-108_run-01.log)
ERROR: failed resampling unit: sub-108 run-02 (log: logs/ds003745-resampling-current/sub-108_run-02.log)
ERROR: failed resampling unit: sub-107 run-02 (log: logs/ds003745-resampling-current/sub-107_run-02.log)
ERROR: failed resampling unit: sub-105 run-01 (log: logs/ds003745-resampling-current/sub-105_run-01.log)
ERROR: failed resampling unit: sub-105 run-02 (log: logs/ds003745-resampling-current/sub-105_run-02.log)
ERROR: failed resampling unit: sub-111 run-01 (log: logs/ds003745-resampling-current/sub-111_run-01.log)
ERROR: failed resampling unit: sub-111 run-02 (log: logs/ds003745-resampling-current/sub-111_run-02.log)
ERROR: failed resampling unit: sub-112 run-02 (log: logs/ds003745-resampling-current/sub-112_run-02.log)
ERROR: failed resampling unit: sub-112 run-01 (log: logs/ds003745-resampling-current/sub-112_run-01.log)
ERROR: failed resampling unit: sub-113 run-02 (log: logs/ds003745-resampling-current/sub-113_run-02.log)
ERROR: failed resampling unit: sub-113 run-01 (log: logs/ds003745-resampling-current/sub-113_run-01.log)
ERROR: failed resampling unit: sub-115 run-01 (log: logs/ds003745-resampling-current/sub-115_run-01.log)
ERROR: failed resampling unit: sub-115 run-02 (log: logs/ds003745-resampling-current/sub-115_run-02.log)
ERROR: failed resampling unit: sub-116 run-01 (log: logs/ds003745-resampling-current/sub-116_run-01.log)
ERROR: failed resampling unit: sub-116 run-02 (log: logs/ds003745-resampling-current/sub-116_run-02.log)
ERROR: failed resampling unit: sub-117 run-02 (log: logs/ds003745-resampling-current/sub-117_run-02.log)
ERROR: failed resampling unit: sub-117 run-01 (log: logs/ds003745-resampling-current/sub-117_run-01.log)
ERROR: failed resampling unit: sub-118 run-02 (log: logs/ds003745-resampling-current/sub-118_run-02.log)
ERROR: failed resampling unit: sub-118 run-01 (log: logs/ds003745-resampling-current/sub-118_run-01.log)
ERROR: failed resampling unit: sub-120 run-01 (log: logs/ds003745-resampling-current/sub-120_run-01.log)
ERROR: failed resampling unit: sub-120 run-02 (log: logs/ds003745-resampling-current/sub-120_run-02.log)
ERROR: failed resampling unit: sub-121 run-01 (log: logs/ds003745-resampling-current/sub-121_run-01.log)
ERROR: failed resampling unit: sub-121 run-02 (log: logs/ds003745-resampling-current/sub-121_run-02.log)
ERROR: failed resampling unit: sub-124 run-01 (log: logs/ds003745-resampling-current/sub-124_run-01.log)
ERROR: failed resampling unit: sub-122 run-02 (log: logs/ds003745-resampling-current/sub-122_run-02.log)
ERROR: failed resampling unit: sub-122 run-01 (log: logs/ds003745-resampling-current/sub-122_run-01.log)
ERROR: failed resampling unit: sub-124 run-02 (log: logs/ds003745-resampling-current/sub-124_run-02.log)
ERROR: failed resampling unit: sub-125 run-01 (log: logs/ds003745-resampling-current/sub-125_run-01.log)
ERROR: failed resampling unit: sub-125 run-02 (log: logs/ds003745-resampling-current/sub-125_run-02.log)
ERROR: failed resampling unit: sub-126 run-01 (log: logs/ds003745-resampling-current/sub-126_run-01.log)
ERROR: failed resampling unit: sub-126 run-02 (log: logs/ds003745-resampling-current/sub-126_run-02.log)
ERROR: failed resampling unit: sub-128 run-01 (log: logs/ds003745-resampling-current/sub-128_run-01.log)
ERROR: failed resampling unit: sub-127 run-01 (log: logs/ds003745-resampling-current/sub-127_run-01.log)
ERROR: failed resampling unit: sub-127 run-02 (log: logs/ds003745-resampling-current/sub-127_run-02.log)
ERROR: failed resampling unit: sub-128 run-02 (log: logs/ds003745-resampling-current/sub-128_run-02.log)
ERROR: failed resampling unit: sub-129 run-01 (log: logs/ds003745-resampling-current/sub-129_run-01.log)
ERROR: failed resampling unit: sub-129 run-02 (log: logs/ds003745-resampling-current/sub-129_run-02.log)
ERROR: failed resampling unit: sub-130 run-01 (log: logs/ds003745-resampling-current/sub-130_run-01.log)
ERROR: failed resampling unit: sub-130 run-02 (log: logs/ds003745-resampling-current/sub-130_run-02.log)
ERROR: failed resampling unit: sub-131 run-01 (log: logs/ds003745-resampling-current/sub-131_run-01.log)
ERROR: failed resampling unit: sub-131 run-02 (log: logs/ds003745-resampling-current/sub-131_run-02.log)
ERROR: failed resampling unit: sub-132 run-01 (log: logs/ds003745-resampling-current/sub-132_run-01.log)
ERROR: failed resampling unit: sub-132 run-02 (log: logs/ds003745-resampling-current/sub-132_run-02.log)
ERROR: failed resampling unit: sub-133 run-01 (log: logs/ds003745-resampling-current/sub-133_run-01.log)
ERROR: failed resampling unit: sub-133 run-02 (log: logs/ds003745-resampling-current/sub-133_run-02.log)
ERROR: failed resampling unit: sub-134 run-01 (log: logs/ds003745-resampling-current/sub-134_run-01.log)
ERROR: failed resampling unit: sub-134 run-02 (log: logs/ds003745-resampling-current/sub-134_run-02.log)
ERROR: failed resampling unit: sub-135 run-01 (log: logs/ds003745-resampling-current/sub-135_run-01.log)
ERROR: failed resampling unit: sub-135 run-02 (log: logs/ds003745-resampling-current/sub-135_run-02.log)
ERROR: failed resampling unit: sub-136 run-02 (log: logs/ds003745-resampling-current/sub-136_run-02.log)
ERROR: failed resampling unit: sub-136 run-01 (log: logs/ds003745-resampling-current/sub-136_run-01.log)
ERROR: failed resampling unit: sub-137 run-01 (log: logs/ds003745-resampling-current/sub-137_run-01.log)
ERROR: failed resampling unit: sub-137 run-02 (log: logs/ds003745-resampling-current/sub-137_run-02.log)
ERROR: failed resampling unit: sub-138 run-01 (log: logs/ds003745-resampling-current/sub-138_run-01.log)
ERROR: failed resampling unit: sub-138 run-02 (log: logs/ds003745-resampling-current/sub-138_run-02.log)
ERROR: failed resampling unit: sub-142 run-01 (log: logs/ds003745-resampling-current/sub-142_run-01.log)
ERROR: failed resampling unit: sub-142 run-02 (log: logs/ds003745-resampling-current/sub-142_run-02.log)
ERROR: failed resampling unit: sub-140 run-01 (log: logs/ds003745-resampling-current/sub-140_run-01.log)
ERROR: failed resampling unit: sub-141 run-01 (log: logs/ds003745-resampling-current/sub-141_run-01.log)
ERROR: failed resampling unit: sub-141 run-02 (log: logs/ds003745-resampling-current/sub-141_run-02.log)
ERROR: failed resampling unit: sub-143 run-01 (log: logs/ds003745-resampling-current/sub-143_run-01.log)
ERROR: failed resampling unit: sub-143 run-02 (log: logs/ds003745-resampling-current/sub-143_run-02.log)
ERROR: failed resampling unit: sub-140 run-02 (log: logs/ds003745-resampling-current/sub-140_run-02.log)
ERROR: failed resampling unit: sub-144 run-01 (log: logs/ds003745-resampling-current/sub-144_run-01.log)
ERROR: failed resampling unit: sub-144 run-02 (log: logs/ds003745-resampling-current/sub-144_run-02.log)
ERROR: failed resampling unit: sub-145 run-01 (log: logs/ds003745-resampling-current/sub-145_run-01.log)
ERROR: failed resampling unit: sub-145 run-02 (log: logs/ds003745-resampling-current/sub-145_run-02.log)
ERROR: failed resampling unit: sub-147 run-01 (log: logs/ds003745-resampling-current/sub-147_run-01.log)
ERROR: failed resampling unit: sub-147 run-02 (log: logs/ds003745-resampling-current/sub-147_run-02.log)
ERROR: failed resampling unit: sub-149 run-01 (log: logs/ds003745-resampling-current/sub-149_run-01.log)
ERROR: failed resampling unit: sub-149 run-02 (log: logs/ds003745-resampling-current/sub-149_run-02.log)
ERROR: failed resampling unit: sub-150 run-01 (log: logs/ds003745-resampling-current/sub-150_run-01.log)
ERROR: failed resampling unit: sub-150 run-02 (log: logs/ds003745-resampling-current/sub-150_run-02.log)
ERROR: failed resampling unit: sub-151 run-01 (log: logs/ds003745-resampling-current/sub-151_run-01.log)
ERROR: failed resampling unit: sub-151 run-02 (log: logs/ds003745-resampling-current/sub-151_run-02.log)
ERROR: failed resampling unit: sub-152 run-01 (log: logs/ds003745-resampling-current/sub-152_run-01.log)
ERROR: failed resampling unit: sub-153 run-01 (log: logs/ds003745-resampling-current/sub-153_run-01.log)
ERROR: failed resampling unit: sub-152 run-02 (log: logs/ds003745-resampling-current/sub-152_run-02.log)
ERROR: failed resampling unit: sub-153 run-02 (log: logs/ds003745-resampling-current/sub-153_run-02.log)
ERROR: failed resampling unit: sub-154 run-01 (log: logs/ds003745-resampling-current/sub-154_run-01.log)
ERROR: failed resampling unit: sub-154 run-02 (log: logs/ds003745-resampling-current/sub-154_run-02.log)
ERROR: failed resampling unit: sub-156 run-01 (log: logs/ds003745-resampling-current/sub-156_run-01.log)
ERROR: failed resampling unit: sub-156 run-02 (log: logs/ds003745-resampling-current/sub-156_run-02.log)
ERROR: failed resampling unit: sub-155 run-01 (log: logs/ds003745-resampling-current/sub-155_run-01.log)
ERROR: failed resampling unit: sub-157 run-01 (log: logs/ds003745-resampling-current/sub-157_run-01.log)
ERROR: failed resampling unit: sub-155 run-02 (log: logs/ds003745-resampling-current/sub-155_run-02.log)
ERROR: failed resampling unit: sub-157 run-02 (log: logs/ds003745-resampling-current/sub-157_run-02.log)
ERROR: failed resampling unit: sub-158 run-01 (log: logs/ds003745-resampling-current/sub-158_run-01.log)
ERROR: failed resampling unit: sub-158 run-02 (log: logs/ds003745-resampling-current/sub-158_run-02.log)
ERROR: failed resampling unit: sub-159 run-02 (log: logs/ds003745-resampling-current/sub-159_run-02.log)
ERROR: failed resampling unit: sub-159 run-01 (log: logs/ds003745-resampling-current/sub-159_run-01.log)
Run units scheduled: 100
Run units completed: 0
Run units failed: 100

COMMAND EXIT: 1
```
