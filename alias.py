#!/usr/bin/env python3

import os
from pathlib import Path

if __name__ == "__main__":

    aliasStr = 'alias gpt="assistant.py'

    # Prompt refinement
    refine = input('Refine user query (1 = True and 0 = False): ')
    refine = True if refine == '1' else False
    aliasStr += f" --refine {refine}"

    # Verbose output
    verbose = input('Verbose output (1 = True and 0 = False): ')
    verbose = True if verbose == '1' else False
    aliasStr += f" --verbose {verbose}"

    # Response reflection
    iters = input('Reflection iteration (integer): ')
    try: 
        iters = int(iters) 
    except ValueError::
        iters = 1
    aliasStr += f" --iters {iters}"

    # Default role selection
    roles = ['compbio','cancer','dev','invest','art','rewrite','story']
    role = input('Default system role (refer to README): ')
    role = role if role in roles else 'assist'
    aliasStr += f" --role {role}"

    # Compose alias text
    outStr = ["\n\n# >>> Added by LLM CLI assistant >>>"]
    outStr.append(f"export PATH=$PATH:{os.path.dirname(os.path.realpath(__file__))}")
    outStr.append(f'{aliasStr} --prompt"')
    outStr.append("# <<< Added by LLM CLI assistant <<<\n\n")
    
    # Add to bash profiles
    homeDir = Path.home()
    for prfl in ["bashrc", "bash_profile", "zshrc", "bash_aliases"]:
        if os.path.isfile(f"{homeDir}/.{prfl}"):
            with open(f"{homeDir}/.{prfl}", "a") as current:
                current.write('\n'.join(outStr))

print('\nAdded to bash profile! Now you can simply type gpt followed by your request in quotations to get your desired set up.\n')
