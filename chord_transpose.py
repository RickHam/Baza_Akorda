import re

NOTES = [
    "C", "C#", "D", "D#", "E", "F",
    "F#", "G", "G#", "A", "A#", "B"
]

FLAT_TO_SHARP = {
    "Db": "C#",
    "Eb": "D#",
    "Gb": "F#",
    "Ab": "G#",
    "Bb": "A#"
}

CHORD_PATTERN = re.compile(
    r"\b([A-G](?:#|b)?)(.*?)(?=\s|$)"
)


def transpose_chord(chord, steps):
    match = CHORD_PATTERN.match(chord)

    if not match:
        return chord

    root = match.group(1)
    suffix = match.group(2)

    root = FLAT_TO_SHARP.get(root, root)

    if root not in NOTES:
        return chord

    idx = NOTES.index(root)
    idx = (idx + steps) % len(NOTES)

    return NOTES[idx] + suffix


def transpose_text(text, steps):

    def replace(match):
        return transpose_chord(match.group(0), steps)

    return CHORD_PATTERN.sub(replace, text)