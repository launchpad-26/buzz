# Plan: issue #956 — ingestion/configuration.md

**Issue:** launchpad-26/buzz#956, parent Feature #620. **Branch:**
`task/956-ingestion-configuration` off `origin/launchpad` at `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`.

## Grounding checked against real repo state

- Corpus tree at `origin/launchpad` (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`)
  has no `ingestion/` directory yet — this is the first node there. `agents/invariants.md`
  (id `agents-invariants`) is the only merged Feature #620 sibling, so it is the id-naming
  and template-choice precedent, not a duplication risk.
- `standards/code-references.md` (merged) governs "every citation ... that names code in a
  repository" — generic. Read in full; it does not address (a) a config value referenced
  but not itself checked in (`.env` vs. `.env.example`), (b) a config file's effective value
  diverging from its literal text (`Cargo.toml`'s `rust-version = "1.88.0"` MSRV floor vs.
  `rust-toolchain.toml`'s `channel = "1.95.0"` actually pinned; Hermit's `bin/cargo ->
  .rustup-1.28.2.pkg` symlink vs. what floats on an unactivated shell's `PATH`), or (c)
  config merely present vs. load-bearing for a specific claim. Those three are this node's
  real incremental angle.
- `templates/policy.md` (merged, `corpus-template-policy`) and `templates/configuration.md`
  (merged, `corpus-template-configuration`) both read in full. `configuration.md`'s own body
  states it is for cataloguing a *settings surface* (env-var tables like
  `layers/configuration/*.md`), explicitly excluding "config-as-evidence" reasoning — not
  this issue's subject. `policy.md` fits: #956's DoD tail is the same
  scope-authority/MUST/SHOULD/enforcement/exceptions/links boilerplate `agents-invariants`
  (built from `policy.md`) already carried for the same reason under the same Feature #620.
- Confirmed via `git show origin/launchpad:<path>` that `corpus-agents`,
  `corpus-standard-code-references`, `corpus-template-policy`, `development-hermit`,
  `layers-configuration-secrets`, `layers-configuration-validation` all resolve on
  `origin/launchpad` today — valid `relationships` targets.
- Primary evidence gathered directly: `.env.example` / `.gitignore` (committed template vs.
  ignored real file), `rust-toolchain.toml` vs. `Cargo.toml` (`[workspace.package]
  rust-version`), `bin/hermit.hcl` + `bin/cargo` symlink target, `crates/buzz-workflow/src/
  schema.rs` (workflow definitions "authored in YAML and stored as canonical JSON" — i.e.
  live as event content, never a repo file), `launchpad/project-intelligence/CONTRACT.md` §1
  (`FACT` explicitly includes "config" as a source class).

## Steps

1. **Draft front matter.** `id: ingestion-configuration`, `type: ingestion`,
   `status: draft`, `origin: launchpad`, audiences `[agent, developer, reviewer]` (no
   `operator` — this is about authoring corpus claims, not operating the product).
   Evidence ledger: one commit-pinned FACT for the recorded revision, FACTs for every
   file/behavior cited above, one INFERENCE for the template choice (confidence ~0.8,
   same reasoning shape as `agents-invariants`'s own template-choice INFERENCE), TEAM_KNOWLEDGE
   entries for the issue's own Objective/DoD text. Relationships: `depends-on:
   corpus-agents`, `implements: corpus-template-policy`, `references:
   corpus-standard-code-references`, `references: development-hermit`, `references:
   layers-configuration-secrets`, `references: layers-configuration-validation`.
   **Done when:** front matter is internally consistent with the evidence gathered above.

2. **Draft body** in `templates/policy.md`'s six-section order (Scope and authority, MUST,
   SHOULD, Enforcement, Exceptions and escalation, Scope and omissions), stating the MUSTs
   for the three new angles (local-vs-committed, effective-vs-literal, present-vs-load-bearing)
   without restating `code-references.md`'s citation-shape rules. **Done when:** all six
   sections present in order, none silently empty, no restatement of `code-references.md`'s
   MUST 1-9 verbatim.

3. **Validate.** Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
   worktree root; fix every reported error. **Done when:** exit code 0.

4. **Earn the commit gate.** Run `python3 -m unittest discover -s
   launchpad/project-intelligence/corpus/tests -p "test_*.py"` as a lone command; confirm
   `OK`. Then commit with `git commit -s`. **Done when:** tests report `OK` and the commit
   exists with a `Signed-off-by` trailer.

5. **Self-review** against `code-references.md`'s citation rules, `policy.md`'s P1-P10, and
   the issue's own DoD line-by-line; re-run `validate.py` after any fix. **Done when:** no
   outstanding finding, `validate.py` still exits 0.
