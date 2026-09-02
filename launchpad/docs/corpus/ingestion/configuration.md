---
id: ingestion-configuration
type: ingestion
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "CONTRACT.md's own provenance table names FACT as a claim 'Directly observed in code, config, tests, docs, git history or runtime output' -- config is its own named source category there, listed separately from code."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/CONTRACT.md"
  - statement: "code-references.md's own Scope and authority section states it governs 'every citation, in any node's evidence ledger, that names code in a repository' -- its stated scope is code, and it neither states nor disclaims a configuration-specific scope anywhere in its own text."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/code-references.md"
  - statement: "This repository's .gitignore excludes .env, .env.local and .env.*.local from version control while .env.example -- a template carrying placeholder/dev-only values only -- is committed at the repository root, and the root AGENTS.md's Getting Started section instructs `cp .env.example .env` as the first setup step."
    entry_class: FACT
    evidence:
      - ".gitignore"
      - ".env.example"
      - "AGENTS.md"
  - statement: "Two separately committed files state two different Rust version numbers for two different declared purposes: Cargo.toml's [workspace.package] table states rust-version = \"1.88.0\" (a minimum-supported-version floor), while the separately committed rust-toolchain.toml states channel = \"1.95.0\" under its own [toolchain] table."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
      - "rust-toolchain.toml"
  - statement: "A rust-toolchain.toml's channel field is rustup's own toolchain-pinning override, so absent an explicit environment override this repository's actually-invoked Rust toolchain is 1.95.0, not the 1.88.0 floor Cargo.toml's rust-version alone would suggest to a reader who stopped at that one file."
    entry_class: INFERENCE
    evidence:
      - "rust-toolchain.toml"
      - "Cargo.toml"
    confidence: 0.8
  - statement: "The root AGENTS.md states that even on a shell whose PATH would otherwise resolve a Homebrew-installed flutter/dart/lefthook first, the pre-push hook 'self-pins regardless': bin/.lefthookrc, sourced by the generated .git/hooks/* dispatchers, prepends the Hermit bin/ to PATH and pins LEFTHOOK_BIN, so hook lane subprocesses resolve the Hermit-pinned toolchain even when an unactivated shell has Homebrew first."
    entry_class: FACT
    evidence:
      - "AGENTS.md:137-145"
  - statement: "bin/.lefthookrc's own comment states its two jobs explicitly: pin dispatch to the Hermit-managed lefthook (bin/lefthook -> .lefthook-2.1.3.pkg) 'even when a newer lefthook is on PATH (e.g. Homebrew)', and prepend the Hermit bin/ to PATH so every lane subprocess 'resolves the repo's pinned toolchain, not whatever the invoking shell had first (e.g. Homebrew flutter)'."
    entry_class: FACT
    evidence:
      - "bin/.lefthookrc"
  - statement: "crates/buzz-workflow/src/schema.rs's own module doc comment states plainly: 'Workflow definitions are authored in YAML and stored as canonical JSON' -- a workflow definition's committed form is a parsing/schema module, not a workflow instance; a specific community's actual configured workflow exists as event content once submitted, never as a file in this repository's tree."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs"
  - statement: "layers-configuration-secrets.md (merged) already distinguishes a config file's checked-in placeholder from a real deployment's actual value in its own evidence: it cites config.rs's DATABASE_URL fallback as 'the same dev-only placeholder as .env.example's DATABASE_URL', and separately states that no Rust source under crates/ reads .env.example's documented TYPESENSE_API_KEY/TYPESENSE_URL variables at all -- a config entry present in a committed file that is not load-bearing for anything."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/configuration/secrets.md"
  - statement: "layers-configuration-validation.md (merged) grounds every configuration effect it claims in a specific parsing or validation call site inside crates/buzz-relay/src/config.rs (for example BUZZ_DRAIN_JITTER_MS's clamp-to-maximum behavior), never in a variable's mere appearance in .env.example or any other document."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/configuration/validation.md"
  - statement: "development-hermit.md (merged) documents that this repository uses Hermit to pin toolchain versions in bin/, activated once per shell with `. ./bin/activate-hermit`, and that using it is 'optional but recommended' per CONTRIBUTING.md -- a contributor who skips activation must instead match the prerequisites table's version floor by hand."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/hermit.md"
  - statement: "code-references.md's generic citation-shape rules (bare-path resolution from the repository root, GitHub-link SHA pinning, the ban on a column or symbol fragment) say nothing about whether a cited artifact is itself checked into the repository the citation resolves against, whether its literal text is the value actually in effect, or whether its mere presence establishes that anything reads it -- three questions a configuration citation raises that an ordinary source-code citation does not, because source code present in the tree is, definitionally, the code that runs, while a configuration artifact's committed text and its runtime effect are two separate facts that can diverge."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/standards/code-references.md"
      - "launchpad/project-intelligence/CONTRACT.md"
    confidence: 0.85
  - statement: "This node follows templates/policy.md's six-section shape (Scope and authority, MUST, SHOULD, Enforcement, Exceptions and escalation, Scope and omissions) rather than templates/configuration.md's settings-table shape, because #956's own Definition of Done tail matches policy.md's Required sections almost exactly (state scope/authority, separate MUST from SHOULD, define enforcement/exceptions, link decisions instead of duplicating them), while templates/configuration.md's own body states its shape is for cataloguing a settings surface -- variable names, defaults, effects, as a structured-entries table -- and this node catalogues no settings surface of Buzz's own product; agents-invariants (#649, merged, under this same Feature #620) made the identical template choice for an analogous 'single canonical policy node' Objective."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/policy.md"
      - "launchpad/docs/corpus/templates/configuration.md"
      - "launchpad/docs/corpus/agents/invariants.md"
    confidence: 0.8
  - statement: "Parent Feature #620's stated Outcome is 'Agents can deterministically navigate, evidence, draft, validate and maintain corpus nodes using documented procedures,' and its Out of scope explicitly excludes 'implementation of the knowledge-crate runtime' -- this node's subject is agent behavior when using configuration as evidence, not a runtime pipeline."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 outcome and out-of-scope text"
  - statement: "Issue #956's own Definition of Done requires this node to state scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define enforcement/checks and exception/escalation process, and link decisions or higher-order policy instead of duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#956 definition of done"
  - statement: "Issue #956's Objective calls this node 'the single canonical policy node for configuration' -- identical phrasing to issue #1332's Objective for the unrelated templates/configuration.md task (a template, not a content node), which templates/configuration.md's own evidence ledger already records as boilerplate the planning apparatus applied uniformly rather than a considered classification specific to either task."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#956 Objective, compared against launchpad/docs/corpus/templates/configuration.md's recorded quote of launchpad-26/buzz#1332 Objective"
