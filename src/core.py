import os
import glob
from datetime import datetime

from src.lib import roleDict, modelList

            
class QueryManager:
    """
    Manages the creation and formatting of queries for the OpenAI API.
    """
    
    def __init__(self, args):
        """
        Initialize the QueryManager with critical variables from parsed arguments.
        """
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        self._set_api_key(args.key)
        self.role, self.label = self._select_role(args.role)
        self.model = self._select_model(args.model)
        self.prefix = f"{self.label}.{self.model.replace('-', '_')}.{self.timestamp}."
        self.prompt, words = self._format_prompt(args.prompt)
        self._handle_image_request(words)
        self.chain_of_thought = self._add_chain_of_thought(args)
        self.iterations = self._calculate_iterations(args)
        self.reflection, self.history_file = self._manage_history(args)
        self.size, self.quality = self._handle_image_params(args)
        self.model = args.model

        # Additional booleans
        self.verbose = args.verbose
        self.silent = args.silent
        self.code = args.code
        self.log = args.log

        if not self.silent:
            self._print_status()

    def _set_api_key(self, key):
        """
        Sets the OpenAI API key.
        """
        if key == "system":
            self.api_key = os.environ.get("OPENAI_API_KEY")
            if not self.api_key:
                raise EnvironmentError("OPENAI_API_KEY environment variable not found!")
        else:
            self.api_key = key
            os.environ["OPENAI_API_KEY"] = self.api_key

    def _select_model(self, model_arg):
        """
        Validates and selects the model based on user input or defaults to `gpt-4o-mini`.
        """
        return model_arg.lower() if model_arg.lower() in modelList else "gpt-4o-mini"
    
    def _select_role(self, role_arg):
        """
        Selects the role based on user input or defaults to a custom role.
        """
        role = roleDict.get(role_arg, role_arg)
        label = role_arg if role_arg in roleDict else "custom"
        if isinstance(role, list) and role[0].endswith('.txt'):
            with open(role[0], 'r') as file:
                role = "\n".join(file.readlines())
        return role, label


    def _check_for_files(self, prompt):
        
        if isinstance(prompt, str):
            prompt = prompt.split()

        new_prompt = ''
        for word in prompt:
            if os.path.exists(word):
                with open(word, 'r') as f:
                    new_prompt += ' '.join(f.readlines())

        if new_prompt != '':
            return new_prompt
        else:
            return " ".join(prompt)


    def _format_prompt(self, prompt):
        """
        Formats the user prompt text for compatibility.
        """
        if isinstance(prompt, list) and prompt[0].endswith('.txt'):
            with open(prompt[0], 'r') as file:
                prompt = file.read()
        else:
            prompt = self._check_for_files(prompt)
        words = set(prompt.strip().lower().split())
        prompt_lines = [f"// {line.strip()}" for line in prompt.split("\n") if line.strip()]
        return "\n".join(prompt_lines), words

    def _handle_image_request(self, words):
        """
        Detects image generation requests and adjusts role and model accordingly.
        """
        art_keywords = {'create', 'generate', 'image', 'picture', 'draw', 'paint', 'painting', 'illustration'}
        photo_keywords = {'create', 'generate', 'photo', 'photograph'}
        if len(words & art_keywords) > 1:
            self.role = roleDict['art']
            self.label = "art"
            self.model = "dall-e-3"
        elif len(words & photo_keywords) > 1:
            self.role = roleDict['photo']
            self.label = "photo"
            self.model = "dall-e-3"

    def _add_chain_of_thought(self, args):
        """
        Adds chain-of-thought reasoning to the role if applicable.
        """
        if args.chain_of_thought and self.label not in {"art", "story", "photo"}:
            self.role += roleDict['chain']
            return "True"
        else:
            return "False"

    def _calculate_iterations(self, args):
        """
        Determines the number of response iterations based on user input and role.
        """
        if self.role in {'refine', 'invest'}:
            return args.iterations + 3
        return args.iterations

    def _manage_history(self, args):
        """
        Manages conversation history for continuity in responses.
        """
        if not args.history and self.role != 'refine':
            return "", f"conversations/{self.prefix}.conversation.log"

        os.makedirs('conversations', exist_ok=True)
        history_file = glob.glob(f"conversations/{self.label}.{self.model}.{self.timestamp}.*.log")
        if history_file:
            with open(history_file[0], "r") as file:
                reflection = file.read()
            return reflection, history_file[0]

        new_file_path = f"conversations/{self.prefix}.conversation.log"
        with open(new_file_path, "w") as file:
            file.write("New session initiated.\n")
        return "", new_file_path

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

    def _print_status(self):
        """
        Prints the current status of the query configuration.
        """
        status = f"""
        Model: {self.model}
        Role: {self.label}
        Chain of Thought: {self.chain_of_thought}
        Reflection: {bool(self.reflection)}
        Iterations: {self.iterations}
        Dimensions: {self.size}
        Quality: {self.quality}
        """
        print(status)

