# Plan: issue #874 — corpus node for event kind 39000 (channel metadata)

Issue https://github.com/launchpad-26/buzz/issues/874
Stated size: not stated in the issue body (no "Size:" line) -> cap: 5 steps (set by the dispatch instruction: "this is a small single-document task")

ALREADY TRUE

- Worktree `__worktrees/task-874-events-kinds-kind-39000-channel-metadata` exists, checked out from `origin/launchpad` at commit `a8b5021efb92264e724366d08b47b2a3839eb90a`, on branch `task/874-events-kinds-kind-39000-channel-metadata`. Verified with `git rev-parse HEAD`.
- The target file `launchpad/docs/corpus/events/kinds/kind-39000-channel-metadata.md` does **not** exist. Verified with `test -f` (reported NOTEXISTS) and a full `find launchpad/docs/corpus -name '*.md'` listing that contains no `events/` subtree at all.
- `launchpad/docs/corpus/templates/event-kind.md` (id `corpus-template-event-kind`) is merged on `origin/launchpad` at this revision and is the sanctioned template for an event-kind node: 9 required sections (title/kind identity, referenced NIP, kind range/classification, tag shape, content semantics, access control/storage, worked example, versioning, relationships).
- `launchpad/docs/corpus/schema/node.schema.json` requires `id, type, status, origin, audiences, evidence`; `type` is a closed 13-value enum including `interfaces-events`, which the template names as the value a real event-kind instance "most plausibly" takes.
- `crates/buzz-core/src/kind.rs` defines `KIND_NIP29_GROUP_METADATA: u32 = 39000` (module doc: "the authoritative source for Buzz kind numbers"). A unit test asserts `is_parameterized_replaceable(39000)` with the comment "NIP-29 group metadata". `39000` is absent from `AUTHOR_ONLY_KINDS`, `P_GATED_KINDS`, `SHARED_GATED_KINDS`, and from `is_relay_only_kind`'s match arms.
- `crates/buzz-relay/src/handlers/side_effects.rs`'s `emit_group_discovery_events` builds the kind-39000 event's exact tag list (`d`, `name`, `about`, `private`/`public`, `hidden`+`p` for DM channels, `closed`, `t`, `topic`, `purpose`, `archived`, `ttl`, `ttl_deadline`) and hands it to `emit_addressable_discovery_event`, which signs with the relay keypair and content `""`, then calls `state.db.replace_addressable_event(..., Some(channel_id))`.
- `crates/buzz-db/src/store/replaceable.rs`'s `replace_addressable_event` doc comment states it covers "NIP-16 kinds (0, 3, 41, 10000-19999) and NIP-29 discovery state (39000-39002)", keeping only the highest `created_at` per `(kind, pubkey, channel_id)`, ties broken by lowest event id.
- `crates/buzz-acp/src/relay.rs` and `crates/buzz-acp/src/pool.rs` each query kind 39000 filtered by the `d` tag (channel UUID) as consumers (channel discovery, and per-turn channel-info refresh for agent prompts).
- `crates/buzz-test-client/tests/e2e_relay.rs::test_nip29_standard_client_flow` and `crates/buzz-test-client/tests/e2e_nostr_interop.rs::test_dm_discovery_events_emitted` assert on kind-39000 events (name tag, hidden/private tags respectively) — existing conformance coverage.
- NIP-01 (fetched at pinned commit `dabfcb2aaecf4fa374eda8b1232ab303a03f60ba`) defines the addressable range as `30000 <= n < 40000`. NIP-29 (same pinned commit) defines the kind-39000 tag vocabulary: `name`, `picture`, `banner`, `about`, `private`, `restricted`, `hidden`, `closed`, `livekit`, `supported_kinds`.
- `python3 launchpad/project-intelligence/corpus/validate.py` and `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` are the two gates this task must pass; neither has been run yet against this branch's new file.

STEP 1 — Draft the corpus node [independent]

