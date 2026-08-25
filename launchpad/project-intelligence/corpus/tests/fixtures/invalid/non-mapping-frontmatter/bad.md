---
- just
- a
- list
---

Invalid fixture: valid YAML, but the frontmatter parses to a list, not a mapping.
An independent review-final pass found this crashes load_nodes with an unhandled
AttributeError one line before jsonschema ever runs -- the sibling case, at the top
level, of the non-dict-entry crash the earlier fix round already caught nested
inside evidence[]/relationships[].
