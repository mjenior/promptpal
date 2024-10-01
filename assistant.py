#!/usr/bin/env python3
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

import requests
from openai import OpenAI

from bin.func import gen_timestamp, pull_code
from bin.arg_manager import get_arguments, parse_args



if __name__ == "__main__":
    args = get_arguments()
    current = gen_timestamp()

    # Get important vars from arguments
    varDict = parse_args(args, current)

    # Assemble query
    query = [{"role": "user", "content": varDict['prompt']}]
    if len(varDict['role']) > 0: query.append({"role": "system", "content": varDict['role']})
    if len(varDict['reflection']) > 0: query.append({"role": "assistant", "content": varDict['reflection']})

    # Record current context
    continued = open(varDict['histFile'], "a")
    continued.write(f"system msg to assistant:\n{varDict['role']}\n\n")
    continued.write(f"user msg:\n{varDict['prompt']}\n\n")

    # Submit query
    client = OpenAI()
    if varDict['label'] != "artist":
        response = client.chat.completions.create(model=varDict['model'], messages=query)
        message = response.choices[0].message.content
        outType = 'response'
    else:
        response = client.images.generate(model=varDict['model'], prompt=varDict['prompt'], n=1, 
                                          size=f"{args.dim_l}x{args.dim_w}", quality=args.qual)
        message = response.data[0].revised_prompt
        outType = 'description'
        image_url = response.data[0].url
        image_data = requests.get(image_url)
        #image_file = image_url.split("/")[-1]
        image_file = f"{varDict['model'].replace('-','')}.{current}.image.png"
        if args.verbose: print('\nGenerated image saved to:', image_file)
        with open(image_file,'wb') as outFile:
            outFile.write(image_data.content)

    # Save current revised prompt text
    continued.write(f"assistant msg:\n{message}\n\n")
    if args.verbose: print(message)
    outFile = f"{varDict['label']}.{varDict['model'].replace('-','')}.{current}.{outType}.txt"
    if args.verbose: print('\nCurrent response text saved to:', outFile)
    with open(outFile, "w") as outFile:
        outFile.write(message)

    # Check for presence of code
    if args.scripts:
        scripts = pull_code(message)
        if args.verbose and len(scripts) > 0:
                print('\nCode identified and saved separately.')
    
    # Clean up
    continued.close()
    if args.verbose: print('\nDone!\n')

