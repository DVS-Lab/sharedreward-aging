# Run Record: behavioral-normalized-win-loss-age

- Timestamp: 20261019-120715
- Branch: main
- Commit: 660d1a5
- Host: CLA19733
- User: tug87422
- Working directory: `/Users/tug87422/github/sharedreward-aging`
- Raw log: `/Users/tug87422/github/sharedreward-aging/logs/runs/20261019-120715_behavioral-normalized-win-loss-age.log`
- Command exit: 0
- Check exit: none
- Summary: CHECK PASSED: normalized partner gaps and paired age-slope contrasts generated.

## Command

```bash
/Users/tug87422/fsl/bin/python3 code/plot_normalized_rating_gaps.py 
```

## Log

```text
RUN START: 20261019-120715
PROJECT_ROOT: /Users/tug87422/github/sharedreward-aging
GIT: main 660d1a5
HOST: CLA19733
USER: tug87422
PWD: /Users/tug87422/github/sharedreward-aging
COMMAND: /Users/tug87422/fsl/bin/python3 code/plot_normalized_rating_gaps.py 

{
  "n": 318,
  "sample_by_dataset": {
    "ds003745": 33,
    "rf1": 285
  },
  "ratings_policy": "within_partner_loss_gt_win_primary_2026-10-01",
  "normalization": "Each participant: (rating - mean of six partner x outcome cells) / sample SD of six cells (ddof=1). Normalize once, then compute each partner win-minus-loss gap. No second normalization of gaps.",
  "model": "Intercept + continuous centered age per decade + dataset + recorded sex (F reference, M/O dummy offsets); same participants in every outcome.",
  "inference": "Paired wide OLS HC3 covariance, pointwise t CIs; direct differences of slopes. One 2-df joint slope-equality Wald test. Raw p and separate Holm families for three slopes and three paired differences.",
  "right_panel": "(Friend win - Friend loss) - (Stranger win - Stranger loss), in within-person SD units. Dots remove fitted dataset/sex contributions relative to empirical means, preserving age effect and residual.",
  "historical_slide": "Current adjusted N318 analysis; not a replication of the supplied historical N205 correlation or its unspecified normalization.",
  "primary_raw_model_changed": false,
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
      "path": "/Users/tug87422/github/sharedreward-aging/code/plot_normalized_rating_gaps.py",
      "sha256": "a254d96b3a5a628448f96377a11e2047b743f0a91ae3ecc879afb9d2210a6f22"
    },
    {
      "path": "/Users/tug87422/github/sharedreward-aging/code/analyze_raw_ratings.py",
      "sha256": "20d9e5b53e1da195114b71f5c5cd3b418b89ce4519da93449823dda2614879f7"
    },
    {
      "path": "/Users/tug87422/github/sharedreward-aging/code/audit_ratings_qc.py",
      "sha256": "49270e365449e66bf4e4375497a4fc574f4946e5481917be3219a235ad3461ef"
    },
    {
      "path": "/Users/tug87422/github/sharedreward-aging/code/plot_normalized_loss_ratings.py",
      "sha256": "fc2f487fe9bf94503a7266b2f0f4597db4bb9bac821e4a39ba43480c24fcb940"
    },
    {
      "path": "/Users/tug87422/github/sharedreward-aging/code/plot_rating_gaps.py",
      "sha256": "dca61b26005a280c05e3204fdf4e8468c02d2f73d03ea2245c47d0a057bb480b"
    }
  ]
}
                  family                          comparison   n  within_person_SD_per_decade   se_hc3  ci95_low  ci95_high  df        p  p_holm_family     chi2
      partner_age_slopes                              Friend 318                    -0.056350 0.021854 -0.099349  -0.013352 313 0.010379       0.031136      NaN
      partner_age_slopes                            Stranger 318                     0.000054 0.021904 -0.043044   0.043153 313 0.998024       0.998024      NaN
      partner_age_slopes                            Computer 318                    -0.041319 0.024704 -0.089926   0.007288 313 0.095416       0.190833      NaN
paired_slope_differences               Friend minus Stranger 318                    -0.056404 0.033947 -0.123197   0.010388 313 0.097600       0.292801      NaN
paired_slope_differences               Friend minus Computer 318                    -0.015031 0.039001 -0.091769   0.061706 313 0.700198       0.700198      NaN
paired_slope_differences             Stranger minus Computer 318                     0.041373 0.030955 -0.019534   0.102280 313 0.182341       0.364682      NaN
    joint_slope_equality Age x partner on win-minus-loss gap 318                          NaN      NaN       NaN        NaN   2 0.166688            NaN 3.583262
CHECK PASSED: normalized partner gaps and paired age-slope contrasts generated.

COMMAND EXIT: 0
```
