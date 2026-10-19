# Run Record: behavioral-next-trial-RT-age

- Timestamp: 20261019-131202
- Branch: main
- Commit: e938e03
- Host: CLA19733
- User: tug87422
- Working directory: `/Users/tug87422/github/sharedreward-aging`
- Raw log: `/Users/tug87422/github/sharedreward-aging/logs/runs/20261019-131202_behavioral-next-trial-RT-age.log`
- Command exit: 0
- Check exit: none
- Summary: CHECK PASSED: all participants retained, adjacency preserved, full interaction tested.

## Command

```bash
/Users/tug87422/fsl/bin/python3 code/plot_next_trial_rt_age.py 
```

## Log

```text
RUN START: 20261019-131202
PROJECT_ROOT: /Users/tug87422/github/sharedreward-aging
GIT: main e938e03
HOST: CLA19733
USER: tug87422
PWD: /Users/tug87422/github/sharedreward-aging
COMMAND: /Users/tug87422/fsl/bin/python3 code/plot_next_trial_rt_age.py 

Minimum RT: 0.15 Pairs: 27957 Participants: 318
          family                                     comparison  n_trials  n_people  estimate  se_cluster  ci95_low  ci95_high            p  df scale  percent_change  percent_low  percent_high  f_statistic  df_num  p_holm_all13  p_holm_family  minimum_rt_s
          global                       Loss minus win at age 50     27957       318 -0.030242    0.005595 -0.041251  -0.019234 1.276039e-07 317 logRT       -2.978957    -4.041143     -1.905013          NaN     NaN      0.000002   5.104155e-07          0.15
          global            Loss minus win age slope per decade     27957       318 -0.003888    0.003013 -0.009815   0.002039 1.977959e-01 317 logRT       -0.388034    -0.976701      0.204132          NaN     NaN      1.000000   5.933878e-01          0.15
          global Previous outcome by previous partner at age 50     27957       318       NaN         NaN       NaN        NaN 8.891984e-01 317   NaN             NaN          NaN           NaN     0.117478     2.0      1.000000   1.000000e+00          0.15
          global    Age by previous outcome by previous partner     27957       318       NaN         NaN       NaN        NaN 8.091895e-01 317   NaN             NaN          NaN           NaN     0.211864     2.0      1.000000   1.000000e+00          0.15
    partner_loss                friend loss minus win at age 50     27957       318 -0.030983    0.008647 -0.047996  -0.013971 3.928308e-04 317 logRT       -3.050806    -4.686210     -1.387342          NaN     NaN      0.004321   7.856617e-04          0.15
partner_loss_age     friend loss minus win age slope per decade     27957       318 -0.005383    0.004654 -0.014540   0.003775 2.483588e-01 317 logRT       -0.536810    -1.443457      0.378178          NaN     NaN      1.000000   7.450763e-01          0.15
    partner_loss              stranger loss minus win at age 50     27957       318 -0.032344    0.008281 -0.048636  -0.016051 1.148137e-04 317 logRT       -3.182613    -4.747239     -1.592287          NaN     NaN      0.001378   3.444410e-04          0.15
partner_loss_age   stranger loss minus win age slope per decade     27957       318 -0.001675    0.004645 -0.010815   0.007465 7.186499e-01 317 logRT       -0.167365    -1.075646      0.749255          NaN     NaN      1.000000   7.450763e-01          0.15
    partner_loss              computer loss minus win at age 50     27957       318 -0.027400    0.007997 -0.043134  -0.011666 6.925661e-04 317 logRT       -2.702819    -4.221717     -1.159833          NaN     NaN      0.006926   7.856617e-04          0.15
partner_loss_age   computer loss minus win age slope per decade     27957       318 -0.004606    0.004214 -0.012898   0.003685 2.752390e-01 317 logRT       -0.459546    -1.281472      0.369223          NaN     NaN      1.000000   7.450763e-01          0.15
 paired_loss_age           friend minus stranger loss-age slope     27957       318 -0.003708    0.006001 -0.015515   0.008100 5.371538e-01 317 logRT       -0.370064    -1.539496      0.813257          NaN     NaN      1.000000   1.000000e+00          0.15
 paired_loss_age           friend minus computer loss-age slope     27957       318 -0.000777    0.005646 -0.011885   0.010332 8.906973e-01 317 logRT       -0.077620    -1.181446      1.038536          NaN     NaN      1.000000   1.000000e+00          0.15
 paired_loss_age         stranger minus computer loss-age slope     27957       318  0.002931    0.005782 -0.008446   0.014308 6.125870e-01 317 logRT        0.293530    -0.841010      1.441051          NaN     NaN      1.000000   1.000000e+00          0.15
Minimum RT: 0.0 Pairs: 28051 Participants: 318
          family                                     comparison  n_trials  n_people  estimate  se_cluster  ci95_low  ci95_high            p  df scale  percent_change  percent_low  percent_high  f_statistic  df_num  p_holm_all13  p_holm_family  minimum_rt_s
          global                       Loss minus win at age 50     28051       318 -0.031445    0.005877 -0.043007  -0.019883 1.681760e-07 317 logRT       -3.095559    -4.209534     -1.968630          NaN     NaN      0.000002   6.727042e-07           0.0
          global            Loss minus win age slope per decade     28051       318 -0.004381    0.003139 -0.010557   0.001794 1.637467e-01 317 logRT       -0.437187    -1.050182      0.179605          NaN     NaN      1.000000   4.912400e-01           0.0
          global Previous outcome by previous partner at age 50     28051       318       NaN         NaN       NaN        NaN 9.083697e-01 317   NaN             NaN          NaN           NaN     0.096133     2.0      1.000000   1.000000e+00           0.0
          global    Age by previous outcome by previous partner     28051       318       NaN         NaN       NaN        NaN 7.304122e-01 317   NaN             NaN          NaN           NaN     0.314458     2.0      1.000000   1.000000e+00           0.0
    partner_loss                friend loss minus win at age 50     28051       318 -0.033760    0.009039 -0.051544  -0.015976 2.226502e-04 317 logRT       -3.319627    -5.023810     -1.584865          NaN     NaN      0.002672   6.679505e-04           0.0
partner_loss_age     friend loss minus win age slope per decade     28051       318 -0.006656    0.004789 -0.016078   0.002765 1.655023e-01 317 logRT       -0.663426    -1.594951      0.276917          NaN     NaN      1.000000   4.965069e-01           0.0
    partner_loss              stranger loss minus win at age 50     28051       318 -0.031555    0.008502 -0.048283  -0.014828 2.431856e-04 317 logRT       -3.106276    -4.713546     -1.471895          NaN     NaN      0.002675   6.679505e-04           0.0
partner_loss_age   stranger loss minus win age slope per decade     28051       318 -0.001830    0.004781 -0.011237   0.007577 7.021586e-01 317 logRT       -0.182840    -1.117432      0.760585          NaN     NaN      1.000000   7.021586e-01           0.0
    partner_loss              computer loss minus win at age 50     28051       318 -0.029019    0.008323 -0.045395  -0.012644 5.582802e-04 317 logRT       -2.860230    -4.437999     -1.256411          NaN     NaN      0.005583   6.679505e-04           0.0
partner_loss_age   computer loss minus win age slope per decade     28051       318 -0.004658    0.004311 -0.013139   0.003823 2.807278e-01 317 logRT       -0.464710    -1.305337      0.383076          NaN     NaN      1.000000   5.614557e-01           0.0
 paired_loss_age           friend minus stranger loss-age slope     28051       318 -0.004826    0.006096 -0.016819   0.007167 4.290992e-01 317 logRT       -0.481466    -1.667884      0.719266          NaN     NaN      1.000000   1.000000e+00           0.0
 paired_loss_age           friend minus computer loss-age slope     28051       318 -0.001998    0.005672 -0.013158   0.009161 7.248177e-01 317 logRT       -0.199643    -1.307152      0.920294          NaN     NaN      1.000000   1.000000e+00           0.0
 paired_loss_age         stranger minus computer loss-age slope     28051       318  0.002828    0.005926 -0.008832   0.014488 6.335645e-01 317 logRT        0.283186    -0.879296      1.459303          NaN     NaN      1.000000   1.000000e+00           0.0
CHECK PASSED: all participants retained, adjacency preserved, full interaction tested.

COMMAND EXIT: 0
```
