from dataclasses import dataclass
from promptpal.agent.agent_role import AgentRole


@dataclass
class ArtistRole(AgentRole):
    """Role representing a digital artist."""

    name: str = "artist"
    prompt: str = """
        Digital artwork.
        Hand-drawn, hand-painted.
        Stylized, illustration, painting.
    """
