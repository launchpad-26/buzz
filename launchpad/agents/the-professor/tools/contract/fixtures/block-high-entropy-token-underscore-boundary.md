---
title: "A high-entropy token whose keyword is joined by an underscore, not a space"
category: "tool-layer"
author: "the-professor"
generated_by: "the-professor"
generated_at: "2026-09-05T00:00:00Z"
---

## Configuring the client

Set the following before starting the client:
`access_token=Q7vN2rX9pL4mB8zK1wF6cH3jD5sA0uEo`. This is a placeholder shape
only, never a real credential. block-high-entropy-token.md already covers the
space-delimited `token = ...` shape, which would have matched even before the
underscore-boundary fix (step 3 of the 2026-09-06 fix round) -- this fixture
is specifically the `access_token=` shape that fix was for, since a plain
`\b` boundary never matched immediately before "token" inside "access_token"
at all (`_` is a word character).
