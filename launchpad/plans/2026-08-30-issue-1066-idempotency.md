Issue #1066 — task: document layers/data/idempotency.md
Stated size: no Size line in the issue body → cap: 5 steps (per the corpus-batch-author dispatch instruction: "this is one small document")

ALREADY TRUE  (verified against git and the issue this session, not notes)
  Issue #1066 (launchpad-26/buzz) is open and its Objective names the target file exactly: launchpad/docs/corpus/layers/data/idempotency.md.
  node.schema.json's type enum includes "layers"; the target path's second segment ("data") is a sub-area name, not a schema field, so type: layers is correct.
  templates/concept.md is the matching template: Definition (required), optional intro/visual-aid/background, Use cases, optional Comparison, Related resources (prefer typed relationships over prose links), Scope and omissions.
  launchpad/docs/corpus/layers/data/idempotency.md does not exist yet (test -f confirmed).
  Worktree __worktrees/task-1066-idempotency on branch task/1066-idempotency is created from origin/launchpad at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5.
  crates/buzz-db/src/event.rs: insert_event (line 273) and insert_event_with_thread_metadata (block from ~line 1140) both use INSERT ... ON CONFLICT DO NOTHING and return was_inserted: bool from rows_affected() > 0. Module doc line 5: "Deduplication is application-layer: ON CONFLICT DO NOTHING."
  migrations/0001_initial_schema.sql line 233: events table PRIMARY KEY (community_id, created_at, id) — id is the Nostr content-derived event id, so resubmitting identical event content is a guaranteed database-level no-op.
  crates/buzz-relay/src/handlers/ingest.rs lines 2971-2976: when was_inserted is false, ingest returns IngestResult { accepted: true, message: "duplicate:" } before the is_side_effect_kind dispatch, so a retry does not re-run fan-out.
  launchpad/docs/corpus/architecture/flows/event-ingestion.md (id architecture-flows-event-ingestion, already on origin/launchpad) lines 327-331 documents this same behavior as "a deliberate idempotent-retry behavior, not a failure path" — a valid references relationship target.
  crates/buzz-media/src/upload.rs lines 94-98, function process_buffered_upload (starts line 54): Blossom uploads key storage by sha256 of the bytes and short-circuit the blob PUT when both sidecar and blob already exist — a second, independent subsystem's idempotent write.
  crates/buzz-db/src/lib.rs line 5156, replace_parameterized_event (NIP-33): keys replacement on (kind, pubkey, d_tag) with last-write-wins by created_at — a different mechanism (overwrite-by-recency) the node's boundary section must not conflate with idempotency.
  crates/buzz-auth/src/nip98_replay.rs lines 1-9: NIP-98 replay protection rejects a reused event id via a TTL-scoped Redis seen-set — the opposite response (reject, not accept-as-no-op) to a different problem (auth replay), the other boundary case worth naming.
  No corpus node besides architecture-flows-event-ingestion discusses idempotency, and no layers/ subtree exists yet — checked via find against origin/launchpad, not assumed.

STEP 1  Draft launchpad/docs/corpus/layers/data/idempotency.md against templates/concept.md's required sections, with front matter id: layers-data-idempotency, type: layers, status: draft, origin: launchpad, audiences: [developer, agent, reviewer], one references relationship to architecture-flows-event-ingestion, and one evidence entry per substantive claim (commit citation for provenance plus the ten claims listed under ALREADY TRUE).                                    [independent]
        done when: the file exists, front matter parses as YAML with those fields, and the body contains Definition, Use cases, Comparison (idempotent dedup vs. NIP-33 LWW vs. NIP-98 replay rejection), Related resources (relationship only, no duplicate prose link), and Scope and omissions sections.

STEP 2  Run python3 launchpad/project-intelligence/corpus/validate.py from the worktree root and fix whatever it reports (schema violation, bad relationship target, bad citation shape) until it exits 0.                        [needs 1]  ← RUNS HERE
        done when: the command's exit status is 0.

STEP 3  Run, as the sole command in its own tool call, python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py" and confirm it reports OK; then, in a separate call, git add the plan file and the new corpus doc and git commit -s.                        [needs 2]
        done when: the unittest run reports OK and `git log -1` shows the new commit on task/1066-idempotency.

STEP 4  Re-read git diff origin/launchpad -- . against every Definition-of-Done bullet in issue #1066's body, line by line; re-open every cited file/line to confirm each evidence entry actually supports its statement; confirm no second hand-authored corpus document exists in the diff; re-run validate.py.                        [needs 3]
        done when: every DoD bullet is satisfied, every citation checked against its live source, and validate.py still exits 0.

PARALLEL  None of these four steps can run in parallel — step 2 needs the file step 1 wrote, step 3 needs a clean validate.py from step 2, and step 4 reviews the commit step 3 makes. This is a single-document, single-worktree task with no independent surface to fan out onto.
GATES     No review-* skill applies — this is a single isolated corpus-authoring task inside a batch run, not a PR-ready branch; the batch orchestrator runs review after bundling. qa explore mode does not apply: there is no runtime interface, only a Markdown document and a schema validator.
BUDGET    Step 1 (drafting the body and evidence ledger) is the step most likely to overrun — writing honest FACT/INFERENCE/TEAM_KNOWLEDGE classifications for every claim takes longer than the validator check itself.
OPEN      Whether standards/atomicity.md (an existing corpus governance node about the corpus's own single-idea-per-node discipline, not database transactional atomicity) should ever relate to this node — read this session; it is not the same subject, so no relationship is added, but a future reviewer disagreeing should say so explicitly rather than this plan assuming it silently.
LEFT OUT  Documenting NIP-33 parameterized-replaceable-event LWW semantics as its own concept node — out of scope per issue #1066's own "Out of scope" section (no second canonical document); named only as a boundary case in this node's Comparison/Scope section. Documenting NIP-98 replay protection as its own concept node — same reason. Any relationship to a hypothetical layers/data overview/index node — none exists in the corpus yet.
