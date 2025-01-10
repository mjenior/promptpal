import os
import re
import sys
import random
from copy import copy
from datetime import datetime

from src.lib import roleDict, chatgptList, unit_tests, extDict

  
class QueryManager:
    """
    Manages the creation and formatting of queries for the OpenAI API.
    """
    
    def __init__(self, args):
        """
        Initialize the QueryManager with critical variables from parsed arguments.
        """
        # Time stamp
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Simple arguments
        self.code = True
        self.logging = True
        for attr in ["model", "prompt","silent", "refine", "chain_of_thought"]:
            setattr(self, attr, getattr(args, attr))

        # Processed arguments
        self.log_text = []
        self.role, self.label = self._select_role(args)
        added_role, words = self._file_scanner(message=self.role, prompt_type='role')
        if len(added_role) > 0:
            self.role += added_role
        if self.chain_of_thought == True: 
            self.role += roleDict['chain']
        self.model, self.base_url = self._select_model(args.model)
        self.api_key = self._set_api_key(args.key)
        self.prefix = f"{self.label}.{self.model.replace('-', '_')}.{self.timestamp}"
        self.added_query, words = self._file_scanner(message=args.prompt, prompt_type='query')
        if len(self.added_query) > 0:
            self.prompt += self.added_query
        self._handle_image_request(words)
        self.iterations = self._calculate_iterations(args)
        self.size, self.quality = self._handle_image_params(args)
        if isinstance(args.seed, int):
            self.seed = args.seed
        else:
            self.seed = string_to_binary(args.seed)

        # Manage reporting
        self.log_file = f"logs/{self.prefix}.transcript.log"
        if self.logging == True:
            self._begin_logging()
        if self.silent == False:
            self._report_query_params()

    def _set_api_key(self, key):
        """
        Sets the OpenAI API key.
        """
        if key == "system":
            self.api_key = os.environ.get("OPENAI_API_KEY")
            if self.model == 'deepseek-chat':
                self.api_key = os.environ.get("DEEPSEEK_API_KEY")                
            
            if not self.api_key:
                raise EnvironmentError("OPENAI_API_KEY environment variable not found!")
        else:
            self.api_key = key
            if self.model == 'deepseek-chat':
                os.environ["DEEPSEEK_API_KEY"] = self.api_key
            else:
                os.environ["OPENAI_API_KEY"] = self.api_key

    def _select_model(self, model_arg):
        """
        Validates and selects the model based on user input or defaults to `gpt-4o-mini`.
        """
        url="https://api.openai.com"
        mod = model_arg.lower()
        
        if mod == 'deepseek-chat': # ready if new deepseek models become available
            url="https://api.deepseek.com"
        elif mod not in chatgptList:
            mod = "gpt-4o-mini"

        return mod, url
    
    def _select_role(self, args):
        """
        Selects the role based on user input or defaults to a custom role.
        """
        role = roleDict.get(args.role, args.role)
        label = args.role if args.role in roleDict.keys() else "custom"

        if label == "custom":
            self.role_name = "Custom"
            role, wrds, check = self._file_text_scanner(role)
            if self.silent == False:
                print(f'\nCustom system role:\n{role}\n')
            if self.logging == True:
                self.log_text.append('\nCustom system role:\n' + role + '\n')
        else:
            self.role_name = role['name']
            role = role["prompt"]

        # Add unit testing to prompt
        if args.unit_testing == True and args.role != 'dev':
            role += unit_tests

        # Add urgency if necessary
        if args.urgent == True:
            role += "\nMy life or career likely depend on you giving me a high quality answer."
            
        return role, label

    def _file_scanner(self, message, prompt_type='query'):
        """Checks for existing files in user-provided text to append to messages"""
        
        if isinstance(message, list):
            message = ' '.join(message)

        # Isolate words
        words = set([word for word in message.split() if len(word) >= 1])

        # Parse for files
        new_words = copy(words)
        new_message = ''
        for word in words:
            for p in ['.', '!', '?' ,':' , ';', ',']:
                if word.endswith(p):
                    word = word.rstrip(p)
            if os.path.isfile(word):
                if self.silent == False:
                    print(f'\nFile found and contents added to {prompt_type} prompt:', word)
                with open(word, 'r') as handle:
                    new_message += ' '.join([x for x in handle.readlines() if len(x.strip()) >= 1])
                    new_words |= set([w for w in message.split() if len(w) >= 1])
            
            # Parse directories if needed
            elif len(word) > 2 and os.path.exists(word) and '/' in word:
                if self.silent == False:
                    print('\nDirectory found and parsing content:')
                
                code_files = []
                for file_name in os.listdir(word):
                    ext = '.' + file_name.split('.')[-1]
                    if ext in set(extDict.keys()):
                        if self.silent == False:
                            print('\tFile found and contents added to {prompt_type} prompt:', word)
                        with open(file_name, 'r') as handle:
                            new_message += ' '.join([x for x in handle.readlines() if len(x.strip()) >= 1])
                            new_words |= set([w for w in message.split() if len(w) >= 1])

        return new_message, new_words

    def _handle_image_request(self, words):
        """
        Detects image generation requests and adjusts role and model accordingly.
        """
        art_keywords = {'create', 'generate', 'image', 'picture', 'draw', 'paint', 'painting', 'illustration'}
        photo_keywords = {'create', 'generate', 'photo', 'photograph'}
        if len(words & art_keywords) > 1:
            self.role = roleDict['art']["prompt"]
            self.label = "art"
            self.model = "dall-e-3"
        elif len(words & photo_keywords) > 1:
            self.role = roleDict['photo']["prompt"]
            self.label = "photo"
            self.model = "dall-e-3"

    def _calculate_iterations(self, args):
        """
        Determines the number of response iterations based on user input and role.
        """
        if self.role in {'refine', 'invest'} and args.iters == 1:
            return args.iters + 2
        return args.iters

    def _begin_logging(self):
        """
        Manages conversation transcript history for continuity in responses.
        """
        os.makedirs('logs', exist_ok=True)
        with open(self.log_file, "w") as f:
            f.write("New session initiated.\n")
        
    def _handle_image_params(self, args):
        """
        Validates and sets image dimensions and quality parameters.
        """
        if self.label in {"art", "photo"}:
            dims, qual = self._validate_image_params(args.dim, args.qual, self.model)
            if self.label == "photo":
                qual = "hd"
            return dims, qual
        return "NA", "NA"

    @staticmethod
    def _validate_image_params(dims, qual, model):
        """
        Validates the image dimensions and quality for the given model.
        """
        valid_dims = {
            'dall-e-3': ['1024x1024', '1792x1024', '1024x1792'],
            'dall-e-2': ['1024x1024', '512x512', '256x256']
        }
        if model in valid_dims and dims.lower() not in valid_dims[model]:
            dims = '1024x1024'
        quality = 'hd' if qual.lower() in {'h', 'hd', 'high', 'higher', 'highest'} else 'standard'
        return dims, quality

    def _report_query_params(self):
        """
        Prints the current status of the query configuration.
        """
        status = f"""
System parameters:
    Model: {self.model}
    Role: {self.role_name}
    Chain of Thought: {self.chain_of_thought}
    Prompt Refinement: {self.refine}
    Relection iterations: {self.iterations}
    Time stamp: {self.timestamp}
    Seed: {self.seed}
    Logging: {self.logging}
    """
        if 'dall-e' in self.model:
            status += f"""  Image dimensions: {self.size}
    Image quality: {self.quality}
    """
        print(status)

        if self.logging == True:
            self.log_text.append(status)

def string_to_binary(input_string, output_str=False, shuffle=False, maxsize=True):
    """Create a binary-like variable from a string for use a random seed"""

    # Convert all characters in a str to ASCII values and then to 8-bit binary
    binary = [format(ord(char), '08b') for char in input_string]

    # Shuffle the list if needed
    binary = ''.join(random.shuffle(binary)) if shuffle else ''.join(binary)

    # Constrain length if needed as seed
    binary = binary[0:len(str(sys.maxsize))] if maxsize else binary

    # Convert to needed data type
    binary = binary if output_str else int(binary)

    return binary
