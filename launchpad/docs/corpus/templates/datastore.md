---
id: corpus-template-datastore
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "A node's front matter is validated against node.schema.json, whose type enum is architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion, and contains no template or policy value."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Every other corpus meta-document at the recorded revision — AGENTS.md excepted, which is type: agent — uses type: governance: README.md, standards/confidence.md and standards/decision-references.md all do."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "schema/README.md and schema/COMPATIBILITY.md were both read in full while choosing this node's type, and neither names a template-specific or policy-specific value beyond what node.schema.json's own field table already states."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/README.md"
      - "launchpad/docs/corpus/schema/COMPATIBILITY.md"
  - statement: "This node is a meta-document about how to author a corpus node, not itself a datastore's schema or operational profile, so governance is chosen by the same reasoning corpus-readme and the sibling architecture-container and architecture-component templates already recorded for their own type choices, rather than as an independent precedent this node invents."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/README.md"
    confidence: 0.6
  - statement: "A corpus node instance actually written from this template — a real datastore document about a real system's Postgres, Redis, or object-storage instance — most plausibly takes type: architecture, the same enum member the sibling architecture-container (#1327, PR #1529) and architecture-component (#1326, PR #1528) templates each independently direct their own real instances to use, on the same grounds those two templates give: node.schema.json offers no finer-grained member distinguishing a container-, component-, or datastore-level structural view from one another, so all three share the single surface value."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.6
  - statement: "Issue #1327's architecture-container template pull request (#1529, open and unmerged at the recorded revision) states, in its own worked container-identity table, that 'a Postgres or Redis instance the system requires to run is a container in the C4 sense (a data store that has to be running), even though nobody in this repository writes its code — \"container\" describes a runtime boundary, not authorship' — establishing, as existing corpus precedent, that this repository's own datastores are already documented as one row of an architecture-container inventory (existence, technology, one-line responsibility, one-line communication edge), which this template's own boundary section builds on rather than re-argues."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1529 (open PR, corpus-template-architecture-container), read directly via gh pr view and gh api contents"
  - statement: "Issue #1326's architecture-component template pull request (#1528, open and unmerged at the recorded revision) states its own boundary against architecture-container as: 'Container is the set of deployable/runnable units (services, databases, apps) and their technology choices. A component-level node documents the inside of exactly one of those units' — confirming that neither existing template goes deeper into a datastore container's own internal shape (schema, access patterns, operational characteristics); that gap is this template's reason to exist."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1528 (open PR, corpus-template-architecture-component), read directly via gh pr view and gh api contents"
  - statement: "The C4 model's container-abstraction primary source defines a container as 'a runtime boundary around some code that is being executed or some data that is being stored,' and its own worked list of container examples includes, verbatim: 'Database: A schema or database in a relational database management system, document store, graph database, etc such as MySQL, Microsoft SQL Server, Oracle Database, MongoDB, Riak, Cassandra, Neo4j, etc'; 'Blob or content store: A blob store (e.g. Amazon S3, Microsoft Azure Blob Storage, etc) or content delivery network'; and 'File system: A full local file system or a portion of a larger networked file system (e.g. SAN, NAS, etc)' — three of the ten worked container-example categories on that page, alongside the code-executing ones (server-side/client-side application, mobile app, serverless function, shell script, and so on)."
    entry_class: FACT
    evidence:
      - "https://c4model.com/abstractions/container"
  - statement: "The C4 model's diagrams overview page names exactly four core (hierarchical) diagram types — system context, container, component, code — and three supplementary diagram types — system landscape, dynamic, deployment — and names no 'Data Store' or 'Database' diagram type anywhere on that page; 'Database' exists in the C4 vocabulary only as one of the Container abstraction's worked example categories, not as its own diagram tier. This was checked directly rather than assumed, because the batch dispatch brief for this task named a 'Data Store pattern in the C4 model's supplementary diagrams' as a candidate to verify, and no such pattern exists at the primary source."
    entry_class: FACT
    evidence:
      - "https://c4model.com/diagrams"
  - statement: "The Twelve-Factor App's Factor IV ('Backing services') defines a backing service as 'any service the app consumes over the network as part of its normal operation,' names datastores (MySQL, CouchDB are its own examples) as backing services, and states 'the code for a twelve-factor app makes no distinction between local and third party services' — both are 'attached resources, accessed via a URL or other locator/credentials stored in the config' — such that swapping a local database for a third-party managed one 'would require only a change to the app's config.'"
    entry_class: FACT
    evidence:
      - "https://12factor.net/backing-services"
  - statement: "Relationships must resolve against the corpus tree on the branch being merged into, and at the recorded revision origin/launchpad's launchpad/docs/corpus tree carries exactly four validated content nodes: AGENTS.md (corpus-agents), README.md (corpus-readme), standards/confidence.md (corpus-standard-confidence) and standards/decision-references.md (corpus-standard-decision-references); schema/ is present but excluded from validation."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> AGENTS.md, README.md, standards/confidence.md, standards/decision-references.md; schema/ present but excluded from validation"
  - statement: "None of the four existing content nodes has datastores, schemas, Postgres, Redis, or backing services as its subject, so no relationships.target among them would be a substantive edge rather than a citation duplicate of what this node's evidence ledger already cites directly."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
    confidence: 0.8
  - statement: "crates/buzz-db/Cargo.toml describes buzz-db as 'Postgres event store and data access layer for Buzz,' and crates/buzz-search/Cargo.toml describes buzz-search as 'Postgres full-text search for Buzz, scoped by community' — both are library crates (src/lib.rs, no [[bin]] target), linked into buzz-relay's binary, that read and write one shared Postgres instance rather than being that instance themselves."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/Cargo.toml"
      - "crates/buzz-search/Cargo.toml"
  - statement: "crates/buzz-pubsub/Cargo.toml describes buzz-pubsub as 'Redis pub/sub fan-out, presence, and typing indicators for Buzz,' depends on the redis and deadpool-redis crates, and is itself a library crate with no [[bin]] target — the same 'data-access code linked into the container, not a container itself' shape architecture-container's own worked table already establishes for buzz-db."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/Cargo.toml"
  - statement: "crates/buzz-media/Cargo.toml describes buzz-media as 'Media storage, validation, and thumbnail generation for Buzz,' and .env.example's S3-Compatible Object Storage section states 'the local MinIO container is reachable from host processes at localhost:9000' and is used for 'media + Git/CAS' — a blob-store-backed datastore in the C4 sense (Amazon S3 is the primary source's own worked example of that category), distinct from both the Postgres and Redis instances."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/Cargo.toml"
      - ".env.example"
  - statement: "Root CLAUDE.md's Repo Structure table describes crates/buzz-relay as the 'WebSocket relay server — main entry point; also hosts git + huddle audio,' meaning the second accessor of the S3-compatible object store named in .env.example's 'media + Git/CAS' comment (the Git smart-HTTP / content-addressable-storage path) lives inside buzz-relay itself rather than in a separate crate the way media access lives in buzz-media."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: ".env.example's Database section sets DATABASE_URL to a postgres:// connection string and separately documents an optional READ_DATABASE_URL for 'an optional read-replica URL; unset/blank keeps all reads on the writer,' and crates/buzz-db/src/lib.rs contains a read_session_query_events method under a #[datastore_span(name = \"read_session_query_events\", system = \"postgresql\")] attribute — a read/write split that exists as a live code path, not merely a documented intention."
    entry_class: FACT
    evidence:
      - ".env.example"
      - "crates/buzz-db/src/lib.rs"
  - statement: "crates/buzz-db/src/runtime/migration.rs embeds a static sqlx::migrate!(\"../../migrations\") MIGRATOR, and its run_migrations function's doc comment states the entire run holds an exclusive SCHEMA_DESTRUCTION_LOCK_KEY session lock, serializing schema changes against destructive-deletion transactions, and that 'a source lint (migration_execution_cannot_bypass_schema_destruction_lock) enforces that MIGRATOR.run has no other call site' — a single, guarded entry point for schema evolution, not an unenforced convention."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "The migrations/ directory at the repository root contains 31 sequentially numbered SQL files at the recorded revision (0001_initial_schema.sql through 0031_workflow_run_error_codes.sql), applied in that numeric order by the embedded migrator above; root CLAUDE.md's Repo Structure table independently describes this directory as 'SQL migrations (auto-applied on relay startup).'"
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "migrations/0031_workflow_run_error_codes.sql"
      - "CLAUDE.md"
  - statement: "crates/buzz-datastore-tracing/Cargo.toml describes itself as 'Privacy-preserving datastore tracing policy macros for Buzz,' and its lib.rs exposes a #[datastore_span(name = ..., system = ...)] proc-macro attribute whose doc comment states it 'instruments an async logical datastore operation according to Buzz policy' so that 'PostgreSQL spans always omit function arguments, use the buzz_datastore target, and expose only canonical semantic fields plus explicitly supplied safe fields' — this repository already has its own load-bearing 'datastore' vocabulary at the code level, independent of and prior to this corpus template."
    entry_class: FACT
    evidence:
      - "crates/buzz-datastore-tracing/Cargo.toml"
      - "crates/buzz-datastore-tracing/src/lib.rs"
  - statement: "Every use of the #[datastore_span] attribute across the repository at the recorded revision (in crates/buzz-db, crates/buzz-audit, crates/buzz-search, and crates/buzz-relay's command_executor.rs) sets system = \"postgresql\"; no call site sets system to a Redis- or object-storage-identifying value, and crates/buzz-pubsub (the Redis crate) does not import or use datastore_span at all — a real, checked gap between the repository's three live datastores and its own datastore-tracing instrumentation, which currently covers Postgres only, named here rather than silently smoothed over. This is not merely unexercised: crates/buzz-datastore-tracing/src/lib.rs's macro implementation itself rejects any other `system` value at compile time (\"unsupported datastore system; only `postgresql` is currently supported\"), so the gap is an enforced, deliberate restriction today, not an oversight this node could resolve by reading further."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
      - "crates/buzz-db/src/runtime/replica_fence.rs"
      - "crates/buzz-audit/src/service.rs"
      - "crates/buzz-search/src/query.rs"
      - "crates/buzz-relay/src/handlers/command_executor.rs"
      - "crates/buzz-pubsub/src/lib.rs"
      - "crates/buzz-datastore-tracing/src/lib.rs"
  - statement: ".env.example's Typesense section still sets TYPESENSE_API_KEY and TYPESENSE_URL and lists Typesense as one of the 'Service ports (defaults)' at the top of the file, but crates/buzz-relay/src/handlers/event.rs contains the comment 'the old Typesense index_event worker and its search_index_tx mpsc are gone with the Typesense backend,' and crates/buzz-search/src/query.rs's own doc comment describes matching a prior 'Typesense relay' matrix rather than using Typesense itself — a live discrepancy between .env.example's still-present Typesense variables and the actual search datastore (Postgres FTS, per buzz-search's own Cargo.toml description), not resolved by this node."
    entry_class: FACT
    evidence:
      - ".env.example"
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-search/src/query.rs"
  - statement: "Issue #605 (parent PRD) states the real acceptance criterion for every template task in this batch as: every template states its purpose, required sections, evidence expectations and the industry model/standard it adapts — distinct from the byte-identical MUST/SHOULD/enforcement/policy checklist copied into this node's own issue #1334 from the standards-track issues."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 (parent PRD), opened directly via gh issue view"
  - statement: "Issue #1334's definition of done otherwise requires one hand-authored canonical document, schema-valid front matter, one independently maintainable idea, traceable FACT/INFERENCE/TEAM_KNOWLEDGE claims, links instead of duplicated content, a check against the recorded provenance revision, and a clean validator run."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1334 definition of done, opened directly via gh issue view"
  - statement: "Issue #1467 records that the cross-model (Codex) review provider is currently unavailable — the Codex workspace is out of credits, confirmed twice including with a trivial read-only prompt, and no other external-model CLI (gemini, agy, pi, llm, ollama, cursor-agent, opencode) is installed — so a same-model adversarial self-review is the substitute this node's own review pass used."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1467, opened directly via gh issue view"
