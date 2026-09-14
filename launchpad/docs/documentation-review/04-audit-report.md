# Output 5 — Documentation audit report

## In plain terms

**What this is.** What I found when I ran the checklist over everything in `launchpad/`.

**Who it's for.** Maintainers deciding what to fix, and in what order.

**What to do with it.** Read the four P1 findings. They are the ones worth acting on this
week. Everything below P1 can wait.

**The short version.** Nothing dangerous. No live credentials — the only credential-shaped
strings are five test fixtures for secret-detection tooling, and no value was reproduced
anywhere. No broken security reporting, no destructive command pointed at an unknown target. But two documents said a
sign-off check protects you and it does not exist; the coverage report flatters itself; and
93.7% of the corpus is still draft. I checked 43 of 122 items — **the other 79 were not
checked, which is not the same as them passing.**

**What changed since.** Six of the sixteen findings are **already fixed in this branch** —
the six that needed no decision from you (F-01, F-06, F-09, F-10, F-11 partly, F-12). The
findings below are kept as they were written, with the fix recorded against each, because an
audit that edits itself to match the repository stops being evidence. The ten that remain
need either a decision only you can make or work larger than a text fix.

**What I got wrong.** More than one thing, and a second model found most of it. F-12 reported
two broken links; one was my own checker's error. The citation count, the link count, the
credential count and the symlink count were all wrong or unreproducible — **none of my census
figures could be reproduced by either reviewer, because I never committed the scripts that
produced them.** The credential count was wrong in the worst direction: it said one match
where there are five. All are corrected below, with `census.py` committed so the numbers can
be checked rather than believed. Read *Census figures corrected* and *Defects found in this
framework* before trusting any number here.

### How the audit was run

```mermaid
flowchart TD
    A["Freeze one revision<br/>78e789369"] --> B["Count everything<br/>2,376 files"]
    B --> C["Automated checks<br/>over ALL of it<br/>citations · links · secrets · structure"]
    C --> D["Sort by consequence<br/>security · recovery · destructive first"]
    D --> E["Deep-read the risky ones"]
    D --> F["Random sample<br/>seed 20260914"]
    E --> G["Open the cited source<br/>does it really say this?"]
    F --> G
    G --> H["16 findings<br/>P0:0 P1:4 P2:9 P3:3"]
    C -.-> I["Record what was<br/>NOT checked"]
    G -.-> I
```

*In words:* freeze one revision so every measurement refers to the same thing; run
automated checks across the whole population; sort what remains by how much harm an error
would cause; deep-read the risky material and a random sample; verify sampled claims by
opening the source they cite. Findings come out of that, and so does an explicit record of
everything left unchecked.

---

## Review identity and bounds

| Field | Value |
|---|---|
| **Object** | The `launchpad/` subtree of `launchpad-26/buzz` |
| **Frozen baseline** | `78e789369e3392f187e8c63753262669108fda81` (2026-09-14, `origin/launchpad`) |
| **Baseline history** | **Measured at `b4a78fe3b7c01da6a986f15e0021f5a486f9abc2`.** `origin/launchpad` advanced to the stated head while the review was running; the baseline was re-pointed only after every finding-bearing path was verified unchanged across the two revisions. See "Re-baselining" below |
| **Population** | 2,376 tracked files, of which **1,651 Markdown**. Within `launchpad/docs/corpus/` (excluding `schema/`): 748 files = **719 canonical nodes + 29 registered generated outputs** |
| **Criteria** | `03-master-checklist.md` v1.1 (122 items) |
| **Methods used** | Full-population deterministic census; purposive deep review of high-risk artefacts; a **seeded random discovery sample** (seed `20260914`, 6 nodes from a 727-node frame) |
| **Methods NOT used** | No reader, operator or contributor task testing. No rendered-surface accessibility evaluation. No screen-reader, keyboard, zoom or contrast exercise. No procedure executed end to end. No reviewer calibration. No statistical sample |
| **What this report may support** | A remediation baseline and a first risk-ranked worklist |
| **What it may NOT support** | Any statement that the corpus is correct, complete, accessible or usable. Deep review was purposive; per `14-documentation-review-at-corpus-scale.md` its results **must not be projected to the population** |

---

## Coverage declaration

| Layer | Coverage achieved |
|---|---|
| Deterministic checks (citations, links, relationships, secrets, structure) | **Census** — 100% of the in-scope population |
| Semantic claim verification | **4 claims across 4 nodes** from the random sample. 0.5% of nodes |
| Genre / architecture / procedure review | **Purposive** — entry points, standards, generated views, deploy runbooks |
| Accessibility | **Source-level only.** Rendered-surface conformance: `UNABLE_TO_ASSESS` |
| Task fitness | **Not assessed.** No reader was tested |

Checklist items assessed: **43 of 122**. The remaining 79 are `NOT_EVALUATED` — not passes.
This distinction is required by `FOUND-012` and is the single most important thing to
carry out of this report.

---

## Findings by priority

### P0 — Critical

**None confirmed.** Stated plainly rather than left implicit: the census found no exposed
credential, no unresolvable citation, no broken security-reporting route, and no
destructive instruction without a bounded target.

**Read that with the correction below attached.** The credential scan originally reported
one fixture match; there are five. The conclusion is unchanged — every one sits in a
declared fixture directory for secret-*detection* tooling, and no value was reproduced —
but a P0 result resting on a count that was wrong by 5× deserves the caveat in the same
place as the claim, not fifteen sections later.

That is a real result, and it is bounded: it covers what deterministic checks and a
purposive review can reach. It does **not** establish that no P0 defect exists — the
classes with no mechanical enumerator (unstated prerequisites, usage constraints, negative
behaviour, per `F07`) were not assessed at all.

---

### P1 — High priority

