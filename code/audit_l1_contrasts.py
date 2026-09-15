#!/usr/bin/env python3
"""Check retained contrast IDs/weights and report unsupported neutral effects."""

import argparse
import io
import json
import re
from pathlib import Path

import numpy as np
from render_pooled_fsf import ROOT, candidate_contrasts

NEUTRAL_IDS = {7, 8, 9, 20, 21, 22}


def matrix(path):
    text = path.read_text()
    return np.loadtxt(io.StringIO(text.split('/Matrix', 1)[1]), ndmin=2)


def audit(directory, kind):
    directory = Path(directory)
    settings = dict(re.findall(r'^set fmri\(([^)]+)\)\s+([^\n]+)',
                               (directory / 'design.fsf').read_text(), re.M))
    if kind not in ('act', 'ppi') and not kind.startswith('ppi_seed-'):
        raise ValueError(f'unknown model type: {kind}')
    ppi = kind != 'act'
    names, weights = zip(*candidate_contrasts(ROOT / 'templates/FULLTRIAL_CONTRAST_CANDIDATE.tsv'))
    names = list(names)
    intended = np.array(weights) if not ppi else np.array(
        [[0.] * 11 + w for w in weights] + [[0.] * 10 + [1.] + [0.] * 10])
    if ppi:
        names.append('phys')
    for key, value in {'conmask1_1': '0', 'smooth': '0', 'featwatcher_yn': '0',
                       'ncon_real': str(len(names)), 'ncon_orig': str(len(names)),
                       'evs_real': str(intended.shape[1]), 'evs_orig': str(intended.shape[1])}.items():
        if settings.get(key) != value:
            raise ValueError(f'{key}: expected {value}, found {settings.get(key)}')
    for mode in ('real', 'orig'):
        for i, name in enumerate(names, 1):
            if settings.get(f'conname_{mode}.{i}', '').strip('"') != name:
                raise ValueError(f'contrast {i}: name/number mismatch')
            actual = [float(settings[f'con_{mode}{i}.{j}']) for j in range(1, intended.shape[1] + 1)]
            if not np.allclose(actual, intended[i-1], atol=1e-8, rtol=0):
                raise ValueError(f'contrast {i}: intended FSF weights differ')
    x, c = matrix(directory / 'design.mat'), matrix(directory / 'design.con')
    if c.shape != (len(names), x.shape[1]) or x.shape[1] < intended.shape[1]:
        raise ValueError('design/contrast dimensions do not match retained model')
    if not np.isfinite(x).all() or not np.isfinite(c).all():
        raise ValueError('nonfinite design or contrast matrix')
    expected = np.pad(intended, ((0, 0), (0, x.shape[1] - intended.shape[1])))
    empty = [i for i in (7, 8, 9) if settings.get(f'shape{i}') == '10']
    for i in empty:
        columns = [i - 1, i + 10] if ppi else [i - 1]
        if np.any(np.abs(x[:, columns]) > 1e-10):
            raise ValueError(f'empty neutral EV {i} has nonzero design values')
        # Installed FSL automatically zeroes a one-EV contrast on an empty EV.
        # Permit either the original intended row or its zeroed form; no other
        # changed weights, dropped slots, or nuisance coefficients are allowed.
        if np.all(c[i-1] == 0):
            expected[i-1] = 0
    if not np.allclose(c, expected, atol=1e-8, rtol=0):
        raise ValueError('generated design.con differs from intended contrast contract')
    # Assess the intended hypotheses, not the automatically zeroed rows.
    requested = np.pad(intended, ((0, 0), (0, x.shape[1] - intended.shape[1])))
    errors = np.max(np.abs(requested - requested @ np.linalg.pinv(x) @ x), axis=1)
    unsupported = [i+1 for i, error in enumerate(errors) if error > 1e-5]
    if set(unsupported) - NEUTRAL_IDS:
        raise ValueError(f'non-estimable primary contrasts: {unsupported}')
    return {'type': kind, 'ncontrasts': len(names), 'empty_neutral_evs': empty,
            'unsupported_neutral_contrasts': [{'cope': i, 'name': names[i-1]} for i in unsupported],
            'fsl_zeroed_contrasts': (np.flatnonzero(np.max(np.abs(c), axis=1) == 0) + 1).tolist(),
            'primary_contrasts_estimable': True,
            'note': 'Neutral contrasts retained for consistent numbering; not approved for inference.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--feat-dir', required=True, type=Path)
    parser.add_argument('--type', required=True, dest='kind')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        result = audit(args.feat_dir, args.kind)
    except (OSError, ValueError, KeyError, IndexError, np.linalg.LinAlgError) as error:
        parser.exit(1, f'ERROR: contrast audit: {error}\n')
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    print('CHECK PASSED: retained contrast numbering/weights and primary estimability.')


if __name__ == '__main__':
    main()
