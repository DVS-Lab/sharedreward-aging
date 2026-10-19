# Run Record: behavioral-loss-age-normalized

- Timestamp: 20261019-115117
- Branch: main
- Commit: 553204a
- Host: CLA19733
- User: tug87422
- Working directory: `/Users/tug87422/github/sharedreward-aging`
- Raw log: `/Users/tug87422/github/sharedreward-aging/logs/runs/20261019-115117_behavioral-loss-age-normalized.log`
- Command exit: 0
- Check exit: none
- Summary: CHECK PASSED: normalized loss plots and paired slope tests, same sample and raw-rating exclusions.

## Command

```bash
/Users/tug87422/fsl/bin/python3 code/plot_normalized_loss_ratings.py 
```

## Log

```text
RUN START: 20261019-115117
PROJECT_ROOT: /Users/tug87422/github/sharedreward-aging
GIT: main 553204a
HOST: CLA19733
USER: tug87422
PWD: /Users/tug87422/github/sharedreward-aging
COMMAND: /Users/tug87422/fsl/bin/python3 code/plot_normalized_loss_ratings.py 

{
  "n": 318,
  "sample_by_dataset": {
    "ds003745": 33,
    "rf1": 285
  },
  "ratings_policy": "within_partner_loss_gt_win_primary_2026-10-01",
  "normalization": "Within each participant, equally weight all six partner x outcome cell means. Center by six-cell mean; z-score by six-cell sample SD (ddof=1). No pooling of SDs, no loss-only normalization.",
  "exclusions": "Applied to raw ratings first. Identical sample for all three models; zero SD fails explicitly. No imaging QC exclusions.",
  "model": "Intercept + centered continuous age per decade + dataset + recorded sex; condition-specific coefficients, paired HC3 covariance.",
  "inference": "Pointwise t confidence intervals. Holm over three pairwise loss-slope tests within each normalization; separately over three individual loss slopes. Exploratory, not experiment-wide correction.",
  "interpretation": "Centering targets relative rating level; z-scoring also adjusts scale spread. Normalization may remove response-style differences and substantive between-person differences; no claim to identify pure response bias.",
  "primary_model_changed": false,
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
      "path": "/Users/tug87422/github/sharedreward-aging/code/plot_normalized_loss_ratings.py",
      "sha256": "9133946093ee11d67b0878ab85bd77a02ca4d18cbe8c59bb2608b5570fdc7df2"
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
      "path": "/Users/tug87422/github/sharedreward-aging/code/plot_rating_age.py",
      "sha256": "71580f76a2f4a5cc13c8e1613444933d8a2d82ba047f9a66f79a25ccde2c46ef"
    },
    {
      "path": "/Users/tug87422/github/sharedreward-aging/code/analyze_loss_rating_age.py",
      "sha256": "d98c205e860580b3a0a52905a14069cf09c316a709aa29cb78635590d15e05ef"
    }
  ]
}
  normalization  sex_adjusted                        family               comparison   n  units_per_decade   se_hc3  ci95_low  ci95_high  df_t        p  p_holm_three     chi2  df_chi2            units
            raw          True    individual_loss_age_slopes                   Friend 318          0.190383 0.072302  0.048124   0.332643 313.0 0.008879      0.024374      NaN      NaN    rating_points
            raw          True    individual_loss_age_slopes                 Stranger 318          0.103591 0.057072 -0.008702   0.215883 313.0 0.070466      0.070466      NaN      NaN    rating_points
            raw          True    individual_loss_age_slopes                 Computer 318          0.146143 0.054861  0.038200   0.254086 313.0 0.008125      0.024374      NaN      NaN    rating_points
            raw          True paired_loss_slope_differences    Friend minus Stranger 318          0.086793 0.063607 -0.038360   0.211945 313.0 0.173389      0.520168      NaN      NaN    rating_points
            raw          True paired_loss_slope_differences    Friend minus Computer 318          0.044240 0.080752 -0.114645   0.203125 313.0 0.584184      0.955579      NaN      NaN    rating_points
            raw          True paired_loss_slope_differences  Stranger minus Computer 318         -0.042553 0.059873 -0.160357   0.075252 313.0 0.477790      0.955579      NaN      NaN    rating_points
            raw          True     joint_loss_slope_equality Age x partner for losses 318               NaN      NaN       NaN        NaN   NaN 0.344799           NaN 2.129587      2.0    rating_points
person_centered          True    individual_loss_age_slopes                   Friend 318          0.118108 0.059857  0.000335   0.235881 313.0 0.049356      0.148068      NaN      NaN    rating_points
person_centered          True    individual_loss_age_slopes                 Stranger 318          0.031315 0.045478 -0.058167   0.120798 313.0 0.491598      0.491598      NaN      NaN    rating_points
person_centered          True    individual_loss_age_slopes                 Computer 318          0.073868 0.049519 -0.023563   0.171300 313.0 0.136779      0.273558      NaN      NaN    rating_points
person_centered          True paired_loss_slope_differences    Friend minus Stranger 318          0.086793 0.063607 -0.038360   0.211945 313.0 0.173389      0.520168      NaN      NaN    rating_points
person_centered          True paired_loss_slope_differences    Friend minus Computer 318          0.044240 0.080752 -0.114645   0.203125 313.0 0.584184      0.955579      NaN      NaN    rating_points
person_centered          True paired_loss_slope_differences  Stranger minus Computer 318         -0.042553 0.059873 -0.160357   0.075252 313.0 0.477790      0.955579      NaN      NaN    rating_points
person_centered          True     joint_loss_slope_equality Age x partner for losses 318               NaN      NaN       NaN        NaN   NaN 0.344799           NaN 2.129587      2.0    rating_points
 person_zscored          True    individual_loss_age_slopes                   Friend 318          0.037610 0.018636  0.000941   0.074278 313.0 0.044436      0.133307      NaN      NaN within_person_SD
 person_zscored          True    individual_loss_age_slopes                 Stranger 318         -0.001804 0.012608 -0.026611   0.023004 313.0 0.886346      0.886346      NaN      NaN within_person_SD
 person_zscored          True    individual_loss_age_slopes                 Computer 318          0.013001 0.014479 -0.015487   0.041490 313.0 0.369908      0.739817      NaN      NaN within_person_SD
 person_zscored          True paired_loss_slope_differences    Friend minus Stranger 318          0.039413 0.024765 -0.009314   0.088141 313.0 0.112512      0.337537      NaN      NaN within_person_SD
 person_zscored          True paired_loss_slope_differences    Friend minus Computer 318          0.024608 0.028987 -0.032425   0.081642 313.0 0.396558      0.793116      NaN      NaN within_person_SD
 person_zscored          True paired_loss_slope_differences  Stranger minus Computer 318         -0.014805 0.020649 -0.055433   0.025824 313.0 0.473925      0.793116      NaN      NaN within_person_SD
 person_zscored          True     joint_loss_slope_equality Age x partner for losses 318               NaN      NaN       NaN        NaN   NaN 0.258639           NaN 2.704647      2.0 within_person_SD
CHECK PASSED: normalized loss plots and paired slope tests, same sample and raw-rating exclusions.

COMMAND EXIT: 0
```
