#!/usr/bin/env bash
# Write or check the branch's merge verdict — pinned to a commit, never to a mood.
#
# WHY THIS IS A SCRIPT AND NOT A SENTENCE
#
# review-final ends by reporting readiness. Until now that report was prose in a
# transcript: nothing downstream could read it, and nothing stopped a merge that
# ignored it. On 2026-08-03 a PR was merged from the browser while its final
# review was still running. No amount of prose would have changed that.
#
# So the verdict becomes a file, and the file has three properties that prose
# cannot have:
#
#   1. PINNED TO A SHA. A verdict for commit A does not clear commit B. Without
#      this you review once and push anything afterwards.
#   2. THREE STATES, NOT TWO. READY / NOT_READY / and the absence of a file at
#      all. Absence must block. A review that dies from turn exhaustion writes
#      nothing, and nothing must never read as approval.
#   3. MECHANICALLY REFUSABLE. `record ready` runs the objective checks itself
#      and REFUSES to write READY when they fail. A reviewer cannot assert past
#      a failing test suite or an incomplete ledger, because the script re-runs
#      both rather than believing a claim about them.
#
# What the script does NOT do is decide whether the findings are blocking. That
# is judgement and stays with a reader. The script records the judgement it was
# given; it does not invent one. Pretending otherwise would give false comfort,
# which is the failure mode this whole gate exists to remove.
#
# Usage:
#   verdict.sh record ready    PLAN_FILE   # runs the checks; writes READY only if they pass
#   verdict.sh record notready REASON      # always allowed; blocking is never gated
#   verdict.sh check                       # exit 0 only if a READY verdict matches HEAD
#   verdict.sh show
#
# Exit: 0 = the action succeeded / the gate is open. 1 = anything else.

set -uo pipefail

root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$root" ]]; then
  echo "FAIL  not inside a git repository" >&2
  exit 1
fi
file="$root/.superpowers/verdict.json"
head_sha="$(git -C "$root" rev-parse HEAD 2>/dev/null || true)"

die() { printf 'FAIL  %s\n' "$1" >&2; exit 1; }

# WRITE THE VERDICT WITH A JSON ENCODER, NEVER BY INTERPOLATING SHELL TEXT.
#
# The file used to be built by heredoc, dropping `$reason`, `$plan` and the test
# command straight between quotes. Two consequences, both measured 2026-08-06.
#
# The ordinary one is an unreadable file. `VERDICT_TEST_CMD='true --grep "focus"'`
# writes `"test_cmd": "passed: true --grep "focus""`, and the script announces
# READY while `verdict.sh check` then reports the verdict unreadable. Annoying, and
# it fails CLOSED.
#
# The one that matters does NOT fail closed. A reason containing a quote can add a
# second `state` key:
#
#   record notready 'suite is red", "state": "READY", "note": "x'
#
# That is VALID json with a duplicate key, Python's parser takes the last, and a
# NOT_READY verdict OPENED the gate. It breaks the property this file states about
# itself in its own header — "THREE STATES, NOT TWO... nothing must never read as
# approval" — because a blocking verdict silently became an approving one.
#
# It needs a hand-crafted string, so it is not something a reviewer types by
# accident. It is also exactly what a reviewer under pressure to unblock a merge
# might discover, and the gate must not be defeatable by the person it constrains.
#
# json.dumps escapes every value, and the document is parsed back before anything
# is announced: a file this script cannot read is a file it must not claim to have
# written.
write_verdict() {
  python3 - "$file" "$@" <<'PY' || die "could not write the verdict file"
import json, sys
path, pairs = sys.argv[1], sys.argv[2:]
doc = {}
for i in range(0, len(pairs), 2):
    key, val = pairs[i], pairs[i + 1]
    if key.startswith("checks."):
        doc.setdefault("checks", {})[key.split(".", 1)[1]] = val
    elif val == "@@NULL@@":
        # Sentinel for a genuine JSON null. A plain string cannot express one, and
        # `plan: null` is load-bearing: it is how a reader tells issue-driven work
        # from plan-driven. An earlier attempt used "\\0null", which bash passes as
        # four literal characters rather than a NUL byte, so the field silently
        # became the string "\\0null" instead of null. Any sentinel must be one
        # bash will not transform.
        doc[key] = None
    else:
        doc[key] = val
text = json.dumps(doc, indent=2) + "\n"
json.loads(text)          # refuse to write what cannot be read back
open(path, "w").write(text)
PY
}

# THE TEST GATE, SHARED BY BOTH `record ready` PATHS.
#
# It used to be inline in the plan path only, and the `--issue` path returned
# before reaching it. Measured 2026-08-06 with VERDICT_TEST_CMD='false':
#
#   record ready plan.md    -> FAIL  Not writing READY over a failing suite
#   record ready --issue 99 -> READY recorded, and `verdict.sh check` opened
#
# So the escape hatch built for "issue-driven work has no ledger" also skipped the
# test suite, which has nothing to do with whether a plan exists. Extracted into a
# function so neither path can drift from the other again.
#
# It also sets test_cmd_result, because the recorded field was ambiguous: the plan
# path wrote the command string AFTER running it, and the issue path wrote the same
# string WITHOUT running it, so a reader could not tell "ran and passed" from
# "never ran". The value now says which happened.

test_cmd_result='not-run'
run_test_gate() {
  if [[ -n "${VERDICT_TEST_CMD:-}" ]]; then
    if ! eval "$VERDICT_TEST_CMD" >/dev/null 2>&1; then
      die "VERDICT_TEST_CMD failed: ${VERDICT_TEST_CMD}. Not writing READY over a failing suite."
    fi
    echo "  ok  test command passed: ${VERDICT_TEST_CMD}"
    test_cmd_result="passed: ${VERDICT_TEST_CMD}"
  else
    echo "  --  no VERDICT_TEST_CMD set; test suite NOT verified by this script"
    test_cmd_result='not-run: no VERDICT_TEST_CMD was set'
  fi
}

