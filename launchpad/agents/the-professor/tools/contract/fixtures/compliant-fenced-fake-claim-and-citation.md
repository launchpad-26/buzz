---
title: "A cited section whose fenced example contains fake claim tags and a citation"
category: "tool-layer"
author: "the-professor"
generated_by: "the-professor"
generated_at: "2026-09-05T00:00:00Z"
---

<!-- professor:section sources="launchpad/agents/the-professor/tools/server.py@c552723#L144-L201" updated_by=the-professor updated_at=2026-09-05 -->
## Resolving a pin, with an example of the tagging convention itself

`resolve_pin` calls `gh api repos/{repo}/commits/{ref}` and refuses to return a value
that is not exactly 40 hex characters (behaviour: launchpad/agents/the-professor/tools/server.py@c552723895f5bfbf399db7e3135a22026597e70a#L144-L201).

```markdown
Here is an example of this contract's own tagging convention, purely as
documentation, never a real claim in this section:

Broken (behaviour: none).

Also here is an example citation shape, never a real one:
some/other/path.py@deadbeefdeadbeefdeadbeefdeadbeefdeadbeef.
```

This closing sentence still belongs to the same section as the citation above,
not a new orphaned claim, and the fenced example's fake tag and citation must
not be counted against this section's real provenance marker (opinion).
