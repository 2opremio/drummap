"""Read a drum map out of a MuseScore .drm kit.

A kit already says, for every drum, which line it sits on and what notehead it
wears. That is the same correspondence drummap needs, written the other way
round, so a kit you already use beats guessing from convention.

MuseScore counts staff lines from the top line downwards, one per diatonic step,
and allows negatives above the staff. On the treble staff a drum part uses, line
0 is F5.
"""

import xml.etree.ElementTree as ET

from .mapping import Drum

LETTERS = "CDEFGAB"
# Line 0 is F5. Numbering diatonic steps absolutely, C0 being 0, puts it here.
TOP_LINE_INDEX = 5 * 7 + LETTERS.index("F")

# MuseScore's notehead names against MusicXML's.
NOTEHEADS = {
    "normal": "normal",
    "cross": "x",
    "xcircle": "circle-x",
    "diamond": "diamond",
    "triangle": "triangle",
    "slash": "slash",
    "plus": "cross",
}


def position_for_line(line):
    """Staff line to display position. Line 0 is the top line, F5, and each
    step down moves one letter down the scale."""
    index = TOP_LINE_INDEX - line
    return f"{LETTERS[index % 7]}{index // 7}"


def load_kit(path):
    """Returns (drum map, ambiguous).

    Kits routinely put several drums on one line and notehead: acoustic and
    electric snare, the two floor toms, china and splash and second crash. Those
    keys land in `ambiguous` with every candidate, for the caller to resolve
    only if the score actually uses them. Picking one here is how a crash
    becomes a ride.
    """
    candidates = {}
    for drum in ET.parse(path).getroot().findall("Drum"):
        pitch = drum.get("pitch")
        line = drum.findtext("line")
        if pitch is None or line is None:
            continue
        head = NOTEHEADS.get(drum.findtext("head") or "normal", "normal")
        name = drum.findtext("name") or f"MIDI {pitch}"
        key = (position_for_line(int(line)), head)
        candidates.setdefault(key, []).append(Drum(name, int(pitch)))

    out = {k: v[0] for k, v in candidates.items() if len(v) == 1}
    ambiguous = {k: v for k, v in candidates.items() if len(v) > 1}
    return out, ambiguous
