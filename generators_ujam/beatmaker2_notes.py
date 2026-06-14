import os
import re

import mido
from mido import Message, MetaMessage, MidiFile, MidiTrack


OUTPUT_DIR = "notes_beatmaker2"
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


def parse_note(note):
    match = re.match(r"^([A-G]#?)(-?\d+)$", note)
    if not match:
        raise ValueError(f"Invalid note: {note}")

    name, octave = match.groups()
    return name, int(octave)


def note_to_midi(note):
    name, octave = parse_note(note)
    return (octave + 2) * 12 + NOTE_NAMES.index(name)


def safe_filename(track_name):
    return track_name.replace(" ", "_")


def note_length_bars(track_name):
    if track_name.startswith(("Fill", "Ending")):
        return 2
    if track_name.startswith("Stop"):
        return 1
    return 4


def build_note_file(note_info, file_number):
    midi_note = note_info["midi"]
    track_name = note_info["track_name"]
    length_bars = note_length_bars(track_name)

    mid = MidiFile(ticks_per_beat=PPQ)
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(MetaMessage("track_name", name=track_name, time=0))
    track.append(MetaMessage("set_tempo", tempo=mido.bpm2tempo(120), time=0))
    track.append(
        MetaMessage(
            "time_signature",
            numerator=4,
            denominator=4,
            clocks_per_click=24,
            notated_32nd_notes_per_beat=8,
            time=0,
        )
    )
    track.append(Message("note_on", note=midi_note, velocity=64, time=0))
    track.append(Message("note_off", note=midi_note, velocity=64, time=TICKS_PER_BAR * length_bars))
    track.append(MetaMessage("end_of_track", time=0))

    filename = f"{file_number:02d} {safe_filename(track_name)}.mid"
    mid.save(os.path.join(OUTPUT_DIR, filename))
    return filename


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    notes = [{**note, "midi": note_to_midi(note["file_note"])} for note in NOTES_DATA]
    notes.sort(key=lambda note: note["midi"])

    print("=" * 70)
    print("BEATMAKER 2 NOTE GENERATOR")
    print("=" * 70)
    print(f"Generating {len(notes)} notes in '{OUTPUT_DIR}' folder")
    print()

    for file_number, note_info in enumerate(notes, start=1):
        filename = build_note_file(note_info, file_number)
        print(f"Created: {filename}")
        print(f"  Track name in Ableton: '{note_info['track_name']}'")
        print(f"  Note: {note_info['file_note']}")
        print(f"  MIDI note: {note_info['midi']}")
        print(f"  Length: {note_length_bars(note_info['track_name'])} bars")
        print()

    print("=" * 70)
    print(f"SUCCESS! Created {len(notes)} MIDI files.")
    print("IMPORT INTO ABLETON:")
    print(f"1. Go to the '{OUTPUT_DIR}' folder")
    print("2. Drag and drop MIDI files into Ableton")
    print("3. Files are numbered by pitch from C3 through B4")
    print("4. Main sections are 4 bars, fills/endings are 2 bars, and stop is 1 bar")


if __name__ == "__main__":
    main()
