import os
import re
import sys
import random
import requests
from subprocess import call
from datetime import datetime
from collections import defaultdict

from openai import OpenAI
from llm_api.lib import roleDict, refineDict, extDict

class OpenAIQueryHandler:
    """
    Manages queries for the OpenAI API, including creation, submission, and response processing.
    """

    def __init__(self, 
                model='gpt-4o-mini',
                verbose=False,
                refine=False,
                chain_of_thought=False,
                code=False,
                logging=False,
                api_key="system",
                seed=42,
                iterations=1,
                image_dimensions='NA',
                image_quality='NA',
                role="assist",
                unit_testing=False):
        """
        Initialize the handler with default or provided values.
        """
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.model = model
        self.verbose = verbose
        self.refine = refine
        self.chain_of_thought = chain_of_thought
        self.code = code
        self.logging = logging
        self.log_text = []
        self.api_key = api_key or self._set_api_key()
        self.iterations = iterations
        self.image_dimensions = image_dimensions
        self.image_quality = image_quality
        self.role = role 
        self.unit_testing = unit_testing
        self.tokens = {'prompt':0, 'completion':0}
        self.seed = seed if isinstance(seed, int) else self._string_to_binary(seed)

        self._setup_model_and_role()

        self.prefix = f"{self.label}.{self.model.replace('-', '_')}.{self.timestamp}"
        self._setup_logging()

        # Initialize client
        if self.model == 'deepseek-chat':
            self.client = OpenAI(api_key=self.api_key, 
                base_url="https://api.deepseek.com")
        else:
            self.client = OpenAI(api_key=self.api_key)

    def _setup_logging(self):
        """
        Prepare logging setup.
        """
        self.log_file = f"logs/{self.prefix}.transcript.log"
        if self.logging:
            os.makedirs('logs', exist_ok=True)
            with open(self.log_file, "w") as f:
                f.write("New session initiated.\n")

    def _setup_model_and_role(self):
        """
        Processes model and role selections.
        """
        self.role, self.label = self._select_role()
        self.model, self.base_url = self._select_model()
        self._set_api_key()

    def _prepare_query(self):
        """
        Prepares the query, including prompt modifications and image handling.
        """
        self.prompt = self._append_file_scanner(self.prompt)
        self._calculate_iterations()
        self._handle_image_request()
        self._handle_image_params()
        self._log_and_print(self._report_query_params())
        if self.refine: 
            self._refine_prompt()
        if self.chain_of_thought:
            self.role += roleDict['chain']
        if self.unit_testing:
            self.prompt = roleDict['refactor']['unit_tests'] + self.prompt
        
    def _set_api_key(self):
        """Sets the OpenAI API key."""
        if self.api_key == "system":
            self.api_key = os.getenv("OPENAI_API_KEY", None)
            if self.model == 'deepseek-chat':
                self.api_key = os.getenv("DEEPSEEK_API_KEY")
            if not self.api_key:
                raise EnvironmentError("OPENAI_API_KEY environment variable not found!")
        else:
            env_key = 'DEEPSEEK_API_KEY' if self.model == 'deepseek-chat' else 'OPENAI_API_KEY'
            os.environ[env_key] = self.api_key

    def _select_model(self):
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
        return self.model.lower() if self.model.lower() in model_to_url else 'gpt-4o-mini', model_to_url.get(self.model.lower(), "https://api.openai.com")

    def _select_role(self):
        """Selects the role based on user input or defaults."""

        if self.role in roleDict:
            role = roleDict[self.role]
            prompt = role['prompt']
            label = self.role
            self.role_name = role['name']
        else:
            prompt = self.role
            label = "custom"
            self.role_name = "Custom"
        
        return prompt, label

    def _append_file_scanner(self, message):
        """Scans files in message and appends their contents."""
        if isinstance(message, list):
            message = ' '.join(message)
        words = set(message.split())
        appended_message, new_words = self._scan_directories_and_files(words)
        return message + appended_message

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

    def _calculate_iterations(self):
        """Determines the number of response iterations."""
        if self.role == 'refine' and self.iterations == 1:
            self.iterations + 2

    def _handle_image_params(self):
        """Sets image dimensions and quality parameters."""
        self.dims = "NA"
        self.qual = "NA"
        if self.label in {"art", "photo"}:
            self.dims, self.qual = self._validate_image_params(self.dim, self.qual, self.model)
            self.qual = "hd" if self.label == "photo" else self.qual

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
        reportStr = self._generate_status()
        self._log_and_print(reportStr)

    def _generate_status(self):
        """Generate status message."""
        status = f"""
System parameters:
    Model: {self.model}
    Role: {self.role_name}
    Chain-of-thought: {self.chain_of_thought}
    Prompt refinement: {self.refine}
    Response iterations: {self.iterations}
    Time stamp: {self.timestamp}
    Seed: {self.seed}
    Text logging: {self.logging}
    Snippet logging: {self.code}
    """
        if 'dall-e' in self.model:
            status += f"""Image dimensions: {self.size}
    Image quality: {self.quality}
    """
        return status

    def request(self, prompt):
        """Submits the query to OpenAI's API and processes the response."""
        if self.verbose == False:
            print("\nProcessing user request...\n")
        self.prompt = prompt
        self.original_query = prompt

        self._prepare_query()
        self._log_and_print("\nProcessing finalized user request...")
        if self.label not in ["artist", "photo"]:
            self._process_text_response()
        else:
            self._process_image_response()
        token_report = self._gen_token_report()
        self._log_and_print(token_report)

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
        if self.iterations > 1:
            message = self._condense_iterations(response)
        else:
            message = response.choices[0].message.content.strip()

        self._update_token_count(response)
        self._log_and_print(message)
        self.message = message

        if self.verbose == False:
            print(self.message)

        # Extract code snippets
        if self.code:
            self.scripts = self.extract_and_save_code(message)
            if self.scripts:
                reportStr = "\nCode extracted from reponse text and saved to:\n\t" + '\n\t'.join(self.scripts)
                self._log_and_print(reportStr)

                # Lint python code
                python_scripts = [x for x in self.scripts if x.endswith(".py")]
                if len(python_scripts) > 0:
                    self._log_and_print("\nPython files detected, linting newly generated code...")
                    for s in python_scripts:
                        call(["black", s])

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
        
        self.message = "\nRevised image prompt:\n" + revised_prompt + "\nGenerated image saved to:\n" + image_file
        self._log_and_print(self.message)
        if self.verbose == False:
            print(self.message)

    def _assemble_query(self):
        """Assembles the query dictionary for the API request."""
        if 'refactor' in self.prompt.lower() or 'rewrite' in self.prompt.lower():
            if len(self.original_query.strip()) > 0:
                self.prompt += "\n\nImprove the following:\n"
                self.prompt += self.original_query
        
        return [{"role": "user", "content": self.prompt},
                {"role": "system", "content": self.role}]

    def extract_and_save_code(self, response):
        """
        Extracts code snippets from the response and saves them into separate files.

        Args:
            response (str): The response string containing potential code blocks.

        Returns:
            list: A list of file paths where the code snippets were saved.
        """
        code_files = self._initialize_code_files()
        counter = 0
        
        for line in response.splitlines():
            if line.startswith("```"):
                if len(code_files["current_code"]) > 2:  # End of a code block
                    counter += 1
                    file_name = self._save_code_block(code_files, lang, self.timestamp, counter)
                    code_files['files'].append(file_name)
                    self._reset_current_code(code_files)
                else:  # Start of a new code block
                    lang = line.replace("```", "").strip().lower()
                    code_files["current_code"].append(f"# {lang}\n")
            elif len(code_files["current_code"]) > 1:  # Within a code block
                code_files["current_code"].append(line)
                code_files = self._extract_code_metadata(line, code_files)
        
        return code_files["files"]

    @staticmethod
    def _initialize_code_files():
        """Initialize the Python objects dictionary."""
        code_files = defaultdict(list)
        code_files["current_code"] = ["# Code generated by ChatGPT\n"]
        return code_files

    @staticmethod
    def _reset_current_code(code_files):
        """Reset the current code accumulator."""
        code_files["current_code"] = ["# Code generated by ChatGPT\n"]

    def _extract_code_metadata(self, line, code_files):
        """
        Extract metadata from a line of code.

        Args:
            line (str): A single line of code.
            code_files (dict): A dictionary to store the metadata.
        """
        if line.strip() and (line.startswith('def') or line.startswith('class')):
            function_name, class_name = self._scrape_object_name(line)
            code_files['functions'].append(function_name)
            code_files['classes'].append(class_name)

        return code_files

    @staticmethod
    def _scrape_object_name(line_of_code):
        # Define regex patterns for function and class definitions
        function_definition_pattern = r'^\s*def\s+([a-zA-Z_]\w*)\s*\(.*\)\s*:'
        class_definition_pattern = r'^\s*class\s+([a-zA-Z_]\w*)\s*\(?[^:]*\)?:'

        # Match the line against patterns
        class_match = re.match(class_definition_pattern, line_of_code)
        function_match = re.match(function_definition_pattern, line_of_code)

        # Return class over function, before defaulting
        func = clss = 'code'
        if class_match:
            clss = class_match[0].split()[1].split(')')[0]
        if function_match:
            func = function_match[0].split()[1].split(')')[0]
        
        return func, clss

    def _save_code_block(self, code_files, lang, timestamp, counter):
        """
        Saves a code block to a file.

        Args:
            code_files (dict): A dictionary containing the current code and metadata.
            lang (str): The language of the code block.
            timestamp (str): A unique timestamp used for filenames.
            counter (int): A counter to differentiate between multiple code files.

        Returns:
            str: The filename where the code block was saved.
        """
        code_files["code"] = "\n".join(code_files["current_code"]) + "\n"
        name = self._select_outfile_ext(code_files['classes'], code_files['functions'], lang)
        extension = extDict.get(lang, f".{lang}")
        
        file_name = f"code/{name}.{timestamp}.{counter}{extension}".lstrip('_')
        
        os.makedirs("code", exist_ok=True)
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(code_files["code"])
        
        return file_name
    
    def _select_outfile_ext(self, classes, functions, lang):
        """
        Determine the base name for an output file based on classes, functions, and language.

        Args:
            classes (list): List of class names identified in the code block.
            functions (list): List of function names identified in the code block.
            lang (str): The language of the code block.

        Returns:
            str: A filename base to use, excluding the path and extension.
        """

        base_name = "output"  # Default base name if no classes or functions found

        # Select a name based on available class or function names
        if classes:
            base_name = classes[0]  # Use the first class name, if available
        elif functions:
            base_name = functions[0]  # Use the first function name, if available
        
        return base_name

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
        return (f"\nTotal tokens generated: {total_tokens}  (${total_cost})"
                f"\n    Prompt (i.e. input): {self.tokens['prompt']}  (${prompt_cost})"
                f"\n    Completion (i.e. output): {self.tokens['completion']}  (${completion_cost})")

    def save_chat_transcript(self):
        """Saves the current response text to a file if specified."""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write("\n".join(self.log_text))
        self._log_and_print(f"\nSaving conversation transcript text to: {self.log_file}\n")

    def _condense_iterations(self, api_response):
        """Condenses multiple API responses into a single coherent response."""
        api_responses = [r.message.content.strip() for r in api_response.choices]
        api_responses = self._gen_iteration_str(api_responses)

        condensed = self.client.chat.completions.create(
            model=self.model,
            seed=self.seed,
            messages=[
                {"role": "system", "content": self.role},
                {"role": "user", "content": f"{refineDict['condense_prompt']}\n\n{api_responses}"}
            ])
        self._update_token_count(condensed)

        message = condensed.choices[0].message.content.strip()
        self._log_and_print(f"\nCondensed text from iterations:\n{message}")

        return message
    
    def _gen_iteration_str(self, responses):
        """Format single string with response iteration text"""
        outStr = '\n\n'.join(['\n'.join([f'Iteration: {i+1}', responses[i]]) for i in range(len(responses))])
        self._log_and_print(outStr)

        return outStr

    def _refine_prompt(self, actions=set(['expand', 'amplify']), temperature=0.7):
        """Refines an LLM prompt using specified rewrite actions."""
        self._log_and_print("\nRefining current user prompt...")

        actions |= set(re.sub(r'[^\w\s]', '', word).lower() for word in self.prompt.split() if word.lower() in refineDict)
        action_str = "\n".join(refineDict[a] for a in actions) + '\n\n'
        updated_prompt = refineDict['refine_prompt'] + action_str + self.prompt

        refined = self.client.chat.completions.create(
            model=self.model, temperature=temperature, n=self.iterations,
            seed=self.seed,
            messages=[
                {"role": "system", "content": self.role},
                {"role": "user", "content": updated_prompt}
            ])
        self._update_token_count(refined)
        if self.iterations > 1: 
            self.prompt = self._condense_iterations(refined)
        else:
            self.prompt = refined.choices[0].message.content.strip()

        self._log_and_print(f"\nRefined query prompt:\n{self.prompt}")

    def _update_token_count(self, response):
        """Updates token count for prompt and completion."""
        self.tokens['prompt'] += response.usage.prompt_tokens
        self.tokens['completion'] += response.usage.completion_tokens

    def _log_and_print(self, message):
        """Logs and prints the provided message if verbose."""
        if message:
            if self.verbose:
                print(message)
            if self.logging:
                self.log_text.append(message)

    def _calculate_cost(self, tokens, perM, dec=5):
        """Calculates approximate cost (USD) of LLM tokens generated to a given decimal place"""
        return round((tokens * perM) / 1e6, dec)

    def _string_to_binary(self, input_string, output_str=False, shuffle=False, maxsize=True):
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
