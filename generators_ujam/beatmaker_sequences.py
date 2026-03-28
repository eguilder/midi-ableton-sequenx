import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage
import os
import re
import itertools

# =========================================
# CONFIG
# =========================================

OUTPUT_DIR = "sequences_beatmaker"
os.makedirs(OUTPUT_DIR, exist_ok=True)

PPQ = 480
TICKS_PER_BAR = PPQ * 4

note_names = ['C', 'C#', 'D', 'D#', 'E', 'F',
              'F#', 'G', 'G#', 'A', 'A#', 'B']

# =========================================
# STYLE NOTES
# =========================================

notes_data = [
    {"file_note": "C#1", "track_name": "Intro C#1"},
    {"file_note": "D#1", "track_name": "Fill 1 D#1"},
    {"file_note": "F#1", "track_name": "Verse 1 F#1"},
    {"file_note": "G#1", "track_name": "Verse 2 G#1"},
    {"file_note": "A#1", "track_name": "Fill 2 A#1"},
    {"file_note": "C#2", "track_name": "Chorus 1 C#2"},
    {"file_note": "D#2", "track_name": "Chorus 2 D#2"},
    {"file_note": "F#2", "track_name": "Break F#2"},
    {"file_note": "G#2", "track_name": "Special G#2"},
    {"file_note": "A#2", "track_name": "Ending A#2"}
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

notes = [{**n, "midi": note_to_midi(n["file_note"])} for n in notes_data]

# =========================================
# GROUPS
# =========================================

def group(prefix):
    return [n for n in notes if n["track_name"].startswith(prefix)]

groups = {
    "intro": group("Intro"),
    "verse": group("Verse"),
    "chorus": group("Chorus"),
    "fill": group("Fill"),
    "break": group("Break"),
    "special": group("Special"),
    "ending": group("Ending"),
}

cycles = {k: itertools.cycle(v) for k, v in groups.items()}

# =========================================
# SECTION LOGIC
# =========================================

def add_section(track, section_type, main_note, fill_note):
    # INTRO (1-bar pattern ×3 + fill)
    if section_type == "intro":
        for _ in range(3):
            track.append(Message('note_on', note=main_note, velocity=100, time=0))
            track.append(Message('note_off', note=main_note, velocity=0, time=TICKS_PER_BAR))

        track.append(Message('note_on', note=fill_note, velocity=100, time=0))
        track.append(Message('note_off', note=fill_note, velocity=0, time=TICKS_PER_BAR))

    # BREAK (2-bar ×2, no fill)
    elif section_type == "break":
        for _ in range(2):
            track.append(Message('note_on', note=main_note, velocity=100, time=0))
            track.append(Message('note_off', note=main_note, velocity=0, time=TICKS_PER_BAR * 2))

    # ENDING (1-bar ×4, no fill)
    elif section_type == "ending":
        for _ in range(4):
            track.append(Message('note_on', note=main_note, velocity=100, time=0))
            track.append(Message('note_off', note=main_note, velocity=0, time=TICKS_PER_BAR))

    # DEFAULT (Verse / Chorus / Special)
    else:
        # Bars 1–2
        track.append(Message('note_on', note=main_note, velocity=100, time=0))
        track.append(Message('note_off', note=main_note, velocity=0, time=TICKS_PER_BAR * 2))

        # Bar 3
        track.append(Message('note_on', note=main_note, velocity=100, time=0))
        track.append(Message('note_off', note=main_note, velocity=0, time=TICKS_PER_BAR))

        # Bar 4 → fill
        track.append(Message('note_on', note=fill_note, velocity=100, time=0))
        track.append(Message('note_off', note=fill_note, velocity=0, time=TICKS_PER_BAR))

# =========================================
# SEQUENCE BUILDER
# =========================================

def build_sequence(structure, filename):
    if len(structure) != 16:
        raise ValueError(f"{filename} must have 16 sections")

    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(MetaMessage('track_name', name=filename, time=0))
    track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(120), time=0))
    track.append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))

    fill_cycle = itertools.cycle(groups["fill"])

    for section_type in structure:
        main_note = next(cycles[section_type])["midi"]
        fill_note = next(fill_cycle)["midi"]

        add_section(track, section_type, main_note, fill_note)

    track.append(MetaMessage('end_of_track', time=0))
    mid.save(os.path.join(OUTPUT_DIR, filename))

# =========================================
# ARRANGEMENTS (16 sections)
# =========================================

arrangements = [
    ["intro","verse","verse","chorus","chorus",
     "verse","verse","break",
     "chorus","chorus","special",
     "verse","verse","chorus",
     "special","ending"],

    ["intro","verse","verse","verse","chorus",
     "chorus","special","verse",
     "break","chorus","chorus",
     "verse","special","chorus",
     "chorus","ending"],

    ["intro","verse","verse","chorus","chorus",
     "break","verse","verse",
     "chorus","chorus","break",
     "special","verse","chorus",
     "chorus","ending"],

    ["intro","verse","verse","chorus","chorus",
     "break","break","chorus",
     "chorus","special","verse",
     "verse","chorus","chorus",
     "special","ending"],

    ["intro","special","verse","verse","chorus",
     "special","chorus","break",
     "verse","verse","special",
     "chorus","chorus","verse",
     "chorus","ending"]
]

# =========================================
# GENERATE
# =========================================

print("Generating Beatmaker sequences (64 bars)...\n")

for i, arr in enumerate(arrangements, start=1):
    filename = f"{i:02d}_sequence.mid"
    build_sequence(arr, filename)
    print(f"✓ Created {filename}")

print("\nDone.")