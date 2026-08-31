# Issue #670: corpus doc — architecture/deployment/kubernetes.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and
`launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad`;
`launchpad/docs/corpus/architecture/deployment/kubernetes.md` does not exist yet.

STEP 1 (RUNS HERE): Gather evidence — read `deploy/charts/buzz/` (README, Chart.yaml,
values.yaml, templates/*.yaml, examples/*.yaml) as the authoritative Kubernetes
deployment automation for Buzz, plus `AGENTS.md`'s ecosystem table for the
external staging-cluster path (`squareup/block-coder-tf-stacks`, not in this repo).

STEP 2: Write front matter (id `architecture-deployment-kubernetes`, type
architecture, status draft, origin launchpad, audiences operator+developer+agent,
evidence ledger with FACT/INFERENCE/TEAM_KNOWLEDGE classified honestly, no
relationships — no sibling architecture/deployment node is merged on
`origin/launchpad` yet) and the body covering the issue's DoD plus the category
tail (topology/execution nodes, container/service/data-store mapping, network/
persistence/trust boundaries, automation-as-authority, failure/recovery).

STEP 3: Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and
re-run until it exits 0.

STEP 4: Earn the verification stamp with the unittest suite, then commit the plan
and the new node in one commit.

PARALLEL: none — single file, single commit.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`review-adjudicate` and the cross-model review pass are explicitly deferred to
the batch owner's morning review — not run in this session.

BUDGET: single session, no iteration expected beyond validator fix-up.

OPEN: the issue's DoD asks the node to describe deployment "without exposing
secrets" and to link automation as authority. The repository's actual production
Kubernetes deployment (Block's staging cluster) is provisioned by
`squareup/block-coder-tf-stacks`, a private repo not present in this checkout —
so this node documents the upstream/OSS Helm chart (`deploy/charts/buzz/`) that
that private pipeline consumes, and says explicitly that the private pipeline's
own manifests were not inspected. This is a real, stated ambiguity in the issue's
DoD (which does not say which of the two layers "the" kubernetes node means), not
one I am resolving silently.

LEFT OUT: `buzz-backend-kubernetes` (the agent-runtime compute backend that
launches remote-agent pods) is a distinct concept — a compute provider for
agents, not the relay's own deployment topology — and is left for its own node
rather than folded in here, per AGENTS.md's "one node is one independently
maintainable idea" rule. `deploy/charts/buzz-push-gateway` (a separate optional
chart) is mentioned only as a pointer, not documented in depth, for the same
reason.
