from dataclasses import dataclass
from typing import Optional


@dataclass
class Role:
    """A dataclass representing an AI agent role configuration.

    This class defines the parameters and settings that determine how an AI agent
    behaves and processes requests.

    Attributes:
        name: The name of the role.
        description: A human-readable description of the role's purpose and capabilities.
        system_instruction: The system prompt/instruction that guides the agent's behavior.
        model: The specific AI model to use (e.g. 'gemini-1.5-pro'). Defaults to None.
        temperature: Controls randomness in responses (0.0-2.0). Lower values make responses
            more focused and deterministic. Defaults to None.
        top_p: Nucleus sampling parameter (0.0-1.0) that controls response diversity.
            Lower values make responses more focused. Defaults to None.
        top_k: Limits vocabulary to k most likely tokens. Lower values make responses
            more focused. Defaults to None.
        max_output_tokens: Maximum number of tokens allowed in the response.
            Defaults to None.
        seed: Random seed for reproducible responses. Defaults to None.
        output_type: Indicates whether the role deals with text or image generation.
            Defaults to None.
        search_web: Indicates whether the role can search the web. Defaults to False.
    """

    name: str
    description: str
    system_instruction: str
    model: Optional[str] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    max_output_tokens: Optional[int] = None
    seed: Optional[int] = None
    output_type: Optional[str] = None
    search_web: bool = False

    def __init__(
        self,
        name: str,
        description: str,
        system_instruction: str,
        model: str = None,
        temperature: float = None,
        top_p: float = None,
        top_k: int = None,
        max_output_tokens: int = None,
        seed: int = None,
        output_type: str = None,
        search_web: bool = False,
    ):
        self.name = name
        self.description = description
        self.system_instruction = system_instruction
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.max_output_tokens = max_output_tokens
        self.seed = seed
        self.output_type = output_type
        self.search_web = search_web
