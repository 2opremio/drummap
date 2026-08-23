# drummap

Give the notes in a MusicXML drum part their sounds.

## The problem

A notated drum note has two properties: how it is drawn, and which drum it plays.

MusicXML can carry both, but some software writes only the first:

- the staff position
- the notehead shape
- rhythm, beaming, ties and the rest

Without the second, the drums are unnamed, so whatever opens the file guesses:
the score looks right and sounds wrong. Switching the staff to a drumset does not
help, since that decides what to play from the note, and the note is a pitch.

## Usage

```bash
python -m drummap --survey score.xml     # what is in the file
python -m drummap score.xml -o fixed.xml
```

No kit file is needed: the built-in map covers a standard drumset. Positions are
kept exactly, so the page looks the same. `--survey` shows what each will
become:

```
  F4  normal      228  Bass Drum
  C5  normal      223  Snare
  G5  x           190  Closed Hi-Hat
  A5  x            44  Crash Cymbal 1
  B5  x            14  Crash Cymbal 2
```

The counts are worth reading: a ride keeps time and lands four or more times a
bar, a crash is an accent and lands once. Override with `--map A5:x=51`.

An unknown position stops the conversion rather than being guessed.

## The default kit

Kick, snare and cross stick, four toms, closed, open and pedal hi-hat, ride and
ride bell, two crashes, china, splash, cowbell, tambourine. General MIDI on
channel 10.

All of it is written into the file, not just the drums in use, so your notation
software offers the whole palette for entering more.

## Using a MuseScore kit instead

Optional. If your transcriber lays drums out differently from the default, take
the map from a MuseScore kit:

```bash
python -m drummap score.xml --kit mykit.drm
```

A kit records how each drum is drawn, so this reads it backwards, to figure out
the note pitches based on the symbols.

However, reverse is not always unique: a cross above the staff might be china,
splash or second crash.

Where the score lands on one, the candidates are listed instead of picked.
Settle it with `--map B5:x=57`.

## Tests

```bash
python -m pytest tests
```
