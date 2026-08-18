#!/usr/bin/env bash
# Controls for verdict.sh.
#
# Two questions per control, the pair this repository uses on any check:
#   1. Could the check PASS if the thing it tests did not exist?
#   2. Could the value it asserts occur by accident?
#
# Case B answers the first. Before 2026-08-06 the `--issue` path returned before
# reaching the test gate, so `record ready --issue N` wrote READY over a FAILING
# suite and `verdict.sh check` then opened. The escape hatch built because
# "issue-driven work has no ledger" also skipped the test suite, which has nothing
# to do with whether a plan exists.
#
# Case D answers the second: the recorded `test_cmd` field used to hold the command
# string on BOTH paths — written after running it on one, and without running it on
# the other — so "ran and passed" was indistinguishable from "never ran".
#
# EVERY CONTROL ASSERTS ON WHETHER THE FILE WAS WRITTEN, not on the exit code
# alone. A refusal that still leaves a READY verdict on disk has failed, and an
# exit-code-only control could not see that.
#
# Fixtures are a throwaway repository, never this one: `record` overwrites
# .superpowers/verdict.json, and running these in place would destroy a real
# verdict.
#
# Usage:  test-verdict.sh
# Exit:   0 = every control behaved, 1 = at least one did not

set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for req in verdict.sh check-ledger.sh; do
  [[ -x "$here/$req" ]] || { echo "FAIL  $req not found or not executable at $here"; exit 1; }
done

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
fail=0

# A repo with a plan whose ledger is COMPLETE, so the ledger check passes and the
# test gate is the only thing left that can refuse. Without a passing ledger the
# plan-path controls would refuse for the wrong reason.
repo="$tmp/repo"
mkdir -p "$repo/.claude/skills/review-final" "$repo/.superpowers/sdd/plan"
cp "$here/verdict.sh" "$here/check-ledger.sh" "$repo/.claude/skills/review-final/"
chmod +x "$repo/.claude/skills/review-final/"*.sh
git -C "$repo" init -q
git -C "$repo" config user.email fixture@example.invalid
git -C "$repo" config user.name fixture
printf '### Task 0: a\n' > "$repo/plan.md"
printf '# SDD ledger — plan: plan.md\nTask 0: complete\n' > "$repo/.superpowers/sdd/plan/progress.md"
printf 'x\n' > "$repo/f.txt"
git -C "$repo" add -A >/dev/null 2>&1
git -C "$repo" commit -qm baseline

V=".claude/skills/review-final/verdict.sh"

# control WANT_WRITTEN LABEL TESTCMD ARGS...
#   WANT_WRITTEN is YES or NO — did a verdict file end up on disk?
#   TESTCMD is the VERDICT_TEST_CMD value, or the literal word UNSET.
control() {
  local want="$1" label="$2" testcmd="$3"; shift 3
  local out wrote
  rm -f "$repo/.superpowers/verdict.json"
  if [[ "$testcmd" == UNSET ]]; then
    out="$(cd "$repo" && bash "$V" record ready "$@" 2>&1)"
  else
    out="$(cd "$repo" && VERDICT_TEST_CMD="$testcmd" bash "$V" record ready "$@" 2>&1)"
  fi
  wrote=NO; [[ -f "$repo/.superpowers/verdict.json" ]] && wrote=YES
  if [[ "$wrote" == "$want" ]]; then
    printf 'PASS  %s\n' "$label"
  else
    printf 'FAIL  %s (verdict written=%s, wanted %s)\n' "$label" "$wrote" "$want"
    printf '%s\n' "$out" | sed 's/^/        /'
    fail=1
  fi
}

# reads the recorded checks.test_cmd value
recorded() {
  python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["checks"]["test_cmd"])' \
    "$repo/.superpowers/verdict.json" 2>/dev/null
}

expect_recorded() {
  local needle="$1" label="$2" got
  got="$(recorded)"
  if [[ "$got" == *"$needle"* ]]; then
    printf 'PASS  %s\n' "$label"
  else
    printf 'FAIL  %s (recorded %q, wanted it to contain %q)\n' "$label" "$got" "$needle"
    fail=1
  fi
}

# ------------------------------------------------------ A: the plan path refuses
control NO "A  plan path + FAILING test command -> refuses" false plan.md

# ------------------------------- B: the regression. --issue must refuse too.
control NO "B  --issue + FAILING test command -> refuses (was: wrote READY)" false --issue 99

