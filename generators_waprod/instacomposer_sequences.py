import os
import re
import sys


# ===============================
# MASTER TEMPLATE (EMBEDDED)
# ===============================
MASTER_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>

<Instacomposer3Preset Version="3.0.2"
    PresetName="{preset_name}"
    PresetFolder="7"
    PresetID="310"
    PresetInfo="Preset info."
    ActiveSection="0"
    ActivveTrack="0"
    EditView="0"
    ProcessMidi="1"
    PlayMode="1"
    Tempo="100.0"
    SyncTempo="0"
    ChordDetBarBeat="0.2000000029802322"
    ChordDetComplexity="0.0"
    ChordDetVoiceOrder="1.0"
    LockTrackSettingSong="0"
    LockTrackSettingActiveSong="0"
    LockMIDIChSong="0"
    LockTrackModeSong="0"
    LockTrackOctaveRangeSong="0"
{section_flags}>

{sections}

</Instacomposer3Preset>
"""


# ===============================
# SNAP EXTRACTION
# ===============================
def extract_snap_content(file_path):

    with open(file_path, "r", encoding="utf-8") as f:
        data = f.read()

    snaps = re.findall(
        r"<Snap\d+.*?</Snap\d+>",
        data,
        flags=re.DOTALL
    )

    fixed_snaps = []

    for snap in snaps:

        # Convert:
        # <Snap0> -> <Snap_0>
        # </Snap0> -> </Snap_0>

        snap = re.sub(
            r"<Snap(\d+)",
            r"<Snap_\1",
            snap
        )

        snap = re.sub(
            r"</Snap(\d+)",
            r"</Snap_\1",
            snap
        )

        fixed_snaps.append(snap)

    return "\n".join(fixed_snaps)


# ===============================
# SECTION BLOCK
# ===============================
def build_section_block(index, snap_content):

    return f"""  <Sec_{index} SecLabel="Sec {index+1}" ActiveSnapShot="0"
         SectionMode="-1" SectionLabel="Sec {index+1}"
         SnapActive_0="1" SnapActive_1="0" SnapActive_2="0"
         SnapActive_3="0" SnapActive_4="0" SnapActive_5="0"
         SnapActive_6="0" SnapActive_7="0">
{snap_content}
  </Sec_{index}>
"""


# ===============================
# SECTION FLAGS
# ===============================
def build_section_flags(section_count):

    flags = ""

    for i in range(18):

        value = "1" if i < section_count else "0"

        flags += (
            f'    SectionActive_{i}="{value}"\n'
        )

    return flags.rstrip()


# ===============================
# DETECT KEYS
# ===============================
def detect_keys(prefix):

    pattern = re.compile(
        rf"^{re.escape(prefix)}_\d+_([A-G]#?m?)_4Bar\.txt$"
    )

    keys = set()

    for filename in os.listdir():

        match = pattern.match(filename)

        if match:
            keys.add(match.group(1))

    return sorted(keys)


# ===============================
# FIND FILES FOR KEY
# ===============================
def find_files_for_key(prefix, key):

    pattern = re.compile(
        rf"^{re.escape(prefix)}_(\d+)_({re.escape(key)})_4Bar\.txt$"
    )

    files = []

    for filename in os.listdir():

        match = pattern.match(filename)

        if match:

            files.append(
                (
                    int(match.group(1)),
                    filename
                )
            )

    files.sort(key=lambda x: x[0])

    return [f[1] for f in files]


# ===============================
# BUILD PRESET
# ===============================
def build_preset(prefix, key):

    section_files = find_files_for_key(
        prefix,
        key
    )

    if not section_files:

        print(
            f"No files found for key {key}"
        )

        return

    print(
        f"Building {prefix}_{key} "
        f"with {len(section_files)} sections"
    )

    sections = ""

    for index, filename in enumerate(
        section_files
    ):

        snap_content = extract_snap_content(
            filename
        )

        sections += build_section_block(
            index,
            snap_content
        )

    section_flags = build_section_flags(
        len(section_files)
    )

    final_xml = MASTER_TEMPLATE.format(
        preset_name=f"{prefix}_{key}",
        section_flags=section_flags,
        sections=sections
    )

    output_name = (
        f"{prefix}_{key}_FullPreset.txt"
    )

    with open(
        output_name,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(final_xml)

    print(
        f"✓ Created {output_name}"
    )


# ===============================
# HELP
# ===============================
def print_help():

    print("Usage:")
    print(
        "  python build_preset.py PREFIX KEY"
    )
    print(
        "  python build_preset.py PREFIX ALL"
    )
    print()

    print("Examples:")
    print(
        "  python build_preset.py AH01FI2 Fm"
    )
    print(
        "  python build_preset.py AH01FI2 F#m"
    )
    print(
        "  python build_preset.py AH01FI2 ALL"
    )
    print()

    print("KEY must be:")
    print(
        "  ALL (case-insensitive)"
    )
    print(
        "  or a valid musical key"
    )
    print(
        "  Examples: Fm Gm Am F#m"
    )


# ===============================
# MAIN
# ===============================
if __name__ == "__main__":

    if len(sys.argv) != 3:

        print_help()
        sys.exit(1)

    prefix = sys.argv[1]
    key = sys.argv[2]

    # ALL (case-insensitive)
    if key.lower() == "all":

        keys = detect_keys(prefix)

        if not keys:

            print(
                f"No keys found for prefix "
                f"'{prefix}'"
            )

            sys.exit(1)

        print(
            "Detected keys: "
            + ", ".join(keys)
        )

        for detected_key in keys:

            build_preset(
                prefix,
                detected_key
            )

        sys.exit(0)

    # Strict key validation
    key_pattern = re.compile(
        r"^[A-G](#?m?)$"
    )

    if not key_pattern.match(key):

        print_help()
        sys.exit(1)

    build_preset(
        prefix,
        key
    )