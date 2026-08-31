# Plan: issue #1288 — document platforms/web/invite-ui.md

## ALREADY TRUE

- Issue #1288 (parent Feature #614) asks for exactly one hand-authored corpus
  node at `launchpad/docs/corpus/platforms/web/invite-ui.md`.
- `launchpad/docs/corpus/platforms/` does not exist yet on `origin/launchpad`
  (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`
  lists no `platforms/**` path) — this is the first node under that surface
  in this checkout.
- No `platforms`-specific template exists in `launchpad/docs/corpus/templates/`
  (33 templates present, none named `platforms*`). Per this Feature's settled
  sibling convention (an INFERENCE, not a merged decision), documents under
  `platforms/**` use `type: platforms` and borrow `component.md`'s section
  shape (Responsibility / Public interface / Dependencies / Boundary /
  Relationships / Scope and omissions) since no purpose-built template exists.
- `launchpad/docs/corpus/architecture/containers/web.md` (id
  `architecture-containers-web`) already exists on `origin/launchpad` and
  covers the `web` container as a whole, including a one-paragraph mention of
  the invite landing page and the `/api/invites/claim` call. It explicitly
  does not go deeper than that mention — no other corpus node documents the
  invite UI's actual component behavior (state machine, policy gating,
  download-platform detection, browser-join path), so this task is not a
  duplicate.
- The real implementation lives at:
  - `web/src/app/routes/invite.$code.tsx` — TanStack Router route, binds `$code`.
  - `web/src/features/invite/ui/InvitePage.tsx` — the component itself.
  - `web/src/features/invite/ui/InviteJoinPolicyNotice.tsx` — age/terms/privacy
    checkboxes sub-component.
  - `web/src/features/invite/invite-api.ts` — `claimInviteInBrowser`, the
    browser-join REST call.
  - Supporting shared libs it calls: `web/src/shared/lib/buzz-download.ts`
    (platform detection), `web/src/shared/lib/nostr-signer.ts`
    (`hasNip07Provider`), `web/src/shared/lib/relay-url.ts`.
  - Relay-side counterpart (dependency, not duplicated content):
    `crates/buzz-relay/src/api/invites.rs` — `join_policy`, `accept_policy`,
    `claim_invite` handlers and their `invite_invalid` / `invite_expired` /
    `invite_exhausted` sentinel strings, which `InvitePage.tsx`'s
    `inviteClaimErrorMessage` translates to user-facing copy.
  - E2E coverage: `web/tests/e2e/smoke.spec.ts` (age/legal consent gating,
    browser NIP-07 join, Safari Mac-picker dialog, mobile download fallback).
- No sibling corpus node (merged or otherwise) documents the relay-side
  invite-claim/accept-policy endpoints as their own node; the known
  in-flight sibling (#1274's invite-api node) exists only on a local branch,
  not on `origin/launchpad`, so it is not cited or referenced.

## STEP 1 — Confirm scope and gather evidence (done, this session)

Read the issue, `AGENTS.md`, `node.schema.json`, `component.md`, and every
source file listed above. Confirmed via `git log --oneline` that the invite
feature has an active history (#3141 use-limited invites, #2190 gated
browsing, #2090 Safari Mac picker, #2001 platform-resolved downloads, #1987
legal-consent gating) — each of those is reflected in the current code read,
not re-derived from the log alone.

## STEP 2 — Draft `platforms/web/invite-ui.md`

Front matter: `id: platforms-web-invite-ui`, `type: platforms`,
`status: draft`, `origin: launchpad`, `audiences: [developer, agent,
reviewer]`, one evidence entry per substantive claim (revision citation,
component structure, policy-gating logic, browser-join flow, download
detection, Mac-picker dialog, relay error-sentinel mapping, E2E coverage).
Body follows `component.md`'s shape (adapted): Responsibility, Public
interface (props/exports), Dependencies (imports both directions),
Boundary, Relationships, Scope and omissions — explicitly noting no
`platforms`-specific template exists yet, per the sibling convention.

## STEP 3 — Relationships

Add `part-of: architecture-containers-web` (confirmed present on
`origin/launchpad`) since the invite UI is a constituent feature of the
`web` container that node already names. No other relationship target
confirmed present and relevant, so none else declared.

## STEP 4 — Validate and diff-isolate

Run `validate.py` with the new file present (expect exit 0, no new FAILs),
then temporarily move the file aside, re-run, confirm the pre-existing FAIL
set is identical, and restore the file.

## STEP 5 — Gate and commit

Run the corpus unittest discovery command alone, then commit with `-s`,
per the two-separate-calls rule.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 with
  the new file present, and the FAIL set is unchanged with it removed.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → `OK`.
- Every DoD bullet in issue #1288 satisfied.
- Commit created with `git commit -s`.

## OPEN

- Whether `type: platforms` is the eventual, standards-track-approved type
  for this document, versus some future `platforms/*` template reshaping it
  — unresolved corpus-wide (per sibling convention note in the task brief),
  named in the node's own Scope and omissions.

## LEFT OUT

- Documenting the relay-side `/api/invites/*` handlers as their own node —
  out of scope for this task (one node, one concept); named as a gap in
  Scope and omissions instead.
- Any change to runtime product behavior.
- Broader `web` container documentation — already owned by
  `architecture-containers-web`.
