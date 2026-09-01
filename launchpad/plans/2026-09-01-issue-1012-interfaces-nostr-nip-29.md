# Issue #1012 — corpus node: interfaces/nostr/nip-29.md

Stated size: issue #1012 body carries no explicit "Size" line -> cap: 5 steps (per
this task's own dispatch instruction, which caps this plan at 5 steps)

RUNS HERE: single agent, this worktree
(`__worktrees/task-1012-interfaces-nostr-nip-29`), sequential steps, no dispatch to
sub-agents.

ALREADY TRUE:
- Worktree created from `origin/launchpad` at commit
  `650354eab8d41ab6ce1a71de079a6c6d95c69052`; `git worktree add ... origin/launchpad`
  already run.
- `gh issue view 1012` confirms the target file, DoD checklist and evidence
  requirement; body genuinely names NIP-29 (relay-based groups), matching root
  `AGENTS.md`'s "Channels use `h` tags (NIP-29 group tag)" — not a `buzz-nip`. Not
  blocked.
- `launchpad/docs/corpus/interfaces/nostr/nip-29.md` does not exist yet (`ls` on that
  path fails: no such file or directory).
- `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum has no `interface`
  value; the correct value for this surface is `interfaces-events` (confirmed by
  reading the schema directly, and independently corroborated by both
  `templates/interface.md` and `templates/event-kind.md`, both already merged on
  `origin/launchpad`).
- `templates/interface.md` (id `corpus-template-interface`) and
  `templates/event-kind.md` (id `corpus-template-event-kind`) are merged on
  `origin/launchpad` (confirmed via `git ls-tree -r --name-only origin/launchpad --
  launchpad/docs/corpus`) and give: the required-sections skeleton (Interface
  description / Operations / Contract and stability / Boundary / Relationships /
  Scope and omissions), the explicit boundary against a single event-kind's own node,
  and pre-verified NIP-29 facts (h-tag MUST, 9000-9020 moderation range, 9021/9022
  join/leave) this plan reuses rather than re-deriving.
- No kind-39000/39001/39002 corpus nodes exist on `origin/launchpad` (issues
  #874/#875/#876 are unmerged) — `relationships[]` cannot target them; they will be
  named in body prose by filename/kind number instead, per `AGENTS.md`'s step 9
  (resolve every relationship target against the merge branch, never the author's own
  worktree).
- `architecture-principles-relay-is-source-of-truth.md` (id
  `architecture-principles-relay-is-source-of-truth`) IS merged on `origin/launchpad`
  and is a valid `references` target.
- Evidence already read directly in this session (paths/symbols, not assumed):
  `crates/buzz-core/src/kind.rs` (kinds 9000/9001/9002/9005/9007/9008/9021/9022 and
  39000/39001/39002/39003, lines ~333-428); `crates/buzz-core/src/filter.rs`
  (`filter_match_one`'s `h`-tag fallback-to-`channel_id` logic, lines 35-104);
  `crates/buzz-relay/src/handlers/ingest.rs` (`required_scope_for_kind` mapping NIP-29
  kinds to `Scope::AdminChannels`/`ChannelsWrite`/`ChannelsRead`, lines 437-521; the
  `"restricted: insufficient scope (need {})"` rejection message, lines 2249-2274);
  `crates/buzz-relay/src/handlers/side_effects.rs` (`emit_group_discovery_events`
  materializing relay-signed 39000/39001/39002 after group create/metadata/membership
  changes, channel-scoped storage, lines 1062-1219); `crates/buzz-relay/src/nip11.rs`
  (`SUPPORTED_NIPS` unconditionally includes `29`, line 15); `crates/buzz-cli/src/
  commands/channels.rs` (`cmd_list_channels`'s member-mode resolution: query
  kind:39002 `#p`, extract `d` tag, query kind:39000 `#d`, lines 29-69);
  `crates/buzz-relay/src/handlers/moderation_authz.rs` /
  `moderation_commands.rs` (Buzz's own ban/timeout/unban/untimeout/resolve-report
  layer, a Buzz-specific extension distinct from NIP-29's own 9000/9001, gated by
  community-role/channel-role lookups); root `AGENTS.md`'s "Channel scoping"
  paragraph. NIP-29 spec text fetched directly at the pinned commit
  `dabfcb2aaecf4fa374eda8b1232ab303a03f60ba` (h-tag MUST; public/private,
  restricted/open, closed tag semantics; 39000-39003; 9000-9008; 9021/9022) —
  corroborates, rather than merely repeats, the same facts `corpus-template-event-kind`
  already carries.
- Precedent check: the four comparable merged architecture nodes documenting Buzz's
  own upstream behavior (`architecture-principles-relay-is-source-of-truth.md`,
  `architecture-principles-community-is-security-boundary.md`,
  `architecture-principles-nostr-first.md`, `architecture-context-nostr-network.md`)
  all carry `origin: launchpad`, not `origin: upstream` — this node follows that
  precedent rather than reasoning independently to a different value.

