# RQA gap analysis — dispositions: policy

Cluster `policy` (18 assessed files, per [`../clusters.md`](../clusters.md)). One entry for each
`### U-POLICY-NN` unit of [`../evidence/policy.md`](../evidence/policy.md), in that file's order.
Revision: `9267b6308714454a3b987622d90cda03a8972827` (short `9267b6308`). Paths are relative to
`launchpad/skills/review-queue-automation/`, per [`../methodology.md`](../methodology.md).

## How each entry was decided

Wave 1 established what each unit does; wave 2 fixed every requirement's gap degree and root cause
in [`../register/br.md`](../register/br.md), [`../register/fr.md`](../register/fr.md) and
[`../register/nfr.md`](../register/nfr.md). This file recommends, per unit, `keep`, `salvage`,
`rework` or `bin`, and nothing else. It designs no replacement: methodology §1 puts that outside
this analysis, so an entry says what should happen to a responsibility and why, never what to build
instead.

Three rules bound every entry below.

- **§7's justification rule.** No unit is recommended `keep` or `salvage` on the strength of
  incumbency, of test coverage, or of behaving correctly at this revision. Each `keep` and
  `salvage` names the requirement served and states what a materially simpler approach would fail
  to do. Where a materially simpler approach *would* serve the requirement, §7 makes the answer
  `rework`, and three entries below reach it that way against requirements the register marks
  `fit`.
- **The disposition follows the root cause.** Where a unit serves a requirement the register marks
  `conflicting`, the entry says where the contradicting execution is, because a `keep` against a
  `conflicting` requirement is otherwise a contradiction. Three entries do this for `RQA-NFR-018`,
  whose two forbidden executions the register locates in `dispatcher.resolve_snapshot`
  (dispatcher.py:1584-1593, dispatcher.py:1567-1571, dispatcher.py:1600, snapshot.py:117-119) —
  dispatch-cluster code that this lane does not disposition.
- **`Requirements: -` starts as a `bin` candidate.** Under the maintainer's 2026-09-06 ruling
  striking nearest-fit mappings, a behaviour no frozen requirement obliges is a candidate for
  removal, and an entry landing anywhere else must say why the estate needs a behaviour the
  specification does not oblige. Two units in this cluster carry `-` throughout (U-POLICY-07,
  U-POLICY-12) and one carries it on two of its four rows (U-POLICY-11).

## Which register rows cite this cluster's units

Several entries below turn on whether a wave-2 register row names the unit. The complete stdout of
that search, run from `launchpad/skills/review-queue-automation/`:

```
$ grep -on 'U-POLICY-[0-9][0-9]' gap/register/br.md gap/register/fr.md gap/register/nfr.md
gap/register/br.md:138:U-POLICY-09
gap/register/br.md:139:U-POLICY-02
gap/register/br.md:150:U-POLICY-08
gap/register/br.md:150:U-POLICY-09
gap/register/fr.md:196:U-POLICY-08
gap/register/fr.md:196:U-POLICY-09
gap/register/fr.md:200:U-POLICY-10
gap/register/fr.md:200:U-POLICY-13
gap/register/fr.md:201:U-POLICY-10
gap/register/fr.md:204:U-POLICY-01
gap/register/fr.md:206:U-POLICY-01
gap/register/fr.md:206:U-POLICY-06
gap/register/fr.md:207:U-POLICY-10
gap/register/fr.md:207:U-POLICY-11
gap/register/fr.md:207:U-POLICY-13
gap/register/fr.md:208:U-POLICY-10
gap/register/nfr.md:399:U-POLICY-10
gap/register/nfr.md:405:U-POLICY-01
gap/register/nfr.md:406:U-POLICY-06
gap/register/nfr.md:408:U-POLICY-10
gap/register/nfr.md:409:U-POLICY-01
gap/register/nfr.md:410:U-POLICY-10
gap/register/nfr.md:411:U-POLICY-10
gap/register/nfr.md:415:U-POLICY-02
gap/register/nfr.md:415:U-POLICY-04
gap/register/nfr.md:415:U-POLICY-12
gap/register/nfr.md:415:U-POLICY-12
gap/register/nfr.md:415:U-POLICY-12
gap/register/nfr.md:417:U-POLICY-01
```

The rows those line numbers name: br.md:138 `RQA-BR-002`, br.md:139 `RQA-BR-004`, br.md:150
`RQA-BR-012`, fr.md:196 `RQA-FR-019`, fr.md:200 `RQA-FR-023`, fr.md:201 `RQA-FR-024`, fr.md:204
`RQA-FR-004`, fr.md:206 `RQA-FR-031`, fr.md:207 `RQA-FR-032`, fr.md:208 `RQA-FR-033`, nfr.md:399
`RQA-NFR-009`, nfr.md:405 `RQA-NFR-005`, nfr.md:406 `RQA-NFR-006`, nfr.md:408 `RQA-NFR-013`,
nfr.md:409 `RQA-NFR-023`, nfr.md:410 `RQA-NFR-027`, nfr.md:411 `RQA-NFR-029`, nfr.md:415
`RQA-NFR-018`, nfr.md:417 `RQA-NFR-025`.

Read against that index: `U-POLICY-03`, `U-POLICY-05`, `U-POLICY-07` and `U-POLICY-14` are named by
no register row at all, and the three `U-POLICY-12` occurrences are all in the one `RQA-NFR-018`
row, which introduces the unit as "comparison baseline, not a mapping" and states that the degree
"rests on the resolve_snapshot ranges alone and does not move if the citation is dropped".

Where an entry's `Requirements:` line carries an ID that the wave-1 evidence row does not, the ID
comes from a register row in that index — wave 2 credited this unit with evidence for that
requirement — and the entry says so. Where the evidence maps an ID the register credits to another
unit, the entry says that too, rather than banking the mapping silently.

---

### U-POLICY-01 — Repo-local config discovery and version-control isolation

Disposition: keep
Requirements: RQA-NFR-005, RQA-FR-004, RQA-FR-031, RQA-NFR-025, RQA-NFR-023
Root cause: `-` for RQA-NFR-005, RQA-FR-004, RQA-FR-031 and RQA-NFR-025, all `fit`; `not built` for RQA-NFR-023, whose row names this unit as the per-repository substrate that lacks the key.

Four `fit` rows name this unit (nfr.md:405, nfr.md:417, fr.md:204, fr.md:206) and they oblige
different things, which is what the keep has to answer for.

`RQA-FR-004` and `RQA-NFR-005` oblige a configuration or policy edit to take effect on the next
review with no rebuild, reinstall or redeploy. The mechanism is that `load_repo_config` reads and
JSON-parses the file at call time (scripts/config.py:446-455) from a path recomputed per call
(scripts/config.py:27-28, scripts/config.py:60-61). The materially simpler alternative is the
common one — parse once at process start and hold the result — and it defeats the requirement
directly: a sweep or tick is long enough for a job to be planned against a configuration the
operator has already changed, and the requirement's whole content is that the next review sees the
edit. A second simpler alternative, searching several candidate locations so an operator can put
the file where they like, breaks a different property: with more than one authoritative path,
"which configuration was in force" stops having an answer, which is the same property
`RQA-FR-012`'s reconstruction depends on.

`RQA-FR-031` obliges one operator to review across two independently configured repositories under
different owners with no centrally hosted service. That follows from the path being *repo-relative*
rather than user-level or installation-level: two repo roots are two configurations with separate
authority and no registry mediating them. Nothing simpler achieves owner-independent isolation
without introducing the central component the requirement forbids.

