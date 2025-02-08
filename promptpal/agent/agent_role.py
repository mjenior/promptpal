# promptpal/agent/agent_role.py


class AgentRole:
    """
    Represents a role that an agent will take on, e.g. developer or artist
    """

    def __init__(self, role_prompt: str):
        self.role_prompt = role_prompt
