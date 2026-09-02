---
id: governance-deprecation-policy
type: governance
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "crates/buzz-relay/src/config.rs declares INERT_MEDIA_READ_AUTH_VARS as a two-element array naming BUZZ_REQUIRE_MEDIA_GET_AUTH and BUZZ_REQUIRE_MEDIA_READ_AUTH, and its doc comment states that both are inert because media reads are now unconditionally authenticated."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "That doc comment states the rationale for the mechanism as an operator belief rather than as a code concern: an operator still setting either variable — 'especially to false' — holds a belief about their deployment that is no longer true."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "Config::from_env iterates inert_env_vars(&INERT_MEDIA_READ_AUTH_VARS, ...) and emits a warn! for each variable found set, whose text names the variable, states that GET/HEAD /media/* always require Blossom t=get auth plus relay membership, instructs the operator to remove it, and says that a value of false does not re-open unauthenticated media reads."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "The inert-variable warning is covered by three unit tests in the same file: one asserting the warning fires when the variable is set to false, one asserting the never-read alias is reported too, and one asserting unrelated variables stay quiet."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "BUZZ_REQUIRE_MEDIA_READ_AUTH was documented in .env.example as an accepted alias but was never read by the relay, so the deprecation notice in .env.example described a variable the code had no handling for at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - ".env.example"
  - statement: "The media-read removal shipped as a single commit — 769ac70b741e3ad6809bff14eba29d3dd2cbd318, 'fix(media): require authenticated reads (#4610)' — that touched eighteen files, reconciling the relay code, .env.example, docs/admin/README.md, the Helm chart's values.yaml, values.schema.json and NOTES.txt, TESTING.md, the desktop Tauri commands and the conformance and end-to-end tests in one change."
    entry_class: FACT
    evidence:
      - ".env.example"
      - "crates/buzz-relay/src/config.rs"
      - "git_show_stat(commit='769ac70b741e3ad6809bff14eba29d3dd2cbd318') -> 18 files changed, including .env.example, crates/buzz-relay/src/config.rs, docs/admin/README.md, deploy/charts/buzz/values.yaml, deploy/charts/buzz/values.schema.json, deploy/charts/buzz/templates/NOTES.txt, TESTING.md and .github/workflows/ci.yml"
  - statement: "The same file takes the opposite action for a different removal: BUZZ_REPLICA_HEAD_MAX_AGE_SECS is refused as a hard startup error naming its replacement BUZZ_REPLICA_READ_MAX_AGE_MS, with an inline comment stating that silently honouring the old name would mean 1000x the intended budget because the units changed from seconds to milliseconds."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: ".github/workflows/ci.yml defines a dead-token-guard job that greps a fixed pattern set — TokenScope, MintTokenResponse, hasApiToken, spr_tok_ — across a fixed path set and exits 1 if any match is found."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "The dead-token-guard's own comment says it covers 'desktop, mobile, docs, or config', but its PATHS variable lists only desktop/src/, desktop/tests/, mobile/test/, mobile/lib/ and .env.example — no docs/ path and no web/ path, so the web client and the docs tree are outside the guard it is described as covering."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "At the recorded revision the four dead-token patterns appear nowhere in the repository except in the guard's own PATTERNS string, so the removal the guard protects is complete and the path gap above is latent rather than live."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
      - "grep_repo(pattern='TokenScope|MintTokenResponse|hasApiToken|spr_tok_', excluding='node_modules,.dart_tool,target') -> exactly one match repository-wide, the PATTERNS string on line 1053 of .github/workflows/ci.yml itself, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "Database migrations are applied by a single embedded sqlx Migrator over migrations/, and the directory contains no .down.sql file of any kind, so no migration carries a reverse."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
      - "list_files(glob='migrations/*.down.sql') -> no matches, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "Multiple migration files carry an explicit comment that a previously applied file must not change checksum or sqlx aborts startup with a VersionMismatch, which is why later changes are written as new additive files rather than edits to published ones."
    entry_class: FACT
    evidence:
      - "migrations/0002_git_repo_names.sql"
      - "migrations/0004_events_tags_gin.sql"
      - "migrations/0010_nip_rs_exact_replay_guard.sql"
  - statement: "Removing a database structure is therefore performed as a forward migration that drops and re-creates: migration 0033 captures the live generated expression for events.search_tsv, drops the column, re-adds it wrapped with a new exclusion and rebuilds the index, and its own comment states the operational cost — a full heap rewrite under an ACCESS EXCLUSIVE lock with no lock_timeout, and relay downtime proportional to the size of events."
    entry_class: FACT
    evidence:
      - "migrations/0033_private_managed_agent_fts.sql"
  - statement: "launchpad/decisions/README.md states the supersession convention in one sentence: superseding a decision does not edit it — write a new record, set the old one's status to 'Superseded by ADR-YYYY', and say so in the new record's Supersedes."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/README.md"
  - statement: "That convention is observed exactly at the recorded revision: seven ADR files carry a 'Superseded by' status (five by ADR-0050, one by ADR-0052, one by ADR-0056), and the three superseding records' supersedes fields together name exactly those same seven — ADR-0050 names ADR-0001, ADR-0002, ADR-0003, ADR-0004 and ADR-0015; ADR-0052 names ADR-0019; ADR-0056 names ADR-0039."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0050-canonical-corpus-supersedes-handbook.md"
      - "launchpad/decisions/ADR-0052-delegated-authority-and-feature-batching.md"
      - "launchpad/decisions/ADR-0056-fork-owned-drop-branch-ci.md"
      - "launchpad/decisions/ADR-0001-handbook-repository-location-and-publication-target.md"
      - "launchpad/decisions/ADR-0019-review-checks-gate-only-when-deterministic.md"
      - "launchpad/decisions/ADR-0039-app-token-authors-drop-pr.md"
  - statement: "An ADR may also be narrowed without being superseded: ADR-0012 carries an amendments front-matter key and an in-body 'Amendment 1' section extending the original decision, so amendment and supersession are two different recorded outcomes."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0012-inference-provider-boundary.md"
  - statement: "No automated check verifies the supersession convention: the only ADR-specific workflow, launchpad-adr-check.yml, runs adr_boundary_check.py, whose own docstring scopes it to ADR-0005's sanctioned-file list agreeing with AGENTS.md section 3 and to those exceptions actually being used — it reads no status or supersedes field of any record."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-adr-check.yml"
      - "launchpad/scripts/adr_boundary_check.py"
  - statement: "node.schema.json's status enum contains deprecated and retired alongside draft, active and flagged, so a corpus node has a schema-legal way to record that it has stopped being current."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "corpus-standard-deprecation owns the corpus-node lifecycle — when a node is deprecated, when it is retired, and why retirement is a status change rather than a deletion — and its own scope-and-omissions states that nothing in that deprecation lifecycle addresses product code."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/deprecation.md"
  - statement: "layers-configuration-relay-configuration already carries a 'Compatibility and deprecation' section describing both relay environment-variable cases in detail and stating that no other setting in that document has a deprecated or renamed predecessor at its own recorded revision."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/configuration/relay-configuration.md"
  - statement: "CONTRIBUTING.md states the event-kind stability rule as 'Adding a new feature means defining a new kind. No breaking changes to existing clients.', making addition rather than removal the sanctioned way to change the wire surface."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "corpus-standard-normative-language reproduces RFC 2119's definitions of MUST, MUST NOT, SHOULD, SHOULD NOT and MAY as the corpus's own keyword contract, so a policy node in this corpus need not restate them."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/normative-language.md"
  - statement: "corpus-template-policy requires a policy-shaped node to carry six sections — scope and authority, MUST, SHOULD, enforcement, exceptions and escalation, scope and omissions — in that relative order, with an H1 of the form '# Policy: <subject>' unless a narrower family template says otherwise."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/policy.md"
  - statement: "validate.py splits a node's text on the front-matter delimiter and binds the remainder to _body, which no other function reads, so no requirement stated in this node's prose is checked by anything."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Source-level deprecation markers are almost unused in this repository: there are zero #[deprecated] attributes across crates/ and desktop/src-tauri/src, zero @Deprecated annotations across mobile/lib, and exactly three @deprecated JSDoc tags across desktop/src and web/src."
    entry_class: FACT
    evidence:
      - "desktop/src/features/agents/ui/agentSessionTranscriptGrouping.ts"
      - "desktop/src/features/communities/types.ts"
      - "desktop/src/shared/ui/markdown/utils.ts"
      - "count_deprecation_markers(rust='crates/,desktop/src-tauri/src', dart='mobile/lib', ts='desktop/src,web/src') -> 0 Rust attributes, 0 Dart annotations, 3 TypeScript JSDoc tags, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "The repository has no single written policy governing how things are removed; what exists is a set of per-surface mechanisms that were each built for one removal and never generalized."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - ".github/workflows/ci.yml"
      - "launchpad/decisions/README.md"
      - "CONTRIBUTING.md"
      - "launchpad/docs/corpus/layers/configuration/relay-configuration.md"
    confidence: 0.75
  - statement: "The two environment-variable cases in config.rs together imply a consistent unwritten rule — a removal whose old input could silently produce wrong behaviour fails startup, while a removal whose old input can only produce a stale belief warns and continues."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/config.rs"
    confidence: 0.7
  - statement: "Issue #911's Definition of Done requires this node to state scope and authority/source of the policy, to separate MUST requirements from SHOULD guidance, to define enforcement/checks and an exception/escalation process, and to link decisions or higher-order policy instead of duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#911 definition of done"
  - statement: "What is guaranteed while a thing still exists — the compatibility half of the same subject — belongs to a separate open task for governance/compatibility-policy.md, which is unmerged at this node's authoring time."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#908"
  - statement: "The gap that let .env.example advertise a variable Config::from_env never read is tracked as an open issue about nothing comparing the two, which records that the drift has already shipped twice."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#2034"
  - statement: "This node's id follows the settled directory-plus-stem form rather than the corpus- prefix that standards/naming.md still mandates, because the mismatch between that rule and the merged corpus is itself an open issue."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#2029"
