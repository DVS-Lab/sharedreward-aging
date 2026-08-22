#!/usr/bin/env bash

# Capture a raw local log and a compact Git-trackable run record.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
# shellcheck source=project_config.sh
source "${SCRIPT_DIR}/project_config.sh"
usage() { echo "Usage: run_logged.sh [--label LABEL] [--include-full-log] -- COMMAND [ARGS...] [--check CHECK_COMMAND [ARGS...]]" >&2; }
label=""; include_full=0
while (( $# )); do case "$1" in --label) label="$2"; shift 2 ;; --include-full-log) include_full=1; shift ;; --) shift; break ;; -h|--help) usage; exit 0 ;; *) echo "ERROR: unknown wrapper argument: $1" >&2; usage; exit 2 ;; esac; done
(( $# )) || { usage; exit 2; }
cmd=(); check=()
while (( $# )); do if [[ "$1" == --check ]]; then shift; check=("$@"); break; fi; cmd+=("$1"); shift; done
[[ -n "$label" ]] || label="$(basename "${cmd[0]}")"; label="$(printf '%s' "${label%.*}" | tr -c 'A-Za-z0-9_.-' '_')"
stamp="$(date +%Y%m%d-%H%M%S)"; raw_dir="${PROJECT_ROOT}/logs/runs"; record_dir="${PROJECT_ROOT}/logs/records"; mkdir -p "$raw_dir" "$record_dir"
raw="${raw_dir}/${stamp}_${label}.log"; record="${record_dir}/${stamp}_${label}.md"; status_file="${raw}.status"
commit="$(git -C "$PROJECT_ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)"; branch="$(git -C "$PROJECT_ROOT" branch --show-current 2>/dev/null || echo unknown)"
cmd_string="$(printf '%q ' "${cmd[@]}")"; check_string=""; (( ${#check[@]} )) && check_string="$(printf '%q ' "${check[@]}")"
echo "Writing raw log: $raw"; echo "Writing run record: $record"
set +e
(
    command_status=0; check_status=none; final=0
    printf 'RUN START: %s\nPROJECT_ROOT: %s\nGIT: %s %s\nHOST: %s\nUSER: %s\nPWD: %s\nCOMMAND: %s\n\n' "$stamp" "$PROJECT_ROOT" "$branch" "$commit" "$(hostname)" "$(whoami)" "$(pwd)" "$cmd_string"
    "${cmd[@]}"; command_status=$?; printf '\nCOMMAND EXIT: %s\n' "$command_status"
    if (( ${#check[@]} )) && (( command_status == 0 )); then printf '\nCHECK COMMAND: %s\n\n' "$check_string"; "${check[@]}"; check_status=$?; printf '\nCHECK EXIT: %s\n' "$check_status"; elif (( ${#check[@]} )); then check_status=skipped; echo 'CHECK SKIPPED: command failed.'; fi
    final="$command_status"; [[ "$check_status" =~ ^[0-9]+$ ]] && (( check_status != 0 )) && final="$check_status"
    printf 'COMMAND_STATUS=%s\nCHECK_STATUS=%s\n' "$command_status" "$check_status" > "$status_file"; exit "$final"
) 2>&1 | tee "$raw"
status=${PIPESTATUS[0]}; set -e; COMMAND_STATUS=unknown; CHECK_STATUS=none; source "$status_file"; rm -f "$status_file"
summary="$(grep -E 'CHECK (PASSED|FAILED):' "$raw" | tail -1 || true)"; [[ -n "$summary" ]] || summary="COMMAND exit ${COMMAND_STATUS}; CHECK ${CHECK_STATUS}."
{
    echo "# Run Record: $label"; echo; echo "- Timestamp: $stamp"; echo "- Branch: $branch"; echo "- Commit: $commit"; echo "- Host: $(hostname)"; echo "- User: $(whoami)"; echo "- Working directory: \`$(pwd)\`"; echo "- Raw log: \`$raw\`"; echo "- Command exit: $COMMAND_STATUS"; echo "- Check exit: $CHECK_STATUS"; echo "- Summary: $summary"; echo; echo '## Command'; echo; echo '```bash'; echo "$cmd_string"; echo '```'
    if (( ${#check[@]} )); then echo; echo '## Check'; echo; echo '```bash'; echo "$check_string"; echo '```'; fi
    if (( include_full )) || [[ "$COMMAND_STATUS" != 0 || ( "$CHECK_STATUS" != none && "$CHECK_STATUS" != 0 ) ]]; then echo; echo '## Log'; echo; echo '```text'; (( include_full )) && cat "$raw" || tail -n "${RUN_RECORD_TAIL_LINES:-120}" "$raw"; echo '```'; fi
} > "$record"
echo "Run record saved: $record"; exit "$status"
