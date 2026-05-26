import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage
import os

# Create output directory
output_dir = "notes_instachord"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Note mapping for Ableton
# In Ableton: C-2 = MIDI 0, C-1 = MIDI 12, C0 = MIDI 24, C1 = MIDI 36, etc.
note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

grid = [
    (1, "Chords A"),
    (2, "Chords B"),
    (3, "Picks A"),
    (4, "Picks B"),
]

notes_data = []
for octave, phrase_group in grid:
    for index, note_name in enumerate(note_names, start=1):
        file_note = f"{note_name}{octave}"
        notes_data.append({
            "file_note": file_note,
            "track_name": f"{phrase_group} {index} {file_note}",
        })

print("=" * 70)
print("INSTACHORD NOTE GENERATOR WITH TRACK-NAME FILENAMES")
print("=" * 70)
print(f"Generating {len(notes_data)} notes in '{output_dir}' folder")
print("Files numbered sequentially from lowest to highest note")
print("Range: C1 through B4 in Ableton notation")
print()

# First, calculate MIDI numbers for all notes and sort them
notes_with_midi = []
for note_info in notes_data:
    file_note = note_info["file_note"]
    track_name = note_info["track_name"]

    # Parse the note name and octave
    note_name = file_note[:-1]  # Remove last character (octave)
    octave = int(file_note[-1])  # Get octave number

    # Find the index of the note
    note_index = note_names.index(note_name)

    # Calculate MIDI number for Ableton
    # Formula: MIDI = (octave + 2) * 12 + note_index
    ableton_midi = (octave + 2) * 12 + note_index

    notes_with_midi.append({
        "file_note": file_note,
        "track_name": track_name,
        "midi": ableton_midi,
        "note_name": note_name,
        "octave": octave,
        "note_index": note_index
    })

# Sort by MIDI number (lowest to highest pitch)
notes_with_midi.sort(key=lambda x: x["midi"])

# Change to output directory
original_dir = os.getcwd()
os.chdir(output_dir)

# Generate each note with sequential numbering
for file_number, note_info in enumerate(notes_with_midi, start=1):
    file_note = note_info["file_note"]
    track_name = note_info["track_name"]
    ableton_midi = note_info["midi"]

    # Calculate what this is in standard notation (for reference)
    standard_octave = (ableton_midi // 12) - 1  # Standard: C-1 = MIDI 0, C0 = MIDI 12
    standard_note_index = ableton_midi % 12
    standard_name = f"{note_names[standard_note_index]}{standard_octave}"

    # Calculate frequency
    frequency = 440.0 * (2.0 ** ((ableton_midi - 69) / 12.0))

    # Create MIDI file
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    # Set track name (this is what Ableton will display)
    track.append(MetaMessage('track_name', name=track_name, time=0))

    # Set tempo (120 BPM)
    tempo = mido.bpm2tempo(120)
    track.append(MetaMessage('set_tempo', tempo=tempo, time=0))

    # Set time signature (4/4)
    track.append(MetaMessage('time_signature', numerator=4, denominator=4,
                             clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))

    # Add note (4 bars at 120 BPM = 1920 ticks)
    track.append(Message('note_on', note=ableton_midi, velocity=64, time=0))
    track.append(Message('note_off', note=ableton_midi, velocity=64, time=1920))

    # Add end of track
    track.append(MetaMessage('end_of_track', time=0))

    # Save file with sequential number and track name (matching Ableton clip name)
    safe_filename = track_name.replace(" ", "_")  # Replace spaces with underscores
    filename = f"{file_number:02d} {safe_filename}.mid"
    mid.save(filename)

    print(f"Created: {filename}")
    print(f"  Track name in Ableton: '{track_name}'")
    print(f"  Note: {file_note}")
    print(f"  MIDI note: {ableton_midi}")
    print(f"  Plays at: {standard_name} pitch (standard notation)")
    print(f"  Frequency: {frequency:.2f} Hz")
    print()

# Change back to original directory
os.chdir(original_dir)

print("=" * 70)
print(f"SUCCESS! Created {len(notes_data)} MIDI files.")
print()
print("FILES CREATED (sequentially numbered with track names):")
print("-" * 70)
print("Filename             | Ableton Track Name | MIDI | Pitch      | Frequency")
print("-" * 70)

# Display in the order they were created (sorted by pitch)
for i, note_info in enumerate(notes_with_midi, start=1):
    file_note = note_info["file_note"]
    track_name = note_info["track_name"]
    ableton_midi = note_info["midi"]

    # Calculate standard pitch
    standard_octave = (ableton_midi // 12) - 1
    standard_note_index = ableton_midi % 12
    standard_name = f"{note_names[standard_note_index]}{standard_octave}"

    # Calculate frequency
    frequency = 440.0 * (2.0 ** ((ableton_midi - 69) / 12.0))

    # Create filename for display
    safe_filename = track_name.replace(" ", "_")
    display_filename = f"{i:02d} {safe_filename}.mid"

    print(f"{display_filename:30} | {track_name:20} | {ableton_midi:4} | {standard_name:10} | {frequency:6.2f} Hz")
