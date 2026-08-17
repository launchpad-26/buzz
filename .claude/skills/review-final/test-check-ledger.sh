#!/usr/bin/env bash
# Controls for check-ledger.sh.
#
# Two questions per control, the pair this repository uses on any check:
#   1. Could the check PASS if the thing it tests did not exist?
#   2. Could the value it asserts occur by accident?
#
# Case B answers the first (zero tasks found must never read as clean). Case E
# answers the second: a real ledger contained "Task 4: complete-pending-fix",
# and a match on "complete" alone would have counted a mid-loop task as done.
#
# Usage:  test-check-ledger.sh
# Exit:   0 = every control behaved, 1 = at least one did not

set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
check="$here/check-ledger.sh"
[[ -x "$check" ]] || { echo "FAIL  check-ledger.sh not found or not executable at $check"; exit 1; }

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
fail=0

# expect <wanted-exit> <label> <args...>
expect() {
  local want="$1" label="$2"; shift 2
  local out rc
  out="$("$check" "$@" 2>&1)"; rc=$?
  if [[ "$rc" -eq "$want" ]]; then
    printf 'PASS  %s\n' "$label"
  else
    printf 'FAIL  %s (wanted exit %s, got %s)\n' "$label" "$want" "$rc"
    printf '%s\n' "$out" | sed 's/^/        /'
    fail=1
  fi
}

# also assert the message names the offending task, not just that it failed —
# a check that fails for the wrong reason is not a working check.
expect_naming() {
  local want="$1" needle="$2" label="$3"; shift 3
  local out rc
  out="$("$check" "$@" 2>&1)"; rc=$?
  if [[ "$rc" -eq "$want" ]] && printf '%s' "$out" | grep -q -- "$needle"; then
    printf 'PASS  %s\n' "$label"
  else
    printf 'FAIL  %s (wanted exit %s containing %q, got exit %s)\n' "$label" "$want" "$needle" "$rc"
    printf '%s\n' "$out" | sed 's/^/        /'
    fail=1
  fi
}

printf '### Task 0: a\n### Task 1: b\n### Task 2: c\n' > "$tmp/plan.md"

printf '# SDD ledger — plan: plan.md\nTask 0: complete (x)\nTask 1: complete (y)\nTask 2: complete (z)\n' > "$tmp/full.md"
expect 0 "A  every task complete -> clean" "$tmp/plan.md" "$tmp/full.md"

printf 'no headings here\njust prose\n' > "$tmp/noheads.md"
expect_naming 1 "NO task headings" "B  zero task headings -> refuses to report clean (vacuity guard)" \
  "$tmp/noheads.md" "$tmp/full.md"

expect_naming 1 "no readable ledger" "C  missing ledger -> FAIL, not SKIP" \
  "$tmp/plan.md" "$tmp/nosuchfile.md"

printf '# SDD ledger — plan: SOMEONE-ELSE.md\nTask 0: complete\nTask 1: complete\nTask 2: complete\n' > "$tmp/wrongplan.md"
expect_naming 1 "does not name" "D  another plan's ledger -> FAIL even though all tasks look complete" \
  "$tmp/plan.md" "$tmp/wrongplan.md"

printf '# SDD ledger — plan: plan.md\nTask 0: complete\nTask 1: complete\nTask 2: complete-pending-fix\n' > "$tmp/pending.md"
expect_naming 1 "task(s) 2" "E  complete-pending-fix does NOT count as complete" \
  "$tmp/plan.md" "$tmp/pending.md"

printf '# SDD ledger — plan: plan.md\nTask 0: complete\nTask 1: complete\nTask 2: fix round 2/5 dispatched\n' > "$tmp/openloop.md"
expect_naming 1 "loop was left open" "F  fix round never closed -> named as an open loop" \
  "$tmp/plan.md" "$tmp/openloop.md"

expect 1 "G  no arguments at all -> FAIL"

# The regression this script exists for: the Loom build, whose ledger stopped at
# task 10 while the plan declared 13. Reconstructed rather than referencing the
# real files, so this test does not break when that repo moves.
printf '### Task %d: x\n' 0 1 2 3 4 5 6 7 8 9 10 11 12 > "$tmp/loomplan.md"
{ printf '# SDD ledger — plan: loomplan.md\n'; printf 'Task %d: complete\n' 0 1 2 3 4 5 6 7 8 9 10; } > "$tmp/loomledger.md"
expect_naming 1 "task(s) 11 12" "H  the real 2026-08-03 regression: plan has 13, ledger stops at 10" \
  "$tmp/loomplan.md" "$tmp/loomledger.md"

# launchpad-26/buzz's serina:plan-issue skill writes plain-text `STEP N` markers,
# not `### Task N:` headings. Before this control existed, that shape hit the
# vacuity guard and reported "found NO task headings" on a plan that plainly has
# structure -- the wrong reason. STEP headings must now be recognised (so the
# guard does not fire), but recognising them must NOT relax the ledger check one
# line down: no SDD ledger exists for a STEP-based plan in that workflow, so this
# must still refuse -- for the true, now-correctly-named reason.
printf 'STEP 1  do the first thing                        [independent]\nSTEP 2  do the second thing                        [needs 1]\n' > "$tmp/stepplan.md"
expect_naming 1 "no readable ledger" "I  STEP N headings are recognised, and still correctly refuse (no ledger exists)" \
  "$tmp/stepplan.md" "$tmp/nosuchfile.md"

if [[ $fail -eq 0 ]]; then
  printf '\nall controls behaved\n'
else
  printf '\nSOME CONTROLS FAILED\n'
fi
exit "$fail"
