# Changelog

All notable changes to the feedpak format specification are documented here.

The format is licensed under [CC0-1.0](LICENSE) (prose) and [MIT](LICENSE-CODE) (schemas,
examples, code). This file follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the specification is versioned per [Semantic Versioning](https://semver.org/) — see
[spec §4](spec/feedpak-v1.md#4-versioning) for how format, side-file, and document versions
relate.

## [Unreleased]

## [1.1.0] - 2026-06-20

Additive (MINOR) release: a new optional manifest field, backward-compatible with 1.0.0 readers.

### Added
- **Manifest `authors` list** ([spec §5.4](spec/feedpak-v1.md#54-authors)): an OPTIONAL
  top-level array crediting the people who authored or edited a feedpak — each entry carries a
  required `name` plus optional `role`, `email`, and `url`. Distinct from `artist` (the recording
  artist). Released as a MINOR bump (`feedpak_version` 1.1.0); older readers ignore the unknown
  key. Schema: a new `$defs/author` in [`schemas/manifest.schema.json`](schemas/manifest.schema.json);
  exercised by the extended example pack.
- [`spec/hand-editing.md`](spec/hand-editing.md) — a practical, vendor-neutral hand-editing
  guide (record/replace stems, edit metadata/cover/lyrics/tuning, re-zip for distribution),
  adapted from the feedback project's user guide with application-specifics removed. Linked
  from the README.

## [1.0.0] - 2026-06-19

Initial public release of the feedpak format specification.

### Added
- Normative specification: [`spec/feedpak-v1.md`](spec/feedpak-v1.md), with a Conformance
  section (RFC 2119 / RFC 8174), Reader/Writer roles, and a "this document is authoritative"
  stance independent of any implementation.
- **Built-in versioning**: top-level `feedpak_version` semver field in the manifest, a
  MAJOR/MINOR/PATCH compatibility policy, and explicit rules separating the format version,
  per-file side-file `version` integers, and the specification-document version.
- Manifest reference (§5), arrangement wire format (§6), and side-file schemas (§7):
  lyrics, vocal pitch, vocal pitch contour, song timeline, drum tab, notation, and
  key/scale annotations.
- JSON Schemas (Draft 2020-12) for the manifest and all structured files, in
  [`schemas/`](schemas/).
- Worked examples in [`examples/`](examples/): a minimal pack and an extended pack
  exercising the optional side-files.
- Reference validator [`tools/validate.py`](tools/validate.py), doubling as the CI gate.
- Repository governance: README, CONTRIBUTING (DCO + enhancement-proposal process),
  GOVERNANCE, CODE_OF_CONDUCT, and dual CC0/MIT licensing.

[Unreleased]: https://github.com/got-feedback/feedback-feedpak-spec/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/got-feedback/feedback-feedpak-spec/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/got-feedback/feedback-feedpak-spec/releases/tag/v1.0.0
