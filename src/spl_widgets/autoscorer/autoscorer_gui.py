import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinterdnd2 import TkinterDnD

from pathlib import Path
from subprocess import run
import re
import pandas as pd

import pkg_resources
import json

from spl_widgets.util.gui_util import RadioFrame, MarginListBox, HelpLinkLabel, HelpTextParser, NOTEBOOK_TAB_WIDTH
from spl_widgets.autoscorer import autoscore

HL = "*"*29

class AutoscorerGUI:
    scoring_mode_radios: RadioFrame
    input_data_listbox: MarginListBox
    ideal_ipa_listbox: MarginListBox
    output_data_listbox: MarginListBox

    def __init__(self, master: tk.Tk):
        self.master = master

        self.make_help_window()
        self.hide_help()
    
        self.make_data_input_frame()
        self.make_options_frame()
        self.make_output_frame()

    @staticmethod
    def show_error_popup(msg: str):
        messagebox.showerror(
            title = "[ERROR] - Autoscorer",
            message = msg
        )

    @staticmethod
    def validate_df(fn: str, subject_df: pd.DataFrame, compare_to: pd.DataFrame):

            if "Target" not in subject_df.columns:
                print(f"[ERROR-INFO] did not find column 'Target' in file '{fn}'")
                AutoscorerGUI.show_error_popup(
                    "[ERROR]: Malformed input file: Must contain column 'Target' (see terminal for details)"
                )
                return False

            subject_df.sort_values(by=["Target"], inplace=True, ignore_index = True)

            # validating df lengths
            if (l1:=len(compare_to.index)) != (l2:=len(subject_df.index)):
                print(f"[ERROR-INFO]: Conflict in file row lengths: found {l1} and {l2}")
                AutoscorerGUI.show_error_popup(
                    "[ERROR]: All subject files must have the same number of sentences (see terminal for details)"
                )
                return False

            # ensuring target sentences match in both dfs
            if not all((t1:=compare_to["Target"]) == (t2:=subject_df["Target"])):
                print(f"[ERROR-INFO]: Conflict in file sentences: found \n\t{t1} and \n\t{t2}")
                AutoscorerGUI.show_error_popup(
                    "[ERROR]: All subject files must have the same list of target sentences (see terminal for details)"
                )
                return False

            return True

    def get_ideal_ipas(self, subject_df: pd.DataFrame, ideal_ipa_path: tuple[str, Path] = ...) -> tuple[str, list[str]]:
        scoring_mode = "preferred-transcription"
        ideal_ipas = ...
            
        if ideal_ipa_path is not ...:
            (fn, fp) = ideal_ipa_path
            ideal_ipas_df = pd.read_excel(fp, header=0)
            ideal_ipas_df.columns = ["Target", "IPA"]

            if self.validate_df("IDEAL IPA FILE: "+fn, ideal_ipas_df, subject_df):
                scoring_mode = "best-match"
                ideal_ipas = ideal_ipas_df["IPA"]
        
        return (scoring_mode, ideal_ipas)

    def process_output_combined(self, input_files: dict[str, Path], ideal_ipa_path: tuple[str, Path] = ...):
        df = None
        for (fn, fp) in input_files:
            subject_df = pd.read_excel(fp, header=0)

            if df is None:
                subject_df.sort_values(by=["Target"], inplace=True, ignore_index = True)
                df = subject_df
                continue

            if self.validate_df(fn, subject_df, df) == False:
                return

            subj_header = subject_df.columns[1]
            subj_transcriptions = subject_df[subj_header]
            df[subj_header] = subj_transcriptions

        (scoring_mode, ideal_ipas) = self.get_ideal_ipas(df, ideal_ipa_path)

        outpath = Path(filedialog.asksaveasfilename(
            filetypes = [("Excel Files", "*.xlsx")],
            title = "Save Autoscorer Output to File"
        ))
        if outpath == "":
            self.show_error_popup("[EXIT]: User bailed while saving autoscored file")
            return False

        out_dir = outpath.parent
        out_fn = outpath.stem

        autoscore.main( df, out_dir, out_fn, ideal_ipas, scoring_mode )

        self.output_data_listbox.add_item(outpath)
        self.output_data_listbox.insert(tk.END, HL) # horizontal line separating output batches

    def process_output_separate(self, input_files: list[tuple[str, Path]]):

        frames = []
        for (fn, fp) in input_files:
            subject_df = pd.read_excel(fp, header=0)

            if frames == []:
                subject_df.sort_values(by=["Target"], inplace=True, ignore_index = True)
                frames.append((fp.stem, subject_df))
                continue
 
            if self.validate_df(fn, subject_df, frames[0][1]) == False:
                return

            frames.append((fp.stem, subject_df))

        if self.ideal_ipa_listbox.size() == 0:
            ideal_ipas = ...

        output_dir = filedialog.askdirectory(
            title="Directory to save output files in"
        )
        if output_dir == "":
            self.show_error_popup("[EXIT]: User bailed while selecting output directory for autoscored files")
            return False
        
        for (fn, df) in frames:
            out_fn = f"{fn}_autoscored"
            autoscore.main(df, output_dir, out_fn, ideal_ipas)

            outfp = Path(output_dir, out_fn+".xlsx")
            self.output_data_listbox.add_item(outfp)

        self.output_data_listbox.insert(tk.END, HL)

    def autoscore_with_data(self):

        if self.ideal_ipa_listbox.size() > 0:
            ideal_ipa_path = [*self.ideal_ipa_listbox.data_items.items()][0]
            
        else:
            ideal_ipa_path = ...

        # validate data
        if self.input_data_listbox.size() == 0:
            return self.show_error_popup("[ERROR]: No input files received")

        input_files = [*self.input_data_listbox.data_items.items()]
        combine_output = self.combine_output.get()

        if combine_output:
            self.process_output_combined(input_files, ideal_ipa_path)
        else:
            self.process_output_separate(input_files, ideal_ipa_path)

    def make_help_window(self):
        self.help_window = tk.Toplevel(self.master)
        self.help_window.resizable(False,True)
        self.help_window.title("Autoscorer GUI Help Menu")

        help_text_fp = pkg_resources.resource_filename("spl_widgets", "data/help_text.json")
        with open(help_text_fp, "r") as reader:
            help_text_json = json.load(reader)

        self.help_app = AutoscorerHelpWindow(self.help_window, help_text_json)

    def update_scoring_mode_radios(self):
        if self.ideal_ipa_listbox.size() == 1:
            self.scoring_mode_radios.radios[0].configure(state="normal")
        else:
            self.scoring_mode_radios.radios[0].configure(state="disabled")
            self.scoring_mode_radios.variable.set(1)

    def make_data_input_frame(self):

        # Subject data file(s) entry
        data_input_frame = tk.Frame(
            self.master, padx=5, pady=5,
            highlightbackground="black",
            highlightthickness=1
        )
        data_input_frame.pack(
            padx=(6,3), pady=5, side="left", anchor="nw",
            fill="y", expand=True
        )

        # utility functions for the drag-and-drop boxes
        def add_subject_data_file(listbox: tk.Listbox, data: dict, e) -> None:
            
            FILENAME_RE = r"({.+?}|[\S]+)"
            filepaths = re.findall(FILENAME_RE, e.data)
            filepaths = [Path(re.sub(r"[\{\}]", "", fp)) for fp in filepaths]

            def try_add_file(f: Path):
                if f.suffix != ".xlsx":
                    print(f"[WARNING]: Only files of type .xlsx allowed, received type '{f.suffix}'")
                    return
    
                name = f.name
                if name not in data:
                    data[name] = f
                    listbox.insert(tk.END, name)

            for path in filepaths:
                if path.is_dir():
                    for xlsx_filepath in path.glob("*.xlsx"):
                        try_add_file(xlsx_filepath)
                else:
                    try_add_file(path)
        def remove_subject_data_file(listbox: tk.Listbox, data) -> None:
            delete_item = (listbox.curselection() or tk.END)

            item_name = listbox.get(delete_item)
            if item_name in data:
                data.pop(item_name)

            listbox.delete(delete_item)

        def add_ideal_ipa_file(listbox: tk.Listbox, data: dict, e) -> None:
            f = Path(re.sub(r"[{}]", "", e.data))
            if f.suffix != ".xlsx":
                print(f"[WARNING]: Only files of type .xlsx allowed, received type '{f.suffix}'")
                return
    
            name = f.name
            remove_ideal_ipa_file(listbox, data)
            data[name] = f
            listbox.insert(0,name)
            self.update_scoring_mode_radios()
        def remove_ideal_ipa_file(listbox: tk.Listbox, data: dict) -> None:
            data.clear()
            listbox.delete(0)
            self.update_scoring_mode_radios()

        input_data_label = HelpLinkLabel(
            data_input_frame, tab_name="File Input",
            onclick=self.focus_help_tab,
            text="Subject Data File(s) (Drag/Drop)"
        )
        input_data_label.pack_frame( pady=(0,5) )

        self.input_data_listbox = MarginListBox(
            data_input_frame,
            add_subject_data_file,
            remove_subject_data_file,
            height=8, width=22
        )
        self.input_data_listbox.pack_frame(side="top")

        ideal_ipa_label = HelpLinkLabel(
            data_input_frame, tab_name="File Input",
            onclick=self.focus_help_tab,
            text="(Optional) Ideal IPA File (Drag/Drop)"
        )
        ideal_ipa_label.pack_frame(pady=(5,0))

        self.ideal_ipa_listbox = MarginListBox(
            data_input_frame, 
            add_ideal_ipa_file,
            remove_ideal_ipa_file,
            pack_args = {"side": "left", "padx": (5,1)},
            height=1, width=18
        )
        self.ideal_ipa_listbox.pack_frame(side="top")

    def make_options_frame(self):
        # Autoscorer Options Frame

        options_frame = tk.Frame(
            self.master, padx=5, pady=5,
            highlightbackground="black",
            highlightthickness=1
        )
        options_frame.pack(
            padx=(3,6), pady=5, side="left", anchor="nw",
            fill="y", expand=True
        )

        options_label = tk.Label(
            options_frame, text="Autoscorer Options"
        )
        options_label.pack( pady=(0,5), anchor="center" )

        self.combine_output = tk.BooleanVar(value=True)
        combine_output_checkbox = tk.Checkbutton(
            options_frame,
            text = "Combine output into a single file",
            variable=self.combine_output,
            onvalue = True, offvalue = False,
        )
        combine_output_checkbox.pack(side="top", padx = 5, pady=(0,3))

        self.scoring_mode_radios = RadioFrame(
            options_frame,
            options = ["Best-Match Transcription", "Preferred Transcription"],
            label_text = "Autoscorer Scoring Mode"
        )
        self.scoring_mode_radios.pack(side="top", anchor="w", padx=5, pady=3)

        # disable the "Best-match" scoring as ideal ipa is empty
        self.update_scoring_mode_radios()

        # replace the stock RadioFrame label with one containing a help link
        newlabel = HelpLinkLabel(
            self.scoring_mode_radios, tab_name="Scoring Mode Options",
            onclick=self.focus_help_tab,
            text="Autoscorer Scoring Mode"
        )
        self.scoring_mode_radios.label.pack_forget()
        newlabel.pack_frame(side="top", anchor="w")


        help_button = tk.Button(
            options_frame,
            text="Show Help Menu",
            command=self.show_help
        )
        help_button.pack(side="top", padx=5, pady=3)

        self.autoscore_button = tk.Button(
            options_frame,
            text = "Autoscore Input",
            command = self.autoscore_with_data
        )
        self.autoscore_button.pack(side="bottom", padx=5, pady=3)

    def make_output_frame(self):
        output_frame= tk.Frame(
            self.master, padx=5, pady=5,
            highlightbackground="black",
            highlightthickness=1
        )
        output_frame.pack(
            padx=(3,6), pady=5, side="left", anchor="nw",
            fill="y", expand=True
        )
        
        output_data_label = HelpLinkLabel(
            output_frame, tab_name="File Output",
            onclick=self.focus_help_tab,
            text="Autoscored Output File(s)"
        )
        output_data_label.pack_frame(pady=(0,5))

        def add_output_file(listbox: MarginListBox, data: dict, filepath: Path):
            fn = filepath.name
            fn2 = f"{filepath.stem}_PER_SEGMENT.xlsx"

            listbox.insert(tk.END, fn)
            listbox.insert(tk.END, fn2)
            data[fn] = filepath
            data[fn2] = Path(filepath.parent, fn2)

        self.output_data_listbox = MarginListBox(
            output_frame,
            add_output_file,
            None,
            include_minus_button=False,
            pack_args={"expand": True},
            height=10, width=20
        )
        self.output_data_listbox.pack_frame(
            side="top", fill="y", expand=True
        )

        def defocus_hl(listbox: MarginListBox):

            if (curselected:=listbox.curselection()) == (): # nothing selected
                return

            if listbox.get(curselected) == HL:
                listbox.selection_clear(0, tk.END)

        self.output_data_listbox.bind(
            "<<ListboxSelect>>",
            lambda x: defocus_hl(x.widget)
        )

        self.output_data_listbox.bind(                   # bind double-clicking on a listbox item to open that file
            "<Double-1>",
            lambda x: self.open_file(x.widget)
        )

    def show_help(self):
        try:
            self.help_window.deiconify()
        except tk.TclError:
            self.make_help_window()
            return self.show_help()

        # set the heights of the scrollbars - done here because the window must be loaded for it to work,
        # and it isn't time consuming so it's not an issue if it runs each time the window opens
        self.help_app.set_scroll_heights()

    def hide_help(self):
        self.help_window.withdraw()

    def open_file(self, listbox: MarginListBox):
        selected = listbox.curselection()
        for idx in selected:
            fn = listbox.get(idx)
            fp = listbox.data_items.get(fn)

            if fp is not None: run(["open", fp])

    def focus_help_tab(self, tab_name: str):
        self.show_help()

        nb = self.help_app.help_notebook
        tab_names = [nb.tab(i, option="text") for i in nb.tabs()]

        tab_idx = tab_names.index(tab_name)
        nb.select(tab_idx)

