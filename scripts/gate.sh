#!/bin/bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly ROOT
cd "${ROOT}"
export PATH="${ROOT}/.cache/tools/bin:${PATH}"
# The Ghostty app bundle on macOS does not put its command-line tool on PATH.
readonly GHOSTTY_APP="/Applications/Ghostty.app/Contents/MacOS"
if [[ "$(uname -s)" == Darwin ]] && ! command -v ghostty >/dev/null && [[ -x "${GHOSTTY_APP}/ghostty" ]]; then
  export PATH="${PATH}:${GHOSTTY_APP}"
fi
export PLAYWRIGHT_BROWSERS_PATH="${ROOT}/.cache/browsers"
export DO_NOT_TRACK=1
export IMPECCABLE_NO_TELEMETRY=1
export PYTHONPATH=scripts
mkdir -p "${ROOT}/.cache/tmp"
export TMPDIR="${ROOT}/.cache/tmp"
export UV_CACHE_DIR="${ROOT}/.cache/uv"
export npm_config_cache="${ROOT}/.cache/npm"
exec uv run --locked python scripts/gate.py
