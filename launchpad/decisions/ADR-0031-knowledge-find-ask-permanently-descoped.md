---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#1418
decided_in: launchpad-26/buzz#1418
supersedes: none
---

# ADR-0031 — `knowledge.find`/`.ask` are permanently out of scope for the shipped crate

## Decision

**Option E.** `knowledge.find(query)` and `knowledge.ask(text)` — the two of #211's
seven methods with an unbounded free-text input domain — are permanently out of scope
for the shipped knowledge crate. #1400 (the task that would have implemented them)
closes as won't-do rather than staying open against a design nobody is committing to
build. `#211`'s existing Python implementation of both methods stays in the tree,
**Option E.** `knowledge.find(query)` — one of #211's seven methods — and
`knowledge.ask(text)` — a separate eighth entry point that shares `find`'s routing
rather than being one of the seven (`CONTRACT.md`: "an eighth public function, not one
of the seven") — are together the only two surfaces with an unbounded free-text input
domain, and both are permanently out of scope for the shipped knowledge crate. #1400
(the task that would have implemented them) closes as won't-do rather than staying
open against a design nobody is committing to build. `#211`'s existing Python
implementation of both methods stays in the tree,
documented and tested on the Python side, but unreachable from the shipped crate.

This rejects Option A (re-implement resolution in Rust at query time) and Option C (an
offline sidecar the crate calls at runtime) — both already rejected in ADR-0027 for the
same reasons repeated below — and does not adopt Option B (a precomputed similarity
index committed as corpus data, with the crate performing lookup-only nearest-neighbor
ranking over it), which would have kept the full seven-method promise at the cost of a
contested reading of Ruling 11's own wording.

**Option D — a curated, bounded natural-language question set, maintained and
pre-rendered by the pipeline like the other six methods — is recorded here as the one
upgrade worth reconsidering later**, if a concrete backlog of common phrasings emerges.
It is not adopted now. It costs nothing against Ruling 11 or Ruling 12 either way, so
nothing about this decision forecloses it; whoever picks it up later should read this
record first rather than starting a fresh `find`/`.ask` proposal from scratch.

`#533`'s success criterion should read six methods
(`explain`/`dependencies`/`impact`/`setup`/`conventions`/`history`), not seven, without
a footnote implying the seventh is still coming.

## Context

ADR-0027 (#578) ratified that the v1 knowledge crate ships free of this problem by
deferring `find`/`.ask` out of v1 — Ruling 11 ("the crate re-derives nothing: no AST
parsing, no embeddings, no traversal logic duplicated in Rust") and Ruling 12 ("the
corpus is a committed artefact; the desktop build does not run the pipeline") both hold
unchanged, and Options A and C were rejected for the reasons this record repeats below.
What ADR-0027 did not settle, because it was scoped to a v1 ship decision, was whether
`find`/`.ask` ever ship at all, and if so, how.

#1400 was filed to answer that, but its own Definition of done bundled the design
decision itself — "a written design exists ... or an explicit, separately-decided
amendment to one of those rulings if neither can hold" — inside a Task's checklist.
That is `launchpad/AGENTS.md` §4 rule 1's own test for an ADR ("a decision plus
rationale, with nothing in the repo changing when it closes"), which the same section
warns "masquerades as work" when left inside a task. #1418 pulled that decision out
into its own issue, parented alongside #1400 under #533, so #1400 could be scoped to
pure implementation once a decision existed.

`find`/`.ask` resolve today by computing a fresh answer at call time over the current
source tree, not by lookup:

```python
# launchpad/project-intelligence/knowledge_agent.py:109-113
def find_concept(self, concept: str):
    """§ Concept Retrieval, delegated whole to #210. Returns its
    PipelineResult, or None when nothing ranked."""
    try:
        return find_it_for_me(self.index, self.graph, concept)
```

```python
# launchpad/project-intelligence/semantic_index.py:208-220
def search(self, concept: str, top_k: int = 3) -> list["SearchResult"]:
    query_embedding = embed_text(concept)
    subsystem_scores = [
        (self._entries[file], cosine_similarity(query_embedding, self._entries[file].embedding))
        for file in self._file_scopes
    ]
    ...
```

`KnowledgeAgent.build()` indexes the crate once per instance (`symbols =
build_index(crate)`), and `search()` ranks a bag-of-words vector representation —
`embed_text`'s own docstring: "not a trained ML embedding model" — freshly at query
time. There is no finite key set an offline pipeline could pre-render this against, so
it is the one part of #211's surface Rulings 11 and 12 cannot both accommodate as
written.

## Decision drivers

- Ruling 11 and Ruling 12 both continue to hold as ratified by ADR-0027; this decision
  does not reopen or reinterpret either.
- `find`/`.ask` are the only two of #211's seven methods with an unbounded input
  domain — the other six are keyed on a symbol, an area, or a task name, and all six
  already return correct content from the packaged corpus.
- `find` (one of #211's seven methods) and `ask` (a separate eighth entry point that
  shares `find`'s routing, not one of the seven) are the only two surfaces with an
  unbounded input domain — the other six methods are keyed on a symbol, an area, or a
  task name, and all six already return correct content in `#211`'s Python prototype,
  which indexes the live source tree at agent construction rather than reading a packaged
  corpus — `KnowledgeAgent.build()` indexes the crate once and every method then reads
  that one index, because re-indexing per question "would make the seven-method surface
  far more expensive than the components it wraps". No knowledge crate exists yet
  (`#551`).
- The Python suites that validate `SemanticIndex.search`'s ranking and provenance
  behavior run in no CI job at all (#270). Any option that ships this logic — in Rust
  (A) or as a called sidecar (C) — inherits that gap; Option B would too, since it
  reuses the same computation, only relocated.
- `#533`'s own milestone entry is scoped Effort: Low against a 2026-09-11 date. Six of
  seven methods already ship real, working capability; the concrete cases an agent
  actually asks (explain a symbol, its dependencies, impact, setup, conventions,
  history) are already covered.
  seven methods already work end-to-end in `#211`'s Python prototype — real, tested
  capability, not yet packaged into the shipped crate (`#551`/`#552`); the concrete
  cases an agent actually asks (explain a symbol, its dependencies, impact, setup,
  conventions, history) are already covered there.
- `#211` is already merged with `find`/`.ask` implemented and tested on the Python
  side. Choosing E makes that implementation permanently unreachable from the shipped
  crate rather than temporarily so — a cost ADR-0027 already named as possible
  ("some of the seven methods' call-time design will not be reachable from the crate").

## Considered options

- **A — the crate re-implements resolution in Rust at query time.** Repeats ADR-0027's
  Option A. Rejected for the same reason: Ruling 11 forbids it in terms, and it
  duplicates provenance-critical logic the Python suites cover but no CI job runs
  (#270), in a second language with no test-suite ancestor proving parity.
- **B — ship a precomputed similarity index as part of the committed corpus; the crate
  performs only nearest-neighbor lookup over it, never rebuilding it from source.**
  Would keep the full seven-method promise. Not adopted: it is only available if
  Ruling 11's "no embeddings ... duplicated in Rust" is read narrowly, as forbidding
  re-derivation from source rather than forbidding a lookup computation over
  already-derived, committed data — a reading nothing about this decision settles, and
  reaching it would also require porting `embed_text`/`cosine_similarity` to Rust with
  new test coverage, since #270 leaves no Python suite to carry over.
- **C — a bundled, offline-only sidecar process the crate calls at runtime.** Repeats
  ADR-0027's Option C. Rejected for the same reason: it contradicts Ruling 12's "the
  desktop build does not run the pipeline" in spirit, and adds an availability
  dependency to an offline help tool.
- **D — a curated, bounded natural-language question set**, larger than the other six
  methods' keys but not truly unbounded; anything outside the maintained list returns a
  fixed "not answerable offline" response. Keeps Rulings 11 and 12 untouched exactly as
  worded. Recorded above as worth reconsidering later; not adopted now for lack of a
  concrete backlog of phrasings to seed it with.
- **E — `find`/`.ask` are permanently out of scope; #1400 closes as won't-do.**
  **Chosen.** Makes explicit a cost ADR-0027 already flagged as possible, instead of
  leaving #1400 open indefinitely against a design nobody is committing to build.

## Consequences

**Good.** #1400 stops carrying an undecided architecture question inside a Task's
Definition of done. The project board reflects reality: six methods ship, one is
permanently out of scope, instead of an open task against a design nobody is building.
Definition of done. The project board reflects reality: six of #211's seven methods are
implemented and validated in the Python prototype awaiting crate packaging, while `find`
— the seventh — and the separate `ask` entry point are both permanently out of scope,
instead of an open task against a design nobody is building.

**Good.** Neither Ruling 11 nor Ruling 12 is touched, reinterpreted, or amended. This
decision closes the gap ADR-0027 already named without adding any new architectural
surface or trust boundary to review.

**Bad, stated plainly.** `#211`'s `find`/`.ask` implementation and its test coverage
are now permanently orphaned code — built, reviewed across five rounds, and never
reachable from the shipped crate. `#533`'s acceptance criteria already read six of
seven methods (ADR-0027's narrowing), so no further edit is needed there; only its
"tracked separately as #1400" cross-reference needs updating once #1400 closes as
won't-do, so it does not read as though this is still an open follow-up.

## Security implications

Whatever answers `find`/`.ask` would have produced would have reached the same public,
shipped audience as the six keyed methods (PRD #4's Security implications; ADR-0027's
context). Choosing E removes that question rather than answering it: no new
computation path, no new trust boundary, and no change to the FACT/INFERENCE/TEAM
KNOWLEDGE provenance discipline the six keyed methods already carry. The rejected
Option B would have reopened a specific exposure — a `ConceptEntry.summary` string
reaching a rendered answer without the same structural provenance handling `#211`'s
review spent five rounds establishing — but that risk does not arise under E.

## Supersedes

none — extends ADR-0027's decision without reopening it.