---

# Template: datastore

How to write a corpus node whose subject is one **datastore** — a single running
technology instance (a Postgres database, a Redis instance, an S3-compatible object
store) that another container already inventories as one row of its own
architecture-container document: what the datastore's own internal shape is (its
schemas or namespaces, at a structural level), how schema changes are made and
ordered, how other containers reach and use it, and what operational characteristics
its own technology gives it. This node is the template itself, not an instance of
one: it states what a datastore node must contain, not a datastore document for any
real system.

## Scope and authority

**This node covers** the purpose of a datastore document, the sections it must
contain, what evidence each section needs, and the industry model it adapts (the C4
model's Container abstraction, specifically its "data that is being stored" half,
read together with the Twelve-Factor App's Backing Services factor). It does not
itself document any real system's datastore in full, beyond one illustrative, scoped
worked example.

**A note on this issue's own definition of done.** Issue #1334's checklist carries a
MUST/SHOULD/enforcement/exception block copied verbatim from the standards-track
issues that produced `standards/confidence.md` and `standards/decision-references.md`
— documents whose subject is a normative policy. This node's subject is a template,
and the parent PRD (#605) states the acceptance bar that actually applies to a
template task: *every template states its purpose, required sections, evidence
expectations and the industry model/standard it adapts.* This document is built
against that sentence. The rest of #1334's checklist — one hand-authored document,
schema-valid front matter, one independently maintainable idea, traceable claims,
links instead of duplication, a check against the recorded revision, a clean
validator run — is generic to any corpus node and is honoured below regardless. This
is the same note the sibling architecture-container (#1327, PR #1529) and deployment
(#1336, PR #1536) templates record for the identical stale-checklist problem.

**Its authority is derived, not original.** `node.schema.json` is the front-matter
law; `AGENTS.md` is the create/update/retire procedure; `standards/confidence.md` and
`standards/decision-references.md` are the two evidence-mechanics standards merged so
far. This document adds nothing to any of those. What it adds is the part none of
them can: what a *datastore-scoped* node must say, and where that shape comes from.

**A note on this template's own `type`, versus a real instance's.** This document is
`type: governance` because it is a meta-document about how to author a node, not a
datastore's schema itself — the same reasoning `corpus-readme`, the architecture-
container template (#1327), and the architecture-component template (#1326) already
apply to themselves. A real instance written *from* this template — an actual
Postgres or Redis instance's own document — most plausibly takes `type: architecture`
instead, the same enum member those two sibling templates independently direct their
own real instances to use, on the grounds their own evidence ledgers give: no
finer-grained enum member exists to distinguish a container-, component-, or
datastore-level structural view from one another.

| For | Read |
|---|---|
| The front-matter contract | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| Evidence classes and citation shapes | `launchpad/docs/corpus/AGENTS.md`, `launchpad/project-intelligence/CONTRACT.md` §3 |
| Relationship types and directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| The boundary this node draws against, primary source | `launchpad-26/buzz#1529` (architecture-container template), `launchpad-26/buzz#1528` (architecture-component template) |
| C4 model, primary source | `https://c4model.com/abstractions/container`, `https://c4model.com/diagrams` |
| Twelve-Factor App, primary source | `https://12factor.net/backing-services` |

If this file and any of those disagree, **they win** — this one has drifted and
should be fixed.

## Purpose

A datastore node exists to answer one question for a reader who already knows a
system's containers (its architecture-container document, if one exists) and already
knows this particular one is a data store rather than an application: ***what does
this datastore actually look like on the inside, how does its shape change over
time, and who is allowed to touch it, how?*** It is not a second container inventory
— it takes the container-level fact "this thing exists and is a Postgres database"
as given, from the architecture-container document, and adds the axis that document
deliberately keeps to one line: the datastore's own schema or namespace structure,
its migration mechanism, its access patterns, and its operational characteristics. It
is also not a domain model — it does not describe *what the data means*, only *where
it lives and how it is reached*.

**The failure this template exists to prevent.** Left unscoped, a datastore document
drifts in one of three directions: back into container territory (re-describing that
the datastore exists and what technology it uses — the architecture-container
document's job, not this one's), sideways into domain-model territory (re-describing
what a Nostr event or a channel *is* — the data-entity template's job, #1333, not this
one's), or forward into environment territory (how many replicas run in production,
whether the instance is externally managed — the deployment template's job, #1336,
not this one's). All three drifts produce a document that is not wrong so much as
mis-shelved. The sections below exist to keep those three concerns out.

## The industry model this adapts

**C4 model, Container abstraction — the data-storage half of it** (Simon Brown,
`https://c4model.com/abstractions/container`, undated — no version number published).
The primary source defines a container, in full, as "a runtime boundary around some
code that is being executed or some data that is being stored" — one definition
covering two different kinds of thing. Its worked list of container *examples*
enumerates ten categories; three of them are the data-storage half this template is
about, quoted verbatim: **Database** ("A schema or database in a relational database
management system, document store, graph database, etc such as MySQL, Microsoft SQL
Server, Oracle Database, MongoDB, Riak, Cassandra, Neo4j, etc"), **Blob or content
store** ("A blob store (e.g. Amazon S3, Microsoft Azure Blob Storage, etc) or content
delivery network"), and **File system** ("A full local file system or a portion of a
larger networked file system (e.g. SAN, NAS, etc)"). The primary source does not
prescribe a distinct diagram type or notation for these — they remain boxes on the
same Container diagram as any code-executing container, distinguished only by an
author's own chosen shape or label, per the model's own stated notational
independence.

**A "Data Store" C4 diagram pattern was checked for and does not exist.** The batch
dispatch brief for this task named a "Data Store pattern in the C4 model's
supplementary diagrams" as a candidate worth verifying before citing. The C4 diagrams
overview page names exactly four core diagram types (system context, container,
component, code) and three supplementary ones (system landscape, dynamic,
deployment); neither "Data Store" nor "Database" appears anywhere on that page as a
diagram type. "Database" exists in the C4 vocabulary only as one of the Container
abstraction's worked *example categories*, quoted above — not as a diagram tier, and
not as anything with its own notation guidance. This template's required sections,
below, are this template's own synthesis of what a reader needs to trust a datastore
document, the same role the sibling architecture-container and deployment templates
play for their own diagram types — except here there is no diagram type to adapt in
the first place, only the abstraction's own two-sentence definition.

**Twelve-Factor App, Factor IV — Backing Services** (Adam Wiggins et al.,
`https://12factor.net/backing-services`, version-controlled on GitHub, no dated
release cited on the page itself). The primary source defines a backing service as
"any service the app consumes over the network as part of its normal operation," and
names datastores (MySQL, CouchDB are its own worked examples) as backing services. Its
central claim: "the code for a twelve-factor app makes no distinction between local
and third party services. To the app, both are attached resources, accessed via a URL
or other locator/credentials stored in the config." Swapping a local database for a
managed one "would require only a change to the app's config." This is the source for
this template's *access* framing: a datastore document states that the application
reaches this datastore through an externalized, config-driven attachment point (a URL,
a set of credentials) — a fact true in every environment — without stating what that
attachment point's value actually is in any one environment, which is a different,
per-environment fact this template does not own.

**Both sources are read together, not merged into one.** C4 answers "what is this
thing, structurally" (a container whose runtime boundary is around stored data). Factor
IV answers "how is it attached" (as an interchangeable, config-addressed resource, not
a hardcoded dependency). Neither source, alone, gives a datastore document its own
required sections; this template synthesizes the two into the sections below.

## The boundary against architecture-container (#1327) and architecture-component (#1326)

Issue #1327's already-open architecture-container template (PR #1529) states the
boundary this node inherits rather than re-derives, in its own worked container-
identity table: "a Postgres or Redis instance the system requires to run is a
container in the C4 sense (a data store that has to be running), even though nobody
in this repository writes its code — 'container' describes a runtime boundary, not
authorship." That template documents a datastore's *existence*, its *technology name*,
and a *one-line responsibility and one-line communication edge* — exactly as much
detail as any other row in a container inventory gets, no more.

Issue #1326's architecture-component template (PR #1528) states its own boundary
against architecture-container directly: "Container is the set of deployable/runnable
units (services, databases, apps) and their technology choices. A component-level node
documents the **inside** of exactly one of those units." That statement is written
about code-executing containers — the internal shape it describes is classes, modules,
and functions. A datastore container's internal shape is not classes and modules; it is
schemas, tables or keyspaces, indexes, and a migration mechanism. Architecture-component
does not claim to cover this, and this template fills that specific gap: the same "zoom
into one container's inside" move architecture-component makes, applied to a container
whose inside is stored data rather than executed code.

**The practical test:** a datastore document and a container-inventory row disagree
only in *depth*, not in subject. If a fact is true at the level "this datastore exists
and this is roughly what it's for" (its name, its technology, that some container talks
to it), it belongs in the architecture-container document, not here. If a fact requires
opening the datastore's own schema, migration files, or access code to state correctly
(what tables/keyspaces exist, how migrations are ordered and guarded, which specific
methods read or write it and under what tracing policy), it belongs here.

## Boundary against data-entity (#1333)

**Not yet drafted at this node's authoring time** — #1333 is being authored in
parallel, by a different agent, in the same batch as this node, and no PR for it
exists yet. This boundary is therefore stated from the batch dispatch brief's own
framing and from first principles, not from reading #1333's actual text, and should be
re-checked once #1333 lands.

**The distinction the brief states, and this node adopts:** a data entity is a domain
concept or model — a Nostr event, a channel, a message thread — the *meaning* of the
data, independent of where it happens to be persisted. A datastore is the storage
technology holding it — Postgres, Redis — the *mechanism*, independent of what the
data means. The same domain entity can, in principle, move between storage
technologies without changing what it *is*; the same datastore can, in principle, hold
different domain entities without changing what it *is*. That symmetry is the
practical test: if a fact would still be true were this data moved to a different
storage technology entirely, it is a data-entity fact, not a datastore fact. If a fact
would still be true even if the data stored were completely different in meaning, it
is a datastore fact, not a data-entity fact.

**Applied to this repository:** "a channel's membership is represented by kind:39002
events, addressed by a `d` tag" is a data-entity fact — true regardless of whether
that event is stored in Postgres, SQLite, or a document store. "The `events` table is
partitioned, and partition creation triggers a floor check on `created_at`" is a
datastore fact — true regardless of what domain meaning any given row carries. A
datastore document's required *schema/namespace inventory* section (below) names
table or keyspace names and, at most, a one-line structural purpose for each — it does
not attempt the domain-level description a data-entity node owns, and it links to the
relevant data-entity node instead of restating what the table's rows *mean*.

## Boundary against deployment (#1336, PR #1536)

Issue #1336's already-open deployment template (PR #1536, its actual diff read in
full before drafting this section, per the coordinate-don't-restate pattern batch 2
used successfully) documents "where does each [container] actually run, in which
environment, and what changes between environments" — physical/environment mapping.
Its own required sections include an "Environment inventory" naming, per environment,
"whether dependencies are external/managed or bundled/in-cluster, how secrets are
provisioned," and a "Container-to-infrastructure mapping" naming, per container per
environment, "which deployment node it runs on, how many instances." A datastore, being
one of the container rows deployment.md's own worked illustration explicitly excludes
(it maps `buzz-relay`, not Postgres or Redis themselves, though the same treatment
would apply to either), is exactly the kind of container a real deployment document
would map across environments.

**The practical test, inherited from deployment's own test against architecture-
container and applied identically here:** would this fact about the datastore still
be true regardless of which environment is being described? "This datastore is reached
through an externalized URL, never a hardcoded address" (Factor IV, above) is true in
every environment — a datastore fact. "In local development this URL points at a
Docker Compose Postgres container; in production it points at an externally managed
instance" is true in one environment and false in another — a deployment fact, not a
datastore fact, even though both facts are about the *same* Postgres instance's
connection string. A datastore document states the shape of the attachment point (a
URL, credentials, a pool-size setting); a deployment document states what that
attachment point's value actually is, per environment. Replica *count*, whether the
instance is externally managed, and secret-provisioning particulars are deployment
facts by this same test; that a read-replica *code path exists at all* (this
repository's `READ_DATABASE_URL` and `read_session_query_events`, cited below) is a
datastore fact, because it is true regardless of whether any environment currently
sets that variable.

## Required sections

A datastore node MUST contain the following, in this order. ("MUST" here is this
template's own requirement for the shape of an instance node, not a restatement of any
MUST/SHOULD normative-policy framework — this document is a template, not a standard,
per the *Scope and authority* note above.)

1. **Purpose & scope statement.** One paragraph naming the datastore this document
   covers (its technology and the container id it is one row of, if an
   architecture-container node exists), stating explicitly that this is a
   datastore-level view — the storage technology's own internal shape and access
   surface, not the domain data it holds (data-entity's job) and not where it
   physically runs per environment (deployment's job). Name the sibling
   architecture-container node this document zooms into, and any sibling data-entity
   node(s) it defers to for domain content.

2. **Technology & attachment profile.** What the datastore's underlying technology is
   (product and major version, e.g. "Postgres 17"), and how the application attaches
   to it per Factor IV's framing: the shape of the connection surface (a URL-style
   connection string, discrete host/port/credential variables, or both), and any
   pooling or concurrency limit the application itself imposes. This section states
   the *shape* of the attachment, not any one environment's actual value for it — see
   the boundary against deployment, above.

3. **Schema / namespace inventory.** A structural list only — one row per top-level
   structure (a table, a keyspace, an object-store bucket or prefix convention, an
   index), naming it and giving
   a one-line *structural* purpose (what kind of thing lives here), explicitly not a
   domain-level description of what the data means. Link to the relevant data-entity
   node(s) for domain content instead of restating it — see the boundary against
   data-entity, above.

4. **Migration / schema-versioning mechanism.** How schema changes are authored,
   ordered, applied, and guarded: what tool or mechanism runs them, what enforces
   ordering, whether concurrent schema changes are prevented and how, and whether
   destructive changes are treated differently from additive ones.

5. **Access-pattern summary.** Which containers or components read and write this
   datastore, by what mechanism (a driver, a client library, a connection pool), and
   under what tracing or instrumentation policy, if the codebase has one. This is one
   level more detail than the container-inventory document's one-line communication
   edge — it is the table that turns "buzz-relay talks to Postgres" into prose a
   reader can verify against the actual call sites.

6. **Operational characteristics the technology itself provides.** Replication or
   read-scaling mechanisms the *codebase* actually uses (not merely what the
   underlying technology is capable of in the abstract), retention or TTL policies
   enforced at the datastore level, and any documented backup or durability posture
   this repository's own code or configuration establishes. Whether a given
   environment actually turns on a given mechanism is deployment's fact, not this
   section's — this section states that the mechanism exists and is wired into the
   codebase, citing the code path.

7. **Scope and omissions**, per `AGENTS.md`'s own required shape for this section:
   what this document does not cover and who owns it (the container's own identity
   and technology name → the architecture-container template, #1327; the domain
   meaning of the data stored → the data-entity template, #1333; where this instance
   actually runs, per environment → the deployment template, #1336), and — separately
   — anything expected to verify while drafting this node and unable to.

## What counts as a datastore, a data-access component, and a data entity

**The datastore/component test, from the C4 primary source's own definition:** is
this a runtime boundary around *stored data*, or code that talks to one? Postgres
itself, Redis itself, and the S3-compatible object store itself are datastores by this
test. `buzz-db`, `buzz-search`, and `buzz-pubsub` are not — each is a library crate
(`src/lib.rs`, no `[[bin]]` target) that is data-access *code*, linked into
`buzz-relay`'s binary, the same "component within a container, not a second container"
shape architecture-container's own worked table already establishes for `buzz-db`
specifically.

**The datastore/data-entity test, from the boundary section above:** would this fact
survive a change of storage technology (data-entity) or a change of data meaning
(datastore)?

**A worked, evidence-checked illustration from this repository** (illustrative only —
not a claim that this is Buzz's authoritative or complete datastore inventory, which is
future work for whoever writes that instance node, not this template):

| Datastore | Technology | Accessed by (component, not container) | Notes |
|---|---|---|---|
| The event/data store | Postgres 17 (`postgres:17-alpine` in `docker-compose.yml`) | `buzz-db` (event store, users, channels, moderation, and more), `buzz-search` (full-text search) | `DATABASE_URL` and optional `READ_DATABASE_URL` in `.env.example`; migrations under `migrations/`, applied by the embedded `sqlx::migrate!` in `crates/buzz-db/src/runtime/migration.rs`. |
| The pub/sub and presence store | Redis 7 (`redis:7-alpine` in `docker-compose.yml`) | `buzz-pubsub` (fan-out, presence, typing indicators) | `REDIS_URL` and `BUZZ_REDIS_POOL_SIZE` in `.env.example`, via the `redis` and `deadpool-redis` crates. Not instrumented by `#[datastore_span]` at the recorded revision — see below. |
| The media / Git-CAS object store | S3-compatible (MinIO locally, per `.env.example`'s `BUZZ_S3_ENDPOINT`) | `buzz-media` (media storage, validation, thumbnails); `buzz-relay` itself for the Git smart-HTTP/CAS path, per root `CLAUDE.md`'s crate map ("also hosts git + huddle audio") | `BUZZ_S3_ENDPOINT`, `BUZZ_S3_ACCESS_KEY`, `BUZZ_S3_BUCKET` and related variables in `.env.example`. |

**One real discrepancy surfaced and deliberately left unresolved.** `.env.example`
still sets `TYPESENSE_API_KEY` and `TYPESENSE_URL` and lists Typesense among its
documented service ports, but `crates/buzz-relay/src/handlers/event.rs` states in a
code comment that "the old Typesense `index_event` worker and its `search_index_tx`
mpsc are gone with the Typesense backend," and `buzz-search`'s own `Cargo.toml`
describes it as Postgres, not Typesense, full-text search. Whether `.env.example`'s
Typesense section is stale documentation of a removed datastore, or a partially
completed removal, was not established while drafting this node — named here as a gap
rather than silently resolved either way.

**A second real gap, of the instrumentation kind rather than the configuration kind —
and one this node could resolve rather than merely name.** Every `#[datastore_span]`
call site in this repository at the recorded revision (across `buzz-db`, `buzz-audit`,
`buzz-search`, and one handler in `buzz-relay`) sets `system = "postgresql"`; none
names Redis or the object store, and `buzz-pubsub` does not import `datastore_span` at
all. This repository's own datastore-tracing policy — built specifically to
instrument "logical datastore operations," per its crate's own doc comment —
currently covers one of this repository's three live datastores. Unlike the Typesense
discrepancy above, this one is not an open question: `buzz-datastore-tracing`'s own
macro implementation rejects any `system` value other than `"postgresql"` at compile
time, with the error message "unsupported datastore system; only `postgresql` is
currently supported." The restriction is enforced and deliberate today, not an
oversight — whether it stays that way is a decision for whoever next wires up Redis or
object-storage tracing, not something left ambiguous by this node.

## Evidence expectations

Every row in the schema/namespace inventory, the access-pattern summary, and the
operational-characteristics section is a claim, and needs the same evidence-ledger
treatment `AGENTS.md` requires of any corpus node — classified honestly, not defaulted
to `FACT`:

- **A schema or namespace structure's existence** is a `FACT` when it cites the actual
  schema-defining artifact: a migration file, a `CREATE TABLE`/`CREATE INDEX`
  statement, a Redis key-naming convention enforced in code, an S3 bucket/prefix
  constant. Do not cite a README's prose description of the schema alone —
  descriptions drift; the migration or the code that constructs the key is what
  actually runs.
- **The migration mechanism's behavior** (ordering, locking, guard rails) is a `FACT`
  when it cites the code that implements it, as this node's own evidence ledger does
  for `crates/buzz-db/src/runtime/migration.rs` — not a comment elsewhere describing what the
  mechanism is believed to do.
- **An access-pattern claim** (which component reads or writes this datastore, and
  how) is a `FACT` when it cites the client/driver code that makes the call — a
  function under a tracing attribute, a query method, a pool acquisition — not a
  container-level diagram from another document repeated at higher resolution.
- **A datastore's future or planned schema, or a migration not yet written** is
  `TEAM_KNOWLEDGE` attributed to the issue, PR, or decision that intends it, never
  `FACT`.
- **An operational mechanism's presence versus whether any environment enables it** is
  frequently a judgement call in a repository with no single "this is our production
  Postgres" document to check against. Where it is a judgement call, it is an
  `INFERENCE` with `confidence`, and the reasoning must be visible per
  `standards/confidence.md`'s Requirement 4 — not asserted as settled fact.
- **Infrastructure this repository does not itself configure** — a managed cloud
  datastore whose provisioning lives in a different repository — cannot be a `FACT`
  cited to a file this repository's checker can open, the same limit deployment.md's
  evidence-expectations section already states for infrastructure generally.

**This template does not restate the FACT/INFERENCE/TEAM_KNOWLEDGE contract itself,
`confidence`'s meaning, or the citation shapes.** `AGENTS.md` and
`standards/confidence.md` own those, and a second copy here would be exactly the
drift-prone duplication `AGENTS.md` warns against.

## Relationships an instance node should consider

This template's own front matter declares none (see *Scope and omissions* below), but
an instance node written from this template usually has real edges to declare once its
siblings exist:

- **`part-of`**, authored by the datastore document, targeting the architecture-
  container node whose inventory row is this datastore, once that node exists and is
  merged. This mirrors the architecture-component template's own reasoning for the
  identical situation (zooming into one container's inside): `part-of`'s schema
  directionality — "source is a constituent section/child of target" — is the closest
  match among the five defined types to a datastore's strict containment inside one
  container-level entry.
- **`references`**, authored by the datastore document, targeting any data-entity
  node(s) describing the domain data this datastore holds. This is the correct
  direction and the correct type: `references`'s stated directionality — "source cites
  target as supporting context; no ownership or currency dependency implied" — matches
  a datastore document pointing a reader at the domain model without the datastore's
  own claims depending on the data-entity node staying current, the same way a
  schema's shape does not stop being true if the domain glossary describing it is
  edited.
- **`depends-on`**, authored by a deployment document (not by the datastore document
  itself), targeting this datastore node — the direction deployment.md's own
  relationships section already establishes for its edge to architecture-container,
  applied identically here: the deployment document's own claims (which environment
  this datastore instance runs in) stop holding the moment the datastore's own shape
  changes, not the other way around.
- **`may` declare `references`** toward this template node itself (target:
  `corpus-template-datastore`) once this node is merged, if the author wants the
  generated `referenced-by` edge; optional, since a node's use of `type: architecture`
  and its shape already show which template it followed — the same optionality the
  architecture-component template records for the identical case.

**`implements` was considered for that same edge and set aside, for consistency with
existing precedent rather than because it fits worse.** `relationships.schema.json`
describes `implements` as "source is the concrete realization of target (e.g. a
template instance of a standard)," which reads, if anything, as the more literally
accurate type for an instance node's relationship to the template it was written from
— arguably more accurate than `references`. The architecture-component template
(#1326, PR #1528) already chose `references` for the identical instance-to-template
edge, and this node follows that precedent for consistency across the batch rather
than re-arguing the choice; a future corpus-wide pass may want to revisit which of the
two is correct for every template's instance-to-template edge at once, rather than
each template deciding independently.

None of these can be declared by *this* template document itself — a template is not
an instance of the datastore it describes, and declaring `part-of`, `references`, or
being the target of a `depends-on` here would point at a node that does not exist for
a system that is never named.

## Boundary against sibling templates

| This template (datastore) | Its neighbors |
|---|---|
| **Container-level existence:** architecture-container (#1327) | Names that the datastore exists, its technology, and a one-line responsibility and communication edge. This template does not repeat that — it names the container document and adds only the datastore's own internal shape. |
| **One container's code-level internals:** architecture-component (#1326) | Internal module/class structure of a container that executes code. Out of scope here — a datastore's "internals" are schemas and migrations, not classes, which is exactly the gap this template exists to fill. |
| **Domain meaning of the data:** data-entity (#1333) | What the data *is* — a Nostr event, a channel, a message thread — independent of storage technology. This template does not repeat that — it names the tables/keyspaces structurally and links out for meaning. |
| **Where an instance actually runs, per environment:** deployment (#1336) | Physical/environment mapping — replica counts, managed-versus-local, secrets provisioning. This template stops at the shape of the attachment point; deployment states what that attachment point's value actually is, per environment. |

## Scope and omissions

**This node covers** the purpose of a datastore document, its required sections, its
evidence expectations, and the industry model (the C4 Container abstraction's
data-storage categories, the Twelve-Factor App's Backing Services factor) it adapts.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| A datastore's container-level existence and technology name | #1327 (architecture-container template) |
| Code-executing container internals (classes, modules) | #1326 (architecture-component template) |
| The domain meaning of the data a datastore holds | #1333 (data-entity template), not yet drafted at this node's authoring time |
| Where a datastore instance actually runs, per environment | #1336 (deployment template) |
| The evidence-class contract itself (FACT/INFERENCE/TEAM_KNOWLEDGE, citation shapes) | `launchpad/docs/corpus/AGENTS.md` |
| The `confidence` field's meaning and requirements | `launchpad/docs/corpus/standards/confidence.md` |
| Citing an accepted decision as evidence | `launchpad/docs/corpus/standards/decision-references.md` |
| A per-type diagram standard (this template needs none — no C4 diagram type exists for a datastore, per the primary-source check above) | Not applicable to this template; #1312 governs diagram notation for templates that do require one |

**No `relationships` in this node's front matter.** At the recorded revision,
`origin/launchpad`'s corpus tree carries four validated content nodes —
`corpus-agents`, `corpus-readme`, `corpus-standard-confidence`,
`corpus-standard-decision-references` — and none of the four has datastores, schemas,
Postgres, Redis, or backing services as its subject. An edge to any of them would be a
citation duplicate of what this node's evidence ledger already cites directly by path,
not a substantive typed relationship. This was checked against the actual tree
(`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`), not assumed
from "the corpus is new." The most likely first genuine edges for this node are
`part-of` targeting a merged architecture-container instance and `references`
targeting a merged data-entity instance, both named above and neither available today.

**No edge to the sibling batch-4 templates (#1329, #1333, #1343, #1348) or to the
already-open architecture and deployment templates authored in the same corpus-
templates effort (#1326, #1327, #1336).** All are being authored in parallel by
independent agents, and none is guaranteed merged when review starts on the others —
declaring an edge to any of them today would validate inside this node's own worktree
but be a hard error against `origin/launchpad`.

**Expected but not verified when this node was written:**

- **No instance of this template has been written yet.** Whether the seven required
  sections above are sufficient, or whether a real datastore surfaces a concern this
  template does not anticipate (a sharded or multi-region datastore, a datastore with
  no migration mechanism at all, a cache treated as ephemeral rather than durable), is
  untested. The first real datastore node is the test.
- **#1333's actual boundary language was not read**, because no PR for it exists at
  this node's authoring time. The boundary against data-entity above is this node's
  own reasoning from the batch dispatch brief and from first principles, and should be
  re-checked once #1333 lands — see the note at the top of that section.
- **Whether `.env.example`'s Typesense variables reflect stale documentation or an
  incomplete removal was not established.** Named as a real gap, not resolved, in the
  worked-illustration section above.
- **Not a gap left open.** An earlier draft of this node left it unresolved whether the
  `#[datastore_span]` instrumentation gap (Postgres only, not Redis or the object
  store) was a deliberate scoping decision or simply not yet extended. It is
  established: `buzz-datastore-tracing`'s own macro rejects any `system` value other
  than `"postgresql"` at compile time, so the restriction is enforced and deliberate
  today. What remains open is only whether it *should* be extended, not whether it
  currently is one — that is a design decision for whoever next wires up Redis or
  object-storage tracing, not a gap in this node's own research.
- **Whether Mermaid or any other in-Markdown notation is useful for a datastore
  document was not evaluated**, because this template's own primary-source check found
  no C4 diagram type for a datastore to begin with — an instance author may still find
  a schema diagram useful, but this template does not require one and did not survey
  notations for it.
- **The worked three-datastore illustration was checked only for the files and code
  paths cited**, and is explicitly not offered as Buzz's own complete or authoritative
  datastore inventory.
- **Cross-model review was not run.** Issue #1467 records that the cross-model review
  provider (Codex) is currently unavailable; a same-model final pass was substituted,
  per the corpus-templates batch dispatch brief.