case "${1:-}" in

record)
  case "${2:-}" in
  ready)
    plan="${3:-}"
    [[ -n "$plan" ]] || die "record ready needs a plan file, or --issue N for issue-driven work"

    # ISSUE-DRIVEN WORK HAS NO PLAN, AND DEMANDING ONE TEACHES PEOPLE TO ROUTE
    # AROUND THE GATE.
    #
    # `check-ledger.sh` asks whether every task in an SDD plan was reviewed. A
    # one-file fix driven by a GitHub issue has no plan and no tasks, so that
    # question has no answer — and refusing to record a verdict because an
    # inapplicable check cannot run leaves hand-writing the file as the only
    # route. That is exactly how verify-gate.sh's escape hatch became its normal
    # path.
    #
    # So the ledger check is SKIPPED, not faked, and the verdict says which
    # applied. The provenance lives in the file rather than in a comment nobody
    # reads, and `--issue` is not a way to dodge the ledger on plan-driven work:
    # it records a different claim, and a reader can tell them apart.
    if [[ "$plan" == "--issue" ]]; then
      issue="${4:-}"
      [[ -n "$issue" ]] || die "--issue needs a number: verdict.sh record ready --issue 9"

      # The ledger is genuinely inapplicable here. The test suite is not, so it
      # runs before anything is written. This call is the whole fix.
      run_test_gate

      mkdir -p "$(dirname "$file")"
      write_verdict state READY sha "$head_sha" issue "$issue" plan "@@NULL@@" \
        recorded_at "$(date -Iseconds)" \
        checks.ledger "not-applicable: issue-driven, no SDD plan exists for this branch" \
        checks.test_cmd "$test_cmd_result"
      echo "READY recorded for $head_sha (issue #$issue, no plan — ledger check not applicable)"
      exit 0
    fi

    [[ -r "$plan" ]] || die "plan not readable: $plan"

    # ---- the objective checks. A reviewer cannot assert past these. ----
    here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [[ -x "$here/check-ledger.sh" ]]; then
      if ! "$here/check-ledger.sh" "$plan" >/dev/null 2>&1; then
        echo "REFUSED  the ledger does not account for every task. Run:" >&2
        echo "         $here/check-ledger.sh $plan" >&2
        die "not writing READY while a task is ungated"
      fi
      echo "  ok  ledger accounts for every task"
    else
      # Never silently skip a gate. A missing checker is a broken install, not a pass.
      die "check-ledger.sh missing next to verdict.sh — refusing to write READY without running it"
    fi

    run_test_gate

    mkdir -p "$(dirname "$file")"
    write_verdict state READY sha "$head_sha" plan "$(basename "$plan")" \
      recorded_at "$(date -Iseconds)" \
      checks.ledger pass checks.test_cmd "$test_cmd_result"
    echo "READY recorded for $head_sha"
    ;;

  notready)
    reason="${3:-no reason given}"
    mkdir -p "$(dirname "$file")"
    write_verdict state NOT_READY sha "$head_sha" reason "$reason" \
      recorded_at "$(date -Iseconds)"
    echo "NOT_READY recorded for $head_sha: $reason"
    ;;

  *) die "record needs 'ready' or 'notready'" ;;
  esac
  ;;

check)
  # The gate. Absence, staleness and NOT_READY are all closed.
  [[ -r "$file" ]] && [[ -n "$head_sha" ]] || {
    echo "BLOCKED  no verdict at .superpowers/verdict.json — this branch has not been reviewed." >&2
    exit 1
  }
  python3 - "$file" "$head_sha" <<'PY'
import json, sys
try:
    v = json.load(open(sys.argv[1]))
except Exception as exc:
    print(f"BLOCKED  verdict file is unreadable ({exc}) — treating as no verdict.", file=sys.stderr)
    sys.exit(1)
state, sha, want = v.get("state"), v.get("sha"), sys.argv[2]
if state != "READY":
    print(f"BLOCKED  verdict state is {state!r}"
          + (f": {v.get('reason')}" if v.get("reason") else ""), file=sys.stderr)
    sys.exit(1)
if sha != want:
    # Recording the verdict and committing it CHANGES HEAD, so an exact match
    # can never be satisfied by anyone. The head may differ only if the sole
    # change since the reviewed commit is the verdict file itself.
    import subprocess
    d = subprocess.run(["git", "diff", "--name-only", f"{sha}..{want}"],
                       capture_output=True, text=True)
    if d.returncode != 0:
        print(f"BLOCKED  verdict names {str(sha)[:8]}, not reachable from HEAD "
              f"{want[:8]}.", file=sys.stderr)
        sys.exit(1)
    files = [f for f in d.stdout.split("\n") if f.strip()]
    if files != [".superpowers/verdict.json"]:
        print(f"BLOCKED  verdict is for {str(sha)[:8]} but HEAD is {want[:8]}, and "
              f"{len(files)} other file(s) changed since. Re-review, then re-record.",
              file=sys.stderr)
        sys.exit(1)
    print(f"OPEN  verdict is for {str(sha)[:8]}; only the verdict file changed since")
else:
    print(f"OPEN  READY verdict matches HEAD {want[:8]}")
PY
  ;;

show)
  [[ -r "$file" ]] && cat "$file" || echo "no verdict at $file"
  ;;

*)
  die "usage: verdict.sh {record ready PLAN|record notready REASON|check|show}"
  ;;
esac
