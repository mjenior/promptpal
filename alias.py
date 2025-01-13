#!/usr/bin/env python3

from os import path
from pathlib import Path

def extract_words(file):

    words = set()
    with open(file, "r") as f:
        for line in f:
            words |= set(line.split())

    return words

if __name__ == "__main__":
    aliasStr = 'alias llm="assistant.py'

    # Prompt refinement
    refine = input('Refine user query (1 = True and 0 = False): ')
    if refine == '1':
        aliasStr += f" --refine True"

    # Chain of Thought 
    chain = input('Include Chain-of-Thought reasoning (1 = True and 0 = False): ')
    if chain == '1':
        aliasStr += f" --chain_of_thought True"

    # Verbose output
    verbose = input('Verbose output (1 = True and 0 = False): ')
    if verbose == '1':
        aliasStr += f" --verbose True"

    # Response reflection
    iters = input('Reflection iteration (integer): ')
    try: 
        iters = int(iters)
        aliasStr += f" --iters {int(iters)}"
    except ValueError:
        pass

    # Default role selection
    role = input('Default system role (refer to README): ')
    role = role if role.lower() in ['compbio','cancer','dev','invest','art','rewrite','story'] else ''
    if role != '':
        aliasStr += f" --role {role.lower()}"

    # Compose alias text
    aliasStr = '\n'.join(["\n\n# >>> Added by LLM CLI assistant >>>",
                        f"export PATH=$PATH:{path.dirname(path.realpath(__file__))}",
                        f'{aliasStr} --prompt"',
                        "# <<< Added by LLM CLI assistant <<<\n\n"])
    aliasWords = set(aliasStr.split())
    
    # Add to bash profiles
    found = 0
    for prfl in ["bashrc", "zshrc", "bash_profile", "bash_aliases"]:
        if path.isfile(f"{Path.home()}/.{prfl}"):
            wrds = extract_words(f"{Path.home()}/.{prfl}")
            if len(aliasWords.difference(wrds)) != 0:
                found += 1
                print(f"Alias added to: ~/.{prfl}")
                with open(f"{Path.home()}/.{prfl}", "a") as f:
                    f.write(aliasStr)

    if found > 0:
        print('\nNow you may simply type llm followed by your request in quotations to submit queries using your preferred settings.\n')
