import xml.etree.ElementTree as ET

import pytest

from drummap.convert import NOTE_ORDER, Unmapped, convert, survey
from drummap.mapping import Drum, parse_overrides

SCORE = """<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="4.0">
  <part-list><score-part id="P1"><part-name>Drums</part-name></score-part></part-list>
  <part id="P1"><measure number="1">
    <note><pitch><step>F</step><octave>4</octave></pitch><duration>8</duration>
      <voice>1</voice><type>eighth</type></note>
    <note><pitch><step>G</step><octave>5</octave></pitch><duration>8</duration>
      <voice>1</voice><type>eighth</type><notehead>x</notehead></note>
    <note><rest/><duration>8</duration><voice>1</voice><type>eighth</type></note>
  </measure></part>
</score-partwise>
"""


def score():
    return ET.ElementTree(ET.fromstring(SCORE))


def test_survey_counts_pitched_notes_only():
    assert survey(score()) == {("F4", "normal"): 1, ("G5", "x"): 1}


def test_midi_unpitched_is_one_above_the_midi_note():
    # MusicXML numbers MIDI notes from 1. Writing the raw number here is the
    # mistake that makes every drum sound a semitone out.
    tree = score()
    convert(tree)
    by_id = {m.get("id"): m.findtext("midi-unpitched")
             for m in tree.getroot().iter("midi-instrument")}
    assert by_id["P1-36"] == "37"
    assert by_id["P1-42"] == "43"


def test_written_position_survives():
    # The page must look identical afterwards; only the sound is being added.
    tree = score()
    convert(tree)
    notes = [n for n in tree.getroot().iter("note") if n.find("unpitched") is not None]
    positions = [(n.findtext("unpitched/display-step"),
                  n.findtext("unpitched/display-octave")) for n in notes]
    assert positions == [("F", "4"), ("G", "5")]
    assert tree.getroot().find(".//pitch") is None


def test_each_note_points_at_its_drum():
    tree = score()
    convert(tree)
    notes = [n for n in tree.getroot().iter("note") if n.find("unpitched") is not None]
    assert [n.find("instrument").get("id") for n in notes] == ["P1-36", "P1-42"]
    # The whole kit is declared, so the reader offers every drum for entry.
    declared = {si.get("id") for si in tree.getroot().iter("score-instrument")}
    assert {"P1-36", "P1-42"} <= declared
    assert "P1-51" in declared, "a drum the score does not use is still offered"
    ids = [mi.get("id") for mi in tree.getroot().iter("midi-instrument")]
    assert sorted(ids) == sorted(declared), "every declared drum needs a sound"


def test_rests_are_left_alone():
    tree = score()
    convert(tree)
    rest = [n for n in tree.getroot().iter("note") if n.find("rest") is not None]
    assert len(rest) == 1
    assert rest[0].find("instrument") is None


def test_children_end_up_in_schema_order():
    # MusicXML's note is a sequence, so a validating reader rejects a file whose
    # instrument lands after voice.
    tree = score()
    convert(tree)
    note = next(n for n in tree.getroot().iter("note") if n.find("unpitched") is not None)
    tags = [c.tag for c in note if c.tag in NOTE_ORDER]
    assert tags == sorted(tags, key=NOTE_ORDER.index)


def test_an_unknown_notehead_stops_the_conversion():
    # Guessing would put a sound in the score that the user never chose, and
    # they would have to notice by ear.
    tree = ET.ElementTree(ET.fromstring(
        SCORE.replace("<octave>5</octave>", "<octave>7</octave>")))
    with pytest.raises(Unmapped) as e:
        convert(tree)
    assert "G7" in str(e.value)


def test_an_override_replaces_one_entry():
    tree = score()
    convert(tree, parse_overrides(["G5:x=51"]))
    note = [n for n in tree.getroot().iter("note")
            if n.find("unpitched") is not None][1]
    assert note.find("instrument").get("id") == "P1-51"


def test_converting_twice_changes_nothing_more():
    tree = score()
    convert(tree)
    first = ET.tostring(tree.getroot())
    convert(tree)
    assert ET.tostring(tree.getroot()) == first


def test_drum_knows_its_own_offset():
    assert Drum("Kick", 36).midi_unpitched == 37
