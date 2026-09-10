Issue #995 — task: document interfaces/nostr/buzz-nips/nip-cw.md
Stated size: none stated  →  cap: 5 steps (this is a small single-document task per
the dispatch brief: one interface node, no second artefact)

Target file: `launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-cw.md`
Node id: `interfaces-nostr-buzz-nips-nip-cw` (assigned by the dispatch brief; permanent)
Base branch: `origin/launchpad`

ALREADY TRUE  (verified against git at 650354eab8d41ab6ce1a71de079a6c6d95c69052, not notes)
  `git status --short` in this worktree reports nothing untracked or modified before
    this plan file itself.
  `launchpad/docs/corpus/interfaces/` does not exist at all — this task creates the
    full `interfaces/nostr/buzz-nips/` path. `find launchpad/docs/corpus -name "*.md"
    -not -path "*/schema/*"` lists 82 files, none under `interfaces/`.
  `docs/nips/NIP-CW.md` exists at the exact path the brief expected and its title
    confirms the subject: "NIP-CW ... Channel Window", `draft optional relay`,
    depends on NIP-01/NIP-11/NIP-29/NIP-98 — issue #995's body (verified via
    `gh issue view 995`) targets `nip-cw` with no numbering mismatch.
  `docs/bridge-channel-window.md` is a second, older engineering doc for the same
    surface; its own header states "NIP-CW is the canonical, standalone specification
    ... where wording differs, NIP-CW governs" — so NIP-CW.md is the primary source,
    not this file, per the brief's own instruction.
  `node.schema.json`'s `type` enum has no separate `interface` value; the combined
    surface is the single token `interfaces-events` (confirmed against the enum list
    directly and against `templates/interface.md`'s own "A note on `type`" section,
    which states a node built from that template "therefore carries
    `type: interfaces-events`").
  `templates/interface.md` (`corpus-template-interface`) is the template to follow:
    required sections are Interface description, Operations, Contract and stability,
    Boundary, Relationships, Scope and omissions.
  The relay implements the wire surface at `crates/buzz-relay/src/api/bridge.rs`
    (`handle_channel_window_filter`, line 489; constants `BRIDGE_WINDOW_DEFAULT_LIMIT`
    = 50, `BRIDGE_WINDOW_MAX_LIMIT` = 200, lines 388-389), kind constants
    `KIND_THREAD_SUMMARY` = 39005 and `KIND_WINDOW_BOUNDS` = 39006 in
    `crates/buzz-core/src/kind.rs` (lines 435, 439), and the DB layer
    `get_channel_window_with_session` in `crates/buzz-db/src/store/thread.rs`
    (line 1048) plus its top-level predicate (lines 582-654: `depth IS NULL OR
    depth = 0 OR (depth = 1 AND broadcast = true)`).
  `POST /query` is NIP-98-authenticated per `crates/buzz-relay/src/router.rs`
    (route table comment line 71, "Nostr HTTP bridge (NIP-98 auth)").
  `crates/buzz-test-client/tests/e2e_nostr_interop.rs` carries both a valid-path
    e2e test, `test_channel_window_rows_overlays_and_exact_multiple_exhaustion`
    (line 1776, `#[ignore]`), and a failure-path e2e test,
    `test_channel_window_rejects_half_cursor_and_client_overlay_kinds` (line 1920,
    `#[ignore]`) that asserts the 400s NIP-CW's cursor-grammar section requires.
  `git log --oneline -- docs/nips/NIP-CW.md` shows exactly one commit,
    `62bb9fe8c` ("GUI read-model overhaul: server-assembled channel windows
    (Correct™ pagination + relay-signed bounds) (#1500)"), matching the NIP text's
    own reference to "#1500 enforces" in §Overlay Trust.
  No sibling `buzz-nips` node exists yet under `interfaces/nostr/buzz-nips/`
    (directory does not exist), so no `relationships[].target` toward a sibling NIP
    node can resolve on `origin/launchpad` — per AGENTS.md step 9, that means no such
    edge is added; siblings get named in prose by filename instead.
  `AGENTS.md`'s evidence table and `node.schema.json`'s conditional rules govern
    FACT/INFERENCE/TEAM_KNOWLEDGE field requirements; all evidence in this node is
    drawn from opened sources (FACT) plus the two GitHub-issue attributions already
    quoted above (TEAM_KNOWLEDGE, `provided_by` the issue).

STEP 1  Create the node file with schema-valid front matter and provenance   [independent]
        Create `launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-cw.md` (creating
        the `interfaces/nostr/buzz-nips/` directories) with front matter: `id:
        interfaces-nostr-buzz-nips-nip-cw`, `type: interfaces-events`,
        `status: draft` (NIP-CW.md itself is tagged `draft`), `origin: launchpad`,
        `audiences: [agent, developer, reviewer]`, and the mandatory commit-only FACT
        recording revision 650354eab8d41ab6ce1a71de079a6c6d95c69052. No
        `relationships` key (per ALREADY TRUE, no sibling node resolves).
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0
                   with the new file present and empty of a body beyond a stub
                   heading, and `git cat-file -e 650354eab8d41ab6ce1a71de079a6c6d95c69052`
                   exits 0.

STEP 2  Write Interface description and Operations           [needs 1]  ← RUNS HERE
        Write the Interface description paragraph (the boundary: `POST /query`'s
        `top_level: true` filter extension on Buzz's NIP-98-authenticated HTTP
        bridge, no new endpoint, wire carries only signed Nostr events) and the
        Operations table: the window request itself (cites `docs/nips/NIP-CW.md`
        §Request and `bridge.rs::handle_channel_window_filter` line 489), the
        `kind:39005` thread-summary overlay (cites `kind.rs:435` and `bridge.rs`
        lines ~625-648), and the `kind:39006` window-bounds overlay (cites
        `kind.rs:439` and `bridge.rs` lines ~649-667). Each row is a FACT citing the
        code symbol plus the NIP section, never restated from memory alone.
        done when: validator exits 0, and every Operations-table row has a matching
                   `evidence` entry citing at least one repo-relative path (checked
                   by reading the table against the ledger).

STEP 3  Write Contract and stability, and the DoD's specific bullets    [needs 2]
        Write Contract and stability covering: inputs/messages (request filter
        fields), outputs/responses (rows, aux closure, summaries, bounds — response
        ordering), error/rejection behavior (zero/multiple `#h` channels → 400 per
        NIP-CW §Request and `bridge.rs` lines 497-503; half a composite cursor → 400
        per §Request and the `test_channel_window_rejects_half_cursor...` test, line
        1920; malformed `before_id` → 400; inaccessible channel → empty result per
        §Access Scoping, not an error), authentication/authorization (NIP-98 on
        `POST /query`, access scoping before any row/overlay is computed),
        versioning/compatibility (§Degradation: extension fields are additive,
        unknown-field-tolerant relays serve a standard filter; overlay kinds are
        parameterized-replaceable, relay-only at ingest), ordering/idempotency
        (`(created_at DESC, id ASC)` keyset order; `has_more`/`next_cursor` as the
        sole exhaustion authority, never row count). Include one valid example
        (the head-request JSON body from NIP-CW §Request, paired with
        `test_channel_window_rows_overlays_and_exact_multiple_exhaustion`, line 1776)
        and one failure example (the half-cursor 400, paired with
        `test_channel_window_rejects_half_cursor_and_client_overlay_kinds`, line
        1920, both `#[ignore]`d e2e tests — noted as such, not claimed as currently
        run in CI).
        done when: validator exits 0; the body contains a fenced JSON example under a
                   heading naming it valid, and a second fenced example or paragraph
                   under a heading naming it a failure case, each citing its backing
                   test by file and line.

STEP 4  Write Boundary and Scope and omissions                         [needs 3]
        Write the Boundary section stating this node does not describe: a single
        Nostr event kind's own full wire contract in isolation (kind 39005/39006 are
        described here only as this interface's overlays, not as independent
        event-kind nodes — none exist yet to `references`); thread *reading* (NIP-CW
        is explicit that replies never appear as window rows); ingest, storage, or
        fan-out changes (explicit non-goal in NIP-CW). Then Scope and omissions per
        AGENTS.md step 8: what this node covers, an owned-by table for what it does
        not (thread-reading interface, if/when a node exists for it; the
        historical-query/live-fanout architecture flows already in the corpus), and
        — separately — what was expected but not verified: the two backing e2e tests
        are `#[ignore]`d (not run in default `cargo test`) and were not executed
        during authoring, only read; and the SHOULD-level Overlay Trust hardening
        NIP-CW itself calls "future hardening, ... not a current guarantee" is
        reported as such, not silently dropped.
        done when: validator exits 0; the body's Boundary section names the three
                   items above; the Scope and omissions table has at least one row;
                   and a `grep -n "not.*run\|ignore" launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-cw.md`
                   prints at least one line documenting the `#[ignore]` gap.

STEP 5  Self-review and full validation                                [needs 4]
        Re-read the finished node line by line against issue #995's Definition-of-done
        checklist (quoted in the dispatch brief) and against `templates/interface.md`'s
        Required sections list. Confirm every evidence entry's cited source was
        actually opened during this work (re-open any in doubt). Confirm no second
        hand-authored corpus document was created. Fix whatever the audit finds.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0;
                   `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
                   prints `OK`; and `git status --short` shows exactly the node file
                   and this plan file as new/changed.

PARALLEL  None. All five steps edit the same single file (the node's body grows
          section by section), and per AGENTS.md two edits to one file are
          sequential regardless of how independent the sections look. There is no
          second artefact — the issue's own out-of-scope list forbids a second
          hand-authored document.

GATES     `review-plan` on this plan before STEP 1 (self-run here; the report says
          so). `review-code` is not separately applicable in the code-diff sense —
          the change is documentation, not source — but the equivalent check is
          STEP 5's validator + evidence self-audit. `review-tests` does not apply:
          no test file is added or modified; STEP 3/4 only *cite* two pre-existing
          `#[ignore]`d tests, they do not run or alter them. `qa` explore mode does
          not apply: no new runtime interface is introduced, only documented.

BUDGET    STEP 3. Mapping NIP-CW's dense normative prose onto the DoD's specific
          bullets (inputs, outputs, errors, auth, versioning, ordering, examples)
          without re-deriving or contradicting the spec text is where the time goes
          — the node must cite and point at NIP-CW.md and the code, not restate the
          wire format from memory, per `templates/interface.md`'s own evidence
          expectations ("do not restate an externally owned protocol's wire format
          from memory").

OPEN      Whether the two `#[ignore]`d e2e tests should be characterized as
          "verification exists but is not exercised in default CI" or left
          unmentioned. Resolved here as: mention them explicitly as the failure/valid
          examples, and flag their `#[ignore]` status in Scope and omissions as an
          honesty requirement, not a corpus-standard obligation this task is
          settling generally.

          Whether `kind:39005`/`kind:39006` eventually get their own event-kind
          corpus nodes (per `#1337`'s template) that this node should `references`.
          Resolved as: no such nodes exist yet, so no edge is declared; a future task
          adds it once they merge.

LEFT OUT  Any `relationships` edges of any type. No sibling `buzz-nips` node and no
          event-kind node for 39005/39006 exists on `origin/launchpad` yet — per
          AGENTS.md step 9 and the brief's own instruction, sibling unmerged nodes
          are named by filename in prose, not linked as a resolving edge.

          A second hand-authored canonical corpus document. The issue's out-of-scope
          list forbids it, and this task creates exactly one file plus this plan.

          Restating the full NIP-CW wire-format prose a second time. The node
          documents the boundary, cites NIP-CW.md and the implementing code, and
          points rather than re-encodes, per `templates/interface.md`'s own guidance.

          Editing `docs/bridge-channel-window.md` or `docs/nips/NIP-CW.md`
          themselves. Both are pre-existing, out of this task's target-file scope.
