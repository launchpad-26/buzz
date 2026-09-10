---
title: "A page that accidentally includes a literal password value"
category: "tool-layer"
author: "the-professor"
generated_by: "the-professor"
generated_at: "2026-09-05T00:00:00Z"
---

## Example configuration

A plain unquoted literal looks like `password: hunter2`. The same value in
JSON form looks like `{"password": "hunter2"}`. Some tools spell the
environment variable with an underscore instead: `DB_PASSWORD=hunter2`. These
are placeholder shapes only, never real credentials.
