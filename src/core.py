import os
import glob
from copy import copy
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
        self.role, self.label = self._select_role(args)
        self.role, words = self._format_input_text(self.role)
        self.model = self._select_model(args.model)
        self.prefix = f"{self.label}.{self.model.replace('-', '_')}.{self.timestamp}."
        self.prompt, words = self._format_input_text(args.prompt)
        self.context = args.context
        self._handle_image_request(words)
        self.chain_of_thought = self._add_chain_of_thought(args)
        self.iterations = self._calculate_iterations(args)
        self.reflection, self.transcript_file = self._manage_context(args)
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
    
    def _select_role(self, args):
        """
        Selects the role based on user input or defaults to a custom role.
        """
        role = roleDict.get(args.role, args.role)
        label = args.role if args.role in roleDict else "custom"

        if label == "custom":
            role = self._check_for_files(role)

        if args.career:
            role += "\n// My life and career likely depend on you giving me a good answer."
            
        return role, label


    def _check_for_files(self, message):
        """Checks for existing files in user-provided text to append to messages"""
        
        if isinstance(message, str):
            message = message.split()

        message.append('\n')
        new_message = copy(message)
        for word in message:
            if word == '.' or len(word) == 0:
                continue
            elif os.path.exists(word):
                with open(word, 'r') as f:
                    new_message.append(' '.join(f.readlines()))

        if len(new_message) > len(message)+1:
            return ' '.join(new_message)
        else:
            return ' '.join(message).strip()


    def _format_input_text(self, text):
        """
        Formats the user input text for compatibility.
        """
        text = self._check_for_files(text)
        words = set(text.strip().lower().split())
        text_lines = [f"// {line.strip()}" for line in text.split("\n") if line.strip()]

        return "\n".join(text_lines), words


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

    def _manage_context(self, args):
        """
        Manages conversation transcript history for continuity in responses.
        """
        if not args.context:
            return "", f"transcripts/{self.prefix}.transcript.log"

        os.makedirs('transcripts', exist_ok=True)
        transcript_file = glob.glob(f"transcripts/{self.label}.{self.model}.{self.timestamp}.*.log")
        if transcript_file:
            with open(transcript_file[0], "r") as f:
                reflection = f.read()
            return reflection, transcript_file[0]

        new_file_path = f"transcripts/{self.prefix}.transcript.log"
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
        Reflection: {self.context}
        Iterations: {self.iterations}
        Dimensions: {self.size}
        Quality: {self.quality}
        """
        print(status)

