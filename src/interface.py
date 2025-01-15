import os
import re
import sys
import random
import requests
from datetime import datetime
from collections import defaultdict

from openai import OpenAI
from src.lib import roleDict, extDict, refineDict

class OpenAIQueryHandler:
    """
    Manages queries for the OpenAI API, including creation, submission, and response processing.
    """

    def __init__(self, 
                model='gpt-4o-mini',
                prompt='',
                verbose=False,
                refine=False,
                chain_of_thought=False,
                code=False,
                logging=False,
                api_key=None,
                seed=None,
                iterations=1,
                image_dimensions='NA',
                image_quality='NA',
                role=None,
                urgent=False,
                unit_testing=False):
        """
        Initialize the handler with default or provided values.
        """
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.model = model
        self.prompt = prompt
        self.verbose = verbose
        self.refine = refine
        self.chain_of_thought = chain_of_thought
        self.code = code
        self.logging = logging
        self.log_text = []
        self.api_key = api_key or self._set_api_key()
        self.seed = seed or self._generate_seed()
        self.iterations = iterations
        self.image_dimensions = image_dimensions
        self.image_quality = image_quality
        self.role = role if role else "assist"
        self.urgent = urgent
        self.unit_testing = unit_testing

        self._setup_logging()
        self._setup_model_and_role()
        self._prepare_query()
    
    # OLD
    #def __init__(self, args):
    #    """
    #    Initialize the handler with variables from parsed arguments.
    #    """
    #    self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    #    self._initialize_args(args)
    #    self._setup_logging()
    #    self._setup_model_and_role(args)
    #    self._prepare_query(args)

    #def _initialize_args(self, args):
    #    """
    #    Sets basic arguments from the user input.
    #    """
    #    self.model = args.model
    #    self.prompt = args.prompt
    #    self.verbose = args.verbose
    #    self.refine = args.refine
    #    self.chain_of_thought = args.chain_of_thought
    #    self.code = args.code
    #    self.logging = args.logging
    #    self.log_text = []

    def _setup_logging(self):
        """
        Prepare logging setup.
        """
        self.log_file = f"logs/{self.timestamp}.transcript.log"
        if self.logging:
            os.makedirs('logs', exist_ok=True)
            with open(self.log_file, "w") as f:
                f.write("New session initiated.\n")

    def _setup_model_and_role(self, args):
        """
        Processes model and role selections.
        """
        self.role, self.label = self._select_role(args)
        self.model, self.base_url = self._select_model(args.model)
        self.api_key = self._set_api_key(args.key)

    def _prepare_query(self, args):
        """
        Prepares the query, including prompt modifications and image handling.
        """
        self._scan_files()
        self._handle_image_request()
        self.iterations = self._calculate_iterations(args)
        self.size, self.quality = self._handle_image_params(args)
        self.seed = args.seed if isinstance(args.seed, int) else self._string_to_binary(args.seed)
        if self.verbose:
            self._report_query_params()

    def _set_api_key(self, key):
        """Sets the OpenAI API key."""
        if key == "system":
            self.api_key = os.getenv("OPENAI_API_KEY", None)
            if self.model == 'deepseek-chat':
                self.api_key = os.getenv("DEEPSEEK_API_KEY")
            if not self.api_key:
                raise EnvironmentError("OPENAI_API_KEY environment variable not found!")
        else:
            self.api_key = key
            env_key = 'DEEPSEEK_API_KEY' if self.model == 'deepseek-chat' else 'OPENAI_API_KEY'
            os.environ[env_key] = self.api_key

    def _select_model(self, model_arg):
        """Validates and selects the model based on user input or defaults."""
        model_to_url = {
            'deepseek-chat': "https://api.deepseek.com",
            'gpt-4o': "https://api.openai.com",
            'gpt-4o-mini': "https://api.openai.com",
            'o1-mini': "https://api.openai.com",
            'o1-preview': "https://api.openai.com",
            'dall-e-3': "https://api.openai.com",
            'dall-e-2': "https://api.openai.com"
        }
        return model_arg.lower() if model_arg.lower() in model_to_url else 'gpt-4o-mini', model_to_url.get(model_arg.lower(), "https://api.openai.com")

    def _select_role(self, args):
        """Selects the role based on user input or defaults."""
        role = roleDict.get(args.role, args.role)
        label = args.role if args.role in roleDict else "custom"
        
        refined_role = self._append_file_scanner(role)
        if self.chain_of_thought:
            refined_role += roleDict['chain']
        refined_role += roleDict['dev']['unit_tests'] if args.unit_testing else ''
        if args.urgent:
            refined_role += "\nMy life or career likely depend on you giving me a high quality answer."
        
        return refined_role, label

    def _append_file_scanner(self, message):
        """Scans files in message and appends their contents."""
        if isinstance(message, list):
            message = ' '.join(message)
        words = set(message.split())
        appended_message, new_words = self._scan_directories_and_files(words)
        return appended_message, words.union(new_words)

    def _scan_directories_and_files(self, words):
        """Scan for existing files in user-provided text to append to messages."""
        new_message = ''
        new_words = set()
        for word in words:
            word = word.rstrip('.!?:;')
            if os.path.isfile(word):
                new_message += self._read_file_contents(word)
            elif len(word) > 2 and os.path.exists(word) and '/' in word:
                new_message += self._read_directory_contents(word)
        return new_message, new_words

    def _read_file_contents(self, filename):
        """Reads the contents of a given file."""
        with open(filename, 'r') as handle:
            return ' '.join([x.strip() for x in handle.readlines()])

    def _read_directory_contents(self, dirname):
        """Reads contents of files in a directory."""
        new_message = ''
        for file_name in os.listdir(dirname):
            new_message += self._read_file_contents(os.path.join(dirname, file_name))
        return new_message

    def _handle_image_request(self):
        """Adjusts role and model for image generation requests."""
        art_keywords = {'create', 'generate', 'image', 'picture', 'draw', 'paint', 'painting', 'illustration'}
        photo_keywords = {'create', 'generate', 'photo', 'photograph'}
        words = self.prompt.split()

        if len(set(words) & art_keywords) > 1:
            self.role = roleDict['art']["prompt"]
            self.label = "art"
            self.model = "dall-e-3"
        elif len(set(words) & photo_keywords) > 1:
            self.role = roleDict['photo']["prompt"]
            self.label = "photo"
            self.model = "dall-e-3"

    def _calculate_iterations(self, args):
        """Determines the number of response iterations."""
        if self.role == 'refine' and args.iters == 1:
            return args.iters + 2
        return args.iters

    def _handle_image_params(self, args):
        """Sets image dimensions and quality parameters."""
        if self.label in {"art", "photo"}:
            dims, qual = self._validate_image_params(args.dim, args.qual, self.model)
            if self.label == "photo":
                qual = "hd"
            return dims, qual
        return "NA", "NA"

    @staticmethod
    def _validate_image_params(dims, qual, model):
        """Validates image dimensions and quality for the model."""
        valid_dims = {
            'dall-e-3': ['1024x1024', '1792x1024', '1024x1792'],
            'dall-e-2': ['1024x1024', '512x512', '256x256']
        }
        if model in valid_dims and dims.lower() not in valid_dims[model]:
            dims = '1024x1024'
        quality = 'hd' if qual.lower() in {'h', 'hd', 'high', 'higher', 'highest'} else 'standard'
        return dims, quality

    def _report_query_params(self):
        """Reports the current query configuration."""
        print(self._generate_status())
        if self.logging:
            self.log_text.append(self._generate_status())

    def _generate_status(self):
        """Generate status message."""
        status = f"""
System parameters:
    Model: {self.model}
    Role: {self.role}
    Chain of Thought: {self.chain_of_thought}
    Prompt Refinement: {self.refine}
    Reflection iterations: {self.iterations}
    Time stamp: {self.timestamp}
    Seed: {self.seed}
    Logging: {self.logging}
    """
        if 'dall-e' in self.model:
            status += f"""Image dimensions: {self.size}
    Image quality: {self.quality}
    """
        return status

    def submit_query(self):
        """Submits the query to OpenAI's API and processes the response."""
        if self.label not in ["artist", "photo"]:
            self._process_text_response()
        else:
            self._process_image_response()
        token_report = self._gen_token_report()
        self.log_text.append(token_report)
        if self.verbose:
            print(token_report)
        if self.logging:
            self.save_chat_transcript()

    def _process_text_response(self):
        """Processes text-based responses from OpenAI's chat models."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self._assemble_query(),
            n=self.iterations,
            seed=self.seed
        )
        message = self._condense_iterations(response)
        self._update_token_count(response)
        self._handle_response_logging(message)
        

    def _process_image_response(self):
        """Processes image generation requests using OpenAI's image models."""
        os.makedirs('images', exist_ok=True)
        response = self.client.images.generate(
            model=self.model, prompt=self.prompt,
            n=1, size=self.size, quality=self.quality
        )
        revised_prompt = response.data[0].revised_prompt
        self._update_token_count(response)
        self._log_and_print(f"\nRevised initial prompt:\n{revised_prompt}")
        image_data = requests.get(response.data[0].url).content
        image_file = f"images/{self.prefix}.image.png"
        with open(image_file, 'wb') as outFile:
            outFile.write(image_data)
        self._log_and_print(f"\nGenerated image saved to: {image_file}\n")

    def _assemble_query(self):
        """Assembles the query dictionary for the API request."""
        if self.refine:
            self.prompt = self._refine_prompt()
            if 'refactor' in self.prompt.lower() or 'rewrite' in self.prompt.lower():
                if len(self.added_query.strip()) > 0:
                    self.prompt += "\n\nImprove the following:\n"
                    self.prompt += self.added_query
            self._log_and_print(f"\n\nRefined query prompt:\n{self.prompt}")
        
        return [{"role": "user", "content": self.prompt},
                {"role": "system", "content": self.role}]

    def _gen_token_report(self):
        """Generates report string for overall cost of the query."""
        prompt_cost, completion_cost = 'Unknown model rate', 'Unknown model rate'
        total_tokens = self.tokens['prompt'] + self.tokens['completion']
        total_cost = 'Unknown model rate'
        rates = {
            'gpt-4o': (2.5, 10),
            'gpt-4o-mini': (0.150, 0.600),
            'o1-mini': (3, 12),
            'o1-preview': (15, 60),
            'dall-e-3': (2.5, 0.040),
            'dall-e-2': (2.5, 0.040)
        }
        if self.model in rates:
            prompt_rate, completion_rate = rates.get(self.model)
            prompt_cost = self._calculate_cost(self.tokens['prompt'], prompt_rate)
            completion_cost = self._calculate_cost(self.tokens['completion'], completion_rate)
            total_cost = round(prompt_cost + completion_cost, 5)
            total_cost = "<< $0.01" if total_cost < 0.01 else f"$ {total_cost}"
        return (f"\nTotal tokens generated: {total_tokens}  ({total_cost})"
                f"\n    Prompt (i.e. input): {self.tokens['prompt']}  ({prompt_cost})"
                f"\n    Completion (i.e. output): {self.tokens['completion']}  ({completion_cost})")

    def save_chat_transcript(self):
        """Saves the current response text to a file if specified."""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write("\n".join(self.log_text))
        self._log_and_print(f"\nSaving conversation transcript text to: {self.log_file}")

    def _condense_iterations(self, api_response):
        """Condenses multiple API responses into a single coherent response."""
        api_responses = [r.message.content.strip() for r in api_response.choices]
        if len(api_responses) > 1:
            condensed = self.client.chat.completions.create(
                model=self.model,
                seed=self.seed,
                messages=[
                    {"role": "system", "content": roleDict['rewrite']},
                    {"role": "user", "content": "\n\n".join(api_responses)}
                ])
            self._update_token_count(condensed)
            return condensed.choices[0].message.content.strip()
        return api_responses[0]

    def _refine_prompt(self, actions=['expand', 'amplify'], temperature=0.7):
        """Refines an LLM prompt using specified rewrite actions."""
        self._log_and_print("\nRefining initial prompt...")
        actions.update(set(re.sub(r'[^\w\s]', '', word).lower() for word in self.prompt.split() if word))
        action_str = "; ".join(f"{a}; {refineDict[a]}" for a in actions)
        updated_role = self.role + "\nDo not respond directly to the provided request. Your primary task is to refine or improve the user prompt."
        updated_prompt = self.prompt + refineDict['prompt'] + action_str
        refined = self.client.chat.completions.create(
            model=self.model, temperature=temperature, n=self.iterations,
            seed=self.seed,
            messages=[
                {"role": "system", "content": updated_role},
                {"role": "user", "content": updated_prompt}
            ])
        self._update_token_count(refined)
        return self._condense_iterations(refined)

    def _update_token_count(self, response):
        """Updates token count for prompt and completion."""
        self.tokens['prompt'] += response.usage.prompt_tokens
        self.tokens['completion'] += response.usage.completion_tokens

    def _log_and_print(self, message):
        """Logs and prints the provided message if verbose."""
        if self.verbose:
            print(message)
        if self.logging:
            self.log_text.append(message)

    def _calculate_cost(self, tokens, perM, dec=5):
        """Calculates approximate cost (USD) of LLM tokens generated to a given decimal place"""
        return round((tokens * perM) / 1e6, dec)

    def _string_to_binary(self,input_string, output_str=False, shuffle=False, maxsize=True):
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
