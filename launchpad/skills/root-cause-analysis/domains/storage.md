---
name: storage
summary: Capacity, throughput, path/LUN failover, filesystem and object-store faults on persistent storage
layer: Storage
---

# Storage

## First five checks

1. Check capacity and inode usage on every filesystem and volume in the failure path, not just the one the alert names — a full or inode-exhausted filesystem one hop away (a shared log volume, a temp directory, an underlying datastore) fails writes just as surely as the volume the application reports.
2. Check for a read-only remount in kernel/system logs — a filesystem that silently flips to read-only after a detected I/O error looks like an application failure (writes rejected, transactions failing) but is a storage-layer event, and it is the single highest-yield check for that specific symptom shape: "worked, then suddenly every write fails."
3. Check multipath/path state and recent failover events for the affected device or LUN — a path down or a failover in progress explains sudden latency spikes or transient errors even when capacity and the filesystem look fine.
4. Check for an active or recently-completed snapshot, backup, replication, or scrub job on the same volume or array — these are the most common source of "everything got slow with no code change," because they compete for the same IOPS and throughput as production traffic.
5. Check IOPS, throughput, and latency against the provisioned or throttling limit for the volume/array — a workload that grew past its provisioned ceiling (cloud burst credits exhausted, array queue depth saturated) degrades gradually and is easy to miss if you only look at whether the storage is "up."

## Evidence sources

- Filesystem and volume capacity/inode metrics (`df`, cloud volume/bucket usage dashboards, array capacity reporting)
- Kernel and syslog messages for I/O errors, remounts, and device state changes
- Multipath daemon logs and path/LUN state (e.g., `multipathd`, SAN switch port logs, HBA logs)
- Storage array or cloud provider performance metrics (IOPS, throughput, queue depth, latency, burst-credit balance)
- Backup, snapshot, and replication job schedules and logs
- Object store access logs and consistency/permission error responses (e.g., 403, 404-on-recently-written-object, version conflicts)
- RAID/array controller health and rebuild status
- Application and database logs for I/O timeouts, "read-only filesystem," or "no space left on device" errors
- Change records for storage provisioning, quota, snapshot schedule, or access-policy changes

## Common root causes in this layer

- Filesystem or volume filled to capacity, or inode exhaustion on a filesystem with many small files, even while raw capacity looks fine
- A detected disk or I/O error triggering an automatic read-only remount of the filesystem
- A snapshot, backup, or scrub job scheduled to run during peak load, saturating shared IOPS/throughput
- Multipath failover to a degraded or higher-latency path after a link, HBA, or switch fault, without a full outage
- Workload growth past a provisioned IOPS/throughput ceiling or exhausted cloud burst-credit balance, causing throttling
- A failing or predictively-failing physical disk causing elevated latency or a RAID rebuild that itself consumes bandwidth
- Object store eventual-consistency window causing a just-written object to appear missing or stale to a subsequent read
- An access-policy or permission change (bucket policy, ACL, IAM role) causing object store requests to start failing with permission errors
- Orphaned snapshots, old volumes, or log/temp file growth silently consuming capacity over time until a threshold is crossed

## Diagnostic commands and queries

- `df -h` / `df -i` — filesystem capacity and inode usage; read-only.
- `du -sh <path>` (on a specific suspect directory, not a full-disk recursive scan mid-incident) — find what is consuming space; read-only but can be I/O-intensive on a large tree, so scope it narrowly.
- `mount | grep -w ro` or checking `/proc/mounts` for a `ro` flag — confirm whether a filesystem has remounted read-only; read-only check.
- `dmesg -T` / `journalctl -k` — kernel messages for I/O errors, remounts, and device resets; read-only.
- `multipath -ll` — current path state and failover status for multipathed devices; read-only. Do not confuse with `multipath -F`, which flushes path maps and is disruptive.
- `iostat -xz 1` / `sar -d` — per-device IOPS, throughput, latency, and queue depth over time; read-only sampling.
- `smartctl -a /dev/<dev>` — drive health and predictive-failure attributes; read-only. Avoid `smartctl -t` self-test invocations mid-incident, as long-running tests add load to a device already under investigation.
- `lsblk` / `lsscsi` — enumerate block devices and their current state; read-only.
- Array or cloud-provider console/API "describe volume" or "get metrics" calls (e.g., a read-only `describe-volumes`/`get-metric-statistics` style call) — provisioned limits, current utilization, burst-credit balance; read-only, distinct from any `modify-volume` or `resize` action.
- Snapshot/backup job scheduler status or job history query — confirm whether a job is currently running or recently completed; read-only listing, distinct from any command that creates, deletes, or restores a snapshot.
- Object store `head-object` / `list-objects` / access-log query — check object existence, metadata, and recent permission-denied responses; read-only, distinct from any `put`, `delete`, or `put-bucket-policy` call.
- RAID controller status query (e.g., a vendor `--detail --state` or read-only status subcommand) — array and rebuild health; read-only, distinct from any command that initiates a rebuild, forces a disk offline, or rewrites parity.

## Escalation signals

- Capacity, inode usage, path state, IOPS/throughput, and read-only status all check out clean, yet the application still reports I/O errors or timeouts — the fault is likely in the application's own connection or file-handle management, not the storage layer.
- The storage layer reports normal latency and no errors, but a specific application or database process is slow or hung — points to the application or database layer, since the storage system delivered the I/O successfully.
- The failure only affects requests going through a particular network path or endpoint to reach the storage (e.g., an NFS mount over a specific link, or an object store reachable only via a particular gateway), while local or alternate-path access is unaffected — points to the network layer rather than the storage system itself.
- Object store requests fail with authentication or authorization errors while object existence and consistency are confirmed fine — points to the identity/access layer (credentials, IAM role, bucket policy principal) rather than storage.
- Multiple unrelated volumes or filesystems across different hosts degrade at the same time with no shared storage backend or array — points to a broader infrastructure or platform issue (hypervisor, cloud region event) rather than a fault isolated to this storage layer.
