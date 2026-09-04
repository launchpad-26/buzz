# The Professor

**A portable Skill-suite plugin, not a standalone agent** — pointed at one target repo at a
time: it scans a repo for undocumented or stale code, drafts and updates its documentation
library, tags every section with provenance, screens everything for sensitive content before
it's written, and keeps the resulting library organized. The distributable unit is the seven
skills plus their tool layer, installable via a marketplace into whatever agent a team already
runs; the bundled persona (`personas/the-professor.persona.md`) is an optional companion voice
for a team that wants a dedicated identity running these skills, not a requirement to use them.
A future goal (explicitly not scoped into any phase yet) is packaging this as a Docker image —
see the redesign document's Summary for why that would also help settle one of its open
questions, not just add a deployment option.

## Redesign proposal (2026-09-03): from one handbook to any repo — Phase 0 resolved, Phases 1–7 not yet built

**Nothing below this line describes what's built.** The group's consensus (2026-09-03) is to
retire MCP entirely — that settles this proposal's central architectural question — but no
script, gate, or dry run exists yet; Phases 1–7 are still a proposal awaiting a go-ahead.
Everything below this section describes the pack as it was actually built for
[#9](https://github.com/launchpad-26/buzz/issues/9) — a single skill (`draft-page`)
hard-coupled to one target, `launchpad-26/handbook`, via a module-level constant in
`tools/server.py`, an MCP server (`professor-tools`) for its five tools, and a gate script
shelled out from that one repo's checkout. That build is accurate history and still describes
exactly what ships in this pack's `tools/` directory today — this redesign hasn't touched it.

The full proposal — why that coupling was accidental rather than necessary, the seven
sub-skills that replace one, why it retires MCP in favor of a plain script-based tool layer
(a bigger move than, and a confirmed departure from, #1402's in-flight dual-mode fix), the
eight-phase-plus-1b build plan, and what's scaffolded in this branch versus left for later phases —
is written up in
[`launchpad/Research/the-professor-skill-suite-redesign.md`](../../Research/the-professor-skill-suite-redesign.md).
Read that document first, especially its §1a and §9, before forming an opinion on this
README alone. This README's older sections below are preserved as the record of what
was actually observed running the original single-skill build, which the redesign
document cites and builds on rather than repeats.

## Model

`anthropic:claude-sonnet-5` (`model` field, `provider:model-id` format
per `PERSONA_PACK_SPEC.md` §4/§10). The Professor's `draft-page` skill is a
multi-tool-call job — resolving pins, fetching source content, checking claims
against it — before it ever writes a sentence, so it needs a model capable of
sustained tool-calling and reasoning across that chain, not just prose
generation. This is a starting choice, not a benchmarked one; no comparison
against a cheaper tier has been run.

## Temperature: 0.4 (starting value, not yet validated)

`temperature: 0.4` is set in `personas/the-professor.persona.md`. This is a
**reasoned starting value**, not an empirical one — no real drafting attempt
has happened yet. `the-professor-design.md` §6 lays out the actual tension:

- **Factual synthesis wants it low.** The Professor's job is not just prose —
  it resolves pins, decides whether a source supports the sentence in front of
  it, and tags which claims came from where. Per the design doc, "tools
  resolve metadata, not meaning": fetching a source doesn't stop the model from
  inventing what that source says, which claim to make from it, or what to
  quietly drop. That's the accuracy-sensitive part of the job, and it's the
  part the whole provenance/claim-tagging gate exists to catch.
- **Voice wants room.** The entire point of a fixed persona (rather than
  "whatever model drafted this page") is a consistent, readable author across
  many pages. Too low a temperature risks flat, repetitive prose that reads
  like a template rather than a voice.

**Where this pack lands, and why:** the failure mode that actually damages
trust in a documentation corpus is a fabricated or misattributed claim, not a
slightly less varied sentence. A page with a plain but accurate voice is
recoverable; a page with a fluent but invented claim is not — a reader has no
way to tell it apart from a correct one without redoing the verification work
themselves. So this pack leans toward the factual side of the tension, but
not all the way to it: The Professor's output is longform, multi-paragraph
prose meant to read as one person's writing across a whole corpus, not
terse structured verdicts (contrast the security-reviewer persona in
`examples/meadow-core`, which runs at `0.3`). `0.4` sits below the
`examples/meadow-core` default (`0.7`, used by its conversational
orchestrator) and below its architecture-reviewer persona (`0.5`, prose that
leans more discretionary than ours), reflecting that claim fidelity is this
persona's primary risk — while staying above the most conservative end of
that range so the prose doesn't flatten out.

**This is explicitly not evidence.** `the-professor-design.md` §6 is clear
that the meadow-core numbers are "two downward overrides from a default... a
real pattern, and still two choices in one example pack rather than a law."
`0.4` is a reasoned starting point, chosen before any real drafting attempt
exists to test it against.

**Open dependency:** whether `temperature` (and `model`) reach any runtime at
all is downstream of a runtime decision this plan has not made yet (tracked as
a later step in this plan, not this one). Pack resolution currently projects
`temperature` only to `GOOSE_TEMPERATURE`, per `the-professor-design.md` §6 —
if the eventual runtime isn't Goose, this field may configure nothing. That
open question doesn't block setting the field now (the pack format requires
it), but it does mean this value shouldn't be read as confirmed-effective yet.

**Validation still to come:** per this plan, a real drafting attempt (a later
step) will exercise this persona against actual pages, and the step after that
records what was observed — whether `0.4` produced accurate, consistently
voiced drafts, or needs to move. Nothing in this document should be read as
that observation; it is the reasoning that precedes it.

## Observed Behaviour (Step 16)

A real drafting attempt happened: `[upstream] Persona Pack format`, citing
`block/buzz` (`crates/buzz-persona/PERSONA_PACK_SPEC.md`) pinned at `main` via
`resolve_pin`, plus `[launchpad]` claims citing `launchpad-26/buzz` at `refs/heads/launchpad`
(`AGENTS.md` §3 and `launchpad/review-agent/`'s existence), both resolved to real
full-SHA commits rather than recalled from memory. The draft passed `check_page`
clean — zero findings, `page_index.ok: true` — independently re-verified against
the real tool after the fact, not just trusted from the transcript.

**`temperature: 0.4` looks right.** The prose is accurate, consistently voiced, and
explicitly honest about its own limits — e.g. "I have a tool that can confirm a
path exists at a pinned commit, and none that reads a file's contents — so I
checked that the spec file is there and pinned it; I did not read what it says."
That is exactly the claim-fidelity-over-flourish behaviour §6's reasoning aimed
for. No real evidence yet that a different value would do better or worse — this
confirms the starting choice was reasonable, not that it is optimal.

**A genuine capability gap surfaced, and it is not a persona defect.** The
drafting reasoning and tool use (`read_contract`, `resolve_pin`, `path_exists_at`,
`check_page`) all worked correctly end-to-end. But once the draft was composed and
validated, the agent had no tool that could write it to disk or post the reply —
only this pack's five read-only MCP tools were ever wired into the runtime; goose's
own built-in shell/file-write extension was never enabled during setup. The agent
correctly recognised it needed to "write the finished draft to disk," said so, and
then looped indefinitely re-verifying with the only tools available, since none of
them could finish the job. The controller extracted the already-validated draft
content from the ACP wire log, independently re-ran `check_page` against it to
confirm the result still holds, and placed it by hand at
`/tmp/the-professor-scratch-drafts/persona-packs-upstream-spec-fork-local-tooling.md`.

**This means Step 16 was not a fully autonomous, one-mention-to-finished-file
proof.** The reasoning and validation are real and the agent's own work; the save
step was not. That gap is exactly why Route 3 (below) has to define a real write
path before this pack is genuinely load-bearing — a scribe that cannot write is
not yet the thing being built toward.

## Runtime Route: Plain `buzz-acp` configured from the environment (Route 2)

The Professor runs as a plain `buzz-acp` process with environment variables
configured to match the pack's resolved values — values that `buzz pack inspect`
displays as a final checklist. This is Route 2 of three candidates
(`the-professor-design.md` §8 lays out the full reasoning).

**Why Route 2 over Route 1 (desktop app recreation):** The desktop app is a GUI,
and GUI actions are neither scriptable nor testable in an agent session. Route 2
uses environment configuration, which is testable and repeatable in a CI/CD
pipeline or a local agent-driven setup. A change to the environment is visible;
a manual recreation in a desktop UI is not. This makes the persona pack
reviewable in its actual runtime context.

**The specification-vs-configuration distinction:** Until something reads the
pack at runtime and automatically configures the agent from it, **this pack is a
specification the runtime is configured to match, not configuration the runtime
reads**. The CLI validates and inspects the pack, and the values it prints are
the source of truth for how to set up the agent's environment. If the pack
changes, the runtime must be reconfigured separately by a human or a script
reading the pack's output. This is a defensible design choice — it puts the
decision about how the pack is consumed into a separate issue — but it must be
stated rather than implied.

**Route 3 (the projector) is filed separately.** A future step in this plan
(Step 20, tracked as a GitHub issue) will propose a small tool that resolves
the pack and emits `buzz-acp` configuration deterministically, making the pack
genuinely load-bearing. That closes the gap between "pack is validated" and
"pack is what runs". For now, the pack is the source document, and the
environment is the runtime configuration.

## Credential Policy: Bring Your Own Key

Route 2 (above) already puts credential custody one layer below the pack: whoever's
environment launches `buzz-acp` supplies the provider and key via
`GOOSE_PROVIDER`/`GOOSE_MODEL`/the provider's own API-key env var (e.g.
`ANTHROPIC_API_KEY`). The pack itself never touches a credential — it only declares the
model shape it wants (`provider:model-id` in the persona frontmatter). This isn't a new
mechanism added for this decision; it's simply naming, explicitly, what Route 2 already
does by construction.

**Decision:** each person running The Professor locally uses their own key. There is no
shared cohort credential for this pack, and none is planned for the interactive Route 2
runtime — consistent with Ruling 5's substitutability requirement (no model, and by
extension no credential, gets to be load-bearing for the pack itself).

