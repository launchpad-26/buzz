Issue #674 — task: document architecture/deployment/single-relay.md

ALREADY TRUE  launchpad/docs/corpus/schema/node.schema.json and AGENTS.md are merged at
  origin/launchpad tip a44cf52fc740ebebbdd671427480d14f0bce0115; the target file
  launchpad/docs/corpus/architecture/deployment/single-relay.md is absent (test -f
  confirmed); the merged corpus at this base carries exactly four nodes (README, AGENTS,
  standards/confidence, standards/decision-references) and zero architecture/deployment
  nodes, so no `relationships` target exists to point at.

STEP 1  Gather evidence for the single-relay deployment topology: deploy/compose/*
        (compose.yml, compose.caddy.yml, compose.dev.yml, .env.example, Caddyfile,
        run.sh), launchpad/deploy/run.sh + README.md + AGENTS.md (the guard and the
        archived-method warning), root Dockerfile, deploy/charts/buzz/README.md +
        values.yaml (the Helm chart's single-replica profile, for contrast), the relay's
        health/readiness handlers (crates/buzz-relay/src/router.rs) and BUZZ_AUTO_MIGRATE
        gate (crates/buzz-relay/src/main.rs), and .github/workflows/docker.yml (image
        publish authority). Record commit a44cf52fc740ebebbdd671427480d14f0bce0115.
STEP 2  Write front matter (id: architecture-deployment-single-relay, type: architecture,
        status: draft, origin: launchpad, audiences: [operator, developer], no
        relationships) and the body: topology/execution nodes, container-to-node mapping,
        network/persistence/trust boundaries, deployment automation as authority,
        failure/recovery implications — the category-tail bullets plus the issue's own
        DoD checklist. One evidence entry per substantive claim, FACT only for sources
        actually opened.
STEP 3  Run python3 launchpad/project-intelligence/corpus/validate.py; fix and re-run
        until it exits 0.                                                    ← RUNS HERE
STEP 4  Self-review the diff line-by-line against the issue's DoD + category tail, run
        the corpus unittest suite for the commit-verification stamp, commit, push, open
        a draft PR.

PARALLEL  None — one hand-authored file, sequential steps.

GATES     validate.py must exit 0 (STEP 3). python3 -m unittest discover for the
          verification stamp (STEP 4). review-adjudicate and the cross-model review-final
          pass are explicitly deferred to the batch owner's morning review — not run in
          this worktree.

BUDGET    STEP 1 (evidence gathering) is the long pole — opening every deploy/ config
          file and the relay's health/migration code before drafting a single claim.

OPEN      The repo has two distinct "single-relay" deployment topologies: the
          single-node/VPS Docker Compose bundle (deploy/compose, literally called
          "single-node" in its own README, governed by launchpad/deploy/run.sh for this
          cohort) and the Helm chart's non-HA replicaCount:1 profile for Kubernetes. The
          issue does not say which. This node documents the Compose/VPS bundle as primary
          (it is the deployment path this fork's own guard script targets) and notes the
          Helm chart's single-replica profile as the analogous Kubernetes topology, rather
          than silently picking one and omitting the other.

LEFT OUT  The archived Ansible/VirtualBox deployment method (launchpad/deploy/archived/)
          — explicitly disclaimed as failed and not a source of deployment truth; named
          only as a boundary marker. The private squareup/* pipelines (buzz-releases,
          sprout-oss, block-coder-tf-stacks) named in the repo's top-level AGENTS.md
          ecosystem table — not accessible from this checkout, not cited as evidence.
          Any change to validate.py, the schema, or Helm chart/Compose files themselves.
