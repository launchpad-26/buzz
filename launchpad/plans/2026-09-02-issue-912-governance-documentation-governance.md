# Issue #912 — governance/documentation-governance.md

ALREADY TRUE at `origin/launchpad` = `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`: 205 corpus nodes are merged outside `schema/` (46 `governance`, 48 `architecture`, 69 `capabilities`, 36 `layers`, 4 `development`, 2 `agent`). `launchpad/docs/corpus/governance/` does not exist — this node creates the directory. `launchpad/docs/corpus/templates/policy.md` (`corpus-template-policy`), `AGENTS.md` (`corpus-agents`), `README.md` (`corpus-readme`), `standards/review-requirements.md` and `standards/documentation-standard.md` are all merged and are legitimate relationship targets.

STEP 1  Gather evidence: read `launchpad/docs/corpus/AGENTS.md`, `schema/node.schema.json`, `schema/README.md`, `templates/policy.md`, all 19 `standards/` filenames, `standards/naming.md`, `standards/review-requirements.md`, `standards/documentation-standard.md`, `launchpad/project-intelligence/corpus/validate.py` end to end, the corpus test suite, `.github/workflows/launchpad-corpus-validate.yml`, `Justfile`'s `corpus-validate` recipe, ADR-0028, ADR-0029, ADR-0050, ADR-0052 (which supersedes ADR-0019), and `launchpad/AGENTS.md` §3/§5/§6. Measure — never restate — the two live divergences: `naming.md` MUST 3's `corpus-` prefix against merged ids, and issues #2029/#2030. ← RUNS HERE

STEP 2  [needs 1] Establish the boundary against the three neighbouring nodes so this is one idea, not a fourth copy: `corpus-readme` owns "which file owns which rule", `corpus-agents` owns create/update/retire, `corpus-standard-review-requirements` owns the reviewer's checklist, `corpus-standard-documentation-standard` owns the shape of a `standards/` document. This node owns the **authority chain and the machine-held/review-held boundary**, plus what happens when a documented rule and merged practice diverge.

STEP 3  [needs 2] Write `launchpad/docs/corpus/governance/documentation-governance.md` to `templates/policy.md`'s six required sections: front matter (`id: governance-documentation-governance`, `type: governance`, `status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`, provenance ledger, relationships), then `# Policy: …` H1, *Scope and authority*, *MUST* (G-identifiers), *SHOULD*, *Enforcement*, *Exceptions and escalation*, *Scope and omissions*. Every FACT entry cites a file opened in STEP 1; the first entry records revision `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`.

STEP 4  [needs 3] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until it prints PASS.

STEP 5  [needs 4] Run the corpus unittest suite as the sole prior command, then commit plan + document with `git commit -s` in a separate call. Stop at the commit — no push, no PR.

PARALLEL: none — one file, one task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must print PASS. `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report OK. Cross-model review is the batch owner's, not run here.

BUDGET: small — one document, no code changes.

OPEN: This node's own `id` (`governance-documentation-governance`) violates `standards/naming.md` MUST 3, which requires a `corpus-` prefix. That divergence is settled for this batch against merged practice (157 of 158 merged content nodes omit the prefix) and tracked at #2029; the node discloses it rather than hiding it. `launchpad/AGENTS.md` §3 calls `launchpad/docs/` the "MkDocs knowledge layer" but no `mkdocs.yml` exists anywhere in the repository — recorded as a gap, not resolved here.

LEFT OUT: No restatement of `review-requirements.md`'s nine reviewer MUSTs, `documentation-standard.md`'s D1–D10, or `AGENTS.md`'s create/update/retire procedures — links only, per the policy template's P9. No new policy invented: only what exists is recorded, with the gaps named. No fixes to #2029 or #2030, and no new issues filed.
