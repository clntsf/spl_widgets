import re                           # config and filename parsing
import pandas as pd                 # subject file parsing
from argparse import ArgumentParser # argparsing
from pathlib import Path            # filesystem I/O below
from subprocess import run
from tkinter import filedialog

# yeah maybe it's black magic but it's so convenient
subj_file_regex = r"(^data_exp_.+\-(\w{4})\-([0-9]+).xlsx$)"
cfg_regex = r"^(\w{4}) \"(.+)\" \[(.+)\]$"
cfg_cols_regex = r"\"(.+?)\"(?:, |$)"

cols_hcheck= ["Response", "ANSWER", "Correct","audio"]
cols_default = ["Response", "audio"]
cfg: dict[str, tuple[str,list[str]]] = {
    "awk4": ["Cooldown", cols_default],
    "l5it": ["Sentence Transcription", cols_default],
    "9bbq": ["Headphone Test", cols_hcheck]
}

# Help text at the top of cfg.txt
cfg_help="""
INSTRUCTIONS ON HOW TO FORMAT THIS FILE:
---------------------------------------

Each line should contain the following:
 - The name of the key to look for (ex. 9bbq). Should be four letters, look in the filename
 - The name of the task corresponding to this key in quotes (ex. "Headphone Test")
 - A list of columns to include in the cleaned .xlsx file for this task, in the format:
    ["col1", "col2", "col3"]

The following lines are the default configuration of the program
and can be used as examples of proper format

(To restore them in case of deletion, just delete this file and
run the program again, and a new file will be generated)

"""

cfg_path = __file__[:__file__.rfind("/")] + "/cfg.txt"

def write_default_cfg():

    path = cfg_path
    with open(path, "w") as writer:
        def_cfg = [[ k, n, '", "'.join(c) ] for (k,(n,c)) in cfg.items()]   # welcome to format hell
        def_cfg = [f'{k} "{n}" ["{c}"]' for (k,n,c) in def_cfg]
        def_cfg = "\n".join(def_cfg)

        writer.write(cfg_help+def_cfg)

def get_cfg():

    try:                                    # read cfg from file
        with open(cfg_path, "r") as reader:
            text = reader.read()
            lines = re.findall(cfg_regex, text, re.MULTILINE)
            return { k: [n, re.findall( cfg_cols_regex, c )] for (k,n,c) in lines }
    except FileNotFoundError:               # write default cfg to file & return it if file does not exist
        write_default_cfg()
        return cfg

def files_in_dir(dir: str):
    return run(["ls", dir], capture_output=True).stdout.decode("utf-8")

def get_subj_files_in_folder(folder: str):

    files = files_in_dir(folder)
    groups = re.findall(subj_file_regex, files, re.MULTILINE) # (fp, key)
    subj_id = groups[0][2]

    groups = [(f"{folder}/{filename}", key) for (filename, key, _id) in groups]
    return (subj_id, [*filter(lambda g: g[1] in cfg, groups)])

def process_subject_folder(folder: str|None = ...):
    if folder == ...:
        folder = filedialog.askdirectory()
        if folder == "": return False       # user bailed in filedialog

    def good_cell(c: str):
        return (
            isinstance(c,str) and c != ""
            and not any(
                c.startswith(x)
                for x in ["AUDIO", "BEGIN", "END"]
            )
        )

    (subj_id, groups) = get_subj_files_in_folder(folder)
    outfp = f"{folder}/{subj_id}_cleaned.xlsx"
    writer = pd.ExcelWriter(outfp, engine="xlsxwriter")

    for (fp, key) in groups:
        data = pd.read_excel(fp)
        (task_name, desired_cols) = cfg[key]

        data: pd.DataFrame = data.loc[map(good_cell, data["Response"]), desired_cols]
        data = data.dropna('index')
        data.to_excel(writer, sheet_name=task_name, index=False)

    writer.save()
    return folder

def make_argparser():
    parser_desc = "Cleans one (or a folder of) folder of subject files from Gorilla's testing service"
    parser = ArgumentParser(prog="gorilla_clean", description=parser_desc)

    parser.add_argument("-f", "--folder",
        action="store_const",
        const=True, default=False,
        help= "Process a batch of subject data folders instead of a single one"
    )

    parser.add_argument("-c", "--config",
        action="store_const",
        const=True, default=False,
        help="Open the program's config files in a text editor (will not run the main program)"
    )

    return parser

def main():
    global cfg

    parser = make_argparser()
    args = parser.parse_args()

    cfg = get_cfg()                     # load cfg if user has not selected -h

    if (args.config):                        # User has selected to open config
        run(["open", cfg_path])
        return True

    if (args.folder):                        # User has selected to batch clean
        folder = filedialog.askdirectory(title="Directory with batch of subject data folders")
        subfolders = files_in_dir(folder).splitlines()

        for fold in subfolders:
            fp = f"{folder}/{fold}"
            if Path(fp).is_dir():
                try:
                    process_subject_folder(fp)
                    print(f"Cleaned Subject data in folder '{fold}'")
                except Exception:
                    print(f"[WARN] Malformed subject data / other directory for Cleaner: {fold}")
        return True

    fold = process_subject_folder()     # Program is running in default single-clean mode
    print(f"Cleaned Subject data in folder '{fold}'")
    return True

if __name__ == "__main__":
    main()