# Exploratory trial behavior

The 2026-10-19 exploration found faster responses with social partners and faster
next-trial responses after losses than wins. It did not establish a pooled
lose-switch guessing effect or a friend-specific post-loss RT effect. These
analyses address response behavior, not the primary subjective-rating hypothesis.

## Sample and source checks

The analysis uses the same 318 participants as the current primary ratings
analysis (285 RF1, 33 ds003745), restricted to their 603 task-ready runs.
There are 33,667 trials, including 603 misses. Missing/invalid/constant ratings
and any partner's loss rating greater than their win rating remain exclusions;
equality is allowed. Task-validity and missed-trial run exclusions remain in
force. MRI motion, coverage and tSNR exclusions are not added to this behavioral
sample. This is therefore not an analysis of every task performer.

RF1 raw logs are resolved and converted in memory using the authoritative
`rf1-sra-linux2` converter. Run totals, misses and all nine partner/outcome
counts must match the current event-QC export. Local RF1 canonical BIDS events
are unavailable, so this does not independently establish per-trial BIDS hash
identity. The older raw logs must match every BIDS event's timing, RT, condition
and block. Sub-144 uses the corrected second logged session. Other concatenated
logs require a unique BIDS-matching session, including sub-145 run 1.
No raw source, BIDS file, imaging model, or exclusion decision is changed.

The [source audit](../qc/trial-behavior-exploratory/source-audit.tsv) records
source hashes, selected logged sessions and verification methods. The local
trial derivative is ignored under `derivatives/behavioral-exploratory/`.

## Models and safeguards

- Current-partner RT: log RT with run fixed effects, partner indicators,
  partner interactions with age, dataset and recorded sex, trial progress and
  squared progress, and older-dataset reward-block context. Partner contrasts
  are evaluated at age 50 and the sample's dataset/sex mix. Age is continuous,
  centered at 50 and expressed per decade. Run intercepts absorb main age,
  dataset and sex offsets; this model does not estimate overall age-related slowing.
- Next-trial RT: log RT conditional on the immediately preceding observed
  outcome. Predictors include previous loss and neutral feedback (win reference),
  loss interactions with age, dataset and previous partner, current/previous
  partner, partner switching, previous log RT, elapsed time from prior outcome
  offset to current decision, and trial progress plus squared progress.
- Next-guess switching: the same lag design, with a binary changed-button
  outcome and a linear probability model. Effects are percentage-point changes,
  not odds ratios. The response-button coding differs across studies but is
  constant within a run; switching compares adjacent buttons within that run.

RF1 lag models have run fixed effects; ds003745 lag models have block fixed
effects and exclude transitions between blocks. All uncertainty uses participant-
clustered CR1 covariance with a finite-sample correction accounting for absorbed
intercepts and t reference degrees of freedom equal to participants minus one.
Tests independently verify this calculation against explicit fixed-effect
regression and statsmodels' cluster covariance.

Lagged variables are formed before filtering. First trials, misses and excluded
RTs never create a connection between nonadjacent trials. Current and previous
responses must both have valid RT for lag modeling. Neutral outcomes are retained
as nuisance observations, not recoded to wins/losses. Trial numbering resets/gaps,
nonmonotonic timing and unexpected response codes fail validation.

The main exploratory RT cutoff is 150 ms, excluding 63 responded trials, with
an all-positive-RT sensitivity analysis. This cutoff is not represented as a
preregistered choice. Misses have missing RT, never a numeric timeout sentinel.
The primary RT models use 33,001 current responses and 31,493 adjacent pairs.
All 318 participants contribute. Results include uncorrected p, Holm correction
within each six-test family, and Holm correction across all 18 tests. Sensitivity
analyses are reported separately; no specification is selected for its p-value.

## Results

At age 50, pooled over the recorded dataset/sex mix, current-trial RT was:

| Comparison | Relative RT difference | Uncorrected p | Holm p across 18 tests |
|---|---:|---:|---:|
| Friend versus stranger | −2.58% | .0000201 | .000301 |
| Friend versus computer | −5.22% | 4.49e−17 | 8.08e−16 |
| Stranger versus computer | −2.71% | .000000321 | .00000514 |

Following a loss rather than a win, next-trial RT was **3.05% faster**
(95% CI 2.00% to 4.09% faster; uncorrected p=3.35e−8), controlling for the
variables above. This effect survives correction across all 18 tests. The
friend-minus-stranger difference in that loss effect was close to zero
(uncorrected p=.854). Next-guess switching increased by 1.60 percentage points,
but its interval includes zero (95% CI −1.02 to +4.22; uncorrected p=.230).

The friend-versus-computer RT ratio declined by about 1.01% per decade
(uncorrected p=.00333; six-test Holm p=.00998; 18-test Holm p=.0466).
The all-positive-RT sensitivity gave about 0.96% per decade (uncorrected
p=.00660), but no longer passed the 18-test correction. Treat this age
interaction as tentative. The friend-versus-stranger age interaction was
not clear (uncorrected p=.0725), nor was age modulation of the post-loss
RT effect (uncorrected p=.0652). Neither survives multiplicity correction.

Overall partner RT and post-loss RT findings persist when very fast responses
are retained. Full estimates, confidence intervals, sensitivity analyses and
null results are in [model tests](../qc/trial-behavior-exploratory/model-tests.tsv).
Omission and switching frequencies are also available as descriptive summaries;
those unadjusted frequencies should not substitute for the lag model estimates.

## Interpretation and figures

These are exploratory associations following the ratings analysis. They are
not replacement evidence for the prediction about subjective pleasure. Faster
responses might reflect attention, familiarity, arousal or motor preparation;
RT alone does not identify valuation. Because feedback was predetermined,
response switching is not evidence of optimal learning or decision accuracy.

The task implementations differ: the older response window is 2.5 seconds and
RF1's is 2.8 seconds; RT timestamping also occurs on different sides of a display
flip. Dataset adjustments and the within-person comparisons reduce, but do not
eliminate, concerns about comparing task versions. The older block structure
also limits generalization of its within-block feedback effect to block changes.

![Trial behavior](../qc/trial-behavior-exploratory/exploratory-trial-behavior.png)

![Partner RT differences by age](../qc/trial-behavior-exploratory/partner-RT-age.png)

The bar panel shows means of participant-specific median RTs with between-person
SEM. Lag panels show adjusted model effects with 95% confidence intervals.
Age curves show relative partner RT differences, not absolute RT or overall
age-related slowing. Vector SVG versions accompany both figures.

Reproduce locally with `python code/explore_trial_behavior.py`. It reads the
adjacent `rf1-sra`, `rf1-sra-linux2` and `srndna-datapaper` clones and the local
older BIDS event snapshots. Paths can be supplied explicitly using `--help`.
Source and model hashes are in the accompanying
[provenance file](../qc/trial-behavior-exploratory/provenance.json).
