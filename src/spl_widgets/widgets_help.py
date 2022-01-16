widget_desc={
    "stk-swx":"Usage: stk-swx [folder]\n\nConverts a desired file of type .stk to a MATLAB-ready .swx file.\n\nIf the optional flag 'folder' is used does the same to each .stk file in a user-specified directory.",
    "gorilla_clean":"Usage: gorilla_clean[folder]\n\nParses a selected folder of subject data returned by gorilla's survey tool into a cleaner .xlsx file with readable results.\n\nIf the optional flag 'folder' is used does the same to every subject data folder in a user-specified directory.",
    "tuner":"Usage: tuner \n\nTakes no flags. GUI program to allow for musical frequency forcing of SWX files with documentation of the parameters used.",
    "update_widgets":"Usage: update_widgets\n\nTakes no flags. Brings the package up-to-date, ensuring all widgets are downloaded in their most recent-versions and properly aliased.",
    "widgets_help":"Usage: widgets_help\n\nTakes no flags. Calls this function, printing messages detailing the use and syntax of each widget/function in this package."
}

menustr = "HELP MENU: CTSF's PYTHON WIDGETS"

def main():
    print(f"{menustr}\n{'*'*len(menustr)}\n")
    for k,v in widget_desc.items():
        print(f"{k}:\n{'*'*(len(k)+1)}\n{v}\n")