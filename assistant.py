#!/usr/bin/env python3

from bin.func import assemble_query, submit_query
from bin.arg_manager import get_arguments, manage_arg_vars

"""
ChatGPT API script for conversation with AI assistant in command line

* Requires OPENAI_API_KEY set as environmental variable

USAGE:
python assistant.py --prompt "Write a script to read fastq files."

REQUIRED
prompt : str
    User prompt text, request that is sent to ChatGPT

OPTIONAL
role : str
    System role text, predefines system behaviours or type of expertise
    Built-in shortcut options include: compbio, investor, artist, storyteller, and developer
    Default is assistant
model : str
    ChatGPT model to interact with
    Default is gpt-4o-mini
chain_of_thought : bool
    Include chain of thought enforcement in user prompt.
    Default is True
scripts : bool
    Save detected code in responses as individual scripts.
    Default is True
reflection : bool
    Search for previous chat history for reflection prompting.
    Default is True
dim_l : int
    Length dimension for Dall-e image generation
    Default is 1024
dim_w : int
    Width dimension for Dall-e image generation
    Default is 1024
qual : str
    Image quality for Dall-e output
    Default is standard
key : str
    User-specific OpenAI API key. 
    Default looks for pre-set OPENAI_API_KEY environmental variable.
verbose : bool
    Print all information to StdOut
    Default is False
"""


if __name__ == "__main__":
    
    # Get important vars from arguments
    args = get_arguments()
    varDict = manage_arg_vars(args)

    # Assemble query
    varDict['query'] = assemble_query(varDict)

    # Submit query and parse response
    response = submit_query(varDict)

    # Record current context
    with open(varDict['histFile'], "a") as continued:
        continued.write(f"""
<user msg>
{varDict['prompt']}
</user msg>

<system msg to assistant>
{varDict['role']}
</system msg to assistant>
""")
