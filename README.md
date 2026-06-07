# MIDI Generators for Ableton Live

A collection of Python scripts for generating MIDI files designed to control sequencer- and phrase-based instruments for usage with **Ableton Live**, **UJAM**, **Native Instruments**, **Spectrasonics**, **WA Production** and **Audiomodern** products. All generators create Ableton-ready MIDI clips with correct octave handling, embedded track names, and predictable note layouts. Other DAWs can use these sequencer notes as well.

The MIDI clips in this repo can either be generated via scripts or used directly inside Ableton Live.

---

## Features

- **Ableton-correct MIDI note mapping** (handles Ableton’s octave offset)
- **Embedded track-name metadata** 
- **Multiple generator layouts** for different instrument ecosystems
- **Sequentially numbered filenames** (sorted by pitch)
- **Clip names that match filenames** for easy browsing

---

## Generator Categories

Generators are organized by target ecosystem and workflow:

1. **Ableton-native generators**: General-purpose note, instrument-note, and chord/progression MIDI clips.
2. **UJAM generators**: Beatmaker, drummer, bassist, guitarist, pianist, synth, Groovemate, SE-DRUMS, and SE-ORCHESTRA trigger-note layouts.
3. **Native Instruments generators**: Kontakt and NI-style phrase, chord, groove, and sound/pattern trigger layouts.
4. **Spectrasonics generators**: Stylus groove trigger clips across extended and normal ranges.
5. **WA Production generators**: Instachord MIDI trigger grids and Instacomposer 3 preset assembly from exported section files.
6. **Audiomodern generators**: Playbeat remix groove trigger clips.
7. **reMIDI generators**: Structured drum, bass, and pad sequence generators for arrangement-style MIDI output.

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

### 9. SE-ORCHESTRA Generator (`se-orch_notes.py`)
Orchestral pattern layout:
- **C1-A1** -> Phrases
- **C#1, D#1, F#1, G#1** -> Additions
- **A#1** -> End
- **B1** -> Stop
- **C2-B2** -> Bass
- **C3-B4** -> Play

### 10. SE-DRUMS Generator (`se-drums_notes.py`)
Drum pattern layout:
- **C2-B2** -> Common Phrases
- **C#2, D#2** -> Hits
- **F#2, G#2, A#2** -> Metals
- **C3-D#4** -> Style Phrases, with Intros, Fills, and Endings
- **C#3, D#3** -> Intros
- **F#3, G#3, A#3** -> Fills
- **C#4, D#4** -> Endings
- **E4** -> Stop

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
**Chord triggering on white keys**:
- **C3, D3, E3, F3, G3, A3, B3, C4** -> Chord 1-8

### 7. TRK-01
**Kick and bass sound/pattern selection**:
- **C1-G1** -> Kick Sound 1-8
- **C2-G2** -> Kick Pattern 1-8
- **C3-G3** -> Bass Sound 1-8
- **C4-G4** -> Bass Pattern 1-8

---

## Spectrasonics Generators

### 1. Stylus Generator (`stylus_grooves.py`)
**Groove triggering across extended and normal ranges**:
- **C1-B2** -> Extended Range grooves
- **C3-A5** -> Normal Range grooves
- Groove output folder: `grooves_stylus` (4-bar clips)
- Hit output folder: `hits_stylus` (2-bar clips)

### 2. Stylus Sequence Generator (`stylus_sequences.py`)
**Randomized groove sequence clips**:
- Output folder: `sequences_stylus`
- Creates 8 Normal Sequence clips and 8 Extended Sequence clips
- Each sequence contains 8 unique notes
- **Normal Sequence 1-8** -> first note `C3`, then 7 random notes from **C3-A5**
- **Extended Sequence 1-8** -> first note `C1`, then 7 random notes from **C1-B2**
- Each note is 4 bars long

---

## WA Production Generators

### 1. Instachord 2
**Instrument x Phrase grid**:
- **C1-B1** -> Chords A 1-12
- **C2-B2** -> Chords B 1-12
- **C3-B3** -> Picks A 1-12
- **C4-B4** -> Picks B 1-12

