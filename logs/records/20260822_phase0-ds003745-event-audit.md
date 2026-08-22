# Phase 0 ds003745 event audit

- Source: tracked OpenNeuro ds003745 v2.1.1 `_events.tsv` files.
- Runs: 100 across 50 subjects (two runs each).
- Trials: 7,200 total; every run contains exactly 72 trial rows.
- Responded `event_*` trials: 6,667.
- `missed_trial` rows: 533.
- Blocks: 900 total; every run contains exactly nine block rows.
- Block duration: exactly 33.5 seconds in all rows.
- Responded-event duration: minimum 3.50293 s, median 3.53150 s, mean 3.53608 s, maximum 4.53675 s.
- Trial labels: nine valid partner × reward/neutral/punish `event_*` categories plus `missed_trial`.
- Block labels: six valid partner × predominant reward/punish categories.
- Runs failing the 72-trial/9-block structural check: 0.

The roughly 4.5-second subset is retained as published rather than normalized to the more common roughly 3.5-second duration. This audit establishes structural integrity, not permission to infer phase boundaries.

## Interpretation

The public representation is internally consistent with a trial/block-oriented model. It is not converted into RF1 decision/outcome phases. `code/convert_harmonized_events.py --dataset ds003745` selects the published full-trial rows without changing onset, duration, partner, or feedback. Block rows remain source metadata for a possible sensitivity analysis.

No raw `Scan-Card_Guessing_Game/logs` source was found in the checked local aging repository or public data-paper repository. This does not block the proposed common full-trial estimand, but it prevents claims that exact historical phase timing was reconstructed.
