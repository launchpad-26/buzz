"""Implementation modules for `tools/professor.py`'s four subcommands.

Split by the same local/network boundary `professor.py`'s own module docstring and
the redesign doc's §4 diagram describe: `netcmd` (resolve-pin, path-exists-at) is the
GitHub-API-backed half; `localcmd` (check-page, screen-content) never makes a network
call.
"""