relationships:
  - type: depends-on
    target: corpus-agents
  - type: implements
    target: corpus-template-policy
  - type: references
    target: corpus-standard-deprecation
  - type: references
    target: corpus-standard-normative-language
  - type: references
    target: layers-configuration-relay-configuration
---

# Policy: removing things from Buzz

How a thing that exists in this repository stops existing — an environment variable
the relay no longer reads, an API surface withdrawn from clients, a database
structure dropped, a decision replaced. This node is about **removal**: retirement,
sunset, supersession. What a consumer is guaranteed *while* a thing still exists is
the compatibility question and belongs to `governance/compatibility-policy.md`.

**Read the first line of *Scope and authority* before treating any MUST below as
established.** Roughly half of this node's rules restate a mechanism that already
exists in the tree and was opened to write them down; the rest are this node's own
proposal, and the two are marked apart rather than blended.

## Scope and authority

**This node governs** how a removal is carried out in `launchpad-26/buzz`: what an
author owes the people who still depend on the thing being removed, what the removal
must leave behind so the removal stays removed, and where a case these rules do not
reach is raised.

**There is no prior written deprecation policy in this repository to derive from.**
That was checked rather than assumed. What exists instead is four unrelated
mechanisms, each built for one removal:

| Surface | The mechanism that exists | Where |
|---|---|---|
| Relay environment variables | An inert-variable list plus a startup warning; separately, a hard startup error for a renamed variable | `crates/buzz-relay/src/config.rs` |
| Client API tokens | A CI job that fails the build if retired identifiers reappear | `.github/workflows/ci.yml`, `dead-token-guard` |
| Database structures | Forward-only migrations; a removal is a new file that drops and re-creates | `migrations/`, `crates/buzz-db/src/runtime/migration.rs` |
| Decisions | A superseding record plus a reciprocal `status:` back-reference on the old one | `launchpad/decisions/README.md` |

