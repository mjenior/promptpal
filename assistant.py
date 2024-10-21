#!/usr/bin/env python3

from src.core import assemble_query, submit_query
from src.i_o import get_arguments, manage_arg_vars

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
    Several built-in options are available, refer to README for details
    Default is assistant
model : str
    ChatGPT model to interact with
    Default is gpt-4o-mini
chain_of_thought : bool
    Include chain of thought enforcement in user prompt.
    Default is False
code : bool
    Save detected code in responses as individual scripts.
    Default is True
history : bool
    Search for previous chat history for reflection prompting.
    Default is True
dim : str
    Dimensions for Dall-e image generation
    Default is 1024x1024
qual : str
    Image quality for Dall-e output
    Default int standard
iterations : int
    Number of responses to generate and parse for highest quality
    Default is 1
key : str
    User-specific OpenAI API key. 
    Default looks for pre-set OPENAI_API_KEY environmental variable.
verbose : bool
    Print all additional information to StdOut
    Default is False
silent : bool
    Silences all StdOut
    Default is False
log : bool
    Save response to query as a separate text file in current working directory
    Default is False
"""


if __name__ == "__main__":
    
    # Get important vars from arguments
    args = get_arguments()
    varDict = manage_arg_vars(args)

    # Assemble query
    varDict['query'] = assemble_query(varDict)

    # Submit query and parse response
    if varDict['silent'] == False:
        print('Thinking...\n')
    response = submit_query(varDict)
    if varDict['silent'] == False:
        print(response)

    # Record current context
    if args.history:
        try:
            outFile = open(varDict['histFile'], "a")
        except FileNotFoundError:
            outFile = open(varDict['histFile'], "w")

        outFile.write(f"""
<user msg>
{varDict['prompt']}
</user msg>

<system msg to assistant>
{varDict['role']}
</system msg to assistant>
""")
        outFile.close()

    if varDict['silent'] == False:
        print('\nDone!\n')
