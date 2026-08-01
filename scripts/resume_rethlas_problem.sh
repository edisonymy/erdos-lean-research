#!/usr/bin/env bash
# Resume one non-blind Rethlas problem after an interrupted first attempt.

set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 <problem-name-without-.md> <attempt-number>" >&2
  exit 2
fi

problem="$1"
attempt="$2"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
workspace="$(cd "$script_dir/.." && pwd)"
runner="${RETHLAS_ROOT:-$workspace/third_party/rethlas-runner}"

if ! command -v jq >/dev/null 2>&1; then
  jq_dir="/c/Users/Edison Yi/AppData/Local/Microsoft/WinGet/Packages/jqlang.jq_Microsoft.Winget.Source_8wekyb3d8bbwe"
  if [[ -x "$jq_dir/jq.exe" ]]; then
    export PATH="$jq_dir:$PATH"
  fi
fi

for dependency in codex curl jq python3; do
  command -v "$dependency" >/dev/null 2>&1 || {
    echo "missing dependency: $dependency" >&2
    exit 2
  }
done

cd "$runner"
export PROBLEM_FILE="data/math_frontier/${problem}.md"
export PROBLEM_ID="math_frontier/${problem}"
export ATTEMPT_NUMBER="$attempt"
export MAX_ATTEMPTS="$attempt"
export MODEL="${MODEL:-gpt-5.6-sol}"
export REASONING_EFFORT="${REASONING_EFFORT:-xhigh}"
export BLIND_RUN=0

exec scripts/resume_single_attempt.sh
