---
id: validator-fixture-leaky-schema-error
type: verification
status: active
origin: launchpad
audiences:
  - agent
evidence: "some/private/path/id_rsa"
---

Invalid fixture: `evidence` is a bare string where node.schema.json requires an array,
and the string is credential-shaped on purpose.

jsonschema renders this violation as `'some/private/path/id_rsa' is not of type
'array'` -- the offending value, verbatim. An earlier revision printed that message
straight through, and because a node with a schema error never reaches the citation
checks, it bypassed their redaction entirely: the one path guaranteed to leak was the
one the credential blocklist never got to see. A cross-model review panel found it.