`RQA-NFR-025` obliges that no credential beyond the GitHub token enters the system. The register's
row rests on the recursive secret-key scan — `find_secret_keys` walking nested dicts and lists
against `SECRET_KEY_HINTS` with a small explicit allowlist (scripts/config.py:409-423,
scripts/config.py:343, scripts/config.py:345-354), folded into the validator's issue list at
scripts/config.py:203-205. A materially simpler top-level key check is the obvious alternative and
misses the case that matters: a credential written into a model-pool entry or a notification
transport block is nested, and those are exactly the places an operator would put one. Recursion is
the requirement-serving part, not an embellishment.

One shape decision runs under all four: `load_repo_config` returns `(None, issues)` rather than
raising. Raising would be simpler to write and would push the fail-closed decision out to every call
site, where one missing handler reintroduces the failure. Round-2 correction: an earlier revision
asserted that the return shape "lets every caller refuse a run" without quoting the caller search.
Complete stdout, run from `launchpad/skills/review-queue-automation/`:

```
$ grep -rn 'load_repo_config' scripts/
scripts/dispatcher.py:38:from config import load_repo_config
scripts/dispatcher.py:2242:    cfg, cfg_path, issues = load_repo_config(args.repo_root)
scripts/config.py:440:def load_repo_config(repo_root) -> tuple[dict[str, Any] | None, pathlib.Path, list[str]]:
scripts/onboarding.py:34:    load_repo_config,
scripts/onboarding.py:219:        loaded, path, issues = load_repo_config(args.repo_root)
scripts/route_probe.py:167:        from config import load_repo_config
scripts/route_probe.py:169:        config, cfg_path, issues = load_repo_config(args.repo_root)
scripts/cli.py:17:from config import load_repo_config
scripts/cli.py:29:    config, path, issues = load_repo_config(repo_root)
scripts/common.py:73:    `config.validate_config` / `load_repo_config` first, so existing config
```

Four production call sites invoke it, and each refuses on a `None` config rather than proceeding:
`dispatcher.main` prints `onboarding_required` (scripts/dispatcher.py:2243-2247),
`onboarding.main`'s `check` prints `valid: false` and exits 1 (scripts/onboarding.py:219-224),
`route_probe.main` prints `config_unusable` and returns 1 (scripts/route_probe.py:169-172), and
`cli.load_config` returns `None` for its callers to exit on (scripts/cli.py:29-31). The remaining
hits are the definition, two imports and one docstring mention.

Two behaviours inside this unit are **not** covered by the argument above, said plainly so the keep
does not launder them. The git-tracked and git-ignored fail-closed checks
(scripts/config.py:458-467), and `is_ignored`/`is_tracked` returning `False` outside a work tree
(scripts/config.py:71-88), answer to repository hygiene; wave 1 records them as beyond the frozen
set and no register row cites them. They ride along with the kept discovery mechanism, and nothing
in the specification is lost if a replacement drops them.

Recorded divergence, not an escalation: wave 1's note grouped the secret-key scan with those
unrequired hygiene behaviours, reasoning that `RQA-NFR-024`, `RQA-NFR-025` and `RQA-NFR-030` govern
the scope of the GitHub credential rather than the contents of a local JSON file. Wave 2 read it
the other way and made `scripts/config.py:409-423` load-bearing evidence for `RQA-NFR-025`'s `fit`
(nfr.md:417). This entry follows the register, which is the input wave 3 is directed to reason
from. A later wave that revisits `RQA-NFR-025` should know the scan's mapping is the one leg of
this keep that two waves have read differently; the other three legs stand without it.

---

### U-POLICY-02 — Fail-closed schema and semantic validation of the runtime config

Disposition: keep
Requirements: RQA-NFR-018, RQA-BR-004, RQA-NFR-026
Root cause: `built contrary` for RQA-NFR-018, whose contradicting executions the register locates in `dispatcher.resolve_snapshot`, not here; `not built` for RQA-BR-004's unmet severity vocabulary, in the verdict cluster; `not built` for RQA-NFR-026, whose absent `merge` activity the maintainer's 2026-09-08 ruling records as a `partial gap`.

`RQA-NFR-018` is `conflicting`, and §7 makes a `keep` against a `conflicting` requirement suspect by
default, so the chain has to be visible. The register's own cell puts both forbidden widenings in
`resolve_snapshot` — the clamp discarded on a `SnapshotError` (dispatcher.py:1584-1593,
snapshot.py:117-119) and an in-flight job resuming on the caller's current configuration — and says
in the same cell that a malformed inline policy "is genuinely caught earlier at config load and the
subcommand refuses outright, and the other fail-closed paths hold". This unit is that compliant
half. Its disposition cannot be a verdict on dispatch-cluster code, and it is not offered as one.

Why no materially simpler validator serves `RQA-NFR-018`'s non-widening obligation: the load-bearing
decision is that validation is all-or-nothing. `validate_config` returns immediately on a missing
required top-level key, so no later check can report against a structure that is not there
(scripts/config.py:114-119), and the `authority` and `policy` sections are validated by their owning
modules into the *same* issue list (scripts/config.py:207-219), so one malformed section makes the
whole configuration unusable. The simpler design — validate each section independently, report what
fails and apply what passed — is common and produces precisely the outcome the requirement forbids:
`authority` applying while a malformed `approval` section is silently dropped. "Never partially
applied" is a property of the accumulation shape, not of the individual checks.

The same argument in the specific: every `risk.protected_triggers` entry is `re.compile`d at
validation time (scripts/config.py:278-291). Compiling lazily, or treating the entry as a literal,
is simpler and moves the failure to match time — where its effect is a silently *narrower* set of
protected paths, the one direction `RQA-NFR-018` forbids. Validating a regex is only useful before
anything depends on it.

For `RQA-BR-004`, this unit supplies the definition the threshold rests on: `risk.bands` must be
present with `low`/`medium`/`high`, each an integer, and must pass `risk.validate_bands`' continuity
check (scripts/config.py:255-273). A simpler presence-and-type check admits a band map with a hole,
in which a computed score falls into no band and the blocking decision two reviewers are meant to
reach consistently is undefined. The register's `not built` cause for that row is a different
obligation — nothing enforces the schema's four-value severity enum on a returned verdict
(U-VERDICT-02, scripts/verdict.py:149-197) — which is additive and lies outside this unit, so it
does not argue against keeping what is here.

For `RQA-NFR-026`, `approval.mode` defaults to `"disabled"` when absent, is rejected unless it names
one of the four known modes, and `live` additionally requires `live_canary_approved` true and a
non-empty `risk.protected_triggers` (scripts/config.py:242-246, scripts/config.py:292-293). A plain
enum check is simpler and lets an operator reach live approval by writing one word; the conjunction
is what makes omission mean deny. The register's `RQA-NFR-026` row rests on `authority.py`
(U-AUTHORITY-01) rather than on this unit — recorded so the mapping is visible rather than assumed:
this is the approval-mode half of the same default-deny posture, and the entry claims no more. Since
the maintainer's 2026-09-08 ruling that row is `partial gap`, and the half claimed here is inside
its met portion: what is unmet is the `merge` activity, which no `approval.mode` check can default
because no activity model declares it.

Not covered by the argument: the unconditional `budget.validate_budget` delegation
(scripts/config.py:225-227), the notifications transport checks (scripts/config.py:316-338) and the
`dispatch.incoming_concurrency == 1` invariant (scripts/config.py:192-196). Wave 1 tested each
against requirement text and found no counterpart, and no register row cites them. They are kept
incidentally with the validator, not because the specification asks for them.

---

### U-POLICY-03 — The tracked example config stays runtime-shippable

Disposition: rework
Requirements: RQA-NFR-005, RQA-FR-004
Root cause: `-` for both, which are `fit`; the rework follows from §7's materially-simpler test rather than from a gap, and no register row cites this unit.

Retained in intent. An operator needs a complete, copyable starting configuration whose sections
match what the runtime requires, and it must carry an inline `policy` section: `snapshot.build_snapshot`
is fail-closed on a missing policy, so a template without one leaves every job unpinned with a blank
`policy_version` (scripts/config.py:373-375). That coupling is real and is the reason the artefact
carries a `policy` block at all (config.example.json:194-241).

