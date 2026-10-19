# Run Record: behavioral-win-loss-gap-age

- Timestamp: 20261019-111634
- Branch: main
- Commit: e25c3e2
- Host: CLA19733
- User: tug87422
- Working directory: `/Users/tug87422/github/sharedreward-aging`
- Raw log: `/Users/tug87422/github/sharedreward-aging/logs/runs/20261019-111634_behavioral-win-loss-gap-age.log`
- Command exit: 0
- Check exit: none
- Summary: CHECK PASSED: partner gap figures and paired age-slope tests generated with primary behavioral exclusions.

## Command

```bash
/Users/tug87422/fsl/bin/python3 code/plot_rating_gaps.py 
```

## Log

```text
RUN START: 20261019-111634
PROJECT_ROOT: /Users/tug87422/github/sharedreward-aging
GIT: main e25c3e2
HOST: CLA19733
USER: tug87422
PWD: /Users/tug87422/github/sharedreward-aging
COMMAND: /Users/tug87422/fsl/bin/python3 code/plot_rating_gaps.py 

{
  "n": 318,
  "sample_by_dataset": {
    "ds003745": 33,
    "rf1": 285
  },
  "task_valid_n": 393,
  "excluded_n": 75,
  "ratings_policy": "within_partner_loss_gt_win_primary_2026-10-01",
  "imaging_exclusions_applied": false,
  "difference": "raw win minus raw loss within each participant and partner",
  "method": "Pooled continuous age per decade, dataset and recorded sex; HC3 with within-person covariance retained.",
  "tests": "Holm over 3 partner age slopes; separately Holm over 3 paired slope differences; one 2-df joint slope-equality Wald test.",
  "uncertainty": "Pointwise 95% t intervals, not simultaneous bands.",
  "limitations": [
    "Exploratory cross-sectional associations, not causal aging.",
    "Response-based exclusions and bounded ratings can affect associations."
  ],
  "sources": [
    {
      "path": "/Users/tug87422/github/sharedreward-aging/logs/records/ratings-qc-subject-level.tsv",
      "sha256": "dc13ec845d927cb66f41139d54b2bce37ee3efbbb3b62466034ee3bd7f6488ed"
    },
    {
      "path": "/Users/tug87422/github/sharedreward-aging/logs/records/analysis-subject-dispositions.tsv",
      "sha256": "e30a4c33fc4adf18fc62bdeaada0360851086b66c9fd24d03f73e67c83ae7616"
    },
    {
      "path": "/Users/tug87422/github/rf1-sra-linux2/bids/participants.tsv",
      "sha256": "10004009f83ae3ffd9977941e6c222ac8f1aabfd70f41968470cfaa70ef35ca4"
    },
    {
      "path": "/Users/tug87422/github/sharedreward-aging/participants-srndna.tsv",
      "sha256": "760730ad4d57f3d5d05ca489620ddead9442380405885b7c84792e413a3dac5e"
    },
    {
      "path": "/Users/tug87422/github/sharedreward-aging/code/plot_rating_gaps.py",
      "sha256": "dca61b26005a280c05e3204fdf4e8468c02d2f73d03ea2245c47d0a057bb480b"
    },
    {
      "path": "/Users/tug87422/github/sharedreward-aging/code/analyze_raw_ratings.py",
      "sha256": "20d9e5b53e1da195114b71f5c5cd3b418b89ce4519da93449823dda2614879f7"
    },
    {
      "path": "/Users/tug87422/github/sharedreward-aging/code/audit_ratings_qc.py",
      "sha256": "49270e365449e66bf4e4375497a4fc574f4946e5481917be3219a235ad3461ef"
    }
  ]
}
                  family                          comparison   n  points_per_decade   se_hc3  ci95_low  ci95_high  df        p  p_holm_family     chi2
      partner_age_slopes                              Friend 318          -0.216792 0.083991 -0.382051  -0.051533 313 0.010303       0.030908      NaN
      partner_age_slopes                            Stranger 318          -0.065616 0.088815 -0.240366   0.109135 313 0.460589       0.460589      NaN
      partner_age_slopes                            Computer 318          -0.164176 0.093484 -0.348112   0.019760 313 0.080032       0.160064      NaN
paired_slope_differences               Friend minus Stranger 318          -0.151176 0.090142 -0.328536   0.026184 313 0.094523       0.283568      NaN
paired_slope_differences               Friend minus Computer 318          -0.052616 0.114143 -0.277200   0.171969 313 0.645144       0.645144      NaN
paired_slope_differences             Stranger minus Computer 318           0.098560 0.096221 -0.090761   0.287882 313 0.306478       0.612957      NaN
    joint_slope_equality Age x partner on win-minus-loss gap 318                NaN      NaN       NaN        NaN   2 0.201793            NaN 3.201022
CHECK PASSED: partner gap figures and paired age-slope tests generated with primary behavioral exclusions.

COMMAND EXIT: 0
```
