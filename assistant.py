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
    Built-in shortcut options include: compbio, investor, artist, story
    Default is "You are a helpful AI assistant."
model : str
    ChatGPT model to interact with
    Default is gpt-4o-mini
thought : bool
    Include chain of thought enforcement in user prompt.
    Default is True
save_code : bool
    Save detected code in responses as individual scripts.
    Default is True
context : str
    Directory to search for previous chat history files.
    May also be set to False
    Default is current working directory
dimensions : str
    Image dimensions for Dall-e image generation
    Default is 1024x1024
api_key : str
    User-specific OpenAI API key. 
    Default looks for pre-set OPENAI_API_KEY environmental variable.
verbose : bool
    Print all information to StdOut
    Default is False
"""

import os
import glob
import requests
from openai import OpenAI

from bin.func import gen_timestamp, get_arguments, translate_args, pull_code


if __name__ == "__main__":
    args = get_arguments()
    current = gen_timestamp()

    # Get OpenAI API key
    if args.api_key == "system":
        try:
            OPENAI_API_KEY=os.environ.get("OPENAI_API_KEY")
        except: 
            raise Exception("OPENAI_API_KEY env variable not found!")
    else:
        os.environ["OPENAI_API_KEY"] = args.api_key

    # Get important vars from arguments
    prompt, role, model, role_lbl = translate_args(args)

    # Check for previous context
    histFile = f"{role_lbl}.{model}.{current}.context.txt"; context = ""
    if args.context != False:
        try:
            histFile = glob.glob(f"{args.context}/{role_lbl}.{model}.*.context.txt")[0]
            with open(histFile, "r") as previous:
                if args.verbose: print(f'\nConversation history with found!')
                context = previous.readlines()
            context = " ".join([y.strip() for y in context])
        except:
            # Establish new session context tracking
            with open(histFile, "w") as newFile:
                newFile.write("This is a conversation between an AI assistant and a user:\n\n")

    # Assemble query
    query = [{"role": "user", "content": prompt}]
    if len(role) > 0: query.append({"role": "system", "content": role})
    if len(context) > 0: query.append({"role": "assistant", "content": context})

    # Record current context
    continued = open(histFile, "a")
    continued.write(f"system msg to assistant:\n{role}\n\n")
    continued.write(f"user msg:\n{prompt}\n\n")

    # Submit query
    client = OpenAI()
    if role_lbl != "artist":
        response = client.chat.completions.create(model=model, messages=query)
        message = response.choices[0].message.content
    else:
        response = client.images.generate(model=model, prompt=prompt, n=1, 
                                          size=args.dimensions, quality="standard")
        message = response.data[0].revised_prompt
        image_url = response.data[0].url
        image_data = requests.get(image_url)
        image_file = image_url.split("/")[-1]
        if args.verbose: print('\nGenerated image saved to:', image_file)
        with open(image_file,'wb') as outFile:
            outFile.write(image_data.content)

    # Save current revised prompt text
    continued.write(f"assistant msg:\n{message}\n\n")
    if args.verbose: print(message)
    outFile = f"{role_lbl}.{model}.{current}.response.txt"
    if args.verbose: print('\nCurrent response text saved to:', outFile)
    with open(outFile, "w") as outFile:
        outFile.write(message)

    # Check for presence of code
    if args.save_code:
        scripts = pull_code(message, current)
        if args.verbose and len(scripts) > 0:
                print('Code found!')
    
    # Clean up
    continued.close()
    if args.verbose: print('\nDone!\n')

