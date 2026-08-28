# Issue #698 — architecture/principles/subsystem-isolation.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and `launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad`; `launchpad/docs/corpus/architecture/principles/subsystem-isolation.md` does not exist yet.

STEP 1  Gather evidence: read `ARCHITECTURE.md`'s "Key architectural principle" (line 97) and crate dependency diagram, then verify against every named subsystem crate's `Cargo.toml` and actual call sites (`buzz-db`, `buzz-auth`, `buzz-pubsub`, `buzz-search`, `buzz-audit`, `buzz-workflow`, `buzz-relay`). Check for any automated enforcement (`deny.toml`, `Justfile` clippy/CI targets). ← RUNS HERE

STEP 2  [needs 1] Write front matter (schema-valid: id `architecture-principles-subsystem-isolation`, type `architecture`, status `draft`, origin `launchpad`, audiences `[agent, developer, reviewer]`, no `relationships` — no existing merged node is a legitimate target) and the body: the invariant as a MUST/MUST NOT statement, its scope, enforcement points and observable failure behavior, and an honest "current compliance" section reporting what evidence actually shows (including any deviation from the stated principle found in STEP 1).

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until exit 0.

STEP 4  [needs 3] Run the corpus unittest suite as the sole prior command to earn the verification stamp, then commit the plan + document in a separate call, push, and open a draft PR.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. `review-adjudicate` and the cross-model final review pass are deferred to the batch owner's morning review — not run here.

BUDGET: small — one document, no code changes, evidence gathering scoped to ~7 Cargo.toml files and a handful of call sites.

OPEN: The issue's DoD asks for "typed relationships appropriate to the node," but no other corpus node currently merged on `origin/launchpad` is a legitimate `relationships` target for this subject (the four merged nodes — `corpus-agents`, `corpus-readme`, `corpus-standard-confidence`, `corpus-standard-decision-references` — are all governance nodes about the corpus itself, not about Buzz's architecture) — `relationships` is omitted per the schema's own guidance that a target naming an id no loaded node carries is a hard validation error. ARCHITECTURE.md's stated principle ("those subsystems are isolated from each other ... buzz-workflow never calls buzz-pubsub, buzz-search never calls buzz-db") does not fully hold against current code: `buzz-pubsub` depends on and calls `buzz-auth`, and `buzz-workflow` depends on and calls `buzz-db` directly. This is reported as fact in the node's body rather than silently resolved or hidden — it is a real, unresolved gap between documented intent and current implementation, and this task does not own fixing either the code or the stale doc.

LEFT OUT: No relationships to sibling architecture nodes (none merged yet). No claim about `buzz-deletion`, `buzz-conformance`, `buzz-relay-mesh`, `buzz-datastore-tracing`, or other crates absent from ARCHITECTURE.md's principle text and diagram — out of scope for this node. No attempt to fix the `buzz-pubsub`/`buzz-auth` or `buzz-workflow`/`buzz-db` coupling, or to update `ARCHITECTURE.md` itself — that is separate implementation/documentation work, not this corpus-authoring task.
