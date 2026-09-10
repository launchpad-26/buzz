---
title: "An uncited tagged claim before the first heading"
category: "tool-layer"
author: "the-professor"
generated_by: "the-professor"
generated_at: "2026-09-05T00:00:00Z"
---

Broken (behaviour: none).

<!-- professor:section sources="launchpad/agents/the-professor/tools/server.py@c552723#L144-L201" updated_by=the-professor updated_at=2026-09-05 -->
## A normal, compliant section afterward

`resolve_pin` calls `gh api repos/{repo}/commits/{ref}` and refuses to return a value
that is not exactly 40 hex characters (behaviour: launchpad/agents/the-professor/tools/server.py@c552723895f5bfbf399db7e3135a22026597e70a#L144-L201).
