# Run Record: behavioral-trial-RT-feedback-exploration

- Timestamp: 20261019-124827
- Branch: main
- Commit: fbc7e7f
- Host: CLA19733
- User: tug87422
- Working directory: `/Users/tug87422/github/sharedreward-aging`
- Raw log: `/Users/tug87422/github/sharedreward-aging/logs/runs/20261019-124827_behavioral-trial-RT-feedback-exploration.log`
- Command exit: 0
- Check exit: none
- Summary: CHECK PASSED: source counts verified; exploratory analyses and primary/sensitivity outputs complete.

## Command

```bash
/Users/tug87422/fsl/bin/python3 code/explore_trial_behavior.py 
```

## Log

```text
RUN START: 20261019-124827
PROJECT_ROOT: /Users/tug87422/github/sharedreward-aging
GIT: main fbc7e7f
HOST: CLA19733
USER: tug87422
PWD: /Users/tug87422/github/sharedreward-aging
COMMAND: /Users/tug87422/fsl/bin/python3 code/explore_trial_behavior.py 

Source-verified runs: 603 Trials: 33667 People: 318
                   family                                     comparison  n_trials  n_people  estimate  se_cluster  ci95_low  ci95_high            p  df       scale  percent_change  percent_low  percent_high  p_holm_family  p_holm_all18  minimum_rt_s
       current_partner_RT                friend minus stranger at age 50     33001       318 -0.026180    0.006047 -0.038077  -0.014284 2.005547e-05 317       logRT       -2.584063    -3.736138     -1.418200   8.022189e-05  3.008321e-04          0.15
       current_partner_RT     friend minus stranger age slope per decade     33001       318 -0.006042    0.003353 -0.012639   0.000556 7.252845e-02 317       logRT       -0.602353    -1.255952      0.055573   1.450569e-01  8.182775e-01          0.15
       current_partner_RT                friend minus computer at age 50     33001       318 -0.053638    0.006029 -0.065499  -0.041776 4.486465e-17 317       logRT       -5.222450    -6.340019     -4.091545   2.691879e-16  8.075637e-16          0.15
       current_partner_RT     friend minus computer age slope per decade     33001       318 -0.010130    0.003424 -0.016868  -0.003393 3.325150e-03 317       logRT       -1.007927    -1.672616     -0.338744   9.975449e-03  4.655209e-02          0.15
       current_partner_RT              stranger minus computer at age 50     33001       318 -0.027457    0.005258 -0.037803  -0.017112 3.213716e-07 317       logRT       -2.708373    -3.709701     -1.696632   1.606858e-06  5.141946e-06          0.15
       current_partner_RT   stranger minus computer age slope per decade     33001       318 -0.004089    0.002885 -0.009764   0.001587 1.573412e-01 317       logRT       -0.408032    -0.971648      0.158792   1.573412e-01  1.000000e+00          0.15
          post_outcome_RT loss minus win (equal partner weights, age 50)     31493       318 -0.030980    0.005471 -0.041745  -0.020215 3.351276e-08 317       logRT       -3.050525    -4.088584     -2.001231   2.010766e-07  5.697169e-07          0.15
          post_outcome_RT            loss minus win age slope per decade     31493       318 -0.004975    0.002689 -0.010265   0.000315 6.518355e-02 317       logRT       -0.496259    -1.021210      0.031476   3.259177e-01  8.182775e-01          0.15
          post_outcome_RT             loss effect: friend minus stranger     31493       318  0.001800    0.009786 -0.017454   0.021055 8.541576e-01 317       logRT        0.180200    -1.730283      2.127825   1.000000e+00  1.000000e+00          0.15
          post_outcome_RT             loss effect: friend minus computer     31493       318  0.001779    0.010001 -0.017898   0.021456 8.589349e-01 317       logRT        0.178052    -1.773867      2.168758   1.000000e+00  1.000000e+00          0.15
          post_outcome_RT           loss effect: stranger minus computer     31493       318 -0.000021    0.009694 -0.019093   0.019051 9.982362e-01 317       logRT       -0.002145    -1.891228      1.923313   1.000000e+00  1.000000e+00          0.15
          post_outcome_RT                loss effect: RF1 minus ds003745     31493       318 -0.003017    0.015966 -0.034430   0.028396 8.502307e-01 317       logRT       -0.301269    -3.384407      2.880256   1.000000e+00  1.000000e+00          0.15
post_outcome_guess_switch loss minus win (equal partner weights, age 50)     31493       318  0.015995    0.013299 -0.010171   0.042161 2.300035e-01 317 probability        1.599466    -1.017148      4.216079   9.200141e-01  1.000000e+00          0.15
post_outcome_guess_switch            loss minus win age slope per decade     31493       318 -0.000773    0.006337 -0.013242   0.011696 9.029974e-01 317 probability       -0.077299    -1.324165      1.169566   1.000000e+00  1.000000e+00          0.15
post_outcome_guess_switch             loss effect: friend minus stranger     31493       318 -0.006951    0.012915 -0.032362   0.018460 5.908290e-01 317 probability       -0.695088    -3.236178      1.846001   1.000000e+00  1.000000e+00          0.15
post_outcome_guess_switch             loss effect: friend minus computer     31493       318 -0.020824    0.012942 -0.046287   0.004640 1.086136e-01 317 probability       -2.082393    -4.628743      0.463958   5.430681e-01  1.000000e+00          0.15
post_outcome_guess_switch           loss effect: stranger minus computer     31493       318 -0.013873    0.012666 -0.038794   0.011048 2.742298e-01 317 probability       -1.387304    -3.879373      1.104764   9.200141e-01  1.000000e+00          0.15
post_outcome_guess_switch                loss effect: RF1 minus ds003745     31493       318 -0.088513    0.047431 -0.181831   0.004806 6.294442e-02 317 probability       -8.851263   -18.183147      0.480620   3.776665e-01  8.182775e-01          0.15
                   family                                     comparison  n_trials  n_people  estimate  se_cluster  ci95_low  ci95_high            p  df       scale  percent_change  percent_low  percent_high  p_holm_family  p_holm_all18  minimum_rt_s
       current_partner_RT                friend minus stranger at age 50     33064       318 -0.025533    0.006225 -0.037781  -0.013285 5.220034e-05 317       logRT       -2.520985    -3.707599     -1.319749   2.088014e-04  7.830052e-04           0.0
       current_partner_RT     friend minus stranger age slope per decade     33064       318 -0.006038    0.003493 -0.012910   0.000834 8.485322e-02 317       logRT       -0.601952    -1.282677      0.083467   1.697064e-01  1.000000e+00           0.0
       current_partner_RT                friend minus computer at age 50     33064       318 -0.052990    0.006125 -0.065041  -0.040940 2.593920e-16 317       logRT       -5.161093    -6.297132     -4.011280   1.556352e-15  4.669057e-15           0.0
       current_partner_RT     friend minus computer age slope per decade     33064       318 -0.009664    0.003534 -0.016617  -0.002710 6.604888e-03 317       logRT       -0.961706    -1.648005     -0.270618   1.981466e-02  9.246844e-02           0.0
       current_partner_RT              stranger minus computer at age 50     33064       318 -0.027457    0.005417 -0.038116  -0.016799 6.833275e-07 317       logRT       -2.708386    -3.739878     -1.665840   3.416638e-06  1.093324e-05           0.0
       current_partner_RT   stranger minus computer age slope per decade     33064       318 -0.003626    0.003050 -0.009626   0.002375 2.353806e-01 317       logRT       -0.361933    -0.958024      0.237746   2.353806e-01  1.000000e+00           0.0
          post_outcome_RT loss minus win (equal partner weights, age 50)     31603       318 -0.031542    0.005777 -0.042908  -0.020175 9.640721e-08 317       logRT       -3.104951    -4.200064     -1.997320   5.784433e-07  1.638923e-06           0.0
          post_outcome_RT            loss minus win age slope per decade     31603       318 -0.004841    0.002859 -0.010467   0.000784 9.140969e-02 317       logRT       -0.482969    -1.041261      0.078472   4.570484e-01  1.000000e+00           0.0
          post_outcome_RT             loss effect: friend minus stranger     31603       318 -0.001591    0.010059 -0.021382   0.018200 8.744240e-01 317       logRT       -0.158979    -2.115527      1.836677   1.000000e+00  1.000000e+00           0.0
          post_outcome_RT             loss effect: friend minus computer     31603       318  0.000531    0.010288 -0.019710   0.020772 9.588762e-01 317       logRT        0.053105    -1.951742      2.098945   1.000000e+00  1.000000e+00           0.0
          post_outcome_RT           loss effect: stranger minus computer     31603       318  0.002122    0.010106 -0.017762   0.022006 8.338315e-01 317       logRT        0.212421    -1.760526      2.224991   1.000000e+00  1.000000e+00           0.0
          post_outcome_RT                loss effect: RF1 minus ds003745     31603       318 -0.002378    0.018064 -0.037918   0.033163 8.953610e-01 317       logRT       -0.237493    -3.720838      3.371878   1.000000e+00  1.000000e+00           0.0
post_outcome_guess_switch loss minus win (equal partner weights, age 50)     31603       318  0.015643    0.013284 -0.010492   0.041778 2.398340e-01 317 probability        1.564298    -1.049223      4.177819   9.593358e-01  1.000000e+00           0.0
post_outcome_guess_switch            loss minus win age slope per decade     31603       318 -0.000844    0.006334 -0.013306   0.011617 8.940506e-01 317 probability       -0.084422    -1.330588      1.161744   1.000000e+00  1.000000e+00           0.0
post_outcome_guess_switch             loss effect: friend minus stranger     31603       318 -0.006568    0.012853 -0.031855   0.018720 6.097232e-01 317 probability       -0.656751    -3.185519      1.872018   1.000000e+00  1.000000e+00           0.0
post_outcome_guess_switch             loss effect: friend minus computer     31603       318 -0.020522    0.012830 -0.045766   0.004721 1.106983e-01 317 probability       -2.052238    -4.576556      0.472079   5.534917e-01  1.000000e+00           0.0
post_outcome_guess_switch           loss effect: stranger minus computer     31603       318 -0.013955    0.012598 -0.038740   0.010831 2.688121e-01 317 probability       -1.395488    -3.874028      1.083052   9.593358e-01  1.000000e+00           0.0
post_outcome_guess_switch                loss effect: RF1 minus ds003745     31603       318 -0.087666    0.047156 -0.180444   0.005111 6.394148e-02 317 probability       -8.766637   -18.044395      0.511120   3.836489e-01  8.312392e-01           0.0
CHECK PASSED: source counts verified; exploratory analyses and primary/sensitivity outputs complete.

COMMAND EXIT: 0
```
