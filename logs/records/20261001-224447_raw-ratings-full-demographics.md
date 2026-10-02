# Run Record: raw-ratings-full-demographics

- Timestamp: 20261001-224447
- Branch: main
- Commit: e1dff75
- Host: CLA19733
- User: tug87422
- Working directory: `/Users/tug87422/github/sharedreward-aging`
- Raw log: `/Users/tug87422/github/sharedreward-aging/logs/runs/20261001-224447_raw-ratings-full-demographics.log`
- Command exit: 0
- Check exit: none
- Summary: COMMAND exit 0; CHECK none.

## Command

```bash
/Users/tug87422/fsl/bin/python3 code/analyze_raw_ratings.py --output-dir qc/ratings-raw 
```

## Log

```text
RUN START: 20261001-224447
PROJECT_ROOT: /Users/tug87422/github/sharedreward-aging
GIT: main e1dff75
HOST: CLA19733
USER: tug87422
PWD: /Users/tug87422/github/sharedreward-aging
COMMAND: /Users/tug87422/fsl/bin/python3 code/analyze_raw_ratings.py --output-dir qc/ratings-raw 

Raw six-cell plot: 347 participants, no rating standardization.
{
  "status": "exploratory_full_demographics",
  "ratings_n": 347,
  "age_model_n": 347,
  "missing_demographics": 0,
  "age_source_label": "canonical upstream RF1 baseline demographics",
  "sample_by_dataset": {
    "ds003745": {
      "n": 34,
      "min_age": 18.0,
      "max_age": 80.0
    },
    "rf1": {
      "n": 313,
      "min_age": 20.0,
      "max_age": 89.0
    }
  },
  "method": "Six-outcome subject-level OLS; continuous age per decade; dataset and recorded-sex offsets separately per cell; cross-outcome HC3 covariance; joint Wald chi-square tests; cell slope t intervals; Holm within stated families.",
  "limitations": [
    "Cross-sectional age association is not causal aging.",
    "No final imaging QC exclusions.",
    "Ratings eligibility retains the existing identical/loss>win rules; response-based selection may affect associations.",
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
      "sha256": "b9ddbd5984e0b8bb7e10ed41f67cd9081268056fa0cbadc3cbff74c2965d74fb"
    }
  ]
}
                      scope                    test   n      chi2  df        p  points_per_decade   se_hc3  ci95_low  ci95_high  p_holm_four_age_terms
pooled_dataset_sex_adjusted     any_age_association 347 15.842903   6 0.014622                NaN      NaN       NaN        NaN                    NaN
pooled_dataset_sex_adjusted            overall_mean 347 10.444677   1 0.001230           0.093095 0.028806  0.036436   0.149754               0.004920
pooled_dataset_sex_adjusted           age_x_outcome 347  2.757703   1 0.096787          -0.111331 0.067041 -0.243196   0.020534               0.290361
pooled_dataset_sex_adjusted           age_x_partner 347  0.516607   2 0.772361                NaN      NaN       NaN        NaN               0.772361
pooled_dataset_sex_adjusted age_x_partner_x_outcome 347  3.639143   2 0.162095                NaN      NaN       NaN        NaN               0.324190
    pooled_dataset_adjusted     any_age_association 347 16.990082   6 0.009320                NaN      NaN       NaN        NaN                    NaN
    pooled_dataset_adjusted            overall_mean 347 10.814891   1 0.001007           0.091113 0.027706  0.036619   0.145607               0.004027
    pooled_dataset_adjusted           age_x_outcome 347  3.102555   1 0.078170          -0.118418 0.067229 -0.250649   0.013814               0.234509
    pooled_dataset_adjusted           age_x_partner 347  1.185762   2 0.552733                NaN      NaN       NaN        NaN               0.552733
    pooled_dataset_adjusted age_x_partner_x_outcome 347  4.596659   2 0.100426                NaN      NaN       NaN        NaN               0.234509
           rf1_sex_adjusted     any_age_association 313  7.964018   6 0.240751                NaN      NaN       NaN        NaN                    NaN
           rf1_sex_adjusted            overall_mean 313  4.511226   1 0.033673           0.060558 0.028512  0.004456   0.116661               0.134692
           rf1_sex_adjusted           age_x_outcome 313  0.745286   1 0.387973          -0.064261 0.074437 -0.210728   0.082206               0.975881
           rf1_sex_adjusted           age_x_partner 313  1.450130   2 0.484293                NaN      NaN       NaN        NaN               0.975881
           rf1_sex_adjusted age_x_partner_x_outcome 313  2.246054   2 0.325294                NaN      NaN       NaN        NaN               0.975881
      ds003745_sex_adjusted     any_age_association  34 21.647231   6 0.001403                NaN      NaN       NaN        NaN                    NaN
      ds003745_sex_adjusted            overall_mean  34  8.330106   1 0.003899           0.276283 0.095726  0.081049   0.471518               0.015597
      ds003745_sex_adjusted           age_x_outcome  34  5.725091   1 0.016724          -0.361078 0.150907 -0.668855  -0.053301               0.050173
      ds003745_sex_adjusted           age_x_partner  34  3.581111   2 0.166867                NaN      NaN       NaN        NaN               0.166867
      ds003745_sex_adjusted age_x_partner_x_outcome  34  5.003967   2 0.081922                NaN      NaN       NaN        NaN               0.163845

COMMAND EXIT: 0
```
