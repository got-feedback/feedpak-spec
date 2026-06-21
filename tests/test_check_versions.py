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


def test_collect_covers_every_location_and_agrees():
    found = cv.collect()
    # All the locations the guard is supposed to watch are present...
    for label in ("spec header", "README table", "README citation",
                  "extended example", "CHANGELOG"):
        assert label in found, f"missing coverage for {label}"
    # ...§4.1 carries the version in more than one spot (yaml block + SHOULD line)...
    assert any(k.startswith("spec §4.1") for k in found)
    # ...and they all agree on a single version.
    assert None not in found.values()
    assert len(set(found.values())) == 1


def test_minimal_example_is_not_pinned_to_current():
    # The minimal pack deliberately stays at 1.0.0; the guard must not force it
    # to the current version (it isn't in the watched set).
    minimal = (ROOT / "examples" / "minimal.feedpak" / "manifest.yaml").read_text(encoding="utf-8")
    assert 'feedpak_version: "1.0.0"' in minimal
    assert "minimal example" not in cv.collect()


def test_section_slice_excludes_minimal_example():
    text = (ROOT / "spec" / "feedpak-v1.md").read_text(encoding="utf-8")
    # The end marker must actually exist, so the slice is genuinely bounded and not a
    # rest-of-document fallback (which could swallow the §5 minimal example).
    assert "### 4.2." in text
    section = cv._section(text, "### 4.1.", "### 4.2.")
    assert section.startswith("### 4.1.")
    assert "### 4.2." not in section
    # The §5 minimal-manifest example pins `feedpak_version: "1.0.0"`; it MUST be outside
    # the §4.1 slice, or the guard would read it as a current-version mismatch.
    assert 'feedpak_version: "1.0.0"' not in section
    # Every `feedpak_version` the slice *does* contain is the current (header) version.
    header = cv._SPEC_HEADER_RE.search(text).group(1)
    hits = cv._FEEDPAK_VERSION_RE.findall(section)
    assert hits and all(v == header for v in hits)


def test_regexes_match_real_files():
    spec = (ROOT / "spec" / "feedpak-v1.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    ext = (ROOT / "examples" / "extended.feedpak" / "manifest.yaml").read_text(encoding="utf-8")
    assert cv._SPEC_HEADER_RE.search(spec)
    assert cv._README_TABLE_RE.search(readme)
    assert cv._README_CITE_RE.search(readme)
    assert cv._FEEDPAK_VERSION_RE.search(ext)
