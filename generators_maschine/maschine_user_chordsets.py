import argparse
import json
import os
import re
import sys
import uuid
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

import mido


SHARP_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLAT_NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
NOTE_NAME_TO_PITCH_CLASS = {
    "C": 0,
    "B#": 0,
    "C#": 1,
    "DB": 1,
    "D": 2,
    "D#": 3,
    "EB": 3,
    "E": 4,
    "FB": 4,
    "E#": 5,
    "F": 5,
    "F#": 6,
    "GB": 6,
    "G": 7,
    "G#": 8,
    "AB": 8,
    "A": 9,
    "A#": 10,
    "BB": 10,
    "B": 11,
    "CB": 11,
}

CHORD_TEMPLATES = {
    (0, 4, 7): "maj",
    (0, 3, 7): "m",
    (0, 3, 6): "dim",
    (0, 4, 8): "aug",
    (0, 5, 7): "sus4",
    (0, 2, 7): "sus2",
    (0, 7): "5",
    (0, 4, 7, 10): "7",
    (0, 4, 7, 11): "maj7",
    (0, 3, 7, 10): "m7",
    (0, 3, 7, 11): "m(maj7)",
    (0, 3, 6, 9): "dim7",
    (0, 3, 6, 10): "m7b5",
    (0, 4, 8, 10): "aug7",
    (0, 4, 8, 11): "augmaj7",
    (0, 5, 7, 10): "7sus4",
    (0, 2, 7, 10): "7sus2",
    (0, 4, 7, 9): "6",
    (0, 3, 7, 9): "m6",
    (0, 2, 4, 7): "add9",
    (0, 2, 3, 7): "madd9",
    (0, 2, 4, 7, 10): "9",
    (0, 2, 4, 7, 11): "maj9",
    (0, 2, 3, 7, 10): "m9",
    (0, 2, 3, 7, 11): "m(maj9)",
    (0, 2, 4, 7, 9): "6/9",
    (0, 2, 3, 7, 9): "m6/9",
}

EXTENSION_NAMES = {
    1: "b9",
    2: "9",
    3: "#9",
    5: "11",
    6: "#11",
    8: "b13",
    9: "13",
    10: "7",
    11: "maj7",
}


@dataclass
class NoteStart:
    tick: int
    note: int
    channel: int


@dataclass
class ChordEvent:
    tick: int
    notes: List[int]
    name: str


@dataclass
class KeyInfo:
    root_name: str
    root_pitch_class: int
    mode_suffix: str

    @property
    def set_name_prefix(self) -> str:
        return f"{self.root_name}{self.mode_suffix}"


def midi_note_name(note: int, note_names: Sequence[str]) -> str:
    # Ableton-style octave numbering used throughout this repository: C3 == MIDI 60.
    return f"{note_names[note % 12]}{(note // 12) - 2}"


def pitch_class_name(pitch_class: int, note_names: Sequence[str]) -> str:
    return note_names[pitch_class % 12]