This differs in shape from `launchpad-26/buzz#53` / ADR-0012 (the upstream-synthesis
inference credential): that ADR governs a *shared*, unattended CI credential with its
own custody, spend, and rotation obligations. BYOK carries none of that weight — there's
no shared secret to fund, rotate, or leak across two systems, because there isn't a
shared one at all.

**Carve-out for Route 3.** Bring-your-own-key only works while a person is present to
start the process and supply it. If The Professor ever runs unattended (Route 3, the
projector — filed as its own follow-up issue at Step 20), there's no individual in the
loop to bring a key, and that runtime will need its own credential decision. This
section does not answer that question and should not be read as having answered it.

## Draft Output: Scratch Path (Not a Pull Request)

For #9's bounded acceptance criteria — *"drafts a page, passes the gate without hand-editing"* — a scratch-path draft (stored in a temporary directory, not committed to the handbook, not opened as a pull request) is sufficient.

**This diverges from the design doc's own conclusion.** Section "Also unspecified: where drafts go" argues that the enforcement boundary (the gate) decides where output goes, and since the gate runs **on pull requests**, drafts should go to pull requests to be checked. By that principle, a scratch draft is "a draft nothing checks."

**Why this divergence is acceptable here:** #9's acceptance does not itself require a pull request — it requires only that a drafted page passes the gate when run manually (Steps 16-17 in the plan). A real write-path against a private repository (the handbook) is a separate permission-boundary decision; the design doc names it as Open Question 2 and explicitly excludes it from #9's scope. Backing into write capability by expanding this issue's scope would be the wrong way to settle that question. Instead, a scratch draft lets #9 deliver its bounded deliverable (a persona that drafts and validates) without making write-permission decisions that belong elsewhere.

