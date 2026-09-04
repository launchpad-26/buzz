# RQA methodology

How [`requirements-specification.md`](requirements-specification.md) is structured, and the conventions every
requirement in it follows.

**This document is structured by the shape of a Requirements Specification as outlined in
ISO/IEC/IEEE 29148:2018 — a scope, a set of individually identified requirements each carrying an EARS-patterned
statement, a priority, a status, a source and a fit criterion, plus set-level and individual-level quality
characteristics — and does not claim conformance to that standard.** The standard's full text was not read (it is
paywalled and outside this task's clean-room inputs); only the shape used by
[`launchpad/REQUIREMENTS.md`](../../../REQUIREMENTS.md), which makes the identical declining-of-conformance
statement, was available. Saying "structured by" is the whole of the claim, exactly as REQUIREMENTS.md's own
methodology section states it for the same reason.

**Which characteristics were applied, and how they were obtained.** Two characteristic sets are applied below:

- **Nine individual characteristics** — necessary, appropriate, unambiguous, complete, singular, feasible,
  verifiable, correct, conforming — assessed per requirement in
  [`requirements-quality-assessment.md`](requirements-quality-assessment.md). These nine are the individual
  requirement-characteristics named by #2069's own definition of done, not an independently chosen subset; they
  were obtained by re-reading each requirement statement against its own clause and fit criterion, not by applying
  an external checklist not provided as a clean-room input.
- **Five set characteristics** — complete, consistent, feasible, comprehensible, validatable — assessed once for
  the whole set in [set-assessment.md](set-assessment.md) below, obtained the same way: by re-reading the set as a whole against
  the extract and against itself.

Both lists were supplied by #2069's definition of done itself, quoted there without a citation to 29148, so no
claim is made that they are 29148's own vocabulary for these characteristics — only that they are the
characteristics #2069 asked this specification to apply.

**EARS pattern legend.** Every requirement is labelled with exactly one of five patterns. The label is a semantic
classification against the test below, not a claim about the sentence's grammar — apply the tests in order and
stop at the first one that fits.

| # | Pattern | Test | Example |
|---|---|---|---|
| 1 | **Optional-feature** | The obligation's entire content depends on an operator-chosen configuration or capability being *present* — there is nothing to obligate in its absence. A standing "shall be able to…" capacity is **not** Optional-feature just because its text names a scenario; the capacity itself must hold regardless, so that stays Ubiquitous (rule 5). | "Where a fallback is explicitly configured, the review shall continue through that fallback…" (RQA-FR-023) — with no fallback configured, there is nothing to continue through. |
| 2 | **State-driven** | The obligation is conditioned on a **condition that holds**: a sticky configuration fact, or a per-instance status, signalled by "while"/"where"/"for a given X"/"when X is/remains Y", a condition-bearing noun phrase as the subject (e.g. "a finding classified as mechanical **and permitted by policy**"), or a biconditional obligating both branches. A condition-class subject wins this test even where the subject is a record — "a malformed or unreadable policy" is the policy's own held state, not a one-off artifact. | "While no fallback is configured for a reviewer, model or provider, the review shall invent no fallback…" (RQA-FR-024). |
| 3 | **Event-driven** | The obligation activates on a discrete **occurrence** — the subject denotes something *happening* — **and the mandated response is a positive action**. A subject that denotes a **produced or supplied artifact** (a finding, an approval, an escalation, a pull request) is not a trigger merely because its arrival could be called an event; if the row states a condition-free universal rule over that artifact class, it is Ubiquitous (rule 5) instead. | "When a pull request's only failing check also fails on its merge base, the review shall classify that failure as inherited…" (RQA-FR-014). |
| 4 | **Unwanted-behaviour** | The residual prohibition class: everything phrased "shall not"/"shall never"/"no…shall"/"shall have no…" that rules 1–3 do not already claim — an unconditional prohibition, or a discrete event whose mandated response is itself a prohibition. | "The system shall hold no deploy-key, relay or VPS credential…" (RQA-NFR-025). |
| 5 | **Ubiquitous** | Reached only once rules 1–4 are checked and none applies: the obligation holds continuously, with no precondition and no prohibition. This includes a standing "shall be able to…"/"shall be configurable" capacity, and a condition-free universal rule over an existing artifact class — "every finding shall carry…", "a human approval… shall name…". A subject that names a **produced record or outcome object**, stating a standing property every instance of that class carries independent of any further condition, is Ubiquitous even where part of the record (a category, a classification) is fixed once assigned. | "Every finding shall carry a category distinguishing mechanical, procedural and creation-time findings from correctness, security, architectural and evidence findings." (RQA-FR-008). |