What changes, first. The example is a second, hand-maintained copy of defaults that
`onboarding_defaults` already generates in code (scripts/config.py:471-530), and the only thing
binding the two is a test comparing top-level section names
(tests/test_config_onboarding.py:271-280). One source of defaults, with the tracked example produced
from it, is materially simpler and serves `RQA-FR-004` and `RQA-NFR-005` identically while removing
the whole drift class the guard exists to catch. The guard is also weaker than the drift it guards
against: two files can agree on every section name and disagree on every value inside them, which is
the failure mode that produced the unpinned-jobs regression the guard was written after.

What changes, second. The template advertises a `strategies.active` allowlist naming four strategy
names (config.example.json:166-172) that no code reads. Run from
`launchpad/skills/review-queue-automation/`, complete stdout:

```
$ grep -rn '"strategies"' scripts/ tests/
scripts/ledger.py:146:        "strategies": [i["payload"] for i in by_kind[STRATEGY]],
scripts/ledger.py:178:    strategies = report.get("strategies") or []
```

Both are the explain report's own output key, not a read of `config["strategies"]`; the register's
`RQA-FR-019` row (fr.md:196) quotes the same search and reaches the same conclusion, and wave 1
records that every `select_strategy` call site passes no `candidates` restriction
(scripts/dispatcher.py:1119-1121), so all twelve registered strategies stay selectable whatever the
key says. A tracked template offering an operator a control that changes nothing is a defect in the
artefact, independent of any requirement.

Why not `bin`. `RQA-NFR-005` and `RQA-FR-004` are `fit`, and this template is the operator's entry
to both. Removing it with nothing in its place would leave `onboarding.py init` as the only route to
a valid configuration — a narrowing this analysis has no requirement to justify, and §7's `bin`
definition does not reach a responsibility that is still needed in a different shape.

---

### U-POLICY-04 — Policy-as-data validation, versioning and content-hash pinning

Disposition: keep
Requirements: RQA-NFR-018, RQA-FR-004, RQA-NFR-005, RQA-FR-012
Root cause: `built contrary` for RQA-NFR-018, located in `dispatcher.resolve_snapshot` rather than here; `-` for RQA-FR-004 and RQA-NFR-005, both `fit`; `not built` for RQA-FR-012's two unmet elements, both outside this unit.

`RQA-FR-004`'s `fit` turns on an edited policy applying to the next review while an in-flight job
keeps its pin, and the register's words for that row are that the policy is "hashed into the
snapshot a job pins". That hash is computed here: SHA-256 over canonical, sort-keyed JSON
(scripts/policy.py:119-132), alongside the `policy_version` string that defaults to `"unversioned"`
when absent (scripts/policy.py:41-44).

Why no materially simpler pin suffices. A version string alone is the obvious cheaper option and is
operator-maintained, therefore not falsifiable: two materially different policies both labelled
`v1` are indistinguishable, so `RQA-FR-012`'s "name exactly which policy produced this decision" has
no answer and `RQA-FR-004`'s in-flight-versus-next-review boundary cannot be checked by anyone. An
mtime or a file path is worse on both counts — each changes without the content changing, and the
content can change without either moving. Canonicalising before hashing is the part that makes the
hash mean *the policy* rather than *the file's formatting*: without it, re-indenting a semantically
identical policy reads as a new one and invalidates every in-flight pin, which is the opposite of
what the requirement asks for.

Why validate-or-raise rather than validate-and-warn. `canonicalize` calls `validate_or_raise`
(scripts/policy.py:129-132) and the error type records that on rejection "existing policy stands"
(scripts/policy.py:38, scripts/policy.py:113-116). That is the compliant half of `RQA-NFR-018`, and
the register says as much in its own cell. A non-raising canonicaliser returning a best-effort
policy is materially simpler and lets a malformed edit take partial effect — the widening the
requirement forbids. The `built contrary` degree itself rests on `resolve_snapshot` discarding a
clamp, which this disposition neither excuses nor repairs.

Scope, so this keep is not read as wider than it is. The reload and pinning behaviour is decided in
`dispatcher.py` and `snapshot.py`, and the register credits U-RESILIENCE-09, U-DISPATCH-09 and
U-DISPATCH-11 with `RQA-FR-004` and `RQA-NFR-005` rather than this unit; `RQA-FR-012`'s two failures
— no protocol identity recorded anywhere, and `_ledger_record` swallowing write failures — are
`not built` in the resilience and dispatch clusters. What is kept here is the validator and the
construction of the pin those units call at scripts/dispatcher.py:1572 and scripts/dispatcher.py:1591.

---

### U-POLICY-05 — Policy derived from config, never invented

Disposition: salvage
Requirements: RQA-NFR-018, RQA-NFR-026
Root cause: `built contrary` for RQA-NFR-018, located in `dispatcher.resolve_snapshot` rather than here; `not built` for RQA-NFR-026, a `partial gap` since the maintainer's 2026-09-08 ruling, whose unmet obligation is the absent `merge` activity and not the non-widening derivation salvaged here. No register row cites this unit; the salvage follows from §7's materially-simpler test.

**The two things to lift, named so they survive without the code around them.**

1. **A derived policy is a copy of the configuration object it is derived from, and every structural
   fallback is bound to the identical literal the configuration generator itself writes** — never to
   a second default table that could carry a more permissive value. This is the non-widening
   invariant `RQA-NFR-018` turns on wherever a policy is seeded from a configuration, and it is the
   reason a derivation cannot move a threshold or grant an activity.
2. **A generated starter configuration must carry an inline `policy` section, because
   `snapshot.build_snapshot` is fail-closed on its absence** — without it every job runs unpinned
   and `policy_version` stays blank in the ledger (scripts/config.py:373-375). That coupling between
   the generator and the snapshot builder is a design decision, not an implementation detail, and it
   must survive whatever replaces either side.

**Why not `keep`.** The invariant is worth carrying; the function around it is a one-caller
indirection whose fallback branch is unreachable from that caller. Round-2 correction: the call-site
claim is a tree-wide count and now carries its search. Complete stdout, run from
`launchpad/skills/review-queue-automation/`:

```
$ grep -rn 'policy_defaults' scripts/ tests/
scripts/config.py:366:def policy_defaults(config: dict[str, Any]) -> dict[str, Any]:
scripts/config.py:529:    defaults["policy"] = policy_defaults(defaults)
tests/test_budget_controls.py:22:from config import policy_defaults  # noqa: E402
tests/test_budget_controls.py:39:    cfg["policy"] = policy_defaults(cfg)
tests/test_dispatch_observability.py:28:from config import policy_defaults  # noqa: E402
tests/test_dispatch_observability.py:51:    cfg["policy"] = policy_defaults(cfg)
tests/test_snapshot_pinning.py:255:    from config import onboarding_defaults, policy_defaults
tests/test_snapshot_pinning.py:259:    assert policy == policy_defaults(cfg), "the policy must be derived, not hand-written"
tests/test_snapshot_pinning.py:276:    from config import policy_defaults
tests/test_snapshot_pinning.py:285:    assert validate_policy(policy_defaults(sparse)) == []
```

One production call site, scripts/config.py:529 — the rest are three test modules, which methodology
§2.3 says confer no product reachability. At :529 the function is handed the `defaults` dict
`onboarding_defaults` has just finished building. That dict already carries all seven `approval` keys
(scripts/config.py:499-507), so the `required_approval` fallback table at scripts/config.py:384-392
never supplies a value on the only product path that reaches it — and that table is a verbatim
duplicate of scripts/config.py:499-507 with nothing binding the two together, so the drift hazard is
in the artefact rather than hypothetical. A materially simpler arrangement writes the `policy`
section from the same literals the generator is already using, which is what §7 makes decisive.

