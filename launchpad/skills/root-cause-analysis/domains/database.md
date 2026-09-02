---
name: database
summary: Connection, locking, indexing, query plan, replication and storage faults inside a database engine
layer: Database
---

# Database

## First five checks

1. Check connection pool saturation on both the application side and the database side — a pool at or near its max, or a rising queue of waiters for a connection, explains a huge share of "everything is slow" and "intermittent timeout" reports before any query is even examined.
2. Check for blocking and deadlocks — list currently blocked sessions and what they are waiting on, and check for a recent deadlock in the engine's own log. A single long-held lock from one bad transaction can stall dozens of otherwise-healthy ones.
3. Check for a query plan regression — compare the current execution plan for the slow query against a known-good plan, and check when statistics were last updated on the tables involved. A stale or newly-recalculated statistics set silently flipping a plan from an index seek to a full scan is one of the most common "nothing changed but it got slow" causes.
4. Check replication lag and replica health if reads are served from a replica — a lagging or paused replica returns stale data or, once it catches up, dumps a burst of write load that looks like an unrelated primary slowdown.
5. Check storage and tablespace/filesystem free space, and disk latency — a data or log volume nearing full triggers autoextend stalls, forced checkpoints, or outright write failures, and elevated disk I/O latency underneath a healthy-looking query plan produces the same symptom as a bad plan.

## Evidence sources

- Database engine slow-query log and general/audit query log
- Connection pool metrics from the application (pool size, active/idle/waiting counts, wait time) and from the database (current connection count, max connections)
- Lock and wait-event views or system tables (blocking chains, wait types, lock wait duration)
- Query plan history or plan cache, and table/index statistics metadata (last updated timestamp, row count estimates)
- Replication status views (lag in bytes or seconds, replica state, last applied transaction)
- Storage and filesystem metrics (volume free space, autoextend events, I/O latency and queue depth)
- Database engine error and startup log (failover events, crash recovery, out-of-space errors)
- Change records for schema migrations, index changes, configuration changes, and statistics jobs
- APM or ORM-level query timing and error-rate dashboards

## Common root causes in this layer

- Connection pool exhaustion from a leak (connections not returned), an undersized pool, or a downstream slowdown holding connections open longer than normal
- Lock contention or a deadlock caused by a long-running transaction, a missing or overly broad index causing lock escalation, or a new access pattern that conflicts with an existing one
- A missing, unused, or newly-invalidated index causing a full table scan where a seek used to occur
- A query plan regression triggered by a statistics refresh, a schema change, a parameter-sniffing issue, or an engine upgrade that changed the optimizer's defaults
- Replication lag from a single-threaded replay bottleneck, a long-running transaction on the replica, network latency to the replica, or a schema change that locks on the replica
- Storage or tablespace exhaustion from unchecked log growth, a runaway temp/scratch space consumer, or a purge/archival job that stopped running
- An unplanned or flapping failover leaving the topology in a split or degraded state, or an application still pointed at the old primary
- A configuration change (connection limit, timeout, isolation level, buffer/cache size) that shifted behavior without a corresponding code change

## Diagnostic commands and queries

- List active/blocked sessions and what they're waiting on — e.g. `SHOW PROCESSLIST` (MySQL/MariaDB), `SELECT * FROM sys.dm_exec_requests WHERE blocking_session_id <> 0` (SQL Server), or a query against `pg_stat_activity` joined to `pg_locks` (PostgreSQL). Read-only; do not pair with a `KILL <id>` or `pg_terminate_backend()` call mid-diagnosis — that is the mutating sibling.
- Check current connection count and configured maximum — e.g. `SHOW STATUS LIKE 'Threads_connected'` and `SHOW VARIABLES LIKE 'max_connections'` (MySQL), or `SELECT count(*) FROM pg_stat_activity` (PostgreSQL). Read-only.
- Inspect the execution plan for a specific query — `EXPLAIN` (PostgreSQL, MySQL) or `SET SHOWPLAN_XML ON` followed by the query (SQL Server). Read-only; shows the planner's chosen plan without running the query. Do not reach for `EXPLAIN ANALYZE` instead — it actually executes the query, so it is not safe against a write statement or anything with side effects, and does not belong in a read-only diagnostic list.
- Check statistics freshness — e.g. query `pg_stat_user_tables` for `last_analyze`/`last_autoanalyze` (PostgreSQL), or `information_schema.STATISTICS` / `sys.dm_db_stats_properties` (MySQL/SQL Server). Read-only; do not confuse with `ANALYZE`, `UPDATE STATISTICS`, or `sp_updatestats`, which mutate statistics rather than report on them.
- Check replication status — `SHOW REPLICA STATUS` / `SHOW SLAVE STATUS` (MySQL), `SELECT * FROM pg_stat_replication` on the primary or `pg_last_wal_receive_lsn()`/`pg_last_wal_replay_lsn()` on the replica (PostgreSQL). Read-only.
- Check storage and tablespace usage — filesystem-level `df -h` on the data and log volumes, or engine-level views such as `pg_database_size()` / `information_schema.TABLES` for per-table size (MySQL). Read-only.
- Check for recent deadlocks — the engine's deadlock log or system view, e.g. `SHOW ENGINE INNODB STATUS` (MySQL, read-only report despite the imperative-sounding name) or the SQL Server deadlock graph in the system health extended event session. Read-only.
- Check index usage to spot an unused or missing index — e.g. `pg_stat_user_indexes` (PostgreSQL) or `sys.dm_db_index_usage_stats` (SQL Server) for scan/seek counts per index. Read-only.
- Check failover/topology state — the orchestrator's or cluster manager's status command (e.g. a Patroni, Orchestrator, or Always On availability group status view) reporting current primary/replica roles. Read-only; distinct from any `failover`, `promote`, or `switchover` command in the same tool, which changes topology.

## Escalation signals

- Connection pool, locking, plan, replication, and storage checks are all clean, query latency at the database is normal end to end, but the caller still reports the problem — the fault is very likely in the application layer (a slow serialization step, a chatty N+1 pattern outside the database, or a downstream call) rather than the database itself.
- The database is healthy and responsive from a local or same-host client, but remote application servers time out reaching it — points to the network layer (path, DNS, firewall, or load balancer in front of the database) rather than the database engine.
- Queries succeed and return correct results quickly, but callers are being rejected or intermittently denied — points to identity and access layers (expired credentials, revoked grants, certificate issues) rather than a database performance fault.
- The database itself reports normal CPU, memory, and I/O, but the underlying host or storage subsystem shows resource pressure (hypervisor steal time, noisy-neighbor contention, underlying SAN/array latency) — hand off to infrastructure or storage/cloud platform ownership rather than continuing to tune the database.
- The failure only appears for a specific client library, driver version, or connection string configuration while other clients against the same database are unaffected — points to the endpoint or application configuration layer, not the database.
