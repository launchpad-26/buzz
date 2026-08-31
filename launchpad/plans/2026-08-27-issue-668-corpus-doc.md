# Issue #668: document architecture/deployment/docker-compose.md

ALREADY TRUE: node.schema.json and launchpad/docs/corpus/AGENTS.md are merged on origin/launchpad; launchpad/docs/corpus/architecture/deployment/docker-compose.md does not exist yet.

STEP 1: Gather evidence -- inspect deploy/compose/*.yml, launchpad/deploy/run.sh + AGENTS.md, root docker-compose.yml + docker-compose.harness.yml, .github/workflows/docker.yml, Justfile, .env.example files, and deploy/charts/buzz/README.md to ground every claim.
STEP 2 (RUNS HERE): Write launchpad/docs/corpus/architecture/deployment/docker-compose.md with schema-valid front matter (type: architecture, status: draft, origin: launchpad) and a body covering environment/topology, execution nodes, container-to-node mapping, network/persistence/trust boundaries, and deployment-automation links with failure/recovery implications, per the issue's DoD and the category tail.
STEP 3: Run python3 launchpad/project-intelligence/corpus/validate.py until it exits 0.
STEP 4: Run the corpus unittest suite as the sole prior command to earn the verification stamp, then commit the plan + document in a separate call.

PARALLEL: none -- single file, single agent, no fan-out.

GATES: python3 launchpad/project-intelligence/corpus/validate.py must exit 0. review-adjudicate and any cross-model review pass are explicitly deferred to the batch owner's morning review -- not run in this task.

BUDGET: single document, no code changes, no test suite beyond the corpus validator/unittest gate -- expect well under an hour of agent time.

OPEN: the issue's DoD does not say whether this node should document the dev-only root docker-compose.yml, the deploy/compose/ single-node/VPS production bundle, or both. Both exist and are explicitly documented as distinct in deploy/compose/README.md ("intentionally separate from the root docker-compose.yml, which remains local development infrastructure"). Given the target path is under architecture/deployment/ and the category tail asks for topology, trust boundaries, and failure/recovery of a deployment, this document treats deploy/compose/ as the primary subject and documents the root docker-compose.yml + harness variant as a clearly-scoped secondary section, rather than silently picking one and hiding the other. This is stated as an explicit choice in the node's own Scope and omissions section, not resolved by inventing a rule the issue never stated.

LEFT OUT: the Kubernetes/Helm production path (deploy/charts/buzz, squareup/block-coder-tf-stacks) is named as a sibling deployment surface but not documented here -- it is a separate node's job. The archived, failed Launchpad VPS deployment method (launchpad/deploy/archived/) is referenced only as a documented failure precedent, not described in detail.
