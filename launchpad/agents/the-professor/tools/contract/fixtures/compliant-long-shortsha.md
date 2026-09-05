---
title: "A marker using an 8-character abbreviated SHA"
category: "tool-layer"
author: "the-professor"
generated_by: "the-professor"
generated_at: "2026-09-05T00:00:00Z"
---

<!-- professor:section sources="launchpad/agents/the-professor/tools/server.py@c5527238#L144-L201" updated_by=the-professor updated_at=2026-09-05 -->
## An 8-character marker abbreviation

`resolve_pin` calls `gh api repos/{repo}/commits/{ref}` and refuses to return a value
that is not exactly 40 hex characters (behaviour: launchpad/agents/the-professor/tools/server.py@c552723895f5bfbf399db7e3135a22026597e70a#L144-L201).
