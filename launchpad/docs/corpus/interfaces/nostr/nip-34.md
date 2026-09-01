---
id: interfaces-nostr-nip-34
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052 on origin/launchpad."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "buzz-core/src/kind.rs declares eight NIP-34 kind constants Buzz's relay recognizes: KIND_GIT_REPO_ANNOUNCEMENT=30617, KIND_GIT_REPO_STATE=30618, KIND_GIT_PATCH=1617, KIND_GIT_PULL_REQUEST=1618, KIND_GIT_PR_UPDATE=1619, KIND_GIT_ISSUE=1621, and the four status kinds KIND_GIT_STATUS_OPEN=1630/KIND_GIT_STATUS_MERGED=1631/KIND_GIT_STATUS_CLOSED=1632/KIND_GIT_STATUS_DRAFT=1633, each doc-commented 'NIP-34: ...'."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:604-623"
  - statement: "buzz-core/src/kind.rs has compile-time assertions that KIND_GIT_REPO_ANNOUNCEMENT and KIND_GIT_REPO_STATE fall inside the parameterized-replaceable kind range (30000-39999), confirming both are NIP-33 parameterized replaceable events addressed by (pubkey, kind, d-tag), not regular immutable events."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:868-876"
  - statement: "buzz-sdk/src/builders.rs provides one typed builder function per NIP-34 kind Buzz emits: build_repo_announcement and build_repo_announcement_with_tags (30617), a build_ref_state_event equivalent lives in buzz-relay (see below) rather than buzz-sdk, build_git_patch (1617), build_git_pull_request (1618), build_git_pr_update (1619), build_git_issue (1621), and build_git_status parameterized over a GitStatus enum covering all four 1630-1633 kinds -- each performing its own field validation (length limits, hex-format checks, required-field checks) rather than being a bare passthrough encoder."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:845-956"
      - "crates/buzz-sdk/src/builders.rs:1018-1080"
      - "crates/buzz-sdk/src/builders.rs:1091-1122"
      - "crates/buzz-sdk/src/builders.rs:1249-1427"
      - "crates/buzz-sdk/src/builders.rs:1429-1527"
      - "crates/buzz-sdk/src/builders.rs:1550-1592"
  - statement: "build_git_patch enforces NIP-34's own SHOULD-use-patch-under-60KB guidance as a hard bound in its own doc comment and validation, rather than silently truncating a patch that must remain git-apply-able."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:1018-1023"
  - statement: "buzz-relay/src/api/git/manifest_event.rs's build_ref_state_event is a pure function (no subprocess, no disk, no S3 call) that builds and signs the kind:30618 ref-state event from an in-memory Manifest snapshot, enforcing NIP-34's own HEAD-tag wrapping ('ref: <head>'), emitting only refs/heads/* and refs/tags/* ref tags, and adding a buzz-specific 'p' tag (pusher or owner pubkey) that the module's own doc comment states is 'not part of NIP-34 but consistent with the rest of buzz's event-publishing conventions'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/manifest_event.rs:1-131"
  - statement: "manifest_event.rs's own test suite (head_tag_always_wraps_with_ref_prefix, skips_non_heads_or_tags_refs, rejects_invalid_oids, rejects_malformed_ref_names) pins the exact NIP-34 conformance behaviors the module's doc comment claims: HEAD wrapping, ref-namespace filtering, and OID/ref-name validation."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/manifest_event.rs:177-334"
  - statement: "buzz-relay/src/handlers/side_effects.rs's handle_git_repo_announcement (dispatched from handle_side_effects for KIND_GIT_REPO_ANNOUNCEMENT) is a stateful, server-side reaction to storing a kind:30617 event: it validates the d-tag as a repo identifier ([a-zA-Z0-9._-]{1,64}, no leading dot, no '..'), atomically reserves the name per-community in Postgres (git_repo_names), enforces a per-pubkey repo quota, and seeds or ensures the object-store manifest pointer that makes the repo cloneable -- this is relay-side event-driven behavior, not merely transport plumbing."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:2595-2726"
      - "crates/buzz-relay/src/handlers/ingest.rs:216-217"
  - statement: "A kind:30617 announcement whose d-tag collides with a name already owned by a different pubkey, or whose owner is at or over its per-pubkey repo quota, causes handle_git_repo_announcement to return Err; the caller (handle_side_effects, invoked from ingest.rs's post-storage side-effect dispatch) only logs that Err via error! and does not alter the already-computed IngestResult -- so the client receives {accepted: true, ...} for a stored, validly-signed Nostr event whose git-hosting name reservation and clone-ability silently did not happen server-side."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:2688-2726"
      - "crates/buzz-relay/src/handlers/ingest.rs:3192-3212"
  - statement: "buzz-relay's write-authorization gate (resolve_write_scope or equivalent scope-resolution match) requires Scope::ReposWrite for KIND_GIT_REPO_ANNOUNCEMENT and KIND_GIT_REPO_STATE, and Scope::MessagesWrite for KIND_GIT_PATCH, KIND_GIT_PULL_REQUEST, KIND_GIT_PR_UPDATE, KIND_GIT_ISSUE and all four status kinds -- an unrecognized kind falls through to a hard 'restricted: unknown event kind' error, but every NIP-34 kind Buzz defines is explicitly recognized and scoped."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:528-540"
      - "crates/buzz-relay/src/handlers/ingest.rs:545"
  - statement: "The same file marks every NIP-34 kind (30617, 30618, 1617, 1618, 1619, 1621, 1630-1633) plus KIND_PROJECT (30621, NIP-MP) as always-global (channel_id = NULL): the ingest pipeline nulls out channel_id even if a client attaches a stray 'h' tag, because these events are addressed by an 'a' tag (repository coordinate) rather than NIP-29 channel scope."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:658-673"
  - statement: "The relay's ingest pipeline uses a small set of OK-message string prefixes to signal rejection categories to the client: 'invalid: ...' for malformed/rejected event content, 'restricted: ...' for authorization failures (including the unknown-kind fallback above), 'error: ...' for internal/database failures, and 'duplicate:' for an already-stored event id -- the same convention every other event kind's ingest path uses, not a NIP-34-specific scheme."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:404-428"
      - "crates/buzz-relay/src/handlers/ingest.rs:545"
      - "crates/buzz-relay/src/handlers/ingest.rs:3192-3197"
  - statement: "buzz-core/src/git_perms.rs's ProtectionRule (parsed from a kind:30617 buzz-protect tag) carries a require_patch flag documented as 'Whether direct push is denied (must use NIP-34 patch)'; when set, the git-push authorization check (a transport-layer function operating on receive-pack ref updates, not the Nostr event-ingest path this node otherwise documents) returns a Denial with reason 'direct push denied: require-patch is set, submit a NIP-34 patch' for every ref-update kind (create, fast-forward, non-fast-forward, delete) against a matching ref."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/git_perms.rs:277-284"
      - "crates/buzz-core/src/git_perms.rs:556-559"
  - statement: "buzz-cli exposes NIP-34 operations as four subcommand groups: 'repos' (create/get/list/bind/protect, wrapping kind:30617), 'patches' (send/get/list/status, wrapping kind:1617 and 1630-1633), 'pr' (open/update/get/list/status, wrapping kind:1618/1619 and 1630-1633), and 'issues' (create/get/list/status, wrapping kind:1621 and 1630-1633) -- each subcommand's own doc comment names the kind it emits."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:1149-1212"
      - "crates/buzz-cli/src/lib.rs:1405-1509"
      - "crates/buzz-cli/src/lib.rs:1511-1653"
      - "crates/buzz-cli/src/lib.rs:1655-1730"
  - statement: "buzz-cli's 'repos create' doc comment states that a repository announced without a buzz-channel binding tag (e.g. by a vanilla NIP-34 client that knows nothing of Buzz's extension) returns 404 for every clone/fetch/push until its author runs 'buzz repos bind' -- i.e. the buzz-channel tag is Buzz's own access-control extension layered on top of the standard NIP-34 announcement, not part of NIP-34 itself, and its absence does not stop the announcement event itself from being valid and stored."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:1171-1174"
      - "crates/buzz-cli/src/lib.rs:1195-1200"
      - "crates/buzz-relay/src/api/git/transport.rs:469"
  - statement: "docs/nips/NIP-MP.md, describing Buzz's own custom kind:30621 (multi-repo project grouping), states plainly that 'repositories, patches, issues, statuses, and ref state are all standard NIP-34 kinds' and that 'maintainers is the standard NIP-34 multi-value tag; Buzz's own announcement builder does not emit it today, so in practice every current claim reduces to signer-is-owner' -- a directly-cited gap in how much of NIP-34's optional tag surface Buzz's own builders actually emit."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-MP.md:21"
      - "docs/nips/NIP-MP.md:217"
  - statement: "docs/nips/NIP-GS.md documents a separate, Buzz-authored NIP (NIP-GS, commit/tag signing with Nostr keys) that explicitly says it 'adds commit-level signatures to NIP-34 workflows' rather than being part of NIP-34 itself, and crates/git-sign-nostr implements it as a git gpg.format=x509 signing program; crates/git-credential-nostr separately implements NIP-98 (HTTP request signing) as a git credential helper authenticating the smart-HTTP transport those NIP-34 clone/push URLs use. Both are related to, but are not part of, the NIP-34 event contract this node documents."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-GS.md:844"
      - "crates/git-sign-nostr/README.md:1-4"
      - "crates/git-credential-nostr/README.md:1-3"
  - statement: "VISION_PROJECTS.md's own capability-status table marks 'Git hosting (smart HTTP + NIP-34)' as 'Ships today', separately from 'NIP-34 issues (kind:1621)' marked 'Designed' in one earlier revision of that table's surrounding prose -- read together with the kind.rs/builders.rs/side_effects.rs evidence above (which shows kind:1621 fully implemented with a builder, an ingest scope, and a buzz-cli issues subcommand), the 'Designed' marker in that doc is stale prose rather than a currently-accurate statement of what ships; this node's own Operations table reflects the code, not that doc's wording."
    entry_class: INFERENCE
    confidence: 0.75
    evidence:
      - "VISION_PROJECTS.md:256-258"
      - "crates/buzz-core/src/kind.rs:614"
      - "crates/buzz-sdk/src/builders.rs:1091-1122"
      - "crates/buzz-cli/src/lib.rs:1655-1730"
  - statement: "Issue #980 ('task: document interfaces/http/git.md'), the sibling node documenting Buzz's git smart-HTTP transport surface, is open and unmerged at the time this node was authored, so it cannot be a valid corpus relationships target yet; this node refers to it by filename in prose instead."
    entry_class: FACT
    evidence:
      - "gh_issue_view(980) -> state: OPEN, title: task: document interfaces/http/git.md"
