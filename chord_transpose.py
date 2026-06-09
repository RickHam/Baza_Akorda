import re

NOTES = ["C", "C#", "D", "D#", "E", "F",
         "F#", "G", "G#", "A", "A#", "B"]

FLAT_TO_SHARP = {
    "Db": "C#",
    "Eb": "D#",
    "Gb": "F#",
    "Ab": "G#",
    "Bb": "A#"
}

H_TO_B = {
       "H": "B"
    }
# chord = root + optional modifiers + optional bass
CHORD_REGEX = re.compile(
    r"([A-H](?:#|b)?(?:m|maj|min|dim|aug|sus\d*|add\d*|7|9|11|13)*)"
    r"(?:/([A-G](?:#|b)?))?"
)


def normalize(note):
    note = H_TO_B.get(note, note)
    return FLAT_TO_SHARP.get(note, note)


def transpose_note(note, steps):
    note = normalize(note)

    if note not in NOTES:
        return note

    i = NOTES.index(note)
    return NOTES[(i + steps) % 12]


def transpose_text(text, steps):

    
    
    def replace(match):
        chord = match.group(1)
        bass = match.group(2)

        # split root + suffix
        m = re.match(r"([A-H](?:#|b)?)(.*)", chord)
        if not m:
            return chord

        root = m.group(1)
        suffix = m.group(2)

        new_root = transpose_note(root, steps)

        if bass:
            new_bass = transpose_note(bass, steps)
            return f"{new_root}{suffix}/{new_bass}"

        return f"{new_root}{suffix}"

    return CHORD_REGEX.sub(replace, text)