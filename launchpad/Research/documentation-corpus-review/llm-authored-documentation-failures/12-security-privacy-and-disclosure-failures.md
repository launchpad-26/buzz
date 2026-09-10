# Security, privacy, and disclosure failures

| Metadata | Value |
|---|---|
| Topic number | 12 |
| Exact research question | How can documentation agents expose secrets, personal information, private operational details, undisclosed vulnerabilities, or unsafe security guidance, and why might ordinary controls miss these failures? |
| Primary model | Codex |
| Research date | 2026-09-09 |
| Scope | Agents that create or revise repository documentation from code, configuration, logs, issues, tool output, and other technical evidence; Markdown source, rendered documentation, examples, runbooks, architecture and security documents; public and access-controlled repositories. “Ordinary controls” means repository permissions, `.gitignore`, provider-pattern secret scanning or push protection, source-code scanning, routine CI, and general editorial review. This report does not assess any live system, disclose a real secret or vulnerability, prescribe jurisdiction-specific privacy compliance, or cover adversarial prompt injection except where it changes disclosure impact. |
| Evidence limitations | Direct empirical research on autonomous documentation agents is sparse. The strongest evidence comes from standards, platform documentation, privacy research, model memorization studies, and code-assistant studies; applying it to documentation workflows is therefore partly an information-flow and tooling inference. No prevalence rate is supportable, no current model was benchmarked, and this public checkout was not searched for secrets, personal data, vulnerabilities, or private infrastructure details. |

## Executive answer

