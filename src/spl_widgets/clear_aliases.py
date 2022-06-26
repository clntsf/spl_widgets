import os

def main():
    zprofile = f"{os.getenv('HOME')}/.zprofile"
    with open(zprofile,"r") as reader:
        lines = reader.readlines()

    newlines = filter(lambda ln: ("spl_widgets" not in ln), lines)
    with open(zprofile, "w") as writer:
        writer.writelines(newlines)

if __name__ == "__main__": main()