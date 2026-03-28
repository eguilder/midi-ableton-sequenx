# MIDI Generators for Ableton Live

A collection of Python scripts for generating MIDI files designed to control sequencer- and phrase-based instruments for usage with **Ableton Live**, **UJAM**, **Native Instruments** and **Audiomodern** products. All generators create Ableton-ready MIDI clips with correct octave handling, embedded track names, and predictable note layouts. Other DAWs can use these sequencer notes as well.

The MIDI clips in this repo can either be generated via scripts or used directly inside Ableton Live.

---

## Features

- **Ableton-correct MIDI note mapping** (handles Ableton’s octave offset)
- **Embedded track-name metadata** (no more “Track 0” clips)
- **Multiple generator layouts** for different instrument ecosystems
- **Sequentially numbered filenames** (sorted by pitch)
- **Clip names that match filenames** for easy browsing

---

## Generator Categories

Generators are organized into **three logical categories**, based on the target ecosystem:

1. **Ableton-native generators**
2. **UJAM generators**
3. **Native Instruments generators**

---

## Ableton Generators

### 1. Main Ableton Generator (`create_notes.py`)
Generates any range of notes from **C0 to C6**, supporting both Ableton and standard MIDI notation.

### 2. Chord Generator (`create_chords.py`)
Generates chord triads and progressions for use with Ableton clips and sequencer instruments:
- Major and minor triads (all 12 keys)
- Common progressions (I–IV–V, ii–V–I, etc.)
- Multiple voicings (root, 1st inversion, 2nd inversion)
- Roman numeral labeling

---

## UJAM Generators

### 1. Beatmaker Generator (`beatmaker_notes.py`)
Generates specific notes for beatmaking with section names:
- C#1 (Intro), D#1 (Fill), F#1 (Verse 1), G#1 (Verse 2), A#1 (Fill)
- C#2 (Chorus 1), D#2 (Chorus 2), F#2 (Break), G#2 (Special), A#2 (Ending)

### 2. Subcraft Generator (`subcraft_notes.py`)
Generates C2 through E2 with loop patterns:
- C2 (Loop 1), C#2 (Loop 2), D2 (Loop 3), D#2 (Stop), E2 (Loop 4)

### 3. USynth Generator (`usynth_notes.py`)
Generates complete octave C1 through B1 with function names:
- Loop patterns, mute, repeat, tempo multipliers (Time x2/x3/x4), stop

### 4. V-Drummer Generator (`drummer_notes.py`)
Generates comprehensive drum patterns across multiple octaves:
- **C3-G3**: Verse 1-5 patterns
- **C#3, D#3**: Intro 1-2 patterns
- **F#3, G#3, A#3**: Fill 1-3 patterns
- **A3-E4**: Chorus 1-5 patterns
- **C#4, D#4**: Ending 1-2 patterns
- **F4, G4, A4**: Special 1-3 patterns
- **F#4, G#4, A#4**: Breakdown 1-3 patterns
- **B4**: Stop pattern

### 5. V-Bassist Generator (`vbassist_notes.py`)
Generates bass patterns with phrases, styles, and transitions:
- **C0**: Silence pattern
- **C#0-B1**: Phrases 1-18 with Intros and Fills
- **C2-A#2**: Styles 1-6 with Style Intros and Style Fills
- **B2**: Stop pattern

### 6. V-Pianist Generator (`pianist_notes.py`)
Generates piano phrases and chord progressions:
- **C1-B1**: Phrases 1-7 with Fills
- **C#1, D#1**: Low Chord and High Chord progressions

### 7. V-Guitarist Generator (`vguitarist_notes.py`)
Generates guitar patterns across multiple ranges:
- **C0**: Silence pattern
- **C#0-B1**: Phrases 1-23
- **C2-A#2**: Styles 1-11
- **B2**: Stop pattern

### 8. Groovemate Generator (`groovemate_notes.py`)
Style pattern layout:
- **C3 D3 E3 F3 G3** → Verses
- **C#3 D#3** → Intros
- **F#3 G#3 A#3** → Fills
- **A3 B3 C4 D4 E4** → Choruses
- **C#4 D#4** → Endings
- **F4 G4 A4** → Specials
- **F#4 G#4 A#4** → Breakdowns
- **B4** → Stop
---

## Native Instruments Generators

These generators follow **Native Instruments’ phrase-based keyboard layouts**, commonly used across Kontakt-based instruments.

### 1. Spotlight Series
**Patterns and Phrases across two octaves**:
- **C1–B1** → Pattern 1–12
- **C2–B2** → Phrase 1–12

### 2. Drumlab
**Groove selection (chromatic)**:
- **C-1–B-1** → Groove 1–12

### 3. Session Percussionist
**Instrument × Phrase grid**:
- **C1–E1** → Inst 1 Phrase 1–5
- **C2–E2** → Inst 2 Phrase 1–5
- **C3–E3** → Inst 3 Phrase 1–5
- **C4–E4** → Inst 4 Phrase 1–5

### 4. Session Horns
**White-key phrase layout**:
- **C1–A1** → Phrase 1–6

### 5. Session Player
**Chromatic phrase triggering**:
- **C1–G1** → Phrase 1–8

### 6. Play Series
**Extended chromatic pattern range**:
- **C3–D#4** → Pattern 1–16

### 6. Playbox

### 6. TRK-01

---
## Audiomodern Generators

### 1. Playbeat
**Remix Groove selection (chromatic)**:
- **C-3–B-4** → Groove 1–12

## Installation

1. Install Python **3.6 or higher**
2. Install dependencies:

---

```bash
pip install -r requirements.txt
```

---

## Usage

The note data is already present in this repo, in the folders notes_* and midi_files_ableton_*.
To re-generate the data, run any generator script directly:

```bash
python ./generators_ableton/create_chords.py
python ./generators_ableton/create_notes.py
python ./generators_ableton/instrument_notes.py

python ./generators_native/drumlab_notes.py
python ./generators_native/playbox_notes.py
python ./generators_native/playseries_notes.py
python ./generators_native/s-horns_notes.py
python ./generators_native/s-percussionist_notes.py
python ./generators_native/session_notes.py
python ./generators_native/spotlight_notes.py
python ./generators_native/trk-01_notes.py

python ./generators_ujam/beatmaker_notes.py
python ./generators_ujam/drummer_notes.py
python ./generators_ujam/pianist_notes.py
python ./generators_ujam/subcraft_notes.py
python ./generators_ujam/usynth_notes.py
python ./generators_ujam/vbassist_notes.py
python ./generators_ujam/vguitarist_notes.py
python ./generators_ujam/groovemate_notes.py

python ./generators_audiomodern/playbeat_notes.py
```

Each script creates a separate folder of **Ableton-ready MIDI clips**, numbered and named for immediate use in the corresponding plugin track.

---

## How It Works

- **Octave correction**: Adjusts for Ableton’s piano roll octave display
- **Track naming**: Stores clip names in MIDI metadata
- **Predictable ordering**: Lowest to highest pitch
- **Controller-friendly layouts**: Designed for Push, Launchpad, APC, and keyboard controllers
