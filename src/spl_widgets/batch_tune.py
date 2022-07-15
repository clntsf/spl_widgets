from argparse import ArgumentParser, RawTextHelpFormatter
from textwrap import dedent
from pathlib import Path
from sys import exit
from tkinter import filedialog
from subprocess import run
import re
from spl_widgets.misc_util import get_scale
from spl_widgets.tune_freq import tune_cols

KEY_REGEX = r"^([01][0-9]{2}-[0-9A-Fa-f]{3})$"

def get_file(*args, **kwargs):
    params_file = filedialog.askopenfilename(*args, **kwargs)
    if params_file is None:                                     # user bailed in filedialog
        print("User bailed in filedialog")
        exit(1)

    return params_file

def make_parser():
    parser_desc = "A companion script to tuner, tunes a passed .swx file with each tuning key in a passed params file."
    parser = ArgumentParser(prog="batch_tune",
        description=parser_desc,
        formatter_class=RawTextHelpFormatter
    )

    params_fp_help = dedent("""\
        Path to a file containing a list of tuning keys to tune the inputted .swx file with.
        If not provided, will prompt the user to pass the file with a file dialog.\
    """)
    parser.add_argument(
        "params_fp", metavar="P",type=str, nargs = "?",
        help=params_fp_help
    )

    swx_fp_help = dedent("""\
        Path to a .swx file to tune with keys in the passed params file.
        If not provided, will prompt the user to pass the file with a file dialog.\
    """)
    parser.add_argument(
        "swx_fp", metavar="S", type=str, nargs="?",
        help=swx_fp_help
    )
    
    return parser

def main():
    parser = make_parser()
    args = parser.parse_args()

    if (params_fp:=args.params_fp) is None:                 # get params file if not in args
        params_fp = get_file(
            filetypes=[("Text Files", "*.txt")],
            title="Parameter file containing tuning keys"
        )
    if (swx_fp:=args.swx_fp) is None:                       # get .swx file if not in args
        swx_fp = get_file(
            filetypes=[("SWX Files", "*.swx")],
            title="SWX File to tune with keys"
        )

    if not Path(swx_fp).is_file():                          # bad swx filepath, bail
        raise ValueError(f"[Error] invalid filepath to .swx file: {swx_fp}")

    try:                                                    # get text from params file
        text = Path(params_fp).read_text()
    except Exception:                               # bad params filepath, bail
        print(Exception.args)
        raise ValueError(f"Invalid path to parameter file: {params_fp}")

    keys = re.findall(KEY_REGEX, text, re.MULTILINE)        # get keys from params file text

    successful=False    # whether the program has successfully done any tunings
    for k in keys:      # tune with each key
        try:                                                # get tuning params from key
            tune_freqs, interval, scale_list = get_scale(k)
            tune_freqs = bool(tune_freqs)
            successful = True
        except Exception:                                   # bad key, skip tune
            print(f"[Warning]: Invalid tuning key: {k}")
            continue
        
        print(f"[DEBUG]: Tuning with key '{k}':")
        print(f" - {tune_freqs = } \n - {interval = } \n - {scale_list = } \n")

        tune_cols(swx_fp, interval, scale_list, tune_freqs) # tune with key

    if not successful:                                  # no keys worked, bail
        print("[Error]: No keys successfully produced a tuned file!")
        return False

    outdir = Path(swx_fp).parent                        # open output dir with tuned files
    run(["open", outdir])

if __name__ == "__main__":
    main()