---
id: operations-runbooks-search-failure
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - developer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "buzz-search's crate doc states the index lives in the events table as `search_tsv TSVECTOR GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED` with `GIN (search_tsv)` as the access path; because the column is GENERATED ALWAYS, every row write to events IS the index update, so there is no separate indexer, queue, reindex job, or consistency window."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/lib.rs"
  - statement: "buzz-search's crate doc states it is the query side only: indexing is the SQL row insert, owned by buzz-db, and the relay refetches canonical events through buzz-db's scoped fetcher and runs access checks per hit, so search is never the access boundary and cannot widen visibility."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/lib.rs"
  - statement: "buzz_search::search's own doc comment states community_id = $ctx is the SQL query's first predicate and non-negotiable, and the function body binds it immediately after the mode-specific tsquery is built, before channel scope, kinds, authors, since, or until are layered on."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/query.rs"
  - statement: "Migration 0001 defines events.search_tsv as a generated column whose CASE expression yields NULL::tsvector (never matched by @@) for kind 1059 (gift wrap), 30300 (event reminder), 30622 (DM visibility), 44100 and 44101 (membership add/remove notices), and creates idx_events_search_tsv as a GIN index over that column."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "Migration 0005 adds kind 44200 (agent turn metric, NIP-44 ciphertext) to the same search_tsv exclusion CASE expression and rebuilds idx_events_search_tsv."
    entry_class: FACT
    evidence:
      - "migrations/0005_agent_turn_metric_fts.sql"
  - statement: "Migration 0008 rewrites search_tsv from a negative exclusion list to a positive allowlist of kinds 0, 9, 40002, 45001, 45003 only when the events table is empty at the moment the migration runs (guarded by `LOCK TABLE events IN SHARE ROW EXCLUSIVE MODE` plus a `SELECT 1 FROM events LIMIT 1` emptiness check inside a DO block); an already-populated database keeps its prior expression untouched, and its own comment states the operator must run a separate out-of-band script to converge it."
    entry_class: FACT
    evidence:
      - "migrations/0008_fresh_install_search_allowlist.sql"
  - statement: "scripts/maintenance/nip_rs_search_allowlist.sql is that out-of-band script: it is explicitly commented as not to be run from relay startup migrations, sets `SET LOCAL lock_timeout = '5s'`, and rewrites search_tsv to the same positive allowlist (kinds 0, 9, 40002, 45001, 45003) inside one transaction, warning that ALTER TABLE takes ACCESS EXCLUSIVE so event reads and writes block until it commits."
    entry_class: FACT
    evidence:
      - "scripts/maintenance/nip_rs_search_allowlist.sql"
  - statement: "Migrations 0014 and 0033 each read the events table's current search_tsv generated expression at runtime via pg_attrdef/pg_get_expr, RAISE EXCEPTION 'events.search_tsv generated expression not found' if that lookup returns NULL, and otherwise drop and re-add the column wrapped with one more kind exclusion (30350 in 0014, 30179 in 0033) before recreating idx_events_search_tsv; PostgreSQL cannot alter a generated expression in place, which is why each rewrites the whole column."
    entry_class: FACT
    evidence:
      - "migrations/0014_push_lease_fts.sql"
      - "migrations/0033_private_managed_agent_fts.sql"
  - statement: "Migration 0033's own comment states this DROP COLUMN plus ADD ... GENERATED ... STORED rewrites the entire events heap and rebuilds the GIN index under an ACCESS EXCLUSIVE lock with no lock_timeout set inside the migration transaction, and warns operators with large brownfield databases to expect relay downtime proportional to the size of events and to schedule a window."
    entry_class: FACT
    evidence:
      - "migrations/0033_private_managed_agent_fts.sql"
  - statement: "The relay's main.rs runs schema migrations only when BUZZ_AUTO_MIGRATE is truthy; when it is not set, main.rs logs 'Skipping database migrations because BUZZ_AUTO_MIGRATE is not enabled' and proceeds without applying any pending migration. When it is enabled and db.migrate() returns an error, main.rs logs 'Failed to run database migrations: {e}' and returns that error, which propagates out of relay startup via the `?` operator."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "The relay builds a dedicated search_pool in main.rs, connecting to config.read_database_url when one is configured and falling back to config.database_url otherwise; the connect call is awaited directly and a failure is mapped to 'Search DB connection failed: {e}' and propagated with `?`, so a search-pool connection failure at startup prevents the relay process from starting at all, not merely from serving search."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "The relay's /_readiness handler checks state.db.ping() (the primary/read-replica pool wired through buzz-db), a Redis pool checkout, and the deletion-serving-catalog validation, each with a 2-second timeout; it does not call state.search or otherwise probe the dedicated search_pool built in main.rs, so a readiness probe reporting 'ready' does not establish that the search-specific connection pool or its target database is reachable."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "handle_search_req (the WebSocket NIP-50 search path) calls state.search.search(&search_query) inside a per-filter, per-page loop; on an Err it logs 'NIP-50 search failed: {e}' at warn level and breaks out of that filter's page loop, but the function still calls conn.send(RelayMessage::eose(sub_id)) once all filters have been processed, so a search backend failure on this path ends the subscription with EOSE and whatever partial results were already emitted, never a protocol-level error the client can distinguish from 'no matches'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "handle_bridge_search (the HTTP POST /query bridge path) calls state.search.search(&search_query).await.map_err(|e| internal_error(&format!(\"search error: {e}\")))?, and internal_error logs the detail server-side and returns HTTP 500 with the fixed body {\"error\": \"internal server error\"} to the caller, so the same backend failure that is silent on the WebSocket path is a genuine, distinguishable error on the HTTP bridge path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/api/mod.rs"
  - statement: "Both search entry points reject a request mixing a search filter with a non-search filter before touching Postgres: handle_bridge_search's caller returns HTTP 400 with body 'mixed search and non-search filters not supported' when has_mixed_search_filters is true, and the WebSocket REQ handler sends a CLOSED message reading 'error: mixed search and non-search filters not supported' for the same condition, in both cases without ever calling buzz-search."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "On both search paths, a candidate hit returned by buzz-search is refetched as a full StoredEvent and re-checked against the current request before being returned: search_hit_accepted (HTTP) and the inline WS check both call filters_match against the original NIP-01 filter, check the event's channel_id against the caller's current accessible_channels, and call the per-event visibility gate (reader_authorized_for_event on the HTTP path, event_visible_to_reader on the WS path); a hit failing any of these three checks is dropped silently — `continue`d out of the loop — rather than surfaced as an error or a partial-result warning to the caller."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "buzz-cli's `messages search` subcommand builds a fixed filter of kinds [9, 40002, 45001, 45003] (message-shaped kinds only) with no --kinds flag anywhere on the command, attaches --query as the NIP-01 search field only when given, and requires at least one of --query or --author; the --author path additionally issues its own NIP-50 kind:0 search when the value is a display name rather than a hex key or npub, requiring an exact case-insensitive match and erroring with the candidate list on ambiguity."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/messages.rs"
  - statement: "buzz-cli maps a non-2xx relay response to CliError::Relay { status, body }, and exit_code maps that variant to exit code 3 only for status 401 or 403, and to exit code 2 (network/relay) for every other status including the 500 that handle_bridge_search's internal_error returns for a search backend failure; a transport-level reqwest failure (connect, timeout, DNS) is CliError::Network, also exit code 2."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/error.rs"
  - statement: "buzz-search/tests/fts_integration.rs's own module doc states it is run against a local Postgres with `BUZZ_TEST_DATABASE_URL=postgres://buzz:buzz_dev@localhost:5432/buzz cargo test -p buzz-search --tests -- --include-ignored`, and that each test creates a uniquely named schema, applies every FTS-affecting migration in order, exercises one scenario, and drops the schema; the file constructs its schema by concatenating the actual migration files (0001, 0002, 0003, 0004, 0005, 0006, 0007, 0008, 0014, 0033) via include_str!, not a hand-written replica of the schema."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/tests/fts_integration.rs"
  - statement: "crates/buzz-cli/TESTING.md's manual smoke-test transcript includes `buzz messages search --query \"Hello\" | jq .` and `buzz messages search --query \"CLI test\" --limit 5 | jq .` as the commands an operator runs by hand to exercise this command end to end against a live relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/TESTING.md"
  - statement: "docker-compose.yml defines a local Postgres service named buzz-postgres (image postgres:17-alpine) as the development database container this repository's local relay connects to."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
  - statement: "No admin-facing search reindex, search-health, or search-statistics command exists anywhere under crates/buzz-admin; the only operator-invoked remediation for a search_tsv expression that has drifted from the current allowlist is running scripts/maintenance/nip_rs_search_allowlist.sql by hand."
    entry_class: FACT
    evidence:
      - "scripts/maintenance/nip_rs_search_allowlist.sql"
  - statement: "The top-level agent contributor guide states as a documented repository gotcha that `messages search` chooses its own supported kinds, that an agent must not add a --kinds option because the current command does not accept one, and that this differs from raw relay filters, which still need explicit kinds."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "Because the search-specific connection pool built in main.rs is entirely separate from the pool the /_readiness handler probes, a scenario where the search database (or its configured read replica) is unreachable while the primary pool buzz-db uses is healthy would report /_readiness as ready while every search request still fails or, on the WebSocket path, silently returns fewer results than expected."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-relay/src/router.rs"
    confidence: 0.85
  - statement: "Because handle_search_req breaks its per-filter page loop on a search() error but still sends EOSE afterward, and because the WS client cannot distinguish a broken-early EOSE from a legitimately exhausted result set, a transient Postgres error during a WebSocket NIP-50 search is more likely to be reported by a user as 'my search returned nothing' or 'my search is missing results' than as a visible error, unlike the same failure on the HTTP bridge path."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
    confidence: 0.8
  - statement: "Issue #1224 is the sibling runbook task in this same Feature for a Postgres-unavailable condition generally, titled 'task: document operations/runbooks/postgres-unavailable.md'."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1224 issue title"
  - statement: "This node was written using launchpad/docs/corpus/templates/runbook.md, which was already merged on origin/launchpad at the recorded revision and directs a runbook's Required sections to be Trigger, Severity and impact, Diagnosis, Mitigation and resolution, Escalation, and Scope and omissions, each traceable to the Google SRE Workbook's playbook definition."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/runbook.md"
relationships:
  - type: implements
    target: corpus-template-runbook
  - type: references
    target: capabilities-search-full-text-search
  - type: references
    target: capabilities-search-search-index
  - type: references
    target: capabilities-search-search-query
  - type: references
    target: capabilities-search-channel-scope
  - type: references
    target: capabilities-search-privacy-filtering
  - type: references
    target: capabilities-search-result-reauthorization
---

# Runbook: search failure

What to do when Buzz's full-text search (NIP-50, over Postgres FTS) returns no
results, fewer results than expected, an error, or results that look wrong for
the query given. This is the concrete realization of
[`corpus-template-runbook`](../../templates/runbook.md) (`implements`, above)
for the search subsystem — read that template for what a runbook node is and
is not.

**Mechanism, not procedure.** How the generated `search_tsv` column, the GIN
index, channel scoping, privacy exclusions, and post-hit reauthorization work
is documented in depth by six already-merged capability nodes —
[`full-text-search`](../../capabilities/search/full-text-search.md),
[`search-index`](../../capabilities/search/search-index.md),
[`search-query`](../../capabilities/search/search-query.md),
[`channel-scope`](../../capabilities/search/channel-scope.md),
[`privacy-filtering`](../../capabilities/search/privacy-filtering.md), and
[`result-reauthorization`](../../capabilities/search/result-reauthorization.md)
— all targeted by `references` above. This node does not restate that
mechanism; it is the decision tree for a responder who already suspects
something is wrong and needs to find out what, in what order.

## Trigger

Any of the following, reported by a user, surfaced by an agent calling
`buzz messages search`, or observed directly against `POST /query` or a
WebSocket `REQ` carrying a NIP-50 `search` filter:

- A search that should return known-existing content returns zero hits.
- A search returns fewer hits than a user expects, or omits a message the
  user can otherwise see by scrolling the channel.
- A search returns content the user does not expect — wrong channel, wrong
  kind, or content that should be private.
- The HTTP `POST /query` bridge returns a non-2xx response for a request
  carrying a `search` field.
- A WebSocket `REQ` subscription carrying a `search` filter is closed with an
  `error:` reason, or ends in `EOSE` unexpectedly fast with no visible cause.
- `buzz messages search` (or `buzz users` display-name resolution, which
  issues its own kind:0 NIP-50 search) exits non-zero or returns an empty
  result set the operator did not expect.

There is no dedicated alert for search specifically in this repository at the
recorded revision — see *Scope and omissions*. This runbook is triggered by
a report or by direct observation, not by a paging system.

## Severity and impact

**Search is a discovery feature layered on top of storage, not storage
itself.** A search failure of any kind described above does not imply data
loss: every search hit is a candidate id that the relay refetches from the
canonical event store and re-authorizes before returning
(`result-reauthorization`, referenced above) — the underlying messages remain
retrievable through `messages get`, `messages thread`, and normal channel
history regardless of whether search can find them.

- **No hits when hits are expected** — degrades discoverability; the message
  is still present and reachable by other means. Low to moderate user
  impact, no data-integrity impact.
- **Fewer hits than expected** — same as above, and often invisible: on the
  WebSocket path in particular, a backend error midway through paging still
  ends the subscription with a normal `EOSE` (see *Diagnosis*), so a user
  cannot tell "no more results exist" from "the search stopped early because
  something broke."
- **Unexpected or wrong-looking hits** — before assuming a bug, check
  whether the result is explained by design: privacy-sensitive kinds are
  excluded from indexing at the storage level
  (`privacy-filtering`, referenced above), and post-hit reauthorization drops
  a hit the caller is not authorized to see. Both are expected behavior, not
  failures.
- **A genuine HTTP 500 from `POST /query` on a search request** — the
  bridge's only failure-visible path (see *Diagnosis*). User-visible as a
  failed request; if it correlates with other endpoints also failing, treat
  it as a Postgres-availability incident and escalate per *Escalation*
  below, not as a search-specific bug.
- **Relay fails to start, logging a migration or connection failure
  mentioning `search_tsv` or `Search DB connection`** — full outage, not a
  search-only degradation. See *Diagnosis*'s fourth branch.

## Prerequisites

- Read access to relay logs (structured logs from `crates/buzz-relay`,
  specifically anything logged from `handlers/req.rs`, `api/bridge.rs`, or
  `main.rs` at startup).
- For a self-hosted or local relay: `psql` access to the community's Postgres
  database, or `docker compose exec postgres psql -U buzz -d buzz` against
  the `buzz-postgres` service defined in `docker-compose.yml`, referenced
  above.
- Knowledge of which relay endpoint the affected client used — WebSocket
  `REQ` or HTTP `POST /query` — because the two paths fail differently (see
  *Diagnosis*). If the report came through `buzz messages search`, that
  command always uses the HTTP bridge (`client.query`, per
  `search-query`, referenced above).
- For the schema-drift branch of *Diagnosis*: ability to run
  `\d+ events` or query `pg_attrdef`/`pg_get_expr` against `events.search_tsv`
  to inspect the column's actual generated expression.

## Diagnosis

Work through these in order. Each branch names what confirms it and what to
do once confirmed; stop at the first branch that matches.

### 1. Is this actually a Postgres-availability problem?

Check first, because it changes everything downstream. If the relay's
`/_readiness` endpoint is reporting `not_ready` with `"postgres": false`, or
if other unrelated endpoints (channel listing, message posting) are also
failing, this is not a search-specific problem — **stop here and hand off to
the postgres-unavailable runbook** (issue #1224 in this repository's issue
tracker; not yet a corpus node at this revision, so it cannot be linked by id
— see *Escalation*).

**The one search-specific trap in this check:** the dedicated `search_pool`
built in `main.rs` is a separate connection pool from the one `/_readiness`
probes, and it can target a different host entirely when
`config.read_database_url` is set. `/_readiness` reporting `ready` does
**not** establish that the search pool's target (primary or replica) is
reachable. If `/_readiness` is green but search specifically is failing,
move to branch 4 rather than concluding Postgres as a whole is healthy.

### 2. Is this a query-shape problem?

Confirms as: an HTTP `POST /query` request returns `400 Bad Request` with
body `mixed search and non-search filters not supported`, or a WebSocket
subscription is closed with `error: mixed search and non-search filters not
supported`. Both relay entry points reject a filter list mixing a `search`
filter with a non-`search` filter before ever calling Postgres.

Also in this category: an empty or all-whitespace `search` string is
normalized to "no query" and short-circuits to zero hits with **no** SQL
round trip at all — this is documented behavior in `search-query`
(referenced above), not a failure.

If the caller is `buzz messages search`: it always sends a fixed
`kinds: [9, 40002, 45001, 45003]` filter and has no `--kinds` flag — this
repository's own documented gotcha. A report that "search doesn't find my
event of kind X" where X is outside that list is not a bug in search; it is
this command's fixed scope. The same applies to `--author` given as a
display name, which requires an exact case-insensitive match and errors
with a candidate list on ambiguity rather than guessing.

**Resolution for this branch:** correct the request shape (split mixed
filters into separate subscriptions/requests; pass a non-empty query; use a
kind inside the CLI's fixed set, or build a raw relay filter with explicit
`kinds` if a different kind must be searched). No relay or database state
needs to change.

### 3. Is this an index/allowlist problem?

Confirms as: a kind that should be searchable (by product expectation) never
surfaces in results, even though the same content is retrievable by
`messages get`/`messages thread`, and the query shape itself is not the
issue (branch 2 already ruled out). This is a schema-drift diagnosis, not a
query-shape one.

`events.search_tsv`'s indexing scope is not one fixed fact about "the"
relay — it depends on migration history and how the database was
provisioned:

- Migrations 0001 and 0005 define a **negative exclusion list**
  (privacy-sensitive kinds are excluded; everything else is indexed).
- Migration 0008 flips **only a database that was empty when that migration
  ran** to a **positive allowlist** (kinds 0, 9, 40002, 45001, 45003 only —
  everything else is excluded). A database that already had rows when 0008
  ran keeps the negative-exclusion-list behavior indefinitely, until an
  operator runs `scripts/maintenance/nip_rs_search_allowlist.sql` by hand.
  There is no automated convergence and no admin command that does this —
  it is a manual, out-of-band, downtime-bearing operation (see below).
- Migrations 0014 and 0033 each read whichever expression the database
  currently has and layer one more excluded kind onto it, preserving
  whichever of the two policies above that database was already on.

**To check which policy this database is on**, inspect the live generated
expression rather than assuming from the migration history alone:

```sql
SELECT pg_get_expr(d.adbin, d.adrelid)
FROM pg_attrdef d
JOIN pg_attribute a ON a.attrelid = d.adrelid AND a.attnum = d.adnum
WHERE d.adrelid = 'events'::regclass AND a.attname = 'search_tsv';
```

A `CASE WHEN kind IN (...)` returning `NULL` for a short, specific list is
the fresh-install positive allowlist; a `CASE WHEN kind IN (...)` returning
`NULL` for privacy-sensitive kinds only, with `to_tsvector(...)` as the
`ELSE`, is the legacy negative-exclusion-list expression.

**Resolution:** if the expected kind is legitimately excluded by design
(privacy-sensitive — see `privacy-filtering`, referenced above), this is not
a bug; say so. If the expected kind should be searchable but this database's
current expression excludes it because it is on the fresh-install allowlist
and the missing kind was never added, running
`scripts/maintenance/nip_rs_search_allowlist.sql` does **not** add a kind —
that script only re-applies the same fixed allowlist. Adding a new kind to
either policy is a **code and migration change** (a new migration following
the 0014/0033 pattern), not an operational runbook step; escalate to
whoever owns the affected feature rather than attempting it as an on-call
mitigation.

**If the live expression itself cannot be read at all** — the query above
returns no row, or a relay startup log shows
`events.search_tsv generated expression not found` — the column itself may
be missing or a prior migration failed partway. This is a schema-integrity
incident, not a routine allowlist gap: escalate per *Escalation* below
before attempting any DDL by hand.

### 4. Is this a permissions/scoping problem?

Confirms as: the caller gets fewer hits than an equivalent query run by
someone with broader access, or a specific expected hit is silently absent
while other hits from the same search text are present.

Two independent narrowing steps happen after Postgres returns candidates,
and either can explain a missing hit with no error anywhere:

- **Channel scope.** A hit whose `channel_id` is outside the caller's
  currently accessible-channel set is dropped. This is computed from active
  channel membership plus channels marked `open` — see `channel-scope`,
  referenced above, for the exact query. A user who was removed from a
  channel, or whose membership cache has not yet reflected a recent add,
  will not see that channel's hits.
- **Post-hit reauthorization.** Both search entry points refetch every
  candidate and re-run the same per-event visibility gate normal reads use
  (author-only kinds, persona/engram shared-gate, result-gated `#p` checks —
  see `result-reauthorization`, referenced above). A hit failing this check
  is dropped with a `continue`, never surfaced as an error or a "N results
  hidden" notice on either transport.

**Resolution:** confirm the caller's actual channel membership and identity
against the missing content's channel and any `#p`/author-only constraints
on its kind. If the caller believes they should have access, that is a
membership or authorization question, not a search defect — resolve access
first and re-run the search; do not conclude search is broken from a single
missing hit until access is confirmed correct.

## Mitigation and resolution

Apply the fix for whichever branch of *Diagnosis* matched, in this order of
preference:

1. **Query-shape (branch 2)** — correct the request; no relay or database
   change needed. Verify per *Verification of recovery* below.
2. **Permissions/scoping (branch 4)** — correct membership/authorization
   state through the normal channel-membership or moderation tooling this
   repository already has for that purpose; do not attempt to work around
   the search-side gate, since it exists specifically to prevent search from
   becoming a wider access boundary than direct reads.
3. **Index/allowlist (branch 3), expected exclusion** — no action; document
   the expected behavior back to the reporter.
4. **Index/allowlist (branch 3), genuine allowlist gap on a populated,
   brownfield database** — schedule
   `scripts/maintenance/nip_rs_search_allowlist.sql` as a maintenance-window
   operation. It is a full-table rewrite under `ACCESS EXCLUSIVE` with a
   `5s` lock timeout; event reads and writes block for its duration. Do
   **not** run it against a live, unscheduled window — its own header
   comment states this explicitly. This only converges a populated database
   to the existing fixed allowlist; it does not add a new kind to that
   allowlist (see branch 3's resolution).
5. **Schema integrity (branch 3, missing expression) or Postgres
   availability (branch 1)** — do not attempt ad hoc DDL against
   `search_tsv`. Escalate immediately per *Escalation* below; this is
   outside the scope of a search-specific mitigation.

## Verification of recovery

- For a query-shape or permissions fix: re-run the exact original query.
  `buzz --format compact messages search --query "<original text>"` (add
  `--author`/`--since`/`--limit` to match the original request) if the
  report came through the CLI; otherwise resubmit the same filter shape to
  whichever transport (`POST /query` or WebSocket `REQ`) the original report
  used. The manual smoke-test commands in `crates/buzz-cli/TESTING.md` (for
  example `buzz messages search --query "Hello" | jq .`) are a reasonable
  known-good baseline query to run alongside the original one, to confirm
  search is functioning at all before re-checking the specific case.
- For a maintenance-script allowlist convergence: re-run the `pg_get_expr`
  query from *Diagnosis* branch 3 and confirm the expression now matches the
  fixed allowlist (kinds 0, 9, 40002, 45001, 45003), then re-run the
  originally reported query and confirm the expected content now surfaces.
- For a schema-integrity or Postgres-availability incident: recovery
  verification is owned by whichever runbook or procedure resolved the
  underlying incident (see *Escalation*) — re-check `/_readiness` reports
  `"postgres": true`, then separately re-verify the search-specific pool by
  running a known-good search query end to end, since `/_readiness` does not
  cover the dedicated search pool (see *Diagnosis* branch 1).
- In every case, confirm the fix against the *reported* symptom specifically
  — a query-shape fix does not verify a permissions fix, and vice versa.

## Escalation

- **Postgres unavailable, or schema integrity broken** (*Diagnosis* branches
  1 and 3's missing-expression case): hand off to the Postgres-unavailable
  runbook. That runbook is tracked as issue #1224 in this repository
  (`task: document operations/runbooks/postgres-unavailable.md`) and is not
  yet a corpus node at this node's recorded revision, so it cannot be linked
  by id here — find it by that issue number or, once merged, by searching
  the corpus for its title. Do not duplicate Postgres-outage diagnosis in
  this node.
- **A new kind needs to be added to the search allowlist**, or the exclusion
  policy itself needs to change: this is a code and migration change (a new
  migration in the 0014/0033 pattern), not an on-call mitigation. Escalate
  to whoever owns the affected feature's event kind, per this repository's
  normal contribution process for adding a new event kind
  (`CONTRIBUTING.md`'s guidance on indexing a new kind for search).
- **A permissions/scoping question that is actually a moderation or
  membership dispute** (not a technical defect): escalate to whoever handles
  channel membership or moderation decisions for the affected community;
  this runbook only diagnoses whether search behaves consistently with the
  caller's actual access, not what that access should be.
- **Anything that does not resolve within one escalation hop above**: treat
  as an incident and follow this repository's normal incident process; this
  runbook does not define one of its own (see *Scope and omissions*).

## Evidence to preserve

Before restarting the relay, running the maintenance script, or otherwise
changing state, capture:

- The exact request that failed or returned unexpected results: the full
  filter JSON (WebSocket `REQ` or HTTP `POST /query` body), including
  `kinds`, `search`, `#h`, `authors`, `since`/`until`, and any
  `search_mode`/`page` bridge extensions.
- The relay's log lines for that request, if available — specifically any
  `NIP-50 search failed`, `NIP-50 batch fetch failed`, or `search error`
  line, which include the underlying `sqlx`/Postgres error detail.
- The output of the `pg_get_expr` query from *Diagnosis* branch 3, if that
  branch was reached, before any maintenance script changes it.
- The `/_readiness` JSON body at the time of the incident, if branch 1 was
  reached.
- Whether the affected client used the WebSocket or HTTP path, since the
  two fail differently (silent partial EOSE versus an explicit HTTP 500) and
  a postmortem needs to know which.

Do not capture or paste raw database credentials, connection strings, or the
contents of the environment file into an issue or incident record — link to
the relay's own structured logs or to `/_readiness` output instead of
transcribing configuration that could contain a secret.

## Scope and omissions

**This node covers** the trigger conditions, severity, and diagnostic
decision tree for a NIP-50 search failure or unexpected-result report
against this repository's relay, mitigation and resolution steps for each
diagnosed cause in executable order, how to verify recovery, and where to
escalate for causes outside search's own scope.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The FTS mechanism itself — the generated column, index, query construction, channel scoping, privacy exclusions, and post-hit reauthorization | The six `capabilities/search/*` nodes referenced above |
| Diagnosing or recovering from a Postgres outage affecting the whole relay, not only search | Issue #1224 (`operations/runbooks/postgres-unavailable.md`), unmerged at this node's recorded revision |
| Adding a new event kind to (or changing the policy of) the search allowlist | This repository's normal event-kind contribution process (`CONTRIBUTING.md`) — a code change, not an operational step |
| A general incident-response process (severity classification, communication, postmortem template) | Not established anywhere in this repository's corpus at this node's recorded revision |
| Desktop-side or mobile-side search UI behavior (query parsing, operators like `from:`/`in:`) | Out of scope for a relay-focused runbook; not investigated here |
| Monitoring, alerting, or dashboards for search latency or error rate | Not found anywhere in this repository at the recorded revision — see below |

**Expected but not verified when this node was written:**

- **No alerting rule, metric, or dashboard specific to search exists in this
  repository at the recorded revision.** A search across `crates/`,
  `.github/workflows/`, and this repository's observability layers found
  Prometheus metrics and OpenTelemetry tracing infrastructure generally, but
  nothing scoped to `buzz-search`, `search_tsv`, or NIP-50 specifically.
  This runbook is therefore triggered by a report, not by a page, and that
  is stated as a documented gap rather than assumed to be an oversight in
  this node.
- **No admin-facing search reindex, health, or statistics command was found
  anywhere under `crates/buzz-admin`.** The only operator-invoked
  remediation for allowlist drift is the maintenance script named above;
  whether that absence is intentional or simply not yet built was not
  established from any source available to this node.
- **This node's diagnosis tree was not exercised against a live failure.**
  The branches above are derived from reading the relay's and buzz-search's
  actual error-handling code paths and the migration history, not from
  observing a real incident of each kind; the first real use of each branch
  should be treated as evidence about this runbook, not only about the
  incident.
- **Whether `/_readiness` should be extended to probe the dedicated search
  pool was not resolved here.** This node names the gap (*Diagnosis* branch
  1) but does not propose or evaluate a fix, since that is an implementation
  change outside an operations runbook's scope.
- **Migration 0033's stated downtime warning ("expect relay downtime
  proportional to the size of events") was read from that migration's own
  comment, not independently measured against a populated database of any
  particular size.** The mitigation step above that schedules a maintenance
  window relies on that comment's own claim, not on this node's own
  benchmark.
