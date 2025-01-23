import os
import re
import sys
import random
import requests
from subprocess import call
from datetime import datetime
from collections import defaultdict

from openai import OpenAI
from llm_api.lib import roleDict, modifierDict, refineDict, extDict

class OpenAIQueryHandler:
    """
    A handler for managing queries to the OpenAI API, including prompt preparation, 
    API request submission, response processing, and logging.

    This class provides a flexible interface to interact with OpenAI's models, including
    text-based models (e.g., GPT-4) and image generation models (e.g., DALL-E). It supports
    features such as associative prompt refinement, chain-of-thought reasoning, code extraction, 
    logging, and unit testing.

    Attributes:
        model (str): The model to use for the query (e.g., 'gpt-4o-mini', 'dall-e-3').
        verbose (bool): If True, prints detailed logs and status messages.
        refine_prompt (bool): If True, refines the prompt before submission.
        chain_of_thought (bool): If True, enables chain-of-thought reasoning.
        save_code (bool): If True, extracts and saves code snippets from the response.
        scan_files (bool): If True, scans prompt for existing files, extracts contents, and adds to prompt.
        logging (bool): If True, logs the session to a file.
        api_key (str): The API key for OpenAI or Deepseek. Defaults to system environment variable.
        seed (int or str): Seed for reproducibility. Can be an integer or a string converted to binary.
        iterations (int): Number of response iterations for refining or condensing outputs.
        dimensions (str): Dimensions for image generation (e.g., '1024x1024').
        quality (str): Quality setting for image generation (e.g., 'hd').
        role (str): The role or persona for the query (e.g., 'assistant', 'artist').
        unit_testing (bool): If True, appends unit testing instructions to the prompt.
        tokens (dict): Tracks token usage for prompt and completion.
        prefix (str): A unique prefix for log files and outputs.
        client (OpenAI): The OpenAI client instance for API requests.
        glyph_prompt (bool): If True, restructures queries into associative glyph formatting (NEEDS TESTING)

    Current role shortcuts:
        assistant (default): Standard personal assistant with improved ability to help with tasks
        compbio: Expertise in bioinformatics and systems biology. Knowledgeable in commonly used computational biology platforms.
        developer: Generates complete, functional application code based on user requirements, ensuring clarity and structure.
        refactor: Senior full stack developer with emphases in correct syntax, documentation, and unit testing.
        writer: Writing assistant to help with generating science & technology related content
        editor: Text editing assistant to help with clarity and brevity
        artist: Creates an images described by the prompt, default style leans toward illustrations
        photographer: Generates more photo-realistic images
        investor: Provides advice in technology stock investment and wealth management.

    Methods:
        __init__: Initializes the handler with default or provided values.
        request: Submits a query to the OpenAI API and processes the response.
        _save_chat_transcript: Saves the conversation transcript to a file.
        _extract_and_save_code: Extracts code snippets from the response and saves them to files.
        _setup_logging: Prepares logging setup.
        _setup_model_and_role: Processes model and role selections.
        _prepare_query: Prepares the query, including prompt modifications and image handling.
        _set_api_key: Sets the OpenAI API key.
        _select_model: Validates and selects the model based on user input or defaults.
        _select_role: Selects the role based on user input or defaults.
        _append_file_scanner: Scans files in the message and appends their contents.
        _handle_image_params: Sets image dimensions and quality parameters.
        _validate_image_params: Validates image dimensions and quality for the model.
        _report_query_params: Reports the current query configuration.
        _process_text_response: Processes text-based responses from OpenAI's chat models.
        _process_image_response: Processes image generation requests using OpenAI's image models.
        _assemble_query: Assembles the query dictionary for the API request.
        _condense_iterations: Condenses multiple API responses into a single coherent response.
        _refine_user_prompt: Refines an LLM prompt using specified rewrite actions.
        _update_token_count: Updates token count for prompt and completion.
        _log_and_print: Logs and prints the provided message if verbose.
        _calculate_cost: Calculates the approximate cost (USD) of LLM tokens generated.
        _string_to_binary: Converts a string to a binary-like variable for use as a random seed.
    """

    def __init__(self, 
                model="gpt-4o-mini",
                verbose=False,
                refine_prompt=False,
                chain_of_thought=False,
                save_code=False,
                scan_files=False,
                logging=False,
                api_key="system",
                seed=42,
                iterations=1,
                dimensions="NA",
                quality="NA",
                role="assistant",
                unit_testing=False,
                glyph_prompt=False):
        """
        Initialize the handler with default or provided values.
        """
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.model = model
        self.verbose = verbose
        self.refine_prompt = refine_prompt
        self.glyph_prompt = glyph_prompt
        self.chain_of_thought = chain_of_thought
        self.save_code = save_code
        self.scan_files = scan_files
        self.logging = logging
        self.log_text = []
        self.api_key = api_key or self._set_api_key()
        self.iterations = iterations
        self.dimensions = dimensions
        self.quality = quality
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
        if self.scan_files == True:
            self.prompt = self._append_file_scanner(self.prompt)
        if self.model in ['dall-e-2', 'dall-e-3']:
            self._handle_image_params()
        self._log_and_print(self._report_query_params())
        if self.refine_prompt: 
            self._refine_user_prompt()
        if self.chain_of_thought:
            self.role += modifierDict['cot']
        if self.unit_testing:
            self.prompt = modifierDict['tests'] + "\n" + self.prompt
        
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
        appended_message = self._scan_directories_and_files(words)
        return message + appended_message

    def _scan_directories_and_files(self, words):
        """Scan for existing files in user-provided text to append to messages."""
        new_message = ''
        for word in words:
            word = word.rstrip('.!?:;')
            if os.path.isfile(word):
                new_message += f"{word}:\n" + self._read_file_contents(word) + "\n"
        return new_message

    def _read_file_contents(self, filename):
        """Reads the contents of a given file."""
        with open(filename, 'r') as handle:
            return ''.join(handle.readlines())

    def _handle_image_params(self):
        """Sets image dimensions and quality parameters."""
        if self.label in {"artist", "photographer"}:
            self.dimensions, self.quality = self._validate_image_params(self.dimensions, self.quality, self.model)
            self.quality = "hd" if self.label == "photographer" else self.quality

    @staticmethod
    def _validate_image_params(dimensions, quality, model):
        """Validates image dimensions and quality for the model."""
        valid_dimensions = {
            'dall-e-3': ['1024x1024', '1792x1024', '1024x1792'],
            'dall-e-2': ['1024x1024', '512x512', '256x256']
        }
        if model in valid_dimensions and dimensions.lower() not in valid_dimensions[model]:
            dimensions = '1024x1024'
        quality = 'hd' if quality.lower() in {'h', 'hd', 'high', 'higher', 'highest'} else 'standard'
        return dimensions, quality

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
    Prompt refinement: {self.refine_prompt}
    Associative glyphs: {self.glyph_prompt}
    Response iterations: {self.iterations}
    Time stamp: {self.timestamp}
    Seed: {self.seed}
    Text logging: {self.logging}
    Snippet logging: {self.save_code}
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

        if self.refine_prompt == True:
            self._log_and_print("\nProcessing finalized user request...")
        else:
            self._log_and_print("\nProcessing user request...")

        if self.label not in ["artist", "photographer"]:
            self._process_text_response()
        else:
            self._process_image_response()
        token_report = self._gen_token_report()
        self._log_and_print(token_report)

        if self.logging:
            self._save_chat_transcript()

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
        if self.save_code:
            self.scripts = self._extract_and_save_code(message)
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

    def _extract_and_save_code(self, response):
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
        code_files['functions'] = []
        code_files['classes'] = []
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
        if line.strip() and ('def ' in line or 'class ' in line):
            function_name, class_name = self._scrape_object_name(line)
            if function_name:
                code_files['functions'].append(function_name)
            if class_name:
                code_files['classes'].append(class_name)

        return code_files

    @staticmethod
    def _scrape_object_name(line_of_code):
        func = clss = None

        # Defined patterns for function and class definitions
        function_test = line_of_code.split('def ')
        if len(function_test) > 1:
            function_test = function_test[1].split('(')[0]
            if function_test != 'main':
                func = function_test

        class_test = line_of_code.split('class ')
        if len(class_test) > 1:
            clss = class_test[1].split('(')[0]

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
        extension = extDict.get(lang, f".{lang}")

        if len(code_files['classes']) > 0:
            object_name = max(code_files['classes'], key=len)
        elif len(code_files['functions']) > 0:
            object_name = max(code_files['functions'], key=len)
        else:
            object_name = 'code'
        
        file_name = f"code/{object_name}.{timestamp}.{counter}{extension}".lstrip('_')
        
        os.makedirs("code", exist_ok=True)
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(code_files["code"])
        
        return file_name
    
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

    def _save_chat_transcript(self):
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
                {"role": "user", "content": f"{modifierDict['condense']}\n\n{api_responses}"}
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

    def _refine_user_prompt(self):
        """Refines an LLM prompt using specified rewrite actions."""
        self._log_and_print("\nRefining current user prompt...")

        temperature = 0.7 # Altered slightly to somewhat increase diversity in responses
        actions = set(['expand', 'amplify'])
        actions |= set(re.sub(r'[^\w\s]', '', word).lower() for word in self.prompt.split() if word.lower() in refineDict)
        action_str = "\n".join(refineDict[a] for a in actions) + '\n\n'
        updated_prompt = modifierDict['refine'] + action_str + self.prompt
        if self.glyph_prompt == True:
            updated_prompt += modifierDict['glyph']

        refined = self.client.chat.completions.create(
            model=self.model, temperature=temperature, n=1,
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
