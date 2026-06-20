#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The feedpak authors
"""Print the CHANGELOG.md body for one version, for use as GitHub Release notes.

Slices the text between a `## [VERSION]` heading and the next `## [` heading.
Used by the release-on-merge workflow (.github/workflows/release.yml), which also
calls `--latest-version` to find which version to release.

Usage:
    python tools/changelog_extract.py 1.2.0
    python tools/changelog_extract.py 1.2.0 path/to/CHANGELOG.md
    python tools/changelog_extract.py --latest-version       # print newest released version

Exit status is non-zero (with a message on stderr) only when the version's section
*heading* is absent. A heading that exists but has an empty body is valid (empty
release notes) and exits 0.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Matches a released section heading like "## [1.2.0]" (semver), but not "## [Unreleased]".
_VERSION_HEADING = re.compile(r"^## \[(\d+\.\d+\.\d+)\]")


def has_section(text: str, version: str) -> bool:
    """True when a `## [VERSION]` heading exists, regardless of body content."""
    return any(line.startswith(f"## [{version}]") for line in text.splitlines())


def latest_version(text: str) -> str | None:
    """The newest released version (first `## [X.Y.Z]` heading), or None if none."""
    for line in text.splitlines():
        m = _VERSION_HEADING.match(line)
        if m:
            return m.group(1)
    return None


def extract(text: str, version: str) -> str:
    body: list[str] = []
    capturing = False
    for line in text.splitlines():
        if line.startswith("## ["):
            if capturing:
                break
            capturing = line.startswith(f"## [{version}]")
            continue
        if capturing:
            body.append(line)
    return "\n".join(body).strip()


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: changelog_extract.py VERSION|--latest-version [CHANGELOG.md]",
              file=sys.stderr)
        return 2

    if argv[1] == "--latest-version":
        path = Path(argv[2]) if len(argv) > 2 else Path("CHANGELOG.md")
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"error: cannot read {path}: {exc}", file=sys.stderr)
            return 1
        version = latest_version(text)
        if version is None:
            print(f"error: no released version section in {path}", file=sys.stderr)
            return 1
        print(version)
        return 0

    version = argv[1].removeprefix("v")
    path = Path(argv[2]) if len(argv) > 2 else Path("CHANGELOG.md")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        return 1
    if not has_section(text, version):
        print(f"error: no CHANGELOG section for version {version}", file=sys.stderr)
        return 1
    print(extract(text, version))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
