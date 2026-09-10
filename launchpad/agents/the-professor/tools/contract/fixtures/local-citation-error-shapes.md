---
title: "Fixture for step 4's local-citation error-shape tests"
category: "tool-layer"
author: "the-professor"
generated_by: "the-professor"
generated_at: "2026-09-05T00:00:00Z"
---

<!-- professor:section sources="some/path.py@c552723895f5bfbf399db7e3135a22026597e70a" updated_by=the-professor updated_at=2026-09-05 -->
## A local citation checked only against broken --target directories

This fixture exists solely for `check_professor.py`'s dedicated
local-citation error-shape test, which runs it against a nonexistent
`--target` path, an empty non-git directory, and an empty git repo with no
matching history -- never against this pack's own real repo
(behaviour: some/path.py@c552723895f5bfbf399db7e3135a22026597e70a).
