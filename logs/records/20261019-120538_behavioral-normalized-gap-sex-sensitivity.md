# Run Record: behavioral-normalized-gap-sex-sensitivity

- Timestamp: 20261019-120538
- Branch: main
- Commit: 8078203
- Host: CLA19733
- User: tug87422
- Working directory: `/Users/tug87422/github/sharedreward-aging`
- Raw log: `/Users/tug87422/github/sharedreward-aging/logs/runs/20261019-120538_behavioral-normalized-gap-sex-sensitivity.log`
- Command exit: 0
- Check exit: none
- Summary: CHECK PASSED: both normalized gap models use the same sample and match direct difference-score regressions.

## Command

```bash
/Users/tug87422/fsl/bin/python3 code/check_normalized_gap_sex.py 
```

## Log

```text
RUN START: 20261019-120538
PROJECT_ROOT: /Users/tug87422/github/sharedreward-aging
GIT: main 8078203
HOST: CLA19733
USER: tug87422
PWD: /Users/tug87422/github/sharedreward-aging
COMMAND: /Users/tug87422/fsl/bin/python3 code/check_normalized_gap_sex.py 

{
  "n": 318,
  "sample_by_dataset": {
    "ds003745": 33,
    "rf1": 285
  },
  "ratings_policy": "within_partner_loss_gt_win_primary_2026-10-01",
  "normalization": "Same six-cell within-participant z-scores (sample SD, ddof=1) in both fits, computed after raw-rating exclusions.",
  "model": "Intercept, continuous centered age/10, RF1 dataset dummy; with/without M/O recorded-sex offsets (F reference).",
  "inference": "Paired HC3 t tests and 95% CIs. Raw p and Holm over three paired comparisons within each specification; separate Holm family for three individual partner gap slopes.",
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
      "path": "/Users/tug87422/github/sharedreward-aging/code/check_normalized_gap_sex.py",
      "sha256": "d839b92b450f0a72041b2df033529fd0c38381a153ff8170040c7e10fab9ff85"
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
      "sha256": "0c9ab0f597aa6b3eb2483fcf5861e2c194d7464c051d1df91319546d4786137c"
    }
  ]
}
 sex_adjusted                   family                          comparison   n  within_person_SD_per_decade   se_hc3  ci95_low  ci95_high  df        p  p_holm_family     chi2
         True       partner_age_slopes                              Friend 318                    -0.056350 0.021854 -0.099349  -0.013352 313 0.010379       0.031136      NaN
         True       partner_age_slopes                            Stranger 318                     0.000054 0.021904 -0.043044   0.043153 313 0.998024       0.998024      NaN
         True       partner_age_slopes                            Computer 318                    -0.041319 0.024704 -0.089926   0.007288 313 0.095416       0.190833      NaN
         True paired_slope_differences               Friend minus Stranger 318                    -0.056404 0.033947 -0.123197   0.010388 313 0.097600       0.292801      NaN
         True paired_slope_differences               Friend minus Computer 318                    -0.015031 0.039001 -0.091769   0.061706 313 0.700198       0.700198      NaN
         True paired_slope_differences             Stranger minus Computer 318                     0.041373 0.030955 -0.019534   0.102280 313 0.182341       0.364682      NaN
         True     joint_slope_equality Age x partner on win-minus-loss gap 318                          NaN      NaN       NaN        NaN   2 0.166688            NaN 3.583262
        False       partner_age_slopes                              Friend 318                    -0.062703 0.021796 -0.105588  -0.019818 315 0.004292       0.012876      NaN
        False       partner_age_slopes                            Stranger 318                    -0.004487 0.021877 -0.047530   0.038556 315 0.837627       0.837627      NaN
        False       partner_age_slopes                            Computer 318                    -0.036652 0.024169 -0.084206   0.010902 315 0.130406       0.260812      NaN
        False paired_slope_differences               Friend minus Stranger 318                    -0.058216 0.033894 -0.124903   0.008470 315 0.086850       0.260549      NaN
        False paired_slope_differences               Friend minus Computer 318                    -0.026051 0.038503 -0.101807   0.049704 315 0.499156       0.588012      NaN
        False paired_slope_differences             Stranger minus Computer 318                     0.032165 0.030601 -0.028042   0.092373 315 0.294006       0.588012      NaN
        False     joint_slope_equality Age x partner on win-minus-loss gap 318                          NaN      NaN       NaN        NaN   2 0.193680            NaN 3.283093
CHECK PASSED: both normalized gap models use the same sample and match direct difference-score regressions.

COMMAND EXIT: 0
```
