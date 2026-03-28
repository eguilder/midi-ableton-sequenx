import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage
import os
import re
import itertools

# =========================================
# CONFIG
# =========================================

OUTPUT_DIR = "sequences_groovemate"
os.makedirs(OUTPUT_DIR, exist_ok=True)

PPQ = 480
TICKS_PER_BAR = PPQ * 4

note_names = ['C', 'C#', 'D', 'D#', 'E', 'F',
              'F#', 'G', 'G#', 'A', 'A#', 'B']

# =========================================
# STYLE PATTERNS
# =========================================

notes_data = [
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

# =========================================
# NOTE → MIDI
# =========================================

def parse_note(note):
    match = re.match(r"^([A-G]#?)(-?\d+)$", note)
    if not match:
        raise ValueError(f"Invalid note: {note}")
    name, octave = match.groups()
    return name, int(octave)

def note_to_midi(note):
    name, octave = parse_note(note)
    return (octave + 2) * 12 + note_names.index(name)

notes = []
for n in notes_data:
    notes.append({**n, "midi": note_to_midi(n["file_note"])})

def group(prefix):
    return [n for n in notes if n["track_name"].startswith(prefix)]

groups = {
    "intro": group("Intro"),
    "verse": group("Verse"),
    "chorus": group("Chorus"),
    "fill": group("Fill"),
    "ending": group("Ending"),
    "special": group("Special"),
    "breakdown": group("Breakdown"),
}

# Create cycling iterators
cycles = {k: itertools.cycle(v) for k, v in groups.items()}

# =========================================
# MIDI BUILDING
# =========================================

def add_section(track, section_type, main_note, fill_note):
    # Intro = 1 bar main + 1 bar fill
    if section_type == "intro":
        track.append(Message('note_on', note=main_note, velocity=100, time=0))
        track.append(Message('note_off', note=main_note, velocity=0, time=TICKS_PER_BAR))

        track.append(Message('note_on', note=fill_note, velocity=100, time=0))
        track.append(Message('note_off', note=fill_note, velocity=0, time=TICKS_PER_BAR))
        return

    # Default = 3 bars main + 1 fill
    for _ in range(3):
        track.append(Message('note_on', note=main_note, velocity=100, time=0))
        track.append(Message('note_off', note=main_note, velocity=0, time=TICKS_PER_BAR))

    track.append(Message('note_on', note=fill_note, velocity=100, time=0))
    track.append(Message('note_off', note=fill_note, velocity=0, time=TICKS_PER_BAR))


def build_sequence(structure, filename):
    if len(structure) != 16:
        raise ValueError(f"{filename} must have 16 sections")

    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(MetaMessage('track_name', name=filename, time=0))
    track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(120), time=0))
    track.append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))

    for section_type in structure:
        main_note = next(cycles[section_type])["midi"]
        fill_note = next(cycles["fill"])["midi"]

        add_section(track, section_type, main_note, fill_note)

    track.append(MetaMessage('end_of_track', time=0))
    mid.save(os.path.join(OUTPUT_DIR, filename))

# =========================================
# HIGH-LEVEL ARRANGEMENTS
# =========================================

arrangements = [
    # Classic
    ["intro","verse","verse","chorus","chorus",
     "verse","verse","breakdown",
     "chorus","chorus","special",
     "verse","verse","chorus",
     "special","ending"],

    # Groove-heavy
    ["intro","verse","verse","verse","chorus",
     "chorus","special","verse",
     "breakdown","chorus","chorus",
     "verse","special","chorus",
     "chorus","ending"],

    # Dense
    ["intro","verse","verse","chorus","chorus",
     "chorus","special","breakdown",
     "verse","verse","chorus",
     "chorus","special","verse",
     "chorus","ending"],

    # Breakdown-focused
    ["intro","verse","verse","chorus","chorus",
     "breakdown","breakdown","chorus",
     "chorus","special","verse",
     "verse","chorus","chorus",
     "special","ending"],

    # Experimental
    ["intro","special","verse","verse","chorus",
     "special","chorus","breakdown",
     "verse","verse","special",
     "chorus","chorus","verse",
     "chorus","ending"]
]

# =========================================
# GENERATE
# =========================================

print("Generating Groovemate arrangement sequences...\n")

for i, arr in enumerate(arrangements, start=1):
    filename = f"{i:02d}_sequence.mid"
    build_sequence(arr, filename)
    print(f"✓ Created {filename}")

print("\nDone.")