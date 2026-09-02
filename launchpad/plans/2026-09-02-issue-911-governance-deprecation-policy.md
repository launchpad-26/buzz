# Issue #911 — governance/deprecation-policy.md

ALREADY TRUE: `origin/launchpad` (commit `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`) carries 233 corpus files; `launchpad/docs/corpus/governance/` does **not** exist, so this node creates the directory. `launchpad/docs/corpus/standards/deprecation.md` (`corpus-standard-deprecation`) IS merged and owns deprecating **corpus nodes** — its own scope-and-omissions says "Nothing in the deprecation lifecycle addresses product code", which is exactly the gap this node fills. `launchpad/docs/corpus/templates/policy.md` (`corpus-template-policy`) is merged and prescribes the six-section policy shape plus the `# Policy: <subject>` H1. Sibling #908 `governance/compatibility-policy.md` is unmerged and is NOT a legal relationship target.

STEP 1  Gather ground truth on how things are actually removed in this repository — no assumption that a written policy exists. Read `crates/buzz-relay/src/config.rs` (`INERT_MEDIA_READ_AUTH_VARS`, its doc comment, the `inert_env_vars` warn loop, the `BUZZ_REPLICA_HEAD_MAX_AGE_SECS` hard error, and the three unit tests), `.env.example`'s media-auth note, `.github/workflows/ci.yml`'s `dead-token-guard`, `migrations/` checksum-stability comments and `crates/buzz-db/src/runtime/migration.rs`, `launchpad/decisions/README.md`'s supersession rule with the actual `status:`/`supersedes:` reciprocity across all 56 ADR files, `launchpad/docs/corpus/schema/node.schema.json`'s `status` enum, and `CONTRIBUTING.md`'s event-kind stability sentence. ← RUNS HERE

STEP 2  [needs 1] Establish the boundary against `corpus-standard-deprecation` (documents) and against `layers-configuration-relay-configuration`, which already carries a *Compatibility and deprecation* section naming both env-var cases in detail. This node links to both and restates neither.

STEP 3  [needs 2] Write front matter (id `governance-deprecation-policy`, type `governance`, status `draft`, origin `launchpad`, audiences `[agent, developer, operator, reviewer]`, evidence ledger with the revision as the first FACT, relationships only to ids confirmed present via `git show origin/launchpad:<path>`) and the body on the `corpus-template-policy` six-section shape with RFC 2119 framing and derived authority.

STEP 4  [needs 3] Run `python3 launchpad/project-intelligence/corpus/validate.py` until it reports PASS.

STEP 5  [needs 4] Run the corpus unittest suite bare and unpiped as the sole prior command, then commit plan + document with `git commit -s` in a separate call. Stop at the commit.

PARALLEL: none — one file, one task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must report PASS; `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report OK. No push, no PR.

OPEN: The repository has **no** written cross-cutting deprecation policy today. Every MUST in this node is therefore either (a) a restatement of a mechanism that already exists and was opened, or (b) this node's own proposal, disclosed as such. The temptation to invent a policy and present it as settled is the main hazard; the second is restating `relay-configuration`'s env-var content instead of linking to it. `standards/identifiers.md` observes a `corpus-` id prefix convention that the corpus has since outgrown (`layers-configuration-*`, `architecture-flows-*`); this node uses the settled `<directory>-<stem>` form per #2029 and records the tension rather than resolving it.

LEFT OUT: Compatibility guarantees while a thing exists (#908, unmerged). Any change to `config.rs`, `ci.yml`, migrations or any ADR. Any edit to `standards/deprecation.md`. Filing the findings surfaced in STEP 1 as issues — reported to the caller instead.
