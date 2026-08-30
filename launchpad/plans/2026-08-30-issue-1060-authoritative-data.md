Issue #1060 — task: document layers/data/authoritative-data.md
Stated size: none in issue body, capped per corpus-batch-author dispatch  →  cap: 5 steps

ALREADY TRUE  (verified against git and the repo, not notes)
  Repository revision: commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5
  (origin/launchpad tip at fetch time; this worktree was created directly from it).
  launchpad/docs/corpus/layers/data/authoritative-data.md does not exist; no
  launchpad/docs/corpus/layers/ directory exists yet (find returned nothing).
  launchpad/docs/corpus/schema/node.schema.json's type enum includes "layers",
  matching the target path's layers/ prefix.
  launchpad/docs/corpus/AGENTS.md (front-matter contract, evidence classes,
  citation shapes) and launchpad/docs/corpus/templates/concept.md (required
  sections: Definition, optional Background, Use cases, optional Comparison,
  Related resources/relationships, Scope and omissions) were read in full. The
  issue's DoD bullets ("defines the term in one sentence before deeper
  explanation", "states boundaries/non-goals", "links related concepts/
  implementation/verification", "examples don't introduce a second canonical
  concept") match concept.md's shape, not glossary-term.md's (which caps at
  1-3 sentences with no deeper explanation) — "authoritative data" needs more
  than a lookup definition.
  docs/multi-tenant-relay.md:76-87 already states the three-tier data model this
  node documents: a canonical message log L (append-only, keyed
  (community_id, created_at, id)), a tenant-scoped relational control plane
  (channels, channel_members, api_tokens, workflows, audit entries), and
  "disposable projections" (mentions, thread metadata, reactions, full-text
  search — community_id-keyed, rebuildable from L, "never authoritative").
  migrations/0001_initial_schema.sql confirms this concretely: events (lines
  190-197) is the canonical log; thread_metadata (509-528, reply_count/
  descendant_count) and reactions (539-549) are derived projections keyed off
  event ids; events.search_tsv (198-210) is a generated column populated from
  content at insert time.
  ARCHITECTURE.md:394-428 (buzz-db) and :432-461 (buzz-pubsub, "Does NOT: ...
  store events") corroborate which crate owns authoritative storage vs. fan-out.
  A real, already-merged corpus node exists to link via references:
  architecture-principles-relay-is-source-of-truth
  (launchpad/docs/corpus/architecture/principles/relay-is-source-of-truth.md),
  confirmed present on origin/launchpad at the recorded revision. It documents
  "the relay is the sole authority for state" at the whole-relay level; this
  node documents the finer-grained question of which persisted structures
  inside that state are authoritative vs. derived — related, not duplicative.
  No existing corpus node names authoritative/derived data tiers as its subject
  (checked the full corpus file listing), so this is a genuinely new node.

STEP 1  Draft launchpad/docs/corpus/layers/data/authoritative-data.md         [independent]
        done when: the file exists at the target path with all schema-required
        front-matter fields present (id: layers-data-authoritative-data, type:
        layers, status: draft, origin: launchpad, audiences, an evidence
        ledger, one relationships entry: references →
        architecture-principles-relay-is-source-of-truth) and a body containing
        Definition, Comparison, Use cases and Scope and omissions sections,
        following templates/concept.md's shape. Evidence cites
        docs/multi-tenant-relay.md, migrations/0001_initial_schema.sql,
        ARCHITECTURE.md and the commit-pinned provenance entry. Scope and
        omissions states the boundary against the relay-as-sole-authority
        invariant, backup/DR procedure, and the git-on-object-storage
        manifest's own narrower authority claim.

STEP 2  Run the corpus validator                                             [needs 1]
        done when: `python3 launchpad/project-intelligence/corpus/validate.py`
        exits 0, run from the repo root, after fixing any reported error (bad
        citation path, unresolved relationship target, schema violation).

STEP 3  Self-check against the issue's own DoD checklist            [needs 2]  ← RUNS HERE
        done when: every DoD bullet in issue #1060 (one canonical document
        only; schema-valid front matter; one independently maintainable idea;
        every claim traceable and correctly classed FACT/INFERENCE/
        TEAM_KNOWLEDGE; links instead of duplicated content; checked against
        the recorded revision; validator clean; one-sentence-then-explanation
        definition; boundaries/non-goals stated; links to related concepts/
        implementation/verification; examples don't introduce a second
        concept) has a concrete, cited answer in the document, and
        `git diff origin/launchpad -- .` shows exactly the plan file plus the
        one target document changed.

PARALLEL  None of the 3 steps can run as independent subagents in practice —
          step 1 is the only real work and steps 2-3 each depend on its
          output in strict sequence. Step 1 is tagged [independent] only in
          the sense that no other pending step touches its file first.
GATES     No review-* skill applies — this is a docs-only corpus node with no
          runtime interface, so `qa` explore mode does not apply either. The
          only gate is the repo-wide commit gate specified by the task brief:
          `python3 -m unittest discover -s
          launchpad/project-intelligence/corpus/tests -p "test_*.py"` must
          report OK before committing, run as the sole command in its own
          step, separate from `git add`/`git commit`.
BUDGET    Step 1 (the draft itself) is the step most likely to eat the
          budget — getting the three-tier explanation and its evidence
          citations right is most of the work; steps 2-3 are fast checks.
OPEN      Whether "operator" belongs in `audiences` — the concept has
          operational relevance for backup/DR judgment calls, but no
          operator-specific procedure is written here. Resolved in favor of
          including it: the schema's `audiences` enum is about who needs to
          read the node, not who owns a procedure.
LEFT OUT  No second corpus document. No changes to runtime product behavior.
          No resolution of the ARCHITECTURE.md:7 / buzz-relay-mesh
          gossip-wording gap already recorded by the sibling
          relay-is-source-of-truth node — out of scope here and already
          owned there. No `depends-on` relationship to
          architecture-principles-relay-is-source-of-truth — `references` is
          the correct type per relationships.schema.json's directionality
          ("supporting context, no ownership or currency dependency
          implied"); this node's own claims do not require that node's
          claims to hold.
