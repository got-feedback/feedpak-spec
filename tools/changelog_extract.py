#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The feedpak authors
"""Print the CHANGELOG.md body for one version, for use as GitHub Release notes.

Slices the text between a `## [VERSION]` heading and the next `## [` heading.
Used by the release-on-tag workflow (.github/workflows/release.yml).

Usage:
    python tools/changelog_extract.py 1.2.0
    python tools/changelog_extract.py 1.2.0 path/to/CHANGELOG.md

Exit status is non-zero (with a message on stderr) only when the version's section
*heading* is absent. A heading that exists but has an empty body is valid (empty
release notes) and exits 0.
"""
from __future__ import annotations

import sys
from pathlib import Path


def has_section(text: str, version: str) -> bool:
    """True when a `## [VERSION]` heading exists, regardless of body content."""
    return any(line.startswith(f"## [{version}]") for line in text.splitlines())


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
        print("usage: changelog_extract.py VERSION [CHANGELOG.md]", file=sys.stderr)
        return 2
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
