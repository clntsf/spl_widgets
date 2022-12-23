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

def get_tuning_info(key: str) -> tuple[int, int, list[int], list[int]]:

    tune_freqs = int(key[0])
    interval = int(key[1:3])

    scale_list = decode_hex_to_num_list(key[4:7])
    
    fmts_to_tune = None
    if len(key) > 8:
        fmts_to_tune = decode_hex_to_num_list(key[8:])

    return (
        tune_freqs,
        interval,
        scale_list,
        fmts_to_tune
    )

# formats a pd.DataFrame to tsv (returns a string to be written to file)
def df_to_tsv(df) -> str:
    rows = ["\t".join(map(str, df.columns))]
    for i in df.index:
        rows.append("\t".join(map(str, df.iloc[i])))
    return "\n".join(rows)

def encode_num_list_as_hex(num_list: set[int]) -> str:
    """
    Encodes a list of unique integers into a hexadecimal string in which
    the value of bit i (where the LSB is 0) indicates whether i+1 is present
    in the list.
    
    Used for the generation of tuning keys, both for the scale notes (3 hex digits)
    and for the formants tuned (2 hex digits)

    Note: The list containing only unique values is not enforced as this is a function
    intended for internal use by tune_cols(), so improper inputs will produce outputs
    that will not decode symmetrically. For use outside of this context sanitization of
    the input should be implemented.

    Parameters
    ----------
    num_list : list[int]
        The list of numbers to be encoded.
        Should contain only unique numbers but this is not enforced (see above)
    
    Returns
    ----------
    str
        The encoded hexadecimal string, formatted and made uppercase

    """

    list_hex = hex(sum( 2**(i-1) for i in num_list ))
    return list_hex[2:].upper()

def decode_hex_to_num_list(encoded_str: str) -> list[int]:
    """
    Decodes a string of hexadecimal digits into a list of unique integers.
    The inverse operation to encode_num_list_as_hex().

    Used internally in get_tuning_info() for the decoding of the scale notes
    and formants to tune from the tuning key passed

    Will always produce a list of unique integers, but may not produce a symmetrical
    output if the list inputted to encode_num_list_as_hex() contained duplicates
    (see documentation for that function)

    Parameters
    ----------
    encoded_str : str
        The encoded hexadecimal string
    
    Returns
    ----------
    list[int]
        The list of unique integers encoded in the inputted string (*: see caveats above)

    """
    
    bits = bin(int(encoded_str, base=16))
    out = [*map(int, bits[:1:-1])]
    return [i+1 for i,n in enumerate(out) if n]