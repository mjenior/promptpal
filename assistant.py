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
import argparse
from openai import OpenAI

from bin.prompts import *
from bin.lib import gen_timestamp, pull_code, ExtDict, modelList


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--prompt', type=str,# nargs='+',
                        help='User prompt text')
    parser.add_argument('-r',"--role", type=str,# nargs='+',
                        default="assistant",
                        help='Assistant role text')
    parser.add_argument('-m',"--model", type=str, default="gpt-4o-mini", 
                        help='ChatGPT model to interact with')
    parser.add_argument('-t',"--thought", type=bool, default=True, 
                        help='Include chain of thought enforcement in user prompt.')
    parser.add_argument('-s',"--save_code", type=bool, default=True, 
                        help='Save detected code in responses as individual scripts.')
    parser.add_argument('-c',"--context", default='.', 
                        help='Directory to search for previous chat history files.')
    parser.add_argument('-a','--api_key', type=str, default="system",
                        help='OpenAI API key. Default looks for OPENAI_API_KEY env var.')
    parser.add_argument('-d',"--dimensions", type=str, default="1024x1024", 
                        help='Image dimensions for Dall-e')
    parser.add_argument('-v',"--verbose", type=bool, default=False, 
                        help='Print all information to StdOut')
    args = parser.parse_args()

    # Get current time
    current = gen_timestamp()

    # Get OpenAI API key
    if args.api_key == "system":
        try:
            OPENAI_API_KEY=os.environ.get("OPENAI_API_KEY")
        except: 
            raise Exception("OPENAI_API_KEY env variable not found!")
    else:
        os.environ["OPENAI_API_KEY"] = args.api_key

    # Select model
    if args.model not in modelList:
        model = "gpt-4o-mini"
        if args.role == "image":
            model = "dall-e-3"
    else:
        model = args.model

    # Format prompt
    prompt = " ".join(list(args.prompt)).strip()
    if args.role == "story":
        prompt = "".join([STORYTIME[0], prompt, STORYTIME[0]])

    # Select role
    if args.role == "story":
        role = STORYTIME
        label = "story"
    elif args.role == "compbio":
        role = COMPBIO
        label = "compbio"
    elif args.role == "investor":
        role = INVESTING
        label = "investor"
    elif args.role == "artist":
        role = ARTIST
        label = "image"
    elif args.role == "assistant":
        role = "You are a helpful AI assistant."
        label = "assistant"
    else:
        role = args.role
        label = "custom"

    # Add Chain of Thought
    if args.thought and label not in ["image","story"]:
        role += COT

    # Check for previous context
    if args.context != False:
        try:
            histFile = glob.glob(f"{args.context}/{label}.{model}.*.context.txt")[0]
            with open(histFile, "r") as previous:
                if args.verbose: print(f'\nConversation history with found!')
                context = previous.readlines()
            context = " ".join([y.strip() for y in context])
        except:
            # Establish current session context tracking
            histFile = f"{label}.{model}.{current}.context.txt"; context = ""
            with open(histFile, "w") as newFile:
                newFile.write("This is a conversation between an AI assistant and a user:\n\n")

    # Assemble query
    query = [{"role": "user", "content": prompt}]
    if len(role) > 0: query.append({"role": "system", "content": role})
    if len(context) > 0: query.append({"role": "assistant", "content": context})

    # Record new context
    continued = open(histFile, "a")
    continued.write(f"system msg to assistant:\n{role}\n\n")
    continued.write(f"user msg:\n{prompt}\n\n")

    # Submit query
    client = OpenAI()
    if label != "image":
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
    outFile = f"{model}.{current}.response.txt"
    if args.verbose: print('\nCurrent response text saved to:', outFile)
    with open(outFile, "w") as outFile:
        outFile.write(message)

    # Check for presence of code
    if args.save_code:
        scripts = pull_code(message, current, ExtDict)
        if args.verbose and len(scripts) > 0:
                print('Code found!')
    
    # Clean up
    continued.close()
    if args.verbose: print('\nDone!\n')

