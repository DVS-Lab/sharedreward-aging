#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)";source "$SCRIPT_DIR/project_config.sh";tool="$RF1_SHAREDREWARD_ROOT/code/smooth_to_target.sh";[[ -f "$tool" ]]||{ echo "ERROR: authoritative utility not found: $tool" >&2;exit 1;};exec bash "$tool" "$@"
