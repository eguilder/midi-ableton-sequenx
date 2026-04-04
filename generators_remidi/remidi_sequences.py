import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage
import os
import random

# ===== CONFIG =====
TICKS_PER_BAR = 1920
BPM = 120

DRUM_DIR = "sequences_remidi_drums"
BASS_DIR = "sequences_remidi_bass"

SEQUENCE_COUNT = 8

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
              'F#', 'G', 'G#', 'A', 'A#', 'B']


def midi_to_ableton_name(midi_num):
    octave = (midi_num // 12) - 2
    note_index = midi_num % 12
    return f"{NOTE_NAMES[note_index]}{octave}"


# ===== ROW NOTE MAP =====
ROW_NOTE_MAP = {
    "0_A": list(range(0, 8)),
    "0_B": list(range(8, 16)),
    "1_A": list(range(16, 24)),
    "1_B": list(range(24, 32)),
    "2_A": list(range(32, 40)),
    "2_B": list(range(40, 48)),
    "3_A": list(range(48, 56)),
    "3_B": list(range(56, 64)),
}

SECTION_MAP = {
    "Intro": "0_A",
    "Verse": "0_B",
    "PreChorus": "1_A",
    "Chorus": "1_B",
    "Bridge": "2_A",
}

BASS_SECTIONS = {"Intro", "Verse", "PreChorus", "Chorus"}

# ===== ARRANGEMENTS =====
ARRANGEMENTS = [
    ["Intro", "Verse", "PreChorus", "Chorus",
     "Verse", "PreChorus", "Chorus",
     "Bridge", "Chorus"],

    ["Intro", "Verse", "Chorus",
     "Verse", "Chorus",
     "Bridge", "Chorus"],

    ["Intro", "Verse", "PreChorus", "Chorus",
     "Verse", "Chorus",
     "Bridge", "PreChorus", "Chorus"],

    ["Intro", "Verse", "Chorus",
     "Bridge", "Chorus"]
]


# ===== MIDI SETUP =====
def create_midi(name):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(MetaMessage('track_name', name=name, time=0))

    tempo = mido.bpm2tempo(BPM)
    track.append(MetaMessage('set_tempo', tempo=tempo, time=0))

    track.append(MetaMessage('time_signature',
                             numerator=4,
                             denominator=4,
                             clocks_per_click=24,
                             notated_32nd_notes_per_beat=8,
                             time=0))
    return mid, track


def add_clip(track, note, bars):
    duration = bars * TICKS_PER_BAR
    track.append(Message('note_on', note=note, velocity=100, time=0))
    track.append(Message('note_off', note=note, velocity=100, time=duration))


# ===== CLIP SELECTION =====
def pick_two_clips(row_id):
    return random.sample(ROW_NOTE_MAP[row_id][:4], 2)


def pick_short_fill():
    return random.choice(ROW_NOTE_MAP["2_B"] + ROW_NOTE_MAP["3_A"])


def pick_long_fill():
    return random.choice(ROW_NOTE_MAP["3_B"])


# ===== MAIN GENERATOR =====
def generate_sequence(index):

    drum_mid, drum_track = create_midi("Drums")
    bass_mid, bass_track = create_midi("Bass")

    arrangement = random.choice(ARRANGEMENTS)

    debug = []

    last_bass = None

    for section in arrangement:

        row_id = SECTION_MAP[section]

        # ===== DRUMS =====
        drum_a, drum_b = pick_two_clips(row_id)

        use_long = random.random() < 0.3

        if use_long:
            fill = pick_long_fill()
            drum_structure = [(drum_a, 8), (drum_b, 4), (fill, 4)]
            fill_type = "LONG"
        else:
            fill = pick_short_fill()
            drum_structure = [(drum_a, 8), (drum_b, 6), (fill, 2)]
            fill_type = "SHORT"

        for d_note, bars in drum_structure:
            add_clip(drum_track, d_note, bars)

        # ===== BASS =====
        if section in BASS_SECTIONS:
            bass_a, bass_b = pick_two_clips(row_id)
            last_bass = (bass_a, bass_b)
        else:
            # reuse previous bass
            if last_bass is None:
                last_bass = pick_two_clips("0_B")  # fallback to Verse
            bass_a, bass_b = last_bass

        # always fill full 16 bars
        add_clip(bass_track, bass_a, 8)
        add_clip(bass_track, bass_b, 8)

        debug.append({
            "section": section,
            "drums": (drum_a, drum_b),
            "fill": fill,
            "fill_type": fill_type,
            "bass": (bass_a, bass_b)
        })

    drum_track.append(MetaMessage('end_of_track', time=0))
    bass_track.append(MetaMessage('end_of_track', time=0))

    drum_path = os.path.join(DRUM_DIR, f"sequence_{index+1:02d}.mid")
    bass_path = os.path.join(BASS_DIR, f"sequence_{index+1:02d}.mid")

    drum_mid.save(drum_path)
    bass_mid.save(bass_path)

    return arrangement, debug


# ===== MAIN =====
def main():
    os.makedirs(DRUM_DIR, exist_ok=True)
    os.makedirs(BASS_DIR, exist_ok=True)

    print("=" * 60)
    print("Generating aligned drum + bass sequences")
    print("=" * 60)

    for i in range(SEQUENCE_COUNT):
        arrangement, debug = generate_sequence(i)

        print(f"\nSequence {i+1:02d}")
        print("Arrangement:", " → ".join(arrangement))

        for entry in debug:
            drum_names = [midi_to_ableton_name(n) for n in entry["drums"]]
            fill_name = midi_to_ableton_name(entry["fill"])
            bass_names = [midi_to_ableton_name(n) for n in entry["bass"]]

            print(f"  {entry['section']}: {drum_names} | fill={fill_name} ({entry['fill_type']}) | bass={bass_names}")

    print("\n✓ Done")
    print("✓ No bass gaps — fully continuous")


if __name__ == "__main__":
    main()