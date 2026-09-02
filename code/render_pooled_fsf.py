#!/usr/bin/env python3
"""Render the pooled full-trial FSF as a narrow transform of legacy templates."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "act": ROOT / "templates/L1_task-sharedreward_model-1_type-act_seed-0_HPC.fsf",
    "ppi": ROOT / "templates/L1_task-sharedreward_model-1_type-ppi_seed-VS_HPC.fsf",
}
EV_KEYS = {
    "evtitle",
    "shape",
    "convolve",
    "convolve_phase",
    "tempfilt_yn",
    "deriv_yn",
    "custom",
}
CONTRAST_KEY = re.compile(
    r"^(?:conpic_(?:orig|real)|conname_(?:orig|real))\.\d+$|"
    r"^con_(?:orig|real)\d+\.\d+$|^conmask\d+_\d+$|^ftest_(?:orig|real)\d+\.\d+$"
)


def candidate_contrasts(path: Path) -> list[tuple[str, list[float]]]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    contrasts = []
    for row in rows:
        weights = [float(value) for value in row["weights_ev1_to_ev10"].split(",")]
        if len(weights) != 10:
            raise ValueError(f"invalid candidate contrast: {row['contrast_name']}")
        contrasts.append((row["contrast_name"], weights))
    if len(contrasts) != 28:
        raise ValueError(f"expected 28 candidate contrasts, found {len(contrasts)}")
    return contrasts


def format_value(value: float) -> str:
    return format(value, ".12g")


def contrast_block(kind: str, contrasts) -> str:
    if kind == "act":
        vectors = [(name, weights) for name, weights in contrasts]
        ev_count = 10
    else:
        vectors = [
            (name, [0.0] * 11 + weights)
            for name, weights in contrasts
        ]
        vectors.append(("phys", [0.0] * 10 + [1.0] + [0.0] * 10))
        ev_count = 21
    lines = ["", "# Pooled full-trial contrasts (generated from the tracked TSV contract)"]
    for contrast_number, (name, weights) in enumerate(vectors, 1):
        if len(weights) != ev_count:
            raise ValueError(f"contrast {name} has {len(weights)} rather than {ev_count} weights")
        for mode in ("real", "orig"):
            lines.append(f"set fmri(conpic_{mode}.{contrast_number}) 1")
            lines.append(f'set fmri(conname_{mode}.{contrast_number}) "{name}"')
            for ev_number, value in enumerate(weights, 1):
                lines.append(
                    f"set fmri(con_{mode}{contrast_number}.{ev_number}) "
                    f"{format_value(value)}"
                )
    for first in range(1, len(vectors) + 1):
        for second in range(1, len(vectors) + 1):
            if first != second:
                lines.append(f"set fmri(conmask{first}_{second}) 0")
    return "\n".join(lines) + "\n"


def render(kind: str, source: Path, contrast_path: Path) -> str:
    mapping = (
        {number: number for number in range(1, 11)}
        if kind == "act"
        else {
            **{number: number for number in range(1, 11)},
            14: 11,
            **{number: number - 3 for number in range(15, 25)},
        }
    )
    ev_count = 10 if kind == "act" else 21
    ncontrasts = 28 if kind == "act" else 29
    rendered = []
    for original in source.read_text().splitlines():
        line = original
        setting = re.match(r"^set fmri\(([^)]+)\)\s+(.*)$", line)
        if not setting:
            rendered.append(line)
            continue
        key, value = setting.groups()
        if key == "smooth":
            rendered.append("set fmri(smooth) 0")
            continue
        if key in {"evs_orig", "evs_real"}:
            rendered.append(f"set fmri({key}) {ev_count}")
            continue
        if key in {"ncon_orig", "ncon_real"}:
            rendered.append(f"set fmri({key}) {ncontrasts}")
            continue
        if CONTRAST_KEY.match(key):
            continue
        simple = re.match(r"^([A-Za-z_]+)(\d+)$", key)
        if simple and simple.group(1) in EV_KEYS:
            prefix, old_text = simple.groups()
            old = int(old_text)
            if old not in mapping:
                continue
            new = mapping[old]
            if old == 10 and prefix == "shape":
                value = "SHAPE_EV"
            elif old == 10 and prefix == "convolve":
                value = "3"
            elif old == 10 and prefix == "custom":
                value = '"MISSED_TRIAL"'
            rendered.append(f"set fmri({prefix}{new}) {value}")
            continue
        pair = re.match(r"^(interactionsd?|ortho)(\d+)\.(\d+)$", key)
        if pair:
            prefix, old_first_text, old_second_text = pair.groups()
            old_first, old_second = int(old_first_text), int(old_second_text)
            if old_first not in mapping or (old_second != 0 and old_second not in mapping):
                continue
            first = mapping[old_first]
            second = 0 if old_second == 0 else mapping[old_second]
            rendered.append(f"set fmri({prefix}{first}.{second}) {value}")
            continue
        rendered.append(line)
    contrasts = candidate_contrasts(contrast_path)
    return "\n".join(rendered) + "\n" + contrast_block(kind, contrasts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--type", choices=("act", "ppi"), required=True, dest="kind")
    parser.add_argument("--source", type=Path)
    parser.add_argument(
        "--contrasts",
        type=Path,
        default=ROOT / "templates/FULLTRIAL_CONTRAST_CANDIDATE.tsv",
    )
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source = args.source or SOURCES[args.kind]
    try:
        text = render(args.kind, source, args.contrasts)
    except (KeyError, OSError, ValueError) as error:
        raise SystemExit(f"ERROR: {error}") from error
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text)
    print(f"Rendered pooled {args.kind} FSF: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
