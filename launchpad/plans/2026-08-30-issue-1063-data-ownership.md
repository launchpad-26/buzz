Issue #1063 — task: document layers/data/data-ownership.md
Stated size: none given (issue has no `Size` line) → user-selected cap: 5 steps

ALREADY TRUE  (verified against git and the repo, not notes)
  `launchpad/docs/corpus/schema/node.schema.json`, `AGENTS.md`, the `concept.md`
    template, and the `standards/` set (taxonomy, identifiers, front-matter, atomicity,
    evidence, linking, naming) are merged on `origin/launchpad`
    (`338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`).
  The target file `launchpad/docs/corpus/layers/data/data-ownership.md` does not exist,
    and neither does the `layers/` directory — this is the first `type: layers` node in
    the corpus (confirmed with `git ls-tree -r --name-only origin/launchpad --
    launchpad/docs/corpus`).
  Two topically adjacent nodes are already merged and available as `references`
    targets: `architecture-principles-signed-events` (id-hash + Schnorr signature
    verification) and `architecture-principles-community-is-security-boundary`
    (host-derived tenant scoping) — both confirmed present in the same `git ls-tree`
    check.
  `migrations/0001_initial_schema.sql`'s `events` table already carries `pubkey BYTEA
    NOT NULL` and `community_id UUID NOT NULL REFERENCES communities(id)` as required
    columns.
  `crates/buzz-relay/src/handlers/event.rs` (line 660) already rejects any event where
    `event.pubkey != auth_pubkey` (gift-wrap carved out) with `"invalid: event pubkey
    does not match authenticated identity"`.
  `crates/buzz-relay/src/handlers/side_effects.rs::validate_standard_deletion_event`
    (called from `crates/buzz-relay/src/handlers/ingest.rs:2453`) already requires the
    deleting actor's pubkey to equal the target event's author pubkey, or that the actor
    is the target's registered agent owner via
    `crates/buzz-db/src/user.rs::is_agent_owner`/`set_agent_owner`.
  `crates/buzz-db/src/deletion.rs` is a different, already-built concept (a
    whole-community destructive-purge/GDPR pipeline: `DeletionRequest`, `DeletionStage`,
    manifest freezing, quiescing, fencing) — confirmed by reading its structure, not
    assumed from its filename.

STEP 1  [independent] Re-confirm the evidence above still holds at build time (files
        can drift between planning and building in a long-running batch) and read
        `crates/buzz-db/src/user.rs`'s `set_agent_owner`/`is_agent_owner` bodies in full
        for their exact semantics (first-mint-wins, one owner per agent pubkey,
        per-community). ← RUNS HERE
        done when: the four evidence citations above (`migrations/0001_initial_schema.sql`,
        `handlers/event.rs`, `handlers/side_effects.rs`, `buzz-db/src/user.rs`) have each
        been opened this session and still say what ALREADY TRUE claims.

STEP 2  [needs 1] Write the front matter: id `layers-data-data-ownership` (path-joined
        per the issue's own stated convention), type `layers`, status `draft`, origin
        `launchpad`, audiences `[agent, developer, operator, reviewer]`, one evidence
        entry per substantive claim from STEP 1 plus the commit-citation provenance
        entry, and two `references` relationships to
        `architecture-principles-signed-events` and
        `architecture-principles-community-is-security-boundary`.
        done when: the file exists with a YAML front-matter block containing all seven
        schema fields the task needs (id, type, status, origin, audiences, evidence,
        relationships) and no others.

STEP 3  [needs 2] Write the body against `templates/concept.md`'s required sections: a
        one-sentence Definition binding a stored event to the pubkey that signed it,
        explicitly disambiguating it from *community* ownership (a different concept,
        named but not documented here); a Use cases section explaining why a
        developer/reviewer needs this to reason about delete/replace authorization; the
        template's boundary-against-reference/procedure/glossary-term framing where it
        applies; and a Scope and omissions section naming both what is out of scope
        (community/tenant ownership and `transfer_community`, the agent-owner
        delegation mechanism's own full semantics, and the whole-community
        destructive-deletion pipeline in `crates/buzz-db/src/deletion.rs`) and what was
        expected but not verified (no live-DB test was run against `is_agent_owner`
        this session).
        done when: every required section from `templates/concept.md` is present
        (Definition, Use cases, Scope and omissions), and every substantive claim in
        the body has a matching `evidence` entry classified FACT with an opened
        citation.

STEP 4  [needs 3] Validate: run `python3 launchpad/project-intelligence/corpus/validate.py`
        against the full corpus tree including the new file. Fix and re-run until it
        exits 0.
        done when: the command exits 0 with no errors reported for the new file.

STEP 5  [needs 4] Earn the commit gate and commit: run
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
        "test_*.py"` as the sole prior command and confirm it reports OK; then, in a
        separate call, stage and commit the plan file and the new document with
        `git commit -s`.
        done when: the unittest run reports OK, and `git log -1 --stat` on the branch
        shows exactly one new commit ahead of `origin/launchpad` touching only the plan
        file and the new corpus document.

PARALLEL  None — STEPs 2 through 5 each depend on the previous step's output landing in
          the same file; there is no independent second file to parallelize against.
GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
          `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
          -p "test_*.py"` must report OK to earn the commit hook's verification stamp.
          review-adjudicate and the cross-model review pass are deferred to the batch
          owner's later bundling PR — not run here, per this task's own instructions
          (isolate/plan/build/verify/commit only, no push, no PR).
BUDGET    Single document, no code changes, no test changes — small, roughly 1-2 hours
          of agent time. STEP 1's re-read is the only step with any variance, and it is
          bounded to four already-identified files.
OPEN      Whether `audiences` should include `operator` is a judgement call — included
          because community-scoped delete authority and agent-owner delegation are both
          operationally relevant to whoever runs a community, and no standard settles
          the question either way. Whether a future `layers/data/` sibling node should
          own the agent-owner delegation mechanism in more depth, versus this node
          growing to cover it later, is left for whichever task discovers the need (per
          `standards/atomicity.md`'s test 4, the edge test).
LEFT OUT  No runtime/product code change. No second canonical document. No
          `relationships` targeting an id this task would have to invent — only ids
          already merged on `origin/launchpad` are used. No diagram — the ownership
          binding is stated in prose and citations, which is sufficient without one. No
          coverage of community/tenant-level ownership (relay operator APIs,
          `transfer_community`) or the whole-community destructive-deletion pipeline
          (`crates/buzz-db/src/deletion.rs`) — both are named as excluded neighbors in
          the node's own scope section, not described in depth.
