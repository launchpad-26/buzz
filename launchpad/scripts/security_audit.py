#!/usr/bin/env python3
"""CLI entrypoint for the #62 security audit. The contract and runner live in
security_audit_core.py; see that module's docstring for the report format and
status meanings, and for why this wrapper exists as a separate file.

Usage:
    python3 security_audit.py [repo-root]
"""

import sys

from security_audit_core import main

if __name__ == "__main__":
    sys.exit(main(sys.argv))
