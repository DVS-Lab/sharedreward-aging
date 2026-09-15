#!/usr/bin/env python3
"""Reject stale pooled models after contrast or input changes; never delete data."""

import argparse
import hashlib
import json
import re
from pathlib import Path

STAMP = "pooled-model-inputs.json"
CONTRACT = "fulltrial-neutral-nuisance-v2"


def fingerprint(path, image=False):
    path = Path(path).resolve(strict=True)
    if image:
        stat = path.stat()
        return {"path": str(path), "size": stat.st_size, "mtime_ns": stat.st_mtime_ns}
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def snapshot(level, kind, inputs, images, parents):
    return {"contract": CONTRACT, "level": level, "type": kind,
            "inputs": [fingerprint(p) for p in inputs],
            "images": [fingerprint(p, True) for p in images],
            "parents": [str(Path(p).resolve()) for p in parents]}


def validate_stamp(stamp, level, kind, expected=None):
    data = json.loads(Path(stamp).read_text())
    if (data["contract"], data["level"], data["type"]) != (CONTRACT, level, kind):
        raise ValueError("model contract/type mismatch")
    current = snapshot(level, kind, [p["path"] for p in data["inputs"]],
                       [p["path"] for p in data["images"]], data["parents"])
    if data != current or (expected is not None and data != expected):
        raise ValueError("model inputs changed")
    for parent in data["parents"]:
        validate_model(Path(parent), "l1", kind)


def validate_model(output, level, kind):
    output = Path(output)
    validate_stamp(output / STAMP, level, kind)
    n = 22 if kind == "act" else 23
    designs = [(output / "design.con", n)] if level == "l1" else [
        (output / f"cope{i}.feat/design.con", 1) for i in range(1, n + 1)]
    for path, expected in designs:
        match = re.search(r"^/NumContrasts\s+(\d+)\s*$", path.read_text(), re.M)
        if not match or int(match[1]) != expected:
            raise ValueError(f"unexpected contrast count: {path}")
    if level == "l2" and (output / f"cope{n+1}.feat").exists():
        raise ValueError("legacy extra cope directory")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("write", "check", "audit"))
    parser.add_argument("--path", required=True, type=Path,
                        help="Stamp for write/check; FEAT directory for audit")
    parser.add_argument("--level", required=True, choices=("l1", "l2"))
    parser.add_argument("--type", required=True, dest="kind")
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--image", action="append", default=[])
    parser.add_argument("--parent", action="append", default=[])
    args = parser.parse_args()
    try:
        if args.action == "audit":
            validate_model(args.path, args.level, args.kind)
        else:
            expected = snapshot(args.level, args.kind, args.input, args.image, args.parent)
            if args.action == "write":
                args.path.write_text(json.dumps(expected, indent=2) + "\n")
            else:
                validate_stamp(args.path, args.level, args.kind, expected)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"ERROR: stale/unverified model: {error}. Review and explicitly rerun; do not retrofit a stamp onto old output.\n")


if __name__ == "__main__":
    main()
