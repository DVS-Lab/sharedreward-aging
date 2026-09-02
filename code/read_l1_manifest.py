#!/usr/bin/env python3
"""Emit the seven path-safe fields consumed by the shell L1 batch wrapper."""

import csv
import sys
from pathlib import Path


path = Path(sys.argv[1])
with path.open(newline="") as handle:
    rows = list(csv.DictReader(handle, delimiter="\t"))
required = {"dataset", "subject", "session", "run", "input", "mask", "confounds"}
if not rows or not required.issubset(rows[0]):
    raise SystemExit("ERROR: L1 manifest contract is incomplete")
for row in rows:
    values = [
        row["dataset"],
        row["subject"],
        row["session"] or "none",
        str(int(row["run"])),
        row["input"],
        row["mask"],
        row["confounds"],
    ]
    if any("|" in value or "\n" in value for value in values):
        raise SystemExit("ERROR: unsupported delimiter in L1 manifest value")
    print("|".join(values))
