---
description: Research into reviewing security and disclosure quality in Buzz's public technical documentation.
tags: [documentation, security, disclosure, vulnerability, secrets, evidence, review, research]
---

# Security and disclosure quality in public technical documentation

Researched 2026-09-08. This is research, not an adopted corpus standard, a security
assessment, a vulnerability disclosure, legal advice, or a statement that a named Buzz
control is effective.

## Research question

How should Buzz review public technical documentation so that it communicates security
architecture, trust assumptions, secure operation, and vulnerability response accurately
enough for legitimate users while preventing disclosure of credentials, private
operational identifiers, live defensive gaps, personal data, or uncoordinated
vulnerability information?

The investigation considered twelve subquestions:

1. Which security information belongs in public documentation, and which belongs in a
   restricted record or coordinated-release process?
2. How should a reviewer distinguish a secret, sensitive operational information,
   security-relevant public information, personal data, and embargoed vulnerability
   information?
3. When does architectural transparency improve security, and when does detail become an
   avoidable operational gap map?
4. What evidence is required for claims about authentication, authorization,
   cryptography, auditability, transport protection, isolation, defaults, and compliance?
5. How should examples, placeholders, commands, logs, screenshots, and configuration
   avoid exposing or accidentally targeting real resources?
6. What must a public vulnerability-reporting policy communicate, and what can a
   `security.txt` file add?
7. How should vulnerability handling, coordinated disclosure, and public advisories be
   separated?
8. What should a documentation reviewer do when review itself reveals a secret or a
   previously undisclosed vulnerability?
9. How should redaction preserve useful and auditable meaning without retaining the
   sensitive material?
10. How should public and private evidence remain connected without revealing restricted
    locations or content?
11. How should ownership and freshness work when an operational fork and an upstream
    product have different reporting authorities?
12. Which checks can be automated, which require security judgment, and which measures
    avoid false assurance?

## Bottom line

Security documentation is part of the security control surface. A false authorization
claim, an unsafe copied command, a stale reporting address, or an exposed credential can
harm users even when the software is unchanged. Review therefore has two simultaneous
duties: make safe security knowledge usable, and stop restricted knowledge from crossing
the publication boundary.

The strongest model for Buzz is:

> **Classify before publishing → verify security claims at the right system layer → expose
> safe models, assumptions, limitations, and actions → route secrets and uncoordinated
> vulnerability details privately → coordinate remediation and disclosure → keep public
> routes and claims owned, tested, and current.**

Twelve conclusions should govern the later checklist:

1. **Public security documentation and secret material are not opposites on one scale.**
   Security models, trust boundaries, supported versions, secure configuration,
   limitations, and reporting instructions are normally useful to publish. Credentials,
   private hostnames, personal data, live control status, access paths, and unpatched
   exploit detail are different information classes with different owners and routes.
2. **Do not use “security by obscurity” to excuse missing design documentation.** Sound
   security should not depend on concealing the design. That principle does not require
   publishing current topology, reachable internal assets, control gaps, or an exploit
   chain. Publish the stable model at the altitude readers need; keep live defensive
   state and embargoed findings restricted.
3. **A security claim needs stronger evidence than ordinary descriptive prose.** Verify
   the implementation, configuration, relevant tests, and operational boundary. State
   whether the text describes design intent, repository implementation, deployment
   expectation, or observed runtime state. “All,” “only,” “never,” “tamper-proof,” and
   compliance-like claims require particular challenge.
4. **A disclosure policy, vulnerability-handling process, advisory, threat model, security
   posture, and incident runbook are different artifacts.** Combining them creates
   unclear audiences, disclosure boundaries, and authorities.
5. **The public reporting route must be easy to find, usable, scoped, and maintained.** It
   should say where to report privately, what information helps, what behavior is
   authorized or prohibited, how reporter data is treated, which products or versions are
   covered, and what response can realistically be expected. A promise is a control claim
   and must be monitored.
6. **`security.txt` is a discovery pointer, not a vulnerability programme or permission
   grant.** RFC 9116 requires a current contact and expiry semantics and explicitly warns
   that the file can become stale or compromised. Authorization and scope belong in the
   linked policy.
7. **Coordinated vulnerability disclosure is a process, not a fixed waiting period.** The
   parties repeatedly decide what action is needed and who needs which information when.
   Publication should help affected users understand exposure and act, normally with a
   fix or mitigation available, while recognizing that timing changes with exploitation,
   multi-vendor dependencies, leaks, and remediation feasibility.
8. **A reviewer who discovers a possible live secret or undisclosed vulnerability must
   stop the public workflow.** Do not paste the material into this report, a public issue,
   a pull request, or a public checklist result. Use the authorized private route and
   preserve only a non-sensitive public marker if one is needed.
9. **Removing a secret from the latest file is not remediation.** Treat it as compromised,
   revoke or rotate it, identify affected services and possible use, then decide with the
   appropriate owners whether disruptive history cleanup is warranted. Scanning helps
   prevention and detection but cannot prove that no secret exists.
10. **Examples must be both non-secret and non-operational.** Use conspicuous placeholders,
    reserved example domains and addresses, minimum privileges, and safe defaults. Mark
    development-only shortcuts. Review copy-and-paste effects, not just whether a literal
    looks fake.
11. **Redaction should remove the minimum sensitive element while retaining category,
    consequence, decision, and provenance.** Review URLs, citations, filenames, diffs,
    histories, logs, screenshots, and metadata as well as prose. Redaction must not hide
    uncertainty or make an unsupported control appear effective.
12. **Automation supplies guardrails, not a security verdict.** Whole-corpus scans can find
    known credential patterns, prohibited citation shapes, unsafe example identifiers,
    and stale links. Humans must decide semantic sensitivity, exploitability, accuracy,
    disclosure timing, and whether the public detail is necessary.

Buzz already has unusually explicit public-repository rules, separate private advisory
routes, a public security posture that deliberately avoids a live control-by-control gap
map, corpus evidence ledgers, and a validator that refuses some credential-shaped citation
paths without echoing them. It does not yet have a corpus-wide semantic security review,
a complete classification scheme, a documented safe redaction pattern, or proof that the
current reporting promises and every security claim are routinely revalidated. Those are
research observations, not vulnerability findings.

## Scope and method

This report covers security-relevant content in public technical documentation:
architecture and trust boundaries, secure configuration, credentials, examples,
operational claims, vulnerability reporting, disclosure, advisories, evidence, redaction,
review escalation, ownership, and freshness.

It does not:

- test Buzz for vulnerabilities or publish any vulnerability detail;
- inspect the cohort's private infrastructure repository or infer its contents;
- validate a credential, hostname, account, control, or production deployment;
- decide legal authorization, safe-harbor language, embargo timing, severity, or
  regulatory obligations for the project;
