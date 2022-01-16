from sys import argv
from spl_widgets import update_widgets, gorilla_clean, stk_swx, widgets_help, tuner

modules_to_alias={
    "update_widgets": update_widgets,
    "widgets_help": widgets_help,
    "gorilla_clean": gorilla_clean,
    "stk_swx": stk_swx,
    "tuner": tuner
}

cmd = argv[1]
if cmd in modules_to_alias.keys(): modules_to_alias[cmd].main()
else: print(f"Bad command ({cmd})")