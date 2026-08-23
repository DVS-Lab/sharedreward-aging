# Run Record: phase0-ds003745-build-remaining-runlist

- Timestamp: 20260822-222158
- Branch: main
- Commit: e26786b
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260822-222158_phase0-ds003745-build-remaining-runlist.log`
- Command exit: 0
- Check exit: 0
- Summary: CHECK PASSED: remaining runlist contains 46 participants.

## Command

```bash
python3 code/build_ds003745_runlist.py --exclude-subject 104 --exclude-subject 105 --exclude-subject 140 --exclude-subject 141 --output logs/runlists/ds003745-fmriprep-remaining.tsv 
```

## Check

```bash
bash -c $'\n    test -f logs/runlists/ds003745-fmriprep-remaining.tsv || exit 1\n    rows=$(awk "END {print NR-1}" \\\n      logs/runlists/ds003745-fmriprep-remaining.tsv)\n    printf "Runlist rows: %s\\n" "$rows"\n    test "$rows" -eq 46 || exit 1\n    echo "CHECK PASSED: remaining runlist contains 46 participants."\n  ' 
```

## Log

```text
RUN START: 20260822-222158
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main e26786b
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: python3 code/build_ds003745_runlist.py --exclude-subject 104 --exclude-subject 105 --exclude-subject 140 --exclude-subject 141 --output logs/runlists/ds003745-fmriprep-remaining.tsv 

Participants in pinned table: 50
Excluded participants: 4
Runlist participants: 46
Runlist: /ZPOOL/data/projects/sharedreward-aging/logs/runlists/ds003745-fmriprep-remaining.tsv

COMMAND EXIT: 0

CHECK COMMAND: bash -c $'\n    test -f logs/runlists/ds003745-fmriprep-remaining.tsv || exit 1\n    rows=$(awk "END {print NR-1}" \\\n      logs/runlists/ds003745-fmriprep-remaining.tsv)\n    printf "Runlist rows: %s\\n" "$rows"\n    test "$rows" -eq 46 || exit 1\n    echo "CHECK PASSED: remaining runlist contains 46 participants."\n  ' 

Runlist rows: 46
CHECK PASSED: remaining runlist contains 46 participants.

CHECK EXIT: 0
```
