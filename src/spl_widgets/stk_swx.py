import pandas as pd
from io import StringIO
import tkinter as tk
from tkinter import filedialog
from sys import argv
from subprocess import run
from itertools import chain

def parse_df(df: pd.DataFrame) -> "tuple[int, pd.DataFrame]":   # Returns the desired columns (active formant freq and amp) from an inputted pd.DataFrame

	df["f0"] = [n*10 for n in range(len(df.index))]
	for fmt in range(4,7):                              		# adds only the formants that are active (changing)

		amp_col = df[f"a{fmt}f"]
		for amp_val in amp_col:
			if amp_val != 30:                           # Check for non-baseline amplitude indicating active formant
				break

		else:
			cols = list(chain([[f"f{fmt}",f"a{fmt}f"] for fmt in range(fmt)]))
			return fmt-1, df[cols]

def stk_to_swx(filepath: str) -> str:
	multipliers = [.7,.4,.2,.1,0.5]

	# --- Read .stk file, and take the info to a dataframe --- #
	with open(filepath, 'r') as reader:
		file_content = ''.join(reader.readlines()[8:])

	formants, df = parse_df( pd.read_csv(StringIO(file_content), sep='\t') )
	amp_cols = [f"a{f+1}" for f in range(formants)]			# get amp col headers and number of formants

	# --- Correct amplitude vals --- #
	amp_max = [max(df[col]) for col in amp_cols]
	for i in range(formants):
		for n in df[amp_cols[i]]:
			n = multipliers[i] * (amp_max[i] / n) if n > 30 else 0

	# --- Prettifying and output --- #
	df.columns = [formants]+['']*(formants*2)
	outFilepath = filepath[:-4]

	df.to_csv(f"{outFilepath}.tsv", index=False, sep='\t')
	run(["mv", f"{outFilepath}.tsv", f"{outFilepath}.swx"], capture_output=False)

	return outFilepath


def main() -> None:
	# --- Get filepath to .stk file --- #
	root = tk.Tk()
	root.focus_force()
	root.wm_geometry("0x0+0+0")

	if "folder" in argv:
		filepath = filedialog.askdirectory()
		if filepath == '': return False

		filesInDir = str(run(["ls", filepath], capture_output=True).stdout)[2:-1].split('\\n')[:-1]		# gets and parses terminal ls output into list of files in directory
		operableFiles = [file for file in filesInDir if file.endswith(".stk")]							# gets files with .stk extension

		for file in operableFiles:
			stk_to_swx(f'{filepath}/{file}')
			print(f"File {file} has been converted")

		print('-'*30+"\nCompatible files have been successfully converted")

	else:
		filepath=filedialog.askopenfilename(filetypes=[('',".stk")])
		if filepath == '': return False

		outFilepath = stk_to_swx(filepath)
		print('\n'+f"File written to {outFilepath}.swx")

	# --- Display completion message, open .swx file/dir if user chooses --- #
	if input("Open Output? (y/n): ").lower() == 'y':
		run(["open", f"{outFilepath}.swx"], capture_output=False)


if __name__ == "__main__":
	main()