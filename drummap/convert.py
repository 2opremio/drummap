"""Rewrite a pitched part as an unpitched percussion part.

Written position is preserved exactly, so the page looks the same afterwards.
What changes is that each note gains a sound: <pitch> becomes <unpitched>, every
note points at a <score-instrument>, and each of those carries the MIDI drum
number in a <midi-instrument>.

Element order matters. MusicXML's schema is a sequence, not a set, and readers
that validate will reject a note whose children are in the wrong order.
"""

import xml.etree.ElementTree as ET

from .mapping import DEFAULT_MAP

# Where each child sits inside <note>, per the MusicXML note content model.
# Anything unlisted keeps its relative order after these.
NOTE_ORDER = [
    "grace", "cue", "chord", "pitch", "unpitched", "rest",
    "duration", "tie", "instrument", "footnote", "level", "voice", "type",
]

# Where score-instrument and midi-instrument sit inside <score-part>.
SCORE_PART_ORDER = [
    "identification", "part-link", "part-name", "part-name-display",
    "part-abbreviation", "part-abbreviation-display", "group",
    "score-instrument", "player", "midi-device", "midi-instrument",
]

DRUM_CHANNEL = 10


class Unmapped(Exception):
    """A note the drum map has no entry for. Guessing would put a sound the
    user never chose into their score, so conversion stops instead."""


def _position(note):
    pitch = note.find("pitch")
    if pitch is None:
        return None
    step = pitch.findtext("step")
    octave = pitch.findtext("octave")
    return f"{step}{octave}" if step and octave else None


def _notehead(note):
    return note.findtext("notehead") or "normal"


def _sorted_children(elem, order):
    rank = {tag: i for i, tag in enumerate(order)}
    tail = len(order)
    return sorted(elem, key=lambda c: rank.get(c.tag, tail))


def _reorder(elem, order):
    children = _sorted_children(elem, order)
    for c in list(elem):
        elem.remove(c)
    elem.extend(children)


def survey(tree):
    """Every (position, notehead) that carries a pitch, with counts. Run this
    before converting to see what the map has to cover."""
    counts = {}
    for note in tree.getroot().iter("note"):
        pos = _position(note)
        if pos is None:
            continue
        counts[(pos, _notehead(note))] = counts.get((pos, _notehead(note)), 0) + 1
    return counts


def convert(tree, drum_map=None, part_name="Drumset"):
    """Convert every pitched note in the score. Returns the drums used.

    Raises Unmapped if any note has no entry, naming what is missing.
    """
    drum_map = {**DEFAULT_MAP, **(drum_map or {})}
    root = tree.getroot()

    found = survey(tree)
    # Already unpitched. Rebuilding the declarations from an empty set would
    # strip the mapping a previous run wrote.
    if not found:
        return {}

    missing = {key for key in found if key not in drum_map}
    if missing:
        listed = ", ".join(f"{pos} ({head})" for pos, head in sorted(missing))
        raise Unmapped(f"no drum for: {listed}")

    used = {}
    for note in root.iter("note"):
        pos = _position(note)
        if pos is None:
            continue
        drum = drum_map[(pos, _notehead(note))]
        used[drum.midi] = drum

        pitch = note.find("pitch")
        unpitched = ET.Element("unpitched")
        ET.SubElement(unpitched, "display-step").text = pitch.findtext("step")
        ET.SubElement(unpitched, "display-octave").text = pitch.findtext("octave")
        note.remove(pitch)
        note.append(unpitched)

        ET.SubElement(note, "instrument").set("id", _instrument_id(root, drum))
        _reorder(note, NOTE_ORDER)

    _declare_instruments(root, used, part_name)
    return used


def _instrument_id(root, drum):
    part_id = root.find("part-list/score-part").get("id")
    return f"{part_id}-{drum.midi}"


def _declare_instruments(root, used, part_name):
    score_part = root.find("part-list/score-part")
    for tag in ("score-instrument", "midi-instrument"):
        for old in score_part.findall(tag):
            score_part.remove(old)

    name = score_part.find("part-name")
    if name is None:
        name = ET.SubElement(score_part, "part-name")
    name.text = part_name

    for drum in sorted(used.values(), key=lambda d: d.midi):
        ident = _instrument_id(root, drum)

        si = ET.SubElement(score_part, "score-instrument")
        si.set("id", ident)
        ET.SubElement(si, "instrument-name").text = drum.name

        mi = ET.SubElement(score_part, "midi-instrument")
        mi.set("id", ident)
        ET.SubElement(mi, "midi-channel").text = str(DRUM_CHANNEL)
        ET.SubElement(mi, "midi-unpitched").text = str(drum.midi_unpitched)

    _reorder(score_part, SCORE_PART_ORDER)
