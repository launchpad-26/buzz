---
id: corpus-standard-deprecation
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision ebe2daf721c7d7a96fdd84eba0a0a5d37eefa109."
    entry_class: FACT
    evidence:
      - "commit ebe2daf721c7d7a96fdd84eba0a0a5d37eefa109"
  - statement: "Enum membership in node.schema.json is the only check any tool in this repository makes on a node's status."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A relationship whose target matches no loaded node's id is a hard validation error."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The validator loads nodes by walking the corpus tree for Markdown files, so whether a node's file is present decides whether its id can satisfy an inbound relationship target."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "No code branches on which legal status value a node holds, so a corpus where an active node declares depends-on a deprecated node and references a retired node validates exactly as one where all three are active."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "supersedes declares that the source replaces the target and the target becomes historical."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "supersedes carries a generated rather than an authored inverse, and no inverse type appears in the relationship type enum, so a replaced node cannot declare the reverse edge itself."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "A depends-on edge asserts the source requires the target to be true or current for the source's own claims to hold, while a references edge cites the target as supporting context and implies no currency dependency."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "The validator reports every id carried by more than one node as an error, so ids are unique across the corpus."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A node's id is never renamed once assigned, because ADR-0028 requires every generated projection to derive reproducibly from one canonical source."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "flagged names ADR-0029's unresolved contradiction between two authoritative sources of the same claim type, which stays unresolved until a human resolves it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "Neither node.schema.json nor the corpus schema README defines deprecated or retired; the only status value either explains is flagged."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/schema/README.md"
  - statement: "The corpus authoring node's retirement procedure is a status change that keeps the file, and it states that nothing in that procedure is enforced by tooling."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "The corpus validator runs in CI on pull requests and on pushes to the launchpad branch that touch the corpus tree."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-corpus-validate.yml"
  - statement: "Citation checking is structural: the validator confirms a cited path resolves to a real file inside the repository and never opens it to compare it against the statement it sits under."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "For claims about how the system currently behaves executable evidence is authoritative, and for claims about intended or authorized behaviour accepted decisions are, including over code that has drifted from them."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "At the recorded revision the merge target carried no corpus node outside the excluded schema/ subtree, so this node had no merged sibling to point at and its citations of the corpus authoring node depend on that node merging first."
    entry_class: FACT
    evidence:
      - "git.ls_tree(origin/launchpad, launchpad/docs/corpus) -> schema/ paths only, no AGENTS.md and no standards/"
  - statement: "The validator parses only a node's YAML front matter and never inspects its Markdown body, so no check can compare a node's prose against another node's."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Every MUST in this node restates a step of the corpus authoring node's procedure for retiring or updating a node, and at least five runs of wording are shared near-verbatim between the two documents."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "The duplication between this node's rules and the corpus authoring node's retirement procedure is recorded as an open task rather than resolved here, and a sibling node's identical citation hazard is recorded separately."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1481 and #1473"
  - statement: "Issue #1311 requires this node to state its scope and the authority behind it, to separate MUST requirements from SHOULD guidance, and to define enforcement and an exception or escalation process."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1311 definition of done"
  - statement: "The general standard for the status field belongs to a separate open task whose objective is a single canonical policy node for status."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1323"
  - statement: "Encoding ADR-0029's claim-type classification and the unestablished/flagged state in the corpus schema and validator belongs to a separate open task and is not implemented."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1410"
  - statement: "Evidence, generated content, linking, provenance and the corpus's human-facing entry point each belong to their own separate open tasks rather than to this node."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1314, #1316, #1318, #1321 and #639 (issue titles and objectives)"
---

# Deprecating and retiring a corpus node

How a node stops being current: what `deprecated` and `retired` each oblige its author
to do, and what a reader arriving at a non-active node is owed.