**So this node's authority is derived, and it is derived twice over.**

- **Where a MUST restates one of those four mechanisms**, the authority is the
  mechanism — the code, the workflow, the migrator, the recorded convention. Those
  rules are not this node's invention and it could not repeal them.
- **Where a MUST or SHOULD generalizes across the four**, the authority is this node
  and nothing else. Issue #911 asked for a policy with a MUST/SHOULD split and an
  escalation route; it did not supply the content. Attributing this node's own
  generalizations to the issue would be dressing a decision up as something somebody
  said. Those rules are offered for a reviewer to accept or replace, and each one
  names the observation it generalizes from so the reasoning stays checkable.

Every rule below is labelled **[derived]** or **[proposed]** on that basis.

**Precedence.** Where this node and executing code, a workflow, `node.schema.json`,
`validate.py`, an accepted ADR or `AGENTS.md` disagree, **they win** — this one has
drifted and should be fixed. Where it and a node that owns a specific surface
disagree about that surface, **the specific node wins**: `relay-configuration` owns
the relay's settings, `corpus-standard-deprecation` owns corpus nodes.

**Keyword meanings** are RFC 2119's, as already adopted corpus-wide by
`corpus-standard-normative-language`. This node does not restate them.

**For each of these, read the owner rather than this page:**

