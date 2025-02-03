
import os
import re
import sys
import time
import string
import requests
from datetime import datetime
from collections import defaultdict

from openai import OpenAI

from promptpal.lib import text_library

roleDict = text_library["roles"]
modifierDict = text_library["modifiers"]
refineDict = text_library["refinement"]
extDict = text_library["extensions"]
patternDict = text_library["patterns"]

    
# Confirm environment API key
api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise EnvironmentError("OPENAI_API_KEY environment variable not found!")

# Initialize OpenAI client and conversation thread
client = OpenAI(api_key=api_key)
thread = client.beta.threads.create()

class CreateAgent:
    """
    A handler for managing queries to the OpenAI API, including prompt preparation,
    API request submission, response processing, and logging.

    This class provides a flexible interface to interact with OpenAIs models, including
    text-based models (e.g., GPT-4) and image generation models (e.g., DALL-E). It supports
    features such as associative prompt refinement, chain-of-thought reasoning, code extraction,
    logging, and unit testing.

    Attributes:
        model (str): The model to use for the query (e.g., 'gpt-4o-mini', 'dall-e-3').
        verbose (bool): If True, prints detailed logs and status messages.
        silent (bool): If True, silences all StdOut messages.
        refine (bool): If True, refines the prompt before submission.
        chain_of_thought (bool): If True, enables chain-of-thought reasoning.
        save_code (bool): If True, extracts and saves code snippets from the response.
        scan_dirs (bool): If True, recursively scans directories found in prompt for existing files, extracts contents, and adds to prompt.
        logging (bool): If True, logs the session to a file.
        summary (bool): If True, summarizes the current conversation context to reference later.
        api_key (str): The API key for OpenAI. Defaults to system environment variable.
        seed (int or str): Seed for reproducibility. Can be an integer or a string converted to binary.
        iterations (int): Number of response iterations for refining or condensing outputs.
        dimensions (str): Dimensions for image generation (e.g., '1024x1024').
        quality (str): Quality setting for image generation (e.g., 'hd').
        role (str): The role or persona for the query (e.g., 'assistant', 'artist').
        tokens (dict): Tracks token usage for prompt and completion.
        prefix (str): A unique prefix for log files and outputs.
        client (OpenAI): The OpenAI client instance for API requests.
        glyph (bool): If True, restructures queries with representative/associative glyphs and logic flow
        temperature (float): Range from 0.0 to 2.0, lower values increase randomness, and higher values increase randomness.
        top_p (float): Range from 0.0 to 2.0, lower values increase determinism, and higher values increase determinism.

    Current role shortcuts:
        assistant: Standard personal assistant with improved ability to help with tasks
        analyst: Expertise in bioinformatics and systems biology. Knowledgeable in commonly used computational biology platforms.
        developer: Generates complete, functional application code based on user requirements, ensuring clarity and structure.
        refactor: Senior full stack developer with emphases in correct syntax and documentation
        tester: Quality assurance tester with experience in software testing and debugging, generates high-quality unit tests
        dataviz: Create clear, insightful data visualizations and provide analysis using structured formats, focusing solely on visualization requests and recommendations.
        writer: Writing assistant to help with generating science & technology related content
        editor: Text editing assistant to help with clarity and brevity
        artist: Creates an images described by the prompt, default style leans toward illustrations
        photographer: Generates more photo-realistic images

    Methods:
        __init__: Initializes the handler with default or provided values.
        request: Submits a query to the OpenAI API and processes the response.
        new_thread: Start a new thread with only the current agent.
        _save_chat_transcript: Saves the conversation transcript to a file.
        _extract_and_save_code: Extracts code snippets from the response and saves them to files.
        _setup_logging: Prepares logging setup.
        _prepare_query_text: Prepares the query, including prompt modifications and image handling.
        _validate_model_selection: Validates and selects the model based on user input or defaults.
        _prepare_system_role: Selects the role based on user input or defaults.
        _append_file_scanner: Scans files in the message and appends their contents.
        _validate_image_params: Validates image dimensions and quality for the model.
        _handle_text_request: Processes text-based responses from OpenAIs chat models.
        _handle_image_request: Processes image generation requests using OpenAIs image models.
        _condense_iterations: Condenses multiple API responses into a single coherent response.
        _refine_user_prompt: Refines an LLM prompt using specified rewrite actions.
        _update_token_count: Updates token count for prompt and completion.
        _log_and_print: Logs and prints the provided message if verbose.
        _calculate_cost: Calculates the approximate cost (USD) of LLM tokens generated.
        _string_to_binary: Converts a string to a binary-like variable for use as a random seed.
    """

    def __init__(
        self,
        logging=True,
        verbose=True,
        silent=False,
        refine=False,
        glyph=False,
        chain_of_thought=False,
        save_code=False,
        scan_dirs=False,
        summary=False,
        model="gpt-4o-mini",
        role="assistant",
        seed="t634e``R75T86979UYIUHGVCXZ",
        iterations=1,
        temperature=0.7,
        top_p=1.0,
        dimensions="NA",
        quality="NA",
        mode='normal',
    ):
        """
        Initialize the handler with default or provided values.
        """
        # Globals
        self.client = client
        self.thread = thread
        self.api_key = api_key

        # Booleans
        self.verbose = verbose
        self.silent = silent
        self.refine_prompt = refine
        self.glyph_prompt = glyph
        self.chain_of_thought = chain_of_thought
        self.save_code = save_code
        self.scan_dirs = scan_dirs
        self.iterations = iterations
        self.summary = summary

        # Additional hyperparams
        self.mode = mode if mode == 'refine_only' else 'normal'
        self.tokens = {"prompt": 0, "completion": 0}
        self.seed = seed if isinstance(seed, int) else self._string_to_binary(seed)
        self._validate_probability_params(temperature, top_p)
        
        # Validate user inputs
        self._prepare_system_role(role)
        self._validate_model_selection(model)
        if self.model in ["dall-e-2", "dall-e-3"]:
            self._validate_image_params(dimensions, quality)
        self._create_new_agent(interpreter=self.save_code)

        # Initialize reporting and related vars
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.prefix = f"{self.label}.{self.model.replace('-', '_')}.{self.timestamp}"        
        self._setup_logging(logging)
        self._log_and_print(self._generate_status(), self.verbose, self.logging)

    def _setup_logging(self, log):
        """
        Prepare logging setup.
        """
        self.logging = log
        self.log_text = []
        self.log_file = f"logs/{self.prefix}.transcript.log"
        os.makedirs("logs", exist_ok=True)
        with open(self.log_file, "w") as f:
            f.write("New session initiated.\n")

    def _validate_probability_params(self, temp, topp):
        """Ensure temperature and top_p are valid"""
        self.temperature = temp
        self.top_p = topp

        # Acceptable ranges
        if self.temperature < 0.0 or self.temperature > 2.0:
            self.temperature = 0.7
        if self.top_p < 0.0 or self.top_p > 2.0:
            self.top_p = 1.0

        # Only one variable is changed at a time
        if self.temperature != 0.7 and self.top_p != 1.0:
            self.top_p = 1.0

    def _prepare_query_text(self, prompt_text):
        """
        Prepares the query, including prompt modifications and image handling.
        """
        self.prompt = prompt_text

        # Identifies files to be read in
        files = self._find_existing_files()
        for f in files:
            self.prompt += "\n\n" + self._read_file_contents(f)
        if self.scan_dirs == True:
            paths = self._find_existing_paths()
            for d in paths:
                self.prompt += "\n\n" + self._scan_directory(d)

        # Refine prompt if required
        if self.refine_prompt or self.glyph_prompt:
            self._log_and_print(
                "\ngpt-4o-mini optimizing initial user request...\n", True, self.logging)
            self.prompt = self._refine_user_prompt(self.prompt)

    def _validate_model_selection(self, input_model):
        """Validates and selects the model based on user input or defaults."""
        openai_models = ["gpt-4o","o1","o1-mini","o1-preview","dall-e-3","dall-e-2"]
        self.model = input_model.lower() if input_model.lower() in openai_models else "gpt-4o-mini"

    def _prepare_system_role(self, input_role):
        """Prepares system role tetx."""

        # Selects the role based on user input or defaults.
        if input_role.lower() in roleDict:
            self.label = input_role.lower()
            builtin = roleDict[input_role.lower()]
            self.role = builtin["prompt"]
            self.role_name = builtin["name"]
        elif input_role.lower() in ["user", ""]:
            self.role = "user"
            self.label = "default"
            self.role_name = "Default User"
        else:
            self.role = role
            self.label = "custom"
            self.role_name = "User-defined custom role"

        # Add chain of thought reporting
        if self.chain_of_thought:
            self.role += modifierDict["cot"]

    def _read_file_contents(self, filename):
        """Reads the contents of a given file."""
        with open(filename, "r", encoding="utf-8") as f:
            return f"# File: {filename}\n{f.read()}"

    def _validate_image_params(self, dimensions, quality):
        """Validates image dimensions and quality for the model."""
        valid_dimensions = {"dall-e-3": ["1024x1024", "1792x1024", "1024x1792"],
                            "dall-e-2": ["1024x1024", "512x512", "256x256"]}
        if (self.model in valid_dimensions and dimensions.lower() not in valid_dimensions[self.model]):
            self.dimensions = "1024x1024"
        else:
            self.dimensions = dimensions

        self.quality = "hd" if quality.lower() in {"h", "hd", "high", "higher", "highest"} else "standard"
        self.quality = "hd" if self.label == "photographer" else self.quality # Check for photo role
        
    def _generate_status(self):
        """Generate status message."""
        status = f"""
Agent parameters:
    Model: {self.model}
    Role: {self.role_name}
    Chain-of-thought: {self.chain_of_thought}
    Prompt refinement: {self.refine_prompt}
    Associative glyphs: {self.glyph_prompt}
    Response iterations: {self.iterations}
    Subdirectory scanning: {self.scan_dirs}
    Time stamp: {self.timestamp}
    Seed: {self.seed}
    Text logging: {self.logging}
    Verbose StdOut: {self.verbose}
    Snippet logging: {self.save_code}
    """
        if "dall-e" in self.model:
            status += f"""Image dimensions: {self.dimensions}
    Image quality: {self.quality}
    """
        return status

    def new_thread(self):
        """Start a new thread with only the current agent."""
        self.thread = self.client.beta.threads.create()

    def request(self, prompt, thread=None):
        """Submits the query to OpenAIs API and processes the response."""

        # Update user prompt 
        self._prepare_query_text(prompt)
        self._log_and_print(
            f"\n{self.model} processing updated conversation thread...\n",
                True, self.logging)

        if self.mode != "refine_only":
            if "dall-e" not in self.model:
                self._handle_text_request()
            else:
                self._handle_image_request()

        token_report = self._gen_token_report()
        self._log_and_print(token_report, self.verbose, self.logging)

        # Save chat logs to file
        if self.logging:
            self._save_chat_transcript()

    def _init_chat_completion(self, prompt, model='gpt-4o-mini', role='user', iters=1, seed=42, temp=0.7, top_p=1.0):
        """Initialize and submit a single chat completion request"""
        message = [{"role": "user", "content": prompt}, {"role": "system", "content": role}]

        completion = self.client.chat.completions.create(
            model=model, messages=message, n=iters,
            seed=seed, temperature=temp, top_p=top_p)

        return completion

    def _generate_context_summary(self):
        """Summarize current conversation history for future context parsing."""
        self._log_and_print(f"\ngpt-4o-mini summarizing current conversation...\n", True, False)

        summarized = self._init_chat_completion(self, 
            prompt=f"{modifierDict['summarize']}\n\n{'\n'.join(self.log_text)}", 
            iters=self.iterations, seed=self.seed)
        self._update_token_count(summarized)
        self.current_context = summarized.choices[0].message.content.strip()

    def _handle_text_request(self):
        """Processes text-based responses from OpenAIs chat models."""
        self.message = self._run_thread_request()
        self._update_token_count(self.run_status)
        self._log_and_print(self.message, True, self.logging)

        # Extract code snippets
        code_snippets = self._extract_code_snippets()
        if self.save_code and len(code_snippets) > 0:
            self.code_files = []
            reportStr = "\nExtracted code saved to:\n"
            for lang in code_snippets.keys():
                code = code_snippets[lang]
                objects = self._extract_object_names(code, lang)
                file_name = f"{self._find_max_lines(code, objects)}.{self.timestamp}{extDict.get(lang, f'.{lang}')}".lstrip("_.")
                reportStr += f"\t{file_name}\n"
                self._write_script(code, file_name)

            self._log_and_print(reportStr, True, self.logging)

        # Summarize current context
        if self.summary == True:
            self._generate_context_summary(self)

    def _write_script(self, content, file_name, outDir="code", lang=None):
        """Writes code to a file."""
        os.makedirs(outDir, exist_ok=True)
        self.code_files.append(f"{os.getcwd()}/{outDir}/{file_name}")
        with open(f"{outDir}/{file_name}", "w", encoding="utf-8") as f:
            if lang:
                f.write(f"#!/usr/bin/env {lang}\n\n")
            f.write(f"# Code generated by {self.model}\n\n")
            f.write(content)

    def _handle_image_request(self):
        """Processes image generation requests using OpenAIs image models."""
        os.makedirs("images", exist_ok=True)
        response = self.client.images.generate(
            model=self.model,
            prompt=self.prompt,
            n=1,
            size=self.dimensions,
            quality=self.quality,
        )
        self._update_token_count(response)
        self._log_and_print(
            f"\nRevised initial prompt:\n{response.data[0].revised_prompt}",
            self.verbose,
            self.logging,
        )
        image_data = requests.get(response.data[0].url).content
        image_file = f"images/{self.prefix}.image.png"
        with open(image_file, "wb") as outFile:
            outFile.write(image_data)

        self.message = (
            "\nRevised image prompt:\n"
            + response.data[0].revised_prompt
            + "\nGenerated image saved to:\n"
            + image_file
        )
        self._log_and_print(self.message, True, self.logging)

    def _gen_token_report(self):
        """Generates report string for overall cost of the query."""
        prompt_cost, completion_cost = "Unknown model rate", "Unknown model rate"
        total_tokens = self.tokens["prompt"] + self.tokens["completion"]
        self.total_cost = "Unknown model rate"
        rates = {
            "gpt-4o": (2.5, 10),
            "gpt-4o-mini": (0.150, 0.600),
            "o1-mini": (3, 12),
            "o1-preview": (15, 60),
            "dall-e-3": (2.5, 0.040),
            "dall-e-2": (2.5, 0.040),
        }
        if self.model in rates:
            prompt_rate, completion_rate = rates.get(self.model)
            prompt_cost = self._calculate_cost(self.tokens["prompt"], prompt_rate)
            completion_cost = self._calculate_cost(
                self.tokens["completion"], completion_rate
            )
            self.total_cost = round(prompt_cost + completion_cost, 5)
        return (
            f"\nTotal tokens generated: {total_tokens}  (${self.total_cost})"
            f"\n    Prompt (i.e. input): {self.tokens['prompt']}  (${prompt_cost})"
            f"\n    Completion (i.e. output): {self.tokens['completion']}  (${completion_cost})"
        )

    def _save_chat_transcript(self):
        """Saves the current response text to a file if specified."""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write("\n".join(self.log_text))
        self._log_and_print(
            f"\nSaving conversation transcript text to: {self.log_file}\n",
            self.verbose,
            self.logging,
        )

    def _condense_iterations(self, api_response):
        """Condenses multiple API responses into a single coherent response."""
        api_responses = [r.message.content.strip() for r in api_response.choices]
        api_responses = self._gen_iteration_str(api_responses)

        self._log_and_print(
            f"\ngpt-4o-mini condensing response iterations...", self.verbose, self.logging
        )
        condensed = self._init_chat_completion(self, 
            prompt=f"{modifierDict['condense']}\n\n{api_responses}", 
            role=self.role, iters=self.iterations, seed=self.seed)
        self._update_token_count(condensed)
        message = condensed.choices[0].message.content.strip()
        self._log_and_print(
            f"\nCondensed text:\n{message}", self.verbose, self.logging
        )

        return message

    def _gen_iteration_str(self, responses):
        """Format single string with response iteration text"""
        outStr = "\n\n".join(
            [
                "\n".join([f"Iteration: {i + 1}", responses[i]])
                for i in range(len(responses))
            ]
        )
        self._log_and_print(outStr, self.verbose, self.logging)

        return outStr

    def _refine_user_prompt(self, old_prompt):
        """Refines an LLM prompt using specified rewrite actions."""
        updated_prompt = old_prompt
        if self.refine_prompt == True:
            actions = set(["expand", "amplify"])
            actions |= set(
                re.sub(r"[^\w\s]", "", word).lower()
                for word in old_prompt.split()
                if word.lower() in refineDict
            )
            action_str = "\n".join(refineDict[a] for a in actions) + "\n\n"
            updated_prompt = modifierDict["refine"] + action_str + old_prompt

        if self.glyph_prompt == True:
            updated_prompt += modifierDict["glyph"]

        refined = self._init_chat_completion(self, 
            prompt=updated_prompt, 
            seed=self.seed, 
            iters=self.iterations,
            temp=self.temperature, 
            top_p=self.top_p)

        self._update_token_count(refined)
        if self.iterations > 1:
            new_prompt = self._condense_iterations(refined)
        else:
            new_prompt = refined.choices[0].message.content.strip()

        self._log_and_print(
            f"\nRefined query prompt:\n{new_prompt}", self.verbose, self.logging)

        return new_prompt

    def _update_token_count(self, response_obj):
        """Updates token count for prompt and completion."""
        self.tokens["prompt"] += response_obj.usage.prompt_tokens
        self.tokens["completion"] += response_obj.usage.completion_tokens

    def _log_and_print(self, message, verb=True, log=True):
        """Logs and prints the provided message if verbose."""
        if message:
            if verb == True and self.silent == False:
                print(message)
            if log == True:
                self.log_text.append(message)

    @staticmethod
    def _calculate_cost(tokens, perM, dec=5):
        """Calculates approximate cost (USD) of LLM tokens generated to a given decimal place"""
        return round((tokens * perM) / 1e6, dec)

    @staticmethod
    def _string_to_binary(input_string):
        """Create a binary-like variable from a string for use a random seed"""
        # Convert all characters in a str to ASCII values and then to 8-bit binary
        binary = ''.join([format(ord(char), "08b") for char in input_string])
        # Constrain length
        return int(binary[0 : len(str(sys.maxsize))])

    @staticmethod
    def _is_code_file(file_path):
        """Check if a file has a code extension."""
        return os.path.splitext(file_path)[1].lower() in set(extDict.values())

    def _scan_directory(self, path="code"):
        """Recursively scan a directory and return the content of all code files."""
        codebase = ""
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                if self._is_code_file(file_path):
                    codebase += f"File: {file_path}\n"
                    codebase += self._read_file_contents(file_path)
                    codebase += "\n\n"

        return codebase

    def _find_existing_paths(self):
        """
        Scan the input string for existing paths and return them in separate lists.
        """
        # Regular expression to match potential file paths
        path_pattern = re.compile(r'([a-zA-Z]:\\[^:<>"|?\n]*|/[^:<>"|?\n]*)')

        # Find all matches in the input string
        matches = path_pattern.findall(self.prompt)

        # Separate files and directories
        existing_paths = []
        for match in matches:
            if os.path.isdir(match):
                existing_paths.append(match)

        return existing_paths

    def _find_existing_files(self):

        # Filter filenames by checking if they exist in the current directory or system's PATH
        existing_files = [
            x
            for x in self.prompt.split()
            if os.path.isfile(x.rstrip(string.punctuation))
        ]

        return existing_files

    def _extract_code_snippets(self):
        """
        Extract code snippets from a large body of text using triple backticks as delimiters.
        Also saves the language tag at the start of each snippet.
        """
        # Regular expression to match code blocks enclosed in triple backticks, including the language tag
        code_snippets = defaultdict(str)
        code_pattern = re.compile(r"```(\w+)\n(.*?)```", re.DOTALL)
        snippets = code_pattern.findall(self.message)
        for lang, code in snippets:
            code_snippets[lang] += code.strip()

        return code_snippets

    @staticmethod
    def _extract_object_names(code, language):
        """
        Extract defined object names (functions, classes, and variables) from a code snippet.
        """
        # Get language-specific patterns
        patterns = patternDict.get(language, {})

        # Extract object names using the language-specific patterns
        classes = patterns.get("class", re.compile(r"")).findall(code)
        functions = patterns.get("function", re.compile(r"")).findall(code)
        variables = patterns.get("variable", re.compile(r"")).findall(code)

        # Select objects to return based on hierarachy
        if len(classes) > 0:
            return classes
        elif len(functions) > 0:
            return functions
        else:
            return variables

    @staticmethod
    def _find_max_lines(code, object_names):
        """
        Count the number of lines of code for each object in the code snippet.

        Args:
            code (str): The code snippet to analyze.
            object_names (list): A list of object names to count lines for.

        Returns:
            str: Name of object with the largest line count.
        """
        rm_names = ["main", "functions", "classes", "variables"]
        line_counts = {name: 0 for name in object_names if name not in rm_names}
        line_counts['code'] = 1
        current_object = None

        for line in code.split("\n"):
            # Check if the line defines a new object
            for name in object_names:
                if re.match(rf"\s*(def|class)\s+{name}\s*[\(:]", line):
                    current_object = name
                    break

            # Count lines for the current object
            if current_object and line.strip() and current_object not in rm_names:
                line_counts[current_object] += 1

        return max(line_counts, key=line_counts.get)

    def _create_new_agent(self, interpreter=False):
        """
        Creates a new assistant based on user-defined parameters

        Args:
            interpreter (bool): Whether to enable the code interpreter tool.

        Returns:
            New assistant assistant class instance
        """
        try:
            self.agent = self.client.beta.assistants.create(
                name=self.role_name,
                instructions=self.role,
                model=self.model,
                tools=[{"type": "code_interpreter"}] if interpreter == True else [])
        except Exception as e:
            raise RuntimeError(f"Failed to create assistant: {e}")

    def _run_thread_request(self) -> str:
        """
        Sends a user prompt to an existing thread, runs the assistant, 
        and retrieves the response if successful.
        
        Returns:
            str: The text response from the assistant.
        
        Raises:
            ValueError: If the assistant fails to generate a response.
        """
        # Adds user prompt to existing thread.
        try:
            new_message = self.client.beta.threads.messages.create(
                thread_id=self.thread.id, role="user", content=self.prompt)
        except Exception as e:
            raise RuntimeError(f"Failed to create message: {e}")

        # Run the assistant on the thread
        current_run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.agent.id)

        # Wait for completion and retrieve responses
        while True:
            self.run_status = self.client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=current_run.id)
            if self.run_status.status in ["completed", "failed"]:
                break
            else:
                time.sleep(2)  # Wait before polling again

        if self.run_status.status == "completed":
            messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
            if messages.data:  # Check if messages list is not empty
                return messages.data[0].content[0].text.value
            else:
                raise ValueError("No messages found in the thread.")
        else:
            raise ValueError("Assistant failed to generate a response.")
