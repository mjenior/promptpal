#!/usr/bin/env python
"""
ChatGPT API script for conversation with comp bio assistant in command line

Requires OPENAI_API_KEY set as environmental variable

Usage:
python assistant.py Write a script to read fastq files.
"""

import os
import pickle
import argparse
from openai import OpenAI
from datetime import datetime

def timestamp():
    timestamp = str(datetime.now()).replace('-','.').replace(':','.').split()
    timestamp[1] = '.'.join(timestamp[1].split('.')[0:-1])
    return '_'.join(timestamp)

path = os.path.dirname(os.path.realpath(__file__))
with open(f"{path}/extDict.pkl", "rb") as inFile:
    extDict= pickle.load(inFile)

OPENAI_API_KEY=os.environ.get("OPENAI_API_KEY")
IMAGE_GENERATION_ENDPOINT="https://api.openai.com/v1/images/generations"

compBio = """// You are software engineer and quantitative computational biologist, with PhD-level expertise across bioinformatics and systems biology.
// You have a particular interest in statistical modeling and machine learning for high-throughput analysis of large dimensional datasets. 
// Your programming languages of choice are python and R, you also have a deep understanding of Docker.
// The code you write should be clear, modular and well documented. Any function or API call made should exist."""
artist = """// Do not generate more than 1 image at a time, and your default output image resolution is 1024x1024 at standard quality unless told otherwise.
// Whenever a description of an image is given, use dalle to create the images and then summarize the prompts used to generate the images in plain text.
// Always mention the image type (photo, oil painting, watercolor painting, illustration, cartoon, drawing, vector, render, etc.) at the beginning of the caption. Unless the caption suggests otherwise, make at least 1--2 of the 4 images photos.
// Your choices should be grounded in reality. For example, all of a given OCCUPATION should not be the same gender or race.
// Don't alter memes, fictional character origins, or unseen people. Maintain the original prompt's intent and prioritize quality.
// Do not create any imagery that would be offensive.
// Silently modify descriptions that include names or hints or references of specific people or celebrity by carefully selecting a few minimal modifications to substitute references to the people with generic descriptions that don't divulge any information about their identities, except for their genders and physiques.
// Modify such prompts even if you don't know who the person is, or if their name is misspelled (e.g. "Barake Obema").
// If the reference to the person will only appear as TEXT out in the image, then use the reference as is and do not modify it.
// The prompt must intricately describe every part of the image in concrete, objective detail. THINK about what the end goal of the description is, and extrapolate that to what would make satisfying images.
// All descriptions sent to dalle should be a paragraph of text that is extremely descriptive and detailed. Each should be more than 3 sentences long."""


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('request', metavar='UserRequest', nargs='+', type=str,
                        help='User request text')
    parser.add_argument("--prompt", default="bioinformatics", type=str,
                        help='Assistant prompt text')
    parser.add_argument("--history", default=True, type=bool,
                        help='Attempt to use previous conversation entries as context')
    parser.add_argument("--verbose", default=False, type=bool, 
                        help='Print information to StdOut')
    parser.add_argument("--code", default=True, type=bool, 
                        help='Save code to seperate script(s)')
    args = parser.parse_args()
    
    client = OpenAI()

    if args.prompt == "bioinformatics":
        prompt = compBio
        model = "gpt-4o-mini"

    elif args.prompt == "artist":
        prompt = artist
        model = "dall-e-3"
    else:
        prompt = str(args.prompt)
        model = "gpt-4o-mini"

    query = [{"role": "system", "content": prompt}]

    # Check for previous context
    model = "".join(filter(lambda x: x.isalnum() or x.isspace(), args.model))
    if args.history:
        histFile = f"{model}_history.txt"
        if os.path.isfile(histFile):
            with open(histFile, "r") as previous:
                if args.verbose: print(f'\nConversation history with {args.model} found!')
                history = previous.readlines()
                history = " ".join([x.strip() for x in history])
                query.append({"role": "assistant", "content": history})
        else:
            with open(histFile, "w") as newFile:
                newFile.write(f"This is a conversation between an AI assistant and a user:\n\n")

        # Submit query
        with open(histFile, "a") as continued:
            newFile.write(f"system msg to assistant:\n{args.prompt}\n\n")

            request = " ".join(list(args.request))
            continued.write(f"user msg:\n{request}\n\n")
            query.append({"role": "user", "content": request})

            response = client.chat.completions.create(model=args.model, messages=query)
            message = response.choices[0].message.content
            continued.write(f"assistant msg:\n{message}\n\n")

    # Capture response
    if args.verbose: print(message)
    outFile = f"response_{timestamp()}.txt"
    if args.verbose: print('\nFull response saved to:', outFile)
    with open(outFile, "w") as outFile:
        outFile.write(message)

    # Save code to seperate scripts
    if args.code:
        code_found = False
        code = ''
        func = ''
        lines = message.split('\n')
        for line in lines:
            if len(line.strip()) == 0:
                continue

            elif line.startswith('```') and code_found == False:
                code_found = True
                lang = line.replace('```','').lower()
                try:
                    ext = extDict[lang]
                except KeyError:
                    ext = '.txt'
                codeFile = f"{lang}_{timestamp()}{ext}"
                continue

            elif line.startswith('```') and code_found == True:
                code_found = False
                codeFile = '_'.join([func, codeFile])
                if codeFile.startswith('_'): codeFile = codeFile.lstrip('_')
                if len(code.split('\n')) > 2:
                    if args.verbose: print(f"{lang} code saved to: {codeFile}")
                    with open(codeFile, "w") as outFile:
                        outFile.write(code)
                code = ''
                func = ''
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

    if args.verbose: print('\nDone!\n')

