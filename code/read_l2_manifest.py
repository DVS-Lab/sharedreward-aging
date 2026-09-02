#!/usr/bin/env python3
"""Emit fixed-effects units and report one-run passthrough units."""

import csv
import sys
from pathlib import Path


with Path(sys.argv[1]).open(newline="") as handle:
    rows = list(csv.DictReader(handle, delimiter="\t"))
required = {"dataset", "subject", "session", "n_runs", "runs"}
if not rows or not required.issubset(rows[0]):
    raise SystemExit("ERROR: L2 manifest contract is incomplete")
for row in rows:
    runs = [str(int(value)) for value in row["runs"].split(",") if value]
    if int(row["n_runs"]) != len(runs) or len(runs) not in {1, 2}:
        raise SystemExit(f"ERROR: invalid subject-level run contract: {row}")
    if len(runs) == 1:
        print(f"PASSTHROUGH\t{row['dataset']}\t{row['subject']}\t{row['session'] or 'none'}\t{runs[0]}", file=sys.stderr)
        continue
    values = [row["dataset"], row["subject"], row["session"] or "none", *runs]
    if any("|" in value or "\n" in value for value in values):
        raise SystemExit("ERROR: unsupported delimiter in L2 manifest value")
    print("|".join(values))
