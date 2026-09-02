#!/usr/bin/env python3
"""Render a pooled fixed-effects FSF as a narrow transform of the legacy L2 template."""

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--type", choices=("act", "ppi"), required=True, dest="kind")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source = ROOT / f"templates/L2_task-sharedreward_model-1_type-{args.kind}.fsf"
    ncopes = 28 if args.kind == "act" else 29
    lines = []
    for line in source.read_text().splitlines():
        if re.match(r"^set fmri\(smooth\)", line):
            lines.append("set fmri(smooth) 0")
        elif re.match(r"^set fmri\(ncopeinputs\)", line):
            lines.append(f"set fmri(ncopeinputs) {ncopes}")
        else:
            cope = re.match(r"^set fmri\(copeinput\.(\d+)\)", line)
            if cope and int(cope.group(1)) > ncopes:
                continue
            lines.append(line)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n")
    print(f"Rendered pooled fixed-effects FSF: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
