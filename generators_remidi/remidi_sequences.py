import argparse
import math
import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage
import os
import random
import re

# ===== CONFIG =====
PPQ = 480
TICKS_PER_BAR = PPQ * 4
BPM = 120

DRUM_DIR = "sequences_remidi_drums"
BASS_DIR = "sequences_remidi_bass"
PAD_DIR = "sequences_remidi_pads"

SEQUENCE_COUNT = 8
MAX_ROW_NUMBER = 7
DEFAULT_ROWS = [0, 1, 2, 3]
DEFAULT_NOTE_LENGTH = 4
DEFAULT_SECTION_LENGTH = 64
DEFAULT_START_NOTE = "C2"
DEFAULT_PAD_COUNT = 16

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
              'F#', 'G', 'G#', 'A', 'A#', 'B']


def midi_to_ableton_name(midi_num):
    octave = (midi_num // 12) - 2
    note_index = midi_num % 12
    return f"{NOTE_NAMES[note_index]}{octave}"


def ableton_name_to_midi(note_name):
    match = re.match(r"^([A-G]#?)(-?\d+)$", note_name)
    if not match:
        raise ValueError(f"Invalid note name: {note_name}")

    name, octave = match.groups()
    return (int(octave) + 2) * 12 + NOTE_NAMES.index(name)


def parse_start_note_arg(start_note_string):
    try:
        start_midi = ableton_name_to_midi(start_note_string)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--start-note must be an Ableton note like C2") from exc

    if start_midi < 0 or start_midi > 127:
        raise argparse.ArgumentTypeError("--start-note must resolve to MIDI note 0-127")
    return start_midi


def parse_pad_count_arg(pad_count_string):
    try:
        pad_count = int(pad_count_string)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--pad-count must be a whole number") from exc

    if pad_count <= 0:
        raise argparse.ArgumentTypeError("--pad-count must be greater than 0")
    return pad_count


def parse_rows_arg(rows_string):
    rows = []
    for part in rows_string.split(","):
        part = part.strip()
        if not part:
            continue
        if not part.isdigit():
            raise ValueError(f"Invalid row number: {part}")
        row_num = int(part)
        if row_num < 0 or row_num > MAX_ROW_NUMBER:
            raise ValueError(f"Row number must be between 0 and {MAX_ROW_NUMBER}: {row_num}")
        rows.append(row_num)
    if not rows:
        raise ValueError("At least one row number is required")
    return list(dict.fromkeys(rows))


def parse_note_length_arg(note_length_string):
    try:
        note_length = float(note_length_string)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--note-length must be a number of bars") from exc

    if note_length <= 0:
        raise argparse.ArgumentTypeError("--note-length must be greater than 0")
    return note_length


def parse_section_length_arg(section_length_string):
    try:
        section_length = float(section_length_string)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--section-length must be a number of bars") from exc

    if section_length <= 0:
        raise argparse.ArgumentTypeError("--section-length must be greater than 0")
    return section_length


def bars_to_ticks(bars):
    return round(bars * TICKS_PER_BAR)


def bars_to_note_count(section_length, note_length):
    note_count = section_length / note_length
    if not math.isclose(note_count, round(note_count), rel_tol=0, abs_tol=1e-9):
        raise argparse.ArgumentTypeError(
            "--section-length must be an exact multiple of --note-length"
        )
    return int(round(note_count))


def map_to_output_range(note, start_midi, pad_count):
    return start_midi + (note % pad_count)


def build_section_map(row_numbers):
    section_map = {}
    for index, section in enumerate(SECTION_ORDER):
        row_num = row_numbers[index] if index < len(row_numbers) else row_numbers[-1]
        suffix = SECTION_SUFFIX[section]
        section_map[section] = f"{row_num}_{suffix}"
    return section_map


def _row_number(row_id):
    return int(row_id.split("_")[0])
ROW_NOTE_MAP = {
    f"{row}_{suffix}": list(range(row * 16 + index * 8, row * 16 + index * 8 + 8))
    for row in range(MAX_ROW_NUMBER + 1)
    for index, suffix in enumerate(["A", "B"])
}

SECTION_MAP = {
    "Intro": "0_A",
    "Verse": "0_B",
    "PreChorus": "1_A",
    "Chorus": "1_B",
    "Bridge": "2_A",
}

BASS_SECTIONS = {"Intro", "Verse", "PreChorus", "Chorus"}
PAD_SECTIONS = {"Intro", "Verse", "PreChorus", "Chorus", "Bridge"}
SECTION_ORDER = ["Intro", "Verse", "PreChorus", "Chorus", "Bridge"]
SECTION_SUFFIX = {"Intro": "A", "Verse": "B", "PreChorus": "A", "Chorus": "B", "Bridge": "A"}

# ===== ARRANGEMENTS =====
ARRANGEMENTS = [
    ["Intro", "Verse", "PreChorus", "Chorus",
     "Verse", "PreChorus", "Chorus",
     "Bridge", "Chorus"],

    ["Intro", "Verse", "Chorus",
     "Verse", "Chorus",
     "Bridge", "Chorus"],

    ["Intro", "Verse", "PreChorus", "Chorus",
     "Verse", "Chorus",
     "Bridge", "PreChorus", "Chorus"],

    ["Intro", "Verse", "Chorus",
     "Bridge", "Chorus"]
]


# ===== MIDI SETUP =====
def create_midi(name):
    mid = MidiFile(ticks_per_beat=PPQ)
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(MetaMessage('track_name', name=name, time=0))

    tempo = mido.bpm2tempo(BPM)
    track.append(MetaMessage('set_tempo', tempo=tempo, time=0))

    track.append(MetaMessage('time_signature',
                             numerator=4,
                             denominator=4,
                             clocks_per_click=24,
                             notated_32nd_notes_per_beat=8,
                             time=0))
    return mid, track


def add_clip(track, note, duration_ticks):
    track.append(Message('note_on', note=note, velocity=100, time=0))
    track.append(Message('note_off', note=note, velocity=100, time=duration_ticks))


# ===== CLIP SELECTION =====
def pick_two_clips(row_id):
    return random.sample(ROW_NOTE_MAP[row_id][:4], 2)


def pick_pad_chord(row_id):
    return tuple(random.sample(ROW_NOTE_MAP[row_id][:6], 3))


def pick_short_fill(allowed_row_ids):
    candidates = []
    for row_id in allowed_row_ids:
        if _row_number(row_id) >= 2:
            candidates.extend(ROW_NOTE_MAP[row_id])
    if not candidates:
        for row_id in allowed_row_ids:
            if _row_number(row_id) >= 1:
                candidates.extend(ROW_NOTE_MAP[row_id])
    if not candidates:
        candidates = [note for row_id in allowed_row_ids for note in ROW_NOTE_MAP[row_id]]
    return random.choice(candidates)


def pick_long_fill(allowed_row_ids):
    candidates = []
    for row_id in allowed_row_ids:
        if _row_number(row_id) >= 3 and row_id.endswith("_B"):
            candidates.extend(ROW_NOTE_MAP[row_id])
    if not candidates:
        for row_id in allowed_row_ids:
            if row_id.endswith("_B") and _row_number(row_id) >= 2:
                candidates.extend(ROW_NOTE_MAP[row_id])
    if not candidates:
        candidates = [note for row_id in allowed_row_ids for note in ROW_NOTE_MAP[row_id]]
    return random.choice(candidates)


# ===== MAIN GENERATOR =====
def generate_sequence(
    index,
    section_types,
    section_map,
    allowed_row_ids,
    note_duration_ticks,
    max_note_count,
    start_midi,
    pad_count
):

    drum_mid = drum_track = None
    bass_mid = bass_track = None
    pad_mid = pad_track = None
    track_note_counts = {section_type: 0 for section_type in section_types}

    if "drums" in section_types:
        drum_mid, drum_track = create_midi("Drums")
    if "bass" in section_types:
        bass_mid, bass_track = create_midi("Bass")
    if "pads" in section_types:
        pad_mid, pad_track = create_midi("Pads")

    arrangement_template = random.choice(ARRANGEMENTS)
    arrangement = []
    debug = []
    last_bass = None
    arrangement_index = 0

    while not all(
        track_note_counts[section_type] >= max_note_count
        for section_type in section_types
    ):
        section = arrangement_template[arrangement_index % len(arrangement_template)]
        arrangement.append(section)
        arrangement_index += 1

        if all(
            track_note_counts[section_type] >= max_note_count
            for section_type in section_types
        ):
            break

        row_id = section_map[section]

        drum_a = drum_b = fill = fill_type = None
        if "drums" in section_types and track_note_counts["drums"] < max_note_count:
            drum_a, drum_b = pick_two_clips(row_id)
            use_long = random.random() < 0.3
            if use_long:
                fill = pick_long_fill(allowed_row_ids)
                drum_structure = [
                    drum_a,
                    drum_b,
                    fill
                ]
                fill_type = "LONG"
            else:
                fill = pick_short_fill(allowed_row_ids)
                drum_structure = [
                    drum_a,
                    drum_b,
                    fill
                ]
                fill_type = "SHORT"

            for d_note in drum_structure:
                if track_note_counts["drums"] >= max_note_count:
                    break
                add_clip(drum_track, map_to_output_range(d_note, start_midi, pad_count), note_duration_ticks)
                track_note_counts["drums"] += 1

            drum_a = map_to_output_range(drum_a, start_midi, pad_count)
            drum_b = map_to_output_range(drum_b, start_midi, pad_count)
            fill = map_to_output_range(fill, start_midi, pad_count)

        bass_a = bass_b = None
        if "bass" in section_types and track_note_counts["bass"] < max_note_count:
            if section in BASS_SECTIONS:
                bass_a, bass_b = pick_two_clips(row_id)
                last_bass = (bass_a, bass_b)
            else:
                if last_bass is None:
                    last_bass = pick_two_clips(section_map.get("Verse", "0_B"))
                bass_a, bass_b = last_bass

            for bass_note in [bass_a, bass_b]:
                if track_note_counts["bass"] >= max_note_count:
                    break
                add_clip(bass_track, map_to_output_range(bass_note, start_midi, pad_count), note_duration_ticks)
                track_note_counts["bass"] += 1

            bass_a = map_to_output_range(bass_a, start_midi, pad_count)
            bass_b = map_to_output_range(bass_b, start_midi, pad_count)

        pad_notes = ()
        if "pads" in section_types and track_note_counts["pads"] < max_note_count:
            pad_notes = pick_pad_chord(row_id)
            for pad_note in pad_notes:
                if track_note_counts["pads"] >= max_note_count:
                    break
                add_clip(pad_track, map_to_output_range(pad_note, start_midi, pad_count), note_duration_ticks)
                track_note_counts["pads"] += 1
            pad_notes = tuple(map_to_output_range(pad_note, start_midi, pad_count) for pad_note in pad_notes)

        debug_entry = {
            "section": section,
            "drums": (drum_a, drum_b) if drum_a is not None else None,
            "fill": fill,
            "fill_type": fill_type,
            "bass": (bass_a, bass_b) if bass_a is not None else None,
            "pads": pad_notes
        }
        debug.append(debug_entry)

    if drum_track is not None:
        drum_track.append(MetaMessage('end_of_track', time=0))
    if bass_track is not None:
        bass_track.append(MetaMessage('end_of_track', time=0))
    if pad_track is not None:
        pad_track.append(MetaMessage('end_of_track', time=0))

    if drum_mid is not None:
        drum_path = os.path.join(DRUM_DIR, f"sequence_{index+1:02d}.mid")
        drum_mid.save(drum_path)
    if bass_mid is not None:
        bass_path = os.path.join(BASS_DIR, f"sequence_{index+1:02d}.mid")
        bass_mid.save(bass_path)
    if pad_mid is not None:
        pad_path = os.path.join(PAD_DIR, f"sequence_{index+1:02d}.mid")
        pad_mid.save(pad_path)

    return arrangement, debug


# ===== MAIN =====
def main():
    parser = argparse.ArgumentParser(description="Generate aligned drum, bass, and pad MIDI sequences.")
    parser.add_argument(
        "section_type",
        choices=["drums", "bass", "pads", "all"],
        help="Which type of sections to create: drums, bass, pads, or all"
    )
    parser.add_argument(
        "--rows",
        default=",".join(str(r) for r in DEFAULT_ROWS),
        help="Comma-separated row numbers to use when generating sequences (0-7)."
    )
    parser.add_argument(
        "--note-length",
        dest="note_length",
        type=parse_note_length_arg,
        default=DEFAULT_NOTE_LENGTH,
        help="Absolute length in bars of each generated note; default is 4."
    )
    parser.add_argument(
        "--section-length",
        dest="section_length",
        type=parse_section_length_arg,
        default=DEFAULT_SECTION_LENGTH,
        help="Total length in bars of each generated sequence; default is 64."
    )
    parser.add_argument(
        "--start-note",
        dest="start_note",
        type=parse_start_note_arg,
        default=ableton_name_to_midi(DEFAULT_START_NOTE),
        help="First Ableton note in the output pad range; default is C2."
    )
    parser.add_argument(
        "--pad-count",
        dest="pad_count",
        type=parse_pad_count_arg,
        default=DEFAULT_PAD_COUNT,
        help="Number of chromatic pads in the output range; default is 16."
    )
    args = parser.parse_args()
    if args.section_type == "all":
        section_types = ["drums", "bass", "pads"]
    else:
        section_types = [args.section_type]

    row_numbers = parse_rows_arg(args.rows)
    note_length = args.note_length
    section_length = args.section_length
    start_midi = args.start_note
    pad_count = args.pad_count
    if start_midi + pad_count - 1 > 127:
        parser.error("--start-note plus --pad-count must stay within MIDI note 0-127")

    note_duration_ticks = bars_to_ticks(note_length)
    try:
        max_note_count = bars_to_note_count(section_length, note_length)
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))

    section_map = build_section_map(row_numbers)
    allowed_row_ids = {f"{row}_{suffix}" for row in row_numbers for suffix in ["A", "B"]}

    if "drums" in section_types:
        os.makedirs(DRUM_DIR, exist_ok=True)
    if "bass" in section_types:
        os.makedirs(BASS_DIR, exist_ok=True)
    if "pads" in section_types:
        os.makedirs(PAD_DIR, exist_ok=True)

    print("=" * 60)
    print(f"Generating aligned {' + '.join(section_types)} sequences")
    print(f"Section length: {section_length:g} bars")
    print(f"Note length: {note_length:g} bars")
    print(f"Notes per sequence: {max_note_count}")
    print(
        "Output range: "
        f"{midi_to_ableton_name(start_midi)} to "
        f"{midi_to_ableton_name(start_midi + pad_count - 1)} "
        f"({pad_count} pads)"
    )
    print("=" * 60)

    for i in range(SEQUENCE_COUNT):
        arrangement, debug = generate_sequence(
            i,
            section_types,
            section_map,
            allowed_row_ids,
            note_duration_ticks,
            max_note_count,
            start_midi,
            pad_count
        )

        print(f"\nSequence {i+1:02d}")
        print("Arrangement:", " -> ".join(arrangement))

        for entry in debug:
            outputs = []
            if "drums" in section_types and entry["drums"] is not None:
                drum_names = [midi_to_ableton_name(n) for n in entry["drums"]]
                fill_name = midi_to_ableton_name(entry["fill"])
                outputs.append(f"drums={drum_names} fill={fill_name} ({entry['fill_type']})")
            if "bass" in section_types and entry["bass"] is not None:
                bass_names = [midi_to_ableton_name(n) for n in entry["bass"]]
                outputs.append(f"bass={bass_names}")
            if "pads" in section_types and entry["pads"]:
                pad_names = [midi_to_ableton_name(n) for n in entry["pads"]]
                outputs.append(f"pads={pad_names}")

            if outputs:
                print(f"  {entry['section']}: " + " | ".join(outputs))

    print("\nDone")
    print("No bass gaps - fully continuous")


if __name__ == "__main__":
    main()
