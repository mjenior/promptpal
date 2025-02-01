#!/usr/bin/env python3

import os
from pathlib import Path


def extract_unique_words(file_path):
    """
    Extract and return a set of unique words from the specified file.
    """
    with open(file_path, "r") as file:
        return {word for line in file for word in line.split()}

def extend_command_string(new_arg, response, current_command):
    """
    Extends the current command string with the new argument.
    """
    current_command += f" --{new_arg} "
    current_command += "True" if response == "1" else "False"
    return current_command

#-------------------------------------------------------------------------------#

if __name__ == "__main__":
    print("\nBlank responses will automatically set to default values.\n")
    
    ### Command assembly
    commandStr = 'python cli.py'

    ## Complex args

    # Determine alias string
    alias = input('Preferred alias string (Default: llmapi): ')
    alias = alias if alias != '' else 'llmapi'

    # Preferred model
    model = input('Preferred model (refer to README): ')
    models = ['deepseek-chat','gpt-4o','gpt-4o-mini','o1-mini','o1-preview','dall-e-2']
    commandStr += f" --model {model.lower()}" if model.lower() in models else ''

    # Default role selection
    role = input('Default system role (refer to README for shortcuts): ')
    commandStr += f" --role {role.lower()}" if role != '' else ''

    # Add API-key manually
    api_key = input('API-key (Corresponds with model, blank defaults to system env var): ')
    commandStr += f" --api_key {api_key}" if api_key != '' else ''

    # Random seed
    seed = input('Random seed (int or str, floats treated as str): ')
    commandStr += f" --seed {seed}" if seed != '' else ''

    # Response iterations
    iters = input('Response iterations (Integer): ')
    try: 
        commandStr += f" --iterations {int(iters)}"
    except ValueError:
        pass

    ## Boolean args

    # Prompt refinement
    commandStr = extend_command_string("refine_prompt", input('Refine user query (1 = True and 0 = False): '), commandStr)
    commandStr = extend_command_string("glyph_prompt", input('Representative glyph association (1 = True and 0 = False): '), commandStr)
    commandStr = extend_command_string("chain_of_thought", input('Include Chain-of-Thought reasoning (1 = True and 0 = False): '), commandStr)
    commandStr = extend_command_string("save_code", input('Save code snippets to scripts (1 = True and 0 = False): '), commandStr)
    commandStr = extend_command_string("scan_files", input('Scan prompt for readable files (1 = True and 0 = False): '), commandStr)
    commandStr = extend_command_string("verbose", input('Verbose output (1 = True and 0 = False): '), commandStr)
    commandStr = extend_command_string("logging", input('Chat logging (1 = True and 0 = False): '), commandStr)
    
    #-------------------------------------------------------------------------------#

    # Compose alias text versions
    commandStr += ' --prompt'
    aliasStr = f'alias {alias}="{commandStr}"'
    profileStr = '\n'.join(["\n# >>> Added by LLM API assistant >>>",
                        f"export PATH=$PATH:{os.path.dirname(os.path.realpath(__file__))}",
                        aliasStr,
                        "# <<< Added by LLM API assistant <<<\n\n"])
    aliasWords = set(profileStr.split())

    # Add to current environment
    os.environ.update({alias: commandStr})
    print("\nAlias added to current environment\n")
    
    # Add to bash profiles
    found = 0
    for prfl in ["bashrc", "zshrc", "bash_profile", "bash_aliases"]:
        if os.path.isfile(f"{Path.home()}/.{prfl}"):
            wrds = extract_unique_words(f"{Path.home()}/.{prfl}")
            if len(aliasWords.difference(wrds)) != 0:
                found += 1
                print(f"Updated ~/.{prfl} with command")
                with open(f"{Path.home()}/.{prfl}", "a") as f:
                    f.write(profileStr)

print(f"""
Now you may simply type {alias} in the terminal followed by your request in quotations to submit queries using your preferred settings.

Full command for reference:
{commandStr}
""")
