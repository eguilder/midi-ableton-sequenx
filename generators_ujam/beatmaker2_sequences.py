import itertools
import os
import re

import mido
from mido import Message, MetaMessage, MidiFile, MidiTrack


OUTPUT_DIR = "sequences_beatmaker2"
PPQ = 480
TICKS_PER_BAR = PPQ * 4

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

NOTES_DATA = [
    {"file_note": "C3", "track_name": "Verse 1 C3"},
    {"file_note": "C#3", "track_name": "Intro 1 C#3"},
    {"file_note": "D3", "track_name": "Verse 2 D3"},
    {"file_note": "D#3", "track_name": "Intro 2 D#3"},
    {"file_note": "E3", "track_name": "Verse 3 E3"},
    {"file_note": "F3", "track_name": "Verse 4 F3"},
    {"file_note": "F#3", "track_name": "Fill 1 F#3"},
    {"file_note": "G3", "track_name": "Verse 5 G3"},
    {"file_note": "G#3", "track_name": "Fill 2 G#3"},
    {"file_note": "A3", "track_name": "Chorus 1 A3"},
    {"file_note": "A#3", "track_name": "Fill 3 A#3"},
    {"file_note": "B3", "track_name": "Chorus 2 B3"},
    {"file_note": "C4", "track_name": "Chorus 3 C4"},
    {"file_note": "C#4", "track_name": "Ending 1 C#4"},
    {"file_note": "D4", "track_name": "Chorus 4 D4"},
    {"file_note": "D#4", "track_name": "Ending 2 D#4"},
    {"file_note": "E4", "track_name": "Chorus 5 E4"},
    {"file_note": "F4", "track_name": "Special 1 F4"},
    {"file_note": "F#4", "track_name": "Breakdown 1 F#4"},
    {"file_note": "G4", "track_name": "Special 2 G4"},
    {"file_note": "G#4", "track_name": "Breakdown 2 G#4"},
    {"file_note": "A4", "track_name": "Special 3 A4"},
    {"file_note": "A#4", "track_name": "Breakdown 3 A#4"},
    {"file_note": "B4", "track_name": "Stop B4"},
]

BODY_SECTIONS = {"verse", "chorus", "special"}
MAIN_SECTIONS = {"verse", "chorus"}
TRANSITIONS = {"fill", "breakdown", "ending"}

# Each tuple is one 4-bar block: (section, optional_bar_4_transition).
# The intro block is 2 bars intro + 2 bars of the named body section.
ARRANGEMENTS = [
    [
        ("intro", "verse"),
        ("verse", "fill"),
        ("chorus", "breakdown"),
        ("verse", None),
        ("chorus", "fill"),
        ("verse", "breakdown"),
        ("chorus", None),
        ("verse", "fill"),
        ("chorus", "fill"),
        ("special", None),
        ("verse", "fill"),
        ("special", None),
        ("chorus", "fill"),
        ("special", None),
        ("chorus", None),
        ("chorus", "ending"),
    ],
    [
        ("intro", "chorus"),
        ("verse", "breakdown"),
        ("chorus", "fill"),
        ("verse", None),
        ("chorus", "breakdown"),
        ("verse", "fill"),
        ("chorus", None),
        ("verse", "breakdown"),
        ("chorus", None),
        ("special", None),
        ("chorus", "fill"),
        ("special", None),
        ("verse", None),
        ("chorus", "breakdown"),
        ("verse", None),
        ("chorus", "ending"),
    ],
    [
        ("intro", "verse"),
        ("verse", None),
        ("verse", "fill"),
        ("chorus", "breakdown"),
        ("chorus", None),
        ("verse", "breakdown"),
        ("chorus", "fill"),
        ("verse", None),
        ("chorus", "fill"),
        ("special", None),
        ("verse", None),
        ("special", None),
        ("chorus", None),
        ("special", None),
        ("verse", "fill"),
        ("chorus", "ending"),
    ],
    [
        ("intro", "verse"),
        ("verse", "fill"),
        ("verse", "fill"),
        ("chorus", None),
        ("chorus", "breakdown"),
        ("verse", None),
        ("chorus", "fill"),
        ("verse", "breakdown"),
        ("chorus", None),
        ("special", None),
        ("verse", "fill"),
        ("special", None),
        ("chorus", None),
        ("verse", "fill"),
        ("chorus", None),
        ("verse", "ending"),
    ],
    [
        ("intro", "verse"),
        ("verse", "fill"),
        ("verse", "breakdown"),
        ("chorus", None),
        ("chorus", "fill"),
        ("verse", "breakdown"),
        ("chorus", None),
        ("verse", None),
        ("chorus", "fill"),
        ("special", None),
        ("verse", "breakdown"),
        ("verse", None),
        ("chorus", "breakdown"),
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
    if first_section != "intro" or first_body not in MAIN_SECTIONS:
        raise ValueError(f"{filename} must start with 2 bars intro plus Verse or Chorus")

    for block_index, (section_type, _) in enumerate(blocks[:8], start=1):
        if section_type == "special" or (section_type == "intro" and blocks[0][1] == "special"):
            raise ValueError(f"{filename} block {block_index} uses Special before the last half")

    for block_index, (section_type, transition) in enumerate(blocks[1:], start=1):
        if section_type not in BODY_SECTIONS:
            raise ValueError(f"{filename} block {block_index + 1} must use Verse, Chorus, or Special")
        if transition is not None and transition not in TRANSITIONS:
            raise ValueError(f"{filename} block {block_index + 1} has invalid transition {transition}")

    for block_index, (section_type, transition) in enumerate(blocks[:-1]):
        if transition == "ending":
            raise ValueError(f"{filename} may only use Ending in the final block")
        if transition == "breakdown":
            next_section = blocks[block_index + 1][0]
            if next_section not in MAIN_SECTIONS:
                raise ValueError(f"{filename} has a Breakdown before {next_section}")

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
        "ending": group(notes, "Ending"),
        "special": group(notes, "Special"),
        "breakdown": group(notes, "Breakdown"),
    }

    print("Generating Beatmaker 2 sequences (64 bars)...\n")

    for index, arrangement in enumerate(ARRANGEMENTS, start=1):
        filename = f"{index:02d}_sequence.mid"
        build_sequence(arrangement, filename, groups, index - 1)
        print(f"Created {filename}")

    print("\nDone.")


if __name__ == "__main__":
    main()
