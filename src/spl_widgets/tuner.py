import tkinter as tk
from tkinter import filedialog, ttk
from spl_widgets.misc_util import *
from spl_widgets.tune_freq import tune_cols
from spl_widgets.util.gui_util import RadioFrame
from subprocess import run
from pathlib import Path

class TunerApp(tk.Tk):

    cb_values = [f"{n} Major Scale" for n in notes]
    cb_values_ext = [f"{notes[i]} {n}" for n in default_scales.keys() for i in range(len(notes))]

    fmts_to_tune: list[int] = None

    # KEY FORMAT:
    # (b == bit), (d == digit), (x == hex digit)
    # All formants tuned -> bdd-xxx
    # Specific formants tuned -> bdd-xxx-xx
    # https://docs.google.com/drawings/d/1bKiHvlINsine1As0t5_E4fHAkb7JKxIh1xgnzI03tgA/edit

    def validate_key(self, *args):
        key = self.key_var.get()
        new_key = key

        def is_hexadecimal(char: str):
            return (char.isdigit()) or (char.lower() in 'abcdef')

        invalid_key = any([
            len(key) > 10,
            (8<len(key)<11) and not ( is_hexadecimal(key[-1]) ),
            (len(key)==8)     and ( key[-1] != "-" ),
            (4<len(key)<8)  and not ( is_hexadecimal(key[-1]) ),
            (len(key) == 4)   and ( key[-1] != "-" ),
            (1<len(key)<4)  and not ( key[-1].isdigit() ),
            (len(key)==1)     and not ( key[0] in '01' )
        ])

        if invalid_key:
            new_key = key[:-1]
        self.key_var.set(new_key.upper())

    def process_tuning_key(self):

        if len(self.key_var.get())<7: return -1
        
        tuning_key = self.key_var.get()
        (tune_freqs, interval, scale_list, fmts_to_tune) = get_tuning_info( tuning_key )

        self.tune_freqs_var.set(tune_freqs)
        self.change_tune_freqs()

        self.interval_var.set(interval)
        self.fmts_to_tune = fmts_to_tune

        self.selector_radios_frame.radios[1].invoke()       # force switch tuning mode to notes

        for i,n in enumerate(self.note_vars):
            n.set(i+1 in scale_list)

    def limit_interval_len(self, *args):
        interval_in = self.interval_var.get()
        if len(interval_in)>2 or (len(interval_in)>0 and not interval_in[-1].isdigit()):
            self.interval_var.set(interval_in[:-1])

    def disable_scale_tuning(self):
        self.scale_combobox.configure(state="disabled")
        self.adv_scale_checkbox.configure(state="disabled")

    def disable_note_tuning(self):
        for note_checkbox in self.note_buttons:
            note_checkbox.configure(state="disabled")

    def enable_scale_tuning(self):
        self.scale_combobox.configure(state="readonly")
        self.adv_scale_checkbox.configure(state="normal")

    def enable_note_tuning(self):
        for note_checkbox in self.note_buttons:
            note_checkbox.configure(state="normal")

    def showsel(self, v: tk.IntVar):

        if v.get():
            self.disable_scale_tuning()
            self.enable_note_tuning()
        else:
            self.disable_note_tuning()
            self.enable_scale_tuning()

    def get_file(self):
        if self.file_type_var.get():
            file = filedialog.askdirectory(
                title="Select Parent Directory of Files to Tune: "
            )
            if file!="":
                self.file_name.configure(text=f"Directory: {file[file.rfind('/')+1:]}")
        else:
            file = filedialog.askopenfilename(
                title="Select File to Tune",
                filetypes=[("SWX Files","*.swx")]
                )
            if file != "":
                self.file_name.configure(text=f'File: {file[file.rfind("/")+1:]}')

        self.file_var.set(file)

    def change_file_type(self, v: tk.IntVar):
        if v.get():
            self.file_label.configure(text="Set Path to Tune: ")
            self.file_var.set("")
            self.file_name.configure(text="")
        else:
            self.file_label.configure(text="Set File to Tune: ")
            self.file_var.set("")
            self.file_name.configure(text="")

    def change_scales_shown(self):
        show_additional = self.show_scales_var.get()
        if show_additional:
            self.scale_combobox.config(values=self.cb_values_ext)
        else:
            self.scale_combobox.config(values=self.cb_values)
            if self.scale_var.get() not in self.cb_values:
                self.scale_var.set("C Major Scale")

    def change_tune_freqs(self):
        tune_freqs = self.tune_freqs_var.get()
        if tune_freqs: 
            self.selector_radios_frame.enable()
            if self.tune_type_var.get():
                self.enable_note_tuning()
            else:
                self.enable_scale_tuning()
        else:
            self.selector_radios_frame.disable()
            self.disable_note_tuning()
            self.disable_scale_tuning()

    def get_scale_vals(self) -> list[int]:
        tune_type = self.tune_type_var.get()        # 0: scale, 1: notes
        if tune_type == 0:
            scale_note, scale_type = self.scale_var.get().split(' ',maxsplit=1)
            return construct_default_scale(notes.index(scale_note)+1, scale_type)
        else:
            return [
                i+1 for i in range(12)
                if self.note_vars[i].get()
            ]

    def generate_tuning_key(self):
        tune_freqs = self.tune_freqs_var.get()
        interval = str(self.interval_var.get()).zfill(2)

        scale = self.get_scale_vals()
        scale_hex = encode_num_list_as_hex(scale)

        new_key = f"{tune_freqs}{interval}-{scale_hex}"
        self.key_var.set(new_key)

    def tune_with_data(self):
        filepath = self.file_var.get()
        interval_str = self.interval_var.get()
        interval = (int(interval_str) if interval_str else False)
        tune_freqs = self.tune_freqs_var.get()
        scale = self.get_scale_vals()

        can_proceed = (filepath and interval and (scale or not tune_freqs))
        if can_proceed:

            if self.file_type_var.get() == 0:   # 1: dir, 0: file
                outfilepath = tune_cols(
                    filepath,
                    interval,
                    scale,
                    bool(tune_freqs),
                    self.fmts_to_tune
                )
                run(['open', outfilepath], capture_output=True)

            else:
                files_in_dir = Path(filepath).glob("*.swx")
                for file in files_in_dir:
                    tune_cols(
                        str(file),
                        interval,
                        scale,
                        bool(tune_freqs),
                        self.fmts_to_tune
                    )
                run(['open', filepath], capture_output=True)

    def __init__(self):
        super().__init__()

        # Window config
        self.title("CTSF's SWX Tuner")
        self.geometry("460x330+50+50")
        self.resizable(False, False)
        self.config(padx=4, pady=5, background="darkgray")

        # CONFIG: Tracked variables setup

        self.interval_var = tk.StringVar()
        self.interval_var.trace('w',self.limit_interval_len)

        self.file_var = tk.StringVar()
        self.scale_var = tk.StringVar(value="C Major Scale")
        self.key_var = tk.StringVar()

        self.tune_type_var = tk.IntVar()
        self.show_scales_var = tk.IntVar()
        self.note_vars = [tk.IntVar() for _ in range(len(notes))]
        self.tune_freqs_var = tk.IntVar(value=1)


        # Top-level Frames for left and right sides

        # Frame for main options
        options_frame = tk.Frame(self,
            highlightbackground="black",
            highlightthickness="1",
        )
        
        # Frame for tuning method options (scales/notes)
        tuning_frame = tk.Frame(self,
            highlightbackground="black",
            highlightthickness=1
        )

        # Packing frames in this order so the options frame expands correctly
        tuning_frame.pack(
            side='right', anchor="n", fill="both",
            padx=1
        )
        options_frame.pack(
            side='left', anchor="n", fill="both",
            padx=1, expand=True
        )

        # File input

        # Frame for file input widgets
        file_input_frame = tk.Frame(
            options_frame,
            highlightbackground="black",
            highlightthickness=1,
            
        )
        file_input_frame.pack(
            side='top', anchor="w", fill="x",
            padx=2, pady=2
        )

        # RadioFrame for whether to tune a file or a directory
        file_radio_frame = RadioFrame(
            file_input_frame,
            options=['Single file', 'Directory'],
            label_text="Object to Tune:",
            orientation="h",
            onchange=self.change_file_type,
            pady=3
        )
        file_radio_frame.pack(side='top', anchor="w")
        self.file_type_var = file_radio_frame.variable  # get var from RadioFrame object and store locally

        # Frame for file input button
        file_button_frame = tk.Frame(file_input_frame)
        file_button_frame.pack(side='top', fill="x", expand=True)

        # Label for file input
        self.file_label = tk.Label(file_button_frame, text="Set File to Tune:")
        self.file_label.pack(side='left', anchor="w")

        # File input widget
        file_input_button = tk.Button(
            file_button_frame, text="Browse...", 
            command=self.get_file
        )
        file_input_button.pack(side='right', anchor="w")

        # Label for filename (updated when a new file/dir is selected)
        self.file_name = tk.Label(file_input_frame)
        self.file_name.pack(side='top', anchor="w", pady=3)


        # Interval input widget

        # Frame for interval input
        interval_frame = tk.Frame(
            options_frame,
            highlightbackground="black",
            highlightthickness=1
        )
        interval_frame.pack(
            side='top', anchor="w", fill="x",
            padx=2, pady=0
        )

        # Label for interval input
        interval_input_label = tk.Label(interval_frame, text="Tuning interval (x10ms): ")
        interval_input_label.pack(side='left',anchor="n", pady=2)

        # Interval input textbox
        interval_input = tk.Entry(interval_frame, width=2, textvariable=self.interval_var)
        interval_input.pack(side='left',anchor="n")


        # Tunetype settings input

        # Frame for selector
        selector_frame = tk.Frame(
            options_frame,
            highlightbackground="black",
            highlightthickness=1
        )
        selector_frame.pack(
            side='top', anchor="w", fill="x",
            padx=2, pady=2
        )

        # checkbutton for whether to tune the file at all
        tune_freqs_checkbox = tk.Checkbutton(
            selector_frame,
            text="Tune Frequencies",
            pady=10,
            command=self.change_tune_freqs,
            onvalue=1, offvalue=0,
            variable=self.tune_freqs_var
        )
        tune_freqs_checkbox.pack(anchor="w", side='top')

        # RadioFrame for whether to tune by scale or by notes
        self.selector_radios_frame = RadioFrame(
            selector_frame,
            options=["Scale", "Notes"],
            label_text="Tune File By:",
            onchange=self.showsel,
            pady=5
        )
        self.tune_type_var = self.selector_radios_frame.variable    # get var from RadioFrame object and store locally
        self.selector_radios_frame.pack(side="top", anchor="w")


        # Submit Button
        submit_frame = tk.Frame(
            options_frame,
            highlightbackground="black",
            highlightthickness=1
        )
        submit_frame.pack(
            side="left", anchor="center", fill="both", expand=True,
            padx=2, pady=2
        )
        submit_button = tk.Button(
            submit_frame,
            text="Tune File",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            command=self.tune_with_data
        )
        submit_button.pack( fill="both",expand=True )

        ##### RIGHT SIDE FRAME #####

        # Scale selection combobox widget

        # frame for scale selector
        scale_radio_frame = tk.Frame(
            tuning_frame,
            highlightbackground="black",
            highlightthickness=1
        )
        scale_radio_frame.pack(
            side="top", anchor="n", fill="x", 
            padx=2, pady=2
        )

        # Label for the scale selection combobox
        scaleRadioLabel = tk.Label(
            scale_radio_frame,
            text="Select scale to tune to: "
        )
        scaleRadioLabel.pack(anchor="w", padx=2)

        # Combobox scale selector
        self.scale_combobox = ttk.Combobox(
            scale_radio_frame,
            textvariable = self.scale_var,
            values=self.cb_values,
            state = "readonly"
        )
        self.scale_combobox.pack(anchor="w", padx=2)

        # Checkbutton for displaying/hiding additional scales
        self.adv_scale_checkbox = tk.Checkbutton(
            scale_radio_frame,
            command=self.change_scales_shown,
            text="Show additional scales",
            onvalue=1,offvalue=0,
            variable=self.show_scales_var
        )
        self.adv_scale_checkbox.pack(anchor="w", pady=2)


        # Note selection checkbuttons widget

        # Frame for note selection label and checkbuttons
        note_buttons_frame = tk.Frame(
            tuning_frame,
            highlightbackground="black",
            highlightthickness=1
        )
        note_buttons_frame.pack(
            anchor="sw", fill="x", expand=True,
            padx=2, pady=0, ipadx=10
        )

        # label for note checkbuttons
        note_buttons_label = tk.Label(
            note_buttons_frame,
            text="Select note(s) to tune to: "
        )
        note_buttons_label.pack(anchor="n")

        # Frame for note checkbuttons (Goes below label)
        bottom_notes_frame=tk.Frame(note_buttons_frame)
        bottom_notes_frame.pack(side='bottom')

        # left column frame for note checkbuttons
        notes_leftcol_frame = tk.Frame(
            bottom_notes_frame,
            borderwidth=3, padx=10
        )        
        notes_leftcol_frame.pack(side='left', anchor="w")

        # right column frame for note checkbuttons
        notes_rightcol_frame = tk.Frame(
            bottom_notes_frame,
            borderwidth=3, padx=10
        )
        notes_rightcol_frame.pack(side='right', anchor="w")

        # ugly list comprehension to generate note checkbuttons
        # (but it works and it'll never need to be changed)
        self.note_buttons = [
            tk.Checkbutton(
                master=(notes_leftcol_frame if i<6 else notes_rightcol_frame),  # half in the left column, half in the right (the ugliness)
                text=n,
                variable=self.note_vars[i],
                onvalue=1, offvalue=0,
                state="disabled"
            )
            for i,n in enumerate(notes)
        ]
        for n in self.note_buttons:         # packing the note buttons
            n.pack(anchor="w")


        # Tuning key Frame
        key_frame = tk.Frame(
            tuning_frame,
            highlightbackground="black",
            highlightthickness=1
        )
        key_frame.pack(
            side='top', anchor="w", fill="x", expand=True,
            ipady=3, pady=2, padx=2
        )

        # Frame for tuning key input widget
        key_input_frame = tk.Frame(key_frame)
        key_input_frame.pack(side="top")

        # key input label
        key_input_label = tk.Label(key_input_frame, text="Tune with key:")
        key_input_label.pack(side='left')

        # key input textbox
        key_input = tk.Entry(key_input_frame, width=9, textvariable=self.key_var)
        key_input.pack(side='left')

        # validate tuning key on edit of textbox content with event listener
        self.key_var.trace('w', self.validate_key)


        # frame for set/get key buttons
        key_buttons_frame = tk.Frame(key_frame)
        key_buttons_frame.pack(side="top", anchor="center")

        # button to generate parameters from current tuning key
        set_key_button = tk.Button(
            key_buttons_frame, text="Set Key",
            command=self.process_tuning_key
        )
        set_key_button.pack(side='left')

        # button to generate key from current params
        get_key_button = tk.Button(
            key_buttons_frame, text="Get Key",
            command=self.generate_tuning_key
        )
        get_key_button.pack(side="right")


def main():
    app = TunerApp()
    app.mainloop()

if __name__ == "__main__":
    main()