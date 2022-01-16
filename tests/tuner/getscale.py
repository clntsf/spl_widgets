from tkinter import *
from misc_util import num_scale_to_strs

def getscale(Key: str):

    tune_freqs = bool(Key[0])
    interval = int(Key[1:3])

    scale_bin = bin(int(Key[-3:],base=16))[2:]
    scale_bin = '0'*(12-len(scale_bin))+scale_bin
    scale_list = [i for i in range(1,13) if scale_bin[-i] == "1"]

    return tune_freqs, interval, scale_list

root=Tk()
root.title("Key validation test")

keyVar = StringVar()

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

def displayKey():
    key = keyVar.get()
    if len(key) == 7:
        tune_freqs, interval, scale_list = getscale(keyVar.get())
        tuneFreqsLabel.config(text=f"{tuneStr} {tune_freqs}")
        intervalLabel.config(text=f"{intervalStr} {interval}")
        scaleLabel.config(text=f"{scaleStr} {num_scale_to_strs(scale_list)}")

keyVar.trace('w', validateKey)

keyInFrame = Frame(root, borderwidth=5)
keyInFrame.pack(side='top', anchor=W)

keyInputLabel = Label(keyInFrame, text="Enter Tuning Key:")
keyInputLabel.pack(side='left')
keyInput = Entry(keyInFrame,width=7,textvariable=keyVar)
keyInput.pack(side='left')

keyOutFrame = Frame(root, borderwidth=5)
keyOutFrame.pack(side='top', anchor=W)

tuneStr = "Tune Freqs:"; intervalStr = "Interval (x10 ms):"; scaleStr = "Scale:"
tuneFreqsLabel = Label(keyOutFrame, text=tuneStr); tuneFreqsLabel.pack(side='top', anchor=W)
intervalLabel = Label(keyOutFrame, text=intervalStr); intervalLabel.pack(side='top', anchor=W)
scaleLabel = Label(keyOutFrame, text=scaleStr); scaleLabel.pack(side='top', anchor=W)

showKeyButton = Button(keyOutFrame, text="Set Key", command=displayKey)
showKeyButton.pack(side='top', anchor=W)

root.mainloop()