---

# NIP-34: interface

Buzz's git-collaboration surface (repository announcement/state, patches,
pull requests, issues, and their status transitions) is implemented as
signed Nostr events under upstream [NIP-34](https://github.com/nostr-protocol/nips/blob/master/34.md)
("git stuff"), exchanged the same way as every other Nostr event: submitted
via `POST /events` or the relay's WebSocket, persisted by the relay, and
read back via `POST /query`/WebSocket `REQ` filters keyed on kind and the
repository's `a`-tag coordinate. The two sides are a git client/CLI (a human
or agent using `buzz repos`/`patches`/`pr`/`issues`, or a third-party NIP-34
client such as `ngit`/gitworkshop.dev) and Buzz's relay, which both stores
these events like any other Nostr event *and* reacts to two of them
(`kind:30617` announcement, and every push) with relay-side side effects —
git name reservation and object-store manifest management — that a vanilla
NIP-34 relay does not have.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Announce/update a repository | kind:30617; `buzz-sdk::build_repo_announcement`/`build_repo_announcement_with_tags`; `buzz repos create` (`buzz-cli/src/lib.rs:1150-1176`) | Parameterized-replaceable event; `d`-tag = repo id. Triggers relay-side name reservation + manifest seeding (`side_effects.rs:2595-2726`). |
| Get/list repository announcements | `buzz repos get`/`list` (`buzz-cli/src/lib.rs:1177-1194`) | Reads via `POST /query`/WebSocket `REQ` filtered on kind:30617 (+ optional `#p` author). |
| Bind a repository to a channel | `buzz repos bind` (`buzz-cli/src/lib.rs:1195-1208`) | Buzz extension, not NIP-34: republishes the announcement with a `buzz-channel` tag, the git-hosting ACL. |
| Manage branch/tag protection | `buzz repos protect list/set/remove` (`buzz-cli/src/lib.rs:1209-1253`); `buzz_core::git_perms::ProtectionRule` | Buzz extension `buzz-protect` tag on kind:30617; `require_patch` ties a ref to the NIP-34 patch workflow (`git_perms.rs:277-284,556-559`). |
| Repository state (ref) update | kind:30618; `buzz-relay::api::git::manifest_event::build_ref_state_event` (`manifest_event.rs:70-114`) | Relay-signed, not client-signed: emitted from the object-store manifest on every push. `d`-tag matches the kind:30617 announcement. |
| Send a patch | kind:1617; `buzz-sdk::build_git_patch` (`builders.rs:1018-1080`); `buzz patches send` (`buzz-cli/src/lib.rs:1407-1448`) | `content` is verbatim `git format-patch` output, capped so a patch stays under NIP-34's SHOULD-be-under-60KB guidance. |
| Get/list patches | `buzz patches get`/`list` (`buzz-cli/src/lib.rs:1449-1469`) | Reads by event id or by repo coordinate (`a` tag). |
| Set patch status | kind:1630/1631/1632/1633; `buzz-sdk::build_git_status`/`GitStatus`; `buzz patches status` (`buzz-cli/src/lib.rs:1470-1509`) | One of open/merged(applied)/closed/draft; merged status carries applied-patch `q` tags, merge-commit, applied-as-commits. |
| Open a pull request | kind:1618; `buzz-sdk::build_git_pull_request` (`builders.rs:1464-1527`); `buzz pr open` (`buzz-cli/src/lib.rs:1513-1560`) | Points at a tip commit + clone URL(s) rather than inlining a diff; distinct from `build_git_patch`. |
| Update a pull request's tip | kind:1619; `buzz-sdk::build_git_pr_update` (`builders.rs:1552-1592`); `buzz pr update` (`buzz-cli/src/lib.rs:1561-1596`) | References the PR via NIP-22-style uppercase root tags (`E`/`P`). |
| Get/list pull requests | `buzz pr get`/`list` (`buzz-cli/src/lib.rs:1597-1620`) | |
| Set pull-request status | kind:1630/1631/1632/1633; `buzz pr status` (`buzz-cli/src/lib.rs:1621-1653`) | Same status-kind family as patches. |
| Create an issue | kind:1621; `buzz-sdk::build_git_issue` (`builders.rs:1091-1122`); `buzz issues create` (`buzz-cli/src/lib.rs:1657-1683`) | `content` is the markdown body; `subject` tag is the title. |
| Get/list issues | `buzz issues get`/`list` (`buzz-cli/src/lib.rs:1684-1707`) | |
| Set issue status | kind:1630/1631/1632/1633; `buzz issues status` (`buzz-cli/src/lib.rs:1708-1730+`) | 1631 reads as "resolved" for an issue rather than "merged". |

