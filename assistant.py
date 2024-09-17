#!/usr/bin/env python
"""
ChatGPT API script for conversation with comp bio assistant in command line

* Requires OPENAI_API_KEY set as environmental variable

Usage:
python assistant.py "Write a script to read fastq files."
"""

import os
import glob
import argparse
from openai import OpenAI

from bin.prompts import *
from bin.lib import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a','--api_key', type=str,
                        default="system",
                        help='OpenAI API key. Default looks for OPENAI_API_KEY env var.')
    parser.add_argument('-p','--prompt', nargs='+', type=str,
                        help='User prompt text')
    parser.add_argument('-r',"--role", type=str,
                        default="You are a helpful AI assistant.",
                        help='Assistant role text')
    parser.add_argument('-v',"--verbose", default=False, type=bool, 
                        help='Print information to StdOut')
    parser.add_argument('-s',"--size", default="1024x1024", type=str,
                        help='Image size for Dall-e, deafilt is 1024x1024')
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
    model = "gpt-4o-mini"
    if args.role == "image": model = "dall-e-3"

    # Format prompt
    prompt = " ".join(list(args.prompt)).strip()
    if args.role == "story":
        prompt = "".join([STORYTIME[0], prompt, STORYTIME[0]])

    # Select role
    if args.role == "story":
        role = "You are a good storyteller with a large knowledge of movies from the last 50 years."
        label = "story"
    elif args.role == "compbio":
        role = COMPBIO + COT
        label = "compbio"
    elif args.role == "invest":
        role = INVESTING + COT
        label = "invest"
    elif args.role == "image":
        role = ARTIST
        label = "image"
    else:
        role = args.role + COT
        label = "custom"

    # Check for previous context
    histFiles = glob.glob(f"{label}.{model}.*.history.txt"); history = ""
    for x in histFiles:
        with open(x, "r") as previous:
            if args.verbose: print(f'\nConversation history with {x.split("_")[0]} found!')
            history += " ".join([x.strip() for x in previous.readlines()])
    
    # Establish current session history tracking
    histFile = f"{label}.{model}.{current}.history.txt"
    with open(histFile, "w") as newFile:
        newFile.write(f"This is a conversation between an AI assistant and a user:\n\n")

    # Assemble query
    query = [{"role": "user", "content": prompt}]
    if len(role) > 0: query.append({"role": "system", "content": role})
    if len(history) > 0: query.append({"role": "assistant", "content": history})

    # Record new history
    continued = open(histFile, "a")
    continued.write(f"system msg to assistant:\n{role}\n\n")
    continued.write(f"user msg:\n{prompt}\n\n")

    # Submit query
    client = OpenAI()
    if label != "image":
        response = client.chat.completions.create(model=model, messages=query)
        message = response.choices[0].message.content
        continued.write(f"assistant msg:\n{message}\n\n")

        # Save current response text
        if args.verbose: print(message)
        outFile = f"{model}.{current}.response.txt"
        if args.verbose: print('\nFull response saved to:', outFile)
        with open(outFile, "w") as outFile:
            outFile.write(message)
    else:
        response = client.images.generate(model=model, prompt=prompt, n=1, 
                                          size=args.size, quality="standard")
        image_url = response.data[0].url
        revised_prompt = response.data[0].revised_prompt
        continued.write(f"assistant revised prompt:\n{revised_prompt}\n\n")

        # Save current revised ptompt text
        if args.verbose: print(revised_prompt)
        outFile = f"{model}.{current}.revised_prompt.txt"
        if args.verbose: print('\nFull revised prompt saved to:', outFile)
        with open(outFile, "w") as outFile:
            outFile.write(revised_prompt)

    # Check for presence of code
    if label == "compbio":
        scripts = pull_code(message, current)
        if args.verbose and len(scripts) > 0:
                print('Code found!')
    
    continued.close()
    if args.verbose: print('\nDone!\n')

