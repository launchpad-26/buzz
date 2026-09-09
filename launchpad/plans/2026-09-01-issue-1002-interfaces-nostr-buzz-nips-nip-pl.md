# Plan: issue #1002 — corpus node `interfaces-nostr-buzz-nips-nip-pl`

Issue #1002 — task: document interfaces/nostr/buzz-nips/nip-pl.md
Stated size: none given — the corpus-doc task template has no Size field  ->  cap: 5 steps

ALREADY TRUE (verified against git and the worktree, not notes)

`launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-pl.md` does not exist —
`find launchpad/docs/corpus/interfaces` returns nothing at all; no `interfaces/`
subtree exists yet under `launchpad/docs/corpus/`. The authoritative spec is at
`docs/nips/NIP-PL.md` (confirmed present, read in full: 453 lines, `kind:30350`
push lease). `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum has
no `interface` value; the correct value for an interface-shaped node is the
single combined `interfaces-events` token (confirmed both in the enum itself
and in `launchpad/docs/corpus/templates/interface.md`'s own "A note on `type`"
section, which states a template-instance node built from it carries
`type: interfaces-events`).

Two corpus nodes already merged on `origin/launchpad` (this worktree's base)
document adjacent NIP-PL subject matter without being this interface node:
`architecture-flows-push-notification` (`launchpad/docs/corpus/architecture/flows/push-notification.md`,
`type: architecture`) documents the wake/reconnect flow, and
`architecture-containers-push-gateway` (`launchpad/docs/corpus/architecture/containers/push-gateway.md`,
`type: architecture`) documents the `buzz-push-gateway` container. Neither is
an `interfaces-events` node describing the `kind:30350` interface itself and
its acceptance/REQ/COUNT contract, so this is a new, non-duplicate node — and
both are valid `references`/`part-of` targets since they already resolve in
`origin/launchpad`.

Implementation confirmed by direct read, not restated from the spec alone:
`crates/buzz-core/src/kind.rs:109` declares `KIND_PUSH_LEASE = 30350` and lists
it in `AUTHOR_ONLY_KINDS` (line 129-133). `crates/buzz-relay/src/handlers/push_lease.rs`
(747 lines) implements `validate_envelope` (tag rules, expiration bounds),
`parse_plaintext`/`validate_plaintext` (schema/size bounds), and `accept()`
(lines 464-565, the full acceptance sequence: push-enabled check, envelope
validation, executor-key check, NIP-44 decrypt, plaintext validation, atomic
persist via `state.db.accept_push_lease_event`). `crates/buzz-relay/src/handlers/ingest.rs:2918-2944`
calls `accept()` and maps its `AcceptLeaseOutcome` variants to
`invalid: stale replacement` / `invalid: stale generation` /
`invalid: endpoint already leased` / `invalid: lease quota exceeded` /
`invalid: source event collision` rejection strings — matching the spec's
Acceptance-and-Origin-Binding step 8. `crates/buzz-relay/src/handlers/req.rs`'s
test `push_lease_requires_self_author_filter_and_count_fallback` (line 2111)
and helper `author_only_filters_authorized` confirm REQ/COUNT author-only
enforcement for `kind:30350` in code, not only in the spec prose.
`crates/buzz-push-gateway/src/http.rs:791-800` registers exactly the seven
`POST` routes the spec's Public APNs Gateway Profile section names.

STEP 1 [independent] — Write the front matter and body of
`launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-pl.md`: `id: interfaces-nostr-buzz-nips-nip-pl`,
`type: interfaces-events`, `status: draft`, `origin: launchpad`,
`audiences: [agent, developer, reviewer]`. Evidence ledger cites the revision
commit, `docs/nips/NIP-PL.md` (FACT, spec text), `crates/buzz-core/src/kind.rs:104-133`,
`crates/buzz-relay/src/handlers/push_lease.rs` (envelope/plaintext/acceptance,
several line-ranges), `crates/buzz-relay/src/handlers/ingest.rs:2918-2944`
(outcome-to-rejection mapping), `crates/buzz-relay/src/handlers/req.rs` (REQ/COUNT
author-only test), `crates/buzz-push-gateway/src/http.rs:780-800` (route table).
Body follows `templates/interface.md`'s required sections: Interface
description, Operations (event write via `POST /events`/WebSocket, REQ/COUNT
reads, plus the seven gateway HTTP routes — each row pointing at its code
symbol or NIP-PL section, not restating it), Contract and stability (versioning
via `generation`/NIP-40 `expiration`, ordering via the two-ordering acceptance
check, idempotency via addressable-event replacement, auth via NIP-42 +
author-only ACL), Boundary (not a single event kind's full tag-shape catalogue
beyond what's needed to describe the interface; not a domain-expert parameter
reference for every gateway field), a valid-lease acceptance example and a
failure example (e.g. `invalid: stale generation`) drawn from the spec's own
worked JSON and the ingest.rs rejection strings, Relationships (`references`
toward `architecture-flows-push-notification` and
`architecture-containers-push-gateway`, both confirmed resolvable above), and
Scope and omissions (naming NIP-46 remote-signer interaction, FCM/UnifiedPush
non-conformance, and the gateway's App Attest transcript details as owned
elsewhere per the spec's own Non-Goals, rather than restating them).
done when: the file exists at that path with schema-required front-matter
fields present and every operation/contract claim in the body backed by an
`evidence` entry citing a source actually opened in ALREADY TRUE above.

STEP 2 [needs 1] — Run `python3 launchpad/project-intelligence/corpus/validate.py` from
the repo root and fix any FAIL line it reports (UNVERIFIED notices are
acceptable; FAIL is not) until it exits 0. done when: the command exits 0 and
its output contains no `FAIL` line attributable to the new node.

STEP 3 [needs 2] — Self-review the diff against issue #1002's Definition-of-done
checklist line by line (one hand-authored doc only; schema-valid front matter;
one independently maintainable node; FACT/INFERENCE/TEAM_KNOWLEDGE not
conflated; links implementation/verification/spec/neighbor nodes without
duplicating their content; checked against the recorded revision; validate.py
clean; inputs/outputs/errors defined; auth/versioning/ordering defined; spec
link present; one valid + one failure example present). done when: every
checklist bullet is confirmed against the actual file content, not assumed.

STEP 4 [needs 3] — Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in its own tool call and confirm it prints `OK`, earning
the commit gate. done when: the command's output contains `OK` and no
`FAILED`/`ERROR` line.

STEP 5 [needs 4] — RUNS HERE. Stage exactly the new node and this plan file
and commit with `git commit -s -m "docs(corpus): document Buzz NIP-PL interface (#1002)"`.
done when: `git log -1 --format=%H` names a new commit whose
`git show --stat` touches only the two intended paths, and `git log -1` shows
a `Signed-off-by` trailer.

PARALLEL: none — one file, one worktree, no fan-out; every step depends on the
previous one's output (the doc must exist before it can validate, validate
before commit-gate tests run, tests before commit).

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
before commit (STEP 2). `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print `OK`,
run alone in its own tool call, to earn the commit verification stamp (STEP 4).
Adjudication and any cross-model review pass are explicitly deferred to the
batch owner's later review — not run in this session.

