#!/usr/bin/env python3

import os
from pathlib import Path

if __name__ == "__main__":
    os.system("pip install -U openai")
    os.system("chmod +x *")
    os.system("chmod +x bin/*")

    libDir = os.path.dirname(os.path.realpath(__file__))
    homeDir = Path.home()

    outStr = "\n\n# >>> Added by ChatGPT CLI assistant >>>\n"
    outStr += f"export PATH=$PATH:{libDir}\n"
    outStr += 'alias gpt="assistant.py"\n'
    outStr += "# <<< Added by ChatGPT CLI assistant <<<\n\n"

    for prfl in ["bashrc", "bash_profile", "zshrc", "bash_aliases"]:
        if os.path.isfile(f"{homeDir}/.{prfl}"):
            with open(f"{homeDir}/.{prfl}", "a") as current:
                current.write(outStr)
            os.system(f". {homeDir}/.{prfl}")

print('\nDone!\n')
