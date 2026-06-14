import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage
import os
import re

# Create output directory
output_dir = "notes_v-bassist"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

PPQ = 480
TICKS_PER_BAR = PPQ * 4
NOTE_LENGTH_BARS = 2

# List of notes with their custom track names
notes_data = [
    # C0 - Silence
    {"file_note": "C0", "track_name": "Silence C0"},
    
    # C#0 through B1 - Phrases (with exceptions)
    {"file_note": "C#0", "track_name": "Phrase 1 C#0"},
    {"file_note": "D0", "track_name": "Phrase 2 D0"},
    {"file_note": "D#0", "track_name": "Phrase 3 D#0"},
    {"file_note": "E0", "track_name": "Phrase 4 E0"},
    {"file_note": "F0", "track_name": "Phrase 5 F0"},
    {"file_note": "F#0", "track_name": "Phrase 6 F#0"},
    {"file_note": "G0", "track_name": "Phrase 7 G0"},
    {"file_note": "G#0", "track_name": "Phrase 8 G#0"},
    {"file_note": "A0", "track_name": "Phrase 9 A0"},
    {"file_note": "A#0", "track_name": "Phrase 10 A#0"},
    {"file_note": "B0", "track_name": "Phrase 11 B0"},
    
    # C1 through B1 - Continuing Phrases (with exceptions)
    {"file_note": "C1", "track_name": "Phrase 12 C1"},
    {"file_note": "C#1", "track_name": "Intro 1 C#1"},  # Exception
    {"file_note": "D1", "track_name": "Phrase 13 D1"},
    {"file_note": "D#1", "track_name": "Intro 2 D#1"},  # Exception
    {"file_note": "E1", "track_name": "Phrase 14 E1"},
    {"file_note": "F1", "track_name": "Phrase 15 F1"},
    {"file_note": "F#1", "track_name": "Fill 1 F#1"},   # Exception
    {"file_note": "G1", "track_name": "Phrase 16 G1"},
    {"file_note": "G#1", "track_name": "Fill 2 G#1"},   # Exception
    {"file_note": "A1", "track_name": "Phrase 17 A1"},
    {"file_note": "A#1", "track_name": "Fill 3 A#1"},   # Exception
    {"file_note": "B1", "track_name": "Phrase 18 B1"},
    
    # C2 through A2 - Styles (with exceptions)
    {"file_note": "C2", "track_name": "Style 1 C2"},
    {"file_note": "C#2", "track_name": "Style Intro 1 C#2"},  # Exception
    {"file_note": "D2", "track_name": "Style 2 D2"},
    {"file_note": "D#2", "track_name": "Style Intro 2 D#2"},  # Exception
    {"file_note": "E2", "track_name": "Style 3 E2"},
    {"file_note": "F2", "track_name": "Style 4 F2"},
    {"file_note": "F#2", "track_name": "Style Fill 1 F#2"},   # Exception
    {"file_note": "G2", "track_name": "Style 5 G2"},
    {"file_note": "G#2", "track_name": "Style Fill 2 G#2"},   # Exception
    {"file_note": "A2", "track_name": "Style 6 A2"},
    {"file_note": "A#2", "track_name": "Style Fill 3 A#2"},   # Exception
    
    # B2 - Stop
    {"file_note": "B2", "track_name": "Stop B2"}
]

print("=" * 70)
print("V-BASSIST NOTE GENERATOR WITH TRACK-NAME FILENAMES")
print("=" * 70)
print(f"Generating {len(notes_data)} notes in '{output_dir}' folder")
print("Filenames match Ableton MIDI clip names")
print("Files numbered sequentially from lowest to highest note")
print("Range: C2 through E2 in Ableton notation")
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
    mid = MidiFile(ticks_per_beat=PPQ)
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
    
    # Add note using the V-Bassist groove length.
    track.append(Message('note_on', note=ableton_midi, velocity=64, time=0))
    track.append(Message('note_off', note=ableton_midi, velocity=64, time=TICKS_PER_BAR * NOTE_LENGTH_BARS))
    
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
    print(f"  Length: {NOTE_LENGTH_BARS} bars")
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
    
    print(f"{display_filename:20} | {track_name:18} | {ableton_midi:4} | {standard_name:10} | {frequency:6.2f} Hz")

