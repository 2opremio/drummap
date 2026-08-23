# drummap

Give the notes in a MusicXML drum part their sounds.

## The problem

MusicXML keeps a percussion note's *appearance* and its *sound* in separate
places, and only one of them is obvious.

Appearance is `<unpitched>` with a `display-step` and `display-octave`, which
say where the notehead sits on the staff. Sound comes from an `<instrument>`
reference on the note, pointing at a `<score-instrument>` whose paired
`<midi-instrument>` carries the MIDI drum number.

Some exporters write a drum part as ordinary pitched notes and declare no
instruments at all:

```xml
<part-list>
  <score-part id="P1"><part-name>Drums</part-name></score-part>
</part-list>
...
<note>
  <pitch><step>G</step><octave>5</octave></pitch>
  <notehead>x</notehead>
</note>
```

That opens looking perfect, because those staff positions are where drums are
drawn, and plays as a melody, because G5 is a pitch. Ticking a drumset box in
your notation software will not rescue it: a drumset staff maps *MIDI pitch* to
drum sound, and G5 is MIDI 79, which is not a drum.

## What it does

Rewrites each pitched note as unpitched, keeping its written position exactly,
so the page looks identical. Then it declares one instrument per drum in use and
points every note at the right one.

```bash
python -m drummap --survey score.xml     # see what is in the file
python -m drummap score.xml -o fixed.xml
```

`--survey` lists every position and notehead found, with counts and the drum
each would map to:

```
  F4  normal      228  Bass Drum
  C5  normal      223  Snare
  G5  x           190  Closed Hi-Hat
  A5  x            44  Ride Cymbal
  B5  x            14  Crash Cymbal
```

The map is keyed on position *and* notehead, because position alone is
ambiguous: a cymbal and a tom can share a line and differ only by an x head.

Transcribers disagree most about which line above the staff is ride and which is
crash, so check those two and override if needed:

```bash
python -m drummap score.xml --map A5:x=49 --map B5:x=51
```

A note the map has no entry for stops the conversion rather than being guessed,
because a wrong guess is something you would only find by ear.

## Notes

`<midi-unpitched>` counts MIDI notes from 1, so the number written for a kick is
37, not 36. Getting that wrong puts every drum one slot out.

Defaults are General MIDI on channel 10.

## Tests

```bash
python -m pytest tests
```
