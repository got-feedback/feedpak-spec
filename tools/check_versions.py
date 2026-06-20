#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The feedpak authors
"""Guard: the spec version, the README version table, and the newest released
CHANGELOG section must all agree.

This is the invariant the project releases under — a version-bump PR moves
`[Unreleased]` to a dated `## [X.Y.Z]` heading and bumps the spec header and the
README table together. Catching a mismatch here (in CI, pre-merge) is what keeps
the published version, the docs, and the release-on-merge workflow in lockstep.

    python tools/check_versions.py            # exit 0 if consistent, 1 otherwise
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from changelog_extract import latest_version  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

_SPEC_RE = re.compile(r"^- \*\*Specification version:\*\* (\d+\.\d+\.\d+)", re.MULTILINE)
_README_RE = re.compile(r"\*\*Specification version\*\*\s*\|\s*(\d+\.\d+\.\d+)")


def _read(rel: str) -> str | None:
    try:
        return (ROOT / rel).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read {rel}: {exc}", file=sys.stderr)
        return None


def _first(pattern: re.Pattern[str], text: str | None, label: str) -> str | None:
    if text is None:
        return None
    m = pattern.search(text)
    if not m:
        print(f"error: could not find the version in {label}", file=sys.stderr)
        return None
    return m.group(1)


def main() -> int:
    spec = _first(_SPEC_RE, _read("spec/feedpak-v1.md"), "spec/feedpak-v1.md")
    readme = _first(_README_RE, _read("README.md"), "README.md")
    changelog_text = _read("CHANGELOG.md")
    changelog = latest_version(changelog_text) if changelog_text is not None else None
    if changelog_text is not None and changelog is None:
        print("error: no released version section in CHANGELOG.md", file=sys.stderr)

    found = {"spec": spec, "README": readme, "CHANGELOG": changelog}
    if None in found.values():
        return 1
    if len(set(found.values())) != 1:
        print("error: version mismatch across sources:", file=sys.stderr)
        for src, ver in found.items():
            print(f"  {src:9} {ver}", file=sys.stderr)
        return 1
    print(f"versions consistent: {spec}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
