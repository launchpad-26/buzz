# Plan: issue #669 — corpus doc architecture/deployment/hosted-topology.md

ALREADY TRUE: node.schema.json and launchpad/docs/corpus/AGENTS.md are merged on
`origin/launchpad` (verified at commit a44cf52fc740ebebbdd671427480d14f0bce0115); the
target file `launchpad/docs/corpus/architecture/deployment/hosted-topology.md` does not
exist yet.

STEP 1 — Gather evidence for hosted topology: the Helm chart (`deploy/charts/buzz`,
`deploy/charts/buzz-push-gateway`), its GitOps examples (ArgoCD/Flux), secret/network/
persistence templates, `docs/git-on-object-storage.md`, and top-level `AGENTS.md`'s
Ecosystem table (block-coder-tf-stacks deploys this same chart to Block's staging
cluster). RUNS HERE.

STEP 2 — Write front matter (id `architecture-deployment-hosted-topology`, type
`architecture`, status `draft`, origin `launchpad`, audiences `operator`+`developer`+
`agent`) plus one evidence entry per substantive claim, classified FACT/INFERENCE/
TEAM_KNOWLEDGE per the schema. No `relationships` — no sibling architecture/deployment
node is merged on `origin/launchpad` yet to target.

STEP 3 — Write the body: environment/topology + execution nodes, container/service/
data-store mapping, network/persistence/trust boundaries (no secrets), deployment
automation as authority, failure/recovery implications — per issue #669's DoD checklist
and the category tail.

STEP 4 — Validate (`python3 launchpad/project-intelligence/corpus/validate.py`), run the
corpus unittest suite for the commit stamp, commit, push, open a draft PR.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` must report OK (earns the commit verification stamp). review-adjudicate and
the cross-model review pass are explicitly deferred to the batch owner's morning review —
not run in this session.

BUDGET: single document, single commit, single draft PR. No code changes, no generated
index regeneration expected.

OPEN: the issue's DoD does not say whether "hosted topology" means Block's internal
staging deployment (block-coder-tf-stacks + ArgoCD, external repo, not inspectable from
this checkout) or the OSS Helm chart's own deployment topology (`deploy/charts/buzz`,
in-repo, fully inspectable, and the same chart block-coder-tf-stacks deploys per
AGENTS.md's Ecosystem table). This document covers the latter as the verifiable
authority and states the former as a named gap rather than guessing at Terraform/ArgoCD
internals this checkout cannot see.

LEFT OUT: no change to `deploy/charts/buzz` itself; no attempt to document
`squareup/block-coder-tf-stacks` internals (external repo, unavailable); no second
canonical corpus document.
