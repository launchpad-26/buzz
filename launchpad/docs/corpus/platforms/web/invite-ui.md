---
id: platforms-web-invite-ui
type: platforms
status: draft
origin: launchpad
audiences:
  - developer
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 46eb901e5aa928aa147fdaef9a509b636218653f."
    entry_class: FACT
    evidence:
      - "commit 46eb901e5aa928aa147fdaef9a509b636218653f"
  - statement: "The invite landing page is served at the client route `/invite/$code`, defined by web/src/app/routes/invite.$code.tsx, which reads the `code` route param and renders `InvitePage`."
    entry_class: FACT
    evidence:
      - "web/src/app/routes/invite.$code.tsx"
  - statement: "InvitePage (web/src/features/invite/ui/InvitePage.tsx) is a React function component accepting a single `{ code: string }` prop, exported as a named export."
    entry_class: FACT
    evidence:
      - "web/src/features/invite/ui/InvitePage.tsx:42"
  - statement: "On mount, InvitePage fetches `/api/join-policy` and stores the result in `policy` state: `undefined` while loading, `null` when the relay has no configured join policy, or a JoinPolicy object (terms_markdown, privacy_markdown, age_attestation_required, version) when one exists; a fetch failure also leaves `policy` as `undefined`."
    entry_class: FACT
    evidence:
      - "web/src/features/invite/ui/InvitePage.tsx:82-90"
  - statement: "When a join policy exists and requires age attestation and/or terms/privacy agreement, InvitePage renders InviteJoinPolicyNotice (web/src/features/invite/ui/InviteJoinPolicyNotice.tsx) inside an animated collapsing container, and disables both the 'Accept invite in Buzz' and 'Join in browser' buttons until the required checkboxes are checked."
    entry_class: FACT
    evidence:
      - "web/src/features/invite/ui/InvitePage.tsx:136-151"
      - "web/src/features/invite/ui/InvitePage.tsx:207-226"
  - statement: "InviteJoinPolicyNotice renders an accessible age-confirmation checkbox (visually hidden native input with a visible custom indicator, `aria-label` on the input, a `<label>` wrapping the visible affordance) when `age_attestation_required` is true, and a second checkbox agreeing to Terms of Service / Privacy Policy when either markdown field is present; each document name is a `<button type=\"button\">` that opens the document in a modal via `onShowDocument` rather than toggling the checkbox."
    entry_class: FACT
    evidence:
      - "web/src/features/invite/ui/InviteJoinPolicyNotice.tsx:16-71"
      - "web/src/features/invite/ui/InviteJoinPolicyNotice.tsx:104-158"
  - statement: "Before either join path proceeds, InvitePage's acceptPolicy() POSTs code, policy_version and age_confirmed to /api/invites/accept-policy and returns a policy_receipt string from the JSON response; if there is no configured policy (`policy` falsy), acceptPolicy() is a no-op returning undefined."
    entry_class: FACT
    evidence:
      - "web/src/features/invite/ui/InvitePage.tsx:92-105"
  - statement: "The desktop-app join path (openInvite) calls acceptPolicy(), then navigates the browser to a `buzz://join?relay=<ws-url>&code=<code>[&policy_receipt=<receipt>]` deep link; when no join policy exists at all, InvitePage instead renders a plain anchor to the same deep link (button vs. anchor is chosen by whether `policy === null`)."
    entry_class: FACT
    evidence:
      - "web/src/features/invite/ui/InvitePage.tsx:107-117"
      - "web/src/features/invite/ui/InvitePage.tsx:238-265"
  - statement: "The in-browser join path (joinInBrowser) is offered only when hasNip07Provider() (web/src/shared/lib/nostr-signer.ts) reports a `window.nostr` NIP-07 signer; it calls acceptPolicy() then claimInviteInBrowser(code, receipt) from web/src/features/invite/invite-api.ts, and on success navigates to `/` via window.location.assign."
    entry_class: FACT
    evidence:
      - "web/src/features/invite/ui/InvitePage.tsx:119-133"
      - "web/src/features/invite/ui/InvitePage.tsx:229-237"
      - "web/src/shared/lib/nostr-signer.ts:44-45"
  - statement: "claimInviteInBrowser (web/src/features/invite/invite-api.ts) POSTs `{ code, policy_receipt }` to `{relayHttpBaseUrl()}/api/invites/claim`, attaching a NIP-98 Authorization header built by makeNip98AuthHeader with `requireNip07: true` (so it throws Nip07UnavailableError rather than falling back to an ephemeral key), and a 15-second (INVITE_REQUEST_TIMEOUT_MS) abort timeout; on a non-ok response it throws using the `error` field of the parsed JSON body, or `HTTP <status>` if that field is absent or the body fails to parse."
    entry_class: FACT
    evidence:
      - "web/src/features/invite/invite-api.ts:1-51"
  - statement: "On a browser-join failure, InvitePage's inviteClaimErrorMessage() rewrites the relay's raw error string into user-facing recovery copy for three known sentinels -- messages containing 'invite_exhausted', 'invite_expired', or 'invite_invalid' each get a distinct explanatory sentence -- and passes any other message through unchanged; the rewritten message is rendered in a `role=\"alert\"` paragraph."
    entry_class: FACT
    evidence:
      - "web/src/features/invite/ui/InvitePage.tsx:27-39"
      - "web/src/features/invite/ui/InvitePage.tsx:266-270"
  - statement: "The relay's claim_invite handler (crates/buzz-relay/src/api/invites.rs) is the source of the `invite_invalid`, `invite_expired`, and `invite_exhausted` sentinel strings that inviteClaimErrorMessage() matches against, returned with HTTP 403 (StatusCode::FORBIDDEN) via its api_error() helper."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:383"
      - "crates/buzz-relay/src/api/invites.rs:444-463"
  - statement: "The relay's accept_policy handler (crates/buzz-relay/src/api/invites.rs) validates the posted policy_version matches the operator's currently configured policy and that age_confirmed is true when age_attestation_required is set, returning 400 join_policy_not_accepted otherwise, then mints a short-lived receipt bound to the invite code via invite_token::mint_policy_acceptance."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs:199-226"
  - statement: "InvitePage detects the visitor's OS/architecture via detectBuzzDownloadPlatform (web/src/shared/lib/buzz-download.ts, an async function) on mount, and resolves a 'Download it now' link URL via resolveBuzzDownloadUrlForPlatform; when the platform is macOS with an undetermined architecture, it instead sets `needsMacChoice` and shows a 'Which Mac do you have?' chooser dialog on click rather than resolving the URL up front."
    entry_class: FACT
    evidence:
      - "web/src/features/invite/ui/InvitePage.tsx:63-80"
      - "web/src/shared/lib/buzz-download.ts:80"
      - "web/src/shared/lib/buzz-download.ts:142"
  - statement: "The Mac-choice dialog is implemented as a `role=\"dialog\"` element with `aria-modal=\"true\"` and an `aria-label`, closable via an Escape keydown listener or a click on the backdrop, and on close moves focus back to the 'Download it now' trigger link (`downloadTriggerRef`) via closeMacChoice()."
    entry_class: FACT
    evidence:
      - "web/src/features/invite/ui/InvitePage.tsx:154-185"
      - "web/src/features/invite/ui/InvitePage.tsx:294-322"
  - statement: "Selecting a Mac option (chooseMacDownload) prevents the default navigation, opens a blank tab immediately (setting `opener = null`), then resolves the platform-specific download URL asynchronously and redirects that already-open tab to it -- guarded by a `choosingMacDownloadRef` so a second click during resolution is ignored."
    entry_class: FACT
    evidence:
      - "web/src/features/invite/ui/InvitePage.tsx:158-176"
  - statement: "InvitePage also renders a second `role=\"dialog\"`/`aria-modal=\"true\"` overlay (the `document` state) that displays a policy document's Markdown (rendered via the `react-markdown` package with the `remark-gfm` plugin, both declared as dependencies in web/package.json) when a user clicks the Terms of Service or Privacy Policy button inside InviteJoinPolicyNotice."
    entry_class: FACT
    evidence:
      - "web/src/features/invite/ui/InvitePage.tsx:366-395"
      - "web/package.json:35-36"
  - statement: "web/tests/e2e/smoke.spec.ts exercises this component with four Playwright specs: age/legal consent gating and button enablement, an end-to-end in-browser join via a mocked NIP-07 provider and a mocked /api/invites/claim response (asserting the NIP-98 Authorization header shape), the Safari Mac-picker dialog (open, choose, Escape-to-close with focus restoration), and download-link fallback behavior for mobile/non-desktop user agents."
    entry_class: FACT
    evidence:
      - "web/tests/e2e/smoke.spec.ts:16-121"
      - "web/tests/e2e/smoke.spec.ts:123-202"
      - "web/tests/e2e/smoke.spec.ts:204-261"
      - "web/tests/e2e/smoke.spec.ts:263-269"
  - statement: "No `platforms`-specific corpus template exists in launchpad/docs/corpus/templates/ at the recorded revision (33 templates present, none matching `platforms*`), so this node borrows the `component.md` template's section shape (Responsibility / Public interface / Dependencies / Boundary / Relationships / Scope and omissions) as an inference rather than following a merged, purpose-built standard."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/component.md"
    confidence: 0.7
  - statement: "This node's approach follows an unmerged working convention from earlier sibling tasks in Feature #614: documents placed under platforms/** use front-matter `type: platforms` and borrow component.md's shape, rather than `type: implementation` (component.md's own literal instruction), because node.schema.json's `platforms` enum member exists specifically for platform-surface documents and no sibling node currently on origin/launchpad demonstrates the alternative."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#614 batch dispatch convention (sibling platforms/** tasks)"
  - statement: "launchpad/docs/corpus/architecture/containers/web.md (id architecture-containers-web) is present on origin/launchpad at the recorded revision and already names the invite landing page and the /api/invites/claim call at container-scope, but does not describe InvitePage's internal policy-gating state machine, its two join paths, or its download/Mac-picker behavior -- so this node adds detail rather than duplicating that container-level node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/web.md"
