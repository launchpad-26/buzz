# Plan: issue #647 — agents/documentation-validation.md

## ALREADY TRUE

- `launchpad/docs/corpus/agents/documentation-validation.md` does not exist yet,
  neither on `origin/launchpad` nor in this worktree (`git ls-tree -r --name-only
  origin/launchpad -- launchpad/docs/corpus` and a local `ls` both confirm).
- `launchpad/docs/corpus/templates/procedure.md` exists on `origin/launchpad`
  with `id: corpus-template-procedure`, `status: active` — a valid relationship
  target.
- `launchpad/docs/corpus/agents/invariants.md` exists on `origin/launchpad` with
  `id: agents-invariants`. Its `Enforcement` section explicitly splits I1-I10
  into mechanically-enforced (I4, I5, I6, I7's field-shape half, I8, I9) versus
  enforced-by-review-only (I1, I2, I3, I7's honesty half, I10) — the split this
  node's genuine incremental value sits on top of.
- `.claude/skills/corpus-review/SKILL.md` exists and already documents a
  four-category review procedure (structural validation quoted from
  `validate.py`; evidence/factual honesty; duplication/atomicity;
  security/public-boundary) — this covers most of the review-only half already.
  This node links to it rather than re-describing its content.
- `python3 launchpad/project-intelligence/corpus/validate.py` run from this
  worktree at commit `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90` exits 0:
  `PASS  corpus validation found no errors; 593 item(s) reported unverified`.
- `check-plan.sh` does not exist anywhere in this repository (confirmed in an
  earlier batch run) — proceeding without it.
- Issue #647's own Definition of Done is how-to-shaped (goal/prerequisites/
  scope, ordered executable steps, success verification/rollback, links
  authoritative commands) — matching `templates/procedure.md`'s Diátaxis
  How-to form, not `templates/reference.md`'s information-oriented lookup
  form. The content itself (run a command, interpret its output, escalate to
  a review procedure) is action-sequenced, not a catalogue of facts, which is
  the second reason `procedure.md` is the right template here.

## STEP 1 — Draft this plan (done, this file)

## STEP 2 — Author the node

Write `launchpad/docs/corpus/agents/documentation-validation.md` following
`templates/procedure.md`'s required sections (Overview; Before you start;
one numbered task sequence per logical goal; See also; Boundary; Relationships;
Scope and omissions).

- `id: agents-documentation-validation` (folder + filename-stem, matching the
  `agents-invariants` precedent already merged under this same directory —
  confirmed by grepping every merged node's `id:` against its path).
- `type: agent`, `status: draft`, `origin: launchpad`,
  `audiences: [agent, reviewer]`.
- Evidence: cite `validate.py`'s actual functions/messages (opened directly),
  `AGENTS.md`'s "Running the check" and "Three things a passing run does not
  mean" sections, `agents-invariants.md`'s Enforcement section, the
  `corpus-review` SKILL.md, the `Justfile` `corpus-validate` recipe, and the
  `.github/workflows/launchpad-corpus-validate.yml` trigger paths. Issue #647's
  own DoD as TEAM_KNOWLEDGE.
- Relationships (checked against `origin/launchpad`, not this worktree):
  `depends-on: corpus-agents`, `references: agents-invariants`,
  `implements: corpus-template-procedure`. All three resolve today.
- Body: two numbered task sequences — (1) run `validate.py` and interpret its
  PASS/FAIL and per-node output; (2) invoke the `corpus-review` skill for the
  review-only invariants nothing mechanical checks. Boundary section states
  explicitly, by title only, that this node is the shared final gate for both
  `#645` (creation) and `#646` (update) — not a third parallel lifecycle stage.

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
worktree root. Fix any schema/citation/relationship error until it exits 0.

**Done-when:** exit code 0, no new `FAIL` lines beyond the pre-existing
UNVERIFIED notices for other nodes.

## STEP 4 — Earn the commit gate

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
Confirm `OK`. Then, in a separate call, `git commit -s`.

**Done-when:** unittest reports `OK`; commit succeeds without `--no-verify`.

## STEP 5 — Review and report

Run `Skill(review-code)` or the `serina:review-code` subagent against the
diff. If unreachable, self-review line-by-line against issue #647's DoD and
re-run `validate.py` after any fix. Report issue number, worktree path,
branch, commit SHA, template used and why, review method, and any BLOCKED
item.

## GATES

- `validate.py` exits 0.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`.
- Review pass (tool-based or documented self-review) with no unresolved
  findings.

## BUDGET

One new corpus node file, one plan file. No other files touched.

## OPEN

- Whether to also invoke the `corpus-review` skill against this very node as
  part of building it: left to the master build loop's own step 6 (which
  specifies `review-code`/self-review), not duplicated here — this node
  documents how corpus-review is invoked as a procedure step, it does not
  require running it against itself to validate the documentation is correct.

## LEFT OUT

- A full reference-shaped catalogue of every `validate.py` error message —
  would drift into `templates/reference.md`'s information-oriented territory
  for content that is actually action-sequenced (run, interpret, escalate,
  re-run); a short table inside the interpretation step, each row cited to
  `validate.py`, is enough per Diátaxis's own "a how-to guide... can include
  a description of how something works" nuance without becoming a second,
  duplicate node.
- Resolving `#1321` (whether a recorded revision may stay put across a partial
  re-verification) — unsettled corpus-wide, out of scope for this node.
- Any edge toward `#645`/`#646` — neither is merged yet; named by title only in
  the Boundary section per the batch brief.
