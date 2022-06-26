import pandas as pd
from io import StringIO
import tkinter as tk
from tkinter import filedialog
import sys
from subprocess import run

class MalformedFileError(Exception): pass

def parse_df(df: pd.DataFrame) -> "tuple[int, pd.DataFrame]":   # Returns the desired columns (active formant freq and amp) from an inputted pd.DataFrame

	df["f0"] = [n*10 for n in range(len(df.index))]
	for fmt in range(4,7):                              		# adds only the formants that are active (changing)

		amp_col = df[f"a{fmt}f"]
		for amp_val in amp_col:
			if amp_val != 30:                           # Check for non-baseline amplitude indicating active formant
				break

		else:
			cols = ["f0"]
			for x in range(1,fmt): cols.extend([f"f{x}",f"a{x}f"])
			return fmt-1, df[cols]

def stk_to_swx(filepath):
	multipliers = [.7,.4,.2,.1,0.5]

	# --- Read .stk file, and take the info to a dataframe --- #
	with open(filepath, 'r') as reader:
		file_content = ''.join(reader.readlines()[8:])
		
	try:
		(formants, df) = parse_df( pd.read_csv(StringIO(file_content), sep='\t') )
	except Exception:
		raise MalformedFileError("File is malformed and does not conform to generic .stk format")

	amp_cols = [f"a{f+1}f" for f in range(formants)]			# get amp col headers and number of formants

	# --- Correct amplitude vals --- #
	amp_max = [max(df[col]) for col in amp_cols]
	for i in range(formants):
		def scalemult(cell):
			if cell<=30: return 0
			return round(multipliers[i] * (amp_max[i] / cell), 4)
	
		colnm = amp_cols[i]
		col = df[colnm]
		df[colnm] = list(map(scalemult, col))

	# --- Prettifying and output --- #
	df.columns = [formants]+['']*(formants*2)
	out_fp = filepath[:-4]

	df.to_csv(f"{out_fp}.tsv", index=False, sep='\t')
	run(["mv", f"{out_fp}.tsv", f"{out_fp}.swx"], capture_output=False)

	return out_fp


def main(*args):
	# --- Get filepath to .stk file --- #
	root = tk.Tk()
	root.focus_force()
	root.wm_geometry("0x0+0+0")

	if "folder" in sys.argv:
		out_fp = filepath = filedialog.askdirectory()
		if filepath == '': return False

		files_in_dir = str(run(["ls", filepath], capture_output=True).stdout)[2:-1].split('\\n')[:-1]		# gets and parses terminal ls output into list of files in directory
		operable_files = [file for file in files_in_dir if file.endswith(".stk")]							# gets files with .stk extension

		for file in operable_files:
			stk_to_swx(f'{filepath}/{file}')
			print(f"File {file} has been converted")

		print("\nCompatible files have been successfully converted")

	else:
		filepath=filedialog.askopenfilename(filetypes=[('',".stk")])
		if filepath == '': return False

		out_fp = stk_to_swx(filepath)
		print('\n'+f"File written to {out_fp}.swx.")

	# --- Display completion message, open .swx file/dir if user chooses --- #
	if input("Open Output? (y/n): ").lower() == 'y':
		run(["open", f"{out_fp}.swx"], capture_output=False)


if __name__ == "__main__":
	main()