---
id: corpus-standard-test-references
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 919886b4192df6251de50c547548ecae5d85afce."
    entry_class: FACT
    evidence:
      - "commit 919886b4192df6251de50c547548ecae5d85afce"
  - statement: "A citation lives in a node's frontmatter evidence array, because the schema requires that array, defines no other field for citations, and rejects any field beyond the seven it names."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "CONTRACT.md section 3 enumerates six citation shapes -- file range, file line, bare path, graph edge, tool result and commit -- and none of them is a URL."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/CONTRACT.md"
  - statement: "AGENTS.md presents those six shapes plus two URL forms as a seven-row table and states explicitly that the table is not a summary of CONTRACT.md section 3, because the two URL rows are forms validate.py recognises and section 3 does not enumerate."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "The tool-result shape's regular expression requires an identifier matched by [A-Za-z_][A-Za-z0-9_.:]* -- no space, no hyphen -- immediately followed by an opening parenthesis, arbitrary content, a closing parenthesis, a literal ' -> ', and then the result; the graph-edge shape requires two such identifiers joined by ' -> ' and a trailing '(N hop(s))', and the checker reports the shared 'names no openable file' verdict for a graph edge and for any tool family no verifier covers, while a tool-result citation naming git or grep is routed to a verifier that reports a family-specific reason and, where the cited source is gone or a pinned replay is contradicted, a hard error."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A realistic test-invocation string written as prose, 'cargo test -p buzz-core --lib kind::tests:: -> 3 passed; 0 failed', matches none of the tool-result, graph-edge, commit or file-position patterns and contains whitespace, so the checker's _classify_citation reports it a hard error ('matches none of CONTRACT.md's six supported citation forms') rather than an unverified notice; wrapping the same invocation as a quoted argument behind a separate identifier, \"run_command('cargo test -p buzz-core --lib kind::tests::') -> 3 passed; 0 failed\", matches the tool-result pattern and is accepted as unverified rather than rejected."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "run_python_check('_SYMBOL, _TOOL_RESULT_RE, _GRAPH_EDGE_RE, _COMMIT_CITATION_RE and _FILE_POSITION_RE copied verbatim from validate.py, tested against both strings') -> unwrapped invocation string matches no pattern and contains whitespace; wrapped invocation string matches _TOOL_RESULT_RE only"
  - statement: "A bare repository path or a path:line/path:range citation naming a test file is resolved on disk exactly as any other file citation: the checker confirms only that the path names a real file, never opens its contents, and a line position's number is checked both for internal consistency -- start at least 1, end not before start -- and against the cited file's length, a position past the end being a hard error since #1459; its content is still never read, so a position that has drifted to a different line that still exists passes while naming the wrong code."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "A FACT resting only on citations the checker classifies UNVERIFIED has, in AGENTS.md's own words, 'not been checked by anything', and under fail-closed validation the UNVERIFIED notice now blocks the run rather than passing as a notice; a tool result no verifier covers still names no openable file, but tool-result citations naming git or grep are no longer uniformly UNVERIFIED -- one whose cited ref no longer exists is a hard error."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "AGENTS.md names exactly one conventional exception to that rule -- the provenance entry recording a node's revision -- and issue #1471 finding 2 documents that this leaves no stated exception for a FACT whose only possible evidence is unverifiable by nature, naming issue #1314 (the evidence standard) as owning the resolution."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "https://github.com/launchpad-26/buzz/issues/1471"
  - statement: "ADR-0029 names 'passing tests' specifically, alongside code, config and schema, as executable evidence that is authoritative over documentation, GitHub history or inference for a claim about how the system currently behaves."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "ADR-0020 records that every test in this repository needing a live relay is marked #[ignore], so a plain cargo test invocation is safe everywhere and does not execute them; ARCHITECTURE.md counts 134 such e2e tests across buzz-test-client requiring a running relay."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
      - "ARCHITECTURE.md:700-707"
      - "TESTING.md"
  - statement: "ADR-0020 records the desktop E2E retry policy as two retries in CI and zero locally, and states that desktop/scripts/summarize-flaky-tests.mjs exists specifically because that retry policy previously hid a real race condition in stream.spec.ts behind a green run for months."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "desktop/scripts/summarize-flaky-tests.mjs reads the Playwright JSON report, walks its suite tree recursively, and reports every test whose status is 'flaky' -- one that failed at least once and then passed on retry -- into the job's summary; the step runs with 'if: !cancelled()' and never fails the job on its own."
    entry_class: FACT
    evidence:
      - "desktop/scripts/summarize-flaky-tests.mjs"
      - ".github/workflows/ci.yml"
  - statement: "Node front matter rejects any field the schema does not name, so a caveat about a test citation's reliability -- that a pass required a retry, that the test is conditionally run, which invocation actually ran -- has nowhere to live except inside the evidence entry's own statement."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Because the tool-result shape's identifier component forbids spaces and hyphens, and a real Rust test invocation such as 'cargo test -p buzz-core' contains both, the identifier in a tool-result citation for a test run can never be the invoked command itself -- it is necessarily an author-chosen label, with the real command relegated to a quoted argument inside the parentheses."
    entry_class: INFERENCE
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
    confidence: 0.8
  - statement: "No equivalent to desktop's retry-then-flaky signal was found for Rust test runs: .github/workflows/ci.yml's cargo nextest invocations carry no retry flag, the Justfile's cargo nextest recipes carry none either, and no nextest.toml exists in the repository to configure one, so a cargo test or cargo nextest citation carries no repository-provided signal comparable to summarize-flaky-tests.mjs's 'flaky' label."
    entry_class: INFERENCE
    evidence:
      - ".github/workflows/ci.yml"
      - "Justfile"
      - "find_file('nextest.toml', root='.') -> not found at the repository root"
    confidence: 0.6
  - statement: "Issue #1325 requires this node to state its scope and the authority its policy rests on, to separate MUST requirements from SHOULD guidance, and to define enforcement and an exception or escalation process."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1325 definition of done"
  - statement: "Issue #1314 (the evidence standard, unmerged) owns the general evidence-classification contract and the graph-edge and tool-result shapes as forms in general, not scoped to tests; issue #1308 (code references, open as PR #1480, unmerged) owns the generic repository-path and GitHub-link mechanics for citing any file in this repository, including a test file considered simply as a file."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1314 and launchpad-26/buzz#1308"
  - statement: "Issue #605's stated outcome names 'a developer or agent' as the two authors a corpus node must serve, which is why this standard's audiences include developer alongside agent and reviewer."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 outcome"
