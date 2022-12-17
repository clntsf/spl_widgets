from tkinter import filedialog
from argparse import ArgumentParser, HelpFormatter
from pathlib import Path
from random import shuffle
from subprocess import run

# shell class to represent the values of the Namespace returned by our argparser
# purely for transparency and convenience
class ParserArgs:
    silence: int
    rep_silence: int
    num_rpt: int
    end_silence: int

def make_parser():
    parser = ArgumentParser(
        prog="jukemake",
        description="Make a config file for a jukebox routine with all .wav files in a passed directory",
        formatter_class=lambda prog: HelpFormatter(prog, max_help_position=27)
    )

    # Arguments
    parser.add_argument( "-s", "--silence",
        type=int, default=3000, metavar="T",
        help="Duration of silence between file plays of the same sentence (ms). Default 3000"
    )
    parser.add_argument( "-r", "--rep-silence",
        type=int, default=4000, metavar="T",
        help="Duration of silence between plays of different sentences (ms). Default 4000"
    )
    parser.add_argument( "-e", "--end-silence",
        type=int, default=6000, metavar="T",
        help="Duration of silence at the end of the trial (ms). Default 6000"
    )
    parser.add_argument( "-n", "--num-rpt",
        type=int, default=3, metavar="N",
        help="Number of times to repeat each file. Default 3"
    )

    return parser

def get_wav_in_dir(dir: Path) -> list[str]:
    return [wf.name for wf in dir.glob("*.wav")]

def format_to_file(files: list[str], pauses: list[int], outfp: str|Path):
    lines = [f"{fn}\t{s}\n" for (fn,s) in zip(files,pauses)]
    with open(outfp, "w") as writer:
        writer.writelines(lines)

def main():

    parser = make_parser()
    args: ParserArgs = parser.parse_args()

    files_dir = filedialog.askdirectory( title="Directory with .wav files" )
    files = get_wav_in_dir(Path(files_dir))

    shuffle(files)

    file_order = [wfn for wfn in files for _ in range(args.num_rpt)]

    num_plays = len(files)*args.num_rpt
    silence_durs = [args.silence]*(num_plays)
    silence_durs[-1] = args.end_silence

    if (args.num_rpt > 1) and (args.rep_silence != args.silence):
        for idx in range(args.num_rpt-1, num_plays-1, args.num_rpt):
            silence_durs[idx] = args.rep_silence

    outpath = Path(files_dir, "jukebox_cfg.txt")
    format_to_file( file_order, silence_durs, outpath ) # output file
    run(["open", outpath])

if __name__ == "__main__":
    main()