from dataclasses import dataclass


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
        quiet: Quiets stdout to be minimal and concise
    """

    name: str
    description: str
    system_instruction: str
    model: str | None = None
    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = None
    max_output_tokens: int | None = None
    seed: int | None = None
    output_type: str | None = None
    search_web: bool = False
    quiet: bool = False
