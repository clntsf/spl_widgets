from argparse import ArgumentParser, RawTextHelpFormatter
from sys import argv
from spl_widgets import tuner, stk_swx, widgets_help, update_widgets, gorilla_clean

parser_desc = "Run one of the python modules created by CTSF for the Barnard Speech Perception Laboratory"
arg_help = "(Positional) The module to run. Options: \
    \n\t- tuner \n\t- stk_swx \n\t- gorilla_clean \n\t- widgets_help \n\t- update_widgets"

mods={
    "tuner": tuner,
    "stk_swx": stk_swx,
    "widgets_help": widgets_help,
    "update_widgets": update_widgets,
    "gorilla_clean": gorilla_clean
}

parser = ArgumentParser(
    "runmod",
    description=parser_desc,
    formatter_class=RawTextHelpFormatter
)
parser.add_argument("mod", metavar="M", help=arg_help)

args = parser.parse_args(argv[1:2])
cmd = args.mod

# Programmatically import and run the desired module, instead of importing everything
try:
    mods[cmd].main(*argv[2:])
except ModuleNotFoundError:
    print("Bad command: " + repr(cmd))