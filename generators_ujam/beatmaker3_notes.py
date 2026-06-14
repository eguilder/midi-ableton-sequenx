import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage
import os
import re

# Create output directory
output_dir = "notes_beatmaker3"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# List of notes with their custom track names
notes_data = [
    {"file_note": "C#1", "track_name": "Intro C#1"},
    {"file_note": "D#1", "track_name": "Fill D#1"},
    {"file_note": "F#1", "track_name": "Verse 1 F#1"},
    {"file_note": "G#1", "track_name": "Verse 2 G#1"},
    {"file_note": "A#1", "track_name": "Fill A#1"},
    {"file_note": "C#2", "track_name": "Chorus 1 C#2"},
    {"file_note": "D#2", "track_name": "Chorus 2 D#2"},
    {"file_note": "F#2", "track_name": "Break F#2"},
    {"file_note": "G#2", "track_name": "Special G#2"},
    {"file_note": "A#2", "track_name": "Ending A#2"}
]

print("=" * 70)
print("BEATMAKER NOTE GENERATOR WITH TRACK-NAME FILENAMES")
print("=" * 70)
print(f"Generating {len(notes_data)} notes in '{output_dir}' folder")
print("✓ Filenames match Ableton MIDI clip names")
print("✓ Files numbered sequentially from lowest to highest note")
print()

# Note mapping for Ableton
# In Ableton: C-2 = MIDI 0, C-1 = MIDI 12, C0 = MIDI 24, C1 = MIDI 36, etc.
note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

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
    note_name = note_info["note_name"]
    octave = note_info["octave"]
    note_index = note_info["note_index"]
    
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
    
    # Add note (8 bars at 120 BPM = 3840 ticks)
    track.append(Message('note_on', note=ableton_midi, velocity=64, time=0))
    track.append(Message('note_off', note=ableton_midi, velocity=64, time=3840))
    
    # Add end of track
    track.append(MetaMessage('end_of_track', time=0))
    
    # Save file with sequential number and track name (matching Ableton clip name)
    safe_filename = track_name.replace(" ", "_")  # Replace spaces with underscores
    filename = f"{file_number:02d} {safe_filename}.mid"
    mid.save(filename)
    
    print(f"✓ Created: {filename}")
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
print("Filename                   | Ableton Track Name       | MIDI | Pitch")
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
    
    # Create filename for display
    safe_filename = track_name.replace(" ", "_")
    display_filename = f"{i:02d} {safe_filename}.mid"
    
    print(f"{display_filename:25} | {track_name:24} | {ableton_midi:4} | {standard_name}")

print()
print("SEQUENTIAL ORDER (by pitch, low to high):")
print("1. Intro C#1  - Start section (lowest pitch)")
print("2. Fill D#1   - Transition fill")
print("3. Verse 1 F#1 - First verse section")
print("4. Verse 2 G#1 - Second verse section")
print("5. Fill A#1   - Additional fill")
print("6. Chorus 1 C#2 - First chorus section")
print("7. Chorus 2 D#2 - Second chorus section")
print("8. Break F#2  - Breakdown section")
print("9. Special G#2 - Special/unique section")
print("10. Ending A#2 - Final section (highest pitch)")
print()
print("IMPORT INTO ABLETON:")
print("1. Go to the 'notes_beatmaker3' folder")
print("2. Drag and drop MIDI files into Ableton")
print("3. Tracks will be named with section names (e.g., 'Intro C#1')")
print("4. Filenames match track names (with underscores instead of spaces)")
print("5. Files are numbered 01-10 by pitch for easy organization")
print()
print("SECTION ORGANIZATION:")
print("• Intro: 01 Intro_C#1")
print("• Fills: 02 Fill_D#1, 05 Fill_A#1")
print("• Verses: 03 Verse_1_F#1, 04 Verse_2_G#1")
print("• Choruses: 06 Chorus_1_C#2, 07 Chorus_2_D#2")
print("• Break: 08 Break_F#2")
print("• Special: 09 Special_G#2")
print("• Ending: 10 Ending_A#2")
print()
print("PRODUCTION WORKFLOW:")
print("1. Use Intro for track beginnings")
print("2. Use Fills for transitions between sections")
print("3. Verses for main rhythmic patterns")
print("4. Choruses for more intense sections")
print("5. Break for breakdowns or drops")
print("6. Special for unique elements or variations")
print("7. Ending for track conclusions")
