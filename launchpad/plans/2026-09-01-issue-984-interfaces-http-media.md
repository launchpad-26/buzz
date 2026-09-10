Issue #984 — interfaces/http/media.md: HTTP media (Blossom) interface node
Stated size: task instructions cap this at 5 steps (small single-document task)  →  cap: 5 steps

ALREADY TRUE  (verified against git, not notes)
  Worktree `__worktrees/task-984-interfaces-http-media` exists on branch
  `task/984-interfaces-http-media`, based on `origin/launchpad` at
  `650354eab8d41ab6ce1a71de079a6c6d95c69052` (`git rev-parse HEAD`).
  `git ls-tree -r --name-only HEAD -- launchpad/docs/corpus` lists no path under
  `interfaces/` anywhere in the tree — the target file
  `launchpad/docs/corpus/interfaces/http/media.md` does not exist; this is a create,
  not an update.
  `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum has no `interfaces-http`
  value — the only interface-shaped value is the single combined token
  `interfaces-events`, confirmed both in the schema and in
  `launchpad/docs/corpus/templates/interface.md`'s "A note on `type`" section.
  `launchpad/docs/corpus/templates/interface.md` (id `corpus-template-interface`) is
  merged to `origin/launchpad` and is the only interface-shaped template; it prescribes
  required sections (Interface description, Operations, Contract and stability,
  Boundary, Relationships, Scope and omissions).
  `launchpad/docs/corpus/architecture/flows/media-upload.md` (id
  `architecture-flows-media-upload`) and `.../media-download.md` (id
  `architecture-flows-media-download`) are both already merged to `origin/launchpad`
  (present in `git ls-tree HEAD`) — both ids resolve today, so `relationships` may
  safely target them.
  The relay's Blossom HTTP surface is implemented in `crates/buzz-relay/src/router.rs`
  (routes), `crates/buzz-relay/src/api/media.rs` (handlers + auth extractor),
  `crates/buzz-media/src/auth.rs` (BUD-11 verification), `crates/buzz-media/src/error.rs`
  (`MediaError` → HTTP status), `crates/buzz-media/src/types.rs` (`BlobDescriptor`),
  `crates/buzz-media/src/upload.rs` (idempotency short-circuit), and
  `crates/buzz-relay/src/config.rs` (size/rate/concurrency defaults) — all opened and
  read while drafting this plan.
  `crates/buzz-test-client/tests/e2e_media.rs` contains (confirmed by grep)
  `test_upload_and_get`, `test_upload_idempotent`, `test_upload_no_auth_returns_401`,
  `test_upload_missing_x_sha256_returns_401`, `test_upload_hash_mismatch_returns_400`
  (misleadingly named; its own assertion checks 401), `test_get_nonexistent_returns_404`,
  `test_unauthenticated_reads_are_rejected`, `test_upload_real_image`.
  Root `AGENTS.md:265-267` states the PR-screenshot workflow deliberately avoids
  `buzz upload`/the relay media endpoint (GitHub camo-proxy failure) — a usage caveat,
  not a contract fact about the endpoint itself.
  `python3 launchpad/project-intelligence/corpus/validate.py` has not yet been run
  against this new file — it does not exist yet.

STEP 1  Draft `launchpad/docs/corpus/interfaces/http/media.md`.  [independent]
        Follow `templates/interface.md`'s
        skeleton: front matter (id `interfaces-http-media`, type `interfaces-events`,
        status `draft`, origin `launchpad`, audiences `[agent, developer, reviewer]`,
        evidence ledger with a provenance commit citation plus one entry per substantive
        claim, `relationships` referencing `architecture-flows-media-upload` and
        `architecture-flows-media-download`); body sections Interface description,
        Operations (PUT /upload, PUT /media/upload legacy alias, GET/HEAD
        /media/{sha256_ext}, each citing its handler symbol), Contract and stability
        (auth model, BUD-01/02/11 versioning, error-status taxonomy, the
        idempotent-short-circuit-on-matching-hash behavior for the DoD's
        ordering/idempotency bullet), Boundary, Relationships, Scope and omissions (incl.
        the PR-screenshot caveat as a citation, and named gaps such as client-side
        auth-event construction not being inspected); a link to the Blossom BUD spec as
        the authoritative machine representation; one valid-flow example
        (`test_upload_and_get`-shaped) and one failure example
        (`test_upload_no_auth_returns_401`), both cited from `e2e_media.rs`.
        done when: the file exists at the exact path with the `id`/`type`/`status` values
        above, every required template section is present, and every FACT/INFERENCE
        evidence entry cites a source opened above or during drafting.

STEP 2  Validate the drafted node.  [needs 1]  ← RUNS HERE
        Run `python3 launchpad/project-intelligence/corpus/validate.py` from the worktree
        root; fix any FAIL line the new node introduces and re-run until clean.
        `UNVERIFIED` notices on the external BUD-spec URL and any commit-only FACT are
        expected, not failures.
        done when: the command exits 0.

STEP 3  Run the corpus schema/test-suite gate.  [needs 2]
        Run, as the sole command in its own tool call:
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
        "test_*.py"`.
        done when: the command prints `OK` with no failures or errors.

