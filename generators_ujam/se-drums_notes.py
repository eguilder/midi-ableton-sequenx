import os

import mido
from mido import Message, MetaMessage, MidiFile, MidiTrack


OUTPUT_DIR = "notes_se-drums"
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

special_common_notes = {
    "C#2": "Hits 1",
    "D#2": "Hits 2",
    "F#2": "Metals 1",
    "G#2": "Metals 2",
    "A#2": "Metals 3",
}

for index, note in enumerate(note_range("C2", "B2"), start=1):
    if note in special_common_notes:
        label = special_common_notes[note]
        notes_data.append({"file_note": note, "track_name": f"{label} {note}"})
    else:
        notes_data.append({"file_note": note, "track_name": f"Common Phrase {index} {note}"})

special_style_notes = {
    "C#3": "Intro 1",
    "D#3": "Intro 2",
    "F#3": "Fill 1",
    "G#3": "Fill 2",
    "A#3": "Fill 3",
    "C#4": "Ending 1",
    "D#4": "Ending 2",
}

style_index = 1
for note in note_range("C3", "D#4"):
    if note in special_style_notes:
        label = special_style_notes[note]
        notes_data.append({"file_note": note, "track_name": f"{label} {note}"})
    else:
        notes_data.append({"file_note": note, "track_name": f"Style Phrase {style_index} {note}"})
        style_index += 1

notes_data.append({"file_note": "E4", "track_name": "Stop E4"})


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
    print("SE-DRUMS NOTE GENERATOR WITH TRACK-NAME FILENAMES")
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
    print("SE-DRUMS PATTERN ORGANIZATION:")
    print("Common Phrases: C2 through B2")
    print("Hits: C#2 and D#2")
    print("Metals: F#2, G#2, and A#2")
    print("Style Phrases: C3 through D4, excluding intro/fill/ending trigger notes")
    print("Intros: C#3 and D#3")
    print("Fills: F#3, G#3, and A#3")
    print("Endings: C#4 and D#4")
    print("Stop: E4")


if __name__ == "__main__":
    main()
