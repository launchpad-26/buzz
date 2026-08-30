Issue #1064 — task: document layers/data/deletion.md
Stated size: no `Size` line in the issue body; batch dispatch caps it  →  cap: 5 steps

ALREADY TRUE  (verified against git and the repo, not notes)
  `origin/launchpad` has no `launchpad/docs/corpus/layers/` tree yet (`find
  launchpad/docs/corpus -maxdepth 2 -type d` lists only architecture/, schema/,
  standards/, templates/) — this is the first `layers`-typed corpus node.
  `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum includes `layers`
  and requires id, type, status, origin, audiences, evidence; relationships is
  optional.
  `launchpad/docs/corpus/templates/concept.md` is the matching template for this
  issue's DoD shape (define in one sentence, state boundaries/non-goals, link
  related concepts, examples must not introduce a second concept).
  Two nodes already merged on `origin/launchpad` are substantive `references`
  targets: `architecture-containers-postgres` and `architecture-containers-relay`.
  Buzz's data layer implements two independent deletion mechanisms, confirmed by
  reading the code directly this session: soft/logical per-event and per-channel
  deletion (`UPDATE events/channels SET deleted_at = NOW()` in
  crates/buzz-db/src/event.rs::soft_delete_event_and_update_thread and
  crates/buzz-db/src/channel.rs::soft_delete_channel, triggered by NIP-09 kind:5
  and NIP-29 kind:9005/9008 in crates/buzz-relay/src/handlers/{ingest,side_effects}.rs),
  and a durable whole-community physical purge (buzz-deletion crate +
  crates/buzz-db/src/deletion.rs's staged DeletionStage lifecycle, migration
  migrations/0029_community_deletion.sql, whose own header states "The community
  row is never removed: it becomes the permanent name tombstone").
  No sibling issue in this batch (#1060-#1101) covers the whole-community deletion
  engine specifically; #1100 (retention.md) and #1072 (object-storage/retention.md)
  are time-based expiry, a different concept from deletion-on-request.
  `launchpad/docs/corpus/layers/data/deletion.md` does not exist yet.

STEP 1  Write front matter for layers/data/deletion.md               [independent]
        id: layers-data-deletion, type: layers, status: draft, origin: launchpad,
        audiences: [agent, developer, operator]; one evidence entry per
        substantive claim (FACT for anything opened this session, INFERENCE for
        reasoned connections, confidence set honestly); two `references`
        relationships to architecture-containers-postgres and
        architecture-containers-relay.
        done when: the front matter is valid YAML and every field name/enum value
        matches node.schema.json.

STEP 2  Write the body per templates/concept.md            [needs 1]  ← RUNS HERE
        Definition (one sentence, then the two-mechanism split); Background (why
        two mechanisms coexist); Use cases; Comparison table (soft-delete vs.
        durable community deletion: trigger, scope, physical effect,
        reversibility); Related resources (the two relationships, in prose too);
        Scope and omissions (excludes retention/TTL expiry — #1100's node;
        excludes full DeletionStage field-by-field mechanics — reference-shaped,
        not concept-shaped; excludes moderation-driven content redaction — not
        inspected this session, named as a gap).
        done when: every DoD bullet in issue #1064's body is satisfied by a
        specific section, and no claim in the body lacks a matching evidence
        entry.

STEP 3  Validate                                            [needs 2]
        Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
        repo root; fix any reported error and re-run.
        done when: the command exits 0.

STEP 4  Earn the commit gate and commit                     [needs 3]
        Run, as the sole command in its own tool call:
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
        -p "test_*.py"`; confirm OK. Then, in a separate call, `git add` the plan
        and the new document and `git commit -s`.
        done when: the unittest run reports OK and the commit succeeds with a DCO
        Signed-off-by trailer, as the only commit ahead of origin/launchpad.

STEP 5  Self-review                                          [needs 4]
        Re-read `git diff origin/launchpad -- .` against issue #1064's DoD
        checklist line by line; confirm both relationship targets still resolve,
        every evidence entry cites something actually opened this session, and
        validate.py still exits 0.
        done when: every DoD bullet has a corresponding sentence/section in the
        diff and validation is still green.

PARALLEL  None of these steps may run as parallel subagents — step 2 depends on
          step 1's chosen id/relationships being fixed before the body's Related
          Resources section names them, and every later step depends on the file
          step 2 produced. This is one small document with no independent
          sub-tasks to fan out.
GATES     No `review-*` skill applies — this is a docs-only corpus node, not a
          code diff. `qa` explore mode does not apply — no runtime interface to
          exercise. The two gates that do apply are named in steps 3 and 4:
          `validate.py` must exit 0 before commit, and the corpus unittest suite
          must report OK to earn `verify-gate.sh`'s stamp before commit.
BUDGET    Step 2 (writing the body) is most likely to eat the budget — it is the
          only step requiring judgment about scope and evidence classification
          rather than a mechanical check.
OPEN      Whether `audiences` should also include `reviewer` — left out because
          this is a subject-matter concept node, not a process document; flagged
          here rather than silently decided either way.
LEFT OUT  Documenting the full DeletionStage state machine's field-by-field
          mechanics — reference-shaped content (a future reference-template task),
          not concept-shaped, and issue #1064's own DoD warns against folding a
          second canonical document's content into this one.
          A relationship to a layers/data/retention.md or
          layers/data/data-lifecycle.md node — neither exists on origin/launchpad
          yet (#1100 and #1062 are unmerged), so no such edge can resolve today;
          named in the body's scope section instead.
