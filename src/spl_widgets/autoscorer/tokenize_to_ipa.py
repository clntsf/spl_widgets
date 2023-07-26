import re
from spl_widgets.util.sqlite_db import SQLiteDB
import pkg_resources

database_fp = pkg_resources.resource_filename("spl_widgets", "data/cmudict.sqlite")
dba = SQLiteDB(database_fp, silent=True)

# https://en.wikipedia.org/wiki/ARPABET#Symbols
phonemes = {
  "AA": "ɑ",
  "AE": "æ",
  "AH": "ʌ",
  "AO": "ɔ",
  "AW": "ɑʊ",
  "AX": "ə",
  "AXR": "ɚ",
  "AY": "ɑi",
  "EH": "ɛ",
  "ER": "ɝ",
  "EY": "ɛi",
  "IH": "ɪ",
  "IX": "ɨ",
  "IY": "i",
  "OW": "oʊ",
  "OY": "ɔi",
  "UH": "ʊ",
  "UW": "u",
  "UX": "ʉ",
  "B": "b",
  "CH": "tʃ",
  "D": "d",
  "DH": "ð",
  "DX": "ɾ",
  "EL": "l̩",
  "EM": "m̩",
  "EN": "n̩",
  "F": "f",
  "G": "ɡ",
  "HH": "h",
  "JH": "dʒ",
  "K": "k",
  "L": "l",
  "M": "m",
  "N": "n",
  "NG": "ŋ",
  "NX": "ɾ̃",
  "P": "p",
  "Q": "ʔ",
  "R": "ɹ",
  "S": "s",
  "SH": "ʃ",
  "T": "t",
  "TH": "θ",
  "V": "v",
  "W": "w",
  "WH": "ʍ",
  "Y": "j",
  "Z": "z",
  "ZH": "ʒ"
}

def get_arpabet(word: str) -> list[list[str]]|str:
    data = dba.execute_read_query(f"SELECT transcriptions FROM phones WHERE word = '{word}'")
    
    if data == []:                          # invalid word
        # ('*'*word.isalpha()) only flags all-alpha invalid words, not just floating punctuation
        # invalid all-alpha words must be flagged so they are ignored by the scorer
        return ('*'*word.isalpha()) + word
    
    transcriptions = eval(data[0][0])
    return transcriptions

def to_arpabet(sentence: str, keep_punct: bool = True) -> list[str]:

    arpa_words = []
    PUNCT_RE = r"(\W*)(\w*)(\W*)"

    for wd in sentence.split(" "):

        if keep_punct:
            prepunct, word, postpunct = re.match(PUNCT_RE, wd).groups(0)
        else:
            prepunct = postpunct = ""
            word = re.sub(PUNCT_RE, r"\2", wd)

        word_arpa = get_arpabet(word.lower())

        # sanitize valid ARPAbet words (and convert AH0 to schwa)
        if isinstance(word_arpa, list):                         # word exists in dictionary
            word_arpa = word_arpa[0]                            # get only the first transcription
        else:
            word_arpa = [word_arpa]

        word_arpa = filter(None, [prepunct, *word_arpa, postpunct, " "])
        arpa_words.extend(word_arpa)

    return arpa_words[:-1]  # remove last added space to simplify the logic

def to_arpabet_all(sentence: str, keep_punct: bool = True) -> list[list[str]]:
    arpa_sentences: list[list[str]] = []
    PUNCT_RE = r"(\W*)(\w*)(\W*)"

    for wd in sentence.split(" "):

        if keep_punct:
            prepunct, word, postpunct = re.match(PUNCT_RE, wd).groups(0)
        else:
            prepunct = postpunct = ""
            word = re.sub(PUNCT_RE, r"\2", wd)

        poss_transcriptions = get_arpabet(word.lower())

        # sanitize valid ARPAbet words (and convert AH0 to schwa)
        if isinstance(poss_transcriptions, list):                         # word exists in dictionary
            poss_arpas = [                                                          # format the arpa transcription for each possible transcription
                [ *filter(None, [prepunct, *transcription_arpa, postpunct, " "]) ]
                for transcription_arpa in poss_transcriptions
            ]
            if arpa_sentences == []:
                arpa_sentences = [arpa for arpa in poss_arpas]
            else:
                arpa_sentences = [s+arpa for s in arpa_sentences for arpa in poss_arpas]

        else:   # not in CMU dict, add to end of each sentence 
            poss_transcriptions = [*filter(None, [prepunct, poss_transcriptions, postpunct, " "])]
            for s in arpa_sentences:
                s.extend(poss_transcriptions)

    return [n[:-1] for n in arpa_sentences] # remove last added space retroactively to simplify the logic

def arpa_to_ipa(arpa: list[str]):
    return [phonemes.get(tk,tk) for tk in arpa]

def str_to_ipa(sentence: str, keep_punct: bool = False) -> list[str]:

    """
    Convert the passed string to IPA using our custom conversion functions

    Parameters
    ----------
        @param sentence ( str ): the user's input
        @param keep_punct ( bool ): whether to keep the sentence's original punctuation

    Returns
    -------
        @returns list[str]: the converted IPA as tokens

    ---

    Summary
    -------
    In essence, this function takes the passed input and passes each word through
    CMUDict's database to retrieve a potential ARPAbet transcription for it, handling
    also unrecognized input. We then tokenize this output and map the tokens to their
    IPA equivalents to yield the IPA-transcribed sentence in token form.

    NB: each (valid) token corresponds to exactly one phoneme. although
    some tokens (diphthongs) are multi-character, they are considered to
    be a single phoneme and so are grouped as an individual token
    """

    arpa_words = to_arpabet(sentence, keep_punct)
    return arpa_to_ipa(arpa_words)

# breaks up an idealized IPA string into tokens (might not be perfect, but it's definitely
# mostly good, and worst case we just switch to passing them as a lists of tokens)
def tokenize_ipa(ipa_str: str) -> list[str]:
    tokens = sorted(phonemes.values(), key=len, reverse=True)   # prioritize finding diphthongs
    token_re = rf"({'|'.join(tokens)}|\s|.)"

    return re.findall(token_re, ipa_str)