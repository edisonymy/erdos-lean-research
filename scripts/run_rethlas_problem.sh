#!/usr/bin/env bash
# Launch one non-blind Rethlas research attempt from Git Bash on Windows.

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 <problem-name-without-.md> [max-attempts]" >&2
  exit 2
fi

problem="$1"
attempts="${2:-1}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
workspace="$(cd "$script_dir/.." && pwd)"
runner="${RETHLAS_ROOT:-$workspace/third_party/rethlas-runner}"

if ! command -v jq >/dev/null 2>&1; then
  jq_dir="/c/Users/Edison Yi/AppData/Local/Microsoft/WinGet/Packages/jqlang.jq_Microsoft.Winget.Source_8wekyb3d8bbwe"
  if [[ -x "$jq_dir/jq.exe" ]]; then
    export PATH="$jq_dir:$PATH"
  fi
fi

for dependency in codex curl jq python3 stat; do
  command -v "$dependency" >/dev/null 2>&1 || {
    echo "missing dependency: $dependency" >&2
    exit 2
  }
done

cd "$runner"
export PROBLEM_FILE="data/math_frontier/${problem}.md"
export PROBLEM_ID="math_frontier/${problem}"
export MAX_ATTEMPTS="$attempts"
export MODEL="${MODEL:-gpt-5.6-sol}"
export REASONING_EFFORT="${REASONING_EFFORT:-xhigh}"
export BLIND_RUN=0
export CONTINUE_ROUNDS="${CONTINUE_ROUNDS:-0}"
export TOKEN_BUDGET="${TOKEN_BUDGET:-0}"
export CODEX_SILENT_TIMEOUT_SECONDS="${CODEX_SILENT_TIMEOUT_SECONDS:-1800}"
export CODEX_POLL_SECONDS="${CODEX_POLL_SECONDS:-30}"

exec scripts/run_with_retries.sh
