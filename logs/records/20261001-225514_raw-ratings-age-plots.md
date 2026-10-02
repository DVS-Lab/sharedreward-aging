# Run Record: raw-ratings-age-plots

- Timestamp: 20261001-225514
- Branch: main
- Commit: cb56ed0
- Host: CLA19733
- User: tug87422
- Working directory: `/Users/tug87422/github/sharedreward-aging`
- Raw log: `/Users/tug87422/github/sharedreward-aging/logs/runs/20261001-225514_raw-ratings-age-plots.log`
- Command exit: 0
- Check exit: none
- Summary: COMMAND exit 0; CHECK none.

## Command

```bash
/Users/tug87422/fsl/bin/python3 code/plot_rating_age.py 
```

## Log

```text
RUN START: 20261001-225514
PROJECT_ROOT: /Users/tug87422/github/sharedreward-aging
GIT: main cb56ed0
HOST: CLA19733
USER: tug87422
PWD: /Users/tug87422/github/sharedreward-aging
COMMAND: /Users/tug87422/fsl/bin/python3 code/plot_rating_age.py 

Created two pooled age figures (PNG/SVG): n=347, complete demographics, no new exclusions.
Output directory: /Users/tug87422/github/sharedreward-aging/qc/ratings-raw

COMMAND EXIT: 0
```

## Post-run verification

- Code was under development on top of cb56ed0 when this record was generated;
  exact plotting and shared-model source hashes are in
  `qc/ratings-raw/age-plots-provenance.json`.
- All 347 eligible participants are included; no additional exclusions.
- Visually inspected both PNGs: all raw points retained, condition panels share
  the rating scale, mean panel's distinct scale is explicit, captions and
  preliminary labels are readable with no clipping.
- All seven predicted means and pointwise HC3 confidence intervals agree with
  independent statsmodels calculations at ages 20, 50 and 80
  (rtol=1e-10, atol=1e-12). Slopes match the previous full-cohort results.
- Full workflow validation: bash/Python syntax PASS, 85 unit tests PASS.
- No L1/L2/FEAT outputs or cohort membership were changed.
