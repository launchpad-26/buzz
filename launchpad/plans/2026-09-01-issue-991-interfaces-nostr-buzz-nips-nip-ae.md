Issue 991
Stated size: task instructions cap this at a small single-document task -> cap: 5 steps

ALREADY TRUE

- `docs/nips/NIP-AE.md` exists at this exact path and is the authoritative NIP-AE
  spec text (Agent Engrams, kind:30174). Read in full.
- `launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-ae.md` does not exist —
  confirmed via `ls` (directory not found). Nothing to update; this is a create.
- `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum has no
  `interface`-literal value. The corpus's own interface template
  (`launchpad/docs/corpus/templates/interface.md`) documents that PRD #602 and the
  schema encode interface-shaped and event-kind-shaped nodes under one combined
  value: `interfaces-events`. That is the value this node must carry.
- Implementation confirmed against code, not just the spec:
  - `crates/buzz-core/src/kind.rs:94` — `pub const KIND_AGENT_ENGRAM: u32 = 30174`,
    doc comment cites `docs/nips/NIP-AE.md` and `crate::engram` directly.
  - `crates/buzz-core/src/engram.rs` — `validate_slug`, `normalize_slug`,
    `conversation_key`, `d_tag`, `Body` enum, `extract_refs`, `build_event`,
    `validate_and_decrypt`, `select_head` implement the spec's Slugs, Addressing,
    Bodies, References, Writing and Head-selection sections respectively.
  - `crates/buzz-cli/src/lib.rs` (`MemCmd` enum, ~line 1801) and
    `crates/buzz-cli/src/commands/mem.rs` — the `buzz mem` subcommand group
    (`ls`, `get`, `hash`, `set`, `patch`, `rm`) is the CLI-facing operation surface;
    `mem.rs` has its own `#[cfg(test)] mod tests` (line 780+).
  - `crates/buzz-relay/src/handlers/ingest.rs:1341` `validate_engram_envelope` —
    write-path envelope validation (exactly one 64-lowercase-hex `d` tag, exactly
    one 64-lowercase-hex `p` tag, syntactically-plausible NIP-44 v2 content),
    invoked at `ingest.rs:2728-2730` when `kind_u32 == KIND_AGENT_ENGRAM`. Tests
    `engram_envelope_accepts_canonical` (valid) and
    `engram_envelope_rejects_missing_p` (failure) exist in the same file
    (~lines 4287-4310). `required_scope_for_kind` (`ingest.rs:437-441`) requires
    `Scope::UsersWrite` for kind:30174 writes.
  - `crates/buzz-relay/src/handlers/req.rs:1239` `engram_filters_authorized` —
    read-path gate: for global (non-channel) subscriptions, a filter that can
    match kind:30174 must have `authors=[self]` or `#p=[self]`, enforced at
    `req.rs:225-230` before the NIP-50 search branch runs.
  - `crates/buzz-relay/src/handlers/ingest.rs:641-644` — kind:30174 is in the
    "never channel-scoped" list (addressed by `(pubkey_a, kind, d_tag)` only).
  - `crates/buzz-acp/src/engram_fetch.rs` — the ACP harness fetches the agent's
    `core` engram at session creation (`build_core_section`) and renders it into
    the agent's prompt, or emits `ONBOARDING_NUDGE` if none exists; never blocks
    session creation on fetch failure.
