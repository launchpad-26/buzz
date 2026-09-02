Issue #994: document interfaces/nostr/buzz-nips/nip-ap.md

Stated size: single hand-authored corpus document, small task -> cap: 5 steps

ALREADY TRUE

- `launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-ap.md` does not exist —
  `find launchpad/docs/corpus/interfaces -type f` returns nothing at all; the whole
  `interfaces/` subtree is unmerged. There is no existing sibling file to update.
- The authoritative spec, `docs/nips/NIP-AP.md`, exists at the repo root and was read
  in full (387 lines): kind:30175 (persona), kind:30176 (team, referenced but not the
  subject), kind:30177 (managed-agent instance), kind:30178 (team-catalog projection),
  the persona slug grammar, the shared-tag-gated read model, relay ingest validation
  rules, and reference test vectors with pinned keys.
- `node.schema.json`'s `type` enum has exactly one interface-shaped value:
  `interfaces-events` (architecture, layers, capabilities, platforms, implementation,
  interfaces-events, verification, operations, development, release, governance,
  agent, ingestion). `launchpad/docs/corpus/templates/interface.md` (a governance node,
  not a fill-in template we copy verbatim) confirms `type: interfaces-events` is the
  value an interface-shaped node carries, and lays out required body sections:
  Interface description, Operations (table pointing at code/NIP, not restating it),
  Contract and stability, Boundary, Relationships, Scope and omissions.
- Implementation confirmed in code, not just the spec prose:
  - `crates/buzz-core/src/kind.rs` defines `KIND_PERSONA = 30175`, `KIND_TEAM = 30176`,
    `KIND_MANAGED_AGENT = 30177`, `KIND_TEAM_CATALOG = 30178`, and
    `SHARED_GATED_KINDS = &[KIND_PERSONA, KIND_TEAM_CATALOG]` plus
    `is_shared_gated_kind()`.
  - `crates/buzz-relay/src/handlers/ingest.rs` has `validate_persona_envelope` (slug
    grammar `^[a-z0-9][a-z0-9_-]{0,63}$`, shared-tag shape) and
    `validate_team_catalog_envelope` (bounded non-empty `d` tag, no slug grammar,
    same shared-tag shape).
  - `crates/buzz-db/src/store/event.rs` implements the pre-`LIMIT` SQL visibility
    pushdown (`shared_gated_reader` field, `AND (kind NOT IN (30175,30178) OR
    pubkey = $reader OR tags @> '[["shared","true"]]')`), backed by
    `migrations/0004_events_tags_gin.sql`.
  - `crates/buzz-cli/src/commands/channels.rs` reads kind:30176 team events for
    persona slugs and paginates kind:30177 managed-agent events for roster
    resolution (`fetch_team_persona_slugs`, `scan_managed_agents_by_owner`).
  - `crates/buzz-acp/src/config.rs` carries `respond_to`/`respond_to_allowlist`
    fields matching the NIP's reserved instance-level behavioral fields.
  - `crates/buzz-test-client/tests/e2e_persona.rs`,
    `crates/buzz-test-client/tests/e2e_team_catalog.rs`,
    `crates/buzz-test-client/tests/e2e_managed_agent.rs`, and
    `crates/buzz-test-client/tests/e2e_team.rs` are the E2E suites exercising this
    NIP's kinds end to end (envelope validation, NIP-33 replacement, the shared-gate
    access-control matrix).
- No `PersonaEventContent`-named struct exists in the crates searched; the wire
  content fields (`display_name`, `system_prompt`, etc.) are parsed ad hoc as
  `serde_json::Value` at the call sites inspected (`channels.rs`). This is recorded
  as a gap in the drafted node rather than invented.
- Worktree HEAD at drafting time: `650354eab8d41ab6ce1a71de079a6c6d95c69052`
  (`git rev-parse HEAD`, matches `origin/launchpad`).

STEP 1 — Draft the node [independent]

