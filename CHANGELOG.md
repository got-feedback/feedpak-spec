# Changelog

All notable changes to the feedpak format specification are documented here.

The format is licensed under [CC0-1.0](LICENSE) (prose) and [MIT](LICENSE-CODE) (schemas,
examples, code). This file follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the specification is versioned per [Semantic Versioning](https://semver.org/) — see
[spec §4](spec/feedpak-v1.md#4-versioning) for how format, side-file, and document versions
relate.

## [Unreleased]

## [1.6.0] - 2026-06-21

MINOR release under the new §4.2 *opt-in file-format relaxation* carve-out: the `.jsonc`
data-file extension (comment-annotated JSON), plus a docs-site version banner. No existing pack is
affected, and a comment-free `.jsonc` file is plain JSON — but a `.jsonc` file that actually
contains comments is **not** readable by a strict-JSON-only Reader; it requires a JSONC-aware
Reader. This is why `.jsonc` ships under an explicit, bounded carve-out rather than the ordinary
"older Readers keep working" minor rule (see the JSONC bullet below and spec §4.2 / §8).

### Added
- Docs site (no format change): a build-time version banner. The site now stamps the newest
  released `CHANGELOG.md` version (`SPEC_VERSION` env → `mkdocs.yml` `extra.spec_version` →
  `overrides/main.html`) into a top announcement bar, so the displayed version is deterministic
  and no longer depends on Material's client-side GitHub-release widget (which is cached in the
  browser's localStorage and could lag a release).
- **JSONC support** ([§2.2](spec/feedpak-v1.md#22-three-core-rules),
  [§3](spec/feedpak-v1.md#3-encodings-and-conventions),
  [§8](spec/feedpak-v1.md#8-reading-and-writing)): `.jsonc` files (C-style-commented JSON) are
  now accepted anywhere `.json` files are specified. Hand-edited data files MAY use the `.jsonc`
  extension to signal that they contain comments; Readers strip comments before parsing, and
  Writers SHOULD preserve them on round-trip. Only comments are permitted — trailing commas and
  other JSON5-style relaxations are not; after comment removal a `.jsonc` file MUST be strict JSON.
  The reference validator (`tools/validate.py`) parses `.jsonc` files accordingly. Shipped as a
  MINOR bump under the §4.2 opt-in-relaxation carve-out: no existing pack is affected, and a
  comment-free `.jsonc` file is plain JSON, but a `.jsonc` file that contains comments is readable
  only by Readers that implement the comment-stripping step (a plain JSON parser errors on `//`),
  so a Writer needing maximum reader compatibility SHOULD keep data files as comment-free `.json`.

## [1.5.0] - 2026-06-21

Additive (MINOR) release: per-note teaching marks. Backward-compatible — a 1.0.0 pack is also a
valid 1.5.0 pack, and older readers ignore the new optional note fields.

### Added
- **Per-note teaching marks** ([spec §6.2.2](spec/feedpak-v1.md#622-teaching-marks-fg-ch-sd)):
  three OPTIONAL note fields that annotate how a note is taught or displayed, never whether it was
  played correctly (the **honesty rule** — graders MUST NOT score them) — `fg` (fret-hand finger,
  `-1` unset / `0` thumb / `1`–`4` index→pinky, same convention as `template.fingers`), `ch`
  (strum-group key: notes sharing a value `≥ 0` are one strum/rake gesture, with `pkd` giving
  direction), and `sd` (scale degree as a chromatic offset `0`–`11` above the active
  [`keys.json`](spec/feedpak-v1.md#77-keysjson) tonic; derivable, so a Reader MAY compute it).
  Schema: `fg` / `ch` / `sd` on `$defs/note` in
  [`schemas/arrangement.schema.json`](schemas/arrangement.schema.json); exercised by the extended
  example pack (an Em-triad rake grouped by `ch`).

## [1.4.0] - 2026-06-20

Additive (MINOR) release: per-note bend shape. Backward-compatible — a 1.0.0 pack is also a valid
1.4.0 pack, and older readers ignore the new optional note fields.

### Added
- **Per-note bend shape** ([spec §6.2.1](spec/feedpak-v1.md#621-bend-shape-bt-bnv)): two OPTIONAL
  note fields complementing the scalar `bn` peak — `bt` (bend intent: up / release / pre-bend /
  pre-bend-release / round-trip) and `bnv` (a time-stamped `[{t, v}]` bend curve). Lets renderers
  draw the bend arc and graders judge the right pitch over the note. Schema: `bt` + `bnv` on
  `$defs/note` in [`schemas/arrangement.schema.json`](schemas/arrangement.schema.json); exercised
  by the extended example pack.

### Fixed
- §5.2 `tuning`: corrected the accepted-length range from "4–7 (4 = bass)" to **4–8**
  (4–6 = bass, 6–8 = extended-range guitar). 6-string bass and 7/8-string guitar were
  already permitted by the schema (`tuning` has no `maxItems`, note `s` has no maximum)
  and by the "Readers MUST NOT hard-code length 6" rule, but the prose under-stated the
  upper bound. Editorial clarification only — no on-disk format change.

## [1.3.0] - 2026-06-20

Tooling, docs, and example release — no on-disk format change (a 1.2.0 pack is also a valid
1.3.0 pack). Bundles the repository's testing/CI, the documentation site, release automation,
and a worked keyboard-notation example.

### Added
- Repository CI/CD (no format change): a `pytest` test suite for the reference validator
  (`tests/`), a Python 3.10–3.13 matrix and a `ruff` lint job in the validate workflow, and a
  GitHub Pages workflow that publishes the JSON Schemas so their `$id` URLs resolve. (Release
  automation is described in its own bullet below.)
- Docs site (no format change): the GitHub Pages site is now built with MkDocs Material
  (light/dark theme, search, rendered spec/hand-editing/changelog). `tools/gen_docs.py` assembles
  the site from the canonical sources and copies the schemas in verbatim so their hosted URLs are
  unchanged.
- Example (no format change): the extended pack now includes a notation-only `keys` arrangement
  (`type: piano`) with a two-stave `notation_<id>.json` part, so the §7.6 standard-notation /
  keyboard-arrangement path is exercised by the validator and CI.
- Release automation (no format change): a reviewed version bump now cuts its GitHub Release
  automatically on merge to `main` (idempotent release-on-merge), replacing the manual
  tag-triggered flow. A `tools/check_versions.py` CI guard enforces that the spec header, the
  README table, and the newest released `CHANGELOG.md` version stay in lockstep.

## [1.2.0] - 2026-06-20

Additive (MINOR) release: new optional song-level and per-arrangement timing data, all
backward-compatible with 1.0.0/1.1.0 readers.

### Added
- **Song-level `tempos` and `time_signatures`** in
  [`song_timeline.json`](spec/feedpak-v1.md#74-song_timelinejson) ([spec §7.4](spec/feedpak-v1.md#74-song_timelinejson)):
  two OPTIONAL time-ordered event arrays giving the song-wide tempo (`{time, bpm}`) and meter
  (`{time, ts: [num, den]}`) maps. Each event applies until the next, like `keys.json`. This gives
  guitar/game consumers a song-wide BPM and meter that previously existed only per-measure inside
  notation files. The file's `version` stays `1`.
- **Per-arrangement `tempos` override** ([spec §6.10](spec/feedpak-v1.md#610-per-arrangement-tempo-optional)):
  an arrangement JSON MAY carry its own `tempos` map; when present a Reader uses it for that chart
  and ignores the song-level tempo. Mirrors the §7.4 side-file-priority rule.
- **`keys.json` disambiguation note** ([spec §7.7](spec/feedpak-v1.md#77-keysjson)): clarifies that
  the key/scale track is instrument-independent and unrelated to a keyboard arrangement — a
  guitar-only pack can signal key changes with no keyboard part. No schema change.
- Schema and example updates: `tempos`/`time_signatures` in
  [`schemas/song-timeline.schema.json`](schemas/song-timeline.schema.json), a `$defs/tempoEvent`
  and `tempos` property in [`schemas/arrangement.schema.json`](schemas/arrangement.schema.json),
  exercised by the extended example pack (song timeline + a per-chart bass override).

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

[Unreleased]: https://github.com/got-feedback/feedpak-spec/compare/v1.6.0...HEAD
[1.6.0]: https://github.com/got-feedback/feedpak-spec/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/got-feedback/feedpak-spec/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/got-feedback/feedpak-spec/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/got-feedback/feedpak-spec/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/got-feedback/feedpak-spec/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/got-feedback/feedpak-spec/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/got-feedback/feedpak-spec/releases/tag/v1.0.0