**Precedence order:** 1 (Optional-feature) → 2 (State-driven) → 3 (Event-driven) → 4 (Unwanted-behaviour) →
5 (Ubiquitous, the true default). The earliest-listed test that applies wins.

**Status-marker legend.** Every requirement below carries exactly one status marker, read exactly as defined in
[`VISION.md` § How to read this](../../../VISION.md#how-to-read-this): `IMPLEMENTED` (true today, evidenced by a
link to the file or commit), `DECIDED` (agreed, not built, evidenced by a link to the accepted decision or the
issue that agreed it), `PROPOSED` (not yet agreed), `OPEN` (undecided, evidenced by a link to the ADR issue). This
document does not restate that legend; it links to it, matching `launchpad/REQUIREMENTS.md`'s own convention.

**Why every requirement below is `DECIDED`, and none is `OPEN` or `IMPLEMENTED`.** `VISION.md`'s `OPEN` means *the
obligation itself* is undecided, evidenced by an ADR issue that owns *whether* the obligation holds — not that
some detail of *how* an agreed obligation is met remains open, and not a publication-placement question either.
Every requirement in this specification traces to a clause #2006 already agrees to
([clause-inventory.md](clause-inventory.md) records the disposition for each). The first derivation surfaced
three narrower questions as draft ADRs (`ADR-A`, `ADR-B`, `ADR-C`) without any of them changing a requirement's
own standing; the 2026-09-04 amendment then resolved all three at the source (see round 9 in
[revision-history.md](revision-history.md)), so none was ever filed as a GitHub issue and no requirement below
carries an ADR pointer. #2064 still owns where this specification itself is published — a placement question,
not a requirement's standing — and RQA-FR-001/RQA-NFR-002/RQA-NFR-003 are unaffected by how that resolves. Every
requirement below is therefore `DECIDED`. This specification was authored with no implementation knowledge of
RQA — the clean-room constraint under which it was written forbids reading anything about RQA's current code,
evidence or impacted components beyond the single authorised re-fetch of #2006's own body — so `IMPLEMENTED`
(which requires "a link to the file or commit") is never available as evidence, and no row uses it.