<!-- RUNS HERE -->
Write `launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-ap.md` with schema-valid
front matter (`id: interfaces-nostr-buzz-nips-nip-ap`, `type: interfaces-events`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`,
`evidence`, no `relationships`) and a body covering: Interface description; an
Operations table (persona create/read/list/delete, team-catalog share/unshare, the
relay's shared-gate enforcement points) each citing a code symbol or NIP section
rather than restating it; Contract and stability (NIP-33 replacement + tiebreak,
slug/d-tag grammars, the shared-tag exact-shape rule, versioning notes from the spec's
"Mixed-version note" and "Slimming: kind:30177" sections); at least one valid example
and one failure example drawn from the spec's Reference test vectors and Ingest
validation rules; a Boundary paragraph excluding per-kind wire-format cataloguing;
Relationships (declared: none, with the check performed named); Scope and omissions
naming the `PersonaEventContent`-struct gap and any other unresolved point.
done when: the file exists, contains YAML front matter parseable as the six required
node.schema.json keys, and its body contains a section header matching each of
Interface description / Operations / Contract and stability / Boundary /
Relationships / Scope and omissions.

STEP 2 — Validate corpus structure [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo root.
Fix any FAIL line the new node introduces (schema violation, broken relationship
target, bad citation shape). UNVERIFIED notices are acceptable; do not silently
work around a FAIL not caused by this node — treat it as a separate finding.
done when: the command exits 0 and prints no FAIL line attributable to
`nip-ap.md`.

STEP 3 — Earn the commit gate [needs 2]

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
done when: the command prints `OK` (no failures, no errors).

STEP 4 — Commit [needs 3]

In a separate tool call from Step 3's test run:
`git add launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-ap.md
launchpad/plans/2026-09-01-issue-994-interfaces-nostr-buzz-nips-nip-ap.md`
then `git commit -s -m "docs(corpus): document Buzz NIP-AP interface (#994)"`.
If the commit is rejected for a missing gate stamp, do not touch the stamp file and
do not use `--no-verify` — report it as a finding instead of routing around it.
done when: `git log -1 --format=%H` shows a new commit containing exactly the two
files above, or the rejection is reported verbatim as a finding.

STEP 5 — Self-review against the DoD [needs 4]

Re-read the committed diff line by line against issue #994's Definition-of-done
checklist (one hand-authored doc only; schema-valid front matter with stable id,
type, status, origin, audiences, evidence, relationships; one independently
maintainable node; every substantive claim traceable and FACT/INFERENCE/
TEAM_KNOWLEDGE not conflated; links to implementation/spec without duplicating it;
checked against the recorded revision; validate.py clean; inputs/outputs/errors,
auth, versioning/compatibility, ordering/idempotency, spec link, valid + failure
example all present). Re-open any cited file whose claim is not obviously supported
on a second look.
done when: every DoD bullet is confirmed against the actual file content (not
memory), `validate.py` is re-run and still exits 0, and no second hand-authored
canonical corpus document exists in the diff.

PARALLEL

None. All five steps are sequential — a single small document with a hard commit
gate has no independent parallel track.

GATES

- `validate.py` exit 0 (Step 2) before committing.
- The corpus test suite prints `OK` (Step 3) before committing — run alone, in its
  own tool call, per the task's explicit instruction.
- The pre-commit/pre-push gate stamp check on `git commit -s` (Step 4) — if it
  rejects the commit, that is reported as a finding, not bypassed.

BUDGET

One file created (`nip-ap.md`), one plan file, one commit. No code changes, no
second corpus document, no PR opened.

OPEN

- Whether `PersonaEventContent`'s ad hoc `serde_json::Value` parsing (rather than a
  named typed struct) is intentional or a gap the corpus should flag more strongly —
  left as a Scope-and-omissions note in the drafted node, not resolved here.
- Whether a future `references` relationship to an event-kind-shaped sibling node
  (once one exists for kind:30175/30177/30178) should be added later — deliberately
  deferred; no such sibling node is merged to `origin/launchpad` yet.

LEFT OUT

- Re-deriving scope from parent Feature #616 or PRD #602 — the issue body is the
  spec, per the task's explicit instruction.
- Any `relationships` entries — sibling `buzz-nip` nodes are unmerged and would be a
  hard validation error against `origin/launchpad`; they are prose-mentioned instead.
- Editing `docs/nips/NIP-AP.md` itself or any implementation code — this is a
  documentation-only corpus task.
