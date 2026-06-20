# SPDX-License-Identifier: MIT
"""Tests for tools/check_versions.py (the version-consistency guard)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import check_versions as cv  # noqa: E402


def test_repo_is_consistent():
    # The committed repo must always satisfy the invariant the guard enforces.
    assert cv.main() == 0


def test_spec_regex_matches_header():
    text = (ROOT / "spec" / "feedpak-v1.md").read_text(encoding="utf-8")
    assert cv._SPEC_RE.search(text)


def test_readme_regex_matches_table():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert cv._README_RE.search(text)