## Contract and stability

- **Kind numbers are fixed by upstream NIP-34**, not Buzz's own to
  renumber; `kind.rs`'s compile-time assertions only check that the two
  parameterized-replaceable kinds (30617, 30618) sit in the correct numeric
  range, not that the numbers themselves may change.
- **Ordering/idempotency for kind:30617/30618** follows NIP-33
  parameterized-replaceable semantics: the relay's last-write-wins on
  `(pubkey, kind, d-tag)`. `handle_git_repo_announcement`'s own
  re-announce path is explicitly idempotent — a same-owner re-announce
  never re-creates or corrupts an existing name reservation, and re-seeds
  the manifest pointer only if it is missing (`side_effects.rs:2678-2726`).
- **Patches, PRs, issues and status events are ordinary immutable Nostr
  events** (no replaceable semantics): a correction is a new status event
  referencing the root via an `e`/`E` tag, never an edit of a prior one.
- **Authorization**: writing any NIP-34 kind requires the relay's normal
  scope check (`Scope::ReposWrite` for announcement/state,
  `Scope::MessagesWrite` for patch/PR/issue/status —
  `ingest.rs:528-540`) on top of standard Nostr signature verification;
  there is no NIP-34-specific auth bypass or extra gate at the event-ingest
  layer. A **separate** authorization layer exists one level down, at the
  git-push (transport) layer: `buzz-protect`'s `require_patch` rule can deny
  a direct push and point the pusher at the NIP-34 patch workflow instead
  (`git_perms.rs:277-284,556-559`) — that check runs against `receive-pack`
  ref updates, not against Nostr event ingest, and is documented in full by
  the sibling HTTP-transport node (see *Boundary*).
