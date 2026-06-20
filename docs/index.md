# feedpak format specification

**feedpak** is an open, hand-editable package format for interactive music notation —
guitar/bass tab, standard notation, drum tabs, lyrics, vocal pitch, beats, sections, and the
audio stems that go with them. One `.feedpak` holds all the authored data for a single song.

The format is plain-text-first (a YAML manifest indexing JSON data files), self-describing, and
designed to be extended without breaking existing readers.

[Read the specification](feedpak-v1.md){ .md-button .md-button--primary }
[Hand-editing guide](hand-editing.md){ .md-button }

## Documents

- [Specification](feedpak-v1.md) — the authoritative, normative reference.
- [Hand-editing guide](hand-editing.md) — practical "edit your own pack" companion.
- [Changelog](changelog.md) — version history.

## Machine-readable schemas

JSON Schema (Draft 2020-12). These are the hosted, resolvable counterparts of each file's
`$id` / `$ref`:

- [manifest.schema.json](schemas/manifest.schema.json)
- [arrangement.schema.json](schemas/arrangement.schema.json)
- [song-timeline.schema.json](schemas/song-timeline.schema.json)
- [notation.schema.json](schemas/notation.schema.json)
- [drum-tab.schema.json](schemas/drum-tab.schema.json)
- [keys.schema.json](schemas/keys.schema.json)
- [lyrics.schema.json](schemas/lyrics.schema.json)
- [vocal-pitch.schema.json](schemas/vocal-pitch.schema.json)
- [vocal-pitch-contour.schema.json](schemas/vocal-pitch-contour.schema.json)

## License

Specification prose is dedicated to the public domain under
[CC0 1.0](https://github.com/got-feedback/feedpak-spec/blob/main/LICENSE); the schemas,
examples, and reference tooling are
[MIT](https://github.com/got-feedback/feedpak-spec/blob/main/LICENSE-CODE).
