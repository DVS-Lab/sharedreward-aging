# Run Record: phase0-ds003745-rf1-grid-resampling-retry

- Timestamp: 20260823-121615
- Branch: main
- Commit: b1307c0
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260823-121615_phase0-ds003745-rf1-grid-resampling-retry.log`
- Command exit: 0
- Check exit: none
- Summary: CHECK PASSED: every ds003745 run has verified RF1-grid BOLD and mask outputs.

## Command

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/run_resampling_batch.py --manifest logs/runlists/ds003745-resampling-ready.tsv --jobs 8 --log-dir logs/ds003745-resampling-current 
```

## Log

```text
RUN START: 20260823-121615
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main b1307c0
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
DONE: sub-106 run-01
DONE: sub-106 run-02
DONE: sub-109 run-01
DONE: sub-110 run-01
DONE: sub-104 run-01
DONE: sub-104 run-02
DONE: sub-109 run-02
DONE: sub-110 run-02
DONE: sub-105 run-01
DONE: sub-105 run-02
DONE: sub-107 run-02
DONE: sub-107 run-01
DONE: sub-111 run-02
DONE: sub-108 run-02
DONE: sub-108 run-01
DONE: sub-111 run-01
DONE: sub-112 run-01
DONE: sub-112 run-02
DONE: sub-113 run-01
DONE: sub-116 run-01
DONE: sub-115 run-01
DONE: sub-113 run-02
DONE: sub-116 run-02
DONE: sub-115 run-02
DONE: sub-117 run-01
DONE: sub-117 run-02
DONE: sub-118 run-01
DONE: sub-120 run-02
DONE: sub-120 run-01
DONE: sub-118 run-02
DONE: sub-121 run-02
DONE: sub-121 run-01
DONE: sub-122 run-01
DONE: sub-124 run-02
DONE: sub-124 run-01
DONE: sub-122 run-02
DONE: sub-125 run-01
DONE: sub-125 run-02
DONE: sub-126 run-01
DONE: sub-126 run-02
DONE: sub-127 run-01
DONE: sub-128 run-01
DONE: sub-129 run-02
DONE: sub-128 run-02
DONE: sub-129 run-01
DONE: sub-127 run-02
DONE: sub-130 run-01
DONE: sub-130 run-02
DONE: sub-131 run-01
DONE: sub-131 run-02
DONE: sub-132 run-02
DONE: sub-133 run-01
DONE: sub-132 run-01
DONE: sub-133 run-02
DONE: sub-134 run-02
DONE: sub-134 run-01
DONE: sub-135 run-01
DONE: sub-135 run-02
DONE: sub-137 run-01
DONE: sub-137 run-02
DONE: sub-136 run-01
DONE: sub-136 run-02
DONE: sub-138 run-02
DONE: sub-138 run-01
DONE: sub-140 run-01
DONE: sub-140 run-02
DONE: sub-141 run-02
DONE: sub-142 run-01
DONE: sub-143 run-02
DONE: sub-142 run-02
DONE: sub-143 run-01
DONE: sub-141 run-01
DONE: sub-144 run-01
DONE: sub-145 run-01
DONE: sub-144 run-02
DONE: sub-145 run-02
DONE: sub-147 run-01
DONE: sub-147 run-02
DONE: sub-149 run-02
DONE: sub-149 run-01
DONE: sub-150 run-01
DONE: sub-151 run-02
DONE: sub-151 run-01
DONE: sub-152 run-02
DONE: sub-150 run-02
DONE: sub-152 run-01
DONE: sub-153 run-01
DONE: sub-153 run-02
DONE: sub-154 run-01
DONE: sub-154 run-02
DONE: sub-156 run-02
DONE: sub-156 run-01
DONE: sub-157 run-02
DONE: sub-155 run-02
DONE: sub-157 run-01
DONE: sub-155 run-01
DONE: sub-158 run-01
DONE: sub-158 run-02
DONE: sub-159 run-01
DONE: sub-159 run-02
Run units scheduled: 100
Run units completed: 100
Run units failed: 0
CHECK PASSED: every ds003745 run has verified RF1-grid BOLD and mask outputs.

COMMAND EXIT: 0
```