STEP 1 [independent]
Write the front matter: `id: interfaces-nostr-nip-29`, `type: interfaces-events`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`
(matching `corpus-template-interface`'s own audience set), one commit-citation
provenance `FACT`, and one `evidence[]` entry per substantive claim planned in
"Already true" above plus the NIP-29 spec facts, each classified honestly
(`FACT` for anything opened directly this session, `TEAM_KNOWLEDGE` for the root
`AGENTS.md` "Channel scoping" quote attributed to that file). `relationships:` carries
exactly `references: architecture-principles-relay-is-source-of-truth` and
`implements: corpus-template-interface` — both confirmed present on
`origin/launchpad` in "Already true" above. No edge toward any kind-3900x node.
done when: the front matter parses as valid YAML, every `evidence[]` entry names a
path/symbol/URL actually opened in this session, and no `relationships[].target`
names an id absent from the `git ls-tree` list already captured above.

STEP 2 [needs 1]
Write the body from `templates/interface.md`'s skeleton: Interface description (the
NIP-29 group protocol boundary — `h`-tag-scoped write, 9000-range moderation
commands, 39000-range addressable discovery state — as Buzz's relay implements it,
not a re-description of the upstream spec); an Operations table (join/leave,
put-user/remove-user/edit-metadata/create-group/delete-group/delete-event, and the
three addressable reads), each row citing the code symbol or NIP-29 kind number, never
restating it from memory; Contract and stability (the `Scope` enum gate, the
`"restricted: insufficient scope (need {})"` rejection shape, `SUPPORTED_NIPS`
advertising 29 unconditionally, and the monotonic-timestamp/relay-signed replace
semantics on 39001/39002 as the ordering/idempotency guarantee); a Boundary paragraph
naming both template exclusions (no single kind's own wire contract; no
parameter-by-parameter API-reference depth) plus this node's own: Buzz's ban/timeout
moderation layer is a distinct Buzz extension, named but not restated here; and Scope
and omissions per `AGENTS.md` step 8, naming the unmerged kind-3900x nodes by filename
and the NIP-43/relay-membership overlap as open gaps rather than silently absorbing
them. Include one valid example (a successful join-request materializing into
kind:39002) and one failure example (the insufficient-scope rejection message).
done when: every one of the six numbered "Required sections" in
`templates/interface.md` is present in the drafted body, in the stated order, and the
Boundary section explicitly names both template exclusions plus the moderation-layer
exclusion.

STEP 3 [needs 2]
Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repository
root; fix whatever it names and re-run until it exits 0. Any `FAIL` line not
attributable to this node's own new file is treated as a fresh finding to report, not
silently worked around.
done when: the command's exit status is 0 and its output contains no `FAIL` line.

STEP 4 [needs 3]
Self-review the diff against issue #1012's Definition-of-done checklist line by line,
confirming: exactly one hand-authored canonical document was created; every
substantive claim traces to an opened source; no relationship targets an unmerged
node; inputs/outputs/errors/auth/versioning/ordering are all present; the NIP-29
spec link is present; both a valid and a failure example exist.
done when: each DoD bullet from the issue body has a corresponding, findable sentence
or section in the drafted node, checked by re-reading the rendered file once, not
assumed from having written it.

STEP 5 [needs 4]
Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` as the sole command in its own call; confirm it prints `OK`. Only then,
in a separate call, `git add` the node and this plan file and commit with `git commit
-s`. Do not push, open a PR, or touch any gate-stamp file — a rejected commit citing a
missing gate stamp is reported back as a finding, not routed around.
done when: the unittest run prints `OK` and `git rev-parse HEAD` after the commit
differs from the pre-commit `HEAD` recorded in "Already true".

PARALLEL: none — one file, one worktree, no independent sub-tasks; all five steps
above are a strict chain (each `[needs N]` on the step immediately before it).

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 with no
`FAIL` line before commit (STEP 3). `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print `OK` before
commit (STEP 5). The repository's own commit gate (whatever stamp mechanism
`git commit -s` depends on here) is not bypassed with `--no-verify` under any
circumstance; a rejection is reported, not routed around.

BUDGET: single document, one sitting — no multi-hour scope expected; this is a
documentation-only change with no code, test, or CI-workflow edits.

OPEN: issue #1012's DoD does not say whether Buzz's own moderation extension
(ban/timeout/unban/untimeout, Buzz-custom kinds, gated by `moderation_authz.rs`) is
in-scope detail for this node or belongs entirely to a separate node once one exists.
This plan resolves it by naming the extension in the Boundary section (it exists, it
is distinct from raw NIP-29 9000/9001, it is not restated here) rather than either
silently absorbing it or silently omitting it — recorded here because the issue itself
does not disambiguate.

LEFT OUT: no `relationships[]` edge toward any kind-39000/39001/39002 node — none is
merged on `origin/launchpad` yet (issues #874/#875/#876 unmerged); those are named in
body prose by filename/kind number instead, per the linking standard's guidance for a
target that "does not yet resolve on the merge branch." No attempt to document
Buzz's NIP-43 relay-membership admin surface (kinds 9030-9036) as part of this node —
it is a textually adjacent but separately-scoped admin surface with its own kind
range, out of this task's one-idea boundary. No second hand-authored canonical
document is created, per the issue's own out-of-scope list.