- Repository revision for provenance: `650354eab8d41ab6ce1a71de079a6c6d95c69052`
  (this worktree's `HEAD`, `origin/launchpad` at fetch time).
- Corpus AGENTS.md's evidence discipline (FACT/INFERENCE/TEAM_KNOWLEDGE), the
  interface template's required-sections skeleton, and `relationships.schema.json`
  are already read and will govern the body/front-matter shape.
- No other corpus node under `interfaces/nostr/buzz-nips/` exists yet (directory
  is new), so no sibling id can be a `relationships` target — per the template's
  own precedent, sibling unmerged nodes are prose-linked by filename, not by
  `relationships`.

STEP 1 [independent] <- RUNS HERE

Draft `launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-ae.md` following
`templates/interface.md`'s required sections (Interface description, Operations,
Contract and stability, Boundary, Relationships, Scope and omissions), with
front matter `id: interfaces-nostr-buzz-nips-nip-ae`, `type: interfaces-events`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`,
and an `evidence` ledger citing only sources actually opened in ALREADY TRUE above
(spec doc, `kind.rs`, `engram.rs`, `mem.rs`/`lib.rs`, `ingest.rs`,
`req.rs`, `engram_fetch.rs`) plus a commit citation for the recorded revision.
Include at least one valid-event example and one failure example (the two
`ingest.rs` test cases above, or the NIP-AE spec's own reference-vector Event 1
and a synthesized malformed-envelope case) and cover inputs/outputs,
error/rejection, auth/authorization (write scope + read `#p`/`authors` gate),
versioning/compatibility (the spec's own domain-prefix versioning note), and
ordering/idempotency (monotonic `created_at`, head selection tie-break).
`relationships`: none (no sibling buzz-nip node exists on `origin/launchpad` yet).
done when: the file exists at that exact path, every DoD bullet from the issue
body is addressed in its body or front matter, and no `relationships` entry is
declared.

STEP 2 [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
worktree root. Fix any FAIL it reports that traces to the new node (bad schema
field, unresolved relationship target, non-existent cited path). If it reports
a FAIL that does NOT trace to the new node, stop and report it as a finding
rather than editing around it.
done when: the command exits 0, or a pre-existing non-caused FAIL is reported
verbatim instead of being silently patched.

STEP 3 [needs 2]

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in its own tool call, and confirm it prints `OK`.
done when: the command's output contains `OK` and no `FAILED`/traceback.

STEP 4 [needs 3]

Stage exactly the two files (the new corpus node and this plan) and commit with
`git commit -s -m "docs(corpus): document Buzz NIP-AE interface (#991)"`. If the
commit is rejected for a missing gate stamp, stop — do not touch any stamp file
and do not pass `--no-verify`; report it as a finding instead.
done when: `git log -1 --name-only` shows exactly those two paths in the new
commit, or the rejection is reported verbatim as a finding.

STEP 5 [needs 4]

Self-review: re-read the committed diff against the issue's Definition-of-done
checklist line by line, confirm every `evidence` entry's citation was actually
opened during this work, confirm no second hand-authored canonical corpus
document was created, and re-run `validate.py` to confirm it still exits 0.
done when: each DoD bullet is confirmed satisfied or explicitly flagged as an
open finding, and `validate.py`'s final run in this step exits 0.

PARALLEL

None of these steps can run in parallel with each other — steps 2-5 each depend
on the previous step's file-on-disk or exit-code state, and step 1 is the sole
entry point. This is a single-document task with a linear build->validate->
gate->commit->review chain, not a multi-file change with independent slices.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
  (UNVERIFIED notices are non-fatal; FAIL lines are not) before committing.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  must print `OK`, run as the sole command in its own tool call per the task's
  explicit instruction, before the commit is attempted.
- The pre-commit/gate-stamp mechanism referenced by the task instructions: if
  `git commit -s` is rejected for a missing stamp, that is a stop-and-report
  condition, not a work-around-it condition.

BUDGET

One document (~150-250 lines of Markdown), one plan file, no code changes, no
new tests to write (existing Rust unit tests are cited as evidence, not
extended). Expected total tool calls: under 20 from this point. No new crate
dependencies, no schema changes, no CI workflow changes.

OPEN

- Whether the corpus standards docs (`standards/naming.md`, `standards/linking.md`,
  `standards/evidence.md`) impose additional per-field conventions beyond
  `node.schema.json` and `templates/interface.md` was not exhaustively checked
  line-by-line before drafting; `validate.py`'s exit code is the objective judge
  and step 2 will surface anything schema-enforced.
- Whether a future sibling `buzz-nip` interface node (e.g. NIP-AM, NIP-AP) should
  later gain a `references`/`part-of` edge to this one is left for that node's
  own author, per the template's own guidance on sibling-node ordering.

LEFT OUT

- No relationships are declared, because no sibling `buzz-nips` node or broader
  "agent interfaces" node exists on `origin/launchpad` yet — adding one now would
  be exactly the false-justification trap `AGENTS.md` warns about in reverse (an
  edge to a node that will exist is still a hard error today).
- No changes to `docs/nips/NIP-AE.md`, `crates/buzz-core/src/engram.rs`, or any
  other implementation/spec file — this task documents existing behavior, it
  does not alter it (issue's own "Out of scope" bullet: no runtime product
  behavior changes).
- No second corpus document, no corpus index regeneration beyond whatever
  `validate.py` reports as expected mechanical output.
- No PR is opened, no push, no merge — the task instructions are explicit that
  this stops at a local commit.
