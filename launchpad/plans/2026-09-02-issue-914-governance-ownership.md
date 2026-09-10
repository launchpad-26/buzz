# Issue #914 — governance/ownership.md

ALREADY TRUE: `launchpad/docs/corpus/` holds 205 validated nodes on `origin/launchpad` at `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`, including `corpus-agents` and `corpus-template-policy`. `launchpad/docs/corpus/governance/` does not exist — this node creates the directory. No merged corpus node covers `launchpad/AGENTS.md` §3's upstream/fork ownership boundary (`grep -rn 'Never move or rename upstream'` over the corpus returns zero hits). Siblings #913 (`governance/maintainers.md`) and #907 (`governance/codeowners.md`) are OPEN and unmerged.

STEP 1  Gather evidence: read `launchpad/AGENTS.md` §3 in full; open every ADR it cites (`ADR-0005`, `ADR-0017`, `ADR-0043`, `ADR-0045`, `ADR-0046`, `ADR-0051`, `ADR-0053`) and confirm each says what §3 claims, including each record's `status:` line; read `launchpad/scripts/adr_boundary_check.py` and `.github/workflows/launchpad-adr-check.yml` for what is mechanically enforced; read `launchpad/scripts/security_audit_classifier.py` for the second, executable encoding of ownership. ← RUNS HERE

STEP 2  [needs 1] Verify the two known drift cases against the tree, not against prose. (a) `git ls-tree -r origin/launchpad -- desktop/src/launchpad` and `grep -rn 'desktop/src/launchpad' launchpad/*.md launchpad/decisions/*.md`; resolve the `@/` alias in `desktop/tsconfig.json` to prove `@/launchpad/settings/registry` is inside upstream's tree. (b) Diff §3's directory map against `git ls-tree origin/launchpad -- launchpad/` programmatically and record exact counts — no `head`-truncated listing, no count restated from the issue.

STEP 3  [needs 2] Write `launchpad/docs/corpus/governance/ownership.md` on the policy template: front matter (`id: governance-ownership`, `type: governance`, `status: draft`, `origin: launchpad`, audiences, provenance ledger with the revision as first FACT, `relationships` only to ids confirmed on `origin/launchpad`); body in the template's six required sections with RFC 2119 keywords, authority stated as derived from §3 and the ADRs, and the two drift cases recorded as measured facts with their filed issue numbers.

STEP 4  [needs 3] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until PASS.

STEP 5  [needs 4] Run the corpus unittest suite as the sole prior command to earn the verification stamp, then in a separate call `git add` the document and this plan and `git commit -s`. Stop at the commit — no push, no PR.

PARALLEL: none — one document, one task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must report PASS. `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report OK, run bare and unpiped as the sole command in its own call. Cross-model final review is the batch owner's, not run here.

BUDGET: small — one Markdown node, no code changes. Evidence is seven ADRs, `launchpad/AGENTS.md`, two enforcement scripts, one workflow, and two tree measurements.

OPEN: `corpus-standard-naming` MUST 3 mandates a `corpus-` prefix on every `id`; this node uses `governance-ownership` per the settled `<directory>-<stem>` convention that 179 of 229 merged content nodes already follow, and the conflict is tracked at #2029. The node records the tension rather than resolving it. `ADR-0046` is `status: Proposed`, not Accepted, while §3 introduces its exception list as "all accepted knowingly" — reported as a measured fact, not fixed here.

LEFT OUT: No edit to `launchpad/AGENTS.md` §3, to any ADR, or to `desktop/src/launchpad/` — the two drift cases are already filed (#2033, #2037) and fixing them is not this task. No second corpus node: maintainers (#913) and CODEOWNERS (#907) are separate tasks and this node links rather than absorbs them. No new policy is invented; where the boundary has no rule, the node names the gap.
