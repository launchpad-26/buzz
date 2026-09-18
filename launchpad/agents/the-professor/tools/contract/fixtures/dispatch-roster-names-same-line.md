---
title: "A page naming two roster candidates on one line"
category: "tool-layer"
author: "the-professor"
generated_by: "the-professor"
generated_at: "2026-09-16T00:00:00Z"
---

## Who can approve a release

Documented by Alex Example — and release approval is restricted to Taylor Sample.

Those two names sit on one line on purpose. One is an attribution and one is
access-control data, and a finding carrying only a line number cannot tell them
apart -- which is what the column offsets exist to fix. These are placeholder
names only, used to exercise the roster-detection category -- not real people.

The em dash on that line is load-bearing, not typography. It is one Unicode
character but three UTF-8 bytes, and it sits between the two names, so the
second name's offsets differ depending on which unit is counted. An all-ASCII
line cannot tell a correct character-offset implementation from a byte-offset
one; this line can. Do not "tidy" it to a hyphen.
