---
name: network
summary: Reachability, latency, loss, MTU and path faults between endpoints
layer: Network
---

# Network

## First five checks

1. Confirm the failure is reachability/latency/loss and not a symptom of something above the network — check whether the destination is reachable and responsive at all (ping, TCP handshake, or a basic connect test) before chasing anything else.
2. Trace the path from a working vantage point to a failing one and compare it against a known-good path for the same destination, looking for a hop that changed, dropped, or now differs between the working and failing paths.
3. Check DNS resolution for the affected name from both a working and a failing vantage point — a huge share of "the network is down" reports are actually a resolver returning a stale, wrong, or empty answer.
4. Check the health and session state of anything terminating or load-balancing the connection (load balancer target health, VIP status, BGP session state, firewall/ACL session table) — many "network" failures are really a control-plane or policy device silently dropping or diverting traffic.
5. Check for MTU/fragmentation and TLS handshake failures on the path — look for packets that connect but then hang or reset, which points to an oversized packet being dropped without a fragmentation-needed reply, or a TLS negotiation failing partway through.

## Evidence sources

- Router, switch, and firewall syslogs and SNMP/telemetry counters (interface errors, drops, discards, CRC errors)
- Load balancer and reverse proxy health-check logs and backend status pages
- BGP session logs and routing table dumps from edge and core routers
- DNS resolver query logs and authoritative zone data
- Flow data (NetFlow/sFlow/IPFIX) for traffic volume and path changes
- Packet captures taken at the client, at the server, and at any intermediate chokepoint
- Network monitoring/APM synthetic checks and latency/loss dashboards
- Change records for router, firewall, load balancer, and DNS configuration
- TLS/certificate expiry and handshake logs from terminating proxies or load balancers

## Common root causes in this layer

- A route withdrawn, flapped, or hijacked upstream (BGP instability, misconfigured route filter or route map)
- Asymmetric routing causing stateful firewalls to drop return traffic
- A firewall or ACL rule change blocking or rate-limiting legitimate traffic
- DNS record misconfiguration, stale cache, or a resolver outage returning wrong or no answers
- MTU mismatch or a path that silently drops ICMP "fragmentation needed" messages (black-hole MTU), causing large-packet flows to hang
- A load balancer marking healthy backends as unhealthy due to an overly strict or misconfigured health check
- Expired, mismatched, or misconfigured TLS certificate causing handshake failures at a terminating device
- Physical layer degradation (bad cable, failing transceiver, duplex mismatch) manifesting as intermittent loss or CRC errors
- Saturated link or interface causing queuing delay, loss, or micro-outages under load
- A recent change to routing, firewall, load balancer, or DNS configuration that coincides with onset

## Diagnostic commands and queries

- `ping <host>` — reachability and round-trip latency; note any tool with a flood mode (`ping -f`) is a load-generating variant and must not be used mid-incident.
- `traceroute <host>` / `tracert <host>` (or `mtr --report <host>` for a combined loss+latency-per-hop view) — path and per-hop loss/latency
- `dig <name>` / `nslookup <name>` — DNS resolution from a specific resolver or against a specific nameserver (`dig @<server> <name>`)
- `dig +trace <name>` — full resolution chain from root to authoritative, useful for isolating which resolver in the chain is wrong
- `tcpdump -i <iface> -n -c <n> host <ip>` (read-only capture; never run with `-w` to an unbounded file on a production box without a size/time cap) — inspect handshake, retransmits, resets
- `openssl s_client -connect <host>:<port>` — inspect TLS handshake and certificate presented by the remote end
- `curl -v --connect-timeout <n> https://<host>` — end-to-end connectivity, TLS, and HTTP response in one read-only call
- `ss -tan` / `netstat -tan` (read-only listing) — local socket and connection state; avoid confusing with `ss -K`, which kills sockets and is destructive
- `ip route get <ip>` / `ip addr show` — local routing decision and interface state, read-only
- `show ip bgp summary` / `show ip route <prefix>` (vendor CLI, read-only "show" commands) — BGP session state and route presence; never run the paired `clear`/`reset` form of these commands mid-incident, as clearing a session or route table is disruptive
- Load balancer/proxy status page or `show <lb> pool status` equivalent — read-only backend health state, distinct from any "drain" or "disable member" command, which is a mutating action
- Interface counters via `show interface <intf>` or SNMP polling — read-only error/discard/drop counters; do not pair with a `clear counters` command, which resets the very data being investigated

## Escalation signals

- Path, DNS, TLS, routing, and load-balancer checks are all clean, reachability and latency are normal, and the failure still reproduces — the fault is very likely in the application or database layer, not the network.
- The failure is scoped to a single host or a single process on otherwise-healthy infrastructure (other services on the same subnet, VLAN, or link are unaffected) — points to endpoint, OS, or application configuration rather than the network path.
- Traffic reaches the backend (visible in server-side logs or packet captures) but the application responds slowly or with errors — the network delivered the request; the fault is downstream.
- The issue only appears under authenticated or authorized requests while anonymous/unauthenticated traffic on the same path succeeds — points to identity or access-control layers rather than network reachability.
- Loss, latency, and error counters at every network hop are within normal baseline, but users report a functional failure (wrong data, application error page, failed transaction) — the transport succeeded; hand off to the application or storage owner.
