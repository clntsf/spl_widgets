import pandas as pd
import numpy as np
from io import StringIO
from subprocess import run
from datetime import datetime
from spl_widgets.misc_util import *
from textwrap import dedent

bad_file_str = dedent("""
    File structure of {} is malformed and cannot be read by tune_freq
    only .swx files created with stk_swx are guaranteed to work with tuner.
    If this file was created with stk_swx, please alert me or Prof. Remez
    and provide a copy of the file and its .stk equivalent (if possible)."""
)

def tune_cols(filepath: str, interval: int, scale: list[int], tune_freqs: bool):

    try:
        df = pd.read_csv(
            StringIO(open(filepath,'r').read()),
            sep='\t', skiprows=[0], header=None
        ).dropna(axis=1)
    except Exception:
        raise MalformedFileError(bad_file_str.format(filepath))

    formants = len(df.columns)//2
    size = df.shape[0]
    out_df = pd.DataFrame(df.iloc[:,0])

    scale_notes = construct_note_freqs(scale)
    for fmt in range(formants):
        amp_col = df.iloc[:,2*fmt+2]

        freq_col = df.iloc[:,2*fmt+1]
        freq_col = np.where(amp_col>0, freq_col, 0)
        new_col =[]
 
        for slice_start in range(0, size, interval):

            slice_end = slice_start + interval
            freq_slice = freq_col[slice_start:slice_end]

            nz_amps = np.count_nonzero(amp_col[slice_start:slice_end])
            range_freq = sum(freq_slice) / max(1, nz_amps)

            if tune_freqs is True and range_freq != 0:
                range_freq = get_closest(scale_notes, range_freq)

            new_col+=[range_freq]*len(freq_slice)

        for i, cell in enumerate(new_col):
            if cell == 0:
                new_col[i] = max(new_col[max(0,i-1):i+2])
        
        out_df[f'F{fmt}']=new_col
        out_df[f'A{fmt}']=amp_col

    out_df.columns = [formants]+['']*(2*formants)

    # Makes, populates and creates a folder for tuned file
    now_str = f'{datetime.now():%Y-%m-%d_%H.%M.%S.%f}'
    filename = filepath[filepath.rfind('/'):-4]

    out_dir_filepath = filepath[:filepath.rfind('/')]+f'/tuning_done_{now_str}'
    run(['mkdir', out_dir_filepath], capture_output=True)

    # convert df to tab-separated format and write to .swx file
    tsv = df_to_tsv(df)
    with open(f"{out_dir_filepath}/{filename}_tuned.swx", "w") as writer:
        writer.write(tsv)

    # Creates params.txt file
    notes_tuning = hex(sum([2**i*(i+1 in scale) for i in range(12)]))[2:]
    tuning_key = f"{int(tune_freqs)}{str(interval).zfill(2)}-{notes_tuning}"

    args=[
        'Tuning Parameters:',
        '*'*20,
        f'Interval: {10*interval}ms (setting: {interval})',
        f'Scale: {num_scale_to_strs(scale) if tune_freqs else "NOT TUNED"}',
        f"Tune Frequencies: {tune_freqs}",
        f'Tuning Key: {tuning_key}'
        ]
    
    with open(f'{out_dir_filepath}/params.txt','w') as writer:
        writer.write('\n'.join(args))
    
    return out_dir_filepath