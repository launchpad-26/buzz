# Plan: issue #664 — corpus doc: architecture/context/external-services

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` is merged and
authoritative; `launchpad/docs/corpus/AGENTS.md` says write against the schema
and expect a later reshape task; `launchpad/docs/corpus/architecture/context/external-services.md`
does not exist yet.

STEP 1 — gather evidence: read `.env.example`, `docker-compose.yml`,
`scripts/dev-setup.sh`, `crates/buzz-auth/src/lib.rs`, `crates/buzz-media/src/config.rs`,
`crates/buzz-push-gateway/src/{lib,config,apns}.rs`, `crates/buzz-agent/src/config.rs`,
`crates/buzz-core/src/agent_turn_metric.rs`, `crates/buzz-relay-mesh/src/lib.rs`,
`crates/buzz-relay/src/api/git/transport.rs`, `launchpad/docs/Observability/current-state/relay.md`,
and this repo's own `AGENTS.md` Ecosystem table, to identify every external
system/actor Buzz's context boundary actually touches at runtime and in its
delivery pipeline. RUNS HERE.

STEP 2 — write front matter (id `architecture-context-external-services`,
type `architecture`, status `draft`, origin `launchpad`, audiences
`[developer, operator, agent]`) plus a body defining the system boundary,
naming each actor/external system and its relationship to Buzz, a Mermaid
C4-style context diagram, and an explicit scope/omissions section — every
substantive claim backed by a real evidence citation (FACT unless genuinely
inferred).

STEP 3 — run `python3 launchpad/project-intelligence/corpus/validate.py`;
fix and re-run until it exits 0.

STEP 4 — commit (after earning the verification stamp via the corpus
unittest suite) and open a draft PR against `launchpad`.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must
exit 0 locally before commit. `review-adjudicate` and the cross-model
review pass are explicitly deferred to the batch owner's morning review —
not run in this task.

BUDGET: single session, no infra required (read-only repo inspection +
one Markdown file).

OPEN: the issue's DoD does not say whether "external services" should
include Buzz's own inter-pod relay mesh (`buzz-relay-mesh`, QUIC transport
between replicas of the *same* deployment) as a context-level external
system. Resolved here by treating it as internal/container-level (same
system, horizontal scale-out) and excluding it from the context diagram,
per the DoD's own "does not descend into container/component
implementation details" — but this is a real judgment call the issue
itself leaves open, not a settled fact, and is called out explicitly in
the document's scope-and-omissions section.

LEFT OUT: no `relationships` front-matter entries — no sibling corpus node
in this category is confirmed merged at the time of writing, and an
unresolved target id is a hard validation error. No per-type template
exists yet (0 of 26 merged per `AGENTS.md`), so no template conformance
check was attempted.
