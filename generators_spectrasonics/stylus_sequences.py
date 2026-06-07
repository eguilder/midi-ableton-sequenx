import os
import random
import re

import mido
from mido import Message, MetaMessage, MidiFile, MidiTrack


OUTPUT_DIR = "sequences_stylus"
SEQUENCE_COUNT = 8
NOTES_PER_SEQUENCE = 8
PPQ = 480
TICKS_PER_BAR = PPQ * 4
NOTE_LENGTH_BARS = 4
NOTE_LENGTH_TICKS = NOTE_LENGTH_BARS * TICKS_PER_BAR
BPM = 120

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_to_midi(note):
    match = re.match(r"^([A-G]#?)(-?\d+)$", note)
    if not match:
        raise ValueError(f"Invalid note format: {note}")

    note_name, octave = match.groups()
    return (int(octave) + 2) * 12 + NOTE_NAMES.index(note_name)


def midi_to_note(midi):
    octave = (midi // 12) - 2
    note_index = midi % 12
    return f"{NOTE_NAMES[note_index]}{octave}"


def build_range(start_note, end_note):
    start_midi = note_to_midi(start_note)
    end_midi = note_to_midi(end_note)
    return list(range(start_midi, end_midi + 1))


def create_midi(track_name):
    mid = MidiFile(ticks_per_beat=PPQ)
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(MetaMessage("track_name", name=track_name, time=0))
    track.append(MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
    track.append(MetaMessage(
        "time_signature",
        numerator=4,
        denominator=4,
        clocks_per_click=24,
        notated_32nd_notes_per_beat=8,
        time=0,
    ))

    return mid, track


def add_note(track, note):
    track.append(Message("note_on", note=note, velocity=64, time=0))
    track.append(Message("note_off", note=note, velocity=64, time=NOTE_LENGTH_TICKS))


def build_sequence(first_note, note_range):
    candidates = [note for note in note_range if note != first_note]
    remaining_count = NOTES_PER_SEQUENCE - 1

    if len(candidates) < remaining_count:
        raise ValueError("Note range is too small to build a sequence without repeats")

    remaining_notes = random.sample(candidates, k=remaining_count)
    return [first_note, *remaining_notes]


def save_sequence(sequence_name, file_number, notes):
    mid, track = create_midi(sequence_name)

    for note in notes:
        add_note(track, note)

    track.append(MetaMessage("end_of_track", time=0))

    safe_name = sequence_name.replace(" ", "_")
    filename = f"{file_number:02d} {safe_name}.mid"
    mid.save(os.path.join(OUTPUT_DIR, filename))

    return filename


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    normal_range = build_range("C3", "G4")
    extended_range = build_range("C1", "B2")

    sequence_sets = [
        {
            "label": "Normal Sequence",
            "first_note": note_to_midi("C3"),
            "note_range": normal_range,
            "file_offset": 0,
        },
        {
            "label": "Extended Sequence",
            "first_note": note_to_midi("C1"),
            "note_range": extended_range,
            "file_offset": SEQUENCE_COUNT,
        },
    ]

    print("=" * 70)
    print("STYLUS SEQUENCE GENERATOR")
    print("=" * 70)
    print(f"Output folder: {OUTPUT_DIR}")
    print(f"Sequences per range: {SEQUENCE_COUNT}")
    print(f"Notes per sequence: {NOTES_PER_SEQUENCE}")
    print(f"Note length: {NOTE_LENGTH_BARS} bars")
    print("- Normal range: C3-G4, first note C3")
    print("- Extended range: C1-B2, first note C1")
    print()

    for sequence_set in sequence_sets:
        for index in range(1, SEQUENCE_COUNT + 1):
            sequence_name = f"{sequence_set['label']} {index}"
            file_number = sequence_set["file_offset"] + index
            notes = build_sequence(sequence_set["first_note"], sequence_set["note_range"])
            filename = save_sequence(sequence_name, file_number, notes)
            note_names = [midi_to_note(note) for note in notes]

            print(f"Created: {filename}")
            print(f"  Track name: {sequence_name}")
            print(f"  Notes: {', '.join(note_names)}")

    print()
    print(f"SUCCESS! Created {SEQUENCE_COUNT * len(sequence_sets)} MIDI files.")


if __name__ == "__main__":
    main()