#### F-01 · The DCO check that two entry points say is enforced does not run
- **Checklist** `DEV-008`, `AGENT-017` · **Status** `INCORRECT`
- **Existing evidence** `launchpad/AGENTS.md:395` — "The DCO check fails any commit without a `Signed-off-by` trailer"; `launchpad/README.md:123` — "the DCO check is not optional"; `launchpad/AGENTS.md:390` — "`-s` is required: DCO check".
- **Code evidence** 0 of **33** tracked files under `.github/workflows/` contain `dco` or `signed-off-by` (case-insensitive, whole-word). Independently: **39** distinct check runs on merged PR #2245 in `launchpad-26/buzz`, **zero** matching `dco|sign.?off`. Prior corroboration: `launchpad/Research/354-dco-check-on-vendor-drops.md` (2026-08-22, 40 PRs scanned).
- **Platform evidence, added 2026-09-14 after a cross-model review challenged the categorical wording.** The objection was fair and is the reason this line exists: workflow text plus one PR's check runs cannot by themselves establish *"nothing here rejects an unsigned commit"*, because a GitHub App or a repository **ruleset** can require a check that no workflow file mentions. This repository's own history contains that exact trap — the legacy branch-protection endpoint can return `404` while a ruleset enforces, so querying one and not the other reads as "no gate" when a gate exists. So both were queried directly:

  | Probe | Result |
  |---|---|
  | `GET /repos/launchpad-26/buzz/rulesets` | `[]` — no rulesets exist |
  | `GET /repos/launchpad-26/buzz/rules/branches/launchpad` | `[]` — no rule applies to the base branch |
  | `GET /repos/launchpad-26/buzz/branches/launchpad/protection` | **no `required_status_checks` key at all**; `required_approving_review_count: 1`, `dismiss_stale_reviews: true`, `require_code_owner_reviews: false` |

  A check that is not *required* cannot reject anything, and there are no required checks of any kind. The claim now rests on three independent sources — workflow text, observed check runs, and the platform's own enforcement configuration — rather than on the first two. **The challenge strengthened the finding rather than overturning it**, which is the outcome an adversarial review is for.
- **Gap** An enforcement mechanism is asserted as fact in the fork's normative spec and its README. It does not exist in this fork. The sentence is true in the root `AGENTS.md`, which is upstream's guide — this is `F09`'s **A3 transplanted obligation** producing **A2 phantom enforcement**.
- **Risk** Contributors and agents rely on a gate that will never catch their mistake. Unsigned commits accumulate and are discovered later, when a branch must be rebased with `--signoff`.
- **Recommended action** Either install a DCO check and keep the sentence, or rewrite both sentences to state what actually happens. **Taken: the sentences were rewritten** — see *Stage 0 remediation*.
- **Sharpened after remediation.** The original wording above said the `commit-msg` hook "enforces" sign-off. It does not, and the distinction is the whole finding. `lefthook.yml:73-76` runs `git interpret-trailers --if-exists doNothing --trailer "Signed-off-by: …" --in-place {1}`: it **adds** the trailer to the message being written. There is no exit-non-zero path, so it cannot reject a commit — it silently repairs the omission when `just hooks` has been run, and silently does nothing when it has not or when `--no-verify` is passed. Calling that "enforcement" would have replaced one phantom gate with a smaller one, which is why the remediation describes the hook as *adding* rather than *checking*.
- **Destination** `launchpad/AGENTS.md` §6; `launchpad/README.md` "Opening a PR".
- **Effort** Small (text) or Medium (install the check). **Owner** Maintainer.
- **Validation** Re-run both checks; the sentence and the check-run list must agree.
- **Note on priority** The checklist default for `DEV-008` is P0 because enforcement claims can be security gates. This instance is rated **P1**: the consequence is process friction, not exposure. The priority model is applied to the finding, not inherited from the item.

