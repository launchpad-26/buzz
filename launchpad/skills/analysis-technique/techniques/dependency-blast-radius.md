---
name: dependency-blast-radius
summary: Map what each affected service shares and work inward to find the common dependency behind an apparently unrelated multi-service failure
reach-for-when:
  - lots of things broke at once and they seem unrelated
  - how far does this reach
  - three different applications failed within minutes of each other with no common owner
  - the on-call for each affected service swears their own change log is clean
evidence-required:
  - a list of every service, application or site reporting a fault, however unrelated they look
  - each affected service's dependency list — DNS resolvers, certificate authorities, identity providers, NTP sources, storage backends, egress paths, shared platforms
  - a rough onset time for each affected service, close enough to tell "same event" from "coincidence"
reduces-with: none
cost: medium
---

# Dependency and Blast Radius Mapping

## Reach for it when
Several services fail together and nobody on the bridge can name what connects them. This is the
"lots of things broke at once and they seem unrelated" call — payments, email and an internal
dashboard all degrade in the same ten minutes, and the three owning teams have never spoken to each
other before this incident. It is also the right move whenever someone asks "how far does this
reach" — before touching anything, before assuming the blast radius is limited to what has been
reported, because what has been reported is only what someone happened to notice first.

Reach for it before single-service techniques when the failing set spans more than one team,
platform or application. A shared dependency does not respect ownership boundaries, so the fix is
rarely inside any one of the affected services.

## Evidence it needs
The full list of what is reporting a fault — not just the loudest complaint. Under-scoping this list
is the most common way this technique fails: a service quietly degrading is easy to miss if nobody
thinks to ask it.

For each affected service, its dependency list: which DNS resolvers it uses, which certificate
authority issued its certificates, which identity provider it authenticates against, which NTP
source it syncs from, which storage backend or shared platform it sits on, and which egress path its
traffic takes. Where this list does not already exist, build it now — an architecture diagram, a
service catalog entry, or an on-call engineer who can name it from memory. A rough onset time for
each service is also needed, close enough to distinguish one event with a shared cause from several
coincidental faults happening near the same time.

## How to run it
1. List every service currently reporting a fault, including ones reported as "acting a bit odd"
   rather than fully down. Note each one's onset time.
2. For each affected service, list its dependencies across the categories that most often turn out
   to be shared: DNS resolvers, certificate authorities, identity providers, NTP sources, storage
   backends, and egress or network paths.
3. Intersect the lists. Any dependency that appears against more than one affected service is a
   candidate common cause.
4. For each candidate, check its own health and change history around the shared onset window: was
   it changed, restarted, failed over, or did it itself throw errors in that window?
5. Rank candidates by how many of the affected services they explain. A candidate that accounts for
   every affected service and no unaffected one is the strongest lead.
6. Confirm the leading candidate by checking a service that depends on it but was **not** reported as
   affected — if that service turns out to be quietly degraded too, the blast radius is larger than
   first reported, and this is itself part of the answer to "how far does this reach".
7. If no dependency appears against more than one affected service, stop mapping shared components
   and treat the simultaneity itself as the finding — see **Don't use it for**.

## Worked example
Within the same six-minute window, an internal email gateway starts rejecting client connections, a
VPN concentrator refuses new tunnels, and an internal API used by three unrelated applications starts
failing TLS handshakes. The three owning teams have no shared change window and no shared code.
Mapping dependencies: the email gateway, the VPN concentrator and the internal API all validate
client and server certificates against the same internal certificate authority. Checking that CA's
own health shows an intermediate certificate expired eleven minutes before the first report. A
fourth service, an internal metrics collector, also depends on the same CA but had not been reported
— checking it directly shows it has been silently failing scrape connections since the same minute.
The expired intermediate certificate is the common dependency; the blast radius includes the
unreported metrics collector.

## Done when
Every affected service has an entry in the dependency intersection, at least one candidate shared
dependency has been checked against its own health and change history for the onset window, and at
least one service that depends on the leading candidate but was not originally reported has been
checked to confirm whether it is also affected.

## Don't use it for
A fault confined to a single service with no other system showing symptoms. There is nothing to
intersect against, and forcing a dependency map onto one service just relabels its own internals as
"shared dependencies" — route to a technique built for a single failing case, such as
`fault-tree-analysis` or `five-whys`, instead.

The absence of an obvious shared dependency is itself evidence, not a dead end. If the intersection
in step 3 comes back empty even after checking DNS, certificate authorities, identity, NTP, storage
and egress, that is a signal the services share a trigger rather than a shared component — a common
change deployed independently to each of them, or a common external event such as a regional power
or network event, rather than a single dependency to fix. Route to `change-analysis` to check for a
trigger deployed to each service separately, or `timeline-reconstruction` to establish whether the
onsets are close enough in time to still be one event.
