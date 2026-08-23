"""Give the notes in a MusicXML drum part their sounds."""

import argparse
import re
import sys
import xml.etree.ElementTree as ET

from .convert import Unmapped, convert, survey
from .mapping import DEFAULT_MAP, parse_overrides
from .musescore import load_kit

# ElementTree drops the doctype, and some readers want it. Carried across
# verbatim from the input rather than reconstructed.
DOCTYPE = re.compile(rb"<!DOCTYPE[^>]*>", re.S)


def _doctype_of(path):
    with open(path, "rb") as f:
        match = DOCTYPE.search(f.read(2048))
    return match.group(0).decode() if match else None


def _write(tree, path, doctype):
    ET.indent(tree, space="  ")
    body = ET.tostring(tree.getroot(), encoding="unicode")
    header = '<?xml version="1.0" encoding="UTF-8"?>\n'
    if doctype:
        header += doctype + "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + body + "\n")


def main(argv=None):
    p = argparse.ArgumentParser(prog="drummap", description=__doc__)
    p.add_argument("input")
    p.add_argument("-o", "--output", help="defaults to INPUT with .drums.xml")
    p.add_argument("--survey", action="store_true",
                   help="list the positions and noteheads found, and stop")
    p.add_argument("--map", action="append", default=[], metavar="POS[:HEAD]=MIDI",
                   help="override one entry, e.g. A5:x=49")
    p.add_argument("--kit", metavar="FILE.drm",
                   help="take the map from a MuseScore kit instead of the defaults")
    p.add_argument("--part-name", default="Drumset")
    args = p.parse_args(argv)

    tree = ET.parse(args.input)
    overrides = parse_overrides(args.map)

    ambiguous = {}
    if args.kit:
        from_kit, ambiguous = load_kit(args.kit)
        overrides = {**from_kit, **overrides}

    # Only an ambiguity the score actually lands on has to be settled.
    unsettled = {k: v for k, v in ambiguous.items()
                 if k in survey(tree) and k not in overrides}
    if unsettled:
        for (pos, head), drums in sorted(unsettled.items()):
            options = ", ".join(f"{d.midi} {d.name}" for d in drums)
            print(f"drummap: {pos} ({head}) could be {options}", file=sys.stderr)
        print("the kit puts several drums there; choose with "
              "--map POSITION:NOTEHEAD=MIDI", file=sys.stderr)
        return 1

    if args.survey:
        found = survey(tree)
        if not found:
            print("no pitched notes: this part is already unpitched")
            return 0
        table = {**DEFAULT_MAP, **overrides}
        width = max(len(pos) for pos, _ in found)
        for (pos, head), count in sorted(found.items(), key=lambda kv: -kv[1]):
            drum = table.get((pos, head))
            print(f"  {pos:<{width}}  {head:<9} {count:>5}  "
                  f"{drum.name if drum else 'UNMAPPED'}")
        return 0

    try:
        used = convert(tree, overrides, args.part_name)
    except Unmapped as e:
        print(f"drummap: {e}", file=sys.stderr)
        print("run with --survey to see what is in the file, "
              "then add entries with --map", file=sys.stderr)
        return 1

    if not used:
        print("no pitched notes: this part already has its sounds")
        return 0

    out = args.output or re.sub(r"\.(musicxml|xml)$", "", args.input) + ".drums.xml"
    _write(tree, out, _doctype_of(args.input))
    for drum in sorted(used.values(), key=lambda d: d.midi):
        print(f"  {drum.name} (MIDI {drum.midi})")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