#### F-02 · The generated coverage report's `documented` disposition is earned by file-level citation, not by documenting the item
- **Checklist** `FOUND-011`, `FOUND-004` · **Status** `INCORRECT`
- **Existing evidence** `launchpad/docs/corpus/generated/coverage.md` — "**37 of 408 in-scope source items are `GAP` rows at this revision**". Its own contract states `documented` is "earned by a canonical node's file/position citation".
- **Code evidence** Every `config:` row lists a near-identical set of ~46 crediting nodes. Sampled five nodes credited with documenting `config:PGPASSWORD` — `layers-data-redis-role`, `layers-networking-heartbeat`, `operations-runbooks-redis-unavailable`, `capabilities-git-git-object-storage`, `corpus-template-datastore` — **each mentions `PGPASSWORD` zero times**. Same result for `TYPESENSE_API_KEY`. 74 nodes cite `.env.example` at all.
- **Gap** Any node citing `.env.example` is credited with documenting *every* key in it — including a **template** being credited with documenting a production database password. The headline reads as 91% coverage; the numerator is not what a reader will take it to be.
- **Risk** Exactly `16-coverage-inflation.md`'s inventory substitution: the visible numerator grows faster than the definition of what must be covered, and the 37 real GAPs look like the whole gap.
- **Recommended action** Require key-level evidence (`\.env\.example:LINE` matching the key's line, or the key name appearing in the node) before awarding `documented`; re-run; expect the GAP count to rise substantially. Until then, add a sentence to `coverage.md` stating that `documented` means "some node cites the file this item lives in".
- **Destination** `launchpad/project-intelligence/corpus/index_defs/coverage.py`; regenerate `generated/coverage.md`.
- **Effort** Medium. **Owner** Developer.
- **Validation** After the change, a node crediting a config key must contain that key.
- **Credit where due** `coverage.md` is *honest about its mechanism* — it states the disposition rule in its own inclusion rules. The defect is that the headline number will be read as something the mechanism does not support.

#### F-03 · The corpus grew 3.5× while the count of `active` nodes did not move
- **Checklist** `GOV-010`, `FOUND-010` · **Status** `PARTIAL`
- **Existing evidence** At baseline: **47 `active`, 701 `draft`** (93.7% draft). The research baseline of 2026-09-08 recorded **47 active of 205**.
- **Code evidence** Front-matter census over all 748 files at the frozen revision.
- **Gap** 543 nodes were added in roughly eight days and not one was promoted. Either promotion is blocked on a gate nobody has run, or `draft` has become the corpus's resting state and carries no information.
- **Risk** `14-documentation-review-at-corpus-scale.md` warns that `draft` does not mean "ignore" — draft material is still found, cited, copied and used by agents. A 93.7% draft corpus that agents read as authoritative has a lifecycle vocabulary that is not doing any work.
- **Recommended action** Decide what promotion requires (`SYNTHESIS.md` adoption decision 3) and either promote a first tranche or state explicitly that `draft` is the expected steady state for generated-from-code nodes.
- **Destination** `launchpad/docs/corpus/standards/status.md`; a governance decision.
- **Effort** Large. **Owner** Human decision.
- **Validation** Either the active count moves, or the status standard says why it will not.

#### F-04 · Confidence values diverge from the standard that governs them, at scale
- **Checklist** `FOUND-011`, `AGENT-021` · **Status** `FAIL`
- **Existing evidence** `launchpad/docs/corpus/standards/confidence.md`: "Two decimal places are not warranted. The scale has no calibration behind it, so `0.83` claims a precision that nothing supports."
- **Code evidence** **349 of 794** `INFERENCE` confidence values (44.0%) use two decimals. The research measured 166 of 384 (43.2%) on 2026-09-09. The *rate held* while the absolute count more than doubled.
- **Gap** A documented rule with no checker does not propagate. The standard's own limitation — "Enforced mechanically: nothing" — is now demonstrated over a population 2× larger.
- **Risk** False precision. A reader comparing `0.83` and `0.85` is comparing noise.
- **Recommended action** Add a deterministic check to `validate.py` restricting `confidence` to the standard's declared band values. This is a Level-A predicate and is cheap.
- **Destination** `launchpad/project-intelligence/corpus/validate.py`.
- **Effort** Small. **Owner** Developer.
- **Validation** The check fails on a seeded two-decimal value and the corpus converges.

---

### P2 — Medium priority

#### F-05 · Audience overdeclaration has increased
- **Checklist** `FOUND-002` · **Status** `PARTIAL`
- **Evidence** **625 of 748** files (83.6%) declare ≥3 of the 4 permitted audiences; **127** declare all four; only 122 declare two, and one declares none. The research measured 75.1% at ≥3 on 2026-09-09.
- **Gap** The corpus's own entry point argues that `audiences` means "who this is written *for*", and calls its own exclusion of `agent` "the corpus's first deliberate audience *exclusion*". The permissive reading has won by a wider margin than when it was measured.
- **Risk** The field is satisfied syntactically and cannot route review or filtering.
- **Action** Either narrow the semantics (and lint for ≥3 as a review trigger) or redefine the field as "may read" and stop treating it as a pitch declaration. **Effort** Medium. **Owner** Maintainer.

#### F-06 · The confidence standard still carries visible merge damage
- **Checklist** `HUMAN-004`, `AGENT-023` · **Status** `INCORRECT`
- **Evidence** `launchpad/docs/corpus/standards/confidence.md` contains **2 H1 headings** and **3 `---` delimiters** in 417 lines. The duplicate `## Requirements`/`## MUST` headings the research found on 2026-09-09 have been fixed; the front-matter/H1 duplication has not, five days later.
- **Corpus-wide** **33 of 748** files contain more than one H1. 715 contain exactly one; none contain zero.
- **Gap** No tracked Markdown linter configuration exists anywhere in the repository (`markdownlint`, `.mdlrc`, `vale`, `remarkrc` — all absent), so nothing catches this class.
- **Risk** Low direct harm; high signal value. A structural defect survived five days in the standard whose subject is honest confidence, which is precisely `F13`'s "polished structure, corrupt substance".
- **Action** Repair the file; add a heading-structure lint. **Effort** Small. **Owner** Developer.

#### F-07 · Diagrams carry no accessible name or description
- **Checklist** `HUMAN-010`, `FOUND-008` · **Status** `PARTIAL`
- **Evidence** **68** Mermaid fences across the corpus; **0** occurrences of `accTitle` or `accDescr`. The research measured 28 fences / 0 accessibility metadata on 2026-09-08; both scaled.
- **Bounded** The active diagram standard requires every diagram claim to appear in prose, which may already supply an equivalent route. **I did not verify that it does**, for any diagram. The honest verdict is: accessible-name metadata is absent and prose equivalence is `UNKNOWN`.
- **Risk** Information available only visually, for an unknown share of 68 diagrams.
- **Action** Sample 5 diagrams; hide each and check the remaining prose supports the same conclusion. Add `accTitle`/`accDescr` where the renderer supports them. **Effort** Medium. **Owner** Technical Writer.

#### F-08 · Table density is the corpus's largest unassessed accessibility surface
- **Checklist** `HUMAN-012` · **Status** `UNKNOWN`
- **Evidence** **721 of 748** files (96%) contain a GFM table. GFM provides one header row and no caption, row-header or complex-header syntax.
- **Gap** Not assessed — no rendered surface was inspected. Recorded as `UNABLE_TO_ASSESS` rather than converted to a pass.
- **Risk** Wide grids carrying prose become unusable one cell at a time under assistive technology.
- **Action** Assess after the delivery surface is decided (see `HC-2`). **Effort** Medium. **Owner** Human decision, then Technical Writer.

#### F-09 · An archived deployment runbook containing destructive commands does not say it is archived
- **Checklist** `GOV-007`, `ARCH-010` · **Status** `INCORRECT`
- **Evidence** `launchpad/deploy/archived/runbooks/dev-deployment-SOP.md` opens identically to the live `launchpad/deploy/runbooks/dev-deployment-SOP.md` — same title, same "What you will have at the end" framing — with no superseded banner in its body. It contains `sudo rm -rf /opt/buzz/web /opt/buzz/admin-web` at line 3179.
- **Gap** The path says `archived/`; the document does not. `F09` D3 and `R07` are explicit that a superseded record retaining its prose "reads as though it still binds" — and a search hit or an agent's retrieval does not show the reader a directory name.
- **Risk** An operator or agent follows a retired procedure containing destructive steps.
- **Action** Add a superseded banner above the first heading naming the live replacement. **Effort** Small. **Owner** DevOps.
- **Validation** The first screen of the archived file says it is archived.

#### F-10 · A destructive command's rationale is placed after the block that contains it
- **Checklist** `HUMAN-008` · **Status** `PARTIAL`
- **Evidence** `launchpad/deploy/runbooks/dev-deployment-SOP.md:3004` runs `ssh … 'sudo rm -rf /opt/buzz/web /opt/buzz/admin-web'`. The explanation — "The `rm -rf` first matters: copying onto an existing folder nests the files *inside* it" — appears **after** the code block.
- **Bounded assessment** This is `R08`'s "warnings after commitment" pattern, but the consequence here is low: the targets are explicitly named, narrow, and on a disposable local dev VM (`127.0.0.1:2222`). It is a `PARTIAL`, not a `FAIL`, and P2 rather than P0. Rated on consequence, not on pattern match.
- **Action** Move the rationale above the block. **Effort** Small. **Owner** DevOps.

#### F-11 · The subtree's entry point does not route to contribution, licence or conduct guidance, and the root guidance it would inherit is disavowed
- **Checklist** `GOV-001`, `GOV-002`, `GOV-003`, `START-002` · **Status** `PARTIAL`
- **Evidence** `launchpad/README.md` contains **zero** mentions of `CONTRIBUTING`, `LICENSE`, or `CODE_OF_CONDUCT`. Those files exist at the repository root. But `launchpad/AGENTS.md:29–32` states that the root `CLAUDE.md`/`AGENTS.md` are "upstream's contributor guide" and that for cohort work "that guidance **is wrong, not merely irrelevant**".
- **Gap** A contributor to `launchpad/` who follows the root `CONTRIBUTING.md` is following a process the fork explicitly disavows, and nothing in the subtree's entry point tells them otherwise.
- **Risk** Wasted contributor effort; contributions shaped by the wrong process.
- **Action** Add a short routing block to `launchpad/README.md`: what governs contributions here (`launchpad/AGENTS.md`), what the licence is, where the code of conduct lives. **Effort** Small. **Owner** Maintainer.

---

#### F-15 · Almost nothing carries a diagram, and no entry point does
- **Checklist** `READER-002`, `ARCH-002` · **Status** `FAIL`
- **Evidence** **67 of 748** corpus files (8%) contain a Mermaid diagram. Of the seven top-level entry points — `README.md`, `AGENTS.md`, `ARCHITECTURE.md`, `VISION.md`, `REQUIREMENTS.md`, `SECURITY-POSTURE.md`, `ENVIRONMENTS.md` — **none contains a diagram at all**, including `ARCHITECTURE.md`.
- **Gap** `R10` is explicit that topology, sequence, containment and relationships are the shapes prose carries worst. An architecture document with no diagram asks every reader to rebuild the structure from sentences, and they will each rebuild it differently.
- **Risk** `F14`'s divergent mental models, entering through the front door rather than through drift.
- **Recommended action** Add one diagram per entry point, and to corpus nodes whose subject has parts, steps or states. Mermaid — it is text, it diffs, and it renders on GitHub. Each diagram needs an equivalent description in words (`HUMAN-010`), or it trades one access problem for another.
- **Destination** The seven entry points first; then architecture and flow nodes.
- **Effort** Medium. **Owner** Technical Writer + Developer.
- **Validation** Re-run the count. Every entry point has a diagram and a text equivalent.

#### F-16 · Whether documents open with a readable summary is unverified
- **Checklist** `READER-001` · **Status** `PARTIAL`
- **Evidence** **628 of 748** corpus files (83%) have more than 80 characters of prose between the title and the first subheading, so the *shape* of an opening summary is common. All seven entry points have one (322–452 characters).
- **Bounded — and this is the point** A block of intro prose is not the same thing as a summary a non-specialist can read and understand in 30 seconds. Establishing that requires reading each one against a timer, with someone who is not its author. **I did not do that**, so this is `PARTIAL`, not a pass.
- **Risk** The measurable proxy looks healthy while the property that matters is untested — which is the failure mode `F07` names as structural completeness substituting for substantive completeness.
- **Recommended action** Timer-test the seven entry points with someone who did not write them. That is an hour of work and it converts an unknown into a result.
- **Effort** Small. **Owner** Human.
- **Validation** A recorded result per entry point: what is this, who is it for, what do I do next — answered inside 30 seconds.

---

### P3 — Low priority

#### F-12 · One relative link does not resolve — *corrected down from two; now remediated*
- **Checklist** `START-002` · **Status** `FAIL` at audit → **`PASS` after remediation** · **1**
  genuine broken link, fixed. *(The "745 links checked" denominator originally quoted here is
  withdrawn as unreproducible — see "Census figures corrected". `census.py` reports 1,540 by a
  stated rule. The finding itself is unaffected: it concerns which links were broken, not how
  many were counted.)*
- **Genuine, and fixed:** `launchpad/docs/corpus/schema/README.md:11` → `../../plans/2026-08-25-issue-622-corpus-schema.md`
  resolved to `launchpad/docs/plans/`; the file is at `launchpad/plans/`. Corrected to `../../../plans/`.
- **False positive, withdrawn:** `launchpad/docs/corpus/standards/linking.md:41` was **not** a broken link
  and **no change was made to it**. Line 41 sits *inside* that node's YAML front matter, which closes at
  line 120. The string is part of a `FACT` statement that **quotes README.md's link as an example** of the
  style it documents. Relative to `launchpad/docs/corpus/README.md` — the file that actually contains the
  link — `../../decisions/` resolves to `launchpad/decisions/`, which exists. My checker resolved it against
  `linking.md`'s own directory (`standards/`) instead of the quoted file's. See methodological correction 4.
- **Effort** Small. **Owner** Developer. **Validation** Re-run the link check. Done — see *Stage 0 remediation* below.

#### F-13 · A public test fixture contains a high-entropy synthetic token indistinguishable from a real credential
- **Checklist** `OPS-011` · **Status** `PASS with observation`
- **Evidence** `launchpad/agents/the-professor/tools/contract/fixtures/block-api-key.md` contains a 44-character token with 40 distinct characters. The file is a deliberate fixture for a secret-*blocking* tool, sits beside `block-private-key.md`, `block-password-literal.md` and 40 other fixtures, and states in its own body "placeholder shape only, never a real credential".
- **The value was not reproduced at any point in this review**, in line with `R15`'s stop-and-route rule.
- **Observation** It is benign, and it is also indistinguishable from a live key to GitHub secret scanning, to any external scanner, and to a future reader. Every scan of this repository will keep surfacing it.
- **Action** Make fixture tokens unmistakably non-functional (an `EXAMPLE_`/`NOTAREALKEY_` prefix, or a charset no provider issues) and record the allowlist. **Effort** Small. **Owner** Developer.
- **Confirmation still wanted:** a human who owns the fixture should confirm it was synthesised, not copied. A shape check cannot establish that.

#### F-14 · Twenty-nine nodes use quoted YAML scalars where the rest of the corpus does not
- **Checklist** `AGENT-023` · **Status** `PARTIAL`
- **Evidence** 29 nodes write `status: "draft"`, `type: "governance"`, `origin: "launchpad"` and quoted audience values; 85 evidence entries use `entry_class: "FACT"`.
- **Bounded** YAML parses `"draft"` and `draft` to the same string, so **schema validation is unaffected and these nodes are valid**. This is a source-consistency observation, not a defect.
- **Action** Normalise, or state in the standard that both forms are acceptable. **Effort** Small. **Owner** Developer.

---

## Human confirmation required

| ID | Question | Why research cannot answer it |
|---|---|---|
| **HC-1** | What is the documentation obligation register for `launchpad/`? | Every coverage number, including `coverage.md`'s own, has an undeclared denominator until this exists (`R04`) |
| **HC-2** | Which rendered surface is official, at what WCAG level, and who owns renderer-controlled failures? | `R13` poses this and explicitly declines to answer it |
| **HC-3** | Under what licence is `launchpad/` documentation published? | Legal decision |
| **HC-4** | Which of the eight hard gates block a merge? | `SYNTHESIS.md` adoption decision 1; an advisory gate documented as enforced is `F09`'s durable failure |
| **HC-5** | Is `draft` the intended steady state for generated-from-code nodes? | Governance decision underlying F-03 |
| **HC-6** | Was the `block-api-key.md` fixture token synthesised rather than copied? | A shape check cannot establish provenance |

---

## Not applicable

| Item | Reason |
|---|---|
| `GOV-008` (changelog) | `launchpad/` is a subtree of a fork, not a released artefact. The root `CHANGELOG.md` is upstream's |
| `API-004` (rate limits) | The `launchpad/` subtree exposes no API of its own |
| `HUMAN-008` for `layers/data/postgres/partitions.md` and `layers/security/provider-boundary.md` | `DROP TABLE` and `rm -rf` appear there only as **quoted test inputs** for injection-rejection tests, not as instructions |

---

## Positive results

The corpus requires that positive findings be recorded, not only defects. These are the
strongest, and several represent remediation of defects the research itself found.

| Result | Measurement |
|---|---|
| **Citation resolution** | **`validate.py` exits 0 with 0 errors** across all 748 files — every citation the repository's own validator can resolve, resolves. *The precise counts originally given here (18,715 of 20,680) are withdrawn as unreproducible; see "Census figures corrected".* |
| **Positional citation bounds** | **0 out-of-bounds** line/range citations (symlink-resolved) |
| **Relationship integrity** | **1,341** typed edges, **0 unresolved targets** |
| **Relationship coverage** | **516 of 748** files (69%) declare relationships, up from 89 of 205 (43%) at the research baseline |
| **Link health** | **1,526 of 1,540** relative links resolve at this branch's HEAD, by `census.py`'s stated rule. **13 of the 14 unresolved are quoted link-syntax examples inside `standards/`, not links.** *The "745" originally given here is withdrawn — no reviewer, including me, could reproduce that denominator.* |
| **Credential hygiene** | **5** credential-shaped matches across 5 files, every one a test fixture — see the correction below. *This row originally read "0 matches … One match, a self-labelled fixture", which was wrong.* |
| **Claim entailment** | **4 of 4** claims sampled from the seeded random sample are exactly supported by their cited source at the cited line range — including a verbatim module-doc quotation. *Not projectable* |
| **Generated-view discipline** | Every generated index declares generator, script, inputs, ordering, input digest, and **both** inclusion and exclusion rules; `stale-docs.md` explicitly refuses to claim a flagged node's FACT is false, "which AGENTS.md itself calls 'a narrowing step, not a certification'" |
| **Denominator honesty** | `INDEX.md` states 719 canonical nodes, names all 29 excluded generated outputs, and reports "0 discovered file(s) failed to parse or validate" |
| **Remediated since the research** | The README/AGENTS **approving-review contradiction** (found by reports 10, 14 and 15 as a live defect on 2026-09-09) is **fixed** — both now say "one" |
| **Remediated since the research** | The **32 out-of-bounds** positional citations and **309 nonexistent-path** citations measured on 2026-09-06 are now **zero** |

---

## Methodological corrections made during this audit

Recorded because `F02` requires that tool-mediated evidence failures be visible rather
than silently absorbed. Four of my own checks produced false positives. The first three were
corrected before any finding was drawn from them; **the fourth was not — it reached F-12 as a
published finding and is corrected here**:

1. **50 "broken links"** — an artefact of extracting only `launchpad/` from the archive, so
   links to files outside it appeared unresolvable. Re-run against the full tracked file
   list: **2** genuine.
2. **18 "out-of-bounds citations"** — all to `CLAUDE.md`, which is a **symlink** (mode
   `120000`) to `AGENTS.md`. My line counter read the 1-line symlink blob. Symlink-resolved:
   **0**.
3. **A 29-node "discrepancy"** between my 748-file count and `INDEX.md`'s declared 719 —
   my arithmetic, not the index's. 748 − 29 registered generated outputs = 719. The index
   was correct and had stated its exclusions explicitly.
4. **One of F-12's two "broken links"** — `launchpad/docs/corpus/standards/linking.md:41`. The
   string is *inside front matter* (which closes at line 120), within a `FACT` that quotes
   **README.md's** link as a style example. My checker resolved every relative link against the
   directory of the file the *text* sits in, which is right for a real link and wrong for a
   quoted one. Resolved against `launchpad/docs/corpus/README.md`, the target exists.
   **1** genuine, not 2.

   This one is worth more than the correction. Unlike the first three it was **not** caught
   before publication: it was written up as a defect, given a status and an action, and would
   have sent someone to "fix" a correct file — the concrete form of the harm `R05` describes
   when a checker's contract is reported as a property of the repository. It survived because a
   link check is easy to trust and its two results looked alike: an identical `../../` prefix
   and an identical off-by-one story made the false one corroborate the true one. **Two findings
   sharing a shape is a reason to re-derive the second independently, not a reason to believe
   it.** Finding 4 is also the only one to touch the `Link health` positive-result figure, so a
   false positive had propagated into a *favourable* measurement as well as an adverse one.

---

## Re-baselining after PR #2259

Every measurement in this report was taken at
`b4a78fe3b7c01da6a986f15e0021f5a486f9abc2`. PR #2259
(`feature/2151-professor-discoverability`) subsequently merged, advancing
`origin/launchpad` to `78e789369e3392f187e8c63753262669108fda81` across 13 commits.

`git merge-base --is-ancestor b4a78fe3b 78e78936` exits 0, so the measured revision is a
genuine **ancestor** of the stated one rather than merely older by date — the test
`AGENT-024` requires, because in a merge-based history those two orders disagree.

The corpus's own provenance rule — and this checklist's `FOUND-010` and `AGENT-024` —
forbid advancing a recorded revision unless every claim is known to hold at the new one.
So the baseline was **not** simply updated. Each path carrying a finding was diffed
between the two revisions:

| Path | Files changed between baselines |
|---|---|
| `.github/workflows/` | 0 |
| `launchpad/AGENTS.md` | 0 |
| `launchpad/README.md` | 0 |
| `launchpad/docs/corpus/` | 0 |
| `launchpad/deploy/` | 0 |
| `launchpad/agents/the-professor/tools/contract/fixtures/` | 0 |

All six are byte-identical, so **all 16 findings hold unchanged**. F-01 was additionally
re-verified directly at the new head: `launchpad/AGENTS.md` still asserts the DCO check,
and 0 of 33 workflow files reference `dco` or `signed-off-by`.

What #2259 did change: `launchpad/agents/the-professor/**` (README, persona, seven
`SKILL.md` files) and one added plan document. It also registered the Professor's skills at
the repository root by symlink.

