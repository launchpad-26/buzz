---
id: corpus-template-configuration
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "node.schema.json's type enum has thirteen members -- architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion -- and none of them is template, policy, or configuration; the enum names the corpus surface a node documents, not the documentation form its prose takes."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Of the corpus's existing meta-documents on origin/launchpad, AGENTS.md carries type: agent while README.md, standards/confidence.md and standards/decision-references.md all carry type: governance, so governance is the precedent for a corpus node that documents the corpus's own authoring rules rather than a piece of architecture/capability/etc. content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "Two open, unmerged sibling template branches -- task/1335-corpus-template-decision-reference and task/1346-corpus-template-reference -- independently chose type: governance for their own template nodes, converging on the same value as the four merged meta-documents without having merged themselves; 'converged on', not 'landed on', is the accurate description, since neither sibling branch is on origin/launchpad at the time this node was written."
    entry_class: FACT
    evidence:
      - "git_show(ref='origin/task/1335-corpus-template-decision-reference', path='launchpad/docs/corpus/templates/decision-reference.md') -> front matter type: governance"
      - "git_show(ref='origin/task/1346-corpus-template-reference', path='launchpad/docs/corpus/templates/reference.md') -> front matter type: governance"
  - statement: "relationships.schema.json defines five relationship types -- depends-on, supersedes, implements, references, part-of -- with references' directionality stated as 'source cites target as supporting context; no ownership or currency dependency implied', generated inverse referenced-by."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "At repository revision a44cf52fc740ebebbdd671427480d14f0bce0115, the corpus tree on origin/launchpad contains exactly four validated nodes -- AGENTS.md, README.md, standards/confidence.md and standards/decision-references.md -- plus the schema/ subtree, which validate.py excludes from checking; none of the four documents configuration-shaped subject matter."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, schema/COMPATIBILITY.md, schema/README.md, schema/fixtures/**, schema/node.schema.json, schema/relationships.schema.json, schema/requirements.txt, schema/tests/test_schema.py, standards/confidence.md, standards/decision-references.md, at commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "The Twelve-Factor App's Config factor states an app's config is 'everything that is likely to vary between deploys', naming as examples 'Resource handles to the database, Memcached, and other backing services', 'Credentials to external services such as Amazon S3 or Twitter', and 'Per-deploy values such as the canonical hostname for the deploy'; it requires 'strict separation of config from code' because 'Config varies substantially across deploys, code does not', and states the litmus test as 'whether the codebase could be made open source at any moment, without compromising any credentials'."
    entry_class: FACT
    evidence:
      - "https://12factor.net/config"
  - statement: "The Twelve-Factor App's Config factor states the app 'stores config in environment variables', reasoning that 'Env vars are easy to change between deploys without changing any code; unlike config files, there is little chance of them being checked into the code repo accidentally', and that unlike config files or 'other config mechanisms such as Java System Properties, they are a language- and OS-agnostic standard'; it also excludes 'internal application config, such as config/routes.rb in Rails ... This type of config does not vary between deploys, and so is best done in the code.'"
    entry_class: FACT
    evidence:
      - "https://12factor.net/config"
  - statement: "The live 12factor.net/config page's own footer reads 'Written by Adam Wiggins - Last updated 2017 - Sourcecode - Download ePub Book', so the page carries an author and a last-updated year, but like Diataxis carries no version number of the kind MADR (4.0.0) or Keep a Changelog (2.0.0) publish, so a claim of the form 'per the current Twelve-Factor App' cannot be pinned to a revision the way a numbered spec can."
    entry_class: FACT
    evidence:
      - "https://12factor.net/config"
      - "curl_fetch('https://12factor.net/config') -> page footer text 'Written by Adam Wiggins - Last updated 2017 - Sourcecode - Download ePub Book', fetched directly rather than taken from a rendered summary"
  - statement: "Diataxis's own reference and colophon pages carry no version number and no last-updated date anywhere -- the reference page's footer reads only 'Copyright (c) Daniele Procida' with no year, and the colophon states 'Diataxis is the work of Daniele Procida. It has been developed over a number of years, and continues to be elaborated and explored', naming no date -- which is the basis for the comparison in the preceding entry: 12factor.net/config carries a last-updated year where Diataxis carries none."
    entry_class: FACT
    evidence:
      - "https://diataxis.fr/reference/"
      - "https://diataxis.fr/colophon/"
  - statement: "The Good Docs Project's Reference template guide (guide_reference.md) names, among the 'common scenarios where reference topics are appropriate': 'For software applications, configuration settings refer to individual settings or options. Providing these settings in a reference document can significantly improve a user's ability to understand the purpose and possible values of each setting.'"
    entry_class: FACT
    evidence:
      - "https://gitlab.com/tgdp/templates/-/raw/main/reference/guide_reference.md"
  - statement: "The Good Docs Project's templates README enumerates every template in all three of its packs (Core: Concept, How-to, README, Reference, Release notes, Tutorial, Troubleshooting; Open source community: Bug report, Changelog, Code of Conduct + its response/incident/remediation records, Contributing guide, Our team, README; Miscellaneous: API getting started, API reference, Contact support, Glossary, Installation guide, Quickstart, SDK overview, Style guide, Terminology system, User personas) and none of the three packs names a dedicated Configuration template."
    entry_class: FACT
    evidence:
      - "https://gitlab.com/tgdp/templates/-/raw/main/README.md"
  - statement: "The Good Docs Project templates repository's current canonical home, gitlab.com/tgdp/templates, licenses its LICENSE file as the MIT No Attribution License, copyright The Good Docs Project 2024. The archived github.com/thegooddocsproject/templates mirror (GitHub API reports archived: true, last push 2022-09-18) genuinely does carry a file titled 'Zero-Clause BSD' at LICENSE.txt, verified by fetching it directly -- so an unmerged research note that cites 'Zero-Clause BSD' from that mirror quoted a real source accurately, but a source the project has since moved off of and relicensed at its current canonical home; the practical guidance for a citation today is still to cite gitlab.com/tgdp/templates and MIT No Attribution, not the archived mirror."
    entry_class: FACT
    evidence:
      - "https://gitlab.com/tgdp/templates/-/raw/main/LICENSE"
      - "https://github.com/thegooddocsproject/templates/blob/104c4e69179166d18eebd752ed9901916ef5e348/LICENSE.txt"
      - "github_api('repos/thegooddocsproject/templates') -> archived: true, pushed_at: 2022-09-18T16:20:39Z"
  - statement: "Diataxis's reference page states 'Reference guides are technical descriptions of the machinery and how to operate it. Reference material is information-oriented.' Its explanation page, contrasting explanation against the other three forms, states explanation 'does not take the user's eye-level view, as in a how-to guide, or a close-up view of the machinery, like reference material' -- so 'a close-up view of the machinery' is Diataxis's own phrase for reference material, stated on the explanation page as the thing explanation is not, rather than a phrase appearing on the reference page itself."
    entry_class: FACT
    evidence:
      - "https://diataxis.fr/reference/"
      - "https://diataxis.fr/explanation/"
  - statement: "This repository's .gitignore excludes .env, .env.local and .env.*.local from version control while .env.example -- a template with placeholder/dev-only values -- is committed at the repository root, and the root AGENTS.md's Getting Started section instructs 'cp .env.example .env' as the first setup step; this is the Twelve-Factor separation (env vars outside the codebase, a non-secret template inside it) already in effect in this repository, not a pattern this node is proposing."
    entry_class: FACT
    evidence:
      - ".gitignore"
      - ".env.example"
      - "AGENTS.md"
  - statement: "crates/buzz-relay/src/config.rs defines the relay's Config struct with each field documented by a doc comment stating its source environment variable, default value and effect (for example drain_jitter_ms from BUZZ_DRAIN_JITTER_MS, capped at MAX_DRAIN_JITTER_MS, or redis_pool_size from BUZZ_REDIS_POOL_SIZE defaulting to 16), and reads the large majority of those fields via std::env::var or equivalent -- 87 call sites in that one file alone."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "launchpad/AGENT_PR_TEMPLATE.md's Verification checklist includes the unchecked box 'No secrets, keys, tokens or hostnames were added to tracked files', applied to every agent-authored pull request including one adding a corpus node -- a corpus node is itself a tracked file, so a configuration-surface node that quotes a live credential value would fail this same checklist."
    entry_class: FACT
    evidence:
      - "launchpad/AGENT_PR_TEMPLATE.md"
  - statement: "Parent Feature #605's acceptance criteria require that 'every template states its purpose, required sections, evidence expectations and the industry model/standard it adapts', and this is the acceptance bar this node is built against rather than issue #1332's own copied-over standards-track Definition of Done."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 acceptance criteria"
  - statement: "Issue #1332's own Definition of Done is byte-identical to the standards-track boilerplate ('States scope and authority/source of the policy. Separates MUST requirements from SHOULD guidance. Defines enforcement/checks and exception/escalation process. Links decisions or higher-order policy instead of duplicating them.'), the same text independently found copied across #1326-#1351."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1332 definition of done"
  - statement: "Issue #1332's Objective reads 'Create launchpad/docs/corpus/templates/configuration.md as the single canonical policy node for configuration', and issue #1326's Objective reads 'Create launchpad/docs/corpus/templates/architecture-component.md as the single canonical policy node for architecture component' -- the identical phrase 'policy node' applied to a different template task, confirming the word is boilerplate carried by the planning apparatus rather than a considered classification specific to #1332."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1332 Objective, compared against launchpad-26/buzz#1326 Objective"
  - statement: "An unmerged research note cataloguing industry-standard project documentation templates does not mention configuration, config files, environment variables or the Twelve-Factor App anywhere in its text."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1466 (unmerged research note, launchpad/Research/project-documentation-templates.md on branch docs/research-project-doc-templates)"
  - statement: "Because the Twelve-Factor App's Config factor is a design principle for how configuration should be structured and stored (deploy-variance, strict separation from code, environment variables) rather than a documentation-shape template -- it prescribes no sections for a document that catalogues settings -- and because no dedicated Configuration template exists in the Good Docs Project's three packs either, a corpus node documenting a configuration surface is best served by combining the Twelve-Factor principle (what qualifies as config, and the litmus test for it) with the Good Docs Project's generic Reference template shape, which its own guide already names configuration-settings documentation as an intended use case for, rather than by treating either source alone as sufficient or inventing a third shape neither source supports."
    entry_class: INFERENCE
    evidence:
      - "https://12factor.net/config"
      - "https://gitlab.com/tgdp/templates/-/raw/main/reference/guide_reference.md"
      - "https://gitlab.com/tgdp/templates/-/raw/main/README.md"
    confidence: 0.85
  - statement: "A configuration-surface node stands to the generic Reference template the way the Good Docs Project's own guide distinguishes a plain Reference article from an API Reference -- a specialization by subject matter and audience depth, not a different documentation form -- because the litmus test, deploy-variance and secret-handling requirements a configuration catalogue needs are domain-specific additions to the same information-oriented, structured-entry shape, not a reason to depart from it."
    entry_class: INFERENCE
    evidence:
      - "https://gitlab.com/tgdp/templates/-/raw/main/reference/guide_reference.md"
    confidence: 0.7
---

# Template: configuration

How to write a corpus node whose body catalogues a **configuration surface** --
environment variables, deploy-time settings, or other values a running instance of
this system reads rather than compiles in. States the required sections, the
evidence expectations for a settings-table claim, the industry model this template
adapts, and the explicit boundary against the generic reference template. This is a
template node, not a policy node -- it prescribes the shape of a future document's
*body*, not a MUST/SHOULD rule about corpus-wide behavior. See *Note on Definition of
Done* below for why that distinction matters for this specific node.

## Scope and authority

**This node covers** what a corpus node's body must contain when it documents a
configuration surface: which settings qualify as configuration at all, the required
sections, the evidence expectations for a settings-table row, the industry model it
adapts, and the boundary against the generic reference template.

**It does not cover** the front-matter contract itself (`node.schema.json` governs
that, unconditionally, for every node type, including which `type` surface value a
configuration-shaped node uses -- see *A note on `type`* below), how to create/
update/retire a node procedurally (`AGENTS.md` governs that), or the generic
reference template (`#1346`) that this template specializes -- see *Scope and
omissions* for the full boundary.

**Its authority is derived, not original.** The structural half is already law:
`node.schema.json` enforces front matter, `validate.py` runs that schema, and CI runs
`validate.py` on every corpus change. What this node adds is the half no schema can
hold -- which sections a configuration-shaped node needs, what evidence backs a
settings-table claim, and which industry models ground the shape. That half is
enforced by review, the same way the existing corpus standards describe their own
review-enforced half.

| For | Read |
|---|---|
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Prose walkthrough of those fields | `launchpad/docs/corpus/schema/README.md` |
| Relationship types and their directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| Citing an accepted decision as evidence | `launchpad/docs/corpus/standards/decision-references.md` |
| The generic reference template this one specializes | `launchpad/docs/corpus/templates/reference.md` (`#1346`, once merged) |
| The industry models this template adapts | *Industry model* below, and the primary sources it cites |

If this node and any of those disagree, **they win** -- this one has drifted and
should be fixed.

## Industry model this template adapts

**The Twelve-Factor App, Config factor** (Adam Wiggins, `12factor.net/config`,
page footer reads "Last updated 2017" -- dated, but carrying no version number the
way MADR 4.0.0 or Keep a Changelog 2.0.0 do). Its own words: an app's config is
*"everything that is likely to vary between deploys (staging, production, developer
environments, etc.)"*, and it requires *"strict separation of config from code"*
because *"Config varies substantially across deploys, code does not."* The **litmus
test** it supplies is the operational definition this template borrows wholesale:
*"whether the codebase could be made open source at any moment, without compromising
any credentials."* A setting that fails that test -- a value the codebase could not
survive being made public with -- is configuration; a value the codebase could
survive being made public with is not, no matter how often it is called "config" in
casual conversation.

**What Twelve-Factor explicitly excludes.** *"Note that this definition of 'config'
does not include internal application config, such as `config/routes.rb` in Rails,
or how code modules are connected in Spring. This type of config does not vary
between deploys, and so is best done in the code."* A configuration-shaped corpus
node documents the first kind, never the second -- a routing table or a dependency
wire-up belongs in an `implementation` or `architecture` node, not here, however
often it is labeled "config" in the source tree.

**Why environment variables specifically.** Twelve-Factor's stated reasoning: *"Env
vars are easy to change between deploys without changing any code; unlike config
files, there is little chance of them being checked into the code repo accidentally
... unlike custom config files, or other config mechanisms such as Java System
Properties, they are a language- and OS-agnostic standard."* This repository already
follows that pattern rather than merely being told to: `.gitignore` excludes `.env`,
`.env.local` and `.env.*.local` from version control, `.env.example` (placeholder
values only) is committed, and the root `AGENTS.md`'s Getting Started section
instructs `cp .env.example .env` as the first setup step. `crates/buzz-relay/src/
config.rs` reads the large majority of its `Config` struct's fields via
`std::env::var` calls, each documented with its source variable, default and effect.
A configuration-shaped corpus node describes settings that already work this way in
this repository; it does not need to argue for the pattern.

**The Good Docs Project, Reference template** (Core pack, `gitlab.com/tgdp/
templates`, MIT No Attribution License, copyright 2024 -- not "Zero-Clause BSD" as
an unmerged research note states; verified here by fetching the LICENSE file
directly, the same discrepancy `#1346`'s own node found and corrected). Its
accompanying guide names, among the scenarios a Reference article is *for*: *"For
software applications, configuration settings refer to individual settings or
options. Providing these settings in a reference document can significantly improve
a user's ability to understand the purpose and possible values of each setting."*
That sentence is load-bearing for this template's whole approach: the Good Docs
Project does not publish a separate Configuration template, but its own Reference
template guide names configuration-settings documentation as one of the things the
Reference shape exists to do.

**Why both, together.** Twelve-Factor supplies the *test* -- what counts as
configuration at all, and why it lives outside the codebase. The Good Docs Project
supplies the *shape* -- a description section, a structured-entry table, an optional
commands section -- that its own guide already recommends for exactly this content.
Twelve-Factor alone gives no template to fill in; the Reference template alone gives
no way to decide whether a given value belongs in the table in the first place. A
corpus node built from only one of the two would either have no way to draw its own
boundary, or no shape to draw it in.

**This is not a case of manufactured authority.** Unlike a generic "PRD template," for
which the parent research note found no standard at all, both sources here are real,
open, and say precisely what this node cites them for: Twelve-Factor's Config factor
is a genuinely load-bearing, widely-cited principle (this repository already follows
it), and the Good Docs Project's own guide names configuration settings as an
intended Reference use case in its own words, not by this node's extrapolation.

## Boundary: what this template is not

Read this section before drafting.

- **Not `#1346` (reference), but a specialization of it.** A configuration-shaped
  node is reference-shaped in Diátaxis's sense -- "information-oriented"
  (`diataxis.fr/reference/`), what Diátaxis's own explanation page calls, by
  contrast, "a close-up view of the machinery, like reference material"
  (`diataxis.fr/explanation/`) -- and the Good Docs Project's own guide treats
  configuration-settings documentation as a Reference use case, not a separate form.
  What earns this a separate template is the same reasoning the Good Docs guide uses
  to split a plain Reference article from an **API Reference**: audience depth and
  subject-specific requirements, not a different documentation form. A configuration
  node adds the litmus test, the deploy-variance framing, and the secrets discipline
  below -- requirements a generic reference table carries no obligation to enforce.
  A settings table with no deploy-variance claim and no secrets discipline is a
  `#1346`-shaped node that happens to describe settings, not a node built from this
  template.
- **Not `#1337` (event kind) or `#1342` (interface).** Neither of this batch's other
  new templates describes deploy-time settings; an event kind's wire shape and an
  interface's contract do not vary between deploys the way configuration does by
  definition, so there is no overlap to draw a line against here. If a future node
  needs to describe a setting that also shapes a wire contract (for example, a
  feature flag that changes which event kinds a relay accepts), that node likely
  needs both templates' required sections, declared as two `part-of` relationships
  to a broader capability node rather than forced into one.
- **Not an `implementation` node describing the code that reads the settings.** This
  template documents the *settings* -- their names, defaults, effects, and
  deploy-variance -- not the parsing/validation logic that loads them. A node
  describing `Config::from_env`'s validation rules, error types, or load order is an
  `implementation` node that may `references` this one, not an instance of it.
- **Not internal application config**, per Twelve-Factor's own exclusion above. A
  routing table, a dependency wire-up, or any value that "does not vary between
  deploys" fails the litmus test and does not belong in a node built from this
  template, regardless of what the source code calls it.

A node built from this template that drifts into any of these has picked the wrong
template, not merely written prose that needs tightening.

## A note on `type`

`node.schema.json`'s `type` enum (`architecture`, `layers`, `capabilities`,
`platforms`, `implementation`, `interfaces-events`, `verification`, `operations`,
`development`, `release`, `governance`, `agent`, `ingestion`) names the corpus
**surface** a node documents -- it has no member for documentation **form**
(reference/configuration/how-to/etc.), and this template does not invent one. A node
built from this template takes whichever `type` its subject matter's surface already
calls for -- for example `operations` for a deployment's environment variables, or
`development` for a local-dev-only `.env` setting with no production equivalent --
exactly as it would if the same settings were documented as prose instead of as a
table. This template node itself carries `type: governance` because it documents the
corpus's own authoring rules, per the precedent in the evidence ledger above, not
because configuration-shaped nodes in general use `governance`.

## Required sections

A corpus node using this template must carry the following in its body, in addition
to whatever schema-required front matter `node.schema.json` demands of every node:

1. **Configuration description.** One paragraph (Good Docs Project's own "Reference
   description" section, specialized) stating which configuration surface the node
   catalogues -- one service's environment variables, one deployment target's
   settings, or similar -- its scope, and which deploy(s) or environment(s) it
   applies to.
2. **Structured entries.** The settings themselves, as a table: at minimum the
   variable/setting name, its type or format, its default (or "none -- required"),
   whether it is required or optional, whether it is a **secret** per the litmus
   test below, and its effect. One row per setting. This template requires row
   order to match the source's own declaration order (e.g. `.env.example`'s
   section order, or the `Config` struct's field order), not alphabetically --
   this is this template's own requirement, not a convention the Good Docs
   Project's guide states; that guide is silent on row ordering, and this
   template does not attribute the choice to it.
3. **Litmus-test statement.** An explicit paragraph confirming every row in the
   table is genuinely deploy-varying per Twelve-Factor's test -- *"whether the
   codebase could be made open source at any moment, without compromising any
   credentials"* -- and naming, if relevant, any value the author considered and
   excluded because it fails the test (internal application config that does not
   vary between deploys).
4. **Secrets discipline.** A node built from this template **must never quote a
   live credential, key, token, or hostname value** -- not even a "just this once"
   example -- per `AGENT_PR_TEMPLATE.md`'s own verification checklist, which a
   corpus node is bound by like any other tracked file. A row for a secret setting
   cites *where* the value comes from (the environment variable name, the code that
   reads it, a placeholder like `.env.example`'s dev-only values) and never *what*
   the value is. Where an example is genuinely needed, use an obviously fake
   placeholder and say so.
5. **Boundary statement.** An explicit paragraph naming what this node does not
   cover, using the exclusions in *Boundary: what this template is not* as the
   checklist (not the generic reference template unless specialized this way; not
   an event-kind or interface contract; not the parsing/validation implementation;
   not internal application config that fails the litmus test), plus any
   node-specific exclusion the author found.
6. **Relationships**, per the guidance below.
7. **Scope and omissions**, per `AGENTS.md`'s own required step 8: what the node
   does not cover, who owns it, and separately, what was expected but could not be
   verified when the node was written.

### Template skeleton

Copy this structure; the bracketed placeholders are not literal content.

````markdown
# [Surface]: configuration

[One paragraph: which configuration surface this node catalogues, its scope, and
which deploy(s) or environment(s) it applies to.]

## Settings

| Variable | Type | Default | Required | Secret | Effect |
|---|---|---|---|---|---|
| ... | ... | ... | ... | yes/no | ... |

## Litmus test

Every row above varies between deploys per the Twelve-Factor litmus test --
"whether the codebase could be made open source at any moment, without
compromising any credentials." [Name anything considered and excluded because it
does not vary between deploys, if applicable.]

## Secrets discipline

No row above quotes a live credential, key, token, or hostname value. [Name where
each secret-marked row's value comes from -- the environment variable name, the
code that reads it, or a placeholder source -- never the value itself.]

## Boundary

This node does not describe:
- [the parsing/validation logic that loads these settings -- see the
  implementation node for <subject>, if one exists]
- [a wire contract or event-kind shape a setting happens to influence -- see the
  event-kind or interface node for <subject>, if one exists]
- [any node-specific exclusion]

## Relationships

- references: <an implementation node describing how these settings are loaded, if any>
- part-of: <a broader capability or deployment node this is a subsection of, if any>

## Scope and omissions

**This node covers** ...

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| ... | ... |

**Expected but not verified when this node was written:**
- ...
````

## Evidence expectations

The corpus-wide evidence rules in `AGENTS.md` apply unchanged: `FACT` means the
author opened the cited source, `INFERENCE` means the author reasoned to the claim
and rated the reasoning, `TEAM_KNOWLEDGE` means an uncorroborated statement
attributed to whoever said it. Nothing about this template relaxes or narrows that.
Four expectations follow specifically from the industry model this template adapts:

- **A settings-table row is a `FACT` or nothing.** Cite the code that reads the
  variable (e.g. a `std::env::var` call site, or the struct field it populates) or
  the `.env.example` entry that documents it -- not a recollection of what the
  variable "probably" does. A default value in the table must match the code's
  actual default, not a comment that may have drifted from it.
- **A default-value claim needs the code, not the example file, when the two could
  disagree.** `.env.example` documents a *suggested* value for local development;
  the authoritative default is whatever the loading code falls back to when the
  variable is unset. Where both exist, cite the code and treat the example file as
  a second, weaker source for what a "typical" value looks like.
- **A secret-status claim (row marked `Secret: yes`) is a `FACT` about the setting's
  *kind*, never about its value.** Cite the code path or the litmus test reasoning
  that makes it a credential-shaped value; never cite, and never produce, the value
  itself as evidence.
- **Do not cite a deployment runbook or a how-to guide as evidence for what a
  setting's default or effect *is*.** A runbook shows one path through a system
  under specific conditions; a configuration table asserts the general fact. Cite
  the loading code or the schema/spec that defines the setting, not a walkthrough
  that happened to set it once.

## Relationships

A node built from this template:

- **may** declare `references` toward an `implementation` node describing the
  parsing/validation logic that loads these settings, when a reader would benefit
  from the loading and validation behavior without this node re-describing it.
  Per `relationships.schema.json`, `references`' directionality is "source cites
  target as supporting context; no ownership or currency dependency implied" --
  exactly the loose coupling a settings-to-implementation pointer needs, since the
  settings table stays accurate even if the loading code is later refactored.
- **may** declare `part-of` toward a broader capability, deployment, or operations
  node this configuration surface is a subsection of, when the settings are one
  part of a larger documented surface rather than independently standing.
- **may** declare `references` toward the generic reference template (`#1346`,
  once merged) or toward this template node itself (target:
  `corpus-template-configuration`), if the author wants the generated
  `referenced-by` edge; this is optional, since a node's shape (Configuration
  description / Settings / Litmus test / Secrets discipline / Boundary) already
  shows which template it followed.
- **must**, per `AGENTS.md`'s own rule, resolve every declared target against
  `origin/launchpad` (or whatever the merge-target branch is at the time), never
  against the author's own worktree.

**This node's own relationships.** Declared: none. Checked: the four nodes present
in `origin/launchpad`'s corpus tree at the recorded revision -- `corpus-agents`,
`corpus-readme`, `corpus-standard-confidence`, `corpus-standard-decision-references`
-- are all procedural/meta-documents about the corpus itself, not configuration-
shaped subject matter this template about configuration documentation would
`references`, `depends-on`, or sit `part-of`. None of this batch's four sibling
templates (`#1337`, `#1342`, `#1345`, `#1349`) target this node or are targeted by
it, deliberately: all five are authored in parallel with no merge ordering between
them, so an edge to any of them would be as likely to break in CI as to resolve.
The generic reference template (`#1346`) this node specializes is also not yet
merged, so it is named in prose above rather than declared as a `references` edge --
the first configuration instance node, or a follow-up to this one once `#1346`
lands, is the natural moment to add it.

## Note on Definition of Done

Issue `#1332`'s own Definition of Done carries the same bullets found copied across
`#1326`-`#1351` -- "states scope and authority/source of the policy," "separates
MUST requirements from SHOULD guidance," "defines enforcement/checks and exception/
escalation process," "links decisions or higher-order policy instead of duplicating
them" -- verbatim from the standards-track issues that produced
`standards/confidence.md` and `standards/decision-references.md`. Those describe a
**policy/standard** node (a MUST/SHOULD normative document over existing corpus
behavior); this node is a **template** (a prescription for the shape of a future
document's body). The real acceptance criterion, from parent Feature `#605` itself,
is: *"every template states its purpose, required sections, evidence expectations
and the industry model/standard it adapts."* This node is built against that
sentence -- *Required sections*, *Evidence expectations* and *Industry model this
template adapts* above answer it directly -- rather than against the standards-track
checklist, which does not fit a document with no MUST/SHOULD normative claims about
existing system behavior to separate.

**This is not confined to the copied DoD checklist.** Issue `#1332`'s own
Objective line also calls this node "the single canonical **policy node** for
configuration" -- and `#1326`'s Objective uses the identical "policy node"
phrasing for its own (architecture-component) template, so the word is the
planning apparatus's default vocabulary for every document `#605` spawned,
template or not, not a considered classification specific to `#1332`. That
weakens, rather than strengthens, reading it as a deliberate instruction to
build a MUST/SHOULD standard here: an identical label attached uniformly to
both templates and standards distinguishes nothing, and `#605`'s own sentence
above is the only source in this reasoning that speaks to templates
specifically rather than reusing one word across both tracks.

## Scope and omissions

**This node covers** what a corpus node's body must contain when it documents a
configuration surface: which settings qualify as configuration under the
Twelve-Factor litmus test, the required sections, the evidence expectations for a
settings-table claim, the secrets discipline every such node must hold to, the
industry models (the Twelve-Factor App's Config factor + the Good Docs Project's
Reference template) the shape adapts, the explicit boundary against the generic
reference template and this batch's other new templates, the note that `type`
tracks corpus surface rather than documentation form, and the relationship types a
node built from this template should use.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The generic reference template (information-oriented cataloguing generally) | `#1346`, open and not yet merged at time of writing |
| The event-kind template (a kind's wire shape, tags, content semantics) | `#1337`, this batch |
| The interface template (a contract's shape) | `#1342`, this batch |
| The parsing/validation implementation that loads configuration | corpus's `implementation` surface, no specific issue found for it |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring any corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |
| Citing an accepted decision as evidence | `launchpad/docs/corpus/standards/decision-references.md` |
| Secrets handling for the codebase generally, beyond a corpus node's own text | Repository-wide practice, not a corpus concern |

**No relationships declared in this node's own front matter.** See *Relationships*
above for what was checked and why none of the four nodes that exist on
`origin/launchpad` at the recorded revision are a fit.

**Expected but not verified when this node was written:**

- **No node has yet been authored from this template.** Every claim above about
  what a configuration-shaped node needs is grounded in the Twelve-Factor App and
  Good Docs Project primary sources plus this repository's own `.env.example` /
  `config.rs` pattern, not in a worked corpus instance. The first real
  configuration node -- likely `buzz-relay`'s environment variables, given
  `crates/buzz-relay/src/config.rs`'s size -- is what will actually test whether
  the required sections above are sufficient or need revision.
- **Whether the litmus test cleanly classifies every setting in this repository was
  not checked row by row.** `crates/buzz-relay/src/config.rs` alone has dozens of
  fields; this node read a representative sample (bind address, pool sizes, drain
  jitter, git-hook HMAC secret) rather than auditing every field against the test.
  A future configuration node covering that file in full may find edge cases this
  template's required sections do not anticipate.
- **Whether `#1346`'s eventual merged text draws the reference/configuration
  boundary the same way this node draws it from its own side was not checked**,
  since `#1346` is not merged at time of writing; this node's boundary section
  reflects `#1346`'s current (unmerged) branch text, which may still change before
  merge.
- **Twelve-Factor App's original publication date (commonly cited elsewhere as
  2011-2012) was not independently verified here.** Only the live page's own
  footer ("Last updated 2017") was fetched and cited; no archival or changelog
  source for an earlier date was opened.