---

# Web platform: invite-acceptance UI

The browser-based invite-acceptance flow at `/invite/<code>` -- the page a
person lands on after clicking a Buzz community invite link, gating entry
behind an operator-configured age/legal policy and offering two ways to
join: opening the desktop app via a `buzz://` deep link, or joining directly
in the browser with a NIP-07 signer.

This node documents `InvitePage` and its immediate collaborators as a
platform-surface (`web`) feature. It does not restate what
`architecture-containers-web` (the container-level node covering `web` as a
whole) already says about the container's technology, deployment, or
security model; it goes one level deeper, into this one feature's actual
behavior.

## Responsibility

`InvitePage` (`web/src/features/invite/ui/InvitePage.tsx`) is the single
component behind the `/invite/$code` route. It is responsible for:

1. Loading the relay's join policy (`GET /api/join-policy`) and gating both
   join actions behind any required age/legal confirmations.
2. Detecting the visitor's OS/architecture to offer a correct "download the
   app" link, including a disambiguation dialog for Mac visitors whose
   architecture cannot be inferred from the user agent.
3. Offering two ways to accept the invite: a `buzz://join` deep link into
   the desktop app, or an in-browser join (only when a NIP-07 signer is
   present) that calls the relay's invite-claim API directly and lands the
   user on `/`.
