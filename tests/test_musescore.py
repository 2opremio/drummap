import textwrap

from drummap.musescore import load_kit, position_for_line

KIT = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <museScore version="4.70">
      <Drum pitch="36"><head>normal</head><line>7</line><name>Bass Drum 1</name></Drum>
      <Drum pitch="38"><head>normal</head><line>3</line><name>Acoustic Snare</name></Drum>
      <Drum pitch="40"><head>normal</head><line>3</line><name>Electric Snare</name></Drum>
      <Drum pitch="42"><head>cross</head><line>-1</line><name>Closed Hi-Hat</name></Drum>
      <Drum pitch="46"><head>xcircle</head><line>-1</line><name>Open Hi-Hat</name></Drum>
      <Drum pitch="49"><head>cross</head><line>-2</line><name>Crash Cymbal 1</name></Drum>
    </museScore>
    """)


def test_line_zero_is_the_top_line():
    assert position_for_line(0) == "F5"


def test_lines_descend_a_step_at_a_time_across_the_octave():
    # The octave number turns over between C and B, not at the staff edge.
    assert [position_for_line(n) for n in range(0, 8)] == [
        "F5", "E5", "D5", "C5", "B4", "A4", "G4", "F4"]


def test_negative_lines_go_above_the_staff():
    assert [position_for_line(n) for n in (-1, -2, -3, -4)] == ["G5", "A5", "B5", "C6"]


def test_a_kit_becomes_a_drum_map(tmp_path):
    path = tmp_path / "kit.drm"
    path.write_text(KIT)
    kit, _ = load_kit(path)
    assert kit[("F4", "normal")].midi == 36
    assert kit[("G5", "x")].midi == 42
    assert kit[("A5", "x")].midi == 49


def test_noteheads_are_translated_to_musicxml_names(tmp_path):
    path = tmp_path / "kit.drm"
    path.write_text(KIT)
    kit, _ = load_kit(path)
    # MuseScore calls them cross and xcircle.
    assert ("G5", "circle-x") in kit
    assert kit[("G5", "circle-x")].midi == 46


def test_a_shared_line_is_reported_rather_than_picked(tmp_path):
    # Two snares on one line. Choosing here is how a crash became a ride.
    path = tmp_path / "kit.drm"
    path.write_text(KIT)
    kit, ambiguous = load_kit(path)
    assert ("C5", "normal") not in kit
    assert [d.midi for d in ambiguous[("C5", "normal")]] == [38, 40]
