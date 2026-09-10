# ADR drafts raised by the #2071 architecture description

Five decisions the architecture could not make alone. All are filed as ADR sub-issues of #2006 with
the template's Decision outcome intentionally blank for a human. Local drafts preserve the
architecture's recommendation; `components.md` §9 is the authoritative #2072 blocking gate.

| draft | issue | question | blocking | recommendation |
|---|---|---|---|---|
| [ADR-D](ADR-D.md) | [#2157](https://github.com/launchpad-26/buzz/issues/2157) | Verdict-authority absence | **blocking** | comment then authority-requirement escalation |
| [ADR-E](ADR-E.md) | [#2158](https://github.com/launchpad-26/buzz/issues/2158) | `gh auth token` floor/ceiling | **blocking** | prove exercised authority; record residual |
| [ADR-F](ADR-F.md) | [#2159](https://github.com/launchpad-26/buzz/issues/2159) | Record integrity | not blocking | hash chain plus operator-key HMAC |
| [ADR-G](ADR-G.md) | [#2160](https://github.com/launchpad-26/buzz/issues/2160) | Exact automatic remedy | **blocking** | exact files, closed formatter, semantic oracle |
| [ADR-H](ADR-H.md) | [#2217](https://github.com/launchpad-26/buzz/issues/2217) | How a non-built-in harness is admitted to run | **blocking** | operator-declared `command` gated by the conformance pair — accepted, [ADR-0065](../../../../decisions/ADR-0065-external-harness-admission.md) |

#2064 (repo-wide placement of policy and contract documents) is an existing open ADR the documents
reference; it is not redrafted here.
