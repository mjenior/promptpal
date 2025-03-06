import hashlib
import logging
import os
import re
from collections import defaultdict
from enum import Enum
from importlib import resources
from pathlib import Path

import yaml
from google import genai

from promptpal.roles import Role
from promptpal.roles.role_schema import validate_role


class PromptRefinementType(Enum):
    """Enum for different types of prompt refinement."""

    PROMPT_ENGINEER = "prompt_engineer"
    REFINE_PROMPT = "refine_prompt"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    GLYPH = "glyph"
    KEYWORD = "keyword"


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
    # Split the message into words
    words = message.split()
    file_paths = []

    for word in words:
        # Remove any punctuation at the end of the word
        word = word.rstrip(".,;:!?")

        # Check if the word is a valid file path
        path = Path(word)
        try:
            # Check if the path exists and is a file
            if path.exists() and path.is_file():
                file_paths.append(word)
        except (OSError, ValueError):
            # Skip invalid paths (e.g., paths with invalid characters)
            continue

    return file_paths


class Promptpal:
    """
    A class for managing and interacting with AI roles and agents.
    """

    def __init__(
        self,
        output_dir: str | None = None,
        load_default_roles: bool = True,
        vertexai: bool = True,
        project: str = "",
        location: str = "",
    ):
        """
        Initialize the Promptpal instance.

        Args:
            output_dir: Directory to save generated files. Defaults to None.
            api_key: Gemini API key. Defaults to None.
            load_default_roles: Whether to load default roles. Defaults to True.
            vertexai: Whether to use Vertex AI. Defaults to True. If set to false, expects an environment variable
                GEMINI_API_KEY to be set. If set to true, expects a project and location to be set.
            project: The project to use for Vertex AI. Defaults to "".
            location: The location to use for Vertex AI. Defaults to "".
        """

        if not vertexai:
            # Check if the GEMINI_API_KEY environment variable is set
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key is None:
                raise OSError("GEMINI_API_KEY environment variable not found!")

            self._client = genai.Client(api_key=api_key, http_options={"api_version": "v1beta"})

        else:
            self._client = genai.Client(
                vertexai=True,
                project=project,
                location=location,
                http_options={"api_version": "v1"},
            )

        # Create a chat instance
        self._chat = self._client.chats.create(model="gemini-2.0-flash-001")

        self._roles = {}  # Store roles by name
        self._last_response = None  # Store the last response
        self._output_dir = output_dir  # Directory for writing code and image files

        self._vertexai = vertexai

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

    def list_roles(self) -> None:
        """
        List the available roles with their descriptions in a formatted output.

        Prints a formatted list of all available roles and their descriptions.
        """
        if not self._roles:
            print("No roles available.")
            return

        # Find the longest role name for formatting
        max_name_length = max(len(name) for name in self._roles.keys())

        print("\nAvailable Roles:")
        print("=" * (max_name_length + 24))  # Header line

        # Sort roles alphabetically for better readability
        for name, role in sorted(self._roles.items()):
            print(f"{name.ljust(max_name_length)} | {role.description}")

        print("=" * (max_name_length + 24))  # Footer line
        print(f"Total: {len(self._roles)} roles\n")

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
        tools = None
        if role.search_web:
            tools = [
                genai.types.Tool(
                    google_search=genai.types.GoogleSearchRetrieval(
                        dynamic_retrieval_config=genai.types.DynamicRetrievalConfig(dynamic_threshold=0.6)
                    )
                )
            ]

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
        # vertexai doesn't support file uploads, so we skip this step if vertexai is True
        file_references = find_existing_files(message)

        if file_references:
            if not self._vertexai:
                # For non-vertexai, upload files to the client
                uploaded_files = {}
                for file_path in file_references:
                    try:
                        uploaded_file = self._client.files.upload(file=file_path)
                        uploaded_files[file_path] = uploaded_file
                    except FileNotFoundError:
                        logger.warning(f"File path detected in prompt but not found: {file_path}")
                        continue

                # Split the message around file references
                message_parts = message.split()
                contents = []
                for part in message_parts:
                    if part in uploaded_files:
                        contents.append(uploaded_files[part])
                    else:
                        contents.append(part)
            else:
                # For vertexai, we can't upload files directly, so we'll read the file contents
                # and include them in the message
                file_contents = {}
                for file_path in file_references:
                    try:
                        with open(file_path) as f:
                            file_contents[file_path] = f.read()
                    except FileNotFoundError:
                        logger.warning(f"File path detected in prompt but not found: {file_path}")
                        continue
                    except Exception as e:
                        logger.warning(f"Error reading file {file_path}: {e}")
                        continue

                # If we have file contents, modify the message to include them
                if file_contents:
                    modified_message = message
                    for file_path, content in file_contents.items():
                        file_info = f"\n\nContents of {file_path}:\n```\n{content}\n```\n"
                        modified_message += file_info
                    contents = modified_message
                else:
                    contents = message
        else:
            contents = message

        # Send the message using the chat instance
        response = self._chat.send_message(
            contents,
            config={
                "temperature": role.temperature,
                "system_instruction": role.system_instruction,
                "max_output_tokens": role.max_output_tokens,
                "tools": tools,
            },
        )

        # Store the response
        self._last_response = response

        # Check the usage metadata of the last response
        if self._last_response:
            usage_metadata = self._last_response.usage_metadata
            if usage_metadata.total_token_count and usage_metadata.total_token_count > token_threshold:
                # Summarize the chat
                summary_role = self._roles.get("summarizer")
                if summary_role:
                    summary_response = self._chat.send_message(["Summarize the previous chat."])
                    summary = summary_response.text

                    # Start a new chat with the summary
                    self.new_chat()
                    self._chat.send_message(["Here is a summary of the previous chat:", summary])
                else:
                    logger.error("Summarizer role not found. Use the default roles or add a summarizer role.")

        # Update token count and message count
        self._token_count += response.usage_metadata.total_token_count
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

        for line in response.text.split("\n"):
            print(line)

    def message(self, role_name: str, message: str):
        """
        Write a message and get a response from the role. Messages are independent and do not
        get saved to a chat history like chat does. Message also does not have the fancy features
        of chat like web search or generating code files, only text in and out.

        This method operates completely independently from the _chat instance used by the chat method.
        Each call to this method is a standalone request with no conversation history.
        """
        role = self._roles.get(role_name)
        if role is None:
            raise ValueError(f"Role '{role_name}' not found.")

        try:
            # Generate content with the model directly (not using _chat)
            response = self._client.models.generate_content(
                model=role.model,
                contents=message,
                config={
                    "temperature": role.temperature,
                    "system_instruction": role.system_instruction,
                    "max_output_tokens": role.max_output_tokens,
                },
            )

            return response.text
        except Exception as e:
            logger.error(f"Error in message method: {e!s}")
            # Log more detailed error information
            logger.error(f"Error details: {type(e).__name__}, {e!s}")
            raise

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

    def get_last_response(self) -> str:
        """
        Get the last response from the chat.
        """
        return self._last_response.text

    def _quiet_response(self, text):
        """Create condensed responses to avoid walls of text"""
        role = self._roles.get("summarizer")
        prompt = role.system_instruction.replace("<user_prompt>", text)

        # Use the LLM to summarize the previous response
        response = self._client.models.generate_content(
            model="gpt-4o-mini",
            prompt=prompt,
        )
        # Return the summarized text
        return response

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

    def _extract_refined_prompt(self, text: str) -> str:
        """
        Extract just the refined prompt from the LLM response, removing any additional text.

        Args:
            text (str): The response text from the LLM containing the refined prompt.

        Returns:
            str: The cleaned refined prompt.
        """
        # Try to identify common patterns that wrap the actual prompt
        patterns = [
            r"Here is your (?:new|refined) prompt(?:[:\n]+)([\s\S]+?)(?:\n\n|$)",
            r"(?:Refined|New) prompt(?:[:\n]+)([\s\S]+?)(?:\n\n|$)",
            r"(?:Refined|New) version(?:[:\n]+)([\s\S]+?)(?:\n\n|$)",
            r"```(?:prompt)?\n([\s\S]+?)\n```",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        # If no pattern matched, return the original text with some cleaning
        # Remove common phrases that might appear at the beginning or end
        text = re.sub(
            r"^(?:Here is|I've created|This is) .*?(?:prompt|version)[:\n]+",
            "",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(r"\n\n(?:This prompt|The prompt|This version).*$", "", text, flags=re.IGNORECASE)

        return text.strip()

    def refine_prompt(self, prompt: str, refinement_type: PromptRefinementType = None) -> str:
        """
        Refine a prompt using different methods.

        Args:
            prompt (str): The prompt to refine.
            refinement_type (PromptRefinementType, optional): The type of refinement to apply. Defaults to None.
            keyword (str, optional): The keyword to use for keyword-based refinement. Defaults to None.

        Returns:
            str: The refined prompt.

        Raises:
            ValueError: If an invalid keyword is provided or if keyword is None when refinement_type is KEYWORD.
        """
        if refinement_type is None:
            logger.warning("No refinement type provided. Returning original prompt.")
            return prompt

        if refinement_type == PromptRefinementType.PROMPT_ENGINEER:
            # Use the prompt_engineer role to refine the prompt
            role = self._roles.get("prompt_engineer")
            if role is None:
                logger.warning("The 'prompt_engineer' role is not available. Returning original prompt.")
                return prompt

            # Generate the refined prompt using the prompt_engineer role
            response = self.message("prompt_engineer", f"Refine this prompt: {prompt}")
            return self._extract_refined_prompt(response)

        elif refinement_type == PromptRefinementType.REFINE_PROMPT:
            # Use the refine_prompt role to refine the prompt
            role = self._roles.get("refine_prompt")
            if role is None:
                logger.warning("The 'refine_prompt' role is not available. Returning original prompt.")
                return prompt

            # Generate the refined prompt using the refine_prompt role
            response = self.message("refine_prompt", f"Refine this prompt: {prompt}")
            return self._extract_refined_prompt(response)

        elif refinement_type == PromptRefinementType.GLYPH:
            # Use the glyph_prompt role to refine the prompt
            role = self._roles.get("glyph_prompt")
            if role is None:
                logger.warning("Glyph prompt role not found. Returning original prompt.")
                return prompt

            response = self.message("glyph_prompt", prompt)
            return self._extract_refined_prompt(response)

        elif refinement_type == PromptRefinementType.CHAIN_OF_THOUGHT:
            # Use the chain_of_thought role to refine the prompt
            role = self._roles.get("chain_of_thought")
            if role is None:
                logger.warning("Chain of thought role not found. Returning original prompt.")
                return prompt

            response = self.message("chain_of_thought", f"Refine this prompt: {prompt}")
            return self._extract_refined_prompt(response)

        elif refinement_type == PromptRefinementType.KEYWORD:
            # Apply keyword-based refinement
            keyword_mapping = {
                "paraphrase": "Restate the prompt in different words while preserving meaning.",
                "reframe": "Present the prompt from a different perspective or angle.",
                "summarize": "Condense the prompt to its essential elements.",
                "expand": "Add more detail and context to the prompt.",
                "explain": "Make the prompt more explanatory and educational.",
                "reinterpret": "Offer a fresh interpretation of the prompt's intent.",
                "simplify": "Use less complex language for easier comprehension.",
                "elaborate": "Add more specific details and examples.",
                "amplify": "Strengthen the prompt's impact and emphasis.",
                "clarify": "Remove ambiguity and make the prompt more precise.",
                "adapt": "Modify the prompt to better suit a specific context.",
                "modernize": "Update the prompt with contemporary language and references.",
                "formalize": "Make the prompt more professional and structured.",
                "informalize": "Make the prompt more conversational and approachable.",
                "condense": "Make the prompt more concise without losing meaning.",
                "emphasize": "Highlight key aspects of the prompt.",
                "diversify": "Broaden the prompt to be more inclusive.",
                "neutralize": "Remove bias or charged language from the prompt.",
                "streamline": "Remove unnecessary elements for a more direct prompt.",
                "embellish": "Add stylistic flourishes to the prompt.",
                "illustrate": "Add metaphors or analogies to the prompt.",
                "synthesize": "Combine different aspects into a cohesive prompt.",
                "sensationalize": "Make the prompt more dramatic or attention-grabbing.",
                "humanize": "Make the prompt more relatable and empathetic.",
                "elevate": "Raise the intellectual or conceptual level of the prompt.",
                "energize": "Make the prompt more dynamic and motivating.",
                "soften": "Make the prompt less direct or confrontational.",
                "exaggerate": "Amplify certain aspects for effect.",
                "downplay": "Reduce emphasis on certain aspects of the prompt.",
            }

            refined_prompt = prompt
            for keyword, replacement in keyword_mapping.items():
                if keyword in prompt.lower():
                    refined_prompt = refined_prompt.replace(keyword, replacement)

            return refined_prompt

        else:
            raise ValueError(f"Unknown refinement type: {refinement_type}")
