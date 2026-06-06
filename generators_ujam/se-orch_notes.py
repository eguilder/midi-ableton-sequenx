import os

import mido
from mido import Message, MetaMessage, MidiFile, MidiTrack


OUTPUT_DIR = "notes_se-orch"
PPQ = 480
BPM = 120
NOTE_DURATION_TICKS = PPQ * 4
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def ableton_note_to_midi(note):
    note_name = note[:-1]
    octave = int(note[-1])
    note_index = NOTE_NAMES.index(note_name)
    return (octave + 2) * 12 + note_index


def midi_to_standard_note(midi_note):
    octave = (midi_note // 12) - 1
    note_name = NOTE_NAMES[midi_note % 12]
    return f"{note_name}{octave}"


def note_range(start_note, end_note):
    start_midi = ableton_note_to_midi(start_note)
    end_midi = ableton_note_to_midi(end_note)
    return [
        f"{NOTE_NAMES[midi_note % 12]}{(midi_note // 12) - 2}"
        for midi_note in range(start_midi, end_midi + 1)
    ]


notes_data = []

special_phrase_notes = {
    "C#1": "Addition 1",
    "D#1": "Addition 2",
    "F#1": "Addition 3",
    "G#1": "Addition 4",
}

phrase_index = 1
for note in note_range("C1", "A1"):
    if note in special_phrase_notes:
        label = special_phrase_notes[note]
        notes_data.append({"file_note": note, "track_name": f"{label} {note}"})
    else:
        notes_data.append({"file_note": note, "track_name": f"Phrase {phrase_index} {note}"})
        phrase_index += 1

notes_data.append({"file_note": "A#1", "track_name": "End A#1"})
notes_data.append({"file_note": "B1", "track_name": "Stop B1"})

for index, note in enumerate(note_range("C2", "B2"), start=1):
    notes_data.append({"file_note": note, "track_name": f"Bass {index} {note}"})

for index, note in enumerate(note_range("C3", "B4"), start=1):
    notes_data.append({"file_note": note, "track_name": f"Play {index} {note}"})


def create_midi_file(track_name, midi_note):
    mid = MidiFile(ticks_per_beat=PPQ)
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(MetaMessage("track_name", name=track_name, time=0))
    track.append(MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
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
    track.append(Message("note_off", note=midi_note, velocity=64, time=NOTE_DURATION_TICKS))
    track.append(MetaMessage("end_of_track", time=0))

    return mid


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    notes_with_midi = [
        {
            "file_note": note_info["file_note"],
            "track_name": note_info["track_name"],
            "midi": ableton_note_to_midi(note_info["file_note"]),
        }
        for note_info in notes_data
    ]
    notes_with_midi.sort(key=lambda note_info: note_info["midi"])

    print("=" * 70)
    print("SE-ORCH NOTE GENERATOR WITH TRACK-NAME FILENAMES")
    print("=" * 70)
    print(f"Generating {len(notes_with_midi)} notes in '{OUTPUT_DIR}' folder")
    print("Files are numbered sequentially from lowest to highest note")
    print()

    for file_number, note_info in enumerate(notes_with_midi, start=1):
        track_name = note_info["track_name"]
        midi_note = note_info["midi"]
        safe_filename = track_name.replace(" ", "_")
        filename = f"{file_number:02d} {safe_filename}.mid"
        output_path = os.path.join(OUTPUT_DIR, filename)

        mid = create_midi_file(track_name, midi_note)
        mid.save(output_path)

        print(f"Created: {filename}")
        print(f"  Track name in Ableton: '{track_name}'")
        print(f"  Note: {note_info['file_note']}")
        print(f"  MIDI note: {midi_note}")
        print(f"  Plays at: {midi_to_standard_note(midi_note)} pitch (standard notation)")
        print()

    print("=" * 70)
    print(f"SUCCESS! Created {len(notes_with_midi)} MIDI files.")
    print()
    print("FILES CREATED:")
    print("-" * 70)
    print("Filename                         | Ableton Track Name     | MIDI | Pitch")
    print("-" * 70)

    for file_number, note_info in enumerate(notes_with_midi, start=1):
        safe_filename = note_info["track_name"].replace(" ", "_")
        filename = f"{file_number:02d} {safe_filename}.mid"
        print(
            f"{filename:32} | {note_info['track_name']:22} | "
            f"{note_info['midi']:4} | {midi_to_standard_note(note_info['midi'])}"
        )

    print()
    print("SE-ORCH PATTERN ORGANIZATION:")
    print("Phrases: C1 through A1, excluding addition trigger notes")
    print("Additions: C#1, D#1, F#1, and G#1")
    print("End: A#1")
    print("Stop: B1")
    print("Bass: C2 through B2")
    print("Play: C3 through B4")


if __name__ == "__main__":
    main()
