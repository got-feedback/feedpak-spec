# SPDX-License-Identifier: MIT
"""Tests for tools/changelog_extract.py (release-notes slicing)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import changelog_extract as ce  # noqa: E402

SAMPLE = """\
# Changelog

## [Unreleased]

## [1.2.0] - 2026-06-20

### Added
- tempo + time signature maps

## [1.1.0] - 2026-06-20

### Added
- authors list
"""


def test_extracts_named_section():
    body = ce.extract(SAMPLE, "1.2.0")
    assert "tempo + time signature maps" in body
    assert "authors list" not in body          # stops at the next heading
    assert "## [" not in body                  # heading lines excluded


def test_extracts_older_section():
    assert "authors list" in ce.extract(SAMPLE, "1.1.0")


def test_unknown_version_is_empty():
    assert ce.extract(SAMPLE, "9.9.9") == ""


def test_extracts_repo_changelog_current_version():
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert ce.extract(text, "1.2.0").strip()    # the real changelog has a 1.2.0 section


def test_has_section_presence():
    assert ce.has_section(SAMPLE, "1.2.0")
    assert not ce.has_section(SAMPLE, "9.9.9")


def test_main_unknown_version_nonzero(capsys):
    rc = ce.main(["changelog_extract.py", "0.0.0", str(ROOT / "CHANGELOG.md")])
    assert rc == 1


def test_main_unreadable_file_nonzero(tmp_path, capsys):
    rc = ce.main(["changelog_extract.py", "1.2.0", str(tmp_path / "nope.md")])
    assert rc == 1
    assert "cannot read" in capsys.readouterr().err


def test_main_empty_but_present_section_succeeds(tmp_path, capsys):
    # A heading that exists with no body is valid (empty release notes), exit 0.
    cl = tmp_path / "CHANGELOG.md"
    cl.write_text("# Changelog\n\n## [3.0.0] - 2026-01-01\n\n## [2.0.0]\n- old\n", encoding="utf-8")
    rc = ce.main(["changelog_extract.py", "3.0.0", str(cl)])
    assert rc == 0
    assert capsys.readouterr().out.strip() == ""


@pytest.mark.parametrize("arg", ["1.2.0", "v1.2.0"])
def test_main_strips_v_prefix(arg, capsys):
    rc = ce.main(["changelog_extract.py", arg, str(ROOT / "CHANGELOG.md")])
    assert rc == 0
    assert capsys.readouterr().out.strip()
