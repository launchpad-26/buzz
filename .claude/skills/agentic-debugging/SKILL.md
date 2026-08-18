---
name: agentic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing or making any code change — enforces an evidence-first investigation loop over speculative edit-test cycles.
version: 1
---

# Agentic Debugging

## Core Principle

Resolve bugs by establishing the cause before modifying code. Never guess when evidence can be gathered. If you catch yourself editing before you can state the cause, stop and go back to evidence.

## The Loop

Advance one stage at a time. Do not skip a stage. Do not advance until its exit criterion is met.

| Stage | Exit criterion |
|---|---|
| Reproduce | You can reliably trigger the failure |
| Gather evidence | You have logs, stack trace, diffs, or test output in hand |
| Localize | You know the relevant function/module/code path |
| Form a hypothesis | The hypothesis is falsifiable |
| Test the hypothesis | Evidence supports or rejects it |
| Implement the fix | Smallest principled change addressing the root cause |
| Add/adjust regression coverage | Coverage matches the bug type (see table below) |
| Verify | The original failure no longer occurs |
| Review the diff | Every changed line contributes to the fix, and final review was done by the other vendor (see Cross-Vendor Final Review) |

If a stage's exit criterion isn't met, do not proceed — do more of that stage, or step back to the one before it.

## Observation / Hypothesis / Test / Result / Conclusion

For every hypothesis you form, write it out in this exact shape before touching code. This separates what you observed from what you're guessing from what you confirmed.

```
Observation: The API returns 500 when `user_id` is omitted.
Hypothesis: Request validation is happening after the database lookup.
Test: Inspect the request handler and add a focused test for the missing-ID path.
Result: Validation occurs after `get_user(user_id)`.
Conclusion: The bug is an ordering error in request validation.
```

Only move to a fix once you have a Conclusion backed by a Result — not a Hypothesis alone.

## Search-Space Minimization

Start narrow, widen only when evidence says to:

1. Start from the stack trace / error message.
2. Inspect the immediate caller and callee of the failing line.
3. Check `git diff`, recent commits, and `git blame` on the failing code.
4. Search the codebase for the exact error string or symbol name.
5. Check config/environment only once evidence points there (env-specific failure, works-on-my-machine, CI-only).
6. Use a targeted test or minimal reproduction before running the full suite.

Do not read the whole repo. Stop widening the search once you have enough evidence to write a falsifiable hypothesis — go test it instead of gathering more.

## Regression Coverage by Bug Type

The right coverage depends on what kind of bug it was — don't default to "add a test" for everything.

| Bug type | Coverage to add |
|---|---|
| Behavioral bug | Regression test reproducing the original failure |
| Config/environment issue | Documented reproduce/verification procedure, not necessarily a test |
| Race/concurrency bug | Deterministic test if possible; otherwise a stress/load test that reliably surfaces it |
| Performance regression | Benchmark or profile evidence showing the metric before/after |
| One-off infrastructure failure (flaky runner, network blip) | Document the diagnosis. Do not invent a code change to "fix" it |

## Tool Selection

Pick the action based on the question you're actually asking, not habit.

| Question | Action |
|---|---|
| What exactly failed? | Read the error/stack trace |
| When did it start? | `git log`, `git blame`, diff against last-known-good |
| Where does this value originate? | Code search + trace the call chain |
| Is this code path broken? | Write a focused test or minimal reproduction |
| Is this environment-specific? | Compare configuration/runtime between environments |
| Is this concurrent? | Inspect synchronization primitives, reproduce under load |
| Did my fix actually work? | Run the regression test AND the original reproduction |

## Escalation Rules

- **After two failed hypotheses**, stop making speculative changes. Re-examine the evidence from the start, broaden the investigation, and name explicitly what assumption you think is wrong.
- **If the failure cannot be reproduced**, do not fabricate a fix. Gather more evidence — logs, CI artifacts, environment info, historical changes — and report your uncertainty instead of shipping a guess.

## Never

- Never guess when evidence can be gathered.
- Don't change code before understanding the failure — except the minimum needed to create a reproduction.
- Don't make multiple unrelated changes during diagnosis.
- Don't weaken a test to make it pass.
- Don't disable a failing test to get green.
- Don't add broad exception handling to hide an error.
- Don't add retries or timeouts without first establishing transient failure as the cause.
- Don't rewrite large portions of code before localizing the problem.
- Don't claim a bug is fixed without verifying the original failure is gone.
- Don't declare success because compilation passes.
- Don't assume the first plausible explanation is correct — test it.

## Reversibility Check

Before finishing, review your final diff line by line. For every changed line, confirm it contributes to fixing the diagnosed root cause. Remove anything that doesn't — including drive-by cleanups, unrelated renames, or "while I'm here" changes.

## Cross-Vendor Final Review

The agent that wrote the fix does not give it final sign-off. Route final review to the other vendor:

- Claude wrote the fix → Codex reviews it.
- Codex wrote the fix → Claude reviews it.

This is not optional and not satisfied by the author re-reading their own diff — that's the Reversibility Check above, and it's a different step. Route the diagnosis (Observation/Hypothesis/Test/Result/Conclusion), the diff, and the regression coverage to the other vendor and get an explicit verdict before marking the task complete. If the tooling can't reach the other vendor, stop and say so rather than skipping the review or self-approving.

If you dispatch the review as a background or async process, block on it. Wait for the process to actually finish and read its real output. Do not end your turn, write your final report, or say the task is done while the review is still in flight — "I've requested a review" or "I'll report back once it lands" is not a verdict and does not satisfy this step. The only thing that satisfies it is the other vendor's actual completed verdict, quoted or summarized from its real output.

Give it two honest attempts. If the tooling still hasn't produced a real verdict after two tries, stop retrying — report exactly what you tried and what happened (empty output, error, timeout) as part of your final report, and say plainly that final review is outstanding. Don't burn the rest of the task budget iterating on invocation flags to force a broken tool to respond.

## Completion Criteria

A debugging task is complete only when all of the following hold:

- [ ] The failure was reproduced, or is sufficiently evidenced without reproduction
- [ ] The root cause is identified, not just a symptom
- [ ] The fix addresses that root cause
- [ ] Regression coverage exists, matching the bug type
- [ ] The original failure no longer occurs
- [ ] Relevant existing tests still pass
- [ ] The final diff contains no unrelated changes
- [ ] Final review was performed by the other vendor (Claude-authored → Codex review; Codex-authored → Claude review)
