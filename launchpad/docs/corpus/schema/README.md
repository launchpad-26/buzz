# Corpus schema

Machine-readable contract for a canonical corpus node (issue #622, parent PRD #605,
parent-parent PRD #602). ADR-0028 decided every node is Markdown with YAML frontmatter;
this directory is the schema that frontmatter must satisfy, plus the fixtures and tests
that prove it.

This directory is the reference point [#636](https://github.com/launchpad-26/buzz/issues/636)
and [#639](https://github.com/launchpad-26/buzz/issues/639) (the corpus documentation
standard / `AGENTS.md` / `README.md`) will link to. It does not itself author that
standard — see [`OPEN`](../../plans/2026-08-25-issue-622-corpus-schema.md) in this
issue's plan for why.

## Files

| File | Purpose |
|---|---|
| `node.schema.json` | A corpus node's frontmatter contract. |
| `relationships.schema.json` | The finite relationship-type enum, with directionality/inverse metadata. |
| `requirements.txt` | Third-party dependencies (`jsonschema`, `PyYAML`) `tests/test_schema.py` needs. |
| `fixtures/valid/` | Fixtures that must validate. |
| `fixtures/invalid/` | One fixture per failure class, each violating exactly one rule. |
| `tests/test_schema.py` | Asserts both schemas are valid JSON Schema, every valid fixture passes, and every invalid fixture fails for its intended reason. |
| `COMPATIBILITY.md` | Schema version history and the breaking-change rule. |

Run the tests: `python3 -m unittest discover -s launchpad/docs/corpus/schema/tests -p "test_*.py" -v`
(CI runs this automatically — see `.github/workflows/launchpad-corpus-schema-tests.yml`).

## `node.schema.json` fields

| Field | Required | Type | Description |
|---|---|---|---|
| `id` | yes | string | Stable identifier for this node. Kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`). Never renamed once assigned — ADR-0028 requires generated projections to derive reproducibly from one canonical source, and a renamed `id` breaks every edge pointing at it. |
| `type` | yes | closed enum | The corpus surface this node documents. Values are PRD #602's own enumerated in-scope surfaces (`architecture`, `layers`, `capabilities`, `platforms`, `implementation`, `interfaces-events`, `verification`, `operations`, `development`, `release`, `governance`, `agent`, `ingestion`) — reused rather than inventing a second taxonomy. |
| `status` | yes | closed enum | One of `draft`, `active`, `deprecated`, `retired`, `flagged`. `flagged` is ADR-0029's "unestablished" state: two same-claim-type authoritative sources contradict each other and no human has resolved it yet. It is not a generic low-confidence marker — it names an unresolved conflict specifically. |
| `origin` | yes | closed enum | One of `upstream`, `launchpad`, `cohort`, `supporting` — reusing ADR-0003's per-claim origin prefixes so the vocabulary stays consistent between the handbook and this corpus. |
| `audiences` | yes | array (min 1, unique, closed enum) | Who the node is written for: `agent`, `developer`, `operator`, `reviewer`. Closed enum rather than free text (see `COMPATIBILITY.md` before adding a value) — a design choice this issue's plan flagged as `OPEN` rather than something the issue itself specified. |
| `evidence` | yes | array (min 1) of evidence entries | The node's provenance ledger, one entry per claim. See below. |
| `relationships` | no | array of relationship entries | Typed edges to other corpus nodes. See `relationships.schema.json`. A node may have none. |

### Evidence entries

Reuses `launchpad/project-intelligence/CONTRACT.md`'s FACT / INFERENCE / TEAM_KNOWLEDGE
claim classification rather than inventing a new one — verified against the code
(`memory.py:82-83`), not just the summary table, because the table's own prose is easy
to misread as "only FACT needs evidence."

| Field | Required | Description |
|---|---|---|
| `statement` | yes | The claim, one sentence. |
| `entry_class` | yes | One of `FACT`, `INFERENCE`, `TEAM_KNOWLEDGE`. |
| `evidence` | for FACT and INFERENCE | Citations (paths, commit-pinned links). **Required for both FACT and INFERENCE** — a common misreading of CONTRACT.md's table is that only FACT needs it; the enforced rule in `memory.py` requires it for INFERENCE too. Optional (never required, never forbidden) on TEAM_KNOWLEDGE. |
| `confidence` | for INFERENCE only | Float in `[0.0, 1.0]`, in addition to `evidence`. **Forbidden** on FACT and TEAM_KNOWLEDGE entries, mirroring `memory.py`'s bidirectional `__post_init__` check — not just required in the "this class needs it" direction. |
| `provided_by` | for TEAM_KNOWLEDGE only | Who told the corpus this. **Forbidden** on FACT and INFERENCE entries, same bidirectional rule. TEAM_KNOWLEDGE needs no evidence — it is the class that exists for uncorroborated statements. |

This issue's plan left open (see its `OPEN` section) whether classification applies
per-node or per-claim-within-a-node — ADR-0028 says explicitly that granularity is
`#605`'s to decide, not this schema's. This schema defaults to per-evidence-entry
classification (each entry in the `evidence` array carries its own `entry_class`).

## `relationships.schema.json`

A `relationships` array item has two fields: a closed-enum `type` and a `target` (the
related node's `id`). Five relationship types are defined, each with a `relationshipMeta`
entry describing its directionality and whether its inverse edge is `authored` (a human
writes both directions) or `generated` (tooling derives the reverse edge; never write it
by hand).

`node.schema.json` inlines its own copy of the `type`/`target` shape (`$defs.relationship`)
rather than `$ref`-ing this file across a schema boundary — an earlier revision did, keyed
to a fake `https://...` `$id`, which meant any standards-conformant validator that didn't
build the same manual resolver this directory's tests once did would attempt a live DNS
lookup and fail on any node using `relationships`. `relationships.schema.json` stays the
canonical source for the enum and its `relationshipMeta`; a test
(`test_relationship_enum_matches_node_schemas_inlined_copy`) asserts the two enum lists
never drift apart.

| Type | Directionality | Inverse |
|---|---|---|
| `depends-on` | source requires target to be true/current for source's own claims to hold | generated (`depended-on-by`) |
| `supersedes` | source replaces target; target becomes historical | generated (`superseded-by`) |
| `implements` | source is the concrete realization of target (e.g. a template instance of a standard) | generated (`implemented-by`) |
| `references` | source cites target as supporting context; no ownership or currency dependency implied | authored (`referenced-by`) |
| `part-of` | source is a constituent section/child of target | generated (`has-part`) |

Hand-authoring a generated inverse type directly (e.g. writing `type: depended-on-by`
instead of the forward `depends-on` edge on the other node) is rejected — see
`fixtures/invalid/wrong-direction-relationship.md`.
