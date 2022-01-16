import pandas as pd
from io import StringIO

def parse_df(df: pd.DataFrame) -> pd.DataFrame:         # Returns the desired columns (active formant freq and amp) from an inputted pd.DataFrame
    new_df = pd.DataFrame( {'x': [n*10 for n in range(len(df.index))]} )

    for fmt in range(1,9):                              # adds only the formants that are active (changing)

        col_name = f'a{fmt}f'
        amp_col = df[col_name]
        for amp_val in amp_col:

            if amp_val != 30:                           # Check for non-baseline amplitude indicating active formant
                new_df[f'f{fmt}'] = df[f'f{fmt}']
                new_df[f'a{fmt}'] = amp_col
                break

        else: break
    
    new_df.columns = [fmt-1] + ['']*2*(fmt-1)
    return new_df

filepath = "/Users/colin/Desktop/LAB/Vowels/CTSF_had1.stk"

with open(filepath, 'r') as reader:
		file_content = ''.join(reader.readlines()[8:])
		df = pd.read_csv(StringIO(file_content), sep='\t')

desired_cols = parse_df(df)
print(desired_cols)