The scope of the guarantee is also narrower than the unit's name suggests, and a later wave should
not inherit the wider reading. This is not a runtime derivation: it runs once, at onboarding. A
job's policy at review time is whatever the operator's own `policy` section says, resolved through
`snapshot.build_snapshot`. So "deriving a policy from a config can never widen that config's own
authority" is, as implemented, a statement about the seed. Relatedly, the returned `"version"` is
the fixed literal `"v1"` (scripts/config.py:394) rather than anything derived, so every
onboarding-seeded policy is born with the same version string — which is exactly the case
U-POLICY-04's content hash has to compensate for.

**Why not `bin`.** `RQA-NFR-018`'s non-widening obligation is live, and any replacement will still
have to seed a policy from a configuration at some point. Binning would discard the design decision
along with the function, and the decision is the part that stops the seeding widening authority.

---

### U-POLICY-06 — Onboarding: a valid, never-overwritten starter config

Disposition: rework
Requirements: RQA-NFR-006, RQA-FR-031, RQA-NFR-026, RQA-NFR-018
Root cause: `-` for RQA-NFR-006 and RQA-FR-031, both `fit` and both citing this unit (nfr.md:406, fr.md:206); `not built` for RQA-NFR-026, a `partial gap` since the maintainer's 2026-09-08 ruling and carried by this unit's own wave-1 evidence row at ../evidence/policy.md:215 rather than by the register index, the generated default-deny configuration being inside its met portion; `built contrary` for RQA-NFR-018, located in `dispatcher.resolve_snapshot` rather than here. The rework follows from §7's materially-simpler test.

Retained in intent. First-run setup that refuses to overwrite an existing configuration and contacts
no GitHub API, no model and no lease (scripts/onboarding.py:2-6, scripts/onboarding.py:94-104); a
generated configuration whose every section is populated default-deny — all six `authority`
activities `"disabled"`, `approval.mode` `"disabled"`, empty pools (scripts/config.py:471-530); and
an update path that never leaves an invalid configuration live. The local-only property is not
incidental: `RQA-FR-031`'s row turns on configuration, state and credentials being per-repo-root
with no hosted service in the loop, which an onboarding step that called GitHub would break, and
`RQA-NFR-006`'s row names this unit for the same reason.

What changes: the write-then-check ordering, on both paths, and the asymmetry between them.
`init_onboard` writes the file at scripts/onboarding.py:120, validates at :122, and on failure
returns an error at :124-125 without deleting or restoring what it just wrote — so an invalid
configuration stays on disk after the CLI reports the run failed. `update_config` handles the same
situation the other way: backup at :149, restore at :157, :162, :177 and :186. Two paths of one
responsibility implement opposite disciplines and only one of them is safe. Wave 1 records the
`init` behaviour as a real, narrow finding bounded in practice by `load_repo_config` re-validating on
every later load (scripts/config.py:457) — bounded, but the artefact left behind is still one the
operator is told does not exist.

Why this is `rework` rather than `keep`. Every check either path performs is computable before the
write: `validate_config` is a pure function of the configuration dict and the root, and
`check_writable` already runs pre-write at :116 and :176. Validating the merged configuration and
writing only on success is materially simpler than write-then-backup-then-restore, serves
`RQA-NFR-018`'s "never left live in a corrupted state" obligation identically, and cannot express the
init/update asymmetry at all. §7 makes that the test, and the current shape fails it. The backup
itself is not what is being criticised — a backup is worth having across a destructive update — but
a backup used as the *mechanism* for validity is the wrong shape for the guarantee.

Not part of that argument, and recorded so a later wave does not read it as requirement-backed:
refusing to overwrite an existing local file, and refusing on a non-directory, a non-work-tree or an
empty `--slug` (scripts/onboarding.py:94-104), have no counterpart in the frozen set. They are
correct operator behaviour and a replacement should keep them, but no requirement obliges them and
they carry none of the weight here.

Round-2 item 1, answered rather than applied. The gate asked this entry to drop `RQA-NFR-026` or to
cite the claim row that credits the unit with it, on the stated finding that a full grep of
`../evidence/policy.md` for `RQA-NFR-026` "returns exactly two hits, both inside the `U-POLICY-02`
(lines 105, 108) and `U-POLICY-05` (line 196) sections". That finding does not reproduce. Complete
stdout, run from `launchpad/skills/review-queue-automation/`:

```
$ grep -c 'RQA-NFR-026' gap/evidence/policy.md
3
$ grep -on 'RQA-NFR-026' gap/evidence/policy.md
105:RQA-NFR-026
196:RQA-NFR-026
215:RQA-NFR-026
$ grep -n '^### U-POLICY-0[67]' gap/evidence/policy.md
200:### U-POLICY-06 — Onboarding: a valid, never-overwritten starter config
237:### U-POLICY-07 — Onboarding runtime-readiness gate
```

There are three, not two. The third, `../evidence/policy.md:215`, is inside this unit's own section:
the `### U-POLICY-06` heading is at ../evidence/policy.md:200 and the next heading, `### U-POLICY-07`,
is at ../evidence/policy.md:237. That row is the unit's second claim — `onboarding_defaults` returning
a configuration with every section populated with safe values, all six `authority` activities
`"disabled"` and `approval.mode` `"disabled"` — and its requirements cell reads `RQA-NFR-026`. So the
ID is grounded exactly the way the preamble's stated rule allows, and the way the gate itself accepted
for `U-POLICY-03` and `U-POLICY-05`: in the unit's own frozen wave-1 evidence row, not in the register
index. The gate is right that the register's `RQA-NFR-026` row (nfr.md:418) does not cite this unit,
which this entry already said of `U-POLICY-02` and now says here; that is not the same as no source.
The mapping is therefore retained. The disposition would not move either way — it rests on the §7
materially-simpler test, not on this ID.

---

### U-POLICY-07 — Onboarding runtime-readiness gate

Disposition: bin
Requirements: -
Root cause: `-`. No frozen requirement obliges the behaviour — wave 1 tested RQA-FR-031, RQA-NFR-004, RQA-NFR-006 and RQA-FR-032 candidate by candidate against the obligation and none covers (../evidence/policy.md:258-307) — and no register row names this unit, per the citation index above.

The maintainer's ruling makes `-` a starting point for removal rather than a neutral finding.
Nothing here displaces it, and two further facts push the same way.

**It is not a gate.** `_check_runtime_ready` returns a boolean and a list of problems
(scripts/onboarding.py:76-87); both callers place them in a returned summary
(scripts/onboarding.py:134-135, scripts/onboarding.py:188-196) and neither refuses, delays, narrows
nor alters anything on the strength of them. It reports. The unit's name says "gate", and the code
does not gate. Complete stdout of the consumer search, run from
`launchpad/skills/review-queue-automation/`:

```
$ grep -rn "runtime_ready\|readiness_issues\|_check_runtime_ready" scripts/ onboarding/ SKILL.md OPERATORS.md references/
scripts/onboarding.py:76:def _check_runtime_ready(config: dict[str, Any]) -> tuple[bool, list[str]]:
scripts/onboarding.py:123:    ready, readiness = _check_runtime_ready(config)
scripts/onboarding.py:134:        "runtime_ready": ready,
scripts/onboarding.py:135:        "readiness_issues": readiness,
scripts/onboarding.py:188:    ready, readiness = _check_runtime_ready(config)
scripts/onboarding.py:193:        "runtime_ready": ready,
scripts/onboarding.py:194:        "readiness_issues": readiness,
OPERATORS.md:52:`runtime_ready: false` until you have filled in the model pools. Onboarding
```

