import pandas as pd
from io import StringIO
from tkinter import filedialog
from argparse import ArgumentParser
from subprocess import run
from pathlib import Path
from spl_widgets.misc_util import df_to_tsv, MalformedFileError

def parse_df(df: pd.DataFrame) -> "tuple[int, pd.DataFrame]":   # Returns the desired columns (active formant freq and amp) from an inputted pd.DataFrame

    df["f0"] = [n*10 for n in range(len(df.index))]
    for fmt in range(4,7):                                      # adds only the formants that are active (changing)

        amp_col = df[f"a{fmt}f"]
        for amp_val in amp_col:
            if amp_val != 30:                           # Check for non-baseline amplitude indicating active formant
                break

        else:
            cols = ["f0"]
            for x in range(1,fmt): cols.extend([f"f{x}",f"a{x}f"])
            return fmt-1, df[cols]

def stk_to_swx(filepath):
    multipliers = [.7,.4,.2,.1,0.5]

    # --- Read .stk file, and take the info to a dataframe --- #
    with open(filepath, 'r') as reader:
        file_content = ''.join(reader.readlines()[8:])
        
    try:
        (formants, df) = parse_df( pd.read_csv(StringIO(file_content), sep='\t') )
    except Exception:
        raise MalformedFileError(f"File @ {filepath} is malformed and does not conform to generic .stk format")

    amp_cols = [f"a{f+1}f" for f in range(formants)]            # get amp col headers and number of formants

    # --- Correct amplitude vals --- #
    amp_max = [max(df[col]) for col in amp_cols]
    for i in range(formants):
        def scalemult(cell):
            if cell<=30: return 0
            return round(multipliers[i] * (amp_max[i] / cell), 4)
    
        colnm = amp_cols[i]
        col = df[colnm]
        df[colnm] = list(map(scalemult, col))

    # --- Prettifying and output --- #
    df.columns = [formants]+['']*(formants*2)
    out_fp = filepath[:-4]

    tsv = df_to_tsv(df)
    with open(f"{out_fp}.swx", "w") as writer:
        writer.write(tsv)

    return f"{out_fp}.swx"

def make_parser():
    parser = ArgumentParser(prog="stk_swx")
    parser.add_argument("-f", "--folder",
        action="store_const",
        const=True, default=False,
        help="Convert a folder of .stk files, as opposed to a single file"
    )
    return parser

def main():
    # --- Get filepath to .stk file --- #

    parser = make_parser()
    args = parser.parse_args()

    USER_BAIL_MSG = "[EXIT] User bailed during selection of target directory"

    if args.folder:
        out_fp = filepath = filedialog.askdirectory()
        if filepath == '':    # user bailed in filedialog
            print(USER_BAIL_MSG)
            return False

        operable_files = map(str, Path(filepath).glob("*.stk"))        # gets and parses terminal ls output into list of files in directory                            # gets files with .stk extension

        for file in operable_files:
            stk_to_swx(file)
            print(f"File {file} has been converted")

        print("\nCompatible files have been successfully converted")

    else:
        filepath=filedialog.askopenfilename(filetypes=[('',".stk")])
        if filepath == '':            # user bailed during filedialog
            print(USER_BAIL_MSG)
            return False

        out_fp = stk_to_swx(filepath)
        print('\n'+f"File written to {out_fp}")

    # --- Display completion message, open .swx file/dir if user chooses --- #
    if input("Open Output? (y/n): ").lower() == 'y':
        run(["open", out_fp])

if __name__ == "__main__":
    main()