BUDGET: one new corpus file, one plan file, one commit. No code changes, no
generated-index regeneration expected (none exist yet under this corpus tree to
regenerate).

OPEN: whether `references` is the correct relationship type (versus `part-of`)
for pointing at `architecture-flows-push-notification` and
`architecture-containers-push-gateway` is a judgment call this plan makes
(`references`' directionality — "source cites target as supporting context; no
ownership or currency dependency implied" — fits an interface node pointing at
adjacent architecture documentation better than `part-of`'s constituent-piece
framing) rather than a settled corpus-wide rule; a reviewer may reasonably
prefer the other type. The exact wording of the failure-example rejection
string to feature (the plan names `invalid: stale generation` as one candidate
among the five `ingest.rs` outcome variants) is left to STEP 1's drafting, not
fixed here.

LEFT OUT: no `event-kind` (#1337-template-shaped) node describing `kind:30350`'s
tag shape field-by-field — this node references the kind constant and cites
`kind.rs`/`push_lease.rs` rather than duplicating a full tag-by-tag catalogue,
per `templates/interface.md`'s own Boundary section. No new `references` edge
back from `push-notification.md`/`push-gateway.md` to this new node — editing
already-merged sibling nodes is out of scope for this task, which only creates
one new file. No change to `docs/nips/NIP-PL.md`, any crate, or any other
corpus node — this task documents the existing interface, it does not modify
it. No FCM/UnifiedPush profile detail beyond noting they are non-conforming in
v1, per the spec's own Transport Profiles section.
