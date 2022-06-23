import os

def main():
    os.system("pip3 -q install spl_widgets --upgrade")
    os.system("pip -q install spl_widgets --upgrade")

    zprofile = f"{os.getenv('HOME')}/.zprofile"
    with open(zprofile,"r") as reader:
        lines = reader.readlines()

    newlines = list(filter(lambda ln: ("spl_widgets" not in ln), lines))
    newlines.append('alias runmod="python3 -m spl_widgets"\n')

    with open(zprofile, "w") as writer:
        writer.writelines(newlines)

if __name__ == "__main__": main()