**One consequence for future audits — figures corrected 2026-09-14.** This paragraph
previously said the repository's symlink count "has gone from one (`CLAUDE.md`) to
nineteen". **That was wrong**, and a cross-model review caught it. Measured with
`git ls-tree -r <rev> | awk '$1==120000'`:

| Scope | `b4a78fe3b` | `78e789369` | Change |
|---|---|---|---|
| Whole repository | **53** | **81** | +28 |
| `launchpad/` only | **2** | **2** | 0 |

The new registrations are seven per directory across `.agents/`, `.claude/`, `.codex/` and
`.goose/` — 28, not nine each in two directories. **"One" was never the repository's symlink
count**; it was the count of symlinks I had personally tripped over (`CLAUDE.md`), silently
generalised into a claim about the repository. That is the same move F-02 criticises in
`coverage.md`: a number true of the sample restated as a number about the population.

The *conclusion* survives and is worth keeping: `AGENTS.md` §4's rule requiring symlink
resolution before checking line bounds — written because a naive line count of `CLAUDE.md`
returns 1 and produced 18 false positives in this audit — now applies to 81 paths rather
than 53. But note the sharper fact the corrected figures expose: **within the audited
subtree the symlink count did not move at all.** The growth is entirely outside
`launchpad/`, so for *this* audit's scope the change is no increase in risk. The original
wording would have had a future auditor brace for a hazard that did not grow.

