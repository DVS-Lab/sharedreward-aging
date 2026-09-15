# ds003745 sub-144 event recovery and model restart

## Source correction (reviewed 2026-09-14)

The authoritative correction lives in `DVS-Lab/srndna-datapaper`, commit
`db67173efd0d6d4ef31800d9ac24ca8d665a20bf`. Its recovery script validates the
second session in the concatenated raw Shared Reward CSV. The old published
sub-144 event files duplicated sub-143. Both sub-144 runs require regenerated
event derivatives and activation/PPI models. Do not reproduce the raw recovery
logic in this repository.

Corrected upstream files, relative to that repository:

- `bids/sub-144/func/sub-144_task-sharedreward_run-01_events.tsv`:
  SHA256 `995f6a8987c15c4dc6a85265e7b74b2c462e81e51f712868e0cdc79631495d2d`.
- `bids/sub-144/func/sub-144_task-sharedreward_run-02_events.tsv`:
  SHA256 `058d75fd5afb31cf742b537a79f02247b5e118619bf5ea84726ae934fa233833`.

These hashes are enforced by `build_event_qc_manifest.py`. It accepts a matching
file in the dataset itself, or selects the matching authoritative upstream file
through `SRNDNA_DATAPAPER_ROOT`. It fails if neither matches; it never falls back
to the old duplicated events. This does not require waiting for an OpenNeuro
release, mutate the pinned DataLad source dataset, or add a Git submodule.

The corrected event conversion yields 72 trials in each run: one missed trial
in run 01 and none in run 02. All six reward/punishment cells are supported in
both runs. Run 02 has no friend-neutral trials, which is allowed by the documented
[neutral decision](NEUTRAL_CONDITION_DECISION.md). Final inclusion still depends
on the freshly rebuilt cohort's other exclusions, not these counts alone.

## What changes and what stays

- Refresh the full event-QC inventory, harmonized event tables and their source
  fingerprints; rebuild cohort dispositions with existing QC/exclusion rules.
- Before rebuilding the full cohort, generate missing ds003745 FSL nuisance
  matrices from the existing named fMRIPrep confounds and audit volume alignment.
  Existing matrix/metadata pairs are not overwritten. RF1 uses its upstream
  matrices unchanged. This prerequisite applies to all ds003745 imaging-QC
  rows even though only sub-144 FEAT models are being recovered.
- Generate corrected sub-144 three-column files and select its eligible runs.
- Rerun paired activation + provisional VS PPI, then two-run fixed effects
  (or one-run passthrough if only one run is eligible), with completeness audits.
- Preserve fMRIPrep, wsinc5 resampling, 6-mm target smoothing, tSNR, masks and
  coverage. This correction changes event timing/labels, not image data.
- Preserve historical logs. Stale sub-144 FEAT/GFEAT directories are moved to
  `derivatives/fsl/replaced-models/sub144-<UTC timestamp>/`, not deleted.
  They are recoverable, but must not enter the current model inventory.
- The preparation refreshes event QC for the entire current smoothing manifest
  because QC version 2 now verifies source content, not just filenames/counts.
  Missing source exclusions and >25% missed-trial rules remain unchanged.

## Linux2 commands

Do not run while another process is writing these cohorts or sub-144 models.
The recovery command locks against another copy of itself. Do not put
`set -e` in the interactive SSH shell.

```bash
conda activate sharedreward-phase0
export PHASE0_ENV=/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0
export IMAGING_PYTHON="$PHASE0_ENV/bin/python"
export SRNDNA_DATAPAPER_ROOT=/ZPOOL/data/projects/srndna-datapaper
export PATH="$PHASE0_ENV/bin:/usr/local/fsl/share/fsl/bin:$PATH"
export FSLDIR=/usr/local/fsl
export FSLOUTPUTTYPE=NIFTI_GZ

git -C "$SRNDNA_DATAPAPER_ROOT" pull --ff-only origin main
git -C /ZPOOL/data/projects/sharedreward-aging pull --ff-only origin main
```

If either pull fails, stop and resolve Git before continuing. If the upstream
clone is elsewhere, change `SRNDNA_DATAPAPER_ROOT`; do not copy arbitrary events.

```bash
cd /ZPOOL/data/projects/sharedreward-aging
bash code/validate_workflow.sh

bash code/run_logged.sh \
  --label sub144-corrected-events-prepare --include-full-log -- \
  "$IMAGING_PYTHON" code/recover_sub144_analysis.py
```

After preparation passes, this single detached command repeats the guarded
preparation and runs sub-144 through both L1 analyses, L1 audits, L2 and final
audits. Maximum two L1 workers; each runs activation then PPI, not four concurrent
FEAT jobs. L2 uses one outer worker and `FSLSUB_PARALLEL=1`.

```bash
nohup bash code/run_logged.sh \
  --label sub144-corrected-events-L1-L2 --include-full-log -- \
  "$IMAGING_PYTHON" code/recover_sub144_analysis.py --run-models \
  > logs/sub144-corrected-events-L1-L2.nohup 2>&1 </dev/null &

tail -n 40 logs/sub144-corrected-events-L1-L2.nohup
```

Expected terminal success is `CHECK PASSED: corrected sub-144 activation and
provisional VS PPI, including subject-level outputs.` followed by `COMMAND EXIT:
0`. Selected inputs are saved in `logs/records/sub144-recovery-selected-inputs.json`;
four completeness reports and the major run records are also Git-trackable.
Per-unit logs and imaging derivatives remain ignored.

```bash
git status --short
git add logs/records logs/sub144-corrected-events-L1-L2.nohup
git commit -m "Record corrected sub-144 event and model recovery"
git pull --rebase origin main
git push origin main
```

Review staged records before committing; resolve any rebase conflict before
pushing. Never force-push to resolve a concurrent log/code update.

## Cohort-wide contrast migration is a separate step

The neutral decision changes the pooled contract from 28 activation / 29 PPI
copes to 22 / 23. Existing old models are not valid merely because their cope22
or cope23 exists: later cope numbers now refer to different contrasts.

New models carry `pooled-model-inputs.json`: content hashes for EVs, confounds,
templates and relevant code, plus size/mtime fingerprints for large imaging
inputs. L2 additionally checks parent provenance and cope/varcope fingerprints.
Workers and audits reject old/missing stamps, changed inputs and wrong contrast
counts. Do not manufacture stamps for old output. Image fingerprints are not
cryptographic verification of the large image payloads.

Only sub-144 is rerun by the recovery command. After its Linux2 pilot passes,
audit the entire newly frozen L1/subject manifests and explicitly migrate any
old-contract outputs before group analyses. The 17 former neutral-only holds
can join the eligible cohort; old count estimates are not a final inventory.
Use the new logged cohort rebuild to report current totals.
