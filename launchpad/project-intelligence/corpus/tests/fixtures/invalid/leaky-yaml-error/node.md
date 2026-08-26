---
id: validator-fixture-leaky-yaml-error
evidence: [some/private/path/id_rsa
type: verification
---

Invalid fixture: the frontmatter is malformed YAML -- an unclosed flow sequence -- and
the line PyYAML chokes on contains a credential-shaped path on purpose.

PyYAML's exception text quotes that source line back, and an earlier revision printed
the exception verbatim, so this document leaked the path straight into CI output. It is
the same leak the schema-error path closed, reached through a different door: a document
that fails to PARSE never reaches schema validation, so that fix could not help it. An
independent cross-model review-final pass found it.