**Re-run at the new head — corrected 2026-09-14.** This paragraph previously said the
citation, link, relationship and secret censuses were not re-run "because their input trees
are byte-identical". A cross-model review pointed out that this was **true only of the
corpus**. The citation and relationship censuses take `launchpad/docs/corpus/` as input, and
that tree is byte-identical, so carrying them forward is sound. But the **link and secret
censuses covered all of `launchpad/`**, and 11 files there did change — the Professor's
README, persona, `.plugin/plugin.json` and seven `SKILL.md` files, plus a new 695-line plan.
Claiming a 100% census while carrying forward a measurement whose input had moved is
`FOUND-011`'s own failure, in the document that defines it.

Rather than weaken the claim with a caveat, the two affected censuses were **re-run over the
11 changed files**:

| Census | Input | Result at new head |
|---|---|---|
| Relative links | 11 changed files | **1 of 1 resolve**, 0 broken |
| Credential patterns (AWS, GitHub, Slack, Google, PEM) | 11 changed files | **0 matches** |

So the census figures stand, and now on measurement rather than on an inference that did not
hold for two of the four. The citation and relationship censuses remain carried forward on
the byte-identical corpus tree, which is a stronger guarantee than re-running would provide.

---

## Stage 0 remediation applied in this branch

The roadmap's Stage 0 is the set of fixes that are unambiguous, small, and need no
maintainer decision. All six were applied **in this branch**, so this report describes a
state that no longer fully holds — recorded here rather than by silently editing the
findings, because an audit that quietly rewrites itself to match the repository stops
being evidence of anything.

