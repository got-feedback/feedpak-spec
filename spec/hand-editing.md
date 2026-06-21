<!--
SPDX-License-Identifier: CC0-1.0
This guide is dedicated to the public domain under CC0 1.0, like the rest of the
feedpak specification prose.
-->

# feedpak Hand-Editing Guide

A `.feedpak` is just a zip of plain files: some YAML, some JSON, some audio (OGG/WAV by default,
optionally MP3/FLAC/Opus), maybe a JPEG.
That means you can open one up and change it. Want to record your own rhythm guitar take and use
that instead of the mix? Fix an artist typo? Swap the cover art? Replace an automated stem split
that bled drums into the "other" stem? You don't need to rebuild the whole pack from its source —
just edit the file.

This guide walks through the most common edits, aimed at musicians who are comfortable with a
text editor and an audio editor like [Audacity](https://www.audacityteam.org/) but don't live on
the command line.

> For the format **schema** (what every field means, how the wire format works, how to extend the
> format with new data types), see the [feedpak specification](feedpak-v1.md). This document is
> the **how-do-I-actually-edit-mine** companion. It describes the format, not any particular
> application; where an app's behaviour matters, it's flagged as application-specific.

---

## 1. The two forms — directory and zip

A feedpak exists in two interchangeable forms ([spec §2](feedpak-v1.md#2-format-at-a-glance)):

| Form | What it is | When to use it |
|---|---|---|
| **Directory** | A folder named `something.feedpak/` with the files loose inside | **Authoring** — easy to edit, no zip/unzip cycle |
| **Zip** | A `something.feedpak` file (zip with the same files inside) | **Distributing** — single file to share |

A conformant reader accepts both, so you can use whichever is convenient.

### Unzipping for editing

Distribution packs usually ship in zip form. To edit one, unzip it:

- **Windows:** rename `mysong.feedpak` → `mysong.zip`, right-click → Extract All. Then rename the
  resulting folder back to `mysong.feedpak/` (the directory form). Or use
  [7-Zip](https://www.7-zip.org/) and extract without renaming.
- **macOS:** rename `.feedpak` → `.zip`, double-click. Or use The Unarchiver.
- **Linux:** `unzip mysong.feedpak -d mysong.feedpak/`.

Once you have the directory form, edit any file inside and your application will pick it up — no
re-zipping required for your own use.

### When edits to a zip don't appear (caching)

Some applications unpack a zip-form pack into a working cache the first time they open it, rather
than reading the zip on every load. If you edit the **original zip** and your changes don't show
up, the usual fixes are:

- Re-save the zip so its modification time / size changes — well-behaved readers re-extract when
  the archive changes.
- Consult your application's docs for how to clear its pack cache.
- Or sidestep caching entirely by using the **directory form** — most readers use it in place, so
  there's nothing to invalidate.

This caching is an application implementation detail; it is not part of the format.

---

## 2. Record and add your own rhythm stem

The use case: an automated stem split (e.g. produced by a tool like Demucs) sounds muddy on the
rhythm guitar, and you'd rather play and record your own take.

### Step 1 — Set up your reference

1. Unzip the pack (see §1).
2. Look in `stems/` and open the reference audio in your audio editor. Two cases:
   - **`stems/full.ogg` is present** — that's the original mixed audio. Open it directly.
   - **No `full.ogg`, only per-instrument stems** (`guitar.ogg`, `bass.ogg`, `drums.ogg`, …).
     This is common after an automated split. Select **all** the per-instrument stems and open
     them together — most editors load each as its own track aligned at `t=0`, and playing them
     all at once reconstructs the full mix.
3. Note the **sample rate** (typically `44100 Hz`). Your recording must match it.

### Step 2 — Record your take aligned to the mix

1. With the reference track(s) open, add a new audio track.
2. Set the editor to play the reference through your headphones while recording your own input.
3. Record your part along with the reference from `t=0`. Critical: **start recording at the very
   beginning of the song.** If you punch in late, alignment will be off when you drop it in.
4. Stop when the song ends. Trim any silence/click at the very start of your recorded track so its
   first sample lines up with `t=0` of the reference (zoom in tight and check visually against the
   kick or first guitar hit).

### Step 3 — Export the audio

1. **Solo** your recorded track (mute every reference track).
2. Export as **OGG Vorbis** — the recommended baseline format. (WAV, FLAC, MP3, or Opus also
   work; see the [spec's audio-format rules](feedpak-v1.md#532-audio-formats--baseline-dispatch-and-portability).
   Keep at least one OGG/WAV stem so the pack stays portable.)
3. Quality slider around **5** is a good size/quality balance for OGG (the [spec's media
   conventions](feedpak-v1.md#appendix-b-non-normative--media-conventions)). Save as
   `rhythm_custom.ogg`.
   - *Exporting a different format?* The quality-slider guidance is OGG-specific (it doesn't
     apply to WAV/FLAC/MP3/Opus). Use the matching file extension (e.g. `rhythm_custom.flac`)
     and use that exact name in the manifest `file:` path in Step 4.
4. Confirm the export sample rate matches the rate you noted in Step 1.

### Step 4 — Drop it in and update the manifest

1. Copy your exported file into the pack's `stems/` folder (this guide uses `rhythm_custom.ogg`;
   if you exported a different format in Step 3, substitute that filename — e.g.
   `rhythm_custom.flac` — everywhere below, and keep at least one OGG/WAV stem for portability).
2. Open `manifest.yaml` in any plain-text editor (VS Code, Notepad++, BBEdit, gedit — all fine;
   just **don't use a word processor**).
3. Find the `stems:` block ([spec §5.3](feedpak-v1.md#53-stems)). Mark the stem you want enabled
   on open with `default: true` (the `file:` value must match the extension you exported):

   ```yaml
   stems:
     - id: rhythm_custom
       file: stems/rhythm_custom.ogg
       default: true
     - id: guitar
       file: stems/guitar.ogg
       default: false
     - id: bass
       file: stems/bass.ogg
       default: true
     - id: drums
       file: stems/drums.ogg
       default: true
     # … other stems unchanged …
   ```

   > **Application note.** The spec defines `default` as "enabled when the song opens." Beyond
   > that, some players treat the **first-listed** stem as the primary mixdown (what you hear
   > without a stem mixer). If your player does, list the stem you want as the main one **first**
   > as well as marking it `default: true`.

4. Save the file. **Mind the indentation** — two spaces, no tabs. YAML is fussy about this.

### Step 5 — Reload and verify

Reload the song. A stem-mixer feature, if your application has one, will show a fader for
`rhythm_custom` next to the others. If you don't see it, check the caching notes in §1.

### Common gotchas

- **Sample-rate mismatch** → choppy / pitched-wrong playback. Re-export at exactly the rate the
  other stems use.
- **Mono vs stereo mismatch** is fine for playback but levels can feel different — match the other
  stems if you want consistent mixer behaviour.
- **Silence padding at the start** of your recording → your stem plays late. Trim it tight before
  exporting.
- **Tabs in `manifest.yaml`** → most readers will refuse to load the song. Use two spaces.

---

## 3. Replace a bad automated stem

Automated separation is good but not perfect — it will occasionally bleed snare into `other.ogg`
or leave drum overtones in the bass track. Fixing it works the same way as adding a custom stem;
you're just overwriting an existing one.

### Option A: overwrite in place

1. Source or record a clean replacement and export it as OGG at the same sample rate.
2. Save it directly over the bad file (e.g. `stems/other.ogg`).
3. Reload — no manifest change needed.

### Option B: keep the original, add a replacement

Useful if you want to A/B them:

1. Save your new file as `stems/other_v2.ogg`.
2. In `manifest.yaml`, change the `file:` path on that stem's entry:

   ```yaml
   - id: other
     file: stems/other_v2.ogg     # was stems/other.ogg
     default: true
   ```

3. The old `other.ogg` stays in the folder but is no longer referenced. Delete it later if you
   want.

### Removing a stem entirely

If you want to drop a stem (e.g. `piano.ogg` is empty for this song):

1. Delete the file from `stems/`.
2. **Also remove** its entry from `manifest.yaml` `stems[]`. The manifest is the index ([spec
   §2.2](feedpak-v1.md#22-three-core-rules)) — an orphan entry pointing at a missing file is a
   broken reference. (Note: `stems` must stay non-empty.)

### A word on `full.ogg`

A freshly built pack often starts with just `stems/full.ogg`. After an automated split, the
builder typically rewrites the manifest to list per-instrument stems and removes `full.ogg`. If
you're hand-editing and want to *keep* `full.ogg` as a fallback (mixed audio in case all the
individual stems are muted), that's fine — leave the file in place and add a manifest entry with
`default: false`. Don't delete `full.ogg` unless the per-instrument stems sum cleanly to a full
mix.

---

## 4. Edit metadata, cover art, lyrics, tuning

All of these are tweaks to either `manifest.yaml` or files it points at. Open `manifest.yaml` in a
text editor for the next sections.

### Title, artist, album, year

Top-level keys in `manifest.yaml` ([spec §5.1](feedpak-v1.md#51-top-level-keys)). Edit the strings:

```yaml
title: "Black Hole Sun"
artist: "Soundgarden"
album: "Superunknown"
year: 1994
duration: 320.5
```

Keep the quotes if the value already has them (especially with an apostrophe or colon). Reload the
song — the library entry updates next time the library refreshes.

> While you're in here, an authored pack may also declare its format version:
> `feedpak_version: "1.0.0"` ([spec §4.1](feedpak-v1.md#41-format-version--feedpak_version)). It's
> optional — an absent value is treated as `1.0.0` — so you don't need to add it, but it's
> harmless to.

### Cover art

Drop a square JPEG or PNG (500–1500 px on a side is the sweet spot) into the pack root and point
the manifest at it:

```yaml
cover: cover.jpg
```

If the manifest has no `cover:` line, add one.

### Lyrics

`lyrics.json` is a flat JSON list of syllable objects ([spec §7.1](feedpak-v1.md#71-lyricsjson)):

```json
[
  {"t": 12.34, "d": 0.18, "w": "Hel"},
  {"t": 12.52, "d": 0.22, "w": "lo-"},
  {"t": 13.10, "d": 0.30, "w": "world"}
]
```

| Field | Meaning |
|---|---|
| `t` | Time the syllable starts, in seconds (float) |
| `d` | Duration in seconds |
| `w` | The syllable text. A trailing `-` joins it to the next syllable as one word. A trailing `+` marks the last syllable of a line. Both are suffixes on a real syllable — not standalone entries |

Common hand-edits:
- **Karaoke timing is off** — bump `t` values up or down a few hundredths of a second.
- **Wrong word** — edit `w`.
- **Missing line break** — append `+` to the last syllable of the line that should end there (e.g.
  change `"w": "world"` to `"w": "world+"`). Don't insert a standalone `"+"` entry — that creates
  an empty syllable that still consumes word-spacing.

It's plain JSON — edit in any text editor.

### Tuning

Per-arrangement, in `manifest.yaml` ([spec §5.2](feedpak-v1.md#52-arrangements)):

```yaml
arrangements:
  - id: lead
    name: Lead
    file: arrangements/lead.json
    tuning: [0, 0, 0, 0, 0, 0]    # E standard
    capo: 0
```

Each number is **semitones from E A D G B E**, lowest string first. Common tunings:

| Tuning | Offsets |
|---|---|
| E Standard | `[0, 0, 0, 0, 0, 0]` |
| Eb Standard | `[-1, -1, -1, -1, -1, -1]` |
| D Standard | `[-2, -2, -2, -2, -2, -2]` |
| Drop D | `[-2, 0, 0, 0, 0, 0]` |
| Drop C | `[-4, -2, -2, -2, -2, -2]` |
| DADGAD | `[-2, 0, 0, 0, -2, -2]` |

The manifest tuning overrides whatever's stored inside `arrangements/lead.json`, so fixing it here
is enough — you don't need to touch the arrangement JSON. For 4-string bass, only indices 0–3 are
meaningful; leave the rest at `0`.

### What *not* to put in `manifest.yaml`

Don't add per-machine settings (audio device picks, MIDI port IDs), UI state, or your own play
counts. A feedpak holds the song's authored data — anything that varies by user or machine belongs
in your application's own config, not the pack. See [spec
§9.5](feedpak-v1.md#95-what-does-not-belong-in-a-feedpak) for the full list.

---

## 5. Re-zipping for distribution

To share your modified pack, re-zip it:

1. Open the `mysong.feedpak/` directory.
2. Select **everything inside** — `manifest.yaml`, `arrangements/`, `stems/`, and any
   `lyrics.json` / `cover.jpg` / side-files.
3. Zip the **contents**, not the parent folder. (If you zip the folder, the archive gets a
   top-level `mysong.feedpak/` directory inside it, and `manifest.yaml` won't be at the zip root
   where readers expect it.)
4. Rename `mysong.zip` → `mysong.feedpak`.

For your own use you can skip this entirely — readers accept the directory form.

---

## Tips for hand-editing JSON data files

Most data files in a feedpak use JSON, which does not allow comments. If you find yourself making
repeated manual edits to a data file and want to leave yourself notes, rename the file from
`.json` to `.jsonc`. The `.jsonc` extension tells Readers that the file MAY contain `//` line
comments and `/* */` block comments (see [spec §8](feedpak-v1.md#8-reading-and-writing)). Readers
strip comments before parsing and good Writers preserve them when re-saving, so your notes survive
round-trips.

For example, to annotate a `song_timeline.jsonc` with section markers:

```jsonc
{
  "version": 1,
  "tempos": [
    { "time": 0.0, "bpm": 120.0 }  // verse tempo
  ],
  "sections": [
    { "name": "intro",  "number": 1, "time": 0.0 },
    { "name": "verse",  "number": 1, "time": 16.0 },
    { "name": "chorus", "number": 1, "time": 32.0 }
  ]
}
```

Then update the manifest pointer from `song_timeline: song_timeline.json` to
`song_timeline: song_timeline.jsonc`. Everything else stays the same.

Two things to keep in mind:

- **Comments are the only thing JSONC adds.** Trailing commas, single-quoted strings, and other
  JSON5-style shortcuts are *not* allowed — once the comments are stripped, the file still has to
  be valid JSON. (A trailing comma is the easy mistake to make if you're used to editing JSONC
  elsewhere.)
- **Comments mean the file needs a JSONC-aware reader.** A `.jsonc` file that actually contains
  comments can only be opened by a reader that understands the extension; a strict-JSON-only reader
  will choke on `//` and `/* */`. So treat comments as notes for your own working copy — if you
  plan to share or distribute the pack, keep its data files as comment-free `.json`. (A
  comment-free `.jsonc` file is just JSON with a different name, so it's always safe.)

## Out of scope (for now)

- **Authoring a pack from scratch** (no source file to convert) — more of a developer task. Start
  at [spec §8 (Reading and writing)](feedpak-v1.md#8-reading-and-writing).
- **Editing notes / chords in `arrangements/*.json`** — technically possible but extremely tedious
  by hand: hundreds of objects with short field names per song. The fields are documented in [spec
  §6 (Arrangement JSON)](feedpak-v1.md#6-arrangement-json), but for any real chart edit you want a
  dedicated arrangement editor. (If you do attempt it, consider renaming the file to `.jsonc` so
  your edits can carry comments.)
- **Loudness normalization / advanced stem processing** — out of scope here; standard audio-editor
  or `ffmpeg` workflows apply to any OGG file before you drop it into `stems/`.
