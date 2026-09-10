# ADR drafts raised by the #2071 architecture description

Four decisions the architecture could not make alone. All four were filed as ADR sub-issues of #2006
and **all four were decided on 2026-09-11, each to the recommendation below**, and recorded as
`launchpad/decisions/ADR-0061`–`ADR-0064`. These drafts are retained as the architecture's rationale;
the accepted records are authoritative. `components.md` §9 carries the #2072 gate.

| draft | issue | question | blocking | recommendation |
|---|---|---|---|---|
| [ADR-D](ADR-D.md) | [#2157](https://github.com/launchpad-26/buzz/issues/2157) | Verdict-authority absence | **blocking** | comment then authority-requirement escalation — accepted, [ADR-0061](../../../../decisions/ADR-0061-rqa-terminal-outcome-without-verdict-authority.md) |
| [ADR-E](ADR-E.md) | [#2158](https://github.com/launchpad-26/buzz/issues/2158) | `gh auth token` floor/ceiling | **blocking** | prove exercised authority; record residual — accepted, [ADR-0062](../../../../decisions/ADR-0062-rqa-credential-floor-and-ceiling.md) |
| [ADR-F](ADR-F.md) | [#2159](https://github.com/launchpad-26/buzz/issues/2159) | Record integrity | not blocking | hash chain plus operator-key HMAC — accepted, [ADR-0063](../../../../decisions/ADR-0063-rqa-record-provenance-integrity.md) |
| [ADR-G](ADR-G.md) | [#2160](https://github.com/launchpad-26/buzz/issues/2160) | Exact automatic remedy | **blocking** | exact files, closed formatter, semantic oracle — accepted, [ADR-0064](../../../../decisions/ADR-0064-rqa-exact-automatic-remedy.md) |

#2064 (repo-wide placement of policy and contract documents) is an existing open ADR the documents
reference; it is not redrafted here.
