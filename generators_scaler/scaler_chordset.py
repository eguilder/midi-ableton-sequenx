import argparse
import os
import sys
import uuid
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple

import mido


@dataclass
class NoteStart:
    tick: int
    note: int
    channel: int


def iter_note_starts(midi_file: mido.MidiFile, include_drums: bool) -> Iterable[NoteStart]:
    absolute_tick = 0

    for message in mido.merge_tracks(midi_file.tracks):
        absolute_tick += message.time

        if message.type != "note_on" or message.velocity == 0:
            continue

        channel = getattr(message, "channel", 0)
        if not include_drums and channel == 9:
            continue

        yield NoteStart(absolute_tick, message.note, channel)


def group_note_starts(note_starts: Sequence[NoteStart], tolerance_ticks: int) -> List[Tuple[int, List[int]]]:
    if not note_starts:
        return []

    groups = []
    current_tick = note_starts[0].tick
    current_notes = [note_starts[0].note]
    last_tick = note_starts[0].tick

    for note_start in note_starts[1:]:
        if note_start.tick - last_tick <= tolerance_ticks:
            current_notes.append(note_start.note)
        else:
            groups.append((current_tick, sorted(set(current_notes))))
            current_tick = note_start.tick
            current_notes = [note_start.note]

        last_tick = note_start.tick

    groups.append((current_tick, sorted(set(current_notes))))
    return groups


def detect_chords(midi_path: str, tolerance_ticks: int, minimum_notes: int, include_drums: bool) -> List[List[int]]:
    midi_file = mido.MidiFile(midi_path)
    note_starts = sorted(iter_note_starts(midi_file, include_drums), key=lambda item: item.tick)
    grouped_notes = group_note_starts(note_starts, tolerance_ticks)

    return [notes for _tick, notes in grouped_notes if len(notes) >= minimum_notes]


def resolve_output_path(output_filename: str, output_dir: Optional[str]) -> str:
    if not output_filename.lower().endswith(".xml"):
        output_filename = f"{output_filename}.xml"

    if output_dir:
        return os.path.join(output_dir, os.path.basename(output_filename))

    return output_filename


def write_scaler_chordset(chords: Sequence[Sequence[int]], output_path: str) -> str:
    output_dir = os.path.dirname(os.path.abspath(output_path))
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    chordset_uuid = str(uuid.uuid4())

    with open(output_path, "w", encoding="utf-8", newline="\n") as output_file:
        output_file.write('<?xml version="1.0" encoding="UTF-8"?>\n\n')
        output_file.write(f'<CHORDSET version="2" uuid="{chordset_uuid}">\n')

        for chord in chords:
            output_file.write("  <CHORD>\n")
            for note in chord:
                output_file.write(f'    <NOTE MIDI="{note}"/>\n')
            output_file.write("  </CHORD>\n")

        output_file.write("</CHORDSET>\n")

    return chordset_uuid


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a MIDI chord sequence into a Scaler chordset XML file."
    )
    parser.add_argument(
        "--input-file",
        required=True,
        help="Path to the MIDI file containing the chord sequence.",
    )
    parser.add_argument(
        "--output-file",
        required=True,
        help="Output XML filename. The .xml extension is added if omitted.",
    )
    parser.add_argument(
        "--output-dir",
        default="scaler_user_chordsets",
        help="Output folder. Default: scaler_user_chordsets.",
    )
    parser.add_argument(
        "--tolerance-ticks",
        type=int,
        default=30,
        help="Group note starts this many ticks apart into one chord. Default: 30.",
    )
    parser.add_argument(
        "--minimum-notes",
        type=int,
        default=2,
        help="Minimum simultaneous notes required to write a chord. Default: 2.",
    )
    parser.add_argument(
        "--include-drums",
        action="store_true",
        help="Include channel 10 MIDI notes instead of skipping them.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        chords = detect_chords(
            midi_path=args.input_file,
            tolerance_ticks=args.tolerance_ticks,
            minimum_notes=args.minimum_notes,
            include_drums=args.include_drums,
        )
        output_path = resolve_output_path(args.output_file, args.output_dir)
        chordset_uuid = write_scaler_chordset(chords, output_path)
    except OSError as error:
        print(f"Could not convert chordset: {error}", file=sys.stderr)
        return 1

    print(f"Detected chords: {len(chords)}")
    print(f"UUID: {chordset_uuid}")
    print(f"Output XML: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
