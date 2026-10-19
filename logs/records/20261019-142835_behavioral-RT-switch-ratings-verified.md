# Run Record: behavioral-RT-switch-ratings-verified

- Timestamp: 20261019-142835
- Branch: main
- Commit: bfee6a2
- Host: CLA19733
- User: tug87422
- Working directory: `/Users/tug87422/github/sharedreward-aging`
- Raw log: `/Users/tug87422/github/sharedreward-aging/logs/runs/20261019-142835_behavioral-RT-switch-ratings-verified.log`
- Command exit: 0
- Check exit: none
- Summary: CHECK PASSED: switching and ratings models complete; original models and exclusions unchanged.

## Command

```bash
/Users/tug87422/fsl/bin/python3 code/analyze_rt_switch_ratings.py 
```

## Log

```text
RUN START: 20261019-142835
PROJECT_ROOT: /Users/tug87422/github/sharedreward-aging
GIT: main bfee6a2
HOST: CLA19733
USER: tug87422
PWD: /Users/tug87422/github/sharedreward-aging
COMMAND: /Users/tug87422/fsl/bin/python3 code/analyze_rt_switch_ratings.py 

                   family                                   comparison  n_trials  n_people  estimate  se_cluster  ci95_low  ci95_high        p  df scale  percent_change  percent_low  percent_high  f_statistic  df_num  p_holm_six  minimum_rt_s
              interaction     Loss effect: switch minus stay at age 50     24602       285 -0.002647    0.009886 -0.022105   0.016811 0.789078 284 logRT       -0.264347    -2.186281      1.695351          NaN     NaN         1.0          0.15
                   global Loss by switch by previous partner at age 50     24602       285       NaN         NaN       NaN        NaN 0.482959 284   NaN             NaN          NaN           NaN     0.729692     2.0         1.0          0.15
              interaction          Loss by switch age slope per decade     24602       285 -0.001008    0.005306 -0.011451   0.009435 0.849487 284 logRT       -0.100727    -1.138569      0.948011          NaN     NaN         1.0          0.15
partner_switch_difference        friend: loss effect switch minus stay     24602       285  0.001136    0.016199 -0.030749   0.033021 0.944150 284 logRT        0.113647    -3.028148      3.357232          NaN     NaN         1.0          0.15
partner_switch_difference      stranger: loss effect switch minus stay     24602       285 -0.017442    0.015324 -0.047605   0.012721 0.255984 284 logRT       -1.729102    -4.648996      1.280208          NaN     NaN         1.0          0.15
partner_switch_difference      computer: loss effect switch minus stay     24602       285  0.008366    0.016178 -0.023479   0.040210 0.605496 284 logRT        0.840061    -2.320518      4.102905          NaN     NaN         1.0          0.15
                   family                                   comparison  n_trials  n_people  estimate  se_cluster  ci95_low  ci95_high        p  df scale  percent_change  percent_low  percent_high  f_statistic  df_num  p_holm_six  minimum_rt_s
              interaction     Loss effect: switch minus stay at age 50     24670       285 -0.001945    0.010087 -0.021801   0.017910 0.847224 284 logRT       -0.194332    -2.156467      1.807150          NaN     NaN         1.0           0.0
                   global Loss by switch by previous partner at age 50     24670       285       NaN         NaN       NaN        NaN 0.377830 284   NaN             NaN          NaN           NaN     0.976655     2.0         1.0           0.0
              interaction          Loss by switch age slope per decade     24670       285 -0.002387    0.005529 -0.013270   0.008496 0.666249 284 logRT       -0.238437    -1.318283      0.853226          NaN     NaN         1.0           0.0
partner_switch_difference        friend: loss effect switch minus stay     24670       285  0.000333    0.016287 -0.031725   0.032390 0.983724 284 logRT        0.033260    -3.122727      3.292060          NaN     NaN         1.0           0.0
partner_switch_difference      stranger: loss effect switch minus stay     24670       285 -0.018880    0.015828 -0.050035   0.012274 0.233917 284 logRT       -1.870322    -4.880369      1.234977          NaN     NaN         1.0           0.0
partner_switch_difference      computer: loss effect switch minus stay     24670       285  0.012712    0.016340 -0.019451   0.044875 0.437236 284 logRT        1.279329    -1.926319      4.589757          NaN     NaN         1.0           0.0
                 scope  normalization                   outcome        model   n  age_slope_per_decade  age_ci95_low  age_ci95_high    age_p  r_squared  adjusted_r_squared  cv_rmse_mean  cv_rmse_change_vs_baseline  df  rt_block_f  rt_block_df_num  rt_block_p  switch_increment_p  cv_rmse_change_vs_three_RT  rt_block_p_holm  age_p_holm_models_targets
                pooled            raw                friend_gap     baseline 318             -0.216792     -0.382051      -0.051533 0.010303   0.056214            0.044153      2.879898                    0.000000 313         NaN              NaN         NaN                 NaN                         NaN              NaN                   0.080110
                pooled            raw                friend_gap   overall_RT 318             -0.238544     -0.407960      -0.069128 0.005933   0.058370            0.043279      2.885247                    0.005349 312    0.705276              1.0    0.401660                 NaN                         NaN         1.000000                   0.059335
                pooled            raw                friend_gap    social_RT 318             -0.217145     -0.382032      -0.052258 0.010014   0.056220            0.041096      2.890748                    0.010850 312    0.001907              1.0    0.965198                 NaN                         NaN         1.000000                   0.080110
                pooled            raw                friend_gap post_loss_RT 318             -0.217952     -0.383815      -0.052089 0.010176   0.056854            0.041740      2.890470                    0.010572 312    0.183562              1.0    0.668626                 NaN                         NaN         1.000000                   0.080110
                pooled            raw                friend_gap all_three_RT 318             -0.239680     -0.410251      -0.069109 0.006036   0.059023            0.037775      2.907012                    0.027113 310    0.283306              3.0    0.837445                 NaN                         NaN         1.000000                   0.059335
                pooled            raw friend_minus_stranger_gap     baseline 318             -0.151176     -0.328536       0.026184 0.094523   0.024433            0.011966      2.961765                    0.000000 313         NaN              NaN         NaN                 NaN                         NaN              NaN                   0.189045
                pooled            raw friend_minus_stranger_gap   overall_RT 318             -0.202701     -0.385025      -0.020378 0.029447   0.036152            0.020705      2.955493                   -0.006271 312    3.717108              1.0    0.054765                 NaN                         NaN         0.328590                   0.117789
                pooled            raw friend_minus_stranger_gap    social_RT 318             -0.167685     -0.342409       0.007040 0.059911   0.037516            0.022091      2.948262                   -0.013503 312    4.735429              1.0    0.030297                 NaN                         NaN         0.242379                   0.179733
                pooled            raw friend_minus_stranger_gap post_loss_RT 318             -0.149617     -0.327703       0.028469 0.099326   0.025553            0.009936      2.966858                    0.005094 312    0.406441              1.0    0.524249                 NaN                         NaN         1.000000                   0.189045
                pooled            raw friend_minus_stranger_gap all_three_RT 318             -0.216820     -0.398553      -0.035086 0.019527   0.050973            0.029544      2.945660                   -0.016105 310    2.808645              3.0    0.039719                 NaN                         NaN         0.278032                   0.097637
                pooled person_zscored                friend_gap     baseline 318             -0.056350     -0.099349      -0.013352 0.010379   0.036285            0.023969      0.727789                    0.000000 313         NaN              NaN         NaN                 NaN                         NaN              NaN                   0.072650
                pooled person_zscored                friend_gap   overall_RT 318             -0.062901     -0.106907      -0.018894 0.005229   0.039398            0.024004      0.729065                    0.001277 312    1.047708              1.0    0.306829                 NaN                         NaN         1.000000                   0.047065
                pooled person_zscored                friend_gap    social_RT 318             -0.058448     -0.101210      -0.015686 0.007544   0.039757            0.024369      0.728644                    0.000855 312    1.169003              1.0    0.280441                 NaN                         NaN         1.000000                   0.060356
                pooled person_zscored                friend_gap post_loss_RT 318             -0.056096     -0.099229      -0.012963 0.010971   0.036774            0.021338      0.729915                    0.002127 312    0.142324              1.0    0.706238                 NaN                         NaN         1.000000                   0.072650
                pooled person_zscored                friend_gap all_three_RT 318             -0.064653     -0.108891      -0.020414 0.004311   0.043584            0.021987      0.732090                    0.004301 310    0.624677              3.0    0.599523                 NaN                         NaN         1.000000                   0.043113
                pooled person_zscored friend_minus_stranger_gap     baseline 318             -0.056404     -0.123197       0.010388 0.097600   0.018805            0.006266      1.124751                    0.000000 313         NaN              NaN         NaN                 NaN                         NaN              NaN                   0.195201
                pooled person_zscored friend_minus_stranger_gap   overall_RT 318             -0.067738     -0.134721      -0.000756 0.047486   0.022815            0.007155      1.126662                    0.001911 312    1.263796              1.0    0.261798                 NaN                         NaN         1.000000                   0.189942
                pooled person_zscored friend_minus_stranger_gap    social_RT 318             -0.062888     -0.128794       0.003018 0.061384   0.033075            0.017580      1.118365                   -0.006385 312    5.682323              1.0    0.017734                 NaN                         NaN         0.141875                   0.189942
                pooled person_zscored friend_minus_stranger_gap post_loss_RT 318             -0.055807     -0.122929       0.011316 0.102871   0.019969            0.004263      1.126922                    0.002171 312    0.399087              1.0    0.528024                 NaN                         NaN         1.000000                   0.195201
                pooled person_zscored friend_minus_stranger_gap all_three_RT 318             -0.073320     -0.139994      -0.006646 0.031245   0.039077            0.017379      1.121943                   -0.002807 310    2.509961              3.0    0.058809                 NaN                         NaN         0.411661                   0.156224
RF1_switch_sensitivity            raw                friend_gap     baseline 285             -0.144508     -0.322093       0.033078 0.110325   0.029951            0.019594      2.861526                    0.000000 281         NaN              NaN         NaN                 NaN                         NaN              NaN                   0.450071
RF1_switch_sensitivity            raw                friend_gap all_three_RT 285             -0.163303     -0.343185       0.016580 0.075012   0.032337            0.011452      2.894849                    0.033322 278    0.230830              3.0    0.874879                 NaN                         NaN         1.000000                   0.450071
RF1_switch_sensitivity            raw                friend_gap  all_four_RT 285             -0.162009     -0.343254       0.019235 0.079572   0.032696            0.008251      2.903712                    0.042185 277    0.203784              4.0    0.936172            0.734758                    0.008863         1.000000                   0.450071
RF1_switch_sensitivity            raw friend_minus_stranger_gap     baseline 285             -0.123883     -0.329075       0.081309 0.235666   0.006607           -0.003998      3.074629                    0.000000 281         NaN              NaN         NaN                 NaN                         NaN              NaN                   0.450071
RF1_switch_sensitivity            raw friend_minus_stranger_gap all_three_RT 285             -0.187417     -0.395063       0.020228 0.076701   0.035013            0.014186      3.061429                   -0.013200 278    2.647605              3.0    0.049315                 NaN                         NaN         0.197261                   0.450071
RF1_switch_sensitivity            raw friend_minus_stranger_gap  all_four_RT 285             -0.187512     -0.395284       0.020260 0.076730   0.035014            0.010629      3.073442                   -0.001187 277    1.978882              4.0    0.097906            0.982934                    0.012013         0.293719                   0.450071
RF1_switch_sensitivity person_zscored                friend_gap     baseline 285             -0.041271     -0.086383       0.003841 0.072797   0.025127            0.014719      0.725654                    0.000000 281         NaN              NaN         NaN                 NaN                         NaN              NaN                   0.291187
RF1_switch_sensitivity person_zscored                friend_gap all_three_RT 285             -0.048983     -0.094325      -0.003641 0.034335   0.033672            0.012816      0.731012                    0.005358 278    0.606477              3.0    0.611295                 NaN                         NaN         1.000000                   0.206010
RF1_switch_sensitivity person_zscored                friend_gap  all_four_RT 285             -0.048988     -0.094574      -0.003403 0.035279   0.033672            0.009253      0.733587                    0.007933 277    0.457075              4.0    0.767199            0.995303                    0.002575         1.000000                   0.206010
RF1_switch_sensitivity person_zscored friend_minus_stranger_gap     baseline 285             -0.039844     -0.113502       0.033814 0.287885   0.007780           -0.002813      1.127351                    0.000000 281         NaN              NaN         NaN                 NaN                         NaN              NaN                   0.356844
RF1_switch_sensitivity person_zscored friend_minus_stranger_gap all_three_RT 285             -0.058118     -0.131654       0.015419 0.120899   0.031914            0.011020      1.125019                   -0.002332 278    2.586109              3.0    0.053449                 NaN                         NaN         0.213796                   0.356844
RF1_switch_sensitivity person_zscored friend_minus_stranger_gap  all_four_RT 285             -0.058465     -0.132052       0.015121 0.118948   0.032086            0.007626      1.129349                    0.001998 277    1.930423              4.0    0.105549            0.826565                    0.004330         0.316648                   0.356844
CHECK PASSED: switching and ratings models complete; original models and exclusions unchanged.

COMMAND EXIT: 0
```
