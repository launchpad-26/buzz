---
title: "Bad YAML
category: "tool-layer"
author: "the-professor"
generated_by: "the-professor"
generated_at: "2026-09-05T00:00:00Z"
---

## An unclosed quote breaks YAML parsing

This page's frontmatter block has an unterminated quoted string, so it never
parses as valid YAML at all -- a distinct failure branch from "no frontmatter
block found" (opinion).