| Subject | Owner |
|---|---|
| Deprecating and retiring a **corpus node** (document lifecycle) | `launchpad/docs/corpus/standards/deprecation.md` |
| The two relay environment-variable cases, setting by setting | `launchpad/docs/corpus/layers/configuration/relay-configuration.md`, *Compatibility and deprecation* |
| What MUST / SHOULD / MAY mean | `launchpad/docs/corpus/standards/normative-language.md` |
| Creating, updating and retiring a node procedurally | `launchpad/docs/corpus/AGENTS.md` |
| The `status` field across all five values | `launchpad/docs/corpus/standards/status.md` |
| How a decision is superseded | `launchpad/decisions/README.md` |
| What is guaranteed while a thing still exists | `governance/compatibility-policy.md` |

## What removal actually looks like here

Five worked examples across the four surfaces above — the relay's environment
variables supply two, because it handles two removals in opposite ways. All were
opened directly. They are the evidence the rules below generalize from, and they are
drawn from this repository rather than invented, because an invented example cannot
go stale and so was never tested against anything.

### 1. An inert environment variable — warn and continue

`crates/buzz-relay/src/config.rs` holds a two-element constant:

```
INERT_MEDIA_READ_AUTH_VARS = [ BUZZ_REQUIRE_MEDIA_GET_AUTH, BUZZ_REQUIRE_MEDIA_READ_AUTH ]
```

Media reads are unconditionally authenticated now, so neither variable is read for
any decision. `Config::from_env` walks the list and emits one `warn!` per variable
found set, naming it, stating that `GET`/`HEAD` on `/media/*` always require Blossom
`t=get` auth plus relay membership, telling the operator to remove it, and adding
that a value of `false` does not re-open unauthenticated media reads.

**The stated rationale is the load-bearing part, and it is about a person, not
about code.** The constant's own doc comment says an operator still setting either
variable — *"especially to `false`"* — holds a belief about their deployment that
is no longer true. That is why the mechanism exists at all: the code is already
correct without it. What is wrong is somebody's mental model of a running system,
and only a message reaches that.

Three unit tests in the same file hold the behaviour: the warning fires when the
variable is set to `false` (the case that matters), the never-read alias warns too,
and unrelated variables stay quiet.

**One of the two variables is a deprecation that shipped as drift.**
`BUZZ_REQUIRE_MEDIA_READ_AUTH` was documented in `.env.example` as an accepted
alias, and the relay never read it. So the removal notice describes a variable the
code had no handling for in the first place, and an operator could have set it for
its entire documented life with no effect whatsoever. Nothing compares `.env.example`
against `Config::from_env`; that gap is open as #2034, which records that the drift
has already shipped twice.

