# Run Record: raw-ratings-primary-within-partner

- Timestamp: 20261001-231616
- Branch: main
- Commit: 4ed1152
- Host: CLA19733
- User: tug87422
- Working directory: `/Users/tug87422/github/sharedreward-aging`
- Raw log: `/Users/tug87422/github/sharedreward-aging/logs/runs/20261001-231616_raw-ratings-primary-within-partner.log`
- Command exit: 0
- Check exit: none
- Summary: COMMAND exit 0; CHECK none.

## Command

```bash
/Users/tug87422/fsl/bin/python3 code/analyze_raw_ratings.py 
```

## Log

```text
RUN START: 20261001-231616
PROJECT_ROOT: /Users/tug87422/github/sharedreward-aging
GIT: main 4ed1152
HOST: CLA19733
USER: tug87422
PWD: /Users/tug87422/github/sharedreward-aging
COMMAND: /Users/tug87422/fsl/bin/python3 code/analyze_raw_ratings.py 

Raw six-cell plot: 318 participants, no rating standardization.
{
  "status": "exploratory_full_demographics",
  "ratings_policy": "within_partner_loss_gt_win_primary_2026-10-01",
  "policy_authority": "User decision; primary until Cooper revises",
  "task_valid_subjects": 393,
  "additional_exclusions": 29,
  "ratings_n": 318,
  "age_model_n": 318,
  "missing_demographics": 0,
  "age_source_label": "canonical upstream RF1 baseline demographics",
  "sample_by_dataset": {
    "ds003745": {
      "n": 33,
      "min_age": 18.0,
      "max_age": 80.0
    },
    "rf1": {
      "n": 285,
      "min_age": 20.0,
      "max_age": 89.0
    }
  },
  "method": "Six-outcome subject-level OLS; continuous age per decade; dataset and recorded-sex offsets separately per cell; cross-outcome HC3 covariance; joint Wald chi-square tests; cell slope t intervals; Holm within stated families.",
  "limitations": [
    "Cross-sectional age association is not causal aging.",
    "No final imaging QC exclusions.",
    "Primary ratings eligibility excludes the person if any partner loss > win; equality allowed; missing/incomplete and all-identical exclusions retained. Response-based selection may affect associations.",
    "Bounded ratings/ceiling effects and linear age specification require sensitivity review before publication.",
    "Main plot includes all ratings-qualified participants, not only those with local ages."
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
      "path": "/Users/tug87422/github/sharedreward-aging/code/analyze_raw_ratings.py",
      "sha256": "20d9e5b53e1da195114b71f5c5cd3b418b89ce4519da93449823dda2614879f7"
    },
    {
      "path": "/Users/tug87422/github/sharedreward-aging/code/audit_ratings_qc.py",
      "sha256": "49270e365449e66bf4e4375497a4fc574f4946e5481917be3219a235ad3461ef"
    }
  ]
}
                      scope                    test   n      chi2  df        p  points_per_decade   se_hc3  ci95_low  ci95_high  p_holm_four_age_terms
pooled_dataset_sex_adjusted     any_age_association 318 14.284273   6 0.026617                NaN      NaN       NaN        NaN                    NaN
pooled_dataset_sex_adjusted            overall_mean 318  5.879442   1 0.015319           0.072275 0.029807  0.013627   0.130923               0.061275
pooled_dataset_sex_adjusted           age_x_outcome 318  4.908237   1 0.026729          -0.148861 0.067192 -0.281067  -0.016656               0.080187
pooled_dataset_sex_adjusted           age_x_partner 318  0.111542   2 0.945756                NaN      NaN       NaN        NaN               0.945756
pooled_dataset_sex_adjusted age_x_partner_x_outcome 318  3.201022   2 0.201793                NaN      NaN       NaN        NaN               0.403587
    pooled_dataset_adjusted     any_age_association 318 14.660324   6 0.023070                NaN      NaN       NaN        NaN                    NaN
    pooled_dataset_adjusted            overall_mean 318  6.182406   1 0.012903           0.071663 0.028821  0.014956   0.128369               0.051611
    pooled_dataset_adjusted           age_x_outcome 318  5.861083   1 0.015479          -0.163629 0.067588 -0.296611  -0.030648               0.051611
    pooled_dataset_adjusted           age_x_partner 318  0.293549   2 0.863489                NaN      NaN       NaN        NaN               0.863489
    pooled_dataset_adjusted age_x_partner_x_outcome 318  3.068385   2 0.215630                NaN      NaN       NaN        NaN               0.431260
           rf1_sex_adjusted     any_age_association 285  6.957218   6 0.324822                NaN      NaN       NaN        NaN                    NaN
           rf1_sex_adjusted            overall_mean 285  1.431549   1 0.231512           0.034501 0.028836 -0.022260   0.091262               0.694536
           rf1_sex_adjusted           age_x_outcome 285  2.249184   1 0.133685          -0.112522 0.075028 -0.260210   0.035167               0.534739
           rf1_sex_adjusted           age_x_partner 285  0.182700   2 0.912698                NaN      NaN       NaN        NaN               0.912698
           rf1_sex_adjusted age_x_partner_x_outcome 285  2.782735   2 0.248735                NaN      NaN       NaN        NaN               0.694536
      ds003745_sex_adjusted     any_age_association  33 22.453635   6 0.001002                NaN      NaN       NaN        NaN                    NaN
      ds003745_sex_adjusted            overall_mean  33  7.531635   1 0.006062           0.274727 0.100105  0.070285   0.479169               0.024250
      ds003745_sex_adjusted           age_x_outcome  33  4.909206   1 0.026714          -0.335429 0.151389 -0.644608  -0.026251               0.080142
      ds003745_sex_adjusted           age_x_partner  33  2.511992   2 0.284792                NaN      NaN       NaN        NaN               0.284792
      ds003745_sex_adjusted age_x_partner_x_outcome  33  4.790582   2 0.091146                NaN      NaN       NaN        NaN               0.182292
                       family                             contrast               status   n  points_per_decade   se_hc3  df_t  ci95_low  ci95_high        p  p_holm_family  family_size
within_partner_loss_minus_win              Computer loss-minus-win exploratory_followup 318           0.164176 0.093484   313 -0.019760   0.348112 0.080032       0.160064            3
within_partner_loss_minus_win              Stranger loss-minus-win exploratory_followup 318           0.065616 0.088815   313 -0.109135   0.240366 0.460589       0.460589            3
within_partner_loss_minus_win                Friend loss-minus-win exploratory_followup 318           0.216792 0.083991   313  0.051533   0.382051 0.010303       0.030908            3
        friend_minus_stranger            Friend-minus-Stranger win exploratory_followup 318          -0.064383 0.057725   313 -0.177961   0.049195 0.265557       0.531114            4
        friend_minus_stranger           Friend-minus-Stranger loss exploratory_followup 318           0.086793 0.063607   313 -0.038360   0.211945 0.173389       0.520168            4
        friend_minus_stranger           Friend-minus-Stranger mean exploratory_followup 318           0.011205 0.040714   313 -0.068904   0.091313 0.783343       0.783343            4
        friend_minus_stranger Friend-minus-Stranger win-minus-loss exploratory_followup 318          -0.151176 0.090142   313 -0.328536   0.026184 0.094523       0.378090            4

COMMAND EXIT: 0
```