print()
print("SEQUENTIAL ORDER (by pitch, low to high):")
print("1. Silence C0        - Silent/rest pattern (lowest pitch)")
print("2. Phrase 1 C#0      - First bass phrase pattern")
print("3. Phrase 2 D0       - Second bass phrase pattern")
print("4. Phrase 3 D#0      - Third bass phrase pattern")
print("5. Phrase 4 E0       - Fourth bass phrase pattern")
print("6. Phrase 5 F0       - Fifth bass phrase pattern")
print("7. Phrase 6 F#0      - Sixth bass phrase pattern")
print("8. Phrase 7 G0       - Seventh bass phrase pattern")
print("9. Phrase 8 G#0      - Eighth bass phrase pattern")
print("10. Phrase 9 A0      - Ninth bass phrase pattern")
print("11. Phrase 10 A#0    - Tenth bass phrase pattern")
print("12. Phrase 11 B0     - Eleventh bass phrase pattern")
print("13. Phrase 12 C1     - Twelfth bass phrase pattern")
print("14. Intro 1 C#1      - First introduction pattern")
print("15. Phrase 13 D1     - Thirteenth bass phrase pattern")
print("16. Intro 2 D#1      - Second introduction pattern")
print("17. Phrase 14 E1     - Fourteenth bass phrase pattern")
print("18. Phrase 15 F1     - Fifteenth bass phrase pattern")
print("19. Fill 1 F#1       - First bass fill pattern")
print("20. Phrase 16 G1     - Sixteenth bass phrase pattern")
print("21. Fill 2 G#1       - Second bass fill pattern")
print("22. Phrase 17 A1     - Seventeenth bass phrase pattern")
print("23. Fill 3 A#1       - Third bass fill pattern")
print("24. Phrase 18 B1     - Eighteenth bass phrase pattern")
print("25. Style 1 C2       - First bass style pattern")
print("26. Style Intro 1 C#2 - First style introduction pattern")
print("27. Style 2 D2       - Second bass style pattern")
print("28. Style Intro 2 D#2 - Second style introduction pattern")
print("29. Style 3 E2       - Third bass style pattern")
print("30. Style 4 F2       - Fourth bass style pattern")
print("31. Style Fill 1 F#2  - First style fill pattern")
print("32. Style 5 G2       - Fifth bass style pattern")
print("33. Style Fill 2 G#2  - Second style fill pattern")
print("34. Style 6 A2       - Sixth bass style pattern")
print("35. Style Fill 3 A#2  - Third style fill pattern")
print("36. Stop B2          - Stop/break pattern (highest pitch)")
print()
print("IMPORT INTO ABLETON:")
print("1. Go to the 'notes_v-bassist' folder")
print("2. Drag and drop MIDI files into Ableton")
print("3. Tracks will be named with phrase/style/fill names (e.g., 'Phrase 1 C#0')")
print("4. Filenames match track names (with underscores instead of spaces)")
print("5. Files are numbered 01-36 by pitch for easy organization")
print()
print("NOTE RANGE DETAILS:")
print("- Range: C0 to B2 in Ableton notation")
print("- Corresponds to: C0 to B2 in standard notation (same)")
print("- Frequency range: 16.35 Hz to 123.47 Hz")
print("- Perfect range for sub-bass to bass frequency content")
print()
print("V-BASSIST PATTERN ORGANIZATION:")
print("- Silence C0: Silent/rest pattern for pauses")
print("- Phrases 1-18: Progressive bass phrase patterns across multiple octaves")
print("- Intros 1-2: Introduction patterns for song openings")
print("- Fills 1-3: Bass fill patterns for transitions")
print("- Styles 1-6: Different bass playing style patterns")
print("- Style Intros 1-2: Introduction patterns for style sections")
print("- Style Fills 1-3: Fill patterns specific to style sections")
print("- Stop B2: Stop/break pattern for dramatic pauses")
print("- Organized by pitch progression across 3 octaves")
print()
print("WORKFLOW SUGGESTIONS:")
print("1. Start with Silence or Intro patterns for clean beginnings")
print("2. Use Phrases 1-12 for deep sub-bass foundations")
print("3. Progress through Phrases 13-18 for standard bass range")
print("4. Insert Fills for smooth transitions between sections")
print("5. Switch to Style patterns for different bass playing techniques")
print("6. Use Style Intros and Fills for style-specific transitions")
print("7. End with Stop pattern for dramatic conclusions")
print("8. Combine patterns across octaves for dynamic bass arrangements")
print()
print("PRODUCTION TIPS:")
print("- Phrases 1-11 (C#0-B0): Use for deep sub-bass foundations")
print("- Phrases 12-18 (C1-B1): Use for standard basslines")
print("- Intros: Perfect for song openings and section beginnings")
print("- Fills: Ideal for transitions and adding rhythmic interest")
print("- Styles: Switch between different bass playing techniques")
print("- Silence: Use for dramatic pauses and rhythmic spacing")
print("- Stop: Create hard breaks and dramatic pauses")
print("- Combine patterns across octaves for full bass frequency coverage")
