# Plan: issue #1000 — document interfaces/nostr/buzz-nips/nip-mp.md

Issue #1000 (`launchpad-26/buzz`), part of Feature #616 ("interface and event
contract corpus exists"). Definition of done is a checklist, no explicit
"Size:" line in the body — treating it as the smallest corpus-authoring unit:
one node, one source spec, no second document.

Stated size: not stated in issue body -> cap: 5 steps

RUNS HERE: /home/serina/Launchpad/buzz/__worktrees/task-1000-interfaces-nostr-buzz-nips-nip-mp on branch task/1000-interfaces-nostr-buzz-nips-nip-mp

ALREADY TRUE

- `docs/nips/NIP-MP.md` exists at repo root and is the authoritative spec for
  Buzz's custom NIP-MP (kind `30621`, "Multi-Repository Projects"). Verified
  by reading it in full at HEAD `650354eab8d41ab6ce1a71de079a6c6d95c69052`.
- `docs/nips/NIP-MP.fixtures.json` and `docs/nips/NIP-MP.fold-fixtures.json`
  exist alongside it (47985 and 22520 bytes respectively) — the machine
  fixture files the spec's Conformance Fixtures section names.
- `KIND_PROJECT: u32 = 30621` is defined in `crates/buzz-core/src/kind.rs`
  (line 632), matching the spec's kind table.
- `validate_project_envelope` is implemented in three places: relay ingest
  (`crates/buzz-relay/src/handlers/ingest.rs`, line 1609, the 8-rule ingest
  validator), the Rust SDK builder (`crates/buzz-sdk/src/builders.rs`, line
  2097), and is exercised by the CLI (`crates/buzz-cli/src/commands/projects.rs`)
  and the e2e suite (`crates/buzz-test-client/tests/e2e_project.rs`).
- `crates/buzz-relay/src/handlers/ingest.rs` line 5332 `include_str!`s
  `../../../../docs/nips/NIP-MP.fixtures.json` directly into its own unit
  tests — the fixture file is the live test oracle, not just documentation.
- `soft_delete_by_coordinate` (the inclusive `created_at <=` tombstone bound
  the spec's Deletion section cites) lives at
  `crates/buzz-db/src/store/event.rs` line 866 — NOT at
  `crates/buzz-db/src/event.rs`, the path the spec prose names. The spec's
  own path citation is stale; the corpus node must cite the real path.
- `validate_standard_deletion_event` (the NIP-OA-owner deletion extension) is
  at `crates/buzz-relay/src/handlers/side_effects.rs` line 229.
- `launchpad/docs/corpus/interfaces/` does not exist yet — no sibling
  `buzz-nips` node, no other `interfaces-events`-typed node to relate to.
  `find launchpad/docs/corpus/interfaces -type f` confirms this.
- `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum has no bare
  `interface` value; the closest fit is `interfaces-events`. This plan uses
  that value — not an invented one.
- The target file
  `launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-mp.md` does not exist
  (`ls` on its parent directory fails: no such file or directory).

STEP 1 [independent]

Draft `launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-mp.md`: front
matter (`id: interfaces-nostr-buzz-nips-nip-mp`, `type: interfaces-events`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer,
reviewer]`, no `relationships` — none resolve yet per ALREADY TRUE) plus a
body covering kind `30621`'s event format, the eight ingest rules, authority/
editing/deletion semantics, the client-side fold and claim-authority model,
and one valid + one failure example, each claim backed by an `evidence`
entry citing the spec file, the fixture files, or the relay/SDK/db source
already inspected above.
done when: the file exists at that path with schema-required front-matter
keys present and at least one `evidence` entry per section of body prose.

STEP 2 [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
worktree root and fix any FAIL line the new node causes (a pre-existing FAIL
unrelated to this node is a separate finding, not something this step
silently patches).
done when: the command exits 0.

STEP 3 [needs 2]

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in its own call.
done when: the command prints `OK` on stderr/stdout and exits 0.

STEP 4 [needs 3]

Stage and commit exactly the new corpus node plus this plan file with
`git commit -s`.
done when: `git log -1 --name-only` lists only
`launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-mp.md` and
`launchpad/plans/2026-09-01-issue-1000-interfaces-nostr-buzz-nips-nip-mp.md`,
and the commit's trailers include `Signed-off-by`.

STEP 5 [needs 4]

Self-review the diff against the issue's Definition-of-done checklist line
by line, confirm no second hand-authored canonical document was created, and
confirm `validate.py` still exits 0 against the committed tree.
done when: every DoD checklist line is either satisfied in the diff or
explicitly named as out of scope, and the LEFT OUT section below still holds.

PARALLEL

None of steps 1-5 can run concurrently — each depends on the previous file
state (draft -> validate -> test -> commit -> review). No independent branch
of work exists for this single-node task.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
  (step 2).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print `OK` (step 3), run alone in its own tool call per
  the task instructions.
- The commit-msg/pre-commit gate stamp requirement: if `git commit -s` is
  rejected for a missing gate stamp, that is reported as a finding — no
  stamp file is touched manually and `--no-verify` is never used.

BUDGET

One corpus node (~150-250 lines of Markdown), one plan file. No code changes,
no dependency changes, no second document. Expected total diff: two new
files.

OPEN

- Whether a future `interfaces-nostr-buzz-nips-*` sibling node (e.g. for
  another Buzz-custom NIP) should declare a `relationships` edge back to this
  one is left for that node's own author, once this node's id is merged and
  resolvable.
- Whether CLI-level (`buzz projects` subcommand) behavior deserves its own
  corpus node is left open — this node documents the wire/event contract,
  not the CLI ergonomics layer, per the issue's "one independently
  maintainable idea" DoD line.

LEFT OUT

- No changes to `docs/nips/NIP-MP.md` itself, even though its
  `crates/buzz-db/src/event.rs` path citation is stale (real path:
  `crates/buzz-db/src/store/event.rs`) — fixing the upstream spec's own prose
  is out of scope for a corpus-authoring task and would be "while here"
  cleanup the issue explicitly excludes.
- No second corpus node for the CLI's `projects` subcommand surface, the
  fold algorithm as a standalone client-behavior node, or the NIP-OA
  deletion-extension as its own policy node — each is a related but
  separately maintainable idea; none is folded into this node.
- No `relationships` front-matter entries — no sibling `interfaces-*` node
  exists in the corpus yet to target, and inventing one would be a hard
  validation error the moment a target id does not resolve.
