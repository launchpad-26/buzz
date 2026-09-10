---
title: "A cited section followed by a tilde-fenced example with a # comment"
category: "tool-layer"
author: "the-professor"
generated_by: "the-professor"
generated_at: "2026-09-05T00:00:00Z"
---

<!-- professor:section sources="launchpad/agents/the-professor/tools/server.py@c552723#L144-L201" updated_by=the-professor updated_at=2026-09-05 -->
## Resolving a pin, with a tilde-fenced example

`resolve_pin` calls `gh api repos/{repo}/commits/{ref}` and refuses to return a value
that is not exactly 40 hex characters (behaviour: launchpad/agents/the-professor/tools/server.py@c552723895f5bfbf399db7e3135a22026597e70a#L144-L201).

~~~python
# This looks like a markdown heading but it is a Python comment inside a
# tilde-fenced code block, not a real section heading.
def example():
    pass
~~~

This closing sentence still belongs to the same section as the citation above,
not a new orphaned one (opinion).
