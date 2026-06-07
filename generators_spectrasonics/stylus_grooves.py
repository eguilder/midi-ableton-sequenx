import os
import re

import mido
from mido import Message, MetaMessage, MidiFile, MidiTrack


PPQ = 480
TICKS_PER_BAR = PPQ * 4

output_sets = [
    {"name": "Grooves", "output_dir": "grooves_stylus", "bars": 4},
    {"name": "Hits", "output_dir": "hits_stylus", "bars": 2},
]


note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_to_midi(note):
    match = re.match(r"^([A-G]#?)(-?\d+)$", note)
    if not match:
        raise ValueError(f"Invalid note format: {note}")

    note_name, octave = match.groups()
    octave = int(octave)
    note_index = note_names.index(note_name)

    # Ableton MIDI formula: C-2 = 0
    return (octave + 2) * 12 + note_index


def midi_to_note(midi):
    octave = (midi // 12) - 2
    note_index = midi % 12
    return f"{note_names[note_index]}{octave}"


def build_notes_data(start_note, end_note):
    start_midi = note_to_midi(start_note)
    end_midi = note_to_midi(end_note)

    notes_data = []
    for midi in range(start_midi, end_midi + 1):
        file_note = midi_to_note(midi)
        range_label = "Extended Range" if midi <= note_to_midi("B2") else "Normal Range"

        notes_data.append({
            "file_note": file_note,
            "track_name": f"{range_label} {file_note}",
            "midi": midi,
        })

    return notes_data


notes_data = build_notes_data("C1", "A5")


print("=" * 70)
print("STYLUS NOTE GENERATOR WITH TRACK-NAME FILENAMES")
print("=" * 70)
print(f"Generating {len(notes_data)} notes in each output folder")
print("- Filenames match Ableton MIDI clip names")
print("- Files numbered sequentially from lowest to highest note")
print("- Range: C1 through A5 in Ableton notation")
print("- Labels: C1-B2 Extended Range, C3-A5 Normal Range")
for output_set in output_sets:
    print(f"- {output_set['name']}: {output_set['output_dir']} ({output_set['bars']} bars)")
print()


original_dir = os.getcwd()


for output_set in output_sets:
    output_dir = output_set["output_dir"]
    note_length = output_set["bars"] * TICKS_PER_BAR

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    os.chdir(output_dir)

    for file_number, note_info in enumerate(notes_data, start=1):
        file_note = note_info["file_note"]
        track_name = note_info["track_name"]
        ableton_midi = note_info["midi"]

        standard_octave = (ableton_midi // 12) - 1
        standard_note_index = ableton_midi % 12
        standard_name = f"{note_names[standard_note_index]}{standard_octave}"

        frequency = 440.0 * (2.0 ** ((ableton_midi - 69) / 12.0))

        mid = MidiFile(ticks_per_beat=PPQ)
        track = MidiTrack()
        mid.tracks.append(track)

        track.append(MetaMessage("track_name", name=track_name, time=0))
        track.append(MetaMessage("set_tempo", tempo=mido.bpm2tempo(120), time=0))
        track.append(MetaMessage(
            "time_signature",
            numerator=4,
            denominator=4,
            clocks_per_click=24,
            notated_32nd_notes_per_beat=8,
            time=0,
        ))

        track.append(Message("note_on", note=ableton_midi, velocity=64, time=0))
        track.append(Message("note_off", note=ableton_midi, velocity=64, time=note_length))
        track.append(MetaMessage("end_of_track", time=0))

        safe_filename = track_name.replace(" ", "_")
        filename = f"{file_number:02d} {safe_filename}.mid"
        mid.save(filename)

        print(f"Created: {output_dir}/{filename}")
        print(f"  Note: {file_note}")
        print(f"  MIDI: {ableton_midi}")
        print(f"  Pitch: {standard_name}")
        print(f"  Bars: {output_set['bars']}")
        print(f"  Frequency: {frequency:.2f} Hz\n")

    os.chdir(original_dir)


print("=" * 70)
print(f"SUCCESS! Created {len(notes_data) * len(output_sets)} MIDI files.")
print()
print("FILES CREATED (sequentially numbered with track names):")
print("-" * 70)
print("Filename             | Ableton Track Name      | MIDI | Pitch      | Frequency")
print("-" * 70)


for i, note_info in enumerate(notes_data, start=1):
    track_name = note_info["track_name"]
    ableton_midi = note_info["midi"]

    standard_octave = (ableton_midi // 12) - 1
    standard_note_index = ableton_midi % 12
    standard_name = f"{note_names[standard_note_index]}{standard_octave}"
    frequency = 440.0 * (2.0 ** ((ableton_midi - 69) / 12.0))

    safe_filename = track_name.replace(" ", "_")
    display_filename = f"{i:02d} {safe_filename}.mid"

    print(f"{display_filename:20} | {track_name:23} | {ableton_midi:4} | {standard_name:10} | {frequency:6.2f} Hz")