**Two of its three conditions already fail closed at the point of use, in reachable code the
register does credit. The third does not, and is treated as a loss below.** An empty
`repository.slug` — like every other `REPOSITORY_KEYS` entry — is rejected by `validate_config`
(scripts/config.py:45, scripts/config.py:124-127), and the dispatcher refuses every subcommand
outright without a valid repo-local configuration (the `RQA-NFR-026` row, nfr.md:418). Empty model
pools mean `resolve_route` derives no candidate and returns `human` with no model selected
(scripts/routing.py:116-186), which is what the `RQA-NFR-027` row's `fit` rests on (nfr.md:410), and
`route_probe.main` refuses with `"no_routes_configured"` rather than reporting a false pass
(scripts/route_probe.py:174-182). For those two conditions the readiness report restates, in
advisory form and at a different time, checks the product already performs where they bind.

Corrected in round 2: an earlier revision claimed the same for the third condition, an empty
`login`. It does not hold. This is a structural fact about one named artefact, so it is cited by
`path:line` rather than searched for: `login` is a member of `REQUIRED_KEYS`
(scripts/config.py:30-44), and `validate_config` tests that set for key **presence** only, returning
early on a missing key (scripts/config.py:117-119); `login` is not a member of `REPOSITORY_KEYS`
(scripts/config.py:45), which is the truthiness loop at scripts/config.py:125-127. No line of
`validate_config` tests `login`'s value. Nor does anything downstream refuse on it: `lease.claim`
raises on an empty login (scripts/lease.py:68-69) but its only call site is itself conditioned on a
non-empty login (`if claim_lease and login:`, scripts/dispatcher.py:1698), so the guard cannot fire,
and `recover_interrupted` tolerates an empty login by skipping release with a logged reason rather
than refusing (scripts/dispatcher.py:1821, scripts/dispatcher.py:1829-1830). An empty login is
silently tolerated in the product, not enforced elsewhere.

**What is lost.** Three things. An earlier and friendlier signal at setup time that a freshly
initialised repository is not yet usable. The `runtime_ready: false` line `OPERATORS.md:52` tells an
operator to expect. And — per the correction above — the *only* place in the tree that reacts at all
to an empty `login`, since no product path refuses on one; binning this report leaves that condition
unremarked rather than merely unrepeated. All three are reasonable things to want; none answers to
the frozen specification, and §7 does not permit keeping a unit on that basis. The empty-login
observation is worth handing to whoever designs the replacement, because it is a real hole in the
estate rather than a property of this unit — but it is not a requirement, and it does not convert
an advisory report into a gate.

**No requirement depends on it.** The citation index above is the complete output of the register
search, and no row names `U-POLICY-07`. One sequencing consequence to hand on rather than decide:
the `OPERATORS.md:52` sentence would have to go with the behaviour, and `OPERATORS.md` is the docs
cluster's file, which this lane does not disposition.

---

### U-POLICY-08 — Named reasoning strategies and deterministic, signal-driven selection

Disposition: rework
Requirements: RQA-FR-019, RQA-BR-012
Root cause: `not built` for both.

This is the one unit in the cluster where the register locates a gap's cause *inside* the unit,
which is what makes it `rework` rather than `keep`. The `RQA-FR-019` cell (fr.md:196) names it
directly: "nothing compares the reasoning strategy or higher-cost method against the policy's stated
assurance — the registry of twelve named strategies is `STRATEGIES`/`STRATEGY_BY_NAME` at
strategies.py:63-90 and the selector that walks them from internal signals is `select_strategy` at
strategies.py:137-181, neither of which reads the policy's assurance statement." The selector this
unit is built around draws its inputs from the review's own signals, and the requirement measures the
choice against something the selector cannot see.

Retained in intent, in descending order of how easily a rebuild loses it:

- **One selector serving both the pre-spend reservation and the execution.**
  `signals_for_profile`/`strategy_for_profile` (scripts/strategies.py:109-134) is called by
  `dispatcher._reserve_budget` (scripts/dispatcher.py:1119-1121) and by `panel._selection_context`
  (scripts/panel.py:435-439), so a job cannot have its budget reserved against one strategy and be
  executed under another. Two selectors that agree at the time of writing diverge silently later,
  and the divergence surfaces as a budget overrun attributable to nothing.
- **Determinism ordered by specificity.** The fixed order — `specialist_need`, prior disagreement,
  `required_independence == "panel"`, challenger, high risk, complexity — with a
  `direct_analysis`/`checklist` default (scripts/strategies.py:137-181) is what stops a review
  reaching for a higher-cost method the signals do not call for.
- **The selection reason returned with the selection**, so the choice is inspectable rather than
  inferred after the fact.

What changes: the policy's stated assurance has to be an *input* to the selection rather than
something the selection could be compared against afterwards. That is the obligation `RQA-FR-019`
states and the one the current input set cannot express. `RQA-BR-012`'s own unmet obligation —
comparing recorded consumption against the policy's required assurance — is `not built` in the
budget and dispatch clusters (U-RESILIENCE-01, scripts/budget.py:217-230; U-DISPATCH-13,
scripts/dispatcher.py:1323-1329) and is not this unit's to close, but a strategy selection blind to
the policy's assurance sits upstream of the same comparison.

Not required, so carried by nothing above: the import-time assertion rejecting a registry row whose
`aggregation` is outside `VALID_AGGREGATIONS` (scripts/strategies.py:95-98), and the dead-field scan
at tests/test_strategy_metadata.py:37-63. The second is worth handing on, narrowed in round 2 to
what its cited source carries: the scan is a source-text grep living inside a test, so it runs only
when the suite runs. Wave 1's own frozen note is the source for the production side —
"nothing under `scripts/` re-runs this check at import time or at dispatch"
(../evidence/policy.md:331-343) — and this entry defers to it rather than restating the absence as
if newly established here.

---

### U-POLICY-09 — Execution-mode semantics: whether a panel happened

Disposition: keep
Requirements: RQA-BR-002, RQA-FR-002, RQA-FR-019, RQA-BR-012
Root cause: `not built` for RQA-BR-002, RQA-FR-019 and RQA-BR-012 — in each the register attributes met obligations to this unit and locates the unmet ones elsewhere; `-` for RQA-FR-002, which is `fit`.

The register cites this unit in three rows (br.md:138, br.md:150, fr.md:196) and in each it is on
the met side of the ledger: the execution-mode mapping is "total over every registered strategy",
and the mode "is sized from the assurance profile so it can never demand more independent
participants than required". The unmet obligations in those rows — the findings taxonomy and the
severity vocabulary (verdict cluster), the consumption-versus-assurance comparison (budget cluster)
— are elsewhere and additive.

Why no materially simpler approach serves `RQA-BR-002`'s and `RQA-FR-002`'s shared-definition
obligation:

- **Participants are discounted before counting, not filtered after it**
  (scripts/modes.py:185-211). A participant that timed out, produced no schema-valid verdict, or
  duplicates a provider family already counted contributes nothing toward the mode's required count,
  and the specific reason is recorded per participant. The simpler design — count what came back,
  then test the threshold — produces exactly the outcome `RQA-BR-002`'s criterion is about: two
  responses from one provider family satisfy an independence requirement they did not meet, and the
  record cannot say why any participant did or did not count. Recording the reason per participant
  is what makes the aggregate falsifiable rather than merely reported.
- **A missing verifier is not a pass** (scripts/modes.py:99-115, scripts/modes.py:224-232). A mode
  declaring a required `verifier_role` resolves to `HUMAN` — `DEGRADED` for `debate_adjudicate`,
  whose spec sets `on_missing_verifier="degraded"` — when no counted participant filled that role.
  Treating a generation as passing because enough participants ran, without asking whether the
  verifying one did, is the simpler rule and is the failure the shared-completion concept exists to
  exclude.
