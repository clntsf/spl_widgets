from os import system

def lighttheme_force():                                 # force python app gui to light theme (optional, for tuner)
    print("Forcing light theme for Python GUI apps")
    system("defaults write org.python.python NSRequiresAquaSystemAppearance -bool yes")