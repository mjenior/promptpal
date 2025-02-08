# promptpal/agent/agent.py


from promptpal.agent.agent_config import AgentConfig
from promptpal.agent.agent_role import AgentRole
from promptpal.clients.client import Client

class Agent:
    """
    Represents an individual agent
    """

    def __init__(self, config: AgentConfig, role: AgentRole, client: Client):
        self.config = config
        self.role = role
        self.client = client

