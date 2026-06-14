import itertools
import os
import re

import mido
from mido import Message, MetaMessage, MidiFile, MidiTrack


OUTPUT_DIR = "sequences_beatmaker3"
PPQ = 480
TICKS_PER_BAR = PPQ * 4

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

NOTES_DATA = [
    {"file_note": "C#1", "track_name": "Intro C#1"},
    {"file_note": "D#1", "track_name": "Fill 1 D#1"},
    {"file_note": "F#1", "track_name": "Verse 1 F#1"},
    {"file_note": "G#1", "track_name": "Verse 2 G#1"},
    {"file_note": "A#1", "track_name": "Fill 2 A#1"},
    {"file_note": "C#2", "track_name": "Chorus 1 C#2"},
    {"file_note": "D#2", "track_name": "Chorus 2 D#2"},
    {"file_note": "F#2", "track_name": "Break F#2"},
    {"file_note": "G#2", "track_name": "Special G#2"},
    {"file_note": "A#2", "track_name": "Ending A#2"},
]

BODY_SECTIONS = {"verse", "chorus", "special"}
MAIN_SECTIONS = {"verse", "chorus"}
TRANSITIONS = {"fill", "break", "ending"}

# Each tuple is one 4-bar block: (section, optional_bar_4_transition).
# The intro block is 2 bars intro + 2 bars of the named body section.
ARRANGEMENTS = [
    [
        ("intro", "verse"),
        ("verse", "fill"),
        ("chorus", "break"),
        ("verse", None),
        ("chorus", "fill"),
        ("special", None),
        ("verse", "break"),
        ("chorus", None),
        ("verse", "fill"),
        ("chorus", "break"),
        ("verse", None),
        ("special", None),
        ("chorus", "fill"),
        ("verse", "break"),
        ("chorus", None),
        ("chorus", "ending"),
    ],
    [
        ("intro", "chorus"),
        ("special", None),
        ("verse", "break"),
        ("chorus", "fill"),
        ("verse", None),
        ("special", None),
        ("chorus", "break"),
        ("verse", "fill"),
        ("chorus", None),
        ("special", None),
        ("verse", "break"),
        ("chorus", "fill"),
        ("verse", None),
        ("chorus", "break"),
        ("verse", None),
        ("chorus", "ending"),
    ],
    [
        ("intro", "verse"),
        ("verse", None),
        ("special", None),
        ("verse", "fill"),
        ("chorus", "break"),
        ("chorus", None),
        ("special", None),
        ("verse", "break"),
        ("chorus", "fill"),
        ("special", None),
        ("verse", None),
        ("chorus", "break"),
        ("chorus", None),
        ("special", None),
        ("verse", "fill"),
        ("chorus", "ending"),
    ],
    [
        ("intro", "special"),
        ("verse", "fill"),
        ("special", None),
        ("verse", "fill"),
        ("chorus", None),
        ("special", None),
        ("chorus", "break"),
        ("verse", None),
        ("chorus", "fill"),
        ("special", None),
        ("verse", "break"),
        ("chorus", None),
        ("special", None),
        ("verse", "fill"),
        ("chorus", None),
        ("verse", "ending"),
    ],
    [
        ("intro", "verse"),
        ("special", None),
        ("verse", "fill"),
        ("verse", "break"),
        ("chorus", None),
        ("special", None),
        ("chorus", "fill"),
        ("special", None),
        ("verse", "break"),
        ("verse", None),
        ("chorus", "fill"),
        ("special", None),
        ("chorus", "break"),
        ("verse", None),
        ("chorus", None),
        ("chorus", "ending"),
    ],
]


def parse_note(note):
    match = re.match(r"^([A-G]#?)(-?\d+)$", note)
    if not match:
        raise ValueError(f"Invalid note: {note}")

    name, octave = match.groups()
    return name, int(octave)


