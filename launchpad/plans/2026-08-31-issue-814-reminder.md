# Plan: issue #814 — document capabilities/reminders/reminder.md

## ALREADY TRUE

- No `launchpad/docs/corpus/capabilities/` directory exists yet on this branch
  (origin/launchpad) — this will be the first capability-typed corpus node.
- `launchpad/docs/corpus/templates/capability.md` (id `corpus-template-capability`)
  defines the required body shape: Capability statement, Maturity, Boundary,
  Relationships, Scope and omissions.
- The reminders capability is a real, shipped, end-to-end feature: NIP-ER
  (`docs/nips/NIP-ER.md`), relay kind `KIND_EVENT_REMINDER` = 30300
  (`crates/buzz-core/src/kind.rs:102`), relay storage/scheduler
  (`crates/buzz-db/src/store/reminder.rs`, `crates/buzz-relay/src/main.rs:769-850`),
  desktop UI (`desktop/src/features/reminders/**`), mobile UI
  (`mobile/lib/shared/reminders/**`), and e2e coverage
  (`crates/buzz-test-client/tests/e2e_event_reminder.rs`,
  `desktop/tests/e2e/reminders.spec.ts`).
- Sibling issue #813 (reminder-lifecycle, a `flow`-typed node) is not merged, so no
  `relationships` edge may target it — its id does not exist in the merged corpus.
- No corpus node currently exists for any architecture/interface node reminders
  would `references`, at the recorded revision on `origin/launchpad`.

## STEP 1 — Confirm target path is free and gather evidence

Confirm `launchpad/docs/corpus/capabilities/reminders/reminder.md` does not exist.
Re-read `docs/nips/NIP-ER.md`, `crates/buzz-core/src/kind.rs`,
`crates/buzz-db/src/store/reminder.rs`, `crates/buzz-relay/src/main.rs` (scheduler),
desktop/mobile reminder feature entry points, and `CHANGELOG.md` reminder entries
for maturity evidence. **Done when**: file confirmed absent; each claim to be made
has an opened, cited source.

## STEP 2 — Draft the node

Write front matter (`id: capabilities-reminders-reminder`, `type: capabilities`,
`status: draft`, `origin: launchpad`, `audiences`, `evidence`, no `relationships`)
and body (Capability statement / Maturity / Boundary / Relationships / Scope and
omissions) per the template. **Done when**: file written, every DoD bullet in #814
addressed.

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` and confirm zero
new FAIL entries beyond the known 21 pre-existing baseline (issue #1951). **Done
when**: exit code and output confirm no new errors from this node.

## STEP 4 — Earn commit gate and commit

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` as the sole command in its own call; confirm `OK`. Then commit the new
file plus this plan with `git commit -s`. **Done when**: commit exists, no push, no
PR.

## STEP 5 — Self-review

Re-read the diff against #814's DoD line by line; re-open every cited source; confirm
no second canonical document was created; confirm zero new validate.py FAIL entries.

## GATES

- `validate.py` exits 0 with zero new FAIL entries.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
  "test_*.py"` prints `OK`.

## BUDGET

Single node, single commit. No code changes, no runtime behavior changes.

## OPEN

- Whether a future architecture/interface corpus node should later gain a
  `references` edge from this capability node — none exists yet to target.
- `KIND_STREAM_REMINDER` (40007) — a distinct, less-implemented "needs action" feed
  kind — is named as an explicit boundary item, not folded into this node's
  Capability statement.

## LEFT OUT

- Documenting the reminder lifecycle flow step-by-step (creation → snooze → done/
  cancel → delivery race handling) — that is issue #813's own node, not duplicated
  here.
- Any architecture/component/container-level description of how the relay
  scheduler or desktop/mobile clients are built — out of this template's scope per
  `corpus-template-capability`'s Boundary section.
