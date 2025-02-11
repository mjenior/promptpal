# promptpal/agent/agent_role.py


from abc import ABC
from dataclasses import dataclass


@dataclass
class AgentRole(ABC):
    """
    Represents a role that an agent will take on, e.g. developer or artist
    """

    name: str
    prompt: str
