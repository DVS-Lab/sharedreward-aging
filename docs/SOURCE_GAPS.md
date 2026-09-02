# Shared Reward source gaps

Status date: 2026-09-02. This separates confirmed missing data from recoverable repository history and unresolved RF1 source requests. Missing sources are never synthesized.

## ds003745 ratings: confirmed absent

The complete ratings audit identifies 11 ds003745 participants without Shared Reward ratings:

`105, 106, 109, 110, 130, 131, 132, 133, 134, 135, 143`

None has an `SR-Ratings` entry in the pinned OpenNeuro ds003745 v2.1.1 download inventory in `code/ds003745-2.1.1.sh`; that inventory contains Shared Reward ratings for 41 other participants. None of the 11 appears anywhere in the full `sharedreward-aging` Git object history. These are accepted missing-data exclusions unless an untracked original archive is discovered later; no external recovery request is currently justified by the available provenance.

## RF1 ratings

The current `rf1-sra` source tree lacks ratings for 19 analysis-cohort participants:

`10418, 10478, 10581, 10606, 10700, 10803, 10810, 10817, 10827, 10834, 10838, 10866, 10977, 11472, 11539, 11587, 11681, 11694, 12037`

RF1 `sub-10803` is recoverable internally. A valid six-row post-scan source was added in historical commit `247d6130d` (`10803 Post Scan`) and is retained as Git object `908135a33726f9e8e3c7cd334fec1bacf0a2c880`, but it is absent from current `main` after later merge/revert activity. Restore it in `rf1-sra` with an explicit provenance note, then rerun the ratings audit.

The remaining 18 participants have no Shared Reward ratings object anywhere in the local full `rf1-sra` history. Ryan's 2026-08-24 review of session notes resolves the recovery priority:

- Confirmed not collected or incomplete (retain ratings exclusion; no source-recovery request): `10418, 10581, 10977, 12037`.
- Reported as completed (highest-priority archive/source search): `10606, 10700, 10827, 10866, 11587, 11681, 11694`.
- No useful ratings-completion information (secondary archive/source search): `10478, 10810, 10817, 10834, 10838, 11472`.
- Experimental manipulation invalid: `11539` used the wrong friend photo in both Shared Reward runs. Both runs are task exclusions regardless of ratings availability.

The exact notes and actions are tracked in `docs/rf1_ratings_source_notes.tsv`. The full pre-review missing-source list was:

`10418, 10478, 10581, 10606, 10700, 10810, 10817, 10827, 10834, 10838, 10866, 10977, 11472, 11539, 11587, 11681, 11694, 12037`

## RF1 event sources

The upstream source-repair work recovered and validated five previously unavailable event files: `sub-11969` runs 1 and 2, `sub-11984` run 1, `sub-12020` run 1, and `sub-12036` run 2. These existing imaging runs regain behavioral eligibility and must be re-audited under the same missed-trial and condition-support rules.

Two analysis-ready imaging runs still lack canonical BIDS events because their private Shared Reward behavior sources remain unavailable upstream:

- `sub-11450`, session 01, run 2
- `sub-12037`, session 01, run 2

These are established upstream source gaps, not new repair requests. The imaging-characterization inventory includes imaging-ready runs regardless of behavioral availability, while the final task manifests automatically exclude the two unresolved runs and retain each participant's valid opposite run.
