Issue #1004 — document interfaces/nostr/buzz-nips/nip-rs.md (parent Feature #616)
Stated size: issue carries no explicit Size line -> cap: 5 steps (dispatch instruction's own cap)

ALREADY TRUE

- `docs/nips/NIP-RS.md` exists at this exact name (797 lines) and is the
  authoritative spec text for "NIP-RS" — confirmed by reading it in full.
  Verified: `docs/nips/NIP-RS.md`.
- `launchpad/docs/corpus/interfaces/` does not exist anywhere in this worktree
  (`find launchpad/docs/corpus/interfaces -type f` → "No such file or
  directory"), so the target file
  `launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-rs.md` does not exist
  and this task creates a new node, not an update.
- `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` shows
  no sibling `buzz-nip*` interface node merged yet, and no other
  `interfaces/**` node — only `AGENTS.md`, `README.md`, `standards/*.md`, and
  `templates/*.md` (including `templates/interface.md`, id
  `corpus-template-interface`, `status: active`). This is the only mergeable
  relationship target found.
- `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum has 13 values;
  none is literally "interface" — the combined surface for interface- and
  event-kind-shaped nodes is the single value `interfaces-events`, confirmed
  both in the schema file and in `templates/interface.md`'s own "A note on
  `type`" section (which states every node built from that template carries
  `type: interfaces-events`).
- `templates/interface.md` is a merged, applicable template (not yet applied
  to any instance node) prescribing required sections: Interface description,
  Operations, Contract and stability, Boundary, Relationships, Scope and
  omissions.
- Code inspection (this session) confirms: `KIND_READ_STATE = 30078` in
  `crates/buzz-core/src/kind.rs:75`; desktop implements the full client
  protocol in `desktop/src/features/channels/readState/` (readStateManager.ts,
  readStateFormat.ts, readStateIdentity.ts, readStateStorage.ts); mobile
  mirrors it in `mobile/lib/shared/read_state/`; the relay recognizes NIP-RS
  coordinates structurally in
  `crates/buzz-db/src/store/replaceable.rs:151-167` (`is_nip_rs`) to hard-delete
  superseded versions instead of soft-tombstoning, and
  `crates/buzz-db/src/runtime/migration.rs` enforces d/t-tag cardinality on
  pre-existing rows. A repo-wide grep for the spec's "Manual-Unread Override
  Layer" wire keys (`ov_s`, `ov_c`, `ov_b`) and its full-state-load machinery
  found no implementation in any client or relay code — only a formal model
  under `docs/formal/nip-rs-unread/` (model.py, exhaustive.py, mutation.py,
  NOTE.md). This is a real scope boundary the node must state honestly, not
  paper over.
- `crates/buzz-cli` has no read-state subcommand or reference to `read-state`
  / `30078` — this NIP has no agent-facing (`buzz-cli`) surface, consistent
  with it being a desktop/mobile client-local sync feature.

STEP 1  Draft the corpus node                                    [independent]  ← RUNS HERE
        Create `launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-rs.md` with:
        - Front matter: `id: interfaces-nostr-buzz-nips-nip-rs`, `type:
          interfaces-events`, `status: draft`, `origin: launchpad`, `audiences:
          [agent, developer, reviewer]`, an `evidence` ledger with one entry per
          substantive claim (revision citation, kind constant, wire format, client
          managers, relay recognition/hard-delete behavior, the absence of the
          override layer in code, absence of a CLI surface), and one
          `relationships` entry: `{type: implements, target:
          corpus-template-interface}` (confirmed mergeable above).
        - Body sections per `templates/interface.md`'s required-sections list:
          Interface description, Operations (table citing code symbols/line
          ranges and the NIP itself), Contract and stability (versioning via
          schema `v:1`, NIP-33 replaceable-event LWW semantics, NIP-44
          encryption, ordering via the max-merge CvRDT rule, error/rejection per
          the spec's Content Validation and Invalid Cases sections), Boundary
          (explicitly excludes the Manual-Unread Override Layer as
          spec-only/unimplemented, and excludes NIP-33/NIP-44/NIP-78 themselves
          as externally-owned protocols this node only cites), one valid
          example and one failure example (both present verbatim in the spec's
          own Test Vectors / Invalid Cases sections — cite rather than invent),
          and Scope and omissions.
        - No second hand-authored canonical corpus document is created.
        done when: the file exists, front matter validates by inspection against
        `node.schema.json`'s required/forbidden fields per entry class, and
        every Definition-of-done bullet in issue #1004 has a corresponding
        section or ledger entry.

STEP 2  Run corpus validation                                    [needs 1]
        Run `python3 launchpad/project-intelligence/corpus/validate.py` from
        the worktree root.
        done when: the command exits 0. `UNVERIFIED` notices are acceptable;
        any `FAIL` line not caused by this new node is reported as a fresh
        finding rather than worked around.

STEP 3  Run the corpus test suite as the commit gate              [needs 2]
        Run `python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the
        sole command in its own tool call.
        done when: output includes `OK`.

STEP 4  Commit                                                    [needs 3]
        `git add` the node and this plan file; `git commit -s -m
        "docs(corpus): document Buzz NIP-RS interface (#1004)"`.
        done when: `git log -1 --format=%H` returns a new commit containing
        exactly those two files (`git show --stat HEAD`), and the commit is
        not rejected for a missing gate stamp. If it is rejected for that
        reason, no stamp file is touched and `--no-verify` is not used — it
        is reported as a finding instead.

STEP 5  Self-review                                                [needs 4]
        Re-read the diff against issue #1004's Definition-of-done checklist
        line by line; confirm every `evidence` entry's citation actually
        supports its `statement`; confirm no second canonical document was
        created; re-run `validate.py` and confirm it still exits 0.
        done when: all four checks above pass, and the final report names
        issue number, worktree path, branch name, and `git rev-parse HEAD`.

PARALLEL  None. Steps 2-5 each depend on the previous step's file/commit
          state; this is a single-file documentation task with no
          independent parallel track.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must
          exit 0 (Step 2). `python3 -m unittest discover -s
          launchpad/project-intelligence/corpus/tests -p "test_*.py"` must
          print `OK` before committing (Step 3) — this is the commit gate;
          it is not bypassed with `--no-verify` under any circumstance. No
          `review-*` skill or `qa` explore mode applies: this is a docs-only
          corpus node with no runtime interface to exercise.

BUDGET    Step 1 (drafting the node) is the step most likely to eat the
          budget — the spec is 797 lines covering a base frontier-sync
          protocol plus an entire unimplemented override layer, and getting
          the Boundary section honest about what is/isn't in code is the
          hard part.

OPEN      Whether the corpus-wide convention for a node's optional self-link
          to its template should be `implements` (this template's own stated
          preference) or `references` (a sibling template's choice) is
          unsettled per `templates/interface.md`'s own "Expected but not
          verified" note — this plan follows the template's own stated
          preference (`implements`) since it is documented in the
          authoritative template for this exact node type.
          Whether the Manual-Unread Override Layer will ever be implemented
          in production code is a product decision outside this task's
          scope; the node states its current absence as a fact, not a
          prediction.

LEFT OUT  Implementing, prototyping, or filing a follow-up issue for the
          Manual-Unread Override Layer — issue #1004's Out-of-scope section
          bars "changing runtime product behavior unless a separately linked
          implementation issue owns that change," and no such issue is named
          here.
          Any second hand-authored canonical corpus document (e.g., a
          dedicated node for kind 30078 itself, or for the override layer) —
          issue #1004's own Out-of-scope section bars this, and the node
          instead `references` those subjects in prose without creating
          nodes for them.
          Editing `docs/nips/NIP-RS.md` itself, or
          `docs/formal/nip-rs-unread/` — this task documents the existing
          spec and code, it does not revise them.
