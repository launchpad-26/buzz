---
id: corpus-ingestion-source-code
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
  - statement: "corpus-standard-code-references states its own authority as citation format and pinning mechanics only -- which forms are permitted, how they are pinned and positioned, what a passing validation run does and does not establish -- and its own Enforcement section states that a green run does not establish 'that a citation supports its claim', because checking is structural."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/code-references.md"
  - statement: "corpus-standard-test-references' own Scope-and-omissions table names, verbatim, 'Citing the production source code a test exercises, as evidence of that code's own behavior' as a topic not covered there and owned by issue #1308."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/test-references.md"
  - statement: "Issue #1308 is titled 'task: document corpus standard for code references' and is the issue that shipped as corpus-standard-code-references; that document, read in full, contains no section addressing which claim a source-code citation supports (existence versus current-behavior) or how conditional compilation, macro expansion or test-only code bear on that -- the topic corpus-standard-test-references named as #1308's to cover was not actually filled by it. That gap is this node's real, non-duplicative scope."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/standards/code-references.md"
      - "launchpad/docs/corpus/standards/test-references.md"
    confidence: 0.85
  - statement: "desktop/src-tauri/build.rs emits `cargo:rustc-cfg=buzz_updater_enabled` only when both BUZZ_UPDATER_PUBLIC_KEY and BUZZ_UPDATER_ENDPOINT are set at build time, and separately emits `cargo:rustc-env=BUZZ_DESKTOP_BUILD_*` values only when their corresponding environment variables are present at build time -- so the same checked-in source text compiles into materially different runtime configuration depending on which environment variables were set when it was built."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/build.rs"
  - statement: "crates/buzz-datastore-tracing/Cargo.toml declares `proc-macro = true` -- a first-party proc-macro crate whose macro expansion at any call site is not present in the call site's own source text."
    entry_class: FACT
    evidence:
      - "crates/buzz-datastore-tracing/Cargo.toml"
  - statement: "`#[cfg(test)]` occurs 346 times across 256 files under crates/, gating code that is present in the checked-in source tree but compiled only into test builds, never into a release binary."
    entry_class: FACT
    evidence:
      - "grep_count('#[cfg(test)]', 'crates/**/*.rs') -> 346 matches across 256 files at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "ADR-0029 names code, config, schema and passing tests together as the executable evidence that outranks documentation, history or inference for a claim about how the system currently behaves -- it does not treat source code alone as sufficient by itself, or distinguish it from the other three."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "Issue #971's own Definition of Done requires this node to state scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define an enforcement/checks and exception/escalation process, and link decisions or higher-order policy instead of duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#971 definition of done"
  - statement: "Feature #620's stated outcome is that agents can deterministically navigate, evidence, draft, validate and maintain corpus nodes using documented procedures -- framing this node as ingestion guidance for the act of drawing evidence from source code, distinct from the standards track's citation-format contract."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 outcome"
relationships:
  - type: depends-on
    target: corpus-standard-code-references
  - type: depends-on
    target: corpus-standard-test-references
---

# Policy: citing source code as evidence of current system behavior

What a citation to this repository's source code actually establishes about the
*system's current behavior*, as distinct from the file merely existing -- and this
repository's own concrete cases (conditional compilation, macro expansion, test-only
code) where the gap between "the file reads this way" and "the system behaves this way"
is real rather than theoretical. Look up the section you need; this is reference
material, not a tutorial.

## Scope and authority

**This node governs** the claim a corpus author is entitled to make about the *system's
current behavior* when the cited evidence is source code, and the specific ways this
repository's own code can make that claim weaker than it looks: conditional compilation
baked in at build time, a macro invocation whose expansion is invisible at the call
site, and code that exists in the tree but is gated out of anything but a test build.

**Its authority is derived, not original**, in the same sense `templates/policy.md`
describes for every policy-shaped node: the structural half is already law
(`node.schema.json`, `validate.py`, CI); this node supplies the half no schema can hold
-- judgment about what a source-code citation actually proves.

