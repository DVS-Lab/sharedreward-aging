# Shared Reward source gaps

Status date: 2026-08-24. This separates confirmed missing data from recoverable repository history and unresolved RF1 source requests. Missing sources are never synthesized.

## ds003745 ratings: confirmed absent

The complete ratings audit identifies 11 ds003745 participants without Shared Reward ratings:

`105, 106, 109, 110, 130, 131, 132, 133, 134, 135, 143`

None has an `SR-Ratings` entry in the pinned OpenNeuro ds003745 v2.1.1 download inventory in `code/ds003745-2.1.1.sh`; that inventory contains Shared Reward ratings for 41 other participants. None of the 11 appears anywhere in the full `sharedreward-aging` Git object history. These are accepted missing-data exclusions unless an untracked original archive is discovered later; no external recovery request is currently justified by the available provenance.

## RF1 ratings

The current `rf1-sra` source tree lacks ratings for 19 analysis-cohort participants:

`10418, 10478, 10581, 10606, 10700, 10803, 10810, 10817, 10827, 10834, 10838, 10866, 10977, 11472, 11539, 11587, 11681, 11694, 12037`

RF1 `sub-10803` is recoverable internally. A valid six-row post-scan source was added in historical commit `247d6130d` (`10803 Post Scan`) and is retained as Git object `908135a33726f9e8e3c7cd334fec1bacf0a2c880`, but it is absent from current `main` after later merge/revert activity. Restore it in `rf1-sra` with an explicit provenance note, then rerun the ratings audit.

The remaining 18 participants have no Shared Reward ratings object anywhere in the local full `rf1-sra` history and form the external RF1 recovery-check list:

`10418, 10478, 10581, 10606, 10700, 10810, 10817, 10827, 10834, 10838, 10866, 10977, 11472, 11539, 11587, 11681, 11694, 12037`

## RF1 event sources

Seven analysis-ready imaging runs lack canonical BIDS events because their private Shared Reward behavior sources are documented as missing upstream:

- `sub-11450`, session 01, run 2
- `sub-11969`, session 01, runs 1 and 2
- `sub-11984`, session 01, run 1
- `sub-12020`, session 01, run 1
- `sub-12036`, session 01, run 2
- `sub-12037`, session 01, run 2

These match the authoritative remaining-source list in `rf1-sra-linux2/docs/behavior-source-repairs.md`. The available opposite-run files do not justify copying or relabeling behavior. Recovery requires original task-log checking by the RF1 data holders. Until then, these seven runs cannot enter event-based L1 modeling even though their imaging derivatives exist.