**What the same change got right is worth naming next to what it got wrong.** The
removal landed as one commit — `769ac70b7`, *fix(media): require authenticated
reads (#4610)* — touching eighteen files: the relay code, `.env.example`,
`docs/admin/README.md`, `TESTING.md`, the Helm chart's `values.yaml`,
`values.schema.json` and `NOTES.txt`, the desktop Tauri media commands, and the
conformance and end-to-end tests. Nothing describing the removed flag was left
behind in a tree the author did not own. That breadth is what **D3** generalizes;
the alias that was never read is what **D3** cannot catch.

### 2. A renamed variable with changed units — hard error

The same file refuses `BUZZ_REPLICA_HEAD_MAX_AGE_SECS` outright, returning a
`ConfigError::InvalidValue` naming the replacement `BUZZ_REPLICA_READ_MAX_AGE_MS`.
The inline comment gives the reason: the old name was seconds, the new one is
milliseconds, and silently honouring the old name would apply a budget a thousand
times larger than intended.

**Two removals, two opposite actions, in one function.** The difference is not
severity of the feature; it is whether the operator's stale input can still change
behaviour. A `false` on an unread variable cannot — so the relay warns and starts. A
number on a renamed variable can — so the relay refuses to start. That contrast is
the clearest thing this repository has to a removal principle, and it is nowhere
written down. It is generalized as **D2** below, marked `[proposed]`.

### 3. A completed removal, guarded — `dead-token-guard`

`.github/workflows/ci.yml` runs a job that greps four retired API-token
identifiers — `TokenScope`, `MintTokenResponse`, `hasApiToken`, `spr_tok_` — across
a fixed path set and exits 1 on any match. Relay crates are excluded on purpose,
with a comment saying so: they still use token auth internally.

This is the only job in `.github/workflows/` whose purpose is to keep a removal
removed, and it is the model D4 generalizes. Of the four mechanisms, it and the
migrator's checksum abort are the only two a machine holds — and only this one was
built on purpose to hold a removal, where sqlx's checksum check protects migration
integrity generally and catches an edited removal as a side effect.

**Two things a reader should know before copying it.** First, the guard works: at
the recorded revision those four patterns appear nowhere in the repository except
in the guard's own `PATTERNS` string. Second, the guard's own comment says it covers
"desktop, mobile, docs, or config", and its `PATHS` list names only
`desktop/src/`, `desktop/tests/`, `mobile/test/`, `mobile/lib/` and `.env.example`.
There is no `docs/` path and no `web/` path. The web client and the docs tree are
outside a guard described as covering them. Because the patterns are absent
everywhere today, the gap is latent rather than live — a reintroduction into
`web/src` would pass CI.

### 4. Decisions — supersede, never edit

`launchpad/decisions/README.md` states it in one sentence: superseding a decision
does not edit it. Write a new record, set the old one's `status` to
`Superseded by ADR-YYYY`, and say so in the new record's `Supersedes`.

The convention holds exactly at the recorded revision. Seven records carry a
`Superseded by` status — five by ADR-0050, one by ADR-0052, one by ADR-0056 — and
those three superseding records' `supersedes:` fields together name precisely those
same seven. Both halves of every pair are present; none is one-sided.

**Supersession is not the only recorded outcome.** ADR-0012 carries an `amendments`
front-matter key and an in-body *Amendment 1* extending the original decision to a
new surface. A decision may be narrowed or extended without being replaced, and the
two are recorded differently.

**Nothing checks any of it.** The only ADR-specific workflow,
`launchpad-adr-check.yml`, runs `adr_boundary_check.py`, whose docstring scopes it
to ADR-0005's sanctioned-file list agreeing with `AGENTS.md` §3 and to those
exceptions actually being used. It reads no record's `status` or `supersedes`. The
seven reciprocal pairs above are seven pairs of authors having been careful.

### 5. Database structures — forward-only, so removal is re-creation

Migrations are applied by a single embedded sqlx `Migrator` over `migrations/`, and
the directory contains no `.down.sql` file of any kind. There is no reverse.
Multiple files carry an explicit comment that a published migration must not change
checksum or sqlx aborts startup with a `VersionMismatch`, which is why a later
change is written as a new additive file rather than an edit to an old one.

So **removing a database structure is a forward operation that drops and
re-creates.** Migration 0033 is the worked case: PostgreSQL cannot alter a generated
expression in place, so it captures the live expression for `events.search_tsv`,
drops the column, re-adds it wrapped with a new exclusion, and rebuilds the GIN
index. Its own comment states the cost honestly — a full heap rewrite under an
`ACCESS EXCLUSIVE` lock inside the migration transaction, no `lock_timeout`, and
relay downtime proportional to the size of `events`. That disclosure is the
behaviour **G3** generalizes.

### The wire surface, for contrast

`CONTRIBUTING.md` states that adding a feature means defining a new event kind, with
"No breaking changes to existing clients." The sanctioned move on the Nostr surface
is addition, not removal, so a kind is not deprecated so much as left unused. This
node does not extend to the wire protocol beyond noting that the rules below were
not written with it in mind.

## MUST

Each rule is labelled with the source of its authority. `[derived]` means it
restates a mechanism that already exists in this repository, cited in the ledger.
`[proposed]` means it is this node's own generalization, unratified, and a reviewer
may reject it without contradicting anything else in the tree.

| # | Requirement |
|---|---|
| **D1** | A removal MUST leave the removed thing's old input reachable by whoever still holds it, and MUST tell them what changed. Deleting the handling silently is the failure mode every mechanism above exists to avoid. Enforced by nothing; `config.rs` is the worked instance. `[derived]` |
| **D2** | Where a stale input can still change behaviour, the removal MUST fail closed — refuse to start, or refuse the operation, naming the replacement. Where a stale input can only produce a false belief, the removal MUST warn and continue. `config.rs` does exactly this in two adjacent cases; nothing enforces the rule across any other surface. `[proposed]` |
| **D3** | A removal MUST NOT leave documentation describing the removed thing as live, and the reconciliation MUST happen in the same change as the code. Commit `769ac70b7` is the worked instance: eighteen files, including `.env.example`, `docs/admin/README.md` and the Helm chart's `values.yaml`, moved together with the relay change. The never-read alias is the counter-example of what happens when they drift instead (#2034). Enforced by nothing. `[derived]` |
| **D4** | A removal that must stay removed MUST be given a mechanical guard naming the retired identifiers, and that guard's path list MUST cover every tree the identifiers could return to. `dead-token-guard` is the model and also the illustration of the second clause: its own comment claims a `docs/` scope its `PATHS` list does not provide. `[proposed]` |
| **D5** | A decision MUST be superseded by a new record, never edited. The superseded record's `status` MUST become `Superseded by ADR-YYYY` and the new record's `supersedes` MUST name it. Both halves, or the pair is one-sided and unfindable from the side a reader arrives on. Stated in `launchpad/decisions/README.md`; no check verifies it. `[derived]` |
| **D6** | A database structure MUST be removed by a new forward migration. A published migration file MUST NOT be edited, because sqlx aborts startup on a checksum change. `[derived]` |
| **D7** | A removal that imposes operational cost — downtime, a table rewrite, a lock — MUST state that cost in the artefact that causes it, where the operator will meet it. Migration 0033's header is the worked instance. `[derived]` |
| **D8** | A corpus node is removed under `corpus-standard-deprecation`, not under this node, and MUST be retired by status change rather than deletion. This node does not restate that procedure and MUST NOT be read as an alternative to it. `[derived]` |
| **D9** | Every removal rule this node states MUST name what enforces it, or state that nothing does. Two of the four mechanisms above are held by a machine and two by a person reading a diff; saying which is which is the point, because "there is a policy" and "something checks the policy" are different claims. `[proposed]` |

## SHOULD

| # | Guidance |
|---|---|
| **G1** | A removal SHOULD name its replacement in the message a holder of the old thing actually sees, not only in a changelog. Both `config.rs` cases do this — the hard error names `BUZZ_REPLICA_READ_MAX_AGE_MS`, the warning names the behaviour that replaced the flag. `[derived]` |
| **G2** | A removal notice SHOULD address the belief, not just the fact. "This is no longer read" leaves an operator wondering whether `false` still helps; "a value of `false` does not re-open unauthenticated media reads" does not. The relay's warning is written the second way deliberately. `[derived]` |
| **G3** | A removal SHOULD disclose its own costs and limits rather than only its benefits. Migration 0033 states that non-stock indexes and storage parameters on the dropped column are not captured or replayed — the reader who needed to know that would never have guessed it. `[derived]` |
| **G4** | A removal SHOULD be exercised by a test asserting the *transitional* behaviour, not only the end state. The three `inert_env_vars` tests assert what happens to an operator who still has the old variable; a test of the new behaviour alone would pass with the warning deleted. `[derived]` |
| **G5** | Removals SHOULD be made one at a time. Batching them makes the per-removal decisions above — which fail mode, which guard, which documentation — hard for a reviewer to check individually, and that review is the only thing checking them at all. `[proposed]` |
| **G6** | Source-level deprecation markers (`#[deprecated]`, `@deprecated`, `@Deprecated`) SHOULD be used where a symbol is on its way out and a compiler or linter can carry the message. They are almost unused here — zero in Rust, zero in Dart, three JSDoc tags in TypeScript — so this is guidance about a road not taken, not a description of practice. `[proposed]` |

## Enforcement

**Of the rules on this page, exactly two have any automated enforcement, and each
only on its own surface.** D4 is held by `dead-token-guard`, which fails CI if four
specific retired identifiers reappear in five specific paths. D6 is held by sqlx,
which aborts startup on a checksum change — not a removal check by design, but it
catches an edited published migration all the same. Everything else — D1, D2, D3,
D5, D7, D8, D9 and every SHOULD — is enforced by a person reading a pull request.
The two unit-test rows below are narrower than they look: they hold the behaviour of
two named variables, not the rule.

Stated per surface, because "nothing enforces this" is too coarse to act on:

| Rule | What actually checks it | What it does not reach |
|---|---|---|
| D1, D2 (env vars) | `config.rs`'s own unit tests, for the two variables named in them | Any other setting, and any other surface |
| D3 (docs match code) | Nothing. `.env.example` and `Config::from_env` are never compared (#2034) | Everything |
| D4 (guard the removal) | `dead-token-guard`, for four patterns in five paths | `web/`, `docs/`, and every removal that has no guard |
| D5 (ADR supersession) | Nothing. `adr_boundary_check.py` reads only ADR-0005's file list | Every `status:` and `supersedes:` field in `launchpad/decisions/` |
| D6 (forward-only) | sqlx itself — a checksum change aborts startup | Whether the forward migration is *correct*, only that it is stable |
| D7 (state the cost) | Nothing | Everything |
| D8 (corpus nodes) | Nothing; `corpus-standard-deprecation` says the same of itself | Everything |

**What a green corpus validation run does not establish about this node.** The check
is `python3 launchpad/project-intelligence/corpus/validate.py`. It parses front
matter and discards the body: `_load_frontmatter` splits on the delimiter and binds
the remainder to `_body`, which no other function reads. So a passing run does not
establish that the six required sections are present, that MUST and SHOULD are
separated, that any rule carries an identifier, that any `[derived]` label is
accurate, or that a cited file says what the statement above it claims — citation
checking is structural, and the file is never opened for comparison. A green run
means this node is well-formed. It says nothing about whether any removal in this
repository followed it.

## Exceptions and escalation

**A rule you cannot follow is recorded, not worked around.** Name the rule and the
reason in the pull request making the removal. Nothing catches the omission, so an
unrecorded exception is indistinguishable from an oversight.

**D6 has no exception.** Editing a published migration is not a judgement call with
a downside; sqlx aborts startup on the checksum change, and the failure lands on
every brownfield deployment rather than on the author. If a published migration is
wrong, the fix is a new file.

**D2's classification is the case that will be disputed**, because deciding whether
a stale input "can still change behaviour" is a judgement about the code, not a
lookup. When it is genuinely unclear, choose the hard failure: an operator who is
stopped can read the message, and an operator who is not stopped may never learn
they were wrong. Record the call in the pull request either way.

**A removal that cannot be made safely is not this node's to authorise.** If the
only correct removal would break a consumer, that is a compatibility decision and
it goes to a `type:adr` issue under `launchpad/AGENTS.md`'s decision lifecycle, not
into a diff. This node governs how a sanctioned removal is carried out; it does not
sanction one.

**A case none of this reaches is escalated, not invented.** Raise it as an issue
against parent Feature #619 describing the removal that was needed and the rule
that did not fit. Do not widen a `[proposed]` rule locally to cover it — a rule each
author quietly reinterprets has stopped being one, and no check will notice.

## Scope and omissions

**This node covers** how a removal is carried out in this repository: the four
mechanisms that exist today (inert environment variables, the dead-token CI guard,
forward-only migrations, ADR supersession), what each obliges an author to do, the
rules generalized from them, which of those rules are derived and which are this
node's own proposal, and what a passing validation run does not establish about any
of it.

**Its declared relationships**, every target confirmed present on `origin/launchpad`
at the recorded revision rather than in this worktree: `depends-on:
corpus-agents`, because the evidence and authoring rules this node is written under
are that node's and not its own; `implements: corpus-template-policy`, because this
is a template instance of that policy shape; and `references` toward
`corpus-standard-deprecation`, `corpus-standard-normative-language` and
`layers-configuration-relay-configuration`, the three nodes this one defers to
rather than restates. No edge to #908 — the file does not exist on the merge target,
so naming its id would be a hard validation error there however cleanly it resolves
anywhere else.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owner |
|---|---|
| What is guaranteed while a thing still exists — the compatibility half of the subject | `governance/compatibility-policy.md` |
| Deprecating and retiring a **corpus node** | `corpus-standard-deprecation` |
| The two relay environment-variable cases, setting by setting | `layers-configuration-relay-configuration` |
| The `status` field across all five corpus values | `corpus-standard-status` |
| Nothing comparing `.env.example` against `Config::from_env` | #2034 |
| The `corpus-` id-prefix rule that most merged nodes no longer follow | #2029 |
| Removal on the Nostr wire surface — event kinds, NIPs, protocol messages | No corpus task found for this surface as of this writing; `CONTRIBUTING.md` states only that addition is the sanctioned change |
| Versioning, release notes and changelog practice around a removal | No corpus task found for this surface as of this writing |

Those issue numbers were looked up individually, not inferred from a range.

**Expected but not verified when this node was written:**

- **No removal was performed to test any rule here.** Every rule is written against
  a mechanism that was opened and read, not against a removal this author carried
  out. D2's fail-closed/warn split in particular is generalized from exactly two
  cases in one function.
- **The `[derived]`/`[proposed]` labels are this author's classification and are not
  checked by anything.** A reviewer who thinks a rule labelled `[derived]` reaches
  further than its cited mechanism should say so; that is the disagreement this
  labelling exists to make possible, not one it settles.
- **`dead-token-guard`'s path gap was confirmed by reading `PATHS`, not by running
  CI.** The claim that a reintroduction into `web/src` would pass is read off the
  path list; no branch was pushed to observe it.
- **Whether any other surface has a removal mechanism was checked by search, not
  exhaustively.** `.github/workflows/` was swept for deprecation vocabulary and
  `dead-token-guard` was the only removal-enforcement job found; a guard written
  without any of those words would not have surfaced.
- **The relationship to #908 is asserted from its issue title, not its content.**
  `governance/compatibility-policy.md` does not exist on `origin/launchpad` and is
  not a legal relationship target. Whether its eventual scope divides cleanly from
  this node's at the line drawn here is unverified, and reconciling the two belongs
  to whoever merges second.
- **`audiences` includes `operator`, which is a judgement call.** The relay's
  inert-variable warning reaches an operator directly and D7 exists for them, so
  they are addressed here in a way they are not by `corpus-standard-deprecation`,
  which excluded both `operator` and `developer`. If a reviewer thinks this node is
  authoring-side only, the field should shrink.