- **Error/rejection behavior**: malformed event content or an unauthorized
  scope produces the relay's standard OK-message prefixes (`invalid:`,
  `restricted:`, `error:`, `duplicate:` — `ingest.rs:404-428,545,3192-3197`),
  identical to every other event kind. **A documented seam**: a
  syntactically valid, correctly-scoped `kind:30617` announcement whose
  `d`-tag collides with a name a different pubkey already owns (or whose
  owner is at/over their per-pubkey repo quota) is still accepted and
  stored as a Nostr event (`{accepted: true, ...}`) — the side effect that
  reserves the git-hosting name and seeds the clone manifest fails
  separately and is only logged server-side (`error!`), never surfaced to
  the client as a rejected write (`side_effects.rs:2688-2726` +
  `ingest.rs:3192-3212`). A client that only checks `accepted` will believe
  its repository is hosted when it is not.
- **Buzz-specific extensions layered on top of the standard tags**: the
  `p`-tag on kind:30618 (pusher/owner pubkey, not part of NIP-34 —
  `manifest_event.rs:14-17`), the `buzz-channel` tag on kind:30617 (the git
  ACL — without it every clone/fetch/push 404s until `buzz repos bind` runs
  — `lib.rs:1171-1174,1195-1200`), and the `buzz-protect` tag (branch/tag
  protection rules, including the `require_patch` NIP-34-patch-only mode).
  None of these three is defined by NIP-34 itself.