- **The mapping is total** (scripts/modes.py:136-152). `mode_for` resolves an unknown or absent
  strategy name to `single` rather than raising, and `spec_for` raises only for a genuinely unknown
  mode string. A partial mapping makes "a panel happened" strategy-dependent — and therefore
  harness- and model-dependent — which is the divergence `RQA-BR-002` measures.

`for_profile` (scripts/modes.py:155-179) derives the mode from the assurance profile's own
`independence`/`required` rather than from the strategy's aggregation, which the register lists as a
met obligation of both `RQA-FR-019` and `RQA-BR-012`. Note its direction, because it is one-way: it
caps what the executed mode may demand against the profile. It does not compare the *strategy* with
the policy's stated assurance, which is `RQA-FR-019`'s unmet obligation and U-POLICY-08's rework.

---

### U-POLICY-10 — Subscription-first model routing with an explicit, non-inventive fallback ladder

Disposition: keep
Requirements: RQA-NFR-009, RQA-FR-023, RQA-FR-024, RQA-FR-032, RQA-FR-033, RQA-NFR-027, RQA-FR-038, RQA-NFR-013, RQA-NFR-023, RQA-NFR-029
Root cause: `-` for RQA-NFR-009, RQA-FR-023, RQA-FR-024, RQA-FR-032, RQA-FR-033 and RQA-NFR-027, all `fit`; `not built` for RQA-FR-038, whose unmet part is credential-scope observability in U-AUTHORITY-02, and for RQA-NFR-013 and RQA-NFR-029, whose rows name this unit as the nearest existing mechanism carrying no send-permission concept, and for RQA-NFR-023, whose row cites this unit's scripts/routing.py:66-98 without naming the unit.

Eight register rows name this unit and six of them are `fit` (fr.md:200, fr.md:201, fr.md:207,
fr.md:208, nfr.md:399, nfr.md:410). They pull in different directions, and that tension is the
justification.

`RQA-FR-023` requires an unavailable configured reviewer, model or provider to be passed over rather
than halting the review. `RQA-NFR-009` and `RQA-FR-024` forbid substituting anything the operator
has not configured. `RQA-NFR-027` requires that with no pool configured nothing leaves for a
provider at all. A materially simpler fallback — a flat list tried in order, or "on failure, reach
for any reachable provider" — satisfies the first by violating the second and third. What satisfies
all of them at once is deriving every rung *solely* from `models.primary`/`models.secondary`, or
from an operator's explicit per-rung pin (scripts/routing.py:66-98), and terminating the fixed rung
order with a `human` rung that sets `final = "human"` and returns **without selecting a model**
(scripts/routing.py:116-186). Exhaustion has to be a named outcome: if it were an error or a
default, the only two remaining behaviours are stalling and substituting, and each contradicts a
different one of these rows.

The `run.attempted` guard and the cooldown skip (scripts/routing.py:101-113,
scripts/routing.py:151-155) are the second decision. Without them, "pass over the unavailable route"
degenerates into retrying the same rung inside one resolution. The simpler alternative — retry with
backoff — serves neither requirement: it converts an unavailable route into latency rather than into
the next *configured* candidate, which is the thing `RQA-FR-024` names.

`RQA-FR-032`'s before-send nameability is served here rather than in U-POLICY-11: `resolve_route`
passes the selected candidate through `model_registry.qualified_route` and attaches the identity at
*selection* time (scripts/routing.py:156-181), before that candidate is executed. That is the timing
bound the requirement states.

Where this unit appears in a `full gap` row it appears as the nearest thing that does not do the
job: `RQA-NFR-013` and `RQA-NFR-029` name it, and `RQA-NFR-023` cites its
scripts/routing.py:66-98 without naming it. Each needs a permit-or-forbid concept for
external-provider sends. The evidentiary source for that absence is the register's own search S6,
quoted with its command and raw output at ../register/nfr.md:256-281 and cited by all three rows;
this entry defers to it rather than restating a tree-wide absence as if newly established here.
Those gaps are `not built`
and additive — closing them puts a gate ahead of the ladder rather than changing how rungs are
derived — so they do not make the current shape wrong. The same holds for `RQA-FR-038`, whose unmet
part is the unobservable credential floor and ceiling, not the routing.

---

### U-POLICY-11 — Model alias registry and qualified-route identity

Disposition: keep
Requirements: RQA-FR-032 (rows 1 and 4); `-` for rows 2 and 3
Root cause: `-` — RQA-FR-032 is `fit` and cites this unit (fr.md:207); rows 2 and 3 carry no mapping at all after the no-nearest-fit ruling.

What is kept is the closed alias table with `resolve` (scripts/model_registry.py:27-51) and
`qualified_route` (scripts/model_registry.py:54-82). What is not is the route-material fingerprint
pair; the two `-` rows are treated separately below, as the ruling requires.

**Why no materially simpler approach serves `RQA-FR-032`.** The requirement is that the specific
provider path can be named *before* evidence is sent to it. A closed, hand-maintained map from each
alias to an exact `runner`/`selector`/`provider_family` triple, with `resolve` raising on an
unsupported alias rather than guessing, makes that name available without asking a provider
anything. Every materially simpler alternative breaks the timing bound rather than the naming:
resolving an alias to whatever the provider currently calls "latest", or accepting a free-text model
string and learning what it resolved to from the response, both make the path nameable only *after*
the send. Raising rather than guessing is the same property in the failure case — a guessed route is
a route nobody named.

**Row 2 lost its mapping and is still kept, and not on its own row's reasoning.** Wave 1 withheld
any before-send timing claim for `qualified_route` because it was describing the *panel* path, where
the call happens after the candidate has run (scripts/panel.py:668, scripts/panel.py:688-698). Both
call sites exist: the other is `routing.resolve_route` at scripts/routing.py:156-181, at selection
time, and U-POLICY-10's fourth row — which does carry `RQA-FR-032` — rests on it. So the estate
needs this function because a frozen requirement's nameability has to resolve to something concrete
enough to attach to a candidate, even though the specification does not name identity-record
construction as an obligation. That is the case the ruling explicitly allows, and it is load-bearing
rather than merely adjacent.

**Row 3 lost its mapping and should go with U-POLICY-12.** `runtime_route_material` and
`route_material_fingerprint` (scripts/model_registry.py:85-104) scope a change-detection hash, and
their consumers are both inside the binned gate. Complete stdout, run from
`launchpad/skills/review-queue-automation/`:

```
$ grep -rn 'runtime_route_material\|route_material_fingerprint' scripts/
scripts/model_registry.py:85:def runtime_route_material(config: dict[str, Any]) -> dict[str, Any]:
scripts/model_registry.py:102:def route_material_fingerprint(config: dict[str, Any]) -> str:
scripts/model_registry.py:103:    material = runtime_route_material(config)
scripts/model_registry.py:116:    fingerprint = route_material_fingerprint(config)
scripts/model_registry.py:145:    fingerprint = route_material_fingerprint(config)
```

`:116` is inside `observe_runtime_routes` and `:145` inside `mark_runtime_qualified` — both
U-POLICY-12's. Nothing in the frozen set needs a route-material fingerprint, so this pair is the
part of the unit that goes, and losing it costs the specification nothing. The dependency runs one
way — `runtime_route_material` calls `qualified_route` at scripts/model_registry.py:95, not the
reverse — so removing the pair leaves the kept identity builder intact.

---

### U-POLICY-12 — Changed route material is locked to shadow until re-qualified

Disposition: bin
Requirements: -
Root cause: `-`. No requirement is mapped: wave 1 tested five candidates text-exactly and none covers, and the one register row citing this unit introduces it as "comparison baseline, not a mapping" and states the degree "rests on the resolve_snapshot ranges alone and does not move if the citation is dropped".