**Nothing on this page is enforced.** A retired node with stale inbound edges validates
exactly like a healthy one, and no check anywhere distinguishes `deprecated` from
`retired`. Read *[What a green run establishes](#what-a-green-run-establishes)* before
relying on any of it.

## Scope and authority

**This node governs** the path a node takes out of currency — when to deprecate, what
deprecation obliges, when to retire, what retirement obliges, and what the retired
node's body must tell a reader who still arrives at it.

**Two kinds of sentence appear below, and they carry different weight:**

| | Backed by | Where to check it |
|---|---|---|
| **Claims** — how the tooling behaves | An entry in this node's `evidence` ledger | The cited source, opened |
| **Rules** — the MUST list | `AGENTS.md`'s *Retiring a node*, which they restate | That procedure, and the mechanism each names |
| **Rules** — SHOULD 2, which restates the same procedure | `AGENTS.md`'s *Retiring a node* | That procedure |
| **Rules** — SHOULD 1, 3 and 4, and the `deprecated`/`retired` split | This node, and nothing else | Nowhere; see below |

**Two different authorities, and conflating them would be the dishonest move.**

The **MUST list is not this node's invention.** It restates the retirement procedure in
`AGENTS.md`, the governing authoring node — which is why the corpus now carries that
policy twice, disclosed under the table below. Those rules have an authority; it is just
not this document.

**What genuinely has no external authority is the lifecycle distinction and the SHOULD
list.** No source in this repository defines what `deprecated` or `retired` *mean* — the
schema and its README explain `flagged` and no other value — so the split between the two,
and the guidance about when to use which, are this node's own. Issue #1311 asked for a
policy with a MUST/SHOULD separation and an escalation process; it did not supply that
content, and attributing this node's choices to it would be dressing up a decision as
something somebody said. Those parts are offered for a reviewer to accept or replace, and
every rule that rests on a mechanism names the mechanism, so the reasoning stays checkable
even where the rule is not sourced.

**Where the rest lives** — this node links these rather than restating them, **with one
disclosed exception** in the first row:

| Subject | Owner |
|---|---|
| Creating, updating and retiring a node, step by step | `launchpad/docs/corpus/AGENTS.md`, *Retiring a node* — **and the MUST list below restates it**, see the note under the table |
| The front-matter contract, including the `status` field itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Relationship types and their directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| Why one canonical representation, and why an id is permanent | `launchpad/decisions/ADR-0028-corpus-canonical-representation.md` |
| Ranking conflicting evidence, and the flagged state | `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` |
| The `status` field's own general standard, across every value | issue #1323 |
| Making `flagged` mean something to tooling | issue #1410 |
| Evidence, generated content, linking, provenance | issues #1314, #1316, #1318, #1321 |

**The first rows are honest about an overlap, not a link.** Every MUST below maps onto a
step of the authoring node's *Retiring a node* procedure, so the corpus currently carries
the retirement policy twice. At least five runs of wording are shared near-verbatim — two
in the prose, and MUST 3, MUST 4 and MUST 6 — so the overlap is not confined to the rules,
and MUST 6's match is with that node's *Updating a node* section rather than its
retirement one. Which document should own the procedure is not this node's to rule on,
and the authoring node
was out of scope to edit here, so the duplication is recorded rather than resolved:
launchpad-26/buzz#1481. Until it is, **treat the two as one policy that must be edited
together** — nothing detects them drifting apart, because the validator never reads body
prose.

**Not covered here.** The `status` field as a field — its full value set, and what
`draft` and `flagged` oblige — is #1323's. This node describes only the three values
that form the path out of currency, and defines none of them for any other purpose.
`flagged` is on the boundary and is explicitly **not** a deprecation stage: it names an
unresolved contradiction between two authoritative sources of the same claim type, which
a human resolves. A node can be flagged and current; a node can be retired and
uncontested. See [ADR-0029](../../../decisions/ADR-0029-corpus-evidence-precedence.md).

## The path out of currency

| Status | What it asserts | What the author owes |
|---|---|---|
| `active` | The node's claims held at the revision in its ledger, and nobody has said otherwise. | Nothing beyond the ordinary update rules. |
| `deprecated` | The node is still the corpus's answer on its subject, and is on its way out. Its claims may be stale, its replacement may not exist yet. | A body that says **why**, and says whether the claims still hold. |
| `retired` | The node is no longer the corpus's answer. It is kept for the references that still point at it. | A body that says **why**, and either names the replacement or says plainly that there is none. |

**Deprecation is a warning; retirement is a fact.** The distinction is only useful if a
reader can act on it, so it is defined by what the body must tell them, not by an
internal label. A `deprecated` node that says nothing about being deprecated is
indistinguishable from an active one, because the status field reaches no reader on its
own — no generated view exists that would surface it, and no check branches on which
value it holds.

**Both are status changes. Neither is a deletion.** That is the one point on this page
with a hard mechanical consequence, and it is the next section.

## Why retirement is never a deletion

The validator matches every `relationships[].target` against the ids of the nodes it
loaded, and it loads nodes by walking the corpus tree for Markdown files. So a node's id
is resolvable exactly as long as its **file** is there.

- **Change the status** — the file stays, the node still loads, every inbound edge still
  resolves. Nothing fails.
- **Delete the file** — the node stops loading, and every edge naming its id becomes a
  hard error. The failure lands on the *other* nodes, not on the one that was removed.

That asymmetry is the whole mechanism, and it cuts both ways: the same property that
makes retirement safe is what makes it silent. Inbound edges keep resolving, so nothing
tells a reader — or a reviewer, or a future generated view — that they have been sent to
a node that stopped being current. **The edges resolving is the problem, not the safety
net.**

## MUST

1. **Retire by setting `status` to `retired`. Never delete the node's file.** Changing
   it to `deprecated` is a different obligation under this same page, not retirement —
   a status change satisfies this rule only when the value is the retired one.
   Deletion breaks every inbound edge; a status change breaks none.
2. **Never reuse or rename a spent id.** ADR-0028 requires generated projections to
   derive reproducibly from one canonical source, so a renamed id breaks whatever
   resolves through it and a reused one silently redirects old references to new content.
3. **Say why, in the node's body and in the `evidence` ledger, and at which revision
   that was decided.** A reader arriving from an old link is owed the reason, not just
   the label — and a reason recorded only in prose is exactly the kind of claim the
   ledger exists to make auditable rather than asserted.
4. **Where another node takes over the subject, that node declares
   `supersedes` targeting the retired id.** The direction is fixed: the source replaces
   the target. The retired node cannot declare the reverse — `supersedes` has a
   *generated* inverse, and no inverse type exists in the relationship enum to write.
5. **Where nothing takes over the subject, the body must say so explicitly.** Silence
   reads as "look harder", and there is nothing to find.
6. **Update the `evidence` ledger in the same edit as the body.** A new claim with no
   entry, or an entry orphaned by deleted prose, are the two ways the two drift apart.
7. **Enumerate the inbound edges before changing the status, and decide each one.**
   Search the corpus for the id. Deciding to leave an edge alone is a decision; not
   looking is not.

## SHOULD

- **Deprecate before retiring** where readers are still arriving and the replacement is
  not ready. Going straight to `retired` is legitimate when the subject is simply gone.
- **Repoint the inbound edges that wanted the subject; leave the ones that meant the
  node.** A `references` edge citing the node as historical context is correct after
  retirement. A `depends-on` edge usually is not — it asserts the target is current.
- **Re-verify a deprecated node's claims, or say plainly that they were not
  re-verified.** Deprecation is not permission for the ledger to go quietly stale.
- **Retire one node per change.** A batch retirement makes the inbound-edge decisions
  in rule 7 hard for a reviewer to check individually, and that review is the only
  thing checking them at all.

## What a green run establishes

The check is `python3 launchpad/project-intelligence/corpus/validate.py`, and CI runs it
on pull requests and on pushes to `launchpad` touching the corpus tree.

**What it proves about a deprecation:** nothing.

That is not a figure of speech, and it is worth stating precisely, because the loose
version of it — "nothing reads `status`" — is false. The field *is* read once: schema
validation rejects a value outside the enum, so `status: obsolete` fails with an enum
violation and exit 1. What no code anywhere does is **branch on which legal value it
holds**. Past that membership check, nothing distinguishes `active` from `deprecated`
from `retired`. So:

| The check does establish | The check does not establish |
|---|---|
| The front matter satisfies the schema, so `status` holds a legal value | That the value is the *right* one, or that the body agrees with it |
| Every `relationships[].target` resolves to a loaded node's id | That the target is still current, or that the edge still makes sense |
| Every cited path resolves to a real file in the repository | That the file says what the statement claims — checking is structural, the file is never opened |
| No two nodes share an id | That a spent id was not quietly reused for new content |

A corpus in which an `active` node declares `depends-on` a `deprecated` node and
`references` a `retired` one validates exactly as one where all three are active.
Reproduce it in a scratch tree with `--root`; the run prints `PASS` and exits 0.

**So the enforcement of everything on this page is a reviewer reading the diff.** Every
MUST above is a convention a person holds, and a green run is evidence that the node is
well-formed, never that it was retired correctly.

## Exceptions and escalation

**A rule you cannot follow is recorded, not worked around.** State which one, and why,
in the pull request that makes the change. Nothing will catch the omission for you, so
an unrecorded exception is indistinguishable from a mistake.

**If a node genuinely must be deleted** — it should never have existed, or it must go
for a reason outside this corpus — you have left this node's scope. The mechanical
consequence is not optional: the validator will fail for every inbound edge until each
one is removed or repointed. That is a human's decision, made on the issue, not an
authoring judgement to make in a diff.

**If two authoritative sources of the same claim type disagree about whether the
subject is still current**, that is not a deprecation. It is ADR-0029's flagged state:
record the contradiction, set `status` to `flagged`, and leave it for a human. Do not
retire a node to make a conflict go away — retirement asserts the subject is settled,
which is the opposite of what is true. Nothing enforces this either; the encoding of the
flagged state in schema and checker is #1410's, and is not implemented.

**Which tiebreaker applies** when deciding whether a node's claims have gone stale is
ADR-0029's, not this node's: executable evidence is authoritative for how the system
currently behaves, and accepted decisions are authoritative for what was intended or
authorized, including over code that has drifted from them.

## Scope and omissions

**This node covers** when a corpus node is deprecated and when it is retired, what each
obliges its author to do, what the retired node's body owes a reader, why retirement is a
status change rather than a deletion, and what a passing validation run does and does not
establish about any of it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owner |
|---|---|
| The `status` field's general standard — every value, `draft` and `flagged` included | #1323 |
| Making `flagged` mean something to the schema and the checker | #1410 |
| Which typed edge to use when repointing, and how corpus links are formed generally | #1318 |
| Whether and when a node's recorded revision moves | #1321 |
| Classifying and citing evidence | #1314 |
| Whether generated views will honour `status` — no generator exists | #1316 |

**No `relationships` in this node's front matter, and the reason expires.** At the
recorded revision the merge target carried no corpus node outside the excluded `schema/`
subtree, so there was no merged node to target and an edge to an unmerged one would be a
hard error on `launchpad` however cleanly it validates on this branch. That is a fact
about **merge order**, not about the corpus being empty — `corpus-agents` exists and is
loadable here. Do not copy this paragraph's reasoning into a later node without
re-running the check; it stops being true the moment the authoring node merges. The
check, which you should run rather than take on this node's word:

```bash
git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus
```

**The same merge-order dependency applies to this node's citations, not only to its
missing edges.** Two `evidence` entries cite `launchpad/docs/corpus/AGENTS.md` by path,
and a bare path is checked against the filesystem. If this node reached `launchpad` ahead
of the branch introducing that file, those citations would fail exactly as an unmatched
relationship target would. This node must merge after it. A sibling node hit the
identical hazard and it is tracked as launchpad-26/buzz#1473. Body prose is not affected
— the validator never reads it — so the links in the tables above carry no such risk.

**Expected but not verified when this node was written:**

- **No node has ever been deprecated or retired in this corpus.** Every rule above is
  written against the mechanism rather than against a retirement anybody has performed.
  The deletion consequence and the status-is-inert claim were reproduced in a scratch
  corpus with `--root`; the *procedure* has never been exercised end to end.
- **Whether any reader ever sees `status` is unknown.** The claim that a retired node
  silently keeps receiving traffic assumes generated views and readers that do not exist
  yet — no corpus generator exists (#1316), and the human entry point is unlanded (#639).
  What is verified is narrower: no check branches on which value the field holds —
  schema validation reads it, but only for enum membership.
- **`developer` was excluded from `audiences`, and that was a judgement call.** Corpus
  nodes are authored by agents under the authoring node's procedure, and the unenforced
  conventions here land on a reviewer, so this ships as `agent` and `reviewer`. Nothing
  in the deprecation lifecycle addresses product code. A reader who thinks a developer
  needs this node should say so — the exclusion was contested and is not settled.
- **The `deprecated`/`retired` split is this node's and is unratified.** It was not
  reviewed against #1323, which owns the field, because that node does not exist. If
  #1323 defines these values differently, it wins and this page follows it.
