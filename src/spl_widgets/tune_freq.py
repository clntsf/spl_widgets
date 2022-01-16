import pandas as pd
import numpy as np
from io import StringIO
from subprocess import run
from datetime import datetime
from spl_widgets.misc_util import *

def tune_cols(filepath: str, interval: int, scale, tune_freqs):

    df = pd.read_csv(StringIO(open(filepath,'r').read()), sep='\t')

    formants = int(len(df.columns)/2)
    size = len(df.index)
    out_df = pd.DataFrame(df.iloc[:,0])

    scale_notes = construct_note_freqs(scale)

    for i in range(formants):

        amp_col = df.iloc[:,2*i+2]
        freq_col = [n * (amp_col[j]>0) for j, n in enumerate(df.iloc[:,2*i+1])]
        new_col =[]
 
        for slice_start in range(0, size, interval):

            slice_end = slice_start + interval
            freq_slice = freq_col[slice_start:slice_end]

            nz_amps = np.count_nonzero(amp_col[slice_start:slice_end])
            range_freq = sum(freq_slice) / max(1, nz_amps)

            if tune_freqs is True and range_freq != 0:
                range_freq = get_closest(scale_notes, range_freq)

            new_col+=[range_freq]*len(freq_slice)

        out_df[f'F{i}']=new_col; out_df[f'A{i}']=amp_col

    out_df.columns = [formants]+['']*(2*formants)

    # Makes, populates and creates a folder for tuned file
    now_str = f'{datetime.now():%Y-%m-%d_%H.%M.%S.%f}'
    filename = filepath[filepath.rfind('/'):-4]

    out_dir_filepath = filepath[:filepath.rfind('/')]+f'/tuning_done_{now_str}'
    run(['mkdir', out_dir_filepath], capture_output=True)

    out_df.to_csv(f'{out_dir_filepath}/{filename}_tuned.tsv', index=False, sep='\t')
    run(['mv', f'{out_dir_filepath}/{filename}_tuned.tsv', f'{out_dir_filepath}/{filename}_tuned.swx'], capture_output=True)

    # Creates params.txt file
    notes_tuning = hex(sum([2**i*(i+1 in scale) for i in range(12)]))[2:]
    tuning_key = f"{int(tune_freqs)}{interval}-{notes_tuning}"

    args=[
        'Tuning Parameters:',
        '*'*20,
        f'Interval: {10*interval}ms (setting: {interval})',
        f'Scale: {num_scale_to_strs(scale) if tune_freqs else "NOT TUNED"}',
        f"Tune Frequencies: {tune_freqs}",
        f'Tuning Key: {tuning_key}'
        ]
    
    with open(f'{out_dir_filepath}/params.txt','w') as writer: writer.write('\n'.join(args))\
        
    return out_dir_filepath

fp = '/Users/colin/desktop/tuner_misc/swxf/bark/bark.swx'
tune_cols(fp,10,construct_default_scale(1,'Major Scale'), True)