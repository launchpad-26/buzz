# Issue #656: document architecture/containers/object-storage.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and
`launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad`;
`launchpad/docs/corpus/architecture/containers/object-storage.md` does not exist yet
(no `architecture/` directory exists in the corpus at all — this is the first node
of that type).

STEP 1 (RUNS HERE): Gather evidence for the object-storage container's
responsibility, technology, inbound/outbound interfaces, and directly connected
containers/systems by reading `crates/buzz-media/**` (storage, auth, validation,
config, bucket taxonomy), `crates/buzz-relay/src/api/media.rs`,
`crates/buzz-relay/src/api/git/store.rs` (the git-on-object-storage CAS client,
which shares the S3 config type but not the `MediaStorage` client instance),
`crates/buzz-relay/src/storage_sweep.rs`, `crates/buzz-relay/src/router.rs`
(route wiring), `ARCHITECTURE.md`, `.env.example`, `deploy/charts/buzz/README.md`
and `docker-compose.yml` (deployment), and `docs/git-on-object-storage.md` (the
CAS design spec). Record every claim's real citation as it is read.

STEP 2: Write the node's front matter (id
`architecture-containers-object-storage`, type `architecture`, status `draft`,
origin `launchpad`, audiences `developer`/`operator`/`agent`, one evidence entry
per claim, classified honestly) and body against `node.schema.json` and the
category tail (responsibility/technology/ownership boundary; inbound/outbound
interfaces and directly connected containers; deployment/data/security
implications; implementation links without duplicating reference detail).

STEP 3: Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
repo root and fix anything it flags until it exits 0.

STEP 4: Earn the commit verification stamp with
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole prior command, then commit the plan and the new node together.

PARALLEL: none — this is a single hand-authored file plus this plan document.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
against the full corpus tree including the new node before committing. The
review-adjudicate pass and the cross-model final review are explicitly deferred
to the batch owner's morning review and are not run in this session — the PR is
opened as a draft for that reason.

BUDGET: single document, one sitting — no more than a handful of read/write/test
tool-call rounds beyond this plan.

OPEN: block-coder-tf-stacks (the private repo that provisions the staging
Kubernetes deployment via Terraform + ArgoCD, per this repo's own `AGENTS.md`) is
not available in this checkout, so what it actually provisions for object storage
in staging cannot be verified here and is named as a gap in the node's own
scope-and-omissions section rather than guessed at.

LEFT OUT: no second node, no edits to any file outside
`launchpad/docs/corpus/architecture/containers/object-storage.md` and this plan
file. No `relationships` are declared — the merged corpus on `origin/launchpad`
has no other `architecture`-typed sibling yet to point at (verified via
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`), and the
node explains that choice rather than reusing prior nodes' boilerplate.
