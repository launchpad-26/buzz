# Issue #1007 — interfaces/nostr/nip-05.md

Stated size: not given a Size line in the issue body -> cap: 5 steps (per task brief).

ALREADY TRUE: `launchpad/docs/corpus/interfaces/nostr/nip-05.md` does not exist anywhere in this
worktree or on `origin/launchpad` (confirmed: `find launchpad/docs/corpus/interfaces` returns
nothing at all — the `interfaces/` subtree itself doesn't exist yet). `launchpad/docs/corpus/schema/node.schema.json`,
`launchpad/docs/corpus/AGENTS.md` and `launchpad/docs/corpus/templates/interface.md` (id
`corpus-template-interface`, type `governance`) are merged on `origin/launchpad`. The relay's
NIP-05 implementation is real code, not a stub: `crates/buzz-relay/src/api/nip05.rs` (the
`GET /.well-known/nostr.json` handler, `canonicalize_nip05`, `extract_domain`,
`relay_url_for_tenant_host`, with unit tests), wired into the route table at
`crates/buzz-relay/src/router.rs:66`, fed by the kind:0 profile side effect at
`crates/buzz-relay/src/handlers/side_effects.rs::handle_kind0_profile` (lines 1271-1360) and
`crates/buzz-db/src/store/user.rs::get_user_by_nip05` (lines 171-208), backed by the
`nip05_handle` column and its partial unique index in `schema/schema.sql:170,191-192`, and
covered by `crates/buzz-test-client/tests/e2e_relay.rs::test_kind0_nip05_sync` (lines 1067-1215)
and `crates/buzz-test-client/tests/conformance_multitenant.rs::users_profiles_nip05::same_nip05_local_part_on_two_hosts_is_independent`
(module starts line 917, test at line 1151). No sibling `interfaces/nostr/*` or event-kind node
for kind:0 exists yet on `origin/launchpad`, so no `relationships` edge besides the merged
template itself resolves.

STEP 1  [independent] Confirm the evidence set is complete and pinned to a commit: re-check that
every source file above still exists at HEAD (`650354eab8d41ab6ce1a71de079a6c6d95c69052`) and that
`crates/buzz-relay/src/nip11.rs::SUPPORTED_NIPS` (line 14) does not list `5`, which is a real,
citable fact about how NIP-05 is advertised (or rather, not advertised in the NIP-11 document)
that belongs in the node rather than being silently dropped. ← RUNS HERE
done when: every file path and line range above has been read in this session and matches what
is written here.

STEP 2  [needs 1] Write `launchpad/docs/corpus/interfaces/nostr/nip-05.md` with schema-valid
front matter (`id: interfaces-nostr-nip-05`, `type: interfaces-events`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, reviewer]`, `evidence` citing only the files
read in STEP 1, `relationships: [{type: implements, target: corpus-template-interface}]` since
that id is confirmed merged) and a body following the interface template's required sections
(Interface description, Operations table, Contract and stability, Boundary, Relationships, Scope
and omissions) plus the issue's own Definition-of-done bullets: inputs/messages (kind:0 `nip05`
field, GET query param), outputs/responses (the `{names, relays}` JSON shape), error/rejection
behavior (invalid/off-domain handles silently cleared, never rejecting the kind:0 event itself),
auth (none — public discovery endpoint, explicitly host-scoped per community), versioning (NIP-05
is a stable upstream spec; Buzz's own extension is the per-tenant host-domain binding),
ordering/idempotency (kind:0 is a NIP-01 replaceable event — latest wins), a link to the
authoritative spec (upstream NIP-05 itself, prose-linked since no NIP-05 corpus node other than
this one exists), and one valid + one failure example drawn from
`test_kind0_nip05_sync`. done when: the file exists at that exact path with all seven bullets of
the issue's DoD checklist addressed in its body.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix any FAIL
line not caused by pre-existing content and re-run until it exits 0 (UNVERIFIED notices are
acceptable). done when: the command's exit code is 0 and its output contains no `FAIL` line
attributable to the new node.

STEP 4  [needs 3] Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in its own call to earn the commit gate stamp, confirm it prints `OK`, then
in a separate call `git add` the plan and the new document and
`git commit -s -m "docs(corpus): document NIP-05 interface (#1007)"`. done when: the unittest run
prints `OK` and `git rev-parse HEAD` afterward names a new commit containing exactly the plan and
the one corpus document.

PARALLEL: none — one document, one task, no independent workstream.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before commit.
The commit-gate stamp from the unittest discovery run in STEP 4 must be earned, not bypassed with
`--no-verify`. `review-adjudicate` and the cross-model final review pass are deferred to the
batch owner's later review — not run in this task.

BUDGET: small — one new markdown file (~150-250 lines), one plan file, no code changes. Evidence
gathering is scoped to the ~7 files enumerated in ALREADY TRUE plus the interface template
already read while planning; no new source exploration is expected during STEP 2.

OPEN: Whether `implements: corpus-template-interface` or omitting `relationships` entirely is the
right call is left to reviewer judgment — the template itself frames this edge as optional
("may declare implements ... if the author wants the generated implemented-by edge"), and this
plan chooses to declare it since the target is confirmed merged and the edge is schema-legal, but
a reviewer may prefer to omit it since the node's own shape already shows which template it
followed. Whether NIP-05's absence from `SUPPORTED_NIPS` belongs in "Contract and stability" or
in "Scope and omissions -> expected but not verified" is left to the author's judgment when
drafting STEP 2, not decided here.

LEFT OUT: No event-kind node for kind:0 (NIP-01 profile metadata) is created or referenced by
`relationships` — none exists yet on `origin/launchpad`, so it is prose-mentioned by filename
only, per the task brief's instruction that unmerged sibling nodes don't resolve. No NIP-11
interface node is created here either, even though `nip11.rs` is closely related — that is a
separate task's scope, not folded into this one. No change to relay runtime behavior, the
`nip05_handle` schema, or `SUPPORTED_NIPS` — this task documents current behavior, it does not
alter it.
