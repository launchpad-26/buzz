---
title: "How resolve-pin verifies GitHub API responses"
category: "tool-layer"
author: "the-professor"
generated_by: "the-professor"
generated_at: "2026-09-05T00:00:00Z"
---

<!-- professor:section sources="launchpad/agents/the-professor/tools/server.py@c552723#L144-L201" updated_by=the-professor updated_at=2026-09-05 -->
## Resolving a pin

`resolve_pin` calls `gh api repos/{repo}/commits/{ref}` and refuses to return a value
that is not exactly 40 hex characters, closing off a truncated or malformed API
response before it is mistaken for a real SHA (behaviour: launchpad/agents/the-professor/tools/server.py@c552723895f5bfbf399db7e3135a22026597e70a#L144-L201).
