# Pre-handoff verification: non-neutral contrasts only

For the completed audit's interpretation, cross-repository provenance and
remaining scientific reviews, see [CURRENT_STATUS.md](CURRENT_STATUS.md).

Decision reaffirmed 2026-09-15: ignore every contrast containing neutral-condition
coefficients for planned inference. Preserve all existing contrast slots; do not
remove or renumber them. `audit_group_readiness.py` selects from the actual tracked
coefficient vectors, not names. In the pooled contract, COPEs 7, 8, 9, 20, 21 and
22 are out of scope, leaving 22 task contrasts for both activation and PPI.
PPI COPE29 (physiology) is not a task contrast and is also outside this gate.
Missing neutral EV trials are allowed; the EV files and fitted design must still
correspond to the events actually available.

## What is verified

- Nonempty L1/L2 manifests, unique run keys, and identical retained-run inventory.
- Both activation and provisional VS-PPI canonical pooled output paths.
- L1 model contract, actual design.con coefficients, and primary estimability.
- No additional FEAT smoothing, no FEAT watcher, and no per-EV temporal filtering.
- EV content against current harmonized events; BOLD/confound identity and lengths.
- Recorded input provenance, model mask and all primary COPE/VARCOPE/ZSTAT maps:
  readable reference-grid 3D images, finite in-mask values, nonnegative VARCOPE
  with some positive in-mask variance.
- Two-run fixed effects with the correct retained L1 parents, selected input COPEs,
  two-row intercept-only designs and one-row unit contrasts. One-run cases use
  the verified retained L1 directly, without inventing an L2 model.

Neutral statistical maps are never required. L2 provenance checks omit neutral
and physiology parent-image entries; primary image entries and all recorded
small-file inputs remain checked. Images use the existing size/mtime provenance,
not a new full-content hash of each 4D dataset.

## Interpretation and scope

The latest successful run record, `20260915-091946_sub144-restored-contrasts-L1-L2.md`,
verifies the isolated sub-144 recovery. It does **not** certify cohort-wide output.
Its rebuilt manifests contain 744 task-ready runs and 393 subject-sessions, before
final imaging/ratings exclusions. Those are expected inputs, not completed models.

Run the new audit on Linux2, where the derivatives exist. It changes no model
files, launches no processing jobs and never changes exclusion decisions. Use a
new report directory for every invocation. Exit 1 means readiness remains
incomplete, with missing/unverified units itemized; it is not authorization to
rerun everyone. An absent canonical model may exist elsewhere and needs inventory
review. A provenance mismatch needs investigation, not a retrofitted stamp.

The `verified-pre-QC-candidates.tsv` report contains only verified primary inputs;
it is **not** an approved L3 cohort. If only some models pass, it is a partial list
and must not silently become the analysis sample. Imaging/ratings exclusions,
demographics/covariates, final seed provenance and L3 statistical choices remain
separate. This audit does not revalidate raw behavioral-source repairs or choose
a group-level analysis mask. Keep the summary and detailed audit reports together.

## Linux2 execution

```bash
cd /ZPOOL/data/projects/sharedreward-aging
git pull --ff-only origin main
conda activate sharedreward-phase0
export IMAGING_PYTHON=/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python
audit_stamp=$(date +%Y%m%d-%H%M%S)
audit_report="logs/records/group-readiness-${audit_stamp}"
nohup env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  bash code/run_logged.sh --label "group-readiness-${audit_stamp}" --include-full-log -- \
  "$IMAGING_PYTHON" code/audit_group_readiness.py \
    --l1-manifest logs/runlists/L1-task-ready.tsv \
    --subject-manifest logs/runlists/L2-task-ready.tsv \
    --fsl-root "$PWD/derivatives/fsl" \
    --reference /ZPOOL/data/projects/rf1-sra-sharedreward/resources/rf1_MNI152NLin6Asym_reference_grid.nii.gz \
    --report-dir "$audit_report" \
  > "logs/group-readiness-${audit_stamp}.nohup" 2>&1 < /dev/null &
```

After it exits, commit the new report directory and corresponding tracked
`logs/records/*group-readiness*.md` run record. Do not commit derivative images.
The report JSON includes manifest, contrast table, audit code and reference
fingerprints so the audited inventory is identifiable without tracking runlists.
