#!/usr/bin/env python3

import argparse

from src.core import OpenAIQueryHandler

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
    LLM to use in queiries.
    Default is gpt-4o
chain_of_thought : bool
    Include chain of thought enforcement in user prompt.
    Default is False
unit_testing : bool
    Write comprehesive unit tests for any generated code.
    Default is False
refine : bool
    Automatically refine user prompt to improve query specificity.
    Default is False
seed : str or int
    Set moded seed for more deterministic reponses
    Converts strings into binary-like equivalent, constrained by max system bit size
    Default is based on the pinnacle code from Freakazoid
dim : str
    Dimensions for Dall-e image generation
    Default is 1024x1024
qual : str
    Image quality for Dall-e image
    Default int standard
iters : int
    WANRING: More testing required for reliability
    Number of responses to generate and parse for model reflection
    Default is 1
key : str
    User-specific OpenAI API key. 
    Default looks for pre-set OPENAI_API_KEY environmental variable.
verbose : bool
    Adds all ptocessing tex to stdout.
    Default is False
urgent : bool
    Add urgency to the request [UNTESTED].
    Default is False
"""

def parse_arguments():
    """
    Parses command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Manage and execute OpenAI queries.")
    parser.add_argument("-p", "--prompt", type=str, default="What is the answer to life the universe and everything?", help="User prompt text or path to a .txt file.")
    parser.add_argument("-r", "--role", type=str, default="assist", help="Assistant role text.")
    parser.add_argument("-m", "--model", type=str, default="gpt-4o", help="LLM to use in queiries.")
    parser.add_argument("-c", "--chain_of_thought", type=bool, default=False, help="Enable chain of thought reasoning.")
    parser.add_argument("-f", "--refine", type=bool, default=False, help="Enable automated input prompt improvement.")
    parser.add_argument("-x", "--code", type=bool, default=False, help="Save detected code in responses to separate scripts.")
    parser.add_argument("-e", "--seed", default=r'"@[=g3,8d]\&fbb=-q]/hk%fg"', help="Set moded seed for more deterministic reponses, accepts integer or strings")
    parser.add_argument("-u", "--unit_testing", type=bool, default=False, help="Write comprehesive unit tests for any generated code.")
    parser.add_argument("-k", "--key", type=str, default="system", help="OpenAI API key.")
    parser.add_argument("-d", "--dim", type=str, default="1024x1024", help="Image dimensions.")
    parser.add_argument("-q", "--qual", type=str, default="standard", help="Image quality.")
    parser.add_argument("-i", "--iters", type=int, default=1, help="Number of response iterations for reflection.")
    parser.add_argument("-v", "--verbose", type=bool, default=False, help="Adds all processing text to stdout.")
    parser.add_argument("-l", "--logging", type=bool, default=False, help="Save full conversation log.")
    return parser.parse_args()


def main():
    """
    Main function for parsing inputs, managing queries, and handling API interactions.
    """
    # Parse arguments
    args = parse_arguments()
   
    # Initialize the user argument and query manager
    llm_api = OpenAIQueryHandler(
        model=args.model,
        prompt=args.prompt,
        verbose=args.verbose,
        refine=args.refine,
        chain_of_thought=args.chain_of_thought,
        code=args.code,
        logging=args.logging,
        api_key=args.key,
        seed=args.seed,
        iterations=args.iters,
        role=args.role,
        image_dimensions=args.dim,
        image_quality=args.qual,
        unit_testing=args.unit_testing)

    # Submit query and parse response
    llm_api.request()
    

if __name__ == "__main__":
    main()
