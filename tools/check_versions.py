#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The feedpak authors
"""Guard: every place the *current* spec version is written must agree.

A version bump is a few hand-edits across several files; this guard fails CI
(pre-merge) if any one of them is missed, keeping the published version, the
docs, and the release-on-merge workflow in lockstep. It checks all of:

  - spec/feedpak-v1.md         header "Specification version"
  - spec/feedpak-v1.md §4.1     every `feedpak_version: "X"` (yaml block + the
                                writer-SHOULD line) — scoped to §4.1 so the §5
                                minimal-manifest example (deliberately 1.0.0) and
                                the historical version list are left alone
  - README.md                  the version table and the suggested-citation string
  - examples/extended.feedpak  manifest `feedpak_version` (the extended pack
                                tracks current; the minimal pack stays 1.0.0)
  - CHANGELOG.md               the newest released `## [X.Y.Z]` section

    python tools/check_versions.py            # exit 0 if consistent, 1 otherwise
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from changelog_extract import latest_version  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

_SPEC_HEADER_RE = re.compile(r"^- \*\*Specification version:\*\* (\d+\.\d+\.\d+)", re.MULTILINE)
_README_TABLE_RE = re.compile(r"\*\*Specification version\*\*\s*\|\s*(\d+\.\d+\.\d+)")
_README_CITE_RE = re.compile(r"(\d+\.\d+\.\d+), https://github\.com/got-feedback/feedpak-spec")
_FEEDPAK_VERSION_RE = re.compile(r'feedpak_version:\s*"(\d+\.\d+\.\d+)"')


def _read(rel: str) -> str | None:
    try:
        return (ROOT / rel).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read {rel}: {exc}", file=sys.stderr)
        return None


def _one(pattern: re.Pattern[str], text: str, label: str) -> str | None:
    m = pattern.search(text)
    if not m:
        print(f"error: could not find the version in {label}", file=sys.stderr)
        return None
    return m.group(1)


def _section(text: str, start: str, end: str) -> str:
    """The slice of `text` from the `start` heading up to the next `end` heading."""
    i = text.find(start)
    if i < 0:
        return ""
    j = text.find(end, i + len(start))
    return text[i:j] if j >= 0 else text[i:]


def collect() -> dict[str, str | None]:
    """Map each version-bearing location to the version it currently states
    (None when a file/pattern is missing). Multiple §4.1 hits get numbered keys."""
    found: dict[str, str | None] = {}

    spec_text = _read("spec/feedpak-v1.md")
    readme_text = _read("README.md")
    ext_text = _read("examples/extended.feedpak/manifest.yaml")
    changelog_text = _read("CHANGELOG.md")
    if spec_text is None or readme_text is None or ext_text is None or changelog_text is None:
        found["<unreadable file>"] = None
        return found

    found["spec header"] = _one(_SPEC_HEADER_RE, spec_text, "spec header")
    found["README table"] = _one(_README_TABLE_RE, readme_text, "README version table")
    found["README citation"] = _one(_README_CITE_RE, readme_text, "README citation")
    found["extended example"] = _one(
        _FEEDPAK_VERSION_RE, ext_text, "extended example feedpak_version")

    changelog = latest_version(changelog_text)
    if changelog is None:
        print("error: no released version section in CHANGELOG.md", file=sys.stderr)
    found["CHANGELOG"] = changelog

    section = _section(spec_text, "### 4.1.", "### 4.2.")
    hits = _FEEDPAK_VERSION_RE.findall(section)
    if not hits:
        print("error: no `feedpak_version` value found in spec §4.1", file=sys.stderr)
        found["spec §4.1"] = None
    else:
        for n, v in enumerate(hits, 1):
            found[f"spec §4.1 ({n})"] = v

    return found


def main() -> int:
    found = collect()
    if None in found.values():
        return 1
    if len(set(found.values())) != 1:
        print("error: version mismatch across sources:", file=sys.stderr)
        for label, ver in found.items():
            print(f"  {label:20} {ver}", file=sys.stderr)
        return 1
    print(f"versions consistent: {found['spec header']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
