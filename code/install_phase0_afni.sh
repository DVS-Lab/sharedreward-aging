#!/usr/bin/env bash

# Install the complete official AFNI command-line distribution without touching dotfiles.

set -euo pipefail

package="${AFNI_PACKAGE:-linux_openmp_64}"
phase0_env="${PHASE0_ENV:-/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0}"
bindir="${AFNI_BIN_DIR:-${phase0_env}/afni-bin}"
url="https://afni.nimh.nih.gov/pub/dist/tgz/${package}.tgz"

for command_name in curl tar sha256sum; do
    command -v "$command_name" >/dev/null || {
        echo "ERROR: required command unavailable: $command_name" >&2
        exit 1
    }
done

[[ -d "$phase0_env" ]] || {
    echo "ERROR: Phase 0 environment not found: $phase0_env" >&2
    exit 1
}

if [[ -e "$bindir" ]]; then
    echo "ERROR: AFNI installation target already exists: $bindir" >&2
    echo "Review it rather than overwriting it." >&2
    exit 1
fi

work="$(mktemp -d "${TMPDIR:-/tmp}/sharedreward-afni.XXXXXX")"
trap 'rm -rf -- "$work"' EXIT
archive="${work}/${package}.tgz"

echo "Downloading: $url"
curl --fail --location --show-error "$url" --output "$archive"
archive_sha256="$(sha256sum "$archive" | awk '{print $1}')"

tar -xzf "$archive" -C "$work"
source_dir="${work}/${package}"
[[ -d "$source_dir" ]] || {
    echo "ERROR: archive did not contain expected directory: $package" >&2
    exit 1
}

for command_name in afni 3dFWHMx 3dresample 3dBlurToFWHM; do
    [[ -x "${source_dir}/${command_name}" ]] || {
        echo "ERROR: downloaded AFNI package lacks: $command_name" >&2
        exit 1
    }
done

mkdir -p "$(dirname "$bindir")"
mv "$source_dir" "$bindir"

{
    printf 'source_url=%s\n' "$url"
    printf 'archive_sha256=%s\n' "$archive_sha256"
    printf 'installed_at=%s\n' "$(date --iso-8601=seconds)"
    printf 'host=%s\n' "$(hostname)"
    printf 'package=%s\n' "$package"
} > "${bindir}/INSTALL_PROVENANCE.txt"

echo "Installed complete AFNI distribution: $bindir"
echo "Archive SHA-256: $archive_sha256"
echo "For this shell, run:"
printf 'export AFNI_BIN_DIR=%q\n' "$bindir"
printf 'export PATH=%q:$PATH\n' "$bindir"
