from tkinter import *
from tkinter import ttk

root = Tk()

notes=['A','A#','B','C','C#','D','D#','E','F','F#','G','G#']
scaletypes=["Major Scale","Natural Minor Scale","Melodic Minor Scale", "Harmonic Minor Scale"]

default_scales ={
    'Major Scale': [0,2,4,5,7,9,11],
    'Natural Minor Scale':[0,2,3,5,7,8,10],
    'Harmonic Minor Scale': [0,2,3,5,7,8,11],
    'Melodic Minor Scale': [0,2,3,5,7,9,11]
}

frm = Frame(padx=20,pady=20)
frm.pack()

def onsel_cmb(evt):
    cmb_text = cmb_string.get()
    scale_note, scale_type = cmb_text.split(' ',1)
    print(scale_note); print(scale_type)

    namelbl.config(text=cmb_text)
    scalelbl.config(text=construct_default_scale(notes.index(scale_note)+1, scale_type))
    return

def construct_default_scale(note: int, scale_type: str) -> list:
    return [(note+n)%12 or 12 for n in default_scales[scale_type]]

cmb_string = StringVar()
cmb = ttk.Combobox(frm,textvariable=cmb_string,state="readonly")
cmb.bind("<<ComboboxSelected>>",onsel_cmb)

cmb.config(values=[f"{notes[i]} {n}" for n in scaletypes for i in range(len(notes))])
cmb.pack()

namelbl = ttk.Label(frm)
namelbl.pack(side='bottom')

scalelbl = ttk.Label(frm)
scalelbl.pack(side='bottom')

mainloop()