## Boundary

This node does not describe:
- **The git smart-HTTP transport itself** — the `/git/{owner}/{repo}` clone
  URL surface, object-storage hydrate/CAS-publish protocol, and the
  `receive-pack` ref-update authorization path (`git_perms.rs`'s
  `Denial`/`default_min_role` machinery in full) — that is
  `interfaces/http/git.md`'s subject (issue #980, open/unmerged at the time
  this node was authored, so referenced here by filename only, not as a
  schema `relationships` edge).
- **NIP-GS (commit/tag signing) and NIP-98 (HTTP request signing)** —
  `git-sign-nostr` and `git-credential-nostr` implement those two separate,
  Buzz-relevant protocols; NIP-GS's own spec says it only "adds
  commit-level signatures to NIP-34 workflows," it is not NIP-34 itself.
- **NIP-MP (`kind:30621` multi-repo projects)** — a separate, Buzz-authored
  kind that groups NIP-34 repository announcements by coordinate; documented
  in `docs/nips/NIP-MP.md`, not restated here.
- **A field-by-field, parameter-by-parameter catalogue of every builder's
  validation rule** in `buzz-sdk/src/builders.rs` — the Operations table
  above names each operation and cites the builder that owns its exact
  field rules rather than restating every length limit and hex check.

## Relationships

