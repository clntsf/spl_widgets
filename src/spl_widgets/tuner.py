from tkinter import *
from tkinter import filedialog, ttk
from spl_widgets.misc_util import *
from spl_widgets.tune_freq import tune_cols
from subprocess import run
from pathlib import Path

class RadioFrame(Frame):

    def __init__(self, parent: Frame, options: "list[str]", label: str, onchange: "function", orientation="v") -> Frame:
        Frame.__init__(self, parent)

        self.parent = parent
        self.variable = IntVar()
        self.onchange = lambda: onchange(self.variable) if onchange else None

        packside = "top" if orientation == "v" else "left"
        anchorside = W if orientation == "v" else N

        self.label = Label(self,text=label)
        self.label.pack(side="top", anchor=W)

        self.radios = [Radiobutton(self,text=o, variable=self.variable, value=i, command=self.onchange) for i,o in enumerate(options)]
        for b in self.radios: b.pack(side=packside, anchor=anchorside)

    def disable(self):
        for b in self.radios:
            b.configure(state="disabled")

    def enable(self):
        for b in self.radios:
            b.configure(state="normal")

class TunerApp(Tk):

    cb_values = [f"{n} Major Scale" for n in notes]
    cb_values_ext = [f"{notes[i]} {n}" for n in default_scales.keys() for i in range(len(notes))]

    fmts_to_tune: list[int] = None

    # KEY FORMAT:
    # b - bit, d - digit, x - hex digit
    # All formants tuned -> bdd-xxx
    # Specific formants tuned -> bdd-xxx-xx

    def validate_key(self, *args):
        key = self.key_var.get()
        new_key = key

        def is_hexadecimal(char: str):
            return (char.isdigit()) or (char.lower() in 'abcdef')

        invalid_key = any([
            len(key) > 10,
            (9<=len(key)<=10) and not ( is_hexadecimal(key[-1]) ),
            (len(key)==8)     and ( key[-1] != "-" ),
            (5<=len(key)<=7)  and not ( is_hexadecimal(key[-1]) ),
            (len(key) == 4)   and ( key[-1] != "-" ),
            (2<=len(key)<=3)  and not ( key[-1].isdigit() ),
            (len(key)==1)     and not ( key[0] in '01' )
        ])

        if invalid_key:
            new_key = key[:-1]
        self.key_var.set(new_key.upper())

    def get_key(self):
        key = self.key_var.get()
        return get_scale(key)

    def process_tuning_key(self):

        if len(self.key_var.get())<7: return -1
        
        (tune_freqs, interval, scale_list, fmts_to_tune) = self.get_key()

        self.tune_freqs_var.set(tune_freqs)
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

    def showsel(self, v: IntVar):

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

    def change_file_type(self, v: IntVar):
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

    def get_scale_vals(self):
        tune_type = self.tune_type_var.get()        # 0: scale, 1: notes
        if tune_type == 0:
            scale_note, scale_type = self.scale_var.get().split(' ',maxsplit=1)
            return construct_default_scale(notes.index(scale_note)+1, scale_type)
        else:
            return [
                i+1 for i in range(12)
                if self.note_vars[i].get()
            ]

    def make_scale(self):
        tune_freqs = self.tune_freqs_var.get()
        interval = str(self.interval_var.get()).zfill(2)

        scale = self.get_scale_vals()
        keys = "".join("1"  if k in scale else "0" for k in range(12,0,-1))
        scale_hex = hex(int(keys, base=2))[2:].upper()

        new_key = f"{tune_freqs}{interval}-{scale_hex}"
        self.key_var.set(new_key)

    def tune_with_data(self):
        filepath = self.file_var.get()
        interval = int(self.interval_var.get())
        tune_freqs = self.tune_freqs_var.get()
        scale = self.get_scale_vals()

        can_proceed = (filepath and interval and (scale or not tune_freqs))
        if can_proceed:
            if self.file_type_var.get() == 0:   # 1: dir, 0: file
                outfilepath = tune_cols(filepath, interval, scale, bool(tune_freqs), self.fmts_to_tune)
                run(['open', outfilepath], capture_output=True)
            else:
                files_in_dir = Path(filepath).glob("*.swx")
                for f in files_in_dir:
                    tune_cols(str(f), interval, scale, bool(tune_freqs), self.fmts_to_tune)
                run(['open', filepath], capture_output=True)

    def __init__(self):
        super().__init__()

        self.title("CTSF's SWX Tuner")
        self.geometry("470x330+50+50")
        self.resizable(False, False)

        self.interval_var = StringVar()
        self.interval_var.trace('w',self.limit_interval_len)

        self.file_var = StringVar()
        self.scale_var = StringVar(value="C Major Scale")
        self.key_var = StringVar()

        self.tune_type_var = IntVar()
        self.show_scales_var = IntVar()
        self.note_vars = [IntVar() for _ in range(len(notes))]
        self.tune_freqs_var = IntVar(value=1)

        options_frame = Frame(self, borderwidth=10)
        options_frame.pack(side='left', anchor=N)

        tuning_frame = Frame(self, pady=5)
        tuning_frame.pack(side='right', anchor=N)


        # File Input
        file_frame = Frame(options_frame, borderwidth=5)
        file_frame.pack(side='top', anchor=W)

        file_radio_frame = RadioFrame(
            file_frame, options=['Single file', 'Directory'],
            label="Object to Tune:", orientation="h",
            onchange=self.change_file_type
        )
        file_radio_frame.configure(borderwidth=3)
        file_radio_frame.pack(side='top', anchor=W)
        self.file_type_var = file_radio_frame.variable

        file_input_frame = Frame(file_frame)
        file_input_frame.pack(side='top')

        self.file_label = Label(file_input_frame, text="Set File to Tune:")
        self.file_label.pack(side='left', anchor=W)

        file_input = Button(
            file_input_frame, text="Browse...", 
            command=self.get_file
        )
        file_input.pack(side='left', anchor=W)

        self.file_name = Label(file_frame)
        self.file_name.pack(side='top', anchor=W)


        # Interval Input
        interval_frame = Frame(options_frame, borderwidth=3)
        interval_frame.pack(side='top', anchor=W)

        interval_input_label = Label(interval_frame, text="Tuning interval (x10ms): ")
        interval_input_label.pack(side='left',anchor=W)

        interval_input = Entry(interval_frame, width=2, textvariable=self.interval_var)
        interval_input.pack(side='right',anchor=S)


        # Submit Button
        submit_button = Button(
            options_frame, text="Tune File",
            command=self.tune_with_data, borderwidth=5
        )
        submit_button.pack(side='bottom',anchor=W)


        # Selector Radios
        selector_frame = Frame(options_frame, borderwidth=3)
        selector_frame.pack(side='top', anchor=W)

        tune_freqs_checkbox = Checkbutton(
            selector_frame, text="Tune Frequencies",
            variable=self.tune_freqs_var, onvalue=1, offvalue=0,
            command=self.change_tune_freqs
        )
        tune_freqs_checkbox.pack(anchor=W, side='top')

        self.selector_radios_frame = RadioFrame(
            selector_frame, options=["Scale", "Notes"],
            label="Tune File By:", onchange=self.showsel
        )
        self.tune_type_var = self.selector_radios_frame.variable
        self.selector_radios_frame.pack(side="top", anchor=W)


        # Scale radio combobox
        scale_radio_frame = Frame(tuning_frame, borderwidth=10)
        scale_radio_frame.pack(anchor=N)

        scaleRadioLabel = Label(scale_radio_frame, text="Select scale to tune to: ")
        scaleRadioLabel.pack(anchor=W)

        self.scale_combobox = ttk.Combobox(
            scale_radio_frame, textvariable = self.scale_var,
            values=self.cb_values, state = "readonly"
        )
        self.scale_combobox.pack(anchor=W)

        self.adv_scale_checkbox = Checkbutton(
            scale_radio_frame, command=self.change_scales_shown,
            text="Show additional scales", onvalue=1,offvalue=0,
            variable=self.show_scales_var
        )
        self.adv_scale_checkbox.pack(anchor=W)


        # Note checkbuttons
        note_buttons_frame = Frame(tuning_frame, padx=10)
        note_buttons_frame.pack(anchor=SW)

        bottom_notes_frame=Frame(note_buttons_frame)
        bottom_notes_frame.pack(side='bottom')

        notes_leftcol_frame = Frame(bottom_notes_frame, borderwidth=3, padx=10)
        notes_leftcol_frame.pack(side='left', anchor=W)

        notes_rightcol_frame = Frame(bottom_notes_frame, borderwidth=3,padx=10)
        notes_rightcol_frame.pack(side='right', anchor=W)

        note_buttons_label = Label(note_buttons_frame, text="Select note(s) to tune to: ")
        note_buttons_label.pack(anchor=N)

        self.note_buttons = [
            Checkbutton(
                master=(notes_leftcol_frame if i<6 else notes_rightcol_frame),
                text=n, variable=self.note_vars[i], onvalue=1, offvalue=0,
                state="disabled"
            ) for i,n in enumerate(notes)
        ]
        for n in self.note_buttons:
            n.pack(anchor=W)


        # Tuning key Frame
        self.key_var.trace('w', self.validate_key)

        key_frame = Frame(tuning_frame, borderwidth=3)
        key_frame.pack(side='top', anchor=W)

        key_input_label = Label(key_frame, text="(beta) Tune with key:")
        key_input_label.pack(side='left')

        key_input = Entry(key_frame,width=7,textvariable=self.key_var)
        key_input.pack(side='left')

        key_buttons_frame = Frame(tuning_frame)
        key_buttons_frame.pack(side="top", anchor=W)

        show_key_button = Button(
            key_buttons_frame, text="Set Key",
            command=self.process_tuning_key
        )
        show_key_button.pack(side='left')

        get_key_button = Button(
            key_buttons_frame, text="Get Key",
            command=self.make_scale
        )
        get_key_button.pack(side="right")

def main():
    app = TunerApp()
    app.mainloop()

if __name__ == "__main__":
    main()