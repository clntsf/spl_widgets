import os
modules_to_alias=["update_widgets","widgets_help","gorilla_clean","stk_swx","tuner"]

def main():
    os.system("pip -q install spl_widgets --upgrade")
    zprofile = f"{os.getenv('HOME')}/.zprofile"
    with open(zprofile,"r") as reader:

        lines = reader.readlines()
        newlines = []
        
        for line in lines: 
            if "spl_widgets" not in line:
                newlines.append(line)
        
        for module in modules_to_alias:
            alias_str = f'alias {module}="python3 -m spl_widgets {module}" \n'
            newlines.append(alias_str)

    with open(zprofile, "w") as writer:
        writer.writelines(newlines)

if __name__ == "__main__": main()