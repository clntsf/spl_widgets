import pandas as pd
import numpy as np
from io import StringIO
from subprocess import run
from datetime import datetime
from spl_widgets import misc_util

def num_nonzero(n: list[int|float]) -> int:
    """ Returns the number of non-zero items in a given list """
    return sum([x>0 for x in n])

def get_slice_avg_freq(slice: list[int|float]):
    return sum(slice)/max(1,num_nonzero(slice))

def remove_zero_amplitude_freqs(df: pd.DataFrame):
    """ Removes frequencies in the file for which the amplitude value is zero, to simplify averaging frequencies. """
    formants = int(df.columns[0])
    for fmt in range(formants):
        frq_col, amp_col = df.iloc[:,2*fmt + 1], df.iloc[:,2*fmt + 2]
        frq_col *= (amp_col > 0)

def make_output_folder(input_filepath: str):

    now_str = f'{datetime.now():%Y-%m-%d_%H.%M.%S.%f}'
    out_dir_filepath = input_filepath.rpartition("/")[2] + f'/tuning_done_{now_str}'
    run(['mkdir', out_dir_filepath], capture_output=True)

    return out_dir_filepath

def tune_cols(filepath: str, interval: int, scale, tune_freqs):

    scale_notes = misc_util.construct_note_freqs(scale)

    with open(filepath,'r') as reader:
        content = StringIO( reader.read() )
    
    df = pd.read_csv(content, sep='\t')
    formants = int(df.columns[0])

    remove_zero_amplitude_freqs(df)
    size = len(df.index)
    print(df.iloc[:50])

    for freq_col_ndx in range(1, 2*formants, 2):
        freq_col = df.iloc[:,freq_col_ndx]
        newcol = []
 
        for slice_start in range(0, size, interval):
            slice = freq_col[slice_start : slice_start + interval] 

            slice_newfreq = get_slice_avg_freq(slice)
            if tune_freqs:
                slice_newfreq = misc_util.get_closest(scale_notes, slice_newfreq)

            newcol += [slice_newfreq]*len(slice)
        df.iloc[:,freq_col_ndx] = newcol

    # Creates params.txt file
    notes_tuning = hex(sum([2**i*(i+1 in scale) for i in range(12)]))[2:]
    tuning_key = f"{int(tune_freqs)}{interval}-{notes_tuning}"

    args=[
        'Tuning Parameters:',
        '*'*20,
        f'Interval: {10*interval}ms (setting: {interval})',
        f'Scale: {misc_util.num_scale_to_strs(scale) if tune_freqs else "NOT TUNED"}',
        f"Tune Frequencies: {tune_freqs}",
        f'Tuning Key: {tuning_key}'
        ]
    
    with open(f'{out_dir_filepath}/params.txt','w') as writer:
        writer.write('\n'.join(args))
    
    return out_dir_filepath

fp = "bark.swx"
tune_cols(fp, 10, [], False)