class AutoscorerHelpWindow:
    def __init__(self, master: tk.Toplevel, text: dict):
        self.master = master
        self.text = text

        help_main_frame = tk.Frame(self.master)
        help_main_frame.pack(fill="both", expand=True, pady=10)

        self.help_notebook = ttk.Notebook(
            help_main_frame, width=NOTEBOOK_TAB_WIDTH+20, height=250, padding=0
        )
        self.help_notebook.pack(side="top", fill="both", expand=True)

        # this is an unbelievably ridiculous hack brought on by the idiocy of MacOS somehow
        # refusing to work properly with tkinter. When a notebook tab is switched, tkinter
        # refuses to draw the contents of the tab until the mouse is moved (or, less reliably,
        # another mouse click occurs). As such, we wait 20ms and simulate a mouse move event
        # whenever we switch tabs, because we just can't have nice things
        def force_refresh(evt: tk.Event):
            sim_event= lambda: self.help_notebook.event_generate("<Motion>", x=100, y=100)
            self.master.after(20, sim_event)

        self.help_notebook.bind("<<NotebookTabChanged>>", force_refresh)

        # File input help tab
        notebook_tab_FILE_INPUT = tk.Frame(
            help_main_frame,
            highlightbackground="black",
            highlightthickness=1
        )
        notebook_tab_FILE_INPUT.pack(fill="both", expand=True)
        self.input_help = HelpTextParser(notebook_tab_FILE_INPUT, text["input-help"])
        self.input_help.pack(side="left", anchor="nw", fill="both", expand=True)

        # Scoring mode help tab
        notebook_tab_SCORING_MODE = tk.Frame(
            help_main_frame,
            highlightbackground="black",
            highlightthickness=1
        )
        notebook_tab_SCORING_MODE.pack(fill="both", expand=True)
        self.scoring_help = HelpTextParser(notebook_tab_SCORING_MODE, text["scoring-mode-help"])
        self.scoring_help.pack(side="top", anchor="nw", fill="both", expand=True)

        # File output help tab
        notebook_tab_FILE_OUTPUT = tk.Frame(
            help_main_frame,
            highlightbackground="black",
            highlightthickness=1
        )
        notebook_tab_FILE_OUTPUT.pack(fill="both", expand=True)
        self.output_help = HelpTextParser(notebook_tab_FILE_OUTPUT, text["output-help"])
        self.output_help.pack(side="top", anchor="nw", fill="both", expand=True)
        
        # Add the tabs to the notebook
        self.help_notebook.add(notebook_tab_FILE_INPUT, text="File Input", sticky="nsew")
        self.help_notebook.add(notebook_tab_SCORING_MODE, text="Scoring Mode Options", sticky="nsew")
        self.help_notebook.add(notebook_tab_FILE_OUTPUT, text="File Output", sticky="nsew")

        # Add the quit button
        help_quitbutton = tk.Button(
            help_main_frame,
            text="Hide this window",
            command=self.master.withdraw
        )
        help_quitbutton.pack(
            side="bottom", anchor="se", pady=0, padx=5
        )

    # set the scroll region of the tabs in the notebook. Can only be run once the help window is loaded
    def set_scroll_heights(self):
        
        for tab_content in [self.input_help, self.scoring_help, self.output_help]:
            width = tab_content.content.winfo_width()
            height = tab_content.content.winfo_height()
            
            tab_content.canvas.configure(scrollregion=(0,0,width,height))

# for use in the output side

def main():
    root = TkinterDnD.Tk()
    root.title("Autoscorer GUI")
    root.resizable(False, False)

    app = AutoscorerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()