def format_position(tick: int, ticks_per_beat: int) -> str:
    ticks_per_bar = ticks_per_beat * 4
    bar = (tick // ticks_per_bar) + 1
    beat_tick = tick % ticks_per_bar
    beat = (beat_tick // ticks_per_beat) + 1
    sub_tick = beat_tick % ticks_per_beat
    return f"{bar}:{beat:02d}:{sub_tick:03d}"


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


def interval_set_for_root(pitch_classes: Sequence[int], root: int) -> Tuple[int, ...]:
    return tuple(sorted({(pitch_class - root) % 12 for pitch_class in pitch_classes}))


def identify_chord(notes: Sequence[int], note_names: Sequence[str]) -> str:
    pitch_classes = sorted({note % 12 for note in notes})
    bass_pitch_class = min(notes) % 12

    if len(pitch_classes) == 1:
        return pitch_class_name(pitch_classes[0], note_names)

    exact_matches = []
    for root in pitch_classes:
        intervals = interval_set_for_root(pitch_classes, root)
        if intervals in CHORD_TEMPLATES:
            exact_matches.append((root, CHORD_TEMPLATES[intervals]))

    if exact_matches:
        root, quality = prefer_bass_or_first_match(exact_matches, bass_pitch_class)
        return slash_chord_name(root, quality, bass_pitch_class, note_names)

    best_match = None
    best_score = -1
    for root in pitch_classes:
        intervals = set(interval_set_for_root(pitch_classes, root))
        for template, quality in CHORD_TEMPLATES.items():
            template_set = set(template)
            if not template_set.issubset(intervals):
                continue

            extra_count = len(intervals - template_set)
            score = (len(template_set) * 4) - (extra_count * 2)
            if root == bass_pitch_class:
                score += 1

            if score > best_score:
                best_score = score
                best_match = (root, quality, tuple(sorted(intervals - template_set)))

    if best_match:
        root, quality, extras = best_match
        extension = "".join(EXTENSION_NAMES.get(extra, f"add{extra}") for extra in extras)
        return slash_chord_name(root, f"{quality}{extension}", bass_pitch_class, note_names)

    note_list = " ".join(pitch_class_name(pitch_class, note_names) for pitch_class in pitch_classes)
    return f"Unknown ({note_list})"


def prefer_bass_or_first_match(matches: Sequence[Tuple[int, str]], bass_pitch_class: int) -> Tuple[int, str]:
    for root, quality in matches:
        if root == bass_pitch_class:
            return root, quality

    return matches[0]


def slash_chord_name(root: int, quality: str, bass_pitch_class: int, note_names: Sequence[str]) -> str:
    chord_name = f"{pitch_class_name(root, note_names)}{quality}"
    if root != bass_pitch_class:
        chord_name = f"{chord_name}/{pitch_class_name(bass_pitch_class, note_names)}"

    return chord_name


def parse_key_from_filename(midi_path: str) -> KeyInfo:
    filename = os.path.splitext(os.path.basename(midi_path))[0]
    parenthetical_matches = re.findall(r"\(([^()]*)\)", filename)
    if not parenthetical_matches:
        raise ValueError(
            "Could not detect root key from filename. Expected a name like "
            "'All Borrowed & Modal Chords (F Minor).mid'."
        )

    key_text = parenthetical_matches[-1].strip()
    match = re.match(r"^([A-Ga-g](?:#|b)?)(?:\s+|-)?(major|minor|maj|min)?$", key_text, re.IGNORECASE)
    if not match:
        raise ValueError(f"Could not parse key from filename text: ({key_text})")

    root_name = format_root_name(match.group(1))
    mode_text = (match.group(2) or "major").lower()
    mode_suffix = "min" if mode_text in {"minor", "min"} else "maj"
    root_pitch_class = NOTE_NAME_TO_PITCH_CLASS[root_name.upper()]

    return KeyInfo(root_name=root_name, root_pitch_class=root_pitch_class, mode_suffix=mode_suffix)


def format_root_name(root_name: str) -> str:
    letter = root_name[0].upper()
    accidental = root_name[1:]
    if accidental == "b":
        return f"{letter}b"
    if accidental == "#":
        return f"{letter}#"
    return letter


def root_reference_midi(chord_events: Sequence[ChordEvent], root_pitch_class: int) -> int:
    lowest_note = min(note for event in chord_events for note in event.notes)
    return lowest_note - ((lowest_note - root_pitch_class) % 12)


def relative_notes(notes: Sequence[int], root_midi: int) -> List[int]:
    notes_relative_to_key = [note - root_midi for note in sorted(set(notes))]
    if not notes_relative_to_key:
        return []

    first_note = notes_relative_to_key[0] % 12
    compact_notes = []

    for note in notes_relative_to_key:
        compact_note = note % 12
        while compact_note < first_note:
            compact_note += 12
        while compact_note in compact_notes:
            compact_note += 12
        compact_notes.append(compact_note)

    return sorted(compact_notes)


def build_chordset_payload(
    set_name: str,
    chord_events: Sequence[ChordEvent],
    root_midi: int,
    slot_count: int = 12,
) -> dict:
    chords = []
    for slot_index in range(slot_count):
        if slot_index < len(chord_events):
            event = chord_events[slot_index]
            chords.append({"name": event.name, "notes": relative_notes(event.notes, root_midi)})
        else:
            chords.append({"name": f"Chd {slot_index + 1}", "notes": []})

    return {
        "chords": chords,
        "name": set_name,
        "typeId": "native-instruments-chord-set",
        "uuid": str(uuid.uuid4()),
        "version": "1.0.0",
    }


def write_chordset_json_files(
    chord_events: Sequence[ChordEvent],
    key_info: KeyInfo,
    root_midi: int,
    output_dir: str,
    chords_per_set: int = 12,
) -> List[str]:
    os.makedirs(output_dir, exist_ok=True)
    output_paths = []

    for chunk_index, start_index in enumerate(range(0, len(chord_events), chords_per_set), 1):
        chunk = chord_events[start_index : start_index + chords_per_set]
        set_name = f"{key_info.set_name_prefix}.{chunk_index:02d}"
        payload = build_chordset_payload(set_name, chunk, root_midi, slot_count=chords_per_set)
        output_path = os.path.join(output_dir, f"{set_name}.json")

        with open(output_path, "w", encoding="utf-8") as output_file:
            json.dump(payload, output_file, indent=4)
            output_file.write("\n")

        output_paths.append(output_path)

    return output_paths


def detect_chord_sequence(
    midi_path: str,
    tolerance_ticks: int,
    include_drums: bool,
    note_names: Sequence[str],
    minimum_notes: int,
) -> Tuple[mido.MidiFile, List[ChordEvent]]:
    midi_file = mido.MidiFile(midi_path)
    note_starts = sorted(iter_note_starts(midi_file, include_drums), key=lambda item: item.tick)
    grouped_notes = group_note_starts(note_starts, tolerance_ticks)

    chord_events = []
    for tick, notes in grouped_notes:
        if len(notes) < minimum_notes:
            continue

        name = identify_chord(notes, note_names)
        chord_events.append(ChordEvent(tick=tick, notes=notes, name=name))

    return midi_file, chord_events


def print_detected_sequence(
    midi_path: str,
    midi_file: mido.MidiFile,
    chord_events: Sequence[ChordEvent],
    note_names: Sequence[str],
    show_notes: bool,
    show_timing: bool,
) -> None:
    print("Maschine user chordset generator")
    print(f"Input MIDI: {os.path.basename(midi_path)}")
    if show_timing:
        print(f"Ticks per beat: {midi_file.ticks_per_beat}")
    print()

    if not chord_events:
        print("No chord sequence detected.")
        return

    if show_notes or show_timing:
        for index, event in enumerate(chord_events, 1):
            line = f"{index:02d}. {event.name}"
            if show_timing:
                position = format_position(event.tick, midi_file.ticks_per_beat)
                line = f"{index:02d}. {position}  tick {event.tick:<6}  {event.name}"
            if show_notes:
                notes = ", ".join(midi_note_name(note, note_names) for note in event.notes)
                line = f"{line:<34}  [{notes}]"
            print(line)
        print()

    print("Detected sequence:")
    print(" - ".join(event.name for event in chord_events))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect a MIDI chord sequence before generating Maschine user chordsets."
    )
    parser.add_argument("midi_file", help="Path to the MIDI file containing the chord sequence.")
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
        help="Minimum simultaneous notes required to print an event. Default: 2.",
    )
    parser.add_argument(
        "--include-drums",
        action="store_true",
        help="Include channel 10 MIDI notes instead of skipping them.",
    )
    parser.add_argument(
        "--flats",
        action="store_true",
        help="Print note and chord names with flats instead of sharps.",
    )
    parser.add_argument(
        "--show-notes",
        action="store_true",
        help="Also print the detected MIDI note names for each chord event.",
    )
    parser.add_argument(
        "--show-timing",
        action="store_true",
        help="Also print bar/beat positions and MIDI ticks for each chord event.",
    )
    parser.add_argument(
        "--output-dir",
        default="maschine_user_chordsets",
        help="Directory to write generated Maschine user chordset JSON files. Default: maschine_user_chordsets.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    note_names = FLAT_NAMES if args.flats else SHARP_NAMES

    try:
        midi_file, chord_events = detect_chord_sequence(
            midi_path=args.midi_file,
            tolerance_ticks=args.tolerance_ticks,
            include_drums=args.include_drums,
            note_names=note_names,
            minimum_notes=args.minimum_notes,
        )
        key_info = parse_key_from_filename(args.midi_file)
    except OSError as error:
        print(f"Could not read MIDI file: {error}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"Could not generate chordsets: {error}", file=sys.stderr)
        return 1

    print_detected_sequence(args.midi_file, midi_file, chord_events, note_names, args.show_notes, args.show_timing)
    if not chord_events:
        return 1

    root_midi = root_reference_midi(chord_events, key_info.root_pitch_class)
    output_paths = write_chordset_json_files(chord_events, key_info, root_midi, args.output_dir)

    print()
    print("Generated JSON chordsets:")
    for output_path in output_paths:
        print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
