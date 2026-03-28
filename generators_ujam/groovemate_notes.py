import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage
import os
import re

# Create output directory
output_dir = "notes_groovemate"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

notes_data = [
    # One shots

    # Quinto
    {"file_note": "C1", "track_name": "Quinto Open C1"},
    {"file_note": "C#1", "track_name": "Quinto Heel C#1"},
    {"file_note": "D1", "track_name": "Quinto Muted D1"},
    {"file_note": "D#1", "track_name": "Quinto Finger D#1"},
    {"file_note": "E1", "track_name": "Quinto Slap E1"},

    # Conga
    {"file_note": "F1", "track_name": "Conga Open F1"},
    {"file_note": "G1", "track_name": "Conga Bass G1"},
    {"file_note": "A1", "track_name": "Conga Bass Muted A1"},

    # Maracas
    {"file_note": "F#1", "track_name": "Maracas Forth F#1"},
    {"file_note": "G#1", "track_name": "Maracas Back G#1"},

    # Clave
    {"file_note": "A#1", "track_name": "Clave A#1"},

    # Tumba
    {"file_note": "B1", "track_name": "Tumba Open B1"},
    {"file_note": "C2", "track_name": "Tumba Bass C2"},
    {"file_note": "D2", "track_name": "Tumba Bass Muted D2"},

    # Cabasa
    {"file_note": "C#2", "track_name": "Cabasa Left C#2"},
    {"file_note": "D#2", "track_name": "Cabasa Right D#2"},

    # Cowbell
    {"file_note": "E2", "track_name": "Cowbell Edge E2"},
    {"file_note": "F2", "track_name": "Cowbell Tip F2"},
    {"file_note": "G2", "track_name": "Cowbell Damped G2"},

    # Tambourine
    {"file_note": "F#2", "track_name": "Tambourine Forth-Back F#2"},
    {"file_note": "G#2", "track_name": "Tambourine Accent G#2"},
    {"file_note": "A#2", "track_name": "Tambourine Shake A#2"},

    # Claps
    {"file_note": "A2", "track_name": "Claps A2"},

    # Style Patterns

    # Verses
    {"file_note": "C3", "track_name": "Verse 1 C3"},
    {"file_note": "D3", "track_name": "Verse 2 D3"},
    {"file_note": "E3", "track_name": "Verse 3 E3"},
    {"file_note": "F3", "track_name": "Verse 4 F3"},
    {"file_note": "G3", "track_name": "Verse 5 G3"},

    # Intros
    {"file_note": "C#3", "track_name": "Intro 1 C#3"},
    {"file_note": "D#3", "track_name": "Intro 2 D#3"},

    # Fills
    {"file_note": "F#3", "track_name": "Fill 1 F#3"},
    {"file_note": "G#3", "track_name": "Fill 2 G#3"},
    {"file_note": "A#3", "track_name": "Fill 3 A#3"},

    # Choruses
    {"file_note": "A3", "track_name": "Chorus 1 A3"},
    {"file_note": "B3", "track_name": "Chorus 2 B3"},
    {"file_note": "C4", "track_name": "Chorus 3 C4"},
    {"file_note": "D4", "track_name": "Chorus 4 D4"},
    {"file_note": "E4", "track_name": "Chorus 5 E4"},

    # Endings
    {"file_note": "C#4", "track_name": "Ending 1 C#4"},
    {"file_note": "D#4", "track_name": "Ending 2 D#4"},

    # Specials
    {"file_note": "F4", "track_name": "Special 1 F4"},
    {"file_note": "G4", "track_name": "Special 2 G4"},
    {"file_note": "A4", "track_name": "Special 3 A4"},

    # Breakdowns
    {"file_note": "F#4", "track_name": "Breakdown 1 F#4"},
    {"file_note": "G#4", "track_name": "Breakdown 2 G#4"},
    {"file_note": "A#4", "track_name": "Breakdown 3 A#4"},

    # Stop
    {"file_note": "B4", "track_name": "Stop B4"},
]

print("=" * 70)
print("GROOVEMATE NOTE GENERATOR")
print("=" * 70)

note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

notes_with_midi = []

for note_info in notes_data:
    file_note = note_info["file_note"]
    track_name = note_info["track_name"]

    match = re.match(r"^([A-G]#?)(-?\d+)$", file_note)
    if not match:
        raise ValueError(f"Invalid note format: {file_note}")

    note_name, octave = match.groups()
    octave = int(octave)

    note_index = note_names.index(note_name)
    ableton_midi = (octave + 2) * 12 + note_index

    notes_with_midi.append({
        "file_note": file_note,
        "track_name": track_name,
        "midi": ableton_midi
    })

notes_with_midi.sort(key=lambda x: x["midi"])

original_dir = os.getcwd()
os.chdir(output_dir)

for i, note_info in enumerate(notes_with_midi, start=1):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(MetaMessage('track_name', name=note_info["track_name"], time=0))
    track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(120), time=0))
    track.append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))

    track.append(Message('note_on', note=note_info["midi"], velocity=64, time=0))
    track.append(Message('note_off', note=note_info["midi"], velocity=64, time=1920))

    track.append(MetaMessage('end_of_track', time=0))

    filename = f"{i:02d} {note_info['track_name'].replace(' ', '_')}.mid"
    mid.save(filename)

    print(f"✓ {filename}")

os.chdir(original_dir)

print("=" * 70)
print("DONE")