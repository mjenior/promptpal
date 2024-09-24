
import argparse
from datetime import datetime

from bin.lib import *

# Generate timestamp string
def gen_timestamp():
    timestamp = str(datetime.now()).replace('-','').replace(':','').split()
    timestamp[1] = ''.join(timestamp[1].split('.')[0:-1])
    return '_'.join(timestamp)

# Parse user args
def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--prompt', type=str, nargs="+",
                        help='User prompt text')
    parser.add_argument('-r',"--role", type=str, default="assistant", nargs="+",
                        help='Assistant role text')
    parser.add_argument('-m',"--model", type=str, default="gpt-4o-mini", 
                        help='ChatGPT model to interact with')
    parser.add_argument('-t',"--thought", type=bool, default=True, 
                        help='Include chain of thought enforcement in user prompt.')
    parser.add_argument('-s',"--save_code", type=bool, default=True, 
                        help='Save detected code in responses as individual scripts.')
    parser.add_argument('-c',"--context", default='.', 
                        help='Directory to search for previous chat history files.')
    parser.add_argument('-k','--api_key', type=str, default="system",
                        help='OpenAI API key. Default looks for OPENAI_API_KEY env var.')
    parser.add_argument('-d',"--dimensions", type=str, default="1024x1024", 
                        help='Image dimensions for Dall-e')
    parser.add_argument('-v',"--verbose", type=bool, default=False, 
                        help='Print all information to StdOut')

    return parser.parse_args()

# Get critical variables from user arguments
def translate_args(arguments):
    report = ""

    # Select model
    if arguments.model not in modelList:
        model = "gpt-4o-mini"
        if arguments.role == "artist":
            model = "dall-e-3"
    else:
        model = arguments.model

    # Format prompt
    prompt = " ".join(list(arguments.prompt)).strip()
    if arguments.role == "story":
        prompt = "".join([STORYTIME[0], prompt, STORYTIME[0]])

    # Select role
    if arguments.role == "story":
        role = STORYTIME
        label = "story"
    elif arguments.role == "compbio":
        role = COMPBIO
        label = "compbio"
    elif arguments.role == "developer":
        role = DEVELOPER
        label = "developer"
    elif arguments.role == "investor":
        role = INVESTING
        label = "investor"
    elif arguments.role == "artist":
        role = ARTIST
        label = "artist"
    elif arguments.role == "assistant":
        role = "You are a helpful AI assistant."
        label = "assistant"
    else:
        role = arguments.role
        label = "custom"

    # Check for image generation request
    prompt_wrds = set(prompt.split())
    art_check = set(['image','picture','draw','create','paint','painting','illustration'])
    if len(prompt_wrds.intersection(art_check)) > 1 and label != 'artist':
        role = ARTIST
        label = "artist"
        model = "dall-e-3"
        if arguments.verbose:
            print(f"Image request detected, switching to Artist system role.")
    report += f"Model: {model}\n"
    report += f"System role type: {label}\n"

    # Add Chain of Thought
    if arguments.thought and label not in ["artist","story"]:
        role += COT
        report += f"Chain of Thought: True\n"
    else:
        report += f"Chain of Thought: False\n"

    if arguments.verbose: print(report)

    return prompt, role, model, label


# Find code snippets in responses and save to separate scripts with appropriate file extensions
def pull_code(response, curr_time='0000_0000', extensions=ExtDict):
    code_found = False; code = ''; func = ''; outFiles = []
    lines = response.split('\n')
    for line in lines:
        if len(line.strip()) == 0:
            continue

        elif line.startswith('```') and code_found == False:
            code_found = True
            lang = line.replace('```','').lower().split()[0]
            try:
                ext = extensions[lang]
            except KeyError:
                ext = lang
            codeFile = curr_time + ext
            continue

        elif line.startswith('```') and code_found == True:
            code_found = False
            codeFile = '_'.join([func, codeFile])
            outFiles.append(codeFile)
            if codeFile.startswith('_'): codeFile = codeFile.lstrip('_')
            if len(code.split('\n')) > 2:
                with open(codeFile, "w") as outFile:
                    outFile.write(code)
            code = ''; func = ''
            continue
        
        elif code_found == True:
            code += f"{line}\n"
            if "def " in line:
                func = line.split()[1].split("(")[0].split("_")
                for i, s in enumerate(func):
                    if i >= 1:
                        func[i] = s.capitalize()
                func = "".join(func)
            elif "<- function(" in line:
                func = line.split()[0].split("_")
                for i, s in enumerate(func):
                    if i >= 1:
                        func[i] = s.capitalize()
                func = "".join(func)
        continue

    return outFiles


