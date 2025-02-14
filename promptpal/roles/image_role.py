from dataclasses import dataclass
from promptpal.agent.agent_role import AgentRole


@dataclass
class ImageRole(AgentRole):
    """Role representing an image generation specialist."""

    name: str = "image"
    prompt: str = """
        Generate only one image at a time. 
        Ensure your choices are logical and complete. 
        Provide detailed, objective descriptions, considering the end goal and satisfaction. 
        Each description must be at least one paragraph, with more than four sentences. 
        If the prompt is more than 4000 characters, summarize text before submission while maintaining complete clarity.
    """