STEP 4  Commit the node and this plan.  [needs 3]
        `git add` the node and this plan file, then
        `git commit -s -m "docs(corpus): document HTTP media (Blossom) interface (#984)"`
        in a separate tool call. If the commit is rejected for a missing gate stamp, stop
        and report it as a finding rather than touching stamp files or using
        `--no-verify`.
        done when: `git log -1` on `task/984-interfaces-http-media` shows the new commit
        with a `Signed-off-by` trailer.

STEP 5  Self-review against issue #984's DoD.  [needs 4]
        Re-read the committed diff against the Definition-of-done checklist line
        by line (one hand-authored node; schema-valid front matter; one independently
        maintainable idea; FACT/INFERENCE/TEAM_KNOWLEDGE not conflated; links without
        duplicating; checked against the recorded revision; validate.py clean;
        inputs/outputs/errors defined; auth/versioning/ordering defined; spec link
        present; valid + failure examples present); confirm no second hand-authored
        canonical corpus document was created; re-run `validate.py` to confirm it still
        exits 0.
        done when: every DoD bullet has a traceable "yes, in section X" answer, or an
        explicit gap is named in the report.

PARALLEL  None of steps 2–5 can run in parallel with each other or with step 1 — each
          depends on the previous step's file state (draft → validate → test → commit →
          review is a strict pipeline for a single file). Step 1 is the only
          `[independent]` step, and there is nothing else to parallelize it against in
          this single-document task.
GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 (step 2)
          before commit. `python3 -m unittest discover -s
          launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print `OK`
          (step 3), run alone per the task instructions. No `review-*` skill or `qa`
          explore mode applies — this is a static Markdown document with no runtime
          interface to exercise.
BUDGET    Step 1 (drafting the node with a correctly evidenced ledger) is the step most
          likely to eat the budget — the evidence-classification and citation work is the
          bulk of the effort; steps 2–5 are mechanical by comparison.
OPEN      Whether `implements: corpus-template-interface` (an optional self-link back to
          the template) is added is left to drafting judgment — the template's own
          "Expected but not verified" section states this convention is unsettled
          corpus-wide; either choice satisfies the issue's DoD, so this plan does not
          decide it in advance.
LEFT OUT  No second corpus document (e.g. a dedicated event-kind node or an
          API-reference-depth catalogue) is created, per the issue's explicit
          out-of-scope list. No runtime/product behavior change. No resolution of the
          unsettled `#1321` provenance-update policy or the `implements`-vs-`references`
          self-link convention — both are named as open elsewhere and this node does not
          adjudicate them. No PR is opened and nothing is pushed, per the task
          instructions.
