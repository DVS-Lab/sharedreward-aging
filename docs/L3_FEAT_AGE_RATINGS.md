# Preliminary pooled FEAT/FLAME1 models

Decision, 2026-10-18: use normal FEAT/FLAMEO FLAME1, not randomise, for the
requested exploratory age analyses. This supersedes the older preliminary
permutation launcher; it does not overwrite its results or rerun L1/L2.

## Models and tracked templates

- `templates/L3_template_pooled_age_flame1.fsf`: intercept, centered age/10,
  centered tSNR, centered mean FD, dataset dummy (RF1=1, ds003745=0).
- `templates/L3_template_pooled_age-ratings_flame1.fsf`: intercept, centered raw
  friend-win minus stranger-win rating, centered age/10, centered tSNR,
  centered mean FD, dataset dummy.

No sex term is included. tSNR is the mean of the retained runs' whole-brain
median tSNR, measured on the smoothed FEAT inputs (`post_target_blur`). Mean FD
is weighted by the number of valid FD observations in the retained runs.
Covariates are centered separately within each model's eligible sample.

The age models test both signs of age for activation and VS-seeded PPI at
COPEs 10 (reward-punishment), 11 (friend-stranger), 12 (friend-computer),
14 (friend-stranger by reward-punishment), 16 (friend-computer by
reward-punishment), and 17 (friend-stranger wins). No neutral contrasts.
This is 12 FEAT models. Optional ratings models add activation and PPI at
COPE17, each testing ratings positive/negative and age positive/negative:
14 FEAT models total. The original task COPE number is distinct from the
group-level zstat number: age-only zstat1/2 = age positive/negative;
ratings zstat1/2 = ratings positive/negative, zstat3/4 = adjusted age.

Current local covariate plan: 358 imaging participants (315 RF1, 43 ds003745),
663 retained runs; 290 participants qualify for the ratings extension.
Ratings use the primary within-partner loss>win exclusion, equality allowed,
plus the existing validated ratings eligibility. Raw ratings are not z-scored.

## Exclusions are applied before modeling

Inputs come only from Cooper's `logs/records/exclusion-ledger/retained-L1.tsv`
and `retained-L2.tsv`, not the pre-QC candidate cohort. The ledger checksum,
no-pending-decisions state, retained run combinations and computational
readiness are verified. Subjects with one retained run use that L1 estimate;
subjects with two use their verified retained-run fixed-effects estimate.

An additional launch-time check rejects retained runs crossing the frozen
dataset-specific FD, tSNR or coverage thresholds. Thresholds are NOT re-estimated
on the surviving sample. Current verification:

| Dataset | High mean FD (mm) | Low median tSNR | Low coverage (%) |
| --- | ---: | ---: | ---: |
| ds003745 | >0.49364 (9 flags) | <24.3286 (0 flags) | <94.2137 (5 flags) |
| RF1 | >0.3659 (44 flags) | <32.8231 (0 flags) | <99.1488 (33 flags) |

None of the flagged runs occur in the 663 retained inputs. Of the 53 FD flags,
47 have a motion exclusion and six were already excluded for other reasons.
Coverage and FD counts overlap and must not be summed. The FD/tSNR covariates
are additional adjustment, not a replacement for exclusions.

## Execution, inference and provenance

`code/run_L3stats.py` renders each FSF and validates the actual `feat_model`
matrices. `code/L3stats.sh` calls `feat`, which calls `flameo` in FLAME1 mode.
There is one variance group, no robust outlier mixture, no added smoothing,
and no FEAT watcher/X11. Outer concurrency defaults to four model workers;
FSLSUB_PARALLEL and BLAS/OpenMP threads are constrained to one per worker.
Preparation and readiness checks precede those workers.

Verified standard-space COPE/VARCOPE/mask/DOF inputs are exposed through
read-only symlink adapter directories under the new L3 output root. These
prevent FEAT from registering or writing into the original L1/L2 directories.
Adapters retain original contrast scaling. An adapter's `design.lev=2` signals
already-standard-space inputs, not a newly estimated fixed-effects model.
Only a single-run L1 input may obtain a constant DOF map from its recorded
`stats/dof`; missing fixed-effects DOF maps fail.

Whole-brain inference: Z>3.1, cluster p<0.05 **per signed map**. There is no
additional correction across models or signs; these analyses are exploratory.
Each result audit verifies fitted matrices, FLAME1 setting, common mask,
finite COPE/VARCOPE/zstat maps, variance, cluster masks and cluster tables.

The independent ROI stage uses the same participant model and shared group
VS/vmPFC masks, intersected with the common available FEAT mask. It estimates
VS activation and vmPFC activation/PPI, with HC3 95% CIs and Holm-adjusted
p-values separately for the 18 age and three ratings ROI tests. Ratings ROI
plots show the ratings coefficient; whole-brain ratings models also test age.
Plots are under `qc/L3-preliminary/LABEL/`. No individual VS masks are created.

The scoped `resources/age-mask-allowance-20261018.json` can permit the ten
previously reviewed upstream whole-brain-mask fingerprint changes for this
preliminary pass. This does not assert old/new voxel identity, change any model
stamp, or bypass other readiness checks. Results remain marked provisional.

Plans, aggregate ROI statistics, cluster tables and completion audits are
tracked under `logs/records/L3-preliminary/LABEL/`; images, ordered subject
designs and subject-level ROI values stay under ignored
`derivatives/fsl/L3-preliminary/LABEL/`. Unique labels prevent overwriting.
This launcher neither starts nor stops the older randomise workflow.

## Linux2 launch

```bash
cd /ZPOOL/data/projects/sharedreward-aging
git pull --ff-only origin main
conda activate sharedreward-phase0
export IMAGING_PYTHON=/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python
export FSLDIR=/usr/local/fsl
source "$FSLDIR/etc/fslconf/fsl.sh"
export PATH="$FSLDIR/share/fsl/bin:$PATH"

l3_label="L3-FLAME1-age-ratings-$(date +%Y%m%d-%H%M%S)"
nohup setsid -f -w bash code/run_logged.sh \
  --label "$l3_label" --include-full-log -- \
  "$IMAGING_PYTHON" code/run_L3stats.py \
    --stage all --label "$l3_label" --with-ratings --jobs 4 \
    --mask-allowance resources/age-mask-allowance-20261018.json \
  > "logs/${l3_label}.nohup" 2>&1 < /dev/null &
tail -f "logs/${l3_label}.nohup"
```

Ctrl-C ends `tail`, not the detached job. `--stage roi` and `--stage wholebrain`
also work independently with distinct labels. Push the completed run record
and aggregate reports for review; do not add derivatives.