relationships:
  - type: depends-on
    target: corpus-agents
  - type: implements
    target: corpus-template-policy
  - type: references
    target: corpus-standard-code-references
  - type: references
    target: layers-configuration-secrets
  - type: references
    target: layers-configuration-validation
  - type: references
    target: development-hermit
---

# Policy: configuration as evidence in corpus authoring

How an agent or reviewer treats a configuration artifact -- an environment variable,
`.env.example`, the `Justfile`, a Hermit toolchain pin under `bin/`, a workflow definition
authored in YAML, or a `Cargo.toml`/`package.json` setting -- as a citable evidence source
while drafting or reviewing **any** corpus node's claim. This is not about cataloguing a
configuration surface as a node's own subject; see *Scope and authority* for that boundary.

## Scope and authority

**This node governs** three distinctions a configuration citation raises that an ordinary
source-code citation does not: whether the cited artifact is itself checked into the
repository the citation resolves against, whether its literal text is the value actually in
effect, and whether its mere presence establishes that anything reads it. It applies
whenever an agent or reviewer cites configuration as evidence for a claim in **any** corpus
node -- not only a node whose subject is configuration itself.

**It does not govern** citation *shape* -- bare-path resolution from the repository root,
GitHub-link SHA pinning, the ban on a column or symbol fragment. `code-references.md`
governs that, unconditionally, for every citation naming code **or** configuration in a
repository, and this node changes none of it: a configuration file resolves and validates
exactly like any other repository path. **It does not govern** cataloguing a specific
configuration surface as a node's own subject -- a settings table of one service's
environment variables, its defaults, and its effects is `templates/configuration.md`'s
shape, already instantiated by the `layers/configuration/*` nodes. This node's own subject
is agent behavior during evidence-gathering, not a settings catalog.

**Its authority is derived, not original.** `CONTRACT.md`'s own FACT definition already
names "config" as its own evidence-source category, distinct from "code";
`code-references.md` already governs the shape half unconditionally; `AGENTS.md` already
governs the FACT/INFERENCE/TEAM_KNOWLEDGE contract and node creation generally. What this
node adds is the half none of those three states: the three configuration-specific
distinctions above. That half is enforced by review, the same way `code-references.md`
names its own MUST 4, MUST 8 and MUST 9 as review-only.

**Where this node and `code-references.md`, `node.schema.json`, or `AGENTS.md` disagree,
they win** -- this one has drifted and should be fixed.

| For | Read |
|---|---|
| Citation shape mechanics (bare path, GitHub-link pinning) | `launchpad/docs/corpus/standards/code-references.md` |
| FACT/INFERENCE/TEAM_KNOWLEDGE class rules | `launchpad/docs/corpus/schema/node.schema.json` |
| Cataloguing a specific configuration surface as a node's own subject | `launchpad/docs/corpus/templates/configuration.md` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| This repository's own Hermit toolchain-pinning practice, worked | `launchpad/docs/corpus/development/hermit.md` |
| This repository's own secret-configuration surface, worked | `launchpad/docs/corpus/layers/configuration/secrets.md` |
| This repository's own configuration-validation mechanism, worked | `launchpad/docs/corpus/layers/configuration/validation.md` |

## MUST

| # | Requirement |
|---|---|
| **CE1** | A claim about a configuration artifact's **effective** value MUST cite the source that determines that value when the process or tool actually runs, not merely a source that states an intended, minimum, or example value, whenever the two could diverge. `rust-toolchain.toml`'s pinned `channel` -- not `Cargo.toml`'s `rust-version` floor alone -- is what a build actually invokes; `bin/.lefthookrc`'s pinning behavior -- not a bare `which <tool>` run on an unactivated shell -- is what a pre-push hook subprocess actually resolves. |
| **CE2** | A claim MUST NOT cite a locally-created or gitignored configuration artifact (a developer's own `.env`, an ad hoc local override) as though it were repository content available to every reader and to `validate.py`, because it resolves to nothing in the tree a reviewer or the validator can open. Cite the checked-in template or pin instead (`.env.example`, `bin/hermit.hcl`, `rust-toolchain.toml`, `bin/.lefthookrc`), and where the claim is genuinely about a live runtime value rather than the template, say plainly that the runtime value itself was not opened. |
| **CE3** | A `FACT` that a configuration file or variable has some effect MUST cite the code path, hook, or mechanism that actually reads and acts on it -- never merely the file's presence or a name's appearance in a documented list. `layers-configuration-secrets.md`'s own finding that `.env.example` documents `TYPESENSE_API_KEY`/`TYPESENSE_URL` variables no Rust source in this repository reads is the worked counterexample: presence in a config file is never, on its own, evidence of effect. |
| **CE4** | A claim about a specific community's configured workflow (its trigger, steps, or enabled state) MUST NOT cite a repository path, because a workflow definition is authored as YAML and exists as event content once submitted -- never as a file in this repository's tree, per `crates/buzz-workflow/src/schema.rs`'s own module documentation. Cite the parsing/schema code for what the format permits in general; classify a claim about one community's actual configured instance as `TEAM_KNOWLEDGE` naming the query or person that supplied it, never as a `FACT` resting on a repository citation that does not exist. |
| **CE5** | An author gathering configuration evidence MUST NOT quote a live secret, key, token, or hostname value even when it is found in a locally-created file open for this purpose alone. This is the same discipline `templates/configuration.md`'s own secrets requirement holds a settings-table row to, extended here to citation practice during authoring generally, per `AGENT_PR_TEMPLATE.md`'s verification checklist, which binds a corpus node like any other tracked file. |
| **CE6** | Citing a configuration file's shape and location follows `code-references.md`'s rules unchanged -- this node restates none of them, and a conflict between the two is `code-references.md`'s to win, per its own stated precedence. |

## SHOULD

| # | Guidance |
|---|---|
| **CQ1** | An author SHOULD prefer citing the code or mechanism that loads or enforces a configuration value over the raw file alone when both exist, and SHOULD name, in the `statement` itself, exactly which one was opened. A statement that says "the environment variable" without naming the file or call site cannot be re-checked without the reviewer re-deriving the same search. |
| **CQ2** | Where a floor or example value (a prerequisites table, `.env.example`) and an authoritative pin or loader disagree or could diverge, an author SHOULD cite the authoritative source for an effective-value claim and name the floor or example separately as a floor, rather than silently picking whichever one was found first. |
| **CQ3** | An author who cannot open a configuration artifact directly -- a production deployment's actual environment, a live community's actual workflow content -- SHOULD classify the resulting claim `TEAM_KNOWLEDGE` and name the source, or omit the claim, rather than reasoning to an unstated value as an `INFERENCE` dressed as fact-adjacent. |
| **CQ4** | Worked examples SHOULD be drawn from this repository's own configuration surfaces rather than invented, per `templates/policy.md`'s own Q1. An invented example of "a config value that differs from its file" cannot go stale, which means it was never tested against anything real. |

## Enforcement

**Nothing automated enforces CE1-CE5.** Per `code-references.md`'s own Enforcement
section, `validate.py` discards a node's Markdown body before any check runs; nothing about
whether an effective value was actually verified, whether a cited artifact is genuinely
checked in, or whether a workflow claim was honestly classified is ever inspected
mechanically.

**What IS mechanically enforced** is inherited, not invented here: citation shape (CE6) is
`code-references.md`'s validator rules, unchanged; the `FACT`/`INFERENCE`/`TEAM_KNOWLEDGE`
field-shape rules an evidence entry above must satisfy are `node.schema.json`'s conditional
rules, run on every node regardless of subject.

**What a green `validate.py` run does NOT establish about this node's subject:**

| Not established | Consequence |
|---|---|
| That a cited configuration file's stated value is still the effective one | `rust-toolchain.toml` can be bumped without any citing node's text changing, and the citation still resolves |
| That an `.env.example` or similar citation was checked against the loading code per CE1/CE3 | An assumed effect passes identically to a verified one |
| That a workflow-YAML claim was not quietly promoted to `FACT` despite CE4 | A citation of `schema.rs` for a claim about one community's specific configured behavior still resolves to a real file |
| That CE2's local-vs-committed distinction was actually honored | A citation naming `.env.example` reads the same whether the author checked `.gitignore` first or not |

## Exceptions and escalation

**There is no exemption from CE1-CE6.** A claim that cannot meet one of them is not yet
ready to cite; it is rewritten to what can honestly be said, or reclassified per CQ3.

**A disputed application is a judgement, not an exception.** Whether a given file is
"authoritative" for a value under CE1, for instance, is recorded as a tension in the pull
request and decided by the reviewer. A repeated disagreement is filed as an issue against
this node, because a rule two people read differently is a defect in the rule.

**`status: flagged` is not the escape hatch.** It names an unresolved evidence conflict per
`ADR-0029`; it is not a substitute for meeting a requirement here.

**A case none of CE1-CE6 covers** -- a configuration source type not named in this node's
scope, for instance -- is escalated as an issue against parent Feature #620 describing the
citation that was needed and could not be written, not invented locally.

## Scope and omissions

**This node covers** the MUST/SHOULD rules for treating configuration -- environment
variables, `.env.example`, the `Justfile`, Hermit toolchain pins, workflow YAML, and
`Cargo.toml`/`package.json` settings -- as an evidence source during corpus authoring,
specifically the three angles `code-references.md`'s generic citation rules do not reach:
local-vs-committed, effective-vs-literal, and present-vs-load-bearing.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Citation shape mechanics for any code or configuration reference | `launchpad/docs/corpus/standards/code-references.md` |
| Cataloguing a specific configuration surface as a node's own subject | `launchpad/docs/corpus/templates/configuration.md`, and the `layers/configuration/*` nodes built from it |
| The `FACT`/`INFERENCE`/`TEAM_KNOWLEDGE` class definitions themselves | `launchpad/docs/corpus/schema/node.schema.json`, and the corpus-wide evidence standard |
| Creating, updating and retiring any corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |
| Secrets handling for the codebase generally, beyond a corpus node's own citation practice | Repository-wide practice, not a corpus concern |
| Concrete agent procedures for evidence-gathering and navigation generally, beyond configuration specifically | Sibling `ingestion/*` and `agents/*` tasks under parent Feature #620, none merged at this node's authoring time |

**Expected but not verified when this node was written:**

- **rustup's own toolchain-resolution precedence** -- that `rust-toolchain.toml` wins over
  `Cargo.toml`'s `rust-version` absent an explicit override -- rests on general rustup
  convention; rustup's own documentation was not opened in this session to independently
  verify that precedence order against a primary source.
- **Whether every configuration source type Buzz actually uses was surveyed.** The six
  named in this node's scope are the ones the parent task named, not an audited exhaustive
  list of every configuration mechanism in this repository.
- **No CI run has exercised this node.** All validator evidence above is local to this
  worktree.
- **Whether any sibling `ingestion/*` node, once drafted, declares a relationship toward
  this node** is that sibling's own edit to make, not something decided here.
