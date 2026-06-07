import os
import re
import sys


# ===============================
# EXTRACT COMPLETE SECTION
# ===============================
def extract_section(file_path):

    with open(file_path, "r", encoding="utf-8") as f:
        data = f.read()

    match = re.search(
        r"<Sec_\d+.*?</Sec_\d+>",
        data,
        flags=re.DOTALL
    )

    if not match:
        raise RuntimeError(
            f"No section block found in {file_path}"
        )

    return match.group(0)


# ===============================
# RENUMBER SECTION
# ===============================
def renumber_section(section_xml, index):

    label = f"Sec {index + 1}"

    section_xml = re.sub(
        r"<Sec_\d+",
        f"<Sec_{index}",
        section_xml,
        count=1
    )

    section_xml = re.sub(
        r"</Sec_\d+>",
        f"</Sec_{index}>",
        section_xml,
        count=1
    )

    section_xml = re.sub(
        r'SecLabel="[^"]*"',
        f'SecLabel="{label}"',
        section_xml
    )

    section_xml = re.sub(
        r'SectionLabel="[^"]*"',
        f'SectionLabel="{label}"',
        section_xml
    )

    return section_xml


# ===============================
# BUILD SECTION FLAGS
# ===============================
def build_section_flags(section_count):

    flags = []

    for i in range(18):
        value = "1" if i < section_count else "0"
        flags.append(
            f'SectionActive_{i}="{value}"'
        )

    return flags


# ===============================
# DETECT KEYS
# ===============================
def detect_keys(prefix):

    pattern = re.compile(
        rf"^{re.escape(prefix)}_\d+_([A-G]#?(?:maj|m))_4Bar\.txt$"
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
# LOAD TEMPLATE FROM FILE
# ===============================
def build_template_from_source(
    source_file,
    preset_name,
    section_count,
    sections_xml
):

    with open(source_file, "r", encoding="utf-8") as f:
        xml = f.read()

    # Extract XML declaration
    xml_decl_match = re.search(
        r"<\?xml.*?\?>",
        xml,
        flags=re.DOTALL
    )

    if not xml_decl_match:
        raise RuntimeError(
            "Could not find XML declaration"
        )

    xml_decl = xml_decl_match.group(0)

    # Extract opening Instacomposer tag
    preset_match = re.search(
        r"<Instacomposer3Preset\b.*?>",
        xml,
        flags=re.DOTALL
    )

    if not preset_match:
        raise RuntimeError(
            "Could not find Instacomposer3Preset tag"
        )

    preset_tag = preset_match.group(0)

    # Update PresetName
    preset_tag = re.sub(
        r'PresetName="[^"]*"',
        f'PresetName="{preset_name}"',
        preset_tag
    )

    # Update SectionActive flags
    flags = build_section_flags(section_count)

    for i, value in enumerate(flags):

        preset_tag = re.sub(
            rf'SectionActive_{i}="[^"]*"',
            value,
            preset_tag
        )

    # Assemble final file
    final_xml = (
        xml_decl
        + "\n\n"
        + preset_tag
        + "\n"
        + sections_xml
        + "\n</Instacomposer3Preset>\n"
    )

    return final_xml


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
        f"Building {prefix}_{key}"
        f" ({len(section_files)} sections)"
    )

    sections = []

    for index, filename in enumerate(
        section_files
    ):

        section_xml = extract_section(
            filename
        )

        section_xml = renumber_section(
            section_xml,
            index
        )

        sections.append(section_xml)

    sections_xml = "\n\n".join(
        sections
    )

    # First file becomes template source
    template_file = section_files[0]

    final_xml = build_template_from_source(
        source_file=template_file,
        preset_name=f"{prefix}_{key}",
        section_count=len(section_files),
        sections_xml=sections_xml
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
        "  python instacomposer_sequences.py PREFIX KEY"
    )
    print(
        "  python instacomposer_sequences.py PREFIX ALL"
    )
    print()

    print("Examples:")
    print(
        "  python instacomposer_sequences.py TMFI2 Cmaj"
    )
    print(
        "  python instacomposer_sequences.py TMFI2 C#maj"
    )
    print(
        "  python instacomposer_sequences.py TMFI2 Fm"
    )
    print(
        "  python instacomposer_sequences.py TMFI2 F#m"
    )
    print(
        "  python instacomposer_sequences.py TMFI2 ALL"
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
        "  Examples: Cmaj C#maj Fm F#m"
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
        r"^[A-G]#?(?:maj|m)$"
    )

    if not key_pattern.match(key):

        print_help()
        sys.exit(1)

    build_preset(
        prefix,
        key
    )
