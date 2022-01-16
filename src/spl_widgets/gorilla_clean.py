import pandas as pd
import tkinter as tk
from tkinter import filedialog
import sys
from subprocess import run

data_modules={
    "awk4":"Cooldown",
    "l5it":"Sentence Transcription",
    "9bbq": "Headphone Test"
}

desired_c_CHECK = ["Response", "ANSWER", "Correct","audio"]
desired_c_DEFAULT = ["Response", "audio"]

class Subject():

    id: int
    source: str
    outfp: str
    tasks: "dict[str,pd.DataFrame]" = {}

    def __init__(self, **kwargs):
        self.source = kwargs.get("source") or self.get_source_by_filedialog()

        self.outfp = kwargs.get("out") or self.source

        self.id = int(self.source[self.source.rfind("_")+1:])

    def get_source_by_filedialog(self):
        return filedialog.askdirectory(title="Subject Data Folder: ")

    def parse(self):
        if self.source == '': return False
        for task_key in data_modules.keys():
            filepath_to_task = f"{self.source}/{self.source[self.source.rfind('/'):self.source.rfind('_')]}_task-{task_key}-{self.id}.xlsx"
            self.tasks[task_key] = pd.read_excel(filepath_to_task)

            self.parse_file(task_key)
        
        self.write_to_excel()

    def parse_file(self, task_key):
        df = self.tasks[task_key]
        desired_c = [desired_c_DEFAULT,desired_c_CHECK][task_key == "9bbq"]

        df_formatted = df[desired_c].loc[[type(n) == str and "response" in n for n in df["Zone Type"]]]

        if task_key == "9bbq":
            pct_correct = str(round(sum(df_formatted["Correct"])/len(df_formatted.index)*100,2))+"%"
            pct_correct_row = pd.DataFrame([["PERCENT CORRECT","","",pct_correct]], columns=desired_c)
            df_formatted = pd.concat([df_formatted, pct_correct_row],axis=0)

        self.tasks[task_key] = df_formatted

    def write_to_excel(self):
        writer = pd.ExcelWriter(f"{self.outfp}/{self.id}_CLEANED.xlsx", engine="xlsxwriter")

        for task_key, df in self.tasks.items():
            df.to_excel(writer, sheet_name = data_modules[task_key], index=False)

        writer.save()


def main():
    
    root = tk.Tk()
    root.focus_force()
    root.wm_geometry("0x0+0+0")

    args = sys.argv
    if 'folder' in args:
        data_dir = filedialog.askdirectory(title="Directory containing subject folders: ")
        if data_dir == '': return False

        in_dir = str(run(["ls",data_dir],capture_output=True).stdout)[2:-2].split('\\n')
        
        for item in in_dir:
            if item.startswith("data_exp"):
                subj = Subject(source=f"{data_dir}/{item}", out=data_dir)
                subj.parse()

    else:
        subj1 = Subject()
        subj1.parse()

if __name__ == "__main__":
    main()