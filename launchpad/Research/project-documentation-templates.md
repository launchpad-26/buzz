# Industry-standard project documentation templates

Researched 2026-08-26 · versions as stated per row; every version below is quoted
from the source that publishes it, not recalled

Written as a reference the Professor (`launchpad/agents/the-professor/`) can consult
when it is asked to produce a document of a given kind. It answers one question per
document type: **is there a canonical template, who publishes it, what version, and
what does it actually require?**

---

## What it is, and the problem it solves

"Industry standard documentation template" is not one thing. The document types split
into four tiers by how much authority actually stands behind them, and the tiers are
not what you would guess:

| Tier | What it means | Examples |
|---|---|---|
| **1 — Versioned spec** | A numbered, dated specification you can pin and cite | Keep a Changelog, SemVer, Conventional Commits, Contributor Covenant, MADR, OpenAPI |
| **2 — Canonical template, unversioned** | A widely adopted template with a single authoritative home, but no version number or date on the page | Diátaxis, arc42, C4, Standard Readme, Rust RFC, KEP |
| **3 — Paywalled formal standard** | A real ISO/IEC/IEEE standard, unreadable without paying | ISO/IEC/IEEE 26514, 29148 |
| **4 — No standard at all** | Vendor blog templates only; nothing authoritative to cite | PRD, "design doc" |

The problem this note solves: an agent asked for "a standard PRD template" will happily
produce one, and there is no standard to have produced it from. Knowing which tier a
request lands in tells you whether to *cite* a template or to *declare* one.

---

## The catalogue

### Decision records — ADR

**Nygard's original five sections** (Michael Nygard, 15 November 2011). Quoted verbatim:

> **Title:** "These documents have names that are short noun phrases."
> **Context:** "This section describes the forces at play, including technological, political, social, and project local."
> **Decision:** "This section describes our response to these forces. It is stated in full sentences, with active voice."
> **Status:** "A decision may be 'proposed' if the project stakeholders haven't agreed with it yet, or 'accepted' once it is agreed."
> **Consequences:** "This section describes the resulting context, after applying the decision. All consequences should be listed here."

**MADR 4.0.0** (Markdown Any Decision Records), released 17 September 2024 — the
maintained successor, and the one to copy. Template quoted verbatim from
`template/adr-template.md`:

```markdown
---
# These are optional metadata elements. Feel free to remove any of them.
status: "{proposed | rejected | accepted | deprecated | … | superseded by ADR-0123}"
date: {YYYY-MM-DD when the decision was last updated}
decision-makers: {list everyone involved in the decision}
consulted: {list everyone whose opinions are sought (typically subject-matter experts); and with whom there is a two-way communication}
informed: {list everyone who is kept up-to-date on progress; and with whom there is a one-way communication}
---

# {short title, representative of solved problem and found solution}

## Context and Problem Statement
## Decision Drivers          <!-- optional -->
## Considered Options
## Decision Outcome
### Consequences             <!-- optional -->
### Confirmation             <!-- optional -->
## Pros and Cons of the Options   <!-- optional -->
## More Information          <!-- optional -->
```

The one section worth noticing is **Confirmation** — "Describe how the implementation /
compliance of the ADR can/will be confirmed. Is there any automated or manual fitness
function?" Most hand-rolled ADR templates omit it, and it is the section that stops an
ADR being an unenforced opinion.

### README

**Standard Readme** — the spec is undated and carries no version number. Section order
is normative. Quoted verbatim:

Required: `Title` ("must match repository, folder and package manager names") ·
`Short Description` ("Must not have its own title. Must be less than 120 characters") ·
`Table of Contents` ("Required; optional for READMEs shorter than 100 lines") ·
`Install` · `Usage` (both "Required by default, optional for documentation
repositories") · `Contributing` ("State where users can ask questions") ·
`License` ("Must be last section").

Optional: `Banner` · `Badges` · `Long Description` · `Security` · `Background` ·
`Extra Sections` · `API` · `Maintainers` · `Thanks` ("Must be called Thanks, Credits
or Acknowledgements").

### Changelog

**Keep a Changelog 2.0.0**, published 7 June 2026 — the current version, and the one to
cite. The six change types are unchanged from 1.x, quoted verbatim:

> "Added for new features. Changed for changes in existing functionality. Deprecated for
> soon-to-be removed features. Removed for now removed features. Fixed for bug fixes.
> Security for vulnerabilities."

Guiding principles in 2.0.0, quoted verbatim:

> "Changelogs are for humans, not machines. Every version should have an entry. Group
> changes of the same type. Make versions and sections linkable. List the latest version
> first. Show the release date of each version. Note which versioning scheme you use.
> Write plainly."

**Do not cite `keepachangelog.com/en/1.1.0/`.** That URL still serves live, and it is
what a search for "keep a changelog" tends to surface, but 2.0.0 supersedes it — see
Corrections below. 2.0.0's changes are to the guidance and framing, not to the six
types, so a changelog already written to 1.1.0 does not need rewriting.

Pairs with **SemVer 2.0.0**: "MAJOR version when you make incompatible API changes;
MINOR version when you add functionality in a backward compatible manner; PATCH
version when you make backward compatible bug fixes" — and **Conventional Commits
1.0.0**:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Proposals — RFC / KEP / design doc

**Rust RFC template** (`0000-template.md`, unversioned): Summary · Motivation ·
Guide-level explanation · Reference-level explanation · Drawbacks · Rationale and
alternatives · Prior art · Unresolved questions · Future possibilities.

**Kubernetes KEP template** (`keps/NNNN-kep-template/README.md`, unversioned) — the
heavier of the two, and the only mainstream proposal template that forces operational
thinking:

Release Signoff Checklist · Summary · Motivation (Goals, Non-Goals) · Proposal (User
Stories, Notes/Constraints/Caveats, Risks and Mitigations) · Design Details (Test Plan,
Graduation Criteria, Upgrade / Downgrade Strategy, Version Skew Strategy) ·
**Production Readiness Review Questionnaire** (Feature Enablement and Rollback;
Rollout, Upgrade and Rollback Planning; Monitoring Requirements; Dependencies;
Scalability; Troubleshooting) · Implementation History · Drawbacks · Alternatives ·
Infrastructure Needed.

**BCP 14 = RFC 2119 + RFC 8174** supplies the requirement keywords any of these should
use when stating obligations. RFC 2119 (Scott Bradner, March 1997) defines them:

> **MUST:** "This word, or the terms 'REQUIRED' or 'SHALL', mean that the definition is an absolute requirement of the specification."
> **SHOULD:** "…there may exist valid reasons in particular circumstances to ignore a particular item, but the full implications must be understood and carefully weighed before choosing a different course."
> **MAY:** "This word, or the adjective 'OPTIONAL', mean that an item is truly optional."

**RFC 8174** (Barry Leiba, May 2017) amends it, and the amendment is the part people get
wrong: "The words have the meanings specified herein only when they are in all capitals."
Lowercase "must" and "should" are ordinary English and carry no obligation. RFC 8174 also
notes the keywords are optional — "normative text does not require the use of these key
words." Use the current boilerplate, not RFC 2119's older one:

> "The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD
> NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to
> be interpreted as described in BCP 14 [RFC2119] [RFC8174] when, and only when, they
> appear in all capitals, as shown here."

### Architecture

**arc42** — twelve sections, CC BY-SA 4.0, © 2003–2026, no version number on the
overview page: 1. Introduction & Goals · 2. Constraints · 3. Context & Scope ·
4. Solution Strategy · 5. Building Block View · 6. Runtime View · 7. Deployment View ·
8. Crosscutting Concepts · 9. Architectural Decisions · 10. Quality Requirements ·
11. Risks & Technical Debt · 12. Glossary.

**C4 model** (Simon Brown, undated): System context diagram · Container diagram ·
Component diagram · Code diagram. Diagrams, not prose — it slots into arc42 §3/§5/§7
rather than competing with it.

### Operational — runbook and postmortem

**Google SRE Workbook** (2018) on playbooks, quoted verbatim:

> "high-level instructions on how to respond to automated alerts. They explain the
> severity and impact of the alert, and include debugging suggestions and possible
> actions to take to mitigate impact and fully resolve the alert."

> "In SRE, whenever an alert is created, a corresponding playbook entry is usually created."

With the caveat that if a playbook becomes "a deterministic list of commands that the
on-call engineer runs every time a particular alert fires", it should be automated
instead of documented.

**Google SRE Book postmortem template** (2017, Appendix D), section headings verbatim:
Summary · Impact · Root Causes · Trigger · Resolution · Detection · Action Items ·
Lessons Learned · Timeline · Supporting information.

### Community health files

GitHub recognises these, and each may live in "root of the repository, the `.github`
folder, or the `docs` folder": `CODE_OF_CONDUCT.md` · `CONTRIBUTING.md` ·
`FUNDING.yml` · `GOVERNANCE.md` · `SECURITY.md` · `SUPPORT.md`. Issue and pull request
templates are the exception — they must sit in `.github/ISSUE_TEMPLATE`. GitHub states
plainly: "You cannot create a default license file."

**Contributor Covenant 3.0** is the code-of-conduct template, CC BY-SA 4.0, stewarded
by the Organization for Ethical Source. Sections: Our Pledge · Encouraged Behaviors ·
Restricted Behaviors · Other Restrictions · Reporting an Issue · Addressing and
Repairing Harm · Scope · Attribution. 3.0 is a structural rewrite of 2.1 — it replaces
the old "Enforcement Guidelines" with a four-rung **enforcement ladder** (Warning →
Temporarily Limited Activities → Temporary Suspension → Permanent Ban), each rung
carrying an Event / Consequence / **Repair** triple. Two `[NOTE: …]` placeholders must
be filled before adoption (reporting route, and whether to keep the suggested ladder).

### Structure and style, not templates

**Diátaxis** — four forms, no version, no date. Authored by Daniele Procida, credited on
the colophon ("Diátaxis is the work of Daniele Procida") though not on the landing page.
Quoted:

> "Diátaxis identifies four distinct needs, and four corresponding forms of
> documentation - _tutorials_, _how-to guides_, _technical reference_ and _explanation_."

> Tutorials: "A tutorial's purpose is to help the pupil acquire basic competence." ·
> How-to guides: "A how-to guide's purpose is to help the already-competent user
> perform a particular task correctly." · Reference: "Reference guides are **technical
> descriptions** of the machinery and how to operate it. Reference material is
> **information-oriented**." · Explanation: "Explanation is a discursive treatment of a
> subject, that permits reflection. Explanation is understanding-oriented."

Reference carries a boundary worth quoting because agent-written docs cross it
constantly: "Although reference should not attempt to show how to perform tasks, it can
and often needs to include a description of how something works or the correct way to use
it." Diátaxis names the pull directly — "It can be tempting to introduce instruction and
explanation" — and grounds the boundary in the reader: "When you're looking for
information - relevant facts - you do not want to be confronted by opinions, speculation,
instructions or interpretation."

Note the boundary is narrower than it is usually reported. Diátaxis does not forbid
describing how something works; it forbids *instructing*. Calling the violation a
"category error" is this note's framing, not the source's.

**The Good Docs Project** — 29 fillable templates across three packs, licensed
**Zero-Clause BSD** ("Permission to use, copy, modify, and/or distribute this software
for any purpose with or without fee is hereby granted"), so they can be copied into a
repo with no attribution burden. Core pack: Concept · How-to · README · Reference ·
Release notes · Troubleshooting · Tutorial. Community pack: Bug report · Changelog ·
Code of Conduct (+ incident record, remediation record, response plan) · Contributing
guide · Our team · README. Misc pack: API getting started · API reference · Contact
support · Glossary · Installation guide · Quickstart · SDK overview · Style guide ·
Terminology system · User personas.

**Google developer documentation style guide** (last updated 2025-04-02) for prose
rules: "Use second person: 'you' rather than 'we.'" · "Use sentence case for document
titles and section headings." · "Use numbered lists for sequences" · "Put code-related
text in code font." · "Put UI elements in bold." · "Put conditions before instructions,
not after." · "Use unambiguous date formatting."

**OpenAPI Specification 3.2.0**, 19 September 2025 — the template for HTTP API
reference, in the sense that the spec *is* the document.

---

## When to use it — and when not to

- **Do not reach for a template when the repo already has a contract.** For handbook
  pages, `read_contract()` is authoritative and this note is not. Templates below are
  inputs to a page's *structure*; the contract governs its *provenance*. Where they
  disagree, the contract wins.
- **Diátaxis is for splitting documents, not for structuring one.** Its value is telling
  you a page is trying to be two things. It gives you no headings.
- **arc42 is too heavy for a component.** Twelve sections on a single crate produces ten
  empty ones. Use it for a system, or lift only §5/§9.
- **KEP's Production Readiness Questionnaire is the wrong tool for a doc change.** It is
  built for a feature that ships to a cluster.
- **Do not present a PRD template as standard.** No standards body defines one (see
  below). If a PRD template is wanted, it is being *chosen*, and whoever chooses it owns
  the choice.
- **ISO templates cannot be quoted.** They are paywalled; citing a clause number you have
  not read is a fabricated citation with a very respectable-looking shape.

---

## How to start

Smallest useful default for a cohort project document, by kind:

| Need | Copy from | Why this one |
|---|---|---|
| Record a decision | MADR 4.0.0 `template/adr-template.md` | Versioned, dated, Markdown-native, has *Confirmation* |
| Repo front page | Standard Readme section order | Normative order; `License` last |
| Release history | Keep a Changelog 2.0.0 six types | Six types, closed set, human-first |
| Propose a change | Rust RFC template | Lightest of the proposal templates |
| Propose an operational change | KEP template | Only one that forces rollback + monitoring |
| Runbook | SRE Workbook playbook definition | Severity, impact, debugging, mitigation |
| Incident write-up | SRE Book Appendix D headings | Ten headings, already in wide use |
| Any prose page | Good Docs template (0BSD) + Google style guide | Fillable, no attribution burden |

---

## What surprised me

**The document types teams argue about have the weakest standards backing, and the ones
nobody argues about have crisp versioned specs.** Changelogs and commit messages —
nobody's idea of contested territory — have numbered, dated, pinnable specifications.
PRDs and design docs, which generate endless template debate, have none at all. The
argument is not about the format; it exists *because* there is no format to appeal to.

**Diátaxis has no version and no date.** The most-cited documentation framework in the
industry cannot be pinned in time. A claim of the form "per Diátaxis, as of 2026…" is not
supportable, because the site will not say when anything on it was written. Authorship is
not the gap — the colophon credits Daniele Procida; it is the absence of a version or date
that defeats citation.

**Reference documentation is defined by what it must not do.** Diátaxis says reference
"should not attempt to show how to perform tasks", while allowing that it "can and often
needs to include a description of how something works". The line is instruction, not
description. That is the exact failure mode of agent-written reference docs, which drift
into tutorial voice within a paragraph.

**"Industry standard" in practice means "widely adopted free template", not "standard".**
The genuine standards — ISO/IEC/IEEE 26514, 29148 — are paywalled and effectively absent
from practice. Every template actually used in the industry is a community artefact.

**KEP is the only mainstream proposal template that asks how the change gets turned
off.** Rollback, version skew, monitoring, and a graduation ladder are all mandatory
sections. Rust's RFC template, arc42, and every PRD template found ask none of them.

---

## Open questions

1. **The ISO/IEC/IEEE 26511/26512/26514/26515 titles and years above are unverified.**
   They come from a search-engine summary, not a page I read; `iso.org` returned HTTP
   403 to every fetch. *Method:* the ISO Online Browsing Platform publishes free
   tables of contents — open `iso.org/obp/ui` from a browser (agent fetches are
   blocked), or ask whether the cohort has institutional IEEE Xplore access. **Do not
   cite a clause number from these until someone has read the document.**
2. **ISO/IEC/IEEE 29148:2018's SRS outline is unread.** It is the nearest thing to a
   standard PRD, and I could not open it. *Method:* same as (1). Third-party "29148
   templates" found in search are reconstructions by vendors, not the standard, and must
   not be quoted as if they were.
3. **Contributor Covenant 3.0's release date (28 July 2025) is unverified** — from a
   search summary of the Ethical Source announcement, not the announcement itself.
   *Method:* fetch `ethicalsource.dev/blog/contributor-covenant-3/` directly.
4. ~~**RFC 8174's amendment to RFC 2119 is not covered here.**~~ **Closed 2026-08-26** —
   read and folded into the BCP 14 entry above.
5. **Whether the Professor should own template selection at all is undecided, and this
   note cannot settle it.** It is a question about the handbook's page contract, not
   about what templates exist. *Method:* `read_contract()`, then ask whether page
   structure is contract-governed or author's choice. **This is not answerable by more
   research** — it is a decision for whoever owns the contract.
6. **Whether any of these templates conflict with the handbook's provenance rules is
   untested.** *Method:* draft one page against a chosen template and run
   `check_page()`; a real `findings` entry is the only proof either way.

---

## Sources

- Michael Nygard, "Documenting Architecture Decisions" — https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions — 15 November 2011
- MADR — https://adr.github.io/madr/ and https://raw.githubusercontent.com/adr/madr/main/template/adr-template.md — v4.0.0, 17 September 2024
- Standard Readme spec — https://github.com/RichardLitt/standard-readme/blob/main/spec.md — undated, no version
- Keep a Changelog — https://keepachangelog.com/en/2.0.0/ — v2.0.0, published 7 June 2026 (supersedes the still-live https://keepachangelog.com/en/1.1.0/)
- Keep a Changelog release history — https://raw.githubusercontent.com/olivierlacan/keep-a-changelog/main/CHANGELOG.md — `[2.0.0] - 2026-06-07`, `[1.1.2] - 2024-09-27`, `[1.1.1] - 2023-03-05`, `[1.1.0] - 2019-02-15`
- Semantic Versioning — https://semver.org/spec/v2.0.0.html — v2.0.0, undated
- Conventional Commits — https://www.conventionalcommits.org/en/v1.0.0/ — v1.0.0, undated
- Rust RFC template — https://raw.githubusercontent.com/rust-lang/rfcs/master/0000-template.md — undated
- Kubernetes KEP template — https://raw.githubusercontent.com/kubernetes/enhancements/master/keps/NNNN-kep-template/README.md — undated
- RFC 2119 / BCP 14, Scott Bradner — https://www.rfc-editor.org/rfc/rfc2119.txt — March 1997
- RFC 8174 / BCP 14, Barry Leiba — https://www.rfc-editor.org/rfc/rfc8174.txt — May 2017
- arc42 — https://arc42.org/overview — CC BY-SA 4.0, © 2003–2026, no version stated
- C4 model, Simon Brown — https://c4model.com/ — undated
- Google, *Site Reliability Engineering* Appendix D — https://sre.google/sre-book/example-postmortem/ — 2017, CC BY-NC-ND 4.0
- Google, *The Site Reliability Workbook*, "Being On-Call" — https://sre.google/workbook/on-call/ — 2018
- GitHub, community health files — https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file — undated
- Contributor Covenant 3.0 — https://www.contributor-covenant.org/version/3/0/code_of_conduct/ — v3.0, CC BY-SA 4.0, release date unverified
- Diátaxis — https://diataxis.fr/ , /tutorials-how-to/ , /reference/ , /explanation/ , /colophon/ — undated, no version; authored by Daniele Procida, credited on /colophon/ but not on the landing page
- The Good Docs Project templates — https://www.thegooddocsproject.dev/template and https://raw.githubusercontent.com/thegooddocsproject/templates/main/LICENSE.txt — 29 templates, Zero-Clause BSD, no version stated
- Google developer documentation style guide — https://developers.google.com/style/highlights — last updated 2025-04-02
- OpenAPI Specification — https://spec.openapis.org/oas/latest.html — v3.2.0, 19 September 2025

---

## Checked — 2026-08-26

Checked in the same session that wrote the note, so this is not independent review — it
is a record of what mechanical verification found. The human block below is still open.

- **All 24 cited URLs resolve.** `curl -o /dev/null -w '%{http_code}' -L` over every
  http link in this file: 24/24 returned `200`. No dead citations.
- **MADR 4.0.0 / 17 September 2024 — confirmed.** `gh release list --repo adr/madr`
  returns `4.0.0  Latest  4.0.0  2024-09-17T11:00:08Z`. Read off a release tag, which is
  a different method than the rendered page the claim came from.
- **Keep a Changelog "latest release 1.1.2, 27 September 2024" — WRONG.** See Corrections.
- **RFC 8174 read** and folded into the BCP 14 entry; open question 4 closed.

## Corrections — what this note got wrong

**One claim was false, and it was one of the three the note had already flagged as most
likely to be wrong.**

**Keep a Changelog: the note said 1.1.0 was the current spec page and 1.1.2 the latest
release. Both are superseded — 2.0.0 was published 7 June 2026.** The error came from
fetching `keepachangelog.com/en/1.1.0/` by direct URL and reading the version off *that
page*, which of course reports 1.1.0. The page is versioned; the URL was chosen from
memory; and a versioned URL will always confirm the version you asked for. It looked like
a sourced claim because it *was* quoted from a live primary page — the page was simply the
wrong one.

Two mechanical checks caught it, neither of which was reading a page:
`gh release list --repo olivierlacan/keep-a-changelog` reported latest `v1.1.1
(2023-03-06)` — which contradicted the "1.1.2, 2024-09-27" claim without yet revealing
2.0.0, because no GitHub release was cut for either. The project's own `CHANGELOG.md`
then showed `## [2.0.0] - 2026-06-07` at the top.

**Two lessons worth keeping.** First: *never fetch a versioned documentation URL by
typing the version from memory* — fetch the unversioned or `/latest/` entry point and let
the site tell you what current is. Second: *a repository's `CHANGELOG.md` and its GitHub
releases can disagree*, and here the releases were the more stale of the two. Two sources,
neither authoritative alone.

**What was merely incomplete, not false:** RFC 2119 was quoted correctly but without
RFC 8174, which is what makes lowercase "should" non-normative — a real gap for anyone
using this note to write requirement language, now filled.

**A second false claim, caught in review: Diátaxis was said to have "no named author on
the site".** It has one — `diataxis.fr/colophon/` states "Diátaxis is the work of Daniele
Procida." The claim was built from the landing page and the three form pages, none of
which name him, and the absence was reported as a property of the site rather than of the
pages actually read. Same shape as the Keep a Changelog error: a fact read off a subset of
pages and generalised to the whole source. The pinnability argument survives intact,
because what defeats citation here is the missing version and date, not the authorship.

**And one quotation was a paraphrase wearing quotation marks.** The note had reference
documentation "should explicitly avoid instruction and explanation" — that string appears
nowhere on the page. The source says "Although reference should not attempt to show how to
perform tasks, it can and often needs to include a description of how something works",
and separately that "It can be tempting to introduce instruction and explanation". The
invented wording was also *stronger* than the source: Diátaxis draws its line at
instructing, not at describing how something works. In a note about which templates you
can actually cite, a fabricated quotation is the worst available error.

---

## Check these first

*For a human. Item 1's Keep a Changelog half is already closed — see Corrections.*

1. **"MADR 4.0.0, released 17 September 2024".** Version-plus-date pairs are the single
   most common thing a note like this gets wrong. Confirmed above against the release
   tag, but by the same session that wrote it. *Method:*
   `gh release list --repo adr/madr --limit 3`.
2. **The Standard Readme required/optional split, and specifically "License … Must be
   last section".** This note states section order as normative; if the spec has since
   relaxed it, every README generated from this row inherits a false constraint.
   *Method:* open https://github.com/RichardLitt/standard-readme/blob/main/spec.md and
   read the Sections table directly — the spec is short.
3. **"No standards body defines a PRD."** This is a claim from absence of evidence, which
   is exactly the shape of claim that turns out wrong. It rests on one web search plus a
   403 from ISO. *Method:* search the IEEE Standards catalogue
   (`standards.ieee.org`) for "product requirements" directly, rather than searching the
   open web about it. If something turns up, tier 4 above collapses into tier 3.
