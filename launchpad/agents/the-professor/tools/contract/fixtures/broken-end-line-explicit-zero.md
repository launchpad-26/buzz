---
title: "A citation whose end line is explicitly zero"
category: "tool-layer"
author: "the-professor"
generated_by: "the-professor"
generated_at: "2026-09-05T00:00:00Z"
---

<!-- professor:section sources="launchpad/agents/the-professor/tools/server.py@c552723#L1-L0" updated_by=the-professor updated_at=2026-09-05 -->
## An end line of zero must not silently fall back to the start line

`resolve_pin` validates that the SHA it returns is exactly 40 hex characters
(behaviour: launchpad/agents/the-professor/tools/server.py@c552723895f5bfbf399db7e3135a22026597e70a#L1-L0).
