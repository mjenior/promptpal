
import os
import glob
import argparse

from src.core import gen_timestamp
from src.lib import roleDict, modelList, CHAIN_OF_THOUGHT, RESPONSES


# Parse user args
def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--prompt', type=str, nargs="+",
                        help='User prompt text')
    parser.add_argument('-r',"--role", type=str, default="assistant",
                        help='Assistant role text')
    parser.add_argument('-m',"--model", type=str, default="gpt-4o-mini", 
                        help='ChatGPT model to interact with')
    parser.add_argument('-t',"--chain_of_thought", type=bool, default=True, 
                        help='Include chain of thought enforcement in user prompt')
    parser.add_argument('-c',"--code", type=bool, default=False, 
                        help='Save detected code in responses as individual scripts')
    parser.add_argument('-g',"--history", default=False, 
                        help='Directory to search for previous chat log files')
    parser.add_argument('-k','--key', type=str, default="system",
                        help='OpenAI API key. Default looks for OPENAI_key env var')
    parser.add_argument('-d',"--dim", type=str, default="1024x1024", 
                        help='Dimension for Dall-e image generation')
    parser.add_argument('-q',"--qual", default='standard', 
                        help='Image quality for Dall-e output')
    parser.add_argument('-i',"--iterations", type=int, default=3, 
                        help='Number of responses to generate and parse for highest quality')
    parser.add_argument('-v',"--verbose", type=bool, default=False, 
                        help='Print all additional information to StdOut')
    parser.add_argument('-s',"--silent", type=bool, default=False, 
                        help='Silences all StdOut')
    parser.add_argument('-n',"--current", type=bool, default=False, 
                        help='Save response to current query as a separate text file')
    
    return parser.parse_args()


def image_params(dims, qual, model, verbose):

    if model == 'dall-e-3' and dims.lower() not in ['1024x1024','1792x1024','1024x1792']:
        dimensions = '1024x1024'
        if verbose: print(f"\nDesired dimensions not available for {model}. Defaulting to 1024x1024.")
    elif model == 'dall-e-2' and dims.lower() not in ['1024x1024','512x512','256x256']:
        dimensions = '1024x1024'
        if verbose: print(f"\nDesired dimensions not available for {model}. Defaulting to 1024x1024.")
    else:
        dimensions = dims.lower()

    if qual.lower() in ['h','hd','high','higher','highest']:
        quality = 'hd'
        if verbose: print(f"\nHigher (HD) generated image quality set.")
    else:
        quality = 'standard'

    return dimensions, quality


def openai_api_key(key):
    # Handle OpenAI API key
    if key == "system":
        try:
            OPENAI_API_KEY=os.environ.get("OPENAI_API_KEY")
        except: 
            raise Exception("OPENAI_API_KEY env variable not found!")
    else:
        os.environ["OPENAI_API_KEY"] = key


def role_select(arg):
    try:
        role = roleDict[arg]
        label = arg
    except KeyError:
        role = arg
        label = "custom"

    return role, label


def manage_reflection(model, label, curr_time):
    """Parses existing converation logs to better inform current responses"""
    reflection = ""; modelLbl = model.replace('-','_')

    try:
        histFile = glob.glob(f"conversations/{label}.{modelLbl}.*.conversation.log")[0]
        with open(histFile, "r") as previous:
            reflection = previous.readlines()
        reflection = " ".join([y.strip() for y in reflection])
    except:
        # Establish new session context tracking
        histFile = f"conversations/{label}.{modelLbl}.{curr_time}.conversation.log"
        with open(histFile, "w") as newFile:
            newFile.write("This is the transcript of an ongoing conversation between you and a user leading up to the current request.\n")

    return histFile, reflection


def format_query_text(text):
    """Reformat input text to JSON-compatible"""

    # Fix some whitespace
    if type(text) is list:
        text = " ".join(text)
    text = text.strip()
    words = set(text.lower().split())

    text = ["\n// " + x.strip() for x in text.split("\n") if len(x.strip()) > 0]
    prompt = "".join(text)
    for x in [".", "?", "!"]:
        prompt = f"{x}\n// ".join(prompt.split(x))
    prompt = prompt.replace('// //','//')
    
    return prompt, words


def response_check(iterations, respStr=RESPONSES):
    """Add multiple response evaluation and summary to prompts"""
    if iterations > 1:
        promptStr = f"// Generate {iterations} completely seperate responses to the supplied prompt."
        promptStr += respStr
    else:
        promptStr = ""

    return promptStr


# Get critical variables from user arguments
def manage_arg_vars(arguments):
    """Manages and reformats user inputs"""

    curr_time = gen_timestamp()

    # Handle OpenAI API key
    openai_api_key(arguments.key)

    # Select role
    role, label = role_select(arguments.role)

    # Select model
    model = arguments.model.lower() if arguments.model.lower() in modelList else "gpt-4o-mini"

    # Format prompt
    prompt, words = format_query_text(arguments.prompt)

    # Check for image generation request    
    art_check = set(['image','picture','draw','create','paint','painting','illustration'])
    if len(words.intersection(art_check)) > 1 and label != 'artist':
        role = roleDict['artist']; label = "artist"; model = "dall-e-3"
        if arguments.verbose: print("\nImage request detected, switching to Artist system role.")

    # Add Chain of Thought
    cot = 'False'
    if arguments.chain_of_thought and label not in ["artist", "story"]:
        role += CHAIN_OF_THOUGHT; cot ='True'
    
    # Add response evaluation
    role += response_check(arguments.iterations)

    # Add reflection prompting from continued previous conversation
    reflect = 'False'; reflection = ""
    os.makedirs('conversations', exist_ok=True)
    histFile = f"conversations/{label}.{model}.{curr_time}.conversation.log"
    if arguments.history:
        histFile, reflection = manage_reflection(model, label, curr_time)
        if reflection != "": reflect = 'True'

    # Image parameters
    size, quality = image_params(arguments.dim, arguments.qual, model, arguments.verbose)

    # Run status
    status = '''
    Model: {mdl}
    System role: {lbl}
    Chain of thought: {c}
    Reflection: {r}'''.format(mdl=model, lbl=label, c=cot, r=reflect)

    if arguments.iterations > 1:
        status += '''
    Iterations: {resp}
'''.format(resp=arguments.iterations)

    if 'dall-e' in model:
        status += '''
    Dimensions: {dim}
    Quality: {qual}'''.format(dim=size, qual=quality)
    
    if arguments.silent == False:
        print(f"{status}\n")

    vars = {'prompt': prompt, 
            'role': role, 
            'model': model, 
            'label': label, 
            'reflection': reflection, 
            'histFile': histFile, 
            'code': arguments.code, 
            'size': size, 
            'quality': arguments.qual, 
            'verbose': arguments.verbose,
            'silent': arguments.silent,
            'current': arguments.current,
            'timestamp': curr_time}

    return vars
