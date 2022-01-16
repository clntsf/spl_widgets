import pandas as pd
from spl_widgets.misc_util import *
from tune_freq import tune_df

class TuningParams():
    def __init__(self, filepath: str, interval: int, scale: list[int] | None = None, tune_freqs: bool = None) -> "TuningParams":

        self.filepath = filepath
        self.interval = interval
        self.scale = scale

        self.tune_freqs = ( scale is not None and
                            tune_freqs is not False )

        note_code = hex(sum( [2**i * (12-i in self.scale) for i in range(12)] )//2)     # Encoding note sequence to hex
        self.key = f"{int(self.tune_freqs)}{self.interval}-{note_code[2:]}".upper()

class Scale(list):

    @classmethod
    def from_notes(cls, notes: list[str] | list[int]):
        if type(notes[0]) == str:
            print([] == list)
            notes = str_scale_to_numbers(notes)
        return cls(notes)

class Tuner():

    def __init__(self, **kwargs):           # Get params from kwargs

        self.filepath   = kwargs.get("filepath")
        self.interval   = kwargs.get("interval")
        self.tune_freqs = kwargs.get("tune_freqs")
        self.scale      = kwargs.get("scale")
        self.meta = {}
        self.num_tune = 0
        self.scale_index = 0

    @classmethod
    def from_params(cls, p: TuningParams):
        """Make Tuner object from TuningParams object."""
        return cls(**p.__dict__)

    @classmethod
    def from_key(cls, k: str):
        """Make a Tuner object from a tuning key (Note: object initializes without filepath)"""

        if (k[:3].isdigit and k[3] == '-' and k[4:].isalnum()):
            interval = int(k[1:3])
            tune_freqs = (k[0] == '1')

            if tune_freqs:
                try:                                 # Get scale notes from key
                    note_str = bin(int(k[4:],base=16))[2:]
                    note_str = '0'*(12-len(note_str))+note_str
                    scale = [i for i in range(12) if note_str[i] == '1']
                except ValueError:
                    print("Invalid Key!")  
            else: scale=None

            return cls(interval=interval, scale=scale, tune_freqs=tune_freqs)

        else: print("Invalid Key!")

    # @staticmethod
    # def get_df_from_filepath(filepath: str) -> tuple[pd.DataFrame, int, tuple[int,int]]:

    #     df = pd.read_csv(filepath, sep='\t')
    #     num_formants = int(df.columns[0])
    #     size = (len(df.index), len(df.columns))

    #     return df, num_formants, size

    def config(self, **kwargs) -> None:
        """Aesthetic function for manual change of the instance's attributes"""
        self.__dict__.update(kwargs)

    def tune_single(self, start_time=0, scale: list[int] = None, store_meta: bool = True, scale_key: int = 0) -> pd.DataFrame:
        """Tunes a the filepath once"""

        if not all(( self.filepath, self.interval, (self.tune_freqs or self.scale or scale) )):
            print("Insufficient parameters")
            return -1

        if scale is None and self.tune_freqs == True:                                       
            scale = self.scale[scale_key] if type(self.scale[0]) == list else self.scale

        tuned = tune_df(self.filepath, self.interval, scale, self.tune_freqs, start_time)
        if store_meta:
            self.meta[self.num_tune]={
                "df": tuned,
                "size":len(tuned.index),
                "fp": self.filepath,
                "interval": self.interval,
                "scale": scale,
                "tune_freqs": self.tune_freqs
            }
            self.num_tune += 1
        return tuned

    def tune_multiscale(self, return_each: bool = False, concat_all: bool = False) -> pd.DataFrame | list[int]:
        if not all(( self.filepath, self.interval, type(self.scale[0]) == list )):
            print("bad!"); return -1

        size=0
        for i, scl in enumerate(self.scale):
            tuned = self.tune_single( start_time = (0 if size == 0 else 10*i*size), scale=scl, store_meta = (not concat_all) )

            if return_each:
                yield tuned
            if concat_all:
                if size == 0:
                    out = tuned; size = self.meta[self.num_tune-1]["size"]
                else:
                    out = pd.concat([out, tuned], ignore_index=True)
        if concat_all:
            self.meta[self.num_tune]={
                "df": out,
                "size":len(tuned.index)*len(self.scale),
                "fp": self.filepath,
                "interval": self.interval,
                "scale": self.scale,
                "tune_freqs": self.tune_freqs
            }
            self.num_tune += 1

        if not (return_each or concat_all):
            return range(self.num_tune-(i+1),self.num_tune)

    def write_to_file(self, key: int = 0, outfn: str = None):
        ...

# fp = "/Users/colin/desktop/tuner_misc/swxf/bark/bark.swx"
# prm = {
#     "filepath":fp,
#     "interval":10,
#     "scale":[4,6,8,9,11,1,3],
# }

# scales = [
#     construct_default_scale(n+1, "Major Scale")
#     for n in range(5)]

# t1 = Tuner.from_params(TuningParams(**prm))
# t1.config(scale=scales)
# x= t1.tune_multiscale(return_each=True, concat_all=False)

# tune_cols(fp,10,construct_default_scale(1,'Major Scale'), True)

print(Scale.from_notes(["A#", "C#"]))