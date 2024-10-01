
import os
import glob
import argparse

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


# Get critical variables from user arguments
def parse_args(arguments, curr_time):

    # Handle OpenAI API key
    if arguments.key == "system":
        try:
            OPENAI_API_KEY=os.environ.get("OPENAI_API_KEY")
            if arguments.verbose: print("\nOpenAI API key found.")
        except: 
            raise Exception("OPENAI_API_KEY env variable not found!")
    else:
        os.environ["OPENAI_API_KEY"] = arguments.key

    # Select role
    try:
        role = roleDict[arguments.role]
        label = arguments.role
    except KeyError:
        role = arguments.role
        label = "custom"

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
    reflection = ""; modelLbl = model.replace('-','_'); ref = 'False'
    if arguments.reflection:
        os.makedirs('history', exist_ok=True)
        try:
            histFile = glob.glob(f"history/{label}.{modelLbl}.*.history.txt")[0]
            with open(histFile, "r") as previous:
                if arguments.verbose: print(f'\nConversation history with found!')
                reflection = previous.readlines()
            reflection = " ".join([y.strip() for y in reflection]); ref = True
        except:
            # Establish new session context tracking
            histFile = f"history/{label}.{modelLbl}.{curr_time}.history.txt"
            with open(histFile, "w") as newFile:
                newFile.write("This is the transcript of an ongoing conversation between you and a user.\n")

    if arguments.verbose: 
        report = '''
        Model: {mdl}
        System role: {lbl}
        Chain of though: {c}
        Reflection: {r}
'''.format(mdl=model, lbl=label, c=cot, r=ref)
        print(report)

    return {'prompt':prompt, 'role':role, 'model':model, 'label':label, 'reflection':reflection, 'histFile':histFile}
