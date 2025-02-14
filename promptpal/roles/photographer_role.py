from dataclasses import dataclass
from promptpal.agent.agent_role import AgentRole


@dataclass
class PhotographerRole(AgentRole):
    """Role representing a professional photographer."""

    name: str = "photographer"
    prompt: str = """
        Photograph.
        Highly detailed, photo-realistic.
        Professional lighting, photography lighting.
        Camera used ARRI, SONY, Nikon.
        85mm, 105mm, f/1.4, f2.8.
    """
