<!--
SPDX-License-Identifier: CC0-1.0
This specification text is dedicated to the public domain under CC0 1.0.
The JSON Schemas, examples, and reference code that accompany it are MIT-licensed
(see LICENSE-CODE).
-->

# feedpak Format Specification

- **Specification version:** 1.0.0
- **Format major version:** 1
- **Status:** Draft
- **Date:** 2026-06-19
- **Editors:** The feedpak authors
- **License:** [CC0 1.0 Universal](../LICENSE) (this document)
- **Machine-readable schemas:** [`schemas/`](../schemas/) (MIT)

## Abstract

**feedpak** is an open, hand-editable package format for interactive music notation —
guitar/bass tab, standard notation, drum tabs, lyrics, vocal pitch, beats, sections, and the
audio stems that go with them. A feedpak holds the authored data for a single song. The format
is plain-text-first (YAML index + JSON data), self-describing, and designed to be extended
without breaking existing readers.

This document is the **authoritative reference** for the on-disk format. It is independent of
any single implementation: anyone may read, write, implement, or extend feedpak under the terms
above, with no obligation to any project.

---

## 1. Conformance

### 1.1. Requirement keywords

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**,
**SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be
interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
[RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they appear in all
capitals, as shown here.

### 1.2. Roles

- A **Reader** is any program that opens a feedpak and consumes its data.
- A **Writer** is any program that produces a feedpak.
- A **conformant feedpak** is a package that satisfies every MUST in this document.

A conformant Reader **MUST NOT** reject a feedpak solely because it carries keys, files, or
fields the Reader does not recognise (see [§4, Versioning](#4-versioning) and
[§9, Extending the format](#9-extending-the-format)). Forward-compatibility through ignored-but-
preserved unknown data is a load-bearing property of this format.

### 1.3. What this document does and does not govern

This specification governs the **bytes of the package on disk** — its structure, its files, and
the schemas of those files. It does **not** govern any runtime transport, API, or rendering
behaviour an application layers on top. Where such implementation detail is informative, it is
confined to a clearly-labelled **non-normative** appendix (see [Appendix A](#appendix-a-non-normative--streaming-and-runtime-notes)).

---

## 2. Format at a glance

A feedpak exists in **two interchangeable forms** that hold identical contents:

| Form | What it is | Used for |
|---|---|---|
| **Directory** | A folder named `*.feedpak/` containing the files below | Authoring, hand editing, tooling development |
| **Zip archive** | A `.feedpak` file (a ZIP archive with the same files inside) | Distribution |

A Reader **MUST** accept both forms and **SHOULD** treat them as equivalent. A Reader that
unpacks the zip form to a cache **SHOULD** key that cache on the archive's size and
modification time so a re-packed archive is re-read.

### 2.1. Directory layout

```
my-song.feedpak/
├── manifest.yaml             # REQUIRED — all metadata + the file index
├── arrangements/
│   ├── lead.json             # One JSON per playable arrangement
│   ├── rhythm.json
│   └── bass.json
├── stems/
│   ├── full.ogg              # Mixed audio (single-stem packs); may be absent after stem splitting
│   ├── guitar.ogg            # Optional individual stems
│   ├── bass.ogg
│   ├── drums.ogg
│   ├── vocals.ogg
│   └── other.ogg
├── lyrics.json               # OPTIONAL — syllable-level lyrics
└── cover.jpg                 # OPTIONAL — album art
```

### 2.2. Three core rules

1. **`manifest.yaml` is the index.** Nothing inside a feedpak is auto-discovered by scanning —
   every consumed file is referenced from the manifest. Readers **MUST NOT** rely on filename
   conventions to locate data; they **MUST** resolve files through the manifest. (Writers MAY
   use the conventional filenames shown here, but Readers MUST follow the manifest's pointers.)
2. **Paths in `manifest.yaml` are POSIX-style relative paths** from the feedpak root: forward
   slashes, no leading `/`, no `..` segments, no drive letters, no backslashes. Readers **MUST**
   reject paths that escape the package root.
3. **YAML for the manifest, JSON for data files.** The manifest is YAML so it is comfortable to
   hand-edit; all structured data files are JSON so they are fast to parse and round-trip. A
   YAML manifest is, by [YAML 1.2](https://yaml.org/spec/1.2.2/) rules, valid against the
   JSON-Schema definitions in [`schemas/`](../schemas/) (YAML is a JSON superset for this
   purpose).

---

## 3. Encodings and conventions

- **Text files** (`manifest.yaml`, all `*.json`) **MUST** be UTF-8 encoded. A Writer **SHOULD
  NOT** emit a byte-order mark.
- **Time** is always expressed in **seconds as a JSON number** (floating point), measured from
  the start of the song's audio. Time fields are named `t` or `time`. Writers **MUST NOT** use
  milliseconds, ticks, or sample counts.
- **Field names** in hot-path data (notes, chords, hits, beats) are deliberately short because
  they may be repeated tens of thousands of times in one file. Writers **MUST NOT** expand
  them. One-off metadata MAY use long, descriptive names.
- **Audio stems** are OGG (Vorbis) by convention; a quality around `-q:a 5` balances size and
  fidelity. **Cover art** is JPEG or PNG, conventionally square, 500–1500 px on a side.
- **Unknown keys / files / fields** are reserved for forward-compatibility. Readers **MUST**
  ignore them rather than error, and Writers that copy or re-emit a feedpak **SHOULD** preserve
  them verbatim.

---

## 4. Versioning

feedpak distinguishes **three independent version axes**. Conflating them is the most common
mistake when implementing the format, so they are defined separately here.

### 4.1. Format version — `feedpak_version`

The manifest **SHOULD** carry a top-level `feedpak_version` key whose value is a
[Semantic Versioning 2.0.0](https://semver.org/) string (for example `"1.0.0"`). It declares
which version of *this format* the package conforms to.

```yaml
feedpak_version: "1.0.0"
```

- A Writer producing a feedpak that conforms to this document **SHOULD** set
  `feedpak_version: "1.0.0"`.
- If `feedpak_version` is **absent**, a Reader **MUST** treat the package as `"1.0.0"`. (This
  makes every package authored before the field existed a valid 1.0.0 package.)
- The value **MUST** be a valid semver string when present. A Reader **MUST** reject a value
  that is not parseable as semver, or **MAY** fall back to treating the package as `"1.0.0"`
  with a logged warning.

### 4.2. Compatibility policy

Changes to the format are released under semver semantics, applied to `feedpak_version`:

| Change | Bump | Meaning |
|---|---|---|
| **MAJOR** (`2.0.0`) | breaking | Required structure or semantics changed. Existing packages may need regeneration. |
| **MINOR** (`1.1.0`) | additive | New OPTIONAL manifest keys or side-files. Older Readers keep working by ignoring them. |
| **PATCH** (`1.0.1`) | editorial | Clarifications, fixed wording, metadata-only adjustments. No schema change. |

**Reader rules.** A Reader that supports feedpak major version *X*:

- **MUST** accept any package whose declared major version is *X*, regardless of its minor or
  patch (it ignores unknown minor additions per [§1.2](#12-roles)).
- **SHOULD** warn, and **MAY** refuse with a clear error, when a package declares a major
  version **greater** than *X*.
- **MAY** accept a package whose major version is **less** than *X*, applying the
  backward-compatibility provisions this document defines.

**Writer rules.** A Writer **MUST NOT** introduce a backward-incompatible structural change
without bumping the **major** version. Additive changes (new optional keys/files) **MUST** be
released as a **minor** bump and **MUST** be safe for an older Reader to ignore.

### 4.3. Side-file schema versions

Several side-files carry their own integer `version` field at their top level
(`lyrics`/`vocal_pitch`/`song_timeline`/`drum_tab`/`notation_<id>` — see [§7](#7-side-files)).
These are **per-file schema versions** and are **orthogonal** to `feedpak_version`:

- They are plain integers (`1`, `2`, …), not semver, and start at `1`.
- They are bumped only when *that file's* entry shape changes incompatibly.
- A Reader **MUST NOT** assume any relationship between a side-file's `version` and the
  package's `feedpak_version`. Every new side-file **SHOULD** include `"version": 1`.

### 4.4. Specification-document version

This published document has its own version (shown in the header, e.g. `1.0.0`) tracking the
prose, schemas, and examples. It matches the format `major.minor` it describes. Major revisions
of the format are published as new documents (`spec/feedpak-v2.md`); minor and patch revisions
update this document in place and are recorded in [`CHANGELOG.md`](../CHANGELOG.md). Each
published version is frozen with a git tag (`v1.0.0`).

---

## 5. `manifest.yaml`

The manifest is the only REQUIRED file. It carries the song's metadata and indexes every other
file in the package.

Minimal valid manifest:

```yaml
feedpak_version: "1.0.0"
title: "Black Hole Sun"
artist: "Soundgarden"
duration: 320.5
arrangements:
  - id: lead
    name: Lead
    file: arrangements/lead.json
    tuning: [0, 0, 0, 0, 0, 0]
    capo: 0
stems:
  - id: full
    file: stems/full.ogg
    default: true
```

### 5.1. Top-level keys

| Key | Type | Required | Description |
|---|---|---|---|
| `feedpak_version` | string (semver) | SHOULD | Format version the package conforms to (see [§4.1](#41-format-version--feedpak_version)). Absent ⇒ `"1.0.0"`. |
| `title` | string | **yes** | Song title. |
| `artist` | string | **yes** | Artist name. |
| `album` | string | no | Album. |
| `year` | int | no | Release year. |
| `duration` | number | **yes** | Song length in seconds. |
| `arrangements` | list | **yes** | Playable arrangements (see [§5.2](#52-arrangements)). MUST be non-empty *or* an arrangement MUST be derivable from a `notation:`-only entry. |
| `stems` | list | **yes** | Audio stems (see [§5.3](#53-stems)). MUST be non-empty. |
| `stem_separation` | object | no | Provenance metadata when stems were produced by an automated separation engine. See [§5.3.1](#531-stem_separation). |
| `lyrics` | string (path) | no | Path to a lyrics JSON file (see [§7.1](#71-lyricsjson)). |
| `lyrics_source` | string | no | Origin of the lyrics: `authored`, `transcribed`, or `user`. Absent ⇒ treat as `authored`. See [§7.1](#71-lyricsjson). |
| `lyric_transcription` | object | no | Provenance metadata when lyrics came from an automated transcription engine. See [§7.1.1](#711-lyric_transcription). |
| `vocal_pitch` | string (path) | no | Path to per-syllable vocal pitch JSON (see [§7.2](#72-vocal_pitchjson)). |
| `pitch_extraction` | object | no | Provenance metadata when vocal pitch was extracted by an automated engine. See [§7.2.1](#721-pitch_extraction). |
| `vocal_pitch_contour` | string (path) | no | Path to a fine-grained pitch-contour JSON (see [§7.3](#73-vocal_pitch_contourjson)). |
| `cover` | string (path) | no | Path to cover image (JPEG/PNG). |
| `preview` | string (path) | no | Path to a short preview audio clip (OGG) for hover-to-listen UIs. |
| `song_timeline` | string (path) | no | Path to a song-wide beats/sections file (see [§7.4](#74-song_timelinejson)). Takes priority over beats/sections embedded in arrangement JSON. |
| `drum_tab` | string (path) | no | Path to a drum-tab file (see [§7.5](#75-drum_tabjson)). |
| `keys` | string (path) | no | Path to a key/scale-annotation file (see [§7.7](#77-keysjson)). |

Any key not listed here is an **extension key** and **MUST** be ignored by Readers that do not
understand it (see [§9](#9-extending-the-format)).

### 5.2. `arrangements[]`

Each entry describes one playable arrangement and points at its JSON file:

```yaml
arrangements:
  - id: lead                     # filesystem-safe stable id, used for filenames
    name: Lead                   # display name
    file: arrangements/lead.json
    tuning: [0, 0, 0, 0, 0, 0]   # six semitone offsets from E A D G B E
    capo: 0
    centOffset: 0.0              # OPTIONAL float, cents; default 0.0
```

| Field | Type | Default | Notes |
|---|---|---|---|
| `id` | string | — | **REQUIRED.** Stable, filesystem-safe, lowercase identifier; used in filenames and referenced by consumers. |
| `name` | string | `id` | Display name. |
| `file` | string (path) | — | Path to the arrangement JSON (see [§6](#6-arrangement-json)). MAY be omitted only when `notation` is present (see below). |
| `tuning` | int[] | `[0,0,0,0,0,0]` | Semitone offsets from standard `E2 A2 D2 G3 B3 E4`. Six elements is the standard convention; 4–7 are accepted (4 = bass). Readers **MUST NOT** hard-code length 6. |
| `capo` | int | `0` | Capo fret. |
| `centOffset` | number | `0.0` | Pitch-shift in cents. Common values: `-1200.0` (one octave down for extended-range bass), small non-zero values for non-A440 reference pitch (e.g. A443 ≈ `+11.8`). |
| `type` | string | — | OPTIONAL instrument hint (`guitar`, `bass`, `piano`, `violin`, …). |
| `notation` | string (path) | — | OPTIONAL path to a standard-notation file for this arrangement (see [§7.6](#76-notation_idjson)). When present, `file` MAY be omitted and the arrangement is notation-only. |

Manifest-level `tuning`, `capo`, and `centOffset` **override** any equivalents embedded inside
the arrangement JSON; the in-JSON values are fallbacks.

### 5.3. `stems[]`

```yaml
stems:
  - id: full
    file: stems/full.ogg
    default: true        # plays by default when the song opens
  - id: drums
    file: stems/drums.ogg
    default: false
```

| Field | Type | Default | Notes |
|---|---|---|---|
| `id` | string | — | **REQUIRED.** Stable identifier referenced by consumers. |
| `file` | string (path) | — | **REQUIRED.** Path to the audio file. |
| `default` | boolean | `false` | Whether this stem is enabled when the song opens. |

`default` is logically boolean. For hand-edited convenience, Readers **MUST** also accept the
case-insensitive strings `"true"`/`"false"`, `"on"`/`"off"`, and `"yes"`/`"no"`, mapping them to
the obvious boolean. Writers **SHOULD** emit a real boolean or `"on"`/`"off"`.

`stems` **MUST** be non-empty. There is no required `id` or filename: a freshly converted pack
typically has a single `{id: full, file: stems/full.ogg}` entry; after stem splitting, `full`
is commonly replaced by per-instrument entries (`guitar`, `bass`, `drums`, `vocals`, `other`,
`piano`, …). No entry is guaranteed to be present beyond the non-empty requirement.

#### 5.3.1. `stem_separation`

When stems were produced by an automated source-separation engine, an OPTIONAL top-level
`stem_separation` object records the provenance:

```yaml
stem_separation:
  engine: demucs           # stable engine id
  model: htdemucs_6s       # engine-specific model name
  version: "1.0.0"         # semver for the stem-artifact contract
```

| Field | Type | Notes |
|---|---|---|
| `engine` | string | Stable identifier for the separation engine. |
| `model` | string | Engine-specific model id used for this split. |
| `version` | string (semver) | Version of the producer's stem-artifact contract, independent of the upstream engine version. Bump: patch = metadata-only, minor = backward-compatible additions, major = stem set / packaging / post-processing changed and existing splits should be regenerated. |

Omitted for single-stem packs and for hand-recorded or hand-edited stems. The three fields
together form a natural cache key: a consumer regenerating stems can treat any change among
them as a cache miss.

---

## 6. Arrangement JSON

Arrangement files (`arrangements/<id>.json`) carry the playable note/chord data for one
arrangement — the **wire format**. This document defines that format; it is the authoritative
reference for it.

### 6.1. Top-level shape

```jsonc
{
  "name": "Lead",
  "tuning": [0, 0, 0, 0, 0, 0],
  "capo": 0,
  "centOffset": 0.0,           // OPTIONAL, float cents, default 0.0
  "notes":      [ /* §6.2 */ ],
  "chords":     [ /* §6.3 */ ],
  "anchors":    [ /* §6.4 */ ],
  "handshapes": [ /* §6.5 */ ],
  "templates":  [ /* §6.6 */ ],
  "phrases":    [ /* OPTIONAL, §6.7 */ ],
  "tones":      { /* OPTIONAL, §6.9 */ },
  "beats":      [ /* §6.8 — see note */ ],
  "sections":   [ /* §6.8 — see note */ ]
}
```

`beats` and `sections` are **song-level** data. For historical reasons they MAY appear inside
the first arrangement's JSON, in which case a Reader **MUST** hoist them to the song. New
packages **SHOULD** instead use a dedicated [`song_timeline.json`](#74-song_timelinejson). When
both are present, the `song_timeline.json` values **MUST** take priority.

### 6.2. Notes

Field names are short on purpose. A Writer **MUST NOT** expand them.

```jsonc
{
  "t": 12.345,    // time (s)
  "s": 2,         // string (0 = lowest)
  "f": 7,         // fret (0 = open, 24 = max)
  "sus": 0.5,     // sustain (s, 0 = none)
  "sl": 9,        // pitched slide-to fret (-1 = no slide)
  "slu": -1,      // unpitched slide-to fret (-1 = no slide)
  "bn": 1.0,      // bend amount in semitones
  "ho": false,    // hammer-on
  "po": false,    // pull-off
  "hm": false,    // natural harmonic
  "hp": false,    // pinch harmonic
  "pm": false,    // palm mute
  "mt": false,    // string mute
  "vb": false,    // vibrato
  "tr": false,    // tremolo
  "ac": false,    // accent
  "tp": false,    // tap
  "ln": false,    // link-next (chord-linking metadata; renderers may ignore)
  "fhm": false,   // fret-hand mute
  "plk": false,   // pluck / pop (bass)
  "slp": false,   // slap (bass)
  "rh": -1,       // right-hand fingering (-1 = unset)
  "pkd": -1,      // pick direction (-1 = unset, 0 = down, 1 = up)
  "ig": false     // ignore (authoring flag — rendered but not scored / sequenced)
}
```

Only `t`, `s`, and `f` are REQUIRED. Numeric defaults are `0`, or `-1` for the slide / `rh` /
`pkd` fields; boolean defaults are `false`. When authoring by hand, a Writer **MAY** omit any
field equal to its default; a Reader **MUST** fill in defaults for absent fields.

### 6.3. Chords

A chord groups note-shaped objects under a single time:

```jsonc
{
  "t": 30.0,
  "id": 12,           // index into templates[]
  "hd": false,        // high-density flag
  "notes": [
    {"s": 0, "f": 3, "sus": 0.0},
    {"s": 1, "f": 5, "sus": 0.0}
  ]
}
```

Chord notes use the same field set as standalone notes **except** that `t` is omitted — the
chord carries the time. `id` indexes into `templates[]` for the fingering/shape.

### 6.4. Anchors

Where the fretting hand sits; drives a renderer's zoom/focus box.

```json
{"time": 12.0, "fret": 5, "width": 4}
```

### 6.5. Hand shapes

Spans during which a chord shape is held:

```json
{"chord_id": 12, "start_time": 30.0, "end_time": 31.5, "arp": false}
```

| Field | Type | Default | Notes |
|---|---|---|---|
| `chord_id` | int | `0` | Index into `templates[]`. |
| `start_time` | number | `0.0` | Span start (s). |
| `end_time` | number | `0.0` | Span end (s). |
| `arp` | boolean | `false` | Treat as an arpeggio span rather than a strummed hold. |

### 6.6. Chord templates

Named shapes referenced by `chord.id` and `handshape.chord_id`:

```json
{
  "name": "Em7",
  "displayName": "Em7",
  "arp": false,
  "fingers": [-1, 2, 1, -1, -1, -1],
  "frets":   [ 0, 2, 2,  0,  0,  0]
}
```

| Field | Type | Default | Notes |
|---|---|---|---|
| `name` | string | `""` | Canonical template name. |
| `displayName` | string | `name` | UI label (MAY carry display-only variants). |
| `arp` | boolean | `false` | Whether the template is arpeggiated. |
| `fingers` | int[] | all `-1` | Fretting-hand fingers, lowest string first. `-1` = unused, `0` = open / no finger, `1..4` = index/middle/ring/pinky. Length matches the string count. |
| `frets` | int[] | all `-1` | Fret numbers, lowest string first. `-1` = unused, `0` = open, positive = fretted. |

### 6.7. Phrases (OPTIONAL — multi-difficulty data)

Sources that carry a per-phrase difficulty ladder include this:

```jsonc
"phrases": [
  {
    "start_time": 0.0,
    "end_time":   12.5,
    "max_difficulty": 4,
    "levels": [
      { "difficulty": 0, "notes": [], "chords": [], "anchors": [], "handshapes": [] },
      { "difficulty": 1, "notes": [], "chords": [], "anchors": [], "handshapes": [] }
    ]
  }
]
```

A Writer with no multi-difficulty data **MUST omit the `phrases` key entirely** rather than
emit `"phrases": []`. A missing key means "single fixed difficulty"; the distinction is
normative because consumers gate a difficulty control on the key's presence.

### 6.8. Beats and sections

```json
"beats":    [{"time": 0.5, "measure": 1}, {"time": 1.0, "measure": -1}],
"sections": [{"name": "verse", "number": 1, "time": 12.5}]
```

`measure: -1` marks a sub-beat (not a downbeat). Section `name` follows the usual
song-structure vocabulary (`intro`, `verse`, `chorus`, `bridge`, `solo`, `outro`, …). See the
note in [§6.1](#61-top-level-shape) regarding placement and the `song_timeline.json` priority
rule.

### 6.9. Tones (OPTIONAL)

`tones` carries the arrangement's gear (amp/pedal/cabinet) and in-song tone switches. Omitted
when the source carries no tone data.

```jsonc
"tones": {
  "base": "Clean Rhythm",
  "changes": [
    {"t": 12.5, "name": "Lead Drive"},
    {"t": 48.0, "name": "Clean Rhythm"}
  ],
  "definitions": [
    {"Name": "Clean Rhythm", "Key": "Tone_A", "GearList": { /* raw gear blocks */ }}
  ]
}
```

- `base` (string) — tone in effect before the first change.
- `changes` (list, time-sorted) — `{"t": seconds, "name": str}` switches.
- `definitions` (list) — raw, opaque tone objects copied from the source. Readers that do not
  interpret gear **MUST** preserve `tones` verbatim.

All three sub-keys are individually OPTIONAL.

---

## 7. Side-files

Each side-file is referenced from the manifest by a pointer key (the "manifest opt-in, file off
to the side" pattern; see [§9.1](#91-the-golden-rule-manifest-opt-in-file-off-to-the-side)).
Every new side-file **MUST** carry a top-level integer `version` (see [§4.3](#43-side-file-schema-versions)).

### 7.1. `lyrics.json`

Referenced by the manifest `lyrics` key. A flat JSON list of syllable objects:

```json
[
  {"t": 12.34, "d": 0.18, "w": "Hel"},
  {"t": 12.52, "d": 0.22, "w": "lo-"},
  {"t": 13.10, "d": 0.30, "w": "world"}
]
```

| Field | Type | Notes |
|---|---|---|
| `t` | number | Time (s). |
| `d` | number | Duration (s). |
| `w` | string | Syllable text. A trailing `-` joins to the next syllable as one word; a trailing `+` marks the last syllable of a line. Both are suffixes on a real syllable, not standalone entries. |

The manifest `lyrics_source` key records the origin: `authored` (from an authored chart),
`transcribed` (machine transcription), or `user` (hand-edited). Absent ⇒ `authored`. A UI MAY
use this to badge machine-generated lyrics differently.

#### 7.1.1. `lyric_transcription`

When `lyrics_source` is `transcribed` (or any future automated origin), an OPTIONAL top-level
`lyric_transcription` object records `{engine, model, version}` with the same shape and semver
semantics as [`stem_separation`](#531-stem_separation). Omitted for `authored`/`user` lyrics.

### 7.2. `vocal_pitch.json`

Referenced by the manifest `vocal_pitch` key — the per-syllable karaoke companion to lyrics:

```json
{
  "version": 1,
  "notes": [
    {"t": 12.34, "d": 0.40, "midi": 64},
    {"t": 12.78, "d": 0.55, "midi": 67}
  ]
}
```

| Field | Type | Notes |
|---|---|---|
| `version` | int | Schema version of this file (currently `1`). |
| `notes` | list | One entry per syllable that could be pitched. `t`/`d` mirror the matching `lyrics.json` entry; `midi` is the MIDI note number (60 = middle C). Unpitched syllables are omitted, so this list MAY be shorter than `lyrics.json`. |

#### 7.2.1. `pitch_extraction`

When pitch came from an automated engine, an OPTIONAL top-level `pitch_extraction` object
records `{engine, model, version}` — same shape and semver-string semantics as
[`stem_separation`](#531-stem_separation). This is distinct from the in-file integer `version`
above. Omitted for hand-edited pitch tracks.

### 7.3. `vocal_pitch_contour.json`

Referenced by the manifest `vocal_pitch_contour` key — a fine-grained pitch contour (one sample
every ~20 ms, Hz rather than MIDI). It is a *different shape* from `vocal_pitch.json` and rides
its own manifest key so the two never collide:

```json
{
  "version": 1,
  "samples": [
    {"t": 0.000, "hz": 220.5},
    {"t": 0.020, "hz": 222.1}
  ]
}
```

### 7.4. `song_timeline.json`

Referenced by the manifest `song_timeline` key. Moves song-wide beats and sections out of the
first arrangement JSON into a dedicated file:

```json
{
  "version": 1,
  "beats": [
    {"time": 0.500, "measure": 1},
    {"time": 1.000, "measure": -1},
    {"time": 2.000, "measure": 2}
  ],
  "sections": [
    {"name": "intro",  "number": 1, "time": 0.0},
    {"name": "verse",  "number": 1, "time": 16.0},
    {"name": "chorus", "number": 1, "time": 32.0}
  ]
}
```

| `beats[]` field | Type | Notes |
|---|---|---|
| `time` | number | Beat timestamp (s). |
| `measure` | int | 1-based downbeat number; `-1` = sub-beat. |

| `sections[]` field | Type | Notes |
|---|---|---|
| `name` | string | Song-structure name (`intro`, `verse`, `chorus`, …). |
| `number` | int | Repeat number. |
| `time` | number | Section start (s). |

When `song_timeline.json` is present and valid, its data **MUST** take priority over any
beats/sections embedded in arrangement JSON. When absent, the Reader **MUST** fall back to the
arrangement-embedded data per [§6.1](#61-top-level-shape). No migration is required for older
packages.

### 7.5. `drum_tab.json`

Referenced by the manifest `drum_tab` key — per-piece drum hits:

```json
{
  "version": 1,
  "name": "Drums",
  "kit": [
    {"id": "kick",      "name": "Kick"},
    {"id": "snare",     "name": "Snare"},
    {"id": "hh_closed", "name": "Hi-hat (closed)"},
    {"id": "ride",      "name": "Ride"}
  ],
  "hits": [
    {"t": 0.500, "p": "kick",      "v": 110},
    {"t": 0.750, "p": "snare",     "v":  92},
    {"t": 0.750, "p": "hh_closed", "v":  70},
    {"t": 1.000, "p": "snare",     "v":  60, "g": true},
    {"t": 1.250, "p": "snare",     "v": 105, "f": true},
    {"t": 4.000, "p": "crash_r",   "v": 120, "k": 0.080}
  ]
}
```

| `hits[]` field | Type | Notes |
|---|---|---|
| `t` | number | Hit time (s), REQUIRED, monotonic across `hits[]`. |
| `p` | string | Piece-id from the vocabulary below, REQUIRED. |
| `v` | int 1–127 | Velocity (default `100`). |
| `g` | boolean | Ghost note. |
| `f` | boolean | Flam. |
| `k` | number | Cymbal-choke tail duration (s). |

`kit[]` is the legend (stable metadata); `hits[]` is the hot path (short field names). Open and
closed hi-hat are **distinct piece-ids**, not articulation flags — a scorer can only reject a
wrong-articulation strike if the articulation is part of the id.

**Canonical piece-id vocabulary.** This is a closed list for v1; unknown piece-ids **MUST**
round-trip (a Reader renders them with a sensible default rather than erroring).

| Piece-id | Category | Default GM MIDI |
|---|---|---|
| `kick` | kick | 35, 36 |
| `snare` | drum | 38, 40 |
| `snare_xstick` | drum | 37 |
| `tom_hi` | drum | 50, 48 |
| `tom_mid` | drum | 47, 45 |
| `tom_low` | drum | 43 |
| `tom_floor` | drum | 41 |
| `hh_closed` | cymbal | 42 |
| `hh_open` | cymbal | 46 |
| `hh_pedal` | cymbal | 44 |
| `stack` | cymbal | 30 |
| `crash_l` | cymbal | 49 |
| `crash_r` | cymbal | 57 |
| `splash` | cymbal | 55 |
| `china` | cymbal | 52 |
| `ride` | cymbal | 51, 59 |
| `ride_bell` | cymbal | 53 |
| `bell` | cymbal | 80 |

### 7.6. `notation_<id>.json`

Referenced by an **arrangement entry's** `notation` key (per-arrangement, not song-wide — a
song MAY carry both `notation_keys.json` and `notation_violin.json`). Promotes staff-notation
instruments (keys, piano, strings, …) to first-class data, separate from the guitar wire
format.

```json
{
  "version": 1,
  "instrument": "piano",
  "staves": [
    {"id": "rh", "clef": "G2", "label": "Right Hand"},
    {"id": "lh", "clef": "F4", "label": "Left Hand"}
  ],
  "measures": [
    {
      "idx": 1,
      "t": 0.0,
      "ts": [4, 4],
      "ks": 0,
      "tempo": 120.0,
      "staves": {
        "rh": {"voices": [{"v": 1, "beats": [
          {"t": 0.000, "dur": 4, "notes": [{"midi": 64}]},
          {"t": 0.500, "dur": 4, "notes": [{"midi": 67}]}
        ]}]},
        "lh": {"voices": [{"v": 1, "beats": [
          {"t": 0.000, "dur": 1, "notes": [{"midi": 52}, {"midi": 60}]}
        ]}]}
      }
    }
  ]
}
```

**Top-level fields**

| Field | Type | Notes |
|---|---|---|
| `version` | int | Always `1` for this schema. |
| `instrument` | string | `piano`, `violin`, `guitar`, … Mirrors the arrangement `type`; makes the file self-describing. |
| `rights` / `lyricist` / `arranger` | string | OPTIONAL credits. Omit when absent. |
| `staves` | list | Static staff definitions: `id` (stable, referenced by `measures[].staves` keys), `clef`, OPTIONAL `label`. |
| `measures` | list | Ordered measure data — the hot path. |

**Clef vocabulary:** `G2` (treble), `F4` (bass), `C3` (alto), `C4` (tenor), `neutral`
(unpitched/percussion).

**Measure fields:** `idx` (1-based number), `t` (downbeat time, s), `ts` (`[num, den]`, omit if
unchanged), `beat_groups` (int[] for compound/irregular meters; the sum MUST equal the
numerator; omit for simple meters), `ks` (key signature, −7..+7 semitones from C; negative =
flats; omit if unchanged), `tempo` (BPM, omit if unchanged), `pickup` (bool anacrusis flag, omit
when false), `staves` (keyed by staff `id`; each has OPTIONAL `clef` and `voices`).

**Beat fields** (inside `staves → voices → beats`): `t` (required), `dur` (required denominator:
`1`=whole … `32`=thirty-second), `dot`, `rest`, `tu` (`[num, den]` tuplet), `beat_pos`
(`[num, den]` exact position within the measure), `notes`, `dyn`, `slr`/`slre`, `grace`
(`"a"`/`"p"`), `arp`, `ferm`, sustain-pedal `spd`/`sph`/`spu`, and additional optional effects
(`cre`, `dec`, `vib`, `vibw`, `fade`, `pm`, `lr`, `slap`, `pop`, `tap`, `su`, `sd`, `rasg`,
`golpe`, `wah`, `txt`, `chrd`).

**Note fields** (inside `beats → notes`): `midi` (required, 0–127), `tied`, `acc` (accidental
override: `0`=force natural, `−2..2` = double-flat..double-sharp), `stem` (`"up"`/`"down"`), and
additional optional effects (`stc`, `ten`, `ac`, `hac`, `vib`, `vibw`, `dead`, `ghost`, `fng`,
`rfng`, `str`, `harm`, `bend`, `slide`, `trill`, `ho`, `po`, `tp`, `barre`).

**v1 non-features (out of scope; ship later only as additive v1.x optional fields):** microtonal
pitch finer than `acc`; figured bass; mid-measure key/time/clef changes (all three are
measure-granular in v1); ottava lines, repeat/volta barline semantics, ornaments beyond trills,
notated tremolo, and glissando lines. A Writer **MUST** drop a source feature on this list (with
a logged warning) rather than approximate it into wrong notation; a Reader **MUST NOT** invent
semantics for an unspecified field name before a future version defines it.

### 7.7. `keys.json`

Referenced by the manifest `keys` key — key/scale annotations for theory-aware visualisations.
Each entry applies until the next:

```json
{
  "version": 1,
  "events": [
    {"t":   0.0, "key": "Em", "scale": "natural_minor"},
    {"t":  64.5, "key": "G",  "scale": "major"}
  ]
}
```

---

## 8. Reading and writing

This section is **informative** — it describes the typical lifecycle, not additional
requirements.

**Reading.** Parse `manifest.yaml`; read `title`/`artist`/`duration`/`feedpak_version` for a
quick metadata view. For a full load, resolve each manifest pointer to its file, validate it
against the relevant schema, and merge per the priority rules in [§6.1](#61-top-level-shape) and
[§7.4](#74-song_timelinejson). Unknown manifest keys and files are retained, not discarded.

**Writing.** Build the package in a working directory: write `arrangements/<id>.json` per
arrangement; encode audio into `stems/`; write any side-files; compose `manifest.yaml` last so
its index matches what was written. Emit YAML with block style and **preserve key order** for
human readability (do not sort keys). Then either keep the directory form or zip it into a
`.feedpak` archive. A round-trip (write → read → write) **SHOULD** be lossless for all
recognised fields and **MUST** preserve unrecognised ones.

---

## 9. Extending the format

feedpak is designed to be extended without breaking older Readers. The conventions below are
how `lyrics`, `stems`, `drum_tab`, `song_timeline`, and `notation` were each added.

### 9.1. The golden rule: manifest opt-in, file off to the side

1. **Drop a new file** alongside the standard ones (`drums.json`, `keys.json`, …).
2. **Add a manifest key** that *points at* that file (`drum_tab: drum_tab.json`).
3. **Gate consumers on the manifest key.** If the key is absent, do nothing. Never
   auto-discover by filename — that breaks the "manifest is the index" rule ([§2.2](#22-three-core-rules)).

Older Readers ignore the unknown key; new consumers act on it. No coordination with other
implementations is required.

### 9.2. Naming conventions

- **Manifest keys:** `snake_case`, descriptive; singular for one value (`lyrics`, `cover`,
  `drum_tab`), plural for lists (`stems`, `arrangements`).
- **Filenames:** lowercase; JSON for structured data, OGG for audio, JPEG/PNG for images.
- **JSON fields:** short names for hot-path data streamed many times (`t`, `s`, `f`); long names
  for one-off metadata.
- **Time fields:** always `t` or `time`, always seconds as floats.
- **Ids/indexes:** stable, filesystem-safe, lowercase.

### 9.3. Always include `version`

Every new side-file **SHOULD** carry `"version": 1`. It is free insurance: a later incompatible
change becomes `version: 2`, and old consumers can branch or fall back gracefully.

### 9.4. Stay backward-compatible

- **Adding fields** is always safe (older Readers ignore them) — release as a **minor** format bump.
- **Removing fields** breaks older Readers — do not; release only under a **major** bump.
- **Repurposing fields** (changing meaning or units) is the most dangerous — bump the side-file
  `version` (and the format major if it is structural) and branch. Prefer adding a new field and
  sunsetting the old one over a version or two.

### 9.5. What does NOT belong in a feedpak

A feedpak holds the song's **authored data** only. The following **MUST NOT** be written into a
package, because they vary by user or machine:

- Per-machine settings (device picks, network addresses, hardware universes).
- UI state (zoom level, panel sizes).
- User progress, scores, or play counts.

---

## 10. Conformance checklist

A **conformant feedpak** (normative summary):

- [ ] Has a `manifest.yaml` at the root, UTF-8, parseable as YAML.
- [ ] Manifest has `title`, `artist`, `duration`, a non-empty `arrangements`, and a non-empty
      `stems` (subject to the notation-only arrangement exception in [§5.2](#52-arrangements)).
- [ ] Every manifest pointer resolves to an existing file via a safe POSIX relative path.
- [ ] `feedpak_version`, if present, is a valid semver string.
- [ ] Every side-file validates against its schema and carries a `version` where this document
      requires one.
- [ ] Times are seconds; hot-path field names are unexpanded.

A **conformant Reader**:

- [ ] Accepts both directory and zip forms.
- [ ] Resolves all data through the manifest, never by filename scanning.
- [ ] Ignores (and, when re-emitting, preserves) unknown keys/files/fields.
- [ ] Applies the `feedpak_version` reader rules ([§4.2](#42-compatibility-policy)) and the
      `song_timeline` priority rule ([§7.4](#74-song_timelinejson)).
- [ ] Rejects paths that escape the package root.

---

## Appendix A (non-normative) — streaming and runtime notes

An application **MAY** transport feedpak data to a renderer over a streaming protocol (e.g. a
WebSocket) rather than handing over the on-disk files directly. Such protocols typically reuse
the same per-object field names defined here, often chunked into typed messages (song info,
notes, chords, beats, sections, lyrics, drum hits, notation measures, …). This is an
implementation choice and is **not** part of the format: the on-disk package defined by §2–§7 is
the sole normative artifact, and the byte-for-byte layout of any wire protocol is out of scope.

## Appendix B (non-normative) — media conventions

- **Stems:** OGG (Vorbis), ~`-q:a 5`. Mono or stereo as the source dictates.
- **Preview clip:** a short OGG (a few seconds) for hover-to-listen UIs.
- **Cover art:** JPEG or PNG, square, 500–1500 px on a side.

## References

- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) — Key words for use in RFCs.
- [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) — Ambiguity of uppercase vs lowercase.
- [Semantic Versioning 2.0.0](https://semver.org/).
- [YAML 1.2.2](https://yaml.org/spec/1.2.2/).
- [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/schema).
- [General MIDI percussion key map](https://en.wikipedia.org/wiki/General_MIDI#Percussion) (drum piece-id GM mapping).
