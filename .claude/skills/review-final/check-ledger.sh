#!/usr/bin/env bash
# Does the SDD ledger account for every task in the plan?
#
# THE CONTRACT IS HERS — and it comes from a real failure, 2026-08-03.
#
# The subagent-driven-development skill says a task is done when it has passed
# its task review and been recorded: "tasks with a `Task <N>: complete` line are
# DONE". On the Loom build, tasks 11 and 12 were dispatched, verified in the
# conversation, and merged — with NO review round and NO ledger entry. Nothing
# noticed. The gap was found by luck, because the final reviewer happened to
# read the ledger.
#
# That is the shape of the failure this script exists to remove:
#
#   The ledger is written by the same agent that is supposed to obey it.
#
# So skipping a task is invisible to everyone including the skipper. This makes
# it checkable. It adds no new requirement — the requirement already existed in
# prose and was enforced by nothing.
#
# Usage:  check-ledger.sh PLAN_FILE [LEDGER_FILE]
#         LEDGER_FILE defaults to <repo>/.superpowers/sdd/<plan-basename>/progress.md
# Exit:   0 = every task accounted for, 1 = anything else
#
# DIVERGENCE from check-plan.sh's convention, stated deliberately: there, a check
# whose input is missing reports SKIP. Here a missing ledger is a FAIL, not a
# SKIP. "No ledger exists" is not an absent input — it is positive evidence that
# nothing was gated, which is the exact condition being tested. The shared rule
# that matters is upheld: a missing input NEVER reports PASS.

set -uo pipefail

fail=0
say() { printf '%s  %s\n' "$1" "$2"; }
pass() { say "PASS" "$1"; }
bad()  { say "FAIL" "$1"; fail=1; }

plan="${1:-}"
if [[ -z "$plan" ]]; then
  bad "no PLAN_FILE given (usage: check-ledger.sh PLAN_FILE [LEDGER_FILE])"
  exit 1
fi
if [[ ! -r "$plan" ]]; then
  bad "plan not readable: $plan"
  exit 1
fi

# ---------------------------------------------------------------- tasks in plan
# The plan's task headings. `### Task N:` is the shape writing-plans produces.
# `^STEP N` is ALSO recognised (launchpad-26/buzz's serina:plan-issue skill produces
# plain-text `STEP N  <description>` markers, not `### Task N:` headings) -- added
# because the unrecognised shape used to make the vacuity guard below fire with a
# misleading "found NO task headings" message on a plan that plainly has structure,
# masking the real, separate reason this gate can't clear a STEP-based plan: no
# repository in this cohort's serina:plan-issue workflow produces the SDD ledger
# this script looks for next. Recognising the heading does not relax the ledger
# check one line down -- a STEP-based plan still has no `.superpowers/sdd/.../
# progress.md` to find, so `record ready` on one still correctly refuses. This
# only makes the refusal name its real cause.
mapfile -t plan_tasks < <(grep -oE '^#{1,4} Task [0-9]+|^STEP [0-9]+' "$plan" | grep -oE '[0-9]+' | sort -n -u)

if [[ ${#plan_tasks[@]} -eq 0 ]]; then
  # THE VACUITY GUARD. Without this the script "passes" any file with no task
  # headings at all — a renamed plan, a wrong path, a plan using a different
  # heading level. Zero tasks found is a broken input, never a clean result.
  bad "found NO task headings in $plan — expected lines like '### Task 3:' or 'STEP 3'. Wrong file, or the plan uses a different heading shape. Refusing to report clean on zero tasks."
  exit 1
fi
pass "plan declares ${#plan_tasks[@]} task(s): ${plan_tasks[*]}"

# --------------------------------------------------------------- locate ledger
ledger="${2:-}"
if [[ -z "$ledger" ]]; then
  root="$(git -C "$(dirname "$plan")" rev-parse --show-toplevel 2>/dev/null || true)"
  base="$(basename "$plan")"
  ledger="${root:-.}/.superpowers/sdd/${base%.md}/progress.md"
fi

if [[ ! -r "$ledger" ]]; then
  bad "no readable ledger at $ledger — so no task was recorded as gated. If the ledger lives elsewhere, pass it as the second argument."
  exit 1
fi
pass "ledger found: $ledger"

# ------------------------------------------------------- ledger names this plan
# The SDD skill's convention: the ledger's first line identifies its plan. A
# ledger belonging to a DIFFERENT plan would otherwise satisfy every check below
# with somebody else's completions.
first="$(head -1 "$ledger")"
if [[ "$first" == *"$(basename "$plan")"* ]]; then
  pass "ledger's first line names this plan"
else
  bad "ledger's first line does not name $(basename "$plan") — it reads: ${first:0:80}. This may be another plan's ledger, whose completions would falsely satisfy this check."
fi

# ------------------------------------------------------------- completed tasks
# `complete` must not be a prefix of something else. A real ledger contained
# "Task 4: complete-pending-fix", which is a task MID-LOOP, not a finished one.
# Matching on "complete" alone would have counted it as done.
mapfile -t done_tasks < <(grep -oE '^Task [0-9]+: complete([^-]|$)' "$ledger" \
  | grep -oE 'Task [0-9]+' | grep -oE '[0-9]+$' | sort -n -u)

missing=()
for t in "${plan_tasks[@]}"; do
  found=0
  for d in "${done_tasks[@]:-}"; do
    [[ "$t" == "$d" ]] && { found=1; break; }
  done
  [[ $found -eq 0 ]] && missing+=("$t")
done

if [[ ${#missing[@]} -eq 0 ]]; then
  pass "every task has a 'Task N: complete' line (${#done_tasks[@]} recorded)"
else
  bad "task(s) ${missing[*]} have NO 'Task N: complete' line in the ledger. Either they were never gated, or they were gated and not recorded — both mean the branch cannot be declared done. (recorded: ${done_tasks[*]:-none})"
fi

# ------------------------------------------- mid-loop tasks are not finished
mapfile -t pending < <(grep -oE '^Task [0-9]+: (complete-pending|fix round)' "$ledger" \
  | grep -oE 'Task [0-9]+' | grep -oE '[0-9]+$' | sort -n -u)
for p in "${pending[@]:-}"; do
  [[ -z "$p" ]] && continue
  closed=0
  for d in "${done_tasks[@]:-}"; do
    [[ "$p" == "$d" ]] && { closed=1; break; }
  done
  [[ $closed -eq 0 ]] && bad "task $p has a fix round or a complete-pending entry but never a plain 'complete' line — its loop was left open."
done

exit "$fail"
