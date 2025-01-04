import os
import re
import glob
from datetime import datetime

from src.lib import roleDict, chatgptList, roleNames, unit_tests

  
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
        for attr in ["silent", "code", "log", "model", "refine", "context"]:
            setattr(self, attr, getattr(args, attr))
        self.context = True if self.refine == True
        self.log_text = []

        # Processed arguments
        self.role, self.label = self._select_role(args)
        self.role, words = self._format_input_text(text=self.role, type='role')
        self.model, self.base_url = self._select_model(args.model)
        self.api_key = self._set_api_key(args.key)
        self.prefix = f"{self.label}.{self.model.replace('-', '_')}.{self.timestamp}."
        self.prompt, words = self._format_input_text(text=args.prompt, refine=args.refine, type="query")
        self._handle_image_request(words)
        self.chain_of_thought = self._add_chain_of_thought(args)
        self.iterations = self._calculate_iterations(args)
        self.reflection, self.transcript_file = self._manage_context(args)
        self.size, self.quality = self._handle_image_params(args)

        if not self.silent:
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
        
        if mod in chatgptList:
            pass
        elif mod == 'deepseek-chat':
            url="https://api.deepseek.com"
        else:
            mod = "gpt-4o-mini"

        return mod, url
    
    def _select_role(self, args):
        """
        Selects the role based on user input or defaults to a custom role.
        """
        role = roleDict.get(args.role, args.role)
        label = args.role if args.role in roleDict.keys() else "custom"

        if label == "custom":
            role, wrds, check = self._file_text_scanner(role)
            if not self.silent:
                print(f'\nCustom system role:\n{role}\n')
            if self.log:
                self.log_text.append(f'\nCustom system role:\n{role}\n')
        else:
            if not self.silent:
                print(f'\nUsing default system role: {roleNames[label]}')
            if self.log:
                self.log_text.append(f'\nUsing default system role: {roleNames[label]}')

        # Add unit testing to prompt
        if args.unit_testing and args.role != 'dev':
            role += unit_tests

        # Add urgency if necessary
        if args.career:
            role += "\n// My life and career likely depend on you giving me a good answer."
            
        return role, label

    def _file_text_scanner(self, message):
        """Checks for existing files in user-provided text to append to messages"""
        
        if isinstance(message, str):
            sentences = [x.strip() for x in message.splitlines() if len(x.strip()) >= 1]
        else:
            sentences = message
        
        # Isolate a cleanup words
        words = []
        for sentence in sentences:
            words += [re.sub(r'[^\w\s]','', word).lower() for word in sentence.split() if len(word) >= 1]

        found = False
        for word in set(words):
            if os.path.isfile(word):
                found = True
                with open(word, 'r') as handle:
                    sentences += [x.strip() for x in handle.readlines() if len(x.strip()) >= 1]

        return sentences, words, found

    def _format_input_text(self, text, refine=False, type="query"):
        """
        Formats the user input text for interpretability.
        """
        check = True
        while check:
            text, wrds, check = self._file_text_scanner(text)

        full_text = "\n".join([f"// {line.capitalize().replace('// ','')}" for line in text]) # Join with new line syntax
        full_text += '.' if full_text[-1] not in ['.','!','?'] else '' # Add puncuation if needed

        if full_text != text:
            if not self.silent:
                print(f'\nReformatted {type} text:\n{full_text}')
            if self.log:
                self.log_text.append(f'\nReformatted {type} text:\n{full_text}')


        return full_text, set(wrds)

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
        if self.role in {'refine', 'invest'} and args.iters == 1:
            return args.iters + 2
        return args.iters

    def _manage_context(self, args):
        """
        Manages conversation transcript history for continuity in responses.
        """
        if not args.context:
            return "", f"transcripts/{self.prefix}.transcript.log"

        os.makedirs('transcripts', exist_ok=True)
        transcript_file = glob.glob(f"transcripts/{self.label}.{self.model}.*.log")
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

    def _report_query_params(self):
        """
        Prints the current status of the query configuration.
        """
        status = f"""
System parameters:
    Model: {self.model}
    Role: {roleNames[self.label]}
    Chain of Thought: {self.chain_of_thought}
    Prompt Refinement: {self.refine}
    Reflection: {self.context}
    Iterations: {self.iterations}
    Dimensions: {self.size}
    Quality: {self.quality}
"""
        print(status)

        if self.log:
            self.log_text.append(status)

