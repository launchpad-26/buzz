"""Test package marker.

Without this file `python3 -m unittest discover` silently finds zero tests and
still exits 0 — discovery does not recurse into a directory that is not an
importable package, so the whole suite passes vacuously. Keep it.
"""
