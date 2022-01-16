import pandas as pd
from io import StringIO
from subprocess import run
from datetime import datetime
from .misc_util import *

def tune_cols(filepath: str, interval: int, scale, tune_freqs):

    # --- Fetches the data from the inputted .swx file --- #
    df = pd.read_csv(StringIO(open(filepath,'r').read()), sep='\t')

    # --- Gets formant number and column length, and creates a DataFrame obj to output to --- #
    formants, vlen = int(len(df.columns)/2), len(df.index)
    out_df = pd.DataFrame(df.iloc[:,0])

    # --- Constructs a list of valid note freqs for the inputted scale --- #
    scale_notes = construct_note_freqs(scale)

    # --- Tunes the file with the given parameters --- #

    for i in range(formants):
        # --- Takes freq col and amp col for the formant, and makes a new one to output to --- #
        freq_col, amp_col, new_col = df.iloc[:,2*i+1], df.iloc[:,2*i+2], []

        # --- Operates over slices of the columns, with a maximum length equal to the averaging interval --- # 
        for j in range(0,vlen,interval):

            # --- Caps slice length if the number of remaining values in the column is less than the averaging interval --- #
            slice = j; slice_end = min(vlen, slice+interval)
            # --- Gets number of non-zero amplitudes, and each of the corresponding frequency values --- #
            amp_ceils = [int(n>0) for n in amp_col[slice:slice_end]]
            nz_freq = [freq * amp_ceils[k] for k, freq in enumerate(freq_col[slice:slice_end])]

            # --- Gets the averaged frequency of the slice, with safety measures to prevent division by 0 --- #
            range_freq = sum(nz_freq)/max(1,sum(amp_ceils))
            # --- If the user wants to force the frequencies to one/more notes, this does it --- #
            if tune_freqs and range_freq: range_freq = get_closest(scale_notes, range_freq)
            # --- Adds the averaged/tuned slice data to the new frequency column --- #
            new_col+=[range_freq]*(slice_end-slice)

        # --- Adds the new freq column and old amp column to the output DataFrame --- #
        out_df[f'F{i}']=new_col; out_df[f'A{i}']=amp_col

    # --- Formats the output DataFrame's column names, setting the first to the number of formants and all others to empty --- #
    out_df.columns = [formants]+['']*(2*formants)

    # --- Misc information for file output --- #
    now_str = f'{datetime.now():%Y-%m-%d_%h.%M.%S.%f}'
    filename = filepath[filepath.rfind('/'):-4]

    # --- Makes a new folder in the original file's directory to store the output and info files --- #
    out_dir_filepath = filepath[:filepath.rfind('/')]+f'/tuning_done_{now_str}'
    run(['mkdir', out_dir_filepath], capture_output=True)

    # --- Writes the file out to a new .swx file --- #
    out_df.to_csv(f'{out_dir_filepath}/{filename}_tuned.tsv', index=False, sep='\t')
    run(['mv', f'{out_dir_filepath}/{filename}_tuned.tsv', f'{out_dir_filepath}/{filename}_tuned.swx'], capture_output=True)

    # --- get tuning key --- #
    notes_tuning = hex(sum([2**i*(i+1 in scale) for i in range(12)]))[2:]
    tuning_key = f"{int(tune_freqs)}{interval}-{notes_tuning}"

    # --- Writes the tuning parameters information file --- #
    args=[
        'Tuning Parameters:',
        '*'*20,
        f'Interval: {10*interval}ms (setting: {interval})',
        f'Scale: {num_scale_to_strs(scale) if tune_freqs else "NOT TUNED"}',
        f"Tune Frequencies: {tune_freqs}",
        f'Tuning Key: {tuning_key}'
        ]
    with open(f'{out_dir_filepath}/params.txt','w') as writer: writer.write('\n'.join(args))
    return out_dir_filepath