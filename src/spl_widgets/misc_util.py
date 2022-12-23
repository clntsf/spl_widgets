from math import log

# for use in stk_swx and tune_freq
class MalformedFileError(Exception): pass

# Stores notes of the chromatic scale for referencing
notes=['A','A#','B','C','C#','D','D#','E','F','F#','G','G#']

# Constructs a major scale starting from a given number note
default_scales ={
    'Major Scale': [0,2,4,5,7,9,11],
    'Natural Minor Scale': [0,2,3,5,7,8,10],
    'Harmonic Minor Scale': [0,2,3,5,7,8,11],
    'Melodic Minor Scale': [0,2,3,5,7,9,11]
}

def construct_default_scale(note: int, scale_type: str) -> list:
    return [(note+n)%12 or 12 for n in default_scales[scale_type]]

# Converts notes in string form to their number equivalents, with A as key 1
def str_scale_to_numbers(scale: "list[str]") -> "list[int]":
    return sorted([notes.index(note.upper())+1 for note in scale])

# Converts notes in number form to their string equivalents, with A as key 1
def num_scale_to_strs(scale: "list[int]") -> "list[str]":
    return [notes[note-1] for note in sorted(scale)]

# Converts note number to frequency
def to_freq(note: int) -> float:
    return 27.5 * (2 ** ((note - 1) / 12))

# Converts frequency to note number
def to_note(freq: float) -> int:
    return round(log(freq/27.5, 2**(1/12))+1,4)

# Get closest element to a target item in a list
def get_closest(pool: list, target: float) -> float:
    return min(pool, key=lambda x: abs(x-target))

# Get all valid note frequencies given a scale of notes
def construct_note_freqs(scale: "list[int]") -> "list[float]":
    return [to_freq((12*i)+j) for i in range(8) for j in scale if 12*i+j<=88]

def get_scale(key: str) -> tuple[int, int, list[int], list[int]]:

    tune_freqs = int(key[0])
    interval = int(key[1:3])

    scale_bin = bin(int(key[4:7],base=16))[2:]
    scale_bin = scale_bin.zfill(12)
    scale_list = [i for i in range(1,13) if scale_bin[-i] == "1"]

    fmts_to_tune = None
    if len(key) > 8:
        bits = bin(int(key[8:], base=16))[2:]
        fmts_to_tune = [*map(int,bits[::-1])]
        fmts_to_tune = [n+1 for n in range(len(bits)) if fmts_to_tune[n]]

    return tune_freqs, interval, scale_list, fmts_to_tune

# formats a pd.DataFrame to tsv (returns a string to be written to file)
def df_to_tsv(df) -> str:
    rows = ["\t".join(map(str, df.columns))]
    for i in df.index:
        rows.append("\t".join(map(str, df.iloc[i])))
    return "\n".join(rows)