- certify conformance with ISO, NIST, RFC, OWASP, GitHub, or another framework;
- establish that root `SECURITY.md` promises are or are not being met;
- prescribe a `security.txt` file or a new repository security tool;
- approve publication of any current open security issue or posture detail; or
- introduce LLM-specific controls, which remain set aside for this research sequence.

Local inspection used repository revision
`eb1cedb19d02e61426bc5e75b7a43cc485c8a133`. It examined root
[`SECURITY.md`](../../../SECURITY.md), the fork's
[`SECURITY-POSTURE.md`](../../SECURITY-POSTURE.md),
[`AGENTS.md` security rules](../../AGENTS.md#8-security), the
[`issue chooser`](../../../.github/ISSUE_TEMPLATE/config.yml), the
[`agent PR template`](../../AGENT_PR_TEMPLATE.md), the corpus
[`threat-model template`](../../docs/corpus/templates/threat-model.md), selected security
architecture and configuration nodes, and the corpus validator. Search counts were used
only to locate likely review surfaces; lexical matches are not findings or a complete
security inventory.

External sources were selected in this order:

1. ISO/IEC 29147:2018 for vulnerability-report receipt and disclosure, and ISO/IEC
   30111:2019 for handling and remediation;
2. RFC 9116 for the precise scope, format, freshness, and security limits of
   `security.txt`;
3. CERT/CC's current Guide to Coordinated Vulnerability Disclosure for process and timing
   trade-offs;
4. NIST SP 800-216 and SP 800-218 for formal reporting/handling and secure-development
   response practices;
5. NIST SP 800-160 Volume 1 Revision 1 for evidence-based security engineering and the
   role of precise, verifiable security specifications;
6. GitHub's current documentation for private advisories, fix-version information, secret
   prevention, rotation, and history-cleanup limits;
7. OWASP's Secrets Management Cheat Sheet for secret lifecycle, least privilege,
   logging, rotation, and documentation; and
8. IETF reserved-domain and reserved-address RFCs for safe technical examples.

ISO's public pages expose abstracts rather than the full paid standards, so this report
does not attribute unseen clauses. NIST SP 800-216 is written for US federal bodies;
GitHub guidance describes one platform; RFC 9116 defines a discovery file rather than an
entire programme; OWASP and CERT/CC are expert guidance rather than project policy. Their
shared principles inform review, but Buzz's named owners must decide local adoption.

## The information-classification decision comes first

A reviewer cannot decide “is this safe to publish?” merely from whether a sentence sounds
technical. The same fact can change class with time, combination, precision, and system
state. A generic trust boundary may be essential public architecture; the current address,
unpatched weakness, and monitoring gap at that boundary may form an actionable attack
map.

The following is a candidate routing model, not an adopted classification policy:

| Class | Examples | Default route | Review question |
|---|---|---|---|
| Public security knowledge | Security model, trust assumptions, supported versions, stable architecture, secure defaults, user mitigations, known limitations safe to disclose | Public documentation | Does the detail help a legitimate reader make a security decision, and is it accurate and current? |
| Public but context-sensitive | Protocol details, dependency versions, port roles, topology abstractions, control limitations, historical incident lessons | Public only after necessity, aggregation, freshness, and adversarial review | Does precision create avoidable operational advantage, privacy harm, or a misleading snapshot? |
| Restricted operational information | Private hostnames and addresses, identities, live topology, current control status, access paths, sensitive logs, private repository coordinates where naming them adds risk | Authorized private system | Can the public text retain the model, decision, and consequence without the live detail? |
| Secret or credential material | Passwords, tokens, private keys, session secrets, signing material, usable connection strings | Secret manager and incident route; never documentation | Has it crossed a public boundary, and if so has it been treated as compromised and revoked or rotated? |
| Personal or confidential data | User content, member rosters, personal identifiers, reporter identity or report attachments | Privacy-appropriate restricted route | Is collection and publication necessary, authorized, minimized, and properly retained? |
| Embargoed vulnerability information | Unpatched flaw, reproducer, exploit chain, affected live target, bypass detail, private report discussion | Private advisory or authorized coordination workspace | Who needs what information now, and what fix, mitigation, or disclosure condition changes the route? |
| Coordinated public advisory | Affected products and versions, impact, severity rationale, fixed version, mitigation, upgrade action, credit and references safe to release | Published advisory and release communication | Can an affected user identify exposure and take a safe action without relying on hidden context? |

Classification must be revisited at publication. “Already public somewhere” is not a
sufficient reason to repeat or aggregate a fact: searchability, authority, context, and
the combination of individually harmless facts can materially change risk. Conversely,
calling every security detail sensitive deprives operators of the information required to
deploy safely and hides assumptions from contributors who could challenge them.

## Publish the security model, not a live defensive dashboard

[NIST SP 800-160 Volume 1 Revision 1](https://csrc.nist.gov/pubs/sp/800/160/v1/r1/final)
frames security engineering as reasoning about trustworthiness using relevant and credible
evidence. The [NIST glossary entry for specification](https://csrc.nist.gov/glossary/term/security_specification)
includes definitions emphasizing completeness, precision, verifiability, and procedures
for determining whether provisions are satisfied. Together they support documenting
architecture, protection needs, interfaces, assumptions, and verification criteria. They
do not imply that all supporting evidence belongs in a public repository.

For a public architecture or posture document, useful content normally includes:

- assets and protection objectives at an appropriate level;
- actors, identities, roles, and trust assumptions;
- trust boundaries and important data flows;
- authentication and authorization decisions;
- security-relevant dependencies and delegated responsibilities;
- secure defaults and deployment prerequisites;
- important limitations and accepted risks safe to disclose;
- what is enforced by code, by configuration, by platform, or only by human process;
- failure behavior and recovery responsibilities; and
- evidence type, owner, and review trigger.

Detail normally requires private treatment or deliberate reduction when it identifies a
current target or control state: exact private coordinates, current credentials, member
identities, access procedures, live firewall or monitoring gaps, sensitive incident
evidence, or an unpatched bypass.

The reconciliation is **stable abstraction plus explicit boundary**. A public document
can say that TLS must terminate at an ingress boundary and name who owns that obligation
without publishing the live ingress address or a current gap. It can describe the classes
of secrets, the injection path, fallback behavior, and rotation responsibility without
including a value. It can explain a threat and mitigation category without publishing an
unremediated reproducer.

## Evidence rules for security claims

Security prose often compresses several distinct propositions. For example, “private
channels are invisible to non-members” could mean design intent, relay query behavior,
desktop presentation, all supported endpoints, a tested version, or every deployed
instance. Review must expand the claim before judging it.

For every material security claim, record:

1. **Object:** component, endpoint, workflow, data, identity, deployment, or version.
2. **Property:** confidentiality, integrity, availability, authenticity, authorization,
   auditability, isolation, secure failure, or another defined property.
3. **Threat and boundary:** against whom, under which capabilities, and where the claim
   stops.
4. **Layer:** intended design, implemented code, default configuration, deployment
   requirement, or observed runtime state.
5. **Conditions and exceptions:** feature flags, fallbacks, supported platforms, proxy
   assumptions, membership state, key custody, failure modes, and time.
6. **Evidence:** source, tests, configuration, independent analysis, runtime observation,
   or an explicitly attributed decision.
7. **Freshness:** revision, version, environment, observation date, owner, and trigger for
   recheck.
8. **Reader action:** what the reader should configure, avoid, verify, upgrade, or report.

Claims deserving adversarial review include:

- universal or exclusive words such as “all,” “every,” “only,” “cannot,” and “never”;
- claims that an unauthenticated or unauthorized actor sees nothing;
- cryptographic properties and the threats they do or do not resist;
- deletion, migration, fallback, keyring, and environment-precedence behavior;
- TLS, encryption-at-rest, sandbox, isolation, SSRF, timeout, and validation claims;
- dependency-scanning or “no unsafe code” claims that imply more than a named check;
- compliance, audit, eDiscovery, certification, or regulatory suitability language; and
- present-tense operational statements about a deployment outside the repository.

Evidence should match the layer. Code inspection may establish an implemented branch but
not the current production configuration. A configuration template may establish a
supported setting but not that it is deployed. One happy-path test cannot establish an
exclusive negative claim across every read path. A decision proves intent or accepted
risk, not implementation. A scanner result proves what that scanner, pattern set, and
revision examined, not absence of vulnerabilities or secrets.

This extends the findings in
[`03-truth-and-evidence-in-living-technical-documentation.md`](03-truth-and-evidence-in-living-technical-documentation.md)
and
[`09-normative-versus-descriptive-technical-writing.md`](09-normative-versus-descriptive-technical-writing.md):
security review must preserve source authority and modality while also stating the threat
model and publication boundary.

## Keep security artifact types distinct

| Artifact | Primary question | Audience | Disclosure boundary |
|---|---|---|---|
| Security architecture or model | What is protected, from what, by which boundaries and mechanisms? | Designers, maintainers, operators, assessors | Stable public model; restrict live target detail |
| Threat model | What can go wrong, what assumptions apply, and how is each threat treated? | Designers and security reviewers | Public when safe; embargo active findings and sensitive evidence |
| Secure configuration guide | What must an operator configure and verify? | Operators | Public procedure with placeholders; no values or private coordinates |
| Security posture | Which risks and security responsibilities currently matter? | Decision-makers and operators | Public accepted risks and boundaries where safe; detailed live control state privately |
| Vulnerability disclosure policy | How may a finder report, and what should both parties expect? | Researchers and users | Public and highly discoverable |
| Vulnerability-handling process | How does the project intake, validate, prioritize, remediate, coordinate, and learn? | Maintainers, security team, coordinators | Usually restricted workflow, with a public summary if useful |
| Security advisory | Who is affected and what should they do about one disclosed vulnerability? | Users and downstreams | Public after coordinated release decision |
| Incident or secret-leak runbook | How do authorized responders contain, investigate, recover, and communicate? | Responders | Restricted when it contains access paths or sensitive evidence |
| Postmortem | What happened, why, impact, response, and learning? | Contributors and stakeholders | Public only after privacy, secret, vulnerability, and operational review |

Buzz's corpus
[`threat-model template`](../../docs/corpus/templates/threat-model.md) already makes
several of these distinctions explicitly. That is a strong foundation. Review should
still verify that an instantiated threat model does not become a repository of active
unpatched findings and that `Mitigated` or `Not Applicable` has evidence proportional to
the consequence.

## Safe examples, commands, configuration, logs, and images

Examples are executable guidance even when labelled illustrative.
[RFC 2606](https://www.rfc-editor.org/rfc/rfc2606.html) reserves `.example` and the names
`example.com`, `example.net`, and `example.org` for documentation;
[RFC 5737](https://www.rfc-editor.org/rfc/rfc5737.html) reserves `192.0.2.0/24`,
`198.51.100.0/24`, and `203.0.113.0/24` for IPv4 examples. These are safer than
invented-looking resources that may belong to someone.

A security review of an example should ask:

- Are credentials represented by unmistakable placeholders rather than plausible values?
- Could a shell expand or persist the placeholder in an unsafe way?
- Are example domains and IP addresses reserved for documentation, or deliberately local
  where local behavior is the lesson?
- Does the command use minimum permissions and a non-production target by default?
- Are destructive, internet-facing, debug, plaintext, bypass, and development-only modes
  identified before the command?
- Does copying the example expose a secret through shell history, process arguments,
  environment dumps, logs, screenshots, or generated files?
- Are cleanup, rotation, rollback, and verification given where the example creates
  security-relevant state?
- Does a sample log contain tokens, headers, user data, internal URLs, hostnames, IDs, or
  reporter details?
- Does a screenshot retain browser chrome, accounts, bookmarks, notifications, file
  paths, metadata, or terminal history?
- Are placeholder and redaction conventions consistent enough that a reader can tell
  what must be replaced and what must remain literal?

The [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
stresses least privilege, revocability, rotation, restricted visibility, and preventing
plaintext secrets from entering logs. It also notes that documentation of a
secret-management process should identify access, rotation dependencies, incident
contacts, exposure impact, and risk-dependent handling. Those are legitimate
documentation subjects; the values themselves are not.

## Public vulnerability reporting surface

[ISO/IEC 29147:2018](https://www.iso.org/standard/72311.html) describes receiving
potential vulnerability reports and disclosing remediation information so users can
manage risk. [ISO/IEC 30111:2019](https://www.iso.org/standard/69725.html) covers
processing and remediating reported vulnerabilities. Together they show why a public
policy cannot substitute for an internal handling capability.

A public reporting policy should be reviewed for:

- an obvious, private, working primary channel and a safe fallback;
- product, repository, service, and version scope;
- a plain prohibition on public reports where that is the policy;
- useful report content, without making perfect reproduction a condition of intake;
- testing authorization and limits, or an explicit statement that no authorization is
  granted;
- safe-harbor and legal language reviewed by an authorized human where offered;
- prohibitions on privacy invasion, data alteration, persistence, denial of service, and
  unnecessary access;
- reporter privacy, retention, encryption, and credit or anonymity choices;
- realistic acknowledgment and update expectations;
- coordination and public-disclosure expectations without an inflexible universal timer;
- supported versions and the consequences of best-effort support;
- multi-party or upstream routing; and
- an owner, tested contact route, last review, and event that triggers revalidation.

[RFC 9116](https://www.rfc-editor.org/rfc/rfc9116.html) adds a machine-discoverable
`/.well-known/security.txt`. It requires a Contact field, an Expires field, HTTPS, and
defined formatting; supports Policy, Encryption, Canonical, languages, and
acknowledgments; and recommends an expiry less than a year away. The RFC warns that stale
information can be worse than no file, that a compromised site can redirect reports to
an attacker, and that the file's presence does not grant permission to test. A later Buzz
decision should therefore consider it only if the project can own, monitor, and renew it.

## Coordinated disclosure and advisory quality

CERT/CC describes coordinated vulnerability disclosure as
[an iterative process](https://certcc.github.io/CERT-Guide-to-CVD/tutorials/cvd_is_a_process/)
organized around two questions: what action should be taken, and who else needs to know
what and when. Its discussion of
[why coordination matters](https://certcc.github.io/CERT-Guide-to-CVD/howto/preparation/why_coordinate/)
rejects both automatic immediate full disclosure and permanent secrecy as generally poor
extremes. This means documentation review should not invent a universal embargo period or
treat the word “coordinated” as a completed process.

Private handling normally needs to cover intake, acknowledgment, validation, affected
scope, prioritization, owner assignment, remediation, fix verification, downstream and
multi-vendor coordination, CVE or advisory decisions where applicable, disclosure timing,
publication, monitoring, and root-cause or control improvement.
[NIST SP 800-216](https://csrc.nist.gov/pubs/sp/800/216/final) similarly links formal
report acceptance, assessment, management, and communication of mitigation or
remediation. [NIST's SSDF](https://csrc.nist.gov/pubs/sp/800/218/final) groups
residual-vulnerability identification and response with prevention of recurrence.

A public advisory should enable an affected user to decide and act. Depending on the
case, review for:

- concise vulnerability and impact description;
- affected product, package, component, deployment mode, and version range;
- unaffected or fixed versions where known;
- prerequisites, exposure conditions, and severity rationale;
- patch, upgrade, mitigation, workaround, or disablement steps;
- verification of successful remediation;
- safe indicators of compromise or detection guidance where appropriate;
- identifiers, credits, publication date, update history, and authoritative references;
- downstream or coordinated-vendor status; and
- clear uncertainty where investigation is incomplete.

[GitHub's repository advisories](https://docs.github.com/en/code-security/concepts/vulnerability-reporting-and-management/repository-security-advisories)
support private discussion and remediation followed by public release. GitHub specifically
recommends adding a fixed version before publication where possible, because otherwise
users can be alerted without a safe version to select. That is a useful actionability
criterion, not a rule to delay every advisory: active exploitation, a leak, missing
maintainers, or an effective mitigation can change the balance.

## Stop-and-route procedure for discoveries during documentation review

If a reviewer encounters material that may be a live credential, private operational
coordinate, personal data, or undisclosed vulnerability, the content review should stop
for that item. The reviewer should not investigate exploitability or validity beyond
their authorization.

Candidate sequence:

1. **Do not reproduce it.** Do not paste it into a public issue, PR comment, report,
   screenshot, chat, test fixture, or command output.
2. **Minimize access.** Avoid opening further copies or widening the audience. Do not ask
   an external service to classify the material unless that transfer is authorized.
3. **Route privately.** Use the repository's private advisory for a suspected
   vulnerability and the authorized security or incident channel for secret, privacy, or
   operational exposure.
4. **Preserve a safe locator.** Give authorized responders the minimum information needed
   to find the item without repeating its value. A public work record, if needed, can say
   only that review paused pending private security disposition.
5. **Let owners assess and contain.** Credential owners decide rotation and service
   impact; security owners validate vulnerability scope and coordination; privacy owners
   handle personal data.
6. **Resume only after disposition.** Public editing, redaction, advisory publication, or
   closure follows the authorized decision, not the documentation reviewer's guess.

[GitHub's leaked-secret guidance](https://docs.github.com/en/code-security/tutorials/remediate-leaked-secrets/remediating-a-leaked-secret)
says to treat a leaked secret as immediately compromised: deleting the line or repository
does not prevent use. Revoke or rotate first, identify dependent services and possible
unauthorized access, then consider repository cleanup. Its separate
[history-removal guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
warns that rewriting is disruptive and cannot remove copies from other clones or forks.
That evidence supports containment before cosmetic cleanup.

## Redaction that preserves meaning

Redaction is successful when the remaining document still supports the reader's decision
without retaining the risky material. Prefer a typed marker such as
`[REDACTED: private hostname]` or a stable public alias over unexplained deletion. Where
appropriate, retain:

- the category of material;
- why it mattered;
- the affected component or trust boundary at a safe altitude;
- the decision and responsible role;
- dates and status that are safe to disclose;
- a non-sensitive reference to an authorized private record; and
- the lesson or public mitigation.

Review the entire publication path. Markdown source may be safe while git history, a diff,
an attachment, a screenshot's metadata, rendered link text, an external citation URL, an
alt description, or CI output retains the value. A redaction should not turn “control not
verified” into “control present,” remove uncertainty, conceal impact, or imply that
restricted evidence was independently assessed when it was not.

## Public and private evidence

The corpus evidence model assumes citations that a reviewer can inspect. Security creates
a legitimate exception: the strongest evidence may be restricted. The answer is not to
publish it or to make an unsupported public claim.

A public node can record:

- the claim at a safe level;
- evidence class rather than sensitive contents;
- the authorized custodian or role, if naming it is safe;
- the date, revision, and scope of an authorized verification;
- a public test or design source that supports the non-sensitive portion;
- limitations and what the public reviewer could not inspect; and
- a private record identifier only when its naming convention and location are safe.

The review result should distinguish **publicly reproducible**, **verified by an
authorized reviewer against restricted evidence**, **owner-attested**, and **unable to
assess**. A private citation must not silently receive the same assurance as evidence the
reviewer opened. Conversely, inability to publish evidence does not automatically make a
claim false; it bounds what the public artifact can prove.

## Freshness and split authority

Security documentation is unusually perishable. Contacts expire, ownership changes,
supported versions move, mitigations become fixes, dependencies update, endpoints change,
threats evolve, and a once-safe architectural detail can become operational. Apply the
freshness model from
[`07-freshness-staleness-and-change-impact.md`](07-freshness-staleness-and-change-impact.md)
with shorter review triggers for high-consequence claims.

At minimum, assign owners and triggers for:

- reporting channels and fallback delivery;
- response-time promises;
- supported-version tables;
- authentication and authorization claims;
- cryptographic and auditability statements;
- secret stores, fallback paths, precedence, and rotation procedures;
- TLS and deployment responsibilities;
- open limitations and accepted risks;
- linked upstream policies and standards; and
- published advisories and mitigations.

Buzz has two relevant authorities. Root [`SECURITY.md`](../../../SECURITY.md) directs
Buzz product vulnerabilities to Block's upstream private advisory. The fork's
[`issue chooser`](../../../.github/ISSUE_TEMPLATE/config.yml) provides the launchpad-26
private advisory route for this fork's operational work, while
[`SECURITY-POSTURE.md`](../../SECURITY-POSTURE.md#the-public-repository-rule) explains the
product/operation distinction. That split may be correct, but a reader should not need to
infer it from three files. Review should verify that entry points consistently answer:
**what is affected, who owns it, and which private route applies?**

## Automation and human review

Useful full-population automation includes:

- known-provider, generic, private-key, and project-specific secret patterns;
- push protection and continuous secret scanning where the repository can enable them;
- prohibited filenames, citation targets, and path traversal;
- reserved example-domain and address checks;
- links to reporting policies and advisory routes;
- `security.txt` syntax, HTTPS, canonical URI, expiry, and reachability;
- stale supported-version and dependency references where an authority is machine-readable;
- high-risk wording such as universal, cryptographic, compliance, and certification terms;
- public references to private coordinates or restricted record conventions;
- rendered-output and attachment inventories; and
- consistency between fork and upstream routing statements.

Human or specialist judgment remains necessary for:

- whether combined details form an operational gap map;
- whether a reported behavior is a vulnerability;
- evidence sufficiency for a threat-bounded claim;
- cryptographic, authorization, privacy, legal, and compliance language;
- safe-harbor and testing authorization;
- exploit detail and disclosure timing;
- whether a redaction preserves user action and audit meaning;
- whether a false positive is safe to allowlist; and
- whether a current limitation belongs in public posture or restricted operations.

Buzz's corpus validator currently rejects selected credential-shaped repository citation
paths, keeps those values out of its error messages, and treats external URLs as
unverified. That is a thoughtful narrow control. It does not scan body prose, semantic
sensitivity, embedded values, images, git history, or the correctness of security claims.
Its passing result must not be described as a secret scan or security review.

## Findings from the current Buzz documentation surfaces

These are content-governance observations, not vulnerability findings.

### The public-repository rule is explicit but not enforced by that document

[`launchpad/AGENTS.md`](../../AGENTS.md#8-security) forbids public vulnerability issues
and tracked secrets, keys, tokens, and private hostnames.
[`SECURITY-POSTURE.md`](../../SECURITY-POSTURE.md#the-public-repository-rule) accurately
distinguishes a binding rule from a checking mechanism and says compliance rests on human
attention. The later checklist should preserve that honesty and separately inventory any
actual preventive and detective controls.

### The posture document already applies a valuable disclosure distinction

[`SECURITY-POSTURE.md`](../../SECURITY-POSTURE.md#what-is-true-today) retired a dated
control-by-control readiness table because it mixed stale present-tense claims with a
public gap map. It retains accepted risks, public reasoning, boundaries, and open
decisions while locating detailed current posture privately. This is a concrete Buzz
example of stable public model versus live restricted state.

It is not a universal reason to omit limitations. Readers still need enough public
information to operate safely, understand delegated responsibilities, and know when the
project cannot provide a protection. The review question is necessity and risk at the
chosen altitude, not whether a fact is flattering.

### Root `SECURITY.md` carries high-consequence claims and promises

The file contains absolute or broad statements about connection authentication, channel
authorization and visibility, audit-log properties, desktop secret storage and fallback,
input validation, TLS responsibility, dependency scanning, and unsafe Rust. It also uses
“SOX-grade” language and promises acknowledgment within 48 hours and a fuller response
within seven days.

This research does not determine whether those statements are correct. Their consequence,
scope, modality, and volatility make them candidates for evidence-backed security review.
In particular, a review should distinguish product implementation from deployment
configuration, test each absolute across applicable interfaces, define the criterion
behind compliance-like wording, and confirm that promised response routes and times have
an owner and observed capability.

### The fork/upstream reporting split needs one obvious explanation

The fork issue chooser routes operational vulnerabilities privately to launchpad-26;
root `SECURITY.md` routes product vulnerabilities privately to Block. Both prohibit
public reporting. The distinction is documented, but distributed. An explicit routing
table or equivalent entry point could reduce misrouting; whether to add one belongs to
the synthesis and project owners.

### Security-relevant corpus nodes are drafts

Selected nodes for WebSocket authentication, the community security boundary, secret
configuration, the audit log, and hosted topology all have `status: draft` at the
inspected revision. Their evidence ledgers are useful, but draft status does not itself
communicate whether a reader may rely on a security claim. Promotion should require
security-specific evidence and disclosure review proportional to consequence.

### The validator protects citation handling, not content meaning

[`validate.py`](../../project-intelligence/corpus/validate.py) uses a deliberately narrow
credential-like filename and extension blocklist, allows conventional public templates
such as `.env.example`, prevents repository-relative citation escape, and does not echo a
rejected citation value. Those design choices reduce leakage and false positives.

The validator cannot establish that body text contains no credential or private hostname,
that a screenshot or history is safe, that a placeholder is non-operational, or that a
security assertion is correct. This boundary should be stated in any corpus-review
report.

## Candidate security-documentation review checklist

These are research outputs for later synthesis, not approved requirements.

### A. Classification and authority

- [ ] Has every security-relevant item been classified before publication?
- [ ] Are public knowledge, context-sensitive detail, restricted operations, secrets,
      personal data, embargoed vulnerabilities, and coordinated advisories distinct?
- [ ] Is the publisher authorized to release this information and evidence?
- [ ] Has combination risk been considered rather than checking each fact in isolation?
- [ ] Is “already public” supported by an authoritative source and a reason to aggregate?
- [ ] Are the product owner, deployment owner, security owner, and disclosure authority
      unambiguous?

### B. Security claims and evidence

- [ ] Does each material claim name its object, property, threat, boundary, layer,
      conditions, version, and exceptions?
- [ ] Is design intent kept distinct from implementation, configured behavior, and
      observed runtime state?
- [ ] Does evidence match the layer and revision claimed?
- [ ] Have absolute, negative, exclusive, cryptographic, isolation, deletion, fallback,
      and compliance-like claims received specialist challenge?
- [ ] Are delegated responsibilities such as TLS termination stated as obligations, with
      verification guidance, rather than implied protections?
- [ ] Are limitations and unverified areas visible without publishing an actionable gap
      map?
- [ ] Does restricted evidence receive an explicitly bounded result rather than silent
      equivalence to public reproducibility?

### C. Architecture, posture, and threat models

- [ ] Are assets, actors, trust boundaries, assumptions, data flows, dependencies, and
      failure behavior described at the necessary stable altitude?
- [ ] Does the public document avoid live private coordinates, access paths, identities,
      and control-by-control operational state?
- [ ] Are public limitations sufficient for a user to operate and assess risk safely?
- [ ] Are threat status and mitigation claims supported, especially `Mitigated` and
      `Not Applicable`?
- [ ] Are active unpatched findings routed out of public threat and architecture records?
- [ ] Does every volatile posture claim have an owner, observation date, and trigger?

### D. Secrets, configuration, and examples

- [ ] Are there no live or plausible credentials, keys, tokens, password hashes,
      connection strings, private hostnames, or personal data?
- [ ] Are example domains and addresses reserved, local by design, or otherwise proven
      non-operational?
- [ ] Are placeholders conspicuous and safe under copy, shell expansion, logging, and
      persistence?
- [ ] Do examples use minimum privilege and safe defaults?
- [ ] Are development-only, plaintext, bypass, debug, internet-facing, and destructive
      modes warned before execution?
- [ ] Are secret custody, access, injection, rotation, revocation, dependencies, incident
      contact, and exposure impact explained without exposing values?
- [ ] Have logs, screenshots, attachments, filenames, URLs, metadata, diffs, generated
      output, and history received equivalent review?

### E. Reporting policy and discovery

- [ ] Is the private primary route obvious, working, access-controlled, and monitored?
- [ ] Is there a safe fallback if that route is unavailable?
- [ ] Are product, service, repository, version, in-scope, and out-of-scope boundaries
      clear?
- [ ] Is useful report content requested without rejecting imperfect good-faith reports?
- [ ] Are testing authorization, safe harbor, privacy, data handling, and prohibited
      actions explicit and approved by the appropriate authority?
- [ ] Are acknowledgment and update expectations realistic, owned, and measured?
- [ ] Do the issue chooser, contributing guide, security policy, website, fork, and
      upstream routes agree?
- [ ] If `security.txt` exists, is it valid, canonical, HTTPS-served, current, monitored,
      and linked to the actual policy rather than treated as permission or the programme?

### F. Vulnerability handling and advisories

- [ ] Are disclosure policy, internal handling, advisory, threat model, posture, and
      incident response represented as distinct artifacts?
- [ ] Does the private process cover intake, validation, priority, ownership,
      remediation, verification, coordination, disclosure, monitoring, and learning?
- [ ] Is disclosure timing an explicit risk decision rather than a universal timer?
- [ ] Does a public advisory identify affected and fixed versions or clearly state what
      remains unknown?
- [ ] Can an affected user understand impact, prerequisites, mitigation, upgrade, and
      verification?
- [ ] Are severity rationale, identifiers, credits, references, update history, and
      multi-party status accurate and safely publishable?
- [ ] Has exploit-enabling detail received an explicit coordinated-release decision?

### G. Discovery, redaction, and remediation

- [ ] Does review stop and route privately on a possible secret, personal-data exposure,
      private operational coordinate, or undisclosed vulnerability?
- [ ] Is the sensitive value absent from all public review artifacts and external tools?
- [ ] Is any public marker minimal and non-sensitive?
- [ ] For a leaked secret, has revocation or rotation taken precedence over text removal?
- [ ] Have dependent services and possible unauthorized use been assessed by owners?
- [ ] Has history cleanup been decided with its coordination, retention, and
      recontamination consequences understood?
- [ ] Does redaction preserve category, consequence, decision, safe provenance, and user
      action?
- [ ] Has the entire delivery path, not only the latest Markdown body, been checked?

### H. Freshness, automation, and reporting

- [ ] Does each high-consequence document have an owner, last review, supported scope,
      and event trigger?
- [ ] Are contact routes, response promises, supported versions, mitigations, and linked
      standards periodically exercised or checked?
- [ ] Are deterministic scans applied to the full publication surface with tested rules
      and narrow, justified allowlists?
- [ ] Are tool limits, false positives, scan revision, coverage, and inaccessible surfaces
      recorded?
- [ ] Is human or specialist review required for semantic sensitivity and technical
      security claims?
- [ ] Does the result state what was checked publicly, what was verified privately, what
      could not be assessed, and what was deliberately excluded?
- [ ] Are urgent findings prevented from entering the ordinary public finding register?

## Measures that support governance

Useful measures retain denominators, scope, and consequence:

- percentage of public reporting entry points whose private route and fallback were
  exercised within the review period;
- response promises with named ownership and observed performance, without exposing
  report details;
- supported-version statements aligned with current release policy;
- high-consequence security claims by evidence layer, revision age, and verification
  state;
- security-relevant nodes reviewed by risk tier, method, depth, and specialist role;
- publication surfaces covered by secret scanning and the pattern or custom-rule families
  enabled;
- confirmed secret exposures by containment time, rotation time, affected-surface review,
  and recurrence, reported without secret material;
- advisories with affected scope, fixed version or mitigation, user action, and update
  history;
- stale, misrouted, or unreachable reporting paths found and corrected;
- security-document defects escaped into a release or operational event; and
- recurring finding classes that changed a template, standard, test, scanner, ownership,
  or process.

Avoid a single security-document quality score, raw secret-pattern hit count, disclosure
detail count, or “zero findings” claim. They reward suppression, create incentives to
avoid difficult review, and collapse radically different evidence. A scan that found
nothing may have excellent coverage, the wrong patterns, no access to images and history,
or no findings; those states are not interchangeable.

## Common failure modes

- **Obscurity as architecture:** security assumptions and boundaries are omitted because
  attackers might read them.
- **Transparency absolutism:** live topology, gaps, or exploit detail is published in the
  name of openness without a necessity or timing decision.
- **Secret-shaped-only scanning:** known token formats pass, so semantic credentials,
  private coordinates, logs, screenshots, and novel formats are assumed safe.
- **Latest-file cleanup:** a leaked secret is deleted from the current file but not
  revoked, rotated, investigated, or considered in history and forks.
- **Plausible placeholder:** an example looks fake but is a real domain, address,
  account, token, or production-shaped default.
- **Copy-paste hazard:** a non-secret example creates world-readable state, excessive
  privilege, disabled verification, or plaintext persistence.
- **Code-proves-production:** source behavior is used to claim a deployment control is
  active.
- **Intent-proves-control:** an ADR, requirement, or policy is treated as runtime evidence.
- **Scanner-proves-absence:** a green pattern scan becomes “there are no secrets.”
- **Compliance adjective:** “grade,” “compliant,” “certified,” or “secure” appears without
  an applicable criterion, scope, authority, and evidence.
- **Absolute without attack surface:** “only” or “invisible” is reviewed on one path while
  another interface is outside the test.
- **Policy-only programme:** a good `SECURITY.md` exists, but no owner monitors intake or
  handles reports.
- **Stale contact:** a discoverable reporting channel routes sensitive reports to an
  abandoned or wrong recipient.
- **`security.txt` permission inference:** the discovery file is mistaken for testing
  authorization.
- **Rigid disclosure clock:** one deadline overrides exploitation, downstream, patch,
  reporter, and multi-vendor conditions.
- **Advisory without action:** users are told a vulnerability exists but not whether they
  are affected or what safe version or mitigation to use.
- **Public triage:** the reviewer asks for a reproducer or secret value in a public issue
  to confirm whether the report is real.
- **Redaction by deletion:** the sensitive phrase disappears along with impact, decision,
  uncertainty, and audit trail.
- **Private-evidence laundering:** “security reviewed” is asserted without naming who was
  authorized, what class of evidence was checked, or what remains unreproducible.
- **Distributed authority:** fork and upstream policies are each locally correct but the
  reader cannot tell which one owns the report.
- **Security-review theatre:** a checklist pass reports no vulnerabilities even though the
  exercise assessed documentation, not the system.

## Competing positions and reconciliations

### “Publish the architecture” versus “do not hand attackers a map”

Architecture, assumptions, and limitations support secure operation and review. Current
coordinates and control gaps can reduce attacker cost. Publish stable abstractions and
delegated responsibilities at the level legitimate readers need; restrict live state and
embargoed findings. Record the disclosure decision rather than relying on vague
“sensitive” labels.

### “The information is already public” versus “do not amplify it”

Public availability can support citation and reproducibility, but aggregation and an
authoritative context can create new value for attackers or new privacy harm. Verify the
source, necessity, currency, and combination risk. Prior publication is evidence, not
automatic authorization to republish.

### “Be specific” versus “do not expose operational detail”

Vague security guidance is unusable; excessive specificity can identify a target. Be
precise about the model, invariant, role, configuration interface, verification method,
and failure consequence. Parameterize environment-specific coordinates and keep current
control state in the authorized operational record.

### “Disclose immediately” versus “wait for a fix”

Immediate disclosure can warn users but also enable exploitation before mitigation.
Waiting can improve remediation but leave users uninformed or permit indefinite delay.
Use coordinated, case-specific decisions that account for exploitation, leaks, severity,
user mitigations, patch readiness, downstreams, and reporter communication. Preserve the
reason for timing.

### “Rewrite history” versus “rotate and move on”

History cleanup reduces discoverability but is disruptive, incomplete across clones and
forks, and can recontaminate the repository. Rotation or revocation removes credential
utility and comes first. Authorized owners should then decide cleanup based on remaining
sensitivity, legal or retention duties, copies, and coordination cost.

### “Automate secret review” versus “humans understand context”

Automation is fast, repeatable, and broad for encoded patterns. Humans recognize semantic
credentials, unsafe combinations, and misleading claims but are inconsistent and can
miss repetitive material. Run tested scanners across the full surface and use human
review for context, with narrow allowlists and incident feedback improving both.

### “All evidence should be public” versus “some evidence must remain restricted”

Public evidence makes claims reproducible; restricted evidence protects systems and
people. Publish what can safely support the claim, state the verification class and
limitations, and use an authorized reviewer for restricted evidence. Do not publish the
evidence or overstate the conclusion merely to satisfy a citation format.

## Claim ledger

| Claim | Main support | Counterevidence or boundary | Confidence / gap |
|---|---|---|---|
| Security documentation needs both useful transparency and a disclosure boundary | NIST SP 800-160 v1r1; RFC 9116; CERT/CC CVD; local security posture | No external source gives a universal public/private content line; context and threat model govern | High on principle; local classification requires a decision |
| Vulnerability disclosure and vulnerability handling are distinct but connected | ISO/IEC 29147 public abstract; ISO/IEC 30111 public abstract; NIST SP 800-216 | Full ISO clauses were not publicly accessible | High on distinction; medium on detailed ISO implementation |
| `security.txt` improves discoverability but is not a programme or permission grant | RFC 9116 fields, scope, stale-information warning, and no-implied-permission section | It is domain-oriented and may not resolve a multi-repository ownership split by itself | High |
| Coordinated disclosure is iterative and case-specific | CERT/CC process and coordination guidance; GitHub advisory workflow | Projects may adopt default timelines, and laws or contracts can impose deadlines | High; local timing authority unresolved |
| Public advisories should prioritize affected-user action | ISO/IEC 29147 purpose; GitHub advisory fix-version guidance; CERT/CC remediation framing | A fixed version may not exist when active exploitation or a leak forces communication | High |
| A leaked secret must be revoked or rotated; deleting text is insufficient | GitHub leaked-secret remediation and history-removal guidance; OWASP secret lifecycle | Exact response depends on provider, validity, dependencies, and incident authority | High |
| Reserved domains and IP ranges reduce accidental contact with real systems | RFC 2606 and RFC 5737 | Localhost and private ranges have different behavior and should not substitute blindly | High |
| Automated scanning cannot prove absence of secrets or semantic disclosure risk | GitHub notes incomplete push-protection coverage; local validator's deliberately narrow scope | Better custom patterns and multiple surfaces increase assurance | High |
| High-consequence security claims need threat-bounded, layer-matched evidence | NIST SP 800-160 v1r1; local corpus evidence model; prior truth research | No reviewed source prescribes Buzz's exact claim schema | High on need; medium on proposed fields |
| Buzz's fork/upstream split is documented but distributed | Root SECURITY.md, fork issue chooser, launchpad security posture | Reader testing was not performed, so actual misrouting is unknown | High on distribution; medium on usability consequence |
| Selected security corpus nodes are drafts | Direct front-matter inspection at the named revision | Selection was purposive, not a census of every security-relevant node | High for named nodes only |
| Buzz's validator guards some citation paths but does not perform semantic security review | Direct validator and test inspection | Other repository controls were not inventoried in this report | High for the validator boundary |

## Implications for the later corpus checklist

The final synthesis should not append a generic “contains no secrets” checkbox to an
otherwise ordinary content review. Security changes the review flow:

1. classify the content and authority before opening or reproducing evidence;
2. apply a safe stop-and-route path before creating a public finding;
3. verify public security claims by threat, boundary, layer, condition, and revision;
4. compose extra criteria for architecture, configuration, procedures, examples,
   policies, posture, threat models, advisories, and incident learning;
5. separate public reproducibility from authorized review of restricted evidence;
6. include rendered artifacts, metadata, diffs, attachments, and history in the
   publication surface;
7. require specialist review for high-consequence claim and disclosure classes;
8. test reporting routes and promises as operational documentation, not just prose;
9. keep product and operational ownership explicit across fork and upstream; and
10. report security-document assurance without claiming that the software was penetration
    tested, vulnerability-free, compliant, or secure.

This report should be reconciled particularly with topics 03, 07, 08, 09, 10, 12, and
14. Evidence quality, freshness, procedural safety, normative force, architecture
abstraction, executable examples, and corpus-scale coverage all acquire sharper handling
when the content can expose systems or mislead users about protection.

## Limitations and open questions

- No security test, penetration test, production observation, private-repository review,
  credential validation, or vulnerability triage was performed.
- The review inspected selected local security surfaces, not every one of the 205 corpus
  nodes or every file outside the corpus.
- Search terms locate likely material but miss semantic security claims and include many
  harmless references; no prevalence estimate is made.
- The full ISO/IEC 29147 and 30111 texts were not publicly available, so only public
  abstracts and lifecycle status informed the synthesis.
- No legal review was performed. Safe harbor, testing authorization, privacy, retention,
  regulatory notice, export-control, and contractual duties require authorized advice.
- The research did not test whether the upstream or fork private advisory is enabled,
  monitored, accessible to an external reporter, or meeting its stated response times.
- The research did not decide whether Buzz should publish `security.txt`, OpenSSF
  Security Insights, a routing table, or additional security metadata.
- It did not determine whether any root `SECURITY.md` design or compliance-like claim is
  true, false, too broad, or deliberately inherited from upstream.
- A project classification vocabulary, redaction syntax, disclosure authority, public
  posture altitude, reviewer qualifications, and exception process remain human
  decisions.
- Disclosure safety changes with deployment, threat, patch status, exploitation, and
  external publication; no permanent word-level allowlist can replace reclassification.

## Sources

### Local sources

- [`SECURITY.md`](../../../SECURITY.md) — upstream product reporting route, supported
  versions, response promises, design claims, and disclosure statement.
- [`launchpad/SECURITY-POSTURE.md`](../../SECURITY-POSTURE.md) — public/private posture
  boundary, accepted risks, reporting split, and public-repository rule.
- [`launchpad/AGENTS.md` §8](../../AGENTS.md#8-security) — binding public-repository and
  vulnerability-routing rules.
- [`.github/ISSUE_TEMPLATE/config.yml`](../../../.github/ISSUE_TEMPLATE/config.yml) —
  fork private advisory entry point.
- [`launchpad/AGENT_PR_TEMPLATE.md`](../../AGENT_PR_TEMPLATE.md) — security implication,
  secret-check, and never-deferrable review prompts.
- [`launchpad/docs/corpus/templates/threat-model.md`](../../docs/corpus/templates/threat-model.md)
  — artifact boundaries, threat status, evidence, and review triggers.
- [`launchpad/project-intelligence/corpus/validate.py`](../../project-intelligence/corpus/validate.py)
  and its [tests](../../project-intelligence/corpus/tests/test_validate.py) — citation
  validation, credential-like path handling, safe errors, and external-URL boundary.
- [`layers/configuration/secrets.md`](../../docs/corpus/layers/configuration/secrets.md),
  [`architecture/deployment/hosted-topology.md`](../../docs/corpus/architecture/deployment/hosted-topology.md),
  [`architecture/flows/websocket-authentication.md`](../../docs/corpus/architecture/flows/websocket-authentication.md),
  [`layers/observability/audit-log.md`](../../docs/corpus/layers/observability/audit-log.md),
  and
  [`architecture/principles/community-is-security-boundary.md`](../../docs/corpus/architecture/principles/community-is-security-boundary.md)
  — selected draft security-relevant corpus nodes.

### External sources

- [ISO/IEC 29147:2018 — Vulnerability disclosure](https://www.iso.org/standard/72311.html)
  — current published standard's public purpose and coverage of report receipt and
  remediation-information disclosure; ISO marks it to be revised.
- [ISO/IEC 30111:2019 — Vulnerability handling processes](https://www.iso.org/standard/69725.html)
  — current confirmed standard's public scope for processing and remediating reported
  potential vulnerabilities; ISO marks it to be revised.
- [RFC 9116 — A File Format to Aid in Security Vulnerability Disclosure](https://www.rfc-editor.org/rfc/rfc9116.html)
  — `security.txt` format, contact, expiry, location, scope, security considerations, and
  no implied permission for testing.
- [CERT/CC Guide: Coordinated Vulnerability Disclosure is a Process, Not an Event](https://certcc.github.io/CERT-Guide-to-CVD/tutorials/cvd_is_a_process/)
  — iterative action and communication decisions.
- [CERT/CC Guide: Why Coordinate?](https://certcc.github.io/CERT-Guide-to-CVD/howto/preparation/why_coordinate/)
  — trade-offs between immediate full disclosure and permanent secrecy.
- [NIST SP 800-216 — Recommendations for Federal Vulnerability Disclosure Guidelines](https://csrc.nist.gov/pubs/sp/800/216/final)
  — formal receipt, handling, and remediation communication guidance; federal scope noted.
- [NIST SP 800-218 — Secure Software Development Framework 1.1](https://csrc.nist.gov/pubs/sp/800/218/final)
  — residual-vulnerability response and recurrence prevention within secure development.
- [NIST SP 800-160 Volume 1 Revision 1 — Engineering Trustworthy Secure Systems](https://csrc.nist.gov/pubs/sp/800/160/v1/r1/final)
  — security-engineering principles, credible evidence, and precise, verifiable security
  specifications.
- [GitHub: Repository security advisories](https://docs.github.com/en/code-security/concepts/vulnerability-reporting-and-management/repository-security-advisories)
  — private collaboration, patch and publication workflow, CVE support, and fix-version
  importance.
- [GitHub: Remediating a leaked secret](https://docs.github.com/en/code-security/tutorials/remediate-leaked-secrets/remediating-a-leaked-secret)
  — immediate-compromise assumption, rotation or revocation, impact investigation,
  history cleanup, and prevention.
- [GitHub: Removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
  — rotation-first guidance and the disruption, persistence, and recontamination risks of
  history rewriting.
- [GitHub: Secret leakage risks](https://docs.github.com/en/code-security/concepts/secret-security/secret-leakage-risks)
  — push protection, continuous scanning, custom patterns, and explicit coverage limits.
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
  — least privilege, lifecycle, rotation, logging, and secret-management documentation.
- [RFC 2606 — Reserved Top Level DNS Names](https://www.rfc-editor.org/rfc/rfc2606.html)
  — domains reserved for documentation and testing.
- [RFC 5737 — IPv4 Address Blocks Reserved for Documentation](https://www.rfc-editor.org/rfc/rfc5737.html)
  — IPv4 ranges reserved for examples.
- [OpenSSF Security Insights](https://github.com/ossf/security-insights) — an optional
  machine-readable snapshot for project security practices, useful as a comparison but
  not adopted or evaluated here.
