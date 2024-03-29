from tkinter import *
from tkinter import filedialog, ttk
from spl_widgets.misc_util import *
from spl_widgets.tune_freq import tune_cols
from subprocess import run

class RadioFrame(Frame):

    def __init__(self, master: Frame, options: "list[str]", label: str, onchange: "function", orientation="v") -> Frame:
        Frame.__init__(self, master)

        self.parent = master
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

def get_scale(key: str):

    tune_freqs = int(key[0])
    interval = int(key[1:3])

    scale_bin = bin(int(key[-3:],base=16))[2:]
    scale_bin = scale_bin.zfill(12)
    scale_list = [i for i in range(1,13) if scale_bin[-i] == "1"]

    return tune_freqs, interval, scale_list

def main():

    root=Tk()
    root.title("CTSF's SWX Tuner")
    root.geometry("470x330+50+50")
    root.resizable(False, False)

    interval_var = StringVar()
    file_var = StringVar()
    scale_var = StringVar(value="C Major Scale")
    key_var = StringVar()

    tune_type_var = IntVar()
    show_scales_var = IntVar()
    note_vars = [IntVar() for _ in range(len(notes))]
    tune_freqs_var = IntVar(value=1)

    cb_values = [f"{n} Major Scale" for n in notes]
    cb_values_ext = [f"{notes[i]} {n}" for n in default_scales.keys() for i in range(len(notes))]

    def validate_key(*args):
        key = key_var.get()
        new_key = key

        invalid_key = (
            len(key) > 7 or
            (4<len(key)<7 and not (key[-1].isdigit() or key[-1].lower() in 'abcdef')) or
            (len(key) == 4 and key[-1] != "-") or
            1<len(key)<4 and not key[-1].isdigit() or
            (len(key)==1 and key[0] not in '01'))

        if invalid_key:
            new_key = key[:-1]
        key_var.set(new_key.upper())

    def process_tuning_key():

        if len(key_var.get())!=7: return -1

        tune_freqs, interval, scale_list = get_scale(key_var.get())
        tune_freqs_var.set(tune_freqs)
        interval_var.set(interval)
        selector_radios_frame.radios[1].invoke()

        for i,n in enumerate(note_vars):
            n.set(i+1 in scale_list)

    def limit_interval_len(*args):
        interval_in = interval_var.get()
        if len(interval_in)>2 or (len(interval_in)>0 and not interval_in[-1].isdigit()):
            interval_var.set(interval_in[:-1])
    interval_var.trace('w',limit_interval_len)

    def disable_scale_tuning():
        scale_combobox.configure(state="disabled")
        adv_scale_checkbox.configure(state="disabled")

    def disable_note_tuning():
        for note_checkbox in note_buttons:
            note_checkbox.configure(state="disabled")

    def enable_scale_tuning():
        scale_combobox.configure(state="readonly")
        adv_scale_checkbox.configure(state="normal")

    def enable_note_tuning():
        for note_checkbox in note_buttons:
            note_checkbox.configure(state="normal")


    def showsel(v: IntVar):

        if v.get():
            disable_scale_tuning()
            enable_note_tuning()
        else:
            disable_note_tuning()
            enable_scale_tuning()

    def get_file():
        if file_type_var.get():
            file = filedialog.askdirectory(
                title="Select Parent Directory of Files to Tune: "
            )
            if file!="":
                file_name.configure(text=f"Directory: {file[file.rfind('/')+1:]}")
        else:
            file = filedialog.askopenfilename(
                title="Select File to Tune",
                filetypes=[("SWX Files","*.swx")]
                )
            if file != "":
                file_name.configure(text=f'File: {file[file.rfind("/")+1:]}')

        file_var.set(file)

    def change_file_type(v: IntVar):
        if v.get():
            file_label.configure(text="Set Path to Tune: ")
            file_var.set("")
            file_name.configure(text="")
        else:
            file_label.configure(text="Set File to Tune: ")
            file_var.set("")
            file_name.configure(text="")

    def change_scales_shown():
        showAdditional = show_scales_var.get()
        if showAdditional:
            scale_combobox.config(values=cb_values_ext)
        else:
            scale_combobox.config(values=cb_values)
            if scale_var.get() not in cb_values:
                scale_var.set("C Major Scale")

    def change_tune_freqs():
        tune_freqs = tune_freqs_var.get()
        if tune_freqs: 
            selector_radios_frame.enable()
            if tune_type_var.get():
                enable_note_tuning()
            else:
                enable_scale_tuning()
        else:
            selector_radios_frame.disable()
            disable_note_tuning()
            disable_scale_tuning()

    def get_scale_vals():
        tune_type = tune_type_var.get()        # 0: scale, 1: notes
        if tune_type == 0:
            scale_note, scale_type = scale_var.get().split(' ',maxsplit=1)
            return construct_default_scale(notes.index(scale_note)+1, scale_type)
        else:
            return [i+1 for i in range(len(note_buttons)) if note_vars[i].get()]

    def make_scale():
        tune_freqs = tune_freqs_var.get()
        interval = interval_var.get()

        scale = get_scale_vals()
        keys = "".join("1"  if k in scale else "0" for k in range(12,0,-1))
        scale_hex = hex(int(keys, base=2))[2:].upper()

        new_key = f"{tune_freqs}{interval}-{scale_hex}"
        key_var.set(new_key)

    def tune_with_data():
        filepath = file_var.get()
        interval = int(interval_var.get())
        tune_freqs = tune_freqs_var.get()
        scale = get_scale_vals()

        can_proceed = (filepath and interval and (scale or not tune_freqs))
        if can_proceed:
            if file_type_var.get() == 0:   # 1: dir, 0: file
                outfilepath = tune_cols(filepath, interval, scale, bool(tune_freqs))
                run(['open', outfilepath], capture_output=True)
            else:
                files_in_dir = run(['ls',filepath],capture_output=True).stdout.decode("utf-8")
                files_in_dir = filter(lambda n:n.endswith(".swx"), files_in_dir.splitlines())
                for f in files_in_dir:
                    tune_cols(f"{filepath}/{f}", interval, scale, bool(tune_freqs))
                run(['open', filepath], capture_output=True)

    options_frame = Frame(root, borderwidth=10)
    options_frame.pack(side='left', anchor=N)

    tuning_frame = Frame(root, pady=5)
    tuning_frame.pack(side='right', anchor=N)


    # File Input
    file_frame = Frame(options_frame, borderwidth=5)
    file_frame.pack(side='top', anchor=W)

    file_radio_frame = RadioFrame(
        file_frame, options=['Single file', 'Directory'],
        label="Object to Tune:", orientation="h",
        onchange=change_file_type
    )
    file_radio_frame.configure(borderwidth=3)
    file_radio_frame.pack(side='top', anchor=W)
    file_type_var = file_radio_frame.variable

    file_input_frame = Frame(file_frame)
    file_input_frame.pack(side='top')

    file_label = Label(file_input_frame, text="Set File to Tune:")
    file_label.pack(side='left', anchor=W)

    file_input = Button(file_input_frame, text="Browse...", command=get_file)
    file_input.pack(side='left', anchor=W)

    file_name = Label(file_frame)
    file_name.pack(side='top', anchor=W)


    # Interval Input
    interval_frame = Frame(options_frame, borderwidth=3)
    interval_frame.pack(side='top', anchor=W)

    interval_input_label = Label(interval_frame, text="Tuning interval (x10ms): ")
    interval_input_label.pack(side='left',anchor=W)

    interval_input = Entry(interval_frame, width=2, textvariable=interval_var)
    interval_input.pack(side='right',anchor=S)


    # Submit Button
    submit_button = Button(options_frame, text="Tune File", command=tune_with_data, borderwidth=5)
    submit_button.pack(side='bottom',anchor=W)


    # Selector Radios
    selector_frame = Frame(options_frame, borderwidth=3)
    selector_frame.pack(side='top', anchor=W)

    tune_freqs_checkbox = Checkbutton(
        selector_frame, text="Tune Frequencies",
        variable=tune_freqs_var, onvalue=1, offvalue=0,
        command=change_tune_freqs
    )
    tune_freqs_checkbox.pack(anchor=W, side='top')

    selector_radios_frame = RadioFrame(
        selector_frame, options=["Scale", "Notes"],
        label="Tune File By:", onchange=showsel
    )
    tune_type_var = selector_radios_frame.variable
    selector_radios_frame.pack(side="top", anchor=W)


    # Scale radio combobox
    scale_radio_frame = Frame(tuning_frame, borderwidth=10)
    scale_radio_frame.pack(anchor=N)

    scaleRadioLabel = Label(scale_radio_frame, text="Select scale to tune to: ")
    scaleRadioLabel.pack(anchor=W)

    scale_combobox = ttk.Combobox(
        scale_radio_frame, textvariable = scale_var,
        values=cb_values, state = "readonly"
    )
    scale_combobox.pack(anchor=W)

    adv_scale_checkbox = Checkbutton(
        scale_radio_frame, command=change_scales_shown,
        text="Show additional scales", onvalue=1,offvalue=0,
        variable=show_scales_var
    )
    adv_scale_checkbox.pack(anchor=W)


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

    note_buttons = [
        Checkbutton(
            master=(notes_leftcol_frame if i<6 else notes_rightcol_frame),
            text=n, variable=note_vars[i], onvalue=1, offvalue=0,
            state="disabled"
        ) for i,n in enumerate(notes)
    ]
    for n in note_buttons:
        n.pack(anchor=W)

    # Tuning key Frame
    key_var.trace('w', validate_key)

    key_frame = Frame(tuning_frame, borderwidth=3)
    key_frame.pack(side='top', anchor=W)

    key_input_label = Label(key_frame, text="(beta) Tune with key:")
    key_input_label.pack(side='left')

    key_input = Entry(key_frame,width=7,textvariable=key_var)
    key_input.pack(side='left')

    key_buttons_frame = Frame(tuning_frame)
    key_buttons_frame.pack(side="top", anchor=W)

    show_key_button = Button(key_buttons_frame, text="Set Key", command=process_tuning_key)
    show_key_button.pack(side='left')

    get_key_button = Button(key_buttons_frame, text="Get Key", command=make_scale)
    get_key_button.pack(side="right")

    root.mainloop()

if __name__ == "__main__": main()