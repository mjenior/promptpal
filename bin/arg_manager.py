
import os
import glob
import argparse

from bin.func import gen_timestamp
from bin.lib import roleDict, modelList, CHAIN_OF_THOUGHT


# Parse user args
def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--prompt', type=str, nargs="+",
                        help='User prompt text')
    parser.add_argument('-r',"--role", type=str, default="assistant",
                        help='Assistant role text')
    parser.add_argument('-m',"--model", type=str, default="gpt-4o-mini", 
                        help='ChatGPT model to interact with')
    parser.add_argument('-c',"--chain_of_thought", type=bool, default=True, 
                        help='Include chain of thought enforcement in user prompt')
    parser.add_argument('-s',"--scripts", type=bool, default=True, 
                        help='Save detected code in responses as individual scripts')
    parser.add_argument('-n',"--name", type=bool, default='script', 
                        help='Optional name extension for scripts created by current query')
    parser.add_argument('-f',"--reflection", default='.', 
                        help='Directory to search for previous chat history files')
    parser.add_argument('-k','--key', type=str, default="system",
                        help='OpenAI API key. Default looks for OPENAI_key env var')
    parser.add_argument('-l',"--dim_l", type=int, default=1024, 
                        help='Length dimension for Dall-e image generation')
    parser.add_argument('-w',"--dim_w", type=int, default=1024, 
                        help='Width dimension for Dall-e image generation')
    parser.add_argument('-q',"--qual", default='standard', 
                        help='Image quality for Dall-e output')
    parser.add_argument('-v',"--verbose", type=bool, default=False, 
                        help='Print all information to StdOut')

    return parser.parse_args()


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
    reflection = ""; modelLbl = model.replace('-','_')

    os.makedirs('history', exist_ok=True)
    try:
        histFile = glob.glob(f"history/{label}.{modelLbl}.*.history.txt")[0]
        with open(histFile, "r") as previous:
            reflection = previous.readlines()
        reflection = " ".join([y.strip() for y in reflection])
    except:
        # Establish new session context tracking
        histFile = f"history/{label}.{modelLbl}.{curr_time}.history.txt"
        with open(histFile, "w") as newFile:
            newFile.write("This is the transcript of an ongoing conversation between you and a user.\n")

    return histFile, reflection


# Get critical variables from user arguments
def manage_arg_vars():

    curr_time = gen_timestamp()

    arguments = get_arguments()

    # Handle OpenAI API key
    openai_api_key(arguments.key)

    # Select role
    role, label = role_select(arguments.role)

    # Select model
    model = arguments.model if arguments.model in modelList else "gpt-4o-mini"

    # Format prompt
    prompt = " ".join(list(arguments.prompt)).strip()
    words = set(prompt.lower().split())

    # Check for image generation request    
    art_check = set(['image','picture','draw','create','paint','painting','illustration'])
    if len(words.intersection(art_check)) > 1 and label != 'artist':
        role = roleDict['artist']; label = "artist"; model = "dall-e-3"
        if arguments.verbose: print(f"Image request detected, switching to Artist system role.")

    # Add Chain of Thought
    cot = 'False'
    if arguments.chain_of_thought and label not in ["artist", "story"]:
        role += CHAIN_OF_THOUGHT; cot ='True'

    # Add reflection prompting from continued previous conversation
    ref = 'False'
    if arguments.reflection:
        histFile, reflection = manage_reflection(model, label, curr_time)
        if reflection != "": ref = 'True'

    # Saving code separately and verbosity
    code = False if arguments.scripts == False else True
    verbose = False if arguments.verbose == False else True

    # Image parameters
    size = f"{arguments.dim_l}x{arguments.dim_w}"
    quality = arguments.qual

    # Run status
    if arguments.verbose: 
        status = '''
        Model: {mdl}
        System role: {lbl}
        Chain of though: {c}
        Reflection: {r}
'''.format(mdl=model, lbl=label, c=cot, r=ref)
        print(status)

    args = {'prompt': prompt, 
            'role': role, 
            'model': model, 
            'label': label, 
            'reflection': reflection, 
            'histFile': histFile, 
            'code': code, 
            'size': size, 
            'quality': quality, 
            'verbose': verbose,
            'timestamp': curr_time}

    return args
