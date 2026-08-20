# The Professor — design

The cohort's knowledge agent: the one you ask *"how do I add this to Buzz?"*, and the one
that writes the pages it answers from.

Written 2026-08-12, for [#9](https://github.com/launchpad-26/buzz/issues/9) under
[#4](https://github.com/launchpad-26/buzz/issues/4). This is the design, not the persona —
the voice is authored separately and deliberately, and #9 excludes it from scope.

This is also the **first** agent built for this fork, so the conventions it sets are written
down here as conventions rather than left implicit. [The last section](#how-the-next-agent-gets-built)
is the part that generalises.

> **Two decisions block the persona body**, and neither is answered here: **how The Professor
> runs** — nothing consumes pack configuration at runtime
> ([§8](#what-that-means-for-how-the-professor-runs)) — and **where drafts go**
> ([§8](#also-unspecified-where-drafts-go)). Both are in
> [Open questions](#open-questions) as items 1 and 2. Everything else in this document holds
> whichever way they are settled.

---

## 1. What The Professor is

One identity, two jobs, in this order:

| | Job | Delivered by |
|---|---|---|
| **Author** | Drafts handbook pages from the five source repositories, against the page contract | #9 — now |
| **Librarian** | Answers *"how does this work / where do I look"* in Buzz channels | PRD stage 4 — later |

**These are the same agent.** #9's own exclusion says so: *"**The Professor running live inside
Buzz**, answering questions in channels. That is PRD stage 4."* Same name, later stage.

The design below is written for both, so the persona authored for #9 does not need rewriting
when the second job arrives.

### Why the authoring job comes first

Not sequencing preference — there is nothing to answer from yet.

**Measured 2026-08-12: the corpus is 13 pages, and the claim parser finds zero claims across
all of them** — the same count before and after that day's parser fix, so it is a property of
the content rather than of the parser. A librarian pointed at it today would have almost
nothing to point at, and no provenance behind what little it said.

PRD #4 orders it the same way:

> No requirement to build a RAG system or knowledge bot yet. […] This PRD establishes the
> **knowledge layer**, not the future retrieval system that may consume it.

The Professor writes the library it will later work in.

### What "point you in the right direction" needs

The librarian job is more modest than it sounds, and that is a feature. Pointing someone at
the right page needs an **index**, not embeddings — and PRD #4's non-goals rule out vector
databases and embeddings explicitly.

`page-index.json` in the handbook already is that index: every page with its category, its
sources and its pins, across the eleven navigation slots. The retrieval story starts there,
not with new infrastructure.

---

## 2. The three layers

The design separates three things that are usually muddled together. The test for which layer
something belongs in is: **is this judgement, is this fact, or is this a guarantee?**

| Layer | Holds | Mechanism | Skippable? |
|---|---|---|---|
| **Persona** | Judgement and voice — what a page says, which prefix applies, whether a source supports a claim | `.persona.md` in a pack | It is who the agent is |
| **Tools** | Facts — resolve a pin, verify a path, read the contract | One MCP server | **Yes** — nothing compels a call. That is what the gate is for. |
| **Gate** | The guarantee — no page merges unchecked | Provenance gate in CI | **No** |

### Why the facts are tools, not prompt text

The page contract requires, per source:

```yaml
sources:
  - repo: block/buzz
    ref: refs/heads/main
    commit: 538e5e113fc33571f939c87b925567fd4e277109   # full 40-char SHA
    paths:
      - crates/buzz-relay/src/tenant.rs                 # must exist at that commit
```

**A language model writing a 40-hex-character SHA from memory is a hallucination with a
checksum's shape.** It will look plausible and be wrong, and the worst case is not a
malformed SHA — it is a real SHA for the wrong commit.

A tool is the right home for it because it puts a *correct* answer within reach and leaves a
record that the answer was fetched.

**It does not make fabrication impossible.** Nothing compels a model to call `resolve_pin`; it
can still write a plausible SHA straight into the frontmatter. An agent that can decline to run
its own check can decline to call a tool, and for the same reason.

So the rule is weaker than it first looks:

> If being wrong is silent and checkable, put the right answer behind a tool **and give the gate
> something to check it against**. If being wrong requires judgement to notice, it belongs to
> the persona — and to review.

### What no tool in this design catches

Naming these matters more than the tools do, because they are where a plausible page goes wrong
without anything noticing:

- whether the chosen `repo` and `ref` are the *right* source for the claim
- whether **every** supporting path was listed, not merely whether one listed path exists
- whether the cited source actually **supports** the sentence in front of it
- whether a claim that should have been made was **omitted**
- whether repository text returned by a tool carries prompt-injection content

The first four are the judgement engine's territory ([#74](https://github.com/launchpad-26/buzz/issues/74))
and a human reviewer's. The fifth is a runtime concern this design does not yet address.

### Enforce at the boundary where the violation happens

**CI is for reviewable artifacts. Runtime is for actions.** A page is an artifact: it can be
checked at merge, independently, by something the agent does not control. A leaked secret, a
write outside an allowed root, an unbounded network call — those are actions, and CI cannot
retroactively un-leak anything. Bound them where they occur.

That distinction is not academic here. [Where drafts go](#also-unspecified-where-drafts-go) is
still open, and if The Professor ever gets a write tool, the write boundary is **runtime**. The
old rule would have sent someone looking for the wrong enforcement point.

**For the page contract specifically, CI is the right boundary — and it is genuinely
unskippable.** Verified 2026-08-12 on the handbook's default branch:

```json
{"name": "main", "enforcement": "active", "conditions": ["~DEFAULT_BRANCH"],
 "rules": [{"type": "required_status_checks", "checks": ["Provenance gate"]}]}
```

> **Check rulesets, not just branch protection.** The legacy branch-protection endpoint returns
> `404 Branch not protected` for this repository *while the ruleset above is actively enforcing
> the gate*. Reading only the legacy endpoint would report an open merge gate that is in fact
> closed — the false negative [#70](https://github.com/launchpad-26/buzz/issues/70) exists to
> prevent. Bypass actors were not enumerated, so "unskippable" is asserted for the required
> check, not for every possible actor.

An agent can decline to run its own check. It cannot decline that one.

---

## 3. What ships, and what is spec-only

Every mechanism below was checked against the source tree on 2026-08-12, not against
`PERSONA_PACK_SPEC.md` alone. The spec describes considerably more than the code implements,
and the difference decides the design.

| Mechanism | Status | Consequence for this design |
|---|---|---|
| `load_pack(dir)`, `resolve_pack(dir)`, `validate_pack(dir)` | ✅ implemented | A pack is a **directory**. Point at a checkout. |
| `buzz pack validate` / `inspect` | ✅ **run against `examples/meadow-core` 2026-08-12** — `Valid.`, exit 0; `inspect` printed three personas | The authoring loop works today, on real input. `inspect` prints a **summary**, not the whole resolved config — MCP servers appear as a count, and runtime, pack instructions and hooks are omitted. |
| **MCP servers** | ✅ live — `build_mcp_servers()` at session creation, with tests | **The tool layer rests on this** |
| `buzz install`, `.buzzpack` zips, `~/.buzz/packs/` | ❌ spec only — the `buzz pack` CLI exposes only `validate` and `inspect`, with no install subcommand (unrelated `install` functions exist elsewhere in the tree) | No install step. Not needed. |
| Lifecycle hooks | ❌ **not executed.** Per-persona hooks are parsed into the resolved persona; the manifest's pack-level `hooks_config` is accepted and then discarded without its file being read | Cannot carry any guarantee |
| Skill copying from a pack's `skills/` | ❌ planned | A skill must land in `$AGENT_CWD/.agents/skills/` |
| Pack dependencies | ❌ future work | One pack cannot require another |

Two conclusions follow, and both simplify the build:

1. **Nothing needs to be built in Buzz first.** The parts this design uses are the parts that
   work.
2. **MCP is the only extension point where the spec and the code agree.** That is why the
   fact layer is an MCP server rather than a hook or a bundled script.

### The constraint to design around

The plain `buzz-acp` CLI entry point builds **at most one** MCP server — zero when
`mcp_command` is empty, one otherwise — because it takes a single `mcp_command`:

```rust
fn build_mcp_servers(config: &Config) -> Vec<McpServer> {
    if config.mcp_command.is_empty() { return vec![]; }
    vec![McpServer { … }]   // one
}
```

**This is a configuration-entry limitation, not an architectural invariant**, and an earlier
draft of this document overstated it as one. The plumbing below carries many: `PromptContext`
holds a `Vec<McpServer>`, ACP session creation accepts and serialises an arbitrary vector, and
the pack resolver already merges shared with per-persona servers. Only the CLI's single
`mcp_command` narrows it to one.

So: The Professor gets **one server exposing every tool it needs**, because that is what its
chosen entry point can supply — a sound choice here, and **not** a rule the next agent should
inherit. Whoever builds the next one should re-check what their entry point accepts.

---

## 4. The tool surface

One MCP server, growing rather than being replaced when the librarian job arrives.
`buzz-dev-mcp` in this repository is the reference implementation to copy.

### For the author (#9)

| Tool | Returns | Why it is a tool |
|---|---|---|
| `resolve_pin(repo, ref)` | full 40-char commit SHA | a model cannot be trusted to produce one |
| `path_exists_at(repo, commit, path)` | boolean | *"Listing extra paths creates false staleness; omitting one creates silence"* |
| `read_contract()` | the page contract, current | read at runtime so it can never go stale in a prompt |
| `list_categories()` | the eleven navigation slots | pages are filed by the question they answer |
| `check_page(draft)` | the gate's findings for a draft | lets the agent self-correct before a human sees it |

### For the librarian (stage 4)

| Tool | Returns |
|---|---|
| `search_pages(query)` | matching pages from the index |
| `page_by_category(category)` | pages in a navigation slot |
| `page_sources(page)` | the pins behind a page, so an answer can cite evidence |

Nothing in the first set is discarded. A librarian that can also resolve a pin can tell you
*"this page cites `tenant.rs` at this commit"* rather than only *"read this page"*.

### What the contract must be read, never copied

`read_contract()` exists so the persona prompt does not quote the contract. A prompt that
quotes it goes stale silently the moment the contract changes; a prompt that reads it cannot.

This is also why the handbook is **not** bundled into the pack. One copy of the truth.

---

## 5. Where it lives

```
launchpad-26/buzz
└── launchpad/
    └── agents/
        ├── README.md                     ← the convention, from the last section
        └── the-professor/                ← the pack: a directory
            ├── .plugin/plugin.json        id, version, engines, personas
            ├── agents/the-professor.persona.md
            ├── instructions.md
            └── README.md
```

**In `launchpad-26/buzz`, not the handbook.** A pack is a directory that `load_pack` reads, so
"which repo" is only a question of where source is kept — and keeping every agent in one place
is worth more than colocation with the corpus.

**Under `launchpad/`, not `examples/`.** `examples/` is upstream's. `launchpad/AGENTS.md` §3 is
explicit: *"Everything cohort-specific lives under `launchpad/`. Upstream owns everything
else."* That rule is about **ownership and review clarity**, and it is sufficient on its own.

It is tempting to reach for a mechanical justification — that a cohort file in `examples/` would
conflict on every upstream sync. It would not: a new file with a name upstream does not use
usually merges cleanly. **The reason to stay out is that the directory is not ours**, not that
git would punish us for it. The same holds for naming fork workflows `launchpad-*.yml`: it
removes collision *risk*, which is weaker and truer than certainty.

`launchpad/AGENTS.md` §3's directory table does not yet list `agents/`. Adding this directory
means adding that row.

> **Naming collision, deliberately noted.** `launchpad/AGENTS.md` is the guide for *agent
> contributors* — humans and AI writing code in this fork. `launchpad/agents/` holds *persona
> packs* — agents that run inside Buzz. Different things, adjacent names. The README in
> `launchpad/agents/` should say so in its first line.

### The handbook stays where it is

Private repository, read by the MCP server from a local checkout. Its path is local
configuration and is never committed.

**How that path actually reaches the server is an open question, and an earlier draft of this
document got it wrong.** It claimed the manifest supports `${VAR_NAME}` interpolation. It does
not. Resolution passes env values through as **literals**, and a test pins that behaviour:

```rust
// resolve.rs:67    "env values as literals (no interpolation in this PR)"
// resolve.rs:106   "literal env passthrough (no ${VAR} interpolation)"
// resolve.rs:504   assert_eq!(env["PATH"], "${HOME}/bin");   // unchanged
```

The spec says the same in a note that the earlier draft read past: *"MCP env var interpolation
(`${VAR_NAME}` resolution) is **planned but not yet implemented**."* This is exactly the
spec-versus-code trap [§3](#3-what-ships-and-what-is-spec-only) exists to catch, walked into by
the author of §3.

So a literal `${HANDBOOK_DIR}` in a manifest **survives pack resolution unchanged** — and then
goes nowhere, because [nothing consumes resolved pack configuration at
runtime](#what-that-means-for-how-the-professor-runs).

The remaining candidates are the **process environment** the MCP server inherits when spawned,
or a config file the server reads for itself. Which one is a decision this design has not yet
made, and it must be made before the server is written.

---

## 6. Temperature

#9 requires `temperature` to be set **with a written reason**. The reason belongs here; the
number is confirmed by the author of the voice.

The tension is real and it pulls both ways:

- **Factual synthesis wants it low.** Drafted claims must be traceable to sources. Invention is
  the failure mode the whole provenance gate exists to catch.
- **Voice wants room.** A corpus with a consistent, readable author is the point of having one
  fixed identity rather than "whatever model drafted this page".

It is tempting to resolve that tension by arguing the facts come from tools, so temperature
governs prose rather than accuracy and a moderate setting costs nothing. **That argument fails
twice.**

### Why there is no number here

**Tools resolve metadata, not meaning.** A pin is fetched rather than recalled, but the model
still decides what a source *says*, whether it supports the sentence in front of it, which
claims to make, and what to leave out. Those are generation decisions, and they are
accuracy-sensitive. Temperature was never off the hook.

**And the setting may reach nothing at all.** Measured 2026-08-12:

- `buzz-acp`'s configuration has **no temperature field**.
- Pack resolution projects temperature to `GOOSE_TEMPERATURE` only, with the source saying so
  in as many words: *"temperature and context_limit stay as `GOOSE_*` (only goose reads them)"*
  (`resolve.rs:388`).

So pack resolution **targets** temperature at Goose and at nothing else — and since no runtime
calls the resolver, that projection currently reaches **no runtime at all**.

**Whether the setting configures anything is downstream of
[the runtime decision](#what-that-means-for-how-the-professor-runs), which is open.** A number
recommended before that decision is a number that may configure nothing.

### What upstream's example shows, and what it does not

`buzz pack inspect examples/meadow-core`, run 2026-08-12:

| Persona | Role | Temperature | Set how |
|---|---|---|---|
| Skip | orchestrator — conversational | `0.7` | **inherited** — `skip.persona.md` sets no temperature |
| Bana | architecture reviewer | `0.5` | per-persona override |
| Lev | security reviewer — the most factual | `0.3` | per-persona override |

The evidence for "lower for factual work" is **two downward overrides from a default** — a real
pattern, and still two choices in one example pack rather than a law. It does not support a
`0.3`–`0.7` convention.

### The rule for this agent and every one after it

1. **Name the runtime first**, and confirm temperature actually reaches it. If it does not, say
   so where the value is set, so nobody reads an inert field as an active choice.
2. **Choose empirically**, against a fixed set of drafting tasks you can re-run, not from first
   principles.
3. **Write down what you observed**, not what you reasoned.

For #9, set the field because the page contract requires it, and give the honest reason —
including the dependency if the runtime question is still open. A written reason that admits
what it rests on is worth more than a confident number that configures nothing.

---

## 7. What this deliberately does not build

- **The persona's voice.** #9 excludes it: *"Voice is authored, not specified."* Nothing in this
  document constrains how The Professor sounds — only what it may assert.
- **The librarian's retrieval.** PRD #4's non-goals: no RAG, no embeddings, no vector database.
  Stage 4 begins from `page-index.json`.
- **A distribution story.** No `.buzzpack`, no registry, no install. A pack is a directory, and
  one pack does not need a marketplace.
- **Hooks.** They do not execute. A guarantee placed in one would be decorative.
- **A second corpus.** PRD #4 Ruling 1: humans and agents are served from the same pages.

## 8. Known limits, stated plainly

- **Half of this document has been independently checked, and half has not.** Every claim about
  `block/buzz` — what ships, what is spec-only, how packs resolve, what the harness does — was
  verified against the source by three reviewers across three passes. **Every claim about the
  handbook was verified by its author alone**: the corpus size, the zero-claim count, the page
  contract's requirements, the nine gate rules, the branch ruleset. The handbook is a private
  repository, so a local reviewer cannot open it, and one flagged that limit explicitly rather
  than accepting the claims.

  The measurements were made and the commands were shown, so this is not a reason to distrust
  them — it is a reason to know **which half rests on one person's care.** If the handbook side
  is ever wrong, no process in this document would have caught it.
- **The claim rules have never judged real content.** Zero live claims in the corpus means
  `prefix-unknown` and `prefix-repo-mismatch` currently judge nothing. The Professor will be
  the first thing to produce claims at scale, and that is when those rules are first genuinely
  exercised. Expect it to surface defects a clean corpus never could.
- **Two known gate defects are open.**
  [#87](https://github.com/launchpad-26/buzz/issues/87) reports two ALL-CAPS constants in a
  fenced block as an `.env` body — a drafting agent writing about configuration will produce
  exactly that, so check it before debugging the persona.
  [#90](https://github.com/launchpad-26/buzz/issues/90) covers three container shapes that
  still bypass the claim rules.
- **A pack is authored and validated by the CLI, and run by nothing.** The desktop app is not
  the runtime consumer either — it preserves the legacy alias fields and calls the crate only
  for `split_frontmatter` during a legacy migration (`desktop/.../migration.rs:1128`), never
  `resolve_pack` — so nothing consumes *resolved pack configuration*. This was
  traced on 2026-08-12 and is the single most surprising finding here. Neither `buzz-acp` nor
  `sprig` resolves a pack — there is no `--pack` flag anywhere in the tree, and no caller of
  `buzz_persona::` outside `buzz-cli`. The consumer is the desktop app's managed-agent system:
  `desktop/src-tauri/src/managed_agents/types.rs` records `persona_team_dir` (*"Installed team
  directory path… Set when agent was created from a team persona"*) and `persona_name_in_team`,
  with `persona_pack_path` and `persona_name_in_pack` kept only as legacy **aliases**.

  So the vocabulary moved from *pack* to *team* on the desktop side, and the spec's
  `~/.buzz/packs/` story describes neither.

- **A pack directory cannot become a running desktop agent, and that is by design rather than
  by omission.** Traced 2026-08-12:

  1. Teams are **records, not directories**. The Tauri surface is `list_teams`, `create_team`,
     `update_team`, `delete_team`. There is no import-a-directory command.
  2. A migration actively **removes** directory backing. `migration/detach.rs` —
     *"T4 migration: lift pack-level instructions into `TeamRecord.instructions` and detach all
     directory-backed teams from their file-layer plumbing"* — runs on app launch whenever any
     `TeamRecord` still has `source_dir`, backfills `team_id`, and clears `persona_team_dir`,
     `persona_name_in_team`, `source_dir`, `is_symlink`, `symlink_target` and `version`.
  3. The only import route is a **team snapshot** (`buzz-team-snapshot` v1, `.team.json` /
     `.team.png`) via `preview_team_snapshot_import` / `confirm_team_snapshot_import`.
  4. A persona-pack zip is **rejected by magic bytes**, with a deliberate message:
     *"Legacy team files are no longer supported. Export a buzz-team-snapshot v1 .team.json or
     .team.png instead."* The function's own doc comment says it rejects *"retired flat team
     JSON and persona-pack ZIP files"*.
  5. **No production constructor sets `persona_team_dir`** — every current one assigns `None`,
     including ordinary agent creation and team-snapshot import. Compatibility tests do assign
     `Some`, deliberately, so "nothing sets it anywhere" would be false.

  **So the pack format is authorable, validatable and inspectable — but not runnable.** Not
  "not yet": the bridge is being dismantled on purpose. The spec says the same thing in §11 —
  *"To get a pack's personas running inside the desktop app today, recreate them there by hand
  using `buzz pack inspect`'s resolved config as reference."*

### What that means for how The Professor runs

**State this plainly: there is no runtime consumer of pack configuration today.**

**The pack is still worth writing.** It is the reviewable, versioned statement of what the agent
should be, and `buzz pack inspect` renders it as concrete post-merge values. But until something
reads it at runtime, it is a **specification, not configuration** — and the difference is the
whole of what follows. The CLI validates and inspects it. Nothing reads it to run an agent.

That has a consequence worth sitting with before choosing a runtime: **calling the pack "the
source of truth" is a claim this design cannot currently honour.** Whatever runs The Professor
is configured separately, so unless something closes the gap, changes to the pack do not change
the running agent, `buzz pack validate` validates something no runtime reads, and the
"[before it is considered done](#before-it-is-considered-done)" checks cannot show that the
inspected pack is what ran.

Three candidates, and the third is the only one that makes the pack load-bearing:

| | Route | Cost |
|---|---|---|
| **1** | Recreate it in the desktop app from `inspect` output, as the spec directs | Manual; drifts the moment either side changes |
| **2** | Run it as a plain `buzz-acp` agent configured from the environment | The MCP layer is wired there — but `buzz-acp` has **no temperature setting at all**, and the pack's temperature is projected only to `GOOSE_TEMPERATURE` (`resolve.rs:388`: *"only goose reads them"*). So this route silently drops behavioural config the pack declares. |
| **3** | Write a small **projector** that resolves the pack and emits `buzz-acp` configuration deterministically | Real work, but it is the only route where the pack is the input rather than a document someone transcribes |

Route 2 does not keep the pack honest — nothing connects the two. **Route 3 is route 2 plus the
missing link.** Route 2 without a projector means the pack is a *specification the runtime is
manually configured to match*, which is defensible but must be said rather than implied.

**This must be settled before the persona body is written.**

**Recommended for #9: route 1 or 2, with route 3 filed as its own issue.** Route 3 is the right
long-term answer and it is real engineering that #9 does not ask for — #9's acceptance is a
`.persona.md` that validates, drafts a page, and sets `temperature` with a written reason.
Building a projector inside it would widen a bounded deliverable into an open-ended one, which
is the same failure this document corrects elsewhere.

So: run it the manual way, say plainly in the pack's README that the pack is a **specification
the runtime is configured to match**, and file the projector separately. That is the fork's
standing rule — non-blocking findings become issues, blockers get fixed now — applied to a
design decision rather than a defect.

### Also unspecified: where drafts go

Raised by review and not yet answered. `buzz-acp` is a relay event harness working from its
process working directory, and the tool surface in [§4](#4-the-tool-surface) contains **no write
tool**. So the design does not say whether a drafted page arrives as a Buzz reply, a local file,
a patch, or a pull request against the handbook.

That is not a detail — it decides whether The Professor needs write access to a private
repository at all, which is the difference between a read-only tool surface and one that needs
a permission boundary designed around it.

**The answer is close to forced, and it follows from this document's own layer rule.** The gate
is the guarantee, and the gate runs **on pull requests**. So a draft that arrives as a Buzz
reply, a local file, or a patch is a draft **nothing checks** — the guarantee simply does not
reach it. Only a pull request against the handbook puts the output where the enforcement
already is.

That is the general principle, stated once because the next agent will need it too:

> **The enforcement boundary decides where output goes, not the other way round.** Choose where
> the guarantee lives first; the destination follows from it. Picking a convenient destination
> and hoping a check reaches it is how output ends up unguarded.

It is recorded here rather than settled because it has a cost — a pull request means write
access to a private repository, which is a permission this design has not yet scoped. That
trade is [Open question 2](#open-questions).

---

## How the next agent gets built

The part that generalises. Every agent in this fork follows this, and the reasons are the ones
above rather than taste.

### Where it goes

`launchpad/agents/<name>/`, as a pack directory. Never `examples/`, never `docs/` — both are
upstream's.

### What goes in the pack

**The layout is whatever `buzz pack validate` accepts. The validator is the contract; this list
is a snapshot.** That distinction matters here more than usual — [§8](#8-known-limits-stated-plainly)
records the pack format actively changing underneath us, and a quoted layout is the
silent-staleness case the defaults below warn against. If this list and the validator ever
disagree, the validator is right and this list is a bug.

As of 2026-08-12:

- `.plugin/plugin.json` — id, version, `engines`, the persona list
- `agents/<name>.persona.md` — identity, behavioural config, and the prompt body
- `instructions.md` — pack-level instructions, if more than one agent shares them
- `README.md` — what this agent is for, in one paragraph

### What stays out

Two categories, because they are obeyed differently. One list in one tone turns useful defaults
into absolutes, and absolutes that everyone quietly breaks teach people to ignore the list.

**Rules — no exceptions.**

| Out | Why |
|---|---|
| Secrets, tokens, credentials, private host paths and member rosters | **Git history outlives every later edit, and a repository outlives its current visibility.** A committed secret is disclosed to everyone who ever gets access, and no deletion undoes that — and this fork is public besides. |

That is the whole list, and it is short on purpose. A rule that admits exceptions is a default
wearing a rule's clothes.

**Defaults — departing from one requires a written reason in the pack's README.**

| Default | Why | When departing is legitimate |
|---|---|---|
| Knowledge, corpora and datasets stay outside the pack | One copy of the truth; a bundled copy is stale on arrival | Small, stable domain knowledge that genuinely versions with the agent |
| Nothing is quoted from a document that changes | A quoted contract goes stale silently; a read one cannot | The quote is pinned to a version and the pin is checked |
| Facts a model could fabricate go behind a tool | **The test: is being wrong silent and mechanically checkable?** Then tool, *and* something whose job is checking it. Does noticing take judgement? Then persona and review. "Could a model get this wrong" is not the test — it could get anything wrong. A tool does not make invention impossible | The fact is self-evident in the output and cheaply reviewed |
| Guarantees are enforced at the boundary where violation occurs | CI for reviewable artifacts, runtime for actions. CI cannot un-leak a secret | — this one is closer to a rule than a default |

The "written reason" requirement is the same discipline this project already uses for allowlist
entries and deferred findings: the exception is allowed, and it is visible in review.

> **The layers have no home for state, and that is a known gap.** Memory, indices, anything an
> agent accumulates across runs is not judgement, not a fact-lookup, and not a guarantee. The
> Professor's drafting job avoids the question; its librarian job will not, and a continuously
> conversational agent hits it on day one. **If you are building one of those, you are past
> what this document conventions** — decide deliberately and write down what you chose, so the
> next person inherits a decision rather than an accident.

> **Nothing belongs in this section if it is true only because of a current implementation gap.**
> Conventions hold their shape; facts have dates. *"Hooks carry no real behaviour"* was in an
> earlier version of this table — it is a fact about today, it will become wrong, and a
> contributor a year from now would have followed a rule whose reason had quietly expired. It
> lives in [§3](#3-what-ships-and-what-is-spec-only) instead, which is dated and explicitly a
> snapshot. Anything else that reads like "X does not work yet" belongs there too.

### The five questions to answer before writing a persona

**A template gets read *instead of* the document it came from, not alongside it.** So these
questions carry the reasoning above rather than an abbreviation of it — a shorter list saves
nothing if it quietly restates what the body spent sections correcting.

1. **What is judgement here, and what is fact?** The test is not "could a model get this
   wrong" — it could get anything wrong. It is: **is being wrong silent and mechanically
   checkable?** Then put the right answer behind a tool *and* give something the job of
   checking it. Does noticing require judgement? Then it belongs to the persona, and to review.
2. **What must be guaranteed, and where would violating it actually happen?** Enforce it
   there — CI for reviewable artifacts, runtime for actions
   ([§2](#enforce-at-the-boundary-where-the-violation-happens)). CI cannot un-leak a secret or
   un-send a message. **"In the persona prompt" is never the answer to this question:** a
   prompt is a request, not a boundary.
3. **What does this agent read that might change?** Anything that changes is read at runtime,
   never quoted into the prompt.
4. **What can this agent do to the world?** List every write, send, execute and delete it can
   perform, and what authorises each. A read-only agent and an agent with one write tool are
   different designs with different blast radii — decide which you are building *before* the
   persona. [Where drafts go](#also-unspecified-where-drafts-go) is the cautionary tale: this
   very document reached a late draft without answering it.
5. **What untrusted content reaches it, and what does it see that others should not?**
   Anything the agent reads — repository text, channel messages, tool output — can carry
   instructions aimed at the agent rather than at you. Decide what happens when it does.
   Separately: anything private it can see (direct messages, rosters, personal data) needs a
   stated rule for where that may reappear.

Behavioural settings follow [§6's rule](#the-rule-for-this-agent-and-every-one-after-it):
confirm the setting reaches the runtime, choose empirically, and write down what you observed.

### Before it is considered done

- `buzz pack validate <dir>` passes
- `buzz pack inspect <dir>` shows the post-merge values you expected — **note that it prints a
  summary, not the whole resolved configuration.** MCP servers appear as a count, and runtime,
  pack instructions and hooks are not shown at all, so `inspect` agreeing with you is weaker
  evidence than it looks.
- Every behavioural setting that differs from the pack default has a written reason
- **You can show that the configuration you validated is the configuration that ran** — or the
  pack's README says plainly that you cannot, and why. Today, for this fork, the honest answer
  is that you cannot ([§8](#what-that-means-for-how-the-professor-runs)).
- The agent has been run against a real task, and its output checked by **whatever boundary
  answers question 2 for this agent** — not by reading it. If no such boundary exists yet,
  building it comes before the persona, not after.

---

## Open questions

**The first two block the persona body. The rest do not.**

1. **How does The Professor run?** Nothing consumes pack configuration at runtime, so the pack
   is a specification until something reads it. Route 1, 2 or 3 in
   [§8](#what-that-means-for-how-the-professor-runs) — and the answer also decides whether
   `temperature` configures anything, and how the handbook path reaches the MCP server.
2. **Where do drafts go?** A Buzz reply, a local file, a patch, or a pull request against the
   handbook. This decides whether the agent needs write access to a private repository at all —
   a read-only tool surface and one with a write tool are different designs.
3. **Which MCP server implementation** — extend `buzz-dev-mcp`'s pattern in a new crate, or a
   standalone process outside this repository? A new crate keeps it reviewable in-tree; a
   standalone one avoids adding a cohort crate to an upstream workspace.
4. **Read-only or read-write?** Reading the handbook is enough to draft against the contract.
   Writing drafted pages back is a different permission, and probably belongs to a pull request
   rather than to the agent. Largely settled by question 2.
5. **Does `check_page` call the gate directly, or reimplement it?** Reimplementing would
   produce a second parser that drifts from the first — the exact failure the gate's own
   modules are structured to avoid.
