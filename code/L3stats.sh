#!/usr/bin/env bash
# One ordinary FEAT higher-level model. Outer Python launcher bounds concurrency.
set -euo pipefail
export FSLSUB_PARALLEL=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
unset DISPLAY
[[ $# == 1 && -s "$1" ]] || { echo 'Usage: bash code/L3stats.sh RENDERED.fsf' >&2; exit 2; }
command -v feat >/dev/null
command -v flameo >/dev/null
exec feat "$1"
