# drummap

Give the notes in a MusicXML drum part their sounds.

## The problem

A drum score says two things about every note: where the notehead sits, and
which drum it is. They are independent. A notehead on the top space is not a
hi-hat because of where it sits; it is a hi-hat because the file says so.

Some exporters write only the first. You open the score and it looks perfect,
because the noteheads are in the right places. Then you press play and it is a
melody, because nothing in the file ever said "hi-hat", and without that the
positions are just pitches.

Changing the instrument to a drumset in your notation software will not fix it.
A drumset staff decides what to play from the note itself, and the notes are
melodic ones, so it has nothing to work with.

## What it does

Fills in the missing half. Every note keeps exactly the position it had, so the
page looks identical, and gains the drum it should have been all along.

```bash
python -m drummap --survey score.xml     # see what is in the file
python -m drummap score.xml -o fixed.xml
```

Start with `--survey`. It lists every position and notehead in the file, how
often each appears, and the drum it would become:

```
  F4  normal      228  Bass Drum
  C5  normal      223  Snare
  G5  x           190  Closed Hi-Hat
  A5  x            44  Crash Cymbal
  B5  x            14  Crash Cymbal 2
```

Read that before converting. The counts tell you whether a guess is right: a
ride keeps time and lands four or more times a bar, a crash is an accent and
lands once. If a line is wrong, override it:

```bash
python -m drummap score.xml --map A5:x=51
```

A position the map does not know stops the conversion rather than being guessed,
because a wrong drum is something you would only discover by ear.

## The default kit

The full five-piece plus cymbals, on the usual drumset positions: kick, snare
and cross stick, four toms, closed, open and pedal hi-hat, ride and ride bell,
two crashes, china, splash, cowbell and tambourine. Noteheads matter, since ride
and high tom share the top line and differ only by an x.

The whole kit is written into the file, not just the drums the score uses.
Notation software builds its drum palette from what the file declares, so a
score using five drums would otherwise leave you no correct slot to enter a
sixth from, and the note you added would play as something else.

Transcribers disagree most about which line above the staff is which cymbal, so
that is the part worth checking with `--survey` on a new score.

Defaults are General MIDI on channel 10.

## Tests

```bash
python -m pytest tests
```
