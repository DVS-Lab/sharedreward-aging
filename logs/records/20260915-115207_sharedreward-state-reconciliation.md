# Run Record: sharedreward-state-reconciliation

- Timestamp: 20260915-115207
- Branch: main
- Commit: a9b1919
- Host: CLA19733
- User: tug87422
- Working directory: `/Users/tug87422/github/sharedreward-aging`
- Raw log: `/Users/tug87422/github/sharedreward-aging/logs/runs/20260915-115207_sharedreward-state-reconciliation.log`
- Command exit: 0
- Check exit: none
- Summary: COMMAND exit 0; CHECK none.

## Command

```bash
/Users/tug87422/fsl/bin/python3 -B /private/tmp/sharedreward-reconciliation.7Huxcp/check_reconciliation.py
```

## Log

```text
RUN START: 20260915-115207
PROJECT_ROOT: /Users/tug87422/github/sharedreward-aging
GIT: main a9b1919
HOST: CLA19733
USER: tug87422
PWD: /Users/tug87422/github/sharedreward-aging
COMMAND: /Users/tug87422/fsl/bin/python3 -B /private/tmp/sharedreward-reconciliation.7Huxcp/check_reconciliation.py

PASS: inventory 767 imaging / 765 events / 744 task-ready runs / 393 subject-sessions (351 two-run, 42 one-run).
CONFIRMED: currently recorded ratings-qualified inventory is 655 runs / 346 subject-sessions, before source refresh.
PASS: input QC 767 rows; 88 review-flagged runs / 61 participants, including 80 task-ready runs.
REVIEW: five task-ready runs carry unresolved upstream historical concerns; no new exclusion applied.
CONFIRMED: pooled v3 audit verified four L1/two subject outputs, all sub-144; full-cohort gate remains incomplete.
PASS: intentional RF1-only 14/34 versus pooled 10/28 and 21/29 contracts; smoothing/per-EV filtering zero; 22 non-neutral primary vectors.
CONFIRMED STALE: 10803 recovered source passes ratings audit, while generated ratings QC still says missing.
10803 source SHA256: 461da4b6290c2a590023808d196c1354eeca89fb534a438b031b740651d1a112
PASS: documentation-only changes and local links: sharedreward-aging
PASS: documentation-only changes and local links: rf1-sra-sharedreward
No new Linux2 model/imaging audit was executed by this local reconciliation check.

COMMAND EXIT: 0
```
