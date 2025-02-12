# promptpal/agent/agent_factory.py

from promptpal.agent.agent_config import AgentConfig
from promptpal.agent.agent import Agent


class AgentFactory:
    """
    Factory class for configuring agents
    """

    def __init__(self):
        pass

    def create_agent(config: AgentConfig) -> Agent:
        """
        Configure and create a new agent
        """
