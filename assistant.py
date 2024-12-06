#!/usr/bin/env python3

import argparse

from src.core import QueryManager
from src.api_handler import OpenAIInterface


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
context : bool
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

def parse_arguments():
    """
    Parses command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Manage and execute OpenAI queries.")
    parser.add_argument("-p", "--prompt", type=str, required=True, help="User prompt text or path to a .txt file.")
    parser.add_argument("-r", "--role", type=str, default="assistant", help="Assistant role text.")
    parser.add_argument("-m", "--model", type=str, default="gpt-4o-mini", help="ChatGPT model.")
    parser.add_argument("-t", "--chain_of_thought", default=True, help="Enable chain of thought reasoning.")
    parser.add_argument("-c", "--code", default=True, help="Save detected code in responses.")
    parser.add_argument("-x", "--context", default=True, help="Use previous chat transcripts for context.")
    parser.add_argument("-k", "--key", type=str, default="system", help="OpenAI API key.")
    parser.add_argument("-d", "--dim", type=str, default="1024x1024", help="Image dimensions.")
    parser.add_argument("-q", "--qual", type=str, default="standard", help="Image quality.")
    parser.add_argument("-i", "--iterations", type=int, default=1, help="Number of response iterations.")
    parser.add_argument("-v", "--verbose", default=True, help="Enable verbose output.")
    parser.add_argument("-s", "--silent", default=False, help="Suppress output.")
    parser.add_argument("-j", "--career", default=False, help="How important is this request?")
    return parser.parse_args()


def main():
    """
    Main function for parsing inputs, managing queries, and handling API interactions.
    """
    # Parse arguments
    args = parse_arguments()
   
    # Initialize the user argument and query manager
    query_manager = QueryManager(args)

    # Initialize the OpenAI API handler and submit query
    query_handler = OpenAIInterface(query_manager)
    query_handler.submit_query(query_manager)
    

if __name__ == "__main__":
    main()