| # | Finding | Change | Now |
|---|---|---|---|
| 0.1a | F-01 | `launchpad/AGENTS.md` — the DCO-check assertion replaced with what actually happens: no CI check, a `commit-msg` hook that *adds* the trailer, and upstream as where it bites | `INCORRECT` → `PASS` |
| 0.1b | F-01 | `launchpad/README.md` — same correction in "Opening a PR" | `INCORRECT` → `PASS` |
| 0.2 | F-09 | `launchpad/deploy/archived/runbooks/dev-deployment-SOP.md` — ARCHIVED banner pointing to the live SOP | `DUPLICATED` → `PASS` |
| 0.3 | F-10 | `launchpad/deploy/runbooks/dev-deployment-SOP.md` — the `rm -rf` rationale moved **above** the block it warns about | `FAIL` → `PASS` |
| 0.4 | F-12 | `launchpad/docs/corpus/schema/README.md:11` — `../../plans/` → `../../../plans/` | `FAIL` → `PASS` |
| 0.5 | F-06 | `launchpad/docs/corpus/standards/confidence.md` — duplicated front matter and second H1 repaired | `FAIL` → `PASS` |
| 0.6 | F-11 | `launchpad/README.md` — governance/licence/conduct routing table, each target's applicability to *this fork* stated | `FAIL` → `PARTIAL` |

