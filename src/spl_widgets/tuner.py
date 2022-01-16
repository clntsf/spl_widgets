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
        for b in self.radios: b.configure(state="disabled")

    def enable(self):
        for b in self.radios: b.configure(state="normal")

def getscale(Key: str):

    tune_freqs = int(Key[0])
    interval = int(Key[1:3])

    scale_bin = bin(int(Key[-3:],base=16))[2:]
    scale_bin = '0'*(12-len(scale_bin))+scale_bin
    scale_list = [i for i in range(1,13) if scale_bin[-i] == "1"]

    return tune_freqs, interval, scale_list

def main():

    root=Tk()
    root.title("CTSF's SWX Tuner")
    root.geometry("470x330+50+50")
    root.resizable(False, False)

    intervalVar = StringVar()
    fileVar = StringVar()
    scaleVar = StringVar(value="C Major Scale")
    keyVar = StringVar()

    tuneTypeVar = IntVar()
    showScalesVar = IntVar()
    noteVars = [IntVar() for _ in range(len(notes))]
    tuneFreqsVar = IntVar(value=1)

    cb_values = [f"{n} Major Scale" for n in notes]
    cb_values_ext = [f"{notes[i]} {n}" for n in default_scales.keys() for i in range(len(notes))]

    def validateKey(*args):
        key = keyVar.get(); newkey = key
        invalidKey = (
            len(key) > 7 or
            (4<len(key)<7 and not (key[-1].isdigit() or key[-1].lower() in 'abcdef')) or
            (len(key) == 4 and key[-1] != "-") or
            1<len(key)<4 and not key[-1].isdigit() or
            (len(key)==1 and key[0] not in '01'))

        if invalidKey: newkey = key[:-1]
        keyVar.set(newkey.upper())

    def processTuningKey():

        if len(keyVar.get())!=7: return -1

        tune_freqs, interval, scale_list = getscale(keyVar.get())
        tuneFreqsVar.set(tune_freqs)
        intervalVar.set(interval)
        selectorRadiosFrame.radios[1].invoke()

        for i,n in enumerate(noteVars):
            n.set(i+1 in scale_list)

    def limitIntervalLen(*args):
        interval_in = intervalVar.get()
        if len(interval_in)>2 or (len(interval_in) >0 and not interval_in[-1].isdigit()):
            intervalVar.set(interval_in[:-1])

    intervalVar.trace('w',limitIntervalLen)

    def disableScaleTuning():
        scaleCombobox.configure(state="disabled")
        advScaleCheckbox.configure(state="disabled")

    def disableNoteTuning():
        for noteCheckbox in noteButtons:
            noteCheckbox.configure(state="disabled")

    def enableScaleTuning():
        scaleCombobox.configure(state="readonly")
        advScaleCheckbox.configure(state="normal")

    def enableNoteTuning():
        for noteCheckbox in noteButtons:
            noteCheckbox.configure(state="normal")

    def showsel(v: IntVar):

        if v.get():
            disableScaleTuning()
            enableNoteTuning()
        else:
            disableNoteTuning()
            enableScaleTuning()

    def getFile():
        if fileTypeVar.get():
            file = filedialog.askdirectory(
                title="Select Parent Directory of Files to Tune: "
            )
            if file!="": fileName.configure(text=f"Directory: {file[file.rfind('/')+1:]}")
        else:
            file = filedialog.askopenfilename(
                title="Select File to Tune",
                filetypes=[("SWX Files","*.swx")]
                )
            if file != "": fileName.configure(text=f'File: {file[file.rfind("/")+1:]}')

        fileVar.set(file)

    def changeFileType(v: IntVar):
        if v.get():
            fileLabel.configure(text="Set Path to Tune: ")
            fileVar.set(""); fileName.configure(text="")
        else:
            fileLabel.configure(text="Set File to Tune: ")
            fileVar.set(""); fileName.configure(text="")

    def changeScalesShown():
        showAdditional = showScalesVar.get()
        if showAdditional: scaleCombobox.config(values=cb_values_ext)
        else:
            scaleCombobox.config(values=cb_values)
            if scaleVar.get() not in cb_values: scaleVar.set("C Major Scale")

    def changeTuneFreqs():
        tuneFreqs = tuneFreqsVar.get()
        if tuneFreqs: 
            selectorRadiosFrame.enable()
            if tuneTypeVar.get(): enableNoteTuning()
            else: enableScaleTuning()
        else:
            selectorRadiosFrame.disable()
            disableNoteTuning(); disableScaleTuning()

    def tuneWithData():
        filepath = fileVar.get()
        interval = int(intervalVar.get())
        tune_freqs = tuneFreqsVar.get()

        tuneType = tuneTypeVar.get()        # 0: scale, 1: notes
        if tuneType == 0:
            scale_note, scale_type = scaleVar.get().split(' ',maxsplit=1)
            scale = construct_default_scale(notes.index(scale_note)+1, scale_type)
        else:
            scale = [i+1 for i in range(len(noteButtons)) if noteVars[i].get()]

        can_proceed = (filepath and interval and (scale or not tune_freqs))
        if can_proceed:
            if fileTypeVar.get() == 0:   # 1: dir, 0: file
                outfilepath = tune_cols(filepath, interval, scale, bool(tune_freqs))
                run(['open', outfilepath], capture_output=True)
            else:
                filesInDir = [n for n in str(run(['ls',filepath],capture_output=True).stdout)[2:].split('\\n') if n.endswith('.swx')]
                for f in filesInDir: tune_cols(f"{filepath}/{f}", interval, scale, bool(tune_freqs))
                run(['open', filepath], capture_output=True)

    optionsFrame = Frame(root, borderwidth=10); optionsFrame.pack(side='left', anchor=N)
    tuningFrame = Frame(root, pady=5); tuningFrame.pack(side='right', anchor=N)

    # File Input
    fileFrame = Frame(optionsFrame, borderwidth=5)
    fileFrame.pack(side='top', anchor=W)

    fileRadioFrame = RadioFrame(fileFrame, options=['Single file', 'Directory'], label="Object to Tune:", orientation="h", onchange=changeFileType)
    fileRadioFrame.configure(borderwidth=3); fileRadioFrame.pack(side='top', anchor=W); fileTypeVar = fileRadioFrame.variable

    fileInputFrame = Frame(fileFrame); fileInputFrame.pack(side='top')

    fileLabel = Label(fileInputFrame, text="Set File to Tune:")
    fileLabel.pack(side='left', anchor=W)

    fileInput = Button(fileInputFrame, text="Browse...", command=getFile)
    fileInput.pack(side='left', anchor=W)

    fileName = Label(fileFrame)
    fileName.pack(side='top', anchor=W)


    # Interval Input
    intervalFrame = Frame(optionsFrame, borderwidth=3)
    intervalFrame.pack(side='top', anchor=W)

    intervalInputLabel = Label(intervalFrame, text="Tuning interval (x10ms): ")
    intervalInputLabel.pack(side='left',anchor=W)

    intervalInput = Entry(intervalFrame, width=2, textvariable=intervalVar)
    intervalInput.pack(side='right',anchor=S)


    # Submit Button
    submitButton = Button(optionsFrame, text="Tune File", command=tuneWithData, borderwidth=5)
    submitButton.pack(side='bottom',anchor=W)

    # Selector Radios
    selectorFrame = Frame(optionsFrame, borderwidth=3)
    selectorFrame.pack(side='top', anchor=W)

    tuneFreqsCheckbox = Checkbutton(selectorFrame, text="Tune Frequencies", variable=tuneFreqsVar, onvalue=1, offvalue=0, command=changeTuneFreqs)
    tuneFreqsCheckbox.pack(anchor=W, side='top')

    selectorRadiosFrame = RadioFrame(selectorFrame, options=["Scale", "Notes"], label="Tune File By:", onchange=showsel)
    tuneTypeVar = selectorRadiosFrame.variable; selectorRadiosFrame.pack(side="top", anchor=W)

    # Scale radio combobox
    scaleRadioFrame = Frame(tuningFrame, borderwidth=10)
    scaleRadioFrame.pack(anchor=N)

    scaleRadioLabel = Label(scaleRadioFrame, text="Select scale to tune to: ")
    scaleRadioLabel.pack(anchor=W)

    scaleCombobox = ttk.Combobox(scaleRadioFrame, textvariable = scaleVar, values=cb_values, state = "readonly")
    scaleCombobox.pack(anchor=W)

    advScaleCheckbox = Checkbutton(scaleRadioFrame, command=changeScalesShown, text="Show additional scales",onvalue=1,offvalue=0, variable=showScalesVar)
    advScaleCheckbox.pack(anchor=W)

    # Note checkbuttons
    noteButtonsFrame = Frame(tuningFrame, padx=10); noteButtonsFrame.pack(anchor=SW)
    bottomNotesFrame=Frame(noteButtonsFrame); bottomNotesFrame.pack(side='bottom')

    leftSideFrame = Frame(bottomNotesFrame, borderwidth=3, padx=10); leftSideFrame.pack(side='left', anchor=W)
    rightSideFrame = Frame(bottomNotesFrame, borderwidth=3,padx=10); rightSideFrame.pack(side='right', anchor=W)

    noteButtonsLabel = Label(noteButtonsFrame, text="Select note(s) to tune to: ")
    noteButtonsLabel.pack(anchor=N)

    noteButtons = [Checkbutton([leftSideFrame,rightSideFrame][i>5], text=n, variable=noteVars[i], onvalue=1, offvalue=0, state="disabled") for i,n in enumerate(notes)]
    for n in noteButtons: n.pack(anchor=W)

    # Tuning key Frame
    keyVar.trace('w', validateKey)

    keyFrame = Frame(tuningFrame, borderwidth=3)
    keyFrame.pack(side='top', anchor=W)

    keyInputLabel = Label(keyFrame, text="(beta) Tune with key:")
    keyInputLabel.pack(side='left')
    keyInput = Entry(keyFrame,width=7,textvariable=keyVar)
    keyInput.pack(side='left')

    showKeyButton = Button(tuningFrame, text="Set Key", command=processTuningKey)
    showKeyButton.pack(side='top', anchor=W)

    root.mainloop()

if __name__ == "__main__": main()