# Plan: issue #1112 — corpus node layers-identity-private-key

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and
`launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad` at commit
338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5; `launchpad/docs/corpus/templates/concept.md`
is merged and fits this subject (a single defined idea needing discursive
explanation, boundaries, use cases and links — not a one-sentence glossary
term); `launchpad/docs/corpus/standards/{evidence,front-matter,linking,
code-references,naming,status,taxonomy}.md` are merged and bind this draft;
no `layers/` directory exists yet anywhere in the merged corpus, so no
sibling `identity` node (keypair #1111, public-key #1113) exists to link to;
the target file `launchpad/docs/corpus/layers/identity/private-key.md` does
not exist.

STEP 1 (RUNS HERE): Gather evidence — already read: `SECURITY.md` (OS
keyring custody, `BUZZ_PRIVATE_KEY` env-var precedence, migration
guarantees), `desktop/src-tauri/src/secret_store.rs` (keyring blob store,
interprocess lock, env short-circuit is deliberately NOT on this path),
`desktop/src-tauri/src/app_state.rs` (`identity_from_env`, resolution
priority: env → keyring → `identity.key` file → generate), `crates/
buzz-ws-client/src/message.rs` (`build_auth_event` + `.sign_with_keys`:
signing happens client-side, only the signed `Event` crosses the wire),
`crates/buzz-auth/src/nip42.rs` (`verify_nip42_event` takes only a signed
`Event`, never a key, confirming the relay-side custody boundary),
`crates/git-sign-nostr/src/lib.rs` (private key also signs git commits/tags
via BIP-340 Schnorr; documents its own zeroization limits and env-var
exposure risk), `README.md` (`BUZZ_PRIVATE_KEY` is how agents authenticate
`buzz-cli`), root `Cargo.toml` / `desktop/src-tauri/Cargo.toml` (the `nostr`
crate, not custom crypto, owns the `Keys`/`SecretKey`/nsec parsing this node
describes).

STEP 2: Write front matter (id `layers-identity-private-key`, type
`layers`, status `draft`, origin `launchpad`, audiences `agent`/
`developer`/`reviewer`) and body against `templates/concept.md`'s required
sections (Definition, Use cases, Boundary, Scope and omissions), covering:
what a private key is (the secret half of a Nostr secp256k1 keypair,
bech32-encoded as `nsec`), that it signs — never leaves — the client/agent
process, the three storage tiers and their precedence, and the boundary
against the sibling `keypair` (#1111) and `public-key` (#1113) concepts
(named in prose since neither exists on `origin/launchpad` yet — no
`relationships` edge is legal to either). No other `relationships`: no
`layers`-typed or identity-subject node exists in the merged corpus at this
task's merge base (checked via
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`).

STEP 3: Run `python3 launchpad/project-intelligence/corpus/validate.py`
from repo root; fix and re-run until exit 0.

STEP 4: Earn the verification stamp with
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole prior command, then commit the plan + target file in a separate
tool call.

PARALLEL: none — single hand-authored file, no fan-out.

GATES: `validate.py` must exit 0 locally before commit. The corpus
unittest suite above must report OK to earn the commit's verification
stamp. `review-adjudicate` and the cross-model review pass are deferred to
the batch owner's review — not run in this session (self-review only).

BUDGET: single document, one sitting — no iteration expected beyond
validator fix-up cycles.

OPEN: whether the eventual `keypair` (#1111) node should hold the
`depends-on`/`part-of` edges instead of this node once all three siblings
land is left to whichever of the three merges last — this task adds none.

LEFT OUT: no second canonical document; no changes to `desktop/src-tauri`,
`crates/buzz-ws-client`, `crates/git-sign-nostr` or any runtime behavior;
no generated index files touched; no resolution of `#1321`'s open question
about when a recorded revision may stay put across edits (not applicable —
this is a new node, not an edit).
