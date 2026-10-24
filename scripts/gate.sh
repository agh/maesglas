#!/bin/bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly ROOT
cd "${ROOT}"
export PATH="${ROOT}/.cache/tools/bin:${PATH}"
export PLAYWRIGHT_BROWSERS_PATH="${ROOT}/.cache/browsers"
export DO_NOT_TRACK=1
export IMPECCABLE_NO_TELEMETRY=1
export PYTHONPATH=scripts
mkdir -p "${ROOT}/.cache/tmp"
export TMPDIR="${ROOT}/.cache/tmp"
export UV_CACHE_DIR="${ROOT}/.cache/uv"
export npm_config_cache="${ROOT}/.cache/npm"
exec uv run --locked python scripts/gate.py