Two waves reached "no frozen requirement obliges this" independently. Wave 1 tested `RQA-NFR-009`,
`RQA-NFR-018`, `RQA-FR-032`, `RQA-NFR-010` and the `RQA-FR-004`/`RQA-NFR-005` pair against the
gate's own obligation; wave 2 then struck the `RQA-NFR-018` mapping inside the register and recorded
that any row citing this unit against that requirement must be re-derived without it. The bin
candidacy is therefore not an artefact of one lane's search.

**Is it load-bearing for something required but unnamed? No.** Round-2 correction: an earlier
revision said the unit's output has "exactly one consumer", which does not reproduce. There are two,
and they are different surfaces. Complete stdout, run from
`launchpad/skills/review-queue-automation/`:

```
$ grep -rn 'route_meta\|route_qualification\|qualification' scripts/
scripts/dispatcher.py:1579:        route_meta = observe_runtime_routes(
scripts/dispatcher.py:1585:        if route_meta["shadow_locked"]:
scripts/dispatcher.py:1604:        "route_qualification": route_meta,
scripts/route_probe.py:188:    qualification: dict[str, Any] | None = None
scripts/route_probe.py:199:                qualification = mark_runtime_qualified(
scripts/route_probe.py:204:                qualification = {"status": "unqualified", "shadow_locked": True}
scripts/route_probe.py:213:        "qualification": qualification,
scripts/common.py:282:            CREATE TABLE IF NOT EXISTS route_qualifications (
scripts/routing.py:160:            # identities; qualification must not discard an otherwise executable
scripts/model_registry.py:112:    it remains `shadow_locked` until qualification explicitly replaces it.
scripts/model_registry.py:118:        "SELECT fingerprint, status FROM route_qualifications WHERE scope=?", (scope,)
scripts/model_registry.py:122:            "INSERT INTO route_qualifications(scope,fingerprint,status,updated_at) VALUES(?,?,?,?)",
scripts/model_registry.py:134:        "UPDATE route_qualifications SET fingerprint=?,status='shadow_locked',updated_at=? WHERE scope=?",
scripts/model_registry.py:147:        "INSERT INTO route_qualifications(scope,fingerprint,status,updated_at) VALUES(?,?,?,?) "
```

**The enforcement consumer.** `dispatcher.resolve_snapshot` reads `shadow_locked` from
`observe_runtime_routes` and clamps `approval.mode` and `authority.approve` to `"shadow"`
(scripts/model_registry.py:133-138, scripts/dispatcher.py:1579-1590). It is the only consumer that
changes what the system does. It also echoes the same dict back to its caller as
`"route_qualification"` in the returned snapshot meta (scripts/dispatcher.py:1604), which is a
report of the decision rather than a second decision.

**The report consumer.** `mark_runtime_qualified`'s return value is assigned in `route_probe.main`
(scripts/route_probe.py:199-202) — with a hand-built `{"status": "unqualified", "shadow_locked":
True}` substituted when not every probed route passed (scripts/route_probe.py:204) — and placed in
the printed report as `report["qualification"]` (scripts/route_probe.py:213), which the `--json`
path serialises to stdout (scripts/route_probe.py:216). That is an operator-visible surface, not an
enforcement point, and it is accounted for in "What is lost" below.

Neither consumer is anybody's obligation. `RQA-NFR-018` forbids *widening* and the clamp narrows —
the register spells out that a changed route silently retaining its prior authority is retention,
which the requirement's text permits. `RQA-NFR-026`'s default-deny, so far as any code delivers it,
comes from `authority.defaults()` with no observation of route material anywhere in it. `RQA-NFR-009`'s
prohibition on unconfigured substitution is satisfied by U-POLICY-10 whether or not a fingerprint is
ever taken. And an operator-visible status field obliges nothing at all.

**What is lost.** Two things. First, after an operator edits a configured route's model, prompt
version, effort or tool set, the next job would no longer be forced to shadow until `route_probe`
re-qualified that scope. Second, `route_probe --json`'s `qualification` block
(scripts/route_probe.py:213) loses its subject: an operator running a probe would no longer be told
whether the current route material is qualified, shadow-locked or merely observed. Both are genuine
defence-in-depth properties and reasonable things for an engineer to want; neither answers to
anything in the frozen specification, and §7 does not permit keeping a unit on that basis. Note that
the second is not independently salvageable as a report: with no gate there is no status to report.

**What binning does not do.** It does not close `RQA-NFR-018`. The register's first forbidden
execution is `resolve_snapshot` *discarding* the clamp on a `SnapshotError` and returning the
unclamped `local_cfg` (scripts/dispatcher.py:1584-1593, scripts/snapshot.py:117-119); the second is
an in-flight job whose pinned snapshot is no longer archived resuming on the caller's current
configuration. Removing the clamp's producer removes the first execution's subject without
addressing its defect, and leaves the second untouched. `RQA-NFR-018` is the dispatch cluster's to
answer, and no reader should take this bin as progress against it.

**Consequences to sequence, not to decide here.** `mark_runtime_qualified`
(scripts/model_registry.py:141-153) loses its only caller at scripts/route_probe.py:199, and the
`route_qualifications` table (scripts/common.py:282) loses both its writers. `route_probe.main`'s
`qualification` report field (scripts/route_probe.py:188, :204, :213) goes with it, as does
`resolve_snapshot`'s `"route_qualification"` meta key (scripts/dispatcher.py:1604) — both are
dispatch- and policy-cluster edits for other hands, named so nobody is surprised. The
`runtime_route_material` / `route_material_fingerprint` pair in U-POLICY-11 loses both its consumers
and goes with this unit. Route probing itself is required and stays — see U-POLICY-13.

---

### U-POLICY-13 — Route probing against the real transport

Disposition: keep
Requirements: RQA-FR-023, RQA-FR-032
Root cause: `-` for both, which are `fit` and both cite this unit (fr.md:200, fr.md:207).

`RQA-FR-023` requires an unavailable configured reviewer, model or provider to be passed over rather
than halting the review. The requirement-serving mechanism is not the probe's verdict but where the
result is written: `persist_probe_result` records a failure as a *timed* provider cooldown in the
`providers` table — `unavailable_until`, derived from `models.cooldown_seconds`
(scripts/route_probe.py:113-135) — and a pass clears it. That is the same table
`routing.is_route_available` reads at scripts/routing.py:151-155. The two materially simpler options
both fail the requirement in opposite directions. An in-process availability flag is discarded
between jobs, because each scheduled tick is a separate process under the timer (methodology §2.2,
E1), so the dead provider is re-tried on every job and the fallback the requirement asks for never
persists. A permanent disable converts a transient outage into a configuration change nobody made,
and the route never returns without operator intervention.

`RQA-FR-032` is served by the documented `route_probe.py --repo-root <repo> --json` command
(OPERATORS.md:151-153) — an E3/E4 instruction, distinct from the disclaimed internal-modules table —
which is how the configured routes are enumerated *ahead of* any review. That is the register's own
reason for citing this unit in the `RQA-FR-032` row. A probe that reported reachability without
naming the routes would not serve it.

Why probing through the real transport rather than a cheaper check. `probe_route` builds its
invocation through the same `runners.build_invocation` adapter the panel's `_run_reviewer` uses and
validates the resulting stdout against `verdict.validate_verdict` (scripts/route_probe.py:59-110,
scripts/panel.py:304-312). A ping, a credential check or an API-version query is materially simpler
and answers a different question: each passes for a route that then returns prose no schema will
accept, so the cooldown `RQA-FR-023` depends on would never be written for the failure mode that
actually occurs.

Not required, so carried by nothing above: the module's read-only posture toward GitHub and the
repository (scripts/route_probe.py:4-11), and `main`'s refusal to probe with no route configured at
all, reporting `"no_routes_configured"` rather than a false pass
(scripts/route_probe.py:174-182, scripts/route_probe.py:225). Wave 1 tested both against requirement
text and found no counterpart. The second is still worth naming here, because it is where the "no
model pool" condition already fails closed in reachable code — one of the reasons U-POLICY-07's
advisory version of the same check is binned.