**Two of these deserve more than a table row.**

**0.5 recovered evidence rather than deleting it.** The damage in `confidence.md` was a
merge that left an orphaned fragment between two `---` delimiters: three YAML lines
stranded in the body, under a stale code-formatted H1. The obvious repair — delete the
stray lines, keep the good H1 — would have destroyed a `TEAM_KNOWLEDGE` entry recording
Serina's decision on `launchpad-26/buzz#1486`. That entry is the *provenance for the very
H1 style the repair adopts*: it says the H1 must no longer code-format the topic. So the
fragment was moved **into** the front matter ledger and only the stale duplicate H1
removed. The node now has 14 evidence entries (10 FACT, 2 INFERENCE, 2 TEAM_KNOWLEDGE),
one H1, two delimiters. `launchpad/project-intelligence/corpus/validate.py` exits 0 with
**0 errors** across the corpus. A destructive "tidy" would also have passed that
validator — schema validity would not have noticed the loss, which is why the check was
read before the edit rather than after.

**0.6 is a partial fix, deliberately.** The routing table tells a reader which governance
file applies to this fork and which is upstream's. It does **not** answer `HC-3` — the
licence covering `launchpad/` documentation — because that is a legal decision no audit
can make. The table records the gap in place rather than papering over it.

**Not fixed here, and why.** F-02, F-03, F-04, F-05, F-07, F-08, F-13 and F-14 are
untouched. Each needs either a maintainer decision (`HC-1` through `HC-6`), a change to
generated tooling, or work larger than Stage 0 admits. They are Stages 1–5 of the roadmap.

**Verification after remediation:** corpus validator exits 0, 0 errors; `confidence.md`
front matter parses with its ledger intact; the one genuine broken link is fixed; the framework's
own 16 self-checks pass. What has *not* been re-run is the full citation, relationship and
secret census — the Stage 0 edits touched six files, none of which carry positional
citations, so those censuses are unaffected. That is a reasoned exemption, not an
assumption: if a later stage edits corpus nodes, the censuses must be re-run.

---

## Defects found in this framework by cross-model review

The framework was reviewed by a second model (Codex) before this branch was proposed for
merge. It was told to refute rather than confirm. It found real defects **in the auditing
instrument itself**, which are recorded here rather than quietly patched, because a
framework that hides its own failures has no standing to demand disclosure from anything
else.

### S-01 · The self-test could not detect a dropped checklist item — `BLOCKER`, fixed

The suite scanned `03-master-checklist.md` with `^\*\*([A-Z]+-\d{3}) ` — **the generator's
own shape**. Deleting one space from an item heading (`**READER-002 ·` → `**READER-002·`)
made both parsers skip the same item. The generator wrote 121 items; `item_count`
self-reported 121; the two ID sets matched *because both were missing the same ID*; the
suite exited 0. The README claimed at the time that the generator "fails loudly rather than
silently dropping an item".

Reproduced independently before fixing: one character, 122 → 121, exit 0.

This is precisely the failure class this checklist names in `AGENT-019` and the research
corpus calls **coverage theatre** — a check whose passing is guaranteed by its own
construction. Generating one artefact from another removes *drift*; it does not remove
*silent loss*, because both sides inherit the same blind spot. **A parity test written in
the generator's vocabulary cannot see what that vocabulary cannot express.**

Fixed by making the suite's scan deliberately *looser* than the generator's
(`^\*\*([A-Z]+-\d{3})\b`), so the two parsers can disagree. The same mutation now fails with
`differ by ['READER-002']` and exit 1, and the unmutated tree still passes.

### S-02 · Parity compared identifiers, not content — `MAJOR`, fixed

The suite compared ID sets and field *presence*. A YAML `requirement` could be replaced with
text contradicting the Markdown and the suite still passed. Demonstrated by substituting
`READER-001`'s requirement with its own negation: exit 0.

Fixed by comparing normalised requirement text per ID. The same substitution now fails with
`requirement text is identical in Markdown and YAML — ['READER-001']`.

### S-03 · Reader-first checks certify weaker predicates than their names claim — `MINOR`, open

`READER-001` passes on a summary heading appearing *anywhere*, not at the top.
`READER-002b` passes on a single `*In words:*` marker anywhere in the file, not one per
diagram. The fence check tests parity only. Anchor-only links are skipped by the link check.
Each is a real gap between the name and the predicate. Filed rather than fixed: they need
the predicates redesigned, not patched, and that is Stage 1 work.

### What this says about the audit above

Two of my three self-checks on the instrument were weaker than their labels, and a
second model found in one pass what I had not found while writing the thing. The audit's
own P0 result — "none confirmed" — is bounded by method and says so, and this is the
concrete shape of that bound. **Treat every `PASS` in this report as "this check did not
fail", not "this property holds".**

---

## Census figures corrected, and made reproducible

Two independent reviewers tried to reproduce this report's census numbers and could not.
That is the most serious class of defect an audit can have — not a wrong number, but a
number **nobody can check**. The cause was mundane and entirely mine: the censuses were run
from throwaway shell pipelines that were never committed, so the rule that produced each
denominator existed only in my session.

The fix is `census.py`, committed beside this report. It states each rule in the code that
applies it and prints every figure below. `python3 census.py <rev>` reproduces this section.

### The citation count was wrong, and the category boundary is the reason

| Source | Repository-path citations | Total citation strings |
|---|---|---|
| This report, as first published | 18,715 | 20,680 |
| Reviewer A (Codex) | 18,791 | 20,850 |
| Reviewer B, independently | 18,791 | 20,850 |
| `census.py`, delegating to `validate.py` | 17,844 | 20,801 |

**Four methods, four answers, over the same 748 files.** Nobody miscounted; each drew the
boundary of "repository-path citation" somewhere slightly different — whether a Markdown-link
citation counts as its target, whether a bare path without a line number counts, how graph
edges and tool results are bucketed. The two reviewers agreeing tells us their *rules*
agreed, not that the figure is canonical.

So the precise figure is withdrawn rather than restated with better arithmetic. **A count
whose definition is contested is not evidence, and picking whichever number has the most
votes would launder that disagreement into false precision.** `census.py` now imports
`validate.py`'s classifier instead of reimplementing it, so this repository has one
definition; but the honest reading is that the boundary itself needs deciding before any
figure is quoted.

**What survives, and it is the claim that actually mattered:**
`launchpad/project-intelligence/corpus/validate.py` exits **0** with **0 errors** over the
whole corpus. Every citation the repository's own validator can resolve, resolves. That is
reproducible by one command, it is the property the original figure was evidence *for*, and
it does not depend on how the buckets are drawn.

### The link denominator was not reproducible; it is now

The report claimed **745** relative links. Neither reviewer could reproduce it by any
method — they obtained 1,515 raw, 895 deduplicated, and 1,273 excluding fragments. Nor can
I. The figure is withdrawn.

`census.py` states its rule — every tracked `.md` file under `launchpad/`, every occurrence
rather than unique pairs, fragments stripped, anchors unverified — and at this branch's HEAD
reports **1,540 relative links, 1,526 resolving, 14 not**.

**13 of those 14 are the F-12 false positive again**, at scale: targets like `url`, `target`,
`...`, `AGENTS.md` and `file.md#some-heading` quoted *inside* `standards/linking.md`,
`standards/diagrams.md` and `standards/code-references.md` as examples of link syntax. A
document that teaches linking is full of strings shaped like links that are not links. The
one plausible genuine case is
`launchpad/plans/2026-08-26-issue-639-corpus-readme.md` → `schema/node.schema.json`, a
historical plan quoting a path relative to a file it is describing rather than itself.

**The checker still cannot tell a link from a quotation** — the same limitation that produced
F-12, now measured rather than stumbled over. Teaching it that difference is Stage 1 work; a
raw count is published here with the caveat attached, rather than a clean number that would
require silently discarding 13 results.

### The credential count was wrong — five matches, not one

The report said "0 matches … One match, a self-labelled fixture". The census finds **5
credential-shaped matches across 5 files**:

| File | Pattern |
|---|---|
| `launchpad/agents/the-professor/tools/contract/fixtures/block-private-key.md` | PEM private key |
| `launchpad/scripts/security_audit_fixtures/secrets/ssh_private_key.txt` | PEM private key |
| `launchpad/scripts/security_audit_fixtures/secrets/registry_token.txt` | GitHub token |
| `launchpad/scripts/security_audit_fixtures/secrets/s3_minio_keys.txt` | AWS access key |
| `launchpad/skills/review-queue-automation/tests/test_rqa_authority_secrecy.py` | GitHub token |

**No value was reproduced at any point**, in this report, in `census.py`'s output, or in the
session that produced either. Every match sits in a directory whose name declares it a
fixture for secret-*detection* tooling, so the security conclusion is unchanged: these are
the scanner's own test material.

But the original figure was still wrong, and wrong in the direction that matters. An audit
that undercounts credential-shaped matches by 5× has produced a *reassuring* error in the
one category where a reader is least able to check it themselves. F-13 discussed one fixture
as though it were the only one; it was an example, and the report presented it as the
population. **The corrected finding is not "there is a fixture" but "there are five, in
three separate subsystems, and none is allowlisted anywhere."**

### The draft percentage mixes two populations

**93.7%** is `701/748` — **all corpus files, including the 29 registered generated outputs**.
The canonical-node figure is `680/727 = 93.5%`. The difference is small; the undisclosed
denominator is not, in a report whose `HC-1` says no coverage number here has an agreed
denominator. Generated projections carry `status: draft` in front matter despite not being
on a draft→active maturity path at all, so folding them in measures something slightly
different from what the sentence claims. Both figures are now printed by `census.py`, which
refuses to pick one.
