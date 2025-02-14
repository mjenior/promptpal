# promptpal/agent/agent_factory.py

from promptpal.agent.agent_config import AgentConfig
from promptpal.agent.agent import Agent
from promptpal.agent.agent_role import AgentRole
from promptpal.clients import Client, OpenAIClient
from promptpal.roles import (
    ArtistRole,
    AssistantRole,
    DataScientistRole,
    DataVisualizationRole,
    DeveloperRole,
    EditorRole,
    ImageRole,
    PhotographerRole,
    PromptEngineerRole,
    RefactorRole,
    UnitTestsRole,
    WriterRole,
)


DEFAULT_CONFIG = AgentConfig()


class AgentFactory:
    """
    Factory class for configuring agents

    """

    def __init__(self):
        self._roles = {
            "artist": ArtistRole,
            "assistant": AssistantRole,
            "data_scientist": DataScientistRole,
            "data_visualization": DataVisualizationRole,
            "developer": DeveloperRole,
            "editor": EditorRole,
            "image": ImageRole,
            "photographer": PhotographerRole,
            "prompt_engineer": PromptEngineerRole,
            "refactor": RefactorRole,
            "unit_tests": UnitTestsRole,
            "writer": WriterRole,
        }

    def create_agent(
        self,
        role: str = "assistant",
        config: AgentConfig = DEFAULT_CONFIG,
        client: Client = OpenAIClient,
    ) -> Agent:
        """
        Configure and create a new agent

        Args:
            config: Configuration settings for the agent
            role_name: Name of the role to assign to agent (defaults to assistant)

        Returns:
            Configured Agent instance
        """

        # Get role class or raise error if role not found
        role_name = role.lower()
        if role_name not in self._roles:
            available_roles = ", ".join(sorted(self._roles.keys()))
            raise ValueError(
                f"Unknown role '{role_name}'. Available roles are: {available_roles}"
            )

        role_class = self._roles[role_name]
        role = role_class()

        # Create and return configured agent
        return Agent(config=config, role=role, client=client)

    def add_role(self, new_role: AgentRole) -> None:
        """
        Register a new role to the factory.

        Args:
            new_role: The role instance to register

        Raises:
            ValueError: If role with same name already exists
        """
        role_name = new_role.name.lower()
        if role_name in self._roles:
            raise ValueError(f"Role '{role_name}' already exists")

        self._roles[role_name] = new_role.__class__