### Tool Server: Read-Only Confirmed

All five tools in `launchpad/agents/the-professor/tools/server.py` are read-only. Confirmed review:

- **`read_contract()`** (lines 112–121): Fetches the handbook's page contract from GitHub via `gh api`. Reads and returns; no writes.
- **`list_categories()`** (lines 124–137): Fetches and parses mkdocs.yml from the handbook. Reads and returns a list; no writes.
- **`resolve_pin(repo, ref)`** (lines 143–200): Resolves a branch/tag/SHA to a full 40-character commit SHA via `gh api`. Reads and returns; no writes, no commits, no pushes.
- **`path_exists_at(repo, commit, path)`** (lines 203–257): Checks if a path exists at a given commit via `gh api`. Reads and returns a boolean; no writes.
- **`check_page(draft_content)`** (lines 344–439): Runs the handbook's provenance gate against a draft page. Refreshes a local handbook checkout via `git fetch` and `git reset` (read operations), writes the draft to an isolated scratch temp directory for testing only, shells out to the handbook's real gate scripts, and returns their results. No pushes, commits, or PR creation. The only write is to a temporary isolated directory with no persistence beyond the call.

None of the five tools performs a write, push, commit, or PR-create call to GitHub or the handbook repository. The tool surface is entirely read-only.
