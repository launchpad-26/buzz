# LLM-authored documentation failures

This collection investigates what goes wrong when agents author technical
documentation. It focuses especially on documentation generated from code,
repository evidence, commands, configuration, schemas, tests, logs, issues, and
tool output.

The collection is research-only. Each topic produced an independent report; the
reports do not establish project policy or change the documentation corpus contract.
The completed reports now contribute to the parent collection's
[cross-topic synthesis](../SYNTHESIS.md), whose recommended review criteria remain
proposed until adopted by a human decision.

Workers follow the [research contract](RESEARCH-CONTRACT.md), use the
[report template](REPORT-TEMPLATE.md), and take the exact assigned question from
[the topic register](TOPICS.md).

## Progress

The model column records the actual primary author. The initial allocation and
the later Codex takeover are retained in [the topic register](TOPICS.md).

| Topic | Short title | Exact report filename | Primary model | Status |
|---:|---|---|---|---|
| 1 | Context selection and evidence sufficiency | `01-context-selection-and-evidence-sufficiency.md` | Claude | Complete |
| 2 | Tool-mediated evidence failures | `02-tool-mediated-evidence-failures.md` | Codex | Complete |
| 3 | Temporal and revision coherence | `03-temporal-and-revision-coherence.md` | Claude | Complete |
| 4 | Technical hallucination and unsupported inference | `04-technical-hallucination-and-unsupported-inference.md` | Codex | Complete |
| 5 | Claim provenance and circular evidence | `05-claim-provenance-and-circular-evidence.md` | Claude | Complete |
| 6 | Code-to-document semantic fidelity | `06-code-to-document-semantic-fidelity.md` | Codex | Complete |
| 7 | Omissions and false completeness | `07-omissions-and-false-completeness.md` | Claude | Complete |
| 8 | Executable procedures, examples, and configuration | `08-executable-procedures-examples-and-configuration.md` | Codex | Complete |
| 9 | Normative distortion | `09-normative-distortion.md` | Claude | Complete |
| 10 | Transformation and summarization fidelity | `10-transformation-and-summarization-fidelity.md` | Claude | Complete |
| 11 | Reader and task fitness | `11-reader-and-task-fitness.md` | Claude | Complete |
| 12 | Security, privacy, and disclosure failures | `12-security-privacy-and-disclosure-failures.md` | Codex | Complete |
| 13 | Epistemic calibration and deceptive fluency | `13-epistemic-calibration-and-deceptive-fluency.md` | Claude | Complete |
| 14 | Cross-document consistency and terminology drift | `14-cross-document-consistency-and-terminology-drift.md` | Codex | Complete |
| 15 | Error propagation and false consensus | `15-error-propagation-and-false-consensus.md` | Codex | Complete |
| 16 | Coverage inflation | `16-coverage-inflation.md` | Codex | Complete |
| 17 | Adversarial context, prompt injection, and source poisoning | `17-adversarial-context-prompt-injection-and-source-poisoning.md` | Codex | Complete |
| 18 | Human review and automation bias | `18-human-review-and-automation-bias.md` | Codex | Complete |
| 19 | Automated detection and validation | `19-automated-detection-and-validation.md` | Codex | Complete |
| 20 | Evaluation, provenance, and accountability | `20-evaluation-provenance-and-accountability.md` | Codex | Complete |