def note_to_midi(note):
    name, octave = parse_note(note)
    return (octave + 2) * 12 + NOTE_NAMES.index(name)


def group(notes, prefix):
    return [note for note in notes if note["track_name"].startswith(prefix)]


def validate_arrangement(blocks, filename):
    if len(blocks) != 16:
        raise ValueError(f"{filename} must have 16 four-bar blocks")

    first_section, first_body = blocks[0]
    if first_section != "intro" or first_body not in BODY_SECTIONS:
        raise ValueError(f"{filename} must start with 2 bars intro plus a body section")

    for block_index, (section_type, transition) in enumerate(blocks[1:], start=1):
        if section_type not in BODY_SECTIONS:
            raise ValueError(f"{filename} block {block_index + 1} must use Verse, Chorus, or Special")
        if transition is not None and transition not in TRANSITIONS:
            raise ValueError(f"{filename} block {block_index + 1} has invalid transition {transition}")

    for block_index, (section_type, transition) in enumerate(blocks[:-1]):
        if transition == "ending":
            raise ValueError(f"{filename} may only use Ending in the final block")
        if transition == "break":
            next_section = blocks[block_index + 1][0]
            if next_section not in MAIN_SECTIONS:
                raise ValueError(f"{filename} has a Break before {next_section}")

    final_section, final_transition = blocks[-1]
    if final_section not in BODY_SECTIONS or final_transition != "ending":
        raise ValueError(f"{filename} must end with 3 bars body + 1 bar Ending")


def add_note(track, midi_note, bars):
    track.append(Message("note_on", note=midi_note, velocity=100, time=0))
    track.append(Message("note_off", note=midi_note, velocity=0, time=TICKS_PER_BAR * bars))


def add_body(track, section_type, cycles, bars):
    add_note(track, next(cycles[section_type])["midi"], bars)


def add_transition(track, transition, cycles):
    add_note(track, next(cycles[transition])["midi"], 1)


def add_block(track, section_type, transition, cycles):
    if section_type == "intro":
        add_note(track, next(cycles["intro"])["midi"], 2)
        add_body(track, transition, cycles, 2)
        return

    if transition is None:
        add_body(track, section_type, cycles, 4)
        return

    add_body(track, section_type, cycles, 3)
    add_transition(track, transition, cycles)


def rotate_group(group_items, offset):
    offset = offset % len(group_items)
    return group_items[offset:] + group_items[:offset]


def build_sequence(blocks, filename, groups, sequence_index):
    validate_arrangement(blocks, filename)

    cycles = {key: itertools.cycle(rotate_group(value, sequence_index)) for key, value in groups.items()}

    mid = MidiFile(ticks_per_beat=PPQ)
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(MetaMessage("track_name", name=filename, time=0))
    track.append(MetaMessage("set_tempo", tempo=mido.bpm2tempo(120), time=0))
    track.append(MetaMessage("time_signature", numerator=4, denominator=4, time=0))

    for section_type, transition in blocks:
        add_block(track, section_type, transition, cycles)

    track.append(MetaMessage("end_of_track", time=0))
    mid.save(os.path.join(OUTPUT_DIR, filename))


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    notes = [{**note, "midi": note_to_midi(note["file_note"])} for note in NOTES_DATA]
    groups = {
        "intro": group(notes, "Intro"),
        "verse": group(notes, "Verse"),
        "fill": group(notes, "Fill"),
        "chorus": group(notes, "Chorus"),
        "break": group(notes, "Break"),
        "special": group(notes, "Special"),
        "ending": group(notes, "Ending"),
    }

    print("Generating Beatmaker 3 sequences (64 bars)...\n")

    for index, arrangement in enumerate(ARRANGEMENTS, start=1):
        filename = f"{index:02d}_sequence.mid"
        build_sequence(arrangement, filename, groups, index - 1)
        print(f"Created {filename}")

    print("\nDone.")


if __name__ == "__main__":
    main()