Boundary: the qualification half of this file goes with U-POLICY-12. scripts/route_probe.py:196-202
calls `mark_runtime_qualified` and is the binned gate's release path, not part of probing.

---

### U-POLICY-14 — Distinct-family candidate eligibility across model pools

Disposition: keep
Requirements: RQA-BR-002, RQA-FR-002
Root cause: `not built` for RQA-BR-002, whose unmet obligations are the findings taxonomy and the severity vocabulary, both verdict-cluster; `-` for RQA-FR-002, which is `fit`. No register row cites this unit.

What this entry can disposition is narrow, and saying so first keeps the rest honest: the unit's
`Files:` line names one artefact, tests/test_panel_policy.py. The behaviour it concerns is decided
in scripts/panel.py (verdict cluster) and scripts/config.py (U-POLICY-02), neither of which this
entry disposes.

**Why keep rather than bin.** The pool-entry field contract has no owner. `validate_config` requires
every pool entry to declare a non-empty `runner`, `selector`, `provider_family` and `capability`,
plus a non-empty `efforts` list (scripts/config.py:168-173). `panel.py` keys the distinct-family
exclusion on `provider_family`, tracking `used_families` and adding the chosen family only on a
successful invocation (scripts/panel.py:656-661, scripts/panel.py:708-710), and keys candidate
eligibility on `capability` and `efforts` (scripts/panel.py:546-557). The two halves sit in different
clusters.

Round-2 correction: the load-bearing claim that no production code cross-checks the two now carries
its search. Complete stdout, run from `launchpad/skills/review-queue-automation/`:

```
$ grep -rn 'provider_family\|"capability"\|"efforts"' scripts/
scripts/dispatcher.py:1209:                 "route.provider_family": payload.get("provider_family", ""),
scripts/dispatcher.py:1210:                 "route.capability": payload.get("capability", ""),
scripts/dispatcher.py:2305:                    "capability": capability,
scripts/findings.py:51:    provider_family: str
scripts/findings.py:102:        family = _clean(verdict.get("provider_family"))
scripts/findings.py:119:                provider_family=family,
scripts/findings.py:168:        families = tuple(sorted({f.provider_family for f in group if f.provider_family}))
scripts/config.py:168:            for field in ("runner", "selector", "provider_family", "capability"):
scripts/config.py:171:            efforts = entry.get("efforts")
scripts/budget.py:213:                       model: str = "", provider_family: str = "") -> None:
scripts/budget.py:214:    _insert(state, RESERVATION, job_id, repo, number, model, provider_family, tokens, 0)
scripts/budget.py:218:                 model: str = "", provider_family: str = "", latency_ms: int = 0) -> None:
scripts/budget.py:220:    _insert(state, SPEND, job_id, repo, number, model, provider_family, tokens, latency_ms)
scripts/budget.py:224:            provider_family: str, tokens: int, latency_ms: int) -> None:
scripts/budget.py:226:        "INSERT INTO cost_ledger(recorded_at,job_id,repo,number,model,provider_family,"
scripts/budget.py:228:        (utcnow(), job_id, repo, int(number), model or "", provider_family or "",
scripts/route_probe.py:117:    provider = str(entry.get("provider") or entry.get("provider_family") or entry.get("runner") or "")
scripts/route_probe.py:144:            efforts = entry.get("efforts") or ["medium"]
scripts/modes.py:39:    `provider_family` and `valid` come from trusted sidecar metadata and schema
scripts/modes.py:45:    provider_family: str = ""
scripts/modes.py:203:        family = participant.provider_family
scripts/assurance.py:62:        return {"capability": self.capability, "effort": self.effort, "independence": self.independence}
scripts/assurance.py:71:    if axis == "capability":
scripts/assurance.py:178:            profile = raised(profile, "capability") or profile
scripts/common.py:341:              provider_family TEXT NOT NULL DEFAULT '',
scripts/routing.py:95:            if rung == "openrouter" and (entry.get("capability") or "") == "economy":
scripts/routing.py:147:            # Canonical pools carry `provider_family`; explicit rungs carry `provider`.
scripts/routing.py:148:            provider = entry.get("provider") or entry.get("provider_family") or rung
scripts/routing.py:165:                "provider": entry.get("provider") or entry.get("provider_family") or provider,
scripts/approval_evaluate.py:113:    families = {str(v.get("provider_family")) for v in verdicts if v.get("provider_family")}
scripts/shadow.py:318:        profile={"capability": "workhorse", "effort": "medium", "independence": "challenger"},
scripts/panel.py:220:    `provider_family` is read from the trusted sidecar the machinery wrote, never
scripts/panel.py:242:            provider_family=str(meta.get("provider_family") or ""),
scripts/panel.py:257:        "provider_family": entry.get("provider_family"),
scripts/panel.py:258:        "capability": entry.get("capability"),
scripts/panel.py:551:        if CAPABILITY_RANK.get(pool.get("capability"), 1) < required_rank:
scripts/panel.py:554:        efforts = pool.get("efforts") or []
scripts/panel.py:657:            family = pool.get("provider_family")
scripts/panel.py:702:                                     capability=pool.get("capability", ""),
scripts/panel.py:703:                                     provider_family=pool.get("provider_family", ""),
scripts/model_registry.py:22:    provider_family: str
scripts/model_registry.py:69:        "provider": str(entry.get("provider") or entry.get("provider_family") or "").strip(),
scripts/model_registry.py:94:            for effort in entry.get("efforts") or ["medium"]:
scripts/fallback.py:72:    if tier == "openrouter" and (entry.get("capability") or "") == "economy":
```

Every line in that output is a read of one field, a write of one field, a dataclass or DDL
declaration of one field, or a docstring. scripts/config.py:168-173 is the only site that enumerates
the required set, and it names no consumer; scripts/panel.py:551, :554 and :657 are the consuming
sites, and they name no validator. No line compares the two. The register's own search S6 reaches
the same place from a different angle: it enumerates all 29 `provider_family` occurrences under
`scripts/` and classifies every one into cost accounting, route identity and log attribution,
provider-diversity corroboration or provider-failure cooldown (../register/nfr.md:264-281) — an
agreement check between validator and consumer is not among them.

So a relaxation on the configuration side — making `provider_family` optional, or admitting an empty
string — would silently disable the provider-diversity exclusion that `RQA-BR-002`'s independence
concept and `RQA-FR-002`'s shared completion definition both rest on, and `modes.py` would then
re-derive its own distinct-family exclusion from metadata that no longer distinguishes anything
(U-POLICY-09). Nothing in production would fail.

**Why no materially simpler approach.** The alternatives are a comment, a JSON schema over the
configuration, or an assertion on the configuration side. A comment enforces nothing. A schema can
require the three fields present but cannot state that `panel.py` keys on *those particular* fields,
which is the half that breaks. A configuration-side assertion has the same blind spot in reverse.
What is kept is the pinning of both ends of the contract in one executable place — and, stated
outright because the unit's `Files:` line allows nothing else, **that place is the test file
itself**, tests/test_panel_policy.py, not a production invariant. This entry recommends retaining an
executable check that lives in the test suite; it does not claim the estate enforces the contract at
runtime, and the argument would be dishonest if read that way. The value is in the pairing of the
two ends, not in the coverage of either side.

**Scope note.** The rest of tests/test_panel_policy.py — malformed and missing-field verdicts
falling through to the next candidate, partial-panel handling, stale verdict clearing, retry-once on
a genuine timeout — exercises `panel.run_panel`'s own selection and retry logic through a fake
`_run_reviewer`. That is verdict-cluster subject matter, wave 1 draws no claim from it, and neither
does this entry.