Documentation agents can disclose protected information through a simple but easily
missed boundary change: the agent is allowed to read material whose audience is narrow,
then copies, paraphrases, aggregates, or operationalizes it into a document whose
audience is wider. The output may contain a recognizable credential; a person's direct
identifier or linkable combination of facts; an operational map assembled from harmless
fragments; vulnerability details published before coordination or remediation; or an
insecure command, code sample, or security recommendation that a reader may execute.
Generative models add two secondary routes: memorized material can sometimes be
reproduced, and sensitive facts can be inferred by joining disparate sources. NIST
expressly identifies leakage, unauthorized disclosure, de-anonymization, memorization,
and cross-source inference as generative-AI privacy risks
([NIST AI 600-1, pp. 7 and 10](https://doi.org/10.6028/NIST.AI.600-1)).

The central conclusion is **high confidence as an information-flow risk but only
moderate confidence about documentation-agent incidence**. Direct context-to-output
copying needs no model defect: correct synthesis can itself violate the publication
boundary. Ordinary controls miss it because each control recognizes only part of the
problem. Pattern scanners cover identifiable secret formats, not every credential and
not ordinary prose that reveals people, topology, weaknesses, or unsafe policy. PII is
contextual and may emerge only through linkage. Source-code analyzers do not establish
that fenced examples or natural-language instructions are safe. Editorial review may
validate truth and readability without re-evaluating audience or disclosure timing.
Finally, a public Git push can create copies that a later deletion cannot reclaim;
GitHub therefore advises revocation or rotation first and notes that clones, forks,
cached views, and pull-request references can retain the material
([GitHub, “Removing sensitive data”](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)).

The supported response is layered and preventive: minimize the agent's readable inputs;
classify both sources and publication destinations; generate with synthetic placeholders;
scan source, rendered output, and history with credential, PII, organization-specific,
and semantic checks; route possible vulnerabilities through a private coordinated
disclosure process; extract and security-test executable examples; and require a human
who understands both the domain and intended audience to approve publication. These
layers reduce risk but do not prove absence. Automated PII detection, for example, is
explicitly not guaranteed to find all sensitive information
([Microsoft Presidio](https://microsoft.github.io/presidio/)).

## Question, scope, and method

### Subquestions

- What information and advice can cross a disclosure boundary in agent-authored
  technical documentation?
- Which model, tool, repository, and review mechanisms create or amplify each route?
- What harms follow, and which claims are supported directly rather than inferred from
  adjacent settings?
- Which preventive and detective controls address each route, and what can each control
  not establish?
- Under what conditions are the risks smaller, and what counterevidence limits
  generalization?

### Exclusions

- Discovery, reproduction, or publication of any live credential, private host detail,
  personal record, or non-public vulnerability.
- A security audit of Buzz, its deployment, this repository, or its history.
- Legal conclusions about whether particular information is personal data, whether a
  breach is reportable, or what disclosure law applies in a jurisdiction.
- Model-training governance except for the bounded risk that memorized training material
  can appear in output.
- Malicious prompt injection and source poisoning as primary causes; those belong to
  topic 17.
- Program-wide synthesis or adoption of the candidate controls as cohort policy.

### Evidence and source plan

Local evidence was inspected first at Git commit
`81b5a1d059ea897968c4fe412497a351892d4598` on branch
`docs/llm-research-program` on 2026-09-09. The checkout's governing instructions say
that committed files are world-readable and forbid tracked secrets, tokens, keys, and
private hostnames
([`launchpad/AGENTS.md` §8 at the inspected revision](../../../AGENTS.md#8-security)).
Its public security-posture document carefully distinguishes a binding rule from an
enforcement mechanism and avoids publishing a current control-by-control gap map
([`launchpad/SECURITY-POSTURE.md` at the inspected revision](../../../SECURITY-POSTURE.md#the-public-repository-rule)).
These observations establish relevant local audience and policy conditions, not the
repository's compliance with them.

External research prioritized NIST guidance and definitions, GitHub and Git's own
documentation of repository controls, FIRST and CERT/CC disclosure guidance, OWASP
technical guidance, and peer-reviewed security studies. A working claim ledger tracked
claim type, direct support, counterevidence, context, confidence, and gaps. Searches
specifically sought scanner limitations, re-identification, secure disclosure, insecure
generated examples, effective controls, and findings that did *not* show increased
security risk. Research stopped when additional searches repeated the same failure
classes and mitigation boundaries. No source located measured the end-to-end prevalence
of disclosure defects in autonomous documentation-agent commits; conclusions that
transfer from adjacent evidence are identified as interpretations.

## Failure taxonomy

| Failure class | Description | Evidence and boundary conditions |
|---|---|---|
| Direct secret reproduction | A credential, private key, session value, authenticated connection string, recovery material, or secret-bearing command is copied from configuration, logs, terminal output, issues, or examples into prose or a code block. Encoding, splitting a credential across locations, or paraphrasing surrounding text can change its detectable shape without reducing its authority. | **High confidence in feasibility.** OWASP's logging guidance lists access tokens, passwords, connection strings, encryption keys, and primary secrets as data that should usually be removed, masked, sanitized, hashed, or encrypted before recording ([OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html#data-to-exclude)). GitHub documents that some credential pairs are detected only when both elements occur in the same file and that push protection covers a subset of identifiable patterns ([secret-scanning scope](https://docs.github.com/en/code-security/reference/secret-security/secret-scanning-scope)). No incidence rate for documentation agents was found. |
| Personal-data disclosure and re-identification | The output repeats a name, address, account identifier, location, health or employment fact, user content, or audit trail. It can also remove a name while retaining enough linked or linkable facts to distinguish or trace someone. | **High confidence in the breadth of the failure class; moderate for agent incidence.** NIST defines PII to include information that distinguishes or traces an individual and other information linked or linkable to them, and recommends minimizing its use, collection, and retention ([NIST SP 800-122, pp. ES-1–ES-2 and §2.1](https://doi.org/10.6028/NIST.SP.800-122)). The definition and required safeguards remain context-dependent; this report makes no legal classification. |
| Private operational-detail aggregation | A document exposes internal names, network or trust relationships, administrative routes, access patterns, deployment cadence, control gaps, backup facts, or component versions. Individual facts may be public-looking; their synthesis can lower the effort needed to map or target a system. | **Moderate confidence.** OWASP treats file paths, internal network names and addresses, and database connection strings as information that may require special handling ([Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html#data-to-exclude)). The local posture document's decision not to publish a current gap table is a repository-specific example of aggregation sensitivity, not empirical proof of attack or a universal rule. |
| Transformative or residual disclosure | Summarization, formatting, “sanitization,” screenshots, generated examples, or rendered output preserves sensitive meaning after obvious strings are removed. Initials, rare roles, dates, error text, metadata, links, filenames, or combined facts can undo superficial redaction. | **High confidence for re-identification risk.** The UK Information Commissioner's Office advises testing apparently anonymous output against a motivated person who can combine it with public sources, and distinguishes pseudonymization from anonymization ([ICO anonymisation guidance](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-sharing/anonymisation/how-do-we-ensure-anonymisation-is-effective/)). This guidance is UK-specific; the technical linkage problem generalizes, while legal consequences do not automatically do so. |
| Premature vulnerability disclosure | An agent turns a private report, failing test, patch explanation, or issue discussion into release notes, troubleshooting guidance, a public issue, or a detailed architecture gap before affected parties have validated and coordinated remediation. Correct technical detail can be the defect because timing and audience are wrong. | **High confidence in the process requirement; unknown incidence.** CERT/CC explains that vulnerability knowledge can increase adversarial advantage when deployers lack remediation and defines coordinated disclosure as sharing among stakeholders before public disclosure ([CERT Guide to CVD](https://certcc.github.io/CERT-Guide-to-CVD/)). FIRST's PSIRT Framework 1.1 calls for honoring embargoes and using secure channels for confidential vulnerability information ([FIRST PSIRT Services Framework 1.1, §1.2.2](https://www.first.org/standards/frameworks/psirts/psirt_services_framework_v1.1)). |
| Unsafe security guidance | A runbook, example, or recommendation disables verification, grants excessive privilege, exposes a service, logs sensitive data, uses weak authentication or cryptography, omits threat-model assumptions, or presents a debugging shortcut as production-safe. The prose can be syntactically valid and operationally effective while weakening security. | **Moderate confidence for transfer to documentation agents.** In a CCS 2023 user study, participants using one Codex-based assistant produced less-secure solutions and expressed more confidence in their security ([Perry et al., 2023](https://arxiv.org/abs/2211.03622)). However, a USENIX 2023 study of 58 students doing a bounded C task found the security impact small and no more than a 10% increase in critical bugs ([Sandoval et al., 2023](https://www.usenix.org/conference/usenixsecurity23/presentation/sandoval)). Model, task, user, and evaluation differences preclude a universal “AI makes guidance insecure” claim. |
| Latent memorization or cross-source inference | The model emits a rare sequence learned during training or infers a sensitive attribute by joining otherwise separate facts, even when the task context does not visibly contain the final disclosure. | **Demonstrated for some models, but low-to-moderate applicability to a particular documentation agent.** Carlini et al. extracted memorized training examples, including public PII, from GPT-2 ([USENIX Security 2021](https://www.usenix.org/conference/usenixsecurity21/presentation/carlini-extracting)); NIST also records cross-source inference as a GAI privacy risk ([NIST AI 600-1, §2.7](https://doi.org/10.6028/NIST.AI.600-1)). These results do not establish that a current agent, model, deployment, or ordinary documentation prompt will reproduce private training data. Directly supplied repository context is the more immediate and testable route. |

## Causes and mechanisms

The first mechanism is **authorization without audience preservation**. A repository
agent may correctly receive read access to private issues, CI output, logs, source,
configuration, or a broad workspace because those inputs help it document the system.
The generated file is a new information object. Its repository, branch, artifact host,
rendered site, and downstream indexes can have a different audience. An input access
check answers whether the agent may read; it does not answer whether every fact may be
republished. OWASP's LLM risk guidance therefore treats sensitive information in both
the model and application context and recommends least privilege and restricted data
sources
([OWASP LLM02:2025](https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/)).
The application to documentation is a **researcher interpretation**: publication needs
an explicit information-flow policy, not merely authenticated retrieval.

The second mechanism is **synthesis-induced sensitivity**. Documentation is designed to
connect scattered evidence. That makes it capable of creating a concise operational map
or a re-identifiable profile even when no source fragment looked independently
restricted. NIST warns that an audit log can trace an individual's activities and that
PII includes logical association with other information
([SP 800-122, §2.1](https://doi.org/10.6028/NIST.SP.800-122)); the ICO's motivated-intruder
test adds the realistic assumption that a reader can search public sources. A literal
redaction pass over source strings cannot detect a harmful relationship that exists only
in the synthesis.

The third is **representation change**. Agents quote, normalize, decode, summarize,
construct example values, turn tables into prose, embed terminal output, and generate
rendered sites. A supported token can become separated from its identifier; personal
data can move from a structured field into narrative; and a dangerous setting can be
described rather than expressed as analyzable code. GitHub documents both the value and
the designed limits of its controls: secret scanning uses patterns and validation;
push protection blocks only a subset of the most identifiable patterns, can miss legacy
tokens and same-secret pairs split across files, and may skip or time out on large
pushes
([GitHub secret-scanning scope](https://docs.github.com/en/code-security/reference/secret-security/secret-scanning-scope)).
Custom patterns extend coverage, but do not turn pattern matching into a classifier for
all confidential facts.

The fourth is **control segmentation**. Different checks answer different questions:
Markdown lint verifies structure, link checking verifies reachability, tests verify
selected behavior, secret scanning looks for supported credential shapes, and code
scanning analyzes supported source languages. GitHub describes CodeQL as building a
database for a listed set of programming languages; Markdown is not one of those
languages
([GitHub CodeQL documentation](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-code-scanning)).
It follows that an ordinary CodeQL success is not evidence that prose or fenced snippets
were analyzed. A separate extractor can test snippets, but even successful execution
does not establish appropriate privilege, confidentiality, or production safety.

The fifth is **late detection at an effectively irreversible boundary**. `.gitignore`
only keeps intentionally untracked files untracked; it does not affect files already
tracked
([Git documentation](https://git-scm.com/docs/gitignore)). Post-push scanning can alert,
but a public disclosure has already occurred. Removing a later commit does not remove
earlier Git objects or copies. GitHub's remediation guidance identifies clones, forks,
cached views, and pull requests as residual locations and makes rotation or revocation
the first response for leaked credentials. This supports preventive publication gates
and an incident plan; it does not support the impossible promise that prevention will
never fail.

Finally, **plausibility can mask unsafe advice**. A security shortcut often appears to
solve the immediate task and may pass a happy-path test. Perry et al.'s controlled study
found both less-secure code and greater confidence for its particular assistant and
tasks. That supports independent security review of generated examples, but the
contrary result from Sandoval et al. shows why the recommendation should be risk-based,
not an assumption that all generated material is worse than human-authored material.
The evidence evaluates code assistance, not documentation review directly.

## Detection and validation

Detection should follow the information flow from source to rendered publication rather
than rely on one repository check.

1. **Inventory inputs and destinations before generation.** Record which repositories,
   branches, issues, logs, commands, and external sources the agent can read; classify
   their audiences; identify the exact target repository and rendered audience. A
   source-to-destination matrix detects the structural risk that a private input is
   feeding a public artifact. It cannot decide whether a specific transformed fact is
   safe.
2. **Inspect the complete output in every material representation.** Scan the Markdown
   source, generated assets, diffs, rendered pages, link targets, metadata, and any
   publication bundle. Examine newly generated files and relevant history, not merely
   the visible prose. This can find outputs hidden from a normal page view, but it does
   not prove that remote caches or external mirrors are clean.
3. **Layer credential detection.** Use provider patterns, non-provider patterns,
   organization-specific custom patterns, entropy or high-risk-field heuristics, and
   review of scanner bypasses and timeouts. GitHub exposes more than 500 supported
   patterns and permits custom patterns
   ([supported patterns, accessed 2026-09-09](https://docs.github.com/en/code-security/reference/secret-security/supported-secret-scanning-patterns)).
   This is meaningful coverage, countering the claim that ordinary scanning is useless;
   the same documentation says password push protection and validity checks have limited
   support, so a clean result remains bounded.
4. **Layer PII and re-identification review.** Run structured and unstructured PII
   detection, then have a privacy-aware reviewer test combinations of roles, dates,
   locations, links, quotes, and metadata using the destination audience's available
   knowledge. Presidio's explicit no-guarantee warning is the boundary: automated
   recognition is a triage layer, not certification.
5. **Perform semantic operational-security review.** Ask what a previously uninformed
   reader learns about identities, trust boundaries, exposed services, administrative
   paths, control gaps, timing, and recovery. Compare that gain with the document's user
   need. This is judgment-intensive and may over-withhold useful architecture; the
   reviewer should record the concrete harm model rather than label all operational
   detail secret.
6. **Divert vulnerability-like material before ordinary review.** A failing security
   test, unpatched weakness, proof of concept, or sensitive patch explanation should go
   to the designated private channel and disclosure owner. Reproduction and publication
   timing require domain expertise and coordination. FIRST says a PSIRT should validate
   remediation and define review and approval for release-note disclosure
   ([PSIRT Framework 1.1, services 3.3 and 5.3](https://www.first.org/standards/frameworks/psirts/psirt_services_framework_v1.1)).
   A keyword detector can route candidates but cannot determine exploitability or the
   public interest in disclosure.
7. **Extract and test executable guidance.** Parse fenced blocks and commands into an
   isolated, least-privileged test environment; run relevant linters and security
   analyzers; review authentication, authorization, cryptography, TLS, logging, network
   exposure, destructive effects, and rollback. Test both documented success and failure
   paths. NIST recommends reviewing generated code for risks and evaluating outputs in
   real-world scenarios
   ([NIST AI 600-1, actions MS-2.6-004 and MS-4.2-002](https://doi.org/10.6028/NIST.AI.600-1)).
   A sandbox test cannot establish safety in every target environment, and intentionally
   unsafe teaching examples need unmistakable scope and warnings.

## Mitigations

**Minimize before prompting.** Give the agent only the repositories, paths, tool output,
fields, and time window needed for the documentation task. Filter logs and command output
at collection, not only after generation. This implements least privilege and NIST's
recommendation to minimize PII. The trade-off is evidence loss: overly narrow context can
make documentation incomplete or wrong, so access minimization needs a task-specific
evidence plan and an escalation path rather than arbitrary truncation.

**Bind source classification to destination.** Attach audience or disclosure labels to
source material and require an explicit rule for a fact moving to a broader audience.
Treat “public,” “internal,” “restricted,” and “under coordinated disclosure” as
information-flow states, not prose hints the model may ignore. Refuse publication when
the destination is unknown. Classification can be stale or wrong, so ownership,
periodic review, and a conservative route for ambiguous material remain necessary.

**Generate safe artifacts by construction.** Prefer purpose-built synthetic fixtures and
clearly impossible placeholders such as `${SERVICE_HOST}` and `${ACCESS_TOKEN}` over
copied production values. Do not ask a model to invent realistic credentials or personal
records. Store secrets outside tracked files and document retrieval interfaces, not
values. Remove screenshots and pasted terminal output unless needed; when needed,
recreate them from sanitized fixtures. This reduces realistic debugging fidelity and can
hide format-specific bugs, so tests may need a private environment using ephemeral
values that never enter the publication artifact.

**Use multi-layer, destination-aware scanning as a gate.** Combine credential scanners,
custom organizational patterns, PII recognition, rendered-output inspection, and a
semantic review checklist. Measure false negatives with seeded synthetic canaries and
false positives through reviewed dry runs. NIST calls for detecting PII in generated
output and monitoring generated content for privacy risks
([NIST AI 600-1, actions MP-4.1-001 and MP-4.1-009](https://doi.org/10.6028/NIST.AI.600-1)).
No test set proves detection of novel secret formats or contextual disclosures, and
canaries must themselves be unmistakably non-functional.

**Separate vulnerability documentation from ordinary documentation.** Route candidates
to a private advisory or PSIRT process, preserve reporter confidentiality, agree what may
be shared with whom, validate remediation, and approve public release notes at the
coordinated time. CERT/CC emphasizes balancing public notice with deployers' ability to
remediate; FIRST calls for secure channels and embargo handling. The trade-off is that
indefinite secrecy can also harm defenders. A documented disclosure owner and escalation
timeline are preferable to either immediate automated publication or automatic silence.
CERT/CC's receiver policy template makes the trade-off explicit: disclosure decisions
should balance public awareness with vendors' time to respond effectively
([CERT/CC receiver policy template](https://certcc.github.io/CERT-Guide-to-CVD/reference/policy_templates/receivers/)).

**Treat examples as software plus instruction.** Generate secure defaults, state target
versions and threat-model assumptions, avoid unexplained “temporary” bypasses, test
commands, and security-review the surrounding prose. NIST's SSDF recommends integrating
security practices throughout the lifecycle rather than relying on an ordinary
development model to supply them
([NIST SP 800-218](https://doi.org/10.6028/NIST.SP.800-218)). Such review costs time and
cannot eliminate environment-specific misuse; risk should determine depth.

**Prepare for disclosure response.** On suspected exposure, stop further publication,
preserve evidence in a restricted channel, revoke or rotate credentials, assess affected
people and systems, follow the applicable privacy or vulnerability process, and only then
consider coordinated history cleanup. Do not paste the suspected material into another
external scanner or issue while investigating it. GitHub's history-removal guidance
shows why deleting a line is not adequate incident response.

## Limits and open questions

- No end-to-end study was found that gives autonomous documentation agents the realistic
  mix of repository access, logs, issue context, rendering, and Git publication, then
  measures secret, privacy, vulnerability, and unsafe-guidance failures. The taxonomy is
  consequently supported by adjacent evidence and information-flow analysis, not by a
  defensible prevalence estimate.
- Model-memorization studies demonstrate possibility under particular models and attack
  procedures. They do not measure current proprietary agents, retrieval configurations,
  retention settings, or routine documentation prompts. The report therefore ranks
  supplied-context leakage as more immediate without claiming it is more frequent.
- The unsafe-guidance evidence conflicts by setting. Perry et al. found worse security
  and higher confidence across several security tasks; Sandoval et al. found little
  effect in one bounded C task. Later systems, different prompts, expert users, and
  security-aware toolchains may produce different outcomes.
- NIST SP 800-122 is US federal guidance from 2010 and ICO anonymisation guidance is
  jurisdiction-specific. They are used for technical concepts—linkability, context, and
  re-identification—not as current legal advice for every reader.
- FIRST, CERT/CC, NIST, OWASP, Microsoft, GitHub, and Git describe practices and tool
  boundaries; most do not quantify documentation-agent incidents. Vendor documentation
  is authoritative about stated product behavior but is not independent evidence of its
  real-world detection rate.
- Security transparency has countervailing value. Architecture, hardening rationale,
  and timely post-remediation advisories help operators and defenders. The correct test
  is not “does this mention security?” but “is this audience, detail, and timing justified
  after considering harm and remediation?” Evidence does not support security through
  obscurity as a blanket mitigation.
- It remains open how to benchmark semantic operational-detail leakage without encoding
  a sensitive infrastructure map in the benchmark itself, and how to test linkability
  against realistic external knowledge without collecting more personal data.
- This work did not verify the configuration or effectiveness of any control in the
  Buzz repositories. The local documents establish a public destination and a binding
  rule at the inspected revision; they explicitly do not establish enforcement or
  compliance.

## Practical review checks

- Candidate check: identify the exact publication destination and its audience before
  allowing the agent to read any narrower-audience source.
- Candidate check: list every repository, issue class, log, command, and external service
  used as evidence; confirm each was necessary and permitted for this output.
- Candidate check: reject real credentials and production-derived examples in favor of
  impossible placeholders or synthetic fixtures; never “mask” a live value and retain a
  usable fragment.
- Candidate check: scan Markdown source, generated assets, rendered pages, link targets,
  the intended commit, and relevant history with provider, generic, custom, and PII
  detectors; record timeouts, exclusions, and bypasses.
- Candidate check: manually test whether names removed from the document can be recovered
  from combined roles, dates, locations, quotes, links, filenames, or public sources.
- Candidate check: ask what new operational capability an uninformed public reader gains
  from the document's combined facts, not only whether each sentence was already known.
- Candidate check: route any unremediated weakness, proof of concept, sensitive failing
  test, or security patch explanation to the private disclosure owner before an ordinary
  documentation review begins.
- Candidate check: extract every executable command and code block; test it in an
  isolated least-privileged environment and review security-sensitive defaults, failure
  paths, prerequisites, cleanup, and version assumptions.
- Candidate check: distinguish deliberately unsafe teaching examples visually and
  textually, state why they are unsafe, and keep them non-deployable by default.
- Candidate check: require separate factual/editorial and security/privacy approval for
  high-impact outputs; neither approval substitutes for the other.
- Candidate check: block publication when a detector fails, skips input, times out, or
  has an unexplained finding; a green result must name its scanned scope.
- Candidate check: rehearse a private response path that prioritizes credential rotation,
  affected-party assessment, coordinated disclosure, and residual-copy analysis rather
  than assuming a follow-up commit erases exposure.

## References

- [Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile](https://doi.org/10.6028/NIST.AI.600-1) — NIST AI 600-1, July 2024; GAI privacy leakage, memorization and inference risks, output monitoring, PII detection, generated-code review, and real-world evaluation.
- [Guide to Protecting the Confidentiality of Personally Identifiable Information](https://doi.org/10.6028/NIST.SP.800-122) — NIST SP 800-122, April 2010; broad PII definition, linkability, context, impact, and data minimization.
- [Secure Software Development Framework (SSDF) Version 1.1](https://doi.org/10.6028/NIST.SP.800-218) — NIST SP 800-218, February 2022; integrating secure practices across the software lifecycle and applying least privilege to development resources.
- [LLM02:2025 Sensitive Information Disclosure](https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/) — OWASP GenAI Security Project, 2025 edition; sensitive output, application-context exposure, sanitization, least privilege, and source restriction.
- [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) — OWASP Cheat Sheet Series, accessed 2026-09-09; credential, PII, internal-network, path, and commercial-information handling boundaries for log evidence.
- [Secret scanning detection scope](https://docs.github.com/en/code-security/reference/secret-security/secret-scanning-scope) — GitHub Docs, accessed 2026-09-09; same-file pair requirements, supported-pattern boundary, legacy-token, size, and timeout limitations.
- [Supported secret scanning patterns](https://docs.github.com/en/code-security/reference/secret-security/supported-secret-scanning-patterns) — GitHub Docs, accessed 2026-09-09; provider, generic, password, push-protection, and validity-check coverage as then documented.
- [Removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository) — GitHub Docs, accessed 2026-09-09; rotation-first response and residual copies in clones, forks, caches, and pull-request references.
- [Code scanning with CodeQL](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-code-scanning) — GitHub Docs, accessed 2026-09-09; supported source-language analysis and incomplete-analysis boundary.
- [gitignore Documentation](https://git-scm.com/docs/gitignore) — Git project documentation, last updated in version 2.55.0 and accessed 2026-09-09; ignored-file purpose and the fact that tracked files are unaffected.
- [Microsoft Presidio](https://microsoft.github.io/presidio/) — Microsoft open-source project documentation, accessed 2026-09-09; automated PII detection capability and explicit no-completeness guarantee.
- [How do we ensure anonymisation is effective?](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-sharing/anonymisation/how-do-we-ensure-anonymisation-is-effective/) — UK Information Commissioner's Office, accessed 2026-09-09; motivated-intruder, linkability, and pseudonymization boundary.
- [PSIRT Services Framework 1.1](https://www.first.org/standards/frameworks/psirts/psirt_services_framework_v1.1) — FIRST, version 1.1, accessed 2026-09-09; secure vulnerability-information sharing, embargoes, validation, disclosure review, and remedy coordination.
- [The CERT Guide to Coordinated Vulnerability Disclosure](https://certcc.github.io/CERT-Guide-to-CVD/) — CERT Coordination Center/Carnegie Mellon SEI, evolving web edition accessed 2026-09-09, based on CMU/SEI-2017-SR-022; adversarial advantage, stakeholders, timing, and coordinated disclosure.
- [Receivers: vulnerability disclosure policy template](https://certcc.github.io/CERT-Guide-to-CVD/reference/policy_templates/receivers/) — CERT Coordination Center/Carnegie Mellon SEI, accessed 2026-09-09; factors and trade-offs for public disclosure timing.
- [Extracting Training Data from Large Language Models](https://www.usenix.org/conference/usenixsecurity21/presentation/carlini-extracting) — Carlini et al., USENIX Security 2021; extraction of memorized GPT-2 training examples and bounded evidence for latent disclosure.
- [Do Users Write More Insecure Code with AI Assistants?](https://arxiv.org/abs/2211.03622) — Perry, Srivastava, Kumar, and Boneh, full version of the ACM CCS 2023 paper (arXiv v3, 2023); controlled evidence of less-secure code and greater confidence with one Codex-based assistant.
- [Lost at C: A User Study on the Security Implications of Large Language Model Code Assistants](https://www.usenix.org/conference/usenixsecurity23/presentation/sandoval) — Sandoval et al., USENIX Security 2023; counterevidence finding a small security effect in one bounded C task with 58 student participants.
- [`launchpad/AGENTS.md` §8 at inspected revision](../../../AGENTS.md#8-security) — launchpad-26/buzz, commit `81b5a1d059ea897968c4fe412497a351892d4598`, inspected 2026-09-09; local public-repository and secret-disclosure rule.
- [`launchpad/SECURITY-POSTURE.md` at inspected revision](../../../SECURITY-POSTURE.md) — launchpad-26/buzz, commit `81b5a1d059ea897968c4fe412497a351892d4598`, inspected 2026-09-09; local distinction between a binding public-repository rule and enforcement, and the risk of publishing a current security-gap map.
