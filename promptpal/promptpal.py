import hashlib
import logging
import os
import re
from collections import defaultdict
from importlib import resources
from pathlib import Path

import yaml
from google import genai

from promptpal.roles import Role
from promptpal.roles.role_schema import validate_role

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_existing_files(message: str) -> list[str]:
    """
    Detect file paths within a message.

    Args:
        message: The message to search for file references.

    Returns:
        A list of file paths found in the message.
    """
    # Regex pattern to match file paths (basic example)
    file_pattern = re.compile(r"/[^\s]+")
    return file_pattern.findall(message)


class Promptpal:
    """
    A class for managing and interacting with AI roles and agents.
    """

    def __init__(
        self,
        output_dir: str | None = None,
        api_key: str | None = None,
        load_default_roles: bool = True,
    ):
        """
        Initialize the Promptpal instance.

        Args:
            output_dir: Directory to save generated files. Defaults to None.
            api_key: Gemini API key. Defaults to None.
            load_default_roles: Whether to load default roles. Defaults to True.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key is None:
            raise OSError("GEMINI_API_KEY environment variable not found!")

        self._client = genai.Client(api_key=api_key, http_options={"api_version": "v1"})

        # Create a chat instance
        self._chat = self._client.chats.create(model="gemini-2.0-flash-001")

        self._roles = {}  # Store roles by name
        self._last_response = None  # Store the last response
        self._output_dir = output_dir  # Directory for writing code and image files

        # Initialize trackers for chat statistics
        self._token_count = 0
        self._message_count = 0
        self._files_written = {"code": 0, "images": 0}
        self._role_message_count = {}

        # Load default roles if specified
        if load_default_roles:
            try:
                with resources.open_text("promptpal.roles", "roles.yaml") as file:
                    # Load roles from the file
                    self.add_roles_from_file(file)
            except FileNotFoundError:
                raise FileNotFoundError("Default roles.yaml file not found.") from None

        if not self._output_dir:
            self._output_dir = "./generated_files"
        Path(self._output_dir).mkdir(parents=True, exist_ok=True)

    def list_roles(self) -> list[str]:
        """
        List the available roles by their names.

        Returns:
            list[str]: A list of role names.
        """
        return list(self._roles.keys())

    def get_role_description(self, role_name: str) -> str:
        """
        Get the description for the given role name.

        Args:
            role_name (str): The name of the role to search for.

        Returns:
            str: The description of the role.

        Raises:
            ValueError: If the role is not found.
        """
        role = self._roles.get(role_name)
        if role:
            return role.description
        raise ValueError(f"Role '{role_name}' not found.")

    def add_roles(self, roles: list[Role] | None = None):
        """
        Add new roles to the internal storage.

        Args:
            roles (list[Role] | None): A list of Role objects to add.
        """
        if roles is None:
            return

        for role in roles:
            if isinstance(role, Role):
                self._roles[role.name] = role  # Store role by name
            else:
                raise TypeError("All items in the roles list must be of type Role.")

    def add_roles_from_file(self, file):
        """
        Add roles from a YAML file.

        Args:
            file: A file-like object containing role definitions.
        """
        roles_data = yaml.safe_load(file)

        # Validate and create Role objects
        roles = []
        for role_name, role_info in roles_data.items():
            # Validate against schema
            validate_role(role_info)

            # Create Role object
            role = Role(
                name=role_name,
                description=role_info["description"],
                system_instruction=role_info["system_instruction"],
                model=role_info.get("model"),
                temperature=role_info.get("temperature"),
                top_p=role_info.get("top_p"),
                top_k=role_info.get("top_k"),
                max_output_tokens=role_info.get("max_output_tokens"),
                seed=role_info.get("seed"),
            )
            roles.append(role)

        # Add roles to internal storage
        self.add_roles(roles)

    def chat(
        self,
        role_name: str,
        message: str,
        write_output: bool = True,
        write_code: bool = True,
        token_threshold: int = 1000,
    ) -> str:
        """
        Send a chat message to the given role and get a response.

        Args:
            role_name (str): The name of the role to use for the chat.
            message (str): The user's message to send.
            write_code (bool): If True, write any code from the response to a file.
            token_threshold (int): The threshold for prompt_token_count.

        Returns:
            str: The response from the LLM.

        Raises:
            ValueError: If the role is not found.
        """
        # Find the role
        role = self._roles.get(role_name)
        if role is None:
            raise ValueError(f"Role '{role_name}' not found.")

        # Check if the role should use web search
        if role.search_web:
            self._chat = self._client.chats.create(
                model="gemini-2.0-flash-001",
                tools=[
                    genai.types.Tool(
                        google_search=genai.types.GoogleSearchRetrieval(
                            dynamic_retrieval_config=genai.types.DynamicRetrievalConfig(
                                dynamic_threshold=0.6
                            )
                        )
                    )
                ],
            )

        # Check if the role is associated with image generation
        if role.output_type == "image":
            raise NotImplementedError("Image generation is not implemented yet.")
            # Generate images using the genai client
            # try:
            #     response = self._client.models.generate_images(
            #         model=role.model,
            #         prompt=message,
            #         config=genai.types.GenerateImagesConfig(
            #             number_of_images=1,
            #         ),
            #     )
            #     logger.debug("Image generation response: %s", response)

            #     # Ensure the output directory exists
            #     if not self._output_dir:
            #         self._output_dir = "./generated_files"
            #     Path(self._output_dir).mkdir(parents=True, exist_ok=True)

            #     # Save images to the output directory
            #     for i, generated_image in enumerate(response.generated_images):
            #         image = Image.open(BytesIO(generated_image.image.image_bytes))
            #         image_path = Path(self._output_dir) / f"{role_name}_image_{i}.png"
            #         image.save(image_path)

            #     return f"Images saved to {self._output_dir}"
            # except Exception as e:
            #     logger.error("Error during image generation: %s", e)
            #     raise

        # Parse the message and look for references to files. If found, upload them to the client.
        file_references = find_existing_files(message)
        uploaded_files = {}
        for file_path in file_references:
            try:
                uploaded_file = self._client.files.upload(file=file_path)
                uploaded_files[file_path] = uploaded_file
            except FileNotFoundError:
                continue

        # Split the message around file references
        message_parts = message.split()
        contents = []
        for part in message_parts:
            if part in uploaded_files:
                contents.append(uploaded_files[part])
            else:
                contents.append(part)

        # Send the message using the chat instance
        response = self._chat.send_message(contents)

        # Store the response
        self._last_response = response

        # Check the usage metadata of the last response
        if self._last_response:
            usage_metadata = self._last_response.usage_metadata
            if (
                usage_metadata.prompt_token_count
                and usage_metadata.prompt_token_count > token_threshold
            ):
                # Summarize the chat
                summary_role = self._roles.get("summarizer")
                if summary_role is None:
                    raise ValueError("Summarizer role not found.")
                summary_response = self._chat.send_message(["Summarize the previous chat."])
                summary = summary_response.text

                # Start a new chat with the summary
                self.new_chat()
                self._chat.send_message(["Here is a summary of the previous chat:", summary])

        # Update token count and message count
        self._token_count += response.usage_metadata.prompt_token_count
        self._message_count += 1
        self._role_message_count[role_name] = self._role_message_count.get(role_name, 0) + 1

        # If write_code is True, extract code snippets and write them to files
        if write_code:
            code_snippets = self.extract_code_snippets(response.text)
            if code_snippets and not self._output_dir:
                self._output_dir = "./generated_files"
            Path(self._output_dir).mkdir(parents=True, exist_ok=True)
            for lang, code in code_snippets.items():
                filename = self.determine_filename(lang, code)
                file_path = Path(self._output_dir) / filename
                with open(file_path, "w") as code_file:
                    code_file.write(code)
            self._files_written["code"] += len(code_snippets)

        # Check for quiet mode
        #if self.quiet == True:
        #    response = self._quiet_response(response.text)

        return response.text

    def extract_code_snippets(self, text: str) -> dict:
        """
        Extract code snippets from the response text.

        Args:
            text (str): The response text containing code snippets.

        Returns:
            dict: A dictionary with language as keys and code snippets as values.
        """
        code_snippets = defaultdict(str)
        code_pattern = re.compile(r"```(\w+)\n(.*?)```", re.DOTALL)
        snippets = code_pattern.findall(text)
        for lang, code in snippets:
            code_snippets[lang] += code.strip()

        return code_snippets

    def determine_filename(self, lang: str, code: str) -> str:
        """
        Determine an appropriate filename and extension for the code snippet.

        Args:
            lang (str): The programming language of the code snippet.
            code (str): The code snippet.

        Returns:
            str: The determined filename with extension.
        """
        # Use a hash of the code to ensure unique filenames
        code_hash = hashlib.md5(code.encode()).hexdigest()[:8]
        extension = {
            "python": ".py",
            "javascript": ".js",
            "java": ".java",
            "c++": ".cpp",
            "html": ".html",
            "css": ".css",
            "bash": ".sh",
        }.get(lang, ".txt")  # Default to .txt if language is unknown

        return f"code_snippet_{code_hash}{extension}"

    def _quiet_response(self, text):
        """Create condensed responses to avoid walls of text"""
        role = self._roles.get("summarizer")
        prompt = role.system_instruction.replace("<user_prompt>", text)

        # Use the LLM to summarize the previous response
        response = self._client.models.generate_content(
            model='gpt-4o-mini',
            prompt=prompt,
            )
        # Return the summarized text
        return response

    def refine_prompt(
        self,
        prompt: str,
        glyph_refinement: bool = False,
        chain_of_thought: bool = False,
        keyword_refinement: str | None = None,
    ) -> str:
        logger.debug(
            "Refining prompt with glyph_refinement=%s, chain_of_thought=%s, keyword_refinement=%s",
            glyph_refinement,
            chain_of_thought,
            keyword_refinement,
        )

        # Ensure only one refinement method is selected
        if sum([glyph_refinement, chain_of_thought, keyword_refinement is not None]) > 1:
            raise ValueError(
                "Only one of glyph_refinement, chain_of_thought, or keyword_refinement can be true."
            )

        # Select the appropriate role or keyword refinement
        role = None
        if glyph_refinement:
            role = self._roles.get("glyph_prompt")
        elif chain_of_thought:
            role = self._roles.get("chain_of_thought")
        elif keyword_refinement:
            refine_dict = {
                "paraphrase": (
                    "Rewrite the text using different words while keeping the original meaning."
                ),
                "reframe": (
                    "Change the perspective or focus of the text while maintaining its intent."
                ),
                "summarize": "Condense the text to highlight key points.",
                "expand": "Add details and explanations for a more comprehensive understanding.",
                "explain": "Clarify the text by simplifying its meaning.",
                "reinterpret": "Offer an alternative understanding of the text.",
                "simplify": "Use less complex language for easier comprehension.",
                "elaborate": "Provide additional context and details to enrich clarity.",
                "amplify": "Emphasize key points to strengthen the message.",
                "clarify": "Remove ambiguity to ensure clear meaning.",
                "adapt": "Modify the text for a specific audience, purpose, or context.",
                "modernize": "Update outdated language or concepts with current equivalents.",
                "formalize": "Transform casual language into a professional tone.",
                "informalize": "Adjust the text to a conversational style.",
                "condense": "Shorten the text while preserving essential points.",
                "emphasize": "Highlight specific points more prominently.",
                "diversify": "Vary vocabulary, sentence structure, or style.",
                "neutralize": "Remove bias or emotion for an objective tone.",
                "streamline": "Make the text more concise and efficient.",
                "embellish": "Add vivid details or creative flourishes.",
                "illustrate": "Include examples or analogies for clarity.",
                "synthesize": "Combine multiple ideas into a cohesive rewrite.",
                "sensationalize": "Make the text more dramatic and engaging.",
                "humanize": "Make the text more personal and relatable.",
                "elevate": "Refine the text to be more polished and sophisticated.",
                "energize": "Make the text more lively and engaging.",
                "soften": "Reduce intensity for a gentler tone.",
                "exaggerate": "Amplify claims or tone for dramatic effect.",
                "downplay": "Present in a more restrained and understated manner.",
            }
            instruction = refine_dict.get(keyword_refinement)
            if instruction is None:
                raise ValueError(f"Keyword refinement '{keyword_refinement}' not recognized.")
            formatted_prompt = f"{instruction}\n\n{prompt}"
        else:
            role = self._roles.get("refine_prompt")

        # Ensure role is assigned a value before use
        if role is not None:
            # Format the prompt with the selected role's system instruction
            formatted_prompt = role.system_instruction.replace("<user_prompt>", prompt)

            # Use the LLM to refine the prompt
            response = self._client.models.generate_content(
                model=role.model,
                contents=formatted_prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0.7,
                ),
            )

            # Return the refined prompt
            return response.text.strip()

        # If using keyword refinement, return the formatted prompt
        return formatted_prompt.strip()

    def new_chat(self):
        """
        Reset the chat by creating a new chat instance.
        """
        self._chat = self._client.chats.create(model="gemini-2.0-flash-001")

    def get_chat_stats(self) -> dict:
        """
        Get the current chat statistics.

        Returns:
            dict: A dictionary containing the number of tokens used, number of messages sent,
                  a summary of code and image files written, and number of messages per role.
        """
        return {
            "tokens_used": self._token_count,
            "messages_sent": self._message_count,
            "files_written": self._files_written,
            "messages_per_role": self._role_message_count,
        }
