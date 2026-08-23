"""Which drum a notehead means.

A drum map binds each written note to a sound. The written position says where
the notehead is drawn; it says nothing about what you hear. Exporters that emit
a drum part as ordinary pitched notes leave the second half unspecified, so the
score looks right and plays as a melody.

Keys are (display position, notehead), because position alone is ambiguous: a
cymbal and a tom can share a line and differ only by an x head.
"""

from dataclasses import dataclass

# General MIDI percussion, channel 10.
KICK = 36
SNARE = 38
HIHAT_CLOSED = 42
HIHAT_OPEN = 46
CRASH = 49
RIDE = 51
TOM_HIGH = 48
TOM_MID = 45
TOM_LOW = 41

# MusicXML counts MIDI notes from 1, so every number written into
# <midi-unpitched> is one higher than the MIDI note it means.
MIDI_UNPITCHED_OFFSET = 1


@dataclass(frozen=True)
class Drum:
    name: str
    midi: int

    @property
    def midi_unpitched(self) -> int:
        return self.midi + MIDI_UNPITCHED_OFFSET


# Positions follow the common drumset convention on a treble staff. Verify
# against the score before trusting the cymbals: transcribers disagree most
# about which line above the staff is ride and which is crash.
DEFAULT_MAP = {
    ("F4", "normal"): Drum("Bass Drum", KICK),
    ("E4", "normal"): Drum("Bass Drum", KICK),
    ("C5", "normal"): Drum("Snare", SNARE),
    ("G5", "x"): Drum("Closed Hi-Hat", HIHAT_CLOSED),
    ("G5", "circle-x"): Drum("Open Hi-Hat", HIHAT_OPEN),
    ("A5", "x"): Drum("Ride Cymbal", RIDE),
    ("B5", "x"): Drum("Crash Cymbal", CRASH),
    ("E5", "normal"): Drum("High Tom", TOM_HIGH),
    ("D5", "normal"): Drum("Mid Tom", TOM_MID),
    ("A4", "normal"): Drum("Low Tom", TOM_LOW),
}


def parse_overrides(pairs):
    """Turn ["A5:x=49", "B5:x=51"] into map entries, for when the defaults
    guess the cymbals the wrong way round."""
    out = {}
    for pair in pairs:
        key, _, midi = pair.partition("=")
        pos, _, head = key.partition(":")
        if not (pos and midi):
            raise ValueError(f"expected POSITION[:NOTEHEAD]=MIDI, got {pair!r}")
        drum = next((d for d in DEFAULT_MAP.values() if d.midi == int(midi)), None)
        out[(pos, head or "normal")] = drum or Drum(f"MIDI {midi}", int(midi))
    return out