### 2. Instacomposer 3
**instacomposer_sequences.py**:
- Builds complete Instacomposer 3 preset text files from exported 4-bar section files
- Input files are matched as `PREFIX_###_KEY_4Bar.txt`
- Renumbers sections sequentially and updates section labels to `Sec 1`, `Sec 2`, etc.
- Updates active section flags for the number of included sections
- Outputs `PREFIX_KEY_FullPreset.txt`
- Requires arguments: `PREFIX` and `KEY` or `ALL`
- `PREFIX` matches exported section files named like `PREFIX_###_KEY_4Bar.txt`
- `KEY` must be a valid exported major or minor key such as `Cmaj`, `C#maj`, `Fm`, or `F#m`; use `ALL` to build every detected key
- Run for one key: `python3 ./generators_waprod/instacomposer_sequences.py PREFIX C#maj`
- Run for all detected keys: `python3 ./generators_waprod/instacomposer_sequences.py PREFIX ALL`

---
## Audiomodern Generators

### 1. Playbeat
**Remix Groove selection (chromatic)**:
- **C-3–B-4** → Groove 1–12

## reMIDI Generators

Generates fully structured song arrangements for use with reMIDI 3, which is a phrase-based MIDI engine.
Unlike static note generators, this system creates complete compositions with section-based logic, timing alignment, and controlled randomness.

`remidi_sequences.py` requires a `section_type` argument: `drums`, `bass`, `pads`, or `all`.
Optional arguments are `--rows 0,1,2,3`, `--note-length 4`, and `--section-length 168`.

### 1. Drums
**Drum Sections**
- **0_A → Intro
- **0_B → Verse
- **1_A → Pre-Chorus
- **1_B → Chorus
- **2_A → Bridge
- **2_B → Fill source
- **3_A → Short fills (2 bars)
- **3_B → Long fills (4 bars)

### 2. Bass
**Drum Sections**
- **0_A → Intro
- **0_B → Verse
- **1_A → Pre-Chorus
- **1_B → Chorus

### 3. Pads
**Progressions Sections**
- **3_A → Intro
- **3_B → Verse
- **4_A → Pre-Chorus
- **4_B → Chorus


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
To re-generate the data, run any generator script directly.

Ableton-native generators:

```bash
python3 ./generators_ableton/create_notes.py
python3 ./generators_ableton/instrument_notes.py
python3 ./generators_ableton/create_chords.py
```

UJAM generators:

```bash
python3 ./generators_ujam/beatmaker_notes.py
python3 ./generators_ujam/beatmaker_sequences.py
python3 ./generators_ujam/drummer_notes.py
python3 ./generators_ujam/groovemate_notes.py
python3 ./generators_ujam/groovemate_sequences.py
python3 ./generators_ujam/pianist_notes.py
python3 ./generators_ujam/se-drums_notes.py
python3 ./generators_ujam/se-orch_notes.py
python3 ./generators_ujam/subcraft_notes.py
python3 ./generators_ujam/usynth_notes.py
python3 ./generators_ujam/vbassist_notes.py
python3 ./generators_ujam/vguitarist_notes.py
```

Native Instruments generators:

```bash
python3 ./generators_native/drumlab_notes.py
python3 ./generators_native/playbox_notes.py
python3 ./generators_native/playseries_notes.py
python3 ./generators_native/s-horns_notes.py
python3 ./generators_native/s-percussionist_notes.py
python3 ./generators_native/session_notes.py
python3 ./generators_native/spotlight_notes.py
python3 ./generators_native/trk-01_notes.py
```

Spectrasonics generators:

```bash
python3 ./generators_spectrasonics/stylus_grooves.py
python3 ./generators_spectrasonics/stylus_sequences.py
```

WA Production generators:

```bash
python3 ./generators_waprod/instachord_notes.py
python3 ./generators_waprod/instacomposer_sequences.py PREFIX C#maj
python3 ./generators_waprod/instacomposer_sequences.py PREFIX ALL
```

Audiomodern generators:

```bash
python3 ./generators_audiomodern/playbeat_notes.py
```

reMIDI generators:

```bash
python3 generators_remidi/remidi_sequences.py all
python3 generators_remidi/remidi_sequences.py drums --rows 0,1,2,3 --note-length 4 --section-length 168
```

Each script creates a separate folder of **Ableton-ready MIDI clips**, numbered and named for immediate use in the corresponding plugin track.

---

## How It Works

- **Octave correction**: Adjusts for Ableton’s piano roll octave display
- **Track naming**: Stores clip names in MIDI metadata
- **Predictable ordering**: Lowest to highest pitch
- **Controller-friendly layouts**: Designed for Push, Launchpad, APC, and keyboard controllers
