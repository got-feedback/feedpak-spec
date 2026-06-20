#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The feedpak authors
"""Assemble the MkDocs `docs/` tree from the canonical sources.

The spec prose lives in `spec/`, the changelog at the repo root, and the schemas in
`schemas/` — those stay the single source of truth. This script copies them into
`docs/` (the MkDocs `docs_dir`) and rewrites the few repo-relative links that would
otherwise break once rendered at the site root.

Generated outputs (`docs/feedpak-v1.md`, `docs/hand-editing.md`, `docs/changelog.md`,
`docs/schemas/`) are gitignored; `docs/index.md` and `mkdocs.yml` are committed. Run by
.github/workflows/pages.yml and reproducible locally before `mkdocs build`.

    python tools/gen_docs.py && mkdocs build
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
BLOB = "https://github.com/got-feedback/feedpak-spec/blob/main"

# Repo-relative links -> site-relative (or absolute GitHub) equivalents. Order matters:
# longer prefixes (LICENSE-CODE) before the shorter ones (LICENSE).
LINK_REWRITES = {
    # MkDocs strips the `<id>` in the §7.6 heading as an HTML tag, so its slug differs
    # from GitHub's; repoint the cross-links to the MkDocs anchor.
    "#76-notation_idjson": "#76-notation_json",
    "../schemas/": "schemas/",
    "../CHANGELOG.md": "changelog.md",
    "../LICENSE-CODE": f"{BLOB}/LICENSE-CODE",
    "../LICENSE": f"{BLOB}/LICENSE",
    "spec/feedpak-v1.md": "feedpak-v1.md",
    "spec/hand-editing.md": "hand-editing.md",
    "(LICENSE-CODE)": f"({BLOB}/LICENSE-CODE)",
    "(LICENSE)": f"({BLOB}/LICENSE)",
    "(tools/": f"({BLOB}/tools/",
    "(examples/": f"({BLOB}/examples/",
    "(CONTRIBUTING.md": f"({BLOB}/CONTRIBUTING.md",
    "(GOVERNANCE.md": f"({BLOB}/GOVERNANCE.md",
}


def _copy_md(src: Path, dest: Path) -> None:
    text = src.read_text(encoding="utf-8")
    for old, new in LINK_REWRITES.items():
        text = text.replace(old, new)
    dest.write_text(text, encoding="utf-8")


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    _copy_md(ROOT / "spec" / "feedpak-v1.md", DOCS / "feedpak-v1.md")
    _copy_md(ROOT / "spec" / "hand-editing.md", DOCS / "hand-editing.md")
    _copy_md(ROOT / "CHANGELOG.md", DOCS / "changelog.md")

    schemas_out = DOCS / "schemas"
    if schemas_out.exists():
        shutil.rmtree(schemas_out)
    schemas_out.mkdir()
    for schema in sorted((ROOT / "schemas").glob("*.json")):
        shutil.copy2(schema, schemas_out / schema.name)

    print(f"docs tree assembled in {DOCS}")


if __name__ == "__main__":
    main()
