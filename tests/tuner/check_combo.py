from tkinter import *
root=Tk()
root.geometry("300x300")
var1='button1'
var2='button2'

def fun(value):
    if value=="button1":
        testmenu.entryconfigure("button1",background="light blue")
        testmenu.entryconfigure("button2", background="#ede8ec")
    if value=="button2":
        testmenu.entryconfigure("button2",background="light blue")
        testmenu.entryconfigure("button1", background="#ede8ec")
    
mainmenu=Menu(root)
root.config(menu=mainmenu)

testmenu=Menu(mainmenu,tearoff=False,background="#ede8ec")

mainmenu.add_cascade(label="Test",menu=testmenu)

testmenu.add_command(label="button1",command=lambda :fun(var1))
testmenu.add_command(label="button2",command=lambda :fun(var2))

label=Label(text="")
label.pack(pady=125)

root.mainloop()