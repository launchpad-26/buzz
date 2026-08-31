#!/usr/bin/env bash
# The trigger. One `tick` per managed repository, per lane, per firing.
#
# WHAT THIS IS FOR. The reviewer panel authenticates with local Claude and Codex
# subscription credentials, which a CI runner cannot hold, so the thing that
# decides "is there work right now" has to run on the operator's own machine.
# This script is what a timer (launchd on macOS, systemd or cron elsewhere)
# invokes. It contains no review logic and no repository-specific knowledge: it
# iterates the repository roots it is given and lets `dispatcher.py tick` decide
# whether each is due.
#
# WHY A FIXED-INTERVAL TIMER AND NOT A SLEEP LOOP. `tick` keeps its own adaptive
# schedule in the `cadence` table, so the timer can fire at the shortest interval
# the cadence can choose and most firings will report `not_due` and exit. That
# keeps the state-directory runtime lock held only while real work happens — the
# one-worker-per-state-directory invariant from 0b8e64732 — and means a crash,
# a reboot or a closed laptop lid costs at most one interval instead of silently
# ending the automation.
#
# ONE STATE DIRECTORY PER REPOSITORY. Each managed repository has its own
# repo-local `.review-queue-automation/config.json` naming its own `state_dir`.
# Sharing one state directory across repositories would cross the same invariant
# and produce `sweep_already_running` instead of work.
#
# Usage:
#   scheduled-tick.sh <repo-root> [<repo-root> ...]
#
# Environment:
#   RQA_LANES   space-separated lanes to tick per repo. Default: "incoming_review".
#               Add "author_triage" once that lane's canary is approved.
#   RQA_LIMIT   jobs dispatched per lane per tick. Default: 2.
#   RQA_PYTHON  python interpreter. Default: python3.
#
# Exit status is the worst of the ticks: 0 when every repository ticked cleanly,
# non-zero when any failed, so a timer's own failure reporting stays meaningful.

set -uo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${RQA_PYTHON:-python3}"
LANES="${RQA_LANES:-incoming_review}"
LIMIT="${RQA_LIMIT:-2}"

if [[ $# -eq 0 ]]; then
  echo "Usage: $(basename "$0") <repo-root> [<repo-root> ...]" >&2
  exit 2
fi

worst=0
for repo_root in "$@"; do
  if [[ ! -d "$repo_root" ]]; then
    echo "{\"status\":\"error\",\"repo_root\":\"$repo_root\",\"reason\":\"not a directory\"}" >&2
    worst=1
    continue
  fi
  # A repository that has never been onboarded has no repo-local config. `tick`
  # already reports `onboarding_required` and exits non-zero for that, which is
  # the honest answer — it is not this script's job to guess a config.
  for lane in $LANES; do
    if ! "$PYTHON" "$SCRIPT_DIR/dispatcher.py" \
        --repo-root "$repo_root" \
        tick --lane "$lane" --limit "$LIMIT"; then
      worst=1
    fi
  done
done

exit "$worst"