relationships:
  - type: references
    target: corpus-agents
---

# Standard: citing a test

How a corpus node cites a **test** -- a test file, a specific test case inside it, or a
test run's observed result -- as evidence for a claim, and how a test's own conditional
execution and flakiness bear on how strong that evidence is. Look up the section you
need; this is reference material, not a tutorial.

## Scope and authority

**This node governs** citing a test as evidence: which claim a test citation can actually
support, which citation shape fits which of those claims, what a passing validation run
establishes about a test citation and what it does not, and how this repository's
conditionally-run and flaky tests bear on citing one as proof of current behavior.

**Its authority is executable**, in the same sense the sibling standards claim theirs:
every verdict below is the measured behaviour of
`launchpad/project-intelligence/corpus/validate.py`, not house style. Where this document
and that program disagree, the program is right and this document has drifted.
`CONTRACT.md` section 3 supplies the vocabulary of shapes; `ADR-0029` supplies the rule
that makes a passing test evidence at all.

**This node does not govern the general mechanics of a repository-path or GitHub-link
citation.** Resolving a path, rejecting an absolute or escaping one, and pinning a GitHub
link belong to whichever node ends up governing code citations generally (issue #1308,
open as PR #1480, not yet merged) -- a test file is a file, and those rules apply to it
identically. **This node does not govern evidence classification or the graph-edge and
tool-result shapes in general either** -- that is issue #1314's, the evidence standard,
also unmerged. What is left, and what this node actually adds, is the part specific to a
*test* as the thing being cited: which of the shared shapes fits which test-shaped claim,
and the flakiness and staleness judgment neither of those sibling scopes reaches.

| For | Read |
|---|---|
| The frontmatter contract, and which field a citation lives in | `launchpad/docs/corpus/schema/node.schema.json` |
| The six citation shapes as vocabulary | `launchpad/project-intelligence/CONTRACT.md` section 3 |
| What the checker actually does with a citation -- the authority for every verdict below | `launchpad/project-intelligence/corpus/validate.py` |
| How evidence is ranked by claim type, and why passing tests count at all | `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` |
| This repository's testing methodology -- levels, `#[ignore]`, retries | `launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |

If this file and any of those disagree, **they win** -- this one has drifted and should be
fixed.

## Which claim is a test citation actually making?

The same test can sit under three different claims, and they need different citations:

| The claim | Example statement | The right shape |
|---|---|---|
| **A test exists** for some behavior | "A test asserting duplicate ids fail validation exists." | Bare repository path, or `path:line` naming the test |
| **A test was run and produced a result** | "Running the corpus schema tests reports all cases passing." | Tool-result citation |
| **The system currently behaves a certain way**, using a test's pass as the evidence | "Duplicate corpus ids are rejected." | Tool-result citation (or a file citation to assertions actually read), plus the current-behavior discipline in *Flakiness and staleness* below |

Conflating these is the specific failure this node exists to prevent: a `FACT` that a test
*exists* proves nothing about whether it passes, and a `FACT` that a test *passed once* is
not, by itself, the same claim as "the system behaves this way" -- see *Flakiness and
staleness*.

### Worked example from this repository

`launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md:93` records: *"`cargo test -p
git-sign-nostr --lib` -> 55 passed, 1 failed. An all-zero BIP-340 x-only pubkey is
supposed to be rejected as invalid but the underlying `nostr` crate's
`PublicKey::from_hex` accepts it."* That is a **run-result** claim, not an existence
claim -- the count is the evidence, not the mere presence of test files in the crate. It
also shows why the distinction in *Flakiness and staleness* matters: the failing count is
evidence of current behavior only as of the invocation that produced it, and only for that
specific invocation.

## The two shapes in play, and what a pass proves

| Form | Example | Checker's verdict | What it proves |
|---|---|---|---|
| Bare repository path to a test file | `crates/buzz-core/src/kind.rs` | `ok` | The file exists. Nothing about its contents. |
| Path with a line, naming a test function | `crates/buzz-core/src/kind.rs:903` | `ok` | The file exists. The line is not checked. |
| Tool result, invocation written as prose | `cargo test -p buzz-core --lib kind::tests:: -> 3 passed; 0 failed` | **error** | Nothing -- rejected outright. Contains whitespace and matches no recognised shape. |
| Tool result, invocation wrapped as an argument | `run_command('cargo test -p buzz-core --lib kind::tests::') -> 3 passed; 0 failed` | `unverified` | Nothing on disk. The checker cannot confirm this was ever run. |
| Graph edge (for contrast, not a test form) | `is_shared_gated_kind -> is_unshared_gated_event (1 hop)` | `unverified` | Nothing on disk -- and it reads deceptively like a tool result. See MUST 2. |

**Read the right-hand column, not the left.** A test's *existence* is the only thing a
passing validation run against a test citation ever confirms on disk. Everything else --
that the test asserts what the `statement` says, that it was actually run, that the run
observed what the citation claims -- is unverified by the checker and rests entirely on
the author having done it honestly and the reviewer having checked.

## MUST

1. **A claim that a test exists** -- a specific file, or a named test case inside it --
   **MUST** cite a repository-relative path to that file, bare or with a line or range
   pinpointing the test. The general path mechanics (resolution, pinning, absolute-path
   rejection) are not restated here -- see *Scope and authority*. What is specific to a
   test: the checker never opens the file, so it cannot confirm the named test is actually
   declared inside it. A `FACT` under this citation **MUST** rest on the author having
   opened the file and located the test, not on a plausible-looking path.
2. **A claim that a test was run and produced an observed result MUST** use the
   tool-result shape, and that shape's grammar is exact: an identifier of letters, digits,
   underscore, dot or colon only -- no space, no hyphen -- immediately followed by `(`,
   arbitrary content, `)`, a literal ` -> `, then the result. A real invocation typed as
   prose, `cargo test -p buzz-core -- kind::tests:: -> 3 passed`, contains a space before
   the first `(` that never arrives and is a **hard validation error**, not an unverified
   notice -- verified in this node's own ledger. Wrap the invocation as a quoted argument
   behind a separate identifier instead: `run_command('cargo test -p buzz-core -- \
   kind::tests::') -> 3 passed; 0 failed`.
3. **A tool-result citation of a test run MUST NOT be written to resemble a graph edge**,
   and vice versa -- the two shapes are visually close (`a -> b (1 hop)` against
   `a(...) -> result`) and the checker reports the identical unverified verdict for both,
   so a mislabelled one will not be caught by validation. Keep the parenthesized-call form
   for a test invocation and the bare `symbol -> symbol (N hops)` form only for a real
   graph edge.
4. **Every tool-result citation of a test run is UNVERIFIED by the checker**, exactly as a
   graph edge or a commit reference is. A `FACT` resting only on such a citation **MUST**
   be written by someone who actually ran the test and is reporting the result honestly --
   nothing else established it.
5. **A `FACT` about current system behavior that cites a test's pass as its evidence MUST**
   be grounded in an observation made at or near the node's recorded revision, not on a
   same-named test merely existing in the tree today. AGENTS.md's node-update procedure
   requires re-verifying a touched claim against its source at current `HEAD`; a claim
   resting on a test's pass is not exempt, and a test's historical pass at an earlier
   commit is not still evidence of current behavior. See *Flakiness and staleness*.
6. **A test's existence alone MUST NOT be worded as evidence that the behavior it
   exercises is currently correct.** It is evidence that a check for that behavior exists,
   nothing more -- the test could be failing, skipped, or excluded from whichever CI job
   the claim assumes protects it. This repository's own `#[ignore]` convention is the
   concrete case: 134 e2e tests exist in `buzz-test-client` and a plain `cargo test` runs
   none of them.
7. **Where a suite of tests is conditionally run** -- this repository marks every test
   needing a live relay `#[ignore]`, specifically so `cargo test` is safe everywhere and
   E2E execution is opt-in -- **a tool-result citation to a test run MUST name the actual
   invocation**, not merely "the tests." Different invocations exercise different subsets
   here, and an unqualified claim gives a reader no way to tell which subset was run.
8. **Node front matter has no field for a citation's caveats.** A reliability caveat --
   that a pass required a retry, that the test is conditionally run, exactly which
   invocation produced the result -- **MUST** be written into the evidence entry's own
   `statement`. Omitting it there is the same as not recording it.

## SHOULD

- **Prefer citing what was actually observed over what a job's summary implies.** This
  repository's desktop E2E suites retry a failed test up to twice in CI (zero retries
  locally), and `desktop/scripts/summarize-flaky-tests.mjs` exists specifically because a
  retried-then-passed test is otherwise invisible in the ordinary green summary. Check it
  before citing a CI pass as clean -- see *Flakiness and staleness*.
- **Name the crate, package or suite alongside the test**, in the `statement` as well as
  the citation. A bare test name recurs across files and packages in a workspace this
  size, and the citation's identifier alone may not disambiguate it for a later reader.
- **Split an existence claim from a run-result claim rather than merging them.** "A test
  for X exists" and "that test currently passes" are different claims with different
  citations and different failure modes -- merging them lets the weaker half borrow the
  stronger half's evidence, the same failure `corpus-standard-decision-references`
  describes for an intent claim wearing a behaviour citation's clothes.
- **When a test's assertions, not merely its pass, are the evidence**, cite the test file
  with a line or range bracketing the assertion, and quote or closely paraphrase what it
  checks in the `statement`. A passing run proves an exit code, not which behavior was
  checked -- only reading the assertion does that.
- **Cite the narrowest test that actually supports the claim, and only that one.** A
  second test cited "for corroboration" is a second thing that can silently drift, and
  the checker will not tell you which one did.

## Flakiness and staleness

**A test's pass is not a timeless fact about the system; it is an observation at a
moment, of one invocation, that may or may not repeat.** Two properties of this
repository's own test suites make that concrete rather than abstract, and both change
what a reviewer has to check before trusting a test citation.

**Retries can mask a failure.** `ADR-0020` records the desktop E2E retry policy as two
retries in CI and zero locally, and states plainly why:
`desktop/scripts/summarize-flaky-tests.mjs` exists because that retry policy once hid a
real membership race in `stream.spec.ts` behind a green run for months. The script reads
the Playwright JSON report and surfaces every test whose recorded status is `flaky` --
failed at least once, then passed -- into the job summary, without failing the job
itself. **A citation reading "the desktop E2E suite passed" can be true of a run that
included a flaky retry on the exact test being cited**, and nothing in the corpus checker
or in an ordinary green CI badge distinguishes that from a clean first-try pass. Check the
flaky summary for the relevant run before citing a desktop E2E pass as reliable current
behavior, and say in the `statement` if the pass needed a retry rather than omitting it.

**Rust test runs carry no equivalent repository-provided signal.** No retry flag was
found on any `cargo nextest run` invocation in `.github/workflows/ci.yml` or the
`Justfile`, and no `nextest.toml` exists to configure one -- so a `cargo test` or `cargo
nextest` citation carries nothing comparable to desktop's `flaky` label. That is not
evidence the tests are more reliable; it is an absence of the tooling that would tell you
either way. A single observed pass of a Rust test is a single observation, full stop, and
the burden of judging whether it is trustworthy evidence of current behavior falls
entirely on the author and the reviewer -- there is no automated second signal to lean on.

**Both cases reduce to the same rule.** ADR-0029 grants "passing tests" authority over a
behavior claim precisely because they are executable evidence -- but a citation is only as
strong as what it actually establishes, and *Which claim is a test citation actually
making?* above is what a reviewer checks it against. Do not cite a pass you have not
personally reproduced, or have not confirmed was not a masked retry, as clean current
behavior; say what you actually know.

## Enforcement

Run it locally, from the repository root:

```bash
python3 launchpad/project-intelligence/corpus/validate.py
```

Exit `0` passes; `1` means at least one error, each naming the node it came from. `just
corpus-validate` runs the same command but needs Hermit activated first
(`. ./bin/activate-hermit`); the direct interpreter form does not. CI runs it on every
pull request and every push to `launchpad` touching `launchpad/docs/corpus/**`, so a
local failure is a CI failure.

**Three things a green run does not establish about a test citation, and the third is not
stated anywhere else in this corpus:**

1. **That the cited test's assertions match the `statement`.** Checking is structural. A
   `FACT` citing a real test file that asserts something else entirely passes cleanly.
2. **That a tool-result citation reflects a run that actually happened, honestly
   reported.** The shape is recognised and reported unverified; nothing confirms the
   command was executed or that its output was transcribed correctly.
3. **That a reported pass was not a retried pass masking a flaky failure.** Nothing in
   `validate.py` reads a test's retry history -- it cannot, the ledger is prose, not a
   Playwright report -- so a citation reading "passed" is silent on whether it passed on
   the first attempt. Only `desktop/scripts/summarize-flaky-tests.mjs`, run against the
   actual CI artifact for that job, answers that, and only for desktop E2E.

**What a reviewer has to hold, because no check will:** that a citation to test existence
is not read as a citation to current correctness (MUST 6); that a tool-result citation's
invocation is specific enough to know what actually ran (MUST 7); that a cited pass was
verified, not merely assumed, against the recorded revision (MUST 5); and, for a desktop
E2E citation specifically, that it was checked against the flaky summary before being
called clean.

## Exceptions and escalation

**There is no exception process for the structural rules.** They are `validate.py`'s
behaviour, enforced before merge, and cannot be waived by agreement in a node's body.

**This node does not resolve the tension issue #1471 (finding 2) raised in `AGENTS.md`:**
whether a `FACT` may rest solely on an UNVERIFIED citation in any case beyond the one
named exception -- the provenance entry recording a node's revision. A tool-result
citation of an observed test run is exactly the case that tension is about, and it is
unresolved as of this node's recorded revision. Until issue #1314 settles it, an author
citing a test run as a `FACT` is relying on the same convention that issue names as
unresolved, and a reviewer should treat it accordingly: check that the run really
happened, because nothing else will, and do not treat the absence of a settled rule as
license to skip that check.

**When a rule here cannot be met**, do not relax it locally -- a standard quietly widened
by one node has stopped being a standard, and nothing will notice. Raise an issue against
`#605` describing the citation that was needed and could not be written.

## Scope and omissions

**This node covers** which claim a test citation supports, which shape fits it, what a
passing validation run establishes about a test citation and what it does not, and how
this repository's conditional and flaky tests bear on citing a pass as current behavior.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The generic repository-path and GitHub-link mechanics -- resolution, pinning, absolute/escaping rejection -- that apply to a test file exactly as to any other file | #1308 |
| Evidence classification in general, and the graph-edge and tool-result shapes as forms in general, not scoped to tests | #1314 |
| Citing the production source code a test exercises, as evidence of that code's own behavior | #1308 |
| Whether a `FACT` may rest solely on an UNVERIFIED citation beyond the one named provenance exception | #1314, flagged unresolved by issue #1471 finding 2 |
| Line numbers not being checked against file length | #1459 |
| Naming, identifiers, taxonomy, status, diagrams and the remaining per-type templates | somewhere in #1307-#1351 |

**Relationships.** This node declares one edge: `references` -> `corpus-agents`. Checked
immediately before finalizing this front matter, against the branch this PR merges into,
not this worktree:

```
git fetch origin launchpad
git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus
```

At the time of that check, `corpus-agents`, `corpus-standard-decision-references` and
`corpus-standard-confidence` are the only ids present on `launchpad`; neither
`corpus-standard-code-references` (issue #1308's, open as unmerged PR #1480) nor any of
the other nodes in this same dispatch batch are. This node's own citation table and shape
discussion draw directly on `AGENTS.md`'s citation-shape table as supporting context --
`references` names exactly that relationship, "source cites target as supporting context,
no ownership or currency dependency implied" -- without asserting that this node's claims
would break if `AGENTS.md`'s prose changed, since its own text says that table is
provisional and expected to move once #1314 lands. No edge is declared to either merged
sibling standard: neither citing a decision nor the `confidence` field is a dependency of
citing a test, and the schema defines no relationship type for "adjacent sibling standard
sharing a template."

**Expected but not verified when this node was written:**

- **No corpus node yet cites a test as evidence of any claim.** Everything here is derived
  from the validator's own regular expressions and from real testing conventions
  documented elsewhere in this repository (`ADR-0020`, `TESTING.md`, `ARCHITECTURE.md`,
  the flaky-test summarizer), not from a worked example inside the corpus itself.
- **The wrapped tool-result citation form in MUST 2 was checked against the regular
  expressions copied from `validate.py`, run directly in Python, not against a full
  `validate.py` invocation over a constructed fixture node.** The two are expected to
  agree -- the copied patterns are the same objects `_classify_citation` calls -- but a
  full end-to-end run exercising this exact citation was not performed.
- **Whether `cargo nextest`'s own retry semantics (a flag this repository does not
  currently pass) would, if adopted, produce a signal comparable to
  `summarize-flaky-tests.mjs`'s was not researched.** The claim made here is only that no
  such signal exists in this repository's current configuration, not that none could.
