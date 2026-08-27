Issue #689 — task: document architecture/principles/community-is-security-boundary.md

ALREADY TRUE  node.schema.json and launchpad/docs/corpus/AGENTS.md are merged on
  origin/launchpad (verified at a44cf52fc740ebebbdd671427480d14f0bce0115); no per-type
  template exists yet (0 of 26 merged, per AGENTS.md); and
  launchpad/docs/corpus/architecture/principles/community-is-security-boundary.md does
  not exist in this worktree.

STEP 1  Gather evidence for the invariant: read crates/buzz-relay/src/tenant.rs
        (bind_community, HostResolver, BindError::UnmappedHost),
        crates/buzz-core/src/tenant.rs (CommunityId, TenantContext, normalize_host),
        crates/buzz-relay/src/router.rs (WS-door bind-before-upgrade + generic 404),
        the 11-file/24-callsite fan-out of bind_community across REST/media/git/
        workflows/admin, crates/buzz-db/src/event.rs#for_community and channel.rs
        (DB-level community_id scoping), crates/buzz-relay/src/handlers/ingest.rs
        #check_channel_membership (the `#h`-tag override-attempt enforcement point),
        migrations/0001_initial_schema.sql (UNIQUE INDEX on lower(host)), NOSTR.md
        (host-derived community prose), docs/multi-tenant-conformance.md ("row zero"
        contract), and crates/buzz-test-client/tests/conformance_multitenant.rs (the
        A/B isolation conformance suite — `#[ignore]`-gated, needs a live two-host relay).
        done when: every claim in the finished document has a citation to a file
        actually opened above.

STEP 2  Write the front matter (id: architecture-principles-community-is-security-
        boundary, type: architecture, status: draft, origin: launchpad, audiences:
        [agent, developer, operator, reviewer], no relationships — no merged node is
        topically related) and the body: one unambiguous MUST/MUST NOT statement of
        the invariant, scope (which states/operations it governs), enforcement points
        and observable failure behavior (generic fail-closed rejection, never a
        default tenant), and a scope-and-omissions section naming the conformance
        suite as the verification mechanism plus what remains unverified (the suite
        is `#[ignore]`-gated and was not executed in this task).
        done when: the file exists and is schema-shaped.                [RUNS HERE]

STEP 3  Validate: `python3 launchpad/project-intelligence/corpus/validate.py` must
        exit 0 against the full corpus tree including the new file.
        done when: exit 0.

STEP 4  Earn the commit-verification stamp with
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        (run alone, in its own tool call), then commit the plan and the document
        together and open a draft PR against launchpad.
        done when: unittest reports OK, commit succeeds, PR is opened as draft.

PARALLEL  None — one document, one plan file, strictly sequential.

GATES     python3 launchpad/project-intelligence/corpus/validate.py (must exit 0).
          review-adjudicate and the cross-model final pass are explicitly deferred to
          the batch owner's morning review of the whole 47-issue run — not run here.

BUDGET    Evidence-gathering (STEP 1) is the step most likely to take the most time:
          the invariant spans host-resolution, per-surface call sites, DB-level
          scoping, and the `#h`-tag override path, and every FACT needs an opened
          source rather than a plausible-sounding one.

OPEN      The issue's DoD asks the document to link "at least one verification/
          conformance mechanism" for the invariant. The only executable conformance
          suite (conformance_multitenant.rs) is `#[ignore]`-gated and requires a live
          two-host relay deployment neither available nor in scope to stand up for
          this task — the document links it and says so plainly, rather than either
          skipping the link or falsely implying the suite was run.

LEFT OUT  Standing up a two-host relay to actually execute the A/B isolation suite.
          Any second hand-authored corpus document. Editing AGENTS.md or the schema.
          Restating node.schema.json's enum lists or field-combination matrix in prose.
