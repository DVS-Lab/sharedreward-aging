# Run Record: behavioral-ceiling-sex-sensitivity

- Timestamp: 20261019-113159
- Branch: main
- Commit: 4d2b928
- Host: CLA19733
- User: tug87422
- Working directory: `/Users/tug87422/github/sharedreward-aging`
- Raw log: `/Users/tug87422/github/sharedreward-aging/logs/runs/20261019-113159_behavioral-ceiling-sex-sensitivity.log`
- Command exit: 1
- Check exit: none
- Summary: COMMAND exit 1; CHECK none.

## Command

```bash
/Users/tug87422/fsl/bin/python3 code/check_ratings_ceiling.py 
```

## Log

```text
RUN START: 20261019-113159
PROJECT_ROOT: /Users/tug87422/github/sharedreward-aging
GIT: main 4d2b928
HOST: CLA19733
USER: tug87422
PWD: /Users/tug87422/github/sharedreward-aging
COMMAND: /Users/tug87422/fsl/bin/python3 code/check_ratings_ceiling.py 

Traceback (most recent call last):
  File "/Users/tug87422/github/sharedreward-aging/code/check_ratings_ceiling.py", line 203, in <module>
    main()
  File "/Users/tug87422/github/sharedreward-aging/code/check_ratings_ceiling.py", line 176, in main
    summary=endpoint_summary(data);results,endpoint_tests=slope_tables(data)
                                                          ^^^^^^^^^^^^^^^^^^
  File "/Users/tug87422/github/sharedreward-aging/code/check_ratings_ceiling.py", line 107, in slope_tables
    b,cov,_=fractional_fit(x,data[CELLS].to_numpy(float))
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/tug87422/github/sharedreward-aging/code/check_ratings_ceiling.py", line 48, in fractional_fit
    raise ValueError(f'Fractional fit did not converge: {fit.message}')
ValueError: Fractional fit did not converge: A bad approximation caused failure to predict improvement.

COMMAND EXIT: 1
```
