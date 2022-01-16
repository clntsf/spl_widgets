from math import log

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