**This node does not govern citation format or pinning.** Resolving a repository path,
rejecting an absolute or escaping one, and pinning a GitHub link to a full SHA are
`corpus-standard-code-references`' territory, declared there as "which forms are
permitted, which are forbidden, how they are pinned and positioned" -- unconditionally,
for every citation naming code, including the ones this node discusses. **This node does
not govern citing a test** -- which claim a test citation supports, and this
repository's flakiness/`#[ignore]` conventions, are `corpus-standard-test-references`'
territory. What is left, and what `corpus-standard-test-references`' own
Scope-and-omissions table names as unfilled by `corpus-standard-code-references`
(pointing at issue #1308, the issue that shipped as that document): *citing the
production source code a test exercises, as evidence of that code's own behavior* --
i.e., the source-code half of the same claim-shape question `corpus-standard-test-references`
already answers for tests.

**Where this node and `corpus-standard-code-references` or `corpus-standard-test-references`
disagree, they win** on their own subjects -- citation mechanics and test-citation
claim-shape respectively. Where either of them is silent on a question this node
answers, this node is not overriding them; it is filling the space they each name as
someone else's.

| For | Read |
|---|---|
| Citation format, pinning, and what a passing validation run checks | `launchpad/docs/corpus/standards/code-references.md` |
| Which claim a *test* citation supports, and test flakiness/staleness | `launchpad/docs/corpus/standards/test-references.md` |
| How evidence is ranked by claim type, and why executable evidence outranks documentation for a current-behavior claim | `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` |
| Finding the right source file or symbol to read in the first place | `launchpad/docs/corpus/agents/repository-navigation.md`, once merged |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| The policy shape this node follows | `launchpad/docs/corpus/templates/policy.md` |

If this document and any of those disagree, **they win** -- this one has drifted and
should be fixed.

## MUST

| # | Requirement |
|---|---|
| **SC1** | A citation to a source-code file or symbol MUST NOT, by itself, be read as evidence that the cited code executes in a running system -- only that the cited text exists in the repository at the cited path. `corpus-standard-code-references`' own table records that a passing check on a bare path or `path:line` citation proves the file exists and nothing about its contents; this node adds that even a citation a human has actually read and understood proves what the *text* does, not that the text is reachable, included in the build, or currently exercised. |
| **SC2** | A `FACT` that the system *currently behaves* a certain way, cited to source code that is built conditionally, MUST be checked against the actual build configuration the claim is about, not assumed from the source text alone. This repository's own `desktop/src-tauri/build.rs` compiles the same checked-in file into materially different runtime configuration depending on which `BUZZ_BUILD_*`/`BUZZ_UPDATER_*` environment variables were set at build time (`cargo:rustc-cfg=buzz_updater_enabled`, several conditional `cargo:rustc-env=...` lines) -- a citation to that file alone does not say which variant the claim describes. |
| **SC3** | A citation to code gated by `#[cfg(test)]` MUST NOT be used as evidence of production behavior. That code is present in the source tree -- 346 occurrences across 256 files in `crates/` at this node's recorded revision -- and is compiled only into test builds; a release binary never contains it. |
| **SC4** | A citation to a macro invocation whose expansion is not visible in the cited text MUST NOT be treated as evidence of the expanded behavior unless the author also opened the macro's own definition (or its expanded output) and says so in the `statement`. This repository ships a first-party proc-macro crate, `buzz-datastore-tracing` (`proc-macro = true`), whose call sites read as ordinary attributes or function calls but whose actual generated code lives entirely in the macro's own implementation. |
| **SC5** | A behavior claim MUST NOT wear the citation of a test that merely exercises the code as if it were a citation of the code's own text. Citing that a test passed is a claim about the test run (`corpus-standard-test-references`' territory); citing what the production code itself does requires opening and citing that code directly -- the two are different evidence for different halves of the same behavior claim, and one is not a substitute for the other. |

## SHOULD

| # | Guidance |
|---|---|
| **SQ1** | For citation shape and positioning, follow `corpus-standard-code-references`' own SHOULD guidance without restating it here; the one thing specific to a *behavior* claim is that the payoff for precision is larger than usual, because SC1-SC5 already limit what a source-code citation can prove -- a precise span is the difference between a reader being able to check the claim at all and not. |
| **SQ2** | For a current-behavior claim, prefer corroborating source code with a passing test or an observed runtime result over source code alone, per ADR-0029's ranking of code, config, schema and passing tests together as executable evidence -- source code shows what would happen if reached; a test or observation shows it was. |
| **SQ3** | When the cited code's behavior depends on a build-time environment variable, a feature flag, or which binary target compiles it, name that dependency in the `statement` rather than leaving the claim unscoped -- see SC2 and SC3. |
| **SQ4** | Prefer the innermost function that actually implements the behavior over a thin wrapper or re-export. A wrapper's own text does not show what it delegates to, and a reader comparing the citation against the `statement` needs the implementation, not the forwarding call. |

## Enforcement

**Nothing automated enforces any requirement on this page.** `validate.py`'s
`_load_frontmatter` splits a node's text on the frontmatter delimiter and discards the
body into a variable nothing else reads, for every node in every directory --
`templates/policy.md` states this and it holds identically for a node under `ingestion/`.
A source-code citation that violates SC1-SC5 validates exactly like one that does not,
provided its path resolves to a real file.

**What a green validation run does not establish about a source-code citation:**

| Not established | Consequence |
|---|---|
| That the cited code is reachable or ever called | Dead code cites cleanly |
| That the cited code is compiled into the artifact the claim is about | A `#[cfg(test)]`-gated or build-flag-gated file cites cleanly regardless |
| That a macro's expansion matches the `statement` | The call site's text is all that is checked to exist, never the expansion |
| That the citation is the narrowest span that actually supports the claim | A whole-file citation for a one-line claim validates the same as a precise range |

**Enforcement is the pull-request review**, exactly as `templates/policy.md` states for
every policy-shaped node: this document exists to give that reviewer something concrete
to check a source-code citation against.

## Exceptions and escalation

**There is no exemption from SC1-SC5.** Each names a real way a source-code citation can
overstate what it proves; none is a formatting preference that can be waived by
agreement in a node's body.

**A requirement whose application is disputed is a judgement, not an exception.** Record
the tension in the pull request; the reviewer decides. Persistent disagreement is filed
as an issue against this node rather than resolved locally.

**A case this node does not reach** -- for example, a language or build system this
repository does not currently use -- is escalated as an issue against parent Feature
#620 or Feature #605, describing the citation that was needed and could not be written,
rather than widened into here informally.

## Scope and omissions

**This node covers** what a source-code citation does and does not establish about the
system's *current behavior* specifically, and this repository's own conditional-
compilation, macro-expansion and test-only-code cases where that gap is concrete rather
than hypothetical.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Citation format, pinning, and repository-path/GitHub-link mechanics for any code citation, including the ones discussed here | `corpus-standard-code-references` (#1308) |
| Which claim a *test* citation supports, and this repository's test flakiness/staleness conventions | `corpus-standard-test-references` (#1325) |
| Evidence classification in general, and the graph-edge and tool-result shapes as forms in general | #1314 |
| Provenance for generated *corpus* artifacts (indexes, `generated/` projections) -- a different subject from product source code being conditionally compiled | #1316 |
| Finding the right source file or symbol to read before it is cited | `launchpad/docs/corpus/agents/repository-navigation.md` (#650), unmerged at this node's authoring time |
| Naming, identifiers, taxonomy, status, diagrams, and the remaining per-type templates | somewhere in #1307-#1351 |

**Relationships.** This node declares two `depends-on` edges: to
`corpus-standard-code-references` and to `corpus-standard-test-references`. `depends-on`
is deliberately the stronger type here, not `references` ("no ownership or currency
dependency implied," per `relationships.schema.json`): this node's entire *Scope and
authority* section is built on those two documents' own stated scope boundaries -- the
citation-mechanics-only authority `corpus-standard-code-references` claims for itself,
and the delegation `corpus-standard-test-references` names toward issue #1308. If either
document's stated scope moves -- for example if `corpus-standard-code-references` is
later amended to cover claim-shape itself -- this node's premise stops holding and needs
re-checking, which is exactly `depends-on`'s directionality: "source requires target to
be true/current for source's own claims to hold." Checked against the merge target
immediately before finalizing this front matter, not this worktree:

```
git fetch origin launchpad
git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus
```

Both ids are present on `origin/launchpad` at this node's recorded revision. No edge to
any other `ingestion/*` sibling in this same dispatch batch -- none are merged, and an
edge to an unmerged sibling would validate in this worktree and become a hard error on
`origin/launchpad` the moment this node reached it first, per `AGENTS.md` step 9's
warning.

**Expected but not verified when this node was written:**

- **No corpus node yet cites source code as a `FACT` about current behavior**, so SC1-SC5
  are stated from first-party inspection of this repository's own conditional-compilation
  and macro cases, not from a worked failure already inside the corpus.
- **Whether other crates besides `buzz-datastore-tracing` define proc-macros was not
  exhaustively checked** -- only `grep`-based discovery of `proc-macro = true` across
  `crates/*/Cargo.toml` was performed; a proc-macro re-exported from a dependency without
  that flag in a first-party `Cargo.toml` would not have been found by this method.
- **Whether `desktop/src-tauri/build.rs`'s conditional lines are exhaustive** was not
  checked against every other `build.rs` in the workspace (`desktop/src-tauri` is the
  only first-party one) -- other conditional-compilation mechanisms (Cargo features,
  `cfg` attributes elsewhere) may exist and were not inventoried here.
