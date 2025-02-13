# promptpal/agent/agent_factory.py

from promptpal.agent.agent_config import AgentConfig
from promptpal.agent.agent import Agent
from promptpal.agent.agent_role import AgentRole
from promptpal.clients.open_ai import OpenAIClient
from promptpal.roles.assistant_role import AssistantRole
from promptpal.roles.developer_role import DeveloperRole


class AgentFactory:
    """
    Factory class for configuring agents
    """

    def __init__(self):
        self._roles = {
            "assistant": AssistantRole,
            "developer": DeveloperRole,
            # ... add other roles as needed
        }

    def create_agent(self, config: AgentConfig, role_name: str = "assistant") -> Agent:
        """
        Configure and create a new agent

        Args:
            config: Configuration settings for the agent
            role_name: Name of the role to assign to agent (defaults to assistant)

        Returns:
            Configured Agent instance
        """
        # Create client
        client = OpenAIClient()

        # Get role class and create instance
        role_class = self._roles.get(role_name.lower(), AssistantRole)
        role = role_class()

        # Create and return configured agent
        return Agent(config=config, role=role, client=client)