Declared: none. No `interfaces-events`-typed node is merged to
`origin/launchpad`'s corpus tree at the recorded revision to `references`,
and the one clear sibling (`interfaces-http-git`, issue #980) is unmerged and
therefore not a resolvable target — see *Boundary* above and the evidence
ledger's final entry. A `references` edge to `interfaces-http-git` and to a
future `nip-mp`/`nip-gs` node (if either is drafted) is the natural follow-up
once those nodes exist.

## Scope and omissions

**This node covers** the Nostr-level NIP-34 event contract Buzz implements:
the eight kind numbers Buzz recognizes (30617, 30618, 1617, 1618, 1619,
1621, 1630-1633), the typed builder functions and `buzz-cli` subcommands
that produce them, the relay-side scope/authorization gate and OK-message
error conventions that apply to them, the relay-side side effects
`kind:30617` triggers (name reservation, manifest seeding) including the
documented accepted-but-side-effect-failed seam, and the three Buzz-specific
tag extensions (`p` on 30618, `buzz-channel`, `buzz-protect`) layered on top
of the standard NIP-34 tag set.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Git smart-HTTP transport, object-storage CAS, push ref-authorization in full | `interfaces/http/git.md` (issue #980, not yet merged) |
| NIP-GS commit/tag signing | `docs/nips/NIP-GS.md` |
| NIP-98 HTTP request signing for git credentials | `crates/git-credential-nostr` (no dedicated corpus node found) |
| NIP-MP multi-repo projects (kind:30621) | `docs/nips/NIP-MP.md` |
| Field-by-field builder validation catalogue | not yet built anywhere in the corpus |

**Expected but not verified when this node was written:**
- **Third-party NIP-34 interoperability** (whether `ngit`/gitworkshop.dev
  actually round-trip Buzz-announced repositories cleanly) was not tested
  live; the claim rests on Buzz's builders emitting the standard tags
  (`clone`, `name`, `description`, `web`, `relays`, `d`) that such clients
  are documented elsewhere (`VISION_PROJECTS.md`) to read, not on an
  executed interop test.
- **The `maintainers` tag and any other NIP-34-optional tag Buzz's builders
  do not emit** beyond the one gap `NIP-MP.md:217` names explicitly — no
  exhaustive diff against the full upstream NIP-34 tag set was performed
  for every kind; the Operations table above should be treated as "what
  Buzz's own builders/CLI expose," not "every tag NIP-34 permits."
- **Whether the accepted-but-side-effect-failed seam (Contract and
  stability, above) is an intentional design tradeoff or an unaddressed
  bug** was not resolved here; it is reported as a finding for a human/later
  pass to triage, not fixed or filed as a new issue by this documentation
  task.

## Finding: event model vs. transport-only

Buzz implements a real, non-trivial subset of NIP-34's own event-level
contract — not merely the git-smart-HTTP transport with Nostr signing bolted
on separately. The evidence for this: eight NIP-34 kind constants with their
own compile-time range checks (`kind.rs:604-623,868-876`); one typed,
independently-validating builder function per kind in `buzz-sdk`
(`builders.rs:845-1592`); a relay-side, event-kind-keyed authorization gate
(`ingest.rs:528-540`) identical in shape to every other Nostr write path; and
a stateful, event-triggered side effect (`side_effects.rs:2595-2726`) that
reserves a name and seeds an object-store manifest purely in reaction to
storing a `kind:30617` event, which a system that only forwarded git's own
transport protocol would have no reason to do. Two caveats keep this from
being "full NIP-34 coverage," both cited above rather than assumed: Buzz's
own announcement builder does not emit the standard `maintainers` tag
(`NIP-MP.md:217`), and no exhaustive audit of every optional NIP-34 tag
against every builder was performed for this node. The accurate framing is:
*Buzz implements NIP-34's core event model (repository lifecycle, patches,
pull requests, issues, and their status transitions) as first-class,
relay-authorized Nostr events with real server-side side effects — layered
with a small, clearly-tagged set of Buzz-specific extensions — rather than
treating NIP-34 as an inert payload format riding on top of a git-transport
implementation.*
