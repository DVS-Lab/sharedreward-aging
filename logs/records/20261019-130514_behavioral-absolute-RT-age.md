# Run Record: behavioral-absolute-RT-age

- Timestamp: 20261019-130514
- Branch: main
- Commit: c959f6e
- Host: CLA19733
- User: tug87422
- Working directory: `/Users/tug87422/github/sharedreward-aging`
- Raw log: `/Users/tug87422/github/sharedreward-aging/logs/runs/20261019-130514_behavioral-absolute-RT-age.log`
- Command exit: 0
- Check exit: none
- Summary: CHECK PASSED: absolute RT curves and paired slope tests use the same verified participants.

## Command

```bash
/Users/tug87422/fsl/bin/python3 code/plot_absolute_rt_age.py 
```

## Log

```text
RUN START: 20261019-130514
PROJECT_ROOT: /Users/tug87422/github/sharedreward-aging
GIT: main c959f6e
HOST: CLA19733
USER: tug87422
PWD: /Users/tug87422/github/sharedreward-aging
COMMAND: /Users/tug87422/fsl/bin/python3 code/plot_absolute_rt_age.py 

               family                   comparison   n  log_rt_per_decade   se_hc3  ci95_low  ci95_high  percent_per_decade  percent_low  percent_high  df            p     chi2  p_holm_family  minimum_rt_s
          overall_age         Mean across partners 318           0.038607 0.007387  0.024072   0.053143            3.936223     2.436409      5.457996 313 3.168801e-07      NaN            NaN          0.15
          partner_age                       friend 318           0.033449 0.007542  0.018610   0.048288            3.401448     1.878409      4.947257 313 1.275465e-05      NaN   1.275465e-05          0.15
          partner_age                     stranger 318           0.038743 0.007858  0.023281   0.054205            3.950361     2.355457      5.570117 313 1.334931e-06      NaN   2.669862e-06          0.15
          partner_age                     computer 318           0.043630 0.007474  0.028924   0.058335            4.459553     2.934652      6.007045 313 1.324339e-08      NaN   3.973017e-08          0.15
paired_age_difference        friend minus stranger 318          -0.005295 0.003309 -0.011806   0.001217           -0.528053    -1.173631      0.121743 313 1.106273e-01      NaN   2.077559e-01          0.15
paired_age_difference        friend minus computer 318          -0.010181 0.003519 -0.017106  -0.003256           -1.012933    -1.696006     -0.325113 313 4.085085e-03      NaN   1.225526e-02          0.15
paired_age_difference      stranger minus computer 318          -0.004886 0.002996 -0.010781   0.001008           -0.487454    -1.072307      0.100856 313 1.038780e-01      NaN   2.077559e-01          0.15
    joint_age_partner All partner age slopes equal 318                NaN      NaN       NaN        NaN                 NaN          NaN           NaN   2 1.482287e-02 8.423168            NaN          0.15
               family                   comparison   n  log_rt_per_decade   se_hc3  ci95_low  ci95_high  percent_per_decade  percent_low  percent_high  df            p     chi2  p_holm_family  minimum_rt_s
          overall_age         Mean across partners 318           0.037419 0.007508  0.022645   0.052192            3.812747     2.290367      5.357785 313 1.034937e-06      NaN            NaN           0.0
          partner_age                       friend 318           0.032243 0.007602  0.017286   0.047199            3.276822     1.743639      4.833109 313 2.926136e-05      NaN   2.926136e-05           0.0
          partner_age                     stranger 318           0.037843 0.008032  0.022039   0.053647            3.856854     2.228412      5.511237 313 3.704319e-06      NaN   7.408639e-06           0.0
          partner_age                     computer 318           0.042170 0.007639  0.027139   0.057200            4.307136     2.751080      5.886757 313 7.113756e-08      NaN   2.134127e-07           0.0
paired_age_difference        friend minus stranger 318          -0.005601 0.003469 -0.012425   0.001224           -0.558492    -1.234856      0.122504 313 1.074016e-01      NaN   2.148031e-01           0.0
paired_age_difference        friend minus computer 318          -0.009927 0.003575 -0.016961  -0.002893           -0.987769    -1.681805     -0.288834 313 5.823266e-03      NaN   1.746980e-02           0.0
paired_age_difference      stranger minus computer 318          -0.004326 0.003126 -0.010477   0.001825           -0.431688    -1.042226      0.182617 313 1.673671e-01      NaN   2.148031e-01           0.0
    joint_age_partner All partner age slopes equal 318                NaN      NaN       NaN        NaN                 NaN          NaN           NaN   2 2.109607e-02 7.717337            NaN           0.0
CHECK PASSED: absolute RT curves and paired slope tests use the same verified participants.

COMMAND EXIT: 0
```
