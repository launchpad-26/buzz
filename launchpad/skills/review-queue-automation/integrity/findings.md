# RQA implementation-integrity findings

This register records the initial T1, T2, T3 and architecture-audit findings for
Feature [#2310](https://github.com/launchpad-26/buzz/issues/2310), followed by their
final dispositions. Evidence is append-only within a finding: remediation does not
replace the observation that caused the work.

## Run identity

| Field | Value |
|---|---|
| Detection base (T1–T3 and the architecture audit ran here) | `4d64f0c4476ed6ab907b69809b96d5c4c2653df6` |
| Remediation base (this branch) | `1f56a303428b40939c70a45e4ac65b1554f5854b`, the head of PR #2315 |
| Baseline RQA suite, detection base | `python3 -m pytest tests -q` — `1441 passed in 19.08s` on Python 3.14.6 / pytest 8.3.4 |
| Baseline RQA suite, remediation base | `python3 -m pytest tests -q` — `1486 passed in 58.30s` on Python 3.14.6 / pytest 8.3.4 |
| Final verification commit | recorded in [Final verification](#final-verification) below |

**The two bases differ, and five findings changed because of it.** Detection ran on a
local #2299/#2300 anchoring chain that predated the published predecessor stack.
Remediation is based on PR #2315's head, which carries PR #2276 (Feature #2188),
PR #2302 (Feature #2189) and PR #2291 (#2273) beneath the same anchoring work, and
whose own ancestry already contains #2274's fix. Moving
to the real base falsified part of the initial triage: A-083/A-084 and C-010 were
classified dead against a tree where nothing reached them, and C-001, C-002 and C-011
were deferred to owners who had, by then, already done the work. Those rows are corrected
below rather than quietly dropped — a finding that does not survive its own base change
is evidence about the detection, not only about the code. None of the predecessors is
on `launchpad` yet, so this branch targets PR #2315 and lands behind it.

## Preserved baseline evidence

The pre-remediation outputs are versioned beside this register, unchanged but for one
masked value:

- `baseline-2310-t1.txt` — T1: 82 findings;
- `baseline-2310-t2.txt` — T2: 3 findings;
- `baseline-2310-t3.txt` — T3: 19 cases, 17 killed, 2 survived, 0 errors. One literal
  in this file is masked and a header note at the top says so: B-INV-003's guard asserts
  that a fabricated canary token does not escape the authority frame, so the failure it
  quotes contains that token in full. It is a fixture, not a credential, but it matches
  gitleaks' `github-oauth` rule and this repository fails a PR on any match;
- `baseline-2310-reference-register.md` — A-001 through A-085 with source and
  evidence;
- `baseline-2310-invariant-register.md` — the initial invariant inventory and the
  two surviving-guard investigations;
- `baseline-2310-architecture-register.md` — C-001 through C-013 with evidence and
  recommended disposition.

## Final disposition map

| finding | source | check | evidence | classification | disposition | action | verification | reason |
|---|---|---|---|---|---|---|---|---|
| A-003–005, A-012, A-033–036, A-039, A-041–042, A-044–045, A-048–049, A-055, A-059, A-067–068, A-076, A-080–082 | Baseline reference register | T1 | Each has a production annotation outside its defining part. | detector false positive | detector-fixed | Count evidenced annotations as supported production references; retain the rule excluding references internal to the exporting part. | Fixture proves annotation use clears T1 while same-part use does not; final T1 guard passes. | #2311 explicitly requires supported annotations to count; treating them as import-only contradicted the specification. |
| A-050 | `rqa.protocol.PROBE_MARKER` | T1 | Supply probing used a duplicate local `"PROBE"` constant. | genuine unwired public definition / duplicate source of truth | wired | Inject the canonical protocol marker into `SubprocessHarnessProber`; remove the supply duplicate. | Probe and reference-integrity tests pass; final T1 no longer reports the symbol. | E-19 owns the marker contract and production probing must consume it. |
| A-085 | `rqa.harness.adapters.BUILTIN_HARNESSES` | T2 | A module-level snapshot of `builtin_harnesses()` with no consumer anywhere. | dead definition | removed | Remove the snapshot; the function it froze remains. | Final T2 guard reports zero findings; harness tests pass. | A frozen copy of a live function's result has no caller and cannot acquire one without re-introducing staleness. |
| A-083–A-084 | `rqa.cli.exitcodes.AUTH`, `.NETWORK` | T2 | **Corrected on the remediation base.** Both are emitted: `tick` maps an `unauthenticated` inventory outage to `3` and any other unreachable one to `2` (`rqa/cli/main.py`). | not a defect — detection-base artefact | retained | Restore both constants and the five-code contract; document in SKILL.md the path that reaches `2` and `3`. | `tests/test_rqa_cli_regressions.py::test_tick_reports_inventory_outage_and_authentication_failure` pins both codes and passes. | The detection base lacked the conformance work that wires them. Removing a public exit code that automation can observe, on evidence from a tree that does not contain its caller, would have been the more expensive error. |
| A-086 | `rqa.authority.grant` | T1 | Found only on the remediation base: tested by 5 references, with no production use outside `rqa.authority`. Production reaches the gate through an injected `Gate.grant`. | deliberate public-surface exception | justified-exception | Record an exact-symbol entry with its architecture reason; do not manufacture a production caller for it. | Final T1 guard passes with 59 current, reasoned entries and no stale ones. | It is E-04 itself (`EDGES["E-04"]`, CONTRACTS.md §9) — the entry point published for a caller that does not hold the managed-repository set, constructing the same `Gate` the composition root injects. Deleting the architecture's own named edge to satisfy an internal-wiring heuristic would be the defect. |
| Remaining A-001–A-082 (58 exact symbols) | `T1_JUSTIFIED_EXCEPTIONS` | T1 | These are architecture-mandated public part surfaces used by external/alternate composition callers or diagnostic tooling, while implementation use stays inside the owning part. | deliberate public-surface exception | justified-exception | Retain exact symbol entries with non-empty architecture-specific reasons; stale entries fail the guard. | Final T1 guard passes with exactly 58 current, reasoned entries. | Removing the published P-01–P-13 surface would break the accepted architecture merely to satisfy an internal-wiring heuristic. |
| B-INV-001 / B-001 | Remediation ordering | T3 | Mutation reading head protection before grant verification initially survived. | ineffective invariant guard | fixed | Add an observable head-access trap to the real remediation path test. | Mutation now kills the named test. | The prior assertion proved eventual denial but not grant-before-head ordering. |
| B-INV-010 / B-002 | Spend sole writer | T3 | A positional `append(..., "spend", ...)` outside supply initially evaded a keyword-only regex. | ineffective invariant guard | fixed | Replace phrase matching with bounded AST inspection recognising positional and keyword `kind`. | Mutation now kills the named test. | The invariant concerns calls, so structural inspection is the appropriate guard. |
| Other initial B-INV cases | `integrity/invariants.json` | T3 | All 17 initial mutations killed their named guard. | effective invariant protection | fixed | Retain as the permanent versioned mutation inventory and standalone runner. | Final runner result recorded below. | Each mutation is bounded to the named must-never/sole-writer rule. |
| C-001 | Managed-repository configuration | Architecture audit | **Resolved on the remediation base.** `rqa/cli/main.py` reads the durable swept set from `<state_dir>/repos.json` and `build_composition` injects it into `Gate(repos=...)` (`rqa/cli/composition.py:123`, `:340`). | already fixed by its named owner | retained | None. #2274 closed COMPLETED on 2026-09-16 and its fix is in this branch's ancestry. | Discovery path and injection located by search at the remediation base; `_configured_repos` and `AuthorityClient(repos=...)` both present. | Deferring to #2274 was correct; the detection base simply predated its fix. |
| C-002 | Repository identity | Architecture audit | **Substantially resolved on the remediation base** at the operator boundary: `_repo_slug` (`rqa/cli/main.py:95`) accepts only `owner/repo` and rejects anything path-shaped, so a checkout path can no longer enter as a repository identity. | already fixed by its named owner | retained | None here. | The validator and its rejection of path-shaped values were read at the remediation base. **Not verified:** whether every internal consumer downstream of that boundary keeps the two senses apart — the check was of the entry point, not of the whole data flow. | The incoherence the audit described was an unguarded shared string; the boundary now guards it. Auditing every downstream consumer is #2274's settled ground, not bounded integrity cleanup. |
| C-003 | Policy blocking configuration | Architecture audit | `severities` and `corroboration` were accepted but had no behavioural consumer. | ineffective configuration | removed | Remove both keys from contract, validator, examples and current docs; reject them as unknown. | Policy tests prove obsolete keys fail and fixed judgement corroboration remains green. | Keeping inert controls misleads operators; wiring them would contradict fixed protocol rules. |
| C-004 | Stable hashing | Architecture audit | GitHub writes duplicated canonical intake hashing behind an obsolete import fallback. | obsolete duplicate implementation | removed | Import the canonical `stable_hash` directly and remove the fallback. | GitHub write and identity tests pass. | The supported tree always contains the canonical owner. |
| C-005 | Package surfaces | Architecture audit / T3 | Tests accepted historical partial-wave module/export sets. | ineffective invariant guard | fixed | Require the assembled final surfaces and add deletion/export mutations. | Final mutation results recorded below. | Earlier assembly waves are not valid current package states. |
| C-006 | External anchor recovery | Architecture audit | Anchors are published externally but no supported path fetches and compares them after local loss. | substantial incomplete behaviour | separate-work | Retain as predecessor gap under #2300; do not fabricate retrieval semantics here. | #2300 is named as the responsible predecessor. | Remote destination and fail-closed recovery behaviour require architecture/product decisions. |
| C-007 | Record integrity docs | Architecture audit | Current diagrams/docs still described superseded HMAC/keychain behaviour. | obsolete competing documentation | fixed | Align current architecture with ADR-0066; preserve ADR-0063 only as explicitly superseded history. | Architecture/requirements validators and focused searches pass. | Normative documents must describe the implemented keyless chain and external anchor model. |
| C-008 | Anchor command inventory | Architecture audit / T3 | Shipped `anchor` was missing from E-17, contracts and command documentation. | stale interface contract | fixed | Add `anchor` to E-17/contracts/docs and guard parser-to-contract parity. | Focused CLI/edge test and mutation pass. | One authoritative command set prevents interface drift. |
| C-009 | Wave-era descriptions/boundaries | Architecture audit | Current files claimed landed modules did not exist and disagreed about the lifecycle-to-record boundary. | obsolete documentation | fixed | Remove assembly-era claims and state one boundary rule. The remediation base had already chosen the boundary by exporting `SQLiteRecordReader` and `append_trace` as `rqa.record` surface, so the documents are aligned to that choice rather than to the detection base's private-submodule reading: P-02 imports P-12's front door for exactly those two names. | Focused searches and architecture validator pass; `rqa/lifecycle`, P-02 §1 and P-12 §1 now state the same rule. | The assembled implementation, not a historical wave, defines the current boundary — and the base had already settled which of the register's three options was taken. |
| C-010 | CLI codes 2 and 3 | Architecture audit / T2 | **Withdrawn on the remediation base.** `rqa/cli/main.py` classifies inventory outages into `AUTH` and `NETWORK`, and a regression test pins both. | not a defect — detection-base artefact | retained | None. The five-code contract in architecture.md §11 stands and SKILL.md now names the reaching path. | `tests/test_rqa_cli_regressions.py` passes with codes `2` and `3` observed. | See A-083–A-084. The original reasoning — do not invent failure classifications — remains right; it simply did not apply, because the classification already existed. |
| C-011 | Trace persistence | Architecture audit | **Resolved on the remediation base.** `append_trace` has four production callers — `lifecycle/admit.py`, `lifecycle/rest.py` and `lifecycle/steps.py` — and is part of `rqa.record`'s re-export list. | already fixed by its named owner | retained | None. #2273's fix is `16b619ec7 feat(rqa): restore dispatch milestone tracing`, an ancestor of this branch through PR #2291 — which is still open, so #2273 stays open too. | Production callers located by search; the named commit verified as an ancestor of the remediation base. | Deferring to #2273 was correct; #2273 had simply already done the work by the time this branch reached its real base. |
| C-012 | GitHub test helpers | Architecture audit | Runner-neutral network/credential helpers intentionally live outside pytest-only support. | deliberate test-support surface | justified-exception | Retain the helper; no synthetic runtime caller. | Credential/network safety tests pass in the supported suite. | Accepted P-09 architecture requires runner-neutral safety evidence. |
| C-013 | Historical conformance report | Architecture audit | F-1/F-2 were presented as current after their code/ADR resolutions. | stale historical-status documentation | fixed | Preserve pinned evidence but mark it resolved/superseded and qualify downstream conclusions by commit. | Documentation review and validators pass. | Historical evidence must not masquerade as the current remediation map. |

Allowed final dispositions are `wired`, `fixed`, `removed`, `detector-fixed`,
`justified-exception`, `retained` and `separate-work`. A `separate-work` row names its
issue and states whether it blocks any Feature #2310 acceptance criterion. A `retained`
row is one where the code was left exactly as it stands, either because the finding did
not survive the move to the remediation base or because its named owner had already
fixed it; the row says which.

## Final verification

Run on the remediation base at the full branch applied to the remediation base, Python 3.14.6 / pytest 8.3.4,
macOS 24.6.0. The last commit changing code or tests is `2b7357c0d`; the two after it
are documentation only.

**T1 and T2 — reference integrity, collected by the RQA pytest lane.**

```
$ python3 -m pytest tests/test_rqa_reference_integrity.py -q
6 passed in 2.92s
```

Zero unexplained findings on either check. T1 carries 59 exact-symbol justified
exceptions, every one with a non-empty architecture-specific reason, and the same guard
fails on a stale entry — an exception that no longer matches a finding is an error, so
the list cannot outlive what it explains. T2 carries none.

**T3 — invariant mutation runner, a standalone script because it runs pytest itself.**

```
$ python3 integrity/run_mutations.py
totals: killed=22 survived=0 errors=0
```

Every case exports the source from one Git commit into a temporary directory and runs
there; neither the tests nor the mutations touch the operator checkout. The inventory
grew from 19 cases to 22: B-INV-020 and B-INV-021 delete a module outright and
B-INV-022 drops a name from `rqa.intake.__all__`, which are the mutations the
two-legitimate-states surface guards used to survive (C-005).

**Whole suite.**

```
$ python3 -m pytest tests -q
1504 passed in 71.01s (0:01:11)
```

Against `1486 passed` on the remediation base: 18 net new tests.

**Per-commit.** Every commit on this branch was exported and run in isolation:

| commit | subject | `python3 -m pytest tests -q` |
|---|---|---|
| `ef121e13a` | test(rqa): detect tested exports without production wiring | 2 failed, 1488 passed |
| `92c780f23` | test(rqa): detect unreferenced public definitions | 3 failed, 1488 passed |
| `b0852ffaa` | test(rqa): add invariant mutation runner | 3 failed, 1493 passed |
| `1bcdf2ec9` | test(rqa): make invariant mutations fail closed | 3 failed, 1493 passed |
| `bf346edde` | refactor(rqa): remove the duplicate stable-hash formula | 3 failed, 1493 passed |
| `833cad522` | fix(rqa): remediate reference integrity findings | 1497 passed |
| `70c4571f5` | fix(rqa): remove inert blocking policy controls | 1498 passed |
| `07edfc6c7` | fix(rqa): publish anchor in the E-17 command contract | 1499 passed |
| `8107e44b2` | docs(rqa): describe the assembled, anchored system | 1499 passed |
| `2b7357c0d` | test(rqa): require the final assembled package surfaces | 1504 passed |
| `cb7263c75` | docs(rqa): mark the superseded conformance findings | 1504 passed |
| `93e8d7959` | docs(rqa): record the integrity baselines and their disposition | 1504 passed |

Each commit was exported with `git archive` into a temporary directory and the suite
run there, so the result is of that commit's tree alone. The last row's hash is the
register commit as it stood when this table was measured; writing this section into
that commit necessarily rewrites its hash, and its content is documentation, so the
`1504 passed` above is the figure the head carries.

The first five commits are red where they land, and that is deliberate rather than
overlooked: T1, T2 and T3 are introduced with their findings outstanding, so the commit
that adds a detector is the commit that proves it detects something. `833cad522` takes
the branch green by remediating them and it stays green through the head. A reviewer
walking the history sees each finding before its fix; a bisect across this branch should
start at `833cad522`.

**Residual risk, stated rather than closed.**

- One finding — C-006, external anchor recovery — remains `separate-work` under #2300,
  which is open and is the predecessor this branch is stacked on. Anchors are published
  but no supported path fetches and compares them after local loss; `rqa/record/anchor.py`
  exposes publication only. Remote destination and fail-closed recovery semantics are
  architecture decisions, not bounded cleanup. No Feature #2310 acceptance criterion
  depends on it.
- C-011's fix (#2273) and C-001/C-002's fix (#2274) are in this branch's ancestry but
  not on `launchpad`: #2274 is closed, while #2273's PR #2291 is still open. Their
  `retained` rows are true of this stack, not of the trunk.
- C-002 is marked substantially resolved on the strength of its entry-point validator.
  Every downstream consumer of a repository identity was not audited.
- The T1 exception list is the one place a genuine defect could hide behind a
  plausible sentence, and no test can tell a good reason from a fluent one. What is
  mechanised is narrower: entries are exact symbols, reasons must be non-empty, and a
  stale entry fails. The reasons themselves are a review judgement, and 59 of them are
  asking for it.
- This branch is based on PR #2315, which is itself based on PR #2302. It cannot merge
  to `launchpad` before its predecessors, and the counts above are true of that stack,
  not of `launchpad` today.
