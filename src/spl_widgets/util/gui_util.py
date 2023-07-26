import tkinter as tk
from tkinter import ttk
from typing import Callable

class RadioFrame(tk.Frame):

    def __init__(
        self,
        master: tk.Frame,
        options: "list[str]",
        label_text: str,
        onchange: Callable = None,
        orientation: str = "v",
        **kwargs
        ):
        super().__init__(master, **kwargs)

        self.master = master
        self.variable = tk.IntVar()
        self.onchange = lambda: onchange(self.variable) if onchange else None

        self.packsides = ["top", "bottom"] if orientation == "v" else ["left", "right"]
        self.anchorside = "w" if orientation == "v" else "n"

        self.label = tk.Label(self, text = label_text)

        self.label.pack(side="top", anchor="w")

        self.radios = [
            tk.Radiobutton(self,text=o, variable=self.variable, value=i, command=self.onchange)
            for i,o in enumerate(options)
        ]
        
        # iterated and packed in reverse order so that the label can be unpacked/repacked without disruption
        for b in self.radios[::-1]:
            b.pack(side=self.packsides[1], anchor = self.anchorside)

    def disable(self):
        for b in self.radios:
            b.configure(state="disabled")

    def enable(self):
        for b in self.radios:
            b.configure(state="normal")

class MarginListBox(tk.Listbox):
    """
    Wrapper cosmetic/functionality class adding an enclosing frame, drag/drop functionality and minus button to a listbox
    """

    enclosing_frame: tk.Frame
    data_items: dict[str,str]

    def __init__(
            self, master: tk.Widget,
            add_item_callback: "Callable[[MarginListBox, dict, tk.Event], None]",
            remove_item_callback: "Callable[[MarginListBox, dict], None]",
            include_minus_button: bool = True,
            pack_args: dict = {},                                                   # args for packing the listbox
            **kwargs                                                                # args for initializing the listbox
        ):

        self.enclosing_frame = tk.Frame(
            master, padx=5, pady=5,
            background="white",
            highlightbackground="black",
            highlightthickness="1"
        )

        super().__init__(self.enclosing_frame, borderwidth=0, **kwargs)

        pack_args.setdefault("padx", 5)
        pack_args.setdefault("pady", (5,1))
        self.pack(fill="both", **pack_args)

        self.drop_target_register("DND_Files")
        self.data_items = {}

        self.add_item = lambda e: add_item_callback(self, self.data_items, e)
        self.dnd_bind('<<Drop>>', self.add_item)

        if include_minus_button:
            self.remove_item = lambda: remove_item_callback(self, self.data_items)

            minus_button = tk.Button(
                self.enclosing_frame, text="-",
                highlightbackground="white", highlightthickness=0,
                command = self.remove_item
            )
            minus_button.pack(anchor="se", padx=0, pady=0)

    def pack_frame(self, **kwargs):
        self.enclosing_frame.pack(**kwargs)

class HelpLinkLabel(tk.Label):
    def __init__(
        self, master: tk.Widget, tab_name: str,
        onclick: Callable, **kwargs
    ):
        padx = kwargs.get("padx", 0)            # transfer padding settings from label to enclosing frame
        pady = kwargs.get("pady", 0)
        kwargs.update({"padx": 0, "pady": 0})

        self.enclosing_frame = tk.Frame(master, padx=padx, pady=pady)

        super().__init__(self.enclosing_frame, **kwargs)
        self.pack( side="left", padx = 0 )

        helplink = tk.Label(self.enclosing_frame, text="(?)", fg="blue", cursor="hand2")
        helplink.bind("<Button-1>", lambda e: onclick(tab_name))
        helplink.pack(side="left", padx=0)

    def pack_frame(self, **kwargs):
        self.enclosing_frame.pack(**kwargs)

FONT_TITLE = ("TkDefaultFont", 14, "bold")
NOTEBOOK_TAB_WIDTH = 350
NOTEBOOK_TAB_MARG=30

class HelpTextParser(tk.Frame):
    content: tk.Frame

    def __init__(self, master, items: dict[str,str], **kwargs):
        super().__init__( master, **kwargs )

        self.canvas=tk.Canvas(self,width=NOTEBOOK_TAB_WIDTH, scrollregion=(0,0,300,500))
        
        scrollbar=tk.Scrollbar(self, command=self.canvas.yview)
        scrollbar.pack(side="right",fill="y", expand=True)
        scrollbar.config(command=self.canvas.yview)

        self.content = tk.Frame(self.canvas)
        self.canvas.create_window((0,0), window=self.content, anchor="nw")
        
        self.canvas.config(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left",expand=True,fill='both')

        self.parse_text(items)

    def parse_text(self, items: dict[str, str]) -> None:

        for (title, content) in items.items():
            heading_frame = tk.Frame(self.content, padx=10)
            heading_frame.pack(side="top", anchor="w")

            heading_title = tk.Label(
                heading_frame, text = title, font = FONT_TITLE,
                wraplength=NOTEBOOK_TAB_WIDTH-NOTEBOOK_TAB_MARG,
                justify="left"
            )
            heading_title.pack(side="top", anchor="w", pady=3)

            heading_text = tk.Label(
                heading_frame, text = content,
                wraplength=NOTEBOOK_TAB_WIDTH-NOTEBOOK_TAB_MARG,
                justify="left"
            )
            heading_text.pack(side="top", anchor="w", padx=5, pady=5)

            sep = ttk.Separator(heading_frame, orient="horizontal")
            sep.pack(fill="x", side="top", pady=5)

            
