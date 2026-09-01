---
name: endpoint
summary: Client-side faults — version skew, cache/profile corruption, agent interference, proxy/cert config, resource pressure, and policy push effects
layer: Endpoint and Client
---

# Endpoint and Client

## First five checks

1. Confirm the failure is scoped to one machine, one build/version, or a specific rollout ring rather than the whole user base — check the affected client's app/OS version and patch level against a known-good peer, since version skew and partial rollouts (staged updates, canary rings, delayed patch cycles) are the single most common source of "works for me, not for them."
2. Check for a recent group policy, MDM profile, or configuration push that lands on the affected machine's timeline — pull the device's applied-policy/profile history and compare the last-applied timestamp against the onset time, since a silent policy push is a frequent cause that leaves no visible error on the client itself.
3. Check for a security agent (EDR, AV, DLP) actively intercepting, quarantining, or blocking the affected process, file, or network call — review the agent's local event log for the affected process/file around the onset time, since endpoint security software is a common and easily overlooked interference source that looks like an application or network fault from the outside.
4. Check local disk space, memory pressure, and CPU load on the affected machine — a machine near capacity produces symptoms (hangs, timeouts, corrupted writes, silent failures) that are indistinguishable from an application or network fault until resource headroom is actually checked.
5. Compare the affected user profile and local cache against a known-good peer on the same build and policy, without clearing either — look for corrupted or abnormally sized profile/cache files, settings that diverge from the peer, or state left over from an interrupted update; a divergence implicates corrupted local state as the fault while leaving that state intact for whoever investigates how it got corrupted.

## Evidence sources

- Endpoint management / MDM console: enrollment status, applied profile and policy history, push timestamps, compliance state
- Group policy result logs (client-side) and the policy/GPO change history on the management server
- EDR/AV/DLP agent console and local agent event log: detections, quarantines, blocked actions, and policy version on the device
- OS and application event/system logs on the affected machine (Windows Event Log, macOS unified log, Linux journal)
- Local application logs, crash dumps, and profile/cache directory contents
- Proxy server and PAC file distribution logs; browser or OS-level proxy configuration on the affected machine
- Local certificate store contents and certificate/keychain error logs
- Software deployment/patch management system: rollout ring membership, version deployed per device, deployment timestamps
- Help desk / ticketing history for the affected user or device (recurring pattern, prior known issues)
- Local disk, memory, and CPU telemetry from the endpoint agent or OS performance counters

## Common root causes in this layer

- Version skew between clients — a staged rollout, delayed patch, or an unmanaged device running an older or newer build than the rest of the fleet
- Corrupted local cache, profile, or configuration state that a fresh profile or cache clear resolves
- EDR, antivirus, or DLP agent quarantining a file, blocking a process, or intercepting network traffic it misclassifies as a threat
- Incorrect or stale proxy configuration or PAC file logic routing traffic incorrectly or through a dead proxy
- An expired, untrusted, or missing certificate in the local certificate store or keychain, breaking TLS validation for one client
- A group policy or MDM profile push that silently changes a setting (proxy, certificate trust, firewall rule, registry key) affecting only the devices it targeted
- Disk space exhaustion, memory pressure, or CPU contention on the endpoint causing timeouts, failed writes, or silent crashes
- A device stuck in a partial or failed policy/profile application state, applying some settings but not others
- Local firewall or host-based security rule blocking a required port or destination that a peer machine allows
- Hardware degradation (failing disk, memory errors) manifesting as intermittent application failures rather than an outright crash

## Diagnostic commands and queries

- `Get-MpComputerStatus` (Windows Defender) or the equivalent AV/EDR console query — read-only status and last-scan/detection state; do not run a remediation or quarantine-release action from the same tool during triage
- Endpoint management console query for a device's applied profile list and last check-in time — read-only inventory lookup, distinct from any "push policy now" or "wipe device" action in the same console
- `gpresult /r` or `gpresult /h report.html` (Windows) — read-only report of applied group policy and the last policy refresh time; do not pair with `gpupdate /force`, which mutates state by re-applying policy mid-diagnosis
- `df -h` / `Get-PSDrive` — read-only disk space check; avoid running any cleanup or deletion command until the fault is understood
- `top` / `Get-Process | Sort-Object CPU -Descending` / Activity Monitor (read-only view) — CPU and memory pressure snapshot; do not kill processes from the same session during triage
- `certutil -store My` (Windows) / `security find-certificate -a` (macOS) — read-only listing of the local certificate store; never pair with the corresponding `-delete` or `-import` forms mid-incident
- `netsh winhttp show proxy` / `networksetup -getwebproxy <service>` (macOS) — read-only proxy configuration query; distinct from the `set` variants, which mutate configuration
- Browser's own proxy/PAC diagnostic page (e.g., `chrome://net-internals/#proxy`, read-only view) — shows the PAC result actually applied for a given URL
- `Get-EventLog` / `wevtutil qe` (Windows) or `log show` (macOS, read-only query) or `journalctl` (Linux, read-only query) filtered to the onset window — application, system, and security event history
- Endpoint agent's local diagnostic/support-bundle export command, where the vendor provides a read-only export — captures agent version, policy version, and recent detection history without altering agent state

## Escalation signals

- The same failure reproduces on a freshly imaged or known-good machine with an identical build, policy, and network path — the fault is not endpoint-local; it points to the application, network, or identity layer.
- Multiple unrelated endpoints across different builds, policies, and physical locations fail at the same time in the same way — a true endpoint-layer fault is device-specific; simultaneous fleet-wide failure points upstream (application, network, or identity/access).
- Clearing the local profile/cache, confirming clean resource headroom, and disabling the security agent (in a controlled test) all fail to change the symptom — the client is behaving correctly and forwarding the fault from somewhere else in the chain.
- The failure only occurs for authenticated or authorized actions while unauthenticated/local actions on the same device succeed — points to the identity or access layer, not the endpoint itself.
- Server-side logs show the request never arriving, or arriving malformed, from a client that is confirmed healthy, current, and unencumbered by agent or policy interference — hand off to the network layer to trace the path from there.