Create `launchpad/docs/corpus/events/kinds/kind-39000-channel-metadata.md` with schema-valid front matter (`id: events-kinds-kind-39000-channel-metadata`, `type: interfaces-events`, `status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`, one commit-only provenance `FACT`, plus one `evidence` entry per substantive body claim, classified FACT/INFERENCE/TEAM_KNOWLEDGE honestly) and a body following the event-kind template's 9 sections, addressing every bullet of issue #874's Definition of done. Declare `relationships: [{type: implements, target: corpus-template-event-kind}]` (that id is merged on `origin/launchpad`, confirmed above) and no other edges, since no sibling kind/interface node exists yet under `launchpad/docs/corpus/events/`.

<!-- RUNS HERE -->

done when: the file exists at that path, is the only new hand-authored corpus document in the diff, and every DoD bullet from the issue body (kind number/name, persistent/replaceable/ephemeral classification, required/optional tags and validation rules, producers/consumers/authorization/persistence/fanout/search/audit treatment, NIP/spec link, handler/registry link, conformance/tests link) is addressed somewhere in the body.

STEP 2 — Validate against the deterministic corpus checker [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repository root. Fix any reported schema violation, unresolved relationship target, or unrecognized/non-resolving citation, and re-run until clean.

done when: the command exits 0.

STEP 3 — Run the corpus test suite (commit gate) [needs 2]

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in its own tool call.

done when: the command prints `OK` and exits 0.

STEP 4 — Self-review against the issue's DoD line by line [needs 3]

Re-read the diff against every Definition-of-done bullet in issue #874, confirm each evidence entry actually supports its claim by re-opening the cited file, confirm no second hand-authored canonical corpus document was created, and confirm `validate.py` still exits 0.

done when: a line-by-line pass over the DoD checklist has been performed and every bullet is either satisfied in the document or explicitly noted as out of scope with a reason, and `validate.py` re-run still exits 0.

STEP 5 — Commit [needs 4]

Stage exactly the new corpus document and this plan file, and create a signed-off commit: `git commit -s -m "docs(corpus): document kind 39000 channel metadata event (#874)"`. If the commit is rejected for a missing gate stamp, stop and report it as a finding rather than routing around it.

done when: `git log -1` on the branch shows the new commit with both files, or the task is reported BLOCKED with the specific gate-refusal reason.

PARALLEL

None. This is a single-file, single-author task; steps 2-5 each depend on the previous step's file state.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before commit (STEP 2).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print `OK` before commit, run as its own isolated tool call per the dispatch instructions (STEP 3).
- The repository's commit gate (signed-off commit, `git commit -s`) must accept the commit; if it refuses for a missing stamp, that is reported, not bypassed (STEP 5).

BUDGET

One document (~150-250 lines including front matter), five steps, no code changes, no test infrastructure changes. Expected total effort: well under an hour of tool time.

OPEN

- Whether `type: interfaces-events` is the correct enum value versus something else is not open — the template (`corpus-template-event-kind`) states this explicitly as the value a real instance "most plausibly" takes, and no other enum member fits an event-kind node. Not re-litigated per step.
- Whether a `depends-on`/`references` edge to a future kind-39001/39002 sibling node should exist is left for whenever those nodes are authored — declaring it now would target an id that does not exist, which is a hard validation error.

LEFT OUT

- Creating sibling corpus nodes for kind 39001 (group admins) or kind 39002 (group members) — each is a separate task/issue, and this task's own out-of-scope list forbids a second hand-authored canonical document.
- Documenting the `buzz-cli` or any consumer-facing operation surface built on top of kind 39000 (an "interface" node) — the event-kind template's own *Boundary against interface* section reserves that to a different node type.
- Reconciling Buzz's tag emission against NIP-29's full tag vocabulary (e.g. why `restricted`, `picture`, `banner`, `livekit`, `supported_kinds` are never emitted) beyond noting the gap — that is a product/spec question, not a documentation-accuracy one, and no issue was found scoping it.