# ---------------------------------------------- C: positive controls, both paths
# Without these, a verdict.sh that refused everything would satisfy A and B.
control YES "C1 --issue + passing test command -> READY" true --issue 99
control YES "C2 plan path + passing test command -> READY" true plan.md

# ------------------------------- D: the recorded field must say WHICH happened
control YES "D1 --issue + passing test -> READY" true --issue 99
expect_recorded "passed:" "D2 records that the command actually ran and passed"

control YES "D3 --issue with no VERDICT_TEST_CMD -> READY" UNSET --issue 99
expect_recorded "not-run" "D4 records that no command ran, distinct from passing"

# ------------------- G: SHELL TEXT MUST NOT REACH THE JSON DOCUMENT UNESCAPED
#
# The file was built by heredoc, so `$reason` landed between quotes verbatim. A
# reason carrying a quote could add a SECOND `state` key — valid JSON with a
# duplicate, Python takes the last — and a NOT_READY verdict OPENED the gate.
# That breaks the property this script states in its own header: "THREE STATES,
# NOT TWO... nothing must never read as approval."
#
# It needs a hand-crafted string, so nobody types it by accident. It is also
# exactly what someone under pressure to unblock a merge might reach for, and a
# gate must not be defeatable by the party it constrains.
rm -f "$repo/.superpowers/verdict.json"
( cd "$repo" && bash "$V" record notready 'red", "state": "READY", "note": "x' >/dev/null 2>&1 )
got_state="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["state"])' \
  "$repo/.superpowers/verdict.json" 2>/dev/null || echo UNPARSEABLE)"
if [[ "$got_state" == "NOT_READY" ]]; then
  printf 'PASS  %s\n' "G1 a crafted notready reason stays NOT_READY"
else
  printf 'FAIL  %s (state read back as %q)\n' "G1 a crafted notready reason stays NOT_READY" "$got_state"; fail=1
fi
if ( cd "$repo" && bash "$V" check >/dev/null 2>&1 ); then
  printf 'FAIL  %s\n' "G2 the gate must stay SHUT after a crafted notready"; fail=1
else
  printf 'PASS  %s\n' "G2 the gate stays shut after a crafted notready"
fi

# A quoted test command used to produce unreadable JSON while announcing READY.
# Fails closed, but the script must not claim to have written what it cannot read.
rm -f "$repo/.superpowers/verdict.json"
( cd "$repo" && VERDICT_TEST_CMD='true --grep "focus"' bash "$V" record ready --issue 99 >/dev/null 2>&1 )
if python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$repo/.superpowers/verdict.json" 2>/dev/null; then
  printf 'PASS  %s\n' "G3 a quoted test command still yields readable JSON"
else
  printf 'FAIL  %s\n' "G3 a quoted test command produced unparseable JSON"; fail=1
fi

# `plan: null` is load-bearing — it is how a reader tells issue-driven work from
# plan-driven. An earlier null sentinel was passed through bash as four literal
# characters and silently became the STRING "\0null".
plan_field="$(python3 -c 'import json,sys; print(repr(json.load(open(sys.argv[1]))["plan"]))' \
  "$repo/.superpowers/verdict.json" 2>/dev/null || echo MISSING)"
if [[ "$plan_field" == "None" ]]; then
  printf 'PASS  %s\n' "G4 the issue path records plan as a real JSON null"
else
  printf 'FAIL  %s (plan is %s, not null)\n' "G4 the issue path records plan as a real JSON null" "$plan_field"; fail=1
fi

# ---------------------------------------- E: the ledger gate is still a gate
# Removing the ledger must make the PLAN path refuse — and must NOT be routable
# around by switching to --issue on work that has a plan. The second half is a
# judgement the script cannot enforce; what it can do is record which claim was
# made, which D above checks.
rm -f "$repo/.superpowers/sdd/plan/progress.md"
control NO "E  plan path with no ledger -> refuses" true plan.md
printf '# SDD ledger — plan: plan.md\nTask 0: complete\n' > "$repo/.superpowers/sdd/plan/progress.md"

# ------------------------------------------- F: arguments that make no sense
control NO "F1 --issue with no number -> refuses" true --issue
control NO "F2 a plan file that does not exist -> refuses" true nosuchplan.md

if [[ $fail -eq 0 ]]; then
  printf '\nall controls behaved\n'
else
  printf '\nSOME CONTROLS FAILED\n'
fi
exit "$fail"
