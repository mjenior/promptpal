# promptpal/agent/agent_config.py


from dataclasses import dataclass


@dataclass
class AgentConfig:
    logging: bool = True
    verbose: bool = True
    silent: bool = False
    refine: bool = False

    # Prompt Settings
    use_glyph_promts: bool = True
    use_chain_of_thought: bool = True

    # Model Settings
    # Accepts an OpenAI model alias, https://platform.openai.com/docs/models
    model: str = "gpt-4o-mini"
    seed: str = "t634e``R75T86979UYIUHGVCXZ"
    iterations: int = 1
    temperature: float = 0.7
    top_p: float = 1.0

    # Image Settings
    dimensions: str = "NA"
    quality: str = "NA"
    state: str = "normal"

    message_limit: int = 20