**MoSCoW priority.** Every requirement carries a MoSCoW priority, following `REQUIREMENTS.md`'s convention. Because
#2006 states P1–P12 and C1–C9 as "the twelve problems this PRD exists to solve" (CL-064) and "the nine design
constraints the solution must hold" (CL-065), and states every AC as baseline acceptance criteria, every
requirement below defaults to `Must`. It is downgraded only where the extract's own text uses permissive language
("may") for the specific capability in question, never on this document's own judgement of importance — see
RQA-NFR-002 and RQA-NFR-012. RQA-NFR-003 is `Must`, with "where practical" carried inside the statement itself (as
C2 states it) and given an evidential fit criterion ([RQA-NFR-003](requirements-specification.md#rqa-nfr-003)) rather than priced away as a
`Should`. RQA-NFR-002 (Could) and RQA-FR-030 (Must) both describe the same non-built-in integration path but carry
different priorities deliberately: NFR-002's Could prices the *contributor's* option to use a thin skill/plugin/
hook (C1's own "may"), while FR-030's Must prices the *system's* obligation to admit that contributor once they
exercise the option (AC15 states this as a hard acceptance criterion with no softening language) — the two rows
are not in tension; they price different actors' obligations for the same path (see each row's Appropriate
judgement in requirements-quality-assessment.md). RQA-NFR-012's split ([singular-splits.md](singular-splits.md)) illustrates the
same discipline in the other direction: the *permission* to send content to a configured external provider stays
Could (C9's own "may"), but the *prohibition* on sending anything to an unconfigured one (RQA-NFR-027 — round 3:
re-derived from C7/CL-024, reconciled with RQA-NFR-009, see [singular-splits.md](singular-splits.md)'s CL-024 entry) is priced
Must, because the security guarantee RQA-NFR-023/RQA-NFR-029 presuppose must not be deferrable merely because the
permission it gates is optional.

**On naming GitHub and other source vocabulary.** No requirement below invents an implementation choice beyond
the source's own terminology; the rule is **"no mechanism, component, product or technology is named beyond what
the source clause itself names."** The deliberate GitHub exception is used in exactly five requirement statements,
each because its cited source clause is itself GitHub- or GitHub-review-state-scoped: RQA-NFR-007 and RQA-FR-028
(`APPROVED`/`CHANGES_REQUESTED`, the vocabulary C6 and AC14 themselves use), RQA-NFR-011 (C8's own "GitHub scope",
stated in C8's own scope-release terms rather than a prohibition — see this row's entry below), RQA-FR-031
(AC16's own "different GitHub owners or organisations"), and RQA-FR-035 (`#109`/`#535`/`#536`, the issue numbers
CL-046's closing criterion itself names). Beyond GitHub, several requirements carry other vocabulary the source
itself supplies rather than a mechanism this specification chose: "skill, plugin or hook" (RQA-NFR-002, C1's own
term), "working tree" and "force-push" / "branch protection" / "protected branch" (RQA-NFR-020/RQA-NFR-021,
CL-057's own enumeration), "a single command"/"one command" (RQA-FR-012/RQA-FR-016, AC06's/AC08's own interface
vocabulary), "architectural component" (RQA-FR-034, the closing criterion's own term for what is being justified),
and "pull-request write"/"repository-content read" (RQA-NFR-024/RQA-NFR-030) and "deploy-key"/"relay"/"VPS" (RQA-NFR-025) — the Security implications section's own credential-scope enumeration, carried in lightly normalised form rather than verbatim: CL-060 itself says "pull-requests write and contents read", and these three rows use the platform-neutral singular/expanded phrasing this specification uses throughout ("repository-content read" rather than GitHub's own "contents read"), not GitHub's own literal string. Fit criteria previously invented a
representation their cited clause never names, rather than testing the clause's own vocabulary: RQA-FR-001's
"single published protocol *document*" is "protocol *definition*" (AC01's own word, not a packaging format);
RQA-NFR-018's "policy *file*" is "policy *input*" (CL-056 says only "malformed or unreadable policy", not a file
specifically); RQA-FR-030's "no *commit*…required" is "source unchanged…regardless of whether a commit was made
and later reverted" (a commit is a Git-specific proxy CL-042/AC15 does not name); RQA-FR-021's fit criterion no
longer prescribes a "measured" label or any other particular representation for an actual resource-consumption
reading (round 3). RQA-NFR-004's fit criterion names "organisation" without qualifying it as a GitHub
organisation, even though C3/CL-020 — its own source clause — is platform-neutral and never mentions GitHub; the
criterion is correct only because C8/RQA-NFR-011 have already scoped the whole specification to GitHub elsewhere,
and this row's own entry records that reliance rather than re-deriving GitHub scoping from CL-020 itself. Each use
is recorded in that row's Conforming judgement in requirements-quality-assessment.md; none of them invents a
mechanism the source clause does not already name.
