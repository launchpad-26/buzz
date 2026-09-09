Issue #1208 — task: document operations/deployment/relay.md
Stated size: no `Size` line on the issue; dispatch brief caps this task at 5 steps  →  cap: 5 steps.

ALREADY TRUE  (verified against git, not notes)
  On branch `task/1208-deployment-relay`, based on `origin/launchpad` HEAD 473205a7457b208455f188847bfb27b01aa83cac,
    working tree clean. `node.schema.json`, `launchpad/docs/corpus/AGENTS.md`, and
    `launchpad/docs/corpus/templates/procedure.md` are merged and authoritative.
    `launchpad/docs/corpus/architecture/containers/relay.md`,
    `launchpad/docs/corpus/architecture/deployment/single-relay.md`, and
    `launchpad/docs/corpus/architecture/deployment/hosted-topology.md` are merged and already
    document the relay's container shape and its two concrete deployment topologies.
    `launchpad/docs/corpus/operations/` does not exist as a directory yet (confirmed:
    `find launchpad/docs/corpus/operations -type f` returns nothing); the target file does
    not exist.

STEP 1  [independent]  Gather evidence for the relay-specific deployment concerns that hold
        true regardless of which platform runs it (Compose/#1203, Helm/#1204,
        Kubernetes/#1205): image build/publish (`Dockerfile`, `.github/workflows/docker.yml`,
        `RELEASING.md`, `Justfile`'s `release-relay`), required env/secrets at the source
        (`crates/buzz-relay/src/config.rs`, `.env.example`, `deploy/compose/.env.example`),
        host-derived community boundary and NIP-11/domain config
        (`crates/buzz-relay/src/tenant.rs`, `crates/buzz-relay/src/nip11.rs`,
        `crates/buzz-relay/src/api/operator.rs`'s `POST /operator/communities`,
        `migrations/0001_initial_schema.sql`'s `communities` table,
        `scripts/seed-local-community.sh`, `scripts/start-relay-for-tests.sh`), startup
        ordering against Postgres/Redis/object storage (`crates/buzz-relay/src/main.rs`),
        health/readiness probes (`crates/buzz-relay/src/router.rs`), and release/upgrade/
        rollback plus verification (`deploy/compose/run.sh`, `deploy/compose/README.md`,
        `deploy/charts/buzz/README.md`).
        done when: every claim planned for the body has a specific opened source (path +
        symbol/line) recorded.

STEP 2  [needs 1]  ← RUNS HERE  Write `launchpad/docs/corpus/operations/deployment/relay.md`
        with schema-valid front matter (`id: operations-deployment-relay`, `type: operations`,
        `status: draft`, `origin: launchpad`, `audiences: [operator, developer]`, an `evidence`
        ledger with one commit-provenance FACT plus one entry per substantive claim, and
        `relationships: [references: architecture-containers-relay, references:
        architecture-deployment-single-relay, references:
        architecture-deployment-hosted-topology]` — all three exist on `origin/launchpad`
        per `<SCRATCH>/existing-node-ids.txt`, and this procedure genuinely assumes their
        background per `standards/linking.md` MUST 6, which forbids letting a body-prose
        mention stand in for a typed edge when the connection is real and resolves against the
        merge branch; no `operations/**` sibling exists yet, so no edge targets one) and a body
        following `templates/procedure.md`'s Required sections: Overview; Before you start;
        one numbered task sequence covering image/build → required env & secrets →
        community+domain/NIP-11 provisioning → startup ordering & health probes → verify
        serving → upgrade/rollback; See also; Boundary; Relationships (the three `references`
        edges above, explained in prose per `standards/linking.md`'s own guidance); Scope and
        omissions naming both what this node excludes and who owns it, and, separately, what
        was expected but could not be verified — including the honest gap found in STEP 1 if
        it holds: no documented production path exists for creating the first `communities`
        row outside the dev-only `scripts/seed-local-community.sh`.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 and
        every issue-1208 DoD bullet, including the four procedure-tail bullets, is addressed
        by a distinct section.

STEP 3  [needs 2]  Self-verify the diff line-by-line against the issue's DoD checklist; confirm
        every evidence entry supports its claim, no second canonical document was created, and
        validate.py still passes.
        done when: the audit is written and validate.py exits 0 on the current tree.

STEP 4  [needs 3]  Earn the verification stamp with the corpus unittest suite as the sole
        command in its own tool call, then commit the plan and the new document together.
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        reports OK and `git commit -s` succeeds without `--no-verify`.

PARALLEL  None — single new file, steps are strictly sequential (evidence gathers before the
          body cites it; the body must exist before it can be audited).

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before
          commit. `review-adjudicate` and the cross-model final review pass are deferred to
          the batch owner's later integration review — not run in this worktree.

BUDGET    STEP 2. The hard part is stating the relay-specific concerns (image, secrets,
          community/domain, startup order, probes, upgrade/rollback) at the altitude that
          holds across Compose/Helm/Kubernetes without drifting into any one platform's own
          command surface, which the three sibling procedure tasks (#1203/#1204/#1205) own.

OPEN      Whether `POST /operator/communities` (the only production-capable path found for
          creating a community row) is actually exercised by any documented operator runbook,
          or is a capability that exists in code without an operator-facing walkthrough
          anywhere in the repository — not resolved here; stated as a gap in the document's
          own scope-and-omissions rather than papered over. Whether
          `deploy/compose/.env.example`'s exact secret names/files are this node's own
          evidence or the Compose sibling's (#1203) — resolved by treating each secret's
          existence and purpose as relay-specific (true across platforms) while deferring the
          platform's exact injection mechanism to the sibling.

LEFT OUT  The relay-not-ready runbook (#1227) — this node documents planned, operator-
          initiated deployment, not incident response to an already-failing relay. Docker
          Compose's own command surface (#1203), the Helm chart's values/templates (#1204),
          and any raw-Kubernetes-manifest path (#1205) — this node names the concern each of
          those owns and links outward in prose rather than restating their mechanics. Block's
          internal `squareup/sprout-oss` → ECR → `squareup/block-coder-tf-stacks` pipeline
          named in root `CLAUDE.md`'s ecosystem table — outside this checkout, not
          independently verifiable, named only as an existing pointer the way the already-
          merged `architecture-deployment-hosted-topology` node does. A `part-of` edge to a
          broader `operations` capability node — no such node exists yet on the merge branch,
          so there is nothing to point at.
