# Issue #655 — corpus doc: architecture/containers/mobile.md

ALREADY TRUE: node.schema.json and launchpad/docs/corpus/AGENTS.md are merged on
origin/launchpad; `launchpad/docs/corpus/architecture/containers/mobile.md` does not
exist yet (no `architecture/` directory exists in the corpus tree at all yet — this
is the first architecture node).

STEP 1 — gather evidence: read mobile/README.md, mobile/pubspec.yaml,
mobile/lib/shared/{relay,auth,community,security,crypto,deeplink}/*, mobile/lib/main.dart,
mobile/lib/features/pairing/*, and RELEASING.md's Mobile section, to ground the
container's responsibility, technology, interfaces, connected systems, and deployment
story in real source.

STEP 2 — write front matter + body: id `architecture-containers-mobile`, type
`architecture`, status `draft`, origin `launchpad`, audiences `[agent, developer]`,
one evidence entry per substantive claim (FACT for opened sources, INFERENCE where I
reason beyond what's written, none expected as TEAM_KNOWLEDGE here). No
`relationships` — no other corpus node exists yet whose id this could target (the
corpus tree currently holds only AGENTS.md/README.md/standards/*, no sibling
architecture node to point at).

STEP 3 — RUNS HERE: validate with
`python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until exit 0.

STEP 4 — commit: run the corpus unittest suite as the sole prior command to earn the
verification stamp, then commit the plan + new doc together.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
review-adjudicate and the cross-model review pass are deferred to the batch owner's
morning review — not run in this task.

PARALLEL: none — single file, single worktree, no fan-out.

BUDGET: small — one document, no code changes, no test suite beyond the existing
corpus validator/unittest suite.

OPEN: the issue's DoD asks for evidence classified FACT/INFERENCE/TEAM_KNOWLEDGE, but
everything discoverable about the mobile container comes from source I can open
directly (code, README, RELEASING.md) — no GitHub issue/PR/discussion surfaced a claim
that only TEAM_KNOWLEDGE could carry, so this node may end up with zero TEAM_KNOWLEDGE
entries. That's a real property of the evidence, not an omission I'm resolving silently.

LEFT OUT: no relationships (no existing sibling corpus node to target); no per-type
template (none merged yet, per AGENTS.md); no changes to any file outside the plan and
the one target document.
