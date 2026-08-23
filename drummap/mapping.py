"""Which drum a written note means.

Keys are (staff position, notehead). Position alone is ambiguous: ride and
high tom share the top line and differ only by an x head, as do snare and
cross stick on the third space.

Positions follow the usual drumset convention on a treble staff. Transcribers
vary, most often about which line above the staff is ride and which is crash,
so check a new score against --survey before trusting the defaults.
"""

from dataclasses import dataclass

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


# General MIDI percussion, channel 10.
BASS_DRUM = Drum("Bass Drum", 36)
SIDE_STICK = Drum("Side Stick", 37)
SNARE = Drum("Snare", 38)
HAND_CLAP = Drum("Hand Clap", 39)
LOW_FLOOR_TOM = Drum("Low Floor Tom", 41)
HIHAT_CLOSED = Drum("Closed Hi-Hat", 42)
HIGH_FLOOR_TOM = Drum("High Floor Tom", 43)
HIHAT_PEDAL = Drum("Pedal Hi-Hat", 44)
LOW_TOM = Drum("Low Tom", 45)
HIHAT_OPEN = Drum("Open Hi-Hat", 46)
LOW_MID_TOM = Drum("Low-Mid Tom", 47)
HIGH_MID_TOM = Drum("High-Mid Tom", 48)
CRASH = Drum("Crash Cymbal", 49)
HIGH_TOM = Drum("High Tom", 50)
RIDE = Drum("Ride Cymbal", 51)
CHINA = Drum("China Cymbal", 52)
RIDE_BELL = Drum("Ride Bell", 53)
TAMBOURINE = Drum("Tambourine", 54)
SPLASH = Drum("Splash Cymbal", 55)
COWBELL = Drum("Cowbell", 56)
CRASH_2 = Drum("Crash Cymbal 2", 57)

DEFAULT_MAP = {
    # Feet, below the staff.
    ("D4", "x"): HIHAT_PEDAL,
    ("E4", "normal"): BASS_DRUM,
    ("F4", "normal"): BASS_DRUM,

    # Drums, on the staff, bottom to top.
    ("G4", "normal"): LOW_FLOOR_TOM,
    ("A4", "normal"): HIGH_FLOOR_TOM,
    ("B4", "normal"): LOW_TOM,
    ("C5", "normal"): SNARE,
    ("C5", "x"): SIDE_STICK,
    ("C5", "circle-x"): SIDE_STICK,
    ("D5", "normal"): LOW_MID_TOM,
    ("E5", "normal"): HIGH_MID_TOM,
    ("F5", "normal"): HIGH_TOM,

    # Cymbals, x heads on and above the staff.
    ("F5", "x"): RIDE,
    ("F5", "diamond"): RIDE_BELL,
    ("G5", "x"): HIHAT_CLOSED,
    ("G5", "circle-x"): HIHAT_OPEN,
    ("G5", "diamond"): HIHAT_OPEN,
    ("A5", "x"): CRASH,
    ("A5", "diamond"): SPLASH,
    ("B5", "x"): CRASH_2,
    ("B5", "diamond"): CHINA,

    # Hands and hardware.
    ("D6", "x"): COWBELL,
    ("E6", "x"): TAMBOURINE,
    ("D5", "x"): HAND_CLAP,
}

BY_MIDI = {d.midi: d for d in DEFAULT_MAP.values()}


def parse_overrides(pairs):
    """Turn ["A5:x=51"] into map entries, for a score that puts a cymbal
    somewhere the defaults do not expect."""
    out = {}
    for pair in pairs:
        key, _, midi = pair.partition("=")
        pos, _, head = key.partition(":")
        if not (pos and midi):
            raise ValueError(f"expected POSITION[:NOTEHEAD]=MIDI, got {pair!r}")
        midi = int(midi)
        out[(pos, head or "normal")] = BY_MIDI.get(midi, Drum(f"MIDI {midi}", midi))
    return out