4. Translating the relay's invite-claim error sentinels into user-facing
   recovery copy.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `InvitePage({ code })` | React component (named export) | Renders the invite landing page for the given invite `code`. | `web/src/features/invite/ui/InvitePage.tsx:42` |
| `InviteJoinPolicyNotice({ ageConfirmed, agreementConfirmed, onAgeConfirmedChange, onAgreementConfirmedChange, onShowDocument, policy })` | React component (named export) | Renders the age/terms/privacy checkboxes; calls `onShowDocument(title, markdown)` when a document link is activated instead of toggling its own checkbox. | `web/src/features/invite/ui/InviteJoinPolicyNotice.tsx:74-97` |
| `claimInviteInBrowser(code, policyReceipt?)` | async function (named export) | POSTs to `{relayHttpBaseUrl()}/api/invites/claim` with a NIP-98 header requiring a NIP-07 signer; resolves to `{status, communityId, host, role}` or throws with the relay's error message. | `web/src/features/invite/invite-api.ts:13-51` |
| `Route` (`/invite/$code`) | TanStack Router file route (named export) | Binds the `code` path param and renders `InvitePage`. | `web/src/app/routes/invite.$code.tsx` |

## Dependencies

**Depends on** (this feature requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `web/src/shared/lib/buzz-download.ts` | Detects visitor OS/architecture and resolves a platform-specific download URL. | `web/src/features/invite/ui/InvitePage.tsx:2-8` |
| `web/src/shared/lib/nostr-signer.ts` | `hasNip07Provider()` decides whether the "Join in browser" button is offered at all. | `web/src/features/invite/ui/InvitePage.tsx:9` |
| `web/src/shared/lib/relay-url.ts` | `relayWsUrl()` builds the `buzz://join` deep link's `relay` parameter and (via `invite-api.ts`) the browser-join HTTP base URL. | `web/src/features/invite/ui/InvitePage.tsx:10` |
| `web/src/shared/lib/nip98.ts` (via `invite-api.ts`) | Builds the NIP-98 `Authorization` header for the browser-join claim request. | `web/src/features/invite/invite-api.ts:1` |
| `web/src/shared/ui/button.tsx` | Shared `Button` component used for both join actions. | `web/src/features/invite/ui/InvitePage.tsx:11` |
| `react-markdown` + `remark-gfm` (web/package.json) | Renders operator-authored Terms/Privacy Markdown inside the document modal. | `web/package.json:35-36` |
| `crates/buzz-relay/src/api/invites.rs` (`join_policy`, `accept_policy`, `claim_invite` handlers) | Relay-side counterpart for every network call this feature makes; also the source of the `invite_invalid`/`invite_expired`/`invite_exhausted` sentinels this feature translates. | `crates/buzz-relay/src/api/invites.rs:112-226`, `crates/buzz-relay/src/api/invites.rs:357-463` |

**Depended on by** (these require this feature):

| Component | Why | Evidence |
|---|---|---|
| `web/src/app/routes/invite.$code.tsx` | The only route that mounts `InvitePage`. | `web/src/app/routes/invite.$code.tsx` |

## Boundary

This node does not describe:
- The `web` container as a whole (technology stack, deployment, ownership
  boundary, CORS/security posture) -- see `architecture-containers-web`.
- The relay-side `/api/invites/*`, `/api/join-policy*` handlers as their own
  documented surface -- only the parts of `crates/buzz-relay/src/api/invites.rs`
  this feature directly depends on are cited here, as a dependency, not as
  this node's own subject.
- The Git-repository-browser feature (`web/src/features/repos/`) -- an
  unrelated feature area of the same `web` platform.
- Install/usage instructions for running `web/` locally -- see the
  repository's own `CLAUDE.md` / `Justfile` targets (`relay-web`, `web`,
  `web-e2e-smoke`).
- Whether any corpus node yet documents the desktop app's own `buzz://join`
  deep-link handler -- not found in the corpus at the recorded revision;
  named as a gap below.

## Relationships

- part-of: architecture-containers-web

## Scope and omissions

**This node covers** `InvitePage`'s responsibility, its public interface,
its policy-gating and two join-path behaviors, its download/Mac-picker
dialog, its relay error-sentinel translation, its real dependency edges in
both directions, and its E2E test coverage, as of the recorded revision.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `web` container as a whole (technology, deployment, security posture) | `architecture-containers-web` |
| The relay-side `/api/invites/*` and `/api/join-policy*` endpoints as their own documented surface | Not yet documented in this corpus (a known sibling attempt exists only on an unmerged local branch and is not cited here) |
| The desktop app's `buzz://join` deep-link handler | Not found in this corpus at the recorded revision |
| The Git-repository-browser feature of the same `web` platform | `web/src/features/repos/`, not this node's subject |
| Whether `type: platforms` is the eventual, standards-track-approved type for this document versus a future reshaping once a `platforms`-specific template lands | Unresolved corpus-wide; this node follows the sibling-task convention (`TEAM_KNOWLEDGE` entry above), not a merged decision |

**Expected but not verified when this node was written:**

- **Whether InvitePage is exercised by any test beyond
  `web/tests/e2e/smoke.spec.ts`** -- no unit-level test file for
  `InvitePage.tsx` or `InviteJoinPolicyNotice.tsx` was found under
  `web/src/features/invite/`; only the four E2E specs cited above were
  located and opened.
- **The desktop app's handling of the `buzz://join` URL** once the deep
  link is followed -- out of this node's reach (`web/` only), and no
  corpus node describing it was found to link to instead.
- **Whether the relay's rate limiting on `claim_invite`
  (`claim_rate_limited`/`claim_key_rate_limited` in
  `crates/buzz-relay/src/api/invites.rs`) surfaces any distinguishable
  error message to this UI** -- the sentinel strings this node documents
  (`invite_invalid`/`invite_expired`/`invite_exhausted`) were confirmed by
  reading the handler; whether a 429 rate-limit response reaches
  `inviteClaimErrorMessage()` with a message it recognizes was not traced
  end-to-end.
