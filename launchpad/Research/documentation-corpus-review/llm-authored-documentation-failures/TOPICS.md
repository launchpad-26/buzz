# Research topics and model assignments

The 20 questions below define the research program. Wording is authoritative:
workers should preserve the exact question in their report metadata and scope
their research within it.

## Initial assignment rationale

Codex handles the eight topics with the greatest code, tool, security, and
validation depth. Claude handles the twelve topics dominated by conceptual
analysis, reader cognition, editorial systems, and synthesis. This split is
resource routing, not a quality ranking. There is no second-model reviewer.

The assignments shown below are the initial allocation. Provider limits
interrupted the remaining Claude work; at the user's direction, Codex completed
topics 14, 15, 16, and 18. Each report's metadata and the progress register
record the actual primary model.

## Questions

1. **Context selection and evidence sufficiency** — **Claude**

   How do documentation agents select incomplete, irrelevant, or misleading repository context, and how can we determine whether the evidence assembled was sufficient for the documentation task?

2. **Tool-mediated evidence failures** — **Codex**

   How do search failures, truncated output, inaccessible files, ignored command errors, unsuitable tools, and lost execution context affect the accuracy of agent-authored documentation?

3. **Temporal and revision coherence** — **Claude**

   How do agents combine evidence from incompatible commits, branches, releases, dependencies, or time periods, and how should generated documentation remain coherent as the underlying system changes?

4. **Technical hallucination and unsupported inference** — **Codex**

   What kinds of technical facts do documentation agents invent or infer without sufficient support, why do these failures occur, and which verification methods detect them?

5. **Claim provenance and circular evidence** — **Claude**

   How do fabricated, misapplied, mutable, or circular citations allow unsupported claims to appear evidence-backed?

6. **Code-to-document semantic fidelity** — **Codex**

   How accurately do agents reconstruct behavior, control flow, data flow, architecture, dependencies, defaults, error handling, and trust boundaries from source code?

7. **Omissions and false completeness** — **Claude**

   Why do agents omit prerequisites, constraints, failure modes, edge cases, negative behavior, or undocumented surfaces while producing documentation that appears comprehensive?

8. **Executable procedures, examples, and configuration** — **Codex**

   How and why do agents generate commands, code samples, procedures, and configuration that are plausible but incorrect, incomplete, non-reproducible, destructive, insecure, or incompatible with the target environment?

9. **Normative distortion** — **Claude**

   How do agents invent obligations, weaken requirements, strengthen recommendations, or confuse policy, design intent, implementation, and observed behavior?

10. **Transformation and summarization fidelity** — **Claude**

    What information is lost, altered, generalized, falsely reconciled, or homogenized when agents summarize, rewrite, split, merge, migrate, or restructure technical documentation?

11. **Reader and task fitness** — **Claude**

    Why does agent-authored documentation become generic, verbose, incorrectly pitched, or disconnected from the decisions and tasks its intended readers need to complete?

12. **Security, privacy, and disclosure failures** — **Codex**

    How can documentation agents expose secrets, personal information, private operational details, undisclosed vulnerabilities, or unsafe security guidance, and why might ordinary controls miss these failures?

13. **Epistemic calibration and deceptive fluency** — **Claude**

    Why do agents express uncertain conclusions with unjustified confidence, and how do polished language and formatting make substantive defects harder for readers and reviewers to detect?

14. **Cross-document consistency and terminology drift** — **Claude**

    How do repeated agent edits produce contradictory claims, inconsistent terminology, incompatible instructions, and divergent mental models across a documentation corpus?

15. **Error propagation and false consensus** — **Claude**

    How do unsupported claims spread through summaries, indexes, runbooks, architecture documents, and later agent context until repetition appears to constitute confirmation?

16. **Coverage inflation** — **Claude**

    How can large quantities of generated documentation create a false impression of corpus completeness while important components, workflows, decisions, or failure conditions remain undocumented?

17. **Adversarial context, prompt injection, and source poisoning** — **Codex**

    How can malicious or strategically written code comments, issues, documentation, tool output, or external sources manipulate an agent's evidence selection, reasoning, or published content?

18. **Human review and automation bias** — **Claude**

    Why do reviewers over-trust agent-authored documentation, which conventional review practices fail against it, and what review conditions improve detection?

19. **Automated detection and validation** — **Codex**

    Which failure classes can be detected reliably through schemas, repository analysis, executable examples, claim-evidence checks, consistency analysis, static validation, or model-assisted review—and which still require human judgment?

20. **Evaluation, provenance, and accountability** — **Codex**

    How should agent-authored documentation record its source selection, tool use, inferences, uncertainty, model contribution, and human review, and how should its quality be measured without creating misleading aggregate assurance?
