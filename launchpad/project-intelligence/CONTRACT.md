# The `knowledge.*` interface contract

**Issue:** #553 · **Feature:** #533 · **PRD:** #4 · **Status:** proposed, not ratified

The interface a calling agent uses to query the knowledge corpus. Derived from
`launchpad/Research/project-intelligence-layer-design.md` § Data Model item 8, and
**reconciled line-by-line against the implementation merged in PR #573** — every
divergence between the design doc and the code is listed in
[§ 7](#7-reconciliation-against-211) rather than quietly resolved in the code's favour.

Where this document and the code disagree, **the code is described and the disagreement is
named.** A contract that documents intentions the implementation does not have is the
defect class #211 hit four times.

---

## 1. The one guarantee

> **No field in a response asserts more than was established.**

Everything else here serves that. Every claim carries a provenance class as a *structural
field*, not a tone of voice:

| Class | Means | Requires |
|---|---|---|
| `FACT` | Directly observed in code, config, tests, docs, git history or runtime output | `evidence`, non-empty |
| `INFERENCE` | Concluded from evidence, stated nowhere | `evidence` **and** `confidence` in `[0.0, 1.0]` |
| `TEAM_KNOWLEDGE` | Told to the layer by a person | `provided_by`; needs **no** evidence — it is the class that exists for uncorroborated statements |

These are enforced at construction, not by convention: `answer.Claim` validates by building
a throwaway `memory.MemoryEntry` and letting #209's `__post_init__` raise. So the rules live
in exactly one place, and a claim shape the memory store would reject cannot become an answer.

A consumer may therefore rely on: **a `FACT` always has evidence; an `INFERENCE` always has
a confidence; a `TEAM_KNOWLEDGE` always names who said it.** Nothing else about content.

---

## 2. Response type

Every method returns one `Answer`. One return type is deliberate — a caller never learns a
second shape to find out whether a field is a fact.

```
Answer
  question              : str                  # non-empty; the question as asked or as rewritten
  short_answer          : str                  # may be ""
  how_it_works          : str                  # may be ""
  relevant_flow         : str                  # may be ""
  important_files       : tuple[str, ...]      # repo-relative paths
  things_to_be_aware_of : str                  # caveats; see §5
  claims                : tuple[Claim, ...]    # the ledger; may be empty

Claim
  statement      : str                          # non-empty
  entry_class    : "FACT" | "INFERENCE" | "TEAM_KNOWLEDGE"
  evidence       : tuple[str, ...]              # citations; see §3
  confidence     : float | None                 # INFERENCE only
  provided_by    : str | None                   # TEAM_KNOWLEDGE only
  temporal_state : "BASE" | "WORKING" | "HISTORY"
```

**`Answer` has no `sources` field, deliberately.** The `## Sources` section is generated from
`claims` at render time. An authored sources list can disagree with the claims it accounts
for, and a provenance layer whose source list is hand-maintained is one that can lie.

Rendering order is fixed and sections with no content are omitted:

```
## Short answer · ## How it works · ## Relevant flow
## Important files · ## Things to be aware of · ## Sources
```

**Omission is uniform, including `## Sources`.** An answer citing nothing emits no Sources
heading rather than an empty one — an empty heading reads as "checked, found nothing", an
absent one as "not established", and the second is the honest signal.

---

## 3. Citation forms

`evidence` entries are not all file references, and a consumer parsing them must handle all
six shapes:

| Shape | Example | Openable? |
|---|---|---|
| File range | `crates/buzz-core/src/kind.rs:219-221` | yes |
| File line | `crates/buzz-core/src/kind.rs:1077` | yes |
| Bare path | `Justfile` | yes, but carries no position |
| Graph edge | `is_shared_gated_kind -> is_unshared_gated_event (1 hop)` | no |
| Tool result | `find_references('x', crate='buzz-core') -> no callers in this crate` | no |
| Commit | `commit 067c085f… (2026-08-05…) by Wes` | no |

A consumer that treats every citation as a path will mis-handle three of six, and one of the
three it *can* open — the bare path — resolves to a whole file rather than to the lines the
claim is about. Bare paths come from `setup()`'s not-found branch, which cites the manifests
it searched (`evidence=tuple(SETUP_SOURCES)`) rather than a location inside one.

`worked_trace.audit_citations()` shows the intended discipline: parse what is parseable, and
**report the rest as unverified rather than skipping it** — a checker that silently ignores
what it cannot read produces a clean audit over nothing.

---

## 4. The seven methods

All take a built `KnowledgeAgent` as first argument. `ask()` is an eighth entry point that
routes to them.

### `find(agent, query: str) -> Answer`

Concept → subsystem → candidate, for a caller who cannot name the symbol yet.

Three claims, split by what was actually established:
- the ranking scores — measured, so `FACT`
- **that the top hit is the implementation the concept means — always `INFERENCE`**, with
  `confidence` set to the measured cosine score itself
- the candidate's graph edges — `FACT` about *that symbol*, worded so it cannot read as
  confirming the match, because those edges exist regardless of what was asked

A score at or below `MINIMUM_CANDIDATE_SCORE` (`1e-9`) resolves to **no candidate**. #210's
pipeline returns its top-ranked candidate even at score `0.0`, with real edges attached;
reporting that as a find is true evidence about the wrong subject.

### `explain(agent, symbol: str, depth: Depth | None = None) -> Answer`

The full four-stage pipeline. **`depth` is accepted, and only `RATIONALE` changes the answer**
— it triggers the history stage, which can add history claims and their caveat. `SUMMARY` and
`TRACE` return identical answers. See §7 and #571.

### `dependencies(agent, symbol: str) -> Answer`

Outward `calls` slice to `DEPENDENCY_HOPS` (2), direct and transitive as **separate claims**.

### `impact(agent, symbol: str) -> Answer`

Inward `called_by` slice. Direct (≤ `IMPACT_DIRECT_HOPS` = 1) and secondary (2) are **never
merged** — conflating them hides which consequences are certain and which want
double-checking before a change.

Both of these read the in-memory graph and make **no live tool call**, so both carry the
snapshot caveat of §5.

### `setup(agent, task: str) -> Answer`

Cited operational steps for `task ∈ {install, run, seed, migrate, test, lint, build, deploy}`,
searched in order through `SETUP_SOURCES`: `Justfile`, `CONTRIBUTING.md`, `README.md`,
`Cargo.toml`, `.env.example`.

Every claim cites file and line. A generic recipe is wrong the moment the project's tooling
differs from the guess, so an unknown task reports not-found rather than inventing one.
**Currently returns the recipe header, not a runnable step** — see §7 and #572.

### `conventions(agent, area: str | None = None) -> Answer`

`TEAM_KNOWLEDGE` and `INFERENCE` from `ProjectMemory`, scoped to `area`.

**`FACT` entries are excluded on purpose.** A convention is what the team decided, not what
the code happens to do; reading conventions off the code is how an accident becomes a rule.

Returns empty on a fresh process and **says so in `things_to_be_aware_of`**, because
`ProjectMemory` does not persist (#570).

### `history(agent, symbol: str) -> Answer`

`HISTORY`-state narrative. A claim drawn from a commit message is **always `INFERENCE`**: a
message states intent, never a measured outcome.

Queries a window of `HISTORY_LINE_WINDOW` (10) lines, not the definition line, and cites the
window actually queried. That is a workaround for #569 — `inspect_git_history` returns zero
commits for a degenerate `start == end` range — and **should be reverted when #569 is fixed**,
because it makes every history citation wider than the claim it supports.

### `ask(agent, text: str) -> Answer`

Decomposes and dispatches to one of the seven. Routing:

| Intent | Method | Cue |
|---|---|---|
| `SETUP` | `setup` | an operational verb **and** a named task |
| `IMPACT` | `impact` | "what happens if", "what breaks", "if i change" |
| `DEPENDENCIES` | `dependencies` | "depend on", "what does it call" |
| `HISTORY` | `history` | "evolve", "over time", "why does", "when was" |
| `CONVENTIONS` | `conventions` | "convention", "do we usually", "house style" |
| `FIND` | `find` | a "where is" phrasing **with no nameable target** |
| `EXPLAIN` | `explain` | fallback |

Two properties a consumer can rely on:
- **An unrecognised question falls back to `EXPLAIN` rather than guessing.**
- **An intent needing a symbol, asked without one, says so** — it does not answer a different
  question and does not raise.

---

## 5. Caveats a consumer must surface

`things_to_be_aware_of` is not decoration. Where it is populated, it is derived from the same
evidence as the claims, so it cannot disagree with the ledger. It is **not** emitted for every
`INFERENCE` claim: `find()` and `conventions()` can return an `INFERENCE` and leave the field
empty. A consumer must therefore treat a caveat as authoritative when present, and must not
read its absence as "no caveat applies".

The conditions below do populate it:

| Condition | The answer says |
|---|---|
| Graph-only answer (`dependencies`, `impact`) | derived from the build-time index, no live re-read |
| `explain`/`ask` routed through the explain pipeline with `BASE` implied | BASE was never read; code claims come from `WORKING` |
| `ProjectMemory` consulted | it does not persist between runs |
| Symbol not located | a statement about **the index**, not about the codebase |
| Candidate rejected at the score floor | the index *did* return one; it was rejected here |

A consumer that renders `claims` and drops `things_to_be_aware_of` **breaks the guarantee in
§1**, because several claims are only honest in the presence of their caveat.

**The `BASE` caveat does not survive routing — #588.** `ask()` classifies the temporal state
and then dispatches to a method that does not carry it, so a question such as *"what happens
at head if I change `X`?"* is routed to `impact()` and comes back with only the graph-snapshot
caveat. The BASE row above is honest for the `explain` pipeline and not for `ask()`; until
#588 lands, a consumer must not infer from the absence of a BASE caveat that the question was
not about `BASE`.

---

## 6. Error modes

The interface distinguishes **an input error**, which raises, from **an absent answer**, which
is returned as a labelled claim. That distinction is the contract's most load-bearing
property after §1: a degraded answer is data, not an exception.

### Raises

**None of the seven methods raise on an empty target.** They wrap the caller's argument before
it reaches a validator — `explain("")` interpolates it into a non-empty question, so
`question.decompose` never sees an empty string, and `dependencies("")` goes straight to a
graph lookup without calling `confidence.assess` at all. Measured 2026-08-24: `explain`,
`dependencies`, `impact`, `setup` and `history` each called with `""` all returned an `Answer`
and none raised. A consumer writing `except ValueError` around a `knowledge.*` call is writing
dead code; handle the labelled no-answer in the next table instead.

The functions below raise, and are reachable only by calling them **directly**:

| Condition | Exception | Raised by |
|---|---|---|
| Empty or non-string question | `ValueError` | `question.decompose` (`question.py:198`) |
| Empty or non-string target | `ValueError` | `confidence.assess` (`confidence.py:175`) |
| No named target | `ValueError` — a nameless question is `find`'s case | `investigate()` (`investigation.py:338`) |
| Claim/Answer violating §1 | `ValueError` at construction | `answer.Claim`, `answer.Answer` |
| Symbol miss | `LookupError`, naming the symbol | `investigator.find_symbol` — a tool helper, called by none of the seven |

### Returns a labelled answer, never raises

| Condition | Response |
|---|---|
| Symbol absent from the index | `FACT`: "the index has no locatable definition for X", evidence = the whole trace |
| Index built from zero symbols | `FACT`: "the SemanticIndex returned no candidate" |
| Candidate below the score floor | `FACT` naming the candidate **and its score** — never "returned no candidate", which would be untrue |
| Cited range unreadable | claim downgraded `FACT` → `INFERENCE`, evidence records the failure |
| Cited range readable but does not support the claim | same downgrade — this is the check that catches a citation resolving to the wrong subject |
| Nothing depends on the symbol | `FACT` scoped to the graph: "the **indexed graph** holds no dependent", never "nothing depends on this" |
| No corroboration lookup was performed | **no claim at all** — absence of evidence must not become evidence of absence |
| Name resolves to several symbols | first is used, and the ambiguity is recorded on the trace and `Findings.ambiguous` |

**Downgraded, never dropped.** A dropped claim leaves an answer quietly shorter, and a reader
cannot distinguish "nothing to say" from "could not confirm what I was going to say".

---

## 7. Reconciliation against #211

DoD item 2. Every place this contract, the design doc, and the merged code diverge.

| # | Divergence | Status |
|---|---|---|
| 1 | Design doc says `knowledge.explain(symbol, depth?)` is "depth-tunable". Implementation accepts `depth` and returns identical answers for `SUMMARY` and `TRACE`; the only effect is that `RATIONALE` triggers the history stage. | **Open — #571.** Contract documents the real behaviour. |
| 2 | Design doc says `setup(task)` returns "cited operational steps". Implementation returns the recipe *header* (`Justfile defines 'test': test:`), with no runnable command. | **Open — #572.** |
| 3 | Design doc treats `BASE` as first-class and separately queryable. Implementation classifies `BASE` and reads `WORKING`, disclosing it in a caveat. | **Open — #588.** BASE reads need `git show HEAD:<path>`. `ask()` also discards the classified state when it routes, so the §5 caveat does not appear for routed questions. |
| 4 | Design doc's step 1 queries three components "for an existing answer". Implementation's `confident` is a `ProjectMemory` hit **only** — a graph or semantic hit proves the symbol exists, which is not an answer. | **Intentional.** The doc's own worked example agrees: `search_symbols` finds `UserRepository` and it still records "confidence: none yet". |
| 5 | `history` queries a 10-line window, not the definition line. | **Workaround for #569.** Revert when fixed. |
| 6 | Design doc's investigation progression lists five tool calls. The real trace has six — the tests stage reads the file to locate `mod tests` *and* searches below it. | **Contract and `PROGRESSION` both list six.** A canonical order omitting a call the code makes is the same lie as a trace omitting it. |
| 7 | `ProjectMemory` has no persistence, so `conventions()` is empty on a fresh process and the confidence gate never fires. | **Open — #570.** Disclosed in every affected answer. |

**Not a divergence, but the consumer must know:** none of the 307 tests behind this interface
runs in CI (#270). The contract is specified against code whose correctness is currently
gated by nothing.

---

## 8. Worked example

DoD item 3. Real output, `buzz-core`, merged code — not constructed for this document.

```
>>> agent = KnowledgeAgent.build("buzz-core")
>>> knowledge.ask(agent, "what happens if I change `is_shared_gated_kind`?")
```

Routed to `impact` by the `IMPACT` intent. Rendered:

```
## Short answer
2 direct and 8 secondary dependents.

## Things to be aware of
Secondary dependents are reached through another symbol, so a change here affects them
only if the direct dependent's own behaviour changes.
Derived from the graph indexed at agent build time, with no live re-read -- an edit to
the working tree since then is not reflected here.

## Sources
- FACT: the indexed graph holds 2 direct dependents of is_shared_gated_kind:
  is_unshared_gated_event, tests::shared_gated_kinds_membership
  -- is_shared_gated_kind -> tests::shared_gated_kinds_membership (1 hop),
     is_shared_gated_kind -> is_unshared_gated_event (1 hop)
- FACT: the indexed graph holds 8 secondary dependents of is_shared_gated_kind: …
  -- is_shared_gated_kind -> is_unshared_gated_event -> tests::… (2 hop), …
```

As structured data:

```
FACT | temporal_state=WORKING | confidence=None
    the indexed graph holds 2 direct dependents of is_shared_gated_kind: …
FACT | temporal_state=WORKING | confidence=None
    the indexed graph holds 8 secondary dependents of is_shared_gated_kind: …
```

Four contract properties visible in one response:

1. **Direct and secondary are separate claims**, not one merged count.
2. **Both are `FACT`, and the wording earns it** — "the *indexed graph* holds", because
   nothing was re-read from the tree.
3. **The snapshot caveat is present**, which is what keeps (2) honest.
4. **Every citation is a graph edge with its hop count** — re-derivable by a reader, and not
   a file path, which is why §3 matters.

---

## 9. Open questions

Three, all needing a decision before #551 scaffolds against this. Each is now filed as an ADR
issue parented to PRD #4, per `launchpad/AGENTS.md` §4 rule 2 — an open question left only in
a document body "gets decided by accident inside whichever task hits it first".

- **9.1** and **9.2** → **#578** (they are one decision; see below)
- **9.3** → **#589**

**9.1 — What shape is the committed corpus?** PRD #4's Ruling 12 says the corpus is a
committed artefact; it does not say whether that is JSON, Markdown with frontmatter, or
SQLite. The format is this contract's serialisation, so it belongs here. Not decided in this
document because it constrains the crate's read path and that is #551's to weigh.

**9.2 — Does the crate answer queries at runtime, or serve pre-rendered pages?** #532 says
"help in Settings"; #533 says "agents read it programmatically". Those may be one surface or
two. If one, the crate must implement the seven methods over the corpus. If two, the human
surface can be pre-rendered and only the agent surface needs the methods. This is the largest
unresolved question in M3 and it changes #551's scope materially.

**Why 9.1 and 9.2 are one decision (#578).** 9.1 cannot be answered before 9.2, because the
format is the serialisation of whatever turns out to be pre-computed. And 9.2 is not a free
choice between two workable designs: Ruling 11 forbids the crate implementing the methods
itself ("no traversal logic duplicated in Rust"), while `find(query)` takes arbitrary free
text resolved at call time (§4), so it has no finite key set to pre-render against either.
Whichever way it goes, Ruling 11, Ruling 12 or #533's seven-method success criterion has to be
amended — which is why it is an ADR and not a task. Ruling 12's own auditability argument
already rules out a binary corpus.

**9.3 — Who owns this contract once the crate exists?** It currently lives beside the Python
implementation because that is the only party that exists. When #551 scaffolds the crate, the
contract governs a boundary between two components and should probably move to the crate or to
`launchpad/decisions/`.

---

## Provenance

Written for #553 against PR #573 as merged (`945619273`). Every constant, signature, error
mode and example was extracted from the code rather than recalled: the values in §2, §4 and §6
come from introspecting the merged modules, and §8's output is a captured live run.

The reconciliation in §7 is the part to distrust first — it is a claim about *agreement between
documents*, which is exactly the kind of claim this layer would label `